def Pack(data=None, input_columns=None, output_column=None, delimiter=",",
         include_column_name=True, col_cast=False, accumulate=None, **generic_arguments):
    """
    DESCRIPTION:
        The Pack() function packs data from multiple input DataFrame columns into a single column.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        input_columns:
            Optional Argument.
            Specifies the names of the input columns to pack into a single output
            column. These names become the column names of the virtual columns.
            By default, all input teradataml DataFrame columns are packed into a
            single output column. If you specify this argument, but do not
            specify all input teradataml DataFrame columns, the function copies
            the unspecified input tablecolumns to the output table.
            Types: str OR list of Strings (str)

        output_column:
            Required Argument.
            Specifies the name to give to the packed output column.
            Types: str

        delimiter:
            Optional Argument.
            Specifies the delimiter (a string) that separates the virtual columns
            in the packed data.
            Default Value: ","
            Types: str

        include_column_name:
            Optional Argument.
            Specifies whether to label each virtual column value with its column
            name (making the virtual column "input_column:value").
            Default Value: True
            Types: bool

        col_cast:
            Optional Argument.
            Specifies whether to get better elapsed times with use cases involving numeric
            columns to be packed.
            Default Value: False
            Types: bool

        accumulate:
            Optional Argument.
            Specifies the input teradataml DataFrame columns to copy to the
            output table. By default, the function copies no input teradataml
            DataFrame columns to the output table.
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
        Instance of Pack.
        Output teradataml DataFrames can be accessed using attribute
        references, such as PackObj.<attribute_name>.
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
        load_example_data("pack", ["ville_temperature"])

        # Create teradataml DataFrame object.
        ville_temperature = DataFrame.from_table("ville_temperature")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Packs data from multiple input DataFrame columns
        #            into a single column.
        obj = Pack(data=ville_temperature,
                   input_columns=['city','state','period','temp_f'],
                   output_column='packed_data',
                   delimiter=',',
                   accumulate='city',
                   include_column_name=True)

        # Print the result DataFrame.
        print(obj.result)


    """
