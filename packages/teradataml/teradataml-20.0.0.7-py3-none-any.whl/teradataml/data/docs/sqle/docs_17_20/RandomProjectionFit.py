def RandomProjectionFit(data=None, target_columns=None, num_components=None, seed=None,
                        epsilon=0.1, density=0.33333333, projection_method="GAUSSIAN",
                        output_featurenames_prefix="td_rpj_feature", **generic_arguments):
    """
    DESCRIPTION:
        The RandomProjectionFit() function returns a random projection matrix
        based on the specified arguments.

        The function also returns the required parameters for transforming the
        input data into lower-dimensional data. The RandomProjectionTransform()
        function uses the RandomProjectionFit() output to reduce the
        dimensionality of the input data.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the columns/features for dimensionality reduction.
            Types: str OR list of Strings (str)

        num_components:
            Required Argument.
            Specifies the target dimension(number of features) into which data
            points from the original dimension will be projected.
            The "num_components" value cannot be greater than the original
            dimension (number of features) and must satisfy the Johnson-Lindenstrauss
            Lemma result. The minimum value allowed for the "num_components" argument
            is calculated using the RandomProjectionMinComponents() function.
            Types: int

        seed:
            Optional Argument.
            Specifies the random seed the function uses for repeatable results.
            The algorithm uses the seed to generate a random projection matrix.
            The seed must be a non-negative integer value.
            Default Value: The Random Seed value is used for generating a random
            projection matrix, and hence the output is non-deterministic.
            Types: int

        epsilon:
            Optional Argument.
            Specifies a value to control distortion introduced while projecting
            the data to a lower dimension. The amount of distortion increases
            if you increase the value.
            Accepts value between 0 and 1.
            Default Value: 0.1
            Types: float OR int

        density:
            Optional Argument.
            Specifies the approximate ratio of non-zero elements in the random
            projection matrix when SPARSE is used as the "projection_method".
            Permitted Values: (0,1]
            Default Value: 0.33333333
            Types: float OR int

        projection_method:
            Optional Argument.
            Specifies the method name for generating the random projection matrix.
            Default Value: "GAUSSIAN"
            Permitted Values: GAUSSIAN, SPARSE
            Types: str

        output_featurenames_prefix:
            Optional Argument.
            Specifies the prefix for the output column names.
            Default Value: "td_rpj_feature"
            Types: str

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept. Below
            are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the
                    function in a table or not. When set to True,
                    results are persisted in a table; otherwise,
                    results are garbage collected at the end of the
                    session.
                    Default Value: False
                    Types: bool

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the
                    function in a volatile table or not. When set to
                    True, results are stored in a volatile table,
                    otherwise not.
                    Default Value: False
                    Types: bool

            Function allows the user to partition, hash, order or local
            order the input data. These generic arguments are available
            for each argument that accepts teradataml DataFrame as
            input and can be accessed as:
                * "<input_data_arg_name>_partition_column" accepts str or
                  list of str (Strings)
                * "<input_data_arg_name>_hash_column" accepts str or list
                  of str (Strings)
                * "<input_data_arg_name>_order_column" accepts str or list
                  of str (Strings)
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if
                the underlying SQL Engine function supports, else an
                exception is raised.

    RETURNS:
        Instance of RandomProjectionFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as RandomProjectionFitObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
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
        load_example_data("teradataml", ["stock_movement"])

        # Create teradataml DataFrame objects.
        stock_movement = DataFrame.from_table("stock_movement")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1 : Get random projection matrix for
        #             stock_movement DataFrame.
        RandomProjectionFit_out = RandomProjectionFit(data = stock_movement,
                                                      target_columns = "1:",
                                                      epsilon = 0.9,
                                                      num_components = 343
                                                      )

        # Print the result DataFrames.
        print(RandomProjectionFit_out.result)
        print(RandomProjectionFit_out.output_data)

    """