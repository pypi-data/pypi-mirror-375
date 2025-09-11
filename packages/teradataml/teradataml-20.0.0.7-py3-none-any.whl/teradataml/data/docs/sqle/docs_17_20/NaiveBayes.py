def  NaiveBayes(data = None, response_column = None, numeric_inputs = None,
                categorical_inputs = None, attribute_name_column = None,
                attribute_value_column = None, attribute_type = None,
                numeric_attributes = None, categorical_attributes = None,
                **generic_arguments):
    """
    DESCRIPTION:
        Function generates classification model using NaiveBayes 
        algorithm.
        The Naive Bayes classification algorithm uses a training dataset with known discrete outcomes
        and either discrete or continuous numeric input variables, along with categorical variables, to generate a model.
        This model can then be used to predict the outcomes of future observations based on their input variable values.
    
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame .
            Types: teradataml DataFrame
        
        response_column:
            Required Argument.
            Specifies the name of the column in "data" containing response values.
            Types: str
        
        numeric_inputs:
            Optional Argument.
            Specifies the names of the columns in "data" containing numeric attributes values.
            Types: str OR list of Strings (str)
        
        categorical_inputs:
            Optional Argument.
            Specifies the names of the columns in "data" containing categorical attributes values.
            Types: str OR list of Strings (str)
        
        attribute_name_column:
            Optional Argument.
            Specifies the names of the columns in "data" containing attributes names.
            Types: str
        
        attribute_value_column:
            Optional Argument.
            Specifies the names of the columns in "data" containing attributes values.
            Types: str
        
        attribute_type:
            Optional Argument, Required if "data" is in sparse format and
            both "numeric_attributes" and "categorical_attributes" are not provided.
            Specifies the attribute type. 
            Permitted Values: 
                * ALLNUMERIC - if all the attributes are of numeric type.
                * ALLCATEGORICAL - if all the attributes are of categorical type.
            Types: str
        
        numeric_attributes:
            Optional Argument.
            Specifies the numeric attributes names.
            Types: str OR list of strs
        
        categorical_attributes:
            Optional Argument.
            Specifies the categorical attributes names.
            Types: str OR list of strs
        
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
        Instance of  NaiveBayes.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as  NaiveBayesObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result
    
    
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
        load_example_data("decisionforestpredict", ["housing_train", "housing_test"])
        
        # Create teradataml DataFrame objects.
        housing_train = DataFrame.from_table("housing_train")
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function  NaiveBayes.
        from teradataml import  NaiveBayes, Unpivoting
        
        # Example 1: NaiveBayes function to generate classification model using Dense input.
        NaiveBayes_out = NaiveBayes(data=housing_train, response_column='homestyle', 
                                    numeric_inputs=['price','lotsize','bedrooms','bathrms','stories','garagepl'], 
                                    categorical_inputs=['driveway','recroom','fullbase','gashw','airco','prefarea'])
        
        # Print the result DataFrame.
        print( NaiveBayes_out.result)

        # Example 2: NaiveBayes function to generate classification model using Sparse input.
        
        # Unpivoting the data for sparse input to naive bayes.
        upvt_data = Unpivoting(data = housing_train, id_column = 'sn',
                               target_columns = ['price','lotsize','bedrooms','bathrms','stories','garagepl','driveway',
                                                 'recroom','fullbase','gashw','airco','prefarea'],
                               attribute_column = "AttributeName", value_column = "AttributeValue",
                               accumulate = 'homestyle')

        NaiveBayes_out = NaiveBayes(data=upvt_data.result, 
                                    response_column='homestyle',
                                    attribute_name_column='AttributeName', 
                                    attribute_value_column='AttributeValue',
                                    numeric_attributes=['price','lotsize','bedrooms','bathrms','stories','garagepl'], 
                                    categorical_attributes=['driveway','recroom','fullbase','gashw','airco','prefarea'])

        # Print the result DataFrame.
        print( NaiveBayes_out.result)
    """
