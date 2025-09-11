def PolynomialFeaturesFit(data=None, target_columns=None, include_bias=True, interaction_only=False, degree=2,
                          **generic_arguments):
    """
    DESCRIPTION:
        PolynomialFeaturesFit() function stores all the specified values in the argument in a DataFrame format.
        All polynomial combinations of the features with degrees less than or equal to the specified degree are
        generated. For example, for a two-dimensional input sample [x, y], the degree-2 polynomial features are
        [x, y, x-squared, xy, y-squared, 1].


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" for which polynomial
            features needs to be generated.
            Types: str OR list of Strings (str)

        include_bias:
            Optional Argument.
            Specifies whether to include bias column in the output or not.
            A bias column acts as an intercept term in a linear model.
            Default Value: True
            Types: bool

        interaction_only:
            Optional Argument.
            Specifies whether to output polynomial combinations only for interaction features
            (features that are products of at most degree distinct input features).
            Default Value: False
            Types: bool

        degree:
            Optional Argument.
            Specifies the maximum degree of the input features to output polynomial combinations.
            Permitted Values: 1, 2, 3
            Default Value: 2
            Types: int

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
        Instance of PolynomialFeaturesFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as PolynomialFeaturesFitObj.<attribute_name>.
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
        load_example_data("teradataml", ["numerics"])

        # Create teradataml DataFrame object.
        numerics = DataFrame.from_table("numerics")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Create fit object to create polynomial features for columns
        #            "integer_col" and "smallint_col".
        fit_obj = PolynomialFeaturesFit(data=numerics,
                                        target_columns=["integer_col", "smallint_col"],
                                        degree=2)

        # Print the result DataFrame.
        print(fit_obj.output)
        print(fit_obj.output_data)
    """