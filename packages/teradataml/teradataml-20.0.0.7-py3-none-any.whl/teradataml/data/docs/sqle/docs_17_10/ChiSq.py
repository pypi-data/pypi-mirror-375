def ChiSq(data=None, alpha=0.05, **generic_arguments):
    """
    DESCRIPTION:
        The ChiSq() function performs Pearson's chi-squared (χ2) test for independence,
        which determines if there is a statistically significant difference between
        the expected and observed frequencies in one or more categories of a
        contingency table (also called a cross tabulation).


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        alpha:
            Optional Argument.
            Specifies the probability below which the null hypothesis is rejected.
            "alpha" must be a numeric value in the range [0, 1].
            Default Value: 0.05
            Types: float

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in table or
                    not. When set to True, results are persisted in table; otherwise,
                    results are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in volatile table
                    or not. When set to True, results are stored in volatile table,
                    otherwise not.
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
                    SQLE Engine function supports, else an exception is raised.

    RETURNS:
        Instance of ChiSq.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ChiSq.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. output_data
            2. output

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
        load_example_data("teradataml", "chi_sq")

        # Create teradataml DataFrame object.
        chi_sq_data = DataFrame.from_table("chi_sq")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example: Run ChiSq() with all arguments.
        obj = ChiSq(data=chi_sq_data,
                    alpha=0.5)

        # Print the output DataFrame and expected values DataFrame.
        print(obj.output)
        print(obj.output_data)

    """
