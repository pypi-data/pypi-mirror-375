def Pivoting(data = None, partition_columns = None, target_columns = None,
             accumulate = None, rows_per_partition = None, pivot_column = None,
             pivot_keys = None, pivot_keys_alias = None, default_pivot_values = None,
             aggregation = None, delimiters = None, combined_column_sizes = None,
             truncate_columns = None, output_column_names = None,
             **generic_arguments):
        
    
    """
    DESCRIPTION:
        Function pivots the data, that is, changes the data from 
        sparse format to dense format.
        Notes:
            * 'data_partition_column' is required argument for partitioning the input data.
            * Provide either the 'rows_per_partition', 'pivot_column', or 'aggregation' arguments 
              along with required arguments.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame to be pivoted.
            Types: teradataml DataFrame
        
        partition_columns:
            Required Argument.
            Specifies the name of the column(s) in "data" on which to partition the 
            input.
            Types: str OR list of Strings (str)
        
        target_columns:
            Required Argument.
            Specifies the name of the column(s) in "data" which contains the data for 
            pivoting.
            Types: str OR list of Strings (str)
        
        accumulate:
            Optional Argument.
            Specifies the name of the column(s) in "data" to copy to the output. 
            By default, the function copies no input table columns to the output.
            Types: str OR list of Strings (str)
        
        rows_per_partition:
            Optional Argument.
            Specifies the maximum number of rows in the partition.
            Types: int
        
        pivot_column:
            Optional Argument.
            Specifies the name of the column in "data" that contains the pivot keys.
            Note:
                * This argument is not needed when 'rows_per_partition' is provided.
            Types: str
        
        pivot_keys:
            Optional Argument.
            Specifies the names of the pivot keys, if "pivot_column" is specified. 
            Notes:
                * This argument is not needed when 'rows_per_partition' is provided.
                * 'pivot_keys' are required when 'pivot_column' is specified.
            Types: str OR list of Strings (str)
        
        pivot_keys_alias:
            Optional Argument.
            Specifies the alias names of the pivot keys, if 'pivot_column' is specified.
            Note:
                * This argument is not needed when 'rows_per_partition' is provided.
            Types: str OR list of Strings (str)
        
        default_pivot_values:
            Optional Argument.
            Specifies one default value for each pivot_key. The nth 
            default_pivot_value applies to the nth pivot_key.
            Note:
                * This argument is not needed when 'rows_per_partition' is provided.
            Types: str OR list of Strings (str)
        
        aggregation:
            Optional Argument.
            Specifies the aggregation for the target columns. 
            Provide a single value {CONCAT | UNIQUE_CONCAT | SUM | 
            MIN | MAX | AVG}  which will be applicable to all target columns or 
            specify multiple values for multiple target columns in 
            following format: ['ColumnName:{CONCAT|UNIQUE_CONCAT|SUM|MIN|MAX|AVG}',...].
            Types: str OR list of Strings (str)
        
        delimiters:
            Optional Argument.
            Specifies the delimiter to be used for concatenating the values of a target column. 
            Provide a single delimiter value applicable to all target columns or 
            specify multiple delimiter values for multiple target columns 
            in the following format: ['ColumnName:single_char',...].
            Note:
                * This argument is not needed when 'aggregation' is not specified.
            Types: str OR list of Strings (str)
        
        combined_column_sizes:
            Optional Argument.
            Specifies the maximum size of the concatenated string.
            Provide a single integer value that applies to all target columns or 
            specify multiple size values for multiple target columns 
            in the following format ['ColumnName:size_value',...].
            Note:
                * This argument is not needed when 'aggregation' is not specified.
            Types: int OR  str OR list of Strings (str)
        
        truncate_columns:
            Optional Argument.
            Specifies columns from the target columns for which 
            to truncate the concatenated string if it exceeds the specified size.
            Note:
                * This argument is not needed when 'aggregation' is not specified.
            Types: str OR list of Strings (str)
        
        output_column_names:
            Optional Argument.
            Specifies the column name to be used for the output column. The nth 
            column name value applies to the nth output column.
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
        Instance of  Pivoting.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as  PivotingObj.<attribute_name>.
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
        load_example_data('unpivot', 'titanic_dataset_unpivoted')
        load_example_data('unpivot', 'star_pivot')
        
        # Create teradataml DataFrame objects.
        titanic_unpvt = DataFrame.from_table('titanic_dataset_unpivoted')
        star = DataFrame.from_table('star_pivot')
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function  Pivoting.
        from teradataml import  Pivoting
        
        # Example 1 : Pivot the input data using 'rows_per_partition'.
        pvt1 = Pivoting(data = titanic_unpvt, 
                        partition_columns = 'passenger', 
                        target_columns = 'AttributeValue',
                        accumulate = 'survived', 
                        rows_per_partition = 2,
                        data_partition_column='passenger',
                        data_order_column='AttributeName')
        
        # Print the result DataFrame.
        print( pvt1.result)

        # Example 2 : Pivot the input data using 'pivot_column' and 'pivot_keys'.
        pvt2 = Pivoting(data = titanic_unpvt, 
                        partition_columns = 'passenger', 
                        target_columns = 'AttributeValue',
                        accumulate = 'survived', 
                        pivot_column = 'AttributeName',
                        pivot_keys = ['pclass','gender'],
                        data_partition_column = 'passenger')

        # Print the result DataFrame.
        print( pvt2.result)

        # Example 3 : Pivot the input data with multiple target columns and
        #             multiple aggregation functions.
        pvt3 = Pivoting(data = star, 
                        partition_columns = ['country', 'state'],
                        target_columns = ['sales', 'cogs', 'rating'],
                        accumulate = 'yr',
                        pivot_column = 'qtr',
                        pivot_keys = ['Q1','Q2','Q3'],
                        aggregation = ['sales:SUM','cogs:AVG','rating:CONCAT'],
                        delimiters = '|', 
                        combined_column_sizes = 64001,
                        data_partition_column = ['country', 'state'],
                        data_order_column = ['qtr'])

        # Print the result DataFrame.
        print( pvt3.result)

        # Example 4 : Pivot the input data with multiple target columns and
        #             multiple aggregation functions.
        pvt4 = Pivoting(data = star, 
                        partition_columns = 'country', 
                        target_columns = ['sales', 'cogs', 'state','rating'],
                        accumulate = 'yr', 
                        aggregation = ['sales:SUM','cogs:AVG','state:UNIQUE_CONCAT','rating:CONCAT'], 
                        delimiters = '|', 
                        combined_column_sizes = ['state:5', 'rating:10'],
                        data_partition_column='country',
                        data_order_column='state')

        # Print the result DataFrame.
        print( pvt4.result)

        # Example 5 : Pivot the input data with truncate columns.
        pvt5 = Pivoting(data = star, 
                        partition_columns = ['state'],
                        target_columns = ['country', 'rating'],
                        accumulate = 'yr',
                        pivot_column = 'qtr',
                        pivot_keys = ['Q1','Q2','Q3'],
                        aggregation = 'CONCAT',
                        combined_column_sizes = 10,
                        truncate_columns = 'country',
                        data_partition_column = 'qtr',
                        data_order_column='state')

        # Print the result DataFrame.
        print( pvt5.result)

        # Example 6 : Pivot the input data with output column names.
        pvt6 = Pivoting(data = star, 
                        partition_columns = ['country','state'],
                        target_columns = ['sales', 'cogs', 'rating'],
                        accumulate = 'yr',
                        rows_per_partition = 3,
                        output_column_names=['sales_q1','sales_q2','sales_q3','cogs_q1','cogs_q2',
                                             'cogs_q3','rating_q1','rating_q2','rating_q3'],
                        data_partition_column = 'qtr',
                        data_order_column=['country','state'])

        # Print the result DataFrame.
        print( pvt6.result)
    """