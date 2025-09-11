def BreuschGodfrey(data=None, data_filter_expr=None, residual_max_lags=None,
                   explanatory_count=None, significance_level=0.05,
                   **generic_arguments):
    """
    DESCRIPTION:
        The BreuschGodfrey() function checks for the presence of serial correlation
        among the residual and error terms after running a regression
        associated with a fitted model. With respect to regression models,
        it is expected that there is no serial correlation among the error terms.

        The following procedure is an example of how to use BreuschGodfrey:
            * Use LinearRegr() for regression testing.
            * Use BreuschGodfrey() on the result from LinearRegr() to
              compute the test statistics and determine if there is serial correlation.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the residual multivariate series
            or TDAnalyticResult object on the output generated
            by the UAF function.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        residual_max_lags:
            Required Argument.
            Specifies the maximum lag number for the
            residuals used in the auxiliary regression. It also
            determines degrees of freedom associated with the test.
            Types: int

        explanatory_count:
            Required Argument.
            Specifies the number of explanatory variables that are present
            in the original regression plus '1' if a constant is
            present.
            Example: If the "formula" parameter used in LinearRegr() is 'Y = B0 + B1*X1',
            it has "explanatory_count" of '2', '1' for 'X1' and '1' for the
            constant 'B0'.
            Types: int

        significance_level:
            Optional Argument.
            Specifies the desired significance level for the test.
            Default Value: 0.05
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
        Instance of BreuschGodfrey.
        Output teradataml DataFrames can be accessed using attribute
        references, such as BreuschGodfrey_obj.<attribute_name>.
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
        data = DataFrame.from_table("house_values")

        # Execute LinearRegr() function to fit house_values data to
        # the curve mentioned in the "formula" for cityid 33. It returns
        # a result containing solved coefficients, model statistics,
        # and residuals statistics.
        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="cityid",
                                  row_index="TD_TIMECODE",
                                  row_index_style="TIMECODE",
                                  payload_field=["salary","house_val"],
                                  payload_content="MULTIVAR_REAL")

        filter_expr = data_series_df.cityid==33
        linear_regr_result = LinearRegr(data=data_series_df,
                                        data_filter_expr=filter_expr,
                                        formula = "Y = B0 + B1*X1",
                                        weights=False,
                                        algorithm='QR',
                                        coeff_stats=True,
                                        variables_count=2,
                                        model_stats=True,
                                        residuals=True)

        # Example 1: Compute the serial correlation among the residual
        #            and error terms. Input is teradataml TDAnalyticResult
        #            object over the output generated by running a linear
        #            regression associated with a fitted model.

        # Create teradataml TDAnalyticResult object.
        data_art_df =  TDAnalyticResult(data=linear_regr_result.result)
        uaf_out = BreuschGodfrey(data=data_art_df,
                                 explanatory_count=2,
                                 residual_max_lags=1,
                                 significance_level=.01)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Compute the serial correlation among the residual
        #            and error terms. Input is teradataml TDSeries
        #            object over the "fitresiduals" dataframe generated
        #            by running a linear regression associated
        #            with a fitted model.

        data_series_bg = TDSeries(data=linear_regr_result.fitresiduals,
                                  id="cityid",
                                  row_index="ROW_I",
                                  row_index_style= "SEQUENCE",
                                  payload_field=["RESIDUAL","ACTUAL_VALUE","CALC_VALUE"],
                                  payload_content="MULTIVAR_REAL")

        uaf_out = BreuschGodfrey(data=data_series_bg,
                                 explanatory_count=2,
                                 residual_max_lags=1,
                                 significance_level=.01)

        # Print the result DataFrame.
        print(uaf_out.result)

    """
