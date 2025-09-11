def WhitesGeneral(data=None, data_filter_expr=None, variables_count=None,
                  significance_level=None, **generic_arguments):
    """
    DESCRIPTION:
        The WhitesGeneral() function checks for the presence of correlation
        among the residual terms after running a regression. The function
        determines if there exists any heteroscedastic variance in the
        residuals of regression tests.
        The output specifies the following:
            * 'ACCEPT' means the null hypothesis is accepted,
              and there is homoscedasticity variance evident.
            * 'REJECT' means the null hypothesis is rejected,
              and there is evidence of heteroscedasticity.

       The Whites-General test does not require reordering like
       the Goldfeld-Quandt test, and is not sensitive to the normal
       distribution assumption like the Breusch-Pagan-Godfrey test.

       The following procedure is an example of how to use WhitesGeneral() function:
            1. Use the function MultivarRegr() for regression testing.
            2. Use WhitesGeneral() on the residual output from MultivarRegr().
            3. Determine if the variance is homoscedastic or heteroscedastic
               from the WhitesGeneral() result.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the residual multivariate series or TDAnalyticResult
            object over the residual output of UAF regression functions.
            Input payload content is 'MULTIVAR_REAL'.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        variables_count:
            Required Argument.
            Specifies the number of explanatory variables used
            in the auxiliary regression in the payload of the
            original series.
            Types: int

        significance_level:
            Required Argument.
            Specifies the significance level used for the test.
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
        Instance of WhitesGeneral.
        Output teradataml DataFrames can be accessed using attribute
        references, such as WhitesGeneral_obj.<attribute_name>.
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
        load_example_data("uaf", ["house_values"])

        # Create teradataml DataFrame object.
        df = DataFrame.from_table("house_values")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=df,
                                  id="cityid",
                                  row_index="TD_TIMECODE",
                                  payload_field=["house_val","salary","mortgage"],
                                  payload_content="MULTIVAR_REAL")

        # Execute multivariate regression function to identify the degree of
        # linearity the explanatory variable and multiple response variables.
        # Generate the model statistics and residual data as well.
        multivar_out = MultivarRegr(data=data_series_df,
                                    variables_count=3,
                                    weights=False,
                                    formula="Y = B0 + B1*X1 + B2*X2",
                                    algorithm='QR',
                                    coeff_stats=True,
                                    model_stats=True,
                                    residuals=True)

        # Example 1: Perform Whites-General test on TDAnalyticResult object
        #            over the result attribute of the "multivar_out" as input.
        # Create teradataml TDAnalyticResult object over the 'result'
        # attribute of the 'multivar_out'.
        data_art_df = TDAnalyticResult(data=multivar_out.result)

        uaf_out = WhitesGeneral(data=data_art_df,
                                variables_count=3,
                                significance_level=0.05)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Perform Whites-General test on TDSeries
        #            object over the 'fitresiduals' attribute
        #            of the 'multivar_out'.
        # Create teradataml TDSeries object over the 'fitresiduals' attribute
        # of the 'multivar_out'.
        data_series_df = TDSeries(data=multivar_out.fitresiduals,
                                  id="cityid",
                                  row_index="ROW_I",
                                  row_index_style="SEQUENCE",
                                  payload_field=["ACTUAL_VALUE","CALC_VALUE","RESIDUAL"],
                                  payload_content="MULTIVAR_REAL")

        uaf_out1 = WhitesGeneral(data=data_series_df, 
                                 variables_count=3, 
                                 significance_level=0.05)

        # Print the result DataFrame.
        print(uaf_out1.result)

    """
