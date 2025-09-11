# -*- coding: utf-8 -*-
"""

Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: mark.sandan@teradata.com
Secondary Owner:

This file implements util functions of data frame.
"""

import numbers
import re
import pandas as pd
from collections import OrderedDict

from teradataml.common.utils import UtilFuncs
from teradataml.common.aed_utils import AedUtils
from teradataml.common.constants import AEDConstants, PTITableConstants, \
    SQLPattern, PythonTypes, TeradataConstants, SQLConstants
from teradataml.common.sqlbundle import SQLBundle
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes

from teradataml.context.context import get_context, get_connection
from teradataml.context.context import _get_current_databasename
from teradataml.dbutils.dbutils import _execute_query_and_generate_pandas_df

from teradataml.options.display import display
from teradataml.options.configure import configure
from teradataml.utils.dtypes import _DtypesMappers
from teradataml.utils.utils import execute_sql

from teradatasqlalchemy.types import FLOAT, NUMBER, DECIMAL, PERIOD_TIMESTAMP
from teradatasqlalchemy.dialect import preparer, dialect as td_dialect
import teradataml.dataframe as tdmldf
from teradataml.dataframe.sql_interfaces import ColumnExpression

from sqlalchemy.sql import select
from sqlalchemy.sql.expression import text
from sqlalchemy import table, column, func
from datetime import datetime, date, time
from decimal import Decimal

# TODO - Need to write unit testcases for these functions
class DataFrameUtils():

    @staticmethod
    def _execute_node_return_db_object_name(nodeid, metaexpression = None):
        """
        Fetches queries and view names from AED node and creates views from queries
        Additionally inspects the metaexpression for consistency

        PARAMETERS:
            nodeid: nodeid to execute
            metaexpression: (optional) updated _metaexpr to validate

        EXAMPLES:
             _execute_node_return_db_object_name(nodeid)
             _execute_node_return_db_object_name(nodeid, metaexpr)

        RETURNS:
            Top level view name.

        """
        aed_obj = AedUtils()
        if not aed_obj._aed_is_node_executed(nodeid):

            view_query_node_type_list = aed_obj._aed_get_exec_query(nodeid)
            view_names, queries, node_query_types, node_ids = view_query_node_type_list

            # Executing Nodes / Creating Views
            for index in range(len(queries) - 1, -1, -1):
                is_persist = False
                if metaexpression and metaexpression._is_persist:
                    is_persist = True

                try:
                    if configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE:
                        UtilFuncs._create_table(view_names[index], queries[index], volatile=True)

                    elif node_query_types[index] == AEDConstants.AED_QUERY_NODE_TYPE_ML_QUERY_MULTI_OUTPUT.value or\
                       ("OUT TABLE " in queries[index] and SQLPattern.SQLMR.value.match(queries[index])) or \
                            is_persist:
                        # TODO:: OR condition in above needs to be removed once AED support is added.
                        UtilFuncs._create_table(view_names[index], queries[index])

                    elif node_query_types in ['groupby', 'groupbytime']:
                        # If query_type is either groupby or groupbytime get it's parent
                        # nodeid and execute queries for the same
                        parent_nodeid = aed_obj._aed_get_parent_nodeids(nodeid)[0]
                        DataFrameUtils._execute_node_return_db_object_name(parent_nodeid)

                    elif node_query_types[index] == AEDConstants.AED_QUERY_NODE_TYPE_REFERENCE.value:
                        # Reference nodes - To be ignored.
                        pass

                    else:
                        UtilFuncs._create_view(view_names[index], queries[index])

                    # Updating Node Status for executed Node
                    aed_obj._aed_update_node_state_single(node_ids[index], AEDConstants.AED_NODE_EXECUTED.value)

                except Exception as emsg:
                    # TODO:: Append node execution details to emsg.
                    #        Node description, such as nodeType or node operation, should be added
                    #        here in 'emsg' to give away more information, where exactly
                    #        node execution failed.
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_EXEC_SQL_FAILED, str(emsg)),
                                      MessageCodes.TDMLDF_EXEC_SQL_FAILED)

        # Setting New Table name retrieved to TDML DF
        result_table_view_name = aed_obj._aed_get_tablename(nodeid)
        # validate the metaexpression
        if configure._validate_metaexpression:
            DataFrameUtils._validate_metaexpression(result_table_view_name, metaexpression)

        return result_table_view_name

    @staticmethod
    def _validate_metaexpression(result_table_view_name, metaexpression):
        """
        Inspects the metaexpression for consistency with the underlying table/view

        PARAMETERS:
            result_table_view_name: a string representing the table/view name to check column metadata
            metaexpression: the metaexpr of the DataFrame to compare against the result_table_view_name

        EXAMPLES:
             _validate_metaexpression('t1', df._metaexpr)
             _execute_node_return_db_object_name(nodeid, metaexpr)

        RETURNS:
            None
            Outputs RuntimeWarnings if mismatches are found

        """
        # metaexpression should have already been updated
        if metaexpression is not None:

            name = lambda x: x[0]
            type_ = lambda x: x[1]

            # compare sorted by name of column
            df = sorted(UtilFuncs._describe_column(DataFrameUtils._get_metadata_from_table(result_table_view_name)), key = lambda x: x[0])
            meta = sorted(metaexpression.c, key = lambda x: x.name)

            # check length
            if len(df) == len(meta):
                for i in range(len(df)):

                    # map Teradata type to python type
                    meta_type = UtilFuncs._teradata_type_to_python_type(meta[i].type)

                    # compare column names and types
                    if meta[i].name != name(df[i]) or meta_type != type_(df[i]):
                        err_msg = "[Mismatch when checking %s]\n\t[Table/View] %s %s\n\t[MetaExpression] %s %s (mapped from => %s)\n"
                        raise RuntimeError(err_msg % (result_table_view_name,
                                                      name(df[i]), type_(df[i]),
                                                      meta[i].name, meta_type, meta[i].type))
            else:
                err_msg = "[Length mismatch when checking %s]\nSource Table/View has length %s but MetaExpression has length %s"
                raise RuntimeError(err_msg % (result_table_view_name, len(df), len(meta)))

    @staticmethod
    def _get_dataframe_print_string(table_name, index_label, orderby=None, undropped_index=None):
        """
        Builds string output for teradataml DataFrame

        PARAMETERS:
            table_name - Name of the database table to read from.
            index_label - String/List specifying column to use as index.
            orderby - order expression to sort returned rows

        EXAMPLES:
             _get_dataframe_print_string('table_name', None, None)

        RETURNS:
            String representation of a pandas DataFrame.

        """
        read_query = SQLBundle._build_top_n_print_query(table_name, display.max_rows, orderby)

        if index_label is not None:
            pandas_df = _execute_query_and_generate_pandas_df(read_query, index=index_label)
        else:
            pandas_df = _execute_query_and_generate_pandas_df(read_query)

        return pandas_df.to_string()

    @staticmethod
    def _get_pprint_dtypes(column_names_and_types, null_count=False):
        """
        returns a string containing the column names and types.
        If null_count is not None, the string will also contain
        the number of non-null values for each column.

        PARAMETERS:
            column_names_and_types - List of column names and types.
            null_count(optional) - List of the non-null count for each column.

        EXAMPLES:
            >>>print(_get_pprint_dtypes(column_names_and_types)
            accounts      str
            Feb         float
            Jan           int
            Mar           int
            Apr           int
            datetime      str

            >>>print(_get_pprint_dtypes(column_names_and_types, null_count)
            accounts    3 non-null str
            Feb         3 non-null float
            Jan         3 non-null int
            Mar         3 non-null int
            Apr         3 non-null int
            datetime    3 non-null str

        RAISES:

        """

        col_names = [i[0] for i in column_names_and_types]
        col_types = [i[1] for i in column_names_and_types]
        max_col_names = len(max(col_names, key=len)) + 4
        max_col_types = len(max(col_types, key=len))
        dtypes_string = ""
        if not null_count:
            for colname, coltype in column_names_and_types:
                dtypes_string += "{0: <{name_width}}{1: >{type_width}}\n".format(colname, coltype,
                                                                                 name_width=max_col_names,
                                                                                 type_width=max_col_types)
        else:
            null_count = [i[2] for i in column_names_and_types]
            max_null_count = len(str(max(null_count, key=len)))
            for colname, coltype, num_nulls in column_names_and_types:
                dtypes_string += "{0: <{name_width}}{1: <{count_width}} non-null {2: <{type_width}}\n".format(colname,
                                                                                                              num_nulls,
                                                                                                              coltype,
                                                                                                              name_width=max_col_names,
                                                                                                              count_width=max_null_count,
                                                                                                              type_width=max_col_types)
        # Remove last new line character.
        dtypes_string = dtypes_string[:-1]
        return dtypes_string

    @staticmethod
    def _get_metadata_from_table(table_name):
        """
        Retrieves column metadata by executing a HELP COLUMN command.

        PARAMETERS:
            table_name - The table name or view name.

        RETURNS:
            returns the result set (column information) from HELP COLUMN.

        RAISES:
            Database error if an error occurred while executing the HELP COLUMN.

        EXAMPLES:
            df = DataFrame.from_table('mytab')
            metadata = _get_metadata_from_table(df._table_name)
        """
        # Construct HELP COLUMN command.
        help_col_sql = SQLBundle._build_help_column(table_name)
        # Execute HELP COLUMN command.
        return UtilFuncs._execute_query(help_col_sql)

    @staticmethod
    def _extract_select_string(select_expression):
        """
        Takes in a string/list representing a Pandas selection clause of any of the forms (only):
            a) "col1" or 'col1'
            b) ["col 1"] or ['col 1']
            c) ["col1", "col2", "col3"] or ['col1', 'col2', 'col3']
            d) [['col1', 'col2', 'col3']] or [["col1", "col2", "col3"]]

        And returns a list with column strings representing the selection of the form:
            a)  ['col1']
            b)  ['col 1']
            c)  ['col1','col2','col3']
            d)  ['col1','col2','col3']

        Column Names ("col1", "col2"..) are Strings representing database table Columns.
        All Standard Teradata Data-Types for columns supported: INTEGER, VARCHAR(5), FLOAT.

        PARAMETERS:
            selection_expression -  Expression representing column selection
            Type - String or List of Strings or List of List (Single level only)
            Required - Yes

        EXAMPLES:
            UtilFuncs._extract_select_string([['col1', 'col2']])
            UtilFuncs._extract_select_string("col1")
            UtilFuncs._extract_select_string(["col1"])
            UtilFuncs._extract_select_string(["col1","col2","col3"])

        RETURNS:
            List of Strings representing column names.

        RAISES:
            TeradataMlException
        """
        tdp = preparer(td_dialect)
        column_list = []

        # Single String column
        if isinstance(select_expression, str):
            # Error handling - Empty String
            if select_expression ==  "":
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_SELECT_NONE_OR_EMPTY),
                                      MessageCodes.TDMLDF_SELECT_NONE_OR_EMPTY)
            else:
                column_list.append(tdp.quote("{0}".format(select_expression.strip())))

        # Error Handling -  [],  [""], [None], ["None"], ['col1', None], ['col1', '']
        elif isinstance(select_expression, list) and (len(select_expression) ==  0  or
                                                    any(element in [None, "None", ""] for element in select_expression)):
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_SELECT_NONE_OR_EMPTY),
                                      MessageCodes.TDMLDF_SELECT_NONE_OR_EMPTY)

        # List - ["col1"] or ["col1", "col2", "col3"]
        elif isinstance(select_expression, list) and all(isinstance(element, str) for element in select_expression):
            if len(select_expression) == 1:
                column_list.append(tdp.quote("{0}".format(select_expression[0].strip())))
            else:
                column_list = [tdp.quote("{0}".format(element.strip())) for element in select_expression]

        # List of List (Single level only - Pandas Syntax) - [["col1", "col2", "col3"]]
        elif isinstance(select_expression, list) and isinstance(select_expression[0], list):
            # Error Handling - [[]], [[""]], [[None]], [['col1', None]], [['col1', "None"]], ["col1", ""]
            if len(select_expression[0]) ==  0  or any(element in [None, "None", ""] for element in select_expression[0]):
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_SELECT_NONE_OR_EMPTY),
                                      MessageCodes.TDMLDF_SELECT_NONE_OR_EMPTY)

            else:
                column_list = [tdp.quote("{0}".format(element.strip())) for element in select_expression[0]]

        # Any other Format - Raise Format Exception
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_SELECT_INVALID_FORMAT),
                                      MessageCodes.TDMLDF_SELECT_INVALID_FORMAT)
        return column_list

    @staticmethod
    def _get_primary_index_from_table(table_name):
        """
        Retrieves the primary index by executing a HELP INDEX command.
        PARAMETERS:
            table_name - The table name or volatile table name.
        RETURNS:
            Returns a list containing the primary index columns from HELP INDEX.
            If the there are no primary index (NoPI table), then returns None.
        RAISES:
            Database error if an error occurred while executing the HELP INDEX.
        EXAMPLES:
            df = DataFrame.from_table('mytab')
            index_labels = df._get_metadata_from_table(df._table_name)
        """
        # Construct HELP INDEX command.
        help_index_sql = SQLBundle._build_help_index(table_name)

        # Execute HELP INDEX command.
        rows = UtilFuncs._execute_query(help_index_sql)
        index_labels = []
        for row in rows:
            # row[1] specifies whether the Index is 'Primary or Secondary?'
            if row[1].rstrip() == 'P':
                # row[2] specifies a string of comma separated column names that form the primary index
                if "," in row[2]:
                    index_cols = row[2].split(',')
                else:
                    index_cols = [row[2]]
                for index_col in index_cols:
                    # Since TD_TIMEBUCKET column in PTI tables is not functionally available, it can be ignored
                    # from the index information as well (else a warning is generated by SQLAlchemy).
                    # row[12] corresponds to 'Timebucket' column in the results of 'help index' SQL command, which
                    # is available only when the version supports PTI tables.
                    if index_col == PTITableConstants.TD_TIMEBUCKET.value and len(row) > 11 and row[12] is not None:
                        continue
                    else:
                        index_labels.append(index_col)

        if len(index_labels) > 0:
            return index_labels
        else:
            return None

    @staticmethod
    def __validate_sort_type_raise_exception(sort_col_type):
        """
        Function to raise TeradatamlException for errors encountered for invalid/incorrect
        "sort_col_type" in "_validate_sort_type" function.

        PARAMETERS:
            sort_col_type: The sort column type.

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            df_utils.__validate_sort_type_raise_exception(PythonTypes.PY_STRING_TYPE.value)
        """
        msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_INDEX_TYPE).format(sort_col_type)
        raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_INDEX_TYPE)

    @staticmethod
    def _validate_sort_col_type(sort_col_type, sort_col_values):
        """
        Validates a list of sort column values with the sort column type.

        PARAMETERS:
            sort_col_type - The sort column type.
            sort_col_values - A single value or list-like values

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            df_utils._validate_sort_col_type(PythonTypes.PY_STRING_TYPE.value, ["Jan", "Feb"])
            df_utils._validate_sort_col_type(PythonTypes.PY_STRING_TYPE.value, "Jan")
            df_utils._validate_sort_col_type(PythonTypes.PY_INT_TYPE.value, [1, 2])
        """
        if isinstance(sort_col_values, list):
            if sort_col_type == PythonTypes.PY_STRING_TYPE.value:
                if not all(isinstance(i, str) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_FLOAT_TYPE.value:
                if not all(isinstance(i, float) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_DECIMAL_TYPE.value:
                if not all(isinstance(i, Decimal) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_DATETIME_TYPE.value:
                if not all(isinstance(i, datetime) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_TIME_TYPE.value:
                if not all(isinstance(i, time) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_DATE_TYPE.value:
                if not all(isinstance(i, date) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_BYTES_TYPE.value:
                if not all(isinstance(i, bytes) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            else:  # numeric type
                if not all(isinstance(i, numbers.Integral) for i in sort_col_values):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
        elif isinstance(sort_col_values, (tuple, dict)):
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_DROP_ARGS),
                                      MessageCodes.TDMLDF_DROP_ARGS)
        else:
            if sort_col_type == PythonTypes.PY_STRING_TYPE.value:
                if not isinstance(sort_col_values, str):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_FLOAT_TYPE.value:
                if not isinstance(sort_col_values, float):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_DECIMAL_TYPE.value:
                if not isinstance(sort_col_values, Decimal):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_DATETIME_TYPE.value:
                if not isinstance(sort_col_values, datetime):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_TIME_TYPE.value:
                if not isinstance(sort_col_values, time):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_DATE_TYPE.value:
                if not isinstance(sort_col_values, date):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            elif sort_col_type == PythonTypes.PY_BYTES_TYPE.value:
                if not isinstance(sort_col_values, bytes):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)
            else:  # numeric type
                if not isinstance(sort_col_values, numbers.Integral):
                    DataFrameUtils.__validate_sort_type_raise_exception(sort_col_type)

    def _get_required_columns_types_from_metaexpr(metaexpr, col_list = None):
        """
        Retrieves column names and types from meta expression. If you want to get types for only some columns,
        pass those columns to 'col_list' argument.

        PARAMETERS:
           metaexpr - Meta expression from which columns and types to be retrieved.
           col_list - Column list for which you want to get types

        RETURNS:
           Dictionary: key as column name and datatype as value.

        EXAMPLES:
           df = DataFrame.from_table('mytab')
           metadata = _get_required_columns_types_from_metaexpr()
        """

        if isinstance(col_list, str):
            col_list = [col_list]

        if col_list is not None and not isinstance(col_list, list):
            return None

        meta_cols = metaexpr.t.c
        meta_columns = [c.name for c in meta_cols]
        col_names = []
        col_types = []

        # When column list to retrieve is not provided, return meta-data for all columns.
        if col_list is None:
            for col_name in meta_columns:
                    col_names.append(meta_cols[col_name].name)
                    col_types.append(meta_cols[col_name].type)

        # Return meta-data for only requested columns otherwise.
        else:
            for col_name in col_list:
                if DataFrameUtils._check_column_exists(col_name, meta_columns):
                    # _metaexpr saves columns without quotes, so unquoting.
                    unquoted_col_name = col_name.replace('"', "")
                    col_names.append(meta_cols[unquoted_col_name].name)
                    col_types.append(meta_cols[unquoted_col_name].type)

        return OrderedDict(zip(col_names, col_types))

    @staticmethod
    def _check_column_exists(column_name, df_columns):
        """
         Checks provide column present in list of columns or not.
         Note:
             It is calling functions responsibility to send the column and columns list in proper case.
             By default the look up is case-sensitive. If they would like to have it case insensitive, then
             one should send the the column_name and df_columns list in lower case.

         PARAMETERS:
            column_name - Column name which need to be check.
            df_columns  - List columns in which column to be check.

         RETURNS:
            True if column exists otherwase False.

         EXAMPLES:
            df = DataFrame.from_table('mytab')
            metadata = _check_column_exists("col1", df.columns)
        """
        unquoted_df_columns = [column.replace('"', "") for column in df_columns]
        if column_name.replace('"', "") in unquoted_df_columns:
            return True
        else:
            return False

    @staticmethod
    def _validate_agg_function(func, col_names):
        """
        Internal function to validate column names against actual
        column names passed as parameter and aggregate operations
        against valid aggregate operations.

        PARAMETERS:
            func  - (Required) Specifies the function(s) to be
                    applied on teradataml DataFrame columns.
                    Acceptable formats for function(s) are string,
                    dictionary or list of strings/functions.
                    Accepted combinations are:
                    1. String function name
                    2. List of string functions
                    3. Dictionary of column names -> string function
                       (or list of string functions)
            col_names - List. Names of the columns in Dataframe.

        RETURNS:
            operations - dict of columns -> aggregate operations
            Unified dictionary, similar to func, even for string and
            list of strings or functions.

        RAISES:
            1. TDMLDF_INVALID_AGGREGATE_OPERATION - If the aggregate
                operation(s) received in parameter 'func' is/are
                invalid.

                Possible Value :
                Invalid aggregate operation(s): minimum, counter.
                Valid aggregate operation(s): count, max, mean, min,
                std, sum.

            2. TDMLDF_AGGREGATE_INVALID_COLUMN - If any of the columns
                specified in 'func' is not present in the dataframe.

                Possible Value :
                Invalid column(s) given in parameter func: col1.
                Valid column(s) : A, B, C, D.

        EXAMPLES:
            Let the dataframe contain 2 columns, col1 and col2.

            VALID EXAMPLES:
            1. operations = DataFrameUtils._validate_agg_function(
                    operation = 'mean', ['col1', 'col2'])

            2. operations = DataFrameUtils._validate_agg_function(
                    operation = ['mean', 'min'], ['col1', 'col2'])

            3. operations = DataFrameUtils._validate_agg_function(
                    {'col1' : ['mean', 'min'], 'col2' : 'count'},
                                                    ['col1', 'col2'])

            INVALID EXAMPLES:
            1. operations = DataFrameUtils._validate_agg_function(
                    operation = 'counter', ['col1', 'col2'])

            2. operations = DataFrameUtils._validate_agg_function(
                    {'col1' : ['mean', 'min'], 'col55' : 'count'},
                                                    ['col1', 'col2'])
        """
        operations = OrderedDict()

        valid_aggregate_operations = UtilFuncs._get_valid_aggregate_operations()

        if isinstance(func, str):
            for column in col_names:
                operations[column] = [func]
        elif isinstance(func, list):
            for column in col_names:
                operations[column] = func
        else:
            for column in func:
                if isinstance(func[column], str):
                    func[column] = [func[column]] # Converts string inside dict to list
            operations = func

        given_columns = operations.keys()
        invalid_columns = []
        all_operations = []
        for col in given_columns:
            all_operations.extend(operations[col])
            if col not in col_names:
                invalid_columns.append(col)
        if len(invalid_columns) > 0:  # If any of the columns specified is not present in dataframe
            col_names.sort()
            invalid_columns.sort()
            msg = Messages.get_message(MessageCodes.TDMLDF_AGGREGATE_INVALID_COLUMN). \
                format(", ".join(invalid_columns), 'func', ", ".join(col_names))
            raise TeradataMlException(msg, MessageCodes.TDMLDF_AGGREGATE_INVALID_COLUMN)

        all_operations = list(set(all_operations))
        invalid_aggregates = []
        for operation in all_operations:
            if operation not in valid_aggregate_operations and not operation.startswith('percentile_') \
                    and operation not in UtilFuncs._get_valid_time_series_aggregate_operations():
                invalid_aggregates.append(operation)
        if len(invalid_aggregates) > 0: # If any of the aggregate operations specified is not valid
            # To raise error message, let's add other time series aggregate operations those can be
            # used with DataFrame.agg() method.
            valid_aggregate_operations = valid_aggregate_operations + ['first', 'last', 'mode']
            valid_aggregate_operations.sort()
            invalid_aggregates.sort()
            msg = Messages.get_message(MessageCodes.TDMLDF_INVALID_AGGREGATE_OPERATION). \
                format(", ".join(invalid_aggregates), ", ".join(valid_aggregate_operations))
            raise TeradataMlException(msg, MessageCodes.TDMLDF_INVALID_AGGREGATE_OPERATION)

        return operations

    @staticmethod
    def _generate_aggregate_column_expression(df, column, operation, describe_op, tdp, **kwargs):
        """
        Function generate the aggregate column expression for the provided column
        and aggregate function.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which is to be used to get the
                desired aggregate column expression.
                Types: teradataml DataFrame

            column:
                Required Argument.
                Specifies the column name for which desired aggregate operation is
                to be used.
                Types: str

            operation:
                Required Argument.
                Specifies the aggregate operation.
                Types: str

            describe_op:
                Required Argument.
                Specifies a boolean flag, that will decide whether the aggregate
                operation is being performed for DataFrame.describe() or not.
                Types: bool

            tdp:
                Required Argument.
                Specifies a TeradataIdentifierPreparer object. It is required for
                quoting.
                Types: TeradataIdentifierPreparer

            kwargs:
                Specifies miscellaneous keyword arguments that can be passed to
                aggregate functions.

        RAISES:
            AttributeError - In case ColumnExpression does not have desired aggregate
            function implemnted.

        RETURNS:
            A boolean stating whether column is supported or not, New column name,
            New column type, A string representing column aggregate expression,
            invalid column information in case column has unsupported type for an
            aggregate operation.

        EXAMPLES:
            column_supported, new_column_name, new_column_type, column_aggr_expr, invalid_column_str = \
                DataFrameUtils._generate_aggregate_column_expression(df=df, column=column, operation=func,
                                                                     describe_op=describe_op, percentile=percentile,
                                                                     tdp=tdp, **kwargs)
        """
        try:
            key_to_process = ""
            # quote column names same as that of the Teradata reserved keywords.
            if "sort_columns" in kwargs:
                key_to_process = "sort_columns"
            elif "sort_column" in kwargs:
                key_to_process = "sort_column"

            if key_to_process:
                quoted_columns = UtilFuncs._process_for_teradata_keyword(kwargs[key_to_process])
                kwargs[key_to_process] = quoted_columns

            if operation.startswith('percentile_'):
                try:
                    _operation_value = operation.split('_')
                    _floatvalue = float(_operation_value[1])
                    if _floatvalue < 0.0 or _floatvalue > 1.0 or len(_operation_value)>2:
                        raise ValueError
                except ValueError:
                    mssg = "Invalid aggregate operation '{}' requested on TeradataML DataFrame." \
                           " Valid operation should be in format 'percentile_<floatvalue>' and <floatvalue> " \
                           "should be in range [0.0, 1.0].".format(operation)
                    raise ValueError(mssg) from None
                func_expression = getattr(df[column], 'percentile')(percentile=_floatvalue)
            else:
                func_expression = getattr(df[column], operation)(describe_op=describe_op, **kwargs)
            new_column_name = column if describe_op else "{1}_{0}".format(column, operation)
            # column_supported, new_column_name, new_column_type, column_aggr_expr, invalid_column_str
            return True, new_column_name, NUMBER() if describe_op else func_expression.type, \
                   func_expression.compile_label(new_column_name), None
        except AttributeError:
            # We are here means, provided operation is invalid and is not supported.
            # This if for internal purpose only.
            # Validation of operations for "agg" should be done in "agg" only.
            raise RuntimeError("Invalid aggregate function: {}".format(operation))
        except RuntimeError:
            # We are here means, column does not support the provided operation.
            # We will ignore this and add the column to invalid column list.
            # invalid_columns[operation].append("({0} - {1})".format(column, column_type)) OR
            # We will raise Generic message, mentioning DF does not have any column with type
            # supported to perform an operation.
            if describe_op:
                return True, tdp.quote(column), NUMBER(), 'null as {}'.format(tdp.quote(column)), None
            else:
                return False, None, None, None, "({0} - {1})".format(column, df[column].type)
        except Exception:
            raise

    @staticmethod
    def _construct_sql_expression_for_aggregations(df, column_names, column_types, func, percentile=.5,
                                                   describe_op=False, **kwargs):
        """
        Internal function to create and return the sql expression
        corresponding to given operation, given column_names and
        column_types.

        Column_types are used to check whether all the datatypes are
        valid types for given operation and throw exception if they
        are not.

        PARAMETERS :
            df:
                Required Argument.
                Specifies teradataml DataFrame which is to be used to get the desired
                aggregate column expression.
                Types: teradataml DataFrame

            column_names:
                Required Argument.
                Specifies the column names for which desired aggregate operation is
                to be executed.
                Types: List of strings

            column_types:
                Required Argument.
                Specifies the respective column types for column names.
                Types: List of teradatasqlalchemy types

            func:
                Required Argument.
                Specifies the aggregate function(s) to be applied on teradataml
                DataFrame columns.
                Types: string, dictionary or list of strings/functions.
                       Accepted combinations are:
                            1. String function name
                            2. List of functions
                            3. Dictionary containing column name as key and aggregate
                               function name (string or list of strings) as value
                            4. ColumnExpression built using the aggregate functions. 
                            5. List of ColumnExpression built using the aggregate functions.

            percentile:
                Optional Argument.
                Specifies a value between 0 and 1 that can only be used with func = 'percentile'.
                The default is .5, which returns the 50th percentiles.
                Types: float

            describe_op:
                Optional Argument.
                Specifies a boolean flag, that will decide whether the aggregate operation being
                performed is for DataFrame.describe() or not.
                Types: bool

            kwargs:
                Specifies miscellaneous keyword arguments that can be passed to aggregate functions.

        RETURNS :
            a)sql expression as
                1. 'min(col1) as min_col1, min(col2) as min_col2' if
                        col1 and col2 are the columns in Dataframe and
                        operation is 'min'
                2. 'max(col1) as max_col1, max(col2) as max_col2' if
                        col1 and col2 are the columns in Dataframe and
                        operation is 'max'
                3. 'min(col1) as min_col1, stddev_samp(col2) as
                        std_col2' if col1, col2 are the columns in
                        Dataframe and operations are min, std.
                etc...
            b) new columns' names (eg min_col1, min_col2 ...)
            c) new columns' types
        RAISES:
            TeradataMLException
            1. TDMLDF_AGGREGATE_COMBINED_ERR - If the provided
                aggregate operations do not support specified columns.

                Possible Value :
                No results. Below is/are the error message(s):
                All selected columns [(col1 - VARCHAR)] is/are
                unsupported for 'sum' operation.

            2. TDMLDF_INVALID_AGGREGATE_OPERATION - If the aggregate
                operation(s) received in parameter 'func' is/are
                invalid.

                Possible Value :
                Invalid aggregate operation(s): minimum, counter.
                Valid aggregate operation(s): count, max, mean, min,
                std, sum.

            3. TDMLDF_AGGREGATE_INVALID_COLUMN - If any of the columns
                specified in func is not present in the dataframe.

                Possible Value :
                Invalid column(s) given in parameter func: col1.
                Valid column(s) : A, B, C, D.

        EXAMPLES:
            col_names, col_types = \
            df_utils._get_column_names_and_types_from_metaexpr(
                                                     self._metaexpr)
            expr, new_col_names, new_col_types = \
            df_utils._construct_sql_expression_for_aggregations(
                                    col_names, col_types, 'min')

            expr1, new_col_names1, new_col_types1 = \
            df_utils._construct_sql_expression_for_aggregations(
                                col_names, col_types, ['min', 'sum'])

            expr2, new_col_names2, new_col_types2 = \
            df_utils._construct_sql_expression_for_aggregations(
                    col_names, col_types, {'col1 : ['min', 'sum'],
                                                'col2' : 'mean'})

        """

        # eg of column_types: [VARCHAR(length=13), INTEGER(), VARCHAR(length=60), VARCHAR(length=5),
        # FLOAT(precision=0)]

        # eg of types of each column are <class 'teradatasqlalchemy.types.VARCHAR'>,
        # <class 'teradatasqlalchemy.types.INTEGER'>, <class 'teradatasqlalchemy.types.FLOAT'>,
        # <class 'teradatasqlalchemy.types.INTERVAL_MINUTE_TO_SECOND'> etc..

        # If function is of type time series aggregates, we process aggregation differently.
        if not isinstance(func, str):
            # If func is not instance of string, that means function call is
            # from DataFrame.agg(). And is made to process multiple functions.
            # We will process the same differently, as we need to map and serialize the
            # column names and aggregate function operate on.
            # If we have just function to be executed on complete DataFrame, then we don't need
            # this extra processing. Also, if call is from DataFrame.agg(), time series aggregate check
            # is not required. As special Time Series aggregate functions cannot be used in
            # DataFrame.agg().
            return DataFrameUtils._construct_sql_expression_for_aggregations_for_agg(df, column_names, column_types,
                                                                                     func, percentile, describe_op,
                                                                                     **kwargs)

        as_time_series_aggregate = False
        if "as_time_series_aggregate" in kwargs.keys():
            as_time_series_aggregate = kwargs["as_time_series_aggregate"]

        if as_time_series_aggregate and func in ['bottom', 'bottom with ties', 'delta_t', 'mad', 'top',
                                                 'top with ties']:
            return DataFrameUtils._construct_sql_expression_for_time_series_aggregations(df, column_names, column_types,
                                                                                         func, **kwargs)

        tdp = preparer(td_dialect)

        # This variable is used to decide whether DataFrame has all columns unsupported
        # for the provided operations.
        all_unsupported_columns = True
        valid_columns = []
        invalid_columns = []
        new_column_names = []
        new_column_types = []
        for column in column_names:
            column_supported, new_column_name, new_column_type, column_aggr_expr, invalid_column_str = \
                DataFrameUtils._generate_aggregate_column_expression(df=df, column=column, operation=func,
                                                                     describe_op=describe_op, percentile=percentile,
                                                                     tdp=tdp, **kwargs)
            if column_supported:
                all_unsupported_columns = False
                new_column_names.append(new_column_name)
                new_column_types.append(new_column_type)
                valid_columns.append(column_aggr_expr)
            else:
                invalid_columns.append("({0} - {1})".format(column, df[column].type))

        if all_unsupported_columns:

            error_msgs = []
            invalid_columns.sort()  # Helps in catching the columns in lexicographic order
            error = MessageCodes.TDMLDF_AGGREGATE_UNSUPPORTED.value.format(", ".join(invalid_columns),
                                                                           func)
            error_msgs.append(error)

            if len(valid_columns) == 0:  # No supported columns in the given list of columns
                raise TeradataMlException(Messages.get_message(
                    MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR).format("\n".join(error_msgs)),
                                          MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR)

        # quote column names same as that of the Teradata reserved keywords.
        quote_column_name = [UtilFuncs._process_for_teradata_keyword(col) for col in column_names]

        # Actual columns should be retained if "drop_columns" is set to False.
        if kwargs.get("drop_columns") is False:
            valid_columns = quote_column_name + valid_columns
            new_column_names = column_names + new_column_names
            new_column_types = column_types + new_column_types

        aggregate_expr = ", ".join(valid_columns)
        return aggregate_expr, new_column_names, new_column_types

    @staticmethod
    def _construct_sql_expression_for_aggregations_for_agg(df, column_names, column_types, func, percentile=.5,
                                                           describe_op=False, **kwargs):
        """
        Internal function to create and return the sql expression
        corresponding to given operation, given column_names and
        column_types.

        Column_types are used to check whether all the datatypes are
        valid types for given operation and throw exception if they
        are not.

        PARAMETERS :
            df:
                Required Argument.
                Specifies teradataml DataFrame which is to be used to get the desired
                aggregate column expression.
                Types: teradataml DataFrame

            column_names:
                Required Argument.
                Specifies the column names for which desired aggregate operation is
                to be executed.
                Types: List of strings

            column_types:
                Required Argument.
                Specifies the respective column types for column names.
                Types: List of teradatasqlalchemy types

            func:
                Required Argument.
                Specifies the aggregate function(s) to be applied on teradataml
                DataFrame columns.
                Types: string, dictionary or list of strings/functions.
                       Accepted combinations are:
                            1. String function name
                            2. List of functions
                            3. Dictionary containing column name as key and aggregate
                               function name (string or list of strings) as value
                            4. ColumnExpression built using the aggregate functions. 
                            5. List of ColumnExpression built using the aggregate functions.

            percentile:
                Optional Argument.
                Specifies a value between 0 and 1 that can only be used with func = 'percentile'.
                The default is .5, which returns the 50th percentiles.
                Types: float

            describe_op:
                Optional Argument.
                Specifies a boolean flag, that will decide whether the aggregate operation being
                performed is for DataFrame.describe() or not.
                Types: bool

            kwargs:
                Specifies miscellaneous keyword arguments that can be passed to aggregate functions.

        RETURNS :
            a)sql expression as
                1. 'min(col1) as min_col1, min(col2) as min_col2' if
                        col1 and col2 are the columns in Dataframe and
                        operation is 'min'
                2. 'max(col1) as max_col1, max(col2) as max_col2' if
                        col1 and col2 are the columns in Dataframe and
                        operation is 'max'
                3. 'min(col1) as min_col1, stddev_samp(col2) as
                        std_col2' if col1, col2 are the columns in
                        Dataframe and operations are min, std.
                etc...
            b) new columns' names (eg min_col1, min_col2 ...)
            c) new columns' types
        RAISES:
            TeradataMLException
            1. TDMLDF_AGGREGATE_COMBINED_ERR - If the provided
                aggregate operations do not support specified columns.

                Possible Value :
                No results. Below is/are the error message(s):
                All selected columns [(col1 - VARCHAR)] is/are
                unsupported for 'sum' operation.

            2. TDMLDF_INVALID_AGGREGATE_OPERATION - If the aggregate
                operation(s) received in parameter 'func' is/are
                invalid.

                Possible Value :
                Invalid aggregate operation(s): minimum, counter.
                Valid aggregate operation(s): count, max, mean, min,
                std, sum.

            3. TDMLDF_AGGREGATE_INVALID_COLUMN - If any of the columns
                specified in func is not present in the dataframe.

                Possible Value :
                Invalid column(s) given in parameter func: col1.
                Valid column(s) : A, B, C, D.

        EXAMPLES:
            col_names, col_types = \
            df_utils._get_column_names_and_types_from_metaexpr(
                                                     self._metaexpr)
            expr, new_col_names, new_col_types = \
            df_utils._construct_sql_expression_for_aggregations_for_agg(
                                    col_names, col_types, 'min')

            expr1, new_col_names1, new_col_types1 = \
            df_utils._construct_sql_expression_for_aggregations_for_agg(
                                col_names, col_types, ['min', 'sum'])

            expr2, new_col_names2, new_col_types2 = \
            df_utils._construct_sql_expression_for_aggregations_for_agg(
                    col_names, col_types, {'col1 : ['min', 'sum'],
                                                'col2' : 'mean'})

        """
        # If function is of type time series aggregates, we process aggregation differently.
        # Also, one is not supposed to pass below time series aggreagtes to DataFrame.agg():
        #   ['bottom', 'bottom with ties', 'delta_t', 'mad', 'top', 'top with ties']
        # Thus, no extra processing is required for time series aggregates over here.

        if isinstance(func, ColumnExpression) or (isinstance(func, list) and isinstance(func[0], ColumnExpression)):
            column_agg_expr = []
            new_column_names = []
            new_column_types = []
            if isinstance(func, ColumnExpression):
                func= UtilFuncs._as_list(func)

            # validate that func is a list of ColumnExpression
            for expr in func:
                if not isinstance(expr, ColumnExpression):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                              'func', ['str, dict, ColumnExpression or list of values of type(s): str, ColumnExpression']),
                                              MessageCodes.UNSUPPORTED_DATATYPE)

            for operations in func:
                alias = operations.alias_name
                column_agg_expr.append(operations.compile_label(alias))
                new_column_names.append(alias)
                new_column_types.append(operations.type)
            aggregate_expr = ", ".join(column_agg_expr)
            return aggregate_expr, new_column_names, new_column_types

        # 'operations' contains dict of columns -> list of aggregate operations
        operations = DataFrameUtils._validate_agg_function(func, column_names)

        all_valid_columns = []
        all_invalid_columns = {}
        all_new_column_names = []
        all_new_column_types = []

        # For each column, the value is True if there is at least one valid operation (operation on valid datatype)
        column_supported = {}
        tdp = preparer(td_dialect)
        for column in operations:
            column_supported[column] = False
            valid_columns = []
            invalid_columns = {}
            new_column_names = []
            new_column_types = []
            for operation in operations[column]:
                is_colop_supported, new_col, new_coltype, column_aggr_expr, invalid_column_info = \
                    DataFrameUtils._generate_aggregate_column_expression(df=df, column=column, operation=operation,
                                                                         describe_op=describe_op, percentile=percentile,
                                                                         tdp=tdp, **kwargs)
                if is_colop_supported:
                    column_supported[column] = is_colop_supported
                    new_column_names.append(new_col)
                    new_column_types.append(new_coltype)
                    valid_columns.append(column_aggr_expr)
                else:
                    if operation in invalid_columns:
                        invalid_columns[operation].append(invalid_column_info)
                    else:
                        invalid_columns[operation] = [invalid_column_info]

            all_valid_columns.extend(valid_columns)
            all_new_column_names.extend(new_column_names)
            all_new_column_types.extend(new_column_types)

            for operation in invalid_columns:
                if operation in all_invalid_columns:
                    all_invalid_columns[operation].extend(invalid_columns[operation])
                else:
                    all_invalid_columns[operation] = invalid_columns[operation]

        unsupported_columns = [col for col in column_supported if not column_supported[col]]
        unsupported_columns.sort()  # helps in catching the columns in lexicographic order

        error_msgs = []
        for operation in sorted(all_invalid_columns):
            all_invalid_columns[operation].sort()  # helps in catching the columns in
            # lexicographic order
            error = MessageCodes.TDMLDF_AGGREGATE_UNSUPPORTED.value.format(
                    ", ".join(all_invalid_columns[operation]), operation)
            error_msgs.append(error)

        if not all(column_supported[oper] for oper in column_supported):
            new_msg = MessageCodes.TDMLDF_AGGREGATE_AGG_DICT_ERR.value.format(", ".join(unsupported_columns))
            error_msgs.append(new_msg)
            msg = Messages.get_message(MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR).format("\n".join(error_msgs))
            raise TeradataMlException(msg, MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR)

        elif len(all_valid_columns) == 0:  # No supported columns in the given list of columns
            raise TeradataMlException(Messages.get_message(
                MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR).format("\n".join(error_msgs)),
                                      MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR)

        aggregate_expr = ", ".join(all_valid_columns)
        return aggregate_expr, all_new_column_names, all_new_column_types

    @staticmethod
    def _construct_sql_expression_for_time_series_aggregations(df, column_names, column_types, func, **kwargs):
        """
        Internal function to create and return the sql expression
        corresponding to given time series function, given column_names and
        column_types.

        Column_types are used to check whether all the datatypes are
        valid types for given operation and throw exception if they
        are not.

        NOTE:
            This function should be used only for time series aggregates.

        PARAMETERS :
            df:
                Required Argument.
                Specifies teradataml DataFrame which is to be used to get the desired
                aggregate column expression.
                Types: teradataml DataFrame

            column_names:
                Required Argument.
                Specifies the column names for which desired aggregate operation is
                to be executed.
                Types: List of strings

            column_types:
                Required Argument.
                Specifies the respective column types for column names.
                Types: List of teradatasqlalchemy types

            func:
                Required Argument.
                Specifies the aggregate function(s) to be applied on teradataml
                DataFrame columns. For Time Series aggregates it is usually a string.
                Types: str

            kwargs:
                Specifies miscellaneous keyword arguments that can be passed to aggregate functions.

        RETURNS :
            a)sql expression as
                1. 'bottom(2, "col1") as "bottom2col1"' if
                        col1 and col2 are the columns in Dataframe and
                        operation is 'bottom'
                etc...
            b) new columns' names (eg min_col1, min_col2 ...)
            c) new columns' types

        RAISES:
            None.

        EXAMPLES:
            colname_to_numvalues = {"col1" : 2, "col2": 3}
            kwargs = {"colname_to_numvalues": colname_to_numvalues}
            aggregate_expr, column_names, column_types = \
                df_utils._construct_sql_expression_for_time_series_aggregations(column_names, column_types,
                                                                                func, **kwargs)

        """

        # eg of column_types: [VARCHAR(length=13), INTEGER(), VARCHAR(length=60), VARCHAR(length=5),
        # FLOAT(precision=0)]

        # eg of types of each column are <class 'teradatasqlalchemy.types.VARCHAR'>,
        # <class 'teradatasqlalchemy.types.INTEGER'>, <class 'teradatasqlalchemy.types.FLOAT'>,
        # <class 'teradatasqlalchemy.types.INTERVAL_MINUTE_TO_SECOND'> etc..

        col_names_and_types = dict(zip(column_names, column_types))
        tdp = preparer(td_dialect)

        select_columns = []
        new_column_names = []
        new_column_types = []
        if func in ["bottom", "bottom with ties", "top", "top with ties"]:
            # Processing for bottom and top.
            # Function name to be used in column aliasing.
            column_alias_func = func.replace(" ", "_")
            bottom_col_val = kwargs["colname_to_numvalues"]
            for column in sorted(list(bottom_col_val.keys())):
                new_col_name = "{2}{0}{1}".format(bottom_col_val[column], column, column_alias_func)
                quoted_parent_column_name = tdp.quote("{0}".format(column))
                quoted_new_column_name = tdp.quote(new_col_name)
                select_columns.append("{0}({1}, {2}) as {3}".format(func, bottom_col_val[column],
                                                                    quoted_parent_column_name, quoted_new_column_name))
                new_column_names.append(new_col_name)
                new_column_types.append(col_names_and_types[column])

        if func == "delta_t":
            # Argument processing for DELTA-T
            new_column_names.append("delta_t_td_timecode")
            quoted_new_column_name = tdp.quote(new_column_names[0])
            new_column_types.append(PERIOD_TIMESTAMP)
            select_columns.append("{0}((WHERE {1}), (WHERE {2})) as {3}".format(func, kwargs["start_condition"],
                                                                                kwargs["end_condition"],
                                                                                quoted_new_column_name))
            
        if func == 'mad':
            # Processing for Median Absolute Deviation.
            # Function name to be used in column aliasing.
            column_alias_func = func.replace(" ", "_")
            bottom_col_val = kwargs["colname_to_numvalues"]
            for column in sorted(list(bottom_col_val.keys())):
                new_col_name = "{2}{0}{1}".format(bottom_col_val[column], column, column_alias_func)
                quoted_parent_column_name = tdp.quote("{0}".format(column))
                quoted_new_column_name = tdp.quote(new_col_name)
                select_columns.append("{0}({1}, {2}) as {3}".format(func, bottom_col_val[column],
                                                                    quoted_parent_column_name, quoted_new_column_name))
                new_column_names.append(new_col_name)
                if type(col_names_and_types[column]) in [DECIMAL, NUMBER]:
                    # If column types is DECIMAL or NUMBER, then output column types should also be same.
                    # Otherwise, it is FLOAT.
                    new_column_types.append(col_names_and_types[column])
                else:
                    new_column_types.append(FLOAT())
                
            if "default_constant_for_columns" in kwargs.keys():
                column_names = kwargs["default_constant_for_columns"]
                column_types = [col_names_and_types[column] for column in column_names]
                if len(column_names) > 0:
                    aggregate_expr, all_new_column_names, all_new_column_types = \
                        DataFrameUtils._construct_sql_expression_for_aggregations(df=df, column_names=column_names,
                                                                                  column_types=column_types, func=func,
                                                                                  )
                    aggregate_expr_default_column_list = [col.strip() for col in aggregate_expr.split(",")]
                    select_columns = select_columns + aggregate_expr_default_column_list
                    new_column_names = new_column_names + all_new_column_names
                    new_column_types = new_column_types + all_new_column_types
                    

        aggregate_expr = ", ".join(select_columns)
        return aggregate_expr, new_column_names, new_column_types
    
    @staticmethod
    def _validate_describe_columns(columns, metaexpr, groupby_column_list):
        """
        Internal function to validate columns provided to describe() are correct or not,
        when DataFrame is output of groupby and groupby_time.
        PARAMETERS:
            columns:
                Optional Argument.
                Specifies the name(s) of columns we are collecting statistics for.
                Types: str ot List of strings (str)
            metaexpr:
                Required Argument.
                Specifies the meta expression for the dataframe.
                Types: _MetaExpression
            groupby_column_list:
                Optional Argument.
                Specifies the group by columns for the dataframe.
                Default Values: None.
                Types: str ot List of strings (str)
        Returns:
            None
        Raises:
            TeradataMLException
        """
        invalid_columns = [_column for _column in groupby_column_list if _column in columns]
        if len(invalid_columns) > 0:
            all_columns = [col.name for col in metaexpr.c]
            valid_columns = [item for item in all_columns if item not in groupby_column_list]
            msg = Messages.get_message(MessageCodes.TDMLDF_AGGREGATE_INVALID_COLUMN). \
                format(", ".join(invalid_columns), 'columns', ", ".join(valid_columns))
            raise TeradataMlException(msg, MessageCodes.TDMLDF_AGGREGATE_INVALID_COLUMN)

    @staticmethod
    def _construct_describe_query(df, columns, metaexpr, percentiles, function_label, groupby_column_list=None,
                                  include=None, is_time_series_aggregate=False, verbose=False, distinct=False,
                                  statistics=None, **kwargs):
        """
        Internal function to create the sql query for describe().

        PARAMETERS :
            df:
                Required Argument.
                Specifies teradataml DataFrame we are collecting statistics for.
                Types: str

            columns:
                Optional Argument.
                Specifies the name(s) of columns we are collecting statistics for.
                Types: str ot List of strings (str)

            metaexpr:
                Required Argument.
                Specifies the meta expression for the dataframe.
                Types: _MetaExpression

            percentiles:
                Required Argument.
                Specifies a list of values between 0 and 1.
                Types: List of floats

            function_label:
                Required Argument.
                Specifies a string value used as the label for the aggregate function column.
                Types: str

            groupby_column_list:
                Optional Argument.
                Specifies the group by columns for the dataframe.
                Default Values: None.
                Types: str ot List of strings (str)

            include:
                Optional Argument.
                Specifies a string that must be "all" or None. If "all", then all columns will be included.
                Otherwise, only numeric columns are used for collecting statistics.
                Default Values: None.
                Types: str

            is_time_series_aggregate:
                Optional Argument.
                Specifies a flag stating whether describe operation is time series aggregate or not.
                Default Values: False.
                Types: bool

            verbose:
                Optional Argument.
                Specifies a flag stating whether DESCRIBE VERBOSE option for time series aggregate is to be
                performed or not.
                Default Values: False.
                Types: bool

            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate rows in calculation or not.
                Default Values: False
                Types: bool

            kwargs:
                Optional Arguments.
                Keyword argument for time series aggregate functions.


        RETURNS :
            A SQL query like:
            select  'count' as "func", cast(count("Feb") as Number) as "Feb", cast(count(accounts) as Number) as accounts from "PYUSER"."salesview"
            union all
            select  'mean' as "func", cast(avg("Feb") as Number) as "Feb", null as accounts from "PYUSER"."salesview"
            union all
            select  'std' as "func", cast(stddev_samp("Feb") as Number) as "Feb", null as accounts from "PYUSER"."salesview"
            union all
            select  'min' as "func", cast(min("Feb") as Number) as "Feb", cast(min(accounts) as Number) as accounts from "PYUSER"."salesview"
            union all
            select  '25%' as "func", percentile_cont(0.25) within group(order by cast("Feb" as Number) ) as "Feb", null as accounts from "PYUSER"."salesview"
            union all
            select  '50%' as "func", percentile_cont(0.5) within group(order by cast("Feb" as Number) ) as "Feb", null as accounts from "PYUSER"."salesview"
            union all
            select  '75%' as "func", percentile_cont(0.75) within group(order by cast("Feb" as Number) ) as "Feb", null as accounts from "PYUSER"."salesview"
            union all
            select  'max' as "func", cast(max("Feb") as Number) as "Feb", cast(max(accounts) as Number) as accounts from "PYUSER"."salesview"

        RAISES:
            TeradataMLException

        EXAMPLES:
            agg_query = \
                df_utils._construct_describe_query("self._table_name", self._metaexpr, [.25, .5, .75], "func", self.groupby_column_list)
            agg_query = \
                df_utils._construct_describe_query("self._table_name", self._metaexpr, [.3, .6], "func", self.groupby_column_list, include="all")

        """
        table_name = df._table_name
        operators = ["count", "mean", "std", "min", "percentile", "max"]
        all_operators = ["count", "unique", "mean", "std", "min", "percentile", "max"]

        if is_time_series_aggregate and verbose:
            # Time Series Aggregate Operators for Vantage DESCRIBE function with verbose
            operators = ['max', 'mean', 'median', 'min', 'mode', "percentile", 'std']
        elif is_time_series_aggregate and not verbose:
            # Time Series Aggregate Operators for Vantage DESCRIBE function.
            operators = ['max', 'mean', 'min', 'std']

        col_names = []
        col_types = []
        sel_agg_stmts = []
        tdp = preparer(td_dialect)
        quoted_function_label = tdp.quote(function_label)

        if include is not None and include == 'all' and not is_time_series_aggregate:
            operators = all_operators

        if include is None and statistics is not None:
            operators = statistics

        table_name, sel_groupby, groupby = DataFrameUtils()._process_groupby_clause(table_name, groupby_column_list,
                                                                                    is_time_series_aggregate, **kwargs)

        for col in metaexpr.c:
            if (include is None and type(col.type) in UtilFuncs()._get_numeric_datatypes()) or include == 'all' or statistics is not None:
                if not(groupby is not None and col.name in groupby_column_list):
                    if columns is None or col.name in columns:
                        col_names.append(col.name)
                        col_types.append(col.type)


        if len(col_names) == 0:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR,
                                     "The DataFrame does not contain numeric columns"),
                MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR)
        for op in operators:
            if op == "percentile":
                for p in percentiles:
                    agg_expr, new_col_names, new_col_types = \
                        DataFrameUtils._construct_sql_expression_for_aggregations(df,
                            col_names, col_types, op, percentile=p, describe_op=True, distinct=distinct,
                            as_time_series_aggregate=is_time_series_aggregate)
                    sel_agg_stmts.append("SELECT \n\t{4} \n\tcast('{0}%' as varchar(6)) as \"{1}\", {2} from {3} ".format(
                        int(p*100), quoted_function_label, agg_expr, table_name, sel_groupby))
            else:
                agg_expr, new_col_names, new_col_types = \
                    DataFrameUtils._construct_sql_expression_for_aggregations(df,
                        col_names, col_types, op, describe_op=True, distinct=distinct,
                        as_time_series_aggregate=is_time_series_aggregate)
                sel_agg_stmts.append("SELECT \n\t{4} \n\tcast('{0}' as varchar(6)) as \"{1}\", \n\t{2} \nfrom \n\t{3} ".format(
                    op, quoted_function_label, agg_expr, table_name, sel_groupby))
        return " \nunion all\n ".join(sel_agg_stmts)

    @staticmethod
    def _process_groupby_clause(table_name, groupby_column_list, is_time_series_aggregate, **kwargs):
        """
        Internal function used to process and generate GROUP BY or GROUP BY TIME clauses required for
        query to be run for describe operation.

        PARAMETERS:
            table_name:
                Required Arguments.
                Specifies table name to be used for forming describe query.
                Types: str

            groupby_column_list:
                Required Arguments.
                Specifies list of column names involved in Group By.
                Types: List of Strings.

            is_time_series_aggregate:
                Required Arguments.
                Specifies a boolean stating whether GROUP BY clause to be formed is for
                Time series aggregate or not.
                Types: bool

            kwargs:
                Optional Arguments.
                Keyword argument for time series aggregate functions.

        RETURNS:
            1. Table Name appended with GROUP BY clause.
            2. Column projection string for GROUP BY columns.
            3. Group By Clause.

        RAISES:
            None.

        EXAMPLES:
            table_name, sel_groupby, groupby = DataFrameUtils()._process_groupby_clause(table_name, groupby_column_list,
                                                                                    is_time_series_aggregate, **kwargs)

        """
        sel_groupby = ""
        grp_by_clause = None

        if is_time_series_aggregate:
            # For time series aggregate timebucket_duration is must so, it'll be always present in kwargs.
            grp_by_clause = "GROUP BY TIME ({0}".format(kwargs['timebucket_duration'])

            # Add columns in value expression to GROUP BY TIME
            if 'value_expression' in kwargs and \
                    kwargs['value_expression'] is not None and \
                    len(kwargs['value_expression']) > 0:
                grp_by_clause = "{0} and {1}".format(grp_by_clause, ", ".join(kwargs['value_expression']))

            # Complete the parenthesis for GROUP BY TIME
            grp_by_clause = "{0})".format(grp_by_clause)

            # Add Time code column information.
            if 'timecode_column' in kwargs and \
                    kwargs['timecode_column'] is not None and \
                    len(kwargs['timecode_column']) > 0:
                if 'sequence_column' in kwargs and \
                        kwargs['timecode_column'] is not None and \
                        len(kwargs['timecode_column']) > 0:
                    grp_by_clause = "{0} USING TIMECODE({1}, {2})".format(grp_by_clause, kwargs['timecode_column'],
                                                                          kwargs['sequence_column'])
                else:
                    grp_by_clause = "{0} USING TIMECODE({1})".format(grp_by_clause, kwargs['timecode_column'])

            # Add Fill inforamtion
            if 'fill' in kwargs and kwargs['fill'] is not None and len(kwargs['fill']) > 0:
                grp_by_clause = "{0} FILL({1})".format(grp_by_clause, kwargs['fill'])

        else:
            if groupby_column_list is not None:
                grp_by_clause = "GROUP BY {0}".format(",".join(groupby_column_list))

        if grp_by_clause is not None:
            table_name = "{0} \n{1}".format(table_name, grp_by_clause)
            tdp = preparer(td_dialect)
            for g in groupby_column_list:
                if is_time_series_aggregate:
                    if g == "TIMECODE_RANGE":
                        g = "$TD_TIMECODE_RANGE"

                    if "GROUP BY TIME" in g:
                        g = "$TD_GROUP_BY_TIME"

                quoted_name = tdp.quote(g)
                sel_groupby += "{0}, ".format(quoted_name)

        return table_name, sel_groupby, grp_by_clause

    @staticmethod
    def _get_column_names_and_types_from_metaexpr(metaexpr):
        """
        Internal function to return column names and respective types
        given _metaexpr.

        PARAMETERS:
            metaexpr:
                Required Argument.
                Dataframe's metaexpr. It is used to get column names and types.
                Types: MetaExpression

        RETURNS:
            Two lists - one for column names and another for column types

        RAISES:
            None

        EXAMPLES:
            dfUtils._get_column_names_and_types_from_metaexpr(
                                                    df._metaexpr)
        """
        # Constructing New Column names & Types for selected columns ONLY using Parent _metaexpr
        col_names = []
        col_types = []
        for c in metaexpr.c:
            col_names.append(c.name)
            col_types.append(c.type)

        return col_names, col_types

    @staticmethod
    def _insert_all_from_table(to_table_name, from_table_name, column_list, to_schema_name=None,
                               from_schema_name=None, temporary=False):
        """
        Inserts all records from one table into the second, using columns ordered by column list.

        PARAMETERS:
            to_table_name - String specifying name of the SQL Table to insert to.
            from_table_name - String specifying name of the SQL Table to insert from.
            column_list - List of strings specifying column names used in the insertion.
            to_schema_name - Name of the database schema to insert table data into.
            from_schema_name - Name of the database schema to insert table data from.
            temporary - Specifies whether to create Vantage tables as permanent or volatile.
                        Default: False
                        Note: When True:
                                1. volatile Tables are created, and
                                2. schema_name is ignored.
                        When False, permanent tables are created.
        RETURNS:
            None

        RAISES:
            Database error if an error occurred while executing the insert command.

        EXAMPLES:
            df_utils._insert_all_from_table('table1_name', 'table2_name', ['col1', 'col2', 'col3'])
        """
        tdp = preparer(td_dialect)

        # Construct INSERT command.
        column_order_string = ', '.join([tdp.quote("{0}".format(element)) for element in column_list])

        # Generate full name of the destination table.
        if to_schema_name:
            full_to_table_name = tdp.quote(to_schema_name) + "." + tdp.quote(to_table_name)
        elif temporary:
            full_to_table_name = tdp.quote(to_table_name)
        else:
            full_to_table_name = tdp.quote(_get_current_databasename()) + "." + tdp.quote(
                to_table_name)

        # Generate full name of source table.
        if from_schema_name:
            full_from_table_name = tdp.quote(from_schema_name) + "." + tdp.quote(from_table_name)
        else:
            full_from_table_name = tdp.quote(_get_current_databasename()) + "." + tdp.quote(
                from_table_name)

        insert_sql = SQLBundle._build_insert_from_table_query(full_to_table_name,
                                                              full_from_table_name,
                                                              column_order_string)
        # Execute INSERT command.
        return UtilFuncs._execute_ddl_statement(insert_sql)

    @staticmethod
    def _dataframe_has_column(data, column):
        """
        Function to check whether column names in columns are present in given dataframe or not.
        This function is used currently only for Analytics wrappers.

        PARAMETERS:
            data - teradataml DataFrame to check against for column existence.
            column - Column name (a string).

        RAISES:
            None

        EXAMPLES:
            DataFrameUtils._dataframe_has_column(data, col)
        """
        if column in [c.name for c in data._metaexpr.c]:
            return True

        return False

    @staticmethod
    def _get_row_count(table_name):
        """
        Function to return the row count of a teradataml Dataframe.
        This function is used currently to determine the shape/size of a dataframe.

        PARAMETERS:
            table_name - Name of the table to get the row count for.

        RAISES:
            TeradataMlException (TDMLDF_INFO_ERROR)

        EXAMPLES:
            DataFrameUtils._get_row_count(table_name)
        """
        # Construct COUNT(*) Query
        try:
            row_count_query = SQLBundle._build_nrows_print_query(table_name)
            res = execute_sql(row_count_query)
            return res.fetchone()[0]

        except TeradataMlException:
            raise

        except Exception as err:
            # TODO Better handle the level of information being presented to the user with logging
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_INFO_ERROR) + str(err),
                                      MessageCodes.TDMLDF_INFO_ERROR) from err

    @staticmethod
    def _get_scalar_value(table_name):
        """
        Function to return the the only 1x1 (scalar) value from a teradataml Dataframe.

        PARAMETERS:
            table_name - Name of the table to get the value from.

        RAISES:
            TeradataMlException (TDMLDF_INFO_ERROR)

        EXAMPLES:
            DataFrameUtils._get_scalar_value(table_name)
        """
        # Construct the base Query
        try:
            select_query = SQLBundle._build_base_query(table_name)
            res = execute_sql(select_query)
            return res.fetchone()[0]

        except TeradataMlException:
            raise

        except Exception as err:
            # TODO Better handle the level of information being presented to the user with logging
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_INFO_ERROR) + str(err),
                                      MessageCodes.TDMLDF_INFO_ERROR) from err

    @staticmethod
    def _get_sorted_nrow(df, n, sort_col, asc=True):
        """
        Internal Utility function that returns a teradataml DataFrame containing n rows
        of the DataFrame. The Dataframe is sorted on the index column or the first column
        if there is no index column.

        PARAMETERS:
            df:  teradataml DataFrame
            n:   Specifies the number of rows to select.
                 Type: int
            sort_col: The column to sort on.
                 Type: str
            asc: (optional) - Specifies sort order.
                 If True, sort in ascending order.
                 If False, sort in descending order.
                 The default value is True.
                 Type: boolean

        RETURNS:
            teradataml DataFrame

        EXAMPLES:
            DataFrameUtils._get_sorted_nrow(df, 10)
            DataFrameUtils._get_sorted_nrow(df, 20, asc=True)
            DataFrameUtils._get_sorted_nrow(df, 30, asc=False)

        """
        #TODO: implement and use this in teradatasqlalchemy
        tdp = preparer(td_dialect)
        aed_utils = AedUtils()

        sort_order = "asc"
        if not asc:
            sort_order = "desc"

        quoted_cols = [tdp.quote(c) for c in df.columns]
        sel_cols_str = ",".join(quoted_cols)
        sel_row_num = "row_number() over (order by \"{0}\" {1}) - 1 as tdml_row_num, {2}".format(sort_col, sort_order, sel_cols_str)
        filter_str = "tdml_row_num < {0}".format(n)
        sel_nodeid = aed_utils._aed_select(df._nodeid, sel_row_num)
        fil_nodeid = aed_utils._aed_filter(sel_nodeid, filter_str)
        sel2_nodeid = aed_utils._aed_select(fil_nodeid, sel_cols_str)
        col_names, col_types = __class__._get_column_names_and_types_from_metaexpr(df._metaexpr)
        new_metaexpr = UtilFuncs._get_metaexpr_using_columns(df._nodeid, zip(col_names, col_types),
                                                             datalake=df._metaexpr.datalake)
        # Call the function from_node from appropriate class either DataFrame or GeoDataFrame
        new_df = df.__class__._from_node(sel2_nodeid, new_metaexpr, df._index_label)
        new_df._orderby = df._orderby
        new_df._metaexpr._n_rows = n
        return new_df

    @staticmethod
    def _get_database_names(connection, schema_name):
        """
        Function to return a list valid of database names for a given sqlalchemy connection.
        This function is used to determine whether the database used is valid in user APIs such as copy_to_sql.

        PARAMETERS:
            connection:     Required Argument.
                            A SQLAlchemy connection object.

            schema_name:   Required Argument
                            String specifying the requested schema name.

        RAISES:
            TeradataMlException (TDMLDF_INFO_ERROR)

        EXAMPLES:
            DataFrameUtils._get_database_names(get_connection(), schema_name)
        """
        #TODO: implement and use this in teradatasqlalchemy
        table_obj = table('databasesV', column('databasename'), schema='dbc')
        stmt = select(text(str(func.lower(table_obj.c.databasename)) + ' as databasename')).where(
            text('databasename (NOT CASESPECIFIC) = {} (NOT CASESPECIFIC)'.format(':schema_name')))
        stmt = text(str(stmt))
        stmt = stmt.bindparams(schema_name=schema_name)
        res = connection.execute(stmt).fetchall()
        return [name.databasename for name in res]

    @staticmethod
    def _get_common_parent_df_from_dataframes(dfs):
        """
        Internal function to return common parent dataframe from given list of dataframes.
        """
        from teradataml import DataFrame, in_schema
        aed_utils = AedUtils()
        if len(dfs) == 1:
            operation = aed_utils._aed_get_node_query_type(dfs[0]._nodeid)
            if operation in ["table", "assign"]:
                # Assign might have removed some columns and if it is only one dataframe,
                # then return the same dataframe.
                # Return the same dataframe if it is DataFrame object from table.
                return dfs[0]

            # If select node or any other node, then get the parent node and execute it.
            pids = aed_utils._aed_get_parent_nodeids(dfs[0]._nodeid)
            if not aed_utils._aed_is_node_executed(pids[0]):
                _ = DataFrameUtils._execute_node_return_db_object_name(pids[0])

            tab_name_first = aed_utils._aed_get_source_tablename(pids[0])

            db_schema = UtilFuncs._extract_db_name(tab_name_first)
            db_table_name = UtilFuncs._extract_table_name(tab_name_first)
            if dfs[0]._metaexpr.datalake:
                return DataFrame(in_schema(db_schema, db_table_name, dfs[0]._metaexpr.datalake))

            if db_schema:
                return DataFrame(in_schema(db_schema, db_table_name))

            return DataFrame(db_table_name)

        pids_first = None
        parent_df = None
        for i in range(len(dfs)):
            pids = aed_utils._aed_get_parent_nodeids(dfs[i]._nodeid)

            if parent_df is None:
                if not aed_utils._aed_is_node_executed(pids[0]):
                    _ = DataFrameUtils._execute_node_return_db_object_name(pids[0])

                tab_name_first = aed_utils._aed_get_source_tablename(pids[0])

                db_schema = UtilFuncs._extract_db_name(tab_name_first)
                db_table_name = UtilFuncs._extract_table_name(tab_name_first)

                if dfs[i]._metaexpr.datalake:
                    parent_df = DataFrame(in_schema(db_schema, db_table_name, dfs[i]._metaexpr.datalake))
                elif db_schema:
                    parent_df = DataFrame(in_schema(db_schema, db_table_name))
                else:
                    parent_df = DataFrame(db_table_name)
                pids_first = pids
            else:
                if pids_first != pids:
                    raise TeradataMlException(Messages.get_message(MessageCodes.DFS_NO_COMMON_PARENT),
                                            MessageCodes.DFS_NO_COMMON_PARENT)

        return parent_df

    @staticmethod
    def _get_sqlalchemy_type_from_str(td_type):
        """
        Function to get teradatasqlalchemy type from string representation of that type.

        PARAMETERS:
            td_type:
                Required Argument.
                Specifies string representation of teradatasqlalchemy type.
                Types: str

        RAISES:
            ValueError

        EXAMPLES:
            >>> dt = DataFrameUtils._get_sqlalchemy_type_from_str("DECIMAL(4,4)")
            >>> dt
            DECIMAL(precision=4, scale=4)
            >>> type(dt)
            teradatasqlalchemy.types.DECIMAL

            >>> dt = DataFrameUtils._get_sqlalchemy_type_from_str("VARCHAR(32000) CHARACTER SET UNICODE")
            >>> dt
            VARCHAR(length=32000, charset='UNICODE')
            >>> type(dt)
            teradatasqlalchemy.types.VARCHAR
        """
        # 4 groups of pattern:
        # 1. Type name
        # 2. Comma separated parameters enclosed in parentheses
        # 3. Comma separated parameters without parenthesis 
        # 4. Remaining string
        pattern = r"([A-Z0-9_]+)(\((.*)\))?(.*)"

        m = re.match(pattern, td_type)
        td_str_type = m.group(1)
        td_str_params = m.group(3)
        td_str_remain = m.group(4)

        if m is None or td_str_type not in _DtypesMappers.DATALAKE_STR_to_TDSQLALCHEMY_DATATYPE_MAPPER.keys():
            raise ValueError("Invalid Teradata type: {} from datalake".format(td_type))

        if td_str_type in ["VARCHAR", "CHAR"]:
            # If VARCHAR or CHAR, extract, length and charset from string.
            length = int(td_str_params.split(",")[0])
            charset = td_str_remain.strip().split(" ")[2]
            return _DtypesMappers.DATALAKE_STR_to_TDSQLALCHEMY_DATATYPE_MAPPER[td_str_type]\
                (length=length, charset=charset)
        
        if td_str_type in ["BLOB"]:
            # Ignoring the charset as BLOB does not have it.
            # If BLOB, extract length from string.
            length = int(td_str_params.split(",")[0])
            return _DtypesMappers.DATALAKE_STR_to_TDSQLALCHEMY_DATATYPE_MAPPER[td_str_type]\
                (length=length)

        if td_str_type in ["DECIMAL"]:
            # If DECIMAL, extract precision and scale from string.
            args = td_str_params.split(",")
            return _DtypesMappers.DATALAKE_STR_to_TDSQLALCHEMY_DATATYPE_MAPPER[td_str_type]\
                (precision=int(args[0]), scale=int(args[1]))

        # TODO: Test for other data types once OTF team finalize all data types.
        return _DtypesMappers.DATALAKE_STR_to_TDSQLALCHEMY_DATATYPE_MAPPER[td_str_type]()

    @staticmethod
    def _get_datalake_table_columns_info(schema, table_name, datalake, use_dialect=False):
        """
        Function to get column names and corresponding teradatasqlalchemy types
        of a datalake table using results of 'help table <datalake>.<db_name>.<table_name>'
        SQL query.

        PARAMETERS:
            schema:
                Required Argument.
                Specifies name of schema.
                Types: str

            table_name:
                Required Argument.
                Specifies name of table.
                Types: str

            datalake:
                Required Argument.
                Specifies name of datalake.
                Types: str

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> DataFrameUtils._get_datalake_table_columns_info(table_name = 'sales',
            ...                                                 schema='otftestdb',
            ...                                                 datalake='datalake_iceberg_glue')
            (['id', 'masters', 'gpa', 'stats', 'programming', 'admitted'],
             [INTEGER(),
              VARCHAR(length=2000, charset='UNICODE'),
              FLOAT(),
              VARCHAR(length=2000, charset='UNICODE'),
              VARCHAR(length=2000, charset='UNICODE'),
              INTEGER()])
        """
        col_names = []
        col_types = []
        if not use_dialect:
            # Get the column information from the strings type.
            prepared = preparer(td_dialect())
            sqlbundle = SQLBundle()
            full_tbl_name = '{}.{}.{}'.format(prepared.quote(datalake),
                                              prepared.quote(schema),
                                              prepared.quote(table_name))
            help_table_sql = sqlbundle._get_sql_query(SQLConstants.SQL_HELP_TABLE).format(full_tbl_name)

            cur = execute_sql(help_table_sql)
            td_types_col_index = -1

            for i, col_metadata in enumerate(cur.description):
                # Help Table returns column names and
                # corresponding IcebergType, TeradataInternalType,
                # TeradataType. We need to extract column index for
                # 'TeradataType' column.
                if col_metadata[0].lower() in ['teradatatype', 'Type']:
                    td_types_col_index = i

            if td_types_col_index > -1:
                for col_info in cur.fetchall():
                    col_names.append(col_info[0])
                    col_types.append(DataFrameUtils._get_sqlalchemy_type_from_str(col_info[td_types_col_index]))
            else:
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_CREATE_FAIL),
                                          MessageCodes.TDMLDF_CREATE_FAIL)
        else:
            new_kwarg = get_connection().dialect.__class__.__name__ + "_datalake"
            all_col_info = get_connection().dialect.get_columns(connection=get_connection(),
                                                                table_name=table_name,
                                                                schema=schema,
                                                                table_only=True,
                                                                **{new_kwarg: datalake})
            for col_dict in all_col_info:
                col_names.append(col_dict.get('name', col_dict.get('Column Name')))
                col_types.append(col_dict.get('type', col_dict.get('Type')))

        return col_names, col_types

    @staticmethod
    def check_otf_dataframe():
        """Decorator for validating if DataFrame is created on OTF table or not and throw error."""
        def decorator(method):
            def wrapper(self, *args, **kwargs):
                if not self._datalake:
                    attr = getattr(type(self), method.__name__, None)
                    caller_name = method.__name__ + '()'
                    if isinstance(attr, property):
                        caller_name = method.__name__
                    raise TeradataMlException(Messages.get_message(MessageCodes.OTF_TABLE_REQUIRED,
                                                                   caller_name),
                                              MessageCodes.UNSUPPORTED_OPERATION)

                return method(self, *args, **kwargs)

            return wrapper

        return decorator
