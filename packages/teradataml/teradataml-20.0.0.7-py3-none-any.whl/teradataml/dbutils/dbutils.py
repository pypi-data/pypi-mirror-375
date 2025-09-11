"""
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rameshchandra.d@teradata.com
Secondary Owner: sanath.vobilisetty@teradata.com

teradataml db utilities
----------
A teradataml database utility functions provide interface to Teradata Vantage common tasks such as drop_table, drop_view, create_table etc.
"""
import concurrent.futures
import enum
import json
import os
import re
import shutil
import tempfile
from datetime import datetime
import functools

import pandas as pd
from sqlalchemy import (CheckConstraint, Column, ForeignKeyConstraint,
                        MetaData, PrimaryKeyConstraint, Table,
                        UniqueConstraint)
from sqlalchemy.sql.functions import Function
from teradatasql import OperationalError
from teradatasqlalchemy.dialect import TDCreateTablePost as post
from teradatasqlalchemy.dialect import dialect as td_dialect
from teradatasqlalchemy.dialect import preparer

import teradataml.dataframe as tdmldf
from teradataml.common.constants import (SessionParamsPythonNames,
                                         SessionParamsSQL, SQLConstants,
                                         TableOperatorConstants,
                                         TeradataTableKindConstants)
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.sqlbundle import SQLBundle
from teradataml.common.utils import UtilFuncs
from teradataml.context import context as tdmlctx
from teradataml.options.configure import configure
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators


@collect_queryband(queryband='DrpTbl')
def db_drop_table(table_name, schema_name=None, suppress_error=False,
                  datalake_name=None, purge=None):
    """
    DESCRIPTION:
        Drops the table from the given schema.

    PARAMETERS:
        table_name:
            Required Argument
            Specifies the table name to be dropped.
            Types: str

        schema_name:
            Optional Argument
            Specifies schema of the table to be dropped. If schema is not specified, function drops table from the
            current database.
            Default Value: None
            Types: str

        suppress_error:
            Optional Argument
            Specifies whether to raise error or not.
            Default Value: False
            Types: bool

        datalake_name:
            Optional Argument
            Specifies name of the datalake to drop table from.
            Note:
                 "schema_name" must be provided while using this argument.
            Default Value: None
            Types: str

        purge:
            Optional Argument
            Specifies whether to use purge clause or not while dropping datalake table.
            It is only applicable when "datalake_name" argument is used. When "datalake_name" is specified,
            but "purge" is not specified, data is purged by default.
            Default Value: None
            Types: bool

    RETURNS:
        True - if the operation is successful.

    RAISES:
        TeradataMlException - If the table doesn't exist.

    EXAMPLES:
        >>> load_example_data("dataframe", "admissions_train")

        # Example 1: Drop table in current database.
        >>> db_drop_table(table_name = 'admissions_train')

        # Example 2: Drop table from the given schema.
        >>> db_drop_table(table_name = 'admissions_train', schema_name = 'alice')

        #Example 3: Drop a table from datalake and purge the data.
        >>> db_drop_table(table_name = 'datalake_table', schema_name = 'datalake_db',
        ...               datalake_name='datalake', purge=True)

    """
    # Argument validations
    awu_matrix = []
    awu_matrix.append(["schema_name", schema_name, True, (str), True])
    awu_matrix.append(["table_name", table_name, False, (str), True])
    awu_matrix.append(["datalake_name", datalake_name, True, (str), True])
    awu_matrix.append(["purge", purge, True, (bool, type(None)), True])
    awu_matrix.append(["suppress_error", suppress_error, True, (bool)])
    # Validate argument types
    _Validators._validate_function_arguments(awu_matrix)

    # Process datalake related arguments.
    purge_clause = None
    if datalake_name is not None:
        if schema_name is None:
            err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "schema_name",
                                        "datalake_name")
            raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

        if purge is False:
            purge_clause = "NO PURGE"
        else:
            purge_clause = "PURGE ALL"

    # Joining view and schema names in the format "schema_name"."view_name"
    table_name = _get_quoted_object_name(schema_name, table_name, datalake_name)

    try:
        return UtilFuncs._drop_table(table_name, purge_clause=purge_clause)
    except (TeradataMlException, OperationalError):
        if suppress_error:
            pass
        else:
            raise
    except Exception as err:
        if suppress_error:
            pass
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.DROP_FAILED, "table",
                                                           table_name),
                                      MessageCodes.DROP_FAILED) from err


@collect_queryband(queryband='DrpVw')
def db_drop_view(view_name, schema_name=None, suppress_error=False):
    """
    DESCRIPTION:
        Drops the view from the given schema.

    PARAMETERS:
        view_name:
            Required Argument
            Specifies view name to be dropped.
            Types: str

        schema_name:
            Optional Argument
            Specifies schema of the view to be dropped. If schema is not specified, function drops view from the current
            database.
            Default Value: None
            Types: str

        suppress_error:
            Optional Argument
            Specifies whether to raise error or not.
            Default Value: False
            Types: bool

    RETURNS:
        True - if the operation is successful.

    RAISES:
        TeradataMlException - If the view doesn't exist.

    EXAMPLES:
        # Create a view.
        >>> execute_sql("create view temporary_view as (select 1 as dummy_col1, 2 as dummy_col2);")

        # Drop view in current schema.
        >>> db_drop_view(view_name = 'temporary_view')

        # Drop view from the given schema.
        >>> db_drop_view(view_name = 'temporary_view', schema_name = 'alice')

        # Drop view by suppressing errors.
        >>> db_drop_view(view_name = 'temporary_view', suppress_error = True)
    """
    # Argument validations
    awu_matrix = []
    awu_matrix.append(["schema_name", schema_name, True, (str), True])
    awu_matrix.append(["view_name", view_name, False, (str), True])
    awu_matrix.append(["suppress_error", suppress_error, True, (bool)])

    # Validate argument types
    _Validators._validate_function_arguments(awu_matrix)

    # Joining view and schema names in the format "schema_name"."view_name"
    view_name = _get_quoted_object_name(schema_name, view_name)

    try:
        return UtilFuncs._drop_view(view_name)
    except (TeradataMlException, OperationalError):
        if suppress_error:
            pass
        else:
            raise
    except Exception as err:
        if suppress_error:
            pass
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.DROP_FAILED, "view",
                                                           view_name),
                                      MessageCodes.DROP_FAILED) from err


@collect_queryband(queryband='LstTbls')
def db_list_tables(schema_name=None, object_name=None, object_type='all', datalake_name=None):
    """
    DESCRIPTION:
        Lists the Vantage objects(table/view) names for the specified schema name.

    PARAMETERS:
        schema_name:
            Optional Argument.
            Specifies the name of schema in the database. If schema is not specified, function lists tables/views from
            the current database.
            Default Value: None
            Types: str

        object_name:
            Optional Argument.
            Specifies a table/view name or pattern to be used for filtering them from the database.
            Pattern may contain '%' or '_' as pattern matching characters.
            - '%' represents any string of zero or more arbitrary characters. Any string of characters is acceptable as
              a replacement for the percent.
            - '_' represents exactly one arbitrary character. Any single character is acceptable in the position in
              which the underscore character appears.
            Note:
                * If '%' is specified in 'object_name', then the '_' character is not evaluated for an arbitrary character.
            Default Value: None
            Types: str
            Example:
                1. '%abc' will return all table/view object names starting with any character and ending with abc.
                2. 'a_c' will return all table/view object names starting with 'a', ending with 'c' and has length of 3.

        object_type:
            Optional Argument.
            Specifies object type to apply the filter. Valid values for this argument are 'all','table','view',
            'volatile','temp'.
                * all - List all the object types.
                * table - List only tables.
                * view - List only views.
                * volatile - List only volatile tables.
                * temp - List all teradataml temporary objects created in the specified database.
            Default Value: 'all'
            Types: str

        datalake_name:
            Optional Argument.
            Specifies the name of datalake to list tables from.
            Note:
                "schema_name" must be provided while using this argument.
            Default Value: None
            Types: str

    RETURNS:
        Pandas DataFrame

    RAISES:
        TeradataMlException - If the object_type argument is provided with invalid values.
        OperationalError    - If any errors are raised from Vantage.

    EXAMPLES:
        # Example 1: List all object types in the default schema
        >>> load_example_data("dataframe", "admissions_train")
        >>> db_list_tables()

        # Example 2: List all the views in the default schema
        >>> execute_sql("create view temporary_view as (select 1 as dummy_col1, 2 as dummy_col2);")
        >>> db_list_tables(None , None, 'view')

        # Example 3: List all the object types in the default schema whose names begin with 'abc' followed by any number
        # of characters in the end.
        >>> execute_sql("create view abcd123 as (select 1 as dummy_col1, 2 as dummy_col2);")
        >>> db_list_tables(None, 'abc%', None)

        # Example 4: List all the tables in the default schema whose names begin with 'adm' followed by any number of
        # characters and ends with 'train'.
        >>> load_example_data("dataframe", "admissions_train")
        >>> db_list_tables(None, 'adm%train', 'table')

        # Example 5: List all the views in the default schema whose names begin with any character but ends with 'abc'
        >>> execute_sql("create view view_abc as (select 1 as dummy_col1, 2 as dummy_col2);")
        >>> db_list_tables(None, '%abc', 'view')

        # Example 6: List all the volatile tables in the default schema whose names begin with 'abc' and ends with any
        # arbitrary character and has a length of 4
        >>> execute_sql("CREATE volatile TABLE abcd(col0 int, col1 float) NO PRIMARY INDEX;")
        >>> db_list_tables(None, 'abc_', 'volatile')

        # Example 7: List all the temporary objects created by teradataml in the default schema whose names begins and
        # ends with any number of arbitrary characters but contains 'filter' in between.
        >>> db_list_tables(None, '%filter%', 'temp')

        # Example 8: List all the tables in datalake's database.
        >>> db_list_tables(schema_name='datalake_db_name', datalake_name='datalake_name')
    """
    if tdmlctx.get_connection() is None:
        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_CONTEXT_CONNECTION),
                                  MessageCodes.INVALID_CONTEXT_CONNECTION)

    # Argument validations
    awu_matrix = []
    awu_matrix.append(["schema_name", schema_name, True, (str), True])
    awu_matrix.append(["object_name", object_name, True, (str), True])
    permitted_object_types = [TeradataTableKindConstants.ALL.value,
                              TeradataTableKindConstants.TABLE.value,
                              TeradataTableKindConstants.VIEW.value,
                              TeradataTableKindConstants.VOLATILE.value,
                              TeradataTableKindConstants.TEMP.value]
    awu_matrix.append(["object_type", object_type, True, (str), True, permitted_object_types])
    awu_matrix.append(["datalake_name", datalake_name, True, (str), True])
    # Validate argument types
    _Validators._validate_function_arguments(awu_matrix)

    # 'schema_name' must be provided while using 'datalake_name'.
    _Validators._validate_dependent_argument(dependent_arg='datalake_name',
                                             dependent_arg_value=datalake_name,
                                             independent_arg='schema_name',
                                             independent_arg_value=schema_name)

    try:
        return _get_select_table_kind(schema_name, object_name, object_type, datalake_name)
    except TeradataMlException:
        raise
    except OperationalError:
        raise
    except Exception as err:
        raise TeradataMlException(Messages.get_message(MessageCodes.LIST_DB_TABLES_FAILED),
                                  MessageCodes.LIST_DB_TABLES_FAILED) from err


def _convert_sql_search_string_to_regex(sql_str):
    """Internal function to convert SQL string matching patterns to python regex."""
    if sql_str:
        # sql_str[1:-1] Removes single quotes from sql_str.
        sql_str = sql_str[1:-1]

        # If '%' is specified in 'sql_str',
        # then the '_' character is not evaluated for an arbitrary character.
        if '%' in sql_str:
            # Replace % with .* if not preceded by a backslash.
            sql_str = re.sub(r'(?<!\\)%', r'.*', sql_str, flags=re.IGNORECASE)
            # Remove the escape character for the replacements.
            sql_str = sql_str.replace(r'\%', '%')
        else:
            # Replace _ with . if not preceded by a backslash.
            sql_str = re.sub(r'(?<!\\)_', r'.', sql_str, flags=re.IGNORECASE)
            # Remove the escape character for the replacements.
            sql_str = sql_str.replace(r'\_', '_')

        # Add boundaries if the string doesn't start or end with '.*' i.e. SQL '%'.
        if not sql_str.startswith('.*'):
            sql_str = '^' + sql_str  # Anchor to the start of the string.
        if not sql_str.endswith('.*'):
            sql_str = sql_str + '$'  # Anchor to the end of the string.
    return sql_str


def _get_select_table_kind(schema_name, table_name, table_kind, datalake_name):
    """
    Get the list of the table names from the specified schema name and datalake.

    PARAMETERS:
        schema_name - The Name of schema in the database. The default value is the current database name.
        table_name -  The pattern to be used to filtering the table names from the database.
                      The table name argument can contain '%' as pattern matching character.For example '%abc'
                      will return all table names starting with any characters and ending with abc.
        table_kind -  The table kind to apply the filter. The valid values are 'all','table','view','volatile','temp'.
                      all - list the all the table kinds.
                      table - list only tables.
                      view - list only views.
                      volatile - list only volatile temp.
                      temp - list all teradata ml temporary objects created in the specified database.
        datalake_name - The name of datalake to search schema in.
    RETURNS:
        Panda's DataFrame - if the operation is successful.

    RAISES:
        Database error if an error occurred while executing query.

    EXAMPLES:
        _get_select_table_kind("schema_name", "table_name", "all")
    """
    object_name_str = None
    if table_name is not None:
        object_name_str = "'{0}'".format(table_name)
    object_table_kind = None

    # Tablekind:
    # 'O' - stands for Table with no primary index and no partitioning
    # 'Q' - stands for Queue table
    # 'T' - stands for a Table with a primary index or primary AMP index, partitioning, or both.
    #       Or a partitioned table with NoPI
    # 'V' - stands for View
    if (table_kind == TeradataTableKindConstants.TABLE.value):
        object_table_kind = ['O', 'Q', 'T']
    elif (table_kind == TeradataTableKindConstants.VIEW.value):
        object_table_kind = ['V']
    elif (table_kind == TeradataTableKindConstants.TEMP.value):
        if table_name is None:
            object_name_str = "'{0}'".format(TeradataTableKindConstants.ML_PATTERN.value)
        else:
            object_name_str = "'{0}','{1}'".format(table_name,
                                                   TeradataTableKindConstants.ML_PATTERN.value)
    else:
        object_table_kind = ['O', 'Q', 'T', 'V']

    if datalake_name is None:
        # Check the schema name.
        if schema_name is None:
            schema_name = tdmlctx._get_current_databasename()

        # Create an empty dataframe with desired column name.
        pddf = pd.DataFrame(columns=[TeradataTableKindConstants.REGULAR_TABLE_NAME.value])

        # Check the table kind.
        if table_kind != TeradataTableKindConstants.VOLATILE.value:
            if object_table_kind is not None:
                object_table_kind = ', '.join([f"'{value}'" for value in object_table_kind])
            query = SQLBundle._build_select_table_kind(schema_name, object_name_str, object_table_kind)
            pddf = pd.read_sql(query, tdmlctx.get_connection())

        # Check if all table kind or volatile table kind is requested.
        # If so,add volatile tables to the pddf.
        if table_kind == TeradataTableKindConstants.ALL.value or \
                table_kind == TeradataTableKindConstants.VOLATILE.value:
            # Create list of volatile tables.
            try:
                vtquery = SQLBundle._build_help_volatile_table()
                vtdf = pd.read_sql(vtquery, tdmlctx.get_connection())
                if not vtdf.empty:
                    # Volatile table query returns different column names.
                    # So, rename its column names to match with normal
                    # 'SELECT TABLENAME FROM DBC.TABLESV' query results.
                    columns_dict = {TeradataTableKindConstants.VOLATILE_TABLE_NAME.value:
                                        TeradataTableKindConstants.REGULAR_TABLE_NAME.value}
                    vtdf.rename(columns=columns_dict, inplace=True)
                    # Volatile table names might contain leading whitespaces. Remove those.
                    vtdf[TeradataTableKindConstants.REGULAR_TABLE_NAME.value] = vtdf[TeradataTableKindConstants.REGULAR_TABLE_NAME.value].str.strip()
                    # Filter volatile tables using table name pattern.
                    if object_name_str and (object_name_str := _convert_sql_search_string_to_regex(object_name_str)):
                        name_filter = vtdf[TeradataTableKindConstants.REGULAR_TABLE_NAME.value].str.strip().str.match(
                            object_name_str,
                            na=False,
                            flags=re.IGNORECASE)
                        vtdf = vtdf[name_filter]
                    # Concat existing list with volatile tables list.
                    frames = [pddf, vtdf[[TeradataTableKindConstants.REGULAR_TABLE_NAME.value]]]
                    pddf = pd.concat(frames)
                    pddf.reset_index(drop=True, inplace=True)
            except Exception as err:
                # No volatile tables exist.
                pass
        else:
            return pddf
    else:
        # TODO: when OTF team enables VSD support for datalake tables
        #  with epic: https://teradata-pe.atlassian.net/browse/OTF-454,
        #  this can be changed to use VSD_tablesV table which is
        #  similar to DBC.TABLESV.
        # For datalake tables' information we need to use help database and
        # then apply filter for table kind and table substring.
        # We can't use select from DBC.TABLESV.
        sqlbundle = SQLBundle()
        help_db_sql = sqlbundle._get_sql_query(SQLConstants.SQL_HELP_DATABASE)
        pddf = pd.read_sql(help_db_sql.format(_get_quoted_object_name(schema_name=datalake_name,
                                                                      object_name=schema_name)),
                           tdmlctx.td_connection.connection)

        if object_name_str:
            object_name_str = _convert_sql_search_string_to_regex(object_name_str)
            if object_name_str:
                name_filter = pddf['Table/View/Macro Name'].str.strip().str.match(object_name_str, na=False,
                                                                                  flags=re.IGNORECASE)
                pddf = pddf[name_filter]

        if object_table_kind is not None:
            object_filter = pddf['Kind'].isin(object_table_kind)
            pddf = pddf[object_filter]

        columns_dict = {'Table/View/Macro Name':
                            TeradataTableKindConstants.REGULAR_TABLE_NAME.value}
        pddf.rename(columns=columns_dict, inplace=True)

    # Return only filtered columns.
    if not pddf.empty:
        return pddf[[TeradataTableKindConstants.REGULAR_TABLE_NAME.value]]
    else:
        return pd.DataFrame()


def _execute_transaction(queries):
    """
    Internal function to execute the query or list of queries passed, as one transaction.

    PARAMETERS:
        queries:
            Required argument.
            Specifies a query or a list of queries to be executed as a single transaction.
            Types: str or list of str

    RAISES:
        Exception

    RETURNS:
        None.

    EXAMPLES:
        >>> _execute_transaction([query1, query2])
    """
    auto_commit_off = "{fn teradata_nativesql}{fn teradata_autocommit_off}"
    auto_commit_on = "{fn teradata_nativesql}{fn teradata_autocommit_on}"
    con = None
    cur = None

    if queries is not None:
        if isinstance(queries, str):
            queries = [queries]

        # Check if we have any queries to execute
        if len(queries) == 0:
            return

        try:
            con = tdmlctx.td_connection
            if con is None:
                raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                          MessageCodes.CONNECTION_FAILURE)
            con = con.connection
            cur = con.cursor()
            # Set auto_commit to OFF
            cur.execute(auto_commit_off)
            for query in queries:
                cur.execute(query)

            # Try committing the transaction
            con.commit()
        except Exception:
            # Let's first rollback
            con.rollback()
            # Now, let's raise the error as is
            raise
        finally:
            # Finally, we must set auto_commit to ON
            cur.execute(auto_commit_on)


def db_transaction(func):
    """
    DESCRIPTION:
        Function to execute another function in a transaction.

    PARAMETERS:
        func:
            Required Argument.
            Specifies the function to be executed in a single transaction.
            Types: function

    RETURNS:
        The object returned by "func".

    RAISES:
        TeradataMlException, OperationalError

    EXAMPLES:
        # Example: Declare a function to delete all the records from two tables
        #          and execute the function in a transaction.
        >>> @db_transaction
        ... def insert_data(table1, table2):
        ...     execute_sql("delete from {}".format(table1))
        ...     execute_sql("delete from {}".format(table2))
        ...     return True
        >>> # Executing the above function in a transaction.
        >>> insert_data("sales", "admissions_train")
        True
        >>>
    """
    @functools.wraps(func)
    def execute_transaction(*args, **kwargs):
        auto_commit_off = "{fn teradata_nativesql}{fn teradata_autocommit_off}"
        auto_commit_on = "{fn teradata_nativesql}{fn teradata_autocommit_on}"
        con = None
        cur = None

        result = None
        try:
            con = tdmlctx.td_connection
            if con is None:
                raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                          MessageCodes.CONNECTION_FAILURE)
            con = con.connection
            cur = con.cursor()
            # Set auto_commit to OFF.
            cur.execute(auto_commit_off)

            # Execute function.
            result = func(*args, **kwargs)

            # Try committing the transaction.
            con.commit()
        except Exception:
            # Let's first rollback.
            con.rollback()
            # Now, let's raise the error as is.
            raise
        finally:
            # Finally, we must set auto_commit to ON.
            cur.execute(auto_commit_on)

        return result

    return execute_transaction


def _execute_stored_procedure(function_call, fetchWarnings=True, expect_none_result=False):
    """
    DESCRIPTION:
       Executes the specified function call of the stored procedure which contains
       function name and parameters used by the function.

    PARAMETERS:
        function_call:
            Required argument.
            Specifies Function object for the stored procedure to be executed.
            This function object contains stored procedure name along with its arguments.
            Types: sqlalchemy.sql.functions.Function

        fetchWarnings:
            Optional Argument.
            Specifies a flag that decides whether to raise warnings thrown from Vantage or not.
            This will be the ideal behaviour for most of the stored procedures to fetch the warnings.
            Default Values: True
            Types: bool

        expect_none_result:
            Optional Argument.
            When set to True, warnings will be ignored, and only result set is returned.
            Returns None if query does not produce a result set.
            This option is ignored when fetchWarnings is set to True.
            Default Values: False
            Types: bool

    RETURNS:
           Results received from Vantage after the execution.

    RAISES:
           Exception thrown by the Vantage.

    EXAMPLES:
        # No parameter needed by stored procedure.
        functioncall = func.SYSUIF.list_base_environments()
        _execute_stored_procedure(functioncall)

        # Parameters are passed to the stored procedure in a list.
        functioncall = func.SYSUIF.install_file('myfile','mapper.py','cz!/documents/mapper.py')
        _execute_stored_procedure("SYSUIF.install_file(functioncall)", fetchWarnings=True)
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["function_call", function_call, False, (Function)])
    __arg_info_matrix.append(["fetchWarnings", fetchWarnings, True, (bool)])
    __arg_info_matrix.append(["expect_none_result", expect_none_result, True, (bool)])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    sqlbundle = SQLBundle()

    # Get the query for running stored procedure.
    exec_sp_stmt = sqlbundle._get_sql_query(SQLConstants.SQL_EXEC_STORED_PROCEDURE)
    exec_sp_stmt = exec_sp_stmt.format(_get_function_call_as_string(function_call))

    return UtilFuncs._execute_query(exec_sp_stmt, fetchWarnings, expect_none_result)


def _get_function_call_as_string(sqlcFuncObj):
    """
    DESCRIPTION:
        This function returns string representation for the sqlalchemy.sql.functions.Function object
        which will be used to create a query to be used to execute the function.

    PARAMETERS:
        sqlcFuncObj:
            Required Argument.
            Specifies function object representing the SQL function call to be executed.

        RAISES:
            None

        RETURNS:
            String representation of the input Function.

        EXAMPLES:
            functioncall = func.SYSUIF.install_file("tdml_testfile", "test_script", "/root/test_script.py")
            _get_function_call_as_string(functioncall)

        Output:
            "SYSUIF.install_file('tdml_testfile', 'test_script', '/root/test_script.py')"
    """
    # This is done by _exec_stored_procedure
    from teradatasqlalchemy.dialect import dialect as td_dialect
    kw = dict({'dialect': td_dialect(),
               'compile_kwargs':
                   {
                       'include_table': False,
                       'literal_binds': True
                   }
               })

    return str(sqlcFuncObj.compile(**kw))


def _get_quoted_object_name(schema_name, object_name, datalake=None):
    """
    DESCRIPTION:
        This function quotes and joins schema name to the object name which can either be table or a view.

    PARAMETERS:
        schema_name
            Required Argument.
            Specifies the schema name.
            Type: str

        object_name
            Required Argument.
            Specifies the object name either table or view.
            Type: str

        datalake
            Optional Argument.
            Specifies the datalake name.
            Default value: None
            Type: str

    RAISES:
        None

    RETURNS:
        Quoted and joined string of schema and object name.

    EXAMPLES:
        _get_quoted_object_name(schema_name = "alice", object_name = "admissions_train")

    OUTPUT:
        '"alice"."admissions_train"'
    """
    tdp = preparer(td_dialect)

    if schema_name is not None:
        schema_name = tdp.quote(schema_name)
    else:
        schema_name = tdp.quote(tdmlctx._get_current_databasename())

    quoted_object_name = "{0}.{1}".format(schema_name, tdp.quote(object_name))
    if datalake is not None:
        quoted_object_name = "{}.{}".format(tdp.quote(datalake), quoted_object_name)
    return quoted_object_name


@collect_queryband(queryband='VwLg')
def view_log(log_type="script", num_lines=1000, query_id=None, log_dir=None):
    """
    DESCRIPTION:
        Function for viewing script, apply or byom log on Vantage.
        Logs are pulled from 'script_log' or 'byom.log' file on database node.
        When log_type is "script", logs are pulled from 'scriptlog' file on database node.
        This is useful when Script.execute() is executed to run user scripts in Vantage.
        When log_type is set to "apply", function downloads the log files to a folder.
        Notes:
            * Logs files will be downloaded based on "log_dir".
            * teradataml creates a sub directory with the name as "query_id"
              and downloads the logs to the sub directory.
            * files generated from "query_id" requires few seconds to generate,
              provide "query_id" to function view_log() after few seconds else
              it will return empty sub directory.

    PARAMETERS:
        log_type:
            Optional Argument.
            Specifies which logs to view.
            If set to 'script', script log is pulled from database node.
            If set to 'byom', byom log is pulled from database node.
            If set to 'apply' logs are pulled from kubernetes container.
            Permitted Values: 'script', 'apply', 'byom'
            Default Value: 'script'
            Types: str

        num_lines:
            Optional Argument.
            Specifies the number of lines to be read and displayed from log.
            Note:
                This argument is applicable when log_type is 'script' otherwise ignored.
            Default Value: 1000
            Types: int

        query_id:
            Required Argument when log_type is 'apply', otherwise ignored.
            Specifies the id of the query for which logs are to be retrieved.
            This query id is part of the error message received when Apply class
            or Dataframe apply method calls fail to execute the Apply table operator
            query.
            Types: str

        log_dir:
            Optional Argument.
            Specifies the directory path to store all the log files for "query_id".
            Notes:
                * This argument is applicable when log_type is 'apply' otherwise ignored.
                * when "log_dir" is not provided, function creates temporary folder
                  and store the log files in the temp folder.
            Types: str

    RETURNS:
        when log_type="apply" returns log files, otherwise teradataml dataframe.

    RAISES:
        TeradataMLException.

    EXAMPLES:
        # Example 1: View script log.
        >>> view_log(log_type="script", num_lines=200)
        >>> view_log(log_type="byom", num_lines=200)

        # Example 2: Download the Apply query logs to a default temp folder.
        # Use query id from the error messages returned by Apply class.
        >>> view_log(log_type="apply", query_id='307161028465226056')
        Logs for query_id "307191028465562578" is stored at "C:\\local_repo\\AppData\\Local\\Temp\\tmp00kuxlgu\\307161028465226056"

        # Example 3: Download the Apply query logs to a specific folder.
        # Use query id from the error messages returned by Apply class.
        >>> view_log(log_type="apply", query_id='307161028465226056',log_dir='C:\\local_repo\\workspace')
        Logs for query_id "307191028465562578" is stored at "C:\\local_repo\\workspace\\307161028465226056"
    """
    awu_matrix_test = []
    awu_matrix_test.append((["num_lines", num_lines, True, (int), True]))
    awu_matrix_test.append(("log_type", log_type, True, (str), True,
                            [TableOperatorConstants.SCRIPT_LOG.value,
                             TableOperatorConstants.APPLY_LOG.value,
                             TableOperatorConstants.BYOM_LOG.value]))
    # Validate argument type.
    _Validators._validate_function_arguments(awu_matrix_test)

    # Validate num_lines is a positive integer.
    _Validators._validate_positive_int(num_lines, "num_lines")

    awu_matrix_test.append(["query_id", query_id, True, (str), True])
    awu_matrix_test.append(["log_dir", log_dir, True, (str), True])

    # Validate argument type.
    _Validators._validate_function_arguments(awu_matrix_test)

    # log_type is script.
    if log_type.upper() in [TableOperatorConstants.SCRIPT_LOG.value, TableOperatorConstants.BYOM_LOG.value]:
        # Validate num_lines is a positive integer.
        _Validators._validate_positive_int(num_lines, "num_lines")

        # Query for viewing last n lines of script log.
        view_log_query = TableOperatorConstants.SCRIPT_LOG_QUERY.value \
            .format(num_lines, configure.default_varchar_size)

    # log_type is apply.
    else:
        if query_id is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING,
                                                           "query_id",
                                                           "log_type=\"apply\""),
                                      MessageCodes.DEPENDENT_ARG_MISSING)
        if log_dir is not None:
            if not os.path.exists(log_dir):
                err_msg = 'The path \'{}\' does not exist.'.format(
                    log_dir)
                raise TeradataMlException(err_msg, MessageCodes.INPUT_FILE_NOT_FOUND)
            if not os.path.isdir(log_dir):
                err_msg = 'Please provide directory path instead of file path.'.format(
                    log_dir)
                raise TeradataMlException(err_msg, MessageCodes.INPUT_FILE_NOT_FOUND)
        from teradataml.scriptmgmt.UserEnv import (_get_auth_token,
                                                   _get_ues_url,
                                                   _process_ues_response)
        ues_url = _get_ues_url(logs=True, query_id=query_id)
        response = UtilFuncs._http_request(ues_url, headers=_get_auth_token())
        resp = _process_ues_response(api_name="view_log", response=response)
        resp = resp.content.decode('utf-8')
        jsons = json.loads(resp)
        if log_dir is None:
            log_dir = tempfile.mkdtemp()
        log_dir = os.path.join(log_dir, query_id)
        if os.path.exists(log_dir):
            shutil.rmtree(log_dir)
        os.mkdir(log_dir)
        urls_and_files = [(log['url'], os.path.join(log_dir, log['name'])) for log in jsons['logs']]
        failed_files = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = {executor.submit(_fetch_url_and_save, url, file_path):
                           (os.path.basename(file_path)) for url, file_path in urls_and_files}
            for future in concurrent.futures.as_completed(results):
                try:
                    file_name = results[future]
                    future.result()
                except (TeradataMlException, RuntimeError, Exception) as emsg:
                    failed_files.append((file_name, emsg))
        if len(failed_files) > 0:
            emsg = ""
            for msg in failed_files:
                emsg += "\nUnable to download the file - {}. Reason: {}" \
                    .format(msg[0], msg[1].args[0])
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "view_log()", emsg)
            raise TeradataMlException(error_msg, msg_code)
        else:
            print("Logs for query_id \"{}\" is stored at \"{}\"".format(query_id, log_dir))
    # Return a teradataml dataframe from query.
    if log_type != 'apply':
        return tdmldf.dataframe.DataFrame.from_query(view_log_query)


def _fetch_url_and_save(url, file_path):
    """
    DESCRIPTION:
       Download file from specifed url and update files at specified path.

    PARAMETERS:
        url:
            Specifies the url from where file needs to be downloaded.

        file_path:
            Specifies the path of file where downloaded file needs to be updated.

    Returns:
        None

    """
    from teradataml.scriptmgmt.UserEnv import _process_ues_response
    response = UtilFuncs._http_request(url)
    resp = _process_ues_response(api_name="view_log", response=response)
    with open(file_path, 'w') as file:
        file.write(resp.content.decode('utf-8'))


def _check_if_python_packages_installed():
    """
    DESCRIPTION:
        Function to set the following global variables based on whether the Vantage node
        has Python and add-on packages including pip3 installed.
        - 'python_packages_installed' to True or False 
        - 'python_version_vantage' to the version of Python installed on Vantage.

    PARAMETERS:
        None.

    RETURNS:
        None.

    RAISES:
        Exception.

    EXAMPLES:
        _check_if_python_packages_installed()
    """
    if tdmlctx.python_packages_installed:
        # Skip check if Python and add-on packages are already installed and checked.
        return

    # Check if Python interpreter and add-ons packages are installed or not.
    try:
        query = TableOperatorConstants.CHECK_PYTHON_INSTALLED.value.format(configure.indb_install_location)
        opt = UtilFuncs._execute_query(query=query)

        python_version = opt[0][0].split(" -- ")[1].split(" ")[1].strip()

        # If query execution is successful, then Python and add-on packages are
        # present.
        tdmlctx.python_packages_installed = True
        tdmlctx.python_version_vantage = python_version
    except Exception as err:
        # Raise Exception if the error message does not contain
        # "bash: pip3: command not found".
        # Default value of the global variable "python_packages_installed" remains
        # same which was set during create_context/set_context.
        if "bash: pip3: command not found" not in str(err):
            raise


@collect_queryband(queryband='PkgDtls')
def db_python_package_details(names=None):
    """
    DESCRIPTION:
        Function to get the Python packages, installed on Vantage, and their corresponding
        versions.
        Note:
            Using this function is valid only when Python interpreter and add-on packages
            are installed on the Vantage node.

    PARAMETERS:
        names:
            Optional Argument.
            Specifies the name(s)/pattern(s) of the Python package(s) for which version
            information is to be fetched from Vantage. If this argument is not specified
            or None, versions of all installed Python packages are returned.
            Default Value: None
            Types: str

    RETURNS:
        teradataml DataFrame, if package(s) is/are present in the Vantage.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # Note:
        #   These examples will work only when the Python packages are installed on Vantage.

        # Example 1: Get the details of a Python package 'dill' from Vantage.
        >>> db_python_package_details("dill")
          package  version
        0    dill  0.2.8.2

        # Example 2: Get the details of Python packages, having string 'mpy', installed on Vantage.
        >>> db_python_package_details(names = "mpy")
                 package  version
        0          simpy   3.0.11
        1          numpy   1.16.1
        2          gmpy2    2.0.8
        3  msgpack-numpy  0.4.3.2
        4          sympy      1.3

        # Example 3: Get the details of Python packages, having string 'numpy' and 'learn',
        #            installed on Vantage.
        >>> db_python_package_details(["numpy", "learn"])
                 package  version
        0   scikit-learn   0.20.3
        1          numpy   1.16.1
        2  msgpack-numpy  0.4.3.2

        # Example 4: Get the details of all Python packages installed on Vantage.
        >>> db_python_package_details()
                  package  version
        0       packaging     18.0
        1          cycler   0.10.0
        2           simpy   3.0.11
        3  more-itertools    4.3.0
        4          mpmath    1.0.0
        5           toolz    0.9.0
        6       wordcloud    1.5.0
        7         mistune    0.8.4
        8  singledispatch  3.4.0.3
        9           attrs   18.2.0

    """
    # Validate arguments.
    __arg_info_matrix = []
    __arg_info_matrix.append(["names", names, True, (str, list), True])

    _Validators._validate_function_arguments(arg_list=__arg_info_matrix)

    # Check if Python interpretor and add-on packages are installed or not.
    _check_if_python_packages_installed()

    # Raise error if Python and add-on packages are not installed.
    if not tdmlctx.python_packages_installed:
        raise TeradataMlException(Messages.get_message(MessageCodes.PYTHON_NOT_INSTALLED),
                                  MessageCodes.PYTHON_NOT_INSTALLED)

    package_str = ""
    # Adding "grep ..." only when the argument "name" is mentioned.
    # Otherwise, all the package details are fetched.
    if names is not None:
        names = UtilFuncs._as_list(names)
        package_str = "|".join(names)
        package_str = "grep -E \"{0}\" | ".format(package_str)

    query = TableOperatorConstants.PACKAGE_VERSION_QUERY.value. \
        format(configure.indb_install_location, package_str, configure.default_varchar_size)

    ret_val = tdmldf.dataframe.DataFrame.from_query(query)

    if ret_val.shape[0] == 0:
        msg_str = "No Python package(s) found based on given search criteria : names = {}"
        print(msg_str.format(names))
        ret_val = None

    return ret_val


def _db_python_package_version_diff(packages=None, only_diff=True):
    """
    DESCRIPTION:
        Internal function to get the pandas dataframe containing the difference in the Python
        packages installed on Vantage and the packages mentioned in the argument "packages".
        Note:
            * Using this function is valid only when Python interpreter and add-on packages
                are installed on the Vantage node.
            * This function also checks for differences in Python packages versions given
                part of package name as string.
            * Returns pandas dataframe of only differences when the argument `only_diff` is set to
                True. Otherwise, returns all the packages.

    PARAMETERS:
        packages:
            Required Argument.
            Specifies the name(s) of the Python package(s) for which the difference
            in the versions is to be fetched from Vantage.
            Note:
            * If this argument is None, all the packages installed on Vantage are considered.
            * If any package is present in Vantage but not in the current environment, then None
                is shown as the version of the package in the current environment.
            Types: str or list of str

        only_diff:
            Optional Argument.
            Specifies whether to return only the differences in the versions of the packages
            installed on Vantage and the packages mentioned in the argument "packages".
            Default Value: True

    RETURNS:
        pandas DataFrame

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # Note:
        #   These examples will work only when the Python packages are installed on Vantage.

        # Example 1: Get the difference in the versions of Python packages 'dill' and 'matplotlib' 
        # installed on Vantage.
        >>> _db_python_package_version_diff(["dill", "matplotlib"])
          package vantage  local
        0    dill   0.3.6  0.3.7

        # Example 2: Get the difference in the versions of Python packages 'dill' and 'matplotlib' 
        # installed on Vantage and 'only_diff' argument set to False.
        >>> _db_python_package_version_diff(["dill", "matplotlib"], only_diff=False)
                    package vantage  local
        0  matplotlib-inline   0.1.6  0.1.6
        1               dill   0.3.6  0.3.7
        2         matplotlib   3.6.2  3.6.2
    """
    # Check if Python interpreter and add-on packages are installed or not.
    _check_if_python_packages_installed()

    # Raise error if Python and add-on packages are not installed.
    if not tdmlctx.python_packages_installed:
        raise TeradataMlException(Messages.get_message(MessageCodes.PYTHON_NOT_INSTALLED),
                                  MessageCodes.PYTHON_NOT_INSTALLED)

    # Installed packages dictionary.
    db_pkg_df = db_python_package_details(packages)
    if db_pkg_df is None:
        return None

    pkgs_dict = {row.package: row.version for row in db_pkg_df.itertuples()}

    from importlib.metadata import PackageNotFoundError, version
    diff_list = []

    for pkg in pkgs_dict.keys():
        vantage_version = pkgs_dict.get(pkg)
        try:
            local_version = version(pkg)
        except PackageNotFoundError:
            # If package is not found in the current environment, then the local version is set to None.
            local_version = None
        except Exception as e:
            # Any other exception is raised.
            raise

        if only_diff:
            if vantage_version != local_version:
                # Add to list only when the versions are different.
                diff_list.append([pkg, vantage_version, local_version])
        else:
            # Add to list all the packages and versions irrespective of the differences.
            diff_list.append([pkg, vantage_version, local_version])

    return pd.DataFrame(diff_list, columns=["package", "vantage", "local"])


@collect_queryband(queryband='PythonDiff')
def db_python_version_diff():
    """
    DESCRIPTION:
        Function to get the difference of the Python intepreter major version installed on Vantage
        and the Python version used in the current environment.

        Note:
            * Using this function is valid only when Python interpreter and add-on packages
              are installed on the Vantage node.

    RETURNS:
        Empty dictionary when Python major version is same on Vantage and the current environment.
        Otherwise, returns a dictionary with the following keys:
            - 'vantage_version': Python major version installed on Vantage.
            - 'local_version': Python major version used in the current environment.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # Note:
        # These examples will work only when the Python packages are installed on Vantage.

        # Example 1: Get the difference in the Python version installed on Vantage and the current environment.
        >>> db_python_version_diff()
        {"vantage_version": "3.7", "local_version": "3.8"}
    """
    # Check if Python interpretor and add-on packages are installed or not.
    _check_if_python_packages_installed()

    # Raise error if Python and add-on packages are not installed.
    if not tdmlctx.python_packages_installed:
        raise TeradataMlException(Messages.get_message(MessageCodes.PYTHON_NOT_INSTALLED),
                                  MessageCodes.PYTHON_NOT_INSTALLED)

    # Get major version of Python installed on Vantage and the current environment.
    python_local = tdmlctx.python_version_local.rsplit(".", 1)[0]
    python_vantage = tdmlctx.python_version_vantage.rsplit(".", 1)[0]

    if python_local != python_vantage:
        return {"vantage_version": python_vantage, "local_version": python_local}

    return {}


@collect_queryband(queryband='PkgDiff')
def db_python_package_version_diff(packages=None):
    """
    DESCRIPTION:
        Function to get the difference of the Python packages installed on Vantage and
        in the current environment mentioned in the argument "packages".

        Notes:
            * Using this function is valid only when Python interpreter and add-on packages
              are installed on the Vantage node.
            * This function also checks for differences in Python packages versions given
              part of package name as string.

    PARAMETERS:
        packages:
            Optional Argument.
            Specifies the name(s) of the Python package(s) for which the difference
            in the versions is to be fetched from Vantage.
            Notes:
                * If this argument is None, all the packages installed on Vantage are considered.
                * If any package is present in Vantage but not in the current environment, then None
                  is shown as the version of the package in the current environment.
            Types: str or list of str

    RETURNS:
        pandas DataFrame

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # Note:
        # These examples will work only when the Python packages are installed on Vantage.

        # Example 1: Get the difference in the versions of Python package 'dill' installed on Vantage.
        >>> db_python_package_version_diff("dill")
                  package   vantage    local
        0            dill    0.10.0   0.11.2

        # Example 2: Get the difference in the versions of all Python packages installed on Vantage.
        >>> db_python_package_version_diff()
                  package   vantage    local
        0    scikit-learn     1.3.3   0.24.2
        1            dill    0.10.0   0.11.2
        ...
        532         attrs    18.2.0   17.0.0

    """
    # Validate arguments.
    __arg_info_matrix = []
    __arg_info_matrix.append(["packages", packages, True, (str, list), True])

    _Validators._validate_function_arguments(arg_list=__arg_info_matrix)

    return _db_python_package_version_diff(packages=packages)


def _create_table(table_name,
                  columns,
                  primary_index=None,
                  unique=True,
                  temporary=False,
                  schema_name=None,
                  set_table=True,
                  **kwargs):
    """
    DESCRIPTION:
        This is an internal function used to construct a SQLAlchemy Table Object.
        This function checks appropriate flags and supports creation of Teradata
        specific Table constructs such as Volatile/Primary Index tables and constraints.

    PARAMETERS:
        table_name:
            Required Argument.
            Specifies the name of SQL table.
            Types: str

        columns:
            Required Argument.
            Specifies a Python dictionary with column-name(key) to column-type(value) mapping
            to create table.
            Types: dict

        primary_index:
            Optional Argument.
            Specifies the column name(s) on which primary index needs to be created.
            Default Value: None
            Types: str OR list of Strings (str)

        unique:
            Optional Argument.
            Specifies whether index is unique primary index or not i.e.,
            if True, index column(s) does not accepts duplicate values,
            if False, index column(s) accepts duplicate values.
            Default Value: True
            Types: bool

        temporary:
            Optional Argument.
            Specifies whether SQL table to be created is Volatile or not.
            Default Value: False
            Types: bool

        schema_name:
            Optional Argument.
            Specifies the name of the SQL schema in the database to write to.
            If not specified, table is created in default schema.
            Default Value: None
            Types: str

        set_table:
            Optional Argument.
            A flag specifying whether to create a SET table or a MULTISET table.
            When True, an attempt to create a SET table is made.
            When False, an attempt to create a MULTISET table is made.
            Default Value: True
            Types: bool

        **kwargs:
            Optional Argument.
            Specifies table_level constraints as keyword arguments.
            Each constraint argument can accept a string or a list of strings.
            Notes:
                * If the same constraint is to be applied multiple times,
                  conditions or columns should be mentioned as individual
                  elements in the list.
                * If the constraint is to be applied on multiple columns,
                  it should be mentioned in a tuple inside the list.
                * For foreign_key_constraint, value should be a list
                  containing 3 elements, constrained columns,
                  referenced columns and referenced table name.
                * If multiple foreign_key_constraint constraints are
                  to be specified, then a list of tuples containing
                  the 3 elements should be specified.
            Permitted values:check_constraint, primary_key_constraint,
                            foreign_key_constraint, unique_key_constraint.

    RETURNS:
        None

    RAISES:
        None

    EXAMPLES:
        # Example 1: Create a table with primary key constraint.
        >>> _create_table(table_name=table_name, columns=columns_to_create, schema_name = schema_name,
                          primary_key_constraint='column_name', set_table=False)

        # Example 2: Create a table with multiple check constraints.
        >>> _create_table(table_name=table_name, columns=columns_to_create, schema_name = schema_name,
                          check_constraint=['column_name > value', 'column_name > value2'], set_table=False)

        # Example 3: Create a table with multiple columns as primary key in primary constraint.
        >>> _create_table(table_name=table_name, columns=columns_to_create, schema_name = schema_name,
                          primary_key_constraint=[('column_name','column_name')], set_table=False)

        # Example 4: Create a table with no constraint and no primary key.
        >>> _create_table(table_name=table_name, columns=columns_to_create, schema_name = schema_name,
                          set_table=False)

    """
    try:
        prefix = []
        pti = post(opts={})

        if temporary is True:
            pti = pti.on_commit(option='preserve')
            prefix.append('VOLATILE')

        if set_table:
            prefix.append('set')
        else:
            prefix.append('multiset')

        meta = MetaData()
        meta.bind = tdmlctx.get_context()

        if primary_index is not None:
            if isinstance(primary_index, list):
                pti = pti.primary_index(unique=unique, cols=primary_index)
            elif isinstance(primary_index, str):
                pti = pti.primary_index(unique=unique, cols=[primary_index])
        else:
            pti = pti.no_primary_index()

        con_form = []
        foreign_constraints = []
        for c_name, parameters in kwargs.items():
            _Validators._validate_function_arguments([["constraint_type", c_name, True, str,
                                                       True, SQLConstants.CONSTRAINT.value]])
            if c_name in 'check_constraint':
                parameters = UtilFuncs._as_list(parameters)
                [con_form.append("{}('{}')".format("CheckConstraint", col)) for col in parameters]
            if c_name in 'foreign_key_constraint':
                parameters = parameters if isinstance(parameters[0], tuple) else [tuple(parameters)]
                # Every element in parameter is 3 elements.
                # 1st element and 2nd element also a list. 3rd element is name of ForeignKey.
                for fk_columns, fk_ref_columns, fk_name in parameters:
                    fk_ref_column_objs = []

                    # fk_ref_columns is in this format - table_name.column_name .
                    # There is no provision for schema name here.
                    # sqlalchemy is not accepting this notation here - schema_name.table_name.column_name
                    # So, create Column Object and bind schema name and table name to it.
                    for fk_ref_column in fk_ref_columns:
                        ref_column_table, ref_column = fk_ref_column.split(".")
                        t = Table(ref_column_table, MetaData(), Column(ref_column), schema=schema_name)
                        fk_ref_column_objs.append(getattr(t, "c")[ref_column])
                    foreign_constraints.append(ForeignKeyConstraint(fk_columns, fk_ref_column_objs, fk_name))

            if c_name in ['primary_key_constraint', 'unique_key_constraint']:
                c_name = "UniqueConstraint" if c_name in 'unique_key_constraint' else 'PrimaryKeyConstraint'
                parameters = UtilFuncs._as_list(parameters)
                [con_form.append("{}('{}')".format(c_name, "','".join(col))) if type(col) == tuple else con_form.append(
                    "{}('{}')".format(c_name, col)) for col in parameters]
        con_form.append("")

        # Create default Table construct with parameter dictionary
        table_str = "Table(table_name, meta,*(Column(c_name, c_type) for c_name,c_type in" \
                    " columns.items()),{} teradatasql_post_create=pti,prefixes=prefix," \
                    "schema=schema_name)".format("" if con_form is None else ",".join(con_form))

        table = eval(table_str)
        for foreign_constraint in foreign_constraints:
            table.append_constraint(foreign_constraint)
        table.create(bind=tdmlctx.get_context())

    except Exception as err:
        msg_code = MessageCodes.EXECUTION_FAILED
        raise TeradataMlException(Messages.get_message(msg_code, "create table", str(err)), msg_code)


def _create_temporal_table(table_name,
                           columns,
                           validtime_columns,
                           primary_index=None,
                           partition_by_range=None,
                           schema_name=None,
                           skip_if_exists=False):
    """
    DESCRIPTION:
        Internal function used to create validTime dimension temporal table.

    PARAMETERS:
        table_name:
            Required Argument.
            Specifies the name of SQL table.
            Types: str

        columns:
            Required Argument.
            Specifies a Python dictionary with column-name(key) to column-type(value) mapping
            to create table. Column-type can be of type string or teradatasqlalchemy type.
            Types: dict

        validtime_columns:
            Required Argument.
            Specifies the validTime columns to be created in the table.
            Note:
                The columns specified in "validtime_columns" should be present in
                "columns" argument.
            Types: tuple of str

        primary_index:
            Optional Argument.
            Specifies the column name(s) on which primary index needs to be created.
            Types: str OR list of Strings (str)

        partition_by_range:
            Optional Argument.
            Specifies the column name(s) on which partition by range needs to be created.
            Types: str OR ColumnExpression

        schema_name:
            Optional Argument.
            Specifies the name of the SQL schema in the database to write to.
            If not specified, table is created in default schema.
            Types: str

    RETURNS:
        None

    RAISES:
        None

    EXAMPLES:
        >>> from teradataml.dbutils.dbutils import _create_temporal_table
        >>> from teradatasqlalchemy.types import *
        # Example: Create a temporal table "Table1" with primary key constraint, partition it by range.
        #          Make sure to specify column validTime temporal column from columns 'start_time'
        #          and 'end_time'.
        >>> _create_temporal_table(table_name="Table1",
        ...                        columns={"column1": "VARCHAR(100)",
        ...                                 "column2": INTEGER,
        ...                                 "start_time": "TIMESTAMP(6)",
        ...                                 "end_time": TIMESTAMP(6)},
        ...                        schema_name = "vfs_test",
        ...                        primary_index='column_name',
        ...                        partition_by_range='column_name',
        ...                        validtime_columns=('start_time', 'end_time'))
    """
    # Prepare column clause first.
    columns_clause_ = ['{} {}'.format(k, v if isinstance(v, str)
                            else v.compile(td_dialect())) for k, v in columns.items()]
    if validtime_columns:
        period_for_clause = ['PERIOD FOR ValidPeriod  ({}, {}) AS VALIDTIME'.format(
            validtime_columns[0], validtime_columns[1])
        ]
    else:
        period_for_clause = []
    columns_clause = ",\n ".join(columns_clause_+period_for_clause)

    # Prepare primary index clause.
    if primary_index:
        primary_index_clause = "PRIMARY INDEX ({})".format(
            ", ".join(UtilFuncs._as_list(primary_index)))
    else:
        primary_index_clause = ""

    # Prepare partition by range clause.
    if partition_by_range:
        partition_by_range_clause = "PARTITION BY RANGE_N({})".format(
            partition_by_range if isinstance(partition_by_range, str) else partition_by_range.compile())
    else:
        partition_by_range_clause = ""

    # Prepare create table statement.
    table_name = UtilFuncs._get_qualified_table_name(schema_name, table_name) if\
        schema_name else table_name
    sql = """
    CREATE MULTISET TABLE {}
    (\n{}\n)\n{}\n{}
    """.format(table_name, columns_clause, primary_index_clause, partition_by_range_clause)

    if skip_if_exists:
        execute_sql(sql, ignore_errors=3803)
    else:
        execute_sql(sql)

    return True


def _create_database(schema_name, size='10e6', spool_size=None,
                     datalake=None, **kwargs):
    """
    DESCRIPTION:
        Internal function to create a database with the specified name and size.

    PARAMETERS:
        schema_name:
            Required Argument.
            Specifies the name of the database to create.
            Types: str

        size:
            Optional Argument.
            Specifies the number of bytes to allocate to new database.
            Note:
                Exponential notation can also be used.
            Types: str or int

        spool_size:
            Optional Argument.
            Specifies the number of bytes to allocate to new database
            for spool space.
            Note:
                Exponential notation can also be used.
            Types: str or int

        datalake:
            Optional Argument.
            Specifies the name of datalake to create database in.
            Types: str

        kwargs:
            Optional Argument.
            Specifies keyword arguments which are used in DBPROPERTIES
            clause as key-value pair while creating datalake database.

    RETURNS:
        bool

    RAISES:
        TeradataMlException.

    EXAMPLES:
        >>> from teradataml.dbutils.dbutils import _create_database
        # Example 1: Create database.
        >>> _create_database("db_name1", "10e5")

        # Example 2: Create database in datalake.
        >>> _create_database("otf_db_1", datalake="datalake_iceberg_glue")

        # Example 3: Create database in datalake having DBPROPERTIES.
        >>> _create_database("otf_db", datalake="datalake_iceberg_glue",
        ...                  owner='tdml_user', other_property='some_value',
        ...                  other_property2=20, comment='Created by tdml_user')
    """
    if datalake:
        db_properties = []
        for key, val in kwargs.items():
            db_properties.append("'{}'='{}'".format(key, val))

        sql = "CREATE DATABASE {}.{}{};".format(datalake, schema_name,
                                                ' DBPROPERTIES({})'.format(','.join(db_properties))
                                                if db_properties else '')

    else:
        sql = "CREATE DATABASE {} FROM {} AS PERM = {}".format(schema_name, tdmlctx._get_database_username(), size)

    # If user pass spool size, create it with specified space.
    if spool_size:
        sql = "{} , SPOOL = {}".format(sql, spool_size)

    execute_sql(sql)
    return True


def _update_data(update_columns_values, table_name, schema_name, datalake_name=None, update_conditions=None):
    """
    DESCRIPTION:
        Internal function to update the data in a table.

    PARAMETERS:
        update_columns_values:
            Required Argument.
            Specifies the columns and it's values to update.
            Types: dict

        table_name:
            Required Argument.
            Specifies the name of the table to update.
            Types: str

        schema_name:
            Required Argument.
            Specifies the name of the database to update the data in the
            table "table_name".
            Types: str

        datalake_name:
            Optional Argument.
            Specifies the name of the datalake to look for "schema_name".
            Types: str

        update_conditions:
            Optional Argument.
            Specifies the key columns and it's values which is used as condition
            for updating the records.
            Types: dict

    RETURNS:
        bool

    RAISES:
        TeradataMlException.

    EXAMPLES:
       >>> from teradataml.dbutils.dbutils import _update_data
       >>> _update_data("db_name1", "tbl", update_conditions={"column1": "value1"})
    """
    # Prepare the update clause.
    update_clause = ", ".join(("{} = ?".format(col) for col in update_columns_values))
    update_values = tuple((_value for _value in update_columns_values.values()))

    # If key_columns_values is passed, then prepare the SQL with where clause.
    # Else, simply update every thing.
    qualified_table_name = _get_quoted_object_name(schema_name, table_name, datalake_name)

    get_str_ = lambda val: "'{}'".format(val) if isinstance(val, str) else val
    if update_conditions:

        # Prepare where clause.
        where_ = []
        for column, col_value in update_conditions.items():
            if isinstance(col_value, list):
                col_value = ", ".join(get_str_(val) for val in col_value)
                col_value = "({})".format(col_value)
                where_.append("{} IN {}".format(column, col_value))
            else:
                where_.append("{} = {}".format(column, col_value))

        where_clause = " AND ".join(where_)

        sql = f"""UPDATE {qualified_table_name} SET {update_clause}
                 WHERE {where_clause}
            """

        execute_sql(sql, (*update_values,))

    else:
        sql = f"""UPDATE {qualified_table_name} SET {update_clause}"""

        execute_sql(sql, update_values)
    return True


def _insert_data(table_name,
                 values,
                 columns=None,
                 schema_name=None,
                 datalake_name=None,
                 return_uid=False,
                 ignore_errors=None):
    """
    DESCRIPTION:
        Internal function to insert the data in a table.

    PARAMETERS:
        table_name:
            Required Argument.
            Specifies the name of the table to insert.
            Types: str

        values:
            Required Argument.
            Specifies the values to insert.
            Types: tuple or list of tuple

        columns:
            Optional Argument.
            Specifies the name of columns to be involved in insert.
            Types: list

        schema_name:
            Optional Argument.
            Specifies the name of the database to insert the data in the
            table "table_name".
            Types: str

        datalake_name:
            Optional Argument.
            Specifies the name of the datalake to look for "schema_name".
            Types: str

        return_uid:
            Optional Argument.
            Specifies whether the function should return the unique identifier
            of the inserted row or not. When set to True, function returns the
            unique ID generated by Teradata Vantage for the inserted row. Otherwise,
            it returns True if the insert operation is successful.
            Note:
                This argument is only applicable when the table is created
                in such a way it generates unique ID automatically.
            Default Value: False
            Types: bool

        ignore_errors:
            Optional Argument.
            Specifies the error code(s) to ignore while inserting data.
            If this argument is not specified, no errors are ignored.
            Note:
                Error codes are Teradata Vantage error codes and not
                teradataml error codes.
            Default Value: None
            Types: int or list of int

    RETURNS:
        bool or int

    RAISES:
        TeradataMlException.

    EXAMPLES:
       >>> from teradataml.dbutils.dbutils import _insert_data
       >>> _insert_data("tbl", (1, 2, 3))
    """
    # Prepare the update clause.
    qualified_table_name = _get_quoted_object_name(schema_name, table_name, datalake_name)

    values = UtilFuncs._as_list(values)

    # Prepare columns clause.
    if columns:
        # Prepare question marks.
        _q_marks = ["?"] * len(columns)
        columns = "({})".format(", ".join(columns))
    else:
        columns = ""
        _q_marks = ["?"] * (len(values[0]))

    if not return_uid:
        sql = "insert into {} {} values ({});".format(qualified_table_name, columns, ", ".join(_q_marks))
        execute_sql(sql, values, ignore_errors)
        return True

    sql = "{{fn teradata_agkr(C)}}insert into {} {} values ({});".format(qualified_table_name, columns, ", ".join(_q_marks))
    c = execute_sql(sql, values, ignore_errors)
    return c.fetchone()[0]


def _upsert_data(update_columns_values,
                 insert_columns_values,
                 upsert_conditions,
                 table_name,
                 schema_name,
                 datalake_name=None):
    """
    DESCRIPTION:
        Internal function to either insert or update the data to a table.

    PARAMETERS:
        update_columns_values:
            Required Argument.
            Specifies the columns and it's values to update.
            Types: dict

        insert_columns_values:
            Required Argument.
            Specifies the columns and it's values to insert.
            Types: dict

        upsert_conditions:
            Required Argument.
            Specifies the key columns and it's values which is used as condition
            for updating the records.
            Types: tuple

        table_name:
            Required Argument.
            Specifies the name of the table to insert.
            Types: str

        schema_name:
            Required Argument.
            Specifies the name of the database to update the data in the
            table "table_name".
            Types: str

        datalake_name:
            Optional Argument.
            Specifies the name of the datalake to look for "schema_name".
            Note:
                "schema_name" must be provided while using this argument.
            Types: str

    RETURNS:
        bool

    RAISES:
        TeradataMlException.

    EXAMPLES:
       >>> from teradataml.dbutils.dbutils import _upsert_data
       >>> _upsert_data("db_name1",
                        "tbl",
                        update_columns_values={"column1": "value1"},
                        insert_columns_values={"column1": "value2"},
                        upsert_conditions={"key1": "val1"}
                        )
    """
    # If user passes datalake name, then append the same to schema name.
    qualified_table_name = _get_quoted_object_name(schema_name, table_name, datalake_name)

    # Prepare the update clause.
    update_clause = ", ".join(("{} = ?".format(col) for col in update_columns_values))
    update_values = tuple((_value for _value in update_columns_values.values()))

    # Prepare the where clause and it's values.
    where_clause = " AND ".join(("{} = ?".format(col) for col in upsert_conditions))
    where_values = tuple((_value for _value in upsert_conditions.values()))

    # Prepare the insert clause and it's values.
    insert_values_clause = ", ".join(("?" for _ in range(len(insert_columns_values))))
    insert_clause = "({}) values ({})".format(", ".join(insert_columns_values), insert_values_clause)
    insert_values = tuple((_value for _value in insert_columns_values.values()))

    sql = f"""UPDATE {qualified_table_name} SET {update_clause}
         WHERE {where_clause}
       ELSE INSERT {qualified_table_name} {insert_clause}
    """
    execute_sql(sql, (*update_values, *where_values, *insert_values))


def _merge_data(target_table,
                target_table_alias_name,
                source,
                source_alias_name,
                condition,
                matched_details=None,
                non_matched_clause=None,
                temporal_clause=None,
                target_table_schema=None,
                source_table_schema=None):
    """
    DESCRIPTION:
        Internal function to merge the data in a table.

    PARAMETERS:
        target_table:
            Required Argument.
            Specifies the name of the target table to merge.
            Types: str

        target_table_alias_name:
            Required Argument.
            Specifies the alias name of the target table to merge.
            Types: str

        source:
            Required Argument.
            Specifies the name of the source table to merge.
            Can be a table name or a teradataml DataFrame.
            Note:
                Source can be a SELECT statement also. In this case,
                one should add paranthesis for the query. For example,
                value of source should be '(SELECT * FROM TABLE)' if
                source is a query.
            Types: str OR teradataml DataFrame

        source_alias_name:
            Required Argument.
            Specifies the alias name of the source table to merge.
            Types: str

        condition:
            Required Argument.
            Specifies the condition to merge the data.
            Types: str OR ColumnExpression

        matched_details:
            Optional Argument.
            Specifies what to do when the condition is matched.
            Teradata allows either UPDATE or DELETE when the condition is matched.
            Note:
                ColumnExpressions are not allowed for key 'set' since the aliases
                should be with the alias name and setting alias name is not straight forward.
                Hence, not allowing it for now.
            Types: dict
            Example: {"action": "UPDATE", "set": {"col1": "src.col1", "col2": "src.col2"}}

        non_matched_clause:
            Optional Argument.
            Specifies what to do when the condition is not matched.
            Teradata allows INSERT when the condition is not matched.
            Note:
                ColumnExpressions are not allowed in 'values' since the aliases
                should be with the alias name and setting alias name is not straight forward.
                Hence, not allowing it for now.
            Types: dict
            Example: {"action": "INSERT", "columns": ["col1", "col2"], "values": ["src.col1", "src.col2"]}

        temporal_clause:
            Optional Argument.
            Specifies the temporal clause to be added to the MERGE statement.
            Types: str

        target_table_schema:
            Optional Argument.
            Specifies the schema name of the target table.
            Types: str

        source_table_schema:
            Optional Argument.
            Specifies the schema name of the source table.
            Note:
                If source is a DataFrame, this argument is ignored.
            Types: str

    RETURNS:
        None

    RAISES:
        ValueError: If required parameters are missing or invalid.

    EXAMPLES:
        >>> _merge_data(
        ...     target_table="target_table",
        ...     target_table_alias_name="tgt",
        ...     source="source_table",
        ...     source_alias_name="src",
        ...     condition="tgt.id = src.id",
        ...     matched_details={"action": "UPDATE", "set": {"col1": "src.col1", "col2": "src.col2"}},
        ...     non_matched_clause={"action": "INSERT", "columns": ["id", "col1"], "values": ["src.id", "src.col1"]}
        ... )
    """
    # Note: Table names are not quoted because source can be a query also.
    #       To keep it intact, both target tables and source tables are not
    #       quoted. Hence it is caller function responsibility to add quote
    #       if either source table or target table has special characters or
    #       is from the user.
    quote = UtilFuncs._get_dialect_quoted_name
    if target_table_schema:
        target_table = "{}.{}".format(quote(target_table_schema), target_table)
    else:
        target_table = target_table

    # If source is DataFrame, extract the query from it.
    if isinstance(source, str):
        source = "{}.{}".format(quote(source_table_schema), source) \
            if source_table_schema else source
    else:
        source = "({})".format(source.show_query())

    # If condition is not a string, then prepare from it.
    condition = condition if isinstance(condition, str) else condition.compile()

    # Start building the MERGE statement
    merge_sql = (f"MERGE INTO {target_table} AS {target_table_alias_name} \n\tUSING "
                 f"{source} AS {source_alias_name} \n\tON {condition}")

    # Handle matched clause
    if matched_details:
        action = matched_details.get("action", "").upper()
        if action == "UPDATE":
            set_clause = ", ".join([f"{col} = {val}"
                                    for col, val in matched_details.get("set", {}).items()])
            merge_sql += f"\n\tWHEN MATCHED THEN \n\t\tUPDATE \n\t\tSET \n\t\t{set_clause}"
        elif action == "DELETE":
            merge_sql += "\n\tWHEN MATCHED THEN \n\tDELETE\n\t\t"
        else:
            raise ValueError("Invalid action in matched_details. Supported actions are 'UPDATE' and 'DELETE'.")

    # Handle non-matched clause
    if non_matched_clause:
        action = non_matched_clause.get("action", "").upper()
        if action == "INSERT":
            columns = ", ".join(non_matched_clause.get("columns", []))
            values = ", ".join(non_matched_clause.get("values", []))
            merge_sql += f"\n\tWHEN NOT MATCHED THEN \n\t\tINSERT ({columns}) \n\t\tVALUES \n\t\t({values})"
        else:
            raise ValueError("Invalid action in non_matched_clause. Supported action is 'INSERT'.")

    # Finalize the statement
    merge_sql += ";"
    if temporal_clause:
        merge_sql = "{} {}".format(temporal_clause, merge_sql)

    execute_sql(merge_sql)


def _delete_data(table_name, schema_name=None, datalake_name=None, delete_conditions=None, temporal_clause=None):
    """
    DESCRIPTION:
        Internal function to delete the data in a table.

    PARAMETERS:
        table_name:
            Required Argument.
            Specifies the name of the table to delete.
            Types: str

        schema_name:
            Optional Argument.
            Specifies the name of the database to delete the data in the
            table "table_name".
            Types: str

        datalake_name:
            Optional Argument.
            Specifies the name of the datalake to look for "schema_name".
            Types: str

        delete_conditions:
            Optional Argument.
            Specifies the ColumnExpression or dictionary containing key values
            pairs to use for removing the data.
            Types: ColumnExpression, dict
        
        temporal_clause:
            Optional Argument.
            Specifies the temporal clause to be added to the DELETE statement.
            Types: str

    RETURNS:
        int, specifies the number of records those are deleted.

    RAISES:
        TeradataMlException.

    EXAMPLES:
       >>> from teradataml.dbutils.dbutils import _delete_data
       >>> _delete_data("tbl", "db_name1", delete_conditions={"column1": "value1"})
    """
    qualified_table_name = _get_quoted_object_name(schema_name, table_name, datalake_name)
    sqlbundle = SQLBundle()

    sql = sqlbundle._get_sql_query(SQLConstants.SQL_DELETE_ALL_ROWS).format(qualified_table_name)

    # If condition exist, the prepare where clause.
    if delete_conditions:
        from teradataml.dataframe.sql import _SQLColumnExpression
        if isinstance(delete_conditions, _SQLColumnExpression):
            where_clause = delete_conditions.compile()
        elif isinstance(delete_conditions, dict):
            get_str_ = lambda val: "'{}'".format(val) if isinstance(val, str) else val
            where_ = []
            for column, col_value in delete_conditions.items():
                if isinstance(col_value, list):
                    col_value = ", ".join(get_str_(val) for val in col_value)
                    col_value = "({})".format(col_value)
                    where_.append("{} IN {}".format(column, col_value))
                else:
                    where_.append("{} = {}".format(column, col_value))
            where_clause = " AND ".join(where_)

        sql = sqlbundle._get_sql_query(SQLConstants.SQL_DELETE_SPECIFIC_ROW).format(qualified_table_name, where_clause)

    if temporal_clause:
        sql = "{} {}".format(temporal_clause, sql)

    res = execute_sql(sql)
    return res.rowcount


@collect_queryband(queryband='LstKwrds')
def list_td_reserved_keywords(key=None, raise_error=False):
    """
    DESCRIPTION:
        Function validates if the specified string or the list of strings is Teradata reserved keyword or not.
        If key is not specified or is a empty list, list all the Teradata reserved keywords.

    PARAMETERS:
        key:
            Optional Argument.
            Specifies a string or list of strings to validate for Teradata reserved keyword.
            Types: string or list of strings

        raise_error:
            Optional Argument.
            Specifies whether to raise exception or not.
            When set to True, an exception is raised,
            if specified "key" contains Teradata reserved keyword, otherwise not.
            Default Value: False
            Types: bool

    RETURNS:
        teradataml DataFrame, if "key" is None or a empty list.
        True, if "key" contains Teradata reserved keyword, False otherwise.

    RAISES:
        TeradataMlException.

    EXAMPLES:
       >>> from teradataml import list_td_reserved_keywords
       >>> # Example 1: List all available Teradata reserved keywords.
       >>> list_td_reserved_keywords()
         restricted_word
       0             ABS
       1         ACCOUNT
       2            ACOS
       3           ACOSH
       4      ADD_MONTHS
       5           ADMIN
       6             ADD
       7     ACCESS_LOCK
       8    ABORTSESSION
       9           ABORT
       >>>

       >>> # Example 2: Validate if keyword "account" is a Teradata reserved keyword or not.
       >>> list_td_reserved_keywords("account")
       True
       >>>

       >>> # Example 3: Validate and raise exception if keyword "account" is a Teradata reserved keyword.
       >>> list_td_reserved_keywords("account", raise_error=True)
       TeradataMlException: [Teradata][teradataml](TDML_2121) '['ACCOUNT']' is a Teradata reserved keyword.

       >>> # Example 4: Validate if the list of keywords contains Teradata reserved keyword or not.
       >>> list_td_reserved_keywords(["account", 'add', 'abc'])
       True

       >>> # Example 5: Validate and raise exception if the list of keywords contains Teradata reserved keyword.
       >>> list_td_reserved_keywords(["account", 'add', 'abc'], raise_error=True)
       TeradataMlException: [Teradata][teradataml](TDML_2121) '['ADD', 'ACCOUNT']' is a Teradata reserved keyword.
    """

    from teradataml.dataframe.dataframe import DataFrame, in_schema

    # Get the reserved keywords from the table
    reserved_keys = DataFrame(in_schema("SYSLIB", "SQLRestrictedWords"))

    # If key is not passed or is a empty list, return the list of Teradata reserved keywords.
    if key is None or len(key) == 0:
        return reserved_keys.select(['restricted_word'])

    key = [key] if isinstance(key, str) else key

    # Store the reserved keywords in buffer.
    if _InternalBuffer.get("reservered_words") is None:
        _InternalBuffer.add(reservered_words={word_[0] for word_ in reserved_keys.itertuples(name=None)})
    reservered_words = _InternalBuffer.get("reservered_words")

    # Check if key contains Teradata reserved keyword or not.
    res_key = (k.upper() for k in key if k.upper() in reservered_words)
    res_key = list(res_key)
    if len(res_key) > 0:
        if raise_error:
            raise TeradataMlException(Messages.get_message(MessageCodes.RESERVED_KEYWORD, res_key),
                                      MessageCodes.RESERVED_KEYWORD)
        return True
    return False


def _rename_table(old_table_name, new_table_name):
    """
    This function renames the existing table present in the database.

    PARAMETERS:
        old_table_name:
            Required Argument.
            Specifies the name of the existing table in vantage.
            Types : String

        new_table_name:
            Required Argument.
            Specifies the  the new name for the existing table.
            Types : String

    RETURNS:
        None

    RAISES:
        None

    EXAMPLES:
        >>> load_example_data("dataframe", "sales")
        >>> _rename_table("sales", "new_sales")
    """
    # Query to rename existing table.
    query = "RENAME TABLE {} TO {};".format(old_table_name, new_table_name)
    # Execute rename query.
    UtilFuncs._execute_ddl_statement(query)


def _execute_query_and_generate_pandas_df(query, index=None, **kwargs):
    """
    DESCRIPTION:
        Function executes the provided query and returns a pandas DataFrame.

    PARAMETERS:
        query:
            Required Argument.
            Specifies the query that needs to be executed to form Pandas
            DataFrame.
            Type: str

        index
            Optional Argument.
            Specifies column(s) to be used as Pandas index.
            Types: str OR list of Strings (str)

    RETURNS:
        Pandas DataFrame.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        pdf = _execute_query_and_generate_pandas_df("SELECT * from t1", "col1")
    """
    # Empty queryband buffer before SQL call.
    UtilFuncs._set_queryband()
    cur = execute_sql(query)
    columns = kwargs.pop('columns', [col[0] for col in cur.description])
    rows = cur.fetchall()
    if cur is not None:
        cur.close()

    # Set coerce_float to True for Decimal type columns.
    if 'coerce_float' not in kwargs:
        kwargs['coerce_float'] = True

    try:
        pandas_df = pd.DataFrame.from_records(data=list(tuple(row) for row in rows),
                                              columns=columns,
                                              index=index,
                                              **kwargs)
    except KeyError:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.INVALID_PRIMARY_INDEX),
            MessageCodes.INVALID_PRIMARY_INDEX)
    except:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.TDMLDF_SELECT_DF_FAIL),
            MessageCodes.TDMLDF_SELECT_DF_FAIL)

    return pandas_df

def _is_trigger_exist(schema_name, trigger_names):
    """
    DESCRIPTION:
        Checks if all given triggers exist in the specified schema.

    PARAMETERS:
        schema_name:
            Required Argument.
            Specifies the schema/database name.
            Types: str

        trigger_names:
            Required Argument.
            Specifies the trigger name(s) to check.
            Types: str or list of str

    RETURNS:
        Tuple - first element specifies whether all provided triggers exist or not. 
                second element specifies total number of triggers found from "trigger_names".

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>> is_trigger_exist("mydb", ["trg1", "trg2"])
        (True, 2)
        >>> is_trigger_exist("mydb", ["trg1", "missing_trg"])
        (False, 1)
    """
    # Normalize trigger_names to list
    triggers = UtilFuncs._as_list(trigger_names)
    if not triggers:
        return False

    # Prepare SQL to check all triggers in one call
    triggers_str = ", ".join("'{}'".format(t) for t in triggers)
    sql = f"""
        SELECT TriggerName
        FROM DBC.TriggersV
        WHERE DatabaseName = '{schema_name}'
        AND TriggerName IN ({triggers_str})
    """

    try:
        result = execute_sql(sql)
        found = {row[0] for row in result.fetchall()}
        num_found = len(found)
        all_exist = all(t in found for t in triggers)
        return all_exist, num_found
    except Exception as e:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.EXECUTION_FAILED, "is_triggers_exist", str(e)),
            MessageCodes.EXECUTION_FAILED)

class _TDSessionParams:
    """
    A successfull connection through teradataml establishes a session with Vantage.
    Every session will have default parameters. For example one can set Offset value
    for parameter 'Session Time Zone'.
    This is an internal utility to store all session related parameters.
    """

    def __init__(self, data):
        """
        Constructor to store columns and rows of session params.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the Session parameters.
                Types: dict
        """
        self.__session_params = data

    def __getitem__(self, parameter):
        """
        Return the value of Session parameter.

        PARAMETERS:
            parameter:
                Required Argument.
                Specifies name of the session parameter.
                Types: str
        """
        if parameter in self.__session_params:
            return self.__session_params[parameter]
        raise AttributeError("'TDSessionParams' object has no attribute '{}'".format(parameter))


def set_session_param(name, value):
    """
    DESCRIPTION:
        Function to set the session parameter.
        Note:
            * Look at Vantage documentation for session parameters.

    PARAMETERS:
        name:
            Required Argument.
            Specifies the name of the parameter to set.
            Permitted Values: timezone, calendar, account, character_set_unicode,
                              collation, constraint, database, dateform, debug_function,
                              dot_notation, isolated_loading, function_trace, json_ignore_errors,
                              searchuifdbpath, transaction_isolation_level, query_band, udfsearchpath
            Types: str

        value:
            Required Argument.
            Specifies the value for the parameter "name" to set.
            Permitted Values:
                1. timezone: timezone strings
                2. calendar: Teradata, ISO, Compatible
                3. character_set_unicode: ON, OFF
                4. account: should be a list in which first item should be "account string" second should be
                            either SESSION or REQUEST.
                5. collation: ASCII, CHARSET_COLL, EBCDIC, HOST, JIS_COLL, MULTINATIONAL
                6. constraint: row_level_security_constraint_name {( level_name | category_name [,...] | NULL )}
                               where,
                               row_level_security_constraint_name:
                                   Name of an existing constraint.
                                   The specified constraint_name must be currently assigned to the user.
                                   User can specify a maximum of 6 hierarchical constraints and 2 non-hierarchical
                                   constraints per SET SESSION CONSTRAINT statement.
                               level_name:
                                   Name of a hierarchical level, valid for the constraint_name, that is to replace the
                                   default level.
                                   The specified level_name must be currently assigned to the user. Otherwise, Vantage
                                   returns an error to the requestor.
                               category_name:
                                   A set of one or more existing non-hierarchical category names valid for the
                                   constraint_name.
                                   Because all assigned category (non-hierarchical) constraint values assigned to a
                                   user are automatically active, "set_session_param" is only useful to specify a
                                   subset of the assigned categories for the constraint.
                                   For example, assume that User BOB has 3 country codes, and wants to load a table
                                   with data that is to be made available to User CARL who only has rights to see data
                                   for his own country. User BOB can use "set_session_param" to specify only the
                                   country code for User CARL when loading the data so Carl can access the data later.
                7. database: Name of the new default database for the remainder of the current session.
                8. dateform: ANSIDATE, INTEGERDATE
                9. debug_function: should be a list in which first item should be "function_name" second should be
                            either ON or OFF.
                10. dot_notation: DEFAULT, LIST, NULL ERROR
                11. isolated_loading: NO, '', CONCURRENT
                12. function_trace: Should be a list. First item should be "mask_string" and second should be table name.
                13. json_ignore_errors: ON, OFF
                14. searchuifdbpath: String in format 'database_name, user_name'
                15. transaction_isolation_level: READ UNCOMMITTED, RU, SERIALIZABLE, SR
                16. query_band: Should be a list. First item should be "band_specification" and second should be either
                                SESSION or TRANSACTION
                17. udfsearchpath: Should be a list. First item should be "database_name" and second should be "udf_name"
            Types: str or list of strings

    Returns:
        True, if session parameter is set successfully.

    RAISES:
        ValueError, teradatasql.OperationalError

    EXAMPLES:
        # Example 1: Set time zone offset for the session as the system default.
        >>> set_session_param('timezone', 'LOCAL')
        True

        # Example 2: Set time zone to "AMERICA PACIFIC".
        >>> set_session_param('timezone', "'AMERICA PACIFIC'")
        True

        # Example 3: Set time zone to "-07:00".
        >>> set_session_param('timezone', "'-07:00'")
        True

        # Example 4: Set time zone to 3 hours ahead of 'GMT'.
        >>> set_session_param('timezone', "3")
        True

        # Example 6: Set calendar to 'COMPATIBLE'.
        >>> set_session_param('calendar', "COMPATIBLE")
        True

        # Example 7: Dynamically changes your account to 'dbc' for the remainder of the session.
        >>> set_session_param('account', ['dbc', 'SESSION'])
        True

        # Example 8: Enables Unicode Pass Through processing.
        >>> set_session_param('character_set_unicode', 'ON')
        True

        # Example 9: Session set to ASCII collation.
        >>> set_session_param('collation', 'ASCII')
        True

        # Example 10: The resulting session has a row-level security label consisting of an unclassified level
        #             and nato category.
        >>> set_session_param('constraint', 'classification_category (norway)')
        True

        # Example 11: Changes the default database for the session.
        >>> set_session_param('database', 'alice')
        True

        # Example 12: Changes the  DATE format to 'INTEGERDATE'.
        >>> set_session_param('dateform', 'INTEGERDATE')
        True

        # Example 13: Enable Debugging for the Session.
        >>> set_session_param('debug_function', ['function_name', 'ON'])
        True

        # Example 14: Sets the session response for dot notation query result.
        >>> set_session_param('dot_notation', 'DEFAULT')
        True

        # Example 15: DML operations are not performed as concurrent load isolated operations.
        >>> set_session_param('isolated_loading', 'NO')
        True

        # Example 16: Enables function trace output for debugging external user-defined functions and
        #             external SQL procedures for the current session.
        >>> set_session_param('function_trace', ["'diag,3'", 'titanic'])
        True

        # Example 17: Enables the validation of JSON data on INSERT operations.
        >>> set_session_param('json_ignore_errors', 'ON')
        True

        # Example 18: Sets the database search path for the SCRIPT execution in the SessionTbl.SearchUIFDBPath column.
        >>> set_session_param('SEARCHUIFDBPATH', 'dbc, alice')
        True

        # Example 19: Sets the read-only locking severity for all SELECT requests made against nontemporal tables,
        #             whether they are outer SELECT requests or subqueries, in the current session to READ regardless
        #             of the setting for the DBS Control parameter AccessLockForUncomRead.
        #             Note: SR and SERIALIZABLE are synonyms.
        >>> set_session_param('TRANSACTION_ISOLATION_LEVEL', 'SR')
        True

        # Example 20: This example uses the PROXYROLE name:value pair in a query band to set the proxy
        #             role in a trusted session to a specific role.
        >>> set_session_param('query_band', ["'PROXYUSER=fred;PROXYROLE=administration;'", 'SESSION'])
        True

        # Example 21: Allows you to specify a custom UDF search path. When you execute a UDF,
        #             Vantage searches this path first, before looking in the default Vantage
        #             search path for the UDF.
        >>> set_session_param('udfsearchpath', ["alice, SYSLIB, TD_SYSFNLIB", 'bitor'])
        True
    """
    # Validate argument types
    function_args = []
    function_args.append(["name", name, False, str, True])
    function_args.append(["value", value, False, (int, str, float, list), False])
    _Validators._validate_function_arguments(function_args)

    # Validate Permitted values for session parameter name.
    permitted_session_parameters = [key.name for key in SessionParamsSQL]
    _Validators._validate_permitted_values(arg=name,
                                           permitted_values=permitted_session_parameters,
                                           arg_name='name',
                                           case_insensitive=True,
                                           includeNone=False)

    if not isinstance(value, list):
        value = [value]

    # Before setting the session, first extract the session parameters
    # and store it in buffer. This helps while unsetting the parameter.
    result = execute_sql('help session')
    data = dict(zip(
        [param[0] for param in result.description],
        [value for value in next(result)]
    ))
    _InternalBuffer.add(session_params=_TDSessionParams(data))
    # Store function name of 'DEBUG_FUNCTION' used.
    _InternalBuffer.add(function_name=value[0] if name.upper() == 'DEBUG_FUNCTION' else '')

    # Set the session parameter.
    execute_sql(getattr(SessionParamsSQL, name.upper()).value.format(*value))
    return True


def unset_session_param(name):
    """
    DESCRIPTION:
        Function to unset the session parameter.

    PARAMETERS:
        name:
            Required Argument.
            Specifies the parameter to unset for the session.
            Permitted Values: timezone, account, calendar, collation,
                              database, dataform, character_set_unicode,
                              debug_function, isolated_loading, function_trace,
                              json_ignore_errors, query_band
            Type: str

    Returns:
        True, if successfully unsets the session parameter.

    RAISES:
    ValueError, teradatasql.OperationalError

    EXAMPLES:
        # Example 1: Unset session's time zone to previous time zone.
        >>> set_session_param('timezone', "'GMT+1'")
        True
        >>> unset_session_param("timezone")
        True

    """
    # Validate argument types
    function_args = []
    function_args.append(["name", name, True, str, True])
    _Validators._validate_function_arguments(function_args)

    # Validate Permitted values for session parameter name which can be unset.
    permitted_session_parameters = [key.name for key in SessionParamsPythonNames] +\
                                   ["character_set_unicode", "debug_function",
                                    "isolated_loading", "function_trace",
                                    "json_ignore_errors", "query_band"]
    _Validators._validate_permitted_values(arg=name,
                                           permitted_values=permitted_session_parameters,
                                           arg_name='name',
                                           case_insensitive=True,
                                           includeNone=False)

    # Check whether session param is set or not first.
    session_params = _InternalBuffer.get('session_params')
    if session_params is None:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "unset_session_param", "Set the parameter before unsetting it.")
        raise TeradataMlException(error_msg, msg_code)
    if name.upper() == "DEBUG_FUNCTION":
        # If unset param is debug_function, then check if any  function name is available to unset.
        if _InternalBuffer.get('function_name') in ('', None):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED, 
                                     "unset_session_param",
                                     "Set the parameter before unsetting it."),
                MessageCodes.FUNC_EXECUTION_FAILED)
    # unset_values stores params which are not available in _InternalBuffer, to unset create a dictionary
    # with param as key and unset param as value
    # TODO: Unset for ISOLATED_LOADING should revert to previous behaviour, but we are setting it to NO.
    #  This is not correct if  ISOLATED_LOADING was CONCURRENT before setting it to NO.
    unset_values = {"CHARACTER_SET_UNICODE": "OFF", "DEBUG_FUNCTION": [_InternalBuffer.get('function_name'), "OFF"],
                    "ISOLATED_LOADING": "NO", "FUNCTION_TRACE": "SET SESSION FUNCTION TRACE OFF",
                    "JSON_IGNORE_ERRORS": "OFF", "QUERY_BAND": ["", "SESSION"]}

    # If 'name' in unset_values unset the params
    if name.upper() in unset_values:
        # When name is 'FUNCTION_TRACE' unset_values already have query for that, use execute_sql on that.
        if name.upper() == "FUNCTION_TRACE":
            execute_sql(unset_values[name.upper()])
        # When name is other than 'FUNCTION_TRACE' use value and key of unset_values to unset param.
        else:
            set_session_param(name, unset_values[name.upper()])
        return True

    previous_value = "{}".format(session_params[getattr(SessionParamsPythonNames, name.upper()).value]) \
        if name.upper() != 'TIMEZONE' else "'{}'".format(
        session_params[getattr(SessionParamsPythonNames, name.upper()).value])

    if name.upper() == "ACCOUNT":
        previous_value = [previous_value, 'SESSION']
    set_session_param(name, previous_value)

    return True


class _Authorize:
    """ Parent class to either provide or revoke access on database objects. """
    _property = None

    def __init__(self, objects, database=None):
        """
        DESCRIPTION:
            Constructor for creating Authorize object.

        PARAMETERS:
            objects:
                Required Argument.
                Specifies the name(s) of the database objects to be authorized.
                Types: str OR list of str OR AccessType Enum

            database:
                Optional Argument.
                Specifies the name of the database to grant or revoke access.
                Types: str

        RETURNS:
            Object of _Authorize.

        RAISES:
            None

        EXAMPLES:
            >>> auth = _Authorize('vfs_v1')
        """
        # Store the objects here. Then use this where ever required.
        self._is_enum = issubclass(objects, enum.Enum)
        self._objects = objects
        self._access_method = self.__class__.__name__.upper()
        self.database = database

    def read(self, user):
        """
        DESCRIPTION:
            Authorize the read access.
            Note:
                One must have admin access to give read access to other "user".

        PARAMETERS:
            user:
                Required Argument.
                Specifies the name of the user to have read only access.
                Types: str

        RETURNS:
            bool.

        RAISES:
            None

        EXAMPLES:
            >>> _Authorize('repo').read('BoB')
        """
        return self._apply_access(user, 'read', 'SELECT')

    def write(self, user):
        """
        DESCRIPTION:
            Authorize the write access.
            Note:
                One must have admin access to give write access to other "user".

        PARAMETERS:
            user:
                Required Argument.
                Specifies the name of the user to have write only access.
                Types: str

        RETURNS:
            bool.

        RAISES:
            None

        EXAMPLES:
            >>> _Authorize('repo').write('BoB')
        """
        return self._apply_access(user, 'write', 'INSERT, UPDATE, DELETE')
    
    def _apply_access(self, user, operation, access_type):
        """
        DESCRIPTION:
            Internal function to grant or revoke access.

        PARAMETERS:
            user:
                Required Argument.
                Specifies the name of the user to have access.
                Types: str

            operation:
                Required Argument.
                Specifies the operation to perform.
                Permitted Values: 'read', 'write'
                Types: str

            access_type:
                Required Argument.
                Specifies the type of access to grant or revoke.
                Permitted Values: 
                    * 'SELECT' for read 
                    * 'INSERT, UPDATE, DELETE' for write
                Types: str

        RETURNS:
            bool, True if access is granted or revoked successfully.

        RAISES:
            TeradataMlException, OperationalError

        EXAMPLES:
            >>> _Authorize('repo')._apply_access('BoB', 'read', 'SELECT')
        """
        sql_objects = UtilFuncs._as_list(self._objects) if not self._is_enum else \
                      getattr(self._objects, operation).value

        for obj in sql_objects:
            if self._is_enum:
                sql = obj.format(
                    grant_revoke_=self._access_method,
                    database_=self.database,
                    to_from_=self._property,
                    user_=user
                )
            else:
                sql = "{} {} ON {} {} {}".format(
                    self._access_method, access_type, obj, self._property, user
                )
            execute_sql(sql)
        return True

    def read_write(self, user):
        """
        DESCRIPTION:
            Authorize the read and write access.
            Note:
                One must have admin access to give read and write access to other "user".

        PARAMETERS:
            user:
                Required Argument.
                Specifies the name of the user to have read and write access.
                Types: str

        RETURNS:
            bool.

        RAISES:
            None

        EXAMPLES:
            >>> _Authorize('repo').read_write('BoB')
        """
        self.read(user)
        return self.write(user)


class Grant(_Authorize):
    """ Class to grant access to tables."""
    _property = "TO"


class Revoke(_Authorize):
    """ Class to revoke access from tables."""
    _property = "FROM"
