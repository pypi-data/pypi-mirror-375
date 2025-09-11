def TFIDF(data = None, doc_id_column = None, token_column = None,
          tf_normalization = "NORMAL", idf_normalization = "LOG", 
          regularization = "NONE", accumulate = None,
          **generic_arguments):
    
    """
    DESCRIPTION:
        Function takes any document set and computes the Term Frequency (TF), 
        Inverse Document Frequency (IDF), and Term Frequency Inverse Document 
        Frequency (TF-IDF) scores for each term.
    
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame that contains
            the document id and the term.
            Types: teradataml DataFrame
        
        doc_id_column:
            Required Argument.
            Specifies the name of the column in "data" that contains the 
            document identifier.
            Types: str
        
        token_column:
            Required Argument.
            Specifies the name of the column in "data" that contains the tokens.
            Types: str
        
        tf_normalization:
            Optional Argument.
            Specifies the normalization method for calculating the term frequency (TF).
            Default Value: "NORMAL"
            Permitted Values: BOOL, COUNT, NORMAL, LOG, AUGMENT
            Types: str
        
        idf_normalization:
            Optional Argument.
            Specifies the normalization method for calculating the inverse 
            document frequency (IDF).
            Default Value: "LOG"
            Permitted Values: UNARY, LOG, LOGNORM, SMOOTH
            Types: str
        
        regularization:
            Optional Argument.
            Specifies the regularization method for calculating the TF-IDF score. 
            Default Value: "NONE"
            Permitted Values: L2, L1, NONE
            Types: str
        
        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
            output.
            Types: str OR list of Strings (str)

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
        Instance of TFIDF.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as  TFIDFObj.<attribute_name>.
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
        load_example_data('naivebayestextclassifier',"token_table")
        
        # Create teradataml DataFrame objects.
        inp = DataFrame.from_table('token_table')
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function  TFIDF.
        from teradataml import  TFIDF
        
        # Example 1 : Compute the TF, IDF and TF-IDF scores
        #             for each term in the input data.
        TFIDF_out = TFIDF(data=inp, 
                          doc_id_column='doc_id',
                          token_column='token',
                          tf_normalization = "LOG", 
                          idf_normalization = "SMOOTH", 
                          regularization = "L2",
                          accumulate=['category'])
        
        # Print the result DataFrame.
        print(TFIDF_out.result)
    """