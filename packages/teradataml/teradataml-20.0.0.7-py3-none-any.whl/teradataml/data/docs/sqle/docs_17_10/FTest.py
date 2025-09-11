def FTest(data = None, alpha = None,
          first_sample_variance=None,
          first_sample_column=None,
          df1=None,
          second_sample_variance=None,
          second_sample_column=None,
          df2=2,
          alternate_hypothesis='two-tailed',
          **generic_arguments):
    """
    DESCRIPTION:
        The FTest() function performs an F-test, for which the test statistic follows an
        F-distribution under the Null hypothesis.
        Function compares the variances of two independent populations.
        If the variances are significantly different, the FTest() function rejects the
        Null hypothesis, indicating that the variances may not come from the same
        underlying population.
        Use the function to compare statistical models that have been fitted to a
        data set, to identify the model that best fits the population from which the data
        were sampled.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        alpha:
            Optional Argument.
            Specifies the probability of rejecting the null hypothesis when it is true
            (value below which null hypothesis is rejected).
            "alpha" must be a numeric value in the range [0, 1].
            Default Value: 0.05
            Types: float

        first_sample_column:
            Required if "first_sample_variance" is omitted, disallowed otherwise.
            Specifies the name of the input column that contains the data for the
            first sample population.
            Types: str

        first_sample_variance:
            Required if "first_sample_column" is omitted, disallowed otherwise.
            Specifies the variance of the first sample population.
            Types: float

        df1:
            Required if "first_sample_column" is omitted, disallowed otherwise.
            Specifies the degrees of freedom of the first sample.
            Types: integer

        second_sample_column:
            Required if "second_sample_variance" is omitted, disallowed otherwise.
            Specifies the name of the input column that contains the data for the
            second sample population.
            Types: str

        second_sample_variance:
            Required if "second_sample_column" is omitted, disallowed otherwise.
            Specifies the variance of the second sample population.
            Types: float

        df2:
            Required if "second_sample_column" is omitted, disallowed otherwise.
            Specifies the degrees of freedom of the second sample.
            Types: integer

        alternate_hypothesis:
            Optional Argument.
            Specifies the alternative hypothesis.
            Permitted Values:
                * lower-tailed - Alternate hypothesis (H 1): μ < μ0.
                * upper-tailed - Alternate hypothesis (H 1): μ > μ0.
                * two-tailed - Rejection region is on two sides of sampling distribution
                               of test statistic.
                               Two-tailed test considers both lower and upper tails of
                               distribution of test statistic.
                               Alternate hypothesis (H 1): μ ≠ μ0
            Default Value: two-tailed
            Types: str

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
        Instance of FTest.
        Output teradataml DataFrames can be accessed using attribute
        references, such as FTestObj.<attribute_name>.
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
        load_example_data("teradataml", "titanic")

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Run FTest() with first_sample_variance, second_sample_variance,
        #            df1 and df2.
        obj = FTest(data=titanic_data, alpha=0.5,
                    second_sample_column="parch",
                    alternate_hypothesis="two-tailed",
                    first_sample_variance=5,
                    second_sample_variance=8,
                    df1=1, df2=2
                    )

        # Print the result DataFrame.
        print(obj.result)

        # Example 2: Run FTest() with only required arguments.
        obj = FTest(data=titanic_data,
                    second_sample_column="parch",
                    second_sample_variance=8,
                    df2=2
                    )

        # Print the result DataFrame.
        print(obj.result)
    """