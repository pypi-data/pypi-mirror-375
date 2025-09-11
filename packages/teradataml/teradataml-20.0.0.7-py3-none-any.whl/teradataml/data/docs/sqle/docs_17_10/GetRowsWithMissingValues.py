def GetRowsWithMissingValues(data=None, target_columns=None, **generic_arguments):
    """
    DESCRIPTION:
        Function displays the rows that have NULL values in the specified input data columns.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Optional Argument.
            Specifies the name(s) of the column(s) in "data", in which NULL value should be checked.
            By default, all columns of the input teradataml DataFrame are considered as target.
            Types: str OR list of Strings (str)
        
        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in table or not.
                    When set to True, results are persisted in table; otherwise, results
                    are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in volatile table or not.
                    When set to True, results are stored in volatile table, otherwise not.
                    Default Value: False
                    Types: boolean

                Function allows the user to partition, hash, order or local order the input
                data. These generic arguments are available for each argument that accepts
                teradataml DataFrame as input and can be accessed as:
                    * "<input_data_arg_name>_partition_column" accepts str or list of str (Strings)
                    * "<input_data_arg_name>_hash_column" accepts str or list of str (Strings)
                    * "<input_data_arg_name>_order_column" accepts str or list of str (Strings)
                    * "local_order_<input_data_arg_name>" accepts boolean
                Note:
                    These generic arguments are supported by teradataml if the underlying
                    SQLE function supports it, else an exception is raised.


    RETURNS:
        Instance of GetRowsWithMissingValues.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as GetRowsWithMissingValuesObj.<attribute_name>.
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

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Get the rows that contain NULL values in columns 'name', 'sex', 'age', 'passenger'.
        obj = GetRowsWithMissingValues(data=titanic_data,
                                       target_columns=['name', 'sex', 'age', 'passenger'])

        # Print the result DataFrame.
        print(obj.result)

    """