# ################################################################################################
# 
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Adithya Avvaru (adithya.avvaru@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# 
# Version: 1.0
# ModelOps SDK Version: 1.0
#
# This file contains _SDKParam class which is used to create SDK function parameters'
# argInfoMatrix.
# 
# ################################################################################################

import logging
from typing import Any, Dict, Tuple, Union

from ._openapi_spec_constants import DefaultConstants as dc
from ._openapi_spec_constants import ParameterObject as po
from ._openapi_spec_constants import RequestBodyObject as rbo
from ._openapi_spec_constants import SchemaObject as so

from._openapi_spec_constants import ResponseObject as ro
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.utils import UtilFuncs
from teradataml.sdk._utils import _remove_duplicate_preserve_order

from ._openapi_spec_constants import MediaTypeObject as mto
from ._utils import _camel_to_snake
from .constants import \
    _OPENAPI_TO_PYTHON_PARAM_TYPE_MAPPER as param_type_mapper
from .constants import ParameterTypes

_logger = logging.getLogger(__name__)

class _SDKParam(object):
    """
    Base class for SDK function parameters.
    """

    def __init__(self, path: str, method: str, operation_id: str,
                 current_module: Any,
                 # Dict for parameters - body, path, query.
                 # Tuple for response - (response_code, response_value).
                 parameter: Union[Dict, Tuple[str, Dict[str, Any]]]=None,
                 param_type: ParameterTypes=ParameterTypes.PARAM,
                 check_empty: bool=True,
                 debug: bool=False,
                 process_header_values: bool=False):
        """
        DESCRIPTION:
            Initialize the SDK function parameters.

        PARAMETERS:
            * path (str): The path of the API endpoint.
            * method (str): The HTTP method of the API endpoint.
            * operation_id (str): The operation ID of the API endpoint.
            * current_module (Any): The current module where the SDK function is defined.
            * parameter (Union[Dict, Tuple[str, Dict[str, Any]]]): The parameter dictionary or
                a tuple containing the response code and response value.
            * param_type (ParameterTypes): The type of the parameter (e.g., PARAM, BODY, PROJECTION, RESPONSE).
            * check_empty (bool): Whether to check for empty string values in the parameter.
            * debug (bool): Whether to enable debug mode for logging.
            * process_header_values (bool): Whether to process header values for response parameters.
        """
        self._parameter = self._response = None
        if param_type == ParameterTypes.RESPONSE:
            self._response_code = parameter[0]
            self._response = parameter[1]
        else:
            self._parameter = parameter
        self._check_empty = check_empty
        self._debug = debug
        self._path = path
        self._method = method
        self._operation_id = operation_id
        self._current_module = current_module
        self._missing_description = None
        if param_type == ParameterTypes.PARAM:
            self._process_regular_parameter()
        elif param_type == ParameterTypes.BODY:
            self._process_body_parameter()
        elif param_type == ParameterTypes.PROJECTION:
            self._process_projection_query_parameter()
        elif param_type == ParameterTypes.RESPONSE:
            self._process_response_parameter(process_header_values=process_header_values)

    def _update_params_dict(self, path_params_dict:dict, query_params_dict:dict):
        """
        Update the path and query parameters dictionaries with key as old parameter name
        (as in spec) and value as the new parameter names, based on path or query parameter type.
        Args:
            path_params_dict (dict): The dictionary of path parameters.
            query_params_dict (dict): The dictionary of query parameters.
        """
        if self._in == "path":
            # Path parameters are mandatory.
            path_params_dict[self._old_name] = self._new_name
        elif self._in == "query":
            # Query parameters are optional.
            query_params_dict[self._old_name] = self._new_name
        else:
            raise ValueError(f"Unsupported parameter type: {self._in}. "\
                             "Currently only path and query parameters are supported.")

    def _process_regular_parameter(self):
        """
        Process the parameter to extract relevant information.
        """
        param = self._parameter

        self._old_name = param.get(po.NAME.value)
        self._new_name = _camel_to_snake(self._old_name)

        # If the "required" field is not specified, the default value depends on the in value:
        #  in: path → "required" defaults to True (mandatory).
        #  in: query, in: header, and in: cookie → required defaults to False (optional).

        self._in = param.get(po.IN.value)
        # Default for required field is False for query, cookie and header params.
        p_required = True if self._in == "path" else False

        _req_key_name = po.REQUIRED.value
        self._required = param.get(_req_key_name) == True or param.get(_req_key_name) == "true" \
            or p_required

        _schema = param.get(po.SCHEMA.value)

        if not _schema:
            print(f"Warning: No schema found for parameter {self._old_name}. Not processing it.")
        else:
            self.__process_schema(_schema)

        _description = param.get(rbo.DESCRIPTION.value)
        if _description is None:
            _description = dc.DEFAULT_DESCRIPTION.value
            self._missing_description = self._old_name
            if self._debug:
                msg = self.__get_warning_message(
                    not_provided=f"Description of path/query parameter '{self._old_name}'",
                    default_value=f"description '{_description}'")
                _logger.warning(msg=msg)

        self.__build_docstring(self._in, _description)

    def __build_permitted_types_str(self):
        """
        Builds and returns a string representation of the permitted types for the object.
        This method iterates over the `_permitted_types` attribute, which is expected to be a list
        of types or other objects. 
        Note:
            If `_permitted_types` is empty, the default string "dict" is used.

        Returns:
            str: A string describing the permitted types, formatted as "Types: <types>".
        """

        _perm_list = []
        for a in self._permitted_types:
            try:
                _perm_list.append(a.__name__)
            except AttributeError:
                # Handle case where a is not a class or does not have __name__ attribute
                _perm_list.append(a)
        _permitted_str = ", ".join(_perm_list) if self._permitted_types else "dict"
        return f"Types: {_permitted_str}"

    def __build_docstring(self, in_: str, description: str, incl_in: bool=False):
        """
        Build the docstring for the parameter, given whether in path/query/body and description.
        """
        _req_str = "Required" if self._required else "Optional"

        # Docstring containing arg details - name, optional/required, query/path/body.
        self._docstr_arg_details = f"{self._new_name} ({_req_str})"
        if incl_in:
            # If 'in' is included, append it to the arg details.
            self._docstr_arg_details += f" ({in_}):"
        else:
            # If 'in' is not included, append it to the arg details.
            self._docstr_arg_details += ":"
        # Docstring containing description.
        self._docstr_desc = description
        # Docstring containing permitted types.
        self._docstr_perm_types = self.__build_permitted_types_str()
        # Docstring containing permitted values.
        self._docstr_perm_values = None
        if self._permitted_values:
            _permitted_values_str = ", ".join([str(v) for v in self._permitted_values])
            self._docstr_perm_values = f"Permitted values: {_permitted_values_str}"

    def _process_body_parameter(self):
        """
        Process the body parameter to extract relevant information.
        """
        body = self._parameter

        # Only one requestBody is allowed per operation.
        # Use oneOf or anyOf for multiple schema possibilities.
        # Use different media types to handle various content types.
        # TODO: So, body.get("content", {}) can have multiple content types.

        _schema = body.get(rbo.CONTENT.value, {}).get("application/json", {}).get("schema")

        if _schema:
            self._old_name = "body"
            self._new_name = "body"
            self._in = "body"

            # "required" field documentation in https://swagger.io/specification/#request-body-object
            # required,	boolean, Determines if the request body is required in the request. Defaults to false.
            self._required = body.get(rbo.REQUIRED.value)

            if self._required is None:
                self._required = False
                if self._debug:
                    msg = self.__get_warning_message(not_provided="'required' field of requestBody",
                                                     default_value=f"value '{self._required}'")
                    _logger.warning(msg=msg)

            self.__process_schema(_schema)

            _description = body.get(rbo.DESCRIPTION.value)
            if _description is None:
                # If description is None, set it to default value.
                _description = "Specifies body description."
                self._missing_description = "requestBody"
                if self._debug:
                    msg = self.__get_warning_message(not_provided=f"Description of 'requestBody'",
                                                     default_value=f"description '{_description}'")
                    _logger.warning(msg=msg)

            self.__build_docstring("body", _description)

        else:
            # If there is no schema.
            print("Warning: No schema found for 'requestBody'. Not processing it.")

    def _process_projection_query_parameter(self):
        """
        Set required class variables to add "projection" as query parameter.
        """
        self._old_name = "projection"
        self._new_name = "projection"
        self._in = "query"
        self._required = False
        self._permitted_types = (str,)
        self._permitted_values = None
        self._default = None
        # Docstring containing arg details - name, optional/required, query/path/body.
        self._docstr_arg_details = "projection (Optional) (query):"
        # Docstring containing description.
        self._docstr_desc = "Specifies the projection type."
        # Docstring containing permitted types.
        self._docstr_perm_types = "Types: str"
        # Docstring containing permitted values.
        self._docstr_perm_values = None
        self._missing_description = "projection" # Description is not provided for projection.
        if self._debug:
            msg = self.__get_warning_message(
                not_provided="Description of path parameter 'projection'",
                default_value=f"description '{self._docstr_desc}'")
            _logger.warning(msg=msg)

    def _process_response_parameter(self, process_header_values: bool=False):
        """
        Process the response parameter to extract relevant information.
        """
        _int_code = int(self._response_code)
        _content:Dict = self._response.get(ro.CONTENT.value)
        _description = self._response.get(ro.DESCRIPTION.value)
        if _description is None:
            _description = UtilFuncs._get_http_status_phrases_description()[_int_code]["phrase"]

        self._permitted_types = None
        self._permitted_values = None
        self._return_types = []
        self._header_values = []

        self._response_docstr = f"{_int_code} ({_description})"

        if _content:
            self._process_response_content(_content)
            
            self._header_values = _remove_duplicate_preserve_order(self._header_values)

            _other_output = ""
            if self._return_types:
                # If return types are found, build the permitted types string.
                self._return_types = _remove_duplicate_preserve_order(self._return_types)
                _other_output += f"{', '.join([t.__name__ for t in self._return_types])}"

            if self._header_values and process_header_values:
                if _other_output != "":
                    _other_output += " "
                _other_output += f"{self._header_values}"

            if _other_output != "":
                self._response_docstr += f": {_other_output}"

    def _process_response_content(self, content:dict):
        """
        Process the response content to extract relevant information - like header values and return types.

        Args:
            content (dict): The response content dictionary.

        This method updates the _header_values and _return_types attributes based on the response content.
        For 2xx response codes, it processes the schema to populate permitted types and values.
        """
        _int_code = int(self._response_code)
        for _resp_header, _resp_schema in content.items():
            self._header_values.append(_resp_header)
            if 200 <= _int_code < 300:
                _schema_obj = _resp_schema.get(mto.SCHEMA.value, {})
                self.__process_schema(_schema_obj) # popualates permitted types and values.
                self._return_types.extend(list(self._permitted_types))
            else:
                self._response_docstr = None

    def get_arg_info_list(self, arg_value: Any):
        """
        Get the argument information list.

        Returns:
            list: A list containing the argument information.
        """
        # arginfomatrix:
        # 0 - arg_name
        # 1 - arg_value
        # 2 - is_optional or not - False means the argument is required.
        # 3 - permitted Data types
        # 4 - empty string check - True means the argument should be checked for empty string.
        # 5 - permitted values if not None
        return [self._new_name, arg_value, self.is_optional, self._permitted_types,
                self._check_empty, self._permitted_values]

    def __get_warning_message(self, not_provided: str, default_value: str):
        """
        Get the warning message for missing description.

        Args:
            not_provided (str): The name/info of the parameter that is not provided.
            default_value (str): The default info to be used.

        Returns:
            str: The warning message.
        """
        return Messages.get_message(MessageCodes.INFO_NOT_PROVIDED_USE_DEFAULT,
                                    not_provided,
                                    self._path,
                                    self._method,
                                    self._operation_id,
                                    default_value)

    @property
    def is_optional(self):
        """
        Check if the parameter is optional.

        Returns:
            bool: True if the parameter is optional, False otherwise.
        """
        return not self._required

    @property
    def param_name(self):
        """
        Get the parameter name.

        Returns:
            str: The parameter name.
        """
        return self._new_name

    @property
    def permitted_types(self):
        """
        Get the permitted types for the parameter.

        Returns:
            tuple: A tuple containing the permitted types.
        """
        return self._permitted_types

    @property
    def permitted_values(self):
        """
        Get the permitted values for the parameter.

        Returns:
            list: A list of permitted values.
        """
        return self._permitted_values

    # def __get_param_arg_signature(self):
    #     """
    #     Returns the parameter argument signature.
    #     """
    #     # TODO: Need some modification here. Seems to be incorrect for required and default values.
    #     param_arg_signature_value = f"{p_name}"
    #     if p_required or p_default == "None":
    #         param_arg_signature_value = f"{param_arg_signature_value} = None"
    #     elif p_default:
    #         param_arg_signature_value = f"{param_arg_signature_value} = {p_default}"
    #     return param_arg_signature_value


    def __process_schema(self, schema:dict):
        """
        Process the schema to extract relevant information.

        Args:
            schema (dict): The schema to process.

        Returns:
            tuple: A tuple containing the permitted types and values.
        """
        _schema_ref = schema.get(so.REF.value)
        if _schema_ref:
            # If $ref exists, use the last part of the reference as the type.
            # Example: "#/components/schemas/ModelOps" -> permitted type is ("ModelOps", dict).
            # For body, permitted values and default values are not applicable.
            _ref_obj_name = _schema_ref.split("/")[-1]
            # TODO: See if we can use this ref_obj_name as argument name.
            #       Uncomment below line if we have to use it.
            # self._new_name = _camel_to_snake(_ref_obj_name)

            # Schema classes are present in models module of the current module.
            models_module = None
            try:
                # If $ref is used, it should be present in the "models" module.
                models_module = getattr(self._current_module, "models")
            except AttributeError as e:
                raise AttributeError(f"Module {self._current_module.__name__} does not have 'models' "
                                     "attribute to access schema classes.") from e
            try:
                schema_class = getattr(models_module, _ref_obj_name)
            except AttributeError as e:
                raise AttributeError(f"Module '{self._current_module.__name__}.models' does not have "
                                     f"'{_ref_obj_name}' class.") from e

            self._permitted_types = (schema_class, dict)
            # Special case for JsonNode because of issue in ModelOps OpenAPI spec.
            # TODO: Remove this if condition and add check for list/array when this is fixed as
            #       part of https://teradata-pe.atlassian.net/browse/VMO-1881.
            if _ref_obj_name == "JsonNode":
                self._permitted_types = (dict, list)

            self._permitted_values = None
            self._default = None
            return

        # If no schema type is found, default to dict.
        p_type = schema.get(so.TYPE.value, dc.DEFAULT_SCHEMA_TYPE.value) \
                    if schema else dc.DEFAULT_SCHEMA_TYPE.value

        # Default to dict if not found in the mapper.
        p_type = param_type_mapper.get(p_type, dict)
        self._permitted_types = (p_type,)
        if p_type == list:
            # If the type is list, check types of items in the schema.
            elem_type = schema.get(so.ITEMS.value, {}).get(so.TYPE.value, dc.DEFAULT_SCHEMA_TYPE.value)
            if elem_type in param_type_mapper:
                self._permitted_types = (param_type_mapper[elem_type], list)
            else:
                # Default to dict OR list of dicts if not found in the mapper.
                self._permitted_types = (dict, list)

        # Get permitted enum values from Schema object.
        self._permitted_values = schema.get(so.ENUM.value)

        self._default = schema.get(so.DEFAULT.value, dc.DEFAULT_SCHEMA_VALUE.value) \
            if schema else dc.DEFAULT_SCHEMA_VALUE.value

    def __repr__(self):
        """
        Return a string representation of the SDK function parameters.

        Returns:
            str: String representation of the SDK function parameters.
        """
        return f"{self.__class__.__name__}" +\
            f"(param_name={self._new_name}, is_optional={not self._required}, ...)"