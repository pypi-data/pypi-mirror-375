def NumApply(data=None, target_columns=None, output_columns=None, accumulate=None, apply_method=None,
             sigmoid_style=None, in_place=None, **generic_arguments):
    """
    DESCRIPTION:
        Apply predefined numeric operation on specified target columns.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" to perform numeric operations on.
            Types: str OR list of Strings (str)

        apply_method:
            Required Argument.
            Specifies the numeric operator/method.
            Permitted Values:
                * EXP - Raises e (base of natural logarithms) to power of value,
                        where e = 2.71828182845905.
                * LOG - Computes base 10 logarithm of value.
                * SIGMOID - Applies sigmoid function to value. See "sigmoid_style".
                * SININV - Computes inverse hyperbolic sine of value.
                * TANH - Computes hyperbolic tangent of value.
            Types: str

        in_place:
            Optional Argument.
            Specifies whether the output columns have the same names as the target columns.
            When set to True, function effectively replaces each value in each target column
            with the result of applying "apply_method" to it, otherwise copies the target
            columns to the output and adds output columns whose values are the result of
            applying "apply_method" to each value.
            No target columns can be part of the "accumulate" column.
            Default Value: True
            Types: boolean

        output_columns:
            Optional Argument.
            Specifies the name(s) of the output column(s) to be generated.
            An output column name cannot exceed 128 characters.
            By default, with "in_place" set to False, 'target_column_operator'; otherwise same as
            "target_column" names.
            Notes:
                1. If any 'target_column_operator' exceeds 128 characters, specify an "output_column" for each
                   target_column.
                2. Ignored with "in_place" set to True.
            Types: str OR list of strs

        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to copy to the output.
            Types: str OR list of Strings (str)

        sigmoid_style:
            Optional Argument, required when "apply_method" is 'sigmoid'.
            Specifies the sigmoid style.
            Permitted Values:
                * LOGIT
                * MODIFIEDLOGIT
                * TANH
            Default Value: LOGIT
            Types: str

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
        Instance of NumApply.
        Output teradataml DataFrames can be accessed using attribute
        references, such as NumApplyObj.<attribute_name>.
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
        load_example_data("teradataml", ["numerics"])

        # Create teradataml DataFrame object.
        numerics = DataFrame.from_table("numerics")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Apply "log" method to column "num1" in numerics.
        obj = NumApply(data=numerics,
                       target_columns="integer_col",
                       apply_method="log",
                       in_place=True)

        # Print the result DataFrame.
        print(obj.result)

        # Example 2: Apply "sigmoid" method and "tanh" as sigmoid style.
        obj = NumApply(data=numerics,
                       target_columns="decimal_col",
                       output_columns="out1",
                       apply_method="sigmoid",
                       sigmoid_style="tanh",
                       in_place=False)

        # Print the result DataFrame.
        print(obj.result)
    """
