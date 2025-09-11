"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements _AnlyFuncMetadata for representing the metadata (json data)
of analytic function. All the functions/API's looking to extract the json data
should look at corresponding API's in _AnlyFuncMetadata.
"""
from collections import OrderedDict
import json, os, sys
from pathlib import Path
from re import sub
from teradataml.analytics.json_parser import PartitionKind, SqleJsonFields, UAFJsonFields, utils
from teradataml.analytics.json_parser.analytic_functions_argument import _AnlyFuncArgument,\
    _AnlyFuncInput, _AnlyFuncOutput, _DependentArgument, _AnlyFuncArgumentUAF, _AnlyFuncOutputUAF, \
    _AnlyFuncInputUAF
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.constants import TeradataAnalyticFunctionTypes, TeradataUAFSpecificArgs,\
    TeradataAnalyticFunctionInfo
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.utils import UtilFuncs
from teradataml.utils.validators import _Validators
from teradataml.utils.dtypes import _ListOf

class _PairedFunction:
    """
    Class to hold the paired function information for analytic functions.
    It holds the information about the relation between the analytic
    functions.
    """
    def __init__(self, function_relation, params):
        """
        DESCRIPTION:
            Constructor of the class.

        PARAMETERS:
            function_relation:
                Required Argument.
                Specifies the relation of the paired function.
                Type: str

            params:
                Required Argument.
                Specifies the reference_function, input_arguments,
                and model_output_argument wrt the paired function.
                Type: dict
        """
        self.function_relation = function_relation
        self.reference_function = params.get("reference_function", [])
        self.input_arguments = params.get("input_arguments", [])
        self.model_output_arguments = params.get("model_output_arguments", [])

    @property
    def arguments(self):
        """
        DESCRIPTION:
            Function to get the input argument of paired function and output argument of referenced function.
        """
        for inp_arg, out_arg in zip(self.input_arguments, self.model_output_arguments):
            yield inp_arg, out_arg


class _AnlyFuncMetadata:
    """ Class to hold the json data. """

    # A class variable to store the r function names and their function names.
    # Note that this is a class variable so it is accessable from all the objects
    # of _AnlyFuncMetadata.
    _reference_function_names = {
        "aa.glm": "GLM",
        "aa.forest": "DecisionForest",
        "aa.naivebayes.textclassifier.train": "NaiveBayesTextClassifier",
        "aa.svm.sparse.train": "SVMSparse"
    }
    # A class variable to store the SQLE JSON Fields.
    json_fields = SqleJsonFields()

    def __init__(self, json_data, json_file, func_type=None):
        """
        DESCRIPTION:
            Constructor for the class.

        PARAMETERS:
            json_data:
                Required Argument.
                Specifies the json content of analytic function.
                Types: dict

            json_file:
                Required Argument.
                Specifies the absolute path of the json file.
                Types: str

            func_type:
                Optional Argument.
                Specifies the type of analytic function.
                Permitted Values: ['FASTPATH', 'TABLE_OPERATOR', 'UAF']
                Types: str
        """

        # Validate func_type.
        arg_info_matrix = []
        arg_info_matrix.append(
            ["func_type", func_type, False, 
             (str, type(None)), True, [TeradataAnalyticFunctionTypes.SQLE.value,
                                       TeradataAnalyticFunctionTypes.TABLEOPERATOR.value,
                                       TeradataAnalyticFunctionTypes.UAF.value,
                                       TeradataAnalyticFunctionTypes.BYOM.value,
                                       TeradataAnalyticFunctionTypes.STORED_PROCEDURE.value,
                                       None]])
        arg_info_matrix.append(["json_file", json_file, False, str, True])
        _Validators._validate_function_arguments(arg_info_matrix)

        # Get the appropriate JSON Fields based on the class of the object i.e UAF or SQLE/TABLE_OPERATOR.
        self.short_description = json_data[self.json_fields.SHORT_DESCRIPTION]
        self.long_description = json_data[self.json_fields.LONG_DESCRIPTION]
        # Store Input Table data objects.
        self.__input_tables = []
        # Store Output Table data objects.
        self.__output_tables = []
        # To store mapping between sql name and lang names of Input Tables.
        self.__input_table_lang_names = {}
        # Store rest of function argument objects.
        self.__arguments = []

        # JSON Object
        self.json_object = json_data
        self._json_file = json_file

        # Store formula args if applicable.
        self.__formula_args = []

        # Variable to hold the name of the argument as key and the corresponding section as
        # value. This is used for checking duplicate arguments.
        self.__arguments_and_sections = {}
        self.func_type = json_data[self.json_fields.FUNCTION_TYPE].lower() if func_type is None else func_type.lower()
        self.sql_function_name = json_data[self.json_fields.FUNC_NAME]
        self.func_category = self.json_object.get(self.json_fields.FUNCTION_CATEGORY, None)

        # Validating func_type and sql_function_name
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["func_type", self.func_type, True, str])
        self.__arg_info_matrix.append(["sql_function_name", self.sql_function_name, False, str])
        _Validators._validate_function_arguments(self.__arg_info_matrix)

        # Generating func_name from the sql_function_name
        self.func_name = self._get_function_name()
        self.__database_version = Path(self._json_file).parts[-2]
        self._func_type_specific_setup()

        # Call a function read JSON and collect arguments, input
        # and output table arguments.
        self.__parse_json()
        self.__function_params = OrderedDict()
        # Lets store the r function name and the function names in a mapper.

        # Storing the paired function information
        self.__paired_functions = []

    def set_paired_functions(self, params):
        """
        DESCRIPTION:
            Function to set the 'paired_function' attribute of _AnlyFuncMetadata.

        PARAMETERS:
            params:
                Required Argument
                Specifies the paired function information like the reference_function,
                input_arguments and model_output_arguments.
                Type: dict

        RETURNS:
            None.

        RAISES:
            None.
        """

        # params as
        #   {
        #     "predict": {
        #       "reference_function": "DecisionForestPredict",
        #       "input_arguments": ["object"],
        #       "model_output_arguments": ["result"]
        #     }
        for paired_function_name, paired_function_params in params.items():
            self.__paired_functions.append(
                _PairedFunction(paired_function_name, paired_function_params))

    def get_paired_functions(self):
        """
        DESCRIPTION:
            Function to get the '__paired_functions' attribute of _AnlyFuncMetadata class.

        RETURNS:
            list of instances
        """
        return self.__paired_functions

    def _func_type_specific_setup(self):
        """
        DESCRIPTION:
            Additional setup required for SQLE and Table Operator functions.

        RETURNS:
            class OR None

        RAISES:
            None
        """
        # TODO: Output schema is not required so not storing it for now. If we need it in
        #       future, then it can be enabled.
        # Store output schema of the function
        # self.standard_output_schema = self.json_object.get(self.json_fields.OUTPUT_SCHEMA)
        self._is_view_supported = self.json_object.get("supports_view", True)
        self.__is_driver_function = self.json_object.get("function_type", "").lower() == "driver"
        self.__refernce_function_name = self.json_object.get("ref_function_r_name")
        self.__r_function_name = self.json_object.get("function_r_name")
        _AnlyFuncMetadata._reference_function_names[self.__r_function_name] = self.func_name

    def get_reference_function_class(self):
        """
        DESCRIPTION:
            Function to get the reference function class. This function checks if the function
            accepts any other function as input. If it accepts, it then returns the class of
            the referenced function.

        RETURNS:
            class OR None

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").get_reference_function_class()
        """
        reference_function = _AnlyFuncMetadata._reference_function_names.get(self.__refernce_function_name)
        if reference_function:
            return UtilFuncs._get_class(reference_function, supress_isinstance_check=True)

    def _get_argument_value(self, argument_properties, property, section, mandatory=True, default_value=None):
        """
        DESCRIPTION:
            Function to get the argument value from the json data. This function, checks
            the argument is a mandatory argument or not. If mandatory and not found in json
            data, raises an error otherwise either returns value or default value.

        PARAMETERS:
            argument_properties:
                Required Argument.
                Specifies json content of one of the below mentioned:
                    * Input argument.
                    * Output table.
                    * Input table.
                Types: dict

            property:
                Required Argument.
                Specifies the argument name to look in "argument_properties"
                Types: str

            section:
                Required Argument.
                Specifies the section of the json to which "property" belongs to.
                Types: str

            mandatory:
                Required Argument.
                Specifies whether "property" is a mandatory field in "argument_properties" or not.
                Default Value: True
                Types: bool

            default_value:
                Required Argument.
                Specifies the default value of "property".
                Types: str OR int OR float OR bool

        RETURNS:
            str OR bool OR int OR float OR list

        RAISES:
            TeradataMlException.

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json")._get_argument_value(
            json_data, "defaultValue", "input_tables",  False)
        """
        if property not in argument_properties and mandatory:
            error_message = Messages.get_message(MessageCodes.MISSING_JSON_FIELD,
                                                 property,
                                                 section)

            raise TeradataMlException(error_message, MessageCodes.MISSING_JSON_FIELD)

        return argument_properties.get(property, default_value)

    def _parse_arguments(self):
        """
        DESCRIPTION:
            Function to parse and store the argument in json file. This function first validates
            whether argument is required for analytic function or not. If required, then arguments
            section in json data is parsed and object of _AnlyFuncArgument is created and stored.
        RETURNS:
            None
        RAISES:
            TeradataMlException.
        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").__parse_arguments()
        """
        section = self.json_fields.ARGUMENT_CLAUSES
        for argument in self.json_object.get(self.json_fields.ARGUMENT_CLAUSES, []):
            is_argument_required = argument.get(self.json_fields.USEINR, False)

            # Append argument to list if useInR is True.
            if is_argument_required:
                use_inR = is_argument_required

                sql_name = self._get_argument_value(argument, self.json_fields.NAME, section)

                regex_match = self._get_argument_value(argument, self.json_fields.REGEX_MATCH, section, False)

                match_name = self._get_argument_value(argument, self.json_fields.MATCH_NAME, section, False)

                lang_name = self._get_argument_value(argument, self.json_fields.LANG_NAME, section, False)
                lang_name = lang_name if lang_name is not None else self._get_pythonic_name_arg_name(
                    self._get_argument_value(argument, self.json_fields.R_NAME, section), is_regex_match=regex_match)

                is_required = self._get_argument_value(argument, self.json_fields.IS_REQUIRED, section)

                sql_description = self._get_argument_value(argument, self.json_fields.DESCRIPTION, section)

                r_description = self._get_argument_value(argument, self.json_fields.R_DESCRIPTION, section)

                datatype = self._get_argument_value(argument, self.json_fields.DATATYPE, section)

                r_order_num = self._get_argument_value(argument, self.json_fields.R_ORDER_NUM, section)

                # Look for default value. If default value is not available, the look for default values.
                # If default values found, the consider the first element as default value.
                default_value = self._get_argument_value(argument, self.json_fields.DEFAULT_VALUE, section, False)
                if isinstance(default_value, list):
                    default_value = default_value[0]

                # Json files can specify INFINITY as lower bound. So, convert it to appropriate
                # type in python.
                lower_bound = self._get_argument_value(argument, self.json_fields.LOWER_BOUND, section, False)
                lower_bound = UtilFuncs._get_negative_infinity() if lower_bound == self.json_fields.INFINITY\
                    else lower_bound

                # Json files can specify INFINITY as upper bound. So, convert it to appropriate
                # type in python.
                upper_bound = self._get_argument_value(argument, self.json_fields.UPPER_BOUND, section, False)
                upper_bound = UtilFuncs._get_positive_infinity() if upper_bound == self.json_fields.INFINITY\
                    else upper_bound

                r_default_value = self._get_argument_value(argument, self.json_fields.R_DEFAULT_VALUE, section,
                                                           False)

                allows_lists = self._get_argument_value(argument, self.json_fields.ALLOWS_LISTS, section, False,
                                                        False)

                allow_padding = self._get_argument_value(argument, self.json_fields.ALLOW_PADDING, section, False,
                                                         False)

                r_formula_usage = self._get_argument_value(argument, self.json_fields.R_FORMULA_USAGE, section, False,
                                                           False)

                allow_nan = self._get_argument_value(argument, self.json_fields.ALLOW_NAN, section, False, False)

                check_duplicate = self._get_argument_value(argument, self.json_fields.CHECK_DUPLICATE, section, False,
                                                           False)

                is_output_column = self._get_argument_value(argument, self.json_fields.IS_OUTPUT_COLUMN, section, False,
                                                            False)

                lower_bound_type = self._get_argument_value(argument, self.json_fields.LOWER_BOUND_TYPE, section, False)

                upper_bound_type = self._get_argument_value(argument, self.json_fields.UPPER_BOUND_TYPE, section, False)

                required_length = self._get_argument_value(argument, self.json_fields.REQUIRED_LENGTH, section, False, 0)

                match_length_of_argument = self._get_argument_value(
                    argument, self.json_fields.MATCH_LENGTH_OF_ARGUMENT, section, False, False)

                permitted_values = self._get_argument_value(argument, self.json_fields.PERMITTED_VALUES, section, False)

                target_table = self._get_argument_value(argument, self.json_fields.TARGET_TABLE, section, False)

                allowed_types = self._get_argument_value(argument, self.json_fields.ALLOWED_TYPES, section, False)

                allowed_type_groups = self._get_argument_value(argument, self.json_fields.ALLOWED_TYPE_GROUPS, section,
                                                               False)

                alternate_sql_name = self._get_argument_value(argument, self.json_fields.ALTERNATE_NAMES, section, False)

                # Check for duplicate arguments.
                self._validate_duplicate_argument(lang_name, self.json_fields.ARGUMENT_CLAUSES)

                # Get the lang name of target table if target table exists for given argument.
                target_table_lang_name = None
                if target_table and len(target_table) > 0:
                    target_table_lang_name = self.__get_input_table_lang_name(sql_name=target_table[0])

                if sql_name.lower() == self.json_fields.SEQUENCE_INPUT_BY or\
                        sql_name.lower() == self.json_fields.UNIQUE_ID:
                    for j in range(len(self.input_tables)):
                        r_order_num = (r_order_num * 10) + j

                        sql_name = self.input_tables[j].get_sql_name()
                        datatype = "COLUMN_NAMES"

                        self.arguments.append(_AnlyFuncArgument(default_value=default_value,
                                                                  permitted_values=permitted_values,
                                                                  lower_bound=lower_bound,
                                                                  lower_bound_type=lower_bound_type,
                                                                  upper_bound=upper_bound,
                                                                  upper_bound_type=upper_bound_type,
                                                                  allow_nan=allow_nan,
                                                                  required_length=required_length,
                                                                  match_length_of_argument=match_length_of_argument,
                                                                  sql_name=sql_name,
                                                                  is_required=is_required,
                                                                  sql_description=sql_description,
                                                                  lang_description=r_description,
                                                                  datatype=datatype,
                                                                  allows_lists=allows_lists,
                                                                  allow_padding=allow_padding,
                                                                  use_in_r=use_inR,
                                                                  r_formula_usage=r_formula_usage,
                                                                  r_default_value=r_default_value,
                                                                  target_table=target_table,
                                                                  target_table_lang_name=target_table_lang_name,
                                                                  check_duplicate=check_duplicate,
                                                                  allowed_types=allowed_types,
                                                                  allowed_type_groups=allowed_type_groups,
                                                                  r_order_num=r_order_num,
                                                                  is_output_column=is_output_column,
                                                                  alternate_sql_name=alternate_sql_name,
                                                                  lang_name=lang_name,
                                                                  regex_match=regex_match,
                                                                  match_name=match_name))
                else:
                    self.arguments.append(_AnlyFuncArgument(default_value=default_value,
                                                              permitted_values=permitted_values,
                                                              lower_bound=lower_bound,
                                                              lower_bound_type=lower_bound_type,
                                                              upper_bound=upper_bound,
                                                              upper_bound_type=upper_bound_type,
                                                              allow_nan=allow_nan,
                                                              required_length=required_length,
                                                              match_length_of_argument=match_length_of_argument,
                                                              sql_name=sql_name,
                                                              is_required=is_required,
                                                              sql_description=sql_description,
                                                              lang_description=r_description,
                                                              datatype=datatype,
                                                              allows_lists=allows_lists,
                                                              allow_padding=allow_padding,
                                                              lang_name=lang_name,
                                                              use_in_r=use_inR,
                                                              r_formula_usage=r_formula_usage,
                                                              r_default_value=r_default_value,
                                                              target_table=target_table,
                                                              target_table_lang_name=target_table_lang_name,
                                                              check_duplicate=check_duplicate,
                                                              allowed_types=allowed_types,
                                                              allowed_type_groups=allowed_type_groups,
                                                              r_order_num=r_order_num,
                                                              is_output_column=is_output_column,
                                                              alternate_sql_name=alternate_sql_name,
                                                              regex_match=regex_match,
                                                              match_name=match_name))


    def _parse_input_tables(self):
        """
        DESCRIPTION:
            Function to parse and store the input tables in json file. This function first validates
            whether input table is required for analytic function or not. If required, then input tables
            section in json data is parsed and object of _AnlyFuncInput is created and stored.

        RETURNS:
            None

        RAISES:
            TeradataMlException.

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").__parse_input_tables()
        """
        section = self.json_fields.INPUT_TABLES
        for input_table_param in self.json_object.get(self.json_fields.INPUT_TABLES, []):
            is_input_table_required = input_table_param.get(self.json_fields.USEINR, False)

            # Append argument/input table to list if useInR is True.
            if is_input_table_required:
                use_InR = is_input_table_required

                r_order_num = self._get_argument_value(input_table_param, self.json_fields.R_ORDER_NUM, section)

                sql_name = self._get_argument_value(input_table_param, self.json_fields.NAME, section)

                is_required = self._get_argument_value(input_table_param, self.json_fields.IS_REQUIRED, section,
                                                       mandatory=False, default_value=True)


                sql_description = self._get_argument_value(input_table_param, self.json_fields.DESCRIPTION, section)

                r_description = self._get_argument_value(input_table_param, self.json_fields.R_DESCRIPTION, section)

                datatype = self._get_argument_value(input_table_param, self.json_fields.DATATYPE, section)

                required_input_kind = self._get_argument_value(
                    input_table_param, self.json_fields.REQUIRED_INPUT_KIND, section, False, None)

                partition_by_one = self._get_argument_value(
                    input_table_param, self.json_fields.PARTITION_BY_ONE, section, False, False)

                partition_by_one_inclusive = self._get_argument_value(
                    input_table_param, self.json_fields.PARTITION_BY_ONE_INCLUSIVE, section, False, False)

                is_ordered = self._get_argument_value(input_table_param, self.json_fields.IS_ORDERED, section, False,
                                                      False)

                is_local_ordered = self._get_argument_value(input_table_param, self.json_fields.IS_LOCAL_ORDERED,
                                                            section, False, False)

                hash_by_key = self._get_argument_value(input_table_param, self.json_fields.HASH_BY_KEY, section, False,
                                                       False)

                allows_lists = self._get_argument_value(input_table_param, self.json_fields.ALLOWS_LISTS, section, False,
                                                        False)

                lang_name = self._get_pythonic_name_arg_name(
                    self._get_argument_value(input_table_param, self.json_fields.R_NAME, section))

                r_formula_usage = self._get_argument_value(input_table_param, self.json_fields.R_FORMULA_USAGE, section,
                                                           False, False)

                alternate_sql_name = self._get_argument_value(input_table_param, self.json_fields.ALTERNATE_NAMES,
                                                              section, False)

                # Check for duplicate arguments.
                self._validate_duplicate_argument(lang_name, self.json_fields.INPUT_TABLES)

                self.input_tables.append(_AnlyFuncInput(required_input_kind=required_input_kind,
                                                          partition_by_one=partition_by_one,
                                                          partition_by_one_inclusive=partition_by_one_inclusive,
                                                          is_ordered=is_ordered,
                                                          hash_by_key=hash_by_key,
                                                          is_local_ordered=is_local_ordered,
                                                          sql_name=sql_name,
                                                          is_required=is_required,
                                                          sql_description=sql_description,
                                                          lang_description=r_description,
                                                          datatype=datatype,
                                                          allows_lists=allows_lists,
                                                          lang_name=lang_name,
                                                          use_in_r=use_InR,
                                                          r_formula_usage=r_formula_usage,
                                                          r_order_num=r_order_num,
                                                          alternate_sql_name=alternate_sql_name))
                # Add entry in map for sql and lang name of input table.
                self.__input_table_lang_names[sql_name.lower()] = lang_name.lower()
                if alternate_sql_name:
                    for alter_sql_name in alternate_sql_name:
                        self.__input_table_lang_names[alter_sql_name.lower()] = lang_name.lower()


    def _parse_output_tables(self):
        """
        DESCRIPTION:
            Function to parse and store the output tables in json file. This function first validates
            whether output table is required for analytic function or not. If required, then output tables
            section in json data is parsed and object of _AnlyFuncOutput is created and stored.

        RETURNS:
            None

        RAISES:
            TeradataMlException.

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").__parse_output_tables()
        """
        section = self.json_fields.OUTPUT_TABLES
        for output_table_param in self.json_object.get(self.json_fields.OUTPUT_TABLES, []):
            is_output_table_required = output_table_param.get(self.json_fields.USEINR, False)

            # Append argument/output table to list if useInR is true.
            if is_output_table_required:
                useInR = is_output_table_required

                sql_name = self._get_argument_value(output_table_param, self.json_fields.NAME, section)

                is_required = self._get_argument_value(output_table_param, self.json_fields.IS_REQUIRED, section)

                sql_description = self._get_argument_value(output_table_param, self.json_fields.DESCRIPTION, section)

                r_description = self._get_argument_value(output_table_param, self.json_fields.R_DESCRIPTION, section)

                datatype = self._get_argument_value(output_table_param, self.json_fields.DATATYPE, section)

                lang_name = self._get_pythonic_name_arg_name(self._get_argument_value(output_table_param,
                                                                                      self.json_fields.R_NAME, section))

                r_order_num = self._get_argument_value(output_table_param, self.json_fields.R_ORDER_NUM, section)

                is_output_table = self._get_argument_value(output_table_param, self.json_fields.IS_OUTPUT_TABLE,
                                                           section, False, False)

                allows_lists = self._get_argument_value(output_table_param, self.json_fields.ALLOWS_LISTS, section,
                                                        False, False)

                alternate_sql_name = self._get_argument_value(output_table_param, self.json_fields.ALTERNATE_NAMES,
                                                              section, False)

                # TODO: Additional dependencies needs to be implemented with ELE-4511.
                is_required_dependent_argument = self._get_argument_value(
                    output_table_param, self.json_fields.IS_REQUIRED_DEPENDENT, section, False)
                dependent_argument = None
                if is_required_dependent_argument:

                    argument_type = "input_tables"
                    if is_required_dependent_argument.get(self.json_fields.DEPENDENT_ARGUMENT_TYPE) == "argument":
                        argument_type = "arguments"
                    elif is_required_dependent_argument.get(self.json_fields.DEPENDENT_ARGUMENT_TYPE) == "input_table":
                        argument_type = "input_tables"

                    argument_name = is_required_dependent_argument.get(self.json_fields.DEPENDENT_ARGUMENT_NAME)
                    operator = is_required_dependent_argument.get(self.json_fields.OPERATOR)
                    right_operand = is_required_dependent_argument.get(self.json_fields.DEPENDENT_ARGUMENT_VALUE)
                    dependent_argument = _DependentArgument(sql_name=argument_name,
                                                            operator=operator,
                                                            right_operand=right_operand,
                                                            type=argument_type)

                # TODO: Output schema is not being used any where in processing. So, skipping it for now.
                # output_schema = self._get_argument_value(output_table_param, self.json_fields.OUTPUT_SCHEMA, False)

                self.output_tables.append(_AnlyFuncOutput(sql_name=sql_name,
                                                            is_required=is_required,
                                                            sql_description=sql_description,
                                                            lang_description=r_description,
                                                            lang_name=lang_name,
                                                            use_in_r=useInR,
                                                            r_order_num=r_order_num,
                                                            is_output_table=is_output_table,
                                                            datatype=datatype,
                                                            allows_lists=allows_lists,
                                                            output_schema=None,
                                                            alternate_sql_name=alternate_sql_name,
                                                            is_required_dependent_argument=dependent_argument))

    def __parse_json(self):
        try:
            # Parse all input tables.
            self._parse_input_tables()

            # Parse all output tables.
            self._parse_output_tables()

            # Parse all arguments.
            self._parse_arguments()

        except Exception as err:
            teradataml_file_path = os.path.join(*Path(self._json_file).parts[-6:])
            raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_JSON,
                                                           teradataml_file_path,
                                                           str(err)),
                                      MessageCodes.INVALID_JSON)

    def __get_analytic_function_args(self):
        """
        DESCRIPTION:
            Internal function to get the arguments of analytic function, which are required
            to generate function signature. This function iterates through every input
            table and argument, and does the below.
            * Check if argument formulates to an argument "formula" when exposed or not. If yes,
              then the argument should be the first argument and is extracted to a different variable.
            * Function arguments with rOrderNum <= 0 are not supposed to be exposed
              to end user. Ignore these arguments.

        RAISES:
            None

        RETURNS:
            tuple, first element specifies formula argument and second element specifies
            list of required arguments for analytic function.

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").__get_analytic_function_args()
        """
        new_args = []
        args = self.input_tables + self.arguments

        for arg in args:
            r_order_num = arg.get_r_order_number()
            is_argument_formula = isinstance(arg, _AnlyFuncArgument) and arg.is_argument_a_formula() \
                                  and arg.get_r_order_number() <= 0
            if is_argument_formula:
                if arg.get_r_order_number() == 0:
                    self.__dependent_formula_arg = arg
                self.__formula_args.append(arg)
                continue

            if r_order_num <= 0:
                continue

            new_args.append(arg)
        return self.__formula_args, new_args

    def _generate_function_parameters(self):
        """
        DESCRIPTION:
            Function to generate the analytic function argument names and their corresponding default values.
            Function arguments are generated by adhering to following:
            *  Signature includes only input as well as other arguments (SQL: Using clause
               arguments). So, process only those.
            *  Output arguments are ignored in the function signature. So, do not process Output arguments.
            *  Also, arguments pertaining to partition and order column are also generated for
               input tables.

        RAISES:
            None

        RETURNS:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json")._generate_function_parameters()
        """

        formula_args, args = self.__get_analytic_function_args()

        # Formula should always appear as first argument. So, start with formula argument.
        if formula_args:
            self.function_params["formula"] = None

        for arg in args:

            arg_name = arg.get_lang_name()
            default_value = arg.get_default_value()

            # Add argument and default value in the same order.
            self.function_params[arg_name] = default_value

    def __process_partition_order_columns(self, arg):
        """
        DESCRIPTION:
            Function to generate the arguments which are related to partition columns
            and order columns arguments.
        
        PARAMETERS:
            arg:
                Required Argument.
                Specifies the object of analytic input argument.
                Types: _AnlyFuncInput

        RAISES:
            None

        RETURNS:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").__process_partition_order_columns(arg)
        """
        partition_column_kind = arg._get_partition_column_required_kind()
        partition_value = arg._get_default_partition_by_value(partition_column_kind)

        # If Function supports only PartitionByOne or PartitionByAny, don't expose
        # partition column to user.
        if arg._only_partition_by_one() or\
                arg._only_partition_by_any():
            pass
        elif partition_column_kind == PartitionKind.KEY or \
                partition_column_kind == PartitionKind.DIMENSIONKEY:
            self.function_params["{}_partition_column".format(arg.get_lang_name())] = None
        elif partition_column_kind in [PartitionKind.ANY,
                                       PartitionKind.DIMENSIONKEYANY,
                                       PartitionKind.ONE]:
            self.function_params['{}_partition_column'.format(arg.get_lang_name())] = partition_value

        # If function type is not a driver or argument is ordered, then add order
        # column also to arguments.
        if not self.__is_driver_function or arg.is_ordered():
            self.function_params["{}_order_column".format(arg.get_lang_name())] = None
        
    def __process_hash_local_order_columns(self, arg):
        """
        DESCRIPTION:
            Generate the arguments related to LOCAL ORDER BY and HASH BY KEY.
        
        PARAMETERS:
            arg:
                Required Argument.
                Specifies the object of analytic input argument.
                Types: _AnlyFuncInput

        RAISES:
            None

        RETURNS:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").__process_hash_local_order_columns(arg)
        """
        # If the argument is local ordered, then add "is_local_ordered"
        # as argument.
        if arg.is_local_ordered():
            self.function_params["{}_is_local_ordered".format(arg.get_lang_name())] = False
        # Let's check if function has HASH BY clause.
        if arg.hash_by_key():
            self.function_params['{}_hash_column'.format(arg.get_lang_name())] = None

    def get_function_parameters_string(self, exclude_args=[]):
        """
        DESCRIPTION:
            Function to generate the function parameters in string format.

        RAISES:
            None

        RETURNS:
            str

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").get_function_parameters_string()
        """
        if not self.function_params:
            self._generate_function_parameters()
        # Along with function parameters, kwargs should be added to accept other parameters.
        return ", ".join(["{} = {}".format(param, '"{}"'.format(value) if isinstance(value, str) else value)
                          for param, value in self.function_params.items() if param not in exclude_args] + ["**generic_arguments"])

    @property
    def input_tables(self):
        """
        DESCRIPTION:
            Function to return input tables.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").input_tables
        """
        return self.__input_tables

    @input_tables.setter
    def input_tables(self, input):
        """
        DESCRIPTION:
            Function to append variable to the input tables list.

        PARAMETERS:
            input:
                Required Argument.
                Specifies the variable to be appended.

        RETURNS:
            None

        RAISES:
            None
        """
        self.__input_tables.append(input)

    @property
    def output_tables(self):
        """
        DESCRIPTION:
            Function to return output tables.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").output_tables
        """
        return self.__output_tables

    @output_tables.setter
    def output_tables(self, output):
        """
        DESCRIPTION:
           Function to append variable to the output tables list.

        PARAMETERS:
            input:
                Required Argument.
                Specifies the variable to be appended.

        RETURNS:
            None

        RAISES:
            None
        """
        self.__output_tables.append(output)

    @property
    def input_table_lang_names(self):
        """
        DESCRIPTION:
            Function to return map between sql name and lang name of input tables.

        RETURNS:
            dict

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").input_table_lang_names
        """
        return self.__input_table_lang_names

    @property
    def arguments(self):
        """
        DESCRIPTION:
            Function to return arguments.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").arguments
        """
        return self.__arguments


    @arguments.setter
    def arguments(self, argument):
        """
        DESCRIPTION:
            Function to append the variable to the arguments list.

        PARAMETERS:
            argument:
                Required Argument.
                Specifies the variable to be appended.

        RETURNS:
            None

        RAISES:
            None
        """
        self.__arguments.append(argument)

    @property
    def arguments_and_sections(self):
        """
        DESCRIPTION:
            Function to return arguments_and_sections.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").arguments_and_sections
        """
        return self.__arguments_and_sections

    @arguments_and_sections.setter
    def arguments_and_sections(self, argument):
        """
        DESCRIPTION:
            Function to update the arguments_and_sections dictonary.

        PARAMETERS:
            argument:
                Required Argument.
                Specifies the variable to be added to the dictonary.

        RETURNS:
            None

        RAISES:
            None
        """
        self.__arguments_and_sections.update(argument)

    @property
    def function_params(self):
        """
        DESCRIPTION:
            Function to get the function_params.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").function_params
        """
        return self.__function_params

    @function_params.setter
    def function_params(self, argument):
        """
        DESCRIPTION:
            Function to set the function_params.

        PARAMETERS:
            argument:
                Required Argument.
                Specifies the variable to be added to the dictonary.

        RETURNS:
            list

        RAISES:
            None

        """
        self.__function_params.update(argument)

    @property
    def formula_args(self):
        """
        DESCRIPTION:
            Function to return formula arguments.
            _AnlyFuncMetadata(json_data, "/abc/TD_GLM.json").formula_args
        """
        return self.__formula_args

    @staticmethod
    def __get_anly_function_name_mapper():
        """
        DESCRIPTION:
            Function to read mapper file teradataml/analytics/jsons/anly_function_name.json,
            which has a mapping between function name specified in json file and function to
            appear in user's context.

        RETURNS:
            list

        RAISES:
            None
        """
        return json.loads(
            UtilFuncs._get_file_contents(os.path.join(UtilFuncs._get_data_directory(dir_name="jsons"),
                                                      "anly_function_name.json")))

    def _validate_duplicate_argument(self, lang_name, section):
        """
        DESCRIPTION:
            Internal function to check the duplicates of arguments. No python function
            accepts duplicate parameters and since analytic functions are being formed at
            run time from json, there are chances that function may be constructed with
            duplicate arguments. This function validates whether arguments are duplicated or not.

        PARAMETERS:
            lang_name:
                Required Argument.
                Specifies the name of the argument which is mentioned in json file.
                Types: str

            section:
                Required Argument.
                Specifies the section of json file, to which argument belongs to.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            _AnlyFuncMetadata(data, "abc.json")._validate_duplicate_argument("abc", "input_tables")
        """
        if lang_name not in self.arguments_and_sections:
            self.arguments_and_sections[lang_name] = section
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.DUPLICATE_PARAMETER,
                                                           lang_name,
                                                           section),
                                      MessageCodes.DUPLICATE_PARAMETER)

    @staticmethod
    def _get_pythonic_name_arg_name(r_name, is_regex_match=False):
        """
        DESCRIPTION:
            Function to get the pythonic name for argument from the name specified
            in json. Conversion of a string to pythonic name does as below:
                * Strips out the trailing and leading spaces.
                * Converts the string to lower case.
                * Replaces the dot(.) with underscore.
                * Replaces the '_table' with '_data'.
                * Replaces the 'table_' with 'data_'.

        PARAMETERS:
            r_name:
                Required Argument.
                Specifies the name of the argument which is mentioned in json file.
                Types: str

            is_regex_match:
                Optional Argument.
                Specifies whether regex match is set or not.
                Default Value: False
                Types: bool

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json")._get_pythonic_name_arg_name("abc")
        """
        # When regex_match is set to True, we consider r_name as a regular expression.
        if is_regex_match:
            return r_name.strip()
        return r_name.strip().lower().replace(".", "_").replace("_table", "_data").replace("table_", "data_")

    def _get_function_name(self):
        """
        DESCRIPTION:
            Function to get the name of the function which is exposed to user.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json")._get_function_name()
        """
        # If teradataml/data/jsons/anly_function_name.json contains a mapping name, function name
        # should be corresponding mapping name. Else, same as function name.

        func_name = self.__get_anly_function_name_mapper().get(self.json_object[self.json_fields.FUNCTION_ALIAS_NAME],
                                                               self.json_object[self.json_fields.FUNCTION_ALIAS_NAME])
        # Few functions are expected to have a name starting with TD_,i.e., json file may
        # contain function name as TD_Xyz. Since we don't want the prefixed characters,
        # removing those.
        return func_name[3:] if func_name.startswith("TD_") else func_name

    def get_doc_string(self):
        """
        DESCRIPTION:
            Function to get the docstring for the function from corresponding docs file.
            If docs file is not found, return a message asking the user to refer to reference guide.

        PARAMETERS:
            None.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadata(json_data, "/abc/Antiselect.json").get_doc_string()
        """
        func_info = getattr(TeradataAnalyticFunctionInfo, self.func_type.upper())
        function_type = func_info.value["func_type"]
        # For version dependent IN-DB functions, get version info as per vantage version
        # and then get exact doc dir.
        # For version independent IN-DB functions, get the docs directory under given
        # function type.
        if function_type in utils.func_type_json_version.keys():
            version_dir = utils.func_type_json_version[function_type]
            doc_dir = "docs_{}".format(version_dir.replace('.', '_'))
        else:
            doc_dir = "docs"
        try:
            # from teradataml.data.docs.<function_type>.<doc_dir_with_version_info>.<func_name>
            # import <func_name>
            func_module = __import__(("teradataml.data.docs.{}.{}.{}".
                                    format(function_type, doc_dir, self.func_name)),
                                    fromlist=[self.func_name])
            return getattr(func_module, self.func_name).__doc__   
        except:
            # For db_version 20.00, if function type is sqle, then check for docs_17_20 directory.
            if version_dir == '20.00' and function_type == 'sqle':
                try:
                    func_module = __import__(("teradataml.data.docs.{}.{}.{}".
                                             format(function_type, "docs_17_20", self.func_name)),
                                             fromlist=[self.func_name])
                    return getattr(func_module, self.func_name).__doc__
                except:
                    pass
            return ("Refer to Teradata Package for Python Function Reference guide for "
                    "Documentation. Reference guide can be found at: https://docs.teradata.com ."
                    "Refer to the section with Database version: {}".format(self.__database_version))

    def __get_input_table_lang_name(self, sql_name):
        """ Internal function to get lang name of input table when sql name is provided. """
        if sql_name.lower() in self.__input_table_lang_names.keys():
            return self.__input_table_lang_names.get(sql_name.lower()).lower()


class _AnlyFuncMetadataUAF(_AnlyFuncMetadata):
    """ Class to hold the UAF json data. """

    # Class variable to hold the UAF json fields.
    json_fields = UAFJsonFields()

    def __init__(self, json_data, json_file, func_type):
        self.__input_fmt_arguments = []
        self.__output_fmt_arguments = []
        super().__init__(json_data, json_file, func_type)

    @property
    def input_fmt_arguments(self):
        """
        DESCRIPTION:
            Property to get the arguments involved in INPUT_FMT section.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadataUAF(json_data, "/abc/ArimaEstimate.json").function_params
        """
        return self.__input_fmt_arguments

    @input_fmt_arguments.setter
    def input_fmt_arguments(self, argument):
        """
        DESCRIPTION:
            Property setter for the arguments involved in INPUT_FMT section.

        PARAMETERS:
            argument:
                Required Argument.
                Specifies the variable to be added to the list.
                Type : _AnlyFuncArgumentUAF

        RETURNS:
            list

        RAISES:
            None

        """
        self.__input_fmt_arguments.append(argument)

    @property
    def output_fmt_arguments(self):
        """
        DESCRIPTION:
            Property to get the arguments involved in OUTPUT_FMT section.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            _AnlyFuncMetadataUAF(json_data, "/abc/ArimaEstimate.json").function_params
        """
        return self.__output_fmt_arguments

    @output_fmt_arguments.setter
    def output_fmt_arguments(self, argument):
        """
        DESCRIPTION:
            Property setter for the arguments involved in OUTPUT_FMT section.

        PARAMETERS:
            argument:
                Required Argument.
                Specifies the variable to be added to the list.
                Type : _AnlyFuncArgumentUAF

        RETURNS:
            list

        RAISES:
            None

        """
        self.__output_fmt_arguments.append(argument)

    def _func_type_specific_setup(self):
        """
        DESCRIPTION:
            Additional setup required for UAF functions.

        RETURNS:
            None

        RAISES:
            None
        """
        # Generic Json Parameters
        self.__function_version = self.json_object[self.json_fields.FUNCTION_VERSION]
        self.__json_version = self.json_object[self.json_fields.JSON_VERSION]
        self.__r_function_name = self.json_object[self.json_fields.R_NAME]
        self.__max_input_files = self.json_object[self.json_fields.MAX_INPUT_FILES]
        self.__is_plottable = self.json_object[self.json_fields.IS_PLOTTABLE]
        self.__input_fmt = self.json_object[self.json_fields.INPUT_FMT]
        self.__output_fmt = self.json_object[self.json_fields.OUTPUT_FMT]

        # Getters
        self.get_function_version = lambda: self.__function_version
        self.get_json_version = lambda: self.__json_version
        self.get_func_r_name = lambda: self.__r_function_name
        self.get_max_input_files = lambda: self.__max_input_files
        self.get_is_plottable = lambda: self.__is_plottable
        self.has_input_fmt = lambda: self.__input_fmt
        self.has_output_fmt = lambda: self.__output_fmt
        self._is_view_supported = False

        # Validation
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["func_description_short", self.short_description, True, str])
        self.__arg_info_matrix.append(["func_description_long", self.long_description, False, (list, str)])
        self.__arg_info_matrix.append(["function_version", self.__function_version, True, str])
        self.__arg_info_matrix.append(["json_version", self.__json_version, True, str])
        self.__arg_info_matrix.append(["func_r_name", self.__r_function_name, True, str])
        self.__arg_info_matrix.append(["max_input_files", self.__max_input_files, False, int])
        self.__arg_info_matrix.append(["is_plottable", self.__is_plottable, False, bool])

        # TODO : uncomment the lines when ELE-5078 is done.
        # self.__arg_info_matrix.append(["input_fmt", self.__input_fmt, False, (bool, _ListOf(dict)), False, [False]])
        # self.__arg_info_matrix.append(["output_fmt", self.__output_fmt, False, (bool, _ListOf(dict)), False, [False]])

        self.__arg_info_matrix.append(["input_fmt", self.__input_fmt, False, (bool, _ListOf(dict))])
        self.__arg_info_matrix.append(["output_fmt", self.__output_fmt, False, (bool, _ListOf(dict))])

        _Validators._validate_function_arguments(self.__arg_info_matrix)

    def __input_params_generation(self, input_table_param, lang_name="data"):
        """
        DESCRIPTION:
            Function to generate the input parameters and form an object of class _AnlyFuncInputUAF.

        RETURNS:
            None

        RAISES:
            None
        """
        section = self.json_fields.INPUT_TABLES
        data_type = self._get_argument_value(input_table_param, self.json_fields.DATATYPE, section)
        description = self._get_argument_value(input_table_param, self.json_fields.DESCRIPTION, section)
        is_required = not self._get_argument_value(input_table_param, self.json_fields.OPTIONAL, section,
                                                   mandatory=False, default_value=True)
        # Check for duplicate arguments.
        self._validate_duplicate_argument(lang_name, self.json_fields.INPUT_TABLES)
        # Create an object of class _AnlyFuncInputUAF and append to the list.
        self.input_tables.append(_AnlyFuncInputUAF(data_type=data_type,
                                                   description=description,
                                                   lang_name=lang_name,
                                                   is_required=is_required))

    def _parse_input_tables(self):
        """
        DESCRIPTION:
            Function to parse and store the input tables in json file. This function first validates
            whether input table is required for analytic function or not. If required, then input tables
            section in json data is parsed and object of _AnlyFuncInputUAF is created and stored.

        RETURNS:
            None

         RAISES:
            None
        """


        if len(self.json_object[self.json_fields.INPUT_TABLES]) == 1:
            input_table_param = self.json_object[self.json_fields.INPUT_TABLES][0]
            self.__input_params_generation(input_table_param)
        else:
            for counter, input_table_param in enumerate(self.json_object[self.json_fields.INPUT_TABLES], 1):
                lang_name = "data{}".format(counter)
                self.__input_params_generation(input_table_param, lang_name)

    def _parse_output_tables(self):
        """
        DESCRIPTION:
            Function to parse and store the output tables in json file. This function first validates
            whether output table is required for analytic function or not. If required, then output tables
            section in json data is parsed and object of _AnlyFuncOutputUAF is created and stored.

        RETURNS:
            None

        RAISES:
            None
        """
        section = self.json_fields.OUTPUT_TABLES

        for output_table_param in self.json_object[self.json_fields.OUTPUT_TABLES]:
            # Specifies the output type.
            data_type = self._get_argument_value(output_table_param, self.json_fields.DATATYPE, section)

            # Specifies the column types for the result table.
            result_table_column_types = self._get_argument_value(output_table_param,
                                                                  self.json_fields.RESULT_TABLE_COLUMN_TYPES, section, False)
            # Specifies the output description.
            description = self._get_argument_value(output_table_param, self.json_fields.DESCRIPTION, section)

            # Specifies whether the argument is required or not.
            is_required = not self._get_argument_value(output_table_param, self.json_fields.OPTIONAL, section, False)

            # Specifies whether the layer is primary or not.
            primary_layer = self._get_argument_value(output_table_param, self.json_fields.PRIMARY_LAYER, section)

            # Specifies the name of the output layer.
            layer_name = self._get_argument_value(output_table_param, self.json_fields.LAYER_NAME, section)

            # Use the layer name as lang_name.
            # Remove 'art' if present in the first three characters from the layer_name.
            lang_name = layer_name.lower()[3:] if layer_name.lower()[:3] in "art" else layer_name.lower()

            self.output_tables.append(_AnlyFuncOutputUAF(data_type=data_type,
                                                           description=description,
                                                           lang_name=lang_name,
                                                           layer_name=layer_name,
                                                           primary_layer=primary_layer,
                                                           result_table_column_types=result_table_column_types,
                                                           is_required=is_required))

    def __argument_parser(self, argument, section, parent = None, is_nested=False, prev_lang_name=None):
        """
       DESCRIPTION:
           Internal function to parse the individual argument in json file.
           Nested arguments if present in json data, are parsed and object of _AnlyFuncArgumentUAF
           are appended to the nested_parameter_list.
           Used for parsing UAF function arguments under section 'func_params' in JSON file.

       RETURNS:
           object of _AnlyFuncArgumentUAF

       RAISES:
           TeradataMlException.
        """
        sql_name = UtilFuncs._as_list(self._get_argument_value(argument, self.json_fields.NAME, section))

        for name in sql_name:
            sql_name = name
            is_required = not self._get_argument_value(argument, self.json_fields.OPTIONAL, section, mandatory=False,
                                                        default_value=True)
            sql_description = self._get_argument_value(argument, self.json_fields.DESCRIPTION, section)

            datatype = self._get_argument_value(argument, self.json_fields.DATATYPE, section)
            nested_params_json = self._get_argument_value(argument, self.json_fields.NESTED_PARAMS_JSON, section,
                                                          mandatory=False, default_value=None)
            # Validate whether nested params exist only if data type is a record.
            if datatype == "record":
                if nested_params_json is None:
                    raise TeradataMlException("For json: {} and parameter with name : {} nested_parameters should"
                                              " be present as type is 'record'.".format(self.sql_function_name,
                                                                                        sql_name))
            else:
                if nested_params_json is not None:
                    raise TeradataMlException("For json: {} and parameter with name : {} type should be"
                                              " 'record' as nested_parameters exist.".format(self.sql_function_name,
                                                                                             sql_name))

            # Look for default value. If list of default values are found,
            # the consider the first element as default value.
            default_value = self._get_argument_value(argument, self.json_fields.DEFAULT_VALUE, section, mandatory=False)

            # Json files can specify INFINITY as lower bound. So, convert it to appropriate
            # type in python.
            lower_bound = self._get_argument_value(argument, self.json_fields.LOWER_BOUND, section, mandatory=False)
            lower_bound = UtilFuncs._get_negative_infinity() if lower_bound == self.json_fields.INFINITY else lower_bound

            # Json files can specify INFINITY as upper bound. So, convert it to appropriate
            # type in python.
            upper_bound = self._get_argument_value(argument, self.json_fields.UPPER_BOUND, section, mandatory=False)
            upper_bound = UtilFuncs._get_positive_infinity() if upper_bound == self.json_fields.INFINITY else upper_bound

            allow_nan = self._get_argument_value(argument, self.json_fields.ALLOW_NAN, section, mandatory=False,
                                                  default_value=False)
            check_duplicates = self._get_argument_value(argument, self.json_fields.CHECK_DUPLICATE, section, mandatory=False,
                                                         default_value=False)
            lower_bound_type = self._get_argument_value(argument, self.json_fields.LOWER_BOUND_TYPE, section, mandatory=False)
            upper_bound_type = self._get_argument_value(argument, self.json_fields.UPPER_BOUND_TYPE, section, mandatory=False)
            required_length = self._get_argument_value(argument, self.json_fields.REQUIRED_LENGTH, section, mandatory=False,
                                                        default_value=0)
            permitted_values = self._get_argument_value(argument, self.json_fields.PERMITTED_VALUES, section, mandatory=False)

            list_type = self._get_argument_value(argument, self.json_fields.LIST_TYPE, section, mandatory=False)

            # If lang_name is present in the JSON and is not equal to '...' use the lang_name from the JSON
            # else lang name is equal to Pythonic sql_name.
            lang_name = self._get_argument_value(argument, self.json_fields.LANG_NAME, section, mandatory=False)
            lang_name = lang_name if lang_name is not None and lang_name != "..."\
                else "_".join(filter(None, [prev_lang_name, self._get_pythonic_name_arg_name(sql_name)]))

            has_nested = False
            nested_param_list = []
            # Loop over the nested params if present and call the function in recursive manner.
            if nested_params_json is not None:
                has_nested = True
                for nested_arg in nested_params_json:
                    for nested_list in self.__argument_parser(argument=nested_arg,
                                                                    section=section,
                                                                    parent=sql_name,
                                                                    is_nested=True,
                                                                    prev_lang_name=lang_name):
                        nested_param_list.append(nested_list)
            yield  _AnlyFuncArgumentUAF(data_type=datatype,
                                        description=sql_description,
                                        name=sql_name,
                                        is_required=is_required,
                                        permitted_values=permitted_values,
                                        lower_bound=lower_bound,
                                        upper_bound=upper_bound,
                                        lower_bound_type=lower_bound_type,
                                        upper_bound_type=upper_bound_type,
                                        check_duplicates=check_duplicates,
                                        list_type=list_type,
                                        allow_nan=allow_nan,
                                        lang_name=lang_name,
                                        default_value=default_value,
                                        required_length=required_length,
                                        parent = parent,
                                        is_nested = is_nested,
                                        has_nested = has_nested,
                                        nested_param_list=nested_param_list)

    def _process_arg_sections(self, section=None, arg_list_name=None):
        """
        DESCRIPTION:
            Function to loop over the ARGUMENT_CLAUSES, INPUT_FMT and OUTPUT_FMT sections,
            call the __argument_parser and populate the corresponding lists
            with the objects of _AnlyFuncArgumentUAF .

        RETURNS:
            None

        RAISES:
            None
        """
        for argument in self.json_object.get(section, []):
            for arg_list in self.__argument_parser(argument, section):
                getattr(self, arg_list_name).append(arg_list)

    def _parse_arguments(self):
        """
        DESCRIPTION:
            Function to process argument section and input_fmt and output_fmt sections, if present.

        RETURNS:
            None

        RAISES:
            None
        """
        # Parse all arguments.
        self._process_arg_sections(section=self.json_fields.ARGUMENT_CLAUSES, arg_list_name="arguments")

        # Parse input_fmt section.
        if self.has_input_fmt():
            self._process_arg_sections(section=self.json_fields.INPUT_FMT, arg_list_name="input_fmt_arguments")

        # Parse output_fmt section.
        if self.has_output_fmt():
            self._process_arg_sections(section=self.json_fields.OUTPUT_FMT, arg_list_name="output_fmt_arguments")

    def __update_function_params_uaf_argument(self, argument):
        """
        DESCRIPTION:
            Function to update the function_params list with argument's lang_name and default value.
            If arguments have nested parameters, the lang_name and default value of the nested_parameters
            are appended to the function_params list and not the parent element.

        RETURNS:
            None

        RAISES:
            None
        """
        if argument.get_has_nested():
            for nested_arg in argument.get_nested_param_list():
                self.__update_function_params_uaf_argument(nested_arg)
        else:
            r_default_value = argument.get_r_default_value()
            default_value = r_default_value if r_default_value is not None else \
                argument.get_default_value()
            self.function_params[argument.get_lang_name()] = default_value

    def _generate_function_parameters(self):
        """
        DESCRIPTION:
            Function to generate the UAF function argument names and their corresponding default values.
            Function arguments are generated by adhering to following:
            *  Signature includes only input as well as other arguments (SQL: Using clause
               arguments). So, process only those.
            *  Output arguments are ignored in the function signature. So, do not process Output arguments.
            *  Also, arguments pertaining to input_format and output_format are added.

        RETURNS:
            None

        RAISES:
            None
        """
        # Process input arguments
        for input_args in self.input_tables:
            lang_name = input_args.get_lang_name()
            filter_exp = "{}_filter_expr".format(lang_name)
            self.function_params.update({lang_name: input_args.get_default_value(),
                                           filter_exp: input_args.get_default_value()})

        # Process arguments section.
        parameters = []
        for argument in self.arguments:
            self.__update_function_params_uaf_argument(argument)

        # If has_input_fmt is True, add arguments related to input_fmt.
        if self.has_input_fmt():
            for argument in self.input_fmt_arguments:
                self.__update_function_params_uaf_argument(argument)

        # If has_output_fmt() is True, then parameters related to output_fmt are added.
        if self.has_output_fmt():
            for argument in self.output_fmt_arguments:
                self.__update_function_params_uaf_argument(argument)

    def _get_function_name(self):
        """
        DESCRIPTION:
            Function to get the pythonic name of the function from the R_NAME
            which is to be exposed to user.

        RETURNS:
            str

        RAISES:
            None
        """
        func_name = self.json_object[self.json_fields.R_NAME]
        func_name = sub(r"(_|-)+", "", func_name[3:])
        return func_name