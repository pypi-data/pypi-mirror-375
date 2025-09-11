from functools import wraps
from teradatasqlalchemy.telemetry.queryband import QueryBand, collect_queryband as tdsqlalchemy_collect_queryband


# Create a global variable to manage querybands for teradataml package.
global session_queryband
session_queryband = QueryBand()


def collect_queryband(*qb_deco_pos_args, **qb_deco_kwargs):
    """
    DESCRIPTION:
        Decorator for calling collect_queryband decorator in telemetry utility
        in teradatasqlalchemy using session_queryband object and other positional
        and keyword arguments expected by collect_queryband.

    PARAMETERS:
        qb_deco_pos_args:
            Optional Argument.
            Specifies the positional arguments accepted by collect_queryband
            decorator in telemetry utility in teradatasqlalchemy.

        qb_deco_kwargs:
            Optional Argument.
            Specifies the keyword arguments accepted by collect_queryband
            decorator in telemetry utility in teradatasqlalchemy.

    EXAMPLES:
        >>> from teradataml.telemetry_utils.queryband import collect_queryband
        # Example 1: Collect queryband for a standalone function.
        @collect_queryband(queryband="CreateContext")
        def create_context(host = None, username ...): ...

        # Example 2: Collect queryband for a class method and use
        #            class attribute to retrive queryband string.
        @collect_queryband(attr="func_name")
        def _execute_query(self, persist=False, volatile=False):...

        # Example 3: Collect queryband for a class method and use
        #            method of same class to retrive queryband string.
        @collect_queryband(method="get_class_specific_queryband")
        def _execute_query(self, persist=False, volatile=False):...
    """
    def outer_wrapper(func):
        @wraps(func)
        def inner_wrapper(*func_args, **func_kwargs):
            # Pass the required argument 'session_queryband' along with other
            # expected arguments to collect_queryband() decorator which is
            # imported as tdsqlalchemy_collect_queryband.
            return tdsqlalchemy_collect_queryband(session_queryband, *qb_deco_pos_args, **qb_deco_kwargs)(func)(*func_args, **func_kwargs)
        return inner_wrapper
    return outer_wrapper
