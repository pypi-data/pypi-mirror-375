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
# This file initializes the ModelOps SDK by reading the OpenAPI specification file and dynamically
# creating classes and methods based on the parsed JSON data. It also provides a mechanism to
# generate classes and methods for the SDK using the OpenAPI spec.
# 
# ################################################################################################

import os
import sys

import pandas as pd

from teradataml.common.garbagecollector import GarbageCollector

from .._json_parser import _SdkJsonParser
from .._utils import _constructor, _create_methods
from ..constants import SdkNames, SdkPackagePaths
from . import _constants as module_constants
from . import models
from ._client import ModelOpsClient

_debug = False

__current_module = sys.modules[__name__]

def _generate_sdk(openapi_json_path):
    """
    Function takes path to OpenAPI spec json, creates dynamic classes and class modules.
    It also returns object of _SdkJsonParser which contains the fields for processing.
    """
    _json_parser = _SdkJsonParser(openapi_spec_path=openapi_json_path,
                                  current_module=__current_module,
                                  debug=_debug)

    for _tag_name, _class_name in _json_parser._class_name_dict.items():
        _class_namespaces = {"__doc__": _json_parser._tag_description_dict[_tag_name],
                             "__init__": _constructor}
        globals()[_class_name] = type(_class_name, (object,), _class_namespaces)

    _create_methods(_json_parser, __current_module, debug=_debug)

    return _json_parser

_json_parser = _generate_sdk(SdkPackagePaths.MODELOPS.value)

def _write_missing_information_to_csv():
    """
    This function is used to save the missing information about paths and tags to CSV files to
    share it to team which developed OpenAPI spec so that they can fix the missing information
    in the OpenAPI spec.
    """
    global _json_parser
    missing_info = _json_parser._missing_information
    temp_dir = GarbageCollector._get_temp_dir_name()
    df = pd.DataFrame(missing_info["paths"])
    file_path = os.path.join(temp_dir, 'missing_information_in_paths.csv')  # Save as CSV instead of Excel
    df.to_csv(file_path, index=False)  # Write to CSV
    print(f"Missing paths information written to {file_path}")

    df = pd.DataFrame(missing_info["tags"], columns=["missing_tag_description"])
    file_path = os.path.join(temp_dir, 'missing_description_for_tags.csv')  # Save as CSV instead of Excel
    df.to_csv(file_path, index=False)  # Write to CSV
    print(f"Missing tags description written to {file_path}")


def blueprint():
    """
    DESCRIPTION:
        Prints the available classes for the ModelOps SDK.

    PARAMETERS:
        None

    RETURNS:
        None

    RAISES:
        None

    EXAMPLES:
        >>> blueprint()
        ----------------------------------------------------------------
        Available classes for ModelOps SDK:
            * teradataml.sdk.modelops.ClassName1
            * teradataml.sdk.modelops.ClassName2
        ----------------------------------------------------------------
    """
    _json_parser._print_classes(__current_module, SdkNames.MODELOPS.value)
