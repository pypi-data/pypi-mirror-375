def XGBoost(formula=None, data=None, input_columns=None, response_column=None, max_depth=5,
            num_boosted_trees=-1, min_node_size=1, seed=1, model_type='REGRESSION',
            coverage_factor=1.0, min_impurity=0.0, lambda1=1, shrinkage_factor=0.5, 
            column_sampling=1.0, iter_num=10, tree_size=-1, base_score=0.0,
            **generic_arguments):
    """
    DESCRIPTION:
        The XGBoost() function, also known as eXtreme Gradient Boosting, is an implementation
        of the gradient boosted decision tree algorithm designed for speed and performance.
        It has recently been dominating applied machine learning.

        In gradient boosting, each iteration fits a model to the residuals (errors) of the
        previous iteration to correct the errors made by existing models. The predicted
        residual is multiplied by this learning rate and then added to the previous
        prediction. Models are added sequentially until no further improvements can be made.
        It is called gradient boosting because it uses a gradient descent algorithm to minimize
        the loss when adding new models.

        Gradient boosting involves three elements:
            * A loss function to be optimized.
            * A weak learner to make predictions.
            * An additive model to add weak learners to minimize the loss function.

        The loss function used depends on the type of problem being solved. For example, regression
        may use a squared error and binary classification may use binomial. A benefit of the gradient
        boosting is that a new boosting algorithm does not have to be derived for each loss function.
        Instead, it provides a generic enough framework that any differentiable loss function can be
        used. The XGBoost() function supports both regression and classification predictive
        modeling problems. The model that it creates is used in the XGBoostPredict() function
        for making predictions.

        The XGBoost() function supports the following features.
            * Regression
            * Multiple-Class and binary classification

        Notes:
            * When a dataset is small, best practice is to distribute the data to one AMP.
              To do this, create an identifier column as a primary index, and use the same
              value for each row.
            * For Classification (softmax), a maximum of 500 classes are supported.
            * For Classification, while the creating DataFrame for the function input,
              the DataFrame column must have a deterministic output. Otherwise, the function
              may not run successfully or return the correct output.
            * The processing time is controlled by (proportional to):
                * The number of boosted trees (controlled by "num_boosted_trees", "tree_size",
                  and "coverage_factor").
                * The number of iterations (sub-trees) in each boosted tree (controlled by "iternum").
                * The complexity of an iteration (controlled by "max_depth", "min_nod_size",
                  "column_sampling", "min_impurity").
              A careful choice of these parameters can be used to control the processing time.
              For example, changing "coverage_factor" from 1.0 to 2.0 doubles the number of boosted trees,
              which as a result, doubles the execution time roughly.


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
            Specifies the teradataml DataFrame containing the input data.
            Types: teradataml DataFrame

        input_columns:
            Required Argument when "formula" is not provided, optional otherwise.
            Specifies the name(s) of the teradataml DataFrame column(s) that need to be used
            for training the model (predictors, features, or independent variables).
            Note:
                * Input column names with double quotation marks are not allowed for this function.
            Types: str OR list of Strings (str)

        response_column:
            Required Argument when "formula" is not provided, optional otherwise.
            Specifies the name of the column that contains the class label for
            classification or target value (dependent variable) for regression.
            Types: str

        model_type:
            Optional Argument.
            Specifies whether the analysis is a regression (continuous response variable) or
            a multiple-class classification (predicting result from the number of classes).
            Default Value: Regression
            Permitted Values:
                * Regression
                * Classification
            Types: str

        max_depth:
            Optional Argument.
            Specifies a decision tree stopping criterion. If the tree reaches a
            depth past this value, the algorithm stops looking for splits.
            Decision trees can grow to (2^(max_depth+1)-1) nodes. This stopping
            criterion has the greatest effect on the performance of the function.
            The maximum value is 2147483647.
            Note:
                * The "max_depth" must be in the range [1, 2147483647].
            Default Value: 5
            Types: int

        num_boosted_trees:
            Optional Argument.
            Specifies the number of parallels boosted trees. Each boosted tree operates on
            a sample of data that fits in an AMP memory. By default, it is chosen equal
            to the number of AMPs with data. If "num_boosted_trees" is greater than
            the number of AMPs with data, each boosting operates on a sample of the input data,
            and the function estimates sample size (number of rows) using this formula:
            sample_size = total_number_of_input_rows / number_of_trees
            The sample_size must fit in an AMP memory. It always uses the sample size
            (or tree size) that fits in an AMP memory to build tree models and ignores
            those rows cannot fit in memory. A higher "num_boosted_trees" value may improve
            function run time but may decrease prediction accuracy.
            Note:
                 * The "num_boosted_trees" must be in the range [-1, 10000]
            Default Value: -1
            Types: int

        min_node_size:
             Optional Argument.
             Specifies a decision tree stopping criterion, which is the minimum size of any
             node within each decision tree.
             Note:
                 * The "min_node_size" must be in the range [1, 2147483647].
             Default Value: 1
             Types: int

        seed:
            Optional Argument.
            Specifies an integer value to use in determining the random seed for
            column sampling.
            Note:
                * The "seed" must be in the range [-2147483648, 2147483647].
            Default Value: 1
            Types: int

        coverage_factor:
            Optional Argument.
            Specifies the level of coverage for the dataset while boosting trees
            (in percentage, for example, 1.25 = 125% coverage). "coverage_factor"
            can only be used if "num_boosted_trees" is not supplied. When "num_boosted_trees"
            is specified, coverage depends on the value of "num_boosted_trees".
            If "num_boosted_trees" is not specified, "num_boosted_trees" is chosen to achieve
            this level of coverage specified by "coverage_factor".
            Note:
                * The "seed" must be in the range (0, 10.0].
            Default Value: 1.0
            Types: float OR int

        min_impurity:
            Optional Argument.
            Specifies the minimum impurity at which the tree stops splitting further down.
            For regression, a criteria of squared error is used, whereas for classification,
            gini impurity is used.
            Note:
                * The "min_impurity" must be in the range [0.0, 1.79769313486231570815e+308].
            Default Value: 0.0
            Types: float OR int

        lambda1:
            Optional Argument.
            Specifies the L2 regularization that the loss function uses while boosting trees.
            The higher the lambda, the stronger the regularization effect.
            Notes:
                * The "lambda1" must be in the range [0, 100000].
                * The value 0 specifies no regularization.
            Default Value: 1
            Types: float OR int

        shrinkage_factor:
            Optional Argument.
            Specifies the learning rate (weight) of a learned tree in each boosting step.
            After each boosting step, the algorithm multiplies the learner by shrinkage to
            factor make the boosting process more conservative.
            Notes:
                * The "shrinkage_factor" is a DOUBLE PRECISION value in the range (0, 1].
                * The value 1 specifies no shrinkage.
            Default Value: 0.5
            Types: float

        column_sampling:
            Optional Argument.
            Specifies the fraction of features to sample during boosting.
            Note:
                * The "column_sampling" must be in the range (0, 1].
            Default Value: 1.0
            Types: float

        iter_num:
            Optional Argument.
            Specifies the number of iterations (rounds) to boost the weak classifiers.
            Note:
                * The "iter_num" must be in the range [1, 100000].
            Default Value: 10
            Types: int

        tree_size:
            Optional Argument.
            Specifies the number of rows that each tree uses as its input data set.
            The function builds a tree using either the smaller of the number of rows
            on an AMP and the number of rows that fit into the AMP memory,
            or the number of rows given by the "tree_size" argument. By default,
            this argument takes the smaller of the number of rows on an AMP and
            the number of rows that fit into the AMP memory.
            Note:
                * The "tree_size" must be in the range [-1, 2147483647].
            Default Value: -1
            Types: int

        base_score:
            Optional Argument.
            Specifies the initial prediction value for all data points.
            Note:
                * The "base_score" must be in the range [-1e50, 1e50].
            Default Value: 0.0
            Types: float

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
                the underlying SQLE Engine function supports, else an
                exception is raised.

    RETURNS:
        Instance of XGBoost.
        Output teradataml DataFrames can be accessed using attribute
        references, such as XGBoostObj.<attribute_name>.
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
        load_example_data("teradataml", "titanic")
        load_example_data("byom", "iris_input")

        # Create teradataml DataFrame objects.
        titanic = DataFrame.from_table("titanic")
        iris_input = DataFrame("iris_input")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Train the model using features 'age', 'survived' and 'pclass'
        #            whereas target value as 'fare'.
        XGBoost_out_1 = XGBoost(data=titanic,
                                input_columns=["age", "survived", "pclass"],
                                response_column = 'fare',
                                max_depth=3,
                                lambda1 = 1000.0,
                                model_type='Regression',
                                seed=-1,
                                shrinkage_factor=0.1,
                                iter_num=2)

        # Print the result DataFrame.
        print(XGBoost_out_1.result)
        print(XGBoost_out_1.output_data)

        # Example 2: Improve the function run time by specifying "num_boosted_trees"
        #            value greater than the number of AMPs.
        XGBoost_out_2 = XGBoost(data=titanic,
                                input_columns=["age", "survived", "pclass"],
                                response_column = 'fare',
                                max_depth=3,
                                lambda1 = 1000.0,
                                model_type='Regression',
                                seed=-1,
                                shrinkage_factor=0.1,
                                num_boosted_tres=10,
                                iter_num=2)

        # Print the result DataFrame.
        print(XGBoost_out_2.result)
        print(XGBoost_out_2.output_data)

        # Example 3: Train the model using titanic input and provided the "formula".
        formula = "fare ~ age + survived + pclass"
        XGBoost_out_3 = XGBoost(data=titanic,
                                formula=formula,
                                max_depth=3,
                                lambda1 = 10000.0,
                                model_type='Regression',
                                seed=-1,
                                shrinkage_factor=0.1,
                                iter_num=2)

        # Print the result DataFrame.
        print(XGBoost_out_3.result)
        print(XGBoost_out_3.output_data)

        # Example 4: Train the model using features 'sepal_length', 'sepal_width',
        #            'petal_length', 'petal_width' whereas target value as 'species'
        #             and model type as 'Classification'.
        XGBoost_out_4 = XGBoost(data=iris_input,
                                input_columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
                                response_column = 'species',
                                max_depth=3,
                                lambda1 = 10000.0,
                                model_type='Classification',
                                seed=-1,
                                shrinkage_factor=0.1,
                                iter_num=2)

        # Print the result DataFrame.
        print(XGBoost_out_4.result)
        print(XGBoost_out_4.output_data)
    """