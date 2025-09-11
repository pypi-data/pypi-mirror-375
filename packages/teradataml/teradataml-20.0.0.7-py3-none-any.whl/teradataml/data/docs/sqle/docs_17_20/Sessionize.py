def Sessionize(data=None, time_column=None, time_out=None, click_lag=None,
               emit_null=False, **generic_arguments):
    """
    DESCRIPTION:
        Sessionize() function maps each click in a session to a unique session identifier.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        time_column:
            Required Argument.
            Specifies the name of the input column that contains the click
            times.
            Note: The "time_column" must also be an "order_column".
            Types: str

        time_out:
            Required Argument.
            Specifies the number of seconds at which the session times out. If
            "time_out" seconds elapse after a click, then the next click
            starts a new session.
            Types: float

        click_lag:
            Optional Argument.
            Specifies the minimum number of seconds between clicks for the
            session user to be considered human. If clicks are more frequent,
            indicating that the user is a bot, the function ignores the session.
            The "click_lag" must be less than "time_out".
            Types: float

        emit_null:
            Optional Argument.
            Specifies whether to output rows that have NULL values in their
            session id and rapid fire columns, even if their timestamp_column has
            a NULL value.
            Default Value: False
            Types: bool

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or not.
                    When set to True, results are persisted in a table; otherwise, results
                    are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table or not.
                    When set to True, results are stored in a volatile table, otherwise not.
                    Default Value: False
                    Types: boolean

            Function allows the user to partition, hash, order or local order the input
            data. These generic arguments are available for each argument that accepts
            teradataml DataFrame as input and can be accessed as:
                * "<input_data_arg_name>_partition_column" accepts str or list of str (Strings)
                * "<input_data_arg_name>_hash_column" accepts str or list of str (Strings)
                * "<input_data_arg_name>_order_column" accepts str or list of str (Strings)
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if the underlying SQL Engine
                function supports, else an exception is raised.

    RETURNS:
        Instance of Sessionize.
        Output teradataml DataFrames can be accessed using attribute
        references, such as SessionizeObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        # Load the example data.
        load_example_data("sessionize", ["sessionize_table"])

        # Create teradataml DataFrame object.
        sessionize_data = DataFrame.from_table("sessionize_table")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Mapping each click in a session to a unique session identifier.
        #            by partition column 'partition_id' and order column 'clicktime'.
        obj = teradataml.Sessionize(data=sessionize_data,
                                    data_partition_column='partition_id',
                                    data_order_column='clicktime',
                                    time_column='clicktime',
                                    time_out=60.0,
                                    click_lag=0.2)

        # Print the result DataFrame.
        print(obj.result)

    """