def HoltWintersForecaster(data=None, data_filter_expr=None, forecast_periods=None,
                          alpha=None, beta=None, gamma=None, seasonal_periods=None,
                          init_level=None, init_trend=None, init_season=None,
                          model=None, fit_percentage=100,
                          prediction_intervals="BOTH", fit_metrics=False,
                          selection_metrics=False, residuals=False,
                          output_fmt_index_style="NUMERICAL_SEQUENCE",
                          **generic_arguments):
    """
    DESCRIPTION:
        The HoltWintersForecaster() function uses triple exponential smoothing
        on a forecast model with seasonal data.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the time series to forecast using historical data
            with series content type as 'REAL' or 'MULTIVAR_REAL'.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        forecast_periods:
            Required Argument.
            Specifies the number of periods to forecast.
            Value must be greater than or equal to 1.
            Types: int

        alpha:
            Optional Argument.
            Specifies a value to control the smoothing relative to
            the level component of the forecasting equation. If
            specified, this value is used in the equation to perform
            the forecasting, else the "alpha" value is estimated using
            goodness-of-fit metrics. Value must be greater than or equal
            to 0 and less than or equal to 1.
            Types: int OR float 

        beta:
            Optional Argument.
            Specifies a value to control the smoothing relative to
            the trend component of the forecasting equation. If
            specified, this value is used in the equation to perform
            the forecasting, else the "beta" value is estimated using
            goodness-of-fit metrics. Value must be greater than or equal
            to 0 and less than or equal to 1.
            Types: int OR float

        gamma:
            Optional Argument.
            Specifies a value to control the smoothing relative to
            the seasonal component of the forecasting equation. If
            specified, this value is used in the equation to perform
            the forecasting, else the "gamma" value is estimated using
            goodness-of-fit metrics. Value must be greater than or equal
            to 0 and less than or equal to 1.
            Types: int OR float

        seasonal_periods:
            Optional Argument.
            Specifies the number of periods or sample points for one season.
            For example, for yearly data with monthly sample points, the parameter
            is 12; and for quarterly data with monthly sample points, the
            parameter is 3. Value must be greater than or equal to 1.
            Note:
                Required when "gamma" or "init_season" is specified.
            Types: int

        init_level:
            Optional Argument.
            Specifies the initialization value used as part of the fitting
            and forecasting operations. If not specified, then the initialization
            value is calculated as an additive level.
            Types: int OR float

        init_trend:
            Optional Argument.
            Specifies the initialization value used as part of the fitting
            and forecasting operations. If not specified, then the initialization
            value is calculated as an additive trend.
            Types: int OR float

        init_season:
            Optional Argument.
            Specifies a list of initialization values, one per period. If
            specified, the initialization value is used as part of the
            fitting and forecasting operations, else the initialization
            value is calculated as a multiplicative seasonality.
            Types: int, list of int, float, list of float

        model:
            Required Argument.
            Specifies the type of Holt Winters forecasting.
            Permitted Values:
                * ADDITIVE: It is based on Holt Winters Additive approach.
                * MULTIPLICATIVE: It is based on Holt Winters Multiplicative approach.
            Types: str

        fit_percentage:
            Optional Argument.
            Specifies percentage of passed-in sample points to use for the
            model fitting or parameter estimation. Value must be greater
            than or equal to 0 and less than or equal to 100.
            Default Value: 100
            Types: int

        prediction_intervals:
            Optional Argument.
            Specifies the confidence level for the prediction.
            Permitted Values:
                * NONE
                * 80
                * 95
                * BOTH
            Default Value: BOTH
            Types: str

        fit_metrics:
            Optional Argument.
            Specifies whether to generate the result set that contains the
            model metadata statistics. When set to True, function generates
            the model statistics, otherwise not. The generated model
            statistics can be retrieved using the attribute "fitmetadata"
            of the function output.
            Default Value: False
            Types: bool

        selection_metrics:
            Optional Argument.
            Specifies whether to generate the result set that contains the
            selection metrics. When set to True, function generates the
            selection metrics, otherwise not. The generated selection metrics
            can be retrieved using the attribute "selmetrics" of the function
            output.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies whether to generate the result set that contains the
            model residuals. When set to True, the function generates the
            residuals, otherwise not. The generated residuals can be retrieved
            using the attribute "fitresiduals" of the function output.
            Default Value: False
            Types: bool

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Permitted Values:
                * NUMERICAL_SEQUENCE
                * FLOW_THROUGH
            Default Value: NUMERICAL_SEQUENCE
            Types: str

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
        Instance of HoltWintersForecaster.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as HoltWintersForecaster_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata - Available when "fit_metrics" is set to True, otherwise not.
            3. selmetrics - Available when "selection_metrics" is set to True, otherwise not.
            4. fitresiduals - Available when "residuals" is set to True, otherwise not.


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
        load_example_data("uaf", ["us_air_pass"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("us_air_pass")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  row_index="idx",
                                  row_index_style="SEQUENCE",
                                  id="id",
                                  payload_field="international",
                                  payload_content="REAL")

        # Example 1: Generate forecast for 12 periods using multiplicative model.
        uaf_out = HoltWintersForecaster(data=data_series_df,
                                        forecast_periods=12,
                                        model="MULTIPLICATIVE",
                                        residuals=True,
                                        fit_metrics=True,
                                        selection_metrics=True)

        # Print the result DataFrames.
        print(uaf_out.result)

        # Print the model statistics result.
        print(uaf_out.fitmetadata)

        # Print the selection metrics result.
        print(uaf_out.selmetrics)
        
        # Print the residuals statistics result.
        print(uaf_out.fitresiduals)
    
    """
