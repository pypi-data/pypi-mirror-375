#!/usr/bin/python
# ##################################################################
#
# Copyright 2018 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# ##################################################################

import re
import datetime
import warnings
import pandas as pd
import pandas.api.types as pt

from sqlalchemy import MetaData, Table, Column
from sqlalchemy.exc import OperationalError as sqlachemyOperationalError
from teradataml.dataframe.sql import ColumnExpression
from teradatasqlalchemy import (INTEGER, BIGINT, BYTEINT, FLOAT)
from teradatasqlalchemy import (TIMESTAMP, DATE)
from teradatasqlalchemy import (VARCHAR)
from teradatasqlalchemy import (PERIOD_DATE,PERIOD_TIMESTAMP)
from teradatasqlalchemy.dialect import TDCreateTablePost as post
from teradataml.common.aed_utils import AedUtils
from teradataml.context.context import *
from teradataml.dataframe import dataframe as tdmldf
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.dbutils.dbutils import _rename_table
from teradataml.common.utils import UtilFuncs
from teradataml.options.configure import configure
from teradataml.common.constants import CopyToConstants, PTITableConstants, TeradataTypes
from teradatasql import OperationalError
from teradataml.common.wrapper_utils import AnalyticsWrapperUtils
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators
from teradataml.telemetry_utils.queryband import collect_queryband
from teradatasqlalchemy.dialect import dialect as td_dialect

from teradataml.utils.dtypes import _TupleOf

@collect_queryband(queryband="CpToSql")
def copy_to_sql(df, table_name,
                schema_name=None, if_exists='append',
                index=False, index_label=None,
                primary_index=None,
                temporary=False, types = None,
                primary_time_index_name = None,
                timecode_column=None,
                timebucket_duration = None,
                timezero_date = None,
                columns_list=None,
                sequence_column=None,
                seq_max=None,
                set_table=False,
                chunksize=CopyToConstants.DBAPI_BATCHSIZE.value,
                match_column_order=True,
                partition_by=None,
                partition_by_case=None,
                partition_by_range=None,
                sub_partition=None,
                **kwargs):
    """
    Writes records stored in a Pandas DataFrame or a teradataml DataFrame to Teradata Vantage.

    PARAMETERS:

        df:
            Required Argument. 
            Specifies the Pandas or teradataml DataFrame object to be saved.
            Types: pandas.DataFrame or teradataml.dataframe.dataframe.DataFrame

        table_name:
            Required Argument.
            Specifies the name of the table to be created in Vantage.
            Types : String

        schema_name:
            Optional Argument. 
            Specifies the name of the SQL schema in Teradata Vantage to write to.
            Types: String
            Default: None (Uses default database schema).

            Note: schema_name will be ignored when temporary=True.

        if_exists:
            Optional Argument.
            Specifies the action to take when table already exists in Vantage.
            Types: String
            Possible values: {'fail', 'replace', 'append'}
                - fail: If table exists, do nothing.
                - replace: If table exists, drop it, recreate it, and insert data.
                - append: If table exists, insert data. Create if does not exist.
            Default : append

            Note: Replacing a table with the contents of a teradataml DataFrame based on
                  the same underlying table is not supported.

        index:
            Optional Argument.
            Specifies whether to save Pandas DataFrame index as a column or not.
            Types : Boolean (True or False)
            Default : False
            
            Note: Only use as True when attempting to save Pandas DataFrames (and not with teradataml DataFrames).

        index_label: 
            Optional Argument.
            Specifies the column label(s) for Pandas DataFrame index column(s).
            Types : String or list of strings
            Default : None
            
            Note: If index_label is not specified (defaulted to None or is empty) and `index` is True, then
                  the 'names' property of the DataFrames index is used as the label(s),
                  and if that too is None or empty, then:
                  1) a default label 'index_label' or 'level_0' (when 'index_label' is already taken) is used
                     when index is standard.
                  2) default labels 'level_0', 'level_1', etc. are used when index is multi-level index.

                  Only use as True when attempting to save Pandas DataFrames (and not on teradataml DataFrames).

        primary_index:
            Optional Argument.
            Specifies which column(s) to use as primary index while creating Teradata table(s) in Vantage.
            When None, No Primary Index Teradata tables are created.
            Types : String or list of strings
            Default : None
            Example:
                primary_index = 'my_primary_index'
                primary_index = ['my_primary_index1', 'my_primary_index2', 'my_primary_index3']

        temporary:
            Optional Argument.
            Specifies whether to creates Vantage tables as permanent or volatile.
            Types : Boolean (True or False)
            Default : False
            
            Note: When True:
                  1. volatile Tables are created, and
                  2. schema_name is ignored.
                  When False, permanent tables are created.
            
        types 
            Optional Argument.
            Specifies required data types for requested columns to be saved in Teradata Vantage.
            Types: Python dictionary ({column_name1: type_value1, ... column_nameN: type_valueN})
            Default: None
            
            Note:
                1. This argument accepts a dictionary of columns names and their required teradatasqlalchemy types
                   as key-value pairs, allowing to specify a subset of the columns of a specific type.
                   i)  When the input is a Pandas DataFrame:
                       - When only a subset of all columns are provided, the column types for the rest are assigned
                         appropriately.
                       - When types argument is not provided, the column types are assigned
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
                   ii) When the input is a teradataml DataFrame:
                       - When only a subset of all columns are provided, the column types for the rest are retained.
                       - When types argument is not provided, the column types are retained.
                2. This argument does not have any effect when the table specified using table_name and schema_name
                   exists and if_exists = 'append'.

        primary_time_index_name:
            Optional Argument.
            Specifies a name for the Primary Time Index (PTI) when the table
            to be created must be a PTI table.
            Type: String

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.

        timecode_column:
            Optional argument.
            Required when the DataFrame must be saved as a PTI table.
            Specifies the column in the DataFrame that reflects the form
            of the timestamp data in the time series.
            This column will be the TD_TIMECODE column in the table created.
            It should be of SQL type TIMESTAMP(n), TIMESTAMP(n) WITH TIMEZONE, or DATE,
            corresponding to Python types datetime.datetime or datetime.date, or Pandas dtype datetime64[ns].
            Type: String

            Note: When you specify this parameter, an attempt to create a PTI table
                  will be made. This argument is not required when the table to be created
                  is not a PTI table. If this argument is specified, primary_index will be ignored.

        timezero_date:
            Optional Argument.
            Used when the DataFrame must be saved as a PTI table.
            Specifies the earliest time series data that the PTI table will accept;
            a date that precedes the earliest date in the time series data.
            Value specified must be of the following format: DATE 'YYYY-MM-DD'
            Default Value: DATE '1970-01-01'.
            Type: String

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.

        timebucket_duration:
            Optional Argument.
            Required if columns_list is not specified or is None.
            Used when the DataFrame must be saved as a PTI table.
            Specifies a duration that serves to break up the time continuum in
            the time series data into discrete groups or buckets.
            Specified using the formal form time_unit(n), where n is a positive
            integer, and time_unit can be any of the following:
            CAL_YEARS, CAL_MONTHS, CAL_DAYS, WEEKS, DAYS, HOURS, MINUTES,
            SECONDS, MILLISECONDS, or MICROSECONDS.
            Type:  String

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.

        columns_list:
            Optional Argument.
            Used when the DataFrame must be saved as a PTI table.
            Required if timebucket_duration is not specified.
            A list of one or more PTI table column names.
            Type: String or list of Strings

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.

        sequence_column:
            Optional Argument.
            Used when the DataFrame must be saved as a PTI table.
            Specifies the column of type Integer containing the unique identifier for
            time series data readings when they are not unique in time.
            * When specified, implies SEQUENCED, meaning more than one reading from the same
              sensor may have the same timestamp.
              This column will be the TD_SEQNO column in the table created.
            * When not specified, implies NONSEQUENCED, meaning there is only one sensor reading
              per timestamp.
              This is the default.
            Type: str

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.

        seq_max:
            Optional Argument.
            Used when the DataFrame must be saved as a PTI table.
            Specifies the maximum number of sensor data rows that can have the
            same timestamp. Can be used when 'sequenced' is True.
            Accepted range:  1 - 2147483647.
            Default Value: 20000.
            Type: int

            Note: This argument is not required or used when the table to be created
                  is not a PTI table. It will be ignored if specified without the timecode_column.

        set_table:
            Optional Argument.
            Specifies a flag to determine whether to create a SET or a MULTISET table.
            When True, a SET table is created.
            When False, a MULTISET table is created.
            Default Value: False
            Type: boolean

            Note: 1. Specifying set_table=True also requires specifying primary_index or timecode_column.
                  2. Creating SET table (set_table=True) may result in
                     a. an error if the source is a Pandas DataFrame having duplicate rows.
                     b. loss of duplicate rows if the source is a teradataml DataFrame.
                  3. This argument has no effect if the table already exists and if_exists='append'.

        chunksize:
            Optional Argument.
            Specifies the number of rows to be loaded in a batch.
            Note:
                This is argument is used only when argument "df" is pandas DataFrame.
            Default Value: 16383
            Types: int

        match_column_order:
            Optional Argument.
            Specifies whether the order of the columns in existing table matches the order of
            the columns in the "df" or not. When set to False, the dataframe to be loaded can
            have any order and number of columns.
            Default Value: True
            Types: bool

        partition_by:
            Optional Argument.
            Specifies the columns on which partition should be created while creating the table.
            Note:
                1. "partition_by", "partition_by_case" and "partition_by_range" are mutually exclusive.
                2. "primary_index" should be specified when "partition_by" is used.
                3. Not applicable for PTI tables.
            Types: str or ColumnExpression

        partition_by_case:
            Optional Argument.
            Specifies different cases to partition the index while creating table.
            Note:
                1. "partition_by", "partition_by_case" and "partition_by_range" are mutually exclusive.
                2. "primary_index" should be specified when "partition_by_case" is used.
                3. Not applicable for PTI tables.
            Types: str or ColumnExpression or tuple of ColumnExpression, str

        partition_by_range:
            Optional Argument.
            Specifies the range of values on which partition should be created while creating a table.
            Note:
                1. "partition_by", "partition_by_case" and "partition_by_range" are mutually exclusive.
                2. "primary_index" should be specified when "partition_by_range" is used.
                3. Not applicable for PTI tables.
            types: str or ColumnExpression

        sub_partition:
            Optional Argument.
            Specifies the details to subpartition the main partition according to the value provided while creating the table.
            Note:
                1. "sub_partition" is applicable only when "partition_by_range" is specified.
                2. Not applicable for PTI tables.
            Types: int or Teradata Interval datatypes

        **kwargs:
            Optional keyword arguments.

            valid_time_columns:
                Optional Argument.
                Specifies the name(s) of the valid time columns to be referred in "df".
                When "valid_time_columns" is specified, then function considers
                these columns as valid time dimension columns and creates a
                valid time dimension temporal table if table does not exist.
                Notes:
                    * If a string is provided, the column must be of PERIOD type.
                Types: tuple of strings or str
            
            derived_column:
                Optional Argument.
                Specifies the name of the derived column to be kept in the temporal table.
                Notes:
                    * Argument is ignored if "valid_time_columns" are not specified.
                    * Argument is considered only if copy_to_sql() is creating a table.
                    * If "valid_time_columns" is specified and "derived_column" is not specified,
                      then copy_to_sql() automatically creates a derived column by adding "_" between
                      the columns mentioned in "valid_time_columns". For example,
                      if "valid_time_columns" is ('col1', 'col2') and "derived_column"
                      is not specified, then copy_to_sql() creates table with
                      derived column name as 'col1_col2'.
                Types: str

    RETURNS:
        None

    RAISES:
        TeradataMlException

    EXAMPLES:
        1. Saving a Pandas DataFrame:

            >>> from teradataml.dataframe.copy_to import copy_to_sql
            >>> from teradatasqlalchemy.types import *

            >>> df = {'emp_name': ['A1', 'A2', 'A3', 'A4'],
            ...       'emp_sage': [100, 200, 300, 400],
            ...       'emp_id': [133, 144, 155, 177],
            ...       'marks': [99.99, 97.32, 94.67, 91.00]
            ...    }

            >>> pandas_df = pd.DataFrame(df)

            a) Save a Pandas DataFrame using a dataframe & table name only:
            >>> copy_to_sql(df=pandas_df, table_name='my_table')

            b) Saving as a SET table
            >>> copy_to_sql(df=pandas_df, table_name='my_set_table', index=True,
                            primary_index='index_label', set_table=True)

            c) Save a Pandas DataFrame by specifying additional parameters:
            >>> copy_to_sql(df=pandas_df, table_name='my_table_2', schema_name='alice',
            ...             index=True, index_label='my_index_label', temporary=False,
            ...             primary_index=['emp_id'], if_exists='append',
            ...             types={'emp_name': VARCHAR, 'emp_sage':INTEGER,
            ...                    'emp_id': BIGINT, 'marks': DECIMAL})

            d) Saving with additional parameters as a SET table
            >>> copy_to_sql(df=pandas_df, table_name='my_table_3', schema_name='alice',
            ...             index=True, index_label='my_index_label', temporary=False,
            ...             primary_index=['emp_id'], if_exists='append',
            ...             types={'emp_name': VARCHAR, 'emp_sage':INTEGER,
            ...                    'emp_id': BIGINT, 'marks': DECIMAL},
            ...             set_table=True)

            e) Saving levels in index of type MultiIndex
            >>> pandas_df = pandas_df.set_index(['emp_id', 'emp_name'])
            >>> copy_to_sql(df=pandas_df, table_name='my_table_4', schema_name='alice',
            ...             index=True, index_label=['index1', 'index2'], temporary=False,
            ...             primary_index=['index1'], if_exists = 'replace')
            
            f) Save a Pandas DataFrame with VECTOR datatype:
            >>> import pandas as pd
            >>> VECTOR_data = {
            ...        'id': [10, 11, 12, 13],
            ...        'array_col': ['1,1', '2,2', '3,3', '4,4']
            ...        }
            >>> df = pd.DataFrame(VECTOR_data)

            >>> from teradatasqlalchemy import VECTOR
            >>> copy_to_sql(df=df, table_name='my_vector_table', types={'array_col': VECTOR})

            g) Saving pandas DataFrame with partition_by:
            >>> copy_to_sql(df=pandas_df, table_name='my_table_5', if_exists='replace',
            ...             primary_index=['emp_id'],
            ...             partition_by='emp_id')

            h) Saving pandas DataFrame with partition_by_case:
            >>> copy_to_sql(df=pandas_df, table_name='my_table_6', if_exists='replace',
            ...             primary_index=['emp_id'],
            ...             partition_by_case='emp_id > 100, emp_id < 500')

            i) Saving pandas DataFrame with partition_by_range:
            >>> copy_to_sql(df=pandas_df, table_name='my_table_7', if_exists='replace',
            ...             primary_index=['emp_id'],
            ...             partition_by_range='emp_id BETWEEN 100 AND 500')


            j) Save a Pandas DataFrame with valid time columns of DATE type to a temporal table.
            >>> import pandas as pd
            >>> from teradataml.dataframe.copy_to import copy_to_sql
            >>> df = pd.DataFrame({
            ...     'id': [1, 2, 3],
            ...     'start_date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01']).date,
            ...     'end_date': pd.to_datetime(['2024-01-10', '2024-02-10', '2024-03-10']).date,
            ...     'description': ['a', 'b', 'c']
            ... })
            >>> copy_to_sql(
            ...     df=df,
            ...     table_name='temporal_table_pandas_date',
            ...     valid_time_columns=('start_date', 'end_date')
            ... )

            k) Save a Pandas DataFrame with valid time columns of TIMESTAMP type
            to a temporal table. Name the derived column as `valid_time`.
            >>> import pandas as pd
            >>> from teradataml.dataframe.copy_to import copy_to_sql
            >>> df = pd.DataFrame({
            ...     'id': [1, 2, 3],
            ...     'start_time': pd.to_datetime(['2024-01-01 10:00:00', '2024-02-01 11:00:00', '2024-03-01 12:00:00']),
            ...     'end_time': pd.to_datetime(['2024-01-01 12:00:00', '2024-02-01 13:00:00', '2024-03-01 14:00:00']),
            ...     'description: ['a', 'b', 'c']
            ... })
            >>> copy_to_sql(
            ...     df=df,
            ...     table_name='temporal_table_pandas_timestamp',
            ...     valid_time_columns=('start_time', 'end_time'),
            ...     derived_column='valid_time'
            ... )

            f) Save a teradataml DataFrame with valid time column of PERIOD type to a temporal table.
            >>> from teradataml.dataframe.dataframe import DataFrame
            >>> from teradataml.dataframe.copy_to import copy_to_sql
            >>> from teradataml.data.load_example_data import load_example_data
            >>> load_example_data("teradataml", "Employee_roles")
            >>> from teradatasqlalchemy.types import PERIOD_DATE
            >>> df = DataFrame('Employee_roles')
            >>> copy_to_sql(
            ...     df,
            ...     table_name = 'employee_roles_temporal',
            ...     valid_time_column='role_validity_period',
            ...     types={'role_validity_period':PERIOD_DATE}
            ... )

        2. Saving a teradataml DataFrame:

            >>> from teradataml.dataframe.dataframe import DataFrame
            >>> from teradataml.dataframe.copy_to import copy_to_sql
            >>> from teradatasqlalchemy.types import *
            >>> from teradataml.data.load_example_data import load_example_data
            
            >>> # Load the data to run the example.
            >>> load_example_data("glm", "admissions_train")
            
            >>> # Create teradataml DataFrame(s)
            >>> df = DataFrame('admissions_train')
            >>> df2 = df.select(['gpa', 'masters'])

            a) Save a teradataml DataFrame by using only a table name:
            >>> df2.to_sql('my_tdml_table')

            b) Save a teradataml DataFrame by using additional parameters:
            >>> df2.to_sql(table_name = 'my_tdml_table', if_exists='append',
                           primary_index = ['gpa'], temporary=False, schema_name='alice')

            c) Alternatively, save a teradataml DataFrame by using copy_to_sql:
            >>> copy_to_sql(df2, 'my_tdml_table_2')

            d) Save a teradataml DataFrame by using copy_to_sql with additional parameters:
            >>> copy_to_sql(df=df2, table_name='my_tdml_table_3', schema_name='alice',
            ...             temporary=False, primary_index=None, if_exists='append',
            ...             types={'masters': VARCHAR, 'gpa':INTEGER})

            e) Saving as a SET table
            >>> copy_to_sql(df = df2, table_name = 'my_tdml_set_table', schema_name='alice',
            ...             temporary=False, primary_index=['gpa'], if_exists='append',
            ...             types={'masters': VARCHAR, 'gpa':INTEGER}, set_table = True)

            f) Saving a teradataml DataFrame into a table by partitioning the table with column 'gpa':
            >>> copy_to_sql(df=df, table_name='my_tdml_table_4', if_exists='replace',
            ...             primary_index=['gpa'],
            ...             partition_by=df.gpa)

            g) Saving a teradataml DataFrame into a table with two partitions as below:
            >>> copy_to_sql(df=df, table_name='my_tdml_table_5', if_exists='replace',
            ...             primary_index=['id'],
            ...             partition_by_case=(df.id < 100, df.gpa < 5.0))

            h) Saving a teradataml DataFrame into a table by partitioning the table with different ranges:
            >>> copy_to_sql(df=df, table_name='my_tdml_table_6', if_exists='replace',
            ...             primary_index=['id'],
            ...             partition_by_range=df.id.between(1, 100))

            i) Saving a teradataml DataFrame into a table by partitioning the table with different ranges.
               Also sub-partitioning based on INTERVAL:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame('sales')
            >>> from teradatasqlalchemy import INTERVAL_DAY
            >>> copy_to_sql(df=df, table_name='my_tdml_table_7', if_exists='replace',
            ...             primary_index="Feb"
            ...             partition_by_range=df.datetime.between('2017-01-01', '2017-01-31'),
            ...             sub_partition=INTERVAL_DAY(1))

            j) Save a teradataml DataFrame with valid time columns of DATE type to a temporal table.
            pdf = pd.DataFrame({
            ...     'id': [1, 2, 3],
            ...     'start_date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01']).date,
            ...     'end_date': pd.to_datetime(['2024-01-10', '2024-02-10', '2024-03-10']).date,
            ...     'description': ['a', 'b', 'c']
            ... })
            >>> df_temporal = DataFrame(data = pdf)
            >>> copy_to_sql(df=df_temporal, table_name='temporal_table_tdml_date',
            ...             valid_time_columns=('start_date', 'end_date'))

            k) Save a teradataml DataFrame with valid time columns of TIMESTAMP type
            to a temporal table. Name the derived column as `validity_period`.
            >>>  df_temporal_ts = DataFrame(data = pd.DataFrame({
            ...     'id': [1, 2, 3],
            ...     'start_time': pd.to_datetime(['2024-01-01 10:00:00', '2024-02-01 11:00:00', '2024-03-01 12:00:00']),
            ...     'end_time': pd.to_datetime(['2024-01-01 12:00:00', '2024-02-01 13:00:00', '2024-03-01 14:00:00']),
            ...     'description': ['a', 'b', 'c']
            ... }))
            >>> copy_to_sql(df=df_temporal_ts, table_name='temporal_table_tdml_timestamp',
            ...             valid_time_columns=('start_time', 'end_time'), derived_column='validity_period')


        3. Saving a teradataml DataFrame as a PTI table:

            >>> from teradataml.dataframe.dataframe import DataFrame
            >>> from teradataml.dataframe.copy_to import copy_to_sql
            >>> from teradataml.data.load_example_data import load_example_data

            >>> load_example_data("sessionize", "sessionize_table")
            >>> df3 = DataFrame('sessionize_table')

            a) Using copy_to_sql
            >>> copy_to_sql(df3, "test_copyto_pti",
            ...             timecode_column='clicktime',
            ...             columns_list='event')

            b) Alternatively, using DataFrame.to_sql
            >>> df3.to_sql(table_name = "test_copyto_pti_1",
            ...            timecode_column='clicktime',
            ...            columns_list='event')

            c) Saving as a SET table
            >>> copy_to_sql(df3, "test_copyto_pti_2",
            ...             timecode_column='clicktime',
            ...             columns_list='event',
            ...             set_table=True)

    """
    # Accept valid_time_columns and derived_column from kwargs
    valid_time_columns = kwargs.get("valid_time_columns", None)
    derived_column = kwargs.get("derived_column", None)

    # Deriving global connection using get_connection().
    con = get_connection()

    try:
        if con is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE), MessageCodes.CONNECTION_FAILURE)

        # Check if the table to be created must be a Primary Time Index (PTI) table.
        # If a user specifies the timecode_column parameter, and attempt to create
        # a PTI will be made.
        is_pti = False
        if timecode_column is not None:
            is_pti = True
            if primary_index is not None:
                warnings.warn(Messages.get_message(MessageCodes.IGNORE_ARGS_WARN,
                                                   'primary_index',
                                                   'timecode_column',
                                                   'specified'), stacklevel=2)
        else:
            ignored = []
            if timezero_date is not None: ignored.append('timezero_date')
            if timebucket_duration is not None: ignored.append('timebucket_duration')
            if sequence_column is not None: ignored.append('sequence_column')
            if seq_max is not None: ignored.append('seq_max')
            if columns_list is not None and (
                    not isinstance(columns_list, list) or len(columns_list) > 0): ignored.append('columns_list')
            if primary_time_index_name is not None: ignored.append('primary_time_index_name')
            if len(ignored) > 0:
                warnings.warn(Messages.get_message(MessageCodes.IGNORE_ARGS_WARN,
                                                   ignored,
                                                   'timecode_column',
                                                   'missing'), stacklevel=2)

        # Unset schema_name when temporary is True since volatile tables are always in the user database
        if temporary is True:
            if schema_name is not None:
                warnings.warn(Messages.get_message(MessageCodes.IGNORE_ARGS_WARN,
                                                   'schema_name',
                                                   'temporary=True',
                                                   'specified'), stacklevel=2)
            schema_name = None

        # Validate DataFrame & related flags; Proceed only when True
        from teradataml.dataframe.data_transfer import _DataTransferUtils
        dt_obj = _DataTransferUtils(df=df, table_name=table_name, schema_name=schema_name,
                                    if_exists=if_exists, index=index, index_label=index_label,
                                    primary_index=primary_index, temporary=temporary,
                                    types=types, primary_time_index_name=primary_time_index_name,
                                    timecode_column=timecode_column,
                                    timebucket_duration=timebucket_duration,
                                    timezero_date=timezero_date, columns_list=columns_list,
                                    sequence_column=sequence_column, seq_max=seq_max,
                                    set_table=set_table, api_name='copy_to',
                                    chunksize=chunksize, match_column_order=match_column_order)

        dt_obj._validate()

        # Validate partition arguments
        _validate_partition_arguments(partition_by=partition_by,
                                      partition_by_case=partition_by_case,
                                      partition_by_range=partition_by_range,
                                      sub_partition=sub_partition)

        # If the table created must be a PTI table, then validate additional parameters
        # Note that if the required parameters for PTI are valid, then other parameters, though being validated,
        # will be ignored - for example, primary_index
        if is_pti:
            _validate_pti_copy_parameters(df, timecode_column, timebucket_duration,
                                          timezero_date, primary_time_index_name, columns_list,
                                          sequence_column, seq_max, types, index, index_label)

        # A table cannot be a SET table and have NO PRIMARY INDEX
        if set_table and primary_index is None and timecode_column is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.SET_TABLE_NO_PI),
                                      MessageCodes.SET_TABLE_NO_PI)

        # Check whether valid time columns are passed to consider it as temporal table.
        is_temporal = False
        if valid_time_columns is not None:
            _validate_valid_time_columns(df, valid_time_columns, derived_column,types)
            is_temporal = True


        # Check if destination table exists
        table_exists = dt_obj._table_exists(con)

        # Raise an exception when the table exists and if_exists = 'fail'
        dt_obj._check_table_exists(is_table_exists=table_exists)

        # Is the input DataFrame a Pandas DataFrame?
        is_pandas_df = isinstance(df, pd.DataFrame)

        # Let's also execute the node and set the table_name when df is teradataml DataFrame
        if not is_pandas_df and df._table_name is None:
            df._table_name = df_utils._execute_node_return_db_object_name(df._nodeid, df._metaexpr)

        # Check table name conflict is present.
        is_conflict = _check_table_name_conflict(df, table_name) if isinstance(df, tdmldf.DataFrame) and \
                                                                    if_exists.lower() == 'replace' else False

        # Create a temporary table name, When table name conflict is present.
        if is_conflict:
            # Store actual destination table name for later use.
            dest_table_name = table_name
            table_name = UtilFuncs._generate_temp_table_name(prefix=table_name,
                                                             table_type=TeradataConstants.TERADATA_TABLE,
                                                             quote=False)

            # If configure.temp_object_type="VT", _generate_temp_table_name() retruns the 
            # table name in fully qualified format. Because of this , test cases started 
            # failing with Blank name in quotation mark. Hence, extracted only the table name.  
            table_name = UtilFuncs._extract_table_name(table_name)

        partition_exp, partition_func = _build_partition_expression(partition_by=partition_by,
                                                                    partition_by_case=partition_by_case,
                                                                    partition_by_range=partition_by_range,
                                                                    sub_partition=sub_partition)

        # Let's create the SQLAlchemy table object to recreate the table
        if not table_exists or if_exists.lower() == 'replace':
            if is_temporal:
                _create_temporal_table(df, table_name, con, primary_index,
                                       schema_name, valid_time_columns, derived_column,
                                       types, None if not is_pandas_df else index,
                                       None if not is_pandas_df else index_label)
            else:
                if is_pti:
                    table = _create_pti_table_object(df, con, table_name, schema_name, temporary,
                                                     primary_time_index_name, timecode_column, timezero_date,
                                                     timebucket_duration, sequence_column, seq_max,
                                                     columns_list, set_table, types,
                                                     None if not is_pandas_df else index,
                                                     None if not is_pandas_df else index_label)
                else:
                    table = _create_table_object(df, table_name, con, primary_index, temporary, schema_name, set_table,
                                                 types, None if not is_pandas_df else index,
                                                 None if not is_pandas_df else index_label,
                                                 partition_expression=partition_exp,
                                                 partition_function=partition_func
                                                 )

                if table is not None:
                    # If the table need to be replaced and there is no table name conflict,
                    # let's drop the existing table first
                    if table_exists and not is_conflict:
                        tbl_name = dt_obj._get_fully_qualified_table_name()
                        UtilFuncs._drop_table(tbl_name)
                    try:
                        table.create(bind=get_context())
                    except sqlachemyOperationalError as err:
                        raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_OBJECT_CREATION_FAILED) +
                                                '\n' + str(err),
                                                MessageCodes.TABLE_OBJECT_CREATION_FAILED)
                else:
                    raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_OBJECT_CREATION_FAILED),
                                            MessageCodes.TABLE_OBJECT_CREATION_FAILED)

        # Check column compatibility for insertion when table exists and if_exists = 'append'
        if table_exists and if_exists.lower() == 'append':
            UtilFuncs._get_warnings('set_table', set_table, 'if_exists', 'append')

            table = UtilFuncs._get_sqlalchemy_table(table_name,
                                                    schema_name=schema_name)

            if table is not None:
                # ELE-2284
                # We are not considering types for 'append' mode as it is a simple insert and no casting is applied
                if is_pandas_df:
                    cols = _extract_column_info(df, index=index, index_label=index_label)
                else:
                    cols, _ = df_utils._get_column_names_and_types_from_metaexpr(df._metaexpr)
                if match_column_order:
                    cols_compatible = _check_columns_insertion_compatible(table.c, cols, is_pandas_df,
                                                                      is_pti, timecode_column, sequence_column, derived_column)

                    if not cols_compatible:
                        raise TeradataMlException(Messages.get_message(MessageCodes.INSERTION_INCOMPATIBLE),
                                              MessageCodes.INSERTION_INCOMPATIBLE)

        # df is a Pandas DataFrame object
        if isinstance(df, pd.DataFrame):
            if not table_exists or if_exists.lower() == 'replace':
                try:
                    # Support for saving Pandas index/Volatile is by manually inserting rows (batch) for now
                    if index or is_pti:
                        _insert_from_dataframe(df, con, schema_name, table_name, index,
                                               chunksize, is_pti, timecode_column,
                                               sequence_column, match_column_order)

                    # When index isn't saved & for non-PTI tables, to_sql insertion used (batch)
                    else:
                        # Empty queryband buffer before SQL call.
                        UtilFuncs._set_queryband()
                        df.to_sql(table_name, get_context(), if_exists='append', index=False, index_label=None,
                                  chunksize=chunksize, schema=schema_name)

                except sqlachemyOperationalError as err:
                    if "Duplicate row error" in str(err):
                        raise TeradataMlException(Messages.get_message(MessageCodes.SET_TABLE_DUPICATE_ROW,
                                                                       table_name),
                                                  MessageCodes.SET_TABLE_DUPICATE_ROW)
                    else:
                        raise

            elif table_exists and if_exists.lower() == 'append':
                _insert_from_dataframe(df, con, schema_name, table_name, index,
                                       chunksize, is_pti, timecode_column,
                                       sequence_column, match_column_order)

        # df is a teradataml DataFrame object (to_sql wrapper used)
        elif isinstance(df, tdmldf.DataFrame):
            df_column_list = [col.name for col in df._metaexpr.c]

            if is_pti:
                # Reorder the column list to reposition the timecode and sequence columns
                df_column_list = _reorder_insert_list_for_pti(df_column_list, timecode_column, sequence_column)

            source_tbl_name = UtilFuncs._extract_table_name(df._table_name)
            from_schema_name = UtilFuncs._extract_db_name(df._table_name)

            df_utils._insert_all_from_table(table_name, source_tbl_name, df_column_list,
                                            to_schema_name=schema_name,
                                            from_schema_name=from_schema_name,
                                            temporary=temporary)

        # While table name conflict is present, Delete the source table after creation of temporary table.
        # Rename the temporary table to destination table name. 
        if is_conflict and if_exists.lower() == 'replace':
            tbl_name = dt_obj._get_fully_qualified_table_name()
            UtilFuncs._drop_table(tbl_name)
            _rename_table(table_name, dest_table_name)


    except (TeradataMlException, ValueError, TypeError):
        raise
    except Exception as err:
        raise TeradataMlException(Messages.get_message(MessageCodes.COPY_TO_SQL_FAIL) + str(err),
                                  MessageCodes.COPY_TO_SQL_FAIL) from err


def _check_table_name_conflict(df, table_name):
    """ 
    Check whether destination "table_name" matches with the teradataml dataframe parent nodes.
    This function traverse the DAG graph from child node to root node and checks for table name conflict.
    
    PARAMETERS:
        df:
            Required Argument. 
            Specifies the teradataml DataFrame object to be checked.
            Types: teradataml.dataframe.dataframe.DataFrame
            
        table_name:
            Required Argument.
            Specifies the name of the table to be created in Vantage.
            Types : String

    RETURNS:
        A boolean value representing the presence of conflict. 

    RAISES:
        None

    EXAMPLES:
        >>> df = DataFrame("sales")
        >>> table_name = "destination_table"
        >>> _check_table_name_conflict(df, table_name)
    """
    aed_obj = AedUtils()
    # Check if length of parent node count greater that 0.
    if aed_obj._aed_get_parent_node_count(df._nodeid) > 0:
        # Let's check "table_name" matches with any of the parent nodes table name.
        # Get current table node id.
        node_id = df._nodeid
        while node_id:

            # Get the parent node id using current table node id.
            parent_node_id = aed_obj._aed_get_parent_nodeids(node_id)

            if parent_node_id:
                # Check "table_name" matches with the parent "table_name".
                # If table name matches, then return 'True'.
                # Otherwise, Traverse the graph from current node to the top most root node.
                if table_name in aed_obj._aed_get_source_tablename(parent_node_id[0]):
                    return True
                else:
                    node_id = parent_node_id[0]
            else:
                # When parent_node_id is empty return 'False'.
                return False
    return False


def _get_sqlalchemy_table_from_tdmldf(df, meta):
    """
    This is an internal function used to generate an SQLAlchemy Table
    object for the underlying table/view of a DataFrame.

    PARAMETERS:
        df:
            The teradataml DataFrame to generate the SQLAlchemy.Table object for.

        meta:
            The SQLAlchemy.Metadata object.

    RETURNS:
        SQLAlchemy.Table

    RAISES:
        None

    EXAMPLES:
        >>> con = get_connection()
        >>> df = DataFrame('admissions_train')
        >>> meta = sqlalchemy.MetaData()
        >>> table = __get_sqlalchemy_table_from_tdmldf(df, meta)

    """
    con = get_connection()
    db_schema = UtilFuncs._extract_db_name(df._table_name)
    db_table_name = UtilFuncs._extract_table_name(df._table_name)

    return Table(db_table_name, meta, schema=db_schema, autoload_with=get_context())


def _get_index_labels(df, index_label):
    """
    Internal function to construct a list of labels for the indices to be saved from the Pandas DataFrames
    based on user input and information from the DataFrame.

    PARAMETERS:
        df:
            The Pandas input DataFrame.

        index_label:
            The user provided label(s) for the indices.

    RAISES:
        None

    RETURNS:
        A list of Strings corresponding the to labels for the indices to add as columns.

    EXAMPLES:
        _get_index_labels(df, index_label)
    """
    default_index_label = 'index_label'
    default_level_prefix = 'level_'
    level_cnt = 0

    is_multi_index = isinstance(df.index, pd.MultiIndex)
    ind_types = [level.dtype for level in df.index.levels] if is_multi_index else [df.index.dtype]

    ind_names = []
    if index_label:
        ind_names = [index_label] if isinstance(index_label, str) else index_label
    else:
        for name in df.index.names:
            if name not in ('', None):
                ind_names.append(name)
            else:
                if is_multi_index:
                    ind_names.append(default_level_prefix + str(level_cnt))
                    level_cnt = level_cnt + 1
                else:
                    df_columns = _get_pd_df_column_names(df)
                    label = default_level_prefix + str(level_cnt) if default_index_label in df_columns else default_index_label
                    ind_names.append(label)

    return ind_names, ind_types

def _validate_partition_arguments(partition_by=None,
                                  partition_by_case=None,
                                  partition_by_range=None,
                                  sub_partition=None):
    """
    Internal function to validate the partition_by arguments.

    PARAMETERS:
        partition_by:
            Optional argument.
            Specifies the columns on which PARTITION BY should be created.
            Types: str or ColumnExpression

        partition_by_case:
            Optional argument.
            Specifies different cases to partition the index.
            Types: str or ColumnExpression or tuple of ColumnExpression, str

        partition_by_range:
            Optional argument.
            Specifies the range of values of Date columns on which partition to be created.
            Types: str or ColumnExpression

        sub_partition:
            Optional argument.
            Specifies the details to subpartition the main partition according to the value provided.
            Types: int or Teradata Interval datatypes


    RETURNS:
        None

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>> _validate_partition_arguments(partition_by='col1')
        >>> _validate_partition_arguments(partition_by_case=(df.col1 < 100, df.col1 < 1000))
    """
    # Validate partition_by argument
    arg_matrix = []
    arg_matrix.append(['partition_by', partition_by, True, (str, ColumnExpression), True])
    arg_matrix.append(['partition_by_case', partition_by_case, True, (ColumnExpression, str, _TupleOf((str, ColumnExpression))), True])
    arg_matrix.append(['partition_by_range', partition_by_range, True, (ColumnExpression, str), True])
    arg_matrix.append(['sub_partition', sub_partition, True, (int, TeradataTypes.TD_RANGE_N_CLAUSE_TYPES.value), True])

    # Validate argument types
    _Validators._validate_function_arguments(arg_matrix)

    # Validate mutually exclusive arguments
    _Validators._validate_mutually_exclusive_argument_groups({"partition_by":partition_by},
                                                             {"partition_by_case":partition_by_case},
                                                             {"partition_by_range":partition_by_range})

def _build_partition_expression(partition_by=None,
                                partition_by_case=None,
                                partition_by_range=None,
                                sub_partition=None):
    """
    DESCRIPTION:
        Internal function to build the partitioning expression for the table.

    PARAMETERS:
        partition_by:
            Optional argument.
            Specifies the columns on which PARTITION BY should be created.
            Types: str or ColumnExpression

        partition_by_case:
            Optional argument.
            Specifies different cases to partition the index.
            Types: str or ColumnExpression or tuple of ColumnExpression, str

        partition_by_range:
            Optional argument.
            Specifies the range of values of Date columns on which partition to be created.
            Types: str or ColumnExpression

        sub_partition:
            Optional argument.
            Specifies the details to subpartition the main partition according to the value provided.
            Types: int or Teradata Interval datatypes

    RAISES:
        None

    RETURNS:
        strings containing the partitioning expression and partition function.

    EXAMPLES:
        >>> _build_partition_expression(partition_by='col1')
        >>> _build_partition_expression(partition_by_case=(df.col1 < 100, df.col1 < 1000))

    """
    partition_exp = None
    partition_fn = None
    # Check if partition_by expression is a ColumnExpression,
    # if so, compile it to a string
    if partition_by:
        partition_exp = partition_by.compile() if isinstance(partition_by, ColumnExpression) \
                        else partition_by

    # Check if partition_by_case is a ColumnExpression or string,
    # if string, join to partition_by expression
    # if ColumnExpression, compile it to a string and join to partition_by expression
    # if tuple, compile each expression to a string and join to partition_by expression
    if partition_by_case:
        partition_fn = "CASE_N"
        partition_by_case = [partition_by_case] if isinstance(partition_by_case, (str, ColumnExpression)) \
                            else partition_by_case
        partition_exp = "{}, NO CASE, UNKNOWN".format(
                        ", ".join(str(exp.compile()) if isinstance(exp, ColumnExpression) else str(exp)
                        for exp in partition_by_case))

    # Check if partition_by_range is a ColumnExpression or string,
    # if so, compile it to a string
    if partition_by_range:
        partition_fn = "RANGE_N"
        sub_partition_clause = ""
        if isinstance(partition_by_range, ColumnExpression):
            partition_by_range = partition_by_range.compile()

        # Check if sub_partition provided,
        # if so, complie the EACH clause for RANGE_N
        # If sub_partition is an int, the convert to string and add to the clause.
        # If sub_partition is a TeradataTypes.TD_RANGE_N_CLAUSE_TYPES,
        # convert to string and extract the precision and add to the clause.
        if sub_partition:
            sub_partition_clause = (
                                    f" EACH {str(sub_partition)}"
                                    if isinstance(sub_partition, int)
                                    else f" EACH INTERVAL '{sub_partition.precision}' {str(sub_partition).split(maxsplit=1)[1]}")

        partition_exp = "{0}{1}".format(partition_by_range, sub_partition_clause)
    # Return partition_by expression and partition function
    return partition_exp, partition_fn


def _validate_pti_copy_parameters(df, timecode_column, timebucket_duration,
                                  timezero_date, primary_time_index_name, columns_list,
                                  sequence_column, seq_max, types, index, index_label):
    """
    This is an internal function used to validate the PTI part of copy request.
    Dataframe, connection & related parameters are checked.
    Saving to Vantage is proceeded to only when validation returns True.

    PARAMETERS:
        df:
            The DataFrame (Pandas or teradataml) object to be saved.

        timecode_column:
            The column in the DataFrame that reflects the form of the timestamp
            data in the time series.
            Type: String

        timebucket_duration:
            A duration that serves to break up the time continuum in
            the time series data into discrete groups or buckets.
            Type: String

        timezero_date:
            Specifies the earliest time series data that the PTI table will accept.
            Type: String

        primary_time_index_name:
            A name for the Primary Time Index (PTI).
            Type: String

        columns_list:
            A list of one or more PTI table column names.
            Type: String or list of Strings

        sequence_column:
            Specifies a column of type Integer with sequences implying that the
            time series data readings are not unique.
            If not specified, the time series data are assumed to be unique in time.
            Type: String

        seq_max:
            Specifies the maximum number of sensor data rows that can have the
            same timestamp. Can be used when 'sequenced' is True.
            Accepted range:  1 - 2147483647.
            Type: int

        types:
            Dictionary specifying column-name to teradatasqlalchemy type-mapping.

        index:
            Flag specifying whether to write Pandas DataFrame index as a column or not.
            Type: bool

        index_label:
            Column label for index column(s).
            Type: String

    RETURNS:
        True, when all parameters are valid.

    RAISES:
        TeradataMlException, when parameter validation fails.

    EXAMPLES:
        _validate_pti_copy_parameters(df = my_df, timecode_column = 'ts', timbucket_duration = 'HOURS(2)')
    """
    if isinstance(df, pd.DataFrame):
        df_columns = _get_pd_df_column_names(df)
    else:
        df_columns = [col.name for col in df._metaexpr.c]

    awu = AnalyticsWrapperUtils()
    awu_matrix = []

    # The arguments added to awu_martix are:
    # arg_name, arg, is_optional, acceptable types
    # The value for is_optional is set to False when the argument
    # a) is a required argument
    # b) is not allowed to be None, even if it is optional
    awu_matrix.append(['timecode_column', timecode_column, False, (str)])
    awu_matrix.append(['columns_list', columns_list, True, (str, list)])
    awu_matrix.append(['timezero_date', timezero_date, True, (str)])
    awu_matrix.append(['timebucket_duration', timebucket_duration, True, (str)])
    awu_matrix.append(['primary_time_index_name', primary_time_index_name, True, (str)])
    awu_matrix.append(['sequence_column', sequence_column, True, (str)])
    awu_matrix.append(['seq_max', seq_max, True, (int)])

    # Validate types
    awu._validate_argument_types(awu_matrix)

    # Validate arg emtpy
    awu._validate_input_columns_not_empty(timecode_column, 'timecode_column')
    awu._validate_input_columns_not_empty(columns_list, 'columns_list')
    awu._validate_input_columns_not_empty(timezero_date, 'timezero_date')
    awu._validate_input_columns_not_empty(timebucket_duration, 'timebucket_duration')
    awu._validate_input_columns_not_empty(sequence_column, 'sequence_column')

    # Validate all the required arguments and optional arguments when not none
    # First the timecode_column
    _validate_column_in_list_of_columns('df', df_columns, timecode_column, 'timecode_column')
    # Check the type of timecode_column
    _validate_column_type(df, timecode_column, 'timecode_column', PTITableConstants.VALID_TIMECODE_DATATYPES.value,
                          types, index, index_label)

    # timezero date
    _validate_timezero_date(timezero_date)

    # timebucket duration
    _Validators._validate_timebucket_duration(timebucket_duration)

    # Validate sequence_column
    if sequence_column is not None:
        _validate_column_in_list_of_columns('df', df_columns, sequence_column, 'sequence_column')
        # Check the type of sequence_column
        _validate_column_type(df, sequence_column, 'sequence_column',
                              PTITableConstants.VALID_SEQUENCE_COL_DATATYPES.value, types, index, index_label)

    # Validate seq_max
    if seq_max is not None and (seq_max < 1 or seq_max > 2147483647):
        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(seq_max, 'seq_max', '1 < integer < 2147483647'),
                                  MessageCodes.INVALID_ARG_VALUE)

    # Validate cols_list
    _validate_columns_list('df', df_columns, columns_list)
    if isinstance(columns_list, str):
        columns_list = [columns_list]

    # Either one or both of timebucket_duration and columns_list must be specified
    if timebucket_duration is None and (columns_list is None or len(columns_list) == 0):
        raise TeradataMlException(
            Messages.get_message(MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT, 'timebucket_duration', 'columns_list'),
            MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)


def _validate_columns_list(df, df_columns, columns_list):
    """
    Internal function to validate columns list specified when creating a
    Primary Time Index (PTI) table.

    PARAMETERS:
        df:
            Name of the DataFrame to which the column being validated
            does or should belong.

        df_columns:
            List of columns in the DataFrame.

        columns_list:
            The column or list of columns.
            Type: String or list of Strings

    RETURNS:
        True if the column or list of columns is valid.

    RAISES:
        Raise TeradataMlException on validation failure.
    """
    if columns_list is None:
        return True

    # Validate DF has columns
    if isinstance(columns_list, str):
        columns_list = [columns_list]

    for col in columns_list:
        _validate_column_in_list_of_columns(df, df_columns, col, 'columns_list')

    return True


def _validate_column_in_list_of_columns(df, df_columns, col, col_arg):
    """
    Internal function to validate the arguments used to specify
    a column name in DataFrame.

    PARAMETERS:
        df:
            Name of the DataFrame to which the column being validated
            does or should belong.

        df_column_list:
            List of columns in the DataFrame.

        col:
            Column to be validated.

        col_arg:
            Name of argument used to specify the column name.

    RETURNS:
         True, if column name is a valid.

    RAISES:
        TeradataMlException if invalid column name.
    """
    if col not in df_columns:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND).format(col,
                                                                                     col_arg,
                                                                                     df,
                                                                                     'DataFrame'),
            MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND)

    return True


def _validate_column_type(df, col, col_arg, expected_types, types = None, index = False, index_label = None):
    """
    Internal function to validate the type of an input DataFrame column against
    a list of expected types.

    PARAMETERS
        df:
            Input DataFrame (Pandas or teradataml) which has the column to be tested
            for type.

        col:
            The column in the input DataFrame to be tested for type.

        col_arg:
            The name of the argument used to pass the column name.

        expected_types:
            Specifies a list of teradatasqlachemy datatypes that the column is
            expected to be of type.

        types:
            Dictionary specifying column-name to teradatasqlalchemy type-mapping.

    RETURNS:
        True, when the columns is of an expected type.

    RAISES:
        TeradataMlException, when the columns is not one of the expected types.

    EXAMPLES:
        _validate_column_type(df, timecode_column, 'timecode_column', PTITableConstants.VALID_TIMECODE_DATATYPES, types)
    """
    # Check if sequence_column is being translated to a valid_type
    if types is not None and col in types:
        if not any(isinstance(types[col], expected_type) for expected_type in expected_types):
            raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_COLUMN_TYPE).
                                      format(col_arg, types[col], ' or '.join(expected_type.__visit_name__
                                                                              for expected_type in expected_types)),
                                      MessageCodes.INVALID_COLUMN_TYPE)
    # Else we need to copy without any casting
    elif isinstance(df, pd.DataFrame):
        t = _get_sqlalchemy_mapping_types(str(df.dtypes[col]))
        if t not in expected_types:
            raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_COLUMN_TYPE).
                                      format(col_arg, t, ' or '.join(expected_type.__visit_name__
                                                                     for expected_type in expected_types)),
                                      MessageCodes.INVALID_COLUMN_TYPE)
    elif not any(isinstance(df[col].type, t) for t in expected_types):
        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_COLUMN_TYPE).
                                  format(col_arg, df[col].type, ' or '.join(expected_type.__visit_name__
                                                                            for expected_type in expected_types)),
                                  MessageCodes.INVALID_COLUMN_TYPE)

    return True


def _create_table_object(df, table_name, con, primary_index, temporary, schema_name, set_table, types, index=None,
                         index_label=None, partition_expression=None, partition_function=None):
    """
    This is an internal function used to construct a SQLAlchemy Table Object.
    This function checks appropriate flags and supports creation of Teradata
    specific Table constructs such as Volatile/Primary Index tables.


    PARAMETERS:
        df:
            The teradataml or Pandas DataFrame object to be saved.

        table_name:
            Name of SQL table.

        con:
            A SQLAlchemy connectable (engine/connection) object

        primary_index:
            Creates Teradata Table(s) with Primary index column if specified.

        temporary:
            Flag specifying whether SQL table to be created is Volatile or not.

        schema_name:
            Specifies the name of the SQL schema in the database to write to.

        set_table:
            A flag specifying whether to create a SET table or a MULTISET table.
            When True, an attempt to create a SET table is made.
            When False, an attempt to create a MULTISET table is made.

        partition_expression:
            Specifies the partitioning expression to be used for partition by clause.

        partition_function:
            Specifies the partitioning function to be used  with partition by clause.

        types:
            Specifies a python dictionary with column-name(key) to column-type(value) mapping to create DataFrames.

        index:
            Flag specifying whether to write Pandas DataFrame index as a column(s) or not.

        index_label:
            Column label(s) for index column(s).

    RETURNS:
        SQLAlchemy Table

    RAISES:
        N/A

    EXAMPLES:
        _create_table_object(df = my_df, table_name = 'test_table', con = tdconnection, primary_index = None,
                             temporary = True, schema_name = schema, set_table=False, types = types, index = True, index_label = None)
        _create_table_object(df = csv_filepath, table_name = 'test_table', con = tdconnection, primary_index = None,
                             temporary = True, schema_name = schema, set_table=False, types = types, index = True, index_label = None)
    """
    # Dictionary to append special flags, can be extended to add Fallback, Journalling, Log etc.
    post_params = {}
    prefix = []
    pti = post(opts=post_params)

    if temporary is True:
        pti = pti.on_commit(option='preserve')
        prefix.append('VOLATILE')

    if not set_table:
        prefix.append('multiset')
    else:
        prefix.append('set')

    meta = MetaData()
    meta.bind = con

    if isinstance(df, pd.DataFrame):
        col_names, col_types = _extract_column_info(df, types, index, index_label)
    elif isinstance(df, str):
        col_names, col_types = _extract_column_info(df, types)
    else:
        col_names, col_types = df_utils._get_column_names_and_types_from_metaexpr(df._metaexpr)
        if types is not None:
            # When user-type provided use, or default when partial types provided.
            col_types = [types.get(col_name, col_type) for col_name, col_type in zip(col_names, col_types)]

    if primary_index is not None:
        if isinstance(primary_index, list):
            pti = pti.primary_index(unique=False, cols=primary_index)
        elif isinstance(primary_index, str):
            pti = pti.primary_index(unique=False, cols=[primary_index])
    else:
        pti = pti.no_primary_index()

    # Partitioning expression and function
    if partition_expression:
        pti = pti.partition_by(partition_expression=partition_expression,
                               partition_fn=partition_function)

    # Create default Table construct with parameter dictionary
    table = Table(table_name, meta,
                  *(Column(col_name, col_type)
                    for col_name, col_type in
                    zip(col_names, col_types)),
                  teradatasql_post_create=pti,
                  prefixes=prefix,
                  schema=schema_name
                  )

    return table


def _create_pti_table_object(df, con, table_name, schema_name, temporary, primary_time_index_name,
                             timecode_column, timezero_date, timebucket_duration,
                             sequence_column, seq_max, columns_list, set_table, types, index=None, index_label=None):
    """
    This is an internal function used to construct a SQLAlchemy Table Object.
    This function checks appropriate flags and supports creation of Teradata
    specific Table constructs such as Volatile and Primary Time Index tables.

    PARAMETERS:
        df:
            The teradataml or Pandas DataFrame object to be saved.

        con:
            A SQLAlchemy connectable (engine/connection) object

        table_name:
            Name of SQL table.

        schema_name:
            Specifies the name of the SQL schema in the database to write to.

        temporary:
            Flag specifying whether SQL table to be created is Volatile or not.

        primary_time_index_name:
            A name for the Primary Time Index (PTI).

        timecode_column:
            The column in the DataFrame that reflects the form of the timestamp
            data in the time series.

        timezero_date:
            Specifies the earliest time series data that the PTI table will accept.

        timebucket_duration:
            A duration that serves to break up the time continuum in
            the time series data into discrete groups or buckets.

        sequence_column:
            Specifies a column with sequences implying that time series data
            readings are not unique. If not specified, the time series data are
            assumed to be unique.

        seq_max:
            Specifies the maximum number of sensor data rows that can have the
            same timestamp. Can be used when 'sequenced' is True.

        columns_list:
            A list of one or more PTI table column names.

        set_table:
            A flag specifying whether to create a SET table or a MULTISET table.
            When True, an attempt to create a SET table is made.
            When False, an attempt to create a MULTISET table is made.

        types:
            Specifies a python dictionary with column-name(key) to column-type(value) mapping to create DataFrames.

        index:
            Flag specifying whether to write Pandas DataFrame index as a column or not.

        index_label:
            Column label for index column(s).

    RETURNS:
        SQLAlchemy Table

    RAISES:
        N/A

    EXAMPLES:
        _create_pti_table_object(df = my_df, table_name = 'test_table', con = tdconnection,
                         timecode_column = 'ts', columns_list = ['user_id', 'location'])

    """
    meta = MetaData()

    if isinstance(df, pd.DataFrame):
        col_names, col_types = _extract_column_info(df, types, index, index_label)
        timecode_datatype = col_types[col_names.index(timecode_column)]()
    else:
        col_names, col_types = df_utils._get_column_names_and_types_from_metaexpr(df._metaexpr)
        if types is not None:
            # When user-type provided use, or default when partial types provided
            col_types = [types.get(col_name, col_type) for col_name, col_type in zip(col_names, col_types)]
        timecode_datatype = df[timecode_column].type

    # Remove timecode and sequence column from col_name and col_types
    # since the required columns will be created automatically
    if timecode_column in col_names:
        ind = col_names.index(timecode_column)
        col_names.pop(ind)
        col_types.pop(ind)

    if sequence_column is not None and sequence_column in col_names:
        ind = col_names.index(sequence_column)
        col_names.pop(ind)
        col_types.pop(ind)

    # Dictionary to append special flags, can be extended to add Fallback, Journalling, Log etc.
    post_params = {}
    prefix = []
    pti = post(opts=post_params)

    # Create Table object with appropriate Primary Time Index/Prefix for volatile
    if temporary:
        pti = pti.on_commit(option='preserve')
        prefix.append('VOLATILE')

    if not set_table:
        prefix.append('multiset')
    else:
        prefix.append('set')

    pti = pti.primary_time_index(timecode_datatype,
                                 name=primary_time_index_name,
                                 timezero_date=timezero_date,
                                 timebucket_duration=timebucket_duration,
                                 sequenced=True if sequence_column is not None else False,
                                 seq_max=seq_max,
                                 cols=columns_list)

    table = Table(table_name, meta,
                  *(Column(col_name, col_type)
                    for col_name, col_type in
                    zip(col_names, col_types)),
                  teradatasql_post_create=pti,
                  prefixes=prefix,
                  schema=schema_name
                  )

    return table

def _create_temporal_table(df, table_name, con, primary_index, schema_name,
                           valid_time_columns, derived_column, types, index=None, index_label=None):
    """
    This is an internal function used to construct a CREATE TABLE statement for a Teradata temporal table.
    Supports creation of tables with a PERIOD FOR derived column using the specified valid time columns.

    PARAMETERS:
        df:
            Required Arugment.
            The teradataml or Pandas DataFrame object to be saved.
            Types: pandas.DataFrame or teradataml.dataframe.dataframe.DataFrame

        table_name:
            Required Argument.
            Name of SQL table.
            Types: String

        con:
            Optional Argument.
            A SQLAlchemy connectable (engine/connection) object.
            Types: SQLAlchemy Engine or Connection

        primary_index:
            Optional Argument.
            Creates Teradata Table(s) with Primary index column if specified.
            Types: String or list of Strings

        schema_name:
            Optional Argument.
            Specifies the name of the SQL schema in the database to write to.
            Types: String

        valid_time_columns:
            Required Argument.
            Specifies a tuple of two column names representing the temporal validity period.
            Types: tuple of Strings or str

        derived_column:
            Optional Argument.
            Specifies the name of the derived PERIOD FOR column to be created.
            Types: String

        types:
            Optional Argument.
            Specifies a python dictionary with column-name(key) to column-type(value) mapping to create DataFrames.
            Types: dict

        index:
            Optional Argument.
            Flag specifying whether to write Pandas DataFrame index as a column(s) or not.
            Types: Boolean

        index_label:
            Optional Argument.
            Column label(s) for index column(s).
            Types: String or list of Strings

    RETURNS:
        None

    RAISES:
        TeradataMlException

    EXAMPLES:
        _create_temporal_table(
            df=my_df,
            table_name='temporal_table',
            con=td_connection,
            primary_index=['id'],
            schema_name='my_schema',
            valid_time_columns=('start_date', 'end_date'),
            derived_column='validity_period',
            types={'id': INTEGER, 'start_date': DATE, 'end_date': DATE},
            index=False,
            index_label=None
        )

    """

    # Extract column names and types
    if isinstance(df, pd.DataFrame):
        col_names, col_types = _extract_column_info(df, types, index, index_label)
    else:
        col_names, col_types = df_utils._get_column_names_and_types_from_metaexpr(df._metaexpr)
        if types is not None:
            col_types = [types.get(col_name, col_type) for col_name, col_type in zip(col_names, col_types)]

    columns_clause_ = []
    # Ensure all col_types are instances, not classes
    for i, col_type in enumerate(col_types):
        if isinstance(col_type, type):
            col_types[i] = col_type()
    # Use col_names and col_types to build the columns clause
    # Compile column types to string using the dialect of the current connection
    # Add NOT NULL to valid_time_columns
    for col_name, col_type in zip(col_names, col_types):
        col_def = '{} {}'.format(col_name, col_type.compile(dialect=td_dialect()))

        if  col_name in valid_time_columns:
            col_def += ' NOT NULL'
            if isinstance(col_type, (PERIOD_DATE, PERIOD_TIMESTAMP)):
                col_def += ' AS VALIDTIME'
        columns_clause_.append(col_def)

    period_for_clause = []
    if isinstance(valid_time_columns, tuple):
        if derived_column is None:
            derived_column = "_".join(valid_time_columns)
        period_for_clause = ['PERIOD FOR {}  ({}, {}) AS VALIDTIME'.format(
            derived_column, valid_time_columns[0], valid_time_columns[1])
        ]
    columns_clause = ",\n ".join(columns_clause_ + period_for_clause)

    # Prepare primary index clause.
    if primary_index:
        primary_index_clause = "PRIMARY INDEX ({})".format(
            ", ".join(UtilFuncs._as_list(primary_index)))
    else:
        primary_index_clause = ""

    # Prepare create table statement.
    table_name = UtilFuncs._get_qualified_table_name(schema_name, table_name) if\
        schema_name else table_name
    sql = """
    CREATE MULTISET TABLE {}
    (\n{}\n)\n{}
    """.format(table_name, columns_clause, primary_index_clause)
    try:
        execute_sql(sql)
    except Exception as err:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.TABLE_OBJECT_CREATION_FAILED) +
            '\n' + str(err),
            MessageCodes.TABLE_OBJECT_CREATION_FAILED
        )


def _rename_column(col_names, search_for, rename_to):
    """
    Internal function to rename a column in a list of columns of a Pandas DataFrame.

    PARAMETERS:
        col_names:
            Required Argument.
            The list of column names of the Pandas DataFrame.

        search_for:
            Required Argument.
            The column name that need to be changed/renamed.

        rename_to:
            Required Argument.
            The column name that the 'search_for' column needs to be replaced with.

    RETURNS:
        A list of renamed columns list.

    EXAMPLES:
        cols = _rename_column(cols, 'col_1', 'new_col_1')
    """
    ind = col_names.index(search_for)
    col_names.pop(ind)
    col_names.insert(ind, rename_to)

    return col_names


def _rename_to_pti_columns(col_names, timecode_column, sequence_column,
                           timecode_column_index=None, sequence_column_index=None):
    """
    Internal function to generate a list of renamed columns of a Pandas DataFrame to match that of the PTI table column names
    in Vantage, or revert any such changes made.

    PARAMETERS:
        col_names:
            The list of column names of the Pandas DataFrame.

        timecode_column:
            The column name that reflects the timecode column in the PTI table.

        sequence_column:
            The column name that reflects the sequence column in the PTI table.

        timecode_column_index:
            The index of the timecode column. When Specified, it indicates that a reverse renaming operation is to be
            performed.

        sequence_column_index:
            The index of the timecode column. When Specified, it indicates that a reverse renaming operation is to be
            performed.

    RETURNS:
        A list of renamed PTI related columns.

    EXAMPLES:
        cols = _rename_to_pti_columns(cols, timecode_column, sequence_column, t_index=None, s_index)
        cols = _rename_to_pti_columns(cols, timecode_column, sequence_column)
    """
    # Rename the timecode_column to what it is in Vantage
    if timecode_column_index is not None:
        col_names = _rename_column(col_names, PTITableConstants.TD_TIMECODE.value, timecode_column)
    else:
        col_names = _rename_column(col_names, timecode_column, PTITableConstants.TD_TIMECODE.value)

    # Rename the sequence_column to what it is in Vantage
    if sequence_column is not None:
        if sequence_column_index is not None:
            col_names = _rename_column(col_names, PTITableConstants.TD_SEQNO.value, sequence_column)
        else:
            col_names = _rename_column(col_names, sequence_column, PTITableConstants.TD_SEQNO.value)

    return col_names


def _reorder_insert_list_for_pti(df_column_list, timecode_column, sequence_column, df_col_type_list = None):
    """
    Internal function to reorder the list of columns used to construct the 'INSERT INTO'
    statement as required when the target table is a PTI table.

    PARAMETERS:
        df_column_list:
            A list of column names for the columns in the DataFrame.

        timecode_column:
            The timecode_columns which should be moved to the first position.

        sequence_column:
            The timecode_columns which should be moved to the first position.

        df_col_type_list:
            Optionally reorder the list containing the types of the columns to match the
            reordering the of df_column_list.

    RETURNS:
        A reordered list of columns names for the columns in the DataFrame.
        If the optional types list is also specified, then a tuple of the list reordered columns names
        and the list of the column types.

    EXAMPLE:
        new_colname_list = _reorder_insert_list_for_pti(df_column_list, timecode_column, sequence_column)
        new_colname_list, new_type_list = _reorder_insert_list_for_pti(df_column_list, timecode_column,
                                                                       sequence_column, df_col_type_list)
    """
    # Reposition timecode (to the first) and sequence column (to the second)
    # in df_column_list
    timecode_column_index = df_column_list.index(timecode_column)
    df_column_list.insert(0, df_column_list.pop(timecode_column_index))
    if df_col_type_list is not None:
        df_col_type_list.insert(0, df_col_type_list.pop(timecode_column_index))

    if sequence_column is not None:
        sequence_column_index = df_column_list.index(sequence_column)
        df_column_list.insert(1, df_column_list.pop(sequence_column_index))
        if df_col_type_list is not None:
            df_col_type_list.insert(0, df_col_type_list.pop(sequence_column_index))

    if df_col_type_list is not None:
        return df_column_list, df_col_type_list
    else:
        return df_column_list


def _check_columns_insertion_compatible(table1_col_object, table2_cols, is_pandas_df=False,
                                        is_pti=False, timecode_column=None, sequence_column=None, derived_column=None):
    """
    Internal function used to extract column information from two lists of SQLAlchemy ColumnExpression objects;
    and check if the number of columns and their names are matching to determine table insertion compatibility.

    PARAMETERS:
        table1_col_object:
            Specifies a list/collection of SQLAlchemy ColumnExpression Objects for first table.
        
        table2_cols:
            Specifies a list of column names for second table (teradataml DataFrame).
        
        is_pandas_df:
            Flag specifying whether the table objects to check are pandas DataFrames or not
            Default: False    
            Note: When this flag is True, table2_cols is passed as a tuple object of
            ([column_names], [column_types])

        is_pti:
            Boolean flag indicating if the target table is a PTI table.

        timecode_column:
            timecode_column required to order the select expression for the insert.
            It should be the first column in the select expression.

        sequence_column:
            sequence_column required to order the select expression for the insert.
            It should be the second column in the select expression.

        derived_column:
            Specifies a derived column that is part of the table schema but not
            part of insert.
            Types: String

    RETURNS:
        a) True, when insertion compatible (number of columns and their names match)
        b) False, otherwise

    RAISES:
        N/A

    EXAMPLES:
        _check_columns_insertion_compatible(table1.c, ['co1', 'col2'], False)
        _check_columns_insertion_compatible(table1.c, (['co1', 'col2'], [int, str]), True, True, 'ts', 'seq')
        _check_columns_insertion_compatible(table1.c, (['co1', 'col2'], [int, str]), True, True, 'ts', 'seq', 'derived_col')

    """
    table1_col_names, _ = UtilFuncs._extract_table_object_column_info(table1_col_object)
    table2_col_names = table2_cols[0] if is_pandas_df else table2_cols

    # Remove derived_column from table1_col_names if specified
    if derived_column is not None and derived_column in table1_col_names:
        table1_col_names.remove(derived_column)

    # Check for number of columns
    if len(table1_col_names) != len(table2_col_names):
        return False

    if is_pti is True:
        # Reposition timecode (to the first) and sequence column (to the second)
        # with their names as generated by the database, in col_name since that
        # is the default position of the columns.
        table2_col_names = _reorder_insert_list_for_pti(table2_col_names, timecode_column, sequence_column)
        table2_col_names = _rename_to_pti_columns(table2_col_names, timecode_column, sequence_column)

    # Check for the column names
    for i in range(len(table1_col_names)):
        if table1_col_names[i] != table2_col_names[i]:
            return False

    # Number of columns and their names in both List of ColumnExpressions match
    return True


def _extract_column_info(df, types = None, index = False, index_label = None):
    """
    This is an internal function used to extract column information for a DF,
    and map to user-specified teradatasqlalchemy types, if specified,
    for Table creation.

    PARAMETERS:
        df:
            The Pandas DataFrame object to be saved.

        types:
            A python dictionary with column names and required types as key-value pairs.

        index:
            Flag specifying whether to write Pandas DataFrame index as a column(s) or not.

        index_label:
            Column label(s) for index column(s).

    RETURNS:
        A tuple with the following elements:
        a) List of DataFrame Column names
        b) List of equivalent teradatasqlalchemy column types

    RAISES:
        None

    EXAMPLES:
        _extract_column_info(df = my_df)
        _extract_column_info(df = my_df, types = {'id_col': INTEGER})

    """
    if isinstance(df, str):
        return list(types.keys()), list(types.values())

    col_names = _get_pd_df_column_names(df)

    # If the datatype is not specified then check if the datatype is datetime64 and timezone is present then map it to
    # TIMESTAMP(timezone=True) else map it according to default value.
    col_types = [types.get(col_name) if types and col_name in types else
                 TIMESTAMP(timezone=True) if pt.is_datetime64_ns_dtype(df.dtypes.iloc[key])
                                             and (df[col_name].dt.tz is not None)
                 else _get_sqlalchemy_mapping_types(str(df.dtypes.iloc[key]))
                 for key, col_name in enumerate(list(df.columns))]

    ind_names = []
    ind_types = []
    if index:
        ind_names, ind_types = _get_index_labels(df, index_label)
        ind_types = [types.get(ind_name) if types and ind_name in types
                     else TIMESTAMP(timezone=True) if pt.is_datetime64_ns_dtype(df.dtypes.iloc[key])
                                                      and (df[ind_name].dt.tz is not None)
                     else _get_sqlalchemy_mapping_types(str(ind_types[key]))
                     for key, ind_name in enumerate(ind_names)]

    return col_names + ind_names, col_types + ind_types


def _insert_from_dataframe(df, con, schema_name, table_name, index, chunksize,
                           is_pti=False, timecode_column=None, sequence_column=None,
                           match_column_order=True):
    """
    This is an internal function used to sequentially extract column info from DF,
    iterate rows, and insert rows manually.
    Used for Insertions to Temporary Tables & Tables with Pandas index.

    This uses DBAPI's executeMany() which is a batch insertion method.

    PARAMETERS:
        df:
            The Pandas DataFrame object to be saved.

        con:
            A SQLAlchemy connectable (engine/connection) object

        schema_name:
            Name of the schema.

        table_name:
            Name of the table.

        index:
            Flag specifying whether to write Pandas DataFrame index as a column or not.

        chunksize:
            Specifies the number of rows to be loaded in a batch.
            Note:
                This is argument is used only when argument "df" is pandas DataFrame.

        is_pti:
            Boolean flag indicating if the table should be a PTI table.

        timecode_column:
            timecode_column required to order the select expression for the insert.
            It should be the first column in the select expression.

        sequence_column:
            sequence_column required to order the select expression for the insert.
            It should be the second column in the select expression.

        match_column_order:
            Specifies the order of the df to be loaded matches the order of the
            existing df or not.

    RETURNS:
        N/A

    RAISES:
        N/A

    EXAMPLES:
        _insert_from_dataframe(df = my_df, con = tdconnection, schema = None, table_name = 'test_table',
                               index = True, index_label = None)
    """
    col_names = _get_pd_df_column_names(df)

    # Quoted, schema-qualified table name
    table = '"{}"'.format(table_name)
    if schema_name is not None:
        table = '"{}".{}'.format(schema_name, table_name)

    try:

        if is_pti:
            # This if for non-index columns.
            col_names = _reorder_insert_list_for_pti(col_names, timecode_column, sequence_column)

        is_multi_index = isinstance(df.index, pd.MultiIndex)

        insert_list = []

        if not match_column_order:
            ins = "INSERT INTO {} {} VALUES {};".format(
                table,
                '(' + ', '.join(col_names) + ')',
                '(' + ', '.join(['?' for i in range(len(col_names) + len(df.index.names)
                                                    if index is True else len(col_names))]) + ')')
        else:
            ins = "INSERT INTO {} VALUES {};".format(
                table,
                '(' + ', '.join(['?' for i in range(len(col_names) + len(df.index.names)
                                                    if index is True else len(col_names))]) + ')')

        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()
        rowcount = 0
        # Iterate rows of DataFrame over new re-ordered columns
        for row_index, row in enumerate(df[col_names].itertuples(index=True)):
            ins_dict = ()
            for col_index, x in enumerate(col_names):
                ins_dict = ins_dict + (row[col_index+1],)

            if index is True:
                ins_dict = ins_dict + row[0] if is_multi_index else ins_dict + (row[0],)

            insert_list.append(ins_dict)
            rowcount = rowcount + 1

            # dbapi_batchsize corresponds to the max batch size for the DBAPI driver.
            # Insert the rows once the batch-size reaches the max allowed.
            if rowcount == chunksize:
                # Batch Insertion (using DBAPI's executeMany) used here to insert list of dictionaries
                cur = execute_sql(ins, insert_list)
                if cur is not None:
                    cur.close()
                rowcount = 0
                insert_list.clear()

        # Insert any remaining rows.
        if rowcount > 0:
            cur = execute_sql(ins, insert_list)
            if cur is not None:
                cur.close()

    except Exception:
        raise


def _get_pd_df_column_names(df):
    """
    Internal function to return the names of columns in a Pandas DataFrame.

    PARAMETERS
        df:
            The Pandas DataFrame to fetch the column names for.

    RETURNS:
         A list of Strings

    RAISES:
        None

    EXAMPLES:
        _get_pd_df_column_names(df = my_df)
    """
    return df.columns.tolist()


def _get_sqlalchemy_mapping(key):
    """
    This is an internal function used to returns a SQLAlchemy Type Mapping
    for a given Pandas DataFrame column Type.
    Used for Table Object creation internally based on DF column info.

    For an unknown key, String (Mapping to VARCHAR) is returned

    PARAMETERS:
        key : String representing Pandas type ('int64', 'object' etc.)

    RETURNS:
        SQLAlchemy Type Object(Integer, String, Float, DateTime etc.)

    RAISES:
        N/A

    EXAMPLES:
        _get_sqlalchemy_mapping(key = 'int64')
    """
    teradata_types_map = _get_all_sqlalchemy_mappings()

    if key in teradata_types_map.keys():
        return teradata_types_map.get(key)
    else:
        return VARCHAR(configure.default_varchar_size,charset='UNICODE')


def _get_all_sqlalchemy_mappings():
    """
    This is an internal function used to return a dictionary of all SQLAlchemy Type Mappings.
    It contains mappings from pandas data type to objects of SQLAlchemy Types

    PARAMETERS:

    RETURNS:
        dictionary { pandas_type : SQLAlchemy Type Object}

    RAISES:
        N/A

    EXAMPLES:
        _get_all_sqlalchemy_mappings()
    """
    teradata_types_map = {'int32':INTEGER(), 'int64':BIGINT(), "Int64": INTEGER(),
                          'object':VARCHAR(configure.default_varchar_size,charset='UNICODE'),
                          'O':VARCHAR(configure.default_varchar_size,charset='UNICODE'),
                          'float64':FLOAT(), 'float32':FLOAT(), 'bool':BYTEINT(),
                          'datetime64':TIMESTAMP(), 'datetime64[ns]':TIMESTAMP(),
                          'datetime64[ns, UTC]':TIMESTAMP(timezone=True),
                          'timedelta64[ns]':VARCHAR(configure.default_varchar_size,charset='UNICODE'),
                          'timedelta[ns]':VARCHAR(configure.default_varchar_size,charset='UNICODE')}

    return teradata_types_map


def _get_sqlalchemy_mapping_types(key):
    """
    This is an internal function used to return a SQLAlchemy Type Mapping
    for a given Pandas DataFrame column Type.
    Used for Table Object creation internally based on DF column info.

    For an unknown key, String (Mapping to VARCHAR) is returned

    PARAMETERS:
        key : String representing Pandas type ('int64', 'object' etc.)

    RETURNS:
        SQLAlchemy Type (Integer, String, Float, DateTime etc.)

    RAISES:
        N/A

    EXAMPLES:
        _get_sqlalchemy_mapping_types(key = 'int64')
    """
    teradata_types_map = _get_all_sqlalchemy_types_mapping()

    if key in teradata_types_map.keys():
        return teradata_types_map.get(key)
    else:
        return VARCHAR(configure.default_varchar_size,charset='UNICODE')


def _get_all_sqlalchemy_types_mapping():
    """
    This is an internal function used to return a dictionary of all SQLAlchemy Type Mappings.
    It contains mappings from pandas data type to SQLAlchemyTypes

    PARAMETERS:

    RETURNS:
        dictionary { pandas_type : SQLAlchemy Type}

    RAISES:
        N/A

    EXAMPLES:
        _get_all_sqlalchemy_types_mapping()
    """
    teradata_types_map = {'int32': INTEGER, 'int64': BIGINT,
                          'object': VARCHAR(configure.default_varchar_size, charset='UNICODE'),
                          'O': VARCHAR(configure.default_varchar_size, charset='UNICODE'),
                          'float64': FLOAT, 'float32': FLOAT, 'bool': BYTEINT,
                          'datetime64': TIMESTAMP, 'datetime64[ns]': TIMESTAMP,
                          'datetime64[ns, UTC]': TIMESTAMP(timezone=True),
                          'timedelta64[ns]': VARCHAR(configure.default_varchar_size, charset='UNICODE'),
                          'timedelta[ns]': VARCHAR(configure.default_varchar_size, charset='UNICODE')}

    return teradata_types_map


def _validate_timezero_date(timezero_date):
    """
    Internal function to validate timezero_date specified when creating a
    Primary Time Index (PTI) table.

    PARAMETERS:
        timezero_date:
            The timezero_date passed to primary_time_index().

    RETURNS:
        True if the value is valid.

    RAISES:
        ValueError when the value is invalid.

    EXAMPLE:
        _validate_timezero_date("DATE '2011-01-01'")
        _validate_timezero_date('2011-01-01') # Invalid
    """
    # Return True is it is not specified or is None since it is optional
    if timezero_date is None:
        return True

    pattern = re.compile(PTITableConstants.PATTERN_TIMEZERO_DATE.value)
    match = pattern.match(timezero_date)

    err_msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(timezero_date,
                                                                          'timezero_date',
                                                                          "str of format DATE 'YYYY-MM-DD'")

    try:
        datetime.datetime.strptime(match.group(1), '%Y-%m-%d')
    except (ValueError, AttributeError):
        raise TeradataMlException(err_msg,
                                  MessageCodes.INVALID_ARG_VALUE)

    # Looks like the value is valid
    return True

def _validate_valid_time_columns(df, valid_time_columns, derived_column=None, types=None):
    """
    Internal function to validate that the columns specified in valid_time_columns
    exist in the DataFrame, are of type DATE or TIMESTAMP, and are of the same type.
    Also checks that the derived_column, if specified, is not present in the DataFrame.

    PARAMETERS:
        df:
            Required Argument.
            Specifies the Pandas or teradataml DataFrame object to be validated.
            Types: pandas.DataFrame or teradataml.dataframe.dataframe.DataFrame

        valid_time_columns:
            Required Argument.
            Specifies a tuple of two column names representing the temporal validity period.
            Types: tuple of Strings

        derived_column:
            Optional Argument.
            Specifies the name of the derived column that should not be
            present in the DataFrame.
            Types: String

        types:
            Optional Argument.
            Specifies a python dictionary with column-name(key) to column-type(value)
            mapping to create DataFrames.
            Types: dict

    RETURNS:
        None

    RAISES:
        TeradataMlException

    EXAMPLES:
        _validate_valid_time_columns(
            df=my_df,
            valid_time_columns=('start_date', 'end_date'),
            derived_column='validity_period',
            types={'start_date': DATE, 'end_date': DATE}
        )
    """
    df_columns = _get_pd_df_column_names(df) if isinstance(df, pd.DataFrame) else df.columns
    df_dtypes = (
        {
            col: _get_sqlalchemy_mapping_types(str(df.dtypes[col]))
            for col in df.dtypes.keys()
        }
        if isinstance(df, pd.DataFrame)
        else df._td_column_names_and_sqlalchemy_types
    )
    # If types argument is provided, override the dtypes for those columns
    if types is not None:
        for col, typ in types.items():
            if col in df_columns:
                df_dtypes[col] = typ


    if derived_column is not None and derived_column in df_columns:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.TDMLDF_COLUMN_IN_ARG_FOUND).format(
                derived_column, 'derived_column', 'dataframe.', 'Provide value which is not part of DataFrame columns'
            ),
            MessageCodes.TDMLDF_COLUMN_IN_ARG_FOUND
        )
    # valid_time_columns can be a tuple of two column names or a single column name
    if isinstance(valid_time_columns, tuple):
        if len(valid_time_columns) != 2:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(
                    valid_time_columns, 'valid_time_columns', 'tuple of two column names'
                ),
                MessageCodes.INVALID_ARG_VALUE
            )
        # Check if both columns are present in the DataFrame
        for col in valid_time_columns:
            if col not in df_columns:
                raise TeradataMlException(
                    Messages.get_message(MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND).format(
                        col, 'valid_time_columns', 'df', 'DataFrame'
                    ),
                    MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND
                )

        col1_type = df_dtypes[valid_time_columns[0]]
        col2_type = df_dtypes[valid_time_columns[1]]

        # When types are specified, ensure they are DATE or TIMESTAMP objects or classes.
        if not (
            isinstance(col1_type, TIMESTAMP) or isinstance(col1_type, DATE) or
            col1_type is TIMESTAMP or col1_type is DATE
        ):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.INVALID_COLUMN_TYPE).format(
                    'valid_time_columns',
                    col1_type.__name__ if isinstance(col1_type, type)
                    else col1_type.__class__.__name__, 'DATE or TIMESTAMP'
                ),
                MessageCodes.INVALID_COLUMN_TYPE
            )
        # When types are specified, ensure they are DATE or TIMESTAMP objects or classes.
        if not (
            isinstance(col2_type, TIMESTAMP) or isinstance(col2_type, DATE) or
            col2_type is TIMESTAMP or col2_type is DATE
        ):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.INVALID_COLUMN_TYPE).format(
                    'valid_time_columns',
                    col2_type.__name__ if isinstance(col2_type, type)
                    else col2_type.__class__.__name__, 'DATE or TIMESTAMP'
                ),
                MessageCodes.INVALID_COLUMN_TYPE
            )

        if type(col1_type) != type(col2_type):
            raise ValueError(
                Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(
                    valid_time_columns, 'valid_time_columns', 'both columns of same type (DATE or TIMESTAMP)'
                ),
                MessageCodes.INVALID_ARG_VALUE
            )
    elif isinstance(valid_time_columns, str):
        col = valid_time_columns
        col_type = df_dtypes[col]

        if col not in df_columns:
                raise TeradataMlException(
                    Messages.get_message(MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND).format(
                        col, 'valid_time_columns', 'df', 'DataFrame'
                    ),
                    MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND
                )
        # When types are specified, ensure they are PERIOD_DATE or PERIOD_TIMESTAMP objects or classes.
        if not (
            isinstance(col_type, PERIOD_TIMESTAMP) or isinstance(col_type, PERIOD_DATE) or
            col_type is PERIOD_TIMESTAMP or col_type is PERIOD_DATE
        ):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.INVALID_COLUMN_TYPE).format(
                    'valid_time_columns',
                    col_type.__name__ if isinstance(col_type, type)
                    else col_type.__class__.__name__, 'PERIOD_DATE or PERIOD_TIMESTAMP'
                ),
                MessageCodes.INVALID_COLUMN_TYPE
            )
    else:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(
                valid_time_columns, 'valid_time_columns', 'tuple of two column names or a single column name'
            ),
            MessageCodes.INVALID_ARG_VALUE
        )

