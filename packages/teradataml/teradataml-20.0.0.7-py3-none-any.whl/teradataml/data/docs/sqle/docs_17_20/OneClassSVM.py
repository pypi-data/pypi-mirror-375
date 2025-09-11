def OneClassSVM(data=None, input_columns=None, iter_max=300, batch_size=10,
                lambda1=0.02, alpha=0.15, iter_num_no_change=50, tolerance=0.001,
                intercept=True, learning_rate="OPTIMAL", initial_eta=0.05, decay_rate=0.25,
                decay_steps=5, momentum=0.0, nesterov=False, local_sgd_iterations=0,
                **generic_arguments):
    """
    DESCRIPTION:
        The OneClassSVM() is a linear support vector machine (SVM) that performs
        classification analysis on datasets to identify outliers or novelty.

        This function supports these models:
            * Classification (loss: hinge). During the training, all the data is
              assumed to belong to a single class (value 1), therefore "response_column"
              is not needed by the model. For OneClassSVMPredict(), output values are 0
              or 1. A value of 0 corresponds to an outlier, and 1 to a normal observation/instance.

        OneClassSVM() is implemented using Minibatch Stochastic Gradient Descent (SGD) algorithm,
        which is highly scalable for large datasets.

        The function output is a trained one-class SVM model, which can be input to the
        OneClassSVMPredict() for prediction. The model also contains model statistics of MSE,
        Loglikelihood, AIC, and BIC.

        Notes:
            * The categorical columns should be converted to numerical columns as preprocessing
              step (for example, OneHotEncoding(), OrdinalEncoding()). OneClassSVM() takes all
              features as numeric input.
            * For a good model, dataset should be standardized before feeding to OneClassSVM()
              as a preprocessing step (for example, using ScaleFit() and ScaleTranform()).
            * The rows with missing values are ignored during training and prediction of
              OneClassSVM/OneClassSVMPredict. Consider filling up those rows using imputation
              (SimpleImputeFit() and SimpleImputeTrasform()) or other mechanism to train
              on rows with missing values.
            * The function supports linear SVMs only.
            * A maximum of 2046 features are supported due to the limitation imposed by the maximum
              number of columns (2048) in a database table for OneClassSVM().


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        input_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" to be used for
            training the model (predictors, features, or independent variables).
            Types: str OR list of Strings (str)

        iter_max:
            Optional Argument.
            Specifies the maximum number of iterations (mini-batches) over the
            training data batches.
             Note:
                * It must be a positive value less than 10,000,000.
            Default Value: 300
            Types: int

        batch_size:
            Optional Argument.
            Specifies the number of observations (training samples) processed in a
            single mini-batch per AMP. The value '0' indicates no mini-batches, the entire
            dataset is processed in each iteration, and the algorithm becomes Gradient
            Descent. A value higher than the number of rows on any AMP will also default
            to Gradient Descent.
            Notes:
                * It must be a non-negative integer value.
                * It must be in the range [0, 2147483647]
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
            becomes effective when "lambda1" is greater than 0. The value represents
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
            loss including the "tolerance" to stop training. A value of '0' indicates
            no early stopping and the algorithm continues until "iter_max"
            iterations are reached.
            Notes:
                * It must be a non-negative integer value.
                * It must be in the range [0, 2147483647]
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
            Specifies whether "intercept" should be estimated or not based on
            whether "data" is already centered or not.
            Default Value: True
            Types: bool

        learning_rate:
            Optional Argument.
            Specifies the learning rate algorithm for SGD iterations.
            Permitted Values: CONSTANT, OPTIMAL, INVTIME, ADAPTIVE
            Default Value: OPTIMAL
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
            Note:
                * It must be in the range [0, 2147483647]
            Default Value: 5
            Types: int

        momentum:
            Optional Argument.
            Specifies the value to use for the momentum learning rate
            optimizer.A larger value indicates a higher momentum contribution.
            A value of '0' means the momentum optimizer is disabled. For a
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
            algorithm. A value of 0 implies Local SGD is disabled. A value higher
            than 0 enables Local SGD and that many local iterations are performed
            before updating the weights for the global model. With Local SGD algorithm,
            recommended values for arguments are as follows:
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
        Instance of OneClassSVM.
        Output teradataml DataFrames can be accessed using attribute
        references, such as OneClassSVMObj.<attribute_name>.
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
        load_example_data("larpredict", ["diabetes"])

        # Create teradataml DataFrame objects.
        data_input = DataFrame.from_table("diabetes")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1 :  Train OneClassSVM model using "input_columns"
        #              which helps in identifying the input data whether
        #              it is normal or novelty when result of OneClassSVM
        #              is passed to OneClassSVMPredict.
        one_class_svm1=OneClassSVM(data=data_input,
                                   input_columns=['age', 'sex', 'bmi',
                                                  'map1', 'tc', 'ldl',
                                                  'hdl', 'tch', 'ltg',
                                                  'glu', 'y'],
                                   local_sgd_iterations=537,
                                   batch_size=1,
                                   learning_rate='CONSTANT',
                                   initial_eta=0.01,
                                   lambda1=0.1,
                                   alpha=0.0,
                                   momentum=0.0,
                                   iter_max=1
                                   )

        # Print the result DataFrame.
        print(one_class_svm1.result)
        print(one_class_svm1.output_data)

        # Example 2 :  Train OneClassSVM model using "input_columns",
        #              "learning_rate" set to 'ADAPTIVE', "momentum"
        #              set to '0.6' for better results.
        one_class_svm2=OneClassSVM(data=data_input,
                                   input_columns=['age', 'sex', 'bmi',
                                                  'map1', 'tc', 'ldl',
                                                  'hdl', 'tch', 'ltg',
                                                  'glu', 'y'],
                                   local_sgd_iterations=537,
                                   batch_size=1,
                                   learning_rate='ADAPTIVE',
                                   initial_eta=0.01,
                                   lambda1=0.1,
                                   alpha=0.0,
                                   momentum=0.6,
                                   iter_max=100
                                   )

        # Print the result DataFrame.
        print(one_class_svm2.result)
        print(one_class_svm2.output_data)

    """
