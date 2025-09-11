def AutoArima(data=None, data_filter_expr=None, max_pq_nonseasonal=[5,5],
              max_pq_seasonal=[2,2], start_pq_nonseasonal=[0,0],
              start_pq_seasonal=[0,0], d=-1, ds=-1, max_d=2, max_ds=1,
              period=1, stationary=False, seasonal=True, constant=True,
              algorithm="MLE", fit_percentage=100,
              infor_criteria="AIC", stepwise=False, nmodels=94,
              max_iterations=100, coeff_stats=False,
              fit_metrics=False, residuals=False, arma_roots=False,
              test_nonseasonal="ADF", test_seasonal="OCSB",
              output_fmt_index_style="NUMERICAL_SEQUENCE", 
              **generic_arguments):
    """
    DESCRIPTION:
        AutoArima() function searches the possible models within the order
        constrains in the function parameters, and returns the best ARIMA
        model based on the criterion provided by the "infor_criteria"
        parameter. AutoArima() function creates a six-layered ART table.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the time series whose value can be REAL.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        max_pq_nonseasonal:
            Optional Argument.
            Specifies the (p,q) order of the maximum autoregression (AR) and
            moving average (MA) parameters.
            Default Value: [5,5]
            Types: list

        max_pq_seasonal:
            Optional Argument.
            Specifies the (P,Q) order of the max seasonal AR and MA
            parameters.
            Default Value: [2,2]
            Types: list

        start_pq_nonseasonal:
            Optional Argument.
            Specifies the start value of (p,q). Only used when "stepwise"=1.
            Default Value: [0,0]
            Types: list

        start_pq_seasonal:
            Optional Argument.
            Specifies the start value of seasonal (P,Q). Only used when
            "stepwise"=1.
            Default Value: [0,0]
            Types: list

        d:
            Optional Argument.
            Specifies the order of first-differencing.
            Default Value: -1 (auto search d).
            Types: int

        ds:
            Optional Argument.
            Specifies the order of seasonal-differencing.
            Default Value: -1 (auto search Ds).
            Types: int

        max_d:
            Optional Argument.
            Specifies the maximum number of non-seasonal differences.
            Default Value: 2
            Types: int

        max_ds:
            Optional Argument.
            Specifies the maximum number of seasonal differences.
            Default Value: 1
            Types: int

        period:
            Optional Argument.
            Specifies the number of periods per season. For non-seasonal
            data, period is 1.
            Default Value: 1
            Types: int

        stationary:
            Optional Argument.
            Specifies whether to restrict search to stationary models.
            If True, the  function restricts search to stationary models.
            Default Value: False
            Types: bool

        seasonal:
            Optional Argument.
            Specifies whether to restrict search to non-seasonal models.
            If False, then the function restricts search to non-seasonal
            models.
            Default Value: True
            Types: bool

        constant:
            Optional Argument.
            Specifies whether an indicator that AutoArima() function includes
            an intercept. If True, means CONSTANT/intercept
            should be included. If False, means
            CONSTANT/intercept should not be included.
            Default Value: True
            Types: bool

        algorithm:
            Optional Argument.
            Specifies the approach used by TD_AUTOARIMA to estimate the
            coefficients.
            Permitted Values:
                * MLE: Use maximum likelihood approach.
                * CSS_MLE: Use the conditional sum-of-squares to determine a
                            start value and then do maximum likelihood.
                * CSS: Use the conditional sum-of squares approach.
            Default Value: MLE
            Types: str

        fit_percentage:
            Optional Argument.
            Specifies the percentage of passed-in sample points used for the
            model fitting (parameter estimation).
            Default Value: 100
            Types: int

        infor_criteria:
            Optional Argument.
            Specifies the information criterion to be used in model selection.
            Permitted Values: AIC, AICC, BIC
            Default Value: AIC
            Types: str

        stepwise:
            Optional Argument.
            Specifies whether the function does stepwise selection or not.
            If True, then the function does stepwise selection otherwise the
            function selects all models.
            Default Value: False
            Types: bool

        nmodels:
            Optional Argument.
            Specifies the maximum number of models considered in the stepwise
            search.
            Default Value: 94
            Types: int

        max_iterations:
            Optional Argument.
            Specifies the maximum number of iterations that can be employed
            to non-linear optimization procedure.
            Default Value: 100
            Types: int

        coeff_stats:
            Optional Argument.
            Specifies the indicator to return coefficient statistical columns
            TSTAT_VALUE and TSTAT_PROB. If True, means return
            the columns otherwise do not return the
            columns.
            Default Value: False
            Types: bool

        fit_metrics:
            Optional Argument.
            Specifies the indicator to generate the secondary result set that
            contains the model metadata statistics. If True,
            means generate the secondary result set otherwise
            do not generate the secondary result set.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies the indicator to generate the tertiary result set that
            contains the model residuals. If True, means
            generate the tertiary result set, otherwise
            do not generate the tertiary result set.
            Default Value: False
            Types: bool

        arma_roots:
            Optional Argument.
            Specifies the indicator to generate the senary result set that
            contains the inverse AR and MA roots of result best 
            model that AutoArima() selected (the model in the
            primary output layer). There should be no inverse 
            roots showing outside of the unit circle. If True,
            means generate result set otherwise do not
            generate a result set.
            Default Value: False
            Types: bool

        test_nonseasonal:
            Optional Argument.
            Specifies the nonseasonal unit root test used to choose
            differencing number "d".
            AutoArima() function only uses ADF test for
            nonseasonal unit root test.
            Permitted Values: ADF
            Default Value: ADF
            Types: str

        test_seasonal:
            Optional Argument.
            Specifies the seasonal unit root test used to choose differencing 
            number "d". AutoArima() function only uses OCSB test for
            seasonal unit root test.
            Permitted Values: OCSB
            Default Value: OCSB
            Types: str

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
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
        Instance of AutoArima.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as AutoArima_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata
            3. fitresiduals
            4. model
            5. icandorder
            6. armaroots


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

        # Import function AutoArima.
        from teradataml import AutoArima

        # Load the example data.
        load_example_data("uaf", ["blood2ageandweight", "covid_confirm_sd"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("blood2ageandweight")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="PatientID",
                                  row_index="SeqNo",
                                  row_index_style="SEQUENCE",
                                  payload_field="BloodFat",
                                  payload_content="REAL")

        # Example 1: Execute AutoArima with start_pq_nonseasonal as [1,1], algorithm = "MLE" and
        #            fit_percentage=80 to find the best ARIMA model.
        uaf_out = AutoArima(data=data_series_df,
                            start_pq_nonseasonal=[1, 1],
                            seasonal=False,
                            constant=True,
                            algorithm="MLE",
                            fit_percentage=80,
                            stepwise=True,
                            nmodels=7,
                            fit_metrics=True,
                            residuals=True)

        # Print the result DataFrames.
        print(uaf_out.result)

        # Example 2: Execute AutoArima with max_pq_nonseasonal as [3,3], arma_roots = True,
        #            to find thhe best ARIMA model.
        covid_confirm_sd = DataFrame("covid_confirm_sd")
        data_series_df = TDSeries(data=covid_confirm_sd,
                                  id="city",
                                  row_index="row_axis",
                                  row_index_style="SEQUENCE",
                                  payload_field="cnumber",
                                  payload_content="REAL")

        uaf_out = AutoArima(data=data_series_df,
                            max_pq_nonseasonal=[3, 3],
                            stationary=False,
                            stepwise=False,
                            arma_roots=True,
                            residuals=True)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.fitresiduals)
        print(uaf_out.model)
        print(uaf_out.icandorder)
        print(uaf_out.armaroots)
    
    """
    