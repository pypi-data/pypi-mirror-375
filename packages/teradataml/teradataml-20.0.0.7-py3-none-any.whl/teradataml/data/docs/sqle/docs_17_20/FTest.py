def FTest(data = None, alpha = 0.05, first_sample_variance=None,
          first_sample_column=None, df1=None, second_sample_variance=None,
          second_sample_column=None, df2=2, alternate_hypothesis='two-tailed',
          sample_name_column=None, sample_value_column=None, first_sample_name=None,
          second_sample_name=None, **generic_arguments):
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
            Specifies the probability of rejecting the null 
            hypothesis when the null hypothesis is true.
            Note:
                * "alpha" must be a numeric value in the range [0, 1].
            Default Value: 0.05
            Types: float

        first_sample_column:
            Optional Argument.
            Specifies the first sample column in F-Test.
            Note:
                * This argument must be specified with "first_sample_variance" and "df1"
                  or allowed combination is "first_sample_column" with 
                  "second_sample_variance" and "df2".
                * This argument cannot be used in conjunction with "sample_name_column"
                  and "sample_value_column".
            Types: str

        first_sample_variance:
            Optional Argument.
            Specifies the first sample variance.
            Note:
                * This argument must be specified with "first_sample_column" and "df1"
                  or other allowed combination is "second_sample_column" with 
                  "first_sample_variance" and "df1".
            Types: float

        df1:
            Optional Argument.
            Specifies the degrees of freedom of the first sample.
            Note:
                * This argument must be specified with "first_sample_column" and 
                  "first_sample_variance".
            Types: integer

        second_sample_column:
            Optional Argument.
            Specifies the second sample column in F-Test.
            Note:
                * This argument must be specified with "second_sample_variance" and "df2"
                  or allowed combination is "second_sample_column" with "first_sample_variance" 
                  and "df1".
                * This argument cannot be used in conjunction with "sample_name_column"
                  and "sample_value_column".
            Types: str

        second_sample_variance:
            Optional Argument.
            Specifies the second sample variance.
            Note:
                * This argument must be specified with "second_sample_column" and "df2"
                  or allowed combination is "first_sample_column" with 
                  "second_sample_variance" and df2.
            Types: float

        df2:
            Optional Argument.
            Specifies the degree of freedom of the second sample.
            Note:
                * This argument must be specified with "second_sample_column" and 
                  "second_sample_variance".
            Types: integer

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
            Default Value: two-tailed
            Types: str

        sample_name_column:
            Optional Argument.
            Specifies the column name in "data" containing the names of the samples
            included in the F-Test.
            Types: str
        
        sample_value_column:
            Optional Argument.
            Specifies the column name in "data" containing the values for each sample member.
            Types: str

        first_sample_name:
            Optional Argument.
            Specifies the name of the first sample included in the F-Test.
            Types: str

        second_sample_name:
            Optional Argument.
            Specifies the name of the second sample included in the F-Test.
            Types: str

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or
                    not. When set to True, results are persisted in a table; otherwise,
                    results are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table
                    or not. When set to True, results are stored in a volatile table,
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
                SQL Engine function supports, else an exception is raised.

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
        load_example_data("ztest", 'insect2Cols')

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")
        insect_gp = DataFrame.from_table("insect2Cols")

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

        # Example 3: Run FTest() with sample_name_column, sample_value_column,
        #            first_sample_name and second_sample_name.
        obj = FTest(data=insect_gp,
                    sample_value_column='groupValue',
                    sample_name_column='groupName',
                    first_sample_name='groupE',
                    second_sample_name='groupC')
        
        # Print the result DataFrame.
        print(obj.result)

        # Example 4: Run FTest() with sample_name_column, sample_value_column,
        #            first_sample_name and second_sample_name.
        obj = FTest(data=insect_gp,
                    sample_value_column='groupValue',
                    sample_name_column='groupName',
                    first_sample_name='groupE',
                    second_sample_variance=100.0,
                    df2=25)

        # Print the result DataFrame.
        print(obj.result)

        # Example 5: Run FTest() with sample_name_column, sample_value_column,
        #            second_sample_name and first_sample_variance.
        obj = FTest(data=insect_gp,
                    sample_value_column='groupValue',
                    sample_name_column='groupName',
                    second_sample_name='groupC',
                    first_sample_variance=85.0,
                    df1=19)
        
        # Print the result DataFrame.
        print(obj.result)
    """