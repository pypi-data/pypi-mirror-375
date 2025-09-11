def ArimaXEstimate(data1=None, data1_filter_expr=None, data2=None, 
                   data2_filter_expr=None, nonseasonal_model_order=None, 
                   seasonal_model_order=None, seasonal_period=None, 
                   xreg=None, init=None, fixed=None, constant=False, 
                   algorithm=None, max_iterations=100, coeff_stats=False, 
                   fit_percentage=100, fit_metrics=False, residuals=False, 
                   input_fmt_input_mode=None, 
                   output_fmt_index_style="NUMERICAL_SEQUENCE", 
                   **generic_arguments):
    """
    DESCRIPTION:
        ArimaXEstimate() function extends the capability of ArimaEstimate() by
        allowing to include external regressors or covariates to an ARIMA model.
        The external regressors are specified in TDSeries payload specification
        after targeting the univariate series.
        The following procedure is an example of how to use:
            1. Run the ArimaXEstimate() function to estimate the coefficients
               of ARIMAX model.
            2. Run the ArimaXForecast() function with the estimated coefficient
               as first input, and the regular input time series table (TDSeries) that
               contains the future value of exogenous variables as second input.

    PARAMETERS:
        data1:
            Required Argument.
            Specifies the input series.
            Types: TDSeries

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Optional Argument.
            Specifies a logical univariate
            series and an art table from previous 
            ArimaXEstimate() call. This allows the user to fit
            the interested series in TDSeries by existing model
            in TDAnalyticResult. In this case, the function's primary
            result set will be based on the existing model's 
            coefficients.
            Types: TDSeries, TDAnalyticResult

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        nonseasonal_model_order:
            Required Argument.
            Specifies the non-seasonal values for the model.
            A list containing three integer values, which are each greater than or equal to 0:
                • p-value: The order of the non-seasonal autoregression
                (AR) component.
                • d-value: The order of the non-seasonal differences
                between consecutive components.
                • q-value: The order of the non-seasonal moving
                average (MA) component.
            Types: int, list of int

        seasonal_model_order:
            Required Argument.
            Specifies the seasonal values for the model.
            A list containing three integer values, which are each greater than or equal to 0:
                • P-value: The order of the seasonal auto-regression
                (SAR) component.
                • D-value: The order of the seasonal differences
                between consecutive components.
                • Q-value: The order of the seasonal moving average
                (SMA) component.
            Types: int, list of int

        seasonal_period:
            Optional Argument.
            Specifies the number of periods per season.
            Types: int

        xreg:
            Required Argument.
            Specifies the number of covariates in external regressors.
            Note:
                * If value is 0, then it suggests to use ArimaEstimate().
                  The input number should match with the number
                  of (payload-1). Otherwise, an error occurs with
                  the message “Unexpected XREG input.”
                * Maximum number for this argument is 10.
            Types: int

        init:
            Optional Argument.
            Specifies the position-sensitive list that specifies the initial
            values to be associated with the non-seasonal AR
            regression coefficients, followed by the non-seasonal
            MA coefficients, the seasonal SAR regression
            coefficients and the SMA coefficients. The formula is
            as follows: 'p+q+P+Q+CONSTANT-length-init-list'
            Types: int, list of int, float, list of float

        fixed:
            Optional Argument.
            Specifies the position-sensitive list that contains the
            fixed values to be associated with the non-seasonal
            AR regression coefficients, followed by the nonseasonal
            MA coefficients, the SAR coefficients and
            the SMA coefficients.
            If an intercept is needed, one more value is added at
            the end to specify the intercept coefficient initial value.
            The formula is as follows: 'p+q+P+Q+CONSTANT-length-fixed-list'
            Types: int, list of int, float, list of float

        constant:
            Optional Argument.
            Specifies the indicator for the ArimaXEstimate() function to
            calculate an intercept. When set to True, it indicates intercept
            should be calculated otherwise it indicates no
            intercept should be calculated.
            Default Value: False
            Types: bool

        algorithm:
            Required Argument.
            Specifies the method to estimate the coefficients.
            Permitted Values: OLE, MLE, MLE_CSS, CSS
            Types: str

        max_iterations:
            Optional Argument.
            Specifies the limit on the maximum number of
            iterations that can be employed to estimate the
            ARIMA parameters. Only relevant for "algorithm" value 'MLE'
            processing.
            Default Value: 100
            Types: int

        coeff_stats:
            Optional Argument.
            Specifies the flag indicating whether to return coefficient
            statistical columns STD_ERROR, TSTAT_VALUE and
            TSTAT_PROB. When set to True, function returns the columns,
            otherwise does not return the columns.
            Default Value: False
            Types: bool

        fit_percentage:
            Optional Argument.
            Specifies the percentage of passed-in sample points
            that are used for the model fitting and parameter estimation.
            Default Value: 100
            Types: int

        fit_metrics:
            Optional Argument.
            Specifies the indicator to generate the secondary result
            set that contains the model metadata statistics.
            When set to True, the function generates the secondary result set
            otherwise does not generate the secondary result set.
            The generated result set is retrieved by issuing the
            ExtractResults function on the analytical result
            table containing the results.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies the indicator to generate the tertiary result set
            that contains the model residuals. When set to True, function
            generates the tertiary result set otherwise, does
            not generate the tertiary result set.
            Default Value: False
            Types: bool

        input_fmt_input_mode:
            Required Argument.
            Specifies the input mode supported by the function.
            Permitted Values: MANY2ONE, ONE2ONE, MATCH
            Types: str

        output_fmt_index_style:
            Optional Argument.
            Specifies the "index_style" of the output format.
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
        Instance of ArimaXEstimate.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as ArimaXEstimate_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata
            3. fitresiduals
            4. model
            5. valdata


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage, before importing the
        #        function in user space.
        #     2. User can import the function, if it is available on
        #        Vantage user is connected to.
        #     3. To check the list of UAF analytic functions available
        #        on Vantage user connected to, use
        #        "display_analytic_functions()".

        # Check the list of available UAF analytic functions.
        display_analytic_functions(type="UAF")

        # Import function ArimaXEstimate.
        from teradataml import ArimaXEstimate

        # Load the example data.
        load_example_data("uaf", "blood2ageandweight")

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("blood2ageandweight")

        # Create teradataml TDSeries objects.
        data1_series_df = TDSeries(data=data1,
                                   id="PatientID",
                                   row_index="SeqNo",
                                   row_index_style="SEQUENCE",
                                   payload_field=["BloodFat", "Age"],
                                   payload_content="MULTIVAR_REAL")


        # Example 1: Execute ArimaXEstimate with single input.
        uaf_out = ArimaXEstimate(data1=data1_series_df,
                                 nonseasonal_model_order=[2,0,1],
                                 xreg=True,
                                 fit_metrics=True,
                                 residuals=True,
                                 constant=True
                                 algorithm=MLE,
                                 fit_percentage=80
                                 )

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.fitmetadata)
        print(uaf_out.fitresiduals)
        print(uaf_out.model)
        print(uaf_out.valdata)
    
    """
    