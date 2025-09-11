def StrApply(data=None, target_columns=None, output_columns=None, accumulate=None, string_operation=None, operating_side=None,
             in_place=True, string=None, escape_string=None, is_case_specific=True, ignore_trailing_blank=False,
             string_length=None, start_index=None, **generic_arguments):
    """
    DESCRIPTION:
        StrApply() function applies a specified string operator to the specified input DataFrame columns.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data"
            to perform string operations on.
            Types: str OR list of Strings (str)

        output_columns:
            Optional Argument.
            Specifies the output column names that contains the output of the
            string operation on the columns values.
            Types: str OR list Strings (str)

        accumulate:
            Optional Argument.
            Specifies the names of input teradataml DataFrame columns to copy to
            the output.
            Types: str OR list of Strings (str)

        string_operation:
            Required Argument.
            Specifies the string method to use on the target columns.
            Permitted Values:
                * TOUPPER
                * TOLOWER
                * strTRIM
                * strCON
                * strPAD
                * strLIKE
                * strINDEX
                * INITCAP
                * TRIMSPACES
                * CHARTOHEXINT
                * strREVERSE
                * SUBstr
                * GETNCHARS
                * UNICODEstr
            Types: str

        operating_side:
            Optional Argument.
            Specifies the operating side to consider while performing operations
            like 'stringPad', 'getNchars'.
            Permitted Values: LEFT, RIGHT
            Default Value: LEFT
            Types: str

        in_place:
            Optional Argument.
            Specifies whether to use the same column name for the resulted target
            columns.
            Default Value: True
            Types: bool

        string:
            Optional Argument.
            Specifies the names of the strings to use as input while applying
            string operation.
            Types: str OR list of Strings (str)

        escape_string:
            Optional Argument.
            Specifies the names of the string to use as an escape string while
            applying stringLike operation.
            Types: str OR list of Strings (str)

        is_case_specific:
            Optional Argument.
            Specifies whether to consider uppercase letters(e.g. "A") and lowercase
            letters(e.g. "a") as same or different.
            Default Value: True
            Types: bool

        ignore_trailing_blank:
            Optional Argument.
            Specifies whether to ignore trailing blanks in the column strings. Used
            if the stringOperation is 'StringLike' only.
            Default Value: False
            Types: bool

        string_length:
            Optional Argument.
            Specifies the length of a string.
            Types: int

        start_index:
            Optional Argument.
            Specifies the start index of the target column string. Used only if
            the string operation is 'SubString'.
            Types: int

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
                These generic arguments are supported by teradataml if the underlying SQLE Engine
                function supports it, else an exception is raised.

    RETURNS:
        Instance of StrApply.
        Output teradataml DataFrames can be accessed using attribute
        references, such as StrApplyObj.<attribute_name>.
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

        # Example 1: Apply 'TOUPPER' string operator to the
        #            specified input "name" columns.
        obj = StrApply(data=titanic_data,
                       target_columns='name',
                       string_operation='TOUPPER',
                       in_place=False)

        # Print the result DataFrame.
        print(obj.result)

        # Example 2: Apply StrApply using all the arguments.
        obj = StrApply(data=titanic_data,
                       data_partition_column='age',
                       data_order_column='age',
                       target_columns='name',
                       accumulate='passenger',
                       output_columns='str_op_output',
                       string_operation='TOUPPER',
                       in_place=False,
                       persist=True)

        # Print the result DataFrame.
        print(obj.result)

    """
