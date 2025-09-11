def SimpleImputeFit(data=None, stats_columns=None, literals_columns=None, partition_column=None,
                    stats=None, literals=None, **generic_arguments):
    """
    DESCRIPTION:
        SimpleImputeFit() function outputs values to substitute for missing
        values in the input data. The output values are input to SimpleImputeTransform()
        function, which makes the substitutions.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        stats_columns:
            Optional Argument.
            Specifies the name(s) of the column(s) in "data" for which to calculate
            the statistics.
            Types: str OR list of Strings (str)

        literals_columns:
            Optional Argument.
            Specifies the name(s) of the column(s) in "data" for which to impute literals.
            Types: str OR list of Strings (str)

        partition_column:
            Optional Argument.
            Specifies the name(s) of the column(s) in "data" to partition on.
            Types: str OR list of Strings (str)

        stats:
            Optional Argument.
            Specifies the stats to compute on input teradataml DataFrame columns.
            Permitted Values: MIN, MAX, MEAN, MEDIAN, MODE
            Types: str OR list of Strings (str)

        literals:
            Optional Argument.
            Specifies the literal value to impute on input teradataml DataFrame
            columns.
            Types: str OR list of Strings (str)

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
        Instance of SimpleImputeFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as SimpleImputeFitObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. output
            2. output_data


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
        load_example_data("teradataml", ["titanic"])

        # Create teradataml DataFrame.
        titanic = DataFrame.from_table("titanic")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Create stats for "fare" column and impute value "2"
        #            in "pclass" column.
        fit_obj = SimpleImputeFit(data=titanic,
                                  stats_columns="fare",
                                  literals_columns="pclass",
                                  partition_column="sex",
                                  stats="median",
                                  literals="2")

        # Print the result DataFrame.
        print(fit_obj.output)
        print(fit_obj.output_data)
    """
