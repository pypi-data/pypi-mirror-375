# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2023 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: shravan.jat@teradata.com
Secondary Owner: pradeep.garre@teradata.com

teradataml.analytics.__init__
----------
This file implements the  function _process_analytic_functions, Internal function to generate the analytic function
based on the json data and attach it to teradataml.
and function _get_executor_class_name, Internal function to get executor class name for function_type provided.
"""
from .byom import *
from .sqle import *
from .table_operator import *
from .uaf import *
from .valib import valib
from .Transformations import Binning, Derive, OneHotEncoder, FillNa, LabelEncoder, MinMaxScalar, \
    Retain, Sigmoid, ZScore
from teradataml.analytics.json_parser.utils import _get_json_data_from_tdml_repo, _process_paired_functions
from teradataml.analytics.analytic_function_executor import _SQLEFunctionExecutor, _TableOperatorExecutor,\
    _UAFFunctionExecutor, _BYOMFunctionExecutor, _StoredProcedureExecutor
from teradataml.common.constants import TeradataAnalyticFunctionTypes


def _process_analytic_functions():
    """
    DESCRIPTION:
        Internal function to generate the analytic function based on the json data
        and attach it to teradataml.

    RETURNS:
        None

    RAISES:
        TeradataMlException.

    EXAMPLES:
        _process_analytic_functions()
    """
    for metadata in _get_json_data_from_tdml_repo():
        import teradataml
        getattr(teradataml, metadata.func_name).__init__.__doc__ = metadata.get_doc_string()
        getattr(teradataml, metadata.func_name).__doc__ = metadata.get_doc_string()
        getattr(teradataml, metadata.func_name)._signature = metadata.get_function_parameters_string()
        getattr(teradataml, metadata.func_name)._func_params = metadata.function_params

    _process_paired_functions()


def _get_executor_class_name(function_type):
    """
    DESCRIPTION:
        Internal function to get executor class name for function_type provided.
    
    PARAMETERS:
        function_type:
            Required Argument.
            Specifies the type of function.
            Permitted Values: ['FASTPATH', 'TABLE_OPERATOR']
            Types: str

    RETURNS:
        str

    RAISES:
        None.

    EXAMPLES:
        _get_executor_class_name("table_operator")
    """
    func_type_to_executor = {
        TeradataAnalyticFunctionTypes.SQLE.value: _SQLEFunctionExecutor,
        TeradataAnalyticFunctionTypes.TABLEOPERATOR.value: _TableOperatorExecutor,
        TeradataAnalyticFunctionTypes.UAF.value: _UAFFunctionExecutor,
        TeradataAnalyticFunctionTypes.BYOM.value: _BYOMFunctionExecutor,
        TeradataAnalyticFunctionTypes.STORED_PROCEDURE.value: _StoredProcedureExecutor
    }
    return func_type_to_executor.get(function_type.upper(), _SQLEFunctionExecutor).__name__
