# ################################################################################################
# 
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Adithya Avvaru (adithya.avvaru@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# 
# Version: 1.0
# SDK Version: 1.0
#
# This file contains utility functions for the OpenAPI SDK.
#
# ################################################################################################

import json
import re
from typing import List, Union

from pydantic import BaseModel, ValidationError

from teradataml.utils.validators import _Validators

from .constants import _REQUEST_FUNCTION_MAPPER


# Define a function to create dynamic classes
def _constructor(self, client):
    """
    Constructor for the dynamic class.
    :param client: The client instance to be used by the class.
    """
    self._client = client

def _read_openapi_spec(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    return json.loads(content)

def _select_header_accept(accepts: List[str]):
    """
    converts list of header into a string

    Return:
        (str): request header
    """
    if not accepts:
        return

    return ", ".join([x.lower() for x in accepts])

def _remove_duplicate_preserve_order(lst: List[str]) -> List[str]:
    """
    Removes duplicates from a list while preserving the order of elements.

    Parameters:
        lst (List[str]): The input list from which duplicates need to be removed.

    Returns:
        List[str]: A new list with duplicates removed, preserving the original order.
    """
    # Since order of return types matter, converting to sets will not retain order.
    # Hence, removing duplicates using a dictionary and list to run in O(n) time.
    _truncated_dict = {}
    _truncated_values = []
    for _header_type in lst:
        if _truncated_dict.get(_header_type) is None: # O(1) check.
            _truncated_dict[_header_type] = True
            _truncated_values.append(_header_type)
    return _truncated_values

# Get string to camel case
def _camel_case(s):
    """
    This is a function to convert a string to camel case, for generating class names.
    "Hello world" -> "HelloWorld"
    """
    return ''.join([i.title() for i in s.split()])

# Convert camelCase to snake_case
def _camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def _create_dynamic_method(processed_function_details, raw_function_details, debug):
    def dynamic_function(*c, **kwargs):
        self = c[0]
        if len(c) > 1:
            _class_name  = self.__class__.__name__
            _func_name = processed_function_details["func_name"]
            raise ValueError("Only keyword arguments are allowed. " + \
                             f"Please check help({_class_name}.{_func_name}) for supported arguments.")

        # dynamic_function.__doc__ = processed_function_details.get("doc_string")

        # Mapping of old (in OpenAPI spec) to new (in function signature) param names.
        _all_params_mapping = processed_function_details.get("query_params_dict").copy()
        _all_params_mapping.update(processed_function_details.get("path_params_dict", {}))

        _arg_info_matrix_all_args_dict = processed_function_details.get("arg_info_matrix_dict", {})

        arg_info_matrix = []

        # Process path and query params.
        parameters = raw_function_details.get("parameters", [])
        path_params_to_values = {}
        query_params_to_values = {}

        # Returns Pydantic model by default. Returns JSON if enabled in kwargs.
        _return_dict = kwargs.get("return_dict", False)

        for param in parameters:
            old_param_name = param['name']
            new_param_name = _all_params_mapping.get(old_param_name, old_param_name)
            func_base_obj = _arg_info_matrix_all_args_dict[new_param_name]
            arg_info_matrix.append(func_base_obj.get_arg_info_list(kwargs.get(new_param_name)))

            if param.get('in') == 'path':
                path_params_to_values[param['name']] = kwargs.get(new_param_name)
            elif param.get('in') == 'query':
                query_params_to_values[param['name']] = kwargs.get(new_param_name)

        # If projection is added to the query params as special case (workaround).
        # "projection" related issues will be fixed in JSON spec by modelOps team as per
        # https://teradata-pe.atlassian.net/browse/VMO-1821.
        if "projection" in _all_params_mapping and "projection" not in query_params_to_values:
            old_param_name = "projection"
            new_param_name = _all_params_mapping.get(old_param_name, old_param_name)
            func_base_obj = _arg_info_matrix_all_args_dict[new_param_name]
            arg_info_matrix.append(func_base_obj.get_arg_info_list(kwargs.get(new_param_name)))
            query_params_to_values[old_param_name] = kwargs.get(new_param_name)

        # Process body params.
        body_params = {}
        body_params_dict = processed_function_details.get("body_params_dict", {})
        for old_param_name, new_param_name in body_params_dict.items():
            # old_param_name will always be "body" for body params.
            func_base_obj = _arg_info_matrix_all_args_dict[new_param_name]
            param_value: Union[dict, BaseModel] = kwargs.get(new_param_name)
            arg_info_values = func_base_obj.get_arg_info_list(param_value)
            arg_info_matrix.append(arg_info_values)

            if func_base_obj._in == 'body':
                # Check if the value passed in body params is of schema type.
                # If it is, convert it to dict if it's a Pydantic model.
                if isinstance(param_value, arg_info_values[3][0]):
                    param_value = param_value.model_dump(by_alias=True, exclude_unset=True)
                body_params[old_param_name] = param_value

        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        header_values = processed_function_details.get("header_values", [])

        header_dict = self._client._prepare_header_dict(accept=header_values)

        method = processed_function_details.get("method").lower()
        path = processed_function_details.get("path")

        all_params = {"path": path.format(**path_params_to_values),
                      "header_params": header_dict, "query_params": query_params_to_values}
        if method != 'get':
            all_params = {**all_params, **body_params}

        if debug:
            print("\nBuilt arg_info_matrix:\n", arg_info_matrix)
            print("\nHeader values:\n", header_values)
            print(f"\nCalling '{method}' request with params:\n{all_params}")

        ret_opt = getattr(self._client, _REQUEST_FUNCTION_MAPPER[method])(**all_params)

        if isinstance(ret_opt, dict) and _return_dict == False:
            for return_type_ in processed_function_details["return_types"]:
                if issubclass(return_type_, BaseModel):
                    return return_type_(**ret_opt)

        return ret_opt

    return dynamic_function

def _get_function_name_from_mapper(current_module, processed_function_details, raw_function_details):
    """
    Get function name from the developer defined dictionary.
    If not found, use the function name created from operationID of the OpenAPI spec.
    """
      # Get function name from the developer defined dictionary.
    # If not found, use the function name created from operationID of the OpenAPI spec.
    func_name = processed_function_details["func_name"]
    _mapper = getattr(getattr(current_module, "module_constants"), # _constants.py of module.
                        "_DEV_DEFINED_CLASS_FUNCTIONS_MAPPER")
    _path = processed_function_details["path"]
    _method = processed_function_details["method"]
    _mapper_details_for_fn = _mapper.get(_path, {}).get(_method, {})

    if _mapper_details_for_fn:
        _operation_id_from_mapper = _mapper_details_for_fn.get("operationID")
        _operation_id_from_spec = raw_function_details.get("operationId")
        if _operation_id_from_mapper != _operation_id_from_spec:
            raise ValueError(f"OperationID in the mapper for the path '{_path}' and method "\
                                f"'{_method}' does not match with OpenAPI spec. Please update "\
                                "the mapper with the correct operationID.")
        # Update the function name with the one from the mapper.
        func_name = _mapper_details_for_fn.get("function_name")
    return func_name

def _create_methods(json_parser, current_module, debug):
    for tag in json_parser._tag_names:
        _class_name = json_parser._class_name_dict[tag]

        # Create class methods dynamically from functions defined by json parser in
        # `_class_name_to_function_dict`.
        for function_details in json_parser._class_name_to_function_dict[_class_name]:
            _raw_function_details = function_details[0]
            _processed_function_details = function_details[1]

            method_func = _create_dynamic_method(_processed_function_details,
                                                 _raw_function_details,
                                                 debug=debug)
            method_func.__doc__ = _processed_function_details["doc_string"]

            # Set the function name to the one from the mapper if it exists.
            # Otherwise, use the one from the OpenAPI spec.
            new_func_name = _get_function_name_from_mapper(current_module,
                                                           _processed_function_details,
                                                           _raw_function_details)

            # Update the docstring to use new function name from mapper, if exists.
            method_func.__name__ = new_func_name
            method_func.__doc__ = _processed_function_details["doc_string"].format(
                function_name=new_func_name,
                description=_processed_function_details["func_description"],
                class_name=_class_name,
                module_name=current_module.__name__)

            setattr(getattr(current_module, _class_name), method_func.__name__, method_func)