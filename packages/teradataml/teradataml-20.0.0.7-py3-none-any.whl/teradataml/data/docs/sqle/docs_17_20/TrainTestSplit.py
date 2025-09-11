def TrainTestSplit(data=None, id_column=None, stratify_column=None,
                   seed=None, train_size=0.75, test_size=0.25,
                   **generic_arguments):
        """
        DESCRIPTION:
            The TrainTestSplit() function simulates how a model would
            perform on new data. The function divides the dataset into
            train and test subsets to evaluate machine learning algorithms
            and validate processes. The first subset is used to train
            the model. The second subset is used to make predictions and
            compare the predictions to actual values.

            Notes:
                * The TrainTestSplit() function gives consistent results
                  across multiple runs on same machine. With different machines,
                  it might produce different train and test datasets.
                * Requires the UTF8 client character set for UNICODE data.
                * Does not support Pass Through Characters (PTCs).
                * Does not support KanjiSJIS or graphic data types.
        
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame on which split
                to be performed.
                Types: teradataml DataFrame
            
            id_column:
                Optional Argument.
                Specifies the input data column name that has the
                unique identifier for each row in the input.
                Notes:
                    * Mandatory when "seed" argument is present so that the
                      output of TrainTestSplit() function is deterministic
                      across multiple function calls.
                Types: str
            
            stratify_column:
                Optional Argument.
                Specifies column name that contains the labels indicating
                which data needs to be stratified.
                Types: str
            
            seed:
                Optional Argument.
                Specifies the seed value that controls the shuffling applied
                to the data before applying the split. Pass an int for reproducible
                output across multiple function calls.
                Notes:
                    * When the argument is not specified, different
                      runs of the query generate different outputs.
                    * It must be in the range [0, 2147483647]
                Types: int
            
            train_size:
                Optional Argument.
                Specifies the size of the train dataset.
                Notes:
                    * If both "train_size" and "test_size" arguments are specified,
                      then their sum must be equal to 1.
                    * "train_size" and "test_size" should be greater than the number
                      of classes when using stratify.
                    * If the input data does not have an identifier column, then
                      FillRowId() function can be used to generate one.
                    * It must be in the range (0, 1)
                Default Value: 0.75
                Types: float
            
            test_size:
                Optional Argument.
                Specifies the size of the test dataset.
                Note:
                    * It must be in the range (0, 1)
                Default Value: 0.25
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
                    the underlying SQL Engine function supports, else an 
                    exception is raised.
        
        RETURNS:
            Instance of TrainTestSplit.
            Output teradataml DataFrames can be accessed using attribute 
            references, such as TrainTestSplitObj.<attribute_name>.
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
            load_example_data("teradataml", ["titanic"])
            
            # Create teradataml DataFrame objects.
            data_input = DataFrame.from_table("titanic")
            
            # Check the list of available analytic functions.
            display_analytic_functions()
            
            # Example 1 : Split the input data to test dataset and train dataset,
            #             with ratio of test:train is 20:80. Note that output
            #             of TrainTestSplit() function contains 'TD_IsTrainRow'
            #             column in which '0' represent test data and '1'
            #             represent train data.
            TrainTestSplit_out = TrainTestSplit(data = data_input,
                                                id_column="passenger",
                                                train_size=0.80,
                                                test_size=0.20,
                                                seed=42)
            
            # Print the result DataFrame.
            print(TrainTestSplit_out.result)
        
        """