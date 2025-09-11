def ZTest(data=None, alpha=0.5, first_sample_column=None, second_sample_column=None,
          alternate_hypothesis="two-tailed", first_sample_variance=None,
          second_sample_variance=None, mean_under_h0=None,
          **generic_arguments):
    
    """
    DESCRIPTION:
        ZTest() function tests the equality of two means under the assumption that the
        population variances are known. For large samples, sample variances
        approximate population variances, so it uses sample variances
        instead of population variances in the test statistic.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        alpha:
            Optional Argument.
            Specifies the value of alpha in hypothesis test function.
            Default Value: 0.5
            Types: float

        first_sample_column:
            Required Argument.
            Specifies the first sample column in z test.
            Types: str

        second_sample_column:
            Optional Argument.
            Specifies the second sample column in z test.
            Types: str

        alternate_hypothesis:
            Optional Argument.
            Specifies the alternate hypothesis.
            Permitted Values:
                * lower-tailed - Alternate hypothesis (H 1): μ < μ0.
                * upper-tailed - Alternate hypothesis (H 1): μ > μ0.
                * two-tailed - Rejection region is on two sides of sampling distribution
                               of test statistic.
                               Two-tailed test considers both lower and upper tails of
                               distribution of test statistic.
                               Alternate hypothesis (H 1): μ ≠ μ0
            Default Value: "two-tailed"
            Types: str

        first_sample_variance:
            Required Argument.
            Specifies the first sample variance.
            Types: float

        second_sample_variance:
            Optional Argument.
            Specifies the second sample variance.
            Types: float

        mean_under_h0:
            Optional Argument.
            Specifies the mean under the null hypothesis.
            Types: float

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in table or not.
                    When set to True, results are persisted in table; otherwise, results
                    are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in volatile table or not.
                    When set to True, results are stored in volatile table, otherwise not.
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
                These generic arguments are supported by teradataml if the underlying SQLE Engine
                function supports, else an exception is raised.

    RETURNS:
        Instance of ZTest.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ZTestObj.<attribute_name>.
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
        load_example_data("teradataml", ["titanic"])

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Perform ZTest analysis on input data column that
        #            contains data for the first sample population and
        #            variance of the first sample population.
        obj = ZTest(data=titanic_data,
                    first_sample_column='age',
                    first_sample_variance=5)

        # Print the result DataFrame.
        print(obj.result)

        # Example 2: Perform ZTest analysis on input data column that
        #            contains data for the first and second sample
        #            population and variance of the first and second sample
        #            population by specifying data_partition_column as ANY.

        # To partition data using ANY, one must import 'PartitionKind' module first,
        # then pass PartitionKind.ANY as input to "data_partition_column" argument.
        from teradataml import PartitionKind
        obj = ZTest(data=titanic_data,
                    alpha=0.5,
                    data_partition_column=PartitionKind.ANY,
                    data_order_column='pclass',
                    first_sample_column='age',
                    second_sample_column='parch',
                    alternate_hypothesis='two-tailed',
                    first_sample_variance=5,
                    second_sample_variance=8,
                    mean_under_h0=0)

        # Print the result DataFrame.
        print(obj.result)

    """
