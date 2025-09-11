# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: mounika.kotha@teradata.com
Secondary Owner:

This is a common class to include common functionality required
by other classes which can be reused according to the need.

Add all the common functions in this class like creating temporary table names, getting
the datatypes etc.
"""
import datetime
import json
import os
import re
import time
import uuid, hashlib
import warnings
from functools import reduce
from inspect import getsource
from math import floor

import requests
import sqlalchemy
from numpy import number
from sqlalchemy import Column, MetaData, Table
from sqlalchemy.exc import OperationalError as sqlachemyOperationalError
from teradatasql import OperationalError
from teradatasqlalchemy.dialect import dialect as td_dialect
from teradatasqlalchemy.dialect import preparer
from teradatasqlalchemy.types import (BIGINT, BLOB, BYTE, BYTEINT, CHAR, CLOB,
                                      DATE, DECIMAL, FLOAT, INTEGER, NUMBER,
                                      SMALLINT, TIME, TIMESTAMP, VARBYTE,
                                      VARCHAR, _TDType)

from teradataml import _version
from teradataml.common import td_coltype_code_to_tdtype
from teradataml.common.constants import (HTTPRequest, PTITableConstants,
                                         PythonTypes, SQLConstants,
                                         TeradataConstants,
                                         TeradataReservedKeywords, TeradataTableKindConstants,
                                         TeradataTypes)
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.sqlbundle import SQLBundle
from teradataml.common.warnings import (OneTimeUserWarning,
                                        VantageRuntimeWarning)
from teradataml.context import context as tdmlctx
from teradataml.options.configure import configure
from teradataml.options.display import display
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators


class UtilFuncs():
    def _get_numeric_datatypes(self):
        """
        Returns the numeric data types used in Teradata Vantage
        **From : https://www.info.teradata.com/HTMLPubs/DB_TTU_16_00/
        index.html#page/General_Reference/B035-1091-160K/psa1472241434371.html

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of numeric data types used in Teradata Vantage
        """
        return [BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT, NUMBER]

    def _get_timedate_datatypes(self):
        """
        Returns a list of TimeDate data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of TimeDate data types used in Teradata Vantage
        """
        return [TIMESTAMP, DATE, TIME]

    def _get_character_datatypes(self):
        """
        Returns a list of Character data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Character data types used in Teradata Vantage
        """
        return [CHAR, VARCHAR, CLOB]

    def _get_byte_datatypes(self):
        """
        Returns a list of byte like data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Byte data types used in Teradata Vantage
        """
        return [BYTE, VARBYTE, BLOB]

    def _get_categorical_datatypes(self):
        """
        Returns a list of containing Character and TimeDate data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Character and TimeDate data types used in Teradata Vantage
        """
        return list.__add__(self._get_character_datatypes(), self._get_timedate_datatypes())

    def _get_all_datatypes(self):
        """
        Returns a list of Character, Numeric and TimeDate data types.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of Character, Numeric and TimeDate data types used in Teradata Vantage
        """
        return list.__add__(self._get_categorical_datatypes(), self._get_numeric_datatypes())

    def _get_db_name_from_dataframe(self, df):
        """
        DESCRIPTION:
            Function to get database name from teradataml DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the input teradataml DataFrame.
                Types: teradataml DataFrame

        RETURNS:
            Database name.

        RAISES:
            None.

        EXAMPLES:
            UtilFuncs()._get_db_name_from_dataframe(df)
        """
        if df._table_name is None:
            from teradataml.dataframe.dataframe_utils import DataFrameUtils
            df._table_name = DataFrameUtils()._execute_node_return_db_object_name(df._nodeid,
                                                                                  df._metaexpr)

        db_name = self._extract_db_name(df._table_name)
        if db_name is None or db_name == "":
            # Extract db_name from SQLAlchemy Engine URL.
            if 'DATABASE' in tdmlctx.get_context().url.query:
                db_name = tdmlctx.get_context().url.query['DATABASE']
            else:
                db_name = tdmlctx._get_current_databasename()
        else:
            db_name = db_name.replace("\"", "")

        return db_name

    @staticmethod
    def _get_valid_aggregate_operations():
        """
        Returns the list of valid aggregate operations on Teradata Vantage

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of valid aggregate operations possible on Teradata Vantage
        """
        return ['count', 'kurtosis', 'max', 'mean', 'median', 'min', 'percentile', 'skew', 'std',
                'sum', 'unique', 'var']

    @staticmethod
    def _get_valid_time_series_aggregate_operations():
        """
        Returns the list of valid aggregate operations on Teradata Vantage

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            List of valid aggregate operations possible on Teradata Vantage
        """
        return ['bottom', 'bottom with ties', 'delta_t', 'first', 'last', 'mad', 'mode', 'top',
                'top with ties']

    @staticmethod
    def _generate_temp_table_name(databasename=None, user=None, prefix=None,
                                  use_default_database=False, gc_on_quit=True, quote=True,
                                  table_type=TeradataConstants.TERADATA_VIEW):
        """
        DESCRIPTION:
            Function to return the random string for temporary table names.

        PARAMETERS:
            databasename:
                Optional Argument.
                Specifies the database name to use while generating the script.
                Types: str

            user:
                Optional Argument.
                Specifies the current username or database name on which user logged on to Teradata Vantage.
                Types: str

            prefix:
                Optional Argument.
                Specifies the prefix of the module from which table/view name is requested.
                Types: str

            use_default_database:
                Optional Argument.
                Specifies whether to create a table or view in the default database when
                "databasename" is not provided.
                Default value: False
                Types: str

            gc_on_quit:
                Optional Argument.
                Specifies whether to garbage collect the table/view with the generated name
                at the end of the session.
                When 'True', the objects created with the generated name will be garbage
                collected at the end of the session.
                Default value: True
                Types: bool

            quote:
                Optional Argument.
                Specifies whether to quote the database name and table/view name.
                When 'True', quotes are added around the database name and the table/view name.
                Default value: True
                Types: bool

            table_type:
                Optional Argument.
                Specifies the type of objects - table or view.
                Default value: TeradataConstants.TERADATA_VIEW
                Types: TeradataConstant

        RETURNS:
            Temporary table name.

        RAISES:

        EXAMPLES:
            >>> new_table_name = UtilFuncs._generate_temp_table_name(user='tdqg', prefix="from_pandas")
            >>> new_table_name = UtilFuncs._generate_temp_table_name(user='tdqg', prefix="from_pandas",
                                                                 table_type = TeradataConstants.TERADATA_VIEW)
            >>> new_table_name = UtilFuncs._generate_temp_table_name(user='tdqg', prefix="from_pandas",
                                                                 table_type = TeradataConstants.TERADATA_TABLE)
            # Example when use_short_object_name is set to True
            >>> from teradataml.options.configure import configure
            >>> configure.use_short_object_name = True
            >>> new_table_name = UtilFuncs._generate_temp_table_name(user='tdqg', prefix="from_pandas")

        Output:
            tdml_temp_table__1517501990393350 (or)
            tdqg.tdml_temp_table__1517501990393350 (or)
            tdml_temp_table__from_pandas_1517501990393350 (or)
            tdqg.tdml_temp_table__from_pandas_1517501990393350 (or)
            ml__1749637109887272
        """
        # Number of seconds since  Jan 1, 1970 00:00:00
        timestamp = time.time()
        use_short_name = configure.use_short_object_name
        tabname = "ml_"
        random_string = "{}{}".format(floor(timestamp / 1000000),
                                      floor(timestamp % 1000000 * 1000000 +
                                            int(str(uuid.uuid4().fields[-1])[:10])))
        
        # Append prefix only if use_short_object_name is False and prefix is provided.
        if (not use_short_name) and (prefix is not None):
            tabname = "{}_{}".format(tabname, prefix)
        # Append prefix "tdml" when use_short_object_name is True and random string is of length 15.
        elif use_short_name and (len(random_string)==15):
            tabname = "tdml"

        tabname = "{}_{}".format(tabname, random_string)

        # ELE-6710 - Use database user associated with the current context for volatile tables.
        if table_type == TeradataConstants.TERADATA_VOLATILE_TABLE:
            from teradataml.context.context import _get_user
            tabname = "\"{}\".\"{}\"".format(_get_user(), tabname)
            return tabname

        if (not use_short_name) and (configure.temp_object_type == TeradataConstants.
                                     TERADATA_VOLATILE_TABLE):
            from teradataml.context.context import _get_user
            return "\"{}\".\"{}_{}\"".format(_get_user(), "vt", tabname)

        if use_default_database and databasename is None:
            tabname = "\"{}\".\"{}\"".format(tdmlctx._get_context_temp_databasename(
                table_type=table_type), tabname)

        if user is not None:
            tabname = "\"{}\".\"{}\"".format(user, tabname)

        if databasename is not None:
            tabname = "\"{}\".\"{}\"".format(databasename, tabname)

        # Enable garbage collection for the temporary view & table created while transformations.
        if gc_on_quit:
            GarbageCollector._add_to_garbagecollector(tabname, table_type)

        return tabname

    @staticmethod
    def _generate_temp_script_name(database_name=None, prefix=None, use_default_database=True,
                                   gc_on_quit=True, quote=True,
                                   script_type=TeradataConstants.TERADATA_SCRIPT,
                                   extension=None):
        """
        DESCRIPTION:
            Function to return the random string for temporary script names.

        PARAMETERS:
            database_name:
                Optional Argument:
                Specifies the database name on which user logged on to Teradata Vantage.
                Types: str

            prefix:
                Optional Argument.
                Specifies the prefix of the module or function from which script name is requested.
                Types: str

            use_default_database:
                Optional Argument.
                Specifies whether the script will be installed in the default/connected database.
                When 'True', the current/default database name will be used for generating the name.
                Default value: True
                Types: bool

            gc_on_quit:
                Optional Argument.
                Specifies whether to garbage collect the object with the generated name
                at the end of the session.
                When 'True', the objects created with the generated name will be garbage
                collected at the end of the session.
                Default value: True
                Types: bool

            quote:
                Optional Argument.
                Specifies whether to quote the database name and script name.
                When 'True', quotes are added around the database name and the script name.
                Default value: True
                Types: bool

            script_type:
                Optional Argument.
                Specifies the type of script.
                Default value: TeradataConstants.TERADATA_SCRIPT
                Types: TeradataConstant

            extension:
                Optional Argument.
                Specifies the extension of the script.
                Default value: None
                Types: str

        RETURNS:
            Temporary script name.

        RAISES:
            None.

        EXAMPLES:
            new_script_name = UtilFuncs._generate_temp_script_name(use_default_database=True,
                                                                  script_type = TeradataConstants.TERADATA_SCRIPT)
        """
        # NOTE:
        # 1. There can be other types of scripts going forward which may require their own type (like for Apply).
        #    Hence, we have a 'script_type' argument which currently has only one possible value.
        # 2. Currently map_row and map_partition use only default database, but going forward this can be changed
        #    to use other databases for installation of script, using 'database_name'.

        timestamp = time.time()
        script_name = "ml_"

        random_string = "{}{}".format(floor(timestamp / 1000000),
                                      floor(timestamp % 1000000 * 1000000 +
                                            int(str(uuid.uuid4().fields[-1])[:10])))

        if prefix is not None:
            script_name = "{}_{}".format(script_name, prefix)

        script_name = "{}_{}".format(script_name, random_string)

        if extension is not None:
            script_name = "{}.{}".format(script_name, extension)

        dbname_to_use = tdmlctx._get_current_databasename()
        if not use_default_database and database_name is not None:
            dbname_to_use = database_name

        script_name = "\"{}\".\"{}\"".format(dbname_to_use, script_name)

        # Enable garbage collection for the temporary script created.
        if gc_on_quit:
            GarbageCollector._add_to_garbagecollector(script_name, script_type)

        return script_name

    @staticmethod
    def _serialize_and_encode(obj):
        """
        DESCRIPTION:
            Internal utility to serialize any Python object (including functions)
            using dill and encode using base64.

        PARAMETERS:
            obj:
                Specifies the Python object to serialize and encode.
                Types: object

        RAISES:
            None.

        RETURNS:
            An encoded byte string representing the serialized object 'obj'.

        EXAMPLES:
            >>> # Serializing and encoding a literal value
            >>> literal = UtilFuncs._serialize_and_encode('literal value')
            >>> # Serializing and encoding a function
            >>> def udf(a, b): return a + b
            >>> func = UtilFuncs._serialize_and_encode(udf)
        """
        from base64 import b64encode as base64_b64encode

        from dill import dumps as dill_dumps

        return base64_b64encode(dill_dumps(obj, recurse=True))

    @staticmethod
    def _quote_table_names(table_name):
        """
        Quotes table names or view names.
        If the table name is in the format schema.table_name, it will quote the
        schema name and table name.

        Example:
            mytab -> "my.tab"
            schema.mytable -> "schema"."my.tab"
            myview -> "myview"

        PARAMETERS:
            table_name - The name of table or view. The name can include the schema (e.g. schema.table_name)

        RETURNS:
            returns the quoted table name.

        RAISES:

        EXAMPLES:
            table_name = UtilFuncs._quote_table_names(table_name)

        """
        table_name_list = re.findall('".+?"', table_name)
        if table_name_list:
            for i in range(0, len(table_name_list)):
                if not (table_name_list[i].startswith("\"") and table_name_list[i].endswith("\"")):
                    table_name_list[i] = UtilFuncs._teradata_quote_arg(table_name_list[i], "\"", False)

            return ".".join(table_name_list)
        else:
            return "\"{}\"".format(table_name)

    @staticmethod
    def _execute_ddl_statement(ddl_statement):
        """
        Executes a DDL statment and commits transaction
        This is an internal function.

        PARAMETERS:
            ddl_statement - Teradata DDL statement.

        RETURNS:

        RAISES:
            Database error if an error occurred while executing the DDL statement.

        EXAMPLES:
            UtilFuncs._execute_ddl_statement('create table mytab (col1 int, col2 varchar(20))')

        """
        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()
        # Let's execute our DDL statement with escape function '{fn teradata_fake_result_sets}'
        # offered by teradatasql driver. This function will allow us catch any warnings thrown
        # from the Vantage. Hence, executing the DDL statement with this escape function.
        ddl_statement = "{fn teradata_fake_result_sets} " + ddl_statement

        if tdmlctx.td_connection is not None:
            cursor = None
            try:
                conn = tdmlctx.td_connection.connection
                cursor = conn.cursor()
                cursor.execute(ddl_statement)

                # Warnings are displayed when the "suppress_vantage_runtime_warnings" attribute is set to 'False'.
                if not display.suppress_vantage_runtime_warnings:
                    # Fetch the result set just to check whether we have received any warnings or not.
                    warnRes = cursor.fetchone()
                    # Check for "display.suppress_vantage_runtime_warnings" set to 'True'.
                    # Check for warning code and warning message
                    # warnRes[5] contains the Warning Code
                    # warnRes[6] contains the actual Warning Message
                    if warnRes[5] != 0 and warnRes[6] != "":
                        # Raise warning raised from Vantage as is.
                        warnings.simplefilter("always")
                        msg_ = Messages.get_message(MessageCodes.VANTAGE_WARNING)
                        warnings.warn(msg_.format(warnRes[5], warnRes[6]), VantageRuntimeWarning)

                conn.commit()
            except:
                # logger.debug("Got exception while executing ({0})".format(teradataSQL))
                raise
            finally:
                if cursor:
                    cursor.close()
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                      MessageCodes.CONNECTION_FAILURE)

    @staticmethod
    def _execute_query(query, fetchWarnings=False, expect_none_result=False):
        """
        Retrieves result set data from query.

        PARAMETERS:
            query:
                Required Argument.
                Specifies the SQL query to execute.
                Types: str

            fetchWarnings:
                Optional Argument.
                Specifies a flag that decides whether to raise warnings thrown from Vanatge or not.
                Default Values: False
                Types: bool

            expect_none_result:
               Optional Argument.
               When set to True, warnings will not be fetched and only result set is fetched.
               Returns None if no result set is received from the backend.
               When fetchWarnings is set to True this option is ignored.
               Default Values: False
               Types: bool

        RETURNS:
            Returns only result set from query if 'fetchWarnings' is False. If set to True, then
            return result set and columns for the result set.

        RAISES:
            Database error if an error occurred while executing query.

        EXAMPLES:
            result = UtilFuncs._execute_query('select col1, col2 from mytab')
            result = UtilFuncs._execute_query('help column mytab.*')

            result = UtilFuncs._execute_query('help column mytab.*')

            # Execute the stored procedure using fetchWarnings.
            UtilFuncs._execute_query("call SYSUIF.INSTALL_FILE('myfile',
                                                             'filename.py',
                                                             'cb!/Documents/filename.py')",
                                                              True, False)

            # Execute the stored procedure without fetchWarnings but still needs resultsets.
            UtilFuncs._execute_query("call SYSUIF.list_base_environments()", False, True)

        """
        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()

        if fetchWarnings:
            # Let's execute our DDL statement with escape function '{fn teradata_fake_result_sets}'
            # offered by teradatasql driver. This function will allow us catch any warnings thrown
            # from the Vantage. Hence, executing the DDL statement with this escape function.
            query = "{fn teradata_fake_result_sets} " + query

        if tdmlctx.td_connection is not None:
            cursor = None
            try:
                conn = tdmlctx.td_connection.connection
                cursor = conn.cursor()
                cursor.execute(query)

                if fetchWarnings:
                    # Fetch the result set just to check whether we have received any warnings or not.
                    warnRes = cursor.fetchone()
                    # Check for warning code and warning message
                    # warnRes[5] contains the Warning Code
                    # warnRes[6] contains the actual Warning Message
                    if (warnRes[5] != 0 and warnRes[6] != "") and not display.suppress_vantage_runtime_warnings:
                        # Raise warning raised from Vantage as is.
                        warnings.simplefilter("always")
                        msg_ = Messages.get_message(MessageCodes.VANTAGE_WARNING)
                        warnings.warn(msg_.format(warnRes[5], warnRes[6]), VantageRuntimeWarning)

                    cursor.nextset()

                    return cursor.fetchall(), [col_desc[0] for col_desc in cursor.description]

                # This check may be removed if DBS side stored procedure are fixed to return empty
                # result sets with columns in cursor.description
                elif expect_none_result:
                    cursor.nextset()
                    # Some stored procedure returns None if result set has no rows.
                    # cannot use fetchall call in such cases. If SPs are fixed to support result sets with zero
                    # rows then below call may be removed in the future.
                    if cursor.rowcount <= 0:
                        return None, None
                    return cursor.fetchall(), [col_desc[0] for col_desc in cursor.description]

                else:
                    return cursor.fetchall()
            except:
                raise
            finally:
                if cursor:
                    cursor.close()
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                      MessageCodes.CONNECTION_FAILURE)

    @staticmethod
    @collect_queryband(queryband='CreateView')
    def _create_view(view_name, query, lock_rows=False):
        """
        Create a view from the given query.

        PARAMETERS:
            view_name - View name
            query - SQL query
            lock_rows - When set to True, teradataml DataFrame locks the corresponding row(s)
                        in underlying table(s) while accessing the data. Otherwise,
                        teradataml DataFrame access the data without locking the rows.
                        Default is False.

        RAISES

        RETURNS:
            True if success.

        EXAMPLES:
            UtilFuncs._create_view(view_name, "select * from table_name")
        """

        crt_view = SQLBundle._build_create_view(view_name, query, lock_rows)
        try:
            UtilFuncs._execute_ddl_statement(crt_view)
            return True
        except:
            raise

    @staticmethod
    @collect_queryband(queryband='CreateTbl')
    def _create_table(table_name, query, volatile=False):
        """
        Create a table from the given query.

        PARAMETERS:
            table_name - Fully qualified quoted table name.
            query - SQL query
            volatile - Specifies whether to create volatile table or not.
                       When set to True, volatile table is created, otherwise
                       permanent table is created.

        RAISES

        RETURNS:
            True if success, false if fails

        EXAMPLES:
            UtilFuncs._create_table('"dbname"."table_name"', "select * from table_name")
        """

        crt_table = SQLBundle._build_create_table_with_data(table_name, query)
        if volatile:
            crt_table = SQLBundle._build_create_volatile_table_with_data(table_name, query)

        UtilFuncs._execute_ddl_statement(crt_table)
        return True

    @staticmethod
    def _get_non_null_counts(col_names, table_name):
        """
        Returns a list of non-null count for each column in col_names from table table_name.

        PARAMETERS:
            col_names - list of column names for table table_name.
            table_name - table name.

        RETURNS:
            returns a list of non-null counts for each column.

        RAISES:

        EXAMPLES:
            UtilFuncs._get_non_null_counts(col_names, 'mytab')

        """
        count_col_names = ["count(\"{0}\")".format(name) for name in col_names]
        select_count = "select {0} from {1}".format(", ".join(count_col_names), table_name)
        result = UtilFuncs._execute_query(select_count)
        return [str(i) for i in result[0]]

    @staticmethod
    @collect_queryband(queryband='CreateVolaTbl')
    def _get_volatile_table(query, with_data=False):
        """
        Creates a volatile table as query.
        If with_data is True, creates the volatile table with data.
        Else, creates the volatile table without data.

        PARAMETERS:
            query - The query used to create the volatile table.
            with_data(optional) - True, creates table with data.
                                  False, creates table without data. Default is False

        RETURNS:
            returns the temporary name of the volatile table.

        RAISES:
            Database error if an error occurred while creating the volatile table.

        EXAMPLES:
            UtilFuncs._get_volatile_table('select col1, col2, from mytab')
            UtilFuncs._get_volatile_table('select col1, col2, from mytab', with_data=True)

        """
        vtab_name = UtilFuncs._generate_temp_table_name()
        if with_data:
            create_vtab_ddl = SQLBundle._build_create_volatile_table_with_data(vtab_name, query)
        else:
            create_vtab_ddl = SQLBundle._build_create_volatile_table_without_data(vtab_name, query)
        UtilFuncs._execute_ddl_statement(create_vtab_ddl)
        return vtab_name

    @staticmethod
    def _drop_table(table_name, check_table_exist=True, purge_clause=None):
        """
        Drops a table.

        PARAMETERS:
            table_name - The table to drop.
            check_table_exist - Checks if the table exist before dropping the table.
            purge_clause - Specifies string representing purge clause to be appended to drop table query.

        RETURNS:
            True - if the table is dropped.

        RAISES:
            Database error if an error occurred while dropping the table.

        EXAMPLES:
            UtilFuncs._drop_table('mytab')
            UtilFuncs._drop_table('mytab', check_table_exist = False)
            UtilFuncs._drop_table('mydb.mytab', check_table_exist = False)
            UtilFuncs._drop_table("mydb"."mytab", check_table_exist = True)
            UtilFuncs._drop_table("my_lake"."my_db"."my_tab", purge_clause='PURGE ALL')
            UtilFuncs._drop_table("my_lake"."my_db"."my_tab", purge_clause='NO PURGE')

        """
        drop_tab = SQLBundle._build_drop_table(table_name, purge_clause)
        if check_table_exist is True:
            helptable = UtilFuncs._get_help_tablename(table_name)
            if helptable:
                UtilFuncs._execute_ddl_statement(drop_tab)
                return True
        else:
            UtilFuncs._execute_ddl_statement(drop_tab)
            return True

        return False

    @staticmethod
    def _drop_view(view_name, check_view_exist=True):
        """
        Drops a view.

        PARAMETERS:
            view_name - The view to drop.
            check_view_exist - Checks if the view exist before dropping the view.

        RETURNS:
            True - if the view is dropped.

        RAISES:
            Database error if an error occurred while dropping the view.

        EXAMPLES:
            UtilFuncs._drop_view('myview')
            UtilFuncs._drop_view('myview', check_view_exist = False)
            UtilFuncs._drop_view('mydb.myview', check_view_exist = False)
            UtilFuncs._drop_view("mydb"."myview", check_view_exist = True)
        """
        drop_view = SQLBundle._build_drop_view(view_name)
        if check_view_exist is True:
            viewdetails = UtilFuncs._get_help_viewname(view_name)
            if viewdetails:
                UtilFuncs._execute_ddl_statement(drop_view)
                return True
        else:
            UtilFuncs._execute_ddl_statement(drop_view)
            return True

        return False

    @staticmethod
    def _delete_script(script_name, file_type=TeradataConstants.TERADATA_SCRIPT,
                       check_script_exist=True):
        """
        DESCRIPTION:
            Function to remove a user-installed file/script.

        PARAMETERS:
            script_name:
                Required Argument.
                Specifies the name of the script to remove.
                Types: str

            file_type:
                Optional Argument.
                Specifies the type of the file to remove, whether it is from
                Enterpise (TeradataConstants.TERADATA_SCRIPT) or from Lake
                (TeradataConstants.TERADATA_APPLY).
                Default value: TeradataConstants.TERADATA_SCRIPT
                Permitted Values: TeradataConstants.TERADATA_SCRIPT, TeradataConstants.TERADATA_APPLY
                Types: TeradataConstants

            check_script_exist:
                Required Argument. Applicable only when "file_type" is
                TeradataConstants.TERADATA_SCRIPT. Ignored otherwise.
                Specifies whether to check if the script exists or not before removing it.
                When 'True', the presence of the script will be check for.
                Default value: True
                Types: bool

        RETURNS:
            True - if the script is removed.

        RAISES:
            Database error if an error occurred while dropping the view.

        EXAMPLES:
            UtilFuncs._delete_script('myview')
            UtilFuncs._delete_script('myview', check_script_exist = False)
            UtilFuncs._delete_script('mydb.myview', check_script_exist = False)
            UtilFuncs._delete_script("mydb"."myview", check_script_exist = True)
        """
        dbname = UtilFuncs._teradata_unquote_arg(UtilFuncs._extract_db_name(script_name),
                                                 quote='"')
        script_alias = UtilFuncs._teradata_unquote_arg(UtilFuncs._extract_table_name(script_name),
                                                       quote='"')
        current_db = tdmlctx._get_current_databasename()

        if file_type == TeradataConstants.TERADATA_SCRIPT:
            script_exists = False
            if check_script_exist:
                query = "select count(*) from dbc.tablesV " \
                        "where databasename = '{}' and tablename = '{}' " \
                        "and tablekind = 'Z'".format(dbname, script_alias)

                script_exists = True if UtilFuncs._execute_query(query)[0][0] == 1 else False

            if script_exists or not check_script_exist:
                try:
                    # If the database is not the current/default database, we need to
                    # set that as the session database to be able to remove the file.
                    if dbname and dbname.lower() != current_db.lower():
                        execute_sql('database {}'.format(dbname))

                    # Strip off the file extension and extract the base name.
                    from pathlib import Path
                    script_base_name = Path(script_alias).stem

                    # Remove the file.
                    remove_file(script_base_name, force_remove=True, suppress_output=True)
                    return True
                except:
                    raise
                finally:
                    # Reset the database if it was set to something else.
                    if dbname and dbname.lower() != current_db.lower():
                        execute_sql('database {}'.format(current_db))
        else:
            # environment name and file name are separated by '::'
            # like <user_env_name(str)>::<apply_script_name>
            env_name, script_alias = script_alias.split('::')

            from teradataml.scriptmgmt.lls_utils import get_env
            env = get_env(env_name)
            env.remove_file(script_alias, suppress_output=True)
            return True

    @staticmethod
    def _get_help_vtablenames():
        """
        Function to get list of volatile tables.

        RETURNS:
            List of volatile tablenames.

        EXAMPLES:
            UtilFuncs._get_help_vtablenames()
        """
        vtables = UtilFuncs._execute_query(SQLBundle._build_help_volatile_table(), fetchWarnings=True)
        if vtables and vtables[0] and vtables[1]:
            rows, columns = vtables
            key = TeradataTableKindConstants.VOLATILE_TABLE_NAME.value
            # Find the index of the column matching the table name
            col_idx = columns.index(key)
            return [row[col_idx].strip() for row in rows if row[col_idx]]
        return []

    @staticmethod
    def _get_help_viewname(view_name):
        """
        Function to get help of the view.

        PARAMETERS:
            view_name - The name of the view.

        RETURNS:
            The help information of the view specified by view_name.

        EXAMPLES:
            UtilFuncs._get_help_viewname(myview)
        """
        return UtilFuncs._execute_query(SQLBundle._build_help_view(view_name))

    @staticmethod
    def _get_help_tablename(table_name):
        """
        Function to get help of the table.

        PARAMETERS:
            table_name - The name of the table.

        RETURNS:
            The help information of the table specified by table_name.

        EXAMPLES:
            UtilFuncs._get_help_tablename(mytable)
        """
        return UtilFuncs._execute_query(SQLBundle._build_help_table(table_name))

    @staticmethod
    def _get_help_datalakename(datalake_name):
        """
        Function to get help of the datalake.

        PARAMETERS:
            datalake_name - The name of the datalake.

        RETURNS:
            The help information of the datalake specified by datalake_name.

        EXAMPLES:
            UtilFuncs._get_help_datalakename(mydatalake)
        """
        return UtilFuncs._execute_query(SQLBundle._build_help_datalake(datalake_name))

    @staticmethod
    def _get_select_table(table_name):
        """
        Function to get a table if exists.

        PARAMETERS:
            table_name - Table name to check if exists in the database.

        RETURNS:
            Table name in a list.

        EXAMPLES:
            UtilFuncs._get_select_table('mytab')

        """
        table = UtilFuncs._execute_query(SQLBundle._build_select_table_name(table_name))
        if table:
            return table[0]
        return []

    @staticmethod
    def _describe_column(metadata, to_type=None):
        """
        This is an internal function to retrieve
        column names and column types for the table or view.

        PARAMETERS:
            metadata:
                The result set from the HELP COLUMN command.

        RETURNS:
            A list of tuples (column_names, column_types).

        RAISES:
            Database errors if a problem occurs while trying to retrieve the column information.

        EXAMPLES:
            column_names_and_types = UtilFuncs._describe_column()

        """
        column_names_and_types = []
        for row in metadata:
            # logger.debug("Retrieving Teradata type for {0}".format(row[31]))
            # row[31] corresponds to 'Column Dictionary Name' column in the result of 'HELP COLUMN' SQL commands result.
            column_name = row[31]
            # We also need to check if the column is a TD_TIMEBUCKET column, in which case we can ignore it.
            # We do so by checking the column name, and row[48] which corresponds to the 'Time Series Column Type'
            # column in the 'HELP COLUMN' command to make sure it is indeed the TD_TIMEBUCKET column in the PTI table,
            # and not just a column with the same name in a PTI/non-PTI table.
            # TD_TIMEBUCKET column is ignored since it is not functionally available to any user.
            if column_name == PTITableConstants.TD_TIMEBUCKET.value and \
                    len(row) > 48 and row[48] is not None and \
                    row[48].strip() == PTITableConstants.TSCOLTYPE_TIMEBUCKET.value:
                continue
            if to_type == "TD":
                # row[18] corresponds to the 'UDT Name' in the 'HELP COLUMN' SQL commands result.
                # row[1] corresponds to the 'Type' in the 'HELP COLUMN' commands result.
                column_names_and_types.append((column_name,
                                               UtilFuncs._help_col_to_td_type(row[1].strip(),
                                                                              row[18],
                                                                              row[44])))
            else:
                column_names_and_types.append((column_name,
                                               UtilFuncs._help_col_to_python_type(row[1].strip(),
                                                                                  row[44])))

        return column_names_and_types

    @staticmethod
    def _get_pandas_converters(col_types):
        """
        DESCRIPTION:
            Internal util function to get a dictionary of Python type names of columns
            in a teradataml DataFrame mapped to lambda functions to process the
            data to convert it to the type, which can be readily used with pandas'
            read_csv() function's 'converters' argument.

            Note: This utility provides converter functions only for values of type
                  int, float, and decimal.Decimal.
                  For types that don't expect empty strings in input
                  i.e. for 'datetime.datetime', 'datetime.date' and 'datetime.time',
                  the converter function returns None for empty string input.

        PARAMETERS:
            col_types:
                Required Argument.
                The list of Python types names corresponding to the columns in the input data.
                Types: list

        RAISES:
            None

        RETURNS:
            dict

        EXAMPLES:
            >>> pandas_converters = UtilFuncs._get_pandas_converters(["int", "str"])
        """
        pandas_converters = dict()
        for i, type_ in enumerate(col_types):
            # Add a functions that converts the string values to float or int when
            # the value is not empty string, else return None.
            if type_ in (PythonTypes.PY_FLOAT_TYPE.value,
                         PythonTypes.PY_DECIMAL_TYPE.value):
                pandas_converters[i] = lambda x: float(x) \
                    if isinstance(x, (bytes, number, int, float)) \
                    else float("".join(x.split())) if len(x.strip()) > 0 else None

            elif type_ == PythonTypes.PY_INT_TYPE.value:
                pandas_converters[i] = lambda x: int(x) \
                    if isinstance(x, (bytes, number, int, float)) \
                    else int(float("".join(x.split()))) if len(x.strip()) > 0 else None

            elif type_ in (PythonTypes.PY_DATETIME_TYPE.value,
                           PythonTypes.PY_DATE_TYPE.value,
                           PythonTypes.PY_TIME_TYPE.value):
                # For types that do not expect empty strings, add function to
                # set them to None when value received is empty string.
                pandas_converters[i] = lambda x: x if len(x.strip()) > 0 else None

            else:
                # For 'str' and 'bytes' types, add function that returns value as is.
                pandas_converters[i] = lambda x: x

        return pandas_converters

    @staticmethod
    def _teradata_type_to_python_type(td_type):
        """
        Translate the Teradata type from metaexpr to Python types.
        PARAMETERS:
            td_type - The Teradata type from metaexpr.

        RETURNS:
            The Python type for the given td_type.

        RAISES:

        EXAMPLES:
            # o is an instance of INTEGER
            pytype = UtilFuncs._teradata_type_to_python_type(o)

        """

        # loggerlogger.debug("_help_col_to_python_type td_type = {0} ".format(td_type))
        if type(td_type) in TeradataTypes.TD_INTEGER_TYPES.value:
            return PythonTypes.PY_INT_TYPE.value
        elif type(td_type) in TeradataTypes.TD_FLOAT_TYPES.value:
            return PythonTypes.PY_FLOAT_TYPE.value
        elif type(td_type) in TeradataTypes.TD_DECIMAL_TYPES.value:
            return PythonTypes.PY_DECIMAL_TYPE.value
        elif type(td_type) in TeradataTypes.TD_BYTE_TYPES.value:
            return PythonTypes.PY_BYTES_TYPE.value
        elif type(td_type) in TeradataTypes.TD_DATETIME_TYPES.value:
            return PythonTypes.PY_DATETIME_TYPE.value
        elif type(td_type) in TeradataTypes.TD_TIME_TYPES.value:
            return PythonTypes.PY_TIME_TYPE.value
        elif type(td_type) in TeradataTypes.TD_DATE_TYPES.value:
            return PythonTypes.PY_DATE_TYPE.value

        return PythonTypes.PY_STRING_TYPE.value

    @staticmethod
    def _help_col_to_python_type(col_type, storage_format):
        """
        Translate the 1 or 2 character TD type codes from HELP COLUMN to Python types.
        PARAMETERS:
            col_type - The 1 or 2 character type code from HELP COLUMN command.
            storage_format - The storage format from HELP COLUMN command.

        RETURNS:
            The Python type for the given col_type.

        RAISES:

        EXAMPLES:
            pytype = UtilFuncs._help_col_to_python_type('CV', None)
            pytype = UtilFuncs._help_col_to_python_type('DT', 'CSV')

        """
        if col_type in TeradataTypes.TD_INTEGER_CODES.value:
            return PythonTypes.PY_INT_TYPE.value
        elif col_type in TeradataTypes.TD_FLOAT_CODES.value:
            return PythonTypes.PY_FLOAT_TYPE.value
        elif col_type in TeradataTypes.TD_DECIMAL_CODES.value:
            return PythonTypes.PY_DECIMAL_TYPE.value
        elif col_type in TeradataTypes.TD_BYTE_CODES.value:
            return PythonTypes.PY_BYTES_TYPE.value
        elif col_type in TeradataTypes.TD_DATETIME_CODES.value:
            return PythonTypes.PY_DATETIME_TYPE.value
        elif col_type in TeradataTypes.TD_TIME_CODES.value:
            return PythonTypes.PY_TIME_TYPE.value
        elif col_type in TeradataTypes.TD_DATE_CODES.value:
            return PythonTypes.PY_DATE_TYPE.value
        elif col_type == "DT":
            sfmt = storage_format.strip()
            if sfmt == "CSV":
                return PythonTypes.PY_STRING_TYPE.value
            elif sfmt == "AVRO":
                return PythonTypes.PY_BYTES_TYPE.value

        return PythonTypes.PY_STRING_TYPE.value

    @staticmethod
    def _help_col_to_td_type(col_type, udt_name, storage_format):
        """
        Translate the 2 character TD type codes from HELP COLUMN to Teradata types.
        PARAMETERS:
            col_type - The 2 character type code from HELP COLUMN command.
            udt_name - The UDT name from the HELP COLUMN command.
            storage_format - The storage format from HELP COLUMN command.

        RETURNS:
            The Teradata type for the given colType.

        RAISES:

        EXAMPLES:
            tdtype = UtilFuncs._help_col_to_td_type('CV', None, None)

        """
        # logger.debug("helpColumnToTeradataTypeName colType = {0} udtName = {1}
        # storageFormat {2}".format(colType, udtName, storageFormat))
        if col_type in td_coltype_code_to_tdtype.HELP_COL_TYPE_TO_TDTYPE:
            return td_coltype_code_to_tdtype.HELP_COL_TYPE_TO_TDTYPE[col_type]

        if col_type == "DT":
            return "DATASET STORAGE FORMAT {0}".format(storage_format.strip())

        if col_type in ["UD", "US", "UT", "A1", "AN"]:
            if udt_name:
                return udt_name

        return col_type

    @staticmethod
    def _convert_date_to_string(date_obj):
        """
        Converts the date from datetime.date object to String type in the format "DATE 1987-06-09".
        PARAMETERS:
            date_obj:
                Required Argument.
                Specifies the date object to convert to string type.
                Types: datetime.date

        RETURNS:
            The String reresentation for the given datetime.date object in the format "DATE 1987-06-09"

        RAISES:
            None

        Examples:
            date_str = UtilFuncs._convert_date_to_string(date_obj)

        """
        date_str = 'DATE {}'.format(date_obj.strftime('%Y-%m-%d'))
        return date_str

    @staticmethod
    def _process_for_teradata_keyword(keyword):
        """
        Processing the Teradata Reserved keywords.
        If keyword is in list of Teradata Reserved keywords, then it'll be quoted in double quotes "keyword".

        PARAMETERS:
            keyword - A string or a list of strings to check whether it belongs to Teradata Reserved
            Keywords or not.

        RETURNS:
            A quoted string or list of quoted strings, if keyword is one of the Teradata Reserved Keyword,
            else same object as is.

        RAISES:
            None.

        EXAMPLES:
            # Passing non-reserved returns "xyz" as is.
            keyword = self.__process_for_teradata_keyword("xyz")
            print(keyword)
            # Passing reserved str returns double-quoted str, i.e., "\"threshold\"".
            keyword = self.__process_for_teradata_keyword("threshold")
            print(keyword)
        """
        # If the input keyword is a list, then call the same function again for every
        # element in the list.
        if isinstance(keyword, list):
            return [UtilFuncs._process_for_teradata_keyword(col) for col in keyword]

        if isinstance(keyword, str) and keyword.upper() in \
                TeradataReservedKeywords.TERADATA_RESERVED_WORDS.value:
            return UtilFuncs._teradata_quote_arg(keyword, "\"", False)

        return keyword

    def _contains_space(item):
        """
        Check if the specified string in item has spaces or tabs in it.
        
        PARAMETERS:
            item:
                Required Argument.
                Specifies a string to check for spaces or tabs.
                Types: str

        RETURNS:
            True, if the specified string has spaces or tabs in it, else False.

        RAISES:
            None.

        EXAMPLES:
            # Passing column name with spaces returns True.
            is_space = UtilFuncs._contains_space("col name")
            print(is_space)
            # Passing column name without spaces returns False.
            is_space = UtilFuncs._contains_space("colname")
            print(is_space)
        """
        # Check if the input is a string and look for spaces or tabs
        if isinstance(item, str):
            return any(char in {' ', '\t'} for char in item)

        # If the input is a list, check each element
        if isinstance(item, list):
            # Check each item in the list
            return any(UtilFuncs._contains_space(col) for col in item)

        return False

    @staticmethod
    def _is_non_ascii(col_lst):
        """
        Description:
            Check if the specified string in col_lst has non-ASCII characters in it.

        PARAMETERS:
            col_lst:
                Required Argument.
                Specifies a list of strings to check for non-ASCII characters.
                Types: list

        RETURNS:
            True, if the specified string has non-ASCII characters in it, else False.

        RAISES:
            None.
        
        EXAMPLES:
            # Passing column name with non-ASCII characters returns True.
            >>> is_non_ascii = UtilFuncs._is_ascii(["col name", "がく片の長さ@name"])
            >>> print(is_non_ascii)
            >>> True
            # Passing column name without non-ASCII characters returns False.
            >>> is_non_ascii = UtilFuncs._is_ascii(["colname", "col_name"])
            >>> print(is_non_ascii)
            >>> False
        """
        if isinstance(col_lst, str):
            # Check if the input is a string and look for non-ASCII characters
            return not col_lst.isascii()

        if isinstance(col_lst, list):
            for item in col_lst:
                if isinstance(item, str) and not item.isascii():
                    return True
        return False

    @staticmethod
    def __get_dot_separated_names(full_qualified_name):
        """
        Takes in fully qualified name of the table/view (db.table), and returns
        a dot separated name from the same.

        PARAMETERS:
            full_qualified_name - Name of the table/view

        EXAMPLES:
            UtilFuncs._extract_db_name('"db1"."tablename"')
            UtilFuncs._extract_db_name('"Icebergs"."db1"."tablename"')

        RETURNS:
            List of dot separated name from the provided name.

        """
        # If condition to handle the quoted name.
        if '"' in full_qualified_name:
            # Extract the double quoted strings.
            names = re.findall(r'["](.*?)["]', full_qualified_name)
            # Remove quotes around the string.
            names = [i.replace('"', '') for i in names]
        # Handle non-quoted string with dot separated name.
        else:
            names = full_qualified_name.split(".")
        return names

    @staticmethod
    def _extract_db_name(full_qualified_name):
        """
        Takes in fully qualified name of the table/view (db.table), and returns
        a database name from the same.

        PARAMETERS:
            full_qualified_name - Name of the table/view

        EXAMPLES:
            UtilFuncs._extract_db_name('"db1"."tablename"')
            UtilFuncs._extract_db_name('"Icebergs"."db1"."tablename"')

        RETURNS:
            Database name from the provided name.

        """
        names = UtilFuncs.__get_dot_separated_names(full_qualified_name)
        if names:
            if len(names) == 2:
                return names[0]
            elif len(names) == 3:
                return names[1]
        else:
            return None

    @staticmethod
    def _extract_table_name(full_qualified_name):
        """
        Takes in fully qualified name of the table/view (db.table), and returns
        a table/view name from the same.

        PARAMETERS:
            full_qualified_name - Name of the table/view

        EXAMPLES:
            UtilFuncs._extract_table_name('"db1"."tablename"')
            UtilFuncs._extract_table_name('"Icebergs"."db1"."tablename"')

        RETURNS:
            Table/View name from the provided name.

        """
        names = UtilFuncs.__get_dot_separated_names(full_qualified_name)
        if names:
            if len(names) == 2:
                return names[1]
            elif len(names) == 3:
                return names[2]
            else:
                return names[0]
        return full_qualified_name

    @staticmethod
    def _extract_datalake_name(full_qualified_name):
        """
        Takes in fully qualified name of the table/view (db.table), and returns
        a datalake name from the same.

        PARAMETERS:
            full_qualified_name - Name of the table/view

        EXAMPLES:
            UtilFuncs._extract_datalake_name('"db1"."tablename"')
            UtilFuncs._extract_datalake_name('"Icebergs"."db1"."tablename"')

        RETURNS:
            Database name from the provided name.

        """
        names = UtilFuncs.__get_dot_separated_names(full_qualified_name)
        if names and len(names) == 3:
            return names[0]
        return None

    @staticmethod
    def _teradata_quote_arg(args, quote="'", call_from_wrapper=True):
        """
        Function to quote argument value.
        PARAMETERS:
            args : Argument to be quoted.
            quote : Type of quote to be used for quoting. Default is
                    single quote (').
        RETURNS:
            Argument with quotes as a string.

        EXAMPLES:
            When a call is being made from wrapper:
                UtilFuncs._teradata_quote_arg(family, "'")
            When a call is being made from non-wrapper function.
                UtilFuncs._teradata_quote_arg(family, "'", False)
        """
        if call_from_wrapper and not configure.column_casesensitive_handler:
            quote = ""
            return args

        # Returning same string if it already quoted. Applicable only for strings.
        if isinstance(args, str) and args.startswith(quote) and args.endswith(quote):
            return args
        if args is None:
            return None
        if isinstance(args, list):
            return ["{0}{1}{0}".format(quote, arg) for arg in args]

        return "{0}{1}{0}".format(quote, args)

    @staticmethod
    def _teradata_unquote_arg(quoted_string, quote="'"):
        """
        Function to unquote argument value.
        PARAMETERS:
            quoted_string : String to be unquoted.
            quote         : Type of quote to be used for unquoting. Default is
                            single quote (').
        RETURNS:
            None if 'quoted_string' is not a string,
            else Argument without quotes as a string.

        EXAMPLES:
            UtilFuncs._teradata_unquote_arg(family, "'")
        """

        if not isinstance(quoted_string, str):
            return None

        # Returning same string if it already unquoted.
        if not quoted_string.startswith(quote) and not quoted_string.endswith(quote):
            return quoted_string

        return quoted_string[1:-1]

    @staticmethod
    def _teradata_collapse_arglist(args_list, quote="'"):
        """
        Given a list as an argument this will single quote all the
        list elements and combine them into a single string separated by
        commas.

        PARAMETERS:
            args_list: List containing string/s to be quoted.
            quote: Type of quote to be used for quoting. Default is single quote (').

        RETURNS:
            Single string separated by commas.

        EXAMPLES:
            UtilFuncs._teradata_collapse_arglist(family, "'")

        """
        expr = r"([\"'][\d.\d\w]+\s*[\"'][,]*\s*)+([\"']\s*[\d.\d\w]+[\"']$)"

        # # return None if list is empty
        # if not args_list and not isinstance(args_list, bool):
        #     return args_list

        # if args_list is a list quote all values of the list
        if isinstance(args_list, list):
            '''
            EXAMPLE:
                arg = ['admitted', 'masters', 'gpa', 'stats', 'programming']
                UtilFuncs._teradata_collapse_arglist(arg, "\"")
            RETURNS:
                '"admitted","masters","gpa","stats","programming"'

            '''
            return ",".join("{0}{1}{0}".format(quote, arg) for arg in args_list)
        elif (isinstance(args_list, str)) and (bool(re.match(expr, args_list)) is True):
            '''
            Quotes the arguments which is string of strings with the provided quote variable
            value.
            The expr should be strings separeted by commas. The string values can be digits or
            alphabets.
            For example:
                args_list = '"masters","gpa","stats"'
                quote = "'"
                The args_list is quoted as below based on the quote argument provided:
                    strQuotes = '"masters"','"gpa"','"stats"'
            RETURNS:
                quoted string

            The quoted value is added to list in the functions with other arguments as:
                funcOtherArgs = ["'2.0'", "'POISSON'", "'IDENTITY'", "'0.05'", "'10'", "'False'", "'True'",
                '\'"masters"\',\'"gpa"\',\'"stats"\',\'"programming"\',\'"admitted"\'',
                '\'"masters"\',\'"stats"\',\'"programming"\'']

            '''
            str_val = re.sub(r"\s+", "", args_list)
            args_list = str_val.split(",")
            return ",".join("{0}{1}{0}".format(quote, arg) for arg in args_list)
        # if argVector is any value of int/str/bool type, quote the value
        else:
            return UtilFuncs._teradata_quote_arg(args_list, quote, False)

    @staticmethod
    def _get_metaexpr_using_columns(nodeid, column_info, with_engine=False, is_persist=False, **kw):
        """
        This internal function takes in input node ID and column information in zipped lists format
        to return metaexpr with or without engine.

        PARAMETERS:
            nodeid - AED DAG node id for which a metaexpr is to be generated.
            column_info - This contains zipped lists of column names and corresponding column types.
            with_engine - A bool parameter, deciding whether to generate metaexpr with engine or not.
                        Default is False.
            is_persist -  A bool parameter, deciding whether to persist the result or not.
                        Default is False.

        RAISES:

        RETURNS:
            metaexpr for the provided node ID and with column inforamtion.

        EXAMPLES:
            node_id_list = self.__aed_utils._aed_ml_query(self.__input_nodeids, self.sqlmr_query, self.__func_output_args, "NaiveBayesMap")
            stdout_column_info = zip(stdout_column_names, stdout_column_types)
            UtilFuncs._get_metaexpr_using_columns(node_id_list[0], stdout_column_info)
        """
        from teradataml.dataframe.sql import _MetaExpression
        if with_engine:
            eng = tdmlctx.get_context()
            meta = sqlalchemy.MetaData(eng)
        else:
            meta = sqlalchemy.MetaData()

        # Get the output table name for node_id from AED
        aed_utils = AedUtils()

        table_name = aed_utils._aed_get_tablename(nodeid)
        db_schema = UtilFuncs._extract_db_name(table_name)
        db_table_name = UtilFuncs._extract_table_name(table_name)

        # Constructing new Metadata (_metaexpr) without DB; _MetaExpression
        ouptut_table = Table(db_table_name, meta,
                             *(Column(col_name, col_type) for col_name, col_type in column_info),
                             schema=db_schema)
        return _MetaExpression(ouptut_table, is_persist=is_persist, **kw)

    @staticmethod
    def _get_metaexpr_using_parent_metaexpr(nodeid, metaexpr):
        """
        This internal function takes in input node ID and metaexpr (parents)
        to return metaexpr with or without engine.

        PARAMETERS:
            nodeid:
                Required Argument.
                Specifies AED DAG node id for which a metaexpr is to be generated.

            metaexpr:
                Required Argument.
                _MetaExpression() of a DataFrame objects which is to be used to extract and
                create a new _MetaExpression.

        RAISES:
            None.

        RETURNS:
            metaexpr for the provided node ID and with metaexpr inforamtion.

        EXAMPLES:
            node_id_list = self.__aed_utils._aed_ml_query(self.__input_nodeids, self.sqlmr_query, self.__func_output_args, "NaiveBayesMap")
            UtilFuncs._get_metaexpr_using_parent_metaexpr(node_id_list[0], parent_metaexpr)
        """
        meta_cols = metaexpr.t.c
        meta_columns = [c.name for c in meta_cols]
        col_names = []
        col_types = []

        # When column list to retrieve is not provided, return meta-data for all columns.
        for col_name in meta_columns:
            col_names.append(meta_cols[col_name].name)
            col_types.append(meta_cols[col_name].type)

        return UtilFuncs._get_metaexpr_using_columns(nodeid, zip(col_names, col_types),
                                                     datalake=metaexpr.datalake)

    @staticmethod
    def _create_table_using_columns(table_name, columns_datatypes, pti_clause=None, storage=None):
        """
        Create a table with columns.

        PARAMETERS:
            table_name - Fully qualified quoted table name.
            columns_datatypes - Column names and dattypes for the table
            pti_clause - Specifies the string for the primary time index.
            storage - Specifies the storage for the table.

        RAISES

        RETURNS:
            True if success, false if fails

        EXAMPLES:
            UtilFuncs._create_table_using_columns('"dbname"."table_name"', 
                            "col1 varchar(10), col2 integer, col3 timestamp")
        """
        # If storage option is specified, add the storage clause in the create table statement.
        if storage:
            table_name = "{}, STORAGE={}".format(table_name, storage)

        crt_table = SQLBundle._build_create_table_using_columns(table_name, columns_datatypes)

        if pti_clause is not None:
            crt_table = "{} PRIMARY TIME INDEX {}".format(crt_table, pti_clause)

        try:
            UtilFuncs._execute_ddl_statement(crt_table)
            return True
        except Exception:
            raise

    @staticmethod
    def _get_engine_name(engine):
        """
        Function to return the name of the engine mapped to the
        argument 'engine' in function mapped dictionary.

        PARAMETERS:
            engine:
                Required Argument.
                Specifies the type of the engine.

        RETURNS:
            Name of the engine.

        RAISES:
            TeradataMLException

        EXAMPLES:
            UtilFuncs._get_engine_name("ENGINE_SQL")

        """
        _Validators._validate_engine(engine)
        supported_engines = TeradataConstants.SUPPORTED_ENGINES.value
        return supported_engines[engine]['name']

    @staticmethod
    def _as_list(obj):
        """
        Function to convert an object to list, i.e., just enclose the value passed to the
        function in a list and return the same, if it is not of list type.
        PARAMETERS:
            obj:
                Required Argument.
                Specifies the object to be enclosed in a list.
                Types: Any type except list.
        RETURNS:
            list
        RAISES:
            None.
        EXAMPLES:
            obj = UtilFuncs._as_list("vantage1.0")
        """
        return obj if isinstance(obj, list) else [obj]

    @staticmethod
    def _get_all_columns(object, is_object_type_tdml_column):
        """
        Function to get all columns from a given teradataml DataFrame
        or teradataml DataFrame column.

        PARAMETERS:
            object:
                Required Argument.
                Specifies either teradataml DataFrame or teradataml DataFrame
                Column.
                Types: teradataml DataFrame, _SQLColumnExpression

            is_object_type_tdml_column:
                Required Argument.
                Specifies whether "object" is a teradataml DataFrame or
                teradataml DataFrame Column.
                If True, "object" treats as teradataml DataFrame Column.
                If False, "object" treats as teradataml DataFrame.
                Types: bool

        RETURNS:
            An iterator and each element in the iterator represents a Column

        RAISES:
            None.

        EXAMPLES:
            obj = UtilFuncs._get_all_columns(df.col, True)
            obj = UtilFuncs._get_all_columns(df, False)
        """
        if is_object_type_tdml_column:
            return UtilFuncs._all_df_column_expressions(object)
        # object._metaexpr.c extracts the data to a list. And, the caller of
        # this function will again iterate through the list, to process the
        # list i.e. object._metaexpr.c is being iterated twice. To avoid this,
        # a generator object is being constructed and returned.
        return (c for c in object._metaexpr.c)

    @staticmethod
    def _get_file_contents(file_path, read_in_binary_mode=False):
        """
        Description:
            Function to get the file content from a file, given absolute
            file path.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute file path of the file.
                Types: str

            read_in_binary_mode:
                Optional Argument.
                Specifies whether to read the file in binary format or not.
                If True, read the file in binary mode.
                If False, read the file in ASCII mode.
                Default value: False
                Types: bool

        RETURNS:
            str OR bytes

        RAISES:
            TeradataMlException

        EXAMPLES:
            obj = UtilFuncs._get_file_contents("/abc/xyz.txt")
            obj = UtilFuncs._get_file_contents("/abc/xyz.txt", True)
        """
        try:
            mode = 'r'
            if read_in_binary_mode:
                mode = 'rb'
            with open(file_path, mode) as file_data:
                _Validators._check_empty_file(file_path)
                return file_data.read()
        except TeradataMlException:
            raise
        except FileNotFoundError:
            raise
        except Exception as err:
            msg_code = MessageCodes.EXECUTION_FAILED
            raise TeradataMlException(
                Messages.get_message(msg_code, "read contents of file '{}'".format(file_path), str(err)), msg_code)

    @staticmethod
    def _create_table_using_table_object(table_obj):
        """
        DESCRIPTION:
            This function creates the table in Vantage using table object.

        PARAMETERS:
            table_obj:
                Specifies the table object.
                Types: sqlalchemy.sql.schema.Table

        RETURNS:
            None.

        RAISES:
            TeradataMlException

        EXAMPLES:
            from sqlalchemy import Table, MetaData, Column

            meta = MetaData()
            # Create default Table construct with parameter dictionary
            table_obj = Table(table_name, meta,
                          *(Column(col_name, col_type)
                            for col_name, col_type in
                            zip(col_names, col_types)),
                          teradatasql_post_create=pti,
                          prefixes=prefix,
                          schema=schema_name
                          )

            _create_table_using_table_object(table_obj)
        """
        if table_obj is not None:
            try:
                table_obj.create(bind=tdmlctx.get_context())
            except sqlachemyOperationalError as err:
                raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_OBJECT_CREATION_FAILED) +
                                          '\n' + str(err),
                                          MessageCodes.TABLE_OBJECT_CREATION_FAILED)
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_OBJECT_CREATION_FAILED),
                                      MessageCodes.TABLE_OBJECT_CREATION_FAILED)

    @staticmethod
    def _extract_table_object_column_info(table_obj):
        """
        Internal function to extract the column name and column types from
        table object.

        PARAMETERS:
            table_obj:
                Required Argument.
                Specifies the table object.
                Types: sqlalchemy.sql

        RETURNS:
            Tuple

        RAISES:
            None

        EXAMPLE:
            meta = MetaData()
            table = Table(table_name, meta, schema=schema_name, autoload_with=eng)
            _extract_table_object_column_info(table.c)
        """
        col_names = []
        col_types = []

        for col in table_obj:
            col_names.append(col.name)
            col_types.append(col.type)

        return col_names, col_types

    @staticmethod
    def _get_warnings(argument_name, argument_value, specified_argument_name, specified_argument_value):
        """
        Internal function to print the warning.

        PARAMETERS:
            argument_name:
                Required Argument.
                Specifies the argument name to check.
                Types: str

            argument_value:
                Required Argument.
                Specifies the argument value to check.
                Types: bool

            specified_argument_name:
                Required Argument.
                Specifies the argument name to use in warning message.
                Types: str

            specified_argument_value:
                Required Argument.
                Specifies the argument value to use in warning message.
                Types: str

        RETURNS:
            None

        RAISES:
            None

        EXAMPLE:
            _get_warnings(argument_name, argument_value, specified_argument_name, specified_argument_value)
        """
        if argument_value:
            warnings.warn(Messages.get_message(MessageCodes.IGNORE_ARGS_WARN,
                                               '{0}',
                                               "{1}='{2}'",
                                               'specified').format(argument_name,
                                                                   specified_argument_name,
                                                                   specified_argument_value))

    @staticmethod
    def _get_sqlalchemy_table(table_name, schema_name=None, check_table_exists=False):
        """
        Internal function returns the SQLAlchemy table object for a table.
        If check_table_exists specified, function also checks for table existence.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the table name.
                Types: str

            schema_name:
                Optional Argument.
                Specifies schema name.
                Types: str

            check_table_exists:
                Optional Argument.
                Specifies whether to check table exists or not.
                Default Value: False
                Types: bool

        RETURNS:
            sqlalchemy.sql.schema.Table

        RAISES:
            None

        EXAMPLE:
            _get_sqlalchemy_table(table_name='my_table')
        """
        con = tdmlctx.get_connection()

        if check_table_exists:
            table_exists = con.dialect.has_table(con, table_name, schema_name, table_only=True)

            if not table_exists:
                raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_DOES_NOT_EXIST, table_name),
                                          MessageCodes.TABLE_DOES_NOT_EXIST)

        meta = MetaData()
        return Table(table_name, meta,
                     schema=schema_name,
                     autoload_with=tdmlctx.get_context())

    @staticmethod
    def _extract_table_object_index_info(table_obj):
        """
        Internal function to extract primary index information of existing table.

        PARAMETERS:
            table_obj:
                Required Argument.
                Specifies the sqlalchemy table object.
                Types: sqlalchemy.sql.schema.Table.

        RETURNS:
            list.

        RAISES:
            None.

        EXAMPLE:
            _extract_table_object_index_info(table_object)
        """
        sqlalchemy_table_primary_index = table_obj.indexes
        primary_index_list = []
        for index in sqlalchemy_table_primary_index:
            primary_index_list = index.columns.keys()
        return primary_index_list

    @staticmethod
    def _get_positive_infinity():
        """
        Description:
            Function to get the positive infinity.

        RETURNS:
            float

        RAISES:
            None

        EXAMPLES:
            inf = UtilFuncs._get_positive_infinity()
        """
        return float("inf")

    @staticmethod
    def _get_negative_infinity():
        """
        Description:
            Function to get the negative infinity.

        RETURNS:
            float

        RAISES:
            None

        EXAMPLES:
            inf = UtilFuncs._get_negative_infinity()
        """
        return -1 * UtilFuncs._get_positive_infinity()

    @staticmethod
    def _get_class(class_name, supress_isinstance_check=False):
        """
        Description:
            Function to get the class dynamically with the name as 'class_name'.

        PARAMETERS:
            class_name:
                Required Parameter.
                Specifies the name of the class generated to be.
                Types: str

            supress_isinstance_check:
                Optional Parameter.
                Specifies whether the dynamically created class should overwrite the
                isinstance method or not. When set to True, if the class generated from
                this function is passed to isinstance method, instead of verifying the
                actual type, it tries to match the name of object's class with 'class_name'.
                Default value: False
                Types: bool

        RETURNS:
            type

        RAISES:
            None

        EXAMPLES:
            inf = UtilFuncs._get_class("test")
        """
        parent_object = object
        if supress_isinstance_check:

            # isinstance function is governed by the dunder method __instancecheck__.
            # However, unlike other dunder method's, __instancecheck__ should be overwritten
            # for a class, instead of object ,i.e., while creating the class itself, __instancecheck__
            # should be overwritten.
            # Note that, python's type accepts either object or any other class as a parent class.
            # Since, other than object, one should pass only a class to a python type, creating a
            # dummy class and specifying the metaclass as SupressInstanceCheck so that the dummy class
            # has updated __instancecheck__ dunder method.
            class SupressInstanceCheck(type):
                def __instancecheck__(self, instance):
                    try:
                        return self.__name__ == instance.__class__.__name__
                    except Exception:
                        return False

            class temp(metaclass=SupressInstanceCheck):
                pass

            parent_object = temp

        return type(class_name, (parent_object, ), {})

    @staticmethod
    def _get_file_size(file_path, in_mb=True):
        """
        Description:
            Function to get the size of file, given absolute file path.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute file path of the file.
                Types: str

            in_mb:
                Optional Argument.
                Specifies whether to get the file size in mega bytes or not.
                If True, size of the file returns in MB's. Otherwise, returns
                in bytes.
                Default value: True
                Types: bool

        RETURNS:
            int OR float

        RAISES:
            TeradataMlException

        EXAMPLES:
            file_size = UtilFuncs._get_file_size("/abc/xyz.txt")
        """
        size_in_bytes = os.path.getsize(file_path)

        return size_in_bytes/(1024*1024.0) if in_mb else size_in_bytes

    @staticmethod
    def _http_request(url, method_type=HTTPRequest.GET, **kwargs):
        """
        Description:
            Function to initiate HTTP(S) request.

        PARAMETERS:
            url:
                Required Argument.
                Specifies the url to initiate http request.
                Types: str

            method_type:
                Optional Argument.
                Specifies the type of HTTP request.
                Default value: HTTPREquest.GET
                Types: HTTPRequest enum

            **kwargs:
                Specifies the keyword arguments required for HTTP Request.
                Below are the expected arguments as a part of kwargs:
                    json:
                        Optional Argument.
                        Specifies the payload for HTTP request in a dictionary.
                        Types: dict

                    data:
                        Optional Argument.
                        Specifies the payload for HTTP request in a string format.
                        Types: str

                    headers:
                        Optional Argument.
                        Specifies the headers for HTTP request.
                        Types: dict

                    verify:
                        Optional Argument.
                        Specifies whether to verify the certificate or not in a HTTPS request.
                        One can specify either False to suppress the certificate verification or
                        path to certificate to verify the certificate.
                        Types: str OR bool

                    files:
                        Optional Argument.
                        Specifies the file to be uploaded with a HTTP Request.
                        Types: tuple

        RETURNS:
            Response object.

        RAISES:
            None

        EXAMPLES:
            resp = UtilFuncs._http_request("http://abc/xyz.teradata")
        """
        kwargs["verify"] = configure.certificate_file

        if not configure.certificate_file:
            warnings.filterwarnings("ignore", message="Unverified HTTPS request is being made to host[ a-zA-Z0-9'-.]*")

        return getattr(requests, method_type.value)(url=url, **kwargs)

    @staticmethod
    def _get_tdml_directory():
        """
        DESCRIPTION:
            Function to get the directory of teradataml module.

        PARAMETERS:
            None.

        RETURNS:
            str.

        EXAMPLES:
            >>> tdml_path = UtilFuncs._get_tdml_directory()
        """
        # Get the directory of teradataml module.
        return os.path.dirname(_version.__file__)

    @staticmethod
    def _get_data_directory(dir_name=None, func_type=None, version=None):
        """
        DESCRIPTION:
            Function to get the directory for jsons or docs from teradataml/data.

        PARAMETERS:
            dir_name:
                Optional Argument.
                Specifies the name of directory required from teradataml/data directory.
                Permitted values : ["jsons", "docs"]
                Types: str

            func_type
                Optional Argument.
                Specifies the type of function for which jsons or docs directory is required.
                Types: TeradataAnalyticFunctionInfo

            version:
                Optional Argument.
                Specifies the version of directory for which jsons or docs directory is required.
                Types: str

        RETURNS:
            path to desired directory.

        EXAMPLES:
            >>> json_dir = UtilFuncs._get_data_directory(dir_name="jsons",
            ...                                          func_type=TeradataAnalyticFunctionInfo.FASTPATH,
            ...                                          version="17.10")

        """
        if func_type:
            func_type = func_type.value["func_type"]
        dir_path = os.path.join(UtilFuncs._get_tdml_directory(), "data")
        levels = [dir_name, func_type, version]
        for level in levels:
            if level:
                dir_path = os.path.join(dir_path, level)
            else:
                break
        if os.path.exists(dir_path):
            return dir_path

    @staticmethod
    def _replace_special_chars(str_value, replace_char="_", addon=None):
        """
        DESCRIPTION:
            Function to replace any special character with a underscore(_).

        PARAMETERS:
            str_value:
                Required Argument.
                Specifies the value of string which has special characters.
                Types: str

            replace_char:
                Optional Argument.
                Specifies the value to be replaced for any special character.
                Types: str

            addon
                Optional Argument.
                Specifies a dictionary with key as value to be checked in "s" and value
                to be replaced in "s".
                Types: dict

        RETURNS:
            str

        EXAMPLES:
            >>> json_dir = UtilFuncs._replace_special_chars("123$%.", addon={"$": "#"})
        """
        char_dict = {'A': 'A',
                     'B': 'B',
                     'C': 'C',
                     'D': 'D',
                     'E': 'E',
                     'F': 'F',
                     'G': 'G',
                     'H': 'H',
                     'I': 'I',
                     'J': 'J',
                     'K': 'K',
                     'L': 'L',
                     'M': 'M',
                     'N': 'N',
                     'O': 'O',
                     'P': 'P',
                     'Q': 'Q',
                     'R': 'R',
                     'S': 'S',
                     'T': 'T',
                     'U': 'U',
                     'V': 'V',
                     'W': 'W',
                     'X': 'X',
                     'Y': 'Y',
                     'Z': 'Z',
                     'a': 'a',
                     'b': 'b',
                     'c': 'c',
                     'd': 'd',
                     'e': 'e',
                     'f': 'f',
                     'g': 'g',
                     'h': 'h',
                     'i': 'i',
                     'j': 'j',
                     'k': 'k',
                     'l': 'l',
                     'm': 'm',
                     'n': 'n',
                     'o': 'o',
                     'p': 'p',
                     'q': 'q',
                     'r': 'r',
                     's': 's',
                     't': 't',
                     'u': 'u',
                     'v': 'v',
                     'w': 'w',
                     'x': 'x',
                     'y': 'y',
                     'z': 'z',
                     '0': '0',
                     '1': '1',
                     '2': '2',
                     '3': '3',
                     '4': '4',
                     '5': '5',
                     '6': '6',
                     '7': '7',
                     '8': '8',
                     '9': '9'}
        char_dict.update({" ": "", "_": "_", "\"": ""})
        if addon:
            char_dict.update(addon)
        return reduce(lambda x,y: x+y, (char_dict.get(c, replace_char) for c in str_value))

    @staticmethod
    def _get_dict_from_libs(lib_name):
        """
        DESCRIPTION:
            Function to format the list of library version string to a dictionary,
            on the basis of regex.

        PARAMETERS:
            lib_name:
                Required Argument.
                Specifies the libs the user wants to format to a dictionary with
                key as lib_name and value as lib_version.
                Types: str, list of str

        RETURNS:
            dict
        """
        result = {}
        if isinstance(lib_name, str):
            lib_name = UtilFuncs._as_list(lib_name)
        for lib in lib_name:
            matches = re.findall(r'([^<>=]+)([<>=].*)', lib)
            if matches:
                for key, value in matches:
                    result[key] = value
            else:
                result[lib] = ''
        return result

    @staticmethod
    def _is_valid_td_type(type_):
        """
        DESCRIPTION:
            Function to check whether it is valid teradatasqlalchemy type or not.

        PARAMETERS:
            type_:
                Required Argument.
                Specifies any value which needs to be validated for teradatasqlalchemy type.
                Types: Any python object

        RETURNS:
            bool
        """
        if isinstance(type_, _TDType):
            return True
        if isinstance(type_, type) and issubclass(type_, _TDType):
            return True
        return False

    @staticmethod
    def _all_df_column_expressions(df_column):
        """
        DESCRIPTION:
            A method to get all the SQLALchemy Columns involved in corresponding DataFrame.

        PARAMETERS:
            df_column:
                Required Argument.
                Specifies teradataml DataFrame ColumnExpression.
                Types: teradataml DataFrame ColumnExpression

        RAISES:
            None

        RETURNS:
            list

        EXAMPLES:
            >>> self._all_df_column_expressions
        """
        cols = []
        for table_ in df_column._get_sqlalchemy_tables(df_column.expression):
            cols = cols + list(table_.columns)
        return cols

    @staticmethod
    def _all_df_columns(df_column):
        """
        DESCRIPTION:
            A method to get all the column names involved in corresponding DataFrame.

        PARAMETERS:
            df_column:
                Required Argument.
                Specifies teradataml DataFrame ColumnExpression.
                Types: teradataml DataFrame ColumnExpression

        RAISES:
            None

        RETURNS:
            list

        EXAMPLES:
            >>> self._all_df_columns
        """
        return [col.name for col in UtilFuncs._all_df_column_expressions(df_column)]

    @staticmethod
    def _is_lake():
        """
        DESCRIPTION:
            An internal function to check whether system is Lake or enterprise.

        PARAMETERS:
            None.

        RAISES:
            None

        RETURNS:
            bool

        EXAMPLES:
            >>> self._is_lake()
        """

        tbl_operator = configure.table_operator.lower() \
            if configure.table_operator else None

        # If the user does not provide a table_operator, check the database version
        # and determine the system type accordingly.
        if tbl_operator is None:
            from teradataml.context.context import _get_database_version
            if int(_get_database_version().split(".")[0]) < 20:
                return False
            # If the database version is 20 or higher, check if the system is VCL or not.
            try:
                res = UtilFuncs._execute_query("SELECT 1 WHERE TD_GetSystemType('PRODUCT') = 'VCL';")
                return True if res else False
            except OperationalError:
                return True

        return tbl_operator == "apply"

    @staticmethod
    def _get_python_execution_path():
        """
         DESCRIPTION:
             An internal function to get the python execution path.

         PARAMETERS:
             None.

         RAISES:
             None

         RETURNS:
             bool

         EXAMPLES:
             >>> self._get_python_execution_path()
         """
        # 'indb_install_location' expects python installation directory path.
        # Hence, postfixing python binary path.
        return "python" if UtilFuncs._is_lake() else \
            '{}/bin/python3'.format(configure.indb_install_location)

    def _is_view(tablename):
        """
        DESCRIPTION:
            Internal function to check whether the object is view or not.
        PARAMETERS:
            tablename:
                Required Argument.
                Table name or view name to be checked.
                Types: str
        RAISES:
            None.
        RETURNS:
            True when the tablename is view, else false.
        EXAMPLES:
            >>> _is_view('"dbname"."tablename"')
        """
        db_name = UtilFuncs._teradata_unquote_arg(UtilFuncs._extract_db_name(tablename), "\"")
        table_view_name = UtilFuncs._teradata_unquote_arg(UtilFuncs._extract_table_name(tablename), "\"")
        query = SQLBundle._build_select_table_kind(db_name, "'{0}'".format(table_view_name), "'V'")

        df = UtilFuncs._execute_query(query)
        if len(df) > 0:
            return True
        else:
            return False

    @staticmethod
    def _set_queryband():
        from teradataml import session_queryband
        try:
            qb_query = session_queryband.generate_set_queryband_query()
            execute_sql(qb_query)
        except Exception as _set_queryband_err:
            pass

    def _create_or_get_env(template):
        """
        DESCRIPTION:
            Internal function to return the environment if already exists else
            creates the environment using template file and return the environment.

        PARAMETERS:
            template:
                Required Argument.
                Template json file name containing details of environment(s) to be created.
                Types: str

        RAISES:
            TeradataMLException

        RETURNS:
            An object of class UserEnv representing the user environment.

        EXAMPLES:
            >>> self._create_or_get_env("open_source_ml.json")
        """
        # Get the template file path.
        from teradataml import _TDML_DIRECTORY
        from teradataml.scriptmgmt.lls_utils import create_env, get_env
        template_dir_path = os.path.join(_TDML_DIRECTORY, "data", "templates", template)

        # Read template file.
        with open(template_dir_path, "r") as r_file:
            data = json.load(r_file)

        # Get env_name.
        _env_name = data["env_specs"][0]["env_name"]

        try:
            # Call function to get env.
            return get_env(_env_name)
        except TeradataMlException as tdml_e:
            # We will get here when error says, env does not exist otherwise raise the exception as is.
            # Env does not exist so create one.

            exc_msg = "Failed to execute get_env(). User environment '{}' not " \
                      "found.".format(_env_name)
            if exc_msg in tdml_e.args[0]:
                print(f"No OpenAF environment with name '{_env_name}' found. Creating one with "\
                      "latest supported python and required packages.")
                return create_env(template=template_dir_path)
            else:
                raise tdml_e
        except Exception as exc:
            raise exc

    def _get_env_name(col=None):
        """
        DESCRIPTION:
            Internal function to get the env name if passed with ColumnExpression
            else the default "openml_env".

        PARAMETERS:
            col:
                Optional Argument.
                Specifies teradataml DataFrame ColumnExpression.
                Types: teradataml DataFrame ColumnExpression
                Default Value: None

        RAISES:
            None.

        RETURNS:
            string
            
        EXAMPLES:
            >>> self._get_env_name(col)
        """

        # If ColumnExpression is passed and env_name is passed with it fetch the env name,
        # else check if default "openml_user_env" env is configured or not,
        # else get the default "openml_env" env if exists or create new deafult env.
        if col and col._env_name is not None:
            from teradataml.scriptmgmt.UserEnv import UserEnv
            env = col._env_name
            env_name = env.env_name if isinstance(col._env_name, UserEnv) else env
        elif configure.openml_user_env is not None:
            env_name = configure.openml_user_env.env_name
        else:
            env_name = UtilFuncs._create_or_get_env("open_source_ml.json").env_name
        return env_name

    def _func_to_string(user_functions):
        """
        DESCRIPTION:
            Internal function to get the user functions in a single string format.

        PARAMETERS:
            user_functions:
                Required Argument.
                List of user functions.
                Types: list

        RAISES:
            None.

        RETURNS:
            string

        EXAMPLES:
            >>> from teradataml.dataframe.functions import udf
            >>> @udf(returns=VARCHAR())
            ... def sum(x, y):
            ...     return x+y
            >>>
            >>> def to_upper(s):
            ...    return s.upper()
            >>> user_functions = [sum(1,2)._udf, to_upper]
            >>> res = self._func_to_string(user_functions)
            >>> print(res)
            def sum(x, y):
                return x+y

            def to_upper(s):
                return s.upper()

            >>>
        """
        user_function_code = ""
        for func in user_functions:
            # Get the source code of the user function.
            # Note that, checking for lambda function is required for teradatamlspk UDFs
            # If the function is a lambda function, get the source code from __source__.
            func = getsource(func) if func.__code__.co_name != "<lambda>" else func.__source__

            # If the function have any extra space in the beginning remove it.
            func = func.lstrip()
            # Function can have decorator,e.g. udf as decorator, remove it.
            if func.startswith("@"):
                func = func[func.find("\n")+1: ].lstrip()
            # If multiple functions are passed, separate them with new line.
            user_function_code += func + '\n'
        return user_function_code

    @staticmethod
    def _get_qualified_table_name(schema_name, table_name):
        """
        DESCRIPTION:
            Internal function to get the fully qualified name of table.

        PARAMETERS:
            schema_name:
                Required Argument.
                Specifies the name of the schema.
                Types: str

            table_name:
                Required Argument.
                Specifies the name of the table.
                Types: str

        RAISES:
            None.

        RETURNS:
            string

        EXAMPLES:
            >>> UtilFuncs._get_qualified_table_name("schema_name", "table_name")
            '"schema_name"."table_name"'
        """
        return '"{}"."{}"'.format(schema_name, table_name)

    def _check_python_version_diff(env = None):
        """
        DESCRIPTION:
            Internal function to check the python version difference between Vantage and local.
            
        PARAMETERS:
            env:
                Optional Argument.
                Specifies the user environment for Vantage Cloud Lake.
                Types: str, object of class UserEnv
                Default Value: None

        RAISES:
            TeradataMlException

        RETURNS:
            None.

        EXAMPLES:
            >>> self._check_python_version_diff(env)
        """
        if env:
            # Get the Python interpreter version of the user environment.
            from teradataml.scriptmgmt.lls_utils import list_user_envs
            from teradataml.scriptmgmt.UserEnv import UserEnv
            env_list = list_user_envs()
            user_env_name = env.env_name if isinstance(env, UserEnv) else env
            env_base_version = env_list[env_list['env_name'] == user_env_name].base_env_name.values
            # Check if the user environment is not found, then return.
            if len(env_base_version) == 0:
                return
            python_env = env_base_version[0].split("_")[1]

            # Get the Python interpreter version of the local environment.
            from teradataml.context import context as tdmlctx
            python_local = tdmlctx.python_version_local.rsplit(".", 1)[0]
            # Check if the Python interpreter major versions are consistent between Lake user environment and local.
            # If not, raise an exception.
            if python_env != python_local:
                raise TeradataMlException(Messages.get_message(MessageCodes.PYTHON_VERSION_MISMATCH_OAF,
                                                                python_env, python_local),
                                            MessageCodes.PYTHON_VERSION_MISMATCH_OAF)
        else:
            from teradataml.context import context as tdmlctx
            from teradataml.dbutils.dbutils import (db_python_version_diff,
                                                    set_session_param)
            set_session_param("searchuifdbpath",
                              UtilFuncs._get_dialect_quoted_name(tdmlctx._get_current_databasename()))
            if len(db_python_version_diff()) > 0:
                # Raise exception when python versions don't match between Vantage and local.
                py_major_vantage_version = tdmlctx.python_version_vantage.rsplit(".", 1)[0]
                raise TeradataMlException(Messages.get_message(MessageCodes.PYTHON_VERSION_MISMATCH,
                                                                tdmlctx.python_version_vantage, py_major_vantage_version),
                                            MessageCodes.PYTHON_VERSION_MISMATCH)

    def _check_package_version_diff(func, packages, env=None):
        """
        DESCRIPTION:
            Internal function to process packages differences between Vantage and local.
            Note:
                * Raises a warning if the versions of certain Python packages are not consistent between Vantage and local.

        PARAMETERS:
            func:
                Required Argument.
                Specifies the function name.
                Types: str

            packages:
                Required Argument.
                Specifies the list of package names.
                Types: list of str

            env:
                Optional Argument.
                Specifies the user environment for Vantage Cloud Lake.
                Types: str, object of class UserEnv
                Default Value: None

        RETURNS:
            None

        RAISES:
            OneTimeUserWarning

        EXAMPLES:
            self._process_package_differences("apply", ["dill"], env)
        """

        # Check if OSML required packages are verified or not.
        from teradataml.opensource._constants import \
            _packages_verified_in_vantage
        _is_packages_verfied_in_vantage = _packages_verified_in_vantage.get(
            func, None)
        if _is_packages_verfied_in_vantage:
            return

        if env:
            from teradataml.scriptmgmt.lls_utils import get_env
            from teradataml.scriptmgmt.UserEnv import UserEnv
            env = env if isinstance(env, UserEnv) else get_env(env)
            env_pkg_df = env.libs
            pkgs_dict = dict(zip(env_pkg_df['name'], env_pkg_df['version']))

            from importlib.metadata import version
            warning_raised = False
            strr = []
            for pkg in packages:
                env_version = pkgs_dict.get(pkg)
                local_version = version(pkg)
                # Write the requirements file listing all the related packages and their versions
                # if the versions Python packages are not consistent between Vantage and local.
                if env_version != local_version:
                    warning_raised = True
                    strr.append(f"{pkg}=={local_version}")

            # If there are differences in package versions, display a warning message to the user.
            # about the package differences and the requirements file created for the user to install the packages
            if warning_raised:
                file_name = f"requirements_{func}.txt"
                req_file = os.path.join(GarbageCollector._get_temp_dir_name(), file_name)
                with open(req_file, "w") as f:
                    f.write("\n".join(strr))

                packages = "{}".format(packages[0]) if len(packages) == 1 else\
                           "', '".join(packages[:-1]) + "' and '" + packages[-1]

                if func == "apply":
                    warning_msg = f"The version of certain Python packages are not consistent between Lake "\
                        f"user environment and local. Teradata recommends to maintain same version of '{packages}' "\
                        f"between Lake user environment and local for '{func}'."
                else:
                    _packages_verified_in_vantage[func] = True
                    warning_msg = "The versions of certain Python packages are not consistent between "\
                        "Lake user environment and local. OpenSourceML compares the versions of '{}' "\
                        f"(and also matches the patterns of these packages) used by 'td_{func}'. "\
                        "Teradata recommends same versions for all the Python packages between Lake "\
                        "user environment and local."

                req = f"\nA requirements file listing all '{func}' " + \
                    f"related packages and their versions has been written to '{req_file}'. "+ \
                    "Update the Lake user environment with the required packages.\n"

                warning_msg += req
                warnings.warn(warning_msg.format(packages), category=OneTimeUserWarning)

        else:
            # Check if the versions of Python packages are consistent between Vantage and local.
            from teradataml.dbutils.dbutils import \
                _db_python_package_version_diff
            all_package_versions = _db_python_package_version_diff(packages, only_diff=False)
            package_difference = \
                all_package_versions[all_package_versions.vantage != all_package_versions.local]
            # If there are differences in package versions, raise a warning.
            if package_difference.shape[0] > 0:
                strr = []
                # Write the requirements file listing all the related packages and their versions.
                for rec in all_package_versions.to_records():
                    strr.append(f"{rec[1]}=={rec[2]}")
                file_name = f"requirements_{func}.txt"
                req_file = os.path.join(GarbageCollector._get_temp_dir_name(), file_name)
                with open(req_file, "w") as f:
                    f.write("\n".join(strr))

                packages = "{}".format(packages[0]) if len(packages) == 1 else\
                           "', '".join(packages[:-1]) + "' and '" + packages[-1]

                if func in ["map_row", "map_partition"]:
                    warning_msg = f"The version of certain Python packages are not consistent between "\
                        "Vantage and local. User can identify them using db_python_package_version_diff() "\
                        f"function. Teradata recommends to maintain same version of '{packages}' "\
                        f"between Vantage and local for '{func}'."
                else:
                    _packages_verified_in_vantage[func] = True
                    warning_msg = "The versions of certain Python packages are not consistent between "\
                        "Vantage and local. User can identify them using db_python_package_version_diff() "\
                        "function. OpenSourceML compares the versions of '{}' (and also matches the "\
                        f"patterns of these packages) used by 'td_{func}'. Teradata "\
                        "recommends to maintain same versions for all the Python packages between Vantage "\
                        "and local."

                # Display a warning message to the user about the package differences
                # and the requirements file created for the user to install the packages.
                req = f"\nA requirements file listing all '{func}' " + \
                    f"related packages and their versions has been written to '{req_file}'.\n"

                warning_msg += req
                warnings.warn(warning_msg.format(packages), category=OneTimeUserWarning)

    @staticmethod
    def _get_dialect_quoted_name(object_name):
        """
        DESCRIPTION:
            Function to quote the SQL identifiers as per teradatasqlalchemy's quoting rules.

        PARAMETERS:
            object_name
                Required Argument.
                Specifies the name of the SQL identifier to be quoted.
                Type: str

        RAISES:
            None

        RETURNS:
            Quoted object name.

        EXAMPLES:
            _get_dialect_quoted_name(object_name = "tdml.alice")

        OUTPUT:
            '"tdml.alice"'
        """
        tdp = preparer(td_dialect)
        return tdp.quote(object_name)

    @staticmethod
    def _get_hash_value(identifier):
        """
        DESCRIPTION:
            Function to get the hash value of the identifier.

        PARAMETERS:
            identifier
                Required Argument.
                Specifies the identifier to be hashed.
                Type: str

        RAISES:
            None

        RETURNS:
            Hash value of the identifier.

        EXAMPLES:
            UtilFuncs._get_hash_value(identifier = "tdml.alice")

        OUTPUT:
            a6c64c2c_58e9_5060_b811_00839ea493ed
        """
        # Generate a hash value using SHA-256
        hash_object = hashlib.sha256(identifier.encode())
        hash_hex = hash_object.hexdigest()

        # Format the hash value to match the desired format
        formatted_hash = f"{hash_hex[:8]}_{hash_hex[8:12]}_{hash_hex[12:16]}_{hash_hex[16:20]}_{hash_hex[20:32]}"

        return formatted_hash

    @staticmethod
    def _get_http_status_phrases_description():
        """
        DESCRIPTION:
            Function to get phrases and description for all HTTP status codes.

        PARAMETERS:
            None

        RETURNS:
            dict

        EXAMPLES:
            >>> UtilFuncs._get_http_status_phrases_description()
        """
        from http import HTTPStatus
        return {status.value: {"phrase": status.phrase, "description": status.description} \
                for status in HTTPStatus}

    @staticmethod
    def _get_time_formatted_string(period):
        """
        DESCRIPTION:
            Converts a string representing Period to the formatted TIMESTAMP/DATE string for snapshot queries.

        PARAMETERS:
            period:
                Required Argument.
                Specifies the period string to be converted.
                Types: str

        RETURNS:
            The formatted TIMESTAMP/DATE string.

        RAISES:
            ValueError.

        EXAMPLES:
        >>> UtilFuncs._get_time_formatted_string('2025-06-01 12:00:00.123')
        """
        # Try to parse as datetime string
        try:
            for fmt in ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
                try:
                    dt = datetime.datetime.strptime(period, fmt)
                    # If input had microseconds, preserve them
                    if "%f" in fmt and "." in period:
                        # Remove trailing zeros and dot if needed
                        result = "TIMESTAMP'{}'".format(dt.strftime("%Y-%m-%d %H:%M:%S.%f").rstrip("0").rstrip("."))
                    elif "%S" in fmt:
                        result = "TIMESTAMP'{}'".format(dt.strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        result = "DATE'{}'".format(dt.strftime("%Y-%m-%d"))
                    return result
                except ValueError:
                    continue
            raise ValueError(f"Unrecognized period format: {period}")
        except Exception as e:
            raise ValueError(f"Could not convert period: {period}") from e

    @staticmethod
    def extract_table_names_from_query(query):
        """
        Extracts all table/view names from FROM, JOIN, and ON-AS clauses in a SQL query.
        Handles nested queries and captures subqueries in ON (...), and ON <table> AS <alias>.
        """
        # Regex for FROM, JOIN, and ON ... AS ... clauses
        # This is a simplification; for production, use a SQL parser.
        table_names = set()
        # FROM ... (possibly with nested SELECT)
        for match in re.finditer(r'from\s+([^\s\(\)]+)', query, re.IGNORECASE):
            table_names.add(match.group(1).strip())
        # JOIN ... (possibly with nested SELECT)
        for match in re.finditer(r'join\s+([^\s\(\)]+)', query, re.IGNORECASE):
            table_names.add(match.group(1).strip())
        # ON ( ... ) AS ... Nested Query in ON Clause.
        for match in re.finditer(r'ON\s+\(([^)]+)\)\s+AS\s+["\']?\w+["\']?', query, re.IGNORECASE):
            table_names.update(UtilFuncs.extract_table_names_from_query(match.group(1)))
        # ON <table> AS <alias> (no parentheses)
        for match in re.finditer(r'ON\s+(["\']?\w+["\']?(?:\.["\']?\w+["\']?)*)\s+AS\s+["\']?\w+["\']?', query, re.IGNORECASE):
            table_names.add(match.group(1).strip())
        return list(table_names)

    @staticmethod
    def _get_normalize_and_deduplicate_columns(columns):
        """
        DESCRIPTION:
            Function that normalizes and deduplicates a list of column names.
            This function processes the "columns", which can be a list of column names
            as strings or ColumnExpression, or a single column name/ColumnExpression.
            It extracts the column names, removes duplicates while preserving order, 
            and returns the resulting list of unique column names.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the column.
                Types: str, ColumnExpression, list of str or ColumnExpression

        RAISES:
            None

        RETURNS:
            list

        EXAMPLES:
            >>> load_examples_data('dataframe', 'sales')
            >>> df = DataFrame('sales')
            >>> columns = [df.Jan, 'Jan', 'Feb', df.Feb, 'Mar']
            >>> UtilFuncs._get_normalize_and_deduplicate_columns(columns)
            ['Jan', 'Feb', 'Mar']

        """
        columns_list = []
        seen = set()

        for column in (columns if isinstance(columns, list) else [columns]):
            name = column if isinstance(column, str) else column.name
            if name not in seen:
                seen.add(name)
                columns_list.append(name)

        return columns_list

# Keeping at the end to avoid circular dependency
from teradataml.common.aed_utils import AedUtils
from teradataml.dbutils.filemgr import remove_file
