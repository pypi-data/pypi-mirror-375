"""
Unpublished work.
Copyright (c) 2020 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: PankajVinod.Purandare@teradata.com
Secondary Owner: Adithya.Avvaru@teradata.com

This file implements the core framework that allows user to execute any Vantage Analytics
Library (VALIB) Function.
"""
import time
import uuid
from math import floor

from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.common import messages
from teradataml.common.constants import TeradataConstants, ValibConstants as VC
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.messages import Messages, MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import get_context, _get_current_databasename
from teradataml.options.configure import configure
from teradataml.dataframe.dataframe import DataFrame, in_schema
from teradataml.utils.validators import _Validators
from teradataml.analytics.Transformations import Binning, Derive, OneHotEncoder, FillNa, \
    LabelEncoder, MinMaxScalar, Retain, Sigmoid, ZScore
from teradataml.common.constants import TeradataReservedKeywords, TeradataConstants


class _VALIB():
    """ An internal class for executing VALIB analytic functions. """

    def __init__(self, *c, **kwargs):
        """ Constructor for VALIB function execution. """
        # Vantage SQL name of the VALIB function.
        self.__sql_func_name = ""
        # teradataml name of the VALIB function.
        self.__tdml_valib_name = ""
        self.__func_arg_sql_syntax_eles = []
        self.__func_other_arg_sql_names = []
        self.__func_other_args = []
        self.result = None
        self.__generated_sql = None
        self.__multioutput_attr_map = {}
        self.__multioutput_attr_map.update(VC.TERADATAML_VALIB_MULTIOUTPUT_ATTR_MAP.value)
        self.__output_arg_map = {}
        self.__output_arg_map.update(VC.VALIB_FUNCTION_OUTPUT_ARGUMENT_MAP.value)

    @property
    def _tdml_valib_name(self):
        """
        DESCRIPTION:
            Function to return VAL function name.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            valib.LinReg._tdml_valib_name
        """
        return self.__tdml_valib_name

    def __getattr__(self, item):
        """
        DESCRIPTION:
            Returns an attribute of the _VALIB class.

        PARAMETERS:
            item:
                Required Argument.
                Specifes the name of the attribute.

        RETURNS:
            An object of _VALIB class.

        RAISES:
            None.

        EXAMPLES:
            valib.ValibFunctionName
        """
        return self.__get_valib_instance(item)

    def __call__(self, **kwargs):
        """
        DESCRIPTION:
            Function makes the instance of this class callable.

        PARAMETERS:
            kwargs:
                Keyword arguments for the callable function.

        RETURNS:
            Returns a callable of object of _VALIB class.

        RAISES:
            None.

        EXAMPLES:
            valib.ValibFunctionName()
        """
        # Input arguments passed to a function.
        # Use the same as the data members for the dynamic class.
        self.__dyn_cls_data_members = kwargs
        return self._execute_valib_function(**kwargs)

    def __get_valib_instance(self, item):
        """
        DESCRIPTION:
            Function creates and returns an instance of valib class for the function
            name assigning the SQL function name and teradataml function name attributes.
        PARAMETERS:
            item:
                Required Argument.
                Specifies the name of the attribute/function.
                Types: str

        RETURNS:
            An object of _VALIB class.

        RAISES:
            None.

        EXAMPLES:
            valib.__get_valib_instance("<function_name>")
        """
        valib_f = _VALIB()
        valib_f.__tdml_valib_name = item

        # Overwriting the multioutput attribute mapper with evaluator map if tdml function name
        # is present in the constant TERDATAML_EVALUATOR_OUTPUT_ATTR_MAP.
        evaluator_map = VC.TERDATAML_EVALUATOR_OUTPUT_ATTR_MAP.value
        if item in evaluator_map:
            valib_f.__multioutput_attr_map = {}
            valib_f.__multioutput_attr_map.update(evaluator_map)

        try:
            valib_f.__sql_func_name = VC.TERADATAML_VALIB_SQL_FUNCTION_NAME_MAP.value[item].upper()
        except:
            valib_f.__sql_func_name = item.upper()
        return valib_f

    def __create_dynamic_valib_class(self):
        """
        DESCRIPTION:
            Function dynamically creates a class of VALIB function type.

        PARAMETERS:
             None

        RETURNS:
            An object of dynamic class of VALIB function name.

        RAISES:
            None.

        EXAMPLE:
            self.__create_dynamic_valib_class()
        """

        # Constructor for the dynamic class.
        def constructor(self):
            """ Constructor for dynamic class """
            # Do Nothing...
            pass
        self.__dyn_cls_data_members["__init__"] = constructor

        # __repr__ method for dynamic class.
        def print_result(self):
            """ Function to be used for representation of VALIB function type object. """
            repr_string = ""
            for key in self._valib_results:
                repr_string = "{}\n############ {} Output ############".format(repr_string, key)
                repr_string = "{}\n\n{}\n\n".format(repr_string, getattr(self, key))
            return repr_string
        self.__dyn_cls_data_members["__repr__"] = print_result

        query = (self.__query, self.__generated_sql)
        # Print the underlying SQL stored procedure call or generated SQL.
        def show_query(self, query_type="sp"):
            """
            Function to return the underlying SQL query.
            """
            _Validators._validate_permitted_values(arg=query_type, 
                                                   permitted_values=["sp", "sql", "both"],
                                                   arg_name="query_type")
            if query_type.lower() == "sp":
                return query[0]
            elif query_type.lower() == "sql":
                return query[1]
            return query

        self.__dyn_cls_data_members["show_query"] = show_query
        
        # To list attributes using dict()
        self.__dyn_cls_data_members["__dict__"] = self.__dyn_cls_data_members

        # Dynamic class creation with VALIB function name.
        valib_class = type(self.__tdml_valib_name, (object,), self.__dyn_cls_data_members)

        return valib_class()

    def __create_output_dataframes(self, out_var):
        """
        DESCRIPTION:
            Internal function to create output DataFrame, set the index labels to
            None and add the same to the result list.
            Function makes sure that all these created variables are added to the
            dynamic class as data members.

        PARAMETERS:
            out_var:
                Required Argument.
                Specifies the name of the output DataFrame.
                Types: str

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self.__create_output_dataframes("result")
        """
        self.__dyn_cls_data_members[out_var] = DataFrame(
            in_schema(self.__db_name, self.__dyn_cls_data_members[out_var]))
        self.__dyn_cls_data_members[out_var]._index_label = None
        self.__dyn_cls_data_members[out_var]._index_query_required = False
        self.__dyn_cls_data_members[VC.OUTPUT_DATAFRAME_RESULTS.value].append(out_var)

    @collect_queryband(attr="_VALIB__sql_func_name")
    def __generate_execute_sp_query(self):
        """
        DESCRIPTION:
            Function generates a stored procedure call corresponding to the function
            and execute the same.

        PARAMETERS:
            None.

        RETURNS:
            Console output of query, if any, otherwise None.

        RAISES:
            TeradataMlException

        EXAMPLES:
             self.__generate_execute_sp_query()
        """
        # Generate and execute SQL VALIB SP call.
        if configure.val_install_location is None:
            message = Messages.get_message(MessageCodes.UNKNOWN_INSTALL_LOCATION,
                                           "Vantage analytic functions",
                                           "option 'configure.val_install_location'")
            raise TeradataMlException(message, MessageCodes.MISSING_ARGS)

        query_string = "call {0}.td_analyze('{1}', '{2};');"
        self.__query = query_string.format(configure.val_install_location, self.__sql_func_name,
                                           ";".join(self.__func_arg_sql_syntax_eles))

        return UtilFuncs._execute_query(self.__query, expect_none_result=True)

    def __generate_valib_sql_argument_syntax(self, arg, arg_name):
        """
        DESCRIPTION:
            Function to generate the VALIB SQL function argument syntax.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies an argument value to be used in VALIB function call.
                Types: Any object that can be converted to a string.

            arg_name:
                Required Argument.
                Specifies a SQL argument name to be used in VALIB function call.
                Types: String

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            self.__generate_valib_sql_argument_syntax(argument, "argument_name")
        """
        arg = UtilFuncs._teradata_collapse_arglist(arg, "")
        self.__func_arg_sql_syntax_eles.append("{}={}".format(arg_name, arg))

    def __extract_db_tbl_name(self, table_name, arg_name, extract_table=True, remove_quotes=False):
        """
        DESCRIPTION:
            Function processes the table name argument to extract database or table from it.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the fully-qualified table name.
                Types: String

            arg_name:
                Required Argument.
                Specifies a SQL argument name to be used in VALIB function call.
                Types: String

            extract_table:
                Optional Argument.
                Specifies whether to extract a table name or database name from
                "table_name". When set to 'True', table name is extracted otherwise
                database name is extracted.
                Default Value: True
                Types: bool

            remove_quotes:
                Optional Argument.
                Specifies whether to remove quotes from the extracted string or not.
                When set to 'True', double quotes will be removed from the extracted
                name.
                Default Value: False
                Types: bool

        RETURNS:
            Extracted name.

        RAISES:
            None.

        EXAMPLES:
            # Extract the table name and remove quotes.
            self.__extract_db_tbl_name(self, table_name, arg_name, remove_quotes=True)

            # Extract the database name.
            self.__extract_db_tbl_name(self, table_name, arg_name, extract_table=False)
        """
        # Extract table name or db name from the 'table_name'
        if extract_table:
            name = UtilFuncs._extract_table_name(table_name)
        else:
            name = UtilFuncs._extract_db_name(table_name)

        # Remove quotes.
        if remove_quotes:
            name = name.replace("\"", "")

        # Generate VALIB function argument call syntax.
        self.__generate_valib_sql_argument_syntax(name, arg_name)

        return name

    def __get_temp_table_name(self):
        """
        DESCRIPTION:
            Generate and get the table name for the outputs.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self.__get_temp_table_name()
        """
        prefix = "valib_{}".format(self.__tdml_valib_name.lower())
        tbl_name =  UtilFuncs._generate_temp_table_name(prefix=prefix, use_default_database=True,
                                                        gc_on_quit=True, quote=False,
                                                        table_type=TeradataConstants.TERADATA_TABLE)
        # With VT option, table name is getting generated with 'vt_'.
        # But its not getting created as Volatile table. Hence
        # explicitly garbage collecting.
        if configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE:
            GarbageCollector._add_to_garbagecollector(tbl_name,
                                                      TeradataConstants.TERADATA_TABLE)
        return tbl_name

    def __process_dyn_cls_output_member(self, arg_name, out_tablename, out_var=None):
        """
        DESCRIPTION:
            Function to process output table name argument. As part of processing it does:
                * Generates the SQL clause for argument name.
                * Adds a data member to the dynamic class dictionary, with the name same as
                  exposed name of the output DataFrame.

        PARAMETERS:
            arg_name:
                Required Argument.
                Specifies the output table SQL argument name.
                Types: str

            out_tablename:
                Required Argument.
                Specifies the output table name.
                Types: str

            out_var:
                Optional Argument.
                Specifies the output DataFrame name to use.
                If this is None, then value for this is extracted from
                'TERADATAML_VALIB_MULTIOUTPUT_ATTR_MAP'.
                Types: str

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self.__process_dyn_cls_output_member("outputtablename", out_tablename,
                                                 ValibConstants.DEFAULT_OUTPUT_VAR.value)
        """
        if out_var is None:
            # If output variable name is None, then extract it from the MAP.
            # This output variable corresponds to the output DataFrame name of the function.
            func_name = self.__get_output_attr_map_func_name()
            out_var = self.__multioutput_attr_map[func_name][arg_name]

        # Add the output DataFrame name, to the dictionary of dynamic class.
        # At start we will just add the corresponding table name as it's value.
        self.__dyn_cls_data_members[out_var] = self.__extract_db_tbl_name(table_name=out_tablename,
                                                                          arg_name=arg_name)

    def __get_table_name_with_extension(self, table_name, extension):
        """
        DESCRIPTION:
            Internal function to create a table name using the extension and add it to Garbage
            Collector.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the table name for which extension is to be suffixed.
                Types: str

            extension:
                Required Argument.
                Specifies the suffix string that is to be added at the end of the table name.
                Types: str

        RETURNS:
            The new table name.

        EXAMPLE:
            self.__get_table_name_with_extension(table_name="<table_name>", extension="_rpt")
        """
        # Add extension to the table name.
        generated_table_name = "{}{}".format(table_name, extension)


        # Register new output table to the GC.
        gc_tabname = "\"{}\".\"{}\"".format(self.__db_name, generated_table_name)
        GarbageCollector._add_to_garbagecollector(gc_tabname, TeradataConstants.TERADATA_TABLE)

        return generated_table_name

    def __get_output_attr_map_func_name(self):
        """
        DESCRIPTION:
            Function to get either teradataml function name or SQL function name from
            "__multioutput_attr_map" based on whether the function is evaluator function or not.

        PARAMETERS:
            None.

        RETURNS:
            Either teradataml function name or SQL function name.

        RAISES:
            None.

        EXAMPLES:
            self.__get_output_attr_map_func_name()
        """
        # __multioutput_attr_map can have either SQL function name or tdml function name.
        # If the function is evaluator function, then __multioutput_attr_map contains the
        # dictionary of tdml function name to dictionary of output tables. Otherwise, it
        # contains the dictionary of SQL function name to dictionary of output tables.
        func_name = self.__sql_func_name
        if self.__tdml_valib_name in self.__multioutput_attr_map:
            func_name = self.__tdml_valib_name
        return func_name

    def __process_func_outputs(self, query_exec_output):
        """
        DESCRIPTION:
            Internal function to process the output tables generated by a stored procedure
            call. Function creates the required output DataFrames from the tables and a
            result list.

        PARAMETERS:
            query_exec_output:
                Required Argument.
                Specifies the output captured by the UtilFuncs._execute_query() API.
                If no output is generated None should be passed.
                Types: tuple

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            exec_out = self.__generate_execute_sp_query()
            self.__process_func_outputs(query_exec_output=exec_out)
        """
        self.__dyn_cls_data_members[VC.OUTPUT_DATAFRAME_RESULTS.value] = []

        func_name = self.__get_output_attr_map_func_name()

        # Processing gensql/gensqlonly output.
        # Checking if user has passed gen_sql or gen_sql_only as an argument and is true.
        # If gen_sql_only is true, don't process the output and return.
        gen_sql_only = self.__dyn_cls_data_members.get("gen_sql_only", False)
        if gen_sql_only:
            self.__generated_sql = query_exec_output[0][0][0]
            self.__dyn_cls_data_members[VC.DEFAULT_OUTPUT_VAR.value] = None
            return
        elif self.__dyn_cls_data_members.get("gen_sql", False):
            self.__generated_sql = query_exec_output[0][0][0]

        if func_name in self.__multioutput_attr_map:
            # Process each output and get it ready for dynamic class creation.
            valib_output_mapper = self.__multioutput_attr_map[func_name]
            for key in valib_output_mapper:
                out_var = valib_output_mapper[key]
                self.__create_output_dataframes(out_var=out_var)
        elif VC.DEFAULT_OUTPUT_VAR.value in self.__dyn_cls_data_members:
            # Process functions that generate only one output.
            self.__create_output_dataframes(out_var=VC.DEFAULT_OUTPUT_VAR.value)
        else:
            # Function which will not produce any output table, but will return result set.
            # "result_set" will contain the actual result data in a list of list format.
            self.__dyn_cls_data_members["result_set"] = query_exec_output[0]
            # "result_columns" will contain the list of column names of the result data.
            self.__dyn_cls_data_members["result_columns"] = query_exec_output[1]
            # TODO - Add support for EXP's does not producing any output tables. Future Purpose.

    def __process_output_extensions(self, output_table_name, output_extensions):
        """
        DESCRIPTION:
            Function to process extended outputs of the function.
            Extended outputs are the output tables generated by SQL function, using
            the existing output table name and adding some extensions to it.
            For example,
                Linear function takes one argument for producing the output tables, but
                it's ends up creating multiple output tables.
                This is how it created these tables.
                    * Creates a coefficients and statistics table by using the name passed to
                      "outputtablename" argument.
                    * Creates a statistical measures table using the name passed to
                      "outputtablename" argument and appending "_rpt" to it.
                    * Creates a XML reports table using the name passed to "outputtablename"
                      argument and appending "_txt" to it.

        PARAMETERS:
            output_table_name:
                Required Argument.
                Specifies the output table name to use the extensions with to produce new
                output table names.
                Types: str

            output_extensions:
                Required Argument.
                Specifies a mapper with output table extensions as keys and output dataframe name
                as value.
                Types: dict

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self.__process_output_extensions("output_table_name",
                                             {"_rpt": "output_df_name1",
                                              "_txt": "output_df_name1"})
        """

        # Now let's process the output extensions and respective output DataFrames.
        for extension in output_extensions:
            new_table_name = self.__get_table_name_with_extension(table_name=output_table_name,
                                                                  extension=extension)

            # Get the teradataml output variable name corresponding to the extension.
            func_name = self.__get_output_attr_map_func_name()
            out_var = self.__multioutput_attr_map[func_name][extension]

            # Add the table name to the dynamic class as it's data member.
            self.__dyn_cls_data_members[out_var] = new_table_name

    def __process_output_argument(self):
        """
        DESCRIPTION:
            Function to process output argument(s) of a VALIB function.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self.__process_output_argument()
        """

        #
        # Note:
        #   So far all the functions we have seen, only one output database argument is present
        #   in SQL functions. In case in future, a function with more output database arguments
        #   are added, we will need to modify this function, especially the below piece and treat
        #   database arguments as we are processing the output table name arguments.
        #
        # Default SQL argument name for the output database argument.
        database_arg_name = "outputdatabase"
        if self.__sql_func_name in self.__output_arg_map:
            # Extract output database argument name for the function and use the same.
            database_arg_name = self.__output_arg_map[self.__sql_func_name]["db"]

        out_tablename = self.__get_temp_table_name()
        self.__db_name = self.__extract_db_tbl_name(table_name=out_tablename,
                                                    arg_name=database_arg_name,
                                                    extract_table=False)

        #
        # Note:
        #   So far all the functions visited, we observed following characteristics about
        #   processing the output tables by SQL function.
        #       1. Function produces only one table, with argument name as "outputtablename",
        #          which is our default case.
        #       2. Function produces only one table, with argument name different than
        #          "outputtablename". In such case, we use 'VALIB_FUNCTION_OUTPUT_ARGUMENT_MAP'
        #          to extract the SQL argument name for specifying the output table.
        #       3. Function produces multiple output tables with multiple output table arguments.
        #          In such case, we use 'VALIB_FUNCTION_OUTPUT_ARGUMENT_MAP' to extract the SQL
        #          argument names for specifying the output tables.
        #       4. Function produces multiple output tables with just one output table argument.
        #          In such cases, SQL uses the specified table name to create one of the output
        #          table and other output tables are created based on the pre-defined extensions
        #          which are appended to the specified table name and using the same.
        #
        # Now that we have processed the output database name argument, we will now process the
        # output table name argument(s).
        if self.__sql_func_name in self.__output_arg_map:
            # Extract the function output argument map.
            func_output_argument_map = self.__output_arg_map[self.__sql_func_name]

            # Extract output table argument name(s) for the function and use the same.
            table_arg_names = func_output_argument_map["tbls"]

            if not isinstance(table_arg_names, list):
                # This is a block to process functions producing multiple outputs with
                #   1. One output table argument.
                #   2. Use the same argument to produce other argument with some extension to it.
                #
                # Extract the table name from the generated name and add it to SQL syntax.
                table_name = self.__extract_db_tbl_name(table_name=out_tablename,
                                                        arg_name=table_arg_names)

                # Process all mandatory output extensions, irrespective of whether the function
                # is scoring or evaluator or any other function.
                if "mandatory_output_extensions" in func_output_argument_map:
                    mandatory_extensions = func_output_argument_map["mandatory_output_extensions"]
                    self.__process_output_extensions(table_name, mandatory_extensions)

                if "evaluator_output_extensions" in func_output_argument_map:
                    # We process either the table in "table_arg_names" or
                    # "evaluator_output_extensions" based on whether the function is evaluator
                    # function or not.
                    #
                    # If the function is:
                    #   1. evaluator function, process extensions as mentioned in evaluator based
                    #      output extensions.
                    #   2. NOT evaluator function (scoring or any other function):
                    #           a. with an entry in TERADATAML_VALIB_MULTIOUTPUT_ATTR_MAP,
                    #              process table in the variable "table_arg_names".
                    #           b. without an entry in  TERADATAML_VALIB_MULTIOUTPUT_ATTR_MAP,
                    #              process table as "result".
                    if self.__tdml_valib_name in self.__multioutput_attr_map:
                        evaluator_extensions = \
                            func_output_argument_map["evaluator_output_extensions"]
                        self.__process_output_extensions(table_name, evaluator_extensions)

                    elif self.__sql_func_name in self.__multioutput_attr_map:
                        out_var = \
                            self.__multioutput_attr_map[self.__sql_func_name][table_arg_names]
                        self.__dyn_cls_data_members[out_var] = table_name

                    else:
                        out_var = VC.DEFAULT_OUTPUT_VAR.value
                        self.__dyn_cls_data_members[out_var] = table_name

                else:
                    # If function produces only one output table, but uses different argument name.
                    func_name = self.__get_output_attr_map_func_name()
                    out_var = self.__multioutput_attr_map[func_name][table_arg_names]
                    self.__dyn_cls_data_members[out_var] = table_name
            else:
                # Function produces multiple outputs.
                for arg_name in table_arg_names:
                    # Generate a table name for each output and add the name to the dictionary
                    # for further processing and dynamic class creation.
                    out_tablename = self.__get_temp_table_name()
                    self.__process_dyn_cls_output_member(arg_name, out_tablename)
        else:
            # Let's use the default output table name argument "outputtablename".
            self.__process_dyn_cls_output_member("outputtablename", out_tablename,
                                                 VC.DEFAULT_OUTPUT_VAR.value)

    def __process_input_argument(self, df, database_arg_name, table_arg_name):
        """
        DESCRIPTION:
            Function to process input argument(s).

        PARAMETERS:
            df:
                Required Argument.
                Specifies the input teradataml DataFrame.
                Types: teradataml DataFrame

            database_arg_name:
                Required Argument.
                Specifies the name of the database argument.
                Types: String

            table_arg_name:
                Required Argument.
                Specifies the name of the table argument.
                Types: String

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self.__process_input_argument(df, "db", "table")
        """
        # Assuming that df._table_name always contains FQDN.
        db_name = UtilFuncs()._get_db_name_from_dataframe(df)

        self.__generate_valib_sql_argument_syntax(db_name, database_arg_name)
        self.__extract_db_tbl_name(df._table_name, table_arg_name, remove_quotes=True)

    def __process_other_arguments(self, **kwargs):
        """
        DESCRIPTION:
            Function to process other arguments.

        PARAMETERS:
            kwargs:
                Specifies the keyword arguments passed to a function.

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self.__process_other_arguments(arg1="string", arg2="db", arg3=2)
        """
        # Argument name dictionary.
        function_arguments = VC.TERADATAML_VALIB_FUNCTION_ARGUMENT_MAP.value
        try:
            func_arg_mapper = function_arguments[self.__sql_func_name]
        except:
            func_arg_mapper = None

        # Input argument name mapper extracted from VALIB_FUNCTION_MULTIINPUT_ARGUMENT_MAP.
        input_arguments = VC.VALIB_FUNCTION_MULTIINPUT_ARGUMENT_MAP.value
        try:
            func_input_arg_mapper = input_arguments[self.__sql_func_name]
            input_handling_required = True
        except:
            func_input_arg_mapper = None
            input_handling_required = False

        for arg in kwargs:
            arg_notin_arg_mapper = func_arg_mapper is not None and arg not in func_arg_mapper
            # Raise error if incorrect argument is passed.
            error_msg = "{0}() got an unexpected keyword argument '{1}'".\
                                                        format(self.__tdml_valib_name, arg)
            if input_handling_required:
                if arg_notin_arg_mapper and arg not in func_input_arg_mapper:
                    raise TypeError(error_msg)
            else:
                if arg_notin_arg_mapper:
                    raise TypeError(error_msg)

            # Arguments to ignore and the once which will not be processed.
            if arg.lower() in VC.IGNORE_ARGUMENTS.value:
                if arg.lower() == "outputstyle":
                    # If user has passed an argument "outputstyle", then we will ignore
                    # user value and then create a table as final outcome.
                    self.__generate_valib_sql_argument_syntax("table", "outputstyle")

                # Other arguments mentioned in 'ValibConstants.IGNORE_ARGUMENTS' will be ignored.
                continue

            # Pop each argument from kwargs.
            arg_value = kwargs.get(arg)

            if input_handling_required and arg in func_input_arg_mapper:
                # Argument provided is an input argument.
                # Let's get the names of the database and table arguments for this arg.
                self.__process_input_argument(df=arg_value,
                                              database_arg_name=
                                                        func_input_arg_mapper[arg]["database_arg"],
                                              table_arg_name=
                                                        func_input_arg_mapper[arg]["table_arg"])
            else:
                # Get the SQL argument name.
                arg_name = func_arg_mapper[arg] if isinstance(func_arg_mapper, dict) else arg
                self.__generate_valib_sql_argument_syntax(arg_value, arg_name)

    def __process_val_transformations(self, transformations, tf_tdml_arg, tf_sql_arg, data,
                                      data_arg="data"):
        """
        DESCRIPTION:
            Internal function to process the transformation(s) and generate the SQL
            argument syntax for the argument.

        PARAMETERS:
            transformations:
                Required Argument.
                Specifies the transformation(s) to be used for variable transformation.
                Types: FillNa

            tf_tdml_arg:
                Required Argument.
                Specifies the name of the argument that accepts transformation(s)
                to be used for variable transformation.
                Types: str

            tf_sql_arg:
                Required Argument.
                Specifies the SQL argument name used for the transformation(s).
                Types: str

            data:
                Required Argument.
                Specifies the input teradataml DataFrame used for Variable Transformation.
                Types: teradataml DataFrame

            data_arg:
                Optional Argument.
                Specifies the name of the input data argument.
                Default Value: "data"
                Types: string

        RETURNS:
            None

        RAISES:
            ValueError

        EXAMPLES:
            self.__process_val_transformations(fillna, "fillna", "nullreplacement", data)
        """
        # A list to contains SQL syntax of each transformation.
        tf_syntax_elements = []

        for tf in UtilFuncs._as_list(transformations):
            # Validates the existence of the columns used for transformation
            # in the input data.
            if tf.columns is not None:
                _Validators._validate_dataframe_has_argument_columns(
                    UtilFuncs._as_list(tf.columns), "columns in {}".format(tf_tdml_arg), data,
                    data_arg)
            tf_syntax_elements.append(tf._val_sql_syntax())

        # Add an entry for transformation in SQL argument syntax.
        self.__generate_valib_sql_argument_syntax(arg="".join(tf_syntax_elements),
                                                  arg_name=tf_sql_arg)

    def _execute_valib_function(self,
                                skip_data_arg_processing=False,
                                skip_output_arg_processing=False,
                                skip_other_arg_processing=False,
                                skip_func_output_processing=False,
                                skip_dyn_cls_processing=False,
                                **kwargs):
        """
        DESCRIPTION:
            Function processes arguments and executes the VALIB function.

        PARAMETERS:
            skip_data_arg_processing:
                Optional Argument.
                Specifies whether to skip data argument processing or not.
                Default is to process the data argument.
                When set to True, caller should make sure to process "data" argument and
                pass SQL argument and values as part of kwargs to this function.
                Default Value: False
                Types: bool

            skip_output_arg_processing:
                Optional Argument.
                Specifies whether to skip output argument processing or not.
                Default is to process the output arguments.
                When set to True, caller should make sure to process all output arguments and
                pass equivalent SQL argument and values as part of kwargs to this function.
                Default Value: False
                Types: bool

            skip_other_arg_processing:
                Optional Argument.
                Specifies whether to skip other argument processing or not.
                Default is to process the other arguments, i.e., kwargs.
                When set to True, caller should make sure to process all other arguments are
                processed internally by the function.
                Default Value: False
                Types: bool

            skip_func_output_processing:
                Optional Argument.
                Specifies whether to skip function output processing or not.
                Default is to process the same.
                When set to True, caller should make sure to process function output
                arguments. Generally, when this argument is set to True, one must also
                set "skip_dyn_cls_processing" to True.
                Default Value: False
                Types: bool

            skip_dyn_cls_processing:
                Optional Argument.
                Specifies whether to skip dynamic class processing or not.
                Default is to process the dynamic class, where it creates a dynamic
                class and an instance of the same and returns the same.
                When set to True, caller should make sure to process dynamic class and
                return an instance of the same.
                arguments.
                Default Value: False
                Types: bool

            kwargs:
                Specifies the keyword arguments passed to a function.

        RETURNS:
            None.

        RAISES:
            TeradataMlException, TypeError

        EXAMPLES:
            self._execute_valib_function(arg1="string", arg2="db", arg3=2)
        """
        if not skip_data_arg_processing:
            # Process data argument.
            try:
                data = kwargs.pop("data")
                if not isinstance(data, DataFrame):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                         ["data"], ["teradataml DataFrame"]))
                self.__process_input_argument(data, "database", "tablename")
            except KeyError:
                # Raise TeradataMlException.
                error_msg = Messages.get_message(MessageCodes.MISSING_ARGS, ["data"])
                raise TeradataMlException(error_msg, MessageCodes.MISSING_ARGS)

        if not skip_output_arg_processing:
            # Process output arguments.
            self.__process_output_argument()

        if not skip_other_arg_processing:
            # Process other arguments.
            self.__process_other_arguments(**kwargs)

        # If the function is evaluator function, add SQL argument "scoringmethod=evaluate".
        if self.__tdml_valib_name in self.__multioutput_attr_map: 
            scoring_method_values = VC.SCORING_METHOD_ARG_VALUE.value
            score_method = "non-default"
            if kwargs.get("gen_sql_only", False):
                score_method = "default"
            self.__generate_valib_sql_argument_syntax(scoring_method_values[score_method],
                                                      VC.SCORING_METHOD_ARG_NAME.value)

        # Generate the query.
        exec_out = self.__generate_execute_sp_query()

        if not skip_func_output_processing:
            # Process the function output DataFrames.
            self.__process_func_outputs(query_exec_output=exec_out)

        if not skip_dyn_cls_processing:
            # Generate the dynamic class and create a object of the
            # same and return the same.
            return self.__create_dynamic_valib_class()

    def Association(self, data, group_column, item_column, **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """
        # Add required arguments, i.e., positional arguments to kwargs for
        # further processing.
        kwargs["data"] = data
        kwargs["group_column"] = group_column
        kwargs["item_column"] = item_column

        # Get a new instance of _VALIB() class for function execution.
        valib_inst = self.__get_valib_instance("Association")

        # Add all arguments to dynamic class as data members.
        valib_inst.__dyn_cls_data_members = {}
        valib_inst.__dyn_cls_data_members.update(kwargs)

        # Get the value of "combinations", "no_support_results", "process_type"
        # parameters from kwargs.
        # These three parameters decide the number of output table generated.
        combinations = kwargs.get("combinations", 11)
        no_support_results = kwargs.get("no_support_results", True)
        process_type = kwargs.get("process_type", "all")
        support_result_prefix = kwargs.pop("support_result_prefix", "ml__valib_association")

        # Support table information based on the combinations.
        # This dict contains a list of names of the support output tables those will
        # be generated for a specific combination.
        combinations_support_tables = {
            11: ["_0_TO_1_SUPPORT", "_1_TO_1_SUPPORT"],
            12: ["_0_TO_1_SUPPORT", "_1_TO_1_SUPPORT", "_2_TO_1_SUPPORT"],
            13: ["_0_TO_1_SUPPORT", "_2_TO_1_SUPPORT", "_3_TO_1_SUPPORT"],
            14: ["_0_TO_1_SUPPORT", "_3_TO_1_SUPPORT", "_4_TO_1_SUPPORT"],
            21: ["_0_TO_1_SUPPORT", "_1_TO_1_SUPPORT", "_2_TO_1_SUPPORT"],
            22: ["_0_TO_1_SUPPORT", "_1_TO_1_SUPPORT", "_2_TO_2_SUPPORT"],
            23: ["_0_TO_1_SUPPORT", "_1_TO_1_SUPPORT", "_2_TO_1_SUPPORT", "_3_TO_2_SUPPORT"],
            31: ["_0_TO_1_SUPPORT", "_2_TO_1_SUPPORT", "_3_TO_1_SUPPORT"],
            32: ["_0_TO_1_SUPPORT", "_1_TO_1_SUPPORT", "_2_TO_1_SUPPORT", "_3_TO_2_SUPPORT"],
            41: ["_0_TO_1_SUPPORT", "_3_TO_1_SUPPORT", "_4_TO_1_SUPPORT"],
        }

        # This dict contains name of the support output table mapped to its corresponding
        # exposed output teradataml DataFrame name.
        support_result_names = {
            "_0_TO_1_SUPPORT": "support_result_01",
            "_1_TO_1_SUPPORT": "support_result_11",
            "_2_TO_1_SUPPORT": "support_result_21",
            "_3_TO_1_SUPPORT": "support_result_31",
            "_4_TO_1_SUPPORT": "support_result_41",
            "_2_TO_2_SUPPORT": "support_result_22",
            "_3_TO_2_SUPPORT": "support_result_32",
        }

        # Association rules produces various outputs. It generates:
        #   1. Support Tables
        #   2. Affinity Tables.

        # Support tables are generated when one of the following conditions occur:
        #   1. When "process_type" is 'support'. Then only two tables are generated as follows:
        #       a. <support_result_prefix>_1_ITEM_SUPPORT
        #       b. <support_result_prefix>_group_count
        #   2. When "no_support_results" is set to False.
        #       a. Multiple support table are generated based on the values passed
        #          to "combinations".
        #       b. A GROUP COUNT support table is also generated.

        # Here are some details on how and what outputs are generated:
        #   1. When "process_type" is 'support', then:
        #       a. No affinity tables are generated.
        #       b. Only two support tables are generated, which are named as:
        #           i. <support_result_prefix>_1_ITEM_SUPPORT
        #           ii. <support_result_prefix>_group_count
        #   2. When "no_support_results" is set to False.
        #       a. Affinity tables are generated.
        #       b. Multiple support table are generated, along with GROUP COUNT table.
        #   3. When "no_support_results" is set to True.
        #       a. Only affinity tables are generated.
        #       b. No support tables are generated.

        # Affinity tables are generated based on the values passed to "combinations"
        # parameter. Number of outputs generated is equal to the number of values passed
        # to "combinations".
        # Here are some cases to understand about this processing:
        #   1. If "combinations" parameter is not passed, i.e., is None, then only
        #      one output table is generated.
        #   2. If only one value is passed to "combinations" parameter, then only
        #      one output table is generated.
        #   3. If only one value is passed in a list to "combinations" parameter,
        #      then only one output table is generated.
        #   4. If list with multiple values is passed to "combinations" parameter,
        #      then number of output tables generated is equal to length of the list.
        #   5. If empty list is passed to "combinations" parameter, then SQL will
        #      take care of throwing appropriate exceptions.

        # Let's add the entry for the function in multi-output attribute mapper
        # as function produces multiple outputs.
        valib_inst.__multioutput_attr_map[valib_inst.__sql_func_name] = {}

        # To process output table parameters:
        #   1. Let's generate the output database name parameter first.
        #   2. Then generate the output table parameter.
        #   3. Once the arguments and it's values are generated, call
        #      _execute_valib_function() and make sure to skip the
        #      output argument processing only.

        # Let's first get the temp table name to be used for creating output
        # tables. Extract the database name and table name which will be used
        # as follows:
        #   1. Database name will be passed to SQL argument 'outputdatabase'.
        #   2. Table name extracted will be used to generate the values for
        #      SQL argument 'outputtablename'.
        out_tablename = valib_inst.__get_temp_table_name()

        # Add an entry for "outputdatabase" in SQL argument syntax.
        valib_inst.__db_name = valib_inst.__extract_db_tbl_name(table_name=out_tablename,
                                                                arg_name="outputdatabase",
                                                                extract_table=False,
                                                                remove_quotes=True)

        __table_name = UtilFuncs._extract_table_name(out_tablename).replace("\"", "")

        # Let's start processing the output table argument.
        # A list containing the output table name argument values.
        output_table_names = []

        # For Association we will create two new variables to store the output DataFrame
        # attribute names for support tables and affinity tables.
        #
        # This is done specifically for Association function as output attribute names
        # will vary based on the input values for "combinations" parameter. Thus, it will
        # help user to know the names of the output DataFrame attributes generated for
        # a specific function call.
        sup_table_attrs = "support_outputs"
        aff_table_attrs = "affinity_outputs"
        valib_inst.__dyn_cls_data_members[sup_table_attrs] = []
        valib_inst.__dyn_cls_data_members[aff_table_attrs] = []

        # Before we proceed here is a common function which will be used for
        # processing support tables.
        def process_support_tables(out_var, support_table_name):
            """ Internal function to process support tables. """
            valib_inst.__dyn_cls_data_members[out_var] = support_table_name
            valib_inst.__multioutput_attr_map[valib_inst.__sql_func_name][out_var] = out_var
            if out_var not in valib_inst.__dyn_cls_data_members[sup_table_attrs]:
                valib_inst.__dyn_cls_data_members[sup_table_attrs].append(out_var)
            GarbageCollector._add_to_garbagecollector(support_table_name,
                                                      TeradataConstants.TERADATA_TABLE)

        # GROUP_COUNT support table will be generated, when "process_type" is 'support'
        # or "no_support_results" is set to False.
        # Add the entry for the table in the output mappers.
        if process_type.lower() == "support" or not no_support_results:
            # Output attribute name of the group count table is "group_count".
            out_var = "group_count"
            grp_cnt_table_name = "{}_group_count".format(support_result_prefix)
            process_support_tables(out_var=out_var, support_table_name=grp_cnt_table_name)

        # Let's process the other support tables and affinity tables.
        if process_type.lower() == "support":
            # We are here that means only 1 item support table along with group count
            # support table is generated. Group count table entry is already added.
            # Output attribute name of the 1 item support table is "support_1_item".
            out_var = "support_1_item"
            sup_tbl_name = "{}_1_ITEM_SUPPORT".format(support_result_prefix)
            process_support_tables(out_var=out_var, support_table_name=sup_tbl_name)

            # Value for output table does not matter when "process_type" is 'support'.
            # No affinity tables are generated.
            output_table_names.append(__table_name)
        else:
            # Affinity tables and other support tables are generated only when "process_type"
            # is not equal to 'support'.

            # Process the affinity tables.
            for combination in UtilFuncs._as_list(combinations):
                # Generate the new output table name.
                extension = "_{}".format(combination)
                out_var = "{}{}".format(VC.DEFAULT_OUTPUT_VAR.value, extension)
                new_tbl_name = valib_inst.__get_table_name_with_extension(table_name=__table_name,
                                                                          extension=extension)

                # Add an entry for affinity output in mappers, which will produce the
                # output DataFrames.
                valib_inst.__dyn_cls_data_members[out_var] = new_tbl_name
                valib_inst.__multioutput_attr_map[valib_inst.__sql_func_name][out_var] = out_var
                valib_inst.__dyn_cls_data_members[aff_table_attrs].append(out_var)

                # Add the name of the output affinity table, which will be used as value
                # for the "outputtablename" argument.
                output_table_names.append(new_tbl_name)
            
                if not no_support_results:
                    # Other support tables are also generated and are not dropped in the end
                    # by Vantage, hence we will create output DataFrames for each one of those.
                    # Let's process all those support tables.
                    # 'combinations_support_tables' contains a name of list of support
                    # output tables those will be generated for a specific combination.
                    for sup_postfix in combinations_support_tables[combination]:
                        sup_out_var = support_result_names[sup_postfix]
                        sup_tbl_name = "{}{}".format(support_result_prefix, sup_postfix)
                        process_support_tables(out_var=sup_out_var, support_table_name=sup_tbl_name)

        # Add an entry for "outputtablename" in SQL argument syntax.
        valib_inst.__generate_valib_sql_argument_syntax(arg=output_table_names,
                                                        arg_name="outputtablename")

        # Execute the function, skip output argument and output dataframe processing.
        return valib_inst._execute_valib_function(skip_output_arg_processing=True, 
                                                  support_result_prefix=support_result_prefix, 
                                                  **kwargs)

    def KMeans(self, data, columns, centers, **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """
        # Add the required arguments to kwargs for further processing.
        kwargs["data"] = data
        kwargs["columns"] = columns
        kwargs["centers"] = centers

        # Get a new instance of _VALIB() class for function execution.
        new_valib_obj = self.__get_valib_instance("KMeans")

        # Add all arguments to dynamic class as data members.
        new_valib_obj.__dyn_cls_data_members = {}
        new_valib_obj.__dyn_cls_data_members.update(kwargs)

        centroids_data = kwargs.pop("centroids_data", None)

        # If there is no "centroids_data", do normal processing.
        if centroids_data is None:
            return new_valib_obj._execute_valib_function(**kwargs)

        # If "centroids_data" is provided, special handling for output argument is needed.
        if not isinstance(centroids_data, DataFrame):
            raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                 ["centroids_data"], ["teradataml DataFrame"]))

        # The following things has to be handled:
        # 1. The table in "centroids_data" is updated with new centroids and the same table
        #    is the result (new output) table.
        # Extract database name and add it to Valib SQL argument syntax.
        new_valib_obj.__db_name = new_valib_obj.__extract_db_tbl_name(
                                                        table_name=centroids_data._table_name,
                                                        arg_name="outputdatabase",
                                                        extract_table=False,
                                                        remove_quotes=True)

        # Extract table name and add it to Valib SQL argument syntax.
        table_name = new_valib_obj.__extract_db_tbl_name(table_name=centroids_data._table_name,
                                                         arg_name="outputtablename",
                                                         extract_table=True,
                                                         remove_quotes=True)

        # Since output argument processing will be skipped, table name is added in dynamic
        # class data member "result", which will be replaced with DataFrame while processing
        # function outputs in the function _execute_valib_function.
        new_valib_obj.__dyn_cls_data_members[VC.DEFAULT_OUTPUT_VAR.value] = table_name

        # 2. Execute the valib function call based on the arguments along with newly added
        #    the SQL argument 'continuation=true' and process output and other arguments
        #    related information.
        return new_valib_obj._execute_valib_function(skip_output_arg_processing=True,
                                                     continuation=True,
                                                     **kwargs)

    def DecisionTreePredict(self, data, model, **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """
        # Add the required arguments to kwargs for further processing.
        kwargs["data"] = data
        kwargs["model"] = model

        # Get a new instance of _VALIB() class for function execution.
        new_valib_obj = self.__get_valib_instance("DecisionTreePredict")

        # Add all arguments to dynamic class as data members.
        new_valib_obj.__dyn_cls_data_members = {}
        new_valib_obj.__dyn_cls_data_members.update(kwargs)

        return new_valib_obj._execute_valib_function(profile=True, **kwargs)

    def DecisionTreeEvaluator(self, data, model, **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """
        # Add the required arguments to kwargs for further processing.
        kwargs["data"] = data
        kwargs["model"] = model

        # Get a new instance of _VALIB() class for function execution.
        new_valib_obj = self.__get_valib_instance("DecisionTreeEvaluator")

        # Add all arguments to dynamic class as data members.
        new_valib_obj.__dyn_cls_data_members = {}
        new_valib_obj.__dyn_cls_data_members.update(kwargs)

        return new_valib_obj._execute_valib_function(profile=True, **kwargs)

    def __validate_overlap_arguments(self, data_val, data_arg, columns_val, columns_arg,
                                     is_optional = True):
        """
        DESCRIPTION:
            Internal function to validate pair of data{i} and columns{i} arguments.

        PARAMETERS:
            data_val:
                Required Argument.
                Specifies the teradataml Dataframe containing input data.
                Types: teradataml Dataframe

            data_arg:
                Required Argument.
                Specifies the argument name for the teradataml DataFrame specified in the
                argument "data_val".
                Types: str

            columns_val:
                Required Argument.
                Specifies the list of column(s) present in the DataFrame "data_val".
                Types: str OR list of strings (str)

            columns_arg:
                Required Argument.
                Specifies the argument name for the columns specified in the
                argument "columns_val".
                Types: str

            is_optional:
                Optional Argument.
                Specifies whether the values in arguments "data_val" and "columns_val" are
                optional in Overlap() function.
                If True, the values in these arguments should be validated as optional arguments
                in Overlap() function. Otherwise, these values are considered as required
                arguments.
                Default Value: True
                Types: bool

        RETURNS:
            None.

        EXAMPLES:
            valib.__validate_overlap_arguments(data_val=data, data_arg="data",
                                               columns_val=columns, columns_arg="columns",
                                               is_optional=False)
        """
        # Create argument information matrix to do parameter checking.
        __arg_info_matrix = []
        __arg_info_matrix.append([data_arg, data_val, is_optional, (DataFrame)])
        __arg_info_matrix.append([columns_arg, columns_val, is_optional, (str, list), True])

        _Validators._validate_function_arguments(arg_list=__arg_info_matrix)

        _Validators._validate_dataframe_has_argument_columns(data=data_val,
                                                             data_arg=data_arg,
                                                             columns=columns_val,
                                                             column_arg=columns_arg,
                                                             is_partition_arg=False)

    # TODO- Delete LogRegPredict function definition if Jira TDAF-7867 is resolved.
    def LogRegPredict(self, **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """

        # Get a new instance of _VALIB() class for function execution.
        valib_inst = self.__get_valib_instance("LogRegPredict")

        # Add all arguments to dynamic class as data members.
        valib_inst.__dyn_cls_data_members = {}
        valib_inst.__dyn_cls_data_members.update(kwargs)

        # Setting scoringmethod to "score" if gen_sql_only is True.
        gen_sql_only = kwargs.get("gen_sql_only", False)
        if gen_sql_only:
            valib_inst.__generate_valib_sql_argument_syntax(arg="score",
                                                            arg_name="scoringmethod")

        return valib_inst._execute_valib_function(**kwargs)

    def Overlap(self, data1, columns1, **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """
        # Validate the required arguments - data1 and columns1.
        # Other arguments are validated as and when they are being processed.
        self.__validate_overlap_arguments(data_val=data1, data_arg="data1",
                                          columns_val=columns1, columns_arg="columns1",
                                          is_optional=False)

        kwargs["data1"] = data1
        kwargs["columns1"] = columns1

        # Each columns argument can take string or list of strings.
        # Ensure all columns related arguments to be list of one or more strings.
        columns1 = UtilFuncs._as_list(columns1)

        valib_inst = self.__get_valib_instance("Overlap")

        # Add all arguments to dynamic class as data members.
        valib_inst.__dyn_cls_data_members = {}
        valib_inst.__dyn_cls_data_members.update(kwargs)

        parse_kwargs = True
        ind = 1
        database_names = []
        table_names = []
        column_names_df = []

        """
        The argument names are data1, data2, ..., dataN and columns1, columns2, ... columnsN
        corresponding to each data arguments.
        Note:
            1.  The number of data arguments should be same as that of columns related arguments.
            2.  The number of columns in each of the columns related arguments (including 
                "columns1" argument) should be same.
        """
        while parse_kwargs:
            data_arg_name = "data{}".format(str(ind))
            data_arg_value = kwargs.pop(data_arg_name, None)
            if data_arg_value is None:
                parse_kwargs = False
            else:
                columns_arg_name = "columns{}".format(str(ind))
                columns_arg_value = kwargs.pop(columns_arg_name, None)

                # Raise error if dataN is present and columnsN is not present.
                if columns_arg_value is None:
                    err_ = Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING,
                                                columns_arg_name, data_arg_name)
                    raise TeradataMlException(err_, MessageCodes.DEPENDENT_ARG_MISSING)

                self.__validate_overlap_arguments(data_val=data_arg_value,
                                                  data_arg=data_arg_name,
                                                  columns_val=columns_arg_value,
                                                  columns_arg=columns_arg_name)

                # Each columns argument can take string or list of strings.
                # Ensure all columns related arguments to be list of one or more strings.
                columns_arg_value = UtilFuncs._as_list(columns_arg_value)

                if len(columns_arg_value) != len(columns1):
                    err_ = Messages.get_message(MessageCodes.INVALID_LENGTH_ARGS,
                                             "'columns1', 'columns2', ..., 'columnsN'")
                    raise TeradataMlException(err_ ,MessageCodes.INVALID_LENGTH_ARGS)

                # If all the validations are done,
                #   1. extract database names
                #   2. extract table names
                #   3. generate SQL syntax for 'columns' argument.
                database_names.append(UtilFuncs()._get_db_name_from_dataframe(data_arg_value))
                __table_name = UtilFuncs._extract_table_name(data_arg_value._table_name).\
                                                                                replace("\"", "")
                table_names.append(__table_name)
                column_names_df.append("{" + ",".join(columns_arg_value) + "}")

            ind = ind + 1

        # gensqlonly implementation.
        gen_sql_only = kwargs.pop("gen_sql_only", False)
        if gen_sql_only:
            valib_inst.__generate_valib_sql_argument_syntax(arg=str(gen_sql_only),
                                                            arg_name="gensqlonly")
        charset = kwargs.pop("charset", None)
        # Raise error if there are additional arguments.
        if len(kwargs) != 0:
            err_ = "The keyword arguments for Overlap() should have data1, data2, ..., dataN " \
                   "and corresponding columns1, columns2, ..., columnsN. " \
                   "Found additional arguments {}."
            raise TypeError(err_.format(list(kwargs.keys())))

        # Generate SQL syntax for SQL arguments database, tablename and columns.
        valib_inst.__generate_valib_sql_argument_syntax(arg=",".join(database_names),
                                                        arg_name="database")
        valib_inst.__generate_valib_sql_argument_syntax(arg=",".join(table_names),
                                                        arg_name="tablename")
        valib_inst.__generate_valib_sql_argument_syntax(arg=",".join(column_names_df),
                                                        arg_name="columns")
        # Generate clause of charset.
        if charset:
            valib_inst.__generate_valib_sql_argument_syntax(arg=charset,
                                                            arg_name="charset")

        return valib_inst._execute_valib_function(skip_data_arg_processing=True,
                                                  skip_other_arg_processing=True)

    def Transform(self, data, bins=None, derive=None, one_hot_encode=None, fillna=None,
                  label_encode=None, rescale=None, retain=None, sigmoid=None, zscore=None, 
                  **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """
        # Argument Validations
        # Note:
        #   Commented code is kept for future purpose. Once all commented code is updated
        #   note will be removed as well.
        arg_info_matrix = []
        arg_info_matrix.append(["data", data, False, (DataFrame)])
        arg_info_matrix.append(["bins", bins, True, (Binning, list)])
        arg_info_matrix.append(["derive", derive, True, (Derive, list)])
        arg_info_matrix.append(["one_hot_encode", one_hot_encode, True, (OneHotEncoder, list)])
        arg_info_matrix.append(["fillna", fillna, True, (FillNa, list)])
        arg_info_matrix.append(["rescale", rescale, True, (MinMaxScalar, list)])
        arg_info_matrix.append(["label_encode", label_encode, True, (LabelEncoder, list)])
        arg_info_matrix.append(["retain", retain, True, (Retain, list)])
        arg_info_matrix.append(["sigmoid", sigmoid, True, (Sigmoid, list)])
        arg_info_matrix.append(["zscore", zscore, True, (ZScore, list)])

        # Argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Add "data" to kwargs for further processing.
        kwargs["data"] = data

        # Get a new instance of _VALIB() class for function execution.
        valib_inst = self.__get_valib_instance("Transform")

        # Add all arguments to dynamic class as data members.
        valib_inst.__dyn_cls_data_members = {}
        valib_inst.__dyn_cls_data_members.update(kwargs)
        valib_inst.__dyn_cls_data_members["bins"] = bins
        valib_inst.__dyn_cls_data_members["derive"] = derive
        valib_inst.__dyn_cls_data_members["one_hot_encode"] = one_hot_encode
        valib_inst.__dyn_cls_data_members["fillna"] = fillna
        valib_inst.__dyn_cls_data_members["label_encode"] = label_encode
        valib_inst.__dyn_cls_data_members["rescale"] = rescale
        valib_inst.__dyn_cls_data_members["retain"] = retain
        valib_inst.__dyn_cls_data_members["sigmoid"] = sigmoid
        valib_inst.__dyn_cls_data_members["zscore"] = zscore

        # Add "outputstyle" argument to generate output table.
        valib_inst.__generate_valib_sql_argument_syntax(arg="table", arg_name="outputstyle")

        # Bin Coding Transformation
        if bins is not None:
            valib_inst.__process_val_transformations(bins, "bins", "bincode", data)

        # Derive Transformation
        if derive is not None:
            valib_inst.__process_val_transformations(derive, "derive", "derive", data)

        # OneHotEncoder Transformation
        if one_hot_encode is not None:
            valib_inst.__process_val_transformations(one_hot_encode, "one_hot_encode", "designcode", data)
            
        # Null Replacement Transformation
        if fillna is not None:
            valib_inst.__process_val_transformations(fillna, "fillna", "nullreplacement", data)

        # LabelEncoder Transformation
        if label_encode is not None:
            valib_inst.__process_val_transformations(label_encode, "label_encode", "recode", data)
            
        # MinMaxScalar Transformation
        if rescale is not None:
            valib_inst.__process_val_transformations(rescale, "rescale", "rescale", data)
            
        # Retain Transformation
        if retain is not None:
            valib_inst.__process_val_transformations(retain, "retain", "retain", data)
            
        # Sigmoid Transformation
        if sigmoid is not None:
            valib_inst.__process_val_transformations(sigmoid, "sigmoid", "sigmoid", data)
            
        # ZScore Transformation
        if zscore is not None:
            valib_inst.__process_val_transformations(zscore, "zscore", "zscore", data)
            
        # Execute the function, just do not process the output dataframes
        # and dynamic class creation for the function.
        return valib_inst._execute_valib_function(**kwargs)

    def XmlToHtmlReport(self, data, analysis_type, **kwargs):
        """
        Please refer to Teradata Python Function Reference guide for Documentation.
        Reference guide can be found at: https://docs.teradata.com
        """
        # Add the required arguments to kwargs for further processing.
        kwargs["data"] = data
        kwargs["analysis_type"] = analysis_type
        # Dict that maps teradataml Class name to SQL name.
        tdml_classname_to_sql_name = {"DecisionTree": "decisiontree",
                                     "DecisionTreeEvaluator": "decisiontreescore",
                                     "PCA": "factor",
                                     "PCAEvaluator": "factorscore",
                                     "LinReg": "linear",
                                     "LogReg": "logistic",
                                     "LogRegEvaluator": "logisticscore"}

        if analysis_type in tdml_classname_to_sql_name:
            kwargs["analysis_type"] = tdml_classname_to_sql_name[analysis_type]

        # Get a new instance of _VALIB() class for function execution.
        new_valib_obj = self.__get_valib_instance("XmlToHtmlReport")

        # Add all arguments to dynamic class as data members.
        new_valib_obj.__dyn_cls_data_members = {}
        new_valib_obj.__dyn_cls_data_members.update(kwargs)

        return new_valib_obj._execute_valib_function(**kwargs)

# Define an object of type _VALIB, that will allow user to execute any VALIB function.
valib = _VALIB()
