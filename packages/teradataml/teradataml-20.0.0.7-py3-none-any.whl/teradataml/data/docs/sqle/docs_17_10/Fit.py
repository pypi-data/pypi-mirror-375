def Fit(data=None, object=None, **generic_arguments):
    """
    DESCRIPTION:
        The Fit() function determines whether specified numeric transformations can be
        applied to specified "target_columns" and outputs a DataFrame to use as input
        "data" for Transform() function, which does the transformations.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        object:
            Required Argument.
            Specifies the transformation teradataml DataFrame that contains transformation
            information for the columns in "data".
            Types: teradataml DataFrame

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
        Instance of Fit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as FitObj.<attribute_name>.
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
        load_example_data("teradataml", ["iris_input", "transformation_table"])

        # Create teradataml DataFrame objects.
        iris_input = DataFrame.from_table("iris_input")
        transformation_df = DataFrame.from_table("transformation_table")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Run Fit() with all arguments.
        fit_df = Fit(data=iris_input,
                     object=transformation_df,
                     object_order_column='TargetColumn'
                    )

        # Print the result DataFrame.
        print(fit_df)

    """