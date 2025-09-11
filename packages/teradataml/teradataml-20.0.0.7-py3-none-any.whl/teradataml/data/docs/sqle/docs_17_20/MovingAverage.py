def MovingAverage(data=None, target_columns=None, alpha=0.1, start_rows=2, window_size=10,
                  include_first=False, mavgtype="C", **generic_arguments):
    """
    DESCRIPTION:
        MovingAverage() function computes average values in a series, using the specified moving average type.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the name of the teradataml DataFrame that contains the
            columns.
            Types: teradataml DataFrame

        target_columns:
            Optional Argument.
            Specifies the input column names for which the moving average is to
            be computed. If you omit this argument, then the function copies
            every input column to the output teradataml DataFrame but does not
            compute moving average.
            Types: str OR list of Strings (str)

        alpha:
            Optional Argument.
            Specifies the damping factor, a value in the range [0, 1], which
            represents a percentage in the range [0, 100]. For example, if alpha
            is 0.2, then the damping factor is 20%. A higher alpha discounts
            older observations faster.
            Default Value: 0.1
            Types: float

        start_rows:
            Optional Argument.
            Specifies the number of rows at the beginning of the time series that
            the function "skips" before it begins the calculation of the
            exponential moving average. The function uses the arithmetic average
            of these rows as the initial value of the exponential moving average.
            The value n must be an integer.
            Default Value: 2
            Types: int

        window_size:
            Optional Argument.
            Specifies the number of previous values to include in the computation
            of the simple moving average.
            Default Value: 10
            Types: int

        include_first:
            Optional Argument.
            Specifies whether the first "start_rows" rows should be included in the
            output or not.
            Default Value: False
            Types: bool

        mavgtype:
            Optional Argument.
            Specifies the moving average type that needs to be used for computing
            moving averages of TargetColumns.
            Default Value: "C"
            Permitted Values: C, S, M, W, E, T
            Types: str

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
        Instance of MovingAverage.
        Output teradataml DataFrames can be accessed using attribute
        references, such as MovingAverageObj.<attribute_name>.
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
        load_example_data("movavg", ["ibm_stock"])

        # Create teradataml DataFrame object.
        ibm_stock = DataFrame.from_table("ibm_stock")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Compute the average values in a series, using the 'C' moving average type.
        obj = MovingAverage(data=ibm_stock,
                            data_partition_column='stockprice',
                            data_order_column='stockprice',
                            include_first=False,
                            alpha=0.1,
                            start_rows=2,
                            window_size=10,
                            mavgtype='C')

        # Print the result DataFrame.
        print(obj.result)

    """
