def ArimaValidate(data=None, data_filter_expr=None, fit_metrics=False,
                  residuals=False,
                  output_fmt_index_style="NUMERICAL_SEQUENCE",
                  **generic_arguments):
    """
    DESCRIPTION:
        The ArimaValidate() function performs an in-sample
        forecast for both seasonal and non-seasonal auto-regressive (AR),
        moving-average (MA), ARIMA models and Box-Jenkins seasonal
        ARIMA model formula followed by an analysis of the produced
        residuals. The aim is to provide a collection of metrics useful to select the model
        and expose the produced residuals such that multiple model validation
        and statistical tests can be conducted.
        The following procedure is an example of how to use ArimaValidate():
            * Run the ArimaEstimate() function to get the coefficients for the ARIMA model.
            * Run the ArimaValidate() function to validate the "goodness of fit" of the ARIMA model,
              when "fit_percentage" is not 100 in ArimaEstimate().

    PARAMETERS:
        data:
            Required Argument.
            Specifies the TDAnalyticResult object over the output
            of ArimaEstimate() function.
            Types: TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        fit_metrics:
            Optional Argument.
            Specifies whether to generate the model metadata statistics.
            When set to True, metadata statistics are generated otherwise, it is not.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies whether to generate the model residuals.
            When set to True, residuals are generated,
            otherwise it is not.
            Default Value: False
            Types: bool

        output_fmt_index_style:
            Optional Argument.
            Specifies the index_style of the output format.
            Default Value: NUMERICAL_SEQUENCE
            Permitted Values: NUMERICAL_SEQUENCE, FLOW_THROUGH
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
        Instance of ArimaValidate.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ArimaValidate_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata - Available when "fit_metrics" is set to True, otherwise not.
            3. fitresiduals - Available when "residuals" is set to True, otherwise not.
            4. model


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

        # Example 1: Validate the "goodness of fit" of the ARIMA model.

        # Create teradataml TDAnalyticResult object over the result attribute of 'arima_estimate_op'.
        data_art_df = TDAnalyticResult(data=arima_estimate_op.result)

        uaf_out = ArimaValidate(data=data_art_df, 
                                fit_metrics=True, 
                                residuals=True)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.fitmetadata)
        print(uaf_out.fitresiduals)
        print(uaf_out.model)
    """
