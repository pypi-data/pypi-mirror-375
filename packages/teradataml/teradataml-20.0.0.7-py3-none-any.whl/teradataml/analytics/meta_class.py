# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2023 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: shravan.jat@teradata.com
Secondary Owner: pradeep.garre@teradata.com

teradataml.analytics.meta_class
----------
This file implements the class _FunctionMetaclass, which is metaclass for SQLE, UAF, BYOM and NOS function,
and class _AnalyticFunction, which is base class for SQLE, UAF, BYOM and NOS function to have more control
and flexibility over this functions.
"""
from teradataml.context.context import get_context

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.options.configure import configure
class _FunctionMetaclass(type):
    """
    Metaclass for BYOM, SQLE, UAF and NOS functions.
    """
    def __str__(self):
        """
        Returns the string representation of Analytic Function.
        """
        return "{}({})".format(self.__name__,
                               "<Get connection to Vantage to view signature>" if not get_context() else self._signature)

    def __repr__(self):
        """
        Returns the string representation of Analytic Function.
        """
        return "{}({})".format(self.__name__,
                               "<Get connection to Vantage to view signature>" if not get_context() else self._signature)

    def __getattribute__(self, name):
        """
        DESCRIPTION:
            Returns an attribute of Analytic Function.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the attribute.
                Type: str

        RETURNS:
             When create_context() is created Return the value of the named attribute,
             Otherwise not.
        """
        if name == '__doc__' and not get_context():
            return "To view documentation connect to Vantage using create_context()."
        else:
            return super().__getattribute__(name)

class _AnalyticFunction(metaclass=_FunctionMetaclass):
    """
    Base class for BYOM, SQLE, UAF and NOS functions.
    """
    __doc__ = "To view documentation connect to Vantage using create_context()."
    _signature = None

    def __getattr__(self, item):
        """
        DESCRIPTION:
            Returns an attribute of the BYOM, SQLE, UAF or NOS function.

        PARAMETERS:
            item:
                Required Argument.
                Specifies the name of the attribute.
                Type: str

        RETURNS:
            Return the value of the named attribute of object (if found).

        RAISES:
            Attribute Error when the named attribute is not found
        """
        if getattr(self.obj, item):
            return getattr(self.obj, item)

        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, item))

    def __repr__(self):
        return self.obj.__repr__()

    def __str__(self):
        return self.obj.__repr__()

    def show_query(self):
        """
        Description:
            Function to return the underlying SQL query.

        PARAMETERS:
            None.

        RETURNS:
            Return underlying SQL query

        RAISES:
            None.

        EXAMPLES:
            sqlefunction.show_query(),
            uaffunction.show_query(),
            byomfunction.show_query(),
            nosfunction.show_query()
        """
        return self.obj.show_query()

    def get_build_time(self):
        """
        Description:
            Function to return the build time of the algorithm in seconds.

        PARAMETERS:
            None.

        RETURNS:
            Return build time of algorithm.

        RAISES:
            None.

        EXAMPLES:
            sqlefunction.get_build_time(),
            uaffunction.get_build_time(),
            byomfunction.get_build_time(),
            nosfunction.get_build_time()
        """
        return self.obj.get_build_time()

def _common_init(self, function_type, **kwargs):
    """
    DESCRIPTION:
        Function execute the sqle, byom, uaf or nos functions and store in
        self.obj instance variable.

    PARAMETERS:
        function_type:
            Required Argument.
                Specifies the type of function used.
                Permitted Values:
                    * sqle
                    * uaf
                    * byom
                    * nos
                Type: str
        kwargs:
            Required Argument.
            Specifies the parameters passed to a dynamic class for sqle, byom, uaf, nos.
            Type: dict

    RETURNS:
        None

    RAISES:
        TeradataMLException when create_context() not established or
        when function signature not found.
    """
    if not get_context():
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                       self.__class__.__name__,
                                                       'Connect to Vantage'),
                                  MessageCodes.FUNC_EXECUTION_FAILED)

    if not self._signature:
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNCTION_NOT_SUPPORTED,
                                                       'current Vantage version({})'.format(configure.database_version)
                                                       ),
                                  MessageCodes.FUNCTION_NOT_SUPPORTED)

    # There may be cases where some of the arguments are marked as default
    # in teradataml but required for Vantage. For such cases, look at metadata
    # and populate the kwargs with default value.
    for _function_arg, _function_arg_vale in self._func_params.items():
        if _function_arg not in kwargs:
            kwargs[_function_arg] = _function_arg_vale

    if function_type == 'sqle':
        from teradataml.analytics.analytic_function_executor import _SQLEFunctionExecutor
        self.obj = _SQLEFunctionExecutor(self.__class__.__name__)._execute_function(**kwargs)
    elif function_type == 'uaf':
        from teradataml.analytics.analytic_function_executor import _UAFFunctionExecutor
        self.obj = _UAFFunctionExecutor(self.__class__.__name__)._execute_function(**kwargs)
    elif function_type == 'byom':
        from teradataml.analytics.analytic_function_executor import _BYOMFunctionExecutor
        self.obj = _BYOMFunctionExecutor(self.__class__.__name__)._execute_function(**kwargs)
    elif function_type == 'stored_procedure':
        from teradataml.analytics.analytic_function_executor import _StoredProcedureExecutor
        self.obj = _StoredProcedureExecutor(self.__class__.__name__)._execute_function(**kwargs)
    else:
        from teradataml.analytics.analytic_function_executor import _TableOperatorExecutor
        self.obj = _TableOperatorExecutor(self.__class__.__name__)._execute_function(**kwargs)

def _common_dir(self):
    """
    DESCRIPTION:
        Function returns the attributes and/or names of the methods of the
        Analytic function.

    PARAMETERS:
        None

    RETURNS:
        list

    RAISES:
        None

    Examples:
        # Load the data.
        titanic_data = DataFrame.from_table("titanic")
        bin_fit_ip = DataFrame.from_table("bin_fit_ip")

        # Run the function.
        bin_code_1 = BincodeFit(data=titanic_data,
                                fit_data=bin_fit_ip,
                                fit_data_order_column = ['minVal', 'maxVal'],
                                target_columns='age',
                                minvalue_column='minVal',
                                maxvalue_column='maxVal',
                                label_column='label',
                                method_type='Variable-Width',
                                label_prefix='label_prefix'
                                )
        # Run dir on the function.
        dir(bin_code_1)
    """
    return [attr for attr in super(self.__class__, self).__dir__() if attr != 'obj']