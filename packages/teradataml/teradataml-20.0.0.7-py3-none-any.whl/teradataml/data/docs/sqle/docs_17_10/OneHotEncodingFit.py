def OneHotEncodingFit(data=None, is_input_dense=None, target_column=None, categorical_values=None, other_column=None,
                      attribute_column=None, value_column=None, target_attributes=None, other_attributes=None,
                      **generic_arguments):
    """
    DESCRIPTION:
        Function records all the parameters required for OneHotEncodingTransform() function.
        Such as, target attributes and their categorical values to be encoded and other parameters.
        Output of OneHotEncodingFit() function is used by OneHotEncodingTransform() function for encoding
        the input data. It supports inputs in both sparse and dense format.
        Note:
            * For input to be considered as sparse input, column names must be provided for
             'data_partition_column' argument.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        is_input_dense:
            Required Argument.
            Specifies whether input is in dense format or sparse format.
            Types: boolean

        target_column:
            Required Argument when 'is_input_dense=True', disallowed otherwise.
            Specifies the name of the column in "data" to be encoded.
            Types: str

        categorical_values:
            Required Argument when 'is_input_dense=True', disallowed otherwise.
            Specifies the categorical values to encode in one-hot form.
            Types: str OR list of strs

        other_column:
            Required Argument when 'is_input_dense=True', disallowed otherwise.
            Specifies a category name for values that "categorical_values" does not specify
            (categorical values not to encode in one-hot form).
            Default Value: 'other'
            Types: str

        attribute_column:
            Required Argument when 'is_input_dense=False', disallowed otherwise.
            Specifies the name of the column in "data" which contains attribute
            names.
            Types: str

        value_column:
            Required Argument when 'is_input_dense=False', disallowed otherwise.
            Specifies the name of the column in "data" which contains attribute
            values.
            Types: str

        target_attributes:
            Required Argument when 'is_input_dense=False', disallowed otherwise.
            Specifies one or more attributes to encode in one-hot form. Every target attribute must
            be in "attribute_column".
            Types: str OR list of strs

        other_attributes:
            Optional Argument when 'is_input_dense=False', disallowed otherwise.
            For each target attribute, specifies a category name for attributes that "target_attributes"
            does not specify. The nth "other_attributes" corresponds to the nth "target_attribute".
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
        Instance of OneHotEncodingFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as OneHotEncodingFitObj.<attribute_name>.
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

        # Example 1: Generate fit object to encode "male" and "female" values of column "sex".
        fit_obj = OneHotEncodingFit(data=titanic_data,
                                    is_input_dense=True,
                                    target_column="sex",
                                    categorical_values=["male", "female"],
                                    other_column="other")

        # Print the result DataFrame.
        print(fit_obj.result)

    """