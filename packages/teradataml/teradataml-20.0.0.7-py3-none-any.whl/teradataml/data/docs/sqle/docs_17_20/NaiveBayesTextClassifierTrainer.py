def NaiveBayesTextClassifierTrainer(data=None, doc_category_column=None, token_column=None, doc_id_column=None,
                                    model_type="MULTINOMIAL", **generic_arguments):
    """
    DESCRIPTION:
        The NaiveBayesTextClassifierTrainer() function calculates the conditional probabilities for 
        token-category pairs, the prior probabilities, and the missing token probabilities for 
        all categories. The trainer function trains the model with the probability values, and 
        the predict function uses the values to classify documents into categories.
    
    
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame
        
        doc_category_column:
            Required Argument.
            Specifies the name of the input data column that contains the 
            document category.
            Types: str
        
        token_column:
            Required Argument.
            Specifies the name of the input data column that contains the tokens.
            Types: str
        
        doc_id_column:
            Optional Argument.
            Specifies the name of the input data column that contains the 
            document identifier.
            Types: str
        
        model_type:
            Optional Argument.
            Specifies the model type of the text classifier. 
            Default Value: "MULTINOMIAL"
            Permitted Values: MULTINOMIAL, BERNOULLI
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
        Instance of NaiveBayesTextClassifierTrainer.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as 
        NaiveBayesTextClassifierTrainerObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. model_data
    
    
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
        load_example_data("textparser", ["complaints", "stop_words"])
        
        # Create teradataml DataFrame objects.
        complaints = DataFrame.from_table("complaints")
        stop_words = DataFrame.from_table("stop_words")
        
        # Check the list of available analytic functions.
        display_analytic_functions()

        # Tokenize the "text_column" and accumulate result by "doc_id" and "category".
        complaints_tokenized = TextParser(data=complaints,
                                          text_column="text_data",
                                          object=stop_words,
                                          remove_stopwords=True,
                                          accumulate=["doc_id", "category"])
        
        # Example 1 : Calculate the conditional probabilities for token-category pairs.
        NaiveBayesTextClassifierTrainer_out = NaiveBayesTextClassifierTrainer(data=complaints_tokenized.result,
                                                                              token_column="token",
                                                                              doc_category_column="category")
        
        # Print the result DataFrames.
        print(NaiveBayesTextClassifierTrainer_out.result)
        print(NaiveBayesTextClassifierTrainer_out.model_data)
    
    """