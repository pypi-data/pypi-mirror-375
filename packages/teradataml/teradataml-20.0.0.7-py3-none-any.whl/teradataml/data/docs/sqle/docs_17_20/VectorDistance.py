def VectorDistance(target_data = None, reference_data = None, target_id_column = None, target_feature_columns = None,
                   ref_id_column = None, ref_feature_columns = None, distance_measure = "COSINE", topk = 10,
                   **generic_arguments):
    """
    DESCRIPTION:
        The VectorDistance() function accepts a dataframe of target vectors and a dataframe of reference vectors and
        returns output containing the distance between target-reference pairs.

        The function computes the distance between the target pair and the reference pair from the same input
        if you provide only one input.

        You must have the same column order in the "target_feature_columns" argument and the "ref_feature_columns"
        argument. The function ignores the feature values during distance computation if the value is either
        None, NAN, or INF.

        The function returns N*N output if you use the "topk" value as -1 because the function includes
        all reference vectors in the output.

        Notes:
            * The algorithm used in this function is of the order of N*N (where N is the number of rows).
                Hence, expect the function to run significantly longer as the number of rows increases in either
                the "target_data" or the "reference_data".
            * Because the reference data is copied to the spool for each AMP before running the query, the user
                spool limits the size and scalability of the input.
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
                For information about PTCs, see Teradata Vantage™ - Analytics Database International Character Set
                Support.
            * This function does not support KanjiSJIS or Graphic data types.
    
    
    PARAMETERS:
        target_data:
            Required Argument.
            Specifies the teradataml DataFrame containing target data vectors.
            Types: teradataml DataFrame
        
        reference_data:
            Optional Argument.
            Specifies the teradataml DataFrame containing reference data vectors.
            Types: teradataml DataFrame
        
        target_id_column:
            Required Argument.
            Specifies the name of the "target_data" column that contains
            identifiers of the target data vectors.
            Types: str
        
        target_feature_columns:
            Required Argument.
            Specifies the names of the "target_data" columns that contain features
            of the target data vectors.
            Note:
                You can specify up to 2018 feature columns.
            Types: str OR list of Strings (str)
        
        ref_id_column:
            Optional Argument.
            Specifies the name of the "reference_data" column that contains
            identifiers of the reference data vectors.
            Types: str
        
        ref_feature_columns:
            Optional Argument.
            Specifies the names of the "reference_data" columns that contain
            features of the reference data vectors.
            Note:
                You can specify up to 2018 feature columns.
            Types: str OR list of Strings (str)
        
        distance_measure:
            Optional Argument.
            Specifies the distance type to compute between the target and the reference vector.
            Default Value: "COSINE"
            Permitted Values:
                * Cosine: Cosine distance between the target vector and the reference vector.
                * Euclidean: Euclidean distance between the target vector and the reference vector.
                * Manhattan: Manhattan distance between the target vector and the reference vector.
            Types: str OR list of strs
        
        topk:
            Optional Argument.
            Specifies the maximum number of closest reference vectors to include in the output table
            for each target vector. The value k is an integer between 1 and 100.
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
                the underlying SQLE Engine function supports, else an 
                exception is raised.
    
    RETURNS:
        Instance of VectorDistance.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as VectorDistanceObj.<attribute_name>.
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
        load_example_data("vectordistance", ["target_mobile_data_dense", "ref_mobile_data_dense"])
        
        # Create teradataml DataFrame objects.
        target_mobile_data_dense=DataFrame("target_mobile_data_dense")
        ref_mobile_data_dense=DataFrame("ref_mobile_data_dense")
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Example 1 : Compute the cosine, euclidean, manhattan distance between the target and reference vectors.
        VectorDistance_out = VectorDistance(target_id_column="userid",
                                            target_feature_columns=['CallDuration', 'DataCounter', 'SMS'],
                                            ref_id_column="userid",
                                            ref_feature_columns=['CallDuration', 'DataCounter', 'SMS'],
                                            distance_measure=['Cosine', 'Euclidean', 'Manhattan'],
                                            topk=2,
                                            target_data=target_mobile_data_dense,
                                            reference_data=ref_mobile_data_dense)
        
        # Print the result DataFrame.
        print(VectorDistance_out.result)
    
    """