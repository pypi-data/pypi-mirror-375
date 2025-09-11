# ##################################################################
#                                                                  #
# Copyright 2020 Teradata. All rights reserved.                    #
# TERADATA CONFIDENTIAL AND TRADE SECRET                           #
#                                                                  #
# Primary Owner: Rohit Khurd (rohit.khurd@teradata.com)            #
# Secondary Owner: Trupti Purohit (trupti.purohit@teradata.com)    #
#                                                                  #
# Description: Utilities for Table Operators.                      #
#                                                                  #
# ##################################################################
import os, json
import teradataml.dataframe as tdmldf
from teradataml.common.constants import TableOperatorConstants, \
    TeradataConstants, OutputStyle
from teradataml import configure
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.dbutils.filemgr import install_file, remove_file
from teradataml.scriptmgmt.lls_utils import get_env
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators
from functools import partial
from inspect import isfunction, getsource
from pathlib import Path


class _TableOperatorUtils:
    """
    Class providing utility functions to execute the different table operator
    and return the required object based on the 'operation'.
    """

    def __init__(self,
                 arg_info_matrix,
                 data,
                 operation,
                 user_function,
                 exec_mode,
                 chunk_size,
                 data_partition_column=None,
                 data_hash_column=None,
                 **kwargs):
        """
        DESCRIPTION:
            Constructor to initialize the object of class _TableOperatorUtils.

        PARAMETERS:
            arg_info_matrix:
                Required Argument.
                Specifies the caller specific argument information matrix that
                can be readily used with Validators.
                Types: list of lists.

            data:
                Required Argument.
                Specifies the teradataml DataFrame to apply the table operator
                on.

            operation:
                Required Argument.
                Specifies the teradataml operation being performed.
                Permitted values: 'map_row', 'map_partition'.
                Types: str

            user_function:
                Required Argument.
                Specifies the user defined function to apply to every row
                or group of rows in "data".
                Types: function

                Notes:
                    * This can be either a lambda function, a regular python
                      function, or an object of functools.partial.
                    * The first argument (positional) to the user defined
                      function must be an iterator on the partition of rows
                      from the teradataml DataFrame represented as a Pandas
                      DataFrame to which it is to be applied.
                    * A non-lambda function can be passed only when the user
                      defined function does not accept any arguments other than
                      the mandatory input - the iterator on the partition of
                      rows, or the input row.
                      A user can also use functools.partial and lambda functions
                      for the same, which are especially handy when:
                          * there is a need to pass positional and/or keyword
                            arguments (lambda).
                          * there is a need to pass keyword arguments only
                            (functool.partial).
                    * The return type of the user defined function must be one
                      of the following:
                          * numpy ndarray
                              * when one-dimensional, having the same number of
                                values as output columns.
                              * when two-dimensional, every array contained in
                                the outer array having the same number of values
                                as output columns.
                          * pandas Series
                          * pandas DataFrame

            exec_mode:
                Required Argument.
                Specifies the mode of execution for the user defined function.
                It can be either of:
                    * IN-DB: Execute the function on data in the teradataml
                             DataFrame in Vantage.
                    * LOCAL: Execute the function locally on sample data (at
                             most "num_rows" rows) from "data".
                Permitted values: 'IN-DB', 'LOCAL', 'REMOTE'
                Types: str

            chunk_size:
                Required Argument.
                Specifies the number of rows to be read in a each chunk using
                the iterator created on top of the data that will be consumed
                by the user defined function.
                Varying this input affects the performance and the memory
                utilized by the function.
                Types: int

            data_partition_column:
                Optional Argument.
                Specifies the Partition By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for partition.
                Types: str OR list of Strings (str)

            data_hash_column:
                Optional Argument.
                Specifies the column to be used for hashing.
                The rows in the data are redistributed to AMPs based on the hash
                value of the column specified.
                Types: str

            data_order_column:
                Required Argument.
                Specifies the Order By columns for data.
                Values to this argument can be provided as a list, if multiple
                columns are used for ordering.
                This argument is used with in both cases:
                "is_local_order = True" and "is_local_order = False".
                Types: str OR list of Strings (str)

            is_local_order:
                Required Argument.
                Specifies a boolean value to determine whether the input data
                is to be ordered locally at each AMP or not.
                This argument is ignored, if "data_order_column" is None.
                When set to 'True', data is ordered locally.
                Types: bool

            nulls_first:
                Required Argument.
                Specifies a boolean value to determine whether NULLS are listed
                first or last during ordering.
                This argument is ignored, if "data_order_column" is None.
                NULLS are listed first when this argument is set to 'True', and
                last when set to 'False'.
                Types: bool

            sort_ascending:
                Required Argument.
                Specifies a boolean value to determine if the input is to be
                sorted on the "data_order_column" in ascending or descending
                order.
                The sorting is ascending when this argument is set to 'True',
                and descending when set to 'False'.
                This argument is ignored, if "data_order_column" is None.
                Types: bool

            returns:
                Required Argument.
                Specifies the output column definition corresponding to the
                output of "user_function".
                Types: Dictionary specifying column name to
                       teradatasqlalchemy type mapping.

            num_rows:
                Required Argument.
                Specifies the maximum number of sample rows to use from the
                teradataml DataFrame to apply the user defined function to when
                "exec_mode" is 'LOCAL'.
                Types: int

            delimiter:
                Required Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing the result columns.
                Types: str

            quotechar:
                Required Argument.
                Specifies the character to use for quoting values in the input
                and output rows.
                Types: str

            auth:
                Required Argument.
                Specifies an authorization to use when running the script.
                Types: str

            charset:
                Required Argument.
                Specifies the character encoding for data in "data".
                Permitted values: 'utf-16', 'latin'
                Types: str

            env_name:
                Required Argument.
                Specifies the name of the remote user environment or an object of class UserEnv.
                Types: str or oject of class UserEnv.

            style:
                Optional Argument.
                Specifies how input is passed to and output is generated by the 'apply_command'
                respectively.
                Note:
                    This clause only supports 'csv' value for Apply.
                Default value: "csv"
                Types: str

        RETURNS:
            Object of class _TableOperatorUtils.

        RAISES:
            TypeError, ValueError, TeradataMlException.

        EXAMPLES:
            tbl_op_util_obj =  _TableOperatorUtils(arg_info_matrix, data,
                                                   operation="map_row",
                                                   user_function, exec_mode,
                                                   chunk_size=chunk_size,
                                                   data_partition_column=None,
                                                   data_hash_column=None,
                                                   data_order_column=data_order_column,
                                                   is_local_order=is_local_order,
                                                   nulls_first=nulls_first,
                                                   sort_ascending=sort_ascending,
                                                   returns=returns, delimiter=delimiter,
                                                   quotechar=quotechar, auth=auth,
                                                   charset=charset, num_rows=num_rows)
        """
        self.data = data
        self.operation = operation
        self.user_function = user_function
        self.exec_mode = exec_mode
        self.chunk_size = chunk_size
        self.data_partition_column = data_partition_column
        self.data_hash_column = data_hash_column
        self.__env = None
        self.debug = kwargs.pop('debug', False)
        self._validate_version = False
        self.packages = []
        # Add all entries from kwargs as class attributes.
        self.__dict__.update(kwargs)

        # Validate the inputs.
        self.__validate(arg_info_matrix)

        # Create the intermediate user script.
        self.__create_user_script()

    def __validate(self, arg_info_matrix=None):
        """
        DESCRIPTION:
            Internal function to validate the inputs corresponding to the
            TableOperator utility function.

        PARAMETERS:
            arg_info_matrix:
                Optional Argument.
                Specifies the caller specific argument information matrix
                that can be readily used with Validators.
                Types: list of lists.

        RETURNS:
            None.

        RAISES:
            TypeError, ValueError.

        EXAMPLES:
            self.__validate()
        """
        # Validate the user defined function.

        if self.operation in [TableOperatorConstants.UDF_OP.value,\
                              TableOperatorConstants.REGISTER_OP.value]:
            for udf_function in self.user_function:
                if not isfunction(udf_function):
                    raise TypeError(Messages.get_message(
                        MessageCodes.UNSUPPORTED_DATATYPE, 'user_function', "'function'"))
        else:
            if not (isfunction(self.user_function) or
                    isinstance(self.user_function, partial)):
                raise TypeError(Messages.get_message(
                    MessageCodes.UNSUPPORTED_DATATYPE, 'user_function',
                    "'function' or 'functools.partial'")
                )

        if arg_info_matrix is None:
            arg_info_matrix = []

        # Validate arguments.
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        # Additional validations for map_row and map_partition and apply operations.
        if self.operation in [TableOperatorConstants.MAP_ROW_OP.value,
                              TableOperatorConstants.MAP_PARTITION_OP.value,
                              TableOperatorConstants.APPLY_OP.value]:
            # Validate that chunk_size and num_rows are positive integers.
            _Validators._validate_positive_int(self.chunk_size, "chunk_size")
            _Validators._validate_positive_int(self.num_rows, "num_rows")



    def __create_user_script(self):
        """
        DESCRIPTION:
            Internal function to create the intermediate script and assigning
            class attributes corresponding to the scripts path, name, and alias
            used for installation.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            Exception.

        EXAMPLES:
            self.__create_user_script()
        """
        # If operation is register, then generate script name based on the
        # user function name and return type.
        # It has the format "tdml_udf_name_<registered_name>_udf_type_<return_type>_register.py"
        if self.operation == TableOperatorConstants.REGISTER_OP.value:
            registered_name = list(self.returns.keys())[0]
            return_type = self.returns[registered_name]
            self.script_name = "tdml_udf_name_{}_udf_type_{}_register.py".format(registered_name, return_type)
            self.script_base_name = Path(self.script_name).stem
        else:
            # Generate script name and alias, and add entry to a Garbage Collector.
            # script_entry is the string that is added to Garbage collector.
            # It has the format "<databasename>"."<file_id>".
            self.script_entry, self.script_alias, self.script_name, self.script_base_name = self.__get_script_name()

        if self.operation not in [TableOperatorConstants.UDF_OP.value, TableOperatorConstants.REGISTER_OP.value]:
            # Get the converters to use with pandas.read_csv, and to correctly
            # typecast the numeric data.
            python_input_col_types = [UtilFuncs._teradata_type_to_python_type(col.type)
                                    for col in self.data._metaexpr.c]
            input_converters = UtilFuncs._get_pandas_converters(python_input_col_types)

            python_output_col_types = [UtilFuncs._teradata_type_to_python_type(type_)
                                    for type_ in list(self.returns.values())]
            output_converters = UtilFuncs._get_pandas_converters(python_output_col_types)

        # Create script in .teradataml directory.
        script_dir = GarbageCollector._get_temp_dir_name()
        # script_path is the actual path where we want to generate the user
        # script at.
        self.script_path = os.path.join(script_dir, self.script_name)

        template_dir = os.path.join(os.path.dirname(
                            os.path.dirname(os.path.abspath(__file__))),
                                            "table_operators",
                                            "templates")
        # Get the template.
        template = {TableOperatorConstants.APPLY_OP.value: TableOperatorConstants.APPLY_TEMPLATE.value,
                    TableOperatorConstants.UDF_OP.value: TableOperatorConstants.UDF_TEMPLATE.value,
                    TableOperatorConstants.REGISTER_OP.value: TableOperatorConstants.REGISTER_TEMPLATE.value                    }
        template_name = template.get(self.operation, TableOperatorConstants.MAP_TEMPLATE.value)
        # Write to the script based on the template.
        try:
            with open(os.path.join(template_dir, template_name), 'r') as input_file:
                with open(self.script_path, 'w') as output_file:
                    if self.operation == TableOperatorConstants.UDF_OP.value:
                        
                        user_function_code = UtilFuncs._func_to_string(self.user_function)
                        output_file.write(input_file.read().format(
                            DELIMITER=self.delimiter,
                            QUOTECHAR=self.quotechar,
                            FUNCTION_DEFINITION=user_function_code,
                            FUNCTION_ARGS =str(self.function_args),
                            INPUT_COLUMNS=json.dumps(self.data.columns),
                            OUTPUT_COLUMNS=json.dumps(list(self.returns.keys())),
                            COLUMNS_DEFINITIONS=json.dumps(self.columns_definitions),
                            OUTPUT_TYPE_CONVERTERS=json.dumps(self.output_type_converters)
                        ))
                    elif self.operation == TableOperatorConstants.REGISTER_OP.value:
                        # Get the source code of the user function.
                        user_function_code = UtilFuncs._func_to_string(self.user_function)
                        output_file.write(input_file.read().format(
                            FUNCTION_DEFINITION=user_function_code,
                            FUNCTION_NAME = self.user_function[0].__name__
                        ))   
                    else:
                        # prepare script file from template file for maprow and mappartition.
                        output_file.write(
                            input_file.read().format(
                                DELIMITER=UtilFuncs._serialize_and_encode(
                                    self.delimiter),
                                STO_OPERATION=UtilFuncs._serialize_and_encode(
                                    self.operation),
                                USER_DEF_FUNC=UtilFuncs._serialize_and_encode(
                                    self.user_function),
                                DF_COL_NAMES_LIST=UtilFuncs._serialize_and_encode(
                                    self.data.columns),
                                DF_COL_TYPES_LIST=UtilFuncs._serialize_and_encode(
                                    python_input_col_types),
                                OUTPUT_COL_NAMES_LIST=UtilFuncs._serialize_and_encode(
                                    list(self.returns.keys())),
                                OUTPUT_CONVERTERS=UtilFuncs._serialize_and_encode(
                                    output_converters),
                                QUOTECHAR=UtilFuncs._serialize_and_encode(
                                    self.quotechar),
                                INPUT_CONVERTERS=UtilFuncs._serialize_and_encode(
                                    input_converters),
                                CHUNK_SIZE=UtilFuncs._serialize_and_encode(
                                    self.chunk_size)
                            )
                        )
        except Exception:
            # We may end up here if the formatting of the templating to create
            # the user script fails.
            # This would possibly create a incorrect or empty file, which
            # needs to be deleted.
            self.__remove_file_and_delete_entry_from_gc(remove_from_sql_eng=False)
            raise

    def execute(self):
        """
        DESCRIPTION:
            Function to call the appropriate table operator function
            based on the 'operation'.

        PARAMETERS:
            None.

        RETURNS:
            object.
            The function may return a DataFrame or an object of the operator class
            corresponding to the 'operation'.

        RAISES:
             Exception.

        EXAMPLES:
            tbl_operator_obj.execute()
        """
        try:
            if self.operation in [TableOperatorConstants.MAP_ROW_OP.value,
                                  TableOperatorConstants.MAP_PARTITION_OP.value] or \
                                  (self.operation == TableOperatorConstants.UDF_OP.value and self.exec_mode == 'IN-DB'):
                return self.__execute_script_table_operator()
            elif self.operation == TableOperatorConstants.APPLY_OP.value or \
                (self.operation == TableOperatorConstants.UDF_OP.value and self.exec_mode == 'REMOTE'):
                return self.__execute_apply_table_operator()
        except Exception:
            raise
        finally:
            # Remove local copy of file to free up the disk space immediately.
            # Garbage collection will take care of it as a failsafe.
            # We may end up here after the script was created, but even before executing it.
            if not self.debug:
                GarbageCollector._delete_local_file(self.script_path)
            elif not self.__dict__.get('is_printed', False):
                self._print_script_path()

    def __get_script_name(self):
        """
        DESCRIPTION:
            Internal function to generate a temporary script name adding it to Garbage Collector's
            persisted file, and also generating the alias of file ID used to install it,
            along with the full entry that goes in the persisted file.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            A 4 -tuple of Strings (str).

        EXAMPLES:
            script_entry, script_alias, script_name, script_base_name = self.__get_script_name()
        """
        script_entry = UtilFuncs._generate_temp_script_name(prefix="" if self.operation is None else self.operation,
                                                            extension="py", gc_on_quit=(self.debug^True))
        # script_alias is the file ID.
        script_alias = UtilFuncs._teradata_unquote_arg(UtilFuncs._extract_table_name(script_entry), quote='"')

        # script_name is the actual file name (basename).
        script_name = script_alias  # alias now contains extension also.

        # Extract the base name without extension.
        script_base_name = Path(script_alias).stem
        return script_entry, script_alias, script_name, script_base_name

    def __execute_script_table_operator(self):
        """
        DESCRIPTION:
            Internal function to return the result of Script for operations like
            'map_row' and 'map_partition' while making sure that Script
            generated a temporary table instead of a view for the 'result' when
            the 'self.exec_mode' is 'IN_DB'.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            teradataml DataFrame, if 'self.exec_mode' is 'IN-DB'.

        EXAMPLES:
           return_obj = self.__execute_script_table_operator()
        """
        # Get the current database to use for setting search_path.
        import teradataml.context.context as context
        database = context._get_current_databasename()

        check_reserved_keyword = False if sorted(list(self.returns.keys())) == sorted(self.data.columns) else True

        # First create Table Object to that validations are done on inputs.
        # For 'script_command' instead of specifying the full path to binary, we are specifying
        # 'configure.indb_install_location' which is pointing to the installation location of In-DB package.
        # Default value is the installation location of 2.0.0 version.
        # User can provide the installation location of previous version in case they are not using the latest.
        # This fix is done for ELE-5958 - https://teradata-pe.atlassian.net/browse/ELE-5958

        # If operation is map_row or map_partition, then it should validate the python and
        # 'dill' package version mismatch.
        if self.operation in ["map_row", "map_partition"]:
            self._validate_version = True
            self.packages = ['dill']

        from teradataml.table_operators.Script import Script
        table_op_obj = Script(data=self.data,
                              script_name=self.script_name,
                              files_local_path=GarbageCollector._get_temp_dir_name(),
                              script_command="{}/bin/python3 ./{}/{}".format(
                                  configure.indb_install_location, database, self.script_name),
                              returns=self.returns,
                              delimiter=self.delimiter,
                              auth=self.auth,
                              quotechar=self.quotechar,
                              data_order_column=self.data_order_column,
                              is_local_order=self.is_local_order,
                              sort_ascending=self.sort_ascending,
                              nulls_first=self.nulls_first,
                              charset=self.charset,
                              data_partition_column=self.data_partition_column,
                              data_hash_column=self.data_hash_column,
                              _validate_version = self._validate_version,
                              _func_name = self.operation,
                              _packages = self.packages
                              )
        table_op_obj.check_reserved_keyword = check_reserved_keyword

        if self.exec_mode.upper() == TableOperatorConstants.INDB_EXEC.value:
            # If not test mode, execute the script in Vantage.
            try:
                # Install that file, suppressing the output message.
                execute_sql('SET SESSION SEARCHUIFDBPATH = \"{}\"'.format(database))
                install_file(file_identifier=self.script_base_name,
                             file_path=self.script_path,
                             suppress_output=True)

                # Execute the script.
                return table_op_obj.execute_script(
                    output_style=OutputStyle.OUTPUT_TABLE.value)
            except Exception:
                raise
            finally:
                self.__remove_file_and_delete_entry_from_gc()
        elif self.exec_mode.upper() == TableOperatorConstants.LOCAL_EXEC.value:
            return table_op_obj.test_script(exec_mode='local')

    def __execute_apply_table_operator(self):
        """
        DESCRIPTION:
            Internal function to return the result of script execution using Apply
            operation while making sure that Script generated a temporary table
            instead of a view for the 'result' when the 'self.exec_mode' is 'REMOTE'.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            teradataml DataFrame, if 'self.exec_mode' is 'REMOTE'.

        EXAMPLES:
           return_obj = self.__execute_apply_table_operator()
        """

        # If operation is apply, then it should validate the python and 'dill' package version mismatch.
        if self.operation == "apply":
            self._validate_version = True
            self.packages = ['dill']

        # First create Apply Table operator object so that validations are done on inputs.
        from teradataml.table_operators.Apply import Apply
        apply_op_obj = Apply(data=self.data,
                             script_name=self.script_name,
                             env_name=self.env_name,
                             files_local_path=GarbageCollector._get_temp_dir_name(),
                             apply_command="python3 {}".format(self.script_name),
                             returns=self.returns,
                             delimiter=self.delimiter,
                             quotechar=self.quotechar,
                             data_order_column=self.data_order_column,
                             is_local_order=self.is_local_order,
                             sort_ascending=self.sort_ascending,
                             nulls_first=self.nulls_first,
                             data_partition_column=self.data_partition_column,
                             data_hash_column=self.data_hash_column,
                             style=self.style,
                             _validate_version=self._validate_version,
                             _func_name = self.operation,
                             _packages = self.packages
                             )

        # APPLY operator requires installation and deletion of script file.
        # Get the UserEnv object and store it in a variable.
        self.__env = get_env(apply_op_obj.env_name) if isinstance(apply_op_obj.env_name, str) \
            else apply_op_obj.env_name

        if self.exec_mode.upper() == TableOperatorConstants.REMOTE_EXEC.value:
            # If not test mode, execute the script using Apply table operator.
            try:
                # If APPLY or UDF, get environment and use it for installing file.
                if self.operation in [TableOperatorConstants.APPLY_OP.value,
                                      TableOperatorConstants.UDF_OP.value]:
                    self.__env.install_file(self.script_path, suppress_output=True)

                # Execute the script.
                return apply_op_obj.execute_script(
                    output_style=OutputStyle.OUTPUT_TABLE.value)

            except Exception:
                raise
            finally:
                self.__remove_file_and_delete_entry_from_gc(remove_from_sql_eng=False)

    def __remove_file_and_delete_entry_from_gc(self,
                                               remove_from_sql_eng=True):
        """
        DESCRIPTION:
            Internal function to remove the installed file and delete it's entry
            from GC's persisted file.

        PARAMETERS:
            remove_from_sql_eng:
                Optional Argument.
                Specifies whether to remove the file from the Advanced SQL
                Engine as well.
                When True, an attempt to remove the file from Advanced SQL
                Engine is made.
                Default value: True
                Types: bool

        RAISES:
            None.

        RETURNS:
            None.

        EXAMPLES:
            self.__remove_file_and_delete_entry_from_gc()
        """
        if remove_from_sql_eng:
            # Remove file from Vantage, suppressing it's output.
            remove_file(file_identifier=self.script_base_name, force_remove=True,
                        suppress_output=True)

        # For apply, remove file from remote user environment.
        if self.operation == TableOperatorConstants.APPLY_OP.value or \
            (self.operation == TableOperatorConstants.UDF_OP.value and self.exec_mode == 'REMOTE'):
            self.__env.remove_file(self.script_name, suppress_output=True)

        # Remove the entry from Garbage Collector
        if self.operation in [TableOperatorConstants.MAP_ROW_OP.value,
                              TableOperatorConstants.MAP_PARTITION_OP.value,
                              TableOperatorConstants.APPLY_OP.value,
                              TableOperatorConstants.UDF_OP.value]:
            if self.debug:
                self._print_script_path()
                self.is_printed = True
            else:
                GarbageCollector._delete_object_entry(
                    objects_to_delete=self.script_entry,
                    object_type=TeradataConstants.TERADATA_SCRIPT,
                    remove_entry_from_gc_list=True
                )
    def _print_script_path(self):
        """
        DESCRIPTION:
            Internal function to print the path of the script file.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            None.
        """
        mssg1 = f"Path for the script {self.script_path}"
        mssg2 = "The user should delete the script file since it is not being garbage collected."
        mssg_len = max(len(mssg1), len(mssg2))
        print("-" * mssg_len)
        print(mssg1)
        print(mssg2)
        print("-" * mssg_len)