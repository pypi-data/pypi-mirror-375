#!/usr/bin/python
# ##################################################################
#
# Copyright 2021 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Sanath Vobilisetty (Sanath.Vobilisetty@teradata.com)
# Secondary Owner: Pankaj Vinod Purandare (PankajVinod.Purandare@Teradata.com)
#
# ##################################################################
import pandas as pd
from collections import OrderedDict
from sqlalchemy.exc import OperationalError as sqlachemyOperationalError
from teradataml.common.constants import DriverEscapeFunctions, TeradataConstants
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.sqlbundle import SQLBundle
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import CopyToConstants
from teradataml.context.context import get_context, get_connection, \
    _get_context_temp_databasename, _get_current_databasename
from teradataml.dataframe import dataframe as tdmldf
from teradataml.dataframe.copy_to import copy_to_sql, _create_table_object, \
    _get_pd_df_column_names, _extract_column_info, \
    _check_columns_insertion_compatible, _get_index_labels
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.dbutils.dbutils import _create_table, _execute_query_and_generate_pandas_df
from teradataml.utils.validators import _Validators
from teradataml.telemetry_utils.queryband import collect_queryband


@collect_queryband(queryband="fstExprt")
def fastexport(df, export_to="pandas", index_column=None,
               catch_errors_warnings=False, csv_file=None,
               **kwargs):
    """
    DESCRIPTION:
        The fastexport() API exports teradataml DataFrame to Pandas DataFrame
        or CSV file using FastExport data transfer protocol.
        Note:
            1. Teradata recommends to use FastExport when number of rows in
               teradataml DataFrame are at least 100,000. To extract lesser rows
               ignore this function and go with regular to_pandas() or to_csv()
               function. FastExport opens multiple data transfer connections to the
               database.
            2. FastExport does not support all Teradata Database data types.
               For example, tables with BLOB and CLOB type columns cannot
               be extracted.
            3. FastExport cannot be used to extract data from a volatile or
               temporary table.
            4. For best efficiency, do not use DataFrame.groupby() and
               DataFrame.sort() with FastExport.

        For additional information about FastExport protocol through
        teradatasql driver, please refer to FASTEXPORT section of
        https://pypi.org/project/teradatasql/#FastExport driver documentation.

    PARAMETERS:
        df:
            Required Argument.
            Specifies teradataml DataFrame that needs to be exported.
            Types: teradataml DataFrame

        export_to:
            Optional Argument.
            Specifies a value that notifies where to export the data.
            Permitted Values:
                * "pandas": Export data to a Pandas DataFrame.
                * "csv": Export data to a given CSV file.
            Default Value: "pandas"
            Types: String

        index_column:
            Optional Argument.
            Specifies column(s) to be used as index column for the converted object.
            Note:
                Applicable only when 'export_to' is set to "pandas".
            Default Value: None.
            Types: String OR list of Strings (str)

        catch_errors_warnings:
            Optional Argument.
            Specifies whether to catch errors/warnings(if any) raised by
            fastexport protocol while converting teradataml DataFrame.
            Notes :
                1.  When 'export_to' is set to "pandas" and 'catch_errors_warnings' is set to True,
                    fastexport() returns a tuple containing:
                        a. Pandas DataFrame.
                        b. Errors(if any) in a list thrown by fastexport.
                        c. Warnings(if any) in a list thrown by fastexport.
                    When set to False, prints the fastexport errors/warnings to the
                    standard output, if there are any.


                2.  When 'export_to' is set to "csv" and 'catch_errors_warnings' is set to True,
                    fastexport() returns a tuple containing:
                        a. Errors(if any) in a list thrown by fastexport.
                        b. Warnings(if any) in a list thrown by fastexport.
            Default Value: False
            Types: bool

        csv_file:
            Optional Argument.
            Specifies the name of CSV file to which data is to be exported.
            Note:
                This is required argument when 'export_to' is set to "csv".
            Types: String

        kwargs:
            Optional Argument.
            Specifies keyword arguments. Accepts following keyword arguments:

            sep:
                Optional Argument.
                Specifies a single character string used to separate fields in a CSV file.
                Default Value: ","
                Notes:
                    1. "sep" cannot be line feed ('\\n') or carriage return ('\\r').
                    2. "sep" should not be same as "quotechar".
                    3. Length of "sep" argument should be 1.
                Types: String

            quotechar:
                Optional Argument.
                Specifies a single character string used to quote fields in a CSV file.
                Default Value: "\""
                Notes:
                    1. "quotechar" cannot be line feed ('\\n') or carriage return ('\\r').
                    2. "quotechar" should not be same as "sep".
                    3. Length of "quotechar" argument should be 1.
                Types: String

            coerce_float:
                Optional Argument.
                Specifies whether to convert non-string, non-numeric objects to floating point.
                Note:
                    For additional information about "coerce_float" please refer to:
                    https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html

            parse_dates:
                Optional Argument.
                Specifies columns to parse as dates.
                Note:
                    For additional information about "parse_date" please refer to:
                    https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html

            open_sessions:
                Optional Argument.
                specifies the number of Teradata sessions to be opened for fastexport.
                Note:
                    If "open_sessions" argument is not provided, the default value
                    is the smaller of 8 or the number of AMPs avaialble.
                    For additional information about number of Teradata data-transfer
                    sessions opened during fastexport, please refer to:
                    https://pypi.org/project/teradatasql/#FastExport
                Types: Integer


    RETURNS:
        1.  When 'export_to' is set to "pandas" and "catch_errors_warnings" is set to True,
            then the function returns a tuple containing:
                a. Pandas DataFrame.
                b. Errors, if any, thrown by fastexport in a list of strings.
                c. Warnings, if any, thrown by fastexport in a list of strings.
            When 'export_to' is set to "pandas" and "catch_errors_warnings" is set to False,
            then the function returns a Pandas DataFrame.
        2.  When 'export_to' is set to "csv" and "catch_errors_warnings" is set to True,
            then the function returns a tuple containing:
                a. Errors, if any, thrown by fastexport in a list of strings.
                b. Warnings, if any, thrown by fastexport in a list of strings.

    EXAMPLES:
        >>> from teradataml import *
        >>> load_example_data("dataframe", "admissions_train")
        >>> df = DataFrame("admissions_train")

        # Print dataframe.
        >>> df
              masters   gpa     stats programming admitted
           id
           13      no  4.00  Advanced      Novice        1
           26     yes  3.57  Advanced    Advanced        1
           5       no  3.44    Novice      Novice        0
           19     yes  1.98  Advanced    Advanced        0
           15     yes  4.00  Advanced    Advanced        1
           40     yes  3.95    Novice    Beginner        0
           7      yes  2.33    Novice      Novice        1
           22     yes  3.46    Novice    Beginner        0
           36      no  3.00  Advanced      Novice        0
           38     yes  2.65  Advanced    Beginner        1

        # Example 1: Export teradataml DataFrame df to Pandas DataFrame using
        #            fastexport().
        >>> fastexport(df)
            Errors: []
            Warnings: []
               masters   gpa     stats programming  admitted
            id
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            20     yes  3.90  Advanced    Advanced         1
            18     yes  3.81  Advanced    Advanced         1
            8       no  3.60  Beginner    Advanced         1
            25      no  3.96  Advanced    Advanced         1
            ...

        # Example 2: Export teradataml DataFrame df to Pandas DataFrame,
        #            set index column, coerce_float and catch errors/warnings thrown by
        #            fastexport.
        >>> pandas_df, err, warn = fastexport(df, index_column="gpa",
                                              catch_errors_warnings=True,
                                              coerce_float=True)
        # Print pandas DataFrame.
        >>> pandas_df
                 id masters     stats programming  admitted
            gpa
            2.65  38     yes  Advanced    Beginner         1
            3.57  26     yes  Advanced    Advanced         1
            3.44   5      no    Novice      Novice         0
            1.87  24      no  Advanced      Novice         1
            3.70   3      no    Novice    Beginner         1
            3.95   1     yes  Beginner    Beginner         0
            3.90  20     yes  Advanced    Advanced         1
            3.81  18     yes  Advanced    Advanced         1
            3.60   8      no  Beginner    Advanced         1
            3.96  25      no  Advanced    Advanced         1
            3.76   2     yes  Beginner    Beginner         0
            3.83  17      no  Advanced    Advanced         1

            ...
        # Print errors list.
        >>> err
            []
        # Print warnings list.
        >>> warn
            []

        # Example 3: Following example exports teradataml DataFrame df
        #            to Pandas DataFrame using fastexport() by opening specified
        #            number of Teradata data-transfer sessions.
        >>> fastexport(df, open_sessions=2)
            Errors: []
            Warnings: []
               masters   gpa     stats programming  admitted
            id
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            20     yes  3.90  Advanced    Advanced         1
            18     yes  3.81  Advanced    Advanced         1
            8       no  3.60  Beginner    Advanced         1
            25      no  3.96  Advanced    Advanced         1
            ...

        # Example 4: Following example exports teradataml DataFrame df
        #            to a given CSV file using fastexport().
        >>> fastexport(df, export_to="csv", csv_file="Test.csv")
            Data is successfully exported into Test.csv

        # Example 5: Following example exports teradataml DataFrame df
        #            to a given CSV file using fastexport() by opening specified
        #            number of Teradata data-transfer sessions.
        >>> fastexport(df, export_to="csv", csv_file="Test_1.csv", open_sessions=2)
            Data is successfully exported into Test_1.csv

        # Example 6: Following example exports teradataml DataFrame df
        #            to a given CSV file using fastexport() and catch errors/warnings
        #            thrown by fastexport.
        >>> err, warn = fastexport(df, export_to="csv", catch_errors_warnings=True,
                                   csv_file="Test_3.csv")
            Data is successfully exported into Test_3.csv
        # Print errors list.
        >>> err
            []
        # Print warnings list.
        >>> warn
            []

        # Example 7: Export teradataml DataFrame to CSV file with '|' as field separator
        #            and single quote(') as field quote character.
        >>> fastexport(df, export_to="csv", csv_file="Test_4.csv",  sep = "|", quotechar="'")
            Data is successfully exported into Test_4.csv

    """
    try:
        # Deriving global connection using context.get_context()
        con = get_context()
        if con is None:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                MessageCodes.CONNECTION_FAILURE)

        awu_matrix = []
        # Add new exports once supported.
        permitted_exports = ["pandas", "csv"]
        from teradataml.dataframe.dataframe import DataFrame
        awu_matrix.append(["df", df, False, DataFrame, True])
        awu_matrix.append(["export_to", export_to, True, str, False,
                           permitted_exports])
        awu_matrix.append(["csv_file", csv_file, True, str, True])

        # Get open_sessions argument.
        open_sessions = kwargs.get("open_sessions", None)
        awu_matrix.append(["open_sessions", open_sessions, True, int, False])

        # Validate arguments unique to fastexport() function.
        _Validators._validate_function_arguments(awu_matrix)

        if open_sessions is not None:
            _Validators._validate_positive_int(open_sessions, "open_sessions")

        # Convert teradataml DataFrame to pandas DataFrame.
        if export_to.lower() == "pandas":
            # Initialize and validate DataTransferUtils object.
            dt_obj = _DataTransferUtils(df, index_column=index_column,
                                        all_rows=True,
                                        catch_errors_warnings=catch_errors_warnings)

            # Call fastexport_get_pandas_df function to get pandas dataframe
            # using fastexport datatransfer protocol.
            # "require" is always True, because with this function user requires
            # fastexport.

            return dt_obj._fastexport_get_pandas_df(require=True, **kwargs)

        # Convert teradataml DataFrame to CSV file.
        if export_to.lower() == "csv":
            if not csv_file:
                raise TeradataMlException(
                    Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, "csv_file",
                                         "{0}='{1}'".format("export_to", "csv")),
                    MessageCodes.DEPENDENT_ARG_MISSING)

            if not csv_file.lower().endswith(".csv"):
                raise TeradataMlException(
                    Messages.get_message(MessageCodes.INVALID_ARG_VALUE, csv_file,
                                         "csv_file", "file with csv format"),
                    MessageCodes.INVALID_ARG_VALUE)

            # Get "sep" and "quotechar" argument.
            sep = kwargs.pop("sep", ",")
            quotechar = kwargs.pop("quotechar", "\"")

            dt_obj = _DataTransferUtils(df, all_rows=True,
                                        sep=sep, quotechar=quotechar,
                                        catch_errors_warnings=catch_errors_warnings)
            return dt_obj._get_csv(require_fastexport=True, csv_file_name=csv_file, **kwargs)

    except TeradataMlException:
        raise
    except TypeError:
        raise
    except ValueError:
        raise
    except Exception as err:
        raise TeradataMlException(
            Messages.get_message(MessageCodes.DATA_EXPORT_FAILED, "fastexport",
                                 export_to, str(err)),
            MessageCodes.DATA_EXPORT_FAILED)


@collect_queryband(queryband="rdCsv")
def read_csv(filepath,
             table_name,
             types=None,
             sep=",",
             quotechar="\"",
             schema_name=None,
             if_exists='replace',
             primary_index=None,
             set_table=False,
             temporary=False,
             primary_time_index_name=None,
             timecode_column=None,
             timebucket_duration=None,
             timezero_date=None,
             columns_list=None,
             sequence_column=None,
             seq_max=None,
             catch_errors_warnings=False,
             save_errors=False,
             use_fastload=True,
             open_sessions=None):
    """
    The read_csv() API loads data from CSV file into Teradata Vantage.
    Function can be used to quickly load large amounts of data in a table on Vantage
    using FastloadCSV protocol.

    Considerations when using a CSV file:
    * Each record is on a separate line of the CSV file. Records are delimited
      by line breaks (CRLF). The last record in the file may or may not have an
      ending line break.
    * First line in the CSV must be header line. The header line lists
      the column names separated by the field separator (e.g. col1,col2,col3).
    * Using a CSV file with FastLoad has limitations as follows:
        1. read_csv API cannot load duplicate rows in the DataFrame if the table is a
           MULTISET table having primary index.
        2. read_csv API does not support all Teradata Advanced SQL Engine data types.
           For example, target table having BLOB and CLOB data type columns cannot be
           loaded.
        3. If there are any incorrect rows, i.e. due to constraint violations, data type
           conversion errors, etc., FastLoad protocol ignores those rows and inserts
           all valid rows.
        4. Rows in the DataFrame that failed to get inserted are categorized into errors
           and warnings by FastLoad protocol and these errors and warnings are stored
           into respective error and warning tables by FastLoad API.
        5. Teradata recommends to use Fastload protocol when number of rows to be loaded
           are at least 100,000. Fastload opens multiple data transfer connections to the
           database.

    For additional information about FastLoadCSV protocol through teradatasql driver,
    please refer the CSV BATCH INSERTS section of https://pypi.org/project/teradatasql/#CSVBatchInserts
    driver documentation for more information.

    PARAMETERS:
        filepath:
            Required Argument.
            Specifies the CSV filepath including name of the file to load the data from.
            Types: String

        table_name:
            Required Argument.
            Specifies the table name to load the data into.
            Types: String

        types:
            Optional Argument when if_exists=append and non-PTI table already exists, Required otherwise.
            Specifies the data types for requested columns to be saved in Vantage.
            Keys of this dictionary should be the name of the columns and values should be
            teradatasqlalchemy.types.
            Default Value: None
            Note:
                * If specified when "if_exists" is set to append and table exists, then argument is ignored.
            Types: OrderedDict

        sep:
            Optional Argument.
            Specifies a single character string used to separate fields in a CSV file.
            Default Value: ","
            Notes:
                * "sep" cannot be line feed ('\\n') or carriage return ('\\r').
                * "sep" should not be same as "quotechar".
                * Length of "sep" argument should be 1.
            Types: String

        quotechar:
            Optional Argument.
            Specifies a single character string used to quote fields in a CSV file.
            Default Value: "\""
            Notes:
                * "quotechar" cannot be line feed ('\\n') or carriage return ('\\r').
                * "quotechar" should not be same as "sep".
                * Length of "quotechar" argument should be 1.
            Types: String

        schema_name:
            Optional Argument.
            Specifies the name of the database/schema in Vantage to write to.
            Default Value: None (Uses default database/schema).
            Types: String

        if_exists:
            Optional Argument.
            Specifies the action to take when table already exists in Vantage.
            Permitted Values: 'fail', 'replace', 'append'
                - fail: If table exists, raise TeradataMlException.
                - replace: If table exists, drop it, recreate it, and insert data.
                - append: If table exists, append the existing table.
            Default Value: replace
            Types: String

        primary_index:
            Optional Argument.
            Specifies which column(s) to use as primary index while creating table
            in Vantage. When set to None, No Primary Index (NoPI) tables are created.
            Default Value: None
            Types: String or list of strings
            Example:
                primary_index = 'my_primary_index'
                primary_index = ['my_primary_index1', 'my_primary_index2', 'my_primary_index3']

        set_table:
            Optional Argument.
            Specifies a flag to determine whether to create a SET or a MULTISET table.
            When set to True, a SET table is created, otherwise MULTISET table is created.
            Default Value: False
            Notes:
                1. Specifying set_table=True also requires specifying primary_index.
                2. Creating SET table (set_table=True) results in
                    a. loss of duplicate rows, if CSV contains any duplicate.
                3. This argument has no effect if the table already exists and if_exists='append'.
            Types: Boolean

        temporary:
            Optional Argument.
            Specifies whether to create table as volatile.
            Default Value: False
            Notes:
                When set to True
                 1. FastloadCSV protocol is not used for loading the data.
                 2. "schema_name" is ignored.
           Types : Boolean

        primary_time_index_name:
            Optional Argument.
            Specifies the name for the Primary Time Index (PTI) when the table
            is to be created as PTI table.
            Note:
                This argument is not required or used when the table to be created
                is not a PTI table. It will be ignored if specified without the "timecode_column".
            Types: String

        timecode_column:
            Optional argument.
            Required when the CSV data must be saved as a PTI table.
            Specifies the column in the csv that reflects the form
            of the timestamp data in the time series.
            This column will be the TD_TIMECODE column in the table created.
            It should be of SQL type TIMESTAMP(n), TIMESTAMP(n) WITH TIMEZONE, or DATE,
            corresponding to Python types datetime.datetime or datetime.date.
            Note:
                When "timecode_column" argument is specified, an attempt to create a PTI table
                will be made. This argument is not required when the table to be created
                is not a PTI table. If this argument is specified, "primary_index" will be ignored.
            Types: String

        timezero_date:
            Optional Argument.
            Used when the CSV data must be saved as a PTI table.
            Specifies the earliest time series data that the PTI table will accept,
            a date that precedes the earliest date in the time series data.
            Value specified must be of the following format: DATE 'YYYY-MM-DD'
            Default Value: DATE '1970-01-01'.
            Note:
                This argument is not required or used when the table to be created
                is not a PTI table. It will be ignored if specified without the "timecode_column".
            Types: String

        timebucket_duration:
            Optional Argument.
            Required if "columns_list" is not specified or is None.
            Used when the CSV data must be saved as a PTI table.
            Specifies a duration that serves to break up the time continum in
            the time series data into discrete groups or buckets.
            Specified using the formal form time_unit(n), where n is a positive
            integer, and time_unit can be any of the following:
            CAL_YEARS, CAL_MONTHS, CAL_DAYS, WEEKS, DAYS, HOURS, MINUTES,
            SECONDS, MILLISECONDS, or MICROSECONDS.
            Note:
                This argument is not required or used when the table to be created
                is not a PTI table. It will be ignored if specified without the "timecode_column".
            Types: String

        columns_list:
            Optional Argument.
            Used when the CSV data must be saved as a PTI table.
            Required if "timebucket_duration" is not specified.
            A list of one or more PTI table column names.
            Note:
                This argument is not required or used when the table to be created
                is not a PTI table. It will be ignored if specified without the "timecode_column".
            Types: String or list of Strings

        sequence_column:
            Optional Argument.
            Used when the CSV data must be saved as a PTI table.
            Specifies the column of type Integer containing the unique identifier for
            time series data readings when they are not unique in time.
            * When specified, implies SEQUENCED, meaning more than one reading from the same
              sensor may have the same timestamp.
              This column will be the TD_SEQNO column in the table created.
            * When not specified, implies NONSEQUENCED, meaning there is only one sensor reading
              per timestamp.
              This is the default.
            Note:
                This argument is not required or used when the table to be created
                is not a PTI table. It will be ignored if specified without the "timecode_column".
            Types: String

        seq_max:
            Optional Argument.
            Used when the CSV data must be saved as a PTI table.
            Specifies the maximum number of data rows that can have the
            same timestamp. Can be used when 'sequenced' is True.
            Permitted range:  1 - 2147483647.
            Default Value: 20000.
            Note:
                This argument is not required or used when the table to be created
                is not a PTI table. It will be ignored if specified without the "timecode_column".
            Types: Integer

        save_errors:
            Optional Argument.
            Specifies whether to persist the errors/warnings(if any) information in Vantage
            or not.
            If "save_errors" is set to False:
             1. Errors or warnings (if any) are not persisted into tables.
             2. Errors table genarated by FastloadCSV are not persisted.
            If "save_errors" is set to True:
             1. The errors or warnings information is persisted and names of error and
                warning tables are returned. Otherwise, the function returns None for
                the names of the tables.
             2. The errors tables generated by FastloadCSV are persisted and name of
                error tables are returned. Otherwise, the function returns None for
                the names of the tables.
            Default Value: False
            Types: Boolean

        catch_errors_warnings:
            Optional Argument.
            Specifies whether to catch errors/warnings(if any) raised by fastload
            protocol while loading data into the Vantage table.
            When set to False, function does not catch any errors and warnings,
            otherwise catches errors and warnings, if any, and returns
            as a dictionary along with teradataml DataFrame.
            Please see 'RETURNS' section for more details.
            Default Value: False
            Types: Boolean

        use_fastload:
            Optional Argument.
            Specifies whether to use Fastload CSV protocol or not.
            Default Value: True
            Notes:
                1. Teradata recommends to use Fastload when number of rows to be loaded
                   are atleast 100,000. To load lesser rows set this argument to 'False'.
                   Fastload opens multiple data transfer connections to the database.
                2. When "use_fastload" is set to True, one can load the data into table
                   using FastloadCSV protocol:
                    a. Set table
                    b. Multiset table
                3. When "use_fastload" is set to False, one can load the data in following
                   types of tables:
                    a. Set table
                    b. Multiset table
                    c. PTI table
                    d. Volatile table
            Types: Boolean

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

    RETURNS:
        When "use_fastload" is set to False, returns teradataml dataframe.
        When "use_fastload" is set to True, read_csv() returns below:
            When "catch_errors_warnings" is set to False, returns only teradataml dataframe.
            When "catch_errors_warnings" is set to True, read_csv() returns a tuple containing:
                a. teradataml DataFrame.
                b. a dict containing the following attributes:
                    a. errors_dataframe: It is a Pandas DataFrame containing error messages
                       thrown by fastload. DataFrame is empty if there are no errors.
                    b. warnings_dataframe: It is a Pandas DataFrame containing warning messages
                       thrown by fastload. DataFrame is empty if there are no warnings.
                    c. errors_table: Name of the table containing errors. It is None, if
                       argument save_errors is False.
                    d. warnings_table: Name of the table containing warnings. It is None, if
                       argument save_errors is False.
                    e. fastloadcsv_error_tables: Name of the tables containing errors generated
                       by FastloadCSV. It is empty list, if argument "save_errors" is False.

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>> from teradataml.dataframe.data_transfer import read_csv
        >>> from teradatasqlalchemy.types import *
        >>> from collections import OrderedDict

        # Example 1: Default execution with types argument is passed as OrderedDict.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv('test_file.csv', 'my_first_table', types)

        # Example 2: Load the data from CSV file into a table using fastload CSV protocol,
        #            while doing so catch all errors and warnings as well as store those in the table.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table1', types=types,
        ...          save_errors=True, catch_errors_warnings=True)

        # Example 3: Load the data from CSV file into a table using fastload CSV protocol.
        #            If table exists, then replace the same. Catch all errors and warnings as well as
        #            store those in the table.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          types=types, if_exists='replace',
        ...          save_errors=True, catch_errors_warnings=True)

        # Example 4: Load the data from CSV file into a table using fastload CSV protocol.
        #            If table exists in specified schema, then append the same. Catch all
        #            errors and warnings as well as store those in the table.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          types=types, if_exists='fail',
        ...          save_errors=True, catch_errors_warnings=True)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          if_exists='append',
        ...          save_errors=True, catch_errors_warnings=True)

        # Example 5: Load the data from CSV file into a SET table using fastload CSV protocol.
        #            Catch all errors and warnings as well as store those in the table.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          types=types, if_exists='replace',
        ...          set_table=True, primary_index='id',
        ...          save_errors=True, catch_errors_warnings=True)

        # Example 6: Load the data from CSV file into a temporary table without fastloadCSV protocol.
        #            If table exists, then append to the same.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          types=types, if_exists='replace',
        ...          temporary=True)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          if_exists='append',
        ...          temporary=True)

        # Example 7: Load the data from CSV file with DATE and TIMESTAMP columns into
        #            a table without Fastload protocol. If table exists in specified
        #            schema, then append to the table.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT,
        ...                     admission_date=DATE, admission_time=TIMESTAMP)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          types=types, if_exists='fail',
        ...          use_fastload=False)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_table',
        ...          if_exists='append',
        ...          use_fastload=False)

        # Example 8: Load the data from CSV file with TIMESTAMP columns into
        #            a PTI table. If specified table exists then append to the table,
        #            otherwise creates new table.
        >>> types = OrderedDict(partition_id=INTEGER, adid=INTEGER, productid=INTEGER,
        ...                     event=VARCHAR, clicktime=TIMESTAMP)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_read_csv_pti_table',
        ...          types=types, if_exists='append',
        ...          timecode_column='clicktime',
        ...          columns_list='event',
        ...          use_fastload=False)

        # Example 9: Load the data from CSV file with TIMESTAMP columns into
        #            a SET PTI table. If specified table exists then append to the table,
        #            otherwise creates new table.
        >>> types = OrderedDict(partition_id=INTEGER, adid=INTEGER, productid=INTEGER,
                                event=VARCHAR, clicktime=TIMESTAMP)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_read_csv_pti_table',
        ...          types=types, if_exists='append',
        ...          timecode_column='clicktime',
        ...          columns_list='event',
        ...          set_table=True)

        # Example 10: Load the data from CSV file with TIMESTAMP columns into
        #            a temporary PTI table. If specified table exists then append to the table,
        #            otherwise creates new table.
        >>> types = OrderedDict(partition_id=INTEGER, adid=INTEGER, productid=INTEGER,
                                event=VARCHAR, clicktime=TIMESTAMP)
        >>> read_csv(filepath='test_file.csv',
        ...          table_name='my_first_read_csv_pti_table',
        ...          types=types, if_exists='append',
        ...          timecode_column='clicktime',
        ...          columns_list='event',
        ...          temporary=True)

        # Example 11: Load the data from CSV file into Vantage table by opening specified
        #             number of Teradata data transfer sesions.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv(filepath='test_file.csv', table_name='my_first_table_with_open_sessions',
                    types=types, open_sessions=2)

        # Example 12: Load the data from CSV file into Vantage table and set primary index provided
        #             through primary_index argument.
        >>> types = OrderedDict(id=BIGINT, fname=VARCHAR, lname=VARCHAR, marks=FLOAT)
        >>> read_csv(filepath='test_file.csv', table_name='my_first_table_with_primary_index',
        ...          types=types, primary_index = ['fname'])

        # Example 13: Load the data from CSV file into VECTOR datatype in Vantage table.
        >>> from teradatasqlalchemy import VECTOR
        >>> from pathlib import Path
        >>> types = OrderedDict(id=BIGINT, array_col=VECTOR)

        # Get the absolute path of the teradataml module
        >>> import teradataml
        >>> base_path = Path(teradataml.__path__[0])

        # Append the relative path to the CSV file
        >>> csv_path = os.path.join(base_path, "data", "hnsw_alter_data.csv")

        >>> read_csv(filepath=csv_path, 
        ...          table_name='my_first_table_with_vector',
        ...          types=types,
        ...          use_fastload=False)
    """
    # Deriving global connection using context.get_context()
    con = get_context()

    try:
        if con is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                      MessageCodes.CONNECTION_FAILURE)

        schema_name = _get_context_temp_databasename() if schema_name is None else schema_name

        # Create _DataTransferUtils object.
        dt_obj = _DataTransferUtils(filepath, table_name=table_name, types=types,
                                    sep=sep, quotechar=quotechar, schema_name=schema_name,
                                    if_exists=if_exists, primary_index=primary_index,
                                    set_table=set_table, temporary=temporary,
                                    primary_time_index_name=primary_time_index_name,
                                    timecode_column=timecode_column,
                                    timebucket_duration=timebucket_duration,
                                    timezero_date=timezero_date, columns_list=columns_list,
                                    sequence_column=sequence_column, seq_max=seq_max,
                                    save_errors=save_errors,
                                    catch_errors_warnings=catch_errors_warnings,
                                    use_fastload=use_fastload,
                                    api_name='read_csv',
                                    open_sessions=open_sessions)

        # Validate read_csv api argument
        dt_obj._validate_read_csv_api_args()

        # Check if CSV file exists
        _Validators._validate_file_exists(filepath)

        # Ignore open_sessions argument when use_fastload is set to False
        if not use_fastload and open_sessions is not None:
            UtilFuncs._get_warnings('open_sessions', open_sessions, 'use_fastload', use_fastload)
            dt_obj.open_sessions = None

        # If temporary=True, set use_fastload=False and schema name=None.
        if temporary:
            # Setting fastload related arguments to False.
            dt_obj.use_fastload = False
            use_fastload = False

            if schema_name is not None:
                UtilFuncs._get_warnings("schema_name", schema_name, "temporary", "True")
            schema_name = None

        # A table cannot be a SET table and have NO PRIMARY INDEX
        if set_table and primary_index is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.SET_TABLE_NO_PI),
                                      MessageCodes.SET_TABLE_NO_PI)

        # Check for PTI table.
        if timecode_column is not None:
            rc_dict = dt_obj._process_pti_load_csv_data(con=con)
            return dt_obj._get_result(rc_dict)

        # Check if table exists.
        table_exists = dt_obj._table_exists(con)

        # Raise exception when table not exists and if_exists='fail'.
        dt_obj._check_table_exists(is_table_exists=table_exists)

        # Let's create the SQLAlchemy table object to recreate the table.
        if not table_exists or if_exists.lower() == 'replace':
            # Validate required argument "types" when table doesn't exist
            _Validators._validate_argument_is_not_None(types, "types")

            dt_obj._create_or_replace_table(con, table_exists=table_exists)

            # Load the CSV data into newly created table.
            if not use_fastload:
                rc_dict = dt_obj._insert_from_csv_without_fastload(table_name=table_name,
                                                                   column_names=types.keys())
            else:
                rc_dict = dt_obj._insert_from_csv_with_fastload(table_name=table_name,
                                                                column_names=types.keys())

        # Check column compatibility for insertion when table exists and if_exists = 'append'.
        if table_exists and if_exists.lower() == 'append':
            if set_table:
                UtilFuncs._get_warnings('set_table', set_table, 'if_exists', 'append')

            # Create SQLAlchemy table object from existing table.
            existing_table = UtilFuncs._get_sqlalchemy_table(table_name,
                                                             schema_name=schema_name)

            # Check compatibility of CSV columns with existing table columns.
            if types is not None:
                cols = _extract_column_info(filepath, types=types)
                dt_obj._check_columns_compatibility(table_obj=existing_table, cols=cols)

            # Validate user provided primary index against primary index of existing table .
            existing_table_primary_index = UtilFuncs._extract_table_object_index_info(existing_table)
            if primary_index is not None:
                dt_obj._check_index_compatibility(primary_index_1=existing_table_primary_index,
                                                  primary_index_2=primary_index)

            cols_name, cols_type = UtilFuncs._extract_table_object_column_info(existing_table.c)
            column_info = dict(zip(cols_name, cols_type))

            if use_fastload:
                rc_dict = dt_obj._create_staging_table_and_load_csv_data(column_info=column_info,
                                                                         primary_index=existing_table_primary_index)
            else:
                rc_dict = dt_obj._insert_from_csv_without_fastload(table_name=table_name,
                                                                   column_names=cols_name)
        # Return the read_csv result.
        return dt_obj._get_result(rc_dict)

    except (TeradataMlException, sqlachemyOperationalError, ValueError, TypeError):
        raise
    except Exception as err:
        error_code = MessageCodes.EXECUTION_FAILED
        error_msg = Messages.get_message(
            error_code, "execute read_csv()", '{}'.format(str(err)))
        raise TeradataMlException(error_msg, error_code)


class _DataTransferUtils():
    """
    This class provides utility functions which enable Data Transfer from
    Teradata Vantage to outside world, for example Data Transfer using
    FastExport Protocol.
    """

    def __init__(self, df, index_column=None, num_rows=99999, all_rows=False,
                 catch_errors_warnings=False, table_name=None,
                 schema_name=None, if_exists='append', index=False,
                 index_label=None, primary_index=None, temporary=False,
                 types=None, batch_size=None, save_errors=False, sep=",",
                 quotechar="\"", set_table=False,
                 primary_time_index_name=None, timecode_column=None,
                 timebucket_duration=None, timezero_date=None,
                 columns_list=None, sequence_column=None, seq_max=None,
                 use_fastload=True, api_name='fastexport',
                 open_sessions=None, chunksize=CopyToConstants.DBAPI_BATCHSIZE.value,
                 match_column_order=True, err_tbl_1_suffix=None,
                 err_tbl_2_suffix=None, err_tbl_name=None, warn_tbl_name=None,
                 err_staging_db=None):
        """
        DESCRIPTION:
            Constructor for the _DataTransferUtils class. It initialises
            arguments that are required for data transfer using FastExport
            protocol or non-fastexport based data transfer using to_pandas()
            API.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the teradataml DataFrame from which data is to be
                extracted. OR
                Specifies the CSV filepath including name of the file to
                load the data from.
                Types: teradataml DataFrame OR str

            index_column:
                Optional Argument.
                Specifies column(s) to be used as index column for the converted
                object.
                Types: str OR list of Strings (str)

            num_rows:
                Optional Argument.
                Specifies the number of rows to be retrieved from teradataml
                DataFrame.
                Default Value: 99999
                Types: int

            all_rows:
                Optional Argument.
                Specifies whether all rows from teradataml DataFrame should be
                retrieved.
                Default Value: False
                Types: bool

            catch_errors_warnings:
                Optional Argument.
                Specifies whether to catch errors/warnings(if any) raised by
                fastexport protocol while converting teradataml DataFrame.
                Default Value: False
                Types: bool

            table_name:
                Optional Argument.
                Specifies the table name to load the data into.
                Types: String

            types:
                Optional Argument.
                Specifies the data types for requested columns to be saved in Vantage.
                Keys of this dictionary should be the name of the columns and values should be
                teradatasqlalchemy.types.
                Default Value: None
                Note:
                    This should be OrderedDict, if CSV file does not contain header.
                Types: OrderedDict

            sep:
                Optional Argument.
                Specifies a single character string used to separate fields in a CSV file.
                Default Value: ","
                Notes:
                    * "sep" cannot be line feed ('\\n') or carriage return ('\\r').
                    * "sep" should not be same as "quotechar".
                    * Length of "sep" argument should be 1.
                Types: String

            quotechar:
                Optional Argument.
                Specifies a single character string used to quote fields in a CSV file.
                Default Value: "\""
                Notes:
                    * "quotechar" cannot be line feed ('\\n') or carriage return ('\\r').
                    * "quotechar" should not be same as "sep".
                    * Length of "quotechar" argument should be 1.
                Types: String

            schema_name:
                Optional Argument.
                Specifies the name of the database schema in Vantage to write to.
                Default Value: None (Uses default database schema).
                Types: String

            if_exists:
                Optional Argument.
                Specifies the action to take when table already exists in Vantage.
                Permitted Values: 'fail', 'replace', 'append'
                    - fail: If table exists, raise TeradataMlException.
                    - replace: If table exists, drop it, recreate it, and insert data.
                    - append: If table exists, insert data. Create if does not exist.
                Default Value: fail
                Types: String

            primary_index:
                Optional Argument.
                Specifies which column(s) to use as primary index while creating table
                in Vantage. When set to None, No Primary Index (NoPI) tables are created.
                Default Value: None
                Types: String or list of strings
                Example:
                    primary_index = 'my_primary_index'
                    primary_index = ['my_primary_index1', 'my_primary_index2', 'my_primary_index3']

            temporary:
                Optional Argument.
                Specifies whether to creates Vantage tables as permanent or volatile.
                When set to True:
                    1. volatile Tables are created, and
                    2. schema_name is ignored.
                When set to False, permanent tables are created.
                Default Value: False
                Types : Boolean (True or False)

            set_table:
                Optional Argument.
                Specifies a flag to determine whether to create a SET or a MULTISET table.
                When set to True, a SET table is created, otherwise MULTISET table is created.
                Default Value: False
                Notes:
                    1. Specifying set_table=True also requires specifying primary_index.
                    2. Creating SET table (set_table=True) results in
                       a. loss of duplicate rows.
                    3. This argument has no effect if the table already exists and if_exists='append'.
                Types: Boolean

            save_errors:
                Optional Argument.
                Specifies whether to persist the errors/warnings(if any) information in Vantage
                or not. If save_errors is set to False, errors/warnings(if any) are not persisted
                as tables. If argument is set to True, the error and warnings information
                are persisted and names of error and warning tables are returned. Otherwise,
                the function returns None for the names of the tables.
                Default Value: False
                Types: bool

            open_sessions:
                Optional Argument.
                Specifies the number of Teradata data transfer sessions to be opened for fastload operation.
                Note :
                    If "open_sessions" argument is not provided, the default value is
                    the one smaller out of 8 and the number of AMPs available.
                Default Value: None
                Types: int

            chunksize:
                Optional Argument.
                Specifies the number of rows to be loaded in a batch.
                Note:
                    This is argument is used only when argument "df" is pandas DataFrame.
                Default Value: 16383
                Types: int

            err_tbl_1_suffix:
                Optional Argument.
                Specifies the suffix for error table 1 created by fastload job.
                Types: String

            err_tbl_2_suffix:
                Optional Argument.
                Specifies the suffix for error table 2 created by fastload job.
                Types: String

            err_tbl_name:
                Optional Argument.
                Specifies the name for error table.
                Types: String

            warn_tbl_name:
                Optional Argument.
                Specifies the name for warning table.
                Types: String

            err_staging_db:
                Optional Argument.
                Specifies the name of the database to be used for creating staging
                table and error tables.
                Note:
                    Current session user must have CREATE, DELETE and INSERT table
                    rights on err_staging_db database.
                Types: String

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj = _DataTransferUtils(df, index_column='gpa')
            dt_obj = _DataTransferUtils(df, num_rows=10)
            dt_obj = _DataTransferUtils(df, all_rows=True, num_rows=5)
            dt_obj = _DataTransferUtils(df, catch_errors_warnings=True,
                                        num_rows=200)
            dt_obj = _DataTransferUtils(df, table_name='my_table',
                                        types={'id': BIGINT, 'fname': VARCHAR,
                                        'lname': VARCHAR, 'marks': FLOAT})
        """

        self.df = df
        self.index_column = index_column
        self.num_rows = num_rows
        self.all_rows = all_rows
        self.catch_errors_warnings = catch_errors_warnings
        self.table_name = table_name
        self.schema_name = schema_name
        self.if_exists = if_exists
        self.index = index
        self.index_label = index_label
        self.primary_index = primary_index
        self.temporary = temporary
        self.types = types
        self.batch_size = batch_size
        self.save_errors = save_errors
        self.sep = sep
        self.quotechar = quotechar
        self.primary_time_index_name = primary_time_index_name
        self.timecode_column = timecode_column
        self.timebucket_duration = timebucket_duration
        self.timezero_date = timezero_date
        self.columns_list = columns_list
        self.sequence_column = sequence_column
        self.seq_max = seq_max
        self.set_table = set_table
        self.use_fastload = use_fastload
        self.api_name = api_name
        self.open_sessions = open_sessions
        self.chunksize = chunksize
        self.match_column_order = match_column_order
        self.err_tbl_1_suffix = err_tbl_1_suffix
        self.err_tbl_2_suffix = err_tbl_2_suffix
        self.err_tbl_name = err_tbl_name
        self.warn_tbl_name = warn_tbl_name
        self.err_staging_db = err_staging_db

        # Validate arguments.
        if self.api_name == 'fastexport':
            self._validate_data_export_api_args()

    # Functions specific to validation of arguments of
    # Datatransfer APIs.
    def _validate_data_export_api_args(self):
        """
        DESCRIPTION:
            Function to validate common arguments used in data export API's
            such as:
                1. DataFrame.to_pandas()
                2. DataFrame.to_csv()
                2. fastexport()

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            TeradataMlException,
            TypeError,
            ValueError.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._validate_data_export_api_args()
        """
        awu_matrix = []
        awu_matrix.append(
            ["index_column", self.index_column, True, (str, list), True])
        awu_matrix.append(["num_rows", self.num_rows, True, (int)])
        awu_matrix.append(["all_rows", self.all_rows, True, (bool)])
        awu_matrix.append(
            ["catch_errors_warnings", self.catch_errors_warnings, True, (bool)])
        awu_matrix.append(["open_sessions", self.open_sessions, True, (int), False])
        awu_matrix.append(["sep", self.sep, True, str, False])
        awu_matrix.append(["quotechar", self.quotechar, True, str, False])

        # Validate argument types.
        _Validators._validate_function_arguments(awu_matrix)
        # Validate if 'num_rows' is a positive int.
        _Validators._validate_positive_int(self.num_rows, "num_rows")
        # Validate if 'open_sessions' is a positive int.
        _Validators._validate_positive_int(self.open_sessions, "open_sessions")

        # Validate "sep" and "quotechar" arguments related to export to CSV.
        self._validate_csv_sep_quotechar()

        # Checking if meta expression exists for given dataframe.
        if self.df._metaexpr is None:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.TDMLDF_INFO_ERROR),
                MessageCodes.TDMLDF_INFO_ERROR)

        # Checking each element in passed columns to be valid column in
        # dataframe.
        _Validators._validate_column_exists_in_dataframe(self.index_column,
                                                         self.df._metaexpr)

    def _validate_read_csv_api_args(self):
        """
        Internal function to validate read_csv api arguments.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            dt_obj = _DataTransferUtils()
            dt_obj._validate_read_csv_api_args()
        """
        # Validate read_csv api arguments.
        self._validate()

        # Validate "sep" and "quotechar" arguments.
        self._validate_csv_sep_quotechar()

    def _validate_csv_sep_quotechar(self):
        """
        Internal function to validate field separator and field quote character
        used in data transfer APIs which involve CSV.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            dt_obj = _DataTransferUtils()
            dt_obj._validate_csv_sep_quotechar()
        """

        # Function to validate char value for length and allowed characters.
        def validate_char_arg_csv(arg_name, arg):

            if arg is not None:
                _Validators._validate_str_arg_length(arg_name, arg, 'EQ', 1)

            not_allowed_values = ["\n", "\r"]
            if arg in not_allowed_values:
                message = Messages.get_message(MessageCodes.NOT_ALLOWED_VALUES,
                                               "{}".format(not_allowed_values), arg_name)
                raise TeradataMlException(message, MessageCodes.NOT_ALLOWED_VALUES)

        # Validate the 'sep' and 'quotechar' arguments.
        validate_char_arg_csv("sep", self.sep)
        validate_char_arg_csv("quotechar", self.quotechar)

        # Validate 'quotechar' and 'sep' arguments not set to same value
        if self.quotechar == self.sep:
            message = Messages.get_message(MessageCodes.ARGUMENT_VALUE_SAME, "sep",
                                           "quotechar")
            raise TeradataMlException(message, MessageCodes.ARGUMENT_VALUE_SAME)

    # End of functions specific to validation of arguments of
    # Datatransfer APIs.

    # Functions specific to fastexport().
    def _validate_df_index_column(self):
        """
        DESCRIPTION:
            Function to validate dataframe index label and throw exception if
            there is any mismatch in the index label and columns present in the
            teradataml DataFrame.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            TeradataMLException.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._validate_df_index_column()
        """
        # Get list of columns in teradatml DataFrame.
        df_column_list = [col.name.lower() for col in self.df._metaexpr.c]

        # Check if TDML DF has appropriate index_label set when required
        if self.df._index_label is not None:
            for index_label in UtilFuncs._as_list(self.df._index_label):
                if index_label.lower() not in df_column_list:
                    raise TeradataMlException(
                        Messages.get_message(MessageCodes.DF_LABEL_MISMATCH),
                        MessageCodes.DF_LABEL_MISMATCH)

    def _get_pandas_df_index(self):
        """
        DESCRIPTION:
            Function returns the final index column to be used in the resultant
            DataFrame after converting teradataml DataFrame to Pandas DataFrame.

        PARAMETERS:
            None.

        RETURNS:
            Final Valid index as str or list of Strings.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._get_pandas_df_index()
        """
        index_col = None
        # Index Order: 1) User specified 2) TDMLDF index 3) DB PI
        # 4)Else default integer index
        if self.index_column:
            index_col = self.index_column
        elif self.df._index_label:
            index_col = self.df._index_label
        else:
            try:
                from teradataml.dataframe.dataframe_utils import DataFrameUtils
                index_col = DataFrameUtils._get_primary_index_from_table(
                    self.df._table_name)
            except Exception as err:
                index_col = None

        return index_col

    def _generate_to_pandas_base_query(self):
        """
        DESCRIPTION:
            Function to generate base query for to_pandas() function. This query
            is further used to generate pandas dataframe.

        PARAMETERS:
            None.

        RETURNS:
            str.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            base_query = dt_obj._generate_to_pandas_base_query()
        """
        # Generate SQL Query using Table name & number of rows required.
        if self.all_rows:
            # Get read query for the whole data.
            return SQLBundle._build_base_query(self.df._table_name,
                                               self.df._orderby)
        else:
            # Get read query using SAMPLE.
            return SQLBundle._build_sample_rows_from_table(self.df._table_name,
                                                           self.num_rows,
                                                           self.df._orderby)

    def _generate_select_query(self):
        """
        DESCRIPTION:
            Function to generate SELECT query.

        PARAMETERS:
            None.

        RETURNS:
            str.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            base_query = dt_obj._generate_select_query()
        """
        # Generate SQL Query using Table name & number of rows required.
        if self.all_rows:
            # Get read query for the whole data.
            return SQLBundle._build_base_query(self.df._table_name,
                                               self.df._orderby)
        else:
            # Get read query using SAMPLE.
            return SQLBundle._build_top_n_print_query(self.df._table_name,
                                                      self.num_rows,
                                                      self.df._orderby)

    def _generate_fastexport_query(self, base_query, require=False, open_sessions=None,
                                   csv_file_name=None):
        """
        DESCRIPTION:
            Function to generate fastexport compatible query.

        PARAMETERS:
            base_query:
                Required Argument.
                Specifies the base query to be used for forming the fastexport
                query.
                Types: str

            require:
                Optional Argument.
                Specifies whether fastexport protocol is required for data
                transfer.
                Default Value: False
                Types: bool

            open_sessions:
                Optional Argument.
                Specifies the number of Teradata sessions to be opened for fastexport.
                Default value: None
                Types: int

            csv_file_name:
                Optional Argument.
                Specifies the name of CSV file to which data is to be exported.
                Types: Str

        RETURNS:
            str.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            base_query = "select * from my_table SAMPLE 200"
            target_csv = "Test.csv"
            dt_obj._generate_fastexport_query(base_query)
            dt_obj._generate_fastexport_query(base_query, require=True)
            dt_obj._generate_fastexport_query(base_query, require=True, open_sessions=5)
            dt_obj._generate_fastexport_query(base_query, require=True, csv_file_name=target_csv)
            dt_obj._generate_fastexport_query(base_query, require=True, open_sessions = 2,
                                              csv_file_name=target_csv)

        """
        fastexport_esc_func = ""
        open_session_esc_func = ""
        if require is not None:
            if require:
                # If require is set to True, we are using
                # 'teradata_require_fastexport' escape sequence as this will run
                # query using fastexport only if the given query is compatible with
                # fastexport else raises error.
                fastexport_esc_func = DriverEscapeFunctions.REQUIRE_FASTEXPORT.value
            else:
                # If require is False, we are using 'teradata_try_fastexport'
                # escape sequence as this will run query using fastexport if the
                # given query is compatible with fastexport else runs it as
                # regular query.
                fastexport_esc_func = DriverEscapeFunctions.TRY_FASTEXPORT.value

            if open_sessions is not None:
                open_session_esc_func = DriverEscapeFunctions.OPEN_SESSIONS.value.format(open_sessions)

        write_csv_escape_func = ""
        field_sep_esc_func = ""
        field_quote_esc_func = ""

        if csv_file_name:
            # The teradata_field_sep and teradata_field_quote escape functions have a
            # single-character string argument. The string argument must follow SQL literal
            # syntax. The string argument may be enclosed in single-quote (') characters or
            # double-quote (") characters.
            field_sep = "'{0}'".format(self.sep)
            if self.sep == "'":
                field_sep = "''''"
            elif self.sep == "\"":
                field_sep = "\"\"\"\""
            # To represent a single-quote character in a string enclosed in single-quote
            # characters, you must repeat the single-quote character.
            # {fn teradata_field_quote('''')}
            # To represent a double-quote character in a string enclosed in double-quote
            # characters, you must repeat the double-quote character.
            # {fn teradata_field_quote("""")}
            field_quote = "'{0}'".format(self.quotechar)
            if self.quotechar == "'":
                field_quote = "''''"
            elif self.quotechar == "\"":
                field_quote = "\"\"\"\""

            write_csv_escape_func = DriverEscapeFunctions.WRITE_TO_CSV.value.format(csv_file_name)
            field_sep_esc_func = DriverEscapeFunctions.FIELD_SEP.value.format(field_sep)
            field_quote_esc_func = DriverEscapeFunctions.FIELD_QUOTE.value.format(field_quote)

        query = "{0}{1}{2}{3}{4}{5}".format(fastexport_esc_func,
                                            open_session_esc_func,
                                            field_sep_esc_func,
                                            field_quote_esc_func,
                                            write_csv_escape_func,
                                            base_query)

        return query

    def _process_fastexport_errors_warnings(self, query):
        """
        DESCRIPTION:
            Function to process errors/warnings(if any) raised while executing
            the fastexport protocol.

        PARAMETERS:
            query:
                Required Argument.
                Specifies the query with fastexport escape sequences that is
                used to convert teradataml DataFrame to Pandas DataFrame.
                Type: str

        RETURNS:
            A tuple with two lists for errors, warnings each containing err/warn
            messages in string format.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            query = "{fn teradata_try_fastexport}select * from my_table SAMPLE
                    200"
            err, warn = dt_obj._process_fastexport_errors_warnings(query)
        """
        err = None
        warn = None
        conn = get_connection().connection
        # Create a cursor from connection object.
        cur = conn.cursor()
        # Get err/warn
        err = self._get_errors_warnings(cur, query,
                                        DriverEscapeFunctions.GET_ERRORS)
        warn = self._get_errors_warnings(cur, query,
                                         DriverEscapeFunctions.GET_WARNINGS)
        return err, warn

    # Functions specific to exporting table data in Vantage into pandas DataFrame.
    def _get_pandas_dataframe(self, **kwargs):
        """
        DESCRIPTION:
            Function that converts teradataml DataFrame to Pandas DataFrame
            using regular approach.

        PARAMETERS:
            kwargs:
                Specifies keyword arguments.

        RETURNS:
            Pandas DataFrame.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._get_pandas_dataframe()

        """
        # Get the final index column.
        final_index_column = self._get_pandas_df_index()
        # Get the base query.
        base_query = self._generate_to_pandas_base_query()
        # Generate pandas dataframe using base query.
        pandas_df = _execute_query_and_generate_pandas_df(base_query,
                                                          final_index_column,
                                                          **kwargs)
        return pandas_df

    def _fastexport_get_pandas_df(self, require=False, **kwargs):
        """
        DESCRIPTION:
            Internal function to convert teradataml DataFrame to Pandas
            DataFrame using FastExport protocol. This internal function can be
            directly used in to_pandas() and fastexport API's if either of
            the functions has to use fastexport.

        PARAMETERS:
            require:
                Optional Argument.
                Specifies whether fastexport protocol is required for data
                transfer.
                Default Value: False
                Types: bool

            kwargs:
                Specifies keyword arguments. Argument "open_sessions"
                can be passed as keyword arguments.
                * "open_sessions" specifies the number of Teradata sessions to
                be opened for fastexport.

        RETURNS:
            When "catch_errors_warnings" is set to True, the function returns
            a tuple containing:
            * Pandas DataFrame.
            * Errors, if any, thrown by fastexport in a list of strings.
            * Warnings, if any, thrown by fastexport in a list of strings.
            Only Pandas DataFrame otherwise.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._fastexport_get_pandas_df(require=False)

        """

        try:
            self._validate_df_index_column()
            final_index_col = self._get_pandas_df_index()
            self.df._DataFrame__execute_node_and_set_table_name(self.df._nodeid,
                                                                self.df._metaexpr)
            base_query = self._generate_to_pandas_base_query()

            # Get open_sessions argument.
            open_sessions = kwargs.pop("open_sessions", None)
            fastexport_query = self._generate_fastexport_query(base_query,
                                                               require=require,
                                                               open_sessions=open_sessions)
            pandas_df = _execute_query_and_generate_pandas_df(fastexport_query,
                                                              final_index_col,
                                                              **kwargs)
            err, warn = \
                self._process_fastexport_errors_warnings(fastexport_query)
            if self.catch_errors_warnings:
                return pandas_df, err, warn
            else:
                print("Errors: {0}".format(err))
                print("Warnings: {0}".format(warn))
                return pandas_df
        except TeradataMlException:
            raise

    # End of functions specific to exporting table data in Vantage into pandas DataFrame.

    # General functions to get warrnings and errors.
    def _get_errors_warnings(self, cur, insert_stmt, escape_function):
        """
        Internal function executes teradatasql provided escape functions
        to get the errors and warnings.

        PARAMETERS:
            cur:
                Required Argument.
                The cursor of connection type which will be used to execute query.
                Types: teradatasql cursor object

            insert_stmt:
                Required Argument.
                Statement to be executed along with escape method.
                Types: String

            escape_function:
                Required Argument.
                Type of escape method to be passed.
                Types: String

        RETURNS:
            A list containing error/warning information.

        RAISES:
            None

        EXAMPLES:
            dt_obj = _DataTransferUtils(df, table_name, types)
            dt_obj._get_errors_warnings(cur, insert_stmt, escape_function)
        """
        errorwarninglist = self._process_escape_functions(cur,
                                                          escape_function=escape_function,
                                                          insert_query=insert_stmt)

        from teradatasql import vernumber
        msg = []
        if errorwarninglist:
            if (errorwarninglist[0][0] != ""):
                msg = errorwarninglist[0][0].split('[Version ' + vernumber.sVersionNumber + ']')[1:]

        return [err_msg.split("\n")[0] for err_msg in msg]

    def _get_pandas_df_from_errors_warnings(self, err_or_warn_dict):
        """
        DESCRIPTION:
            Internal function creates Pandas dataframe.

        PARAMETERS:
            err_or_warn_dict:
                Required Argument.
                Specifies the error or warning dictionary.
                Types: Python dictionary

        RETURNS:
            Pandas Dataframe.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._get_pandas_df_from_errors_warnings(err_or_warn_dict)
        """
        # For fastload API, we check the 'batch_no' key is present in dictionary and
        # whether it has non-zero value or not.
        # For read_csv API, we check whether the length of 'error_message' key's
        # value is greater than 0 or not.
        if ('batch_no' in err_or_warn_dict and bool(err_or_warn_dict.get('batch_no'))) or \
                len(err_or_warn_dict['error_message']) != 0:
            return pd.DataFrame(err_or_warn_dict)

        return pd.DataFrame()

    def _create_error_warnings_table(self, pdf, msg_type, logon_seq_number, table_name=None):
        """
        DESCRIPTION:
            Internal function creates the errors and warnings table in Vantage.

        PARAMETERS:
            pdf:
                Required Argument.
                Specifies pandas dataframe containing errors and warnings.
                Types: Pandas DataFrame

            msg_type:
                Required Argument.
                Specifies the type of message.
                Possible Values : 'err', 'warn'
                Types: String

            logon_seq_number:
                Required Argument.
                Specifies logon sequence number of the session.
                Types: Integer

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            dt_obj = _DataTransferUtils(df, table_name, types)
            dt_obj._create_error_warnings_table(pdf, msg_type, logon_seq_number)
        """
        if not table_name:
            table_name = "td_fl_{0}_{1}_{2}".format(self.table_name, msg_type, logon_seq_number)
        copy_to_sql(pdf, table_name, schema_name=self.err_staging_db,
                    if_exists='replace')
        return "{}.{}".format(self.err_staging_db if self.err_staging_db
                              else _get_current_databasename(),
                              table_name)

    def _process_escape_functions(self, cur, escape_function, insert_query=None):
        """
        DESCRIPTION:
            Internal function executes the autocommit to manage the transactions.

        PARAMETERS:
            cur:
                Required Argument.
                The cursor of connection type which will be used to execute query.
                Types: teradatasql cursor object

            escape_function:
                Required Argument.
                Specifies the escape function to use.
                Permitted Values : 'autocommit_off', 'autocommit_on', 'logon_sequence_number'
                Types: String

            insert_query:
                Optional Argument.
                Specifies the insert query.
                Types: String

        RETURNS:
            If escape_function is 'logon_sequence_number' then returns
            a list containing logon sequence number.
            If escape_function is 'teradata_get_errors' then returns
            a list containing errors observed by FastLoad.
            If escape_function is 'teradata_get_warnings' then returns
            a list containing warnings observed by FastLoad.
            Otherwise returns None.

        RAISES:
            None

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._process_escape_functions(cur, escape_function)
        """
        # All escape functions follow same syntax hence, the query formation at the start.
        query = "{}{}".format(DriverEscapeFunctions.NATIVE_SQL.value, escape_function.value)

        # If escape function requires to be executed along with the query.
        if escape_function in [DriverEscapeFunctions.LOGON_SEQ_NUM,
                               DriverEscapeFunctions.GET_ERRORS,
                               DriverEscapeFunctions.GET_WARNINGS]:
            cur.execute(query + insert_query)
            return [row for row in cur.fetchall()]
        else:
            cur.execute(query)

    # End of general functions to get warnings and errors.

    # Functions specific to read_csv().
    def _form_insert_query(self, table, column_names=None):
        """
        DESCRIPTION:
            Internal function forms the INSERT query using escape function.

        PARAMETERS:
            table:
                Required Argument.
                Specifies the table name.
                Types: str

            column_names:
                Optional Argument.
                Specifies the list of column names.
                Types: list of Strings (str)

        RETURNS:
            str.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df, api_name='read_csv')
            ins_query = dt_obj._form_insert_query()
        """

        escape_funcs = ""

        # Get the fastload escape function.
        if self.use_fastload:
            escape_funcs = escape_funcs + DriverEscapeFunctions.REQUIRE_FASTLOAD.value

        # Get the escape function clause for open_sessions.
        if self.open_sessions is not None:
            escape_funcs = escape_funcs + DriverEscapeFunctions.OPEN_SESSIONS.value.format(self.open_sessions)

        # Create the list of values to be inserted.
        if self.api_name == "fastload":
            col_names = _get_pd_df_column_names(self.df)
            insert_values = ", ".join(['?' for i in range(len(col_names) + len(self.df.index.names)
                                                          if self.index is True else len(col_names))])

        # Get escape functions related to read_csv.
        if self.api_name == "read_csv":
            # Get the column names.
            if self.if_exists == 'append' and column_names is not None:
                col_names = column_names
            else:
                col_names, _ = _extract_column_info(self.df, self.types)

            # Get read_csv escape function.
            escape_funcs = escape_funcs + DriverEscapeFunctions.READ_CSV.value.format(self.df)
            insert_values = ", ".join(['?' for i in range(len(col_names))])

            # Create escape function for sep.
            field_sep = "'{0}'".format(self.sep)
            if self.sep == "'":
                field_sep = "''''"
            elif self.sep == "\"":
                field_sep = "\"\"\"\""
            escape_funcs = escape_funcs + DriverEscapeFunctions.FIELD_SEP.value.format(field_sep)

            # Create escape function for quotechar.
            field_quote = "'{0}'".format(self.quotechar)
            if self.quotechar == "'":
                field_quote = "''''"
            elif self.quotechar == "\"":
                field_quote = "\"\"\"\""
            escape_funcs = escape_funcs + DriverEscapeFunctions.FIELD_QUOTE.value.format(field_quote)

        # Create base insert query.
        base_insert_query = "INSERT INTO {0} VALUES ({1});".format(table, insert_values)

        # Get the escape function clauses for error table and DB related escape functions.
        # TODO: This condition will be optimized with ELE-6743.
        if self.api_name == "fastload" and self.save_errors and not self.err_tbl_name:
            escape_funcs = escape_funcs + DriverEscapeFunctions.ERR_TBL_MNG_FLAG.value.format("off")

        if self.err_tbl_1_suffix:
            escape_funcs = escape_funcs + DriverEscapeFunctions.ERR_TBL_1.value.format(self.err_tbl_1_suffix)

        if self.err_tbl_2_suffix:
            escape_funcs = escape_funcs + DriverEscapeFunctions.ERR_TBL_2.value.format(self.err_tbl_2_suffix)

        if self.err_staging_db:
            escape_funcs = escape_funcs + DriverEscapeFunctions.ERR_STAGING_DB.value.format(self.err_staging_db)

        # Generate final insert query by appending all escape functions.
        query = "{0}{1}".format(escape_funcs, base_insert_query)
        return query

    def _table_exists(self, con):
        """
        DESCRIPTION:
            Internal function validates whether table exists or not.

        PARAMETERS:
            con:
                Required argument.
                Specifies a SQLAlchemy connectable (engine/connection) object
                Types: Teradata connection object

        RETURNS:
            boolean.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            ins_query = dt_obj._table_exists()
        """
        return con.dialect.has_table(get_connection(), self.table_name, self.schema_name,
                                     table_only=True)

    def _get_fully_qualified_table_name(self, table_name=None, schema_name=None):
        """
        DESCRIPTION:
            Function returns schema qualified table name
            Such as:
                   "alice"."my_table" OR
                   "mldb"."my_table"

        PARAMETERS:
            table_name:
                Optional Argument.
                Specifies the table name.
                Types: str

            schema_name:
                Optional Argument.
                Specifies the schema name.
                Types: str

        RETURNS:
            str.

        RAISES:
            None

        EXAMPLES:
            dt_obj = _DataTransferUtils(df, table_name, types)
            dt_obj._get_fully_qualified_table_name()
        """
        table_name = table_name if table_name else self.table_name

        table = '"{}"'.format(table_name)
        if schema_name is not None:
            table = '"{}"."{}"'.format(schema_name, table_name)
        elif self.schema_name is not None:
            table = '"{}"."{}"'.format(self.schema_name, table_name)

        return table

    def _create_table(self, con, table_name=None, schema_name=None):
        """
        DESCRIPTION:
            Internal function creates table in the Vantage.

        PARAMETERS:
            con:
                Required Argument.
                A SQLAlchemy connectable (engine/connection) object
                Types: Teradata connection object

            table_name:
                Optional Argument.
                Specifies the table name.
                Types: str

            schema_name:
                Optional Argument.
                Specifies the schema name where table needs to be created.
                Types: str

        RETURNS:
            None.

        RAISES:
            None

        EXAMPLES:
            dt_obj = _DataTransferUtils(df, table_name, types)
            dt_obj._create_table(con)
        """
        table_name = table_name if table_name else self.table_name
        schema_name = schema_name if schema_name else self.schema_name
        table = _create_table_object(df=self.df, table_name=table_name, types=self.types, con=con,
                                     schema_name=schema_name, primary_index=self.primary_index,
                                     temporary=self.temporary, set_table=self.set_table, index=self.index,
                                     index_label=self.index_label)

        UtilFuncs._create_table_using_table_object(table)

    def _insert_from_csv_with_fastload(self, table_name=None, column_names=None):
        """
        DESCRIPTION:
            This insert function loads the data from csv file to Vantage table.

        PARAMETERS:
            table_name:
                Optional Argument.
                Specifies the table name.
                Types: str

            column_names:
                Optional Argument.
                Specifies the list column names.
                Types: list of Strings (str).

        RETURNS:
            A dict containing the following attributes:
                1. errors_dataframe: It is a Pandas DataFrame containing error messages
                   thrown by fastload. DataFrame is empty if there are no errors.
                2. warnings_dataframe: It is a Pandas DataFrame containing warning messages
                   thrown by fastload. DataFrame is empty if there are no warnings.
                3. errors_table: Name of the table containing errors. It is None, if
                   argument save_errors is False.
                4. warnings_table: Name of the table containing warnings. It is None, if
                   argument save_errors is False.

        RAISES:
            None

        EXAMPLES:
            dt_obj = _DataTransferUtils(df, table_name, types, api_name='read_csv')
            dt_obj._insert_from_csv()
        """
        conn = get_connection()
        conn1 = conn.connection
        cur = conn1.cursor()

        error_tablename = ""
        warn_tablename = ""

        try:
            # Quoted, schema-qualified table name.
            table = self._get_fully_qualified_table_name(table_name)

            # Form the INSERT query for read_csv.
            ins = self._form_insert_query(table, column_names=column_names)

            # Turn off autocommit before the Fastload insertion.
            self._process_escape_functions(cur, escape_function= \
                DriverEscapeFunctions.AUTOCOMMIT_OFF)

            # Initialize dict template for saving error/warning information.
            err_dict = {}
            warn_dict = {}
            err_dict['error_message'] = []
            warn_dict['error_message'] = []

            # Empty queryband buffer before SQL call.
            UtilFuncs._set_queryband()
            # Execute insert statement
            cur.execute(ins)

            # Get error and warning information
            err, _ = self._process_fastexport_errors_warnings(ins)
            if len(err) != 0:
                err_dict['error_message'].extend(err)

            # Get logon sequence number to be used for error/warning table names
            logon_seq_number = self._process_escape_functions(cur, escape_function= \
                DriverEscapeFunctions.LOGON_SEQ_NUM,
                                                              insert_query=ins)

            # Commit the rows
            conn1.commit()

            # Get error and warning information, if any.
            # Errors/Warnings like duplicate rows are added here.
            _, warn = self._process_fastexport_errors_warnings(ins)
            if len(warn) != 0:
                warn_dict['error_message'].extend(warn)

            # Get error and warning information for error and warning tables, persist
            # error and warning tables to Vantage if user has specified save_error as True
            # else show it as pandas dataframe on console.
            pd_err_df = self._get_pandas_df_from_errors_warnings(err_dict)
            if not pd_err_df.empty and self.save_errors:
                msg_type = "err"
                error_tablename = self._create_error_warnings_table(pd_err_df, msg_type, logon_seq_number[0][0])

            pd_warn_df = self._get_pandas_df_from_errors_warnings(warn_dict)
            if not pd_warn_df.empty and self.save_errors:
                msg_type = "warn"
                warn_tablename = self._create_error_warnings_table(pd_warn_df, msg_type, logon_seq_number[0][0])

            # These tables are created by FastloadCSV.
            fastloadcsv_err_tables = [table_name + "_ERR_1", table_name + "_ERR_2"]
            err_warn_dict = {"errors_dataframe": pd_err_df, "warnings_dataframe": pd_warn_df,
                             "errors_table": error_tablename, "warnings_table": warn_tablename,
                             "fastloadcsv_error_tables": fastloadcsv_err_tables}

            # If user don't want to persist the error tables,
            # drop the tables created by FastloadCSV.
            if not self.save_errors:
                for table in fastloadcsv_err_tables:
                    if conn.dialect.has_table(conn, table_name=table, schema=self.schema_name,
                                              table_only=True):
                        UtilFuncs._drop_table(self._get_fully_qualified_table_name(table))
                    err_warn_dict.update({"fastloadcsv_error_tables": []})
                return err_warn_dict

            return err_warn_dict

        except Exception:
            conn1.rollback()
            raise
        finally:
            # Turn on autocommit.
            self._process_escape_functions(cur, escape_function= \
                DriverEscapeFunctions.AUTOCOMMIT_ON)
            cur.close()

    def _get_result(self, result_dict=None):
        """
        DESCRIPTION:
            Internal function loads data from csv to table.
            And created the teradataml dataframe of the table.

        PARAMETERS:
            result_dict:
                Optional Argument.
                Specifies the dictionary containg values for error_dataframe,
                warning_dataframe, error_table, warning_table.
                Types: dict

        RETURNS:
            When "catch_errors_warnings" is set to True, then the
            function returns a tuple containing:
                a. Teradataml DataFrame.
                b. A dict containing the following attributes:
                    a. errors_dataframe: It is a Pandas DataFrame containing error messages
                       thrown by fastload. DataFrame is empty if there are no errors.
                    b. warnings_dataframe: It is a Pandas DataFrame containing warning messages
                       thrown by fastload. DataFrame is empty if there are no warnings.
                    d. errors_table: Name of the table containing errors. It is None, if
                       argument save_errors is False.
                    e. warnings_table: Name of the table containing warnings. It is None, if
                       argument save_errors is False.
            When "catch_errors_warnings" is False, then the function
            returns a Teradataml DataFrame.

        RAISES:
            None.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df, table_name, types)
            ins_query = dt_obj._get_result()
        """
        tdml_df = tdmldf.DataFrame(self._get_fully_qualified_table_name())

        if not self.use_fastload:
            return tdml_df

        if self.catch_errors_warnings:
            return tdml_df, result_dict
        return tdml_df

    def _get_dataframe_columns(self):
        """
        Internal function used to get dataframe columns name.

        PARAMETERS:
            None

        Returns
            list

        RAISES:
            None

        EXAMPLES:
            _get_dataframe_columns()
        """
        if isinstance(self.df, pd.DataFrame):
            return _get_pd_df_column_names(self.df)
        elif isinstance(self.df, tdmldf.DataFrame):
            return [col.name for col in self.df._metaexpr.c]

    def _get_sqlalc_table_columns(self):
        """
        Internal function to get column info if types is not None otherwise get
        the column info from existing table.
        If types is None and if_exists is append then it will first check for table
        existence, if table does not exists on system, it will raise an exception.

        PARAMETERS:
            None

        RETURNS:
            list

        RAISES:
            ValueError

        EXAMPLES:
            _get_sqlalc_table_columns()
        """
        table = None
        if self.types is None and self.if_exists == 'append':
            # Raise an exception when the table does not exists, if_exists='append'
            # and types=None.
            if not self._table_exists(get_connection()):
                err = "Table '{}' does not exists in the system and if_exists " \
                      "is set to 'append'.".format(self.table_name)
                _Validators._validate_argument_is_not_None(self.types, "types",
                                                           additional_error=err)

            table = UtilFuncs._get_sqlalchemy_table(self.table_name,
                                                    schema_name=self.schema_name)

        df_columns, _ = UtilFuncs._extract_table_object_column_info(table.c) \
            if table is not None else \
            _extract_column_info(self.df, types=self.types)

        return df_columns

    def _validate(self):
        """
        This is an internal function used to validate the api parameters.
        Dataframe, connection & related parameters are checked.
        Saving to Vantage is proceeded to only when validation returns True.

        PARAMETERS:
            None

        RETURNS:
            True, when all parameters are valid.

        RAISES:
            TeradataMlException, when parameter validation fails.

        EXAMPLES:
            dt_obj = _DataTransferUtils()
            dt_obj._validate()
        """
        awu = _Validators()
        awu_matrix = []

        # The arguments added to awu_martix are:
        # arg_name, arg, is_optional, acceptable types
        # The value for is_optional is set to False when the argument
        # a) is a required argument
        # b) is not allowed to be None, even if it is optional
        types_t = (dict)
        is_optional = True
        if self.api_name == 'read_csv':
            awu_matrix.append(['filepath', self.df, False, (str)])

            types_t = (OrderedDict)
            is_optional = False if self.if_exists in ['replace', 'fail'] else True
        else:
            # Validates the dataframe passed to copyto and fastload apis.
            # We are validating dataframe with separate function because
            # current implementation of __getTypeAsStr() always returns
            # 'teradataml DataFrame' if argument type.__name__ is DataFrame.
            _Validators._validate_dataframe(self.df)

        awu_matrix.append(['types', self.types, is_optional, types_t])
        awu_matrix.append(['table_name', self.table_name, False, (str), True])
        awu_matrix.append(['schema_name', self.schema_name, True, (str), True])
        awu_matrix.append(['index', self.index, False, (bool)])
        awu_matrix.append(['temporary', self.temporary, False, (bool)])
        awu_matrix.append(['if_exists', self.if_exists, False, (str),
                           True, ['APPEND', 'REPLACE', 'FAIL']])
        awu_matrix.append(['primary_index', self.primary_index, True, (str, list), True])
        awu_matrix.append(['set_table', self.set_table, False, (bool)])
        awu_matrix.append(['save_errors', self.save_errors, False, (bool)])
        awu_matrix.append(['sep', self.sep, False, (str)])
        awu_matrix.append(['quotechar', self.quotechar, True, (str)])
        awu_matrix.append(['catch_errors_warnings', self.catch_errors_warnings, False, (bool)])
        awu_matrix.append(['use_fastload', self.use_fastload, False, (bool)])
        awu_matrix.append(['open_sessions', self.open_sessions, True, (int), False])
        awu_matrix.append(['chunksize', self.chunksize, False, (int)])
        awu_matrix.append(['match_column_order', self.match_column_order, True, (bool)])
        if isinstance(self.df, pd.DataFrame):
            awu_matrix.append(['index_label', self.index_label, True, (str, list), True])

        # Validate types
        awu._validate_function_arguments(awu_matrix)

        # Validate if 'open_sessions' is a positive int.
        if self.open_sessions is not None:
            _Validators._validate_positive_int(self.open_sessions, "open_sessions")

        # Validate 'chunksize' is a positive int.
        _Validators._validate_positive_int(self.chunksize, "chunksize")

        # Get columns name
        if self.api_name == 'read_csv':
            df_columns = self._get_sqlalc_table_columns()
        else:
            df_columns = self._get_dataframe_columns()

        eng = get_context()
        current_user = eng.url.username

        allowed_schemas = df_utils._get_database_names(get_connection(), self.schema_name)
        allowed_schemas.append(current_user)

        if self.schema_name is not None and self.schema_name.lower() not in allowed_schemas:
            raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                           str(self.schema_name), 'schema_name',
                                                           'A valid database/schema name.'),
                                      MessageCodes.INVALID_ARG_VALUE)

        if isinstance(self.df, pd.DataFrame):
            if self.index:
                is_multi_index = isinstance(self.df.index, pd.MultiIndex)
                if self.index_label:
                    if hasattr(self.df.index, 'levels'):
                        index_levels = len(self.df.index.levels)
                    num_index = len(self.index_label)
                    is_index_list = isinstance(self.index_label, list)

                    if (is_multi_index and ((isinstance(self.index_label, str) and index_levels != 1) or
                                            (is_index_list and index_levels != len(self.index_label)))) or \
                            (not is_multi_index and is_index_list and
                             (is_index_list and num_index > 1)):
                        valid_arg_msg = 'String or list of Strings with the number of ' \
                                        'Strings matching the number of levels' \
                                        ' in the index'
                        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                                       self.index_label, 'index_label',
                                                                       valid_arg_msg),
                                                  MessageCodes.INVALID_ARG_VALUE)

                # When Pandas DF's used and Pandas Index is saved, get list of levels to add as columns
                index_names_to_add = _get_index_labels(self.df, self.index_label)[0]
                for label in index_names_to_add:
                    if label in df_columns:
                        raise TeradataMlException(Messages.get_message(MessageCodes.INDEX_ALREADY_EXISTS, label),
                                                  MessageCodes.INDEX_ALREADY_EXISTS)

                df_columns = df_columns + index_names_to_add

            if self.index_label is not None and self.index is False:
                raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_INDEX_LABEL),
                                          MessageCodes.INVALID_INDEX_LABEL)

        elif isinstance(self.df, tdmldf.DataFrame):
            # teradataml DataFrame's do not support saving pandas index/index_label
            if self.index_label is not None:
                raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                               str(self.index_label), 'index_label', 'None'),
                                          MessageCodes.INVALID_ARG_VALUE)

            if self.index is not False:
                raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                               str(self.index), 'index', 'False'),
                                          MessageCodes.INVALID_ARG_VALUE)

        # Check for number of columns
        if len(df_columns) > TeradataConstants.TABLE_COLUMN_LIMIT.value:
            raise TeradataMlException(Messages.get_message(MessageCodes.TD_MAX_COL_MESSAGE),
                                      MessageCodes.TD_MAX_COL_MESSAGE)

        # Check for existence of Primary Index Columns
        pindex = self.primary_index
        if self.primary_index is not None:
            if isinstance(self.primary_index, str):
                pindex = [self.primary_index]

            for column in pindex:
                if column not in df_columns:
                    raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_PRIMARY_INDEX),
                                              MessageCodes.INVALID_PRIMARY_INDEX)

        # Verify types argument is a dictionary, non-empty, and contains appropriate columns
        if self.types is not None:
            # Verify types argument is non-empty when specified
            if not (self.types):
                raise TeradataMlException(Messages.get_message(MessageCodes.ARG_EMPTY, 'types'),
                                          MessageCodes.ARG_EMPTY)

            # Check if all column names provided in types are valid DataFrame columns
            if any(key not in df_columns for key in self.types):
                # Only iterate entire types dictionary if an invalid column value passed
                for key in self.types:
                    if key not in df_columns:
                        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                                       str(key), 'types', ', '.join(df_columns)),
                                                  MessageCodes.INVALID_ARG_VALUE)

    def _check_table_exists(self, is_table_exists):
        """
        Internal function to raise an exception when table does not exists
        and if_exists is set to 'fail'.

        PARAMETERS:
            is_table_exists:
                Required Argument.
                Specifies whether table exists or not.
                Types: bool

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            _check_table_exists(True)
        """
        # Raise an exception when the table exists and if_exists = 'fail'
        if is_table_exists and self.if_exists.lower() == 'fail':
            raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_ALREADY_EXISTS, self.table_name),
                                      MessageCodes.TABLE_ALREADY_EXISTS)

    def _create_or_replace_table(self, con, table_exists):
        """
        Internal function to create the table if table does not exists on
        system. If table exists then drop the existing table and create
        new table.

        PARAMETERS:
            con:
                Required Argument.
                A SQLAlchemy connectable (engine/connection) object
                Types: Teradata connection object

            table_exists:
                Required Argument.
                Specifies whether table exists or not.
                Types: bool

        Returns:
            None

        RAISES:
            None

        EXAMPLES:
            _create_or_replace_table(con, True)
        """
        # If the table need to be replaced, let's drop the existing table first.
        if table_exists:
            UtilFuncs._drop_table(self._get_fully_qualified_table_name())

        # Create target table for FastLoad
        self._create_table(con)

    def _check_columns_compatibility(self, table_obj, cols):
        """
        Internal function checks the columns' compatibility with already
        existing table.

        PARAMETERS:
            table_obj:
                Required Argument.
                Specifies the table object.
                Types: sqlalchemy.sql.schema.Table

            cols:
                Required Argument.
                Specifies list of column names.
                Types: list

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            _check_columns_compatibility(table_obj, ['c1', 'c2'])
        """
        cols_compatible = _check_columns_insertion_compatible(table_obj.c, cols,
                                                              True)
        if not cols_compatible:
            raise TeradataMlException(Messages.get_message(MessageCodes.INSERTION_INCOMPATIBLE),
                                      MessageCodes.INSERTION_INCOMPATIBLE)

    def _create_staging_table_and_load_csv_data(self, column_info=None, primary_index=None):
        """
        Internal function to create the staging table and load the csv
        data into it.

        PARAMETERS:
            column_info:
                Required Argument.
                Specifies the data types for columns to be saved in Vantage.
                Keys of this dictionary should be the name of the columns and values should be
                teradatasqlalchemy.types.
                Types: dict (key should be the name of column,
                             value should be the data type of column)

            primary_index:
                Optional Argument.
                Specifies primary index.
                Default Value: None
                Types: list of Strings (str)

        RETURNS:
            dict

        RAISES:
            None

        EXAMPLES:
            _create_staging_table_and_load_csv_data(column_info={"id": INTEGER})
            _create_staging_table_and_load_csv_data(column_info={"id": INTEGER}, primary_index = ['id'])

        """
        stage_table_created = False
        try:
            # Generate the temporary table.
            stag_table_name = UtilFuncs._generate_temp_table_name(prefix="fl_staging",
                                                                  gc_on_quit=False,
                                                                  quote=False,
                                                                  table_type=TeradataConstants.TERADATA_TABLE)

            # If configure.temp_object_type="VT", _generate_temp_table_name() retruns the 
            # table name in fully qualified format. Because of this , test cases started 
            # failing with Blank name in quotation mark. Hence, extracted only the table name.  
            stag_table_name = UtilFuncs._extract_table_name(stag_table_name)

            # Information about uniqueness of primary index and
            # SET/MULTISET property of existing table is not available,
            # so over-assuming to be False.
            unique = False
            set_table = False

            if not primary_index:
                primary_index = None

            # Create staging table where column info deduced from the existing table.
            _create_table(table_name=stag_table_name, columns=column_info,
                          primary_index=primary_index, unique=unique,
                          temporary=False, schema_name=self.schema_name,
                          set_table=set_table)
            stage_table_created = True
            column_names = list(column_info.keys())

            # Load the data from CSV to staging table.
            rc_dict = self._insert_from_csv_with_fastload(table_name=stag_table_name,
                                                          column_names=column_names)

            # Insert all rows from staging table to already existing table.
            df_utils._insert_all_from_table(self.table_name,
                                            stag_table_name,
                                            column_names,
                                            to_schema_name=self.schema_name,
                                            from_schema_name=self.schema_name)

            return rc_dict
        finally:
            # Drop the staging table.
            if stage_table_created:
                UtilFuncs._drop_table(self._get_fully_qualified_table_name(stag_table_name))

    #
    # These functions are specific to read_csv() without using FastloadCSV.
    #
    def _insert_from_csv_without_fastload(self, table_name=None, column_names=None):
        """
        Internal function to read the csv file and load the data into
        a table in Vantage.

        PARAMETERS:
            table_name:
                Optional Argument.
                Specifies the table name to load the data into.
                Types: String

            column_names:
                Optional Argument.
                Specifies the list of column names.
                Types: list of Strings (str)

        RETURNS:
              None

        RAISES:
            None

        EXAMPLES:
            _insert_from_csv_without_fastload(con, "my_table", [VARCHAR, DATE])

        """
        # Form the INSERT query.
        insert_stmt = self._form_insert_query(table=table_name,
                                              column_names=column_names)

        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()
        try:
            conn = get_connection().connection
            cur = conn.cursor()

            # Execute INSERT query.
            cur.execute(insert_stmt)
        except Exception:
            raise

    def _check_index_compatibility(self, primary_index_1, primary_index_2):
        """
        Internal function to check the compatibility of user provided primary index
        with primary index of already existing table.

        PARAMETERS:
            primary_index_1:
                Required Argument.
                Specifies the primary index columns of existing table.
                Types: list of Strings (str)

            primary_index_2:
                Required Argument.
                Specifies the primary index columns provided by user.
                Types: str OR list of Strings (str)

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            _check_index_compatibility(['c1'], ['c1', 'c2'])
            _check_index_compatibility(['c1'], 'c1')
        """
        if isinstance(primary_index_2, str):
            primary_index_2 = [primary_index_2]

        if not (sorted(primary_index_1) == (sorted(primary_index_2))):
            raise TeradataMlException("Unable to perform insertion to existing table; Indexes do not match.",
                                      MessageCodes.INSERTION_INCOMPATIBLE)

    def _process_pti_load_csv_data(self, con):
        """
        Function processes the CSV data so that it can be loaded in a PTI table.
        To do so, it first creates a staging table and loads the data into same
        and the creates/loads into the PTI table using copy_to_sql().

        PARAMETERS:
            con:
                Required Argument.
                Specifies a SQLAlchemy connectable (engine/connection) object.
                Types: sqlalchemy.engine.base.Engine

        RETURNS:
            If catch_errors_warnings is set to True returns dict, otherwise None.

        RAISES:
            ValueError

        EXAMPLES:
            _process_pti_load_csv_data(con)

        """
        stag_table_name = ""
        try:
            # Types argument is required while appending the PTI table.
            if self._table_exists(con) and self.if_exists == "append" and self.types is None:
                _Validators._validate_argument_is_not_None(self.types, "types")

            # Generate the staging table name.
            stag_table_name = UtilFuncs._generate_temp_table_name(prefix="rc_pti_staging",
                                                                  gc_on_quit=False,
                                                                  quote=False,
                                                                  table_type=TeradataConstants.TERADATA_TABLE)

            # If configure.temp_object_type="VT", _generate_temp_table_name() retruns the 
            # table name in fully qualified format. Because of this , test cases started 
            # failing with Blank name in quotation mark. Hence, extracted only the table name.  
            stag_table_name = UtilFuncs._extract_table_name(stag_table_name)

            # Get the teradataml dataframe from staging table using read_csv()
            read_csv_output = read_csv(filepath=self.df, table_name=stag_table_name,
                                       types=self.types, sep=self.sep,
                                       quotechar=self.quotechar,
                                       schema_name=self.schema_name,
                                       save_errors=self.save_errors,
                                       catch_errors_warnings=self.catch_errors_warnings,
                                       use_fastload=self.use_fastload)

            rc_dict = None
            if self.catch_errors_warnings:
                stage_table_tdml_df, rc_dict = read_csv_output
            else:
                stage_table_tdml_df = read_csv_output

            # To create the PTI table use copy_to_sql().
            copy_to_sql(df=stage_table_tdml_df, table_name=self.table_name,
                        schema_name=self.schema_name, if_exists=self.if_exists,
                        primary_index=self.primary_index,
                        temporary=self.temporary,
                        primary_time_index_name=self.primary_time_index_name,
                        timecode_column=self.timecode_column,
                        timebucket_duration=self.timebucket_duration,
                        timezero_date=self.timezero_date,
                        columns_list=self.columns_list,
                        sequence_column=self.sequence_column,
                        seq_max=self.seq_max, set_table=self.set_table)

            return rc_dict
        finally:
            if stag_table_name:
                UtilFuncs._drop_table(self._get_fully_qualified_table_name(stag_table_name))

    # End of functions specific to read_csv().

    # Functions specific to exporting Vantage table data into CSV
    # which can be done with teradatasql driver escape functions with or without
    # fastexport protocol.
    def _get_csv(self, require_fastexport=True, csv_file_name=None, **kwargs):
        """
        DESCRIPTION:
            Internal function to export the data present in teradataml DataFrame into a CSV file
            using teradatasql driver's escape functions meant for writing to CSV. This can be done with or
            without Fastexport protocol.

        PARAMETERS:
            require_fastexport:
                Optional Argument.
                Specifies whether fastexport protocol is required for data
                transfer.
                Default Value: True
                Types: boolean

            csv_file_name:
                Required Argument.
                Specifies the name of CSV file to which data is to be exported.
                Default Value: None
                Types: Str

            kwargs:
                Specifies keyword arguments. Argument "open_sessions"
                can be passed as keyword arguments.
                * "open_sessions" specifies the number of Teradata sessions to
                be opened for fastexport.

        RETURNS:
            When "catch_errors_warnings" is set to True, the function returns
            a tuple containing:
                * Errors, if any, thrown by fastexport in a list of strings.
                * Warnings, if any, thrown by fastexport in a list of strings.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            dt_obj = _DataTransferUtils(df)
            dt_obj._get_csv(require_fastexport = True, csv_file_name = "Test.csv")
            dt_obj._get_csv(csv_file_name = "Test.csv")
            dt_obj._get_csv(csv_file_name = "Test.csv", open_sessions = 2)

        """
        try:
            base_query = self._generate_to_pandas_base_query()
            base_query = base_query.lstrip()
            # Get open_sessions argument.
            open_sessions = kwargs.pop("open_sessions", None)
            if not require_fastexport and open_sessions is not None:
                raise TeradataMlException("'{0}' can only be used when '{1}' is set to True." \
                                          .format("open_sessions", "fastexport or require"),
                                          MessageCodes.DEPENDENT_ARGUMENT)

            csv_export_query = self._generate_fastexport_query(base_query,
                                                               require=require_fastexport,
                                                               open_sessions=open_sessions,
                                                               csv_file_name=csv_file_name)

            UtilFuncs._execute_query(csv_export_query)
            err, warn = \
                self._process_fastexport_errors_warnings(csv_export_query)

            print('\nData is successfully exported into {}'.format(csv_file_name))
            if self.catch_errors_warnings:
                return err, warn
        except TeradataMlException:
            raise
