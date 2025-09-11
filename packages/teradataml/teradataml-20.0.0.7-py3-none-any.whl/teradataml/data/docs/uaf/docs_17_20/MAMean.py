def MAMean(data=None, data_filter_expr=None, forecast_periods=None,
           algorithm=None, prediction_intervals="BOTH", k_order=None,
           fit_metrics=False, residuals=False,
           output_fmt_index_style="NUMERICAL_SEQUENCE", 
           **generic_arguments):
    """
    DESCRIPTION:
        The MAMean() function forecasts a user-defined number of periods into the future,
        that is the number of periods beyond the last observed sample point in the series.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a logical univariate series with historical data.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        forecast_periods:
            Required Argument.
            Specifies the number of periods to forecast ahead.
            The argument "forecast_periods" must be a positive integer value in the range [1, 32000].
            Types: int

        algorithm:
            Required Argument.
            Specifies the type of algorithm to use.
            Permitted Values:
                * MA: Moving Average
                * MEAN: Mean average
                * NAIVE: Naive, also known as random walk forecast
            Types: str

        prediction_intervals:
            Optional Argument.
            Specifies the confidence level for the prediction, such that 85 means 85% confidence.
            Permitted Values: NONE, 80, 95, BOTH
            Default Value: BOTH
            Types: str

        k_order:
            Optional Argument.
            Specifies the moving average forecast.
            The argument "k_order" must be a positive int value in the range [1, 32000].
            Note:
                * This is a required argument when "alogorithm" is set to 'MA'.
            Types: int

        fit_metrics:
            Optional Argument.
            Specifies a flag to generate the secondary result set that contains the model metadata
            statistics. When set to True, function generate the secondary result set, otherwise
            not. The generated result set can be retrieved using the attribute fitmetadata of
            the function output.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies a flag to generate the tertiary result set that contains the model residuals.
            When set to True, means generate the tertiary result set, otherwise not.
            The generated result set can be retrieved using the attribute fitresiduals of
            the function output.
            Default Value: False
            Types: bool

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Default Value: NUMERICAL_SEQUENCE
            Permitted Values: NUMERICAL_SEQUENCE
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
        Instance of MAMean.
        Output teradataml DataFrames can be accessed using attribute
        references, such as MAMean_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata - Available when "model_stats" is set to True, otherwise not.
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
        load_example_data("uaf", ["orders1"])

        # Create teradataml DataFrame object.
        df = DataFrame.from_table("orders1")

        # Create teradataml TDSeries object.
        result = TDSeries(data=df,
                          id="store_id",
                          row_index="seq",
                          row_index_style="SEQUENCE",
                          payload_field="sales",
                          payload_content="REAL")

        # Example 1: Forecast 8 number of periods into the future beyond the last observed sample
        #            point in the series using the moving average algorithm and generate metadata as
        #            well as residuals data.
        uaf_out = MAMean(data=result,
                         forecast_periods=8,
                         algorithm='MA',
                         prediction_intervals='BOTH',
                         k_order=3,
                         fit_metrics=True,
                         residuals=True)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.fitresiduals)
        print(uaf_out.fitmetadata)
    
    """
    