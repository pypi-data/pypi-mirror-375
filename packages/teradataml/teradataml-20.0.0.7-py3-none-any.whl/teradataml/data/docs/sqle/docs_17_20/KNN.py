def KNN(test_data = None, train_data = None, id_column = None, input_columns = None,
        model_type = "classification", k = 5, accumulate = None,  response_column = None,
        voting_weight = 0, tolerance = 1.0E-7, output_prob = False, output_responses = None,
        emit_neighbors = None, emit_distances = False, **generic_arguments):
    """
    DESCRIPTION:
        The KNN() function classifies data objects based on proximity to other 
        data objects with known categories.
    
    
    PARAMETERS:
        test_data:
            Required Argument.
            Specifies the input teradataml DataFrame containing the test data.
            Types: teradataml DataFrame
        
        train_data:
            Required Argument.
            Specifies the teradataml DataFrame containing the train data.
            Types: teradataml DataFrame
        
        id_column:
            Required Argument.
            Specifies the name of the column that uniquely identifies a data object 
            both in train and test data.
            Types: str
        
        input_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in train data that the 
            function uses to compute the distance between a test object and 
            the train objects. The test data must also have these columns.
            Types: str OR list of Strings (str)
        
        model_type:
            Optional Argument.
            Specifies the model type for KNN function.
            Default Value: "classification"
            Permitted Values: regression, classification, neighbors
            Types: str
        
        k:
            Optional Argument.
            Specifies the number of nearest neighbors to use in the algorithm.
            Any positive integer value > 0 and <= 1000 can be chosen.
            Default Value: 5
            Types: int
        
        accumulate:
            Optional Argument.
            Specifies the name(s) of the column(s) in test data
            to be copied to output.
            Types: str OR list of Strings (str)
        
        response_column:
            Optional Argument. Required when model type is regression or classification.
            Specifies the name of the train data column that contains the 
            numeric response variable values to be used for prediction in KNN 
            based regression or classification.
            Types: str
        
        voting_weight:
            Optional Argument.
            Specifies the voting weight of the train object for determining 
            the class of the test object as a function of the distance between 
            the train and test objects. The voting weight is calculated as w, 
            where w=1/POWER(distance, voting_weight) and distance is the distance 
            between the test object and the train object. Must be a 
            non-negative real number.
            Default Value: 0
            Types: float OR int
        
        tolerance:
            Optional Argument.
            Specifies the user to define the smallest distance to be considered. 
            When a non-zero voting weight is used, the case of zero distance 
            causes the weight (w=1/POWER(distance, voting_weight)) to be undefined.
            For any distance under the given tolerance, the weight is calculated as 
            w=1/POWER(tolerance, voting_weight).
            Default Value: 1.0E-7
            Types: float OR int
        
        output_prob:
            Optional Argument.
            Specifies whether the function should output the probability for each 
            response specified in "response_column". If "response_column" is not given, 
            outputs the probability of the predicted response.
            Default Value: False
            Types: bool
        
        output_responses:
            Optional Argument.
            Specifies the class labels for which to output probabilities.
            Types: str OR list of strs
        
        emit_neighbors:
            Optional Argument.
            Specifies whether the neighbors are to be emitted in the output.
            Default Value: False
            Types: bool
        
        emit_distances:
            Optional Argument.
            Specifies whether the neighbor distances are to be emitted in the output.
            Default Value: False
            Types: bool
        
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
                * "local_order_<input_data_arg_name>" accepts bool
            Note:
                These generic arguments are supported by teradataml if 
                the underlying SQL Engine function supports, else an 
                exception is raised.
    
    RETURNS:
        Instance of KNN.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as KNNObj.<attribute_name>.
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
        load_example_data("knn", ["computers_train1_clustered", "computers_test1"])
        
        # Create teradataml DataFrame objects.
        computers_test1 = DataFrame.from_table("computers_test1")
        computers_train1_clustered = DataFrame.from_table("computers_train1_clustered")
        
        # Check the list of available analytic functions.
        display_analytic_functions()

        # Generate fit object for column "computer_category".
        fit_obj = OneHotEncodingFit(data=computers_train1_clustered,
                                    is_input_dense=True,
                                    target_column="computer_category",
                                    categorical_values=["ultra", "special"],
                                    other_column="other")


        # Encode "ultra" and "special" values of column "computer_category".
        computers_train1_encoded = OneHotEncodingTransform(data=computers_train1_clustered,
                                                           object=fit_obj.result,
                                                           is_input_dense=True)

        # Example 1: Map the test computer data to "special" category.
        KNN_out = KNN(train_data = computers_train1_encoded.result,
                      test_data = computers_test1,
                      k = 50,
                      response_column = "computer_category_special",
                      id_column="id",
                      output_prob=False,
                      input_columns = ["price", "speed", "hd", "ram", "screen"],
                      voting_weight = 1.0,
                      emit_distances=False)

        # Print the result DataFrame.
        print(KNN_out.result)

        # Example 2: Get the distance of 10 nearest neighbours based on "price", "speed" and "hd".
        KNN_out = KNN(train_data = computers_train1_encoded.result,
                      test_data = computers_test1,
                      k=10,
                      model_type="neighbors",
                      id_column="id",
                      input_columns = ["price", "speed", "hd"],
                      emit_distances=True,
                      emit_neighbors=True)

        # Print the result DataFrame.
        print(KNN_out.result)
    """