def PACF(data=None, data_filter_expr=None,
         input_type=None, algorithm=None, max_lags=None,
         unbiased=False, alpha=None, **generic_arguments):
    """
    DESCRIPTION:
        The PACF() function provides insight as to whether the function
        being modeled is stationary or not. The partial auto correlations
        are used to measure the degree of correlation between series sample points.
        The algorithm removes the effects of the previous lag. For example,
        the coefficient for lag 4 focuses on the effect of activity based only
        at lag 4, with effects of lags 3, 2, and 1 removed.


    PARAMETERS:
        data:
            Required Argument.
            Specifies a series or an analytical result that contains previously
            computed auto correlation coefficients for lag and magnitude.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies filter expression for "data".
            Types: ColumnExpression

        input_type:
            Optional Argument.
            Specifies the type of data in the series.
            Permitted Values:
                * DATA_SERIES: A one dimensional input array that contains
                               a time series or a spatial series.
                * ACF: A one dimensional input array that is indexed by
                       LAG values, and contains previously-generated ACF magnitudes.
            Types: str

        algorithm:
            Required Argument.
            Specifies the algorithm to generate the partial auto-correlation function
            "PACF" coefficients.
            Permitted Values: LEVINSON_DURBIN, OLS
            Types: str

        max_lags:
            Required Argument.
            Specifies the maximum number of lags to calculate the partial autocorrelation.
            The lag value is limited to one less than the number of observations in the series.
            If the specified lag value exceeds the limit, the value is replaced with the
            system-defined maximum value.
            Default is 10*log10(N) where N is the number of observations.
            Types: int

        unbiased:
            Optional Argument.
            Specifies the formula to calculate the autocorrelation intermediate values.
            When set to False, denominator for autocorrelation calculation uses the
            Jenkins & Watts formula, otherwise uses the Box & Jenkins formula.
            Note:
                Only valid when "input_type" is 'DATA_SERIES'.
            Default Value: False
            Types: bool

        alpha:
            Optional Argument.
            Specifies confidence intervals for the given level. For example, if 0.05 is entered,
            then 95% confidence intervals are returned for standard deviation computed according
            to Bartlett’s formula.
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
        Instance of PACF.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as PACF_obj.<attribute_name>.
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
        load_example_data("uaf", ["test_pacf_12"])

        # Create teradataml DataFrame object.
        df = DataFrame.from_table("test_pacf_12")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=df,
                                  id="buoy_id",
                                  row_index="n_seq_no",
                                  row_index_style="SEQUENCE",
                                  payload_field="magnitude1",
                                  payload_content="REAL")

        # Example 1 : Calculate the partial autocorrelation function coefficients using
        #             'LEVINSON_DURBIN' algorithm, with maximum of 10 lags.
        PACF_out = PACF(data=data_series_df,
                        algorithm='LEVINSON_DURBIN',
                        max_lags=10)

        # Print the result DataFrame.
        print(PACF_out.result)
    
    """
    
