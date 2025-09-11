def SMOTE(data = None, encoding_data = None, id_column = None,
          response_column = None, input_columns = None, categorical_columns = None,
          median_standard_deviation = None, minority_class = None,
          oversampling_factor = 5, sampling_strategy = "smote",
          fill_sampleid = True, noninput_columns_value = "sample", n_neighbors = 5,
          seed = None, **generic_arguments):
    """
    DESCRIPTION:
        SMOTE() function generates data by oversampling a minority class using 
        smote, adasyn, borderline-2 or smote-nc algorithms.
    
    
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame
        
        encoding_data:
            Optional Argument, Required when "sampling_strategy" is set to 'smotenc' algorithm.
            Specifies the teradataml dataframe containing the ordinal encoding information.
            Types: teradataml DataFrame
        
        id_column:
            Required Argument.
            Specifies the name of the column in "data" that 
            uniquely identifies a data sample.
            Types: str
        
        response_column:
            Optional Argument.
            Specifies the name of the column in "data" that contains the 
            numeric value to be used as the response value for a sample.
            Types: str
        
        input_columns:
            Required Argument.
            Specifies the name of the input columns in "data" for oversampling.
            Types: str OR list of Strings (str)
        
        categorical_columns:
            Optional Argument, Required when "sampling_strategy" is set to 'smotenc' algorithm.
            Specifies the name of the categorical columns in the "data" that 
            the function uses for oversampling with smotenc.
            Types: str OR list of Strings (str)
        
        median_standard_deviation:
            Optional Argument, Required when "sampling_strategy" is set to 'smotenc' algorithm.
            Specifies the median of the standard deviations computed over the 
            numerical input columns.
            Types: float
        
        minority_class:
            Required Argument.
            Specifies the minority class for which synthetic samples need to be 
            generated. 
            Note:
                * The label for minority class under response column must be numeric integer.
            Types: str
        
        oversampling_factor:
            Optional Argument.
            Specifies the factor for oversampling the minority class.
            Default Value: 5
            Types: float
        
        sampling_strategy:
            Optional Argument.
            Specifies the oversampling algorithm to be used to create synthetic samples.
            Default Value: "smote"
            Permitted Values: "smote", "adasyn", "borderline", "smotenc"
            Types: str
        
        fill_sampleid:
            Optional Argument.
            Specifies whether to include the id of the original observation used 
            to generate each synthetic observation.
            Default Value: True
            Types: bool
        
        noninput_columns_value:
            Optional Argument.
            Specifies the value to put in a sample column for columns not 
            specified as input columns.
            Default Value: "sample"
            Permitted Values: "sample", "neighbor", "null"
            Types: str
        
        n_neighbors:
            Optional Argument.
            Specifies the number of nearest neighbors for choosing the sample to 
            be used in oversampling.
            Default Value: 5
            Types: int
        
        seed:
            Optional Argument.
            Specifies the random seed the algorithm uses for repeatable results. 
            The function uses the seed for random interpolation and generate the 
            synthetic sample.
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
        Instance of SMOTE.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as SMOTEObj.<attribute_name>.
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
        load_example_data("dataframe", "iris_test")
        load_example_data("teradataml", "titanic")
        
        # Create teradataml DataFrame objects.
        iris_input = DataFrame.from_table("iris_test").iloc[:25]
        titanic_input = DataFrame("titanic").iloc[:50]

        # Create Encoding DataFrame objects.
        encoded_data = OrdinalEncodingFit(data=titanic_input,
                                          target_column=['sex','embarked'],
                                          approach="AUTO")
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function SMOTE.
        from teradataml import SMOTE
        
        # Example 1 : Generate synthetic samples using smote algorithm.
        smote_out = SMOTE(data = iris_input,
                          n_neighbors = 5,
                          id_column='id',
                          minority_class='3',
                          response_column='species',
                          input_columns =['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
                          oversampling_factor=2,
                          sampling_strategy='smote',
                          seed=10)
        
        # Print the result DataFrame.
        print(smote_out.result)

        # Example 2 : Generate synthetic samples using smotenc algorithm with categorical columns.
        smote_out2 = SMOTE(data = titanic_input, 
                           encoding_data = encoded_data.result, 
                           id_column = 'passenger', 
                           response_column = 'survived', 
                           input_columns = ['parch', 'age', 'sibsp'], 
                           categorical_columns = ['sex', 'embarked'],
                           median_standard_deviation = 31.47806044604718,
                           minority_class = '1', 
                           oversampling_factor = 5,
                           sampling_strategy = "smotenc", 
                           noninput_columns_value = "null", 
                           n_neighbors = 5)
        
        # Print the result DataFrame.
        print(smote_out2.result)
    """