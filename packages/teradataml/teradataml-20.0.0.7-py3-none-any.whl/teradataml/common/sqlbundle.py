# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: ellen.nolan@teradata.com
Secondary Owner:

teradataml.common.sqlbundle
----------
A class for holding all SQL texts.
"""

from teradataml.common.constants import SQLConstants
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes

class SQLBundle:

    def __init__(self):
        """
        Initializer for SQLBundle.
        Contains the SQL texts (bundles) for different versions of Teradata Vantage.

        PARAMETERS:
            None

        RETURNS:
            Instance of SQLBundle

        RAISES:
            None

        """

        self._sqlversion_map_ = {}
        self.sql16_00 = [
                [SQLConstants.SQL_BASE_QUERY, "SELECT * FROM {0}"],
                [SQLConstants.SQL_SAMPLE_QUERY, " {0} SAMPLE {1}"],
                [SQLConstants.SQL_SAMPLE_WITH_WHERE_QUERY, " {0} WHERE {1} SAMPLE {2}"],
                [SQLConstants.SQL_CREATE_VOLATILE_TABLE_FROM_QUERY_WITH_DATA, "CREATE MULTISET VOLATILE TABLE {0} AS ({1}) WITH DATA NO PRIMARY INDEX ON COMMIT PRESERVE ROWS"],
                [SQLConstants.SQL_CREATE_VOLATILE_TABLE_FROM_QUERY_WITHOUT_DATA, "CREATE MULTISET VOLATILE TABLE {0} AS ({1}) WITH NO DATA NO PRIMARY INDEX"],
                [SQLConstants.SQL_CREATE_VOLATILE_TABLE_USING_COLUMNS, "CREATE MULTISET VOLATILE TABLE {0}( {1} ) NO PRIMARY INDEX"],
                [SQLConstants.SQL_CREATE_TABLE_FROM_QUERY_WITH_DATA, "CREATE MULTISET TABLE {0} AS ({1}) WITH DATA"],
                [SQLConstants.SQL_HELP_COLUMNS, "help column {0}.*"],
                [SQLConstants.SQL_DROP_TABLE, "DROP TABLE {0}"],
                [SQLConstants.SQL_DROP_VIEW, "DROP VIEW {0}"],
                [SQLConstants.SQL_NROWS_FROM_QUERY, "SELECT CAST(COUNT(*) AS BIGINT) FROM {0}"],
                [SQLConstants.SQL_TOP_NROWS_FROM_TABLEORVIEW, "select top {0} * from {1}"],
                [SQLConstants.SQL_INSERT_INTO_TABLE_VALUES, "insert into {0} values({1})"],
                [SQLConstants.SQL_SELECT_COLUMNNAMES_FROM, "sel {0} from ({1}) as {2}"],
                [SQLConstants.SQL_SELECT_DATABASE, "select database"],
                [SQLConstants.SQL_HELP_VOLATILE_TABLE, "HELP VOLATILE TABLE"],
                [SQLConstants.SQL_CREATE_VIEW, "CREATE VIEW {0} AS {1}"],
                [SQLConstants.SQL_SELECT_TABLE_NAME, "SELECT TRIM(TABLENAME) FROM DBC.TABLESV WHERE TABLENAME = '{0}'"],
                [SQLConstants.SQL_SELECT_USER, "select user"],
                [SQLConstants.SQL_HELP_VIEW, "HELP VIEW {0}"],
                [SQLConstants.SQL_HELP_TABLE, "HELP TABLE {0}"],
                [SQLConstants.SQL_HELP_INDEX, "help index {0}"],
                [SQLConstants.SQL_SELECT_DATABASENAME, "SELECT TABLENAME FROM DBC.TABLESV WHERE DATABASENAME = '{0}'"],
                [SQLConstants.SQL_AND_TABLE_KIND, " AND TABLEKIND IN ({0})"],
                [SQLConstants.SQL_AND_TABLE_NAME, " AND TABLENAME = '{0}'"],
                [SQLConstants.SQL_AND_TABLE_NAME_LIKE, " AND TABLENAME LIKE ALL ({0})"],
                [SQLConstants.SQL_INSERT_ALL_FROM_TABLE, "INSERT into {0} SELECT {2} from {1}"],
                [SQLConstants.SQL_DELETE_ALL_ROWS, "DELETE FROM {0}"],
                [SQLConstants.SQL_DELETE_SPECIFIC_ROW, "DELETE FROM {0} WHERE {1}"],
                [SQLConstants.SQL_CREATE_TABLE_USING_COLUMNS, "CREATE MULTISET TABLE {0}( {1} )"],
                [SQLConstants.SQL_EXEC_STORED_PROCEDURE, "call {0}"],
                [SQLConstants.SQL_SELECT_COLUMNNAMES_WITH_WHERE, "sel {0} from {1} where {2}"],
                [SQLConstants.SQL_HELP_DATABASE, "HELP DATABASE {0}"],
                [SQLConstants.SQL_HELP_DATALAKE, "HELP DATALAKE {0}"],
                [SQLConstants.SQL_INSERT_INTO_TABLE_VALUES_WITH_COLUMN_NAMES, "insert into {0} ({1}) values({2})"],
                [SQLConstants.SQL_HELP_DATALAKE, "HELP DATALAKE {0}"],
                [SQLConstants.SQL_TD_OTF_METADATA, "SELECT * FROM {0}(ON ({1})) D;"],
                [SQLConstants.SQL_TD_OTF_SNAPSHOT, "SELECT * FROM {0} FOR SNAPSHOT AS OF {1};"],
                [SQLConstants.SQL_LIST_TRIGGERS, "SELECT TriggerName FROM DBC.TRIGGERSV WHERE DatabaseName = '{0}' AND TriggerName LIKE '{1}'"],
                [SQLConstants.SQL_SHOW_TABLE, "SHOW TABLE {0}"],
                [SQLConstants.SQL_SHOW_VIEW, "SHOW VIEW {0}"]
        ]
        self._add_sql_version()

    def _get_sql_query(self, sqlkey, userdbsversion="16.00"):
        """
        Retrieves the SQL text for the specified key and DBS version

        PARAMETERS:
            sqlkey - The key to use for retrieving the SQL text from the bundle.
                     The key should be a constant from daoconstants.py
            userdbsversion - The DBS version, default is 16.00

        RETURNS:
            SQL text or None if not found.

        RAISES:
            TeradataMlException

        EXAMPLES:
            sqltext = sqlbundle._getSQLQuery(SQLConstants.SQL_BASE_QUERY, '16.00')

        """
        for sqlversion in self._sqlversion_map_:
            if (float(userdbsversion) >= float(sqlversion)):
                sqlkeylist = self._sqlversion_map_[sqlversion]
                for querylist in sqlkeylist:
                    if (querylist[0] == sqlkey):
                        query = querylist[1]
                        return query
        raise TeradataMlException(Messages.get_message(MessageCodes.SQL_UNKNOWN_KEY), MessageCodes.SQL_UNKNOWN_KEY)

    def _add_sql_version(self):
        """
        Adds the SQL texts (bundle) for a DBS version

        PARAMETERS:
            None

        RETURNS:
            DBS Version

        RAISES:
            None

        EXAMPLES:
            sqlbundle.addsqlquery()

        """
        self._sqlversion_map_['16.00'] = self.sql16_00

    # ***** SQL QUERY BUILDER Functions ***** #
    @staticmethod
    def _build_base_query(name, orderby = None):
        """
        Builds a base select query for a table or view.
        For Example,
            SELECT * FROM <table_name>

        PARAMETERS:
            name:
                Required Argument.
                Specifies a table or view name.
                Types: str.

            orderby:
                Optional Argument.
                Specifies the orderby predicate of parent dataframe(if any).
                Default Value: None.
                Types: str.

        RETURNS:
            A base SELECT query.

        RAISES:
            None

        EXAMPLES:
            base_query = SQLBundle._build_base_query(table_name)
        """
        if orderby is not None:
            name = "{} order by {}".format(name, orderby)
        sqlbundle = SQLBundle()
        return sqlbundle._get_sql_query(SQLConstants.SQL_BASE_QUERY).format(name)

    @staticmethod
    def _build_create_view(view_name, select_expression, lock_rows=False):
        """
        Builds a CREATE VIEW DDL statement.
        For Example,
            CREATE VIEW viewname AS select * from tablename;

        PARAMETERS:
            view_name - Viewname to be created
            select_expression - A SQL from which a view is to be created. (SELECT query)
            lock_rows - When set to True, teradataml DataFrame locks the corresponding row(s) 
                        in underlying table(s) while accessing the data. Otherwise, 
                        teradataml DataFrame access the data without locking the rows.
                        Default is False.
            

        RETURNS:
            A CREATE VIEW DDL statement

        RAISES:
            None

        EXAMPLES:
            crt_view_ddl = SQLBundle._build_create_view()
        :return:
        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_CREATE_VIEW)
        if lock_rows:
            select_expression = "LOCKING ROW FOR ACCESS {}".format(select_expression)
        return query.format(view_name, select_expression)

    @staticmethod
    def _build_create_volatile_table_without_data(tablename, select_query):
        """
        Builds a create volatile table DDL statement
        with the AS(QUERY) CLAUSE with no data.
        Example:
            create multiset volatile table new_table_name AS (sel * from someview where col1 > 300) with no data

        PARAMETERS:
            tablename - The name of the new volatile table.
            select_query - The query to create the new volatile table from

        RETURNS:
            returns a create volatile table DDL statement.

        RAISES:
            None

        EXAMPLES:
            ddlstmt = SQLBundle._build_create_volatile_table_without_data('new_table_name', 'sel * from someview where col1 > 300')
        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_CREATE_VOLATILE_TABLE_FROM_QUERY_WITHOUT_DATA)
        return query.format(tablename, select_query)

    @staticmethod
    def _build_create_volatile_table_with_data(tablename, select_query):
        """
        Builds a create volatile table DDL statement
        with the AS(QUERY) CLAUSE with data.
        Example:
            create multiset volatile table new_table_name AS (sel * from someview where col1 > 300) with data on commit preserve rows

        PARAMETERS:
            tablename - The name of the new volatile table.
            select_query - The query to create the new volatile table from

        RETURNS:
            returns a create volatile table DDL statement.

        RAISES:
            None

        EXAMPLES:
            ddlstmt = SQLBundle._build_create_volatile_table_with_data('new_table_name', 'sel * from someview where col1 > 300')

        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_CREATE_VOLATILE_TABLE_FROM_QUERY_WITH_DATA)
        return query.format(tablename, select_query)

    @staticmethod
    def _build_create_table_with_data(tablename, select_query):
        """
        Builds a create multiset table DDL statement
        with the AS(QUERY) CLAUSE with data.
        Example:
            create multiset table new_table_name AS (sel * from someview where col1 > 300) with data

        PARAMETERS:
            tablename - The fully qualified quoted table name of the new table.
            select_query - The query to create the new table from

        RETURNS:
            returns a create table DDL statement.

        RAISES:
            None

        EXAMPLES:
            ddlstmt = SQLBundle._build_create_table_with_data('"dbname"."new_table_name"', 'sel * from someview where col1 > 300')

        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_CREATE_TABLE_FROM_QUERY_WITH_DATA)
        return query.format(tablename, select_query)

    @staticmethod
    def _build_drop_table(tablename, purge_clause=None):
        """
        Returns a drop table DDL statement for a table.
        Example:
            drop table mytab

        PARAMETERS:
            tablename - The table to drop.
            purge_clause - String representing purge clause.

        RETURNS:
            Returns a drop table DDL statement for the table.

        RAISES:
            None

        EXAMPLES:
            drop_stmt = SQLBundle._build_drop_table('my_tab')
            drop_stmt = SQLBundle._build_drop_table("my_lake"."my_db"."my_tab",
                                                    purge_clause='PURGE ALL')
            drop_stmt = SQLBundle._build_drop_table("my_lake"."my_db"."my_tab",
                                                    purge_clause='NO PURGE')
        """
        sqlbundle = SQLBundle()
        drop_stmt = sqlbundle._get_sql_query(SQLConstants.SQL_DROP_TABLE).format(tablename)
        if purge_clause:
            drop_stmt = "{} {}".format(drop_stmt, purge_clause)
        return drop_stmt

    @staticmethod
    def _build_drop_view(viewname):
        """
        Returns a drop view DDL statement for a view.
        Example:
            drop view myview

        PARAMETERS:
            viewname - The name of the view to be drop

        RETURNS:
            Returns a drop view DDL statement for the view.

        RAISES:
            None

        EXAMPLES:
            dropstmt = SQLBundle._build_drop_view('myview')

        """
        sqlbundle = SQLBundle()
        dropstmt = sqlbundle._get_sql_query(SQLConstants.SQL_DROP_VIEW)
        return dropstmt.format(viewname)

    @staticmethod
    def _build_help_column(table_name):
        """
        Builds a HELP COLUMN command to retrieve column metadata for table or view.
        Example:
            "help column mytab.*"
            "help column myview.*"

        PARAMETERS:
            table_name - The name of table or view.

        RETURNS:
            returns a HELP COLUMN command.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_help_column('mytab')

        """
        sqlbundle = SQLBundle()
        help_col_sql = sqlbundle._get_sql_query(SQLConstants.SQL_HELP_COLUMNS)
        return help_col_sql.format(table_name)

    def _build_help_view(view_name):
        """
        Builds a HELP VIEW command to retrieve column metadata for view.
        Example:
            "help view myview"

        PARAMETERS:
            view_name - The name of the view.

        RETURNS:
            returns a HELP TABLE command.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_help_view('myview')

        """
        sqlbundle = SQLBundle()
        help_view_sql = sqlbundle._get_sql_query(SQLConstants.SQL_HELP_VIEW)
        return help_view_sql.format(view_name)

    def _build_help_table(table_name):
        """
        Builds a HELP TABLE command to retrieve column metadata for table.
        Example:
            "help table mytable"

        PARAMETERS:
            table_name - The name of the table.

        RETURNS:
            returns a HELP TABLE command.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_help_table('mytable')
            query = SQLBundle._build_help_table('mydb.mytable')
            query = SQLBundle._build_help_table("mydb"."mytable")

        """
        sqlbundle = SQLBundle()
        help_table_sql = sqlbundle._get_sql_query(SQLConstants.SQL_HELP_TABLE)
        return help_table_sql.format(table_name)

    @staticmethod
    def _build_help_volatile_table():
        """
        Builds a query to get help from a volatile table.

        Example:
            "HELP VOLATILE TABLE"

        PARAMETERS:

        RETURNS:
            returns a HELP VOLATILE TABLE command.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_help_volatile_table()
        """
        sqlbundle = SQLBundle()
        return sqlbundle._get_sql_query(SQLConstants.SQL_HELP_VOLATILE_TABLE)

    @staticmethod
    def _build_help_datalake(datalake_name):
        """
        Builds a query to get help on datalake.

        Example:
            "HELP DATALAKE datalake_name;"

        PARAMETERS:

        RETURNS:
            returns a HELP DATALAKE <datalake_name> command.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_help_datalake(datalake_name)
        """
        sqlbundle = SQLBundle()
        help_datalake_sql = sqlbundle._get_sql_query(SQLConstants.SQL_HELP_DATALAKE)
        return help_datalake_sql.format(datalake_name)

    def _build_select_table_name(tab_name):
        """
        Builds a query to get table name from DBC.TABLESV

        Example:
            "SELECT TRIM(TABLENAME) FROM DBC.TABLESV WHERE TABLENAME = 'tab_name'"

        PARAMETERS:

        RETURNS:
            returns a SELECT TABLE NAME SQL query.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_select_table_name()
        """
        sqlbundle = SQLBundle()
        return sqlbundle._get_sql_query(SQLConstants.SQL_SELECT_TABLE_NAME).format(tab_name)

    @staticmethod
    def _build_select_table_kind(schema_name, table_name, table_kind):
        """
        Builds a query to get the table names from DBC.TABLESV based on table kind.

        Example:
            "SELECT TABLENAME FROM DBC.TABLESV WHERE DATABASENAME = 'db1' and TABLENAME = 'tab_name%' and tablekind = 'V'"

        PARAMETERS:
            schema_name - The name of the schema.
            table_name  - The table name.
            table_kind  - The table kind.

        RETURNS:
            Returns a SELECT TABLE NAME SQL query.

        RAISES:
            None.

        EXAMPLES:
            query = SQLBundle._build_select_table_kind('db1','abc%','V')
        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_SELECT_DATABASENAME).format(schema_name)
        if table_name:
            if '%' in table_name:
                # Check if '%' is present in the between of table name excluding first and last character
                # as '%' can be present at the start or end of table name
                # and replace single quotes with empty string
                # Checking for following cases with % in between table name:
                # eg: table_name = 'ab%c', '%a%bc', '%ab%c%' or 'ab%c%'

                # table_name[1:-1] - Removing single quotes from table name
                # table_name[1:-1][1:-1] - Removing first and last character from table_name[1:-1]
                if '%' in table_name[1:-1][1:-1]:
                    query = "{0}{1}".format(query, sqlbundle._get_sql_query(SQLConstants.SQL_AND_TABLE_NAME_LIKE).format(table_name))
                else:
                    # Checking for following cases with % at the start or end of table name:
                    # eg: table_name = '%abc', 'abc%', '%abc%'
                    # Extracting table name without '%' character
                    table_name_str = table_name.replace('%', '')

                    # Adding condition to check if table name contains the string using POSITION function.
                    # POSITION function returns the position index of the substring in the string if found,
                    # else returns 0
                    query = "{0}{1}{2}".format(query, sqlbundle._get_sql_query(SQLConstants.SQL_AND_TABLE_NAME_LIKE).format(table_name), \
                                            " AND POSITION({0} IN TABLENAME) > 0".format(table_name_str))
            else:
                query = "{0}{1}".format(query, sqlbundle._get_sql_query(SQLConstants.SQL_AND_TABLE_NAME_LIKE).format(table_name))
        if table_kind:
            query = '{0}{1}'.format(query, sqlbundle._get_sql_query(SQLConstants.SQL_AND_TABLE_KIND).format(table_kind))
        
        return query

    # TODO :: Following SQLConstants needs to be implemented as and when needed.
    #   1. SQL_SAMPLE_QUERY
    #   2. SQL_SAMPLE_WITH_WHERE_QUERY
    #   3. SQL_CREATE_VOLATILE_TABLE_USING_COLUMNS, "CREATE MULTISET VOLATILE TABLE {0}( {1} )"],
    #   4. SQL_SELECT_COLUMNNAMES_FROM
    #   5. SQL_SELECT_DATABASE

    @staticmethod
    def _build_nrows_print_query(table_name):
        """
        Returns select query to return number of rows.

        PARAMETERS:
            table_name - Table name

        EXAMPLES:
            sqlbundle._build_nrows_print_query("table_test")

        RETURNS:
            select query.

        RAISES:
            None
        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_NROWS_FROM_QUERY)
        return query.format(table_name)

    @staticmethod
    def _build_top_n_print_query(table_name, no_of_rows, orderby = None):
        """
        Returns select query to return top no_of_rows rows.

        PARAMETERS:
            no_of_rows - top numbers of to be returned
            table_name - Table name
            orderby    - order expression to sort returned rows.
                         Expression should be properly quoted as per the Database rules.

        EXAMPLES:
            UtilFuncs._build_top_n_print_query(10, "table_test")

        RETURNS:
            select query.

        RAISES:
            None
        """
        # Append orderby cluase to the table name if it is not None.
        if orderby is not None:
            table_name = "{} order by {}".format(table_name, orderby)
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_TOP_NROWS_FROM_TABLEORVIEW)
        return query.format(no_of_rows, table_name)

    @staticmethod
    def _build_help_index(table_name):
        """
        Builds a HELP INDEX command to retrieve primary index for table or volatile table.
        Example:
            "help index mytab"
            "help index myvoltab"

        PARAMETERS:
            table_name - The name of table or volatile table.

        RETURNS:
            Returns a HELP INDEX command.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_index_column('mytab')

        """
        sqlbundle = SQLBundle()
        help_index_sql = sqlbundle._get_sql_query(SQLConstants.SQL_HELP_INDEX)
        return help_index_sql.format(table_name)

    @staticmethod
    def _build_insert_from_table_query(to_table_name, from_table_name, column_order_string):
        """
        Returns insert query to insert all rows from from_table_name table to to_table_name table
        using columns listed in order as per column_order_string.

        PARAMETERS:
            to_table_name - String specifying name of the SQL Table to insert records into.
            from_table_name - String specifying name of the SQL Table to insert records from.
            column_order_string - String specifying comma separated table column names to be used.

        EXAMPLES:
            UtilFuncs._build_insert_from_table_query('table1', 'table2', 'col1, col2, col3')

        RETURNS:
            Insert query string.

        RAISES:
            None
        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_INSERT_ALL_FROM_TABLE)
        return query.format(to_table_name, from_table_name, column_order_string)
    
    @staticmethod
    def _build_create_table_using_columns(tablename, columns_datatypes):
        """
        Builds a create table DDL statement with colummns and datatypes
        Example:
            create multiset table tablename (col1 varchar(10), col2 integer, col3 timestamp)

        PARAMETERS:
            tablename - The name of the table.
            columns_datatypes - Columns and datatypes to build the DDL stattement

        RETURNS:
            returns a create table DDL statement.

        RAISES:
            None

        EXAMPLES:
            ddlstmt = SQLBundle._build_create_table_using_columns('col1 varchar(10), col2 integer, col3 timestamp')

        """
        sqlbundle = SQLBundle()
        ddlstmt = sqlbundle._get_sql_query(SQLConstants.SQL_CREATE_TABLE_USING_COLUMNS)
        return ddlstmt.format(tablename, columns_datatypes)
    
    @staticmethod
    def _build_insert_into_table_records(tablename, columns, column_names=None):
        """
        Builds a prepared statement with parameter markers for a table.
        This is an internal function.
        
        PARAMETERS:
            tablename - Table name to insert data.
            columns - The parameter markers for the prepared statement
            column_names - The column names to be inserted.

        RETURNS:
            Returns a prepared statement.

        RAISES:
            None
        
        EXAMPLES:
            preprdstmt = SQLBundle.SQL_INSERT_INTO_TABLE_VALUES('mytab', '?, ?')
            preprdstmt = SQLBundle.SQL_INSERT_INTO_TABLE_VALUES_WITH_COLUMN_NAMES('mytab', 'column1, column2',  '?, ?')

        """
        sqlbundle = SQLBundle()
        sqlkey = (SQLConstants.SQL_INSERT_INTO_TABLE_VALUES_WITH_COLUMN_NAMES
              if column_names else SQLConstants.SQL_INSERT_INTO_TABLE_VALUES)
        query = sqlbundle._get_sql_query(sqlkey)
        return (query.format(tablename, column_names, columns)
            if column_names else query.format(tablename, columns))

    @staticmethod
    def _build_delete_all_rows_from_table(tablename):
        """
        Builds a SQL statement with parameter markers for a table, to delete all rows.
        This is an internal function.

        PARAMETERS:
            tablename - Table name whose all rows needs to be deleted.

        RETURNS:
            Returns a delete statement.

        RAISES:
            None

        EXAMPLES:
            deletestmt = SQLBundle._build_delete_all_rows_from_table('mytab')

        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_DELETE_ALL_ROWS)
        return query.format(tablename)

    @staticmethod
    def _build_delete_spcific_rows_from_table(tablename, conditional_predicate):
        """
        Builds a SQL statement with parameter markers for a table, to delete certain rows.
        This is an internal function.

        PARAMETERS:
            tablename - Table name whose rows needs to be deleted.
            conditional_predicate - Predicate to be used for deleting rows.

        RETURNS:
            Returns a delete statement.

        RAISES:
            None

        EXAMPLES:
            deletestmt = SQLBundle._build_delete_spcific_rows_from_table('mytab', "col1 == 10")

        """
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_DELETE_SPECIFIC_ROW)
        return query.format(tablename, conditional_predicate)

    @staticmethod
    def _build_sample_rows_from_table(table_name, num_rows, orderby = None):
        """
        Builds a SQL statement to sample specified number of rows.
        This is an internal function.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the table name whose rows needs to be sampled.
                Types: str.

            num_rows:
                Required Argument.
                Specifies the number of rows to be sampled.
                Types: int.

            orderby:
                Optional Argument.
                Specifies the orderby predicate of parent dataframe(if any).
                Default Value: None.
                Types: str.

        RETURNS:
            A SELECT query with SAMPLE.

        RAISES:
            None

        EXAMPLES:
            query = SQLBundle._build_sample_rows_from_table('mytab', 10)

        """
        # Append orderby cluase to the table name if it is not None.
        if orderby is not None:
            table_name = "{} order by {}".format(table_name, orderby)
        sqlbundle = SQLBundle()
        query = sqlbundle._get_sql_query(SQLConstants.SQL_SAMPLE_QUERY)
        return query.format(sqlbundle._get_sql_query(SQLConstants.SQL_BASE_QUERY).format(table_name), num_rows)