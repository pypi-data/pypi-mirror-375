def SimpleExp(data=None, data_filter_expr=None, forecast_periods=None, 
              alpha=None, prediction_intervals="BOTH", 
              forecast_starting_value="FIRST", fit_metrics=False, 
              residuals=False, 
              output_fmt_index_style="NUMERICAL_SEQUENCE", 
              **generic_arguments):
    """
    DESCRIPTION:
        The SimpleExp() function uses simple exponential smoothing for
        the forecast model for univariate data. It does not use seasonality
        or trends for the model.


    PARAMETERS:
        data:
            Required Argument.
            Specifies a logical univariate series with historical data.
            Input value should be 'REAL'.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        forecast_periods:
            Required Argument.
            Specifies number of periods to forecast.
            This value must be a positive integer in the range of [1, 32000].
            Types: int

        alpha:
            Optional Argument.
            Specifies if this argument is specified, its value is used
            in the equation to perform the forecasting. If this argument
            is not specified, the value of 'alpha' is estimated by using
            goodness-of-fit metrics. Value must be greater than or equal to
            0 and less than or equal to 1.
            Types: int OR float

        prediction_intervals:
            Optional Argument.
            Specifies the confidence level for the prediction. For example,
            85 means 85% confidence.
            Permitted Values: NONE, 80, 95, BOTH
            Default Value: BOTH
            Types: str

        forecast_starting_value:
            Optional Argument.
            Specifies the starting value for the interval.
            Permitted Values: FIRST, MEAN
            Default Value: FIRST
            Types: str

        fit_metrics:
            Optional Argument.
            Specifies whether to generate the result set that
            contains the model metadata statistics. When set to True,
            function generates the model statistics, otherwise not.
            The generated model statistics can be retrieved using the
            attribute "fitmetadata" of the function output.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies whether to generate the result set that
            contains the model residuals. When set to True, the function
            generates the residuals, otherwise not. The generated residuals
            can be retrieved using the attribute "fitresiduals" of
            the function output.
            Default Value: False
            Types: bool

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Permitted Values: NUMERICAL_SEQUENCE, FLOW_THROUGH
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
        Instance of SimpleExp.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as SimpleExp_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata - Available when "fit_metrics" is set to True, otherwise not.
            3. fitresiduals - Available when "residuals" is set to True, otherwise not.


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
        load_example_data("uaf","inflation")

        # Create teradataml DataFrame object.
        df=DataFrame.from_table("inflation")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=df,
                                  id="countryid",
                                  row_index="year_recorded",
                                  row_index_style= "TIMECODE",
                                  payload_field="inflation_rate",
                                  payload_content="REAL")

        # Example 1 : Execute SimpleExp() function which uses simple exponential
        #             smoothing for the forecast model for univariate data to
        #             produce historical observed values, forecasted value,
        #             predicted values, residuals and metrics containing goodness
        #             of fit.
        uaf_out = SimpleExp(data=data_series_df,
                            forecast_periods=4,
                            prediction_intervals="80",
                            fit_metrics=True,
                            residuals=True)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.fitresiduals)
        print(uaf_out.fitmetadata)
    
    """
    