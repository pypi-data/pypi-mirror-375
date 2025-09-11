def ConvertTo(data = None, target_columns = None, target_datatype = None,
              **generic_arguments):
    """
    DESCRIPTION:
        The ConvertTo() function converts the specified input DataFrame columns to
        specified data types.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the input teradataml DataFrame columns which needs to be
            casted/converted to another data type.
            Types: str OR list of Strings (str)

        target_datatype:
            Required Argument.
            Specify target data type(s) into which "target_columns" need to be
            converted. If one value is provided, it applies to all "target_columns".
            If more than one value is specified, each "target_datatype" value applies to
            corresponding "target_columns" value (in the order specified by the user).
            Types: str OR list of strs

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
                Specifies whether to put the results of the function in volatile table
                or not. When set to True, results are stored in volatile table,
                otherwise not.
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
                SQLE Engine function supports, else an exception is raised.

    RETURNS:
        Instance of ConvertTo.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ConvertToObj.<attribute_name>.
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
        load_example_data("teradataml", "titanic")

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example: Convert datatype of 'fare' to integer.
        obj = ConvertTo(data=titanic_data,
                        target_columns="fare", target_datatype="integer"
                       )

        # Print the result DataFrame.
        print(obj.result)

    """