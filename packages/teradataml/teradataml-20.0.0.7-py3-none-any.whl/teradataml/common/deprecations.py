import warnings
from functools import wraps


def package_deprecation(version, replacement=None, type="class"):
    """
    Define a deprecation decorator.

    PARAMETERS:
        replacement:
            Optional Argument.
            `replacement` should refer to the new API to be used instead.

        type:
            Optional Argument.
             Specifies the type of entity being deprecated.
             For example,
                class or function

    EXAMPLES:
        @package_deprecation('16.20.x.y')
        def old_func(): ...
        @package_deprecation('16.20.x.y', 'teradataml.analytics.mle')
        def old_func(): ..."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            msg = "\nThe \"{}\" {} has moved to a new package in version {}."
            if replacement:
                msg += "\nImport from the teradataml package, or directly from the {} module." + \
                       "\nSee the teradataml {} User Guide for more information."
            warnings.warn(msg.format('.'.join([func.__module__, func.__name__]), type, version,
                                     replacement + '.' + func.__name__, version),
                          category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wraps(func)(wrapper)

    return decorator


def argument_deprecation(tdml_version, deprecated_arguments, behaviour=False, alternatives=None):
    """
    Decorator for deprecating of argument(s) for a function or class constructor.

    PARAMETERS:
        tdml_version:
            Required Argument.
            Specifies the teradataml version when the argument will be deprecated.
            Types: str

        deprecated_arguments:
            Required Argument.
            Specifies the name(s) of the argument(s) to be deprecated.
            Types: str OR list of Strings (str)

        behaviour:
            Optional Argument.
            Specifies whether behaviour of the argument is deprecated.
            Types: bool

        alternatives:
            Optional Argument.
            Specifies the name(s) of the argument(s) that are alternative
            to the deprecate arguments.
            Types: str OR list of Strings (str)


    EXAMPLES:
        # Example 1: Deprecate behavior of arguments "arg1" and "arg2".
        @argument_deprecation("17.20.00.02", ["arg1", "arg2"], True)
        def old_func(self): ...

        # Example 2: Deprecate argument completely.
        @argument_deprecation("17.20.00.02", "old_arg")
        def old_func(self): ...

        # Example 3: Deprecate arguments completely with alternative.
        @argument_deprecation("17.20.00.02", ["arg1", "arg2"], False, ["new_arg"])
        def old_func(self): ...

        # Example 4: Deprecate behavior of arguments "old_arg1" and "old_arg2" and provide alternatives.
        @argument_deprecation("17.20.00.02", ["arg1", "arg2"], True, ["alt_arg1", "alt_arg2"])
        def old_func(self): ...

    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check if deprecated arguments is a list, if not convert it to a list
            deprecated_args_list = deprecated_arguments if isinstance(deprecated_arguments, list) \
                else [deprecated_arguments]
            # Check list of deprecated arguments are used in the function call
            deprecated_arguments_used = [arg for arg in deprecated_args_list if arg in kwargs]
            if deprecated_arguments_used:
                msg = "\nThe argument(s) \"{}\" will be deprecated in {}."
                if behaviour:
                    msg = "\nBehaviour of the argument(s) \"{}\" will change in {}."
                msg = msg.format(deprecated_arguments_used, tdml_version)
                if alternatives is not None:
                    msg += "\nUse argument(s) \"{}\" instead.".format(alternatives)
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wraps(func)(wrapper)

    return decorator


def function_deprecation(tdml_version, behaviour=False, alternatives=None):
    """
    Decorator for deprecating a function.

    PARAMETERS:
        tdml_version:
            Required Argument.
            Specifies the teradataml version when the function will be deprecated.
            Types: str

        behaviour:
            Optional Argument.
            Specifies whether behaviour of the function is deprecated.
            Default value: False
            Types: bool


        alternatives:
            Optional Argument.
            Specifies the name of the function that is alternative
            to the deprecate function.
            Default value: None
            Types: str


    EXAMPLES:
        # Example 1: Deprecate behavior of function "old_func".
        @function_deprecation("17.20.00.03", True)
        def old_func(self): ...

        # Example 2: Deprecate function "old_func" completely.
        @function_deprecation("17.20.00.03")
        def old_func(self): ...

        # Example 3: Deprecate function "old_func" completely with alternative function "new_func".
        @function_deprecation("17.20.00.03", False, "new_func")
        def old_func(self): ...

        # Example 4: Deprecate behavior of function "old_func".
        @function_deprecation("17.20.00.03", True)
        def old_func(self): ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            msg = "\nThe function \"{}\" will be deprecated in {}."
            if behaviour:
                msg = "\nBehaviour of the function \"{}\" will change in {}."
            msg = msg.format(func.__name__, tdml_version)
            if alternatives is not None:
                msg += "\nInstead, Use following function \"{}\".".format(alternatives)
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wraps(func)(wrapper)

    return decorator