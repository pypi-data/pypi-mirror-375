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
# This file contains the constants needed for SDK.
# 
# ################################################################################################

import os
from enum import Enum

from teradataml import _TDML_DIRECTORY


class SdkPackagePaths(Enum):
    """
    This class contains enums holding paths to json file for each SDK.
    Note:
        Developers should add paths to json files and use it in corresponding __init__.py file/
    """
    MODELOPS = os.path.join(_TDML_DIRECTORY, "data", "sdk", "modelops", "modelops_spec.json")

class SdkNames(Enum):
    """
    This class contains enums holding names of SDKs.
    Note:
        Developers should add names to SDKs and use it in corresponding __init__.py file/
    """
    MODELOPS = "ModelOps"

_OPENAPI_TO_PYTHON_PARAM_TYPE_MAPPER = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None)
}

_REQUEST_FUNCTION_MAPPER = {
    'get': 'get_request',
    'post': 'post_request',
    'put': 'put_request',
    'patch': 'patch_request',
    'delete': 'delete_request'}

class ParameterTypes(Enum):
    """
    This class contains enum holding parameter types.
    """
    PARAM = "PARAM"
    BODY = "BODY"
    PROJECTION = "PROJECTION"
    RESPONSE = "RESPONSE"