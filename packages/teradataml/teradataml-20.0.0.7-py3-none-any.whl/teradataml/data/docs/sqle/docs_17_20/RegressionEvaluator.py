def RegressionEvaluator(data=None, observation_column=None,
                        prediction_column=None, metrics=None,
                        independent_features_num=None, freedom_degrees=None):
    """
    DESCRIPTION:
        The RegressionEvaluator() function computes metrics to evaluate and compare
        multiple models and summarizes how close predictions are to their expected
        values.

        Notes:
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
            * For information about PTCs, see Teradata Vantage™ - Analytics Database
              International Character Set Support.
            * This function does not support KanjiSJIS or Graphic data types.
        
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame
            
        observation_column:
            Required Argument.
            Specifies the column name in "data" containing observation labels.
            Types: str
            
        prediction_column:
            Required Argument.
            Specifies the column name in "data" containing predicted labels.
            Types: str
            
        metrics:
            Optional Argument.
            Specifies the list of evaluation metrics. The function returns
            the following metrics if the list is not provided:
                MAE:
                    Mean absolute error (MAE) is the arithmetic average of the
                    absolute errors between observed values and predicted values.
                MSE:
                    Mean squared error (MSE) is the average of the squares of
                    the errors between observed values and predicted values.
                MSLE:
                    Mean Square Log Error (MSLE) is the relative difference
                    between the log-transformed observed values and predicted
                    values.
                MAPE:
                    Mean Absolute Percentage Error (MAPE) is the mean or
                    average of the absolute percentage errors of forecasts.
                MPE:
                    Mean percentage error (MPE) is the computed average
                    of percentage errors by which predicted values differ from
                    observed values.
                RMSE:
                    Root means squared error (MSE) is the square root of the
                    average of the squares of the errors between observed
                    values and predicted values.
                RMSLE:
                    Root means Square Log Error (MSLE) is the square root
                    of the relative difference between the log-transformed
                    observed values and predicted values.
                R2:
                    R Squared (R2) is the proportion of the variation in the
                    dependent variable that is predictable from the independent
                    variable(s).
                AR2:
                    Adjusted R-squared (AR2) is a modified version of R-squared
                    that has been adjusted for the independent variable(s) in
                    the model.
                EV:
                    Explained variation (EV) measures the proportion to which
                    a mathematical model accounts for the variation (dispersion)
                    of a given data set.
                ME:
                    Max-Error (ME) is the worst-case error between observed
                    values and predicted values.
                MPD:
                    Mean Poisson Deviance (MPD) is equivalent to Tweedie
                    Deviances when the power parameter value is 1.
                MGD:
                    Mean Gamma Deviance (MGD) is equivalent to Tweedie
                    Deviances when the power parameter value is 2.
                FSTAT:
                    F-statistics (FSTAT) conducts an F-test. An F-test
                    is any statistical test in which the test statistic has an
                    F-distribution under the null hypothesis.
                    * F_score:
                        F_score value from the F-test.
                    * F_Critcialvalue:
                        F critical value from the F-test. (alpha, df1, df2,
                        UPPER_TAILED), alpha = 95%
                    * p_value:
                        Probability value associated with the F_score value
                        (F_score, df1, df2, UPPER_TAILED)
                    * F_conclusion:
                        F-test result, either 'reject null hypothesis' or
                        'fail to reject null hypothesis'. If F_score >
                        F_Critcialvalue, then 'reject null hypothesis'
                        Else 'fail to reject null hypothesis'
            Types: str OR list of strs
            
        independent_features_num:
            Optional Argument.
            Specifies the number of independent variables in the model.
            Required with Adjusted R Squared metric, else ignored.
            Types: int
            
        freedom_degrees:
            Optional Argument.
            Specifies the numerator degrees of freedom (df1) and denominator
            degrees of freedom (df2). Required with fstat metric, else ignored.
            Types: int OR list of ints
            
        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept. Below
            are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the
                    function in a table or not. When set to True,
                    results are persisted in a table; otherwise,
                    results are garbage collected at the end of the
                    session.
                    Default Value: False
                    Types: bool
                    
                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the
                    function in a volatile table or not. When set to
                    True, results are stored in a volatile table,
                    otherwise not.
                    Default Value: False
                    Types: bool
                     
            Function allows the user to partition, hash, order or local
            order the input data. These generic arguments are available
            for each argument that accepts teradataml DataFrame as
            input and can be accessed as:
                * "<input_data_arg_name>_partition_column" accepts str or
                    list of str (Strings)
                * "<input_data_arg_name>_hash_column" accepts str or list
                    of str (Strings)
                * "<input_data_arg_name>_order_column" accepts str or list
                    of str (Strings)
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if
                the underlying SQL Engine function supports, else an
                exception is raised.
        
    RETURNS:
        Instance of RegressionEvaluator.
        Output teradataml DataFrames can be accessed using attribute
        references, such as RegressionEvaluatorObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result
        
        
    RAISES:
        TeradataMlException, TypeError, ValueError
        
        
    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        from teradataml import valib

        # Set the 'configure.val_install_location' variable.
        from teradataml import configure
        configure.val_install_location = "val"
            
        # Create required teradataml DataFrame.
        # Load the example data.
        load_example_data("teradataml", "titanic")
            
        # Create teradataml DataFrame objects.
        titanic = DataFrame.from_table("titanic")

        # First generate linear regression model using LinReg() function from 'valib'.
        lin_reg_obj = valib.LinReg(data=titanic,
                                   columns=["age", "survived", "pclass"],
                                   response_column="fare")

        # Score the data using the linear regression model generated above.
        obj = valib.LinRegPredict(data=titanic,
                                  model=lin_reg_obj.model,
                                  accumulate = "fare",
                                  response_column="fare_prediction")
            
        # Check the list of available analytic functions.
        display_analytic_functions()
            
        # Example 1 : Compute 'RMSE', 'R2' and 'FSTAT' metrics to evaluate
        #             the model.
        RegressionEvaluator_out = RegressionEvaluator(data = obj.result,
                                                      observation_column = "fare",
                                                      prediction_column = "fare_prediction",
                                                      freedom_degrees = [1, 2],
                                                      independent_features_num = 2,
                                                      metrics = ['RMSE','R2','FSTAT'])

        # Print the result DataFrame.
        print(RegressionEvaluator_out.result)
        
    """
