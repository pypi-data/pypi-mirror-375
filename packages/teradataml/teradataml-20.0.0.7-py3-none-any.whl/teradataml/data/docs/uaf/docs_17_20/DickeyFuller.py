def DickeyFuller(data=None, data_filter_expr=None, algorithm=None, 
                 max_lags=0,
                 **generic_arguments):
    """
    DESCRIPTION:
        The DickeyFuller() function tests for the presence of one or more
        unit roots in a series to determine if the series is non-stationary.
        When a series contains unit roots, it is non-stationary. When a series
        contains no unit roots, whether the series is stationary is based on
        other factors.

        The following procedure is an example of how to use DickeyFuller() function:
            * Run DickeyFuller() on the time series being modeled.
            * Retrieve the results of the DickeyFuller() test to determine if the
              time series contains any unit roots.
            * If unit roots are present, use a technique such as differencing such as Diff()
              or seasonal normalization, such as SeasonalNormalize(), to create a new series,
              then rerun the DickeyFuller() test to verify that the differenced or
              seasonally-normalized series unit root are removed.
            * If the result shows unit roots, use Diff() and SeasonalNormalize()
              to remove unit roots.


    PARAMETERS:
        data:
            Required Argument.
            Specifies a single logical-runtime series as an input or TDAnalyticResult which
            contains ARTFITRESIDUALS layer.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        algorithm:
            Required Argument.
            Specifies the type of regression that is run for the test.
            Permitted Values:
                * NONE: Random walk
                * DRIFT: Random walk with drift
                * DRIFTNTREND: Random walk with drift and trend
                * SQUARED: Random walk with drift, trend, and
                           quadratic trend.
            Types: str

        max_lags:
            Optional Argument.
            Specifies the maximum number of lags to use with the regression
            equation. Range is [0, 100]
            DefaultValue: 0
            Types: int

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
        Instance of DickeyFuller.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as DickeyFuller_obj.<attribute_name>.
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
        df = DataFrame.from_table("timeseriesdatasetsd4")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=df,
                                  id="dataset_id",
                                  row_index="seqno",
                                  row_index_style= "SEQUENCE",
                                  payload_field="magnitude",
                                  payload_content="REAL")

        # Example 1 : Determine whether the series is non-stationary by testing
        #             for the presence of the unit roots using random walk with
        #             linear trend for regression.
        uaf_out = DickeyFuller(data=data_series_df,
                               algorithm='DRIFT')

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    