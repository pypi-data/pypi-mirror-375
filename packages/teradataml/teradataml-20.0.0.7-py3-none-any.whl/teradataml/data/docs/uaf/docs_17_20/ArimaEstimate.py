def ArimaEstimate(data1=None, data1_filter_expr=None, data2=None, 
                  data2_filter_expr=None, nonseasonal_model_order=None,
                  seasonal_model_order=None, seasonal_period=None, 
                  lags_ar=None, lags_sar=None, lags_ma=None, lags_sma=None,
                  init=None, fixed=None, constant=False, algorithm=None,
                  max_iterations=100, coeff_stats=False, fit_percentage=100,
                  fit_metrics=False, residuals=False, 
                  input_fmt_input_mode=None, 
                  output_fmt_index_style="NUMERICAL_SEQUENCE", 
                  **generic_arguments):
    """
    DESCRIPTION:
        The ArimaEstimate() function estimates the coefficients corresponding to an
        ARIMA (AutoRegressive Integrated Moving Average) model, and to
        fit a series with an existing ARIMA model. The function can also
        provide the "goodness of fit" and the residuals of the fitting operation.
        The function generates model layer used as input for the ArimaValidate() 
        and ArimaForecast() functions. This function is for univariate series.

        The ArimaEstimate() function takes one or two inputs, the second input is optional.
        The first input is a time series. The second input references
        the model context. When only one input is passed in, the ArimaEstimate() 
        function operates in a coefficient estimate mode. When two inputs are passed in,
        ArimaEstimate() function operates in a model apply mode. When the second input
        is passed in, user must include an input format mode argument.
        
        User can use the "fit_percentage" argument to pass a portion of the data,
        such as 80%, to the ArimaEstimate() function. The ART produced
        includes the ARTVALDATA layer which contains the remaining 20%,
        and can be used with ArimaValidate() function for the validation exercise.
        
        The following functions are run after ArimaEstimate() function to determine
        if the residuals are zero mean, have no serial correlation or exhibit
        homoscedastic variance:
            * CumulPeriodogram
            * HoltWintersForecaster
            * SignifPeriodicities
            * SimpleExp
        
        The following procedure is an example of how to use ArimaEstimate() function:
            1. Run the ArimaEstimate() function to get the coefficients
               for the ARIMA model.
            2. [Optional] Run ArimaValidate() function to validate the
               'goodness of fit' of the ARIMA model, when "fit_percentage" argument value
               is not 100 in ArimaEstimate() function.
            3. Run the ArimaForecast() function with input from step 1
               or step 2 to forecast the future periods beyond the last
               observed period.
        Notes:
            The following arguments are ignored when using two input files:
                * algorithm
                * constant
                * fixed
                * init
                * lags_ar
                * lags_sar
                * lags_ma
                * lags_sma
                * nonseasonal_model_order
                * seasonal_model_order
                * seasonal_period
            However, "algorithm", "constant", and "nonseasonal_model_order" arguments
            must be included in the ArimaEstimate() function, as they are mandatory.


    PARAMETERS:
        data1:
            Required Argument.          
            Specifies the input time series whose payload content is 'REAL'.
            Types: TDSeries

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Optional Argument.
            Specifies the TDSeries or TDAnalyticResult object created
            over the output of ArimaEstimate() function.
            Notes:
                When the "data2" is passed, user must include
                "input_fmt_input_mode" argument with the following behavior:
                    * MATCH: If no matching identifiers are found, then an
                      empty dataframe is returned.
                    * MANY2ONE or ONE2ONE: If the "data1" input is an empty
                      time series, then the function returns an empty result 
                      dataframe. If the "data2" input is an empty series, 
                      then an error is returned from the function.
            Types: TDSeries, TDAnalyticResult

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        nonseasonal_model_order:
            Required Argument.
            Specifies the non-seasonal values for the model. A list 
            containing three integer values, where each value is greater
            than or equal to 0:
                * First value is 'p', the order of the non-seasonal
                  auto-regression (AR) component.
                * Second value is 'd', the order of the non-seasonal differences
                  between consecutive components.
                * Third value is 'q', the order of the non-seasonal
                  moving average (MA) component.
            Types: int, list of int

        seasonal_model_order:
            Optional Argument.
            Specifies the seasonal values for the model. A list 
            containing three integer values, where each value is greater
            than or equal to 0:
                * First value is 'P', the order of the seasonal
                  auto-regression (SAR) component.
                * Second value is 'D', the order of the seasonal differences between
                  consecutive components.
                * Third value is 'Q', the order of the seasonal moving
                  average (SMA) component.
            Types: int, list of int

        seasonal_period:
            Optional Argument.
            Specifies the number of periods per season.
            Types: int

        lags_ar:
            Optional Argument.
            Specifies the p-length-lag-list is the lag values for the non-seasonal
            auto-regression component. The position-sensitive list that specifies the lags
            to be associated with the non-seasonal auto-regressive (AR)
            regression terms. Default is length of "nonseasonal_model_order" ([1,2,3,...p]).
            Types: int, list of int

        lags_sar:
            Optional Argument.
            Specifies the P-length-lag-list is the seasonal auto-regression components.
            the position-sensitive list that specifies the lags 
            associated with the seasonal auto-regressive (SAR) terms.
            Default is length of "seasonal_model_order" ([1xS, 2xS, ...., PxS]). 
            Types: int, list of int

        lags_ma:
            Optional Argument.
            Specifies The q-length-lag-list is the values for the moving average
            component. The position-sensitive list that specifies the lags associated
            with the moving average (MA) terms. Default is length
            of "nonseasonal_model_order" ([1,2,3,...q]).
            Types: int, list of int

        lags_sma:
            Optional Argument.
            Specifies the Q-length-lag-list is the values for the seasonal
            moving average component. The position-sensitive list that specifies
            the lags associated with the seasonal moving average (SMA) terms. Default
            is length of "seasonal_model_order" ([1xS, 2xS, ..., PxS]). 
            Types: int, list of int

        init:
            Optional Argument.
            Specifies the position-sensitive list that specifies the 
            initial values to be associated with the 'p' non-seasonal
            AR regression coefficients, followed by the 'q'
            non-seasonal MA coefficients, the 'P' seasonal SAR
            regression coefficients and the 'Q' SMA coefficients.
            
            If an intercept is needed, one more value is added
            at the end to specify the intercept coefficient initial
            value, then the formula is as follows:
                p+q+P+Q+constant
            Types: int, list of int, float, list of float

        fixed:
            Optional Argument.
            Specifies the position-sensitive list that specifies the 
            fixed values to be associated with the 'p' non-seasonal
            AR regression coefficients, followed by the 'q'
            non-seasonal MA coefficients, the 'P' seasonal 
            SAR regression coefficients and the 'Q' SMA coefficients.
            
            If an intercept is needed, one more value is added
            at the end to specify the intercept coefficient initial
            value, then the formula is as follows:
                p+q+P+Q+constant
            Types: int, list of int, float, list of float

        constant:
            Optional Argument.
            Specifies whether to calculate an intercept. When set to False, function
            does not calculate the intercept, otherwise calculates intercept.
            Default Value: False
            Types: bool

        algorithm:
            Required Argument.
            Specifies the approach used to estimate the coefficients.
            Permitted Values:
                * OLE: Use the sum of ordinary least squares approach.
                  Then, "fixed" and "init" are disabled.
                * MLE: Use maximum likelihood approach.
                * CSS_MLE: Use the conditional sum-of-squares to 
                  determine a start value and then do maximum likelihood.
                * CSS:  Use conditional sum-of-squares approach.
            Types: str

        max_iterations:
            Optional Argument.
            Specifies the limit on the maximum number of iterations to 
            estimate the ARIMA argument.
            Notes:
                * Applicable only when "algorithm" is set to 'MLE' processing.
                * If not present, then default is 100 iterations.
            Default Value: 100
            Types: int

        coeff_stats:
            Optional Argument.
            Specifies whether to return coefficient statistical columns
            TSTAT_VALUE and TSTAT_PROB. When set to True, function
            returns the columns, otherwise not. 
            Default Value: False
            Types: bool

        fit_percentage:
            Optional Argument.
            Specifies the percentage of passed in sample points that
            are used for the model fitting and parameter estimation.
            Default Value: 100
            Types: int

        fit_metrics:
            Optional Argument.
            Specifies whether to generate the model metadata statistics.
            The generated result set can be retrieved using the attribute
            'fitmetadata' of the function output. When set to True,
            function generate the model metadata statistics,
            otherwise not.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies whether to generate the residuals data.
            The generated residuals result can be viewed using
            the 'fitresiduals' attribute on the function output.
            When set to False, function does not generate the residual
            data, otherwise generates it.
            Default Value: False
            Types: bool

        input_fmt_input_mode:
            Optional Argument.
            Specifies the input mode supported by the function.
            Note:
                The "input_fmt_input_mode" argument is supported, when both
                "data1" and "data2" are passed.
            Permitted Values: MANY2ONE, ONE2ONE, MATCH
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
                    creation or configuration argument. Argument is ignored,
                    if "output_table_name" is not specified.
                    Types: str


    RETURNS:
        Instance of ArimaEstimate.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as ArimaEstimate_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata - Available when "fit_metrics" is set to True, otherwise not.
            3. fitresiduals - Available when "residuals" is set to True, otherwise not.
            4. model
            5. valdata


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
        load_example_data("uaf", ["stock_data"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("stock_data")

        # Example 1 : Execute ArimaEstimate() function to estimate the coefficients
        #             and statistical ratings corresponding to an ARIMA model.
        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="data_set_id",
                                  row_index="seq_no",
                                  row_index_style="SEQUENCE",
                                  payload_field="magnitude",
                                  payload_content="REAL")

        # Execute ArimaEstimate function.
        uaf_out = ArimaEstimate(data1=data_series_df,
                                nonseasonal_model_order=[2,0,0],
                                constant=False,
                                algorithm="OLE",
                                coeff_stats=True,
                                fit_metrics=True,
                                residuals=True,
                                fit_percentage=80)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.fitmetadata)
        print(uaf_out.fitresiduals)
        print(uaf_out.model)
        print(uaf_out.valdata)

    """
    