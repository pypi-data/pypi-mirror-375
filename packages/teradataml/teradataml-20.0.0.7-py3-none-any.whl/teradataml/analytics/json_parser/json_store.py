"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements the class _JsonStore, which stores the json data for analytic functions.
_JsonStore will be used to access the json data of analytic functions. so, one should refer to
_JsonStore to access the json data instead of parsing the json data again.
"""
import sys
from teradataml.analytics.json_parser.metadata import _AnlyFuncMetadata
from teradataml.common.constants import TeradataAnalyticFunctionInfo
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.exceptions import TeradataMlException
from teradataml.utils.validators import _Validators


class _JsonStore:
    """ An internal class for storing json data. """
    __data = {}
    version = None
    # Functions to exclude from json store.
    _functions_to_exclude = {"NaiveBayesPredict", "DecisionTreePredict"}
    # Store a nested map between function type, category and corresponding list of function names.
    _func_type_category_name_dict = {}

    @classmethod
    def add(cls, json_object):
        """
        DESCRIPTION:
            Function to add the json object to _JsonStore.

        PARAMETERS:
            json_object:
                Required Argument.
                Specifies the json object.
                Types: Object of type _AnlyFuncMetadata

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Add json data for XGBoost.
            _JsonStore.add(xg_boost_json_data)
        """
        # Validate whether the json object is of type _AnlyFuncMetadata or not.
        arg_info_matrix = [["json_object", json_object, False, _AnlyFuncMetadata]]
        _Validators._validate_function_arguments(arg_info_matrix)

        cls.__data[json_object.func_name] = json_object

    @classmethod
    def clean(cls):
        """
        DESCRIPTION:
            Function to clean the json store. This function does below:
            * Removes all the analytic functions attached to teradataml from _JsonStore.
            * Remove all json objects from _JsonStore.
            * unset the json store version.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # remove all json objects from _JsonStore.
            _JsonStore.clean()
        """
        cls.__data.clear()
        cls._func_type_category_name_dict.clear()
        cls.version = None

    @classmethod
    def get_function_metadata(cls, analytic_function_name):
        """
        DESCRIPTION:
            Function to get the Analytic function metadata a.k.a json object.

        PARAMETERS:
            analytic_function_name:
                Required Argument.
                Specifies the analytic function name.
                Types: str

        RETURNS:
            Object of type _AnlyFuncMetadata

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Get json data for XGBoost.
            _JsonStore.get_function_metadata("XGBoost")
        """
        # Validate whether the analytic_function_name is of type str or not.
        arg_info_matrix = [["analytic_function_name", analytic_function_name, False, str]]
        _Validators._validate_function_arguments(arg_info_matrix)

        if analytic_function_name in cls.__data:
            return cls.__data[analytic_function_name]
        else:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.INVALID_FUNCTION_NAME,
                                     analytic_function_name),
                MessageCodes.INVALID_FUNCTION_NAME)

    @classmethod
    def _get_function_list(cls):
        """
        DESCRIPTION:
            Function to get the list of available analytic functions.

        PARAMETERS:
            None

        RETURNS:
            tuple 
                - Containing dictionary with key as function name and 
                  value as function metadata object, list of excluded functions.

        RAISES:
            None

        EXAMPLES:
            _JsonStore._get_function_list()
        """
        return cls.__data,  list(cls._functions_to_exclude)

    @classmethod
    def _get_func_type_category_name_dict(cls):
        """
        DESCRIPTION:
            Function to get the dictionary having information about IN-DB
            function types, categories if available and list of analytic
            functions.

        PARAMETERS:
            None

        RETURNS:
            dictionary
                - Having key as function type and value as either a list of
                  functions of that function type or a dictionary with key
                  as function category and value as list of functions of
                  that category.

        RAISES:
            None

        EXAMPLES:
            _JsonStore._get_func_type_category_name_dict()
        """
        if len(cls._func_type_category_name_dict) > 0:
            return cls._func_type_category_name_dict
        else:
            # Create a nested map between function type, category and corresponding
            # list of function names.
            # Add entry for functions which are not part of IN-DB framework.
            func_type_category_name_dict = {"SQLE": {"Model Scoring": ["DecisionTreePredict",
                                                                       "NaiveBayesPredict"]}}

            # Iterate over metadata and populate information in dictionary.
            if len(cls.__data) > 0:
                # Create the dictionary and update it with the function type
                # and category.
                for func_name, func_metadata in cls.__data.items():
                    if func_metadata.func_category:
                        func_type_category_name_dict.setdefault(getattr(TeradataAnalyticFunctionInfo,
                                                                        func_metadata.func_type.upper()).
                                                                value["display_function_type_name"], {}).\
                            setdefault(func_metadata.func_category, []).append(func_name)

                    else:
                        func_type_category_name_dict.setdefault(getattr(TeradataAnalyticFunctionInfo,
                                                                func_metadata.func_type.upper()).
                                                                value["display_function_type_name"], []). \
                                                                append(func_name)

            # Update nested dictionary in _JsonStore and return the same.
            cls._func_type_category_name_dict = func_type_category_name_dict
            return func_type_category_name_dict

