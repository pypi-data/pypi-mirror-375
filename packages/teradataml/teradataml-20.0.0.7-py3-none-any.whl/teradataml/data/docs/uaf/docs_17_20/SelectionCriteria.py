def SelectionCriteria(data=None, data_filter_expr=None, var_count=None, 
                      constant=False, use_likelihood=False, **generic_arguments):
    """
    DESCRIPTION:
        The SelectionCriteria() function calculates metrics to help
        determine the users for an forecast modeling project.


    PARAMETERS:
        data:
            Required Argument.
            Specifies a single multivariate series or a TDAnalyticResult object
            created on the residual results from a previously run regression
            operation. A single multivariate series has the following fields:
                * First field is the original series value.
                * Second field is the calculated series value from the model.
                * Third field is the calculated residual, which is the original
                  value minus the calculated value.
            When TDAnalyticResult is used, make sure TDAnalyticResult is created without
            passing the "layer" argument.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        var_count:
            Required Argument.
            Specifies the total number of arguments present in the model.
            Types: int

        constant:
            Optional Argument.
            Specifies whether model has a constant. When set to False,
            model has no constant, otherwise has constant.
            Default Value: False
            Types: bool

        use_likelihood:
            Optional Argument.
            Specifies whether the selection criteria use residual sum squares
            (RSS) or log-likelihood. When set to False, indicates RSS, otherwise
            indicates log-likelihood.
            Note:
                * Applicable only when input is from the ArimaEstimate() function.
            Default Value: False
            Types: bool

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
        Instance of SelectionCriteria.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as SelectionCriteria_obj.<attribute_name>.
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
        load_example_data("uaf", ["blood2ageandweight"])

        # Create teradataml DataFrame object.
        df = DataFrame.from_table("blood2ageandweight")

        # Create teradataml TDSeries object.
        series_arimaestimate = TDSeries(data=df,
                                        id="PatientID",
                                        row_index="SeqNo",
                                        row_index_style="SEQUENCE",
                                        payload_field="Age",
                                        payload_content="REAL")

        # Function outputs a result set that contains the estimated
        # coefficients with accompanying per-coefficient statistical ratings.
        arima_estimate = ArimaEstimate(data1=series_arimaestimate,
                                       nonseasonal_model_order=[1,0,2],
                                       constant=True,
                                       algorithm='MLE',
                                       fit_percentage=70,
                                       coeff_stats=True,
                                       fit_metrics=True,
                                       residuals=True
                                       )

        # Example 1 : Calculate the metrics on the series created on the output
        #             of ArimaEstimate() function.

        # Create teradataml TDSeries object.
        selectioncriteria_series = TDSeries(data=arima_estimate.fitresiduals,
                                            id="PatientID",
                                            row_index="ROW_I",
                                            row_index_style= "SEQUENCE",
                                            payload_field=["ACTUAL_VALUE",  "CALC_VALUE","RESIDUAL"],
                                            payload_content="MULTIVAR_REAL")

        uaf_out=SelectionCriteria(data=selectioncriteria_series,
                                  var_count=4,
                                  constant=True,
                                  use_likelihood=False)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2 : Calculate the metrics on the the output of ArimaEstimate()
        #             function. Note that output of ArimaEstimate() is encapsulated
        #             in TDAnalyticResult while passing as input.

        # Create teradataml TDAnalyticResult object.
        art_SelectionCriteria = TDAnalyticResult(data=arima_estimate.result)

        uaf_out=SelectionCriteria(data=art_SelectionCriteria,var_count=4,
                                  constant=True,
                                  use_likelihood=True)

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    