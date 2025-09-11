"""
Unpublished work.
Copyright (c) 2020 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Rohit.Khurd@teradata.com
Secondary Owner:

This file is for creating a two way mapper between client specific attribute/input/output names to
their SQL specific counterparts.
"""
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.constants import ModelCatalogingConstants
from teradataml.context.context import _get_vantage_version
from teradataml.utils.validators import _Validators
from teradataml.common.constants import ModelCatalogingConstants as mac, \
    FunctionArgumentMapperConstants as famc
import inspect
import json
import os


class _ArgumentMapperSuper(object):
    """
    The parent class for the function argument mapper with simple functions to
    set and get attribute values.
    """

    def __init__(self):
        pass

    def _SetKeyValue(self, name, value):
        super().__setattr__(name, value)

    def _GetValue(self, name):
        return super().__getattribute__(name)


def _create_property(name):
    """
    Internal function to create a property with getter and setter with the required name.
    """
    storage_name = '_' + name

    @property
    def prop(self):
        return self._GetValue(storage_name)

    @prop.setter
    def prop(self, value):
        self._SetKeyValue(storage_name, value)

    return prop


class _ArgumentMapper(_ArgumentMapperSuper):
    """
    Dictionary to map teradataml argument names to SQL argument names and vice-versa.
    """
    input_output_arg_map = _create_property('input_output_arg_map')

    def __init__(self):
        """
        PARAMETERS:
            None.
        """
        super().__init__()
        # input_output_arg_map: It is required to create the dictionary to hold the map.
        # Types: dict
        super().__setattr__('input_output_arg_map', {})

    def __setattr__(self, name, value):
        if hasattr(self, name):
            # We will set the 'input_output_arg_map' argument map when it is updated from
            # the __load_function_map method
            if name == 'input_output_arg_map' and inspect.stack()[1][3] == '__load_function_map':
                if not isinstance(value, dict):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                         name, 'dict'),
                                    MessageCodes.UNSUPPORTED_DATATYPE)
                super().__setattr__(name, value)
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def _get_function_map(self, engine, function_name):
        """
        DESCRIPTION:
            Function to return the function argument mapper for a given function.

        PARAMETERS:
            engine:
                Required Argument.
                Specifies the analytics engine to which the function belongs to.
                Supported values: 'ML Engine', 'Advanced SQL Engine'
                Types: str

            function_name:
                Required Argument.
                Specifies the name of the function on the analytics engine provided to get the map for.
                Types: str

        RAISES:
            None.

        RETURNS:
            A dictionary mapping the teradataml equivalent argument, input table,
            and output table names to SQL names, and vice-versa.

        EXAMPLES:
            >>> from teradataml.catalog.function_argument_mapper import _argument_mapper
            >>> _argument_mapper._get_function_map('ML Engine', 'GLM')

        """
        arg_info_matrix = []
        arg_info_matrix.append(["engine", engine, False, (str), True, [mac.MODEL_ENGINE_ADVSQL.value,
                                                                        mac.MODEL_ENGINE_ML.value]])
        arg_info_matrix.append(["function_name", function_name, False, (str), True])

        # Make sure that a non-NULL value has been supplied for all mandatory arguments
        _Validators._validate_missing_required_arguments(arg_info_matrix)

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        # Set the Vantage version attribute when required, i.e. when attempting to populate the Function map
        # for the first time.
        # Setting it to 'Vantage 1.1 GA' by default, just as in 'configure'.
        if not hasattr(self, '_vantage_version'):
            vantage_version = _get_vantage_version()
            super().__setattr__('_vantage_version', vantage_version if vantage_version else 'Vantage 1.1 GA')

        # Standardise the engine name to use in the mapper
        if engine.lower() == ModelCatalogingConstants.MODEL_ENGINE_ML.value.lower():
            engine = ModelCatalogingConstants.MODEL_ENGINE_ML.value
        elif engine.lower() == ModelCatalogingConstants.MODEL_ENGINE_ADVSQL.value.lower():
            engine = ModelCatalogingConstants.MODEL_ENGINE_ADVSQL.value

        # Also use lower case algorithm names for case insensitive checks
        self.__load_function_map(engine, function_name.lower())
        return self.input_output_arg_map[engine][function_name.lower()]

    def __load_function_map(self, engine, function_name):
        """
        DESCRIPTION:
            Internal function to check for the presence of the given function in the mapper, and when not found,
            load the function argument mapping for function specified by the engine and function_name arguments.

        PARAMETERS:
            engine:
                Required Argument.
                Specifies the name of the engine the function belongs to.
                Acceptable values: 'ML Engine', 'Advanced SQL Engine'
                Types: str

            function_name:
                Required Argument.
                Specifies the name of the function to check and load the argument mapping for.
                Types: str

        RAISES:
            TeradataMlException

        RETURNS:
            NA

        EXAMPLES:
            >>> self.__load_function_map('ML Engine', 'GLM')

        """
        if engine not in self.input_output_arg_map or \
           function_name not in self.input_output_arg_map[engine]:

            curr_dir = os.path.dirname(os.path.abspath(__file__))
            function_json_file = None

            # The path of the JSON files for the function is expected to be:
            # teradataml/analytics/sqle/<function_name>_sqle.json - for SQLE functions
            if engine == ModelCatalogingConstants.MODEL_ENGINE_ML.value:
                function_json_file = os.path.join(curr_dir,
                                                  '../analytics/mle/json/{}_mle.json'.format(function_name))
            elif engine == ModelCatalogingConstants.MODEL_ENGINE_ADVSQL.value:
                function_json_file = os.path.join(curr_dir,
                                                  '../analytics/sqle/json/{}_sqle.json'.format(function_name))

            try:
                function_json = json.load(open(function_json_file, 'r'))
            except Exception:
                raise TeradataMlException(Messages.get_message(MessageCodes.FUNCTION_JSON_MISSING,
                                                               function_name, engine),
                                          MessageCodes.FUNCTION_JSON_MISSING)

            self.__setattr__('input_output_arg_map',
                             self.__update_json_dict_for_function(self.input_output_arg_map, engine,
                                                                  function_name,
                                                                  function_json))

    def __resolve_arg_types(self, arg):
        """
        DESCRIPTION:
            Internal function to return the python data type corresponding to the acceptable SQL data type
            for an argument.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies a dictionary related to the function argument from the function argument map.
                Types: dict

        RAISES:
            TypeError

        RETURNS:
            Python data type for the argument specified.

        EXAMPLES:
            >>> expected_python_types = self.__resolve_arg_types(arg)

        """
        # Raise and error if the type is not expected
        if not isinstance(arg, dict):
            raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                 'arg', 'dict'),
                            MessageCodes.UNSUPPORTED_DATATYPE)

        # Let's check if the argument accepts lists
        allows_lists = False
        if famc.ALLOWS_LISTS.value in arg:
            allows_lists = arg[famc.ALLOWS_LISTS.value]

        # The default type of argument is str
        python_type = str
        if arg[famc.DATATYPE.value] == famc.BOOL_TYPE.value:
            python_type = bool
        elif arg[famc.DATATYPE.value] in famc.INT_TYPE.value:
            python_type = int
        elif arg[famc.DATATYPE.value] in famc.FLOAT_TYPE.value:
            python_type = float

        # When the argument accepts lists, we create a 2-tuple of expected types,
        # where 'list' is the second item in the tuple.
        if allows_lists:
            python_type = (python_type, list)

        return python_type

    def __resolve_sequence_input_args(self, function_map, sequence_arg):
        """
        DESCRIPTION:
            Internal function to add mapping for SequenceInputBy argument between its SQL and teradataml counterparts.

        PARAMETERS:
            function_map:
                Required Argument.
                Specifies the function argument map to update with the information related
                to the SequenceInputBy argument.
                Types: dict

            sequence_arg:
                Required Argument.
                Specifies the dictionary element from the function JSON file corresponding
                to the SequenceInputBy argument.
                Types: dict

        RAISES:
            None

        RETURNS:
            A dictionary - the updated function argument map.

        EXAMPLES:
            >>> self.__resolve_sequence_input_args(function_map, sequence_arg)

        """
        arg_info_matrix = []
        arg_info_matrix.append(["function_map", function_map, False, (dict)])
        arg_info_matrix.append(["sequence_arg", sequence_arg, False, (dict)])

        # Make sure that a non-NULL value has been supplied for all mandatory arguments
        _Validators._validate_missing_required_arguments(arg_info_matrix)

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        # First, make a list of all tdml names for inputs
        input_tdml_names = set([key for key in function_map[famc.INPUTS.value][famc.TDML_TO_SQL.value]])

        # Python type for sequenceBy argument is always str or a list of strs
        python_type = (str, list)

        # Convert the rName to teradataml name
        r_name = self.__convert_rName_to_tdml(sequence_arg[famc.R_NAME.value])

        # All teradataml sequence arguments are names <input_name>_sequence_column
        tdml_name = [ '{}_{}'.format(input_name, r_name) for input_name in input_tdml_names ]

        arg_name = sequence_arg[famc.NAME.value]
        sql_name_to_use = self.__resolve_name(arg_name).lower()

        if isinstance(arg_name, list):
            for i in range(len(arg_name)):
                # We can use only one of the SQL equivalents
                if i == 0:
                    function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                sql_name=arg_name[i],
                                                                tdml_name=tdml_name,
                                                                tdml_type=python_type)
                    function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][arg_name[i].lower()][
                        famc.USED_IN_SEQUENCE_INPUT_BY.value] = True
                    for name in tdml_name:
                        function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][name] = sql_name_to_use
                # The rest of the SQL equivalents can be treated as alternate names
                else:
                    function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                sql_name=arg_name[i],
                                                                sql_name_to_use=sql_name_to_use,
                                                                alternate_to=True)

        # The arg_name can be a dictionary where the keys are the Vantage versions,
        # and each version has it's own list of acceptable names
        if isinstance(arg_name, dict):
            for vv, value in arg_name.items():
                for i in range(len(value)):
                    if i == 0:
                        function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                    sql_name=value[i],
                                                                    tdml_name=tdml_name,
                                                                    tdml_type=python_type)
                        function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][value[i].lower()][
                            famc.USED_IN_SEQUENCE_INPUT_BY.value] = True
                        for name in tdml_name:
                            function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][name] = sql_name_to_use
                    else:
                        function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                    sql_name=value[i],
                                                                    sql_name_to_use=sql_name_to_use,
                                                                    alternate_to=True)

        return function_map

    def __resolve_formula_args(self, function_map, formula_args):
        """
        DESCRIPTION:
            Internal function to add mapping for formula argument between it's SQL and teradataml counterparts.

        PARAMETERS:
            function_map:
                Required Argument.
                Specifies the function argument map to update with the information related to the formula argument.
                Types: dict

            formula_args:
                Required Argument.
                Specifies the list of dictionary elements from the function JSON file corresponding
                to the formula argument.
                Types: list

        RAISES:
            None.

        RETURNS:
            A dictionary - the updated function argument map.

        EXAMPLES:
            >>> self.__resolve_formula_args(function_map, formula_args)

        """
        arg_info_matrix = []
        arg_info_matrix.append(["function_map", function_map, False, (dict)])
        arg_info_matrix.append(["formula_args", formula_args, False, (list)])

        # Make sure that a non-NULL value has been supplied for all mandatory arguments
        _Validators._validate_missing_required_arguments(arg_info_matrix)

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        # Check if formula is split into dependent and independent clauses
        found_dependent = False
        for arg in formula_args:
            # rOrderNum = 0 indicates it is dependent variable in the formula
            if arg[famc.R_ORDER_NUM.value] == 0:
                found_dependent = True
                break

        # Python type for formula is always str
        python_type = str
        tdml_name = famc.TDML_FORMULA_NAME.value
        arg_counter = 0
        for arg in formula_args:
            arg_counter = arg_counter + 1
            # Either the function needs a clear distinction between dependent
            # and independent variables (Like DecisionForest), or just the list (like GLM)
            if arg[famc.R_ORDER_NUM.value] == 0:
                used_in_formula = famc.DEPENDENT_ATTR.value
            else:
                if found_dependent:
                    used_in_formula = famc.INDEPENDENT_ATTR.value
                else:
                    used_in_formula = True

            arg_name = arg[famc.NAME.value]
            sql_name_to_use = self.__resolve_name(arg_name).lower()

            if isinstance(arg_name, list):
                for i in range(len(arg_name)):
                    if i == 0:
                        function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                    sql_name=arg_name[i],
                                                                    tdml_name=tdml_name,
                                                                    tdml_type=python_type)
                        function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][arg_name[i].lower()][
                            famc.USED_IN_FORMULA.value] = used_in_formula
                        if arg_counter > 1:
                            function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                                tdml_name] = function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                                                                             tdml_name] + [sql_name_to_use]
                        else:
                            function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                                tdml_name] = [sql_name_to_use]
                    else:
                        function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                    sql_name=arg_name[i],
                                                                    sql_name_to_use=sql_name_to_use,
                                                                    alternate_to=True)

            # The arg_name can be a dictionary where the keys are the Vantage versions,
            # and each version has it's own list of acceptable names
            if isinstance(arg_name, dict):
                for vv, value in arg_name.items():
                    for i in range(len(value)):
                        # Handle all other arguments
                        if i == 0:
                            function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                        sql_name=value[i],
                                                                        tdml_name=tdml_name,
                                                                        tdml_type=python_type)
                            function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][value[i].lower()][
                                famc.USED_IN_FORMULA.value] = used_in_formula
                            if arg_counter > 1:
                                function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                                    tdml_name] = function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                                                                                     tdml_name] + [sql_name_to_use]
                            else:
                                function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                                    tdml_name] = [sql_name_to_use]
                        else:
                            function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                        sql_name=value[i],
                                                                        sql_name_to_use=sql_name_to_use,
                                                                        alternate_to=True)

        return function_map

    def __resolve_name(self, name_arg):
        """
        DESCRIPTION:
            Internal function to resolve the SQL name for a given argument based on the Vantage version.

        PARAMETERS:
            name_arg:
                Required Argument.
                Specifies the name as defined in the function JSON file corresponding
                to any argument.
                Types: dict or list

        RAISES:
            None.

        RETURNS:
            A String representing the SQL name to use based on the Vantage version.

        EXAMPLES:
            >>> self.__resolve_name(['InputColumns', 'TargetColumns'])
            InputColumns
            >>> # Assuming Vantage version is 1.1
            >>> self.__resolve_name({'Vantage 1.0': ['InputCols'], 'Vantage 1.1 GA': ['InputColumns', 'TargetColumns'])
            InputColumns

        """
        # If the name_arg is of type dict, it means the argument has different names based on the Vantage version.
        # If name_arg is of type list, it means the argument has alternate names too, and they haven't changed since
        # the last release.
        # If name_arg is of type str, it means that the it points to the name to use which hasn't changed.

        if isinstance(name_arg, dict):
            name_arg = name_arg[self._vantage_version]

        if isinstance(name_arg, list):
            name_arg = name_arg[0]

        return name_arg

    def __convert_rName_to_tdml(self, r_name):
        """
        DESCRIPTION:
            Internal function to replace r_name to tdml_name by replacing '.' with '_'.

        PARAMETERS:
            r_name:
                Required Argument.
                A String representing the r name of any argument, input, output of a function, as mentioned in the
                corresponding JSON file.
                Types: str

        RAISES:
            TypeError

        RETURNS:
            A String representing the teradataml equivalent name for the given r name.

        EXAMPLES:
            >>> self.__convert_rName_to_tdml('sequence.column')
            sequence_column

        """
        if not isinstance(r_name, str):
            raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                 'r_name', 'str'),
                            MessageCodes.UNSUPPORTED_DATATYPE)

        if r_name is not None:
            return r_name.replace(".", "_")

        return r_name

    def __add_function_input_output_entries(self, field, func_ip_op, function_map):
        """
        DESCRIPTION:
            Internal function to add entries for the functions inputs or outputs to the function argument map.

        PARAMETERS:
            field:
                Required Argument.
                Specifies one of 'inputs' or 'outputs'.
                Types: str

            func_ip_op:
                Required Argument.
                Specifies the dictionary from the JSON corresponding to the the 'inputs' or 'ouputs'.
                Types: dict

            function_map:
                Required Argument.
                Specifies the function argument map to updated and return.
                Types: dict

        RAISES:
            None.

        RETURNS:
            dict - function argument map updated with the requested information, 'input' or 'outputs'.

        EXAMPLES:
            >>> function_map = self.__add_function_input_output_entries(self, 'inputs', func_inputs, function_map)
        """
        for entry in func_ip_op:
            sql_name = entry[famc.NAME.value]
            tdml_name = self.__convert_rName_to_tdml(entry[famc.R_NAME.value])
            sql_name_to_use = self.__resolve_name(sql_name).lower()

            if isinstance(sql_name, list):
                for i in range(len(sql_name)):
                    function_map[field][famc.SQL_TO_TDML.value][sql_name[i].lower()] = tdml_name
                function_map[field][famc.TDML_TO_SQL.value][tdml_name] = sql_name_to_use

            if isinstance(sql_name, dict):
                for vv, value in sql_name.items():
                    for i in range(len(value)):
                        function_map[field][famc.SQL_TO_TDML.value][value[i].lower()] = tdml_name
                function_map[field][famc.TDML_TO_SQL.value][tdml_name] = sql_name_to_use

        return function_map

    def __update_json_dict_for_function(self, input_output_arg_map, engine, function_name, function_json):
        """
        DESCRIPTION:
            Internal function to load or update the input_output_arg_map property for the function specified.

        PARAMETERS:
            input_output_arg_map:
                Required Argument.
                Specified the dictionary to be updated with the map for the given function from the given engine.
                Types: dict

            engine:
                Required Argument.
                Specifies the name of the engine the function belongs to.
                Acceptable values: 'ML Engine', 'Advanced SQL Engine'
                Types: str

            function_name:
                Required Argument.
                Specifies the name of the function to check and load the argument mapping for.
                Types: str

            function_json:
                Required Argument.
                Specified the dictionary representing the Json file for the function.
                Types: dict

        RAISES:
            None.

        RETURNS:
            The updated input_output_arg dictionary.

            Note:
                The input_output_arg dictionary is of the following form:
                {
                    'ML Engine' : {
                        <func_name_11>: {
                            'input': {
                                'sql_to_tdml' : {
                                    '<sql_input_name_1>': '<tdml_input_name_1>',
                                    '<sql_input_name_2>': '<tdml_input_name_2>'
                                },
                                'tdml_to_sql' : {
                                    '<tdml_input_name_1>': '<sql_input_name_1>',
                                    '<tdml_input_name_2>': '<sql_input_name_2>',
                                }
                            },
                            'output': {
                                'sql_to_tdml' : {
                                    '<sql_input_name_1>': '<tdml_input_name_1>',
                                    '<sql_input_name_2>': '<tdml_input_name_2>'
                                },
                                'tdml_to_sql' : {
                                    '<tdml_input_name_1>': '<sql_input_name_1>',
                                    '<tdml_input_name_2>': '<sql_input_name_2>',
                                }
                            },
                            'arguments': {
                                'sql_to_tdml' : {
                                        'TargetColumns' : {
                                            'tdml_name': '<tdml_name>',
                                            'tdml_type': <python_type_tuple>,
                                            'used_in_formula': True or 'dependent' or 'independent',
                                            'alternate_to' : None
                                        },
                                        'CategoricalColumns': {
                                            'tdml_name': '<tdml_name>',
                                            'tdml_type': <python_type_tuple>,
                                            'used_in_formula': True or 'dependent' or 'independent',
                                            'alternate_to' : None
                                        },
                                        'Intercept1.0' : {
                                            'tdml_name': '<tdml_name>',
                                            'tdml_type': <python_type_tuple>,
                                            'used_in_formula': True or 'dependent' or 'independent',
                                            'alternate_to' : None
                                        },
                                        # This is how you would define an alternate name
                                        'InterceptNew1.1' : {
                                            'alternate_to' : 'sqlname1'
                                        },
                                        'UniqueId': {
                                            'tdml_name': ['data_sequence_input_by', 'data1_sequence_input_by']
                                            'tdml_type': str,
                                            'used_in_sequence_by': True
                                        }
                                },
                                'tdml_to_sql' : {
                                    # Keep one to one
                                    'formula' : ['<sql_name_1>', 'sql_name_2'],
                                    'data_sequence_input_by': ['UniqueId', 'SequenceInputBy'],
                                    'data1_sequence_input_by': ['UniqueId', 'SequenceInputBy'],
                                    'weight': 'WeightColumns'
                                }
                            }
                        },
                        <func_name_12>: {
                        }
                    },
                    'Advanced SQL Engine' : {
                        <func_name_21>: {
                        },
                        <func_name_22>: {
                        }
                    }
                }

        EXAMPLE:
            >>> self.__update_json_dict_for_function(input_output_arg_map, 'ML Engine', 'GLM', glm_json)

        """
        function_map = {}
        # First, let's add the tdml name for the function
        function_map[famc.FUNCTION_TDML_NAME.value] = function_json[famc.FUNCTION_TDML_NAME.value]
        # Section corresponding to arguments
        function_args = function_json[famc.ARGUMENT_CLAUSES.value]
        # Section corresponding to inputs
        function_inputs = function_json[famc.INPUT_TABLES.value]
        function_outputs = None
        if famc.OUTPUT_TABLES.value in function_json:
            # Section corresponding to outputs
            function_outputs = function_json[famc.OUTPUT_TABLES.value]

        # Create Input dict
        function_map[famc.INPUTS.value] = {}
        function_map[famc.INPUTS.value][famc.SQL_TO_TDML.value] = {}
        function_map[famc.INPUTS.value][famc.TDML_TO_SQL.value] = {}
        function_map = self.__add_function_input_output_entries(field=famc.INPUTS.value,
                                                                func_ip_op=function_inputs,
                                                                function_map=function_map)

        # Create output dict
        function_map[famc.OUTPUTS.value] = {}
        function_map[famc.OUTPUTS.value][famc.SQL_TO_TDML.value] = {}
        function_map[famc.OUTPUTS.value][famc.TDML_TO_SQL.value] = {}
        if function_outputs is not None:
            function_map = self.__add_function_input_output_entries(field=famc.OUTPUTS.value,
                                                                    func_ip_op=function_outputs,
                                                                    function_map=function_map)
            # Default output thrown back at the prompt - tdml_name is 'output'
            function_map[famc.OUTPUTS.value][famc.SQL_TO_TDML.value][
                famc.DEFAULT_OUTPUT.value] = famc.DEFAULT_OUTPUT_TDML_NAME_MULTIPLE.value
            function_map[famc.OUTPUTS.value][famc.TDML_TO_SQL.value][
                famc.DEFAULT_OUTPUT_TDML_NAME_MULTIPLE.value] = famc.DEFAULT_OUTPUT.value
        else:
            # Default output thrown back at the prompt - tdml_name is 'result'
            function_map[famc.OUTPUTS.value][famc.SQL_TO_TDML.value][
                famc.DEFAULT_OUTPUT.value] = famc.DEFAULT_OUTPUT_TDML_NAME_SINGLE.value
            function_map[famc.OUTPUTS.value][famc.TDML_TO_SQL.value][
                famc.DEFAULT_OUTPUT_TDML_NAME_SINGLE.value] = famc.DEFAULT_OUTPUT.value

        # Create argument dict
        function_map[famc.ARGUMENTS.value] = {}
        function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value] = {}
        function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value] = {}
        formula_args = []
        sequence_arg = None
        for arg in function_args:
            # Handle formula related args separately
            if famc.R_FOMULA_USAGE.value in arg and arg[famc.R_FOMULA_USAGE.value] == True:
                formula_args.append(arg)
                continue

            arg_name = arg[famc.NAME.value]
            tdml_name = self.__convert_rName_to_tdml(arg[famc.R_NAME.value])
            sql_name_to_use = self.__resolve_name(arg_name).lower()

            # Handle sequence input arg separately
            if tdml_name == famc.TDML_SEQUENCE_COLUMN_NAME.value:
                sequence_arg = arg
                continue

            python_type = self.__resolve_arg_types(arg)

            if isinstance(arg_name, list):
                for i in range(len(arg_name)):
                    # Handle all other arguments
                    if i == 0:
                        function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                    sql_name=arg_name[i],
                                                                    tdml_name=tdml_name,
                                                                    tdml_type=python_type)
                        function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                            tdml_name] = sql_name_to_use
                    else:
                        function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                    sql_name=arg_name[i],
                                                                    sql_name_to_use=sql_name_to_use,
                                                                    alternate_to=True)

            if isinstance(arg_name, dict):
                for vv, value in arg_name.items():
                    for i in range(len(value)):
                        # Handle all other arguments
                        if i == 0:
                            function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                        sql_name=value[i],
                                                                        tdml_name=tdml_name,
                                                                        tdml_type=python_type)
                            function_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value][
                                tdml_name] = sql_name_to_use
                        else:
                            function_map = self.__add_sql_to_tdml_entry(function_map=function_map,
                                                                        sql_name=value[i],
                                                                        sql_name_to_use=sql_name_to_use,
                                                                        alternate_to=True)

        if len(formula_args) > 0:
            function_map = self.__resolve_formula_args(function_map, formula_args)

        if sequence_arg is not None:
            function_map = self.__resolve_sequence_input_args(function_map, sequence_arg)

        # Finally, update the input_output_arg_map with an entry for the function
        if engine not in input_output_arg_map:
            input_output_arg_map[engine] = {}
        input_output_arg_map[engine][function_name] = function_map

        return input_output_arg_map

    def __add_sql_to_tdml_entry(self, function_map, sql_name, tdml_name=None,
                                tdml_type=None, sql_name_to_use=None, alternate_to=False):
        """
        DESCRIPTION:
            Internal function to add the SQL to teradataml entry for a function argument.

        PARAMETERS:
            function_map:
                Required Argument.
                Specifies the function argument map to update with the SQL to teradataml
                entries for the arguments.
                Types: dict

            sql_name:
                Required argument.
                Specifies the SQL name of the argumemnt to add the mapper entry for.
                Types: str

            tdml_name:
                Optional Argument. Required when alternate_to is set to False.
                Specifies the teradataml name corresponding to the given SQL name.
                When specified, must also specify tdml_type.
                Types: str

            tdml_type:
                Optional Argument. Required when alternate_to is set to False.
                Specifies the acceptable python data type for the argument.
                When specified, must also specify tdml_name.
                Types: Python type or tuple of Python types

            sql_name_to_use:
                Specifies the teradataml name to use in case there are alternate names.
                Types: str

            alternate_to:
                Specifies whether the SQL Name is an alternate to another SQL name that we wish to use.
                When set to True, must also specify sql_name and sql_name_to_use.
                Types: bool
                Default Value: False

        RAISES:
            None.

        RETURNS:
            dict - the updated function_map with the newly added entries.

        EXAMPLES:
             >>> function_map = self.__add_sql_to_tdml_entry(function_map, tdml_name, tdml_type)
        """
        if alternate_to:
            function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][sql_name.lower()] = {}
            function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][sql_name.lower()][
                famc.ALTERNATE_TO.value] = sql_name_to_use
        else:
            function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][sql_name.lower()] = {}
            function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][sql_name.lower()][
                famc.TDML_NAME.value] = tdml_name
            function_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][sql_name.lower()][
                famc.TDML_TYPE.value] = tdml_type

        return function_map

_argument_mapper = _ArgumentMapper()
