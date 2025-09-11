#!/usr/bin/python
# ##################################################################
#
# Copyright 2020 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Trupti Purohit (trupti.purohit@teradata.com)
# Secondary Owner: Gouri Patwardhan (gouri.patwardhan@teradata.com)
#
# Function Version: 1.0
#
# Description: Base class for Teradata's Table Operators
# ##################################################################

import os
import time
import uuid
from math import floor
import warnings
import subprocess
from pathlib import Path
import teradataml.dataframe as tdmldf
from teradataml.common.constants import OutputStyle, TeradataConstants
from teradataml.common.constants import TableOperatorConstants
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.wrapper_utils import AnalyticsWrapperUtils
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.options.configure import configure
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators
from teradatasqlalchemy import (BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT, NUMBER)
from teradatasqlalchemy import (TIMESTAMP, DATE, TIME)
from teradatasqlalchemy import (CHAR, VARCHAR, CLOB)
from teradatasqlalchemy import (BYTE, VARBYTE, BLOB)
from teradatasqlalchemy import (PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP)
from teradatasqlalchemy import (INTERVAL_YEAR, INTERVAL_YEAR_TO_MONTH, INTERVAL_MONTH, INTERVAL_DAY,
                                INTERVAL_DAY_TO_HOUR, INTERVAL_DAY_TO_MINUTE, INTERVAL_DAY_TO_SECOND,
                                INTERVAL_HOUR, INTERVAL_HOUR_TO_MINUTE, INTERVAL_HOUR_TO_SECOND,
                                INTERVAL_MINUTE, INTERVAL_MINUTE_TO_SECOND, INTERVAL_SECOND)
from teradataml.context.context import _get_current_databasename, get_context, get_connection
from io import StringIO


class TableOperator:

    def __init__(self,
                 data=None,
                 script_name=None,
                 files_local_path=None,
                 delimiter="\t",
                 returns=None,
                 quotechar=None,
                 data_partition_column=None,
                 data_hash_column=None,
                 data_order_column=None,
                 is_local_order=False,
                 sort_ascending=True,
                 nulls_first=True):
        """
        DESCRIPTION:
            Table Operators are a type of User-Defined Function, only available when connected to a
            Vantage.

        PARAMETERS:
            data:
                Optional Argument.
                Specifies a teradataml DataFrame containing the input data for the script.

            script_name:
                Required Argument.
                Specifies the name of the user script.
                Types: str

            files_local_path:
                Required Argument.
                Specifies the absolute local path where the user script and all supporting files
                like model files, input data file reside.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns.
                The delimiter is a single character chosen from the set of punctuation characters.
                Types: str

            returns:
                Required Argument.
                Specifies the output column definition.
                Types: Dictionary specifying column name to teradatasqlalchemy type mapping.
                Default: None

            data_hash_column:
                Optional Argument.
                Specifies the column to be used for hashing.
                The rows in the data are redistributed to AMPs based on the hash value of the
                column specified. The user-installed script file then runs once on each AMP.
                If there is no data_hash_column, then the entire result set,
                delivered by the function, constitutes a single group or partition.
                Types: str
                Note:
                    "data_hash_column" can not be specified along with "data_partition_column",
                    "is_local_order" and "data_order_column".

            data_partition_column:
                Optional Argument.
                Specifies Partition By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for partition.
                Default Value: ANY
                Types: str OR list of Strings (str)
                Notes:
                    1) "data_partition_column" can not be specified along with "data_hash_column".
                    2) "data_partition_column" can not be specified along with "is_local_order = True".

            is_local_order:
                Optional Argument.
                Specifies a boolean value to determine whether the input data is to be ordered locally
                or not. 'sort_ascending' specifies the order in which the values in a group, or partition,
                are sorted. This argument is ignored, if data_order_column is None.
                When set to 'True', qualified rows are ordered locally in preparation to be input
                to the function.
                Default Value: False
                Types: bool
                Note:
                    "is_local_order" can not be specified along with "data_hash_column".
                    When "is_local_order" is set to 'True', "data_order_column" should be specified,
                    and the columns specified in "data_order_column" are used for local ordering.

            data_order_column:
                Optional Argument.
                Specifies Order By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for ordering.
                This argument is used with in both cases: "is_local_order = True"
                and "is_local_order = False".
                Types: str OR list of Strings (str)
                Note:
                    "data_order_column" can not be specified along with "data_hash_column".

            sort_ascending:
                Optional Argument.
                Specifies a boolean value to determine if the input data is to be sorted on
                the data_order_column column in ascending or descending order.
                When this is set to 'True' data is sorted in ascending order,
                otherwise data is sorted in descending order.
                This argument is ignored, if data_order_column is None.
                Default Value: True
                Types: bool

            nulls_first:
                Optional Argument.
                Specifies a boolean value to determine whether NULLS from input data are listed
                first or last during ordering.
                When this is set to 'True' NULLS are listed first, otherwise NULLS are listed last.
                This argument is ignored, if data_order_column is None.
                Default Value: True
                Types: bool

        RETURNS:
             An instance of TableOperator class.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Apply class extends this base class.
            apply_obj = Apply(data=barrierdf,
                              script_name='mapper.py',
                              files_local_path= '/root/data/scripts/',
                              apply_command='python3 mapper.py',
                              data_order_column="Id",
                              is_local_order=False,
                              nulls_first=False,
                              sort_ascending=False,
                              env_name = "test_env",
                              returns={"word": VARCHAR(15), "count_input": VARCHAR(2)},
                              style='csv',
                              delimiter=',')
        """
        self.result = None
        self._tblop_query = None
        self.data = data
        self.script_name = script_name
        self.files_local_path = files_local_path
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.returns = returns
        self.data_partition_column = data_partition_column
        self.data_hash_column = data_hash_column
        self.data_order_column = data_order_column
        self.is_local_order = is_local_order
        self.sort_ascending = sort_ascending
        self.nulls_first = nulls_first

        # Datatypes supported in returns clause of a table operator.
        self._supported_returns_datatypes = (BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT, NUMBER,
                             TIMESTAMP, DATE, TIME, CHAR, VARCHAR, CLOB, BYTE, VARBYTE,
                             BLOB, PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP, INTERVAL_YEAR,
                             INTERVAL_YEAR_TO_MONTH, INTERVAL_MONTH, INTERVAL_DAY, INTERVAL_DAY_TO_HOUR,
                             INTERVAL_DAY_TO_MINUTE, INTERVAL_DAY_TO_SECOND, INTERVAL_HOUR,
                             INTERVAL_HOUR_TO_MINUTE, INTERVAL_HOUR_TO_SECOND, INTERVAL_MINUTE,
                             INTERVAL_MINUTE_TO_SECOND, INTERVAL_SECOND
                             )

        # Create AnalyticsWrapperUtils instance which contains validation functions.
        # This is required for is_default_or_not check.
        # Rest all validation is done using _Validators.
        self.__awu = AnalyticsWrapperUtils()

        self.awu_matrix = []
        self.awu_matrix.append(["data", self.data, True, (tdmldf.dataframe.DataFrame)])
        self.awu_matrix.append(["data_partition_column", self.data_partition_column, True, (str, list), True])
        self.awu_matrix.append(["data_hash_column", self.data_hash_column, True, (str, list), True])
        self.awu_matrix.append(["data_order_column", self.data_order_column, True, (str, list), True])
        self.awu_matrix.append(["is_local_order", self.is_local_order, True, (bool)])
        self.awu_matrix.append(["sort_ascending", self.sort_ascending, True, (bool)])
        self.awu_matrix.append(["nulls_first", self.nulls_first, True, (bool)])
        self.awu_matrix.append(["script_name", self.script_name, True, (str), True])
        self.awu_matrix.append(["files_local_path", self.files_local_path, True, (str), True])
        self.awu_matrix.append(["delimiter", self.delimiter, True, (str), False])
        self.awu_matrix.append(["quotechar", self.quotechar, True, (str), False])

        # Perform the function validations.
        self._validate()

    def _validate(self, for_data_args=False):
        """
        Function to validate Table Operator Function arguments, which verifies missing
        arguments, input argument and table types. Also processes the
        argument values.
        @param: for_data_args: Specifies whether the validation is for only arguments related to data or not.
                               When set to True, validation is only for data arguments. Otherwise, validation
                               is for all arguments. By default, system validates all the arguments.
        """

        if not for_data_args:
            # Make sure that a non-NULL value has been supplied for all mandatory arguments
            _Validators._validate_missing_required_arguments(self.awu_matrix)

            # Validate argument types
            _Validators._validate_function_arguments(self.awu_matrix,
                                                     skip_empty_check={"quotechar": ["\n", "\t"],
                                                                       "delimiter": ["\n"]})

        if self.data is not None:
            # Hash and order by can be used together as long as is_local_order = True.
            if all([self.data_hash_column,
                    self.data_order_column]) and not self.is_local_order:
                raise TeradataMlException(
                    Messages.get_message(MessageCodes.CANNOT_USE_TOGETHER_WITH,
                                         "data_hash_column' and 'data_order_column",
                                         "is_local_order=False"),
                    MessageCodes.CANNOT_USE_TOGETHER_WITH)

            # Either hash or partition can be used.
            if all([self.data_hash_column, self.data_partition_column]):
                raise TeradataMlException(Messages.get_message(MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT,
                                                               "data_hash_column", "data_partition_column"),
                                          MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)

            # Either local order by or partition by can be used.
            if all([self.is_local_order, self.data_partition_column]):
                raise TeradataMlException(Messages.get_message(MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT,
                                                               "is_local_order=True",
                                                               "data_partition_column"),
                                          MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)

            # local order by requires column name.
            if self.is_local_order and self.data_order_column is None:
                raise TeradataMlException(Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING,
                                                               "data_order_column",
                                                               "is_local_order=True"),
                                          MessageCodes.DEPENDENT_ARG_MISSING)

            if self.__awu._is_default_or_not(self.data_partition_column, "ANY"):
                _Validators._validate_dataframe_has_argument_columns(self.data_partition_column, "data_partition_column",
                                                                    self.data, "data", True)

            _Validators._validate_dataframe_has_argument_columns(self.data_order_column, "data_order_column",
                                                                    self.data, "data", False)

            _Validators._validate_dataframe_has_argument_columns(self.data_hash_column, "data_hash_column",
                                                                    self.data, "data", False)

        if not for_data_args:
            # Check for length of the arguments "delimiter" and "quotechar".
            if self.delimiter is not None:
                _Validators._validate_str_arg_length('delimiter', self.delimiter, 'EQ', 1)

            if self.quotechar is not None:
                _Validators._validate_str_arg_length('quotechar', self.quotechar, 'EQ', 1)

            # The arguments 'quotechar' and 'delimiter' cannot take newline character.
            if self.delimiter == '\n':
                raise TeradataMlException(Messages.get_message(MessageCodes.NOT_ALLOWED_VALUES,
                                                               "\n", "delimiter"),
                                          MessageCodes.NOT_ALLOWED_VALUES)
            if self.quotechar == '\n':
                raise TeradataMlException(Messages.get_message(MessageCodes.NOT_ALLOWED_VALUES,
                                                               "\n", "quotechar"),
                                          MessageCodes.NOT_ALLOWED_VALUES)

            # The arguments 'quotechar' and 'delimiter' cannot have the same value.
            if self.delimiter == self.quotechar:
                raise TeradataMlException(Messages.get_message(MessageCodes.ARGUMENT_VALUE_SAME,
                                                               "delimiter", "quotechar"),
                                          MessageCodes.ARGUMENT_VALUE_SAME)

    def set_data(self,
                 data,
                 data_partition_column=None,
                 data_hash_column=None,
                 data_order_column=None,
                 is_local_order=False,
                 sort_ascending=True,
                 nulls_first=True):
        """
        DESCRIPTION:
            Function enables user to set data and data related arguments without having to
            re-create Script object.

        PARAMETERS:
            data:
                Required Argument.
                Specifies a teradataml DataFrame containing the input data for the script.

            data_hash_column:
                Optional Argument.
                Specifies the column to be used for hashing.
                The rows in the data are redistributed to AMPs based on the
                hash value of the column specified.
                The user installed script then runs once on each AMP.
                If there is no data_partition_column, then the entire result set delivered
                by the function, constitutes a single group or partition.
                Types: str
                Note:
                    "data_hash_column" can not be specified along with
                    "data_partition_column", "is_local_order" and "data_order_column".

            data_partition_column:
                Optional Argument.
                Specifies Partition By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for partition.
                Default Value: ANY
                Types: str OR list of Strings (str)
                Note:
                    1) "data_partition_column" can not be specified along with
                       "data_hash_column".
                    2) "data_partition_column" can not be specified along with
                       "is_local_order = True".

            is_local_order:
                Optional Argument.
                Specifies a boolean value to determine whether the input data is to be
                ordered locally or not. Order by specifies the order in which the
                values in a group or partition are sorted.  Local Order By specifies
                orders qualified rows on each AMP in preparation to be input to a table
                function. This argument is ignored, if "data_order_column" is None. When
                set to True, data is ordered locally.
                Default Value: False
                Types: bool
                Note:
                    1) "is_local_order" can not be specified along with
                       "data_hash_column".
                    2) When "is_local_order" is set to True, "data_order_column" should be
                       specified, and the columns specified in "data_order_column" are
                       used for local ordering.

            data_order_column:
                Optional Argument.
                Specifies Order By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for ordering.
                This argument is used in both cases:
                "is_local_order = True" and "is_local_order = False".
                Types: str OR list of Strings (str)
                Note:
                    "data_order_column" can not be specified along with
                    "data_hash_column".

            sort_ascending:
                Optional Argument.
                Specifies a boolean value to determine if the result set is to be sorted
                on the column specified in "data_order_column", in ascending or descending
                order.
                The sorting is ascending when this argument is set to True, and descending
                when set to False.
                This argument is ignored, if "data_order_column" is None.
                Default Value: True
                Types: bool

            nulls_first:
                Optional Argument.
                Specifies a boolean value to determine whether NULLS are listed first or
                last during ordering.
                This argument is ignored, if "data_order_column" is None.
                NULLS are listed first when this argument is set to True, and
                last when set to False.
                Default Value: True
                Types: bool

        RETURNS:
            None.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> self.set_data(df)
        """

        awu_matrix_setter = []
        awu_matrix_setter.append(["data", data, True, (tdmldf.dataframe.DataFrame)])
        awu_matrix_setter.append(["data_partition_column", data_partition_column,
                                  True, (str, list), True])
        awu_matrix_setter.append(["data_hash_column", data_hash_column, True,
                                       (str, list), True])
        awu_matrix_setter.append(["data_order_column", data_order_column, True,
                                  (str, list), True])
        awu_matrix_setter.append(["is_local_order", is_local_order, True, (bool)])
        awu_matrix_setter.append(["sort_ascending", sort_ascending, True, (bool)])
        awu_matrix_setter.append(["nulls_first", nulls_first, True, (bool)])

        # Perform the function validations
        _Validators._validate_missing_required_arguments([["data", data, False,
                                                           (tdmldf.dataframe.DataFrame)]])
        _Validators._validate_function_arguments(awu_matrix_setter)

        self.data = data
        self.data_partition_column = data_partition_column
        self.data_hash_column = data_hash_column
        self.data_order_column = data_order_column
        self.is_local_order = is_local_order
        self.sort_ascending = sort_ascending
        self.nulls_first = nulls_first

    def _execute(self, output_style='VIEW'):
        """
        Function to execute Table Operator queries.
        Create DataFrames for the required Table Operator output.
        """
        table_type = TeradataConstants.TERADATA_VIEW
        if output_style == OutputStyle.OUTPUT_TABLE.value:
            table_type = TeradataConstants.TERADATA_TABLE

        # Generate STDOUT table name and add it to the output table list.
        tblop_stdout_temp_tablename = UtilFuncs._generate_temp_table_name(prefix="td_tblop_out_",
                                                                          use_default_database=True, gc_on_quit=True,
                                                                          quote=False,
                                                                          table_type=table_type
                                                                          )

        try:
            if configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE:
                UtilFuncs._create_table(tblop_stdout_temp_tablename, self._tblop_query, volatile=True)
            elif output_style == OutputStyle.OUTPUT_TABLE.value:
                UtilFuncs._create_table(tblop_stdout_temp_tablename, self._tblop_query)
            else:
                UtilFuncs._create_view(tblop_stdout_temp_tablename, self._tblop_query)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_EXEC_SQL_FAILED, str(emsg)),
                                      MessageCodes.TDMLDF_EXEC_SQL_FAILED)


        self.result = self.__awu._create_data_set_object(
            df_input=UtilFuncs._extract_table_name(tblop_stdout_temp_tablename), source_type="table",
            database_name=UtilFuncs._extract_db_name(tblop_stdout_temp_tablename))

        return self.result

    def _returns_clause_validation(self):
        """
        DESCRIPTION:
            Function validates 'returns' clause for a table operator query.

        PARAMETERS:
            None.

        RETURNS:
            None

        RAISES:
            Error if argument is not of valid datatype.

        EXAMPLES:
            self._returns_clause_validation()
        """
        # Validate keys and datatypes in returns.
        if self.returns is not None:
            awu_matrix_returns = []
            for key in self.returns.keys():
                awu_matrix_returns.append(["keys in returns", key, False, (str), True])
                awu_matrix_returns.append(["values in returns", self.returns[key], False, self._supported_returns_datatypes])
            _Validators._validate_function_arguments(awu_matrix_returns)


    def test_script(self, supporting_files=None, input_data_file=None, script_args="",
                    exec_mode='local', **kwargs):
        """
        DESCRIPTION:
            Function enables user to run script in docker container environment outside
            Vantage.
            Input data for user script is read from file.

        PARAMETERS:
            supporting_files:
                Optional Argument
                Specifies a file or list of supporting files like model files to be
                copied to the container.
                Types: string or list of str

            input_data_file:
                Required Argument.
                Specifies the name of the input data file.
                It should have a path relative to the location specified in
                "files_local_path" argument.
                If set to None, read data from AMP, else from file passed in the argument
                'input_data_file'.
                File should have at least permissions of mode 644.
                Types: str

            script_args:
                Optional Argument.
                Specifies command line arguments required by the user script.
                Types: str

            exec_mode:
                Optional Argument.
                Specifies the mode in which user wants to test the script.
                If set to 'local', the user script will run locally on user's system.
                Permitted Values: 'local'
                Default Value: 'local'
                Types: str

            kwargs:
                Optional Argument.
                Specifies the keyword arguments required for testing.
                Keys can be:
                    data_row_limit:
                        Optional Argument. Ignored when data is read from file.
                        Specifies the number of rows to be taken from all amps when
                        reading from a table or view on Vantage.
                        Default Value: 1000
                        Types: int

                    password:
                        Optional Argument. Required when reading from database.
                        Specifies the password to connect to vantage where the data
                        resides.
                        Types: str

                    data_file_delimiter:
                        Optional Argument.
                        Specifies the delimiter used in the input data file. This
                        argument can be specified when data is read from file.
                        Default Value: '\t'
                        Types: str

                    data_file_header:
                        Optional Argument.
                        Specifies whether the input data file contains header. This
                        argument can be specified when data is read from file.
                        Default Value: True
                        Types: bool

                    data_file_quote_char:
                        Optional Argument.
                        Specifies the quotechar used in the input data file.
                        This argument can be specified when data is read from file.
                        Default Value: '"'

                    logmech:
                        Optional Argument.
                        Specifies the type of logon mechanism to establish a connection to
                        Teradata Vantage.
                        Permitted Values: 'TD2', 'TDNEGO', 'LDAP', 'KRB5' & 'JWT'.
                            TD2:
                                The Teradata 2 (TD2) mechanism provides authentication
                                using a Vantage username and password. This is the default
                                logon mechanism using which the connection is established
                                to Vantage.

                            TDNEGO:
                                A security mechanism that automatically determines the
                                actual mechanism required, based on policy, without user's
                                involvement. The actual mechanism is determined by the
                                TDGSS server configuration and by the security policy's
                                mechanism restrictions.

                            LDAP:
                                A directory-based user logon to Vantage with a directory
                                username and password and is authenticated by the directory.

                            KRB5 (Kerberos):
                                A directory-based user logon to Vantage with a domain
                                username and password and is authenticated by
                                Kerberos (KRB5 mechanism).
                                Note:
                                    User must have a valid ticket-granting ticket in
                                    order to use this logon mechanism.

                            JWT:
                                The JSON Web Token (JWT) authentication mechanism enables
                                single sign-on (SSO) to the Vantage after the user
                                successfully authenticates to Teradata UDA User Service.
                                Note:
                                    User must use logdata parameter when using 'JWT' as
                                    the logon mechanism.
                        Default Value: TD2
                        Types: str

                        Note:
                            teradataml expects the client environments are already setup with appropriate
                            security mechanisms and are in working conditions.
                            For more information please refer Teradata Vantage™ - Advanced SQL Engine
                            Security Administration at https://www.info.teradata.com/

                    logdata:
                        Optional Argument.
                        Specifies parameters to the LOGMECH command beyond those needed by
                        the logon mechanism, such as user ID, password and tokens
                        (in case of JWT) to successfully authenticate the user.
                        Types: str

                Types: dict

        RETURNS:
            Output from user script.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Assumption - sto is Script() object. Please refer to help(Script)
            # for creating Script object.

            # Run user script in local mode with input from table.
            >>> sto.test_script(data_row_limit=300, password='alice', exec_mode='local')

            ############ STDOUT Output ############
                    word  count_input
            0          1            1
            1        Old            1
            2  Macdonald            1
            3        Had            1
            4          A            1
            5       Farm            1

            # Run user script in local mode with logmech as 'TD2'.
            >>> sto.test_script(script_args="4 5 10 6 480", password="alice", logmech="TD2")

            # Run user script in local mode with logmech as 'TDNEGO'.
            >>> sto.test_script(script_args="4 5 10 6 480", password="alice", logmech="TDNEGO")

            # Run user script in local mode with logmech as 'LDAP'.
            >>> sto.test_script(script_args="4 5 10 6 480", password="alice", logmech="LDAP")

            # Run user script in local mode with logmech as 'KRB5'.
            >>> sto.test_script(script_args="4 5 10 6 480", password="alice", logmech="KRB5")

            # Run user script in local mode with logmech as 'JWT'.
            >>> sto.test_script(script_args="4 5 10 6 480", password="alice",
                                logmech='JWT', logdata='token=eyJpc...h8dA')

        """
        logmech_valid_values = ['TD2', 'TDNEGO', 'LDAP', 'KRB5', 'JWT']

        awu_matrix_test = []
        awu_matrix_test.append((["supporting_files", supporting_files, True,
                                 (str, list), True]))
        awu_matrix_test.append((["input_data_file", input_data_file, True, (str), True]))
        awu_matrix_test.append((["script_args", script_args, True, (str), False]))
        awu_matrix_test.append((["exec_mode", exec_mode, True, (str), True,
                                 [TableOperatorConstants.LOCAL_EXEC.value]]))

        data_row_limit = kwargs.pop("data_row_limit", 1000)
        awu_matrix_test.append((["data_row_limit", data_row_limit, True, (int), True]))

        data_file_delimiter = kwargs.pop("data_file_delimiter", '\t')
        awu_matrix_test.append((["data_file_delimiter", data_file_delimiter, True,
                                 (str), False]))

        data_file_quote_char = kwargs.pop("data_file_quote_char", '"')
        awu_matrix_test.append((["data_file_quote_char", data_file_quote_char, True,
                                 (str), False]))

        data_file_header = kwargs.pop("data_file_header", True)
        awu_matrix_test.append((["data_file_header", data_file_header, True, (bool)]))

        logmech = kwargs.pop("logmech", "TD2")
        awu_matrix_test.append(
            ["logmech", logmech, True, (str), True, logmech_valid_values])

        logdata = kwargs.pop("logdata", None)
        awu_matrix_test.append(["logdata", logdata, True, (str), True])

        # Validate argument types.
        _Validators._validate_function_arguments(awu_matrix_test)

        self._validate()

        if logmech == "JWT" and not logdata:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING, 'logdata',
                                     'logmech=JWT'),
                MessageCodes.DEPENDENT_ARG_MISSING)

        if data_row_limit <= 0:
            raise ValueError(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT).
                             format("data_row_limit", "greater than"))

        # Either of 'input_data_file' or 'password' argument is required.
        password = kwargs.pop("password", None)

        # When exec_mode is local, the connection object is used to get the values in the table.
        if exec_mode == "local" and not (input_data_file or self.data):
            message = Messages.get_message(MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT,
                                           "input_data_file", "Script data")
            raise TeradataMlException(message, MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)

        if not self.script_name and self.files_local_path:
            message = Messages.get_message(MessageCodes.MISSING_ARGS,
                                           "script_name and files_local_path")
            raise TeradataMlException(message, MessageCodes.MISSING_ARGS)

        if input_data_file:
            if self.files_local_path is None:
                message = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING,
                                               "files_local_path", "input_data_file")
                raise TeradataMlException(message, MessageCodes.DEPENDENT_ARG_MISSING)
            else:
                # Check if file exists.
                fpath = os.path.join(self.files_local_path,
                                     input_data_file)
                _Validators._validate_file_exists(fpath)

        if self.script_name and self.files_local_path:
            # Check if file exists.
            fpath = os.path.join(self.files_local_path,
                                 os.path.basename(self.script_name))
            _Validators._validate_file_exists(fpath)

        if exec_mode.upper() == TableOperatorConstants.LOCAL_EXEC.value:
            user_script_path = os.path.join(self.files_local_path, self.script_name)
            import sys
            cmd = [str(sys.executable), user_script_path]
            cmd.extend(script_args)

            if input_data_file is not None:
                input_file_path = os.path.join(self.files_local_path, input_data_file)

                # Run user script locally with input from a file.
                exec_cmd_output = self.__local_run_user_script_input_file(
                    cmd, input_file_path, data_file_delimiter, data_file_quote_char, data_file_header)
                try:
                    return self.__process_test_script_output(exec_cmd_output)
                except Exception as exp:
                    raise

            else:
                if self.data.shape[0] > data_row_limit:
                    raise ValueError(
                        Messages.get_message(MessageCodes.DATAFRAME_LIMIT_ERROR,
                                             'data_row_limit', 'data_row_limit',
                                             data_row_limit))

                if not self.data._table_name:
                    self.data._table_name = df_utils._execute_node_return_db_object_name(
                        self.data._nodeid, self.data._metaexpr)

                table_name = UtilFuncs._extract_table_name(self.data._table_name)

                # Run user script locally with input from db.
                exec_cmd_output = self.__local_run_user_script_input_db(cmd, table_name)
                try:
                    return self.__process_test_script_output(exec_cmd_output)
                except Exception as exp:
                    raise

    def __local_run_user_script_input_file(self, cmd, input_file_path,
                                           data_file_delimiter='\t',
                                           data_file_quote_char='"',
                                           data_file_header=True):
        """
        DESCRIPTION:
            Function to run the user script in local mode with input from file.

        PARAMETERS:
            cmd:
                Required Argument.
                Specifies the command for running the user script.
                Types: str

            input_file_path:
                Required Argument.
                Specifies the absolute local path of input data file.
                Types: str

            data_file_delimiter:
                Optional Argument.
                Specifies the delimiter used in input data file.
                Default Value: '\t'
                Types: str

            data_file_quote_char:
                Optional Argument.
                Specifies the quote character used in input data file.
                Default Value: '"'
                Types: str

            data_file_header:
                Optional Argument.
                Specifies whether the input data file has header.
                Default Value: True
                Types: bool

        RETURNS:
            The string output of the command that is run on input data file.

        RAISES:
            Exception.

        EXAMPLES:
            self.__local_run_user_script_input_file(cmd ="cmd",
                                                    input_file_path = "input_file_path",
                                                    data_file_delimiter = "data_file_delimiter",
                                                    data_file_quote_char = "data_file_quote_char",
                                                    data_file_header = True)

        """
        with open(input_file_path) as data_file:
            import csv
            from pandas import isna as pd_isna

            data_handle = StringIO()

            # Read data from input file.
            ip_data = csv.reader(data_file,
                                 delimiter=data_file_delimiter,
                                 quotechar=data_file_quote_char)
            # Skip the first row of input file if data_file_header is True.
            if data_file_header:
                next(ip_data)
            for row in ip_data:
                if self.quotechar is not None:
                    # A NULL value should not be enclosed in quotes.
                    # The CSV module has no support for such output with writer,
                    # and hence the custom formatting.
                    line = ['' if pd_isna(s) else "{}{}{}".format(self.quotechar,
                                                                  str(s),
                                                                  self.quotechar)
                            for s in row]
                else:
                    line = ['' if pd_isna(s) else str(s) for s in row]

                complete_line = (self.delimiter.join(line))

                data_handle.write(complete_line)
                data_handle.write("\n")

            return self.__run_user_script_subprocess(cmd, data_handle)

    def __run_user_script_subprocess(self, cmd, data_handle):
        """
        DESCRIPTION:
            Function to run the user script in a new process and return the output.

        PARAMETERS:
            cmd:
                Required Argument.
                Specifies the command for running the script.
                Types: str

            data_handle:
                Required Argument.
                Specifies the data handle for the input data required by the user script.

        RETURNS:
            Output of user script on input data supplied in data_handle.

        RAISES:
            None.

        EXAMPLES:
            self.__run_user_script_subprocess(cmd = "exec_cmd_output",
                                              data_handle = data_handle)

        """
        # Launching new process to run the user script.
        try:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            process_output, process_error = proc.communicate(data_handle.getvalue().encode())
            data_handle.close()

            if proc.returncode == 0:
                return process_output.decode("utf-8").rstrip("\r|\n")
            else:
                message = Messages.get_message(MessageCodes.SCRIPT_LOCAL_RUN_ERROR).\
                    format(process_error)
                raise TeradataMlException(message, MessageCodes.SCRIPT_LOCAL_RUN_ERROR)
        except Exception as e:
            raise e

    def __process_test_script_output(self, exec_cmd_output):
        """
        DESCRIPTION:
            Function to format the output of the user script.

        PARAMETERS:
            exec_cmd_output:
                Required Argument.
                Specifies the output returned by the user script.
                Types: str

        RETURNS:
            The test script output as Pandas DataFrame.

        RAISES:
            Exception.

        EXAMPLES:
            self.__process_test_script_output(exec_cmd_output = "exec_cmd_output")
        """
        try:
            kwargs = dict()
            if self.quotechar is not None:
                kwargs['quotechar'] = self.quotechar
                kwargs['quoting'] = 1  # QUOTE_ALL

            output = StringIO(exec_cmd_output)

            from pandas import read_csv as pd_read_csv

            # Form a pandas dataframe.
            df = pd_read_csv(output, sep=self.delimiter, index_col=False, header=None,
                             names=list(self.returns.keys()), **kwargs)
            return df

        except Exception as exp:
            raise exp

    def __local_run_user_script_input_db(self, cmd, table_name):
        """
        DESCRIPTION:
            Function to run the user script in local mode with input from db.

        PARAMETERS:
            cmd:
                Required Argument.
                Specifies the command for running the user script.
                Types: str

            table_name:
                Required Argument.
                Specifies the table name for input to user script.
                Types: str

        RETURNS:
            The string output of the command that is run on the Vantage table.

        RAISES:
            Exception.

        EXAMPLES:
            self.__local_run_user_script_input_db(cmd = "cmd", table_name = "table_name")

        """
        db_data_handle = StringIO()
        try:
            con = get_connection()
            # Query for reading data from DB.
            query = ("SELECT * FROM {} ORDER BY 1;".format(table_name))
            cur = execute_sql(query)
            row = cur.fetchone()
            from pandas import isna as pd_isna
            while row:
                if self.quotechar is not None:
                    # A NULL value should not be enclosed in quotes.
                    # The CSV module has no support for such output with writer,
                    # and hence the custom formatting.
                    line = ['' if pd_isna(s) else "{}{}{}".format(self.quotechar,
                                                                  str(s),
                                                                  self.quotechar)
                            for s in row]
                else:
                    line = ['' if pd_isna(s) else str(s) for s in row]

                complete_line = (self.delimiter.join(line))
                db_data_handle.write(complete_line)
                db_data_handle.write("\n")
                row = cur.fetchone()
        except Exception as exp:
            raise exp

        return self.__run_user_script_subprocess(cmd, db_data_handle)

    def __repr__(self):
        """
        Returns the string representation for the class instance.
        """
        if self.result is None:
            repr_string = "Result is empty. Please run execute_script first."
        else:
            repr_string = "############ STDOUT Output ############"
            repr_string = "{}\n\n{}".format(repr_string, self.result)
        return repr_string

    def deploy(self, model_column, partition_columns=None, model_file_prefix=None, retry=3,
               retry_timeout=30):
        """
        DESCRIPTION:
            Function deploys the models generated after running `execute_script()` in database in
            VantageCloud Enterprise or in user environment in VantageCloud Lake.
            If deployed files are not needed, these files can be removed using `remove_file()` in
            database or `UserEnv.remove_file()` in lake.

            Note:
                If the models (one or many) fail to get deployed in Vantage even after retries,
                try deploying them again using `install_file()` function or remove installed
                files using `remove_file()` function.

        PARAMETERS:
            model_column:
                Required Argument.
                Specifies the column name in which models are present.
                Supported types of model in this column are CLOB and BLOB.
                Note:
                    The column mentioned in this argument should be present in
                    <apply_obj/script_obj>.result.
                Types: str

            partition_columns:
                Optional Argument.
                Specifies the columns on which data is partitioned.
                Note:
                    The columns mentioned in this argument should be present in
                    <apply_obj/script_obj>.result.
                Types: str OR list of str

            model_file_prefix:
                Optional Argument.
                Specifies the prefix to be used to the generated model file.
                If this argument is None, prefix is auto-generated.
                If the argument "model_column" contains multiple models and
                    * "partition_columns" is None - model file prefix is appended with
                      underscore(_) and numbers starting from one(1) to get model file
                      names.
                    * "partition_columns" is NOT None - model file prefix is appended
                      with underscore(_) and unique values in partition_columns are joined
                      with underscore(_) to generate model file names.
                Types: str

            retry:
                Optional Argument.
                Specifies the maximum number of retries to be made to deploy the models.
                This argument helps in retrying the deployment of models in case of network issues.
                This argument should be a positive integer.
                Default Value: 3
                Types: int

            retry_timeout:
                Optional Argument. Used along with retry argument. Ignored otherwise.
                Specifies the time interval in seconds between each retry.
                This argument should be a positive integer.
                Default Value: 30
                Types: int

        RETURNS:
            List of generated file identifiers in database or file names in lake.

        RAISES:
            - TeradatamlException
            - Throws warning when models failed to deploy even after retries.

        EXAMPLES:
            >>> import teradataml
            >>> from teradataml import load_example_data
            >>> load_example_data("openml", "multi_model_classification")

            >>> df = DataFrame("multi_model_classification")
            >>> df
                           col2      col3      col4  label  group_column  partition_column_1  partition_column_2
            col1
            -1.013454  0.855765 -0.256920 -0.085301      1             9                   0                  10
            -3.146552 -1.805530 -0.071515 -2.093998      0            10                   0                  10
            -1.175097 -0.950745  0.018280 -0.895335      1            10                   0                  11
             0.218497 -0.968924  0.183037 -0.303142      0            11                   0                  11
            -1.471908 -0.029195 -0.166141 -0.645309      1            11                   1                  10
             1.082336  0.846357 -0.012063  0.812633      1            11                   1                  11
            -1.132068 -1.209750  0.065422 -0.982986      0            10                   1                  10
            -0.440339  2.290676 -0.423878  0.749467      1             8                   1                  10
            -0.615226 -0.546472  0.017496 -0.488720      0            12                   0                  10
             0.579671 -0.573365  0.160603  0.014404      0             9                   1                  10

            ## Run in VantageCloud Enterprise using Script object.
            # Install Script file.
            >>> file_location = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "deploy_script.py")
            >>> install_file("deploy_script", file_location, replace=True)

            >>> execute_sql("SET SESSION SEARCHUIFDBPATH = <db_name>;")

            # Variables needed for Script execution.
            >>> from teradataml import configure
            >>> script_command = f'{configure.indb_install_location} ./<db_name>/deploy_script.py enterprise'
            >>> partition_columns = ["partition_column_1", "partition_column_2"]
            >>> columns = ["col1", "col2", "col3", "col4", "label",
                           "partition_column_1", "partition_column_2"]
            >>> returns = OrderedDict([("partition_column_1", INTEGER()),
                                       ("partition_column_2", INTEGER()),
                                       ("model", CLOB())])

            # Script execution.
            >>> obj = Script(data=df.select(columns),
                             script_command=script_command,
                             data_partition_column=partition_columns,
                             returns=returns
                             )
            >>> opt = obj.execute_script()
            >>> opt
            partition_column_1  partition_column_2               model                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    model
                            0                  10   b'gAejc1.....drIr'
                            0                  11   b'gANjcw.....qWIu'
                            1                  10   b'abdwcd.....dWIz'
                            1                  11   b'gA4jc4.....agfu'
            
            # Example 1: Provide only "partition_columns" argument. Here, "model_file_prefix" 
            #            is auto generated.
            >>> obj.deploy(model_column="model",
                           partition_columns=["partition_column_1", "partition_column_2"])
            ['model_file_1710436227163427__0_10',
             'model_file_1710436227163427__1_10',
             'model_file_1710436227163427__0_11',
             'model_file_1710436227163427__1_11']
            
            # Example 2: Provide only "model_file_prefix" argument. Here, filenames are suffixed 
            #            with 1, 2, 3, ... for multiple models.
            >>> obj.deploy(model_column="model", model_file_prefix="my_prefix_new_")
            ['my_prefix_new__1',
             'my_prefix_new__2',
             'my_prefix_new__3',
             'my_prefix_new__4']

            # Example 3: Without both "partition_columns" and "model_file_prefix" arguments.
            >>> obj.deploy(model_column="model")
            ['model_file_1710438346528596__1',
             'model_file_1710438346528596__2',
             'model_file_1710438346528596__3',
             'model_file_1710438346528596__4']
            
            # Example 4: Provide both "partition_columns" and "model_file_prefix" arguments.
            >>> obj.deploy(model_column="model", model_file_prefix="my_prefix_new_", 
                           partition_columns=["partition_column_1", "partition_column_2"])
            ['my_prefix_new__0_10',
             'my_prefix_new__0_11',
             'my_prefix_new__1_10',
             'my_prefix_new__1_11']

            # Example 5: Assuming that 2 model files fail to get installed due to network issues,
            #            the function retries installing the failed files twice with timeout between
            #            retries of 10 secs.
            >>> opt = obj.deploy(model_column="model", model_file_prefix="my_prefix_",
                                 partition_columns=["partition_column_1", "partition_column_2"],
                                 retry=2, retry_timeout=10)
            RuntimeWarning: The following model files failed to get installed in Vantage:
            ['my_prefix__1_10', 'my_prefix__1_11'].
            Try manually deploying them from the path '<temp_path>' using:
                - `install_file()` when connected to Enterprise/On-Prem system or
                - `UserEnv.install_file()` when connected to Lake system.
            OR
            Remove the returned installed files manually using `remove_file()` or `UserEnv.remove_file()`.
            >>> opt
            ['my_prefix__0_10',
             'my_prefix__0_11']

            ## Run in VantageCloud Lake using Apply object.
            # Let's assume an user environment named "user_env" already exists in VantageCloud Lake,
            # which will be used for the examples below.

            # ApplyTableOperator returns BLOB type for model column as per deploy_script.py.
            >>> returns = OrderedDict([("partition_column_1", INTEGER()),
                                       ("partition_column_2", INTEGER()),
                                       ("model", BLOB())])

            # Install the script file which returns model and partition columns.
            >>> user_env.install_file(file_location)

            >>> script_command = 'python3 deploy_script.py lake'
            >>> obj = Apply(data=df.select(columns),
                            script_command=script_command,
                            data_partition_column=partition_columns,
                            returns=returns,
                            env_name="user_env"
                            )

            >>> opt = obj.execute_script()
            >>> opt
            partition_column_1  partition_column_2               model                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    model
                            0                  10   b'gAejc1.....drIr'
                            0                  11   b'gANjcw.....qWIu'
                            1                  10   b'abdwcd.....dWIz'
                            1                  11   b'gA4jc4.....agfu'

            # Example 6: Provide both "partition_columns" and "model_file_prefix" arguments.
            >>> obj.deploy(model_column="model", model_file_prefix="my_prefix_",
                           partition_columns=["partition_column_1", "partition_column_2"])
            ['my_prefix__0_10',
             'my_prefix__0_11',
             'my_prefix__1_10',
             'my_prefix__1_11']

            # Other examples are similar to the examples provided for VantageCloud Enterprise.
        """

        arg_info_matrix = []
        arg_info_matrix.append(["model_column", model_column, False, (str)])
        arg_info_matrix.append(["partition_columns", partition_columns, True, (str, list)])
        arg_info_matrix.append(["model_file_prefix", model_file_prefix, True, (str)])
        arg_info_matrix.append(["retry", retry, True, (int)])
        arg_info_matrix.append(["retry_timeout", retry_timeout, True, (int)])
        _Validators._validate_function_arguments(arg_info_matrix)

        _Validators._validate_positive_int(retry, "retry", lbound_inclusive=True)
        _Validators._validate_positive_int(retry_timeout, "retry_timeout", lbound_inclusive=True)

        if self.result is None:
            return "Result is empty. Please run execute_script first."

        if partition_columns is None:
            partition_columns = []
        partition_columns = UtilFuncs._as_list(partition_columns)

        req_columns = [model_column] + partition_columns

        _Validators._validate_column_exists_in_dataframe(columns=req_columns, metaexpr=self.result._metaexpr)

        data = self.result.select(req_columns)
        data._index_column = None # Without this, first column i.e., model column will be index column.


        if model_file_prefix is None:
            timestamp = time.time()
            tmp = "{}{}".format(floor(timestamp / 1000000),
                                floor(timestamp % 1000000 * 1000000 +
                                    int(str(uuid.uuid4().fields[-1])[:10])))
            model_file_prefix = f"model_file_{tmp}_"

        vals = data.get_values()

        model_column_type = data._td_column_names_and_sqlalchemy_types[model_column.lower()].__class__.__name__

        n_models = len(vals)

        # Default location for .teradataml is user's home directory if configure.local_storage is not set.
        tempdir =  GarbageCollector._get_temp_dir_name()

        def __install_file(model_file, model_file_path):
            """
            Function to install the model file in Vantage and return the status.
            """
            file_installed = True
            try:
                if self.__class__.__name__ == "Script":
                    from teradataml.dbutils.filemgr import install_file
                    install_file(file_identifier=model_file, file_path=model_file_path,
                                is_binary=True, suppress_output=True, replace=True)
                elif self.__class__.__name__ == "Apply":
                    self.env.install_file(file_path=model_file_path, suppress_output=True, replace=True)
            except Exception as e:
                file_installed = False
            return file_installed

        installed_files = []
        failed_files = []

        for i, row in enumerate(vals):
            model = row[0]
            partition_values = ""
            if partition_columns:
                partition_values = "_".join([str(x) for x in row[1:]])
            elif n_models > 1:
                partition_values = str(i+1)

            model_file = f"{model_file_prefix}_{partition_values}"
            model_file_path = os.path.join(tempdir, model_file)

            if model_column_type == "CLOB":
                import base64
                model = base64.b64decode(model.partition("'")[2])
            elif model_column_type == "BLOB":
                # No operation needed.
                # Apply model training returns BLOB type.
                pass
            else:
                raise ValueError(f"Model column type {model_column_type} is not supported.")

            with open(model_file_path, "wb") as f:
                f.write(model)

            file_installed = __install_file(model_file, model_file_path)

            if file_installed:
                installed_files.append(model_file)
                os.remove(model_file_path)
            else:
                # File failed to get installed in Vantage. Hence, keeping the file in tempdir.
                failed_files.append(model_file)

        while retry and failed_files:
            # If there are any failed files and retry is not zero, retry installing the failed files.
            time.sleep(retry_timeout)
            retry_failed_files = []
            for model_file in failed_files:
                model_file_path = os.path.join(tempdir, model_file)
                file_installed = __install_file(model_file, model_file_path)

                if file_installed:
                    installed_files.append(model_file)
                    os.remove(model_file_path)
                else:
                    # File failed to get installed in Vantage. Hence, keeping the file in tempdir.
                    retry_failed_files.append(model_file)
            failed_files = retry_failed_files
            retry -= 1

        if failed_files:
            failed_files.sort()
            warning_message = "The following model files failed to get installed in Vantage:\n" + str(failed_files) + ".\n"
            warning_message += "Try manually deploying them from the path '" + tempdir + "' using:\n"
            warning_message += "    - `install_file()` when connected to Enterprise/On-Prem system or\n"
            warning_message += "    - `UserEnv.install_file()` when connected to Lake system.\n"
            warning_message += "OR\nRemove the returned installed files manually using `remove_file()` or `UserEnv.remove_file()`."
            warnings.warn(RuntimeWarning(warning_message))

        return installed_files
