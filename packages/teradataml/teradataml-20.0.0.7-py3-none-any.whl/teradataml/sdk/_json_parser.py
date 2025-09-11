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
# This file contains the _SdkJsonParser class which is used to parse the OpenAPI specification
# JSON file and populate the required properties to be accessed later during dynamic class and 
# method generation.
# The class also exposes some properties to be used by the SDK - openapi_version,
# openapi_description, openapi_title, sdk_version, contact_details.
#
# ################################################################################################

import logging
import re

from teradataml.common.utils import UtilFuncs

from ._func_params import _SDKParam
from ._openapi_spec_constants import ContactObject as co
from ._openapi_spec_constants import DefaultConstants as dc
from ._openapi_spec_constants import InfoObject as ioo
from ._openapi_spec_constants import OpenAPIObject as oapi
from ._openapi_spec_constants import OperationObject as oo
from ._openapi_spec_constants import ParameterObject as po
from ._openapi_spec_constants import RequestBodyObject as rbo
from ._openapi_spec_constants import SchemaObject as so
from ._openapi_spec_constants import TagObject as to
from ._utils import (_camel_case, _camel_to_snake, _read_openapi_spec,
                     _remove_duplicate_preserve_order)
from .constants import ParameterTypes as pt

_logger = logging.getLogger(__name__)

class _SdkJsonParser:

    def __init__(self, openapi_spec_path, current_module, debug=False):
        self._openapi_spec = _read_openapi_spec(openapi_spec_path)
        self._current_module = current_module # Current module where the SDK needsto be generated.

        self._tag_names = [] # List of all tag names
        self._class_names = [] # List of all class names
        self._tag_description_dict = {} # Dict of tag name to tag description
        self._class_name_dict = {} # Dict of tag name to class name
        self._debug = debug # Debug flag

        self._missing_information = {} # List of missing information in the OpenAPI spec
        self._missing_information["tags"] = []
        self._missing_information["paths"] = []

        self._class_name_to_function_dict = {} # Dict of class name to function information.
        self._parse_tags()
        self._parse_paths()

    def _openapi_version(self):
        """
        Returns the OpenAPI version from the spec.
        """
        return self._openapi_spec.get(oapi.OPENAPI.value)

    def _openapi_description(self):
        """
        Returns the OpenAPI description from the spec.
        """
        return self._openapi_spec.get(oapi.INFO.value, {}).get(ioo.DESCRIPTION.value, None)

    def _openapi_title(self):
        """
        Returns the OpenAPI title from the spec.
        """
        return self._openapi_spec.get(oapi.INFO.value, {}).get(ioo.TITLE.value)
    
    def _sdk_version(self):
        """
        Returns the SDK version from the OpenAPI spec.
        """
        return self._openapi_spec.get(oapi.INFO.value, {}).get(ioo.VERSION.value)

    def _contact_details(self):
        """
        Returns contact details of the OpenAPI spec Owners.
        """
        return self._openapi_spec.get(oapi.INFO.value, {}).get(ioo.CONTACT.value, {})

    def _parse_tags(self):
        """
        Parses the OpenAPI spec to create dictionaries for tag descriptions and class names.

        """
        _tags = self._openapi_spec.get(oapi.TAGS.value, None)
        if _tags is None:
            return
        for tag in _tags:
            tag_name = tag.get(to.NAME.value)

            if tag_name:
                self._tag_names.append(tag_name)
                _tag_description = tag.get(to.DESCRIPTION.value)
                if _tag_description is None:
                    _tag_description = dc.DEFAULT_DESCRIPTION.value
                    self._missing_information["tags"].append(tag_name)
                self._tag_description_dict[tag_name] = _tag_description

                class_name = _camel_case(tag_name)
                self._class_names.append(class_name)
                self._class_name_dict[tag_name] = class_name

                self._class_name_to_function_dict[class_name] = []

    def _process_request_body(self, body, path, method, operation_id):
        """
        Processes the request body from the OpenAPI spec.
        """
        arg_list = []
        param_arg_docstrings = []
        body_params_dict = {}
        arg_info_matrix_dict = {}

        misssing_description = []

        if body is not None:
            body_obj = _SDKParam(path=path, method=method, operation_id=operation_id,
                                 current_module=self._current_module, parameter=body,
                                 param_type=pt.BODY, debug=self._debug)

            body_params_dict[body_obj._old_name] = body_obj._new_name

            if body_obj._missing_description:
                # We are saving missing argument description to CSV files to share it to team which
                # developed OpenAPI spec so that they can fix the missing information
                # in the OpenAPI spec.
                misssing_description.append(body_obj._missing_description)

            _docstr_lines = [body_obj._docstr_arg_details, body_obj._docstr_desc,
                             body_obj._docstr_perm_types, body_obj._docstr_perm_values]
            param_arg_docstrings.append(_docstr_lines)

            arg_info_matrix_dict[body_obj._new_name] = body_obj

            # arg_list.append(self.__get_param_arg_signature(p_name=body_param_name,
            #                                                p_type=schema_type,
            #                                                p_required=b_required,
            #                                                p_default="None"))

        return {"doc_strings": param_arg_docstrings, "arg_signature": arg_list,
                "body_params_dict": body_params_dict, "arg_info_matrix_dict": arg_info_matrix_dict,
                "missing_description": misssing_description}

    def _process_parameters(self, parameters, path, method, operation_id):
        """
        Processes the parameters from the OpenAPI spec.
        """        
        arg_list = []
        param_arg_docstrings = []
        path_params_dict = {} # Dictionary of old to new path params.
        query_params_dict = {} # Dictionary of old to new query params.
        arg_info_matrix_dict = {} # Dictionary of new argument to _SDKParam objects.
        missing_description = []

        if parameters is not None:
            for param in parameters:
                param_obj = _SDKParam(path=path, method=method, operation_id=operation_id,
                                      current_module=self._current_module, parameter=param,
                                      param_type=pt.PARAM, debug=self._debug)

                if param_obj._missing_description:
                    # We are saving missing argument description to CSV files to share it to team
                    # which developed OpenAPI spec so that they can fix the missing information
                    # in the OpenAPI spec.
                    missing_description.append(param_obj._old_name)

                param_obj._update_params_dict(path_params_dict=path_params_dict,
                                              query_params_dict=query_params_dict)

                _docstr_lines = [param_obj._docstr_arg_details, param_obj._docstr_desc,
                                 param_obj._docstr_perm_types, param_obj._docstr_perm_values]
                param_arg_docstrings.append(_docstr_lines)

                arg_info_matrix_dict[param_obj._new_name] = param_obj

                # arg_list.append(self.__get_param_arg_signature(p_name=p_name,
                                                            #    p_type=p_types,
                                                            #    p_required=p_required,
                                                            #    p_default=p_default))

        # `projection` argument is present in some endpoints, not in others.
        # ModelOps team says that it is used when the path contains `/search`.
        # For more info, read through comments in 
        # https://teradata-pe.atlassian.net/browse/VMO-1821

        # `projection` argument is also used by `get` endpoints of format `/api/<func_name>/{id}`.
        # Hence adding `projection` argument for those endpoints as well.

        if ("/search" in path and "projection" not in query_params_dict.keys()) or \
            (re.search(pattern=r"^/api/[a-zA-Z]+/\{id\}$", string=path) is not None and method == "get"):
            # TODO: Confirm with ModelOps team.
            #       There is "projection" parameter in query params for some endpoints
            #       but missing in some other endpoints.
            #       Need to confirm with ModelOps team if this "projection" parameter is same as
            #       excerpt projection.
            # "projection" related issues will be fixed in JSON spec by modelOps team as per
            # https://teradata-pe.atlassian.net/browse/VMO-1821.
            # Currently, adding for only those endpoints which don't have "projection" in query params.

            proj_obj = _SDKParam(path=path, method=method, operation_id=operation_id,
                                 current_module=self._current_module, param_type=pt.PROJECTION,
                                 debug=self._debug)

            if proj_obj._missing_description:
                # We are saving missing argument description to CSV files to share it to team which
                # developed OpenAPI spec so that they can fix the missing information
                # in the OpenAPI spec.
                missing_description.append(proj_obj._old_name)

            proj_obj._update_params_dict(path_params_dict=path_params_dict,
                                         query_params_dict=query_params_dict)

            _docstr_lines = [proj_obj._docstr_arg_details, proj_obj._docstr_desc,
                             proj_obj._docstr_perm_types, proj_obj._docstr_perm_values]
            param_arg_docstrings.append(_docstr_lines)

            arg_info_matrix_dict[proj_obj._new_name] = proj_obj
            # arg_list.append(self.__get_param_arg_signature(p_name=proj_obj._new_name,
            #                                                p_type=proj_obj._param_type,
            #                                                p_required=proj_obj._required,
            #                                                p_default=proj_obj._default))

        return {"doc_strings": param_arg_docstrings, "arg_signature": arg_list,
                "path_params_dict": path_params_dict, "query_params_dict": query_params_dict,
                "arg_info_matrix_dict": arg_info_matrix_dict,
                "missing_description": missing_description}

    def _process_responses(self, responses:dict, path:str, method:str, operation_id:str):
        """
        Processes the responses from the OpenAPI spec.
        """
        _all_return_types = []
        _all_code_docstrings = []
        _all_header_values = []
        
        for resp_code, response in responses.items():
            resp_obj = _SDKParam(path=path, method=method, operation_id=operation_id,
                                 current_module=self._current_module,
                                 parameter=(resp_code, response),
                                 param_type=pt.RESPONSE, debug=self._debug)

            _all_header_values.extend(resp_obj._header_values)
            if resp_obj._response_docstr:
                _all_code_docstrings.append(resp_obj._response_docstr)
            if resp_obj._return_types is not None:
                _all_return_types.extend(resp_obj._return_types)

        return {"response_docstrings": _all_code_docstrings,
                "return_types": _remove_duplicate_preserve_order(_all_return_types),
                "header_values": _remove_duplicate_preserve_order(_all_header_values)}

    def _process_security(self, security):
        """
        Processes the security details from the OpenAPI spec.
        """
        if security is None:
            return None
        return "SECURITY"

    def _process_function(self, function_details, path, method):
        """
        Processes a function from the OpenAPI spec to create a method.
        """
        ret_func_details = {}

        _missing_info = {}
        _missing_info["path"] = path
        _missing_info["method"] = method
        _missing_info["operation_id"] = function_details.get(oo.OPERATION_ID.value)
        _missing_info["missing_arg_descriptions"] = None # Default - all arg descriptions exist.


        _func_description = function_details.get(oo.DESCRIPTION.value) or \
            function_details.get(oo.SUMMARY.value)
        _missing_info["missing_func_description"] = "NO" # Default - Function description exists.
        if _func_description is None:
            _func_description = dc.DEFAULT_DESCRIPTION.value
            _missing_info["missing_func_description"] = "YES" # Function description missing.

        _operation_id = function_details.get(oo.OPERATION_ID.value)
        ret_func_details["func_description"] = _func_description
        ret_func_details["operation_id"] = _operation_id
        ret_func_details["func_name"] = _camel_to_snake(_operation_id.replace("-", '_'))
        
        request_body_dict = self._process_request_body(body=function_details.get(oo.REQUEST_BODY.value),
                                                       path=path,
                                                       method=method,
                                                       operation_id=_operation_id)
        body_arg_descriptions = request_body_dict["doc_strings"]
        body_arg_signature = request_body_dict["arg_signature"]
        body_arg_info_matrix_dict = request_body_dict["arg_info_matrix_dict"]
        ret_func_details["body_params_dict"] = request_body_dict["body_params_dict"]

        parameter_dict = self._process_parameters(parameters=function_details.get(oo.PARAMETERS.value),
                                                  path=path,
                                                  method=method,
                                                  operation_id=_operation_id)

        _missing_info["missing_arg_descriptions"] = ",".join(request_body_dict["missing_description"] + \
                                                      parameter_dict["missing_description"])

        params_arg_descriptions = body_arg_descriptions + parameter_dict["doc_strings"]
        ret_func_details["arg_signature"] = body_arg_signature + parameter_dict["arg_signature"]
        ret_func_details["path_params_dict"] = parameter_dict["path_params_dict"]
        ret_func_details["query_params_dict"] = parameter_dict["query_params_dict"]
        ret_func_details["arg_info_matrix_dict"] = {**parameter_dict["arg_info_matrix_dict"],
                                                    **body_arg_info_matrix_dict}

        response_dict = self._process_responses(responses=function_details.get(oo.RESPONSES.value),
                                                path=path,
                                                method=method,
                                                operation_id=_operation_id)
        ret_func_details["return_types"] = response_dict["return_types"]
        ret_func_details["header_values"] = response_dict["header_values"]

        ret_func_details["required_security"] = self._process_security(function_details.get(oo.SECURITY.value))


        _doc_string = self._build_docstring(params_arg_descriptions=params_arg_descriptions,
                                            response_docstrings=response_dict["response_docstrings"])

        if self._debug:
            print(f"\nPath: {path}, Method: {method}, "\
                  f"OperationID: {ret_func_details['operation_id']}, "\
                  f"function name: {ret_func_details['func_name']}")
            print("request body dict: \n", request_body_dict)
            print("parameter dict: \n", parameter_dict)
            print(f"Doc string: \n{_doc_string}\n\n")

        # TODO: Add response details to doc string.
        ret_func_details["doc_string"] = _doc_string

        self._missing_information["paths"].append(_missing_info)

        return ret_func_details

    def _build_docstring(self, params_arg_descriptions, response_docstrings=None):
        _doc_string = (
        "     DESCRIPTION: \n"
        "         The function '{function_name}' does the following: \n"
        "         - {description}\n\n"
        )

        # Parameters section.
        _comma_with_tab = "\t     "
        _doc_string += "     PARAMETERS:\n"
        if params_arg_descriptions:
            for param in params_arg_descriptions:
                _doc_string_1 = "         " + param[0] + "\n"
                _doc_string_2 = f"{_comma_with_tab}{param[1]}\n"
                _doc_string += _doc_string_1 + _doc_string_2

                if param[3] is not None:
                    # Permitted values can be None i.e., no permitted values.
                    _doc_string += f"{_comma_with_tab}{param[3]}\n"

                _doc_string += f"{_comma_with_tab}{param[2]}\n\n" # permitted types
        else:
            _doc_string += "         None\n\n"

        if params_arg_descriptions:
            # Add another argument `return_dict` to the docstring, if parameters exist.
            _doc_string += "         return_dict (Optional):\n"
            _doc_string += f"{_comma_with_tab}Specifies whether to return dict. When set to" \
                f" False, schema class objects are returned. Otherwise, the function" \
                f" returns dict.\n{_comma_with_tab}If the API in the backend does not return" \
                " schema object, the function returns the output as it is returned by backend, "\
                "irrespective of this argument's value.\n"
            _doc_string += f"{_comma_with_tab}Default Value: False\n"
            _doc_string += f"{_comma_with_tab}Types: bool\n\n"

        # Returns section.
        _doc_string += "     RETURNS:\n"
        for resp_doc in response_docstrings:
            _doc_string += "         - " + resp_doc + "\n"
        _doc_string += "\n"


        # Raises section.
        _doc_string += "     RAISES:\n"
        _doc_string += "         - requests.exceptions.HTTPError\n"
        _doc_string += "         - teradataml.common.exceptions.TeradatamlException\n"
        _doc_string += "         - teradataml.common.exceptions.TeradatamlRestException\n\n"

        # Examples section.
        _doc_string += "     EXAMPLES:\n"
        _doc_string += (
            "         # Instantiate client object. It can be specific client for SDK. Using `Client` now.\n"
            "         >>> from teradataml.sdk import Client # For, modelops SDK, use `teradataml.sdk.modelops.ModelOpsClient`.\n"
            "         >>> client = Client(...) # Run `help(Client)` or `help(ModelOpsClient)` for supported arguments.\n\n"
            "         # Instantiate SDK class '{class_name}' from module '{module_name}'.\n"
            "         >>> from {module_name} import {class_name}\n"
            "         >>> obj = {class_name}(client=client)\n"
            "         >>> obj.{function_name}(...)\n\n"
        )

        return _doc_string

    def _print_classes(self, module_name, sdk_name):
        """
        Print available classes for the SDK.
        """
        parent_module = module_name.__name__

        print("----------------------------------------------------------------")
        print(f"Available classes for {sdk_name} SDK:")
        for _class_name in self._class_names:
            print(f"    * {parent_module}.{_class_name}")
        print("----------------------------------------------------------------")

    def _parse_paths(self):
        """
        Parses the OpenAPI spec to create dictionaries for path details.
        """
        paths = self._openapi_spec[oapi.PATHS.value]

        _is_empty_tag = False

        # Create classes and attach methods
        for path, methods in paths.items():
            for method, details in methods.items():
                tags_ = details.get(oo.TAGS.value, [dc.DEFAULT_TAG.value])
                if tags_[0] == dc.DEFAULT_TAG.value and not _is_empty_tag:
                    _is_empty_tag = True
                    class_name = dc.DEFAULT_CLASS.value
                    self._tag_names.append(tags_[0])
                    self._tag_description_dict[tags_[0]] = dc.DEFAULT_TAG_DESC.value

                    self._class_names.append(class_name)
                    self._class_name_dict[dc.DEFAULT_TAG.value] = class_name
                    self._class_name_to_function_dict[class_name] = []


                processed_func_details = self._process_function(details, path, method)
                processed_func_details["path"] = path
                processed_func_details["method"] = method

                for tag_ in tags_:
                    class_name = self._class_name_dict[tag_]

                    self._class_name_to_function_dict[class_name].append(
                        (details, processed_func_details))
