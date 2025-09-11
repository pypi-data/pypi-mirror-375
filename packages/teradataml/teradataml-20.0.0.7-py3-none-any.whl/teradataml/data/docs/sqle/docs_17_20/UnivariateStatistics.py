def UnivariateStatistics(newdata=None, target_columns=None, partition_columns=None,
                         stats='ALL', centiles=[1, 5, 10, 25, 50, 75, 90, 95, 99],
                         trim_percentile=20, **generic_arguments):
    """
    DESCRIPTION:
        UnivariateStatistics() function displays descriptive statistics for each specified numeric input DataFrame column.

    PARAMETERS:
        newdata:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" for which univariate
            statistics need to be displayed.
            Types: str OR list of Strings (str)

        partition_columns:
            Optional Argument.
            Specifies the names of the input partition columns.
            Types: str OR list of Strings (str)

        stats:
            Optional Argument.
            Specifies the statistics to calculate.
            Permitted Values:
                * SUM
                * COUNT or CNT
                * MAXIMUM or MAX
                * MINIMUM or MIN
                * MEAN
                * UNCORRECTED SUM OF SQUARES or USS
                * NULL COUNT or NLC
                * POSITIVE VALUES COUNT or PVC
                * NEGATIVE VALUES COUNT or NVC
                * ZERO VALUES COUNT or ZVC
                * TOP5 or TOP
                * BOTTOM5 or BTM
                * RANGE or RNG
                * GEOMETRIC MEAN or GM
                * HARMONIC MEAN or HM
                * VARIANCE or VAR
                * STANDARD DEVIATION or STD
                * STANDARD ERROR or SE
                * SKEWNESS or SKW
                * KURTOSIS or KUR
                * COEFFICIENT OF VARIATION or CV
                * CORRECTED SUM OF SQUARES or CSS
                * MODE
                * MEDIAN or MED
                * UNIQUE ENTITY COUNT or UEC
                * INTERQUARTILE RANGE or IQR
                * TRIMMED MEAN or TM
                * PERCENTILES or PRC
                * ALL
            Default Value: 'ALL'
            Types: str OR list of Strings (str)

        centiles:
            Optional Argument.
            Specifies the percentile to calculate.
            The function ignores Centiles unless Stats specifies PERCENTILES, PRC, or ALL.
            Default Value: [1, 5, 10, 25, 50, 75, 90, 95, 99]
            Types: int or list of int

        trim_percentile:
            Optional Argument.
            Specifies the trimmed lower percentile.
            Default Value: 20
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
                These generic arguments are supported by teradataml if the underlying SQL Engine
                function supports, else an exception is raised.

    RETURNS:
        Instance of UnivariateStatistics.
        Output teradataml DataFrames can be accessed using attribute
        references, such as UnivariateStatisticsObj.<attribute_name>.
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

        # Example 1: Display descriptive statistics of input DataFrame
        #            column "fare" by partitioning "sex" and "age".
        obj = UnivariateStatistics(newdata=titanic_data,
                                   target_columns='fare',
                                   partition_columns=['sex', 'age'],
                                   stats='ALL',
                                   centiles=[1, 5, 10, 25, 50, 75, 90, 95, 99],
                                   trim_percentile=20)

        # Print the result DataFrame.
        print(obj.result)

    """