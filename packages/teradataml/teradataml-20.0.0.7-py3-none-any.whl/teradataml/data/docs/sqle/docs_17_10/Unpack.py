def Unpack(data=None, input_column=None,
           output_columns=None, output_datatypes=None,
           delimiter=",", column_length=None,
           regex="(.*)", regex_set=1, exception=False,
           accumulate=None, **generic_arguments):
    """
    DESCRIPTION:
        The Unpack() function unpacks data from a single packed column into
        multiple columns. The packed column is composed of multiple virtual columns,
        which become the output columns. To determine the virtual  columns, the function
        must have either the delimiter that separates them in the packed column or their
        lengths.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the teradataml DataFrame containing the input attributes.
            Types: teradataml DataFrame

        input_column:
            Required Argument.
            Specifies the name of the input column that contains the packed data.
            Types: str

        output_columns:
            Required Argument.
            Specifies the names to give to the output columns, in the order in
            which the corresponding virtual columns appear in "input_column". If you
            specify fewer output column names than there are in virtual input
            columns, the function ignores the extra virtual input columns. That
            is, if the packed data contains x+y virtual columns and the
            "output_columns" argument specifies x output column names, the function
            assigns the names to the first x virtual columns and ignores the
            remaining y virtual columns.
            Types: str OR list of Strings (str)

        output_datatypes:
            Required Argument.
            Specifies the datatypes of the unpacked output columns.Supported
            output.datatypes are VARCHAR, int, float, TIME, DATE, and
            TIMESTAMP. If "output_datatypes" specifies only one value and
            "output_columns" specifies multiple columns, then the specified value
            applies to every output_column. If "output_datatypes" specifies
            multiple values, then it must specify a value for each output_column.
            The nth datatype corresponds to the nth output_column.The function
            can output only 16 VARCHAR columns.
            Types: str OR list of Strings (str)

        delimiter:
            Optional Argument.
            Specifies the delimiter (a string) that separates the virtual
            columns in the packed data. If the virtual columns are separated by a
            delimiter, then specify the delimiter with this argument; otherwise, specify
            the "column_length" argument. Do not specify both - this argument and
            the "column_length" argument.
            Default Value: ","
            Types: str

        column_length:
            Optional Argument.
            Specifies the lengths of the virtual columns; therefore, to use this
            argument, you must know the length of each virtual column. If
            "column_length" specifies only one value and "output_columns" specifies
            multiple columns, then the specified value applies to every
            output_column. If "column_length" specifies multiple values, then it
            must specify a value for each output_column. The nth datatype
            corresponds to the nth output_column. However, the last column_name
            can be an asterisk (*), which represents a single virtual column that
            contains the remaining data. For example, if the first three virtual
            columns have the lengths 2, 1, and 3, and all remaining data belongs
            to the fourth virtual column, you can specify "column_length" as
            ("2", "1", "3", *). If you specify this argument, you must omit the
            delimiter argument.
            Types: str OR list of Strings (str)

        regex:
            Optional Argument.
            Specifies a regular expression that describes a row of packed data,
            enabling the function to find the data values. A row of packed data
            contains one data value for each virtual column, but the row might
            also contain other information (such as the virtual column name). In
            the "regex", each data value is enclosed in parentheses.
            For example, suppose that the packed data has two virtual columns,
            age and sex, and that one row of packed data is: age:34,sex:male The
            "regex" that describes the row is ".*:(.*)". The ".*:"
            matches the virtual column names, age and sex, and the "(.*)" matches
            the values, 34 and male. The default "regex" is "(.*)"
            which matches the whole string (between delimiters, if any). When
            applied to the preceding sample row, the default "regex" causes the function
            to return "age:34" and "sex:male" as data values. To represent multiple data
            groups in "regex", use multiple pairs of parentheses. By default, the last
            data group in "regex" represents the data value (other data groups are
            assumed to be virtual column names or unwanted data). If a different
            data group represents the data value, specify its group number with
            the "regex_set" argument.
            Default Value: "(.*)"
            Types: str

        regex_set:
            Optional Argument.
            Specifies the ordinal number of the data group in "regex" that represents the
            data value in a virtual column. By default, the last data group in "regex"
            represents the data value.
            For example, suppose that "regex" is: "([a-zA-Z]*):(.*)". If
            group number is "1", then "([a-zA-Z]*)" represents the data value. If
            group number is "2", then "(.*)" represents the data value.
            Default Value: 1
            Types: int

        exception:
            Optional Argument.
            Specifies whether the function ignores rows that contain invalid data;
            By default the function to fails if it encounters a row with invalid data.
            Default Value: False
            Types: bool

        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
            output. By default, the function copies no input teradataml
            DataFrame columns to the output.
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
                These generic arguments are supported by teradataml if the underlying
                SQLE function supports it, else an exception is raised.

    RETURNS:
        Instance of Unpack.
        Output teradataml DataFrames can be accessed using attribute
        references, such as UnpackObj.<attribute_name>.
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
        load_example_data("Unpack",["ville_tempdata","ville_tempdata1"])

        # Create teradataml DataFrame objects.
        ville_tempdata1 = DataFrame.from_table("ville_tempdata1")
        ville_tempdata = DataFrame.from_table("ville_tempdata")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Delimiter separates Virtual Columns.
        #           The input table, ville_tempdata, is a collection of temperature readings
        #           for two cities, Nashville and Knoxville, in the state of Tennessee.
        #           In the column of packed data, the delimiter comma (,) separates the virtual
        #           columns.
        unpack_out1 = Unpack(data=ville_tempdata,
                             input_column='packed_temp_data',
                             output_columns=['city','state','temp_f'],
                             output_datatypes=['varchar','varchar','real'],
                             delimiter=',',
                             regex='(.*)',
                             regex_set=1,
                             exception=True)

        # Print the results DataFrame.
        print(unpack_out1.result)

        # Example 2: No Delimiter separates Virtual Columns.
        #            The input, ville_tempdata1, contains same data as the previous example,
        #            except that no delimiter separates the virtual columns in the packed data.
        #            To enable the function to determine the virtual columns, the function call
        #            specifies the column lengths.
        unpack_out2 = Unpack(data=ville_tempdata1,
                             input_column='packed_temp_data',
                             output_columns=['city','state','temp_f'],
                             output_datatypes=['varchar','varchar','real'],
                             column_length=['9','9','4'],
                             regex='(.*)',
                             regex_set=1,
                             exception=True)

        # Print the results DataFrame.
        print(unpack_out2.result)
    """
