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
# Description: Apply is a TeradataML wrapper around Teradata's
# Apply Table Operator
# ##################################################################

import os, re
from collections import OrderedDict
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import OutputStyle
from teradataml.options.display import display
from teradataml.common.wrapper_utils import AnalyticsWrapperUtils
from teradataml.scriptmgmt.UserEnv import UserEnv
from teradataml.scriptmgmt.lls_utils import get_user_env, get_env
from teradataml.common.constants import TeradataConstants
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.sqlbundle import SQLBundle
from teradataml.table_operators.TableOperator import TableOperator
from teradataml.table_operators.apply_query_generator import ApplyTableOperatorQueryGenerator
from teradatasqlalchemy.dialect import dialect as td_dialect
from teradataml.utils.validators import _Validators
from teradatasqlalchemy import (BYTEINT, SMALLINT, INTEGER, BIGINT, DECIMAL, FLOAT, NUMBER)
from teradatasqlalchemy import (CHAR, VARCHAR)


class Apply(TableOperator):

    def __init__(self,
                 data=None,
                 script_name=None,
                 files_local_path=None,
                 apply_command=None,
                 delimiter=",",
                 returns=None,
                 quotechar=None,
                 env_name=None,
                 style="csv",
                 data_partition_column=None,
                 data_hash_column=None,
                 data_order_column=None,
                 is_local_order=False,
                 sort_ascending=True,
                 nulls_first=True,
                 **kwargs):
        """
        DESCRIPTION:
            The fastpath Apply table operator executes a user-installed script or
            any Linux command inside the remote user environment using Open Analytics Framework.
            The installed script will be executed in parallel with data from Advanced SQL Engine.

        PARAMETERS:
            apply_command:
                Required Argument.
                Specifies the command/script to run.
                Note:
                    * 'Rscript --vanilla ..' helps user to run R script without saving or restoring anything in
                      the process and keep things clean.
                Types: str

            script_name:
                Required Argument.
                Specifies the name of the user script.
                Types: str

            files_local_path:
                Required Argument.
                Specifies the absolute local path where user script and all supporting files
                like model files, input data file reside.
                Types: str

            env_name:
                Required Argument.
                Specifies the name of the remote user environment or an object of class UserEnv.
                Types: str or oject of class UserEnv.

            returns:
                Optional Argument.
                Specifies the output column definition.
                Data argument is required when "returns" is not specified.
                When "returns" is not specified, output column definition should match
                with column definition of table specified in the data argument.
                Types: Dictionary specifying column name to teradatasqlalchemy type mapping.
                Default: None

            data:
                Optional Argument.
                Specifies a teradataml DataFrame containing the input data for the script.

            data_hash_column:
                Optional Argument.
                Specifies the column to be used for hashing.
                The rows in the input data are redistributed to AMPs based on the hash value of the
                column specified.
                If there is no "data_hash_column", then the entire result set,
                delivered by the function, constitutes a single group or partition.
                Types: str
                Notes:
                    1. "data_hash_column" can not be specified along with "data_partition_column".
                    2. "data_hash_column" can not be specified along with "is_local_order=False" and
                       "data_order_column".

            data_partition_column:
                Optional Argument.
                Specifies Partition By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for partition. If there is no "data_partition_column",
                then the entire result set delivered by the function, constitutes a single
                group or partition.
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
                    When "is_local_order" is set to 'True', "data_order_column" should be
                    specified, and the columns specified in "data_order_column"
                    are used for local ordering.


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

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    1) The Quotechar cannot be the same as the Delimiter.
                    2) The value of delimiter cannot be an empty string, newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and output values for the script.
                Note: The Quotechar cannot be the same as the Delimiter.
                Default value: double quote (")
                Types: str

            style:
                Optional Argument.
                Specifies how input is passed to and output is generated by the 'apply_command'
                respectively.
                Note:
                    This clause only supports 'csv' value for Apply.
                Default value: "csv"
                Types: str

        RETURNS:
            Apply Object

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Note - Refer to User Guide for setting required permissions.
            # Load example data.
            >>> load_example_data("Script", ["barrier"])

            # Example 1 - The Python script mapper.py reads in a line of text input ("Old Macdonald Had A Farm")
            #             from csv and  splits the line into individual words, emitting a new row for each word.

            # Create teradataml DataFrame objects.
            >>> barrierdf = DataFrame.from_table("barrier")

            # Create remote user environment.
            >>> testenv = create_env('testenv', 'python_3.7.13', 'Demo environment')
            User environment testenv created.

            >>> import os, teradataml
            >>> teradataml_dir = os.path.dirname(teradataml.__file__)

            # Create an Apply object that allows us to execute script.
            >>> apply_obj = Apply(data=barrierdf,
                                  script_name='mapper.py',
                                  files_local_path= os.path.join(teradataml_dir, 'data', 'scripts'),
                                  apply_command='python3 mapper.py',
                                  data_order_column="Id",
                                  is_local_order=False,
                                  nulls_first=False,
                                  sort_ascending=False,
                                  returns={"word": VARCHAR(15), "count_input": VARCHAR(10)},
                                  env_name=testenv,
                                  delimiter='\t')

            # Run user script locally using data from csv.
            # This helps the user to fix script level issues outside Open Analytics
            # Framework.
            >>> apply_obj.test_script(input_data_file=os.path.join(teradataml_dir, 'data', 'barrier.csv'))
            ############ STDOUT Output ############

                    word count_input
            0  Macdonald           1
            1          A           1
            2       Farm           1
            3        Had           1
            4        Old           1
            5          1           1

            # Install file in remote user environment.
            >>> apply_obj.install_file(file_name=os.path.join(teradataml_dir, 'data', 'mapper.py'))
            File 'mapper.py' installed successfully in the remote user environment 'testenv'.

            # Execute the user script in the Open Analytics Framework.
            >>> apply_obj.execute_script()
                    word count_input
            0  Macdonald           1
            1          A           1
            2       Farm           1
            3        Had           1
            4        Old           1
            5          1           1

            # Remove the installed file from remote user environment.
            >>> apply_obj.remove_file(file_name='mapper.py')
            File 'mapper.py' removed successfully from the remote user environment 'testenv'.

            # Example 2 - The R script mapper.R reads in a line of text input ("Old Macdonald Had A Farm")
            #             from csv and splits the line into individual words, emitting a new row for each word.

            # Create teradataml DataFrame object.
            >>> barrierdf = DataFrame.from_table("barrier")

            # Create remote user environment.
            >>> testenv = create_env('test_env_for_r', 'r_4.1', 'Demo environment')
            User environment test_env_for_r created.

            >>> import os, teradataml

            # Install file in remote user environment.
            >>> testenv.install_file(file_path=os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.R"))
            File 'mapper.R' installed successfully in the remote user environment 'test_env_for_r'.

            # Create an Apply object that allows us to execute script.
            >>> apply_obj = Apply(data=barrierdf,
                                  apply_command='Rscript --vanilla mapper.R',
                                  data_order_column="Id",
                                  is_local_order=False,
                                  nulls_first=False,
                                  sort_ascending=False,
                                  returns={"word": VARCHAR(15), "count_input": VARCHAR(10)},
                                  env_name=testenv,
                                  delimiter='\t')

            # Execute the user script in the Open Analytics Framework.
            >>> apply_obj.execute_script()
                     word count_input
            0  Macdonald            1
            1          A            1
            2       Farm            1
            3        Had            1
            4        Old            1
            5          1            1

            # Remove the installed file from remote user environment.
            >>> apply_obj.remove_file(file_name='mapper.R')
            File 'mapper.R' removed successfully from the remote user environment 'test_env_for_r'.
        """
        # Common variables and their validation in base class.
        super(Apply, self).__init__(data,
                                    script_name,
                                    files_local_path,
                                    delimiter,
                                    returns,
                                    quotechar,
                                    data_partition_column,
                                    data_hash_column,
                                    data_order_column,
                                    is_local_order,
                                    sort_ascending,
                                    nulls_first)
        # Create AnalyticsWrapperUtils instance which contains validation functions.
        # This is required for is_default_or_not check.
        # Rest all validation is done using _Validators
        self.__awu = AnalyticsWrapperUtils()

        # Perform argument validation for arguments specific to this class.
        self.__arg_info_matrix = []

        self.__arg_info_matrix.append(["style", style, True, (str), True, ['CSV']])
        self.__arg_info_matrix.append(["env_name", env_name, False, (str, UserEnv), True])
        self.__arg_info_matrix.append(["apply_command", apply_command, False, (str), True])
        self.__arg_info_matrix.append(["returns", returns, True, (dict), True])
        self._skip_argument_validation = False
        # Perform the function argument validations.
        self.__apply__validate()

        # If user do not pass environment, get the default environment.
        if env_name is None:
            env_name = get_user_env()
        self._open_af_env = env_name

        # Set the variable specific to this child class.
        self.apply_command = apply_command
        self.env_name = env_name if isinstance(env_name, str) else env_name.env_name
        self.style = style
        self.returns = returns

        # Internal variable to check if validation is required for Python and python package versions mismatch.
        _validation_required = kwargs.pop('_validate_version', False)
        # Interval variable to store the function name for which validation is required.
        _func_name = kwargs.pop('_func_name', None)
        # Internal variable to store the list of packages required for the function.
        _packages = kwargs.pop('_packages', None)

        # Check if validation for Python and python package versions mismatch is required.
        if _validation_required:
            # Check if the Python interpreter major versions are consistent between Vantage and local.
            UtilFuncs._check_python_version_diff(self.env_name)
            # Check if the package versions are consistent between Vantage and local.
            UtilFuncs._check_package_version_diff(_func_name, _packages, self.env_name)


    @property
    def env(self):
        """
        DESCRIPTION:
            Getter to get environment.

        RETURNS:
            bool

        RAISES:
            None
        """
        if isinstance(self._open_af_env, str):
            self._open_af_env = get_env(self._open_af_env)

        return self._open_af_env

    @property
    def skip_argument_validation(self):
        """
        DESCRIPTION:
            Getter for self._skip_argument_validation.

        RETURNS:
            bool

        RAISES:
            None
        """
        return self._skip_argument_validation

    @skip_argument_validation.setter
    def skip_argument_validation(self, flag):
        """
        DESCRIPTION:
            Setter for self._skip_argument_validation

        PARAMETERS:
            flag:
               Required Argument.
               Specifies whether the argument validation should be skipped or not.
               Types: bool

        RETURNS:
            None

        RAISES:
            None
        """
        self._skip_argument_validation = flag

    def __apply__validate(self):

        if self._skip_argument_validation:
            return
        # Make sure that a non-NULL value has been supplied for all mandatory arguments.
        _Validators._validate_missing_required_arguments(self.__arg_info_matrix)

        # Validate argument types.
        _Validators._validate_function_arguments(self.__arg_info_matrix)

        if all([self.returns is None, self.data is None]):
            raise TeradataMlException(Messages.get_message(MessageCodes.SPECIFY_AT_LEAST_ONE_ARG,
                                                           "data",
                                                           "returns"),
                                      MessageCodes.SPECIFY_AT_LEAST_ONE_ARG)

        if self.returns is None:
            self.returns = OrderedDict(zip(self.data.columns,
                                           [col.type for col in
                                           self.data._metaexpr.c]))

    def install_file(self, file_name, replace=False):
        """
        DESCRIPTION:
            Function to install script in remote user environment specified in env_name
            argument of an Apply class object.
            On success, prints a message that file is installed or replaced.
            This language script can be executed via execute_script() function.

        PARAMETERS:
            file_name:
                Required Argument:
                Specifies the name of the file including file extension to be installed
                or replaced.
                Note:
                    File names are case sensitive.
                Types: str

            replace:
                Optional Argument.
                Specifies if the file is to be installed or replaced.
                Default Value: False
                Types: bool

        RETURNS:
             True, if successful.

        RAISES:
            TeradataMLException, SqlOperationalError

        EXAMPLES:
            # Example 1: Install the file mapper.py found at the relative path data/scripts/ using
            #            the default text mode.

            # In order to run example 1, "mapper.py" is required to be present on client.
            # Provide the path of "mapper.py" in "file_path" argument.
            # Create a file named "mapper.py" with content as follows:
            -----------------------------------------------------------
            #!/usr/bin/python
            import sys
            for line in sys.stdin:
            line = line.strip()
            words = line.split()
            for word in words:
                print ('%s\t%s' % (word, 1))
            ------------------------------------------------------------

            # Create teradataml DataFrame objects.
            >>> barrierdf = DataFrame.from_table("barrier")

            # Create remote user environment.
            >>> from teradataml import create_env
            >>> test_env = create_env('test_env', 'python_3.7.9', 'Demo environment')
            User environment testenv created.

            >>> import teradataml, os
            >>> teradataml_dir = os.path.dirname(teradataml.__file__)
            # Create an Apply object that allows user to execute script using Open Analytics Framework.
            >>> apply_obj = Apply(data=barrierdf,
                                  files_local_path='data/scripts/',
                                  script_name='mapper.py',
                                  apply_command='python3 mapper.py',
                                  data_order_column="Id",
                                  env_name=test_env,
                                  returns={"word": VARCHAR(15), "count_input": VARCHAR(2)}
                                  )

            # Install file in remote user environment.
            >>> apply_obj.install_file(file_name='mapper.py')
            File 'mapper.py' installed successfully in the remote user environment 'test_env'.

            # Replace file in remote user environment.
            >>> apply_obj.install_file(file_name='mapper.py', replace=True)
            File 'mapper.py' replaced successfully in the remote user environment 'test_env'.
        """
        # Install/Replace file in the remote user environment.
        try:
            __arg_info_matrix = []
            __arg_info_matrix.append(["file_name", file_name, False, (str), True])

            # Validate arguments
            _Validators._validate_missing_required_arguments(__arg_info_matrix)
            _Validators._validate_function_arguments(__arg_info_matrix)

            file_path = os.path.join(self.files_local_path, file_name)

            # Install file in remote user environment.
            self.env.install_file(file_path=file_path, replace=replace)
        except:
            raise

    def remove_file(self, file_name):
        """
        DESCRIPTION:
            Function to remove user installed files/scripts from remote user environment.

        PARAMETERS:
            file_name:
                Required Argument.
                Specifies the name of user-installed file with extension.
                Note:
                    File names are case sensitive.
                Types: str

        RETURNS:
             True, if successful.

        RAISES:
            TeradataMLException, SqlOperationalError

        EXAMPLES:
            # Refer install_file example to create mapper.py script and install the file
            # in remote user environment.

            # Remove the installed file.
            >>> apply_obj.remove_file(file_name='mapper.py')
            File mapper.py removed successfully from the remote user environment test_env.

        """
        # Remove file from remote user environment.
        self.env.remove_file(file_name)

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
            re-create Apply object.

        PARAMETERS:
            data:
                Required Argument.
                Specifies a teradataml DataFrame containing the input data.

            data_partition_column:
                Optional Argument.
                Specifies Partition By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for partition. If there is no "data_partition_column",
                then the entire result set delivered by the function, constitutes a single
                group or partition.
                Default Value: ANY
                Types: str OR list of Strings (str)
                Notes:
                    1) "data_partition_column" can not be specified along with
                       "data_hash_column".
                    2) "data_partition_column" can not be specified along with
                       "is_local_order = True".

            data_hash_column:
                Optional Argument.
                Specifies the column to be used for hashing.
                The rows in the input data are redistributed to AMPs based on the hash value of the
                column specified.
                If there is no data_hash_column, then the entire result set,
                delivered by the function, constitutes a single group or partition.
                Types: str
                Note:
                    "data_hash_column" can not be specified along with "data_partition_column",
                    "is_local_order" and "data_order_column".

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

            is_local_order:
                Optional Argument.
                Specifies a boolean value to determine whether the input data is to be
                ordered locally or not. Order by specifies the order in which the
                values in a group or partition are sorted. Local Order By specifies
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
            # Load example data.
            >>> load_example_data("Script", ["barrier", "barrier_new"])

            # Create teradataml DataFrame objects.
            >>> barrierdf = DataFrame.from_table("barrier")
            >>> barrierdf
                                    Name
            Id
            1   Old Macdonald Had A Farm
            >>>

            # List base environments.
            >>> from teradataml import list_base_envs, create_env
            >>> list_base_envs()
                   base_name language version
            0  python_3.7.13   Python  3.7.13
            1  python_3.8.13   Python  3.8.13
            2  python_3.9.13   Python  3.9.13
            >>>

            # Create an environment.
            >>> demo_env = create_env(env_name = 'demo_env', base_env = 'python_3.8.13', desc = 'Demo Environment')
            User environment 'demo_env' created.
            >>>

            >>> import teradataml
            >>> from teradatasqlalchemy import VARCHAR
            >>> td_path = os.path.dirname(teradataml.__file__)

            # The script mapper.py reads in a line of text input
            # ("Old Macdonald Had A Farm") from csv and
            # splits the line into individual words, emitting a new row for each word.
            # Create an APPLY object with data and its arguments.
            >>> apply_obj = Apply(data = barrierdf,
            ...                   script_name='mapper.py',
            ...                   files_local_path= os.path.join(td_path,'data', 'scripts'),
            ...                   apply_command='python3 mapper.py',
            ...                   data_order_column="Id",
            ...                   is_local_order=False,
            ...                   nulls_first=False,
            ...                   sort_ascending=False,
            ...                   returns={"word": VARCHAR(15), "count_input": VARCHAR(10)},
            ...                   env_name=demo_env,
            ...                   delimiter='\t')

            # Install file in environment.
            >>> apply_obj.install_file('mapper.py')
            File 'mapper.py' installed successfully in the remote user environment 'demo_env'.
            >>>

            >>> apply_obj.execute_script()
                    word count_input
            0  Macdonald           1
            1          A           1
            2       Farm           1
            3        Had           1
            4        Old           1
            5          1           1
            >>>

            # Now run the script on a new DataFrame.
            >>> barrierdf_new = DataFrame.from_table("barrier_new")
            >>> barrierdf_new
                                    Name
            Id
            1   Old Macdonald Had A Farm
            2   On his farm he had a cow
            >>>

            # Note:
            #    All data related arguments that are not specified in set_data() are
            #    reset to default values.
            >>> apply_obj.set_data(data=barrierdf_new,
            ...                    data_order_column='Id',
            ...                    nulls_first = True)
            >>>

            # Execute the user script on Vantage.
            >>> apply_obj.execute_script()
                    word count_input
            0        his           1
            1         he           1
            2        had           1
            3          a           1
            4          1           1
            5        Old           1
            6  Macdonald           1
            7        Had           1
            8          A           1
            9       Farm           1
            >>>
        """
        super(Apply, self).set_data(data,
                                    data_partition_column,
                                    data_hash_column,
                                    data_order_column,
                                    is_local_order,
                                    sort_ascending,
                                    nulls_first)

        self._validate(for_data_args=True)

    def __form_table_operator_query(self):
        """
        Function to generate the Table Operator queries. The function defines
        variables and list of arguments required to form the query.
        """
        # Output table arguments list
        self.__func_output_args_sql_names = []
        self.__func_output_args = []

        # Generate lists for rest of the function arguments
        self.__func_other_arg_sql_names = []
        self.__func_other_args = []
        self.__func_other_arg_json_datatypes = []

        self.__func_args_before_using_clause_names = []
        self.__func_args_before_using_clause_values = []
        self.__func_args_before_using_clause_types = []

        self.__func_other_arg_sql_names.append("APPLY_COMMAND")
        self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.apply_command, "'"))
        self.__func_other_arg_json_datatypes.append("STRING")

        self.__func_other_arg_sql_names.append("ENVIRONMENT")
        self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.env_name, "'"))
        self.__func_other_arg_json_datatypes.append("STRING")

        self.__func_other_arg_sql_names.append("STYLE")
        self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.style, "'"))
        self.__func_other_arg_json_datatypes.append("STRING")

        if self.delimiter is not None:
            self.__func_other_arg_sql_names.append("delimiter")
            self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.delimiter, "'"))
            self.__func_other_arg_json_datatypes.append("STRING")

        # Generate returns clause
        if self.returns is not None:
            if isinstance(self.returns, dict):
                returns_clause = ', '.join(
                    '{} {}'.format(key, self.returns[key].compile(td_dialect())) for key in self.returns.keys())
                self.__func_other_arg_sql_names.append("returns")
                self.__func_other_args.append(returns_clause)
                self.__func_other_arg_json_datatypes.append("STRING")

        if self.quotechar is not None:
            self.__func_other_arg_sql_names.append("quotechar")
            self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.quotechar, "'"))
            self.__func_other_arg_json_datatypes.append("STRING")

        # Declare empty lists to hold input table information.
        self.__func_input_arg_sql_names = []
        self.__func_input_table_view_query = []
        self.__func_input_dataframe_type = []
        self.__func_input_distribution = []
        self.__func_input_partition_by_cols = []
        self.__func_input_order_by_cols = []
        self.__func_input_order_by_type = []
        self.__func_input_sort_ascending = self.sort_ascending
        self.__func_input_nulls_first = None

        # Process data
        if self.data is not None:
            data_distribution = "FACT"
            if self.data_hash_column is not None:
                data_distribution = "HASH"
                self.data_partition_column = UtilFuncs._teradata_collapse_arglist(self.data_hash_column, "\"")
            else:
                if self.__awu._is_default_or_not(self.data_partition_column, "ANY"):
                    self.data_partition_column = UtilFuncs._teradata_collapse_arglist(
                        self.data_partition_column, "\"")
                else:
                    self.data_partition_column = None
            if self.data_order_column is not None:
                if self.is_local_order:
                    self.__func_input_order_by_type.append("LOCAL")
                    if not self.data_hash_column:
                        data_distribution = None
                else:
                    self.__func_input_order_by_type.append(None)
                self.__func_input_order_by_cols.append(
                    UtilFuncs._teradata_collapse_arglist(self.data_order_column, "\""))
            else:
                self.__func_input_order_by_type.append(None)
                self.__func_input_order_by_cols.append("NA_character_")

            self.__table_ref = self.__awu._teradata_on_clause_from_dataframe(self.data, False)
            self.__func_input_distribution.append(data_distribution)
            self.__func_input_arg_sql_names.append("input")
            self.__func_input_table_view_query.append(self.__table_ref["ref"])
            self.__func_input_dataframe_type.append(self.__table_ref["ref_type"])
            self.__func_input_partition_by_cols.append(self.data_partition_column)
            self.__func_input_nulls_first = self.nulls_first

        function_name = "Apply"
        # Create instance to generate Table Operator Query.
        applyqg_obj = ApplyTableOperatorQueryGenerator(function_name
                                         , self.__func_input_arg_sql_names
                                         , self.__func_input_table_view_query
                                         , self.__func_input_dataframe_type
                                         , self.__func_input_distribution
                                         , self.__func_input_partition_by_cols
                                         , self.__func_input_order_by_cols
                                         , self.__func_other_arg_sql_names
                                         , self.__func_other_args
                                         , self.__func_other_arg_json_datatypes
                                         , self.__func_output_args_sql_names
                                         , self.__func_output_args
                                         , self.__func_input_order_by_type
                                         , self.__func_input_sort_ascending
                                         , self.__func_input_nulls_first
                                         , engine="ENGINE_SQL"
                                            )

        # Invoke call to Apply Table operator query generation.
        self._tblop_query = applyqg_obj._gen_table_operator_select_stmt_sql()

        # Print Table Operator query if requested to do so.
        if display.print_sqlmr_query:
            print(self._tblop_query)

    def execute_script(self, output_style='VIEW'):
        """
        DESCRIPTION:
            Function enables user to execute Python scripts using Open Analytics Framework.

        PARAMETERS:
            output_style:
                Specifies the type of output object to create - a table or a view.
                Permitted values: 'VIEW', 'TABLE'.
                Default value: 'VIEW'
                Types: str

        RETURNS:
            Output teradataml DataFrames can be accessed using attribute
            references, such as ScriptObj.<attribute_name>.
            Output teradataml DataFrame attribute name is:
                result

        RAISES:
            TeradataMlException

        EXAMPLES:
            Refer to help(Apply)
        """
        # Validate the output_style.
        permitted_values = [OutputStyle.OUTPUT_TABLE.value,
                            OutputStyle.OUTPUT_VIEW.value]
        _Validators._validate_permitted_values(output_style, permitted_values, 'output_style',
                                               case_insensitive=False, includeNone=False)

        # Generate the Table Operator query
        self.__form_table_operator_query()

        # Execute Table Operator query and return results
        return self._execute(output_style)

    # TODO: Remove the function with ELE-5010.
    def _execute(self, output_style="TABLE"):
        """
        DESCRIPTION:
            Function to execute APPLY Query and store the result in a table.

        PARAMETERS:
            output_style:
                Specifies the type of output object to create - a table or a view.
                Permitted values: 'VIEW', 'TABLE'.
                Default value: 'VIEW'
                Types: str

        RETURNS:
            Output teradataml DataFrames can be accessed using attribute
            references, such as ScriptObj.<attribute_name>.
            Output teradataml DataFrame attribute name is:
                result

        RAISES:
            TeradataMlException

        EXAMPLES:
            self._execute("VIEW")
        """
        # Generate STDOUT table name and add it to the output table list.
        tblop_stdout_temp_tablename = UtilFuncs._generate_temp_table_name(prefix="td_tblop_out_",
                                                                          use_default_database=True, gc_on_quit=True,
                                                                          quote=False,
                                                                          table_type=TeradataConstants.TERADATA_TABLE
                                                                          )

        try:
            # Create table.
            columns_clause = ', '.join(
                '{} {}'.format(key, self.returns[key].compile(td_dialect())) for key in self.returns.keys())
            UtilFuncs._create_table_using_columns(tblop_stdout_temp_tablename,
                                                  columns_datatypes=columns_clause,
                                                  storage="TD_OFSSTORAGE")

            # Use insert with select to populate the data to table.
            # Insert with select accepts a table as a table and columns as
            # second and third parameter. So, converting the Query to a subquery
            # so the query acts as a table.
            query = "({}) as apply_result".format(self._tblop_query)
            ins_table = SQLBundle._build_insert_from_table_query(tblop_stdout_temp_tablename,
                                                                 query,
                                                                 "*")
            UtilFuncs._execute_query(ins_table)

        except Exception as emsg:
            emsg = str(emsg)
            pattern = r'\b\d{18}\b'
            query_id = re.findall(pattern, emsg)
            print("-----------------------------------------------------------------------")
            print("User should run view_log() to download the logs with the query id \"{}\".".format(query_id[0]))
            print("-----------------------------------------------------------------------")
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_EXEC_SQL_FAILED, emsg),
                                      MessageCodes.TDMLDF_EXEC_SQL_FAILED)

        self.result = self.__awu._create_data_set_object(
            df_input=UtilFuncs._extract_table_name(tblop_stdout_temp_tablename), source_type="table",
            database_name=UtilFuncs._extract_db_name(tblop_stdout_temp_tablename))

        return self.result