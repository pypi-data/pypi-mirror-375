def BincodeFit(data=None, fit_data=None, target_columns=None, method_type=None,
               nbins=None, label_prefix=None, target_colnames=None,
               minvalue_column=None, maxvalue_column=None, label_column=None,
               **generic_arguments):
    """
    DESCRIPTION:
        The BinCodeFit() function outputs a DataFrame of information to input to
        BinCodeTransform() function, which bin-codes the specified input DataFrame.
        Bin-coding is typically used to convert numeric data to categorical data by
        binning the numeric data into multiple numeric bins (intervals).
        The bins can have a fixed-width with auto-generated labels or can have variable
        widths and labels.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        fit_data:
            Optional Argument.
            Specifies the input teradataml DataFrame containing binning parameters for
            VARIABLE-WIDTH. It is not needed for EQUAL-WIDTH.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the input teradataml DataFrame columns to generate bins information
            and binning parameters on.
            Types: str OR list of Strings (str)

        method_type:
            Required Argument.
            Specifies the Method Type which will be used for histogram computation.
            Permitted Values: EQUAL-WIDTH, VARIABLE-WIDTH
            Types: str

        nbins:
            Optional Argument.
            Specifies the number of bins to be used when "method_type" is
            EQUAL-WIDTH. It is not needed for VARIABLE-WIDTH. If one value is provided,
            it applies to all target columns, if more than one value is
            specified, "nbins" values apply to "target_columns" in the order
            specified by the user.
            Types: int OR list of ints

        label_prefix:
            Optional Argument.
            Specify the label prefix to be used when MethodType is EQUAL-WIDTH. If
            one value is provided, it applies to all target columns. If more than
            one value is specified, "label_prefix" values apply to "target_columns"
            in the order specified by the user.
            Default Value:  target column names.
            Types: str OR list of strs

        target_colnames:
            Optional Argument.
            Specifies the "fit_data" column which contains column name for
            which bins are specified.
            Default Value: ColumnName.
            Types: str

        minvalue_column:
            Optional Argument.
            Specifies the "fit_data" column which contains Min Value for the
            specified bins.
            Default Value: MinValue.
            Types: str

        maxvalue_column:
            Optional Argument.
            Specifies the "fit_data" column which contains Max Value for the
            specified bins.
            Default Value: MaxValue.
            Types: str

        label_column:
            Optional Argument.
            Specifies the "fit_data" column which contains label for which
            bins are specified.
            Default Value: Label.
            Types: str

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or
                    not. When set to True, results are persisted in a table; otherwise,
                    results are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table
                    or not. When set to True, results are stored in a volatile table,
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
                SQLE function supports it, else an exception is raised.

    RETURNS:
        Instance of BincodeFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as BincodeFitObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. output
            2. output_data


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
        load_example_data("teradataml", ["titanic", "bin_fit_ip"])

        # Create teradataml DataFrame objects.
        titanic_data = DataFrame.from_table("titanic")
        bin_fit_ip = DataFrame.from_table("bin_fit_ip")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Transform the data using BincodeFit object with Variable-Width.
        bin_code_1 = BincodeFit(data=titanic_data,
                                fit_data=bin_fit_ip,
                                fit_data_order_column = ['minVal', 'maxVal'],
                                target_columns='age',
                                minvalue_column='minVal',
                                maxvalue_column='maxVal',
                                label_column='label',
                                method_type='Variable-Width',
                                label_prefix='label_prefix'
                               )

        # Print the result.
        print(bin_code_1.output)

        # Example 2: Transform the data using BincodeFit object with Equal-Width.
        bin_code_2 = BincodeFit(data=titanic_data,
                                target_columns='age',
                                method_type='Equal-Width',
                                nbins=2,
                                label_prefix='label_prefix'
                               )

        # Print the result.
        print(bin_code_2.output)

    """