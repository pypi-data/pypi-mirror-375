def Portman(data=None, data_filter_expr=None, max_lags=None, test=None, 
            degrees_freedom=None, pacf_method=None, 
            significance_level=None, **generic_arguments):
    """
    DESCRIPTION:
        The Portman() function (Portmanteau test) uses a series of tests to
        determine whether the residuals can be classified as zero mean, no
        evidence of serial correlation, or the residuals exhibit homoscedastic
        variance. These residuals are also referred to as white noise. All the
        tests assume that the calculated statistic follows a chi-squared distribution.

        The following procedure is an example of how to use Portman() function:
            1. Use ArimaEstimate() function to get residuals from the data set.
            2. Use ArimaValidate() function to validate the output.
            3. Use Portman() to check the residuals for zero mean white noise using the 
            "fitresiduals" output attribute of ArimaValidate() function.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a residual univariate series data.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        max_lags:
            Required Argument.
            Specifies the number of explanatory variables referenced in the payload
            declaration in the original series specification. These
            explanatory variables are the variables that are used for the
            auxiliary regression.
            Types: int

        test:
            Required Argument.
            Specifies the Portmanteau test to use.
            Permitted Values:
                BP : Box-Pierce Q test. It calculates a test statistic value based
                     on the square of the auto-correlation coefficients associated
                     with the residual series. Result is expected to follow a Chi-squared
                     distribution.
                LB : Ljung-Box Q test. It calculates a test statistic value based on
                     the square of the auto-correlation coefficients adjusted by its
                     asymptotic variance.
                LM : Li-McLeod Q test. It calculates a test statistic value based
                     on the square of the auto-correlation coefficients, and does a
                     conservative adjustment to the value by its asymptotic variance.
                MQ : Monti Q test. It calculates a test statistic value based on
                     the square of the partial auto-correlation coefficients which
                     are then adjusted toward their asymptotic variance.
                ML : McLeod-Li Q test. It creates a new series from the residual
                     series by squaring each of the series entries, calculates the
                     auto-correlation coefficients associated with the new series,
                     and then calculates a test statistic value based on the square
                     of those auto-correlation coefficients, adjusted toward their
                     asymptotic variance.

            Types: str

        degrees_freedom:
            Required Argument.
            Specifies the degrees of freedom to be subtracted from "max_lags".
            Types: int

        pacf_method:
            Optional Argument.
            Specifies the underlying algorithm to calculate the partial auto-orrelation
            coefficients.
            Note:
                Applicable to Monti Q test only.
            Permitted Values: LEVINSON_DURBIN, OLS
            Types: str

        significance_level:
            Required Argument.
            Specifies the desired significance level for the test.
            Types: float

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
        Instance of Portman.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as Portman_obj.<attribute_name>.
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
        load_example_data("uaf","timeseriesdatasetsd4")

        # Create teradataml DataFrame object.
        df=DataFrame.from_table("timeseriesdatasetsd4")

        # Create teradataml TDSeries object for ArimaEstimate.
        series_arimaestimate = TDSeries(data=df,
                                        id="dataset_id",
                                        row_index="seqno",
                                        row_index_style="SEQUENCE",
                                        payload_field="Magnitude",
                                        payload_content="REAL")

        # Function outputs a result set that contains the estimated
        # coefficients with accompanying per-coefficient statistical ratings.
        arima_estimate = ArimaEstimate(data1=series_arimaestimate,
                                       nonseasonal_model_order=[1,0,0],
                                       constant=True,
                                       algorithm='MLE',
                                       fit_percentage=70,
                                       coeff_stats=True,
                                       fit_metrics=True,
                                       residuals=True
                                       )

        # Create teradataml TDAnalyticResult object for ArimaValidate.
        art_arimavalidate = TDAnalyticResult(data=arima_estimate.result)

        # Function produces a multiple outputs to return up to four result sets.
        arima_validate=ArimaValidate(data=art_arimavalidate,
                                     fit_metrics=True,
                                     residuals=True)

        # Create teradataml TDSeries object for Portman.
        series_portman = TDSeries(data=arima_validate.fitresiduals,
                                  id="dataset_id",
                                  row_index="ROW_I",
                                  row_index_style="SEQUENCE",
                                  payload_field="RESIDUAL",
                                  payload_content="REAL")

        # Example 1 : Calculates a test statistic value based
        #             on the square of the auto-correlation coefficients
        #             associated with the residual series using TDSeries.
        portman1 = Portman(data=series_portman,
                          max_lags=2,
                          test='BP',
                          degrees_freedom=1,
                          significance_level=0.05)

        # Print the result DataFrame.
        print(portman1.result)

        # Example 2 : Calculates a test statistic value based
        #             on the square of the auto-correlation coefficients
        #             associated with the residual series using TDAnalyticResult.

        # Create teradataml TDAnalyticResult object for Portman.
        art_portman = TDAnalyticResult(data=arima_validate.result,layer="ARTFITRESIDUALS")

        portman2 = Portman(data=art_portman,
                          max_lags=2,
                          test='BP',
                          degrees_freedom=1,
                          significance_level=0.05)

        # Print the result DataFrame.
        print(portman2.result)

    """
    