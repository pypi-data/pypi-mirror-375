def Shap(data = None, object = None, id_column=None, training_function = None,
         model_type = "Regression", input_columns = None, detailed = False,
         accumulate = None, num_parallel_trees = 1000, num_boost_rounds = 10,
         **generic_arguments):

    """
    DESCRIPTION:
        Function to get explanation for individual predictions 
        (feature contributions) in a machine learning model based on the 
        co-operative game theory optimal Shapley values.
    
    PARAMETERS:
        data:
            Required Argument.
            Specifies the teradataml DataFrame.
            Types: teradataml DataFrame
        
        object:
            Required Argument.
            Specifies the teradataml DataFrame containing the model data.
            Types: teradataml DataFrame

        id_column:
            Required Argument.
            Specifies the input data column name that has the unique identifier
            for each row in the "data".
            Types: str
        
        training_function:
            Required Argument.
            Specifies the model type name.
            Permitted Values: TD_GLM, TD_DECISIONFOREST, TD_XGBOOST
            Types: str
        
        model_type:
            Required Argument.
            Specifies the operation to be performed on input data.
            Default Value: "Regression"
            Permitted Values: Regression, Classification
            Types: str
        
        input_columns:
            Required Argument.
            Specifies the names of the columns in "data" used for 
            training the model (predictors, features or independent variables).
            Types: str OR list of Strings (str)
        
        detailed:
            Optional Argument.
            Specifies whether to output detailed shap information about the 
            forest trees.
            Note: 
                * It is only supported for "TD_XGBOOST" and "TD_DECISIONFOREST" 
                  training functions.
            Default Value: False
            Types: bool
        
        accumulate:
            Optional Argument.
            Specifies the names of the input columns to copy to the output teradataml DataFrame.
            Types: str OR list of Strings (str)
        
        num_parallel_trees:
            Optional Argument.
            Specify the number of parallel boosted trees. Each boosted tree 
            operates on a sample of data that fits in an AMPs memory.
            Note:
                * By default, "num_parallel_trees" is chosen equal to the number of AMPs with 
                  data.
            Default Value: 1000
            Types: int
        
        num_boost_rounds:
            Optional Argument.
            Specifies the number of iterations to boost the weak classifiers. The 
            iterations must be an int in the range [1, 100000].
            Default Value: 10
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
        Instance of Shap.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as ShapObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            1. output
    
    
    RAISES:
        TeradataMlException, TypeError, ValueError
    
    
    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage, before importing the 
        #        function in user space.
        #     2. User can import the function, if it is available on 
        #        Vantage user is connected to.
        #     3. To check the list of analytic functions available on 
        #        Vantage user connected to, use 
        #        "display_analytic_functions()".
        
        # Load the example data.
        load_example_data("byom", "iris_input")
        load_example_data("teradataml", ["cal_housing_ex_raw"])
        
        # Create teradataml DataFrame objects.
        iris_input = DataFrame("iris_input")
        data_input = DataFrame.from_table("cal_housing_ex_raw")
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function Shap.
        from teradataml import Shap, XGBoost, DecisionForest, SVM
        
        # Example 1: Shap for classification model.
        XGBoost_out = XGBoost(data=iris_input,
                              input_columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
                              response_column = 'species',
                              model_type='Classification',
                              iter_num=25)
        
        Shap_out = Shap(data=iris_input, 
                        object=XGBoost_out.result, 
                        id_column='id',
                        training_function="TD_XGBOOST", 
                        model_type="Classification",
                        input_columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'], 
                        detailed=True)
        # Print the result DataFrame.
        print(Shap_out.output_data)

        # Example 2: Shap for regression model.

        from teradataml import ScaleFit, ScaleTransform

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
        
        decision_forest_out = DecisionForest(data=transform_obj.result,
                                             input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                                            'AveBedrms', 'Population', 'AveOccup',
                                                            'Latitude', 'Longitude'],
                                             response_column="MedHouseVal",
                                             model_type="Regression",
                                             max_depth = 10
                                             )
        Shap_out2 = Shap(data=transform_obj.result, 
                         object=decision_forest_out.result,
                         id_column='id',
                         training_function="TD_DECISIONFOREST",
                         model_type="Regression",
                         input_columns=['MedInc', 'HouseAge', 'AveRooms','AveBedrms', 'Population', 'AveOccup','Latitude', 'Longitude'],
                         detailed=True)

        # Print the result DataFrame.
        print(Shap_out2.output_data)

        # Example 3: Shap for GLM model.
        from teradataml import GLM
        GLM_out = GLM(data=transform_obj.result,
                      input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                     'AveBedrms', 'Population', 'AveOccup',
                                     'Latitude', 'Longitude'],
                      response_column="MedHouseVal",
                      family="GAUSSIAN")
        
        Shap_out3 = Shap(data=transform_obj.result, 
                         object=GLM_out.result,
                         id_column='id',
                         training_function="TD_GLM",
                         model_type="Regression",
                         input_columns=['MedInc', 'HouseAge', 'AveRooms','AveBedrms', 'Population', 'AveOccup','Latitude', 'Longitude'],
                         detailed=False)

        # Print the result DataFrame.
        print(Shap_out3.output_data)
    """
