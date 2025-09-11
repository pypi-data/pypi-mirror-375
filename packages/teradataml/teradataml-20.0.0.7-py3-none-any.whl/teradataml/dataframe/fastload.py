#!/usr/bin/python
# ##################################################################
#
# Copyright 2019 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Abhinav Sahu (abhinav.sahu@teradata.com)
# Secondary Owner: 
#
# ##################################################################

import re
import datetime
import warnings
import pandas as pd

from sqlalchemy import MetaData, Table, Column
from sqlalchemy.exc import OperationalError as sqlachemyOperationalError

from teradataml.context.context import _get_current_databasename
from teradataml.dataframe import dataframe
from teradataml.context.context import *
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.common.constants import TeradataConstants, DriverEscapeFunctions
from teradataml.common.utils import UtilFuncs
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.utils.validators import _Validators
from teradataml.dataframe.copy_to import copy_to_sql, \
                                        _validate_pti_copy_parameters, _create_table_object, \
                                        _create_pti_table_object, _extract_column_info, \
                                        _check_columns_insertion_compatible
from teradataml.dataframe.data_transfer import _DataTransferUtils
from teradataml.telemetry_utils.queryband import collect_queryband


@collect_queryband(queryband="fstLd")
def fastload(df, table_name, schema_name=None, if_exists='replace', index=False, 
             index_label=None, primary_index=None, types=None, batch_size=None, 
             save_errors=False, open_sessions=None, err_tbl_1_suffix=None,
             err_tbl_2_suffix=None, err_tbl_name=None, warn_tbl_name=None,
             err_staging_db=None):
    """
    The fastload() API writes records from a Pandas DataFrame to Teradata Vantage 
    using Fastload. FastLoad API can be used to quickly load large amounts of data
    in an empty table on Vantage.
    1. Teradata recommends to use this API when number rows in the Pandas DataFrame
       is greater than 100,000 to have better performance. To insert lesser rows, 
       please use copy_to_sql for optimized performance. The data is loaded in batches.
    2. FastLoad API cannot load duplicate rows in the DataFrame if the table is a
       MULTISET table having primary index.
    3. FastLoad API does not support all Teradata Advanced SQL Engine data types. 
       For example, target table having BLOB and CLOB data type columns cannot be
       loaded.
    4. If there are any incorrect rows i.e. due to constraint violations, data type 
       conversion errors, etc., FastLoad protocol ignores those rows and inserts 
       all valid rows.
    5. Rows in the DataFrame that failed to get inserted are categorized into errors 
       and warnings by FastLoad protocol and these errors and warnings are stored 
       into respective error and warning tables by FastLoad API.
    6. fastload() creates 2 error tables when data is erroneous. These error tables are
       refered as ERR_1 and ERR_2 tables.
       * ERR_1 table is used to capture rows that violate the constraints or have format
         errors. It typically contains information about rows that could not be inserted
         into the target table due to data conversion errors, constraint violations, etc.
       * ERR_2 table is used to log any duplicate rows found during the load process and
         which are not loaded in target table, since fastLoad does not allow duplicate
         rows to be loaded into the target table.
    7. When "save_errors" argument is set to True, ERR_1 and ERR_2 tables are presisted.
       The fully qualified names of ERR_1, ERR_2 and warning tables are shown once the
       fastload operation is complete.
    8. If user wants both error and warnings information from pandas dataframe to be
       persisted rather than that from ERR_1 and ERR_2 tables, then "save_errors" should
       be set to True and "err_tbl_name" must be provided.

    For additional information about FastLoad protocol through teradatasql driver, 
    please refer the FASTLOAD section of https://pypi.org/project/teradatasql/#FastLoad
    driver documentation for more information.

    PARAMETERS:
        df:
            Required Argument. 
            Specifies the Pandas DataFrame object to be saved in Vantage.
            Types: pandas.DataFrame

        table_name:
            Required Argument.
            Specifies the name of the table to be created in Vantage.
            Types: String

        schema_name:
            Optional Argument. 
            Specifies the name of the database schema in Vantage to write to.
            Types: String
            Default: None (Uses default database schema).

        if_exists:
            Optional Argument.
            Specifies the action to take when table already exists in Vantage.
            Types: String
            Possible values: {'fail', 'replace', 'append'}
                - fail: If table exists, raise TeradataMlException.
                - replace: If table exists, drop it, recreate it, and insert data.
                - append: If table exists, insert data. Create if does not exist.
            Default: replace

        index:
            Optional Argument.
            Specifies whether to save Pandas DataFrame index as a column or not.
            Types: Boolean (True or False)
            Default: False

        index_label: 
            Optional Argument.
            Specifies the column label(s) for Pandas DataFrame index column(s).
            Types: String or list of strings
            Default: None

        primary_index:
            Optional Argument.
            Specifies which column(s) to use as primary index while creating table 
            in Vantage. When set to None, No Primary Index (NoPI) tables are created.
            Types: String or list of strings
            Default: None
            Example:
                primary_index = 'my_primary_index'
                primary_index = ['my_primary_index1', 'my_primary_index2', 'my_primary_index3']

        types: 
            Optional Argument.
            Specifies the data types for requested columns to be saved in Vantage.
            Types: Python dictionary ({column_name1: type_value1, ... column_nameN: type_valueN})
            Default: None

            Note:
                1. This argument accepts a dictionary of columns names and their required 
                teradatasqlalchemy types as key-value pairs, allowing to specify a subset
                of the columns of a specific type.
                   i)  When only a subset of all columns are provided, the column types
                       for the rest are assigned appropriately.
                   ii) When types argument is not provided, the column types are assigned
                       as listed in the following table:
                       +---------------------------+-----------------------------------------+
                       |     Pandas/Numpy Type     |        teradatasqlalchemy Type          |
                       +---------------------------+-----------------------------------------+
                       | int32                     | INTEGER                                 |
                       +---------------------------+-----------------------------------------+
                       | int64                     | BIGINT                                  |
                       +---------------------------+-----------------------------------------+
                       | bool                      | BYTEINT                                 |
                       +---------------------------+-----------------------------------------+
                       | float32/float64           | FLOAT                                   |
                       +---------------------------+-----------------------------------------+
                       | datetime64/datetime64[ns] | TIMESTAMP                               |
                       +---------------------------+-----------------------------------------+
                       | datetime64[ns,<time_zone>]| TIMESTAMP(timezone=True)                |
                       +---------------------------+-----------------------------------------+
                       | Any other data type       | VARCHAR(configure.default_varchar_size) |
                       +---------------------------+-----------------------------------------+
                2. This argument does not have any effect when the table specified using
                   table_name and schema_name exists and if_exists = 'append'.

        batch_size:
            Optional Argument.
            Specifies the number of rows to be loaded in a batch. For better performance,
            recommended batch size is at least 100,000. batch_size must be a positive integer. 
            If this argument is None, there are two cases based on the number of 
            rows, say N in the dataframe 'df' as explained below:
            If N is greater than 100,000, the rows are divided into batches of 
            equal size with each batch having at least 100,000 rows (except the 
            last batch which might have more rows). If N is less than 100,000, the
            rows are inserted in one batch after notifying the user that insertion 
            happens with degradation of performance.
            If this argument is not None, the rows are inserted in batches of size 
            given in the argument, irrespective of the recommended batch size. 
            The last batch will have rows less than the batch size specified, if the 
            number of rows is not an integral multiples of the argument batch_size.
            Default Value: None
            Types: int            

        save_errors:
            Optional Argument.
            Specifies whether to persist the error/warning information in Vantage 
            or not.
            Notes:
               *  When "save_errors" is set to True, ERR_1 and ERR_2 tables are presisted.
                 The fully qualified names of ERR_1, ERR_2 and warning table are returned
                 in a dictionary containing keys named as "ERR_1_table", "ERR_2_table",
                 "warnings_table" respectively.
               * When "save_errors" is set to True and "err_tbl_name" is also provided,
                 "err_tbl_name" takes precedence and error information is persisted into
                  a single table using pandas dataframe rather than in ERR_1 and ERR_2 tables.
               * When "save_errors" is set to False, errors and warnings information is
                 not persisted as tables, but it is returned as pandas dataframes in a
                 dictionary containing keys named as "errors_dataframe" and "warnings_dataframe"
                 respectively.
            Default Value: False
            Types: bool

        open_sessions:
            Optional Argument.
            Specifies the number of Teradata data transfer sessions to be opened for fastload operation.
            Note : If "open_sessions" argument is not provided, the default value is the smaller of 8 or the
                   number of AMPs available.
                   For additional information about number of Teradata data-transfer
                   sessions opened during fastload, please refer to:
                   https://pypi.org/project/teradatasql/#FastLoad
            Default Value: None
            Types: int

        err_tbl_1_suffix:
            Optional Argument.
            Specifies the suffix for error table 1 created by fastload job.
            Default Value: "_ERR_1"
            Types: String

        err_tbl_2_suffix:
            Optional Argument.
            Specifies the suffix for error table 2 created by fastload job.
            Default Value: "_ERR_2"
            Types: String

        err_tbl_name:
            Optional Argument.
            Specifies the name for error table. This argument takes precedence
            over "save_errors" and saves error information in single table,
            rather than ERR_1 and ERR_2 error tables.
            Default value: "td_fl_<table_name>_err_<unique_id>" where table_name
                           is name of target/staging table and unique_id is logon
                           sequence number of fastload job.
            Types: String

        warn_tbl_name:
            Optional Argument.
            Specifies the name for warning table.
            Default value: "td_fl_<table_name>_warn_<unique_id>" where table_name
                           is name of target/staging table and unique_id is logon
                           sequence number of fastload job.
            Types: String

        err_staging_db:
            Optional Argument.
            Specifies the name of the database to be used for creating staging
            table and error/warning tables.
            Note:
                Current session user must have CREATE, DROP and INSERT table
                permissions on err_staging_db database.
            Types: String

    RETURNS:
        A dict containing the following attributes:
            1. errors_dataframe: It is a Pandas DataFrame containing error messages
               thrown by fastload. DataFrame is empty if there are no errors or
               "save_errors" is set to True.
            2. warnings_dataframe: It is a Pandas DataFrame containing warning messages 
               thrown by fastload. DataFrame is empty if there are no warnings.
            3. errors_table: Fully qualified name of the table containing errors. It is
               an empty string (''), if argument "save_errors" is set to False.
            4. warnings_table: Fully qualified name of the table containing warnings. It is
               an empty string (''), if argument "save_errors" is set to False.
            5. ERR_1_table: Fully qualified name of the ERR 1 table created by fastload
               job. It is an empty string (''), if argument "save_errors" is set to False.
            6. ERR_2_table: Fully qualified name of the ERR 2 table created by fastload
               job. It is an empty string (''), if argument "save_errors" is set to False.

    RAISES:
        TeradataMlException

    EXAMPLES:
        Saving a Pandas DataFrame using Fastload:
        >>> from teradataml.dataframe.fastload import fastload
        >>> from teradatasqlalchemy.types import *

        >>> df = {'emp_name': ['A1', 'A2', 'A3', 'A4'],
                  'emp_sage': [100, 200, 300, 400],
                  'emp_id': [133, 144, 155, 177],
                  'marks': [99.99, 97.32, 94.67, 91.00]
                  }

        >>> pandas_df = pd.DataFrame(df)

        # Example 1: Default execution.
        >>> fastload(df = pandas_df, table_name = 'my_table')

        # Example 2: Save a Pandas DataFrame with primary_index.
        >>> pandas_df = pandas_df.set_index(['emp_id'])
        >>> fastload(df = pandas_df, table_name = 'my_table_1', primary_index='emp_id')

        # Example 3: Save a Pandas DataFrame using fastload() with index and primary_index.
        >>> fastload(df = pandas_df, table_name = 'my_table_2', index=True,
                     primary_index='index_label')

        # Example 4: Save a Pandas DataFrame using types, appending to the table if it already exists.
        >>> fastload(df = pandas_df, table_name = 'my_table_3', schema_name = 'alice',
                     index = True, index_label = 'my_index_label',
                     primary_index = ['emp_id'], if_exists = 'append',
                     types = {'emp_name': VARCHAR, 'emp_sage':INTEGER,
                    'emp_id': BIGINT, 'marks': DECIMAL})

        # Example 5: Save a Pandas DataFrame using levels in index of type MultiIndex.
        >>> pandas_df = pandas_df.set_index(['emp_id', 'emp_name'])
        >>> fastload(df = pandas_df, table_name = 'my_table_4', schema_name = 'alice',
                     index = True, index_label = ['index1', 'index2'],
                     primary_index = ['index1'], if_exists = 'replace')

        # Example 6: Save a Pandas DataFrame by opening specified number of teradata data transfer sessions.
        >>> fastload(df = pandas_df, table_name = 'my_table_5', open_sessions = 2)

        # Example 7: Save a Pandas Dataframe to a table in specified target database "schema_name".
        #            Save errors and warnings to database specified with "err_staging_db".
        #            Save errors to table named as "err_tbl_name" and warnings to "warn_tbl_name".
        #            Given that, user is connected to a database different from "schema_name"
        #            and "err_staging_db".

        # Create a pandas dataframe having one duplicate and one fualty row.
        >>>> data_dict = {"C_ID": [301, 301, 302, 303, 304, 305, 306, 307, 308],
                         "C_timestamp": ['2014-01-06 09:01:25', '2014-01-06 09:01:25',
                                         '2015-01-06 09:01:25.25.122200', '2017-01-06 09:01:25.11111',
                                         '2013-01-06 09:01:25', '2019-03-06 10:15:28',
                                         '2014-01-06 09:01:25.1098', '2014-03-06 10:01:02',
                                         '2014-03-06 10:01:20.0000']}
        >>> my_df = pd.DataFrame(data_dict)

        # Fastlaod data in non-default schema "target_db" and save erors and warnings in given tables.
        >>> fastload(df=my_df, table_name='fastload_with_err_warn_tbl_stag_db',
                    if_exists='replace', primary_index='C_ID', schema_name='target_db',
                    types={'C_ID': INTEGER, 'C_timestamp': TIMESTAMP(6)},
                    err_tbl_name='fld_errors', warn_tbl_name='fld_warnings',
                    err_staging_db='stage_db')
        Processed 9 rows in batch 1.
        {'errors_dataframe':    batch_no                                      error_message
        0         1   [Session 14527] [Teradata Database] [Error 26...,
        'warnings_dataframe':         batch_no                                      error_message
        0  batch_summary   [Session 14526] [Teradata SQL Driver] [Warnin...,
        'errors_table': 'stage_db.fld_errors',
        'warnings_table': 'stage_db.fld_warnings',
        'ERR_1_table': '',
        'ERR_2_table': ''}

        # Validate loaded data table.
        >>>  DataFrame(in_schema("target_db", "fastload_with_err_warn_tbl_stag_db"))
        C_ID	C_timestamp
        303	2017-01-06 09:01:25.111110
        306	2014-01-06 09:01:25.109800
        304	2013-01-06 09:01:25.000000
        307	2014-03-06 10:01:02.000000
        305	2019-03-06 10:15:28.000000
        301	2014-01-06 09:01:25.000000
        308	2014-03-06 10:01:20.000000

        # Validate error and warning tables.
        >>> DataFrame(in_schema("stage_db", "fld_errors"))
        batch_no      error_message
        1             [Session 14527] [Teradata Database] [Error 2673] FastLoad failed to insert 1 of 9 batched rows. Batched row 3 failed to insert because of Teradata Database error 2673 in "target_db"."fastload_with_err_warn_tbl_stag_db"."C_timestamp"

        >>> DataFrame(in_schema("stage_db", "fld_warnings"))
        batch_no        error_message
        batch_summary   [Session 14526] [Teradata SQL Driver] [Warning 518] Found 1 duplicate or faulty row(s) while ending FastLoad of database table "target_db"."fastload_with_err_warn_tbl_stag_db": expected a row count of 8, got a row count of 7

        # Example 8: Save a Pandas Dataframe to a table in specified target database "schema_name".
        #            Save errors in ERR_1 and ERR_2 tables having user defined suffixes provided
        #            in "err_tbl_1_suffix" and "err_tbl_2_suffix".
        #            Source Pandas dataframe is same as Example 7.

        >>> fastload(df=my_df, table_name = 'fastload_with_err_warn_tbl_stag_db',
                     schema_name = 'target_db', if_exists = 'append',
                     types={'C_ID': INTEGER, 'C_timestamp': TIMESTAMP(6)},
                     err_staging_db='stage_db', save_errors=True,
                     err_tbl_1_suffix="_user_err_1", err_tbl_2_suffix="_user_err_2")
        {'errors_dataframe': Empty DataFrame
         Columns: []
         Index: [],
         'warnings_dataframe':         batch_no                                      error_message
         0  batch_summary   [Session 14699] [Teradata SQL Driver] [Warnin...,
         'errors_table': '',
         'warnings_table': 'stage_db.td_fl_fastload_with_err_warn_tbl_stag_db_warn_1730',
         'ERR_1_table': 'stage_db.ml__fl_stag_1716272404181579_user_err_1',
         'ERR_2_table': 'stage_db.ml__fl_stag_1716272404181579_user_err_2'}

        # Validate ERR_1 and ERR_2 tables.
        >>> DataFrame(in_schema("stage_db", "ml__fl_stag_1716270574550744_user_err_1"))
        ErrorCode	ErrorFieldName	DataParcel
        2673	F_C_timestamp	b'12E...'

        >>> DataFrame(in_schema("stage_db", "ml__fl_stag_1716270574550744_user_err_2"))
        C_ID	C_timestamp

    """
    # Deriving global connection using get_connection()
    con = get_connection()
    try:
        if con is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE), 
                                      MessageCodes.CONNECTION_FAILURE)

        if isinstance(df, dataframe.DataFrame):
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, 
                                      'df', "Pandas DataFrame"), MessageCodes.UNSUPPORTED_DATATYPE)

        dt_obj = _DataTransferUtils(df=df, table_name=table_name, schema_name=schema_name, if_exists=if_exists,
                                    index=index, index_label=index_label, primary_index=primary_index,
                                    types=types, batch_size=batch_size,
                                    save_errors=save_errors, api_name='fastload',
                                    use_fastload=True, open_sessions=open_sessions,
                                    err_tbl_1_suffix=err_tbl_1_suffix, err_tbl_2_suffix=err_tbl_2_suffix,
                                    err_tbl_name=err_tbl_name, warn_tbl_name=warn_tbl_name,
                                    err_staging_db=err_staging_db)
        # Validate DataFrame & related flags; Proceed only when True
        dt_obj._validate()

        # We have commented out the PTI related code for now as fastload fails to 
        # load data into PTI tables. Same has been reported to gosql team. We'll 
        # un-comment this once the issue is fixed.
        # Check if the table to be created must be a Primary Time Index (PTI) table.
        # If a user specifies the timecode_column parameter, and attempt to create
        # a PTI will be made.
#        is_pti = False
#        if timecode_column is not None:
#            is_pti = True
#            if primary_index is not None:
#                warnings.warn(Messages.get_message(MessageCodes.IGNORE_ARGS_WARN,
#                                                   'primary_index',
#                                                   'timecode_column',
#                                                   'specified'))
#        else:
#            ignored = []
#            if timezero_date is not None: ignored.append('timezero_date')
#            if timebucket_duration is not None: ignored.append('timebucket_duration')
#            if sequence_column is not None: ignored.append('sequence_column')
#            if seq_max is not None: ignored.append('seq_max')
#            if columns_list is not None and (
#                    not isinstance(columns_list, list) or len(columns_list) > 0): ignored.append('columns_list')
#            if primary_time_index_name is not None: ignored.append('primary_time_index_name')
#            if len(ignored) > 0:
#                warnings.warn(Messages.get_message(MessageCodes.IGNORE_ARGS_WARN,
#                                                   ignored,
#                                                   'timecode_column',
#                                                   'missing'))
      
        # Check and calculate batch size for optimized performance for FastLoad
        if batch_size is None:
            batch_size = _get_batchsize(df)
        else:
            # Validate argument batch_size type
            _Validators._validate_function_arguments([["batch_size", batch_size,
                                                      False, (int)]])
            if batch_size < 100000:
                warnings.warn("The batch_size provided is less than 100000. "
                              "Teradata recommends using 100000 as minimum batch "
                              "size for improved performance.", stacklevel=2)

        # If the table created must be a PTI table, then validate additional parameters
        # Note that if the required parameters for PTI are valid, then other parameters, though being validated,
        # will be ignored - for example, primary_index
#        if is_pti:
#            _validate_pti_copy_parameters(df, timecode_column, timebucket_duration,
#                                          timezero_date, primary_time_index_name, columns_list,
#                                          sequence_column, seq_max, types, index, index_label)

        # Check if destination table exists
        table_exists = dt_obj._table_exists(con)

        # Raise an exception when the table not exists and if_exists='fail'
        dt_obj._check_table_exists(is_table_exists=table_exists)

        # Let's create the SQLAlchemy table object to recreate the table
        if not table_exists or if_exists.lower() == 'replace':
            dt_obj._create_or_replace_table(con, table_exists=table_exists)

            # Insert data to target table using fastload.
            fl_dict = _insert_from_pd_dataframe_with_fastload(dt_obj, table_name, batch_size)
            
        # Check column compatibility for insertion when table exists and if_exists = 'append'
        if table_exists and if_exists.lower() == 'append':
            # Create table object
            table = UtilFuncs._get_sqlalchemy_table(table_name,
                                                    schema_name=schema_name)

            cols = _extract_column_info(df, index=index, index_label=index_label)
            if table is not None:
                dt_obj._check_columns_compatibility(table_obj=table, cols=cols)

            stag_table_name = ''
            try:
                # Create staging table and use FastLoad to load data.
                # Then copy all the rows from staging table to target table using insert_into sql.
                # If err_staging_db is not provided, create staging table
                # object in default connected DB.
                if err_staging_db is None:
                    err_staging_db = _get_current_databasename()
                stag_table_name = UtilFuncs._generate_temp_table_name(databasename=err_staging_db,
                                                                      prefix="fl_stag",
                                                                      gc_on_quit=False,
                                                                      quote=False,
                                                                      table_type=TeradataConstants.TERADATA_TABLE)

                # Get the table name without schema name for further steps.
                stag_table_name = UtilFuncs._extract_table_name(stag_table_name)
                # Create staging table object.
                dt_obj._create_table(con, table_name=stag_table_name,
                                     schema_name=err_staging_db)

                # Insert data to staging table using fastload.
                fl_dict = _insert_from_pd_dataframe_with_fastload(dt_obj, stag_table_name, batch_size, err_staging_db)

                # Insert data from staging table to target table.
                df_utils._insert_all_from_table(table_name,
                                                stag_table_name,
                                                cols[0],
                                                schema_name,
                                                err_staging_db)
            except:
                raise
            finally:
                # Drop the staging table.
                if stag_table_name:
                    UtilFuncs._drop_table(dt_obj._get_fully_qualified_table_name(stag_table_name, err_staging_db))

    except (TeradataMlException, ValueError, TypeError):
        raise
    except Exception as err:
        raise TeradataMlException(Messages.get_message(MessageCodes.FASTLOAD_FAILS), 
                                  MessageCodes.FASTLOAD_FAILS) from err
    return fl_dict


def _insert_from_pd_dataframe_with_fastload(dt_obj, table_name, batch_size, to_schema_name=None):
    """
    This is an internal function used to sequentially extract column info from pandas DataFrame,
    iterate rows, and insert rows manually. Used for insertions to Tables with Pandas index.
    This uses DBAPI's escape functions for Fastload which is a batch insertion method.

    PARAMETERS:
        dt_obj:
            Object of _DataTransferUtils class.
            Types: object

        table_name:
            Name of the table.
            Types: String

        batch_size:
            Specifies the number of rows to be inserted in a batch.
            Types: Int

        to_schema_name:
            Optional Argument.
            Specifies name of the database schema where target table needs to be created.

    RETURNS:
        dict

    RAISES:
        Exception

    EXAMPLES:
        _insert_from_pd_dataframe_with_fastload(dt_obj, table_name, batch_size=100)
    """
    conn = get_connection().connection
    # Create a cursor from connection object
    cur = conn.cursor()

    error_tablename = ""
    warn_tablename = ""

    try:
#        if is_pti:
#            # This if for non-index columns.
#            col_names = _reorder_insert_list_for_pti(col_names, timecode_column, sequence_column)

        is_multi_index = isinstance(dt_obj.df.index, pd.MultiIndex)

        # The Fastload functionality is provided through several escape methods using
        # teradatasql; like: {fn teradata_try_fastload}, {fn teradata_get_errors}, etc.
        # - {fn teradata_nativesql}: This escape method is to specify to use native
        # SQL escape calls.
        # - {fn teradata_autocommit_off}: This escape method is to turn off auto-commit.
        # For FastLoad it is required that it should not execute any transaction
        # management SQL commands when auto-commit is on.
        # - {fn teradata_try_fastload}: This escape method tries to use FastLoad
        # for the INSERT statement, and automatically executes the INSERT as a regular
        # SQL statement when the INSERT is not compatible with FastLoad.
        # - {fn teradata_require_fastload}: This escape method requires FastLoad
        # for the INSERT statement, and fails with an error when the INSERT is not
        # compatible with FastLoad.
        # - {fn teradata_get_errors}: This escape method returns in one string all
        # data errors observed by FastLoad for the most recent batch. The data errors
        # are obtained from FastLoad error table 1, for problems such as constraint
        # violations, data type conversion errors, and unavailable AMP conditions.
        # - {fn teradata_get_warnings}: This escape method returns in one string all
        # warnings generated by FastLoad for the request. The warnings are obtained
        # from FastLoad error table 2, for problems such as duplicate rows.
        # - {fn teradata_logon_sequence_number}: This escape method returns the string
        # form of an integer representing the Logon Sequence Number(LSN) for the
        # FastLoad. Returns an empty string if the request is not a FastLoad.

        # Quoted, schema-qualified table name.
        table = dt_obj._get_fully_qualified_table_name(table_name, to_schema_name)

        # Form the INSERT query for fastload.
        ins = dt_obj._form_insert_query(table)

        #  Turn off autocommit before the Fastload insertion
        dt_obj._process_escape_functions(cur, escape_function= \
                                        DriverEscapeFunctions.AUTOCOMMIT_OFF)

        # Initialize dict template for saving error/warning information
        err_dict = {key: [] for key in ['batch_no', 'error_message']}
        warn_dict = {key: [] for key in ['batch_no', 'error_message']}

        batch_number = 1
        num_batches = int(dt_obj.df.shape[0]/batch_size)

        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()

        for i in range(0, dt_obj.df.shape[0], batch_size):
            # Add the remaining rows to last batch after second last batch
            if (batch_number == num_batches) :
                last_elem = dt_obj.df.shape[0]
            else:
                last_elem = i + batch_size

            pdf = dt_obj.df.iloc[i:last_elem]
            insert_list = []
            # Iterate rows of DataFrame per batch size to convert it to list of lists.
            for row_index, row in enumerate(pdf.itertuples(index=True)):
                insert_list2 = []
                for col_index, x in enumerate(pdf.columns):
                    insert_list2.append(row[col_index+1])
                if dt_obj.index is True:
                    insert_list2.extend(row[0]) if is_multi_index else insert_list2.append(row[0])
                insert_list.append(insert_list2)
            # Execute insert statement.
            cur.execute(ins, insert_list)

            # Get error and warning information from cursor.
            err, _ = dt_obj._process_fastexport_errors_warnings(ins)
            if len(err) != 0:
                err_dict['batch_no'].extend([batch_number] * len(err))
                err_dict['error_message'].extend(err)

            print("Processed {} rows in batch {}.".format(pdf.shape[0], batch_number))

            # If shape of DataFrame equal to last_elem of last batch.
            if last_elem == dt_obj.df.shape[0]:
                break

            batch_number += 1

        # Get logon sequence number to be used for error/warning table names
        logon_seq_number = dt_obj._process_escape_functions(cur, escape_function= \
                                                            DriverEscapeFunctions.LOGON_SEQ_NUM,
                                                            insert_query=ins)
        # Commit the rows
        conn.commit()

        # Get error and warning information, if any.
        # Errors/Warnings like duplicate rows are added here.
        _, warn = dt_obj._process_fastexport_errors_warnings(ins)
        if len(warn) != 0:
            warn_dict['batch_no'].extend(['batch_summary'] * len(warn))
            warn_dict['error_message'].extend(warn)

        # Get error and warning information for error and warning tables, persist
        # error and warning tables to Vantage if user has specified save_error as True
        # else show it as pandas dataframe on console.
        pd_err_df = dt_obj._get_pandas_df_from_errors_warnings(err_dict)
        pd_warn_df = dt_obj._get_pandas_df_from_errors_warnings(warn_dict)

        # Create persistent tables using pandas df if
        # save_errors=True or
        # tables names for errors or warning are provided by user.
        if dt_obj.save_errors or dt_obj.err_tbl_name:
            if not pd_err_df.empty:
                error_tablename = dt_obj._create_error_warnings_table(pd_err_df, "err", logon_seq_number[0][0],
                                                                      dt_obj.err_tbl_name)
        if dt_obj.save_errors or dt_obj.warn_tbl_name:
            if not pd_warn_df.empty:
                warn_tablename = dt_obj._create_error_warnings_table(pd_warn_df, "warn", logon_seq_number[0][0],
                                                                     dt_obj.warn_tbl_name)

        # Generate ERR_1 and ERR_2 table names if save_errors=True and
        # errors are not stored in user provided error table name.
        if dt_obj.save_errors and not dt_obj.err_tbl_name:
            err_1_table = "{}.{}{}".format(dt_obj.err_staging_db if dt_obj.err_staging_db else _get_current_databasename(),
                                           table_name,
                                           dt_obj.err_tbl_1_suffix if dt_obj.err_tbl_1_suffix else "_ERR_1")
            err_2_table = "{}.{}{}".format(dt_obj.err_staging_db if dt_obj.err_staging_db else _get_current_databasename(),
                                           table_name,
                                           dt_obj.err_tbl_2_suffix if dt_obj.err_tbl_2_suffix else "_ERR_2")

        else:
            err_1_table = ""
            err_2_table = ""

    except Exception:
        conn.rollback()
        raise
    finally:
        # Turn on autocommit.
        dt_obj._process_escape_functions(cur, escape_function=DriverEscapeFunctions.AUTOCOMMIT_ON)
        cur.close()

    return {"errors_dataframe": pd_err_df, "warnings_dataframe": pd_warn_df,
            "errors_table": error_tablename, "warnings_table": warn_tablename,
            "ERR_1_table": err_1_table, "ERR_2_table": err_2_table}


def _get_batchsize(df):
    """
    This internal function calculates batch size which should be more than 100000 
    for better fastload performance.

    PARAMETERS:
        df:
            The Pandas DataFrame object for which the batch size has to be calculated.
            Types: pandas.DataFrame

    RETURNS:
        Batch size i.e. number of rows to be inserted in a batch.

    RAISES:
        N/A

    EXAMPLES:
        _get_batchsize(df)
    """
    return df.shape[0] if df.shape[0] <= 100000 else round(df.shape[0]/int(df.shape[0]/100000))


def _create_table_for_fastload(df, con, table_name, schema_name=None, primary_index=None, 
                               is_pti=False, primary_time_index_name=None, timecode_column=None,
                               timezero_date=None, timebucket_duration=None, sequence_column=None,
                               seq_max=None, columns_list=[], types=None, index=False,
                               index_label=None):
    """
    PARAMETERS:
        df:
            Specifies the Pandas DataFrame object to be saved.
            Types: pandas.DataFrame
                
        con:
            A SQLAlchemy connectable (engine/connection) object
            Types: Teradata connection object

        table_name:
            Specifies the name of the table to be created in Vantage.
            Types: String

        schema_name:
            Specifies the name of the database schema in Teradata Vantage to write to.
            Types: String

        index:
            Specifies whether to save Pandas DataFrame index as a column or not.
            Types: Boolean (True or False)
            
        index_label: 
            Specifies the column label(s) for Pandas DataFrame index column(s).
            Types: String or list of strings
            
        primary_index:
            Specifies which column(s) to use as primary index while creating Teradata 
            table in Vantage. When None, No Primary Index Teradata tables are created.
            Types: String or list of strings

        types: 
            Specifies required data-types for requested columns to be saved in Vantage.
            Types: Python dictionary ({column_name1: type_value1, ... column_nameN: type_valueN})
                   
    RETURNS:
        Table object

    RAISES:
        TeradataMlException, sqlalchemy.OperationalError

    EXAMPLES:
        _create_table_for_fastload(df, con, table_name, schema_name, primary_index, 
                                   is_pti, primary_time_index_name, timecode_column, 
                                   timezero_date, timebucket_duration, sequence_column,
                                   seq_max, columns_list, types, index, index_label)
    """
    if is_pti:
        table = _create_pti_table_object(df=df, con=con, table_name=table_name,
                                         schema_name=schema_name, temporary=False,
                                         primary_time_index_name=primary_time_index_name,
                                         timecode_column=timecode_column, timezero_date=timezero_date,
                                         timebucket_duration=timebucket_duration,
                                         sequence_column=sequence_column, seq_max=seq_max,
                                         columns_list=columns_list, set_table=False,
                                         types=types, index=index, index_label=index_label)

        UtilFuncs._create_table_using_table_object(table)

