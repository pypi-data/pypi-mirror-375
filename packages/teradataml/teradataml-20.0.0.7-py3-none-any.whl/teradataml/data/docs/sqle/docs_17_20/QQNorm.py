def QQNorm(data=None, target_columns=None, rank_columns=None, output_columns=None, accumulate=None,
           **generic_arguments):
    """
    DESCRIPTION:
        Function determines if values in input data columns follow normal distribution or not. 
        It returns the quantiles of the column values and corresponding theoretical quantile
        values from a normal distribution. If the column values are normally distributed, then
        the quantiles of column values and normal quantile values appear in a straight line
        when plotted on a 2D graph.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" to generate standard normal quantiles.
            Types: str OR list of Strings (str)

        rank_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" containing rank values for "target_columns".
            Types: str OR list of Strings (str)

        output_columns:
            Optional Argument.
            Specifies the name(s) of the output column(s) to be generated that contain the theoretical
            quantiles of the target column(s). If not specified, name(s) will be generated as
            "<column name in target_columns>_theoretical_quantiles".
            Types: str OR list of strs

        accumulate:
            Optional Argument.
            Specifies the names of input teradataml DataFrame columns to copy to the output.
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
                These generic arguments are supported by teradataml if the underlying
                SQL Engine function supports, else an exception is raised.

    RETURNS:
        Instance of QQNorm.
        Output teradataml DataFrames can be accessed using attribute
        references, such as QQNormObj.<attribute_name>.
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

        # Load the sample rank_df DataFrame.
        load_example_data("teradataml", ["rank_table"])

        # Create teradataml DataFrame object.
        rank_df = DataFrame.from_table("rank_table")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Get theoretical quantile values for 'age' and 'fare'.
        obj = QQNorm(data=rank_df,
                     target_columns=["age", "fare"],
                     rank_columns=["rank_age", "rank_fare"])

        # Print the result DataFrame.
        print(obj.result)
    """