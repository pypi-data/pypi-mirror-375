def DecisionForest(formula=None, data = None, input_columns = None, response_column = None,
                   max_depth = 5, num_trees = -1, min_node_size = 1, mtry = -1,
                   mtry_seed = 1, seed = 1, tree_type = "REGRESSION", tree_size = -1,
                   coverage_factor = 1.0, min_impurity = 0.0, **generic_arguments):
    """
    DESCRIPTION:
        The decision forest model function is an ensemble algorithm used for classification
        and regression predictive modeling problems. It is an extension of bootstrap
        aggregation (bagging) of decision trees. Typically, constructing a decision tree
        involves evaluating the value for each input feature in the data to select a split point.
        
        The function reduces the features to a random subset (that can be considered at each split point);
        the algorithm can force each decision tree in the forest to be very different to 
        improve prediction accuracy.
        
        The function uses a training dataset to create a predictive model. The DecisionForestPredict()
        function uses the model created by the DecisionForest() function for making predictions.
        
        The function supports regression, binary, and multi-class classification.

        Notes:
            * All input features are numeric. Convert the categorical columns to numerical
              columns as preprocessing step.
            * For classification, class labels ("response_column" values) can only be integers.
            * Any observation with a missing value in an input column is skipped and 
              not used for training. One can use either SimpleImpute() or FillNa() and valib.Transform() function
              to assign missing values.
        
        The number of trees built by the function depends on the "num_trees", "tree_size",
        "coverage_factor" values, and the data distribution in the cluster. The trees are constructed
        in parallel by all the AMPs, which have a non-empty partition of data.
            * When you specify the "num_trees" value, the number of trees built by the function is adjusted as:
                "Number_of_trees = Num_AMPs_with_data * (num_trees/Num_AMPs_with_data)" 
            * To find out number of AMPs with data value, please use hashamp() + 1 function 
              from teradataml extension with sqlalchemy.
            * When you do not specify the "num_trees" value, the number of trees built by an AMP is calculated as:
                "Number_of_AMP_trees = coverage_factor * Num_Rows_AMP / tree_size"
              The number of trees built by the function is the sum of Number_of_AMP_trees.
            * The "tree_size" value determines the sample size used to build a tree in the forest and
              depends on the memory available to the AMP. By default, this value is computed internally
              by the function. The function reserves approximately 40% of its available memory to store
              the input sample, while the rest is used to build the tree.
       
    PARAMETERS:
        formula:
            Required Argument when "input_columns" and "response_column" are not provided,
            optional otherwise.
            Specifies a string consisting of "formula". Specifies the model to be fitted. 
            Only basic formula of the "col1 ~ col2 + col3 +..." form are 
            supported and all variables must be from the same teradataml 
            DataFrame object. The response should be column of type float, int or bool.
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
            Specifies the names of the input DataFrame columns to be used for
            training the model (predictors, features or independent variables).
            Note:
                * Provide either "formula" argument or "input_columns" and
                  "response_column" arguments.
            Types: str OR list of Strings (str)
        
        response_column:
            Required Argument when "formula" is not provided, optional otherwise.
            Specifies the name of the column containing the class label for 
            classification or target value (dependent variable) for regression.
            Note:
                * Provide either "formula" argument or "input_columns" and
                  "response_column" arguments.
            Types: str
        
        max_depth:
            Optional Argument.
            Specifies a decision tree stopping criterion. If the tree reaches a 
            depth past this value, the algorithm stops looking for splits. 
            Decision trees can grow to (2^(max_depth+1)-1) nodes. This stopping 
            criterion has the greatest effect on the performance of the function
            Note:
                Must be a non-negative integer value.
            Default Value: 5
            Types: int
        
        num_trees:
            Optional Argument.
            Specifies the number of trees to grow in the forest model. When 
            specified, the number of trees must be greater than or equal to the 
            number of AMPs with data. By default, the function builds the minimum 
            number of trees that provides the input dataset with coverage based 
            on "coverage_factor".
            Default Value: -1
            Types: int
        
        min_node_size:
            Optional Argument.
            Specifies the minimum number of observations in a tree node.
            The algorithm stops splitting a node if the number of observations
            in the node is equal to or smaller than this value. You must specify
            a non-negative integer value. 
            Default Value: 1
            Types: int
        
        mtry:
            Optional Argument.
            Specifies the number of features from input columns for evaluating
            the best split of a node. A higher value improves the splitting and
            performance of a tree. A smaller value improves the robustness of 
            the forest and prevents it from overfitting. When the value is -1,
            all variables are used for each split.
            Default Value: -1
            Types: int
        
        mtry_seed:
            Optional Argument.
            Specifies  the random seed that the algorithm uses for the "mtry" argument. 
            Default Value: 1
            Types: int
        
        seed:
            Optional Argument.
            Specifies the random seed that the algorithm uses for repeatable results.
            Default Value: 1
            Types: int
        
        tree_type:
            Optional Argument.
            Specifies whether the analysis is a regression (continuous response 
            variable) or a multiple-class classification (predicting result from 
            the number of classes).
            Default Value: "REGRESSION"
            Permitted Values: REGRESSION, CLASSIFICATION
            Types: str
        
        tree_size:
            Optional Argument.
            Specifies the number of rows that each tree uses as its input dataset. 
            The function builds a tree using either the number of rows on an AMP, 
            the number of rows that fit into the AMP"s memory (whichever is less),
            or the number of rows given by the "tree_size" argument. By 
            default, this value is the minimum of the number of rows on an AMP,
            and the number of rows that fit into the AMP"s memory.
            Default Value: -1
            Types: int
        
        coverage_factor:
            Optional Argument.
            Specifies the level of coverage for the dataset while building trees,
            in percentage. 
            For example, 1.25 = 125% coverage.
            Notes:
                * "coverage_factor" can only be used when "num_trees" is not specified.
                * When "num_trees" is specified, coverage depends on the value of 
                  the "num_trees".
                * When "num_trees" is not specified, "num_trees" is chosen to achieve 
                  level of coverage specified by this argument.
                * A higher coverage level will ensure a higher probability of each row in input 
                  data to be selected during the tree building process (at the cost of building 
                  more trees).
                * Because of internal sampling in bootstrapping, some rows may be chosen
                  multiple times, and some not at all.
            Default Value: 1.0
            Types: float OR int
        
        min_impurity:
            Optional Argument.
            Specifies the minimum impurity at which the tree stops splitting 
            further down. For regression, a criteria of squared error is used 
            whereas for classification, gini impurity is used.
            Default Value: 0.0
            Types: float OR int

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
        Instance of DecisionForest.
        Output teradataml DataFrames can be accessed using attribute
        references, such as DecisionForestObj.<attribute_name>.
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

        # Load the example data.
        load_example_data("decisionforest", ["boston"])
        
        # Create teradataml DataFrame objects.
        boston_sample = DataFrame.from_table("boston")
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Example 1 : Generate decision forest regression model using
        #             input dataframe and input_columns and response_column
        #             instead of formula.
        DecisionForest_out = DecisionForest(data = boston_sample, 
                                input_columns = [ 'crim', 'zn', 'indus', 'chas', 'nox', 'rm',
                                                'age', 'dis', 'rad', 'tax', 'ptratio', 'black',
                                                'lstat'], 
                                response_column = 'medv', 
                                max_depth = 12, 
                                num_trees = 4, 
                                min_node_size = 1, 
                                mtry = 3, 
                                mtry_seed = 1, 
                                seed = 1, 
                                tree_type = 'REGRESSION')
        # Print the result DataFrame.
        print(DecisionForest_out.result)  
              
        # Example 2 : Generate decision forest regression model using
        #             input teradataml dataframe and provided formula.
        DecisionForest_out = DecisionForest(data = boston_sample, 
                                formula = "medv ~ crim + zn + indus + chas + nox + rm + age + dis + rad + tax + ptratio + black + lstat",  
                                max_depth = 12, 
                                num_trees = 4, 
                                min_node_size = 1, 
                                mtry = 3, 
                                mtry_seed = 1, 
                                seed = 1, 
                                tree_type = 'REGRESSION')
        
        # Print the result DataFrame.
        print(DecisionForest_out.result)
    """