def ExtractResults(data=None, data_filter_expr=None, **generic_arguments):
    """
    DESCRIPTION:
        The ExtractResults() function retrieves auxiliary result sets
        stored in an ART. The auxillary layers are as follows:
            * ARTFITRESIDUALS contains the residual series.
            * ARTFITMETADATA contains the goodness-of-fit metrics.
            * ARTMODEL shows the validation model context.
            * ARTVALDATA is used for the internal validation process

        The functions that have multiple layers are shown in the table.
        Layers of each function can be extracted from the function output,
        i.e., "result" attribute, using the layer name specified below:

        ------------------------------------------------------------------
        | Function                    | Layers                           |
        ------------------------------------------------------------------
        | LinearRegr                  | 1. ARTPRIMARY                    |
        |                             | 2. ARTFITMETADATA                |
        |                             | 3. ARTFITRESIDUALS               |
        |                             |                                  |
        | MultivarRegr                | 1. ARTPRIMARY                    |
        |                             | 2. ARTFITMETADATA                |
        |                             | 3. ARTFITRESIDUALS               |
        |                             |                                  |
        | ArimaEstimate               | 1. ARTPRIMARY                    |
        |                             | 2. ARTFITMETADATA                |
        |                             | 3. ARTFITRESIDUALS               |
        |                             | 4. ARTMODEL                      |
        |                             | 5. ARTVALDATA                    |
        |                             |                                  |
        | ArimaValidate               | 1. ARTPRIMARY                    |
        |                             | 2. ARTFITMETADATA                |
        |                             | 3. ARTFITRESIDUALS               |
        |                             | 4. ARTMODEL                      |
        |                             |                                  |
        | SeasonalNormalize           | 1. ARTPRIMARY                    |
        |                             | 2. ARTMETADATA                   |
        |                             |                                  |
        | CumulPeriodogram            | 1. ARTPRIMARY                    |
        |                             | 2. ARTCPDATA                     |
        |                             |                                  |
        | MAMean                      | 1. ARTPRIMARY                    |
        |                             | 2. ARTFITMETADATA                |
        |                             | 3. ARTFITRESIDUALS               |
        |                             |                                  |
        | SimpleExp                   | 1. ARTPRIMARY                    |
        |                             | 2. ARTFITMETADATA                |
        |                             | 3. ARTFITRESIDUALS               |
        |                             |                                  |
        | HoltWintersForecast         | 1. ARTPRIMARY                    |
        |                             | 2. ARTFITMETADATA                |
        |                             | 3. ARTSELMETRICS                 |
        |                             | 4. ARTFITRESIDUALS               |
        ------------------------------------------------------------------

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input data as TDAnalyticResult object
            with "layer" argument.
            Types: TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

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
        Instance of ExtractResults.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as ExtractResults_obj.<attribute_name>.
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


        # Create teradataml TDSeries object for ArimaEstimate.
        series_arimaestimate = TDSeries(data=df,
                                        id="dataset_id",
                                        row_index="seqno",
                                        row_index_style="SEQUENCE",
                                        payload_field="magnitude",
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

        # Example 1 : Extract the residuals from the ArimaEstimate function
        #             output, by specifying the layer name 'ARTFITRESIDUALS'.
        # Create teradataml TDAnalyticResult object.
        art_extractresult = TDAnalyticResult(data=arima_estimate.result,
                                             layer="ARTFITRESIDUALS")

        # Execute the function ExtractResults() to extract the layer.
        uaf_out1 = ExtractResults(data=art_extractresult)

        # Print the result DataFrame.
        print(uaf_out1.result)

        # Example 2 : Extract the residuals from the ArimaEstimate function
        #             output, by specifying the layer name 'ARTFITMETADATA'.
        # Create teradataml TDAnalyticResult object.
        art_extractresult = TDAnalyticResult(data=arima_estimate.result,
                                             layer="ARTFITMETADATA")

        # Execute the function ExtractResults() to extract the layer.
        uaf_out2 = ExtractResults(data=art_extractresult)

        # Print the result DataFrame.
        print(uaf_out2.result)
    
    """
    