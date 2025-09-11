"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements the utilities which are required for bulk exposure.
"""
from teradataml.common.constants import TDMLFrameworkKeywords

def _validate_unimplemented_function(func_name, func_params, *args, **kwargs):
    """
    DESCRIPTION:
        Function to validate the signature of an unimplemented Function using
        Parameter Structure. If the signature is expected, it then returns all
        the parameters in keyword arguments.

    PARAMETERS:
        func_name:
            Required Argument.
            Specifies the name of the function.
            Types: str

        func_params:
            Required Argument.
            Specifies the expected parameters of the function.
            Types: list of Dictionaries (dict)

        args:
            Optional Argument.
            Specifies the positional arguments to be passed to the
            function.
            Types: Tuple

        kwargs:
            Optional Argument.
            Specifies the keyword arguments to be passed to the
            function.
            Types: Dictionary

    RAISES:
        TypeError.

    RETURNS:
        dict, with keys as argument name and value as value passed to it.

    EXAMPLES:
        # validate the arguments for function: msum.
        # msum accepts two parameters, width & sort_columns.
        # >>> from teradataml.dataframe.sql_function_parameters import SQL_AGGREGATE_FUNCTION_ADDITIONAL_PARAMETERS
        # >>> msum_expected_params = SQL_AGGREGATE_FUNCTION_ADDITIONAL_PARAMETERS["MSUM"]

        # Example 1: Passing all arguments as positional arguments.
        >>> _validate_unimplemented_function("msum", msum_expected_params, 1, 2)
        {'width': 1, 'sort_columns': 2}

        # Example 2: Passing arguments as mix of positional & keyword arguments.
        >>> _validate_unimplemented_function("msum", msum_expected_params, 1, sort_columns=lambda x:x)
        {'width': 1, 'sort_columns': <function <lambda> at 0x00000184871E06A8>}

        # Example 3: Passing additional positional argument.
        >>> _validate_unimplemented_function("msum", msum_expected_params, 1, 2, 3)
        TypeError: msum() takes 2 positional arguments but 3 were given

        # Example 4: Passing unexpected keyword argument.
        >>> _validate_unimplemented_function("msum", msum_expected_params, 1, p="q")
        TypeError: msum() got an unexpected keyword argument 'p'

    """
    expression_params = []
    return_values = []

    # Converting args to kwargs is difficult as before convert,
    # validation should be performed whether all the parameter's are expected
    # or not. And, if all are expected, then iterate through every parameter
    # in args and map it to keyword argument carefully. However, this
    # approach seems to be difficult as one has to identify the keyword argument
    # carefully. So, to avoid this, creating a dummy function which has signature
    # similar to expected function and returns a Dictionary with key's as
    # expected parameter name and value as value passed in either args or
    # kwargs.
    for param in func_params:
        if "default_value" in param:
            expression = "{}={}".format(param["arg_name"],
                                        param["default_value"])
        else:
            expression = param["arg_name"]
        return_values.append('"{0}": {0}'.format(param["arg_name"]))
        expression_params.append(expression)

    return_statement = "return {{{}}}".format(", ".join(return_values))
    function_signature = ", ".join(expression_params)

    # Creating function expression.
    function_expression = """def {}({}): {}""".format(func_name,
                                                      function_signature,
                                                      return_statement)
    # Creating function object from the string in locals.
    global_scope = {}
    namespace = {}
    exec(function_expression, global_scope, namespace)

    # kwargs may contain other properties too. So, before we call the function,
    # copying kwargs to another variable and remove additional properties.
    kw = {}
    for param in kwargs:
        if not param in TDMLFrameworkKeywords.AGGREGATE_FUNCTION_DEFAULT_ARGUMENTS.value:
            kw[param] = kwargs[param]

    return namespace[func_name](*args, **kw)

