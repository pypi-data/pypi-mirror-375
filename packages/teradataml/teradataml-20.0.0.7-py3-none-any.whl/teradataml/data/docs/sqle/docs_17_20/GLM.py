def GLM(formula=None, data=None, input_columns=None, response_column=None, family="GAUSSIAN",
        iter_max=300, batch_size=10, lambda1=0.02, alpha=0.15,
        iter_num_no_change=50, tolerance=0.001, intercept=True, class_weights="0:1.0, 1:1.0",
        learning_rate=None, initial_eta=0.05, decay_rate=0.25, decay_steps=5, momentum=0.0,
        nesterov=True, local_sgd_iterations=0, stepwise_direction=None, max_steps_num=5,
        initial_stepwise_columns=None, attribute_data=None, parameter_data=None, iteration_mode="BATCH",
        partition_column=None, **generic_arguments):
    """
    DESCRIPTION:
        The generalized linear model (GLM) function performs regression and classification
        analysis on data sets, where the response follows an exponential family distribution
        and supports the following models:
            * Regression (GAUSSIAN family): The loss function is squared error.
            * Binary Classification (BINOMIAL family): The loss function is logistic and
                                                       implements logistic regression.
                                                       The only response values are 0 or 1.

        The function uses the Minibatch Stochastic Gradient Descent (SGD) algorithm that is highly
        scalable for large datasets. The algorithm estimates the gradient of loss in minibatches,
        which is defined by the "batch_size" argument and updates the model with a learning rate using
        the "learning_rate" argument.

        The function also supports the following approaches:
            * L1, L2, and Elastic Net Regularization for shrinking model parameters.
            * Accelerated learning using Momentum and Nesterov approaches.

        The function uses a combination of "iter_num_no_change" and "tolerance" arguments
        to define the convergence criterion and runs multiple iterations (up to the specified
        value in the "iter_max" argument) until the algorithm meets the criterion.

        The function also supports LocalSGD, a variant of SGD, that uses "local_sgd_iterations"
        on each AMP to run multiple batch iterations locally followed by a global iteration.

        The weights from all mappers are aggregated in a reduce phase and are used to compute
        the gradient and loss in the next iteration. LocalSGD lowers communication costs and
        can result in faster learning and convergence in fewer iterations, especially when there
        is a large cluster size and many features.

        Due to gradient-based learning, the function is highly-sensitive to feature scaling.
        Before using the features in the function, you must standardize the Input features
        using ScaleFit() and ScaleTransform() functions.

        The function only accepts numeric features. Therefore, before training, you must convert
        the categorical features to numeric values.

        The function skips the rows with missing (null) values during training.

        The function output is a trained GLM model that is used as an input to the TDGLMPredict()
        function. The model also contains model statistics of MSE, Loglikelihood, AIC, and BIC.
        You can use RegressionEvaluator(), ClassificationEvaluator(), and ROC() functions to perform
        model evaluation as a post-processing step.


    PARAMETERS:
        formula:
            Required Argument when "input_columns" and "response_column" are not provided,
            optional otherwise.
            Specifies a string consisting of "formula". Specifies the model to be fitted.
            Only basic formula of the "col1 ~ col2 + col3 +..." form are
            supported and all variables must be from the same teradataml
            DataFrame object.
            Notes:
                * The function only accepts numeric features. User must convert the categorical
                  features to numeric values, before passing to the formula.
                * In case, categorical features are passed to formula, those are ignored, and
                  only numeric features are considered.
                * Provide either "formula" argument or "input_columns" and "response_column" arguments.
            Types: str

        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        input_columns:
            Required Argument when "formula" is not provided, optional otherwise.
            Specifies the name(s) of the column(s) in "data" to be used for
            training the model (predictors, features or independent variables).
            Note:
                * Provide either "formula" argument or "input_columns" and "response_column" arguments.
            Types: str OR list of Strings (str)

        response_column:
            Required Argument when "formula" is not provided, optional otherwise.
            Specifies the name of the column that contains the class label for
            classification or target value (dependent variable) for regression.
            Note:
                * Provide either "formula" argument or "input_columns" and "response_column" arguments.
            Types: str

        family:
            Optional Argument.
            Specifies the distribution exponential family.
            Permitted Values: BINOMIAL, GAUSSIAN
            Default Value: GAUSSIAN
            Types: str

        iter_max:
            Optional Argument.
            Specifies the maximum number of iterations over the training data
            batches. If the batch size is 0, "iter_max" equals the number of
            epochs (an epoch is a single pass over entire training data). If
            there are 1000 rows in an AMP, and batch size is 10, then 100
            iterations will result into one epoch and 500 iterations will result
            into 5 epochs over this AMP's data. Because it is not guaranteed
            that the data will be equally distributed on all AMPs, this may
            result into different number of epochs for other AMPs.
            Note:
                * It must be a positive value less than 10,000,000.
            Default Value: 300
            Types: int

        batch_size:
            Optional Argument.
            Specifies the number of observations (training samples) to be parsed
            in one mini-batch. The value '0' indicates no mini-batches, the entire
            dataset is processed in each iteration, and the algorithm becomes Gradient
            Descent. A value higher than the number of rows on any AMP will also default
            to Gradient Descent.
            Note:
                * It must be a non-negative integer value.
            Default Value: 10
            Types: int

        lambda1:
            Optional Argument.
            Specifies the amount of regularization to be added. The higher the
            value, the stronger the regularization. It is also used to compute
            the learning rate when the "learning_rate" is set to 'OPTIMAL'.
            A value '0' means no regularization.
            Note:
                * It must be a non-negative float value.
            Default Value: 0.02
            Types: float OR int

        alpha:
            Optional Argument.
            Specifies the Elasticnet parameter for penalty computation. It only
            becomes effective when "lambda1" greater than 0. The value represents
            the contribution ratio of L1 in the penalty. A value '1.0' indicates
            L1 (LASSO) only, a value '0' indicates L2 (Ridge) only, and a value
            in between is a combination of L1 and L2. Default value is 0.15.
            Note:
                * It must be a float value between 0 and 1.
            Default Value: 0.15(15% L1, 85% L2)
            Types: float OR int

        iter_num_no_change:
            Optional Argument.
            Specifies the number of iterations (batches) with no improvement in
            loss (including the tolerance) to stop training (early stopping).
            A value of 0 indicates no early stopping and the algorithm will
            continue till "iter_max" iterations are reached.
            Note:
                * It must be a non-negative integer value.
            Default Value: 50
            Types: int

        tolerance:
            Optional Argument.
            Specifies the stopping criteria in terms of loss function improvement.
            Training stops the following condition is met:
            loss > best_loss - "tolerance" for "iter_num_no_change" times.
            Notes:
                * Only applicable when "iter_num_no_change" greater than 0.
                * It must be a non-negative value.
            Default Value: 0.001
            Types: float OR int

        intercept:
            Optional Argument.
            Specifies whether to estimate intercept or not based on
            whether "data" is already centered or not.
            Default Value: True
            Types: bool

        class_weights:
            Optional Argument.
            Specifies the weights associated with classes. If the weight of a class is omitted,
            it is assumed to be 1.0.
            Note:
                * Only applicable for 'BINOMIAL' family. The format is '0:weight,1:weight'.
                  For example, '0:1.0,1:0.5' will give twice the weight to each observation
                  in class 0.
            Default Value: "0:1.0, 1:1.0"
            Types: str

        learning_rate:
            Optional Argument.
            Specifies the learning rate algorithm for SGD iterations.
            Permitted Values: CONSTANT, OPTIMAL, INVTIME, ADAPTIVE
            Default Value:
                * 'INVTIME' for 'GAUSSIAN' family , and
                * 'OPTIMAL' for 'BINOMIAL' family.
            Types: str

        initial_eta:
            Optional Argument.
            Specifies the initial value of eta for the learning rate. When
            the "learning_rate" is 'CONSTANT', this value is applicable for
            all iterations.
            Default Value: 0.05
            Types: float OR int

        decay_rate:
            Optional Argument.
            Specifies the decay rate for the learning rate.
            Note:
                * Only applicable for 'INVTIME' and 'ADAPTIVE' learning rates.
            Default Value: 0.25
            Types: float OR int

        decay_steps:
            Optional Argument.
            Specifies the decay steps (number of iterations) for the 'ADAPTIVE'
            learning rate. The learning rate changes by decay rate after the
            specified number of iterations are completed.
            Default Value: 5
            Types: int

        momentum:
            Optional Argument.
            Specifies the value to use for the momentum learning rate optimizer.
            A larger value indicates a higher momentum contribution. A value of 0
            means the momentum optimizer is disabled. For a good momentum contribution,
            a value between 0.6 and 0.95 is recommended.
            Note:
                * It must be a non-negative float value between 0 and 1.
            Default Value: 0.0
            Types: float OR int

        nesterov:
            Optional Argument.
            Specifies whether to apply Nesterov optimization to the momentum optimizer 
            or not.
            Note:
                * Only applicable when "momentum" greater than 0
            Default Value: True
            Types: bool

        local_sgd_iterations:
            Optional Argument.
            Specifies the number of local iterations to be used for Local SGD
            algorithm. A value of 0 implies Local SGD is disabled. A value higher
            than 0 enables Local SGD and that many local iterations are performed
            before updating the weights for the global model. With Local SGD algorithm,
            recommended values for arguments are as follows:
                * local_sgd_iterations: 10
                * iter_max: 100
                * batch_size: 50
                * iter_num_no_change: 5
            Note:
                * It must be a positive integer value.
            Default Value: 0
            Types: int

        stepwise_direction:
            Optional Argument.
            Specify the type of stepwise algorithm to be used.
            Permitted Values: 'FORWARD', 'BACKWARD', 'BOTH', 'BIDIRECTIONAL'
            Types: str

        max_steps_num:
            Optional Argument.
            Specifies the maximum number of steps to be used for the Stepwise Algorithm.
            Note:
                *  The "max_steps_num" must be in the range [1, 2147483647].
            Default Value: 5
            Types: int
        
        attribute_data:
            Optional Argument.
            Specifies the teradataml DataFrame containing the attribute data.
            Note:
                * This is valid when "data_partition_column" argument is used.
            Types: teradataml DataFrame
        
        parameter_data:
            Optional Argument.
            Specifies the teradataml DataFrame containing the parameter data.
            Note:
                * This is valid when "data_partition_column" argument is used.
            Types: teradataml DataFrame
        
        iteration_mode:
            Optional Argument.
            Specifies the iteration mode.
            Note:
                * This is valid when "data_partition_column" argument is used.
            Permitted Values: 'BATCH', 'EPOCH'
            Default Value: 'BATCH'
            Types: str

        partition_column:
            Optional Argument.
            Specifies the column names of "data" on which to partition the input.
            The name should be consistent with the "data_partition_column".
            Note:
                * If the "data_partition_column" is unicode with foreign language characters, 
                  it is necessary to specify "partition_column" argument. 
                * Column range is not supported for "partition_column" argument. 
                * This is valid when "data_partition_column" argument is used.
            Types: str
        

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
        Instance of GLM.
        Output teradataml DataFrames can be accessed using attribute
        references, such as GLMObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. output_data


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        # Load the example data.
        load_example_data("dataframe", "admissions_train")

        # Create teradataml DataFrame objects.
        admissions_train = DataFrame.from_table("admissions_train")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # GLM() function requires features in numeric format for processing,
        # so first let's transform categorical columns to numerical columns
        # using VAL Transform() function.

        # Import required libraries.
        from teradataml import valib, OneHotEncoder, Retain

        # Configure VAL install location.
        configure.val_install_location = "VAL"

        # Define encoders for categorical columns.
        masters_code = OneHotEncoder(values=["yes", "no"],
                                     columns="masters",
                                     out_columns="masters")
        stats_code = OneHotEncoder(values=["Advanced", "Novice"],
                                   columns="stats",
                                   out_columns="stats")
        programming_code = OneHotEncoder(values=["Advanced", "Novice", "Beginner"],
                                         columns="programming",
                                         out_columns="programming")
        # Retain numerical columns.
        retain = Retain(columns=["admitted", "gpa"])

        # Transform categorical columns to numeric columns.
        glm_numeric_input = valib.Transform(data=admissions_train,
                                            one_hot_encode=[masters_code, stats_code,
                                            programming_code],
                                            retain=retain)

        # Example 1 : Generate generalized linear model(GLM) using
        #             input dataframe and provided formula.
        GLM_out_1 = GLM(formula = "admitted ~ gpa + yes_masters + no_masters + Advanced_stats + Novice_stats + Advanced_programming + Novice_programming + Beginner_programming",
                        data = glm_numeric_input.result,
                        learning_rate = 'INVTIME',
                        momentum = 0.0
                        )

        # Print the result DataFrame.
        print(GLM_out_1.result)
        print(GLM_out_1.output_data)

        # Example 2 : Generate generalized linear model(GLM) using
        #             input dataframe and input_columns and response_column
        #             instead of formula.
        GLM_out_2 = GLM(input_columns= ["gpa", "yes_masters", "no_masters",
                                        "Advanced_stats", "Novice_stats",
                                        "Advanced_programming", "Novice_programming",
                                        "Beginner_programming"],
                        response_column = "admitted",
                        data = glm_numeric_input.result,
                        learning_rate = 'INVTIME',
                        momentum = 0.0
                        )

        # Print the result DataFrame.
        print(GLM_out_2.result)
        print(GLM_out_2.output_data)

        # Example 3 : Generate generalized linear model(GLM) using stepwise regression algorithm.
        #             This example uses the boston dataset and scales the data.
        #             Scaled data is used as input data to generate the GLM model.
        # loading the example data
        load_example_data("decisionforest", ["boston"])
        load_example_data('glm', ['housing_train_segment', 'housing_train_parameter', 'housing_train_attribute'])

        # Create teradataml DataFrame objects.
        boston_df = DataFrame('boston')
        housing_seg = DataFrame('housing_train_segment')
        housing_parameter = DataFrame('housing_train_parameter')
        housing_attribute = DataFrame('housing_train_attribute')

        # Scaling the data
        # Scale "target_columns" with respect to 'STD' value of the column.
        fit_obj = ScaleFit(data=boston_df,
                        target_columns=['crim','zn','indus','chas','nox','rm','age','dis','rad','tax','ptratio','black','lstat',],
                        scale_method="STD")

        # Scale values specified in the input data using the fit data generated by the ScaleFit() function above.
        obj = ScaleTransform(object=fit_obj.output,
                            data=boston_df,
                            accumulate=["id","medv"])

        boston = obj.result

        # Generate generalized linear model(GLM) using stepwise regression algorithm.
        glm_1 = GLM(data=boston,
                    input_columns=['indus','chas','nox','rm'],
                    response_column='medv',
                    family='GAUSSIAN',
                    lambda1=0.02,
                    alpha=0.33,
                    batch_size=10,
                    learning_rate='optimal',
                    iter_max=36,
                    iter_num_no_change=100,
                    tolerance=0.0001,
                    initial_eta=0.02,
                    stepwise_direction='backward',
                    max_steps_num=10)
        
        # Print the result DataFrame.
        print(glm_1.result)

        # Example 4 : Generate generalized linear model(GLM) using
        #             stepwise regression algorithm with initial_stepwise_columns.
        glm_2 = GLM(data=boston,
                    input_columns=['crim','zn','indus','chas','nox','rm','age','dis','rad','tax','ptratio','black','lstat'],
                    response_column='medv',
                    family='GAUSSIAN',
                    lambda1=0.02,
                    alpha=0.33,
                    batch_size=10,
                    learning_rate='optimal',
                    iter_max=36,
                    iter_num_no_change=100,
                    tolerance=0.0001,
                    initial_eta=0.02,
                    stepwise_direction='bidirectional',
                    max_steps_num=10,
                    initial_stepwise_columns=['rad','tax']
            )

        # Print the result DataFrame.
        print(glm_2.result)

        # Example 5 : Generate generalized linear model(GLM) using partition by key.
        glm_3 = GLM(data=housing_seg,
                    input_columns=['bedrooms', 'bathrms', 'stories', 'driveway', 'recroom', 'fullbase', 'gashw', 'airco'],
                    response_column='price',
                    family='GAUSSIAN',
                    batch_size=10,
                    iter_max=1000,
                    data_partition_column='partition_id'
                    )

        # Print the result DataFrame.
        print(glm_3.result)

        # Example 6 : Generate generalized linear model(GLM) using partition by key with attribute data.
        glm_4 = GLM(data=housing_seg,
                    input_columns=['bedrooms', 'bathrms', 'stories', 'driveway', 'recroom', 'fullbase', 'gashw', 'airco'],
                    response_column='price',
                    family='GAUSSIAN',
                    batch_size=10,
                    iter_max=1000,
                    data_partition_column='partition_id',
                    attribute_data = housing_attribute,
                    attribute_data_partition_column = 'partition_id'
                    )

        # Print the result DataFrame.
        print(glm_4.result)

        # Example 7 : Generate generalized linear model(GLM) using partition by key with parameter data
        glm_5 = GLM(data=housing_seg,
                    input_columns=['bedrooms', 'bathrms', 'stories', 'driveway', 'recroom', 'fullbase', 'gashw', 'airco'],
                    response_column='homestyle',
                    family='binomial',
                    iter_max=1000,
                    data_partition_column='partition_id',
                    parameter_data = housing_parameter,
                    parameter_data_partition_column = 'partition_id'
                    )

        # Print the result DataFrame.
        print(glm_5.result)

    """