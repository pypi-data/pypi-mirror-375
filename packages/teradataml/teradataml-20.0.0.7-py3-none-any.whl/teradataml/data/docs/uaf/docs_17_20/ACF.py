def ACF(data=None, data_filter_expr=None, max_lags=None, 
        func_type=False, unbiased=False, demean=True, 
        qstat=False, alpha=None,
        **generic_arguments):
    """
    DESCRIPTION:
        The ACF() function calculates the autocorrelation or
        autocovariance of a time series. The autocorrelation and
        autocovariance show how the time series correlates or
        covaries with itself when delayed by a lag in time or space.
        When the ACF() function is computed, a coefficient corresponding
        to a particular lag is affected by all the previous lags.
        For example, the coefficient for lag 4 includes effects of
        activity at lags 3, 2, and 1.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input time series with payload 
            content value as 'REAL' or 'MULTIVAR_REAL'.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        max_lags:
            Optional Argument.
            Specifies the maximum number of lags to calculate the
            autocorrelation or autocovariance, a positive integer
            less than or equal to N-1, where N is the number of
            observations in the time series. The default is 10*log10(N).

            When "max_lags" value exceeds N-1, the function ignores "max_lags"
            and uses the system-defined value.
            Note:
                For the function to resolve, 
                the number-of-entries-per-series * max_lags must be less than
                7,864,200,000. For a series having more than 88,600 entries,
                the "max_lags" value must be a number smaller than 88,600 for
                the function to complete.
            Types: int

        func_type:
            Optional Argument.
            Specifies the calculation type, that is whether to use
            autocorrelation or autocovariance method. 
            When set to False, calculation type as autocorrelation,
            otherwise it is autocovariance.
            Default Value: False
            Types: bool

        unbiased:
            Optional Argument.
            Specifies the formula for the denominator
            to calculate the autocovariance,
            When set to False, Jenkins-Watts formula is used,
            otherwise Box-Jenkins is used.
            Default Value: False
            Types: bool

        demean:
            Optional Argument.
            Specifies whether to subtract the mean X from 
            each element of X in the formula before 
            calculating the autocorrelation or autocovariance. 
            When set to False, mean value is not subtracted 
            from each element, otherwise subtracted.
            Default Value: True
            Types: bool

        qstat:
            Optional Argument.
            Specifies whether to provide the Ljung-Box 
            q-statistic and its associated p-value for each
            autocorrelation coefficient. When set to True,
            the Ljung-Box q-statistic and its associated 
            p-value included in the result, otherwise not.
            Default Value: False
            Types: bool

        alpha:
            Optional Argument.
            Specifies the level to return confidence interval.
            Use a positive float to return the interval. The
            function computes the standard deviation for confidence
            intervals with Bartlett's formula. For example,
            if "alpha" value is '0.05' meaning the 95% level, then 
            confidence intervals (CONFINT) are included in the results
            where the standard deviation is computed according to
            Bartlett’s formula.
            Default behavior when "alpha" avoided or not a positive
            float: 
                * The function does not return confidence intervals.
            Types: int OR float

        **generic_arguments:
            Specifies the generic keyword arguments of UAF functions.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the
                    function in a table or not. When set to True,
                    results are persisted in a table; otherwise,
                    results are garbage collected at the end of the
                    session.
                    Note that, when UAF function is executed, an 
                    analytic result table (ART) is created.
                    Default Value: False
                    Types: bool

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the
                    function in a volatile ART or not. When set to
                    True, results are stored in a volatile ART,
                    otherwise not.
                    Default Value: False
                    Types: bool

                output_table_name:
                    Optional Argument.
                    Specifies the name of the table to store results. 
                    If not specified, a unique table name is internally 
                    generated.
                    Types: str

                output_db_name:
                    Optional Argument.
                    Specifies the name of the database to create output 
                    table into. If not specified, table is created into 
                    database specified by the user at the time of context 
                    creation or configuration parameter. Argument is ignored,
                    if "output_table_name" is not specified.
                    Types: str


    RETURNS:
        Instance of ACF.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as ACF_obj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            1. result


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        # Check the list of available UAF analytic functions.
        display_analytic_functions(type="UAF")

        # Load the example data.
        load_example_data("uaf", ["ocean_buoy2"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("ocean_buoy2")

        # Example 1: Apply the ACF() function to calculate the autocorrelation 
        #            of a time series with itself by using "max_lags".
        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="buoy_id",
                                  row_index_style="SEQUENCE",
                                  row_index="n_seq_no",
                                  payload_field="magnitude1",
                                  payload_content="REAL")

        # Execute ACF for TDSeries.
        uaf_out = ACF(data=data_series_df,
                      max_lags=2)

        # Print the result DataFrame.
        print(uaf_out.result)

    """
