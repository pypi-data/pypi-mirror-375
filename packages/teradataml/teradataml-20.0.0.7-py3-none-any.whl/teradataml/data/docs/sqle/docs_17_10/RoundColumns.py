def RoundColumns(data=None, target_columns=None, precision_digit=0, accumulate=None, **generic_arguments):
    """
    DESCRIPTION:
        Function to round the values of each specified input DataFrame column to a
        specified number of decimal places.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" to round every value to
            precision digits.
            Types: str OR list of Strings (str)

        precision_digit:
            Optional Argument.
            Specifies the number of decimal places to which to round values for
            the "target_columns".
            If positive, the function rounds values to the right of the decimal point.
            If negative, the function rounds values to the left of the decimal point.
            If not provided, the function rounds the column values to 0 places.
            Note:
                If the column values have the DECIMAL/NUMERIC data type with a precision less
                than 38, then the function increases the precision by 1. For example, when a
                DECIMAL (4,2) value of 99.99 is rounded to 0 places, the function returns a
                DECIMAL (5,2) value, 100.00. However, if the precision is 38, then the function
                only reduces the scale value by 1 unless the scale is 0. For example, the
                function returns a DECIMAL (38, 36) value of 99.999999999 as a DECIMAL
                (38, 35) value, 100.00.
            Default Value: 0
            Types: int

        accumulate:
            Optional Argument.
            Specifies the names of input teradataml DataFrame columns to copy to the output.
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
                SQLE Engine function supports, else an exception is raised.

    RETURNS:
        Instance of RoundColumns.
        Output teradataml DataFrames can be accessed using attribute
        references, such as RoundColumnsObj.<attribute_name>.
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


        # Example 1: Rounding "fare" column to 2 decimal places.
        obj = RoundColumns(data=titanic_data,
                           target_columns="fare",
                           precision_digit=2,
                           accumulate=['pclass', 'sex'])

        # Print the result DataFrame.
        print(obj.result)
    """