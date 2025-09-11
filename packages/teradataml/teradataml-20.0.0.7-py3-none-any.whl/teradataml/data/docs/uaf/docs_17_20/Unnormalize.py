def Unnormalize(data1=None, data1_filter_expr=None, data2=None, 
                data2_filter_expr=None, fields=None, 
                input_fmt_input_mode=None, 
                output_fmt_index_style="NUMERICAL_SEQUENCE", 
                **generic_arguments):
    """
    DESCRIPTION:
        The Unnormalize() function reconstructs a series created by SeasonalNormalize().
        The function is usually used for the forecasting phase of modeling.

        The following procedure is an example of how to use function when the series
        to be modeled is found to be unstationary:
            * Use SeasonalNormalize() to make the series stationary.
            * Develop the ARIMA forecast model.
            * Use the ARIMA model to forecast the normalized series.
            * Use function on the forecasted normalized series to undo the
              effects of normalization and produce the final forecasted series result.


    PARAMETERS:
        data1:
            Required Argument.
            Specifies the input series to unnormalize.
            Input payload content type can be REAL, MUTLIVAR_REAL, or
            MUTLTIVAR_ANYTYPE. TDSeries must include "interval" argument.
            Types: TDSeries

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Required Argument.
            Specifies the output series. Output series type matches input series type.
            This should be a metadata output of SeasonalNormalize() function or
            TDAnalyticResults created on the teradataml dataframe that contains
            previously normalized results with the (mean, standardDeviation) pairs
            needed to unnormalize the first input series.
            Types: TDSeries, TDAnalyticResult

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        fields:
            Optional Argument.
            Specifies fields to unnormalize. The fields should be separated by commas.
            When specified, only the specified payload fields in the list are unnormalized,
            otherwise all payload fields of the first input are unnormalized.
            Values should be 0 or positive numbers. The payload field indices start
            at 1.
            Types: int

        input_fmt_input_mode:
            Required Argument.
            Specifies the input mode supported by the function.
            Permitted Values: MANY2ONE, ONE2ONE, MATCH
            Types: str

        output_fmt_index_style:
            Optional Argument.
            Specifies the INDEX_STYLE of the output format.
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
        Instance of Unnormalize.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as Unnormalize_obj.<attribute_name>.
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
        load_example_data("uaf", ["store_sales"])

        # Create teradataml DataFrame objects.
        df = DataFrame("store_sales")

        # Create teradataml TDSeries objects.
        td_series = TDSeries(data=df,
                             row_index="ts",
                             row_index_style="TIMECODE",
                             id="StoreID",
                             payload_field="Sales",
                             payload_content="REAL",
                             interval="CAL_MONTHS(1)"
                             )

        # Produce the stationary series.
        seasonalnormalize = SeasonalNormalize(data=td_series,
                                              season_cycle="CAL_YEARS",
                                              cycle_duration=1,
                                              output_fmt_index_style="FLOW_THROUGH"
                                              )

        # Create teradataml TDSeries objects.
        td_series1 = TDSeries(data=seasonalnormalize.result,
                              id="StoreID",
                              row_index="ROW_I",
                              row_index_style="TIMECODE",
                              payload_field="Sales",
                              payload_content="REAL",
                              interval="CAL_MONTHS(1)"
                              )

        # Example 1 : Function reverse the effects of normalization and
        #             produce the final forecasted series result using TDSeries.

        # Create teradataml TDSeries objects.
        td_series2 = TDSeries(data=seasonalnormalize.metadata,
                              id="StoreID",
                              row_index="ROW_I",
                              row_index_style="SEQUENCE",
                              payload_field=["MEAN_Sales", "SD_Sales"],
                              payload_content="MULTIVAR_REAL"
                              )

        uaf_out = Unnormalize(data1=td_series1,
                              data2=td_series2,
                              input_fmt_input_mode="MATCH",
                              output_fmt_index_style="FLOW_THROUGH")

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2 : Function reverse the effects of normalization and
        #             produce the final forecasted series result using TDAnalyticResult.

        # Create teradataml TDAnalyticResult objects.
        td_art = TDAnalyticResult(data=seasonalnormalize.result,
                                  layer='ARTMETADATA')

        uaf_out = Unnormalize(data1=td_series1,
                              data2=td_art,
                              input_fmt_input_mode="MATCH",
                              output_fmt_index_style="FLOW_THROUGH")

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    