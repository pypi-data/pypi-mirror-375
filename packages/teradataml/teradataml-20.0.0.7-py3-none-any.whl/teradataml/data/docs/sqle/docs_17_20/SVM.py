def SVM(formula=None, data=None, input_columns=None, response_column=None, model_type="Classification",
        iter_max=300, epsilon=0.1, batch_size=10, lambda1=0.02, alpha=0.15, iter_num_no_change=50,
        tolerance=0.001, intercept=True, class_weights="0:1.0, 1:1.0", learning_rate=None,
        initial_eta=0.05, decay_rate=0.25, decay_steps=5, momentum=0.0, nesterov=False,
        local_sgd_iterations=0, **generic_arguments):
    """
    DESCRIPTION:
        The SVM() function is a linear support vector machine (SVM) that performs
        classification and regression analysis on data sets.

        This function supports these models:
            * Regression (loss: epsilon_insensitive).
            * Classification (loss: hinge). Only binary classification is supported. The
              only response values are 0 or 1.

        SVM() is implemented using Minibatch Stochastic Gradient Descent (SGD) algorithm,
        which is highly scalable for large datasets.

        Due to gradient-based learning, the function is highly sensitive to feature scaling.
        Before using the features in the function, you must standardize the Input features
        using ScaleFit() and ScaleTransform() functions. The function only accepts numeric
        features. Therefore, before training, you must convert the categorical features to
        numeric values. The function skips the rows with missing (null) values during training.

        The function output is a trained SVM model, which can be input to the SVMPredict()
        for prediction. The model also contains model statistics of mean squared error (MSE),
        Loglikelihood, Akaike information criterion (AIC), and Bayesian information criterion (BIC).

        Further model evaluation can be done as a post-processing step using functions such as
        RegressionEvaluator(), ClassificationEvaluator(), and ROC().


    PARAMETERS:
        formula:
            Required Argument when "input_columns" and "response_column" are not provided,
            optional otherwise.
            Specifies a string consisting of "formula" which is the model to be fitted.
            Only basic formula of the "col1 ~ col2 + col3 +..." form are
            supported and all variables must be from the same teradataml
            DataFrame object.
            Notes:
                * The function only accepts numeric features. User must convert the categorical
                  features to numeric values, before passing to the formula.
                * In case categorical features are passed to formula, those are ignored, and
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

        model_type:
            Optional Argument.
            Specifies the type of the analysis.
            Permitted Values: Regression, Classification
            Default Value: 'Classification'
            Types: str

        iter_max:
            Optional Argument.
            Specifies the maximum number of iterations (mini-batches) over the
            training data batches.
            Note:
                * It must be a positive value less than 10,000,000.
            Default Value: 300
            Types: int

        epsilon:
            Optional Argument.
            Specifies the epsilon threshold for 'Regression' (the value of epsilon
            for epsilon_insensitive loss). Any difference between the current prediction
            and the correct label is ignored within this threshold.
            Default Value: 0.1
            Types: float OR int

        batch_size:
            Optional Argument.
            Specifies the number of observations (training samples) processed in a
            single mini-batch per AMP. The value '0' indicates no mini-batches, the entire
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
            A value of '0' means no regularization.
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
            in between is a combination of L1 and L2.
            Note:
                * It must be a float value between 0 and 1.
            Default Value: 0.15(15% L1, 85% L2)
            Types: float OR int

        iter_num_no_change:
            Optional Argument.
            Specifies the number of iterations (mini-batches) with no improvement in
            loss including the tolerance to stop training. A value of '0' indicates
            no early stopping and the algorithm continues until "iter_max"
            iterations are reached.
            Note:
                * It must be a non-negative integer value.
            Default Value: 50
            Types: int

        tolerance:
            Optional Argument.
            Specifies the stopping criteria in terms of loss function improvement.
            Notes:
                * Applicable when "iter_num_no_change" is greater than '0'.
                * It must be a positive value.
            Default Value: 0.001
            Types: float OR int

        intercept:
            Optional Argument.
            Specifies whether intercept should be estimated or not based on
            whether "data" is already centered or not.
            Default Value: True
            Types: bool

        class_weights:
            Optional Argument.
            Specifies the weights associated with classes. If the weight of a class is omitted,
            it is assumed to be 1.0.
            Note:
                * Only applicable when "model_type" is set to 'Classification' . The format is
                  '0:weight,1:weight'. For example, '0:1.0,1:0.5' will give twice the
                  weight to each observation in class 0.
            Default Value: "0:1.0, 1:1.0"
            Types: str

        learning_rate:
            Optional Argument.
            Specifies the learning rate algorithm for SGD iterations.
            Permitted Values: CONSTANT, OPTIMAL, INVTIME, ADAPTIVE
            Default Value:
                * 'INVTIME' when "model_type" is set to 'Regression'
                * 'OPTIMAL' when "model_type" is set to 'Classification'
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
            A larger value indicates a higher momentum contribution.
            A value of 0 means the momentum optimizer is disabled.  For a
            good momentum contribution, a value between 0.6-0.95 is recommended.
            Note:
                * It must be a non-negative float value between 0 and 1.
            Default Value: 0.0
            Types: float OR int

        nesterov:
            Optional Argument.
            Specifies whether Nesterov optimization should be applied to the
            momentum optimizer or not.
            Note:
                * Applicable when "momentum" is greater than 0.
            Default Value: False
            Types: bool

        local_sgd_iterations:
            Optional Argument.
            Specifies the number of local iterations to be used for Local SGD
            algorithm. A value of 0 implies that Local SGD is disabled. A value higher
            than 0 enables Local SGD and that many local iterations are performed
            before updating the weights for the global model. With Local SGD algorithm,
            recommended values for this argument are as follows:
                * local_sgd_iterations: 10
                * iter_max:100
                * batch_size: 50
                * iter_num_no_change: 5
            Note:
                * It must be a positive integer value.
            Default Value: 0
            Types: int

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
        Instance of SVM.
        Output teradataml DataFrames can be accessed using attribute
        references, such as SVMObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
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
        load_example_data("teradataml", ["cal_housing_ex_raw"])

        # Create teradataml DataFrame objects.
        data_input = DataFrame.from_table("cal_housing_ex_raw")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Scale "target_columns" with respect to 'STD' value of the column.
        fit_obj = ScaleFit(data=data_input,
                           target_columns=['MedInc', 'HouseAge', 'AveRooms',
                                           'AveBedrms', 'Population', 'AveOccup',
                                           'Latitude', 'Longitude'],
                           scale_method="STD")

        # Transform the data.
        transform_obj = ScaleTransform(data=data_input,
                                       object=fit_obj.output,
                                       accumulate=["id", "MedHouseVal"])


        # Example 1 : Train the transformed data using SVM when "model_type" is 'Regression'
        #             and default values provided.
        obj1 = SVM(data=transform_obj.result,
                  input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                 'AveBedrms', 'Population', 'AveOccup',
                                 'Latitude', 'Longitude'],
                  response_column="MedHouseVal",
                  model_type="Regression"
                  )

        # Print the result DataFrame.
        print(obj1.result)
        print(obj1.output_data)

        # Example 2 : Train the transformed data using SVM when "model_type" is 'Classification'
        #             when "learning_rate" is 'INV_TIME'.
        obj2 = SVM(data=transform_obj.result,
                  input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                 'AveBedrms', 'Population', 'AveOccup',
                                 'Latitude', 'Longitude'],
                  response_column="MedHouseVal",
                  model_type="Classification",
                  batch_size=12,
                  iter_max=301,
                  lambda1=0.1,
                  alpha=0.5,
                  iter_num_no_change=60,
                  tolerance=0.01,
                  intercept=False,
                  class_weights="0:1.0,1:0.5",
                  learning_rate="INVTIME",
                  initial_data=0.5,
                  decay_rate=0.5,
                  momentum=0.6,
                  nesterov=True,
                  local_sgd_iterations=1,
                  )

        # Print the result DataFrame.
        print(obj2.result)
        print(obj2.output_data)

        # Example 3 : Generate linear support vector machine(SVM) when "learning_rate"
        #             is 'ADAPTIVE' and "class_weight" is '0:1.0,1:0.5'.
        obj3 = SVM(data=transform_obj.result,
                  input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                 'AveBedrms', 'Population', 'AveOccup',
                                 'Latitude', 'Longitude'],
                  response_column="MedHouseVal",
                  model_type="Classification",
                  batch_size=1,
                  iter_max=1,
                  lambda1=0.0,
                  iter_num_no_change=60,
                  tolerance=0.01,
                  intercept=False,
                  class_weights="0:1.0,1:0.5",
                  learning_rate="ADAPTIVE",
                  initial_data=0.1,
                  decay_rate=0.5,
                  momentum=0.7,
                  nesterov=True,
                  local_sgd_iterations=1,
                  )

        # Print the result DataFrame.
        print(obj3.result)
        print(obj3.output_data)

        # Example 4 : Generate linear support vector machine(SVM) when "decay_rate" is 0.5
        #             and "model_type" is 'regression'.
        obj4 = SVM(data=transform_obj.result,
                  input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                 'AveBedrms', 'Population'],
                  response_column="MedHouseVal",
                  model_type="Regression",
                  decay_rate=0.5,
                  momentum=0.7,
                  nesterov=True,
                  local_sgd_iterations=1,
                  )

        # Print the result DataFrame.
        print(obj4.result)
        print(obj4.output_data)

        # Example 5 : Generate linear support vector machine(SVM) using
        #             input dataframe and provided formula and "model_type" is 'regression'.
        formula = "MedHouseVal~MedInc + HouseAge + AveRooms + AveBedrms + Population + AveOccup + Latitude + Longitude"
        obj5 = SVM(data=transform_obj.result,
                  formula=formula,
                  model_type="Regression"
                  )

        # Print the result DataFrame.
        print(obj5.result)
        print(obj5.output_data)
    """