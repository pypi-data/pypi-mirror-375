def SeasonalNormalize(data=None, data_filter_expr=None, season_cycle=None,
                      cycle_duration=None, season_info=0,
                      output_fmt_index_style="NUMERICAL_SEQUENCE",
                      **generic_arguments):
    """
    DESCRIPTION:
        SeasonalNormalize() takes a non-stationary series and normalizes the
        series by first dividing the series into cycles and intervals, then averaging
        and normalizing with respect to each interval over all cycles.
        This form of normalization is effective relative to eliminating
        non-stationary properties such as unit roots and periodicities.

        The following procedure is an example of how to use SeasonalNormalize():
            1. Detect the unit roots using DickeyFuller().
            2. Use SeasonalNormalize() to create a series with potentially the unit roots eliminated.
            3. Use DickeyFuller() to verify that unit roots were eliminated from the newly-formed normalized series.
            4. Use ArimaEstimate() and ArimaValidate() to create an ARIMA model from the normalized series.
            5. Use ArimaForecast() to forecast the normalized series.
            6. Use Unnormalize() passing in the forecasted series and the original unnormalized series to
               produce a forecasted series with the effects of SeasonalNormalize() removed.


    PARAMETERS:
        data:
            Required Argument.
            Single input source that contains univariate series instances.
            The associated "payload_content" is 'REAL'.
            The payload is the series element magnitude.
            TDSeries must include the usage of the "interval" parameter
            that is the interval to used by the function to divide the
            series cycles into intervals.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        season_cycle:
            Required Argument.
            Specifies the logical time-unit.
            Permitted Values:
                * CAL_YEARS
                * CAL_MONTHS
                * CAL_DAYS
                * WEEKS
                * DAYS
                * HOURS
                * MINUTES
                * SECONDS
                * MILLISECONDS
                * MICROSECONDS
            Types: str

        cycle_duration:
            Required Argument.
            Specifies the number of time-units as the duration of each seasonal
            cycle.
            Types: int

        season_info:
            Optional Argument.
            Specifies whether to generate additional columns CYCLE_NO and
            SEASON_NO. CYCLE_NO is the n-th cycle of the season. SEASON_NO
            is the season for the data.
            Permitted Values:
                * 0 indicates no extra columns being generated.
                * 1 indicates SEASON_NO column being generated.
                * 2 indicates CYCLE_NO column being generated.
                * 3 indicates both SEASON_NO and CYCLE_NO columns being generated.
            Default Value: 0
            Types: int

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Default Value: NUMERICAL_SEQUENCE
            Permitted Values:
                * NUMERICAL_SEQUENCE
                * FLOW_THROUGH
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
        Instance of SeasonalNormalize.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as SeasonalNormalize_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. metadata


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
        load_example_data("uaf", ["river_data"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("river_data")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="station_id",
                                  row_index="timevalue",
                                  row_index_style="TIMECODE",
                                  payload_field="flow_velocity",
                                  payload_content="REAL",
                                  interval="CAL_MONTHS(1)")

        # Example 1 : Normalize the series by removing the unit roots.
        uaf_out = SeasonalNormalize(data=data_series_df,
                                    season_cycle="CAL_MONTHS",
                                    cycle_duration=1)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.metadata)
    
    """
    