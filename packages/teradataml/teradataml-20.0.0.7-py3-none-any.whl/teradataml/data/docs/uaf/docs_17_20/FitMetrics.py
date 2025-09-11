def FitMetrics(data=None, data_filter_expr=None, var_count=None,
               fstat=False, significance_level=None, **generic_arguments):
    """
    DESCRIPTION:
        The FitMetrics() takes the original series, the model-predicted series,
        the original series mean and the modeling residuals to generate the
        goodness-of-fit of the modeling exercise.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a single multivariate series as an input or a
            TDAnalyticResult object over the residual results from
            a previously run regression operation.
            When multivariate series is the input, the three fields
            should be the original series, predicted series,
            and residuals from the original regression.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        var_count:
            Required Argument.
            Specifies an integer indicating how many explanatory variables
            including the constant are used while calculating the fitness
            metrics.
            Types: int

        fstat:
            Optional Argument.
            Specifies whether to include F-test related
            statistics in the final result.
            When set to True, results are included otherwise,
            results are not included.
            Default Value: False
            Types: bool

        significance_level:
            Optional Argument.
            Specifies the significance level for the test.
            Value should be between 0 and 1.
            Note:
                Valid only when "fstat" is set to True.
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
        Instance of FitMetrics.
        Output teradataml DataFrames can be accessed using attribute
        references, such as FitMetrics_obj.<attribute_name>.
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
        load_example_data("uaf", ["timeseriesdatasetsd4"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("timeseriesdatasetsd4")

        # Execute ArimaEstimate() function to estimate the coefficients
        # and statistical ratings corresponding to an ARIMA model.

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="dataset_id",
                                  row_index="seqno",
                                  row_index_style="SEQUENCE",
                                  payload_field="magnitude",
                                  payload_content="REAL")

        # Execute ArimaEstimate function.
        arima_estimate_op = ArimaEstimate(data1=data_series_df,
                                          nonseasonal_model_order=[2,0,0],
                                          constant=False,
                                          algorithm="MLE",
                                          coeff_stats=True,
                                          fit_metrics=True,
                                          residuals=True,
                                          fit_percentage=80)

        # Example 1: Generate goodness of fit metrics by using TDAnalyticResult
        #            object over the result attribute of 'arima_estimate_op'
        #            with 'ARTFITRESIDUALS' layer as input.
        # Create teradataml TDAnalyticResult object.
        data_art_df = TDAnalyticResult(data=arima_estimate_op.result,
                                       layer="ARTFITRESIDUALS")

        uaf_out = FitMetrics(data=data_art_df,
                             var_count=5,
                             fstat=True,
                             significance_level=0.05)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Generate goodness of fit metrics by using TDSeries over
        #            the 'fitresiduals' attribute of 'arima_estimate_op'
        #            as input.
        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=arima_estimate_op.fitresiduals,
                                  id="dataset_id",
                                  row_index="ROW_I",
                                  row_index_style="SEQUENCE",
                                  payload_field=["RESIDUAL", "ACTUAL_VALUE",
                                                 "CALC_VALUE"],
                                  payload_content="MULTIVAR_REAL")

        uaf_out = FitMetrics(data=data_series_df, var_count=5)

        # Print the result DataFrame.
        print(uaf_out.result)

    """
