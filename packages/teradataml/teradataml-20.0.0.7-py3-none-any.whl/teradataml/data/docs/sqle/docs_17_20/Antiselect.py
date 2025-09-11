def Antiselect(data=None, exclude=None, **generic_arguments):
    """
    DESCRIPTION:
        Antiselect() function returns all columns except those specified in the Exclude syntax element.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        exclude:
            Required Argument.
            Specifies the names of the columns not to return.
            Types: str OR list of Strings (str)

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or not.
                    When set to True, results are persisted in a table; otherwise, results
                    are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table or not.
                    When set to True, results are stored in a volatile table, otherwise not.
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
                These generic arguments are supported by teradataml if the underlying SQL Engine
                function supports, else an exception is raised.

    RETURNS:
        Instance of Antiselect.
        Output teradataml DataFrames can be accessed using attribute
        references, such as AntiselectObj.<attribute_name>.
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
        load_example_data("antiselect", ["antiselect_input"])

        # Create teradataml DataFrame object.
        antiselect_input = DataFrame.from_table("antiselect_input")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Returns all columns except those specified in the exclude argument.
        obj = Antiselect(data=antiselect_input,
                         exclude=['rowids', 'orderdate', 'discount', 'province', 'custsegment'])

        # Print the result.
        print(obj.result)

    """