def CFilter(data = None, target_column = None, transaction_id_columns = None,
            partition_columns = None, max_distinct_items = 100,
            **generic_arguments):
    
    """
    DESCRIPTION:
        Function calculates several statistical measures of how likely 
        each pair of items is to be purchased together.
    
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame
        
        target_column:
            Required Argument.
            Specifies name of the column from the "data" containing data for filtration.
            Types: str
        
        transaction_id_columns:
            Required Argument.
            Specifies the name of the columns in "data" containing transaction id that defines the groups of items listed
            in the input columns that are purchased together.
            Types: str OR list of Strings (str)
        
        partition_columns:
            Optional Argument.
            Specifies the name of the column in "data" to partition the data on.
            Types: str OR list of Strings (str)
        
        max_distinct_items:
            Optional Argument.
            Specifies the maximum size of the item set. 
            Default Value: 100
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
        Instance of CFilter.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as CFilterObj.<attribute_name>.
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
        load_example_data("dataframe", ["grocery_transaction"])
        
        # Create teradataml DataFrame objects.
        df = DataFrame.from_table("grocery_transaction")
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function CFilter.
        from teradataml import CFilter
        
        # Example 1: CFilter function to calculate the statistical measures
        #            of how likely each pair of items is to be purchased together, without
        #            specifying the partition_columns.
        CFilter_out = CFilter(data=df, 
                              target_column='item',
                              transaction_id_columns = 'tranid',
                              max_distinct_items=100)
        
        # Print the result DataFrame.
        print(CFilter_out.result)

        # Example 2: CFilter function to calculate the statistical measures
        #            of how likely each pair of items is to be purchased together,
        #            specifying the partition_columns.
        CFilter_out2 = CFilter(data=df, 
                               target_column='item', 
                               transaction_id_columns = 'tranid',
                               partiton_columns='storeid',
                               max_distinct_items=100)

        # Print the result DataFrame.
        print(CFilter_out2.result)
    """
