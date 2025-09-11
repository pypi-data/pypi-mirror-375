def Unpivoting(data = None, id_column = None, target_columns = None,
                alias_names = None, attribute_column = "AttributeName", value_column = "AttributeValue",
                accumulate = None, include_nulls = False, input_types = False, output_varchar = False,
                indexed_attribute = False, include_datatypes = False,
                **generic_arguments):
    
    """
    DESCRIPTION:
        Function unpivots the data, that is, changes the data from
        dense format to sparse format.
    
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame
        
        id_column:
            Required Argument.
            Specifies the name of the column in "data" which contains the input data identifier.
            Types: str
        
        target_columns:
            Required Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) which contains the data for  
            unpivoting.
            Types: str OR list of Strings (str)

            Optional Argument.
            Specifies alternate names for the values in the 'attribute_column'.
            Types: str OR list of strs

        alias_names:
            Optional Argument.
            Specifies alternate names for the values in the 'attribute_column'. 
            column.
            Types: str OR list of strs
        
        attribute_column:
            Optional Argument.
            Specifies the name of the column in the output DataFrame, which holds the names of pivoted columns.
            Default Value: "AttributeName"
            Types: str
        
        value_column:
            Optional Argument.
            Specifies the name of the column in the output DataFrame, which holds the values of pivoted columns.
            Default Value: "AttributeValue"
            Types: str
        
        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to copy to the output.
            By default, the function copies no input teradataml DataFrame columns to the output.
            Types: str OR list of Strings (str)
        
        include_nulls:
            Optional Argument.
            Specifies whether or not to include nulls in the transformation.
            Default Value: False
            Types: bool
        
        input_types:
            Optional Argument.
            Specifies whether attribute values should be organized into multiple columns based on data type groups.
            Note:
                * 'input_types' argument cannot be used when output_varchar is set to True.
            Default Value: False
            Types: bool
        
        output_varchar:
            Optional Argument.
            Specifies whether to output the 'value_column' in varchar format regardless of its data type.
            Note:
                * 'output_varchar' argument cannot be used when input_types is set to True.
            Default Value: False
            Types: bool
        
        indexed_attribute:
            Optional Argument.
            Specifies whether to output the column indexes instead of column names in AttributeName column. 
            When set to True, outputs the column indexes instead of column names.
            Default Value: False
            Types: bool
        
        include_datatypes:
            Optional Argument.
            Specifies whether to output the original datatype name. When set to True,
            outputs the original datatype name.
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
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if 
                the underlying SQL Engine function supports, else an 
                exception is raised.        
    
    RETURNS:
        Instance of Unpivoting.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as UnpivotingObj.<attribute_name>.
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
        load_example_data('unpivot', 'unpivot_input')
        
        # Create teradataml DataFrame objects.
        upvt_inp = DataFrame('unpivot_input')
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function  Unpivoting.
        from teradataml import  Unpivoting
        
        # Example 1 : Unpivot the data.
        upvt1 = Unpivoting(data = upvt_inp, 
                           id_column = 'sn', 
                           target_columns = 'city',
                           accumulate = 'week',
                           include_nulls = True)
        
        # Print the result DataFrame.
        print( upvt1.result)

        # Example 2 : Unpivot the data with alternate names for the values in
        #             the AttributeName output column.
        upvt2= Unpivoting(data = upvt_inp, 
                          id_column = 'sn',
                          target_columns = 'city',
                          alias_names = 'city_us', 
                          attribute_column = "Attribute", 
                          value_column = "value",
                          accumulate = 'week', 
                          include_nulls = True)

        # Print the result DataFrame.
        print( upvt2.result)

        # Example 3 : Unpivot the data with multiple target columns and output
        #             data types.
        upvt3 = Unpivoting(data = upvt_inp, 
                           id_column = 'sn', 
                           target_columns = ['city','pressure'],
                           attribute_column = "Attribute", 
                           value_column = "value",
                           accumulate = 'week', 
                           include_nulls = True,
                           indexed_attribute = True, 
                           include_datatypes = True)

        # Print the result DataFrame.
        print( upvt3.result)
    
        # Example 4 : Unpivot the data with multiple target columns and output
        #             the input types.
        upvt4 = Unpivoting(data = upvt_inp, 
                           id_column = 'sn', 
                           target_columns = ['city','temp'],
                           accumulate = 'week', 
                           include_nulls = True, 
                           input_types = True)
                        
        # Print the result DataFrame.
        print( upvt4.result)

    """