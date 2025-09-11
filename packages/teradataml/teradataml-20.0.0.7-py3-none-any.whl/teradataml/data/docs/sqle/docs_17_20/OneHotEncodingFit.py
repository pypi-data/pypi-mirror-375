def OneHotEncodingFit(data=None, category_data=None, target_column=None,
                      attribute_column=None, value_column=None, is_input_dense=None,
                      approach="LIST", categorical_values=None, target_column_names=None,
                      categories_column=None, other_column="other", category_counts=None,
                      target_attributes=None, other_attributes=None, **generic_arguments):
    """
    DESCRIPTION:
        The OneHotEncodingFit() function outputs a DataFrame of attributes and categorical
        values to input to OneHotEncodingTransform() function, which encodes them as
        one-hot numeric vectors.
        Notes:
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
            * This function does not support KanjiSJIS or Graphic data types.
            * For input to be considered as sparse input, column names should be
              provided for 'data_partition_column' argument.
            * In case of dense input, only allowed value for 'data_partition_column'
              is PartitionKind.ANY and that for 'category_data_partition_column' is
              PartitionKind.DIMENSION.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        category_data:
            Optional Argument.
            Specifies the data containing the input categories for 'LIST' approach.
            Types: teradataml DataFrame

        target_column:
            Required when "is_input_dense" is set to 'True', disallowed otherwise.
            Specifies the name of the column in "data" to be encoded.
            Note:
                * The maximum number of unique columns in the "target_column"
                  argument is 2018.
            Types: str OR list of Strings (str)

        attribute_column:
            Required when "is_input_dense" is set to 'False', disallowed otherwise.
            Specifies the name of the column in "data" which contains attribute
            names.
            Types: str

        value_column:
            Required when "is_input_dense" is set to 'False', disallowed otherwise.
            Specifies the name of the column in "data" which contains attribute
            values.
            Types: str

        is_input_dense:
            Required Argument.
            Specifies whether input is in dense format or sparse format.
            Note:
                "category_data" is meant for dense input format and not for sparse format.
            Types: bool

        approach:
            Optional Argument.
            Specifies whether to determine categories automatically from the
            input data (AUTO approach) or the user provided list (LIST approach).
            Default Value: "LIST"
            Permitted Values: AUTO, LIST
            Types: str

        categorical_values:
            Required when "approach" is set to 'LIST' and a single value
            is present in "target_column", optional otherwise.
            Specifies the list of categories that need to be encoded in
            the desired order.
            When only one target column is provided, category values are read
            from this argument. Otherwise, they will be read from the
            "category_data".
            Notes:
                * The number of characters in "target_column_names" plus the
                  number of characters in the category specified in the
                  "categorical_values" argument must be less than 128 characters.
                * The maximum number of categories in the "categorical_values"
                  argument is 2018.
            Types: str OR list of Strings (str)

        target_column_names:
            Required when "category_data" is used, optional otherwise.
            Specifies the "category_data" column which contains the
            names of the target columns.
            Types: str

        categories_column:
            Required when "category_data" is used, optional otherwise.
            Specifies the "category_data" column which contains the
            category values.
            Types: str

        other_column:
            Optional when "is_input_dense" is set to 'True', disallowed otherwise.
            Specifies the column name for the column representing one-hot encoding
            for values other than the ones specified in the "categorical_values"
            argument or "category_data" or categories found through the 'auto'
            approach.
            Default Value: 'other'
            Types: str

        category_counts:
            Required when "category_data" is used or "approach" is
            set to 'auto', optional otherwise.
            Specifies the category counts for each of the "target_column".
            The number of values in "category_counts" should be the same
            as the number of "target_column".
            Types: str OR list of Strings (str)

        target_attributes:
            Required when "is_input_dense" is set to 'False', disallowed otherwise.
            Specifies one or more attributes to encode in one-hot form. Every target attribute must
            be in "attribute_column".
            Types: str OR list of Strings (str)

        other_attributes:
            Optional when "is_input_dense" is set to 'False', disallowed otherwise.
            For each target attribute, specifies a category name for attributes that "target_attributes"
            does not specify. The nth "other_attributes" corresponds to the nth "target_attribute".
            Notes:
                * The number of characters in values specified in the "target_attributes" argument
                  plus the number of characters in values specified in the "other_attributes"
                  argument must be less than 128 characters.
                * The number of values passed to the "target_attributes" argument and "other_attributes"
                  argument must be equal.
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
                SQL Engine function supports, else an exception is raised.


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
        load_example_data("teradataml", ["titanic", "cat_table"])

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")
        cat_data = DataFrame.from_table("cat_table")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Generate fit object to encode 'male' and 'female' values of column 'sex'.
        fit_obj1 = OneHotEncodingFit(data=titanic_data,
                                     is_input_dense=True,
                                     target_column="sex",
                                     categorical_values=["male", "female"],
                                     other_column="other")

        # Print the result DataFrame.
        print(fit_obj1.result)

        # Example 2: Generate fit object to encode column 'sex' and 'embarked' in dataset.
        fit_obj2 = OneHotEncodingFit(data=titanic_data,
                                     is_input_dense=True,
                                     approach="auto",
                                     target_column=["sex", "embarked"],
                                     category_counts=[2, 3],
                                     other_column="other")
        # Print the result DataFrame.
        print(fit_obj2.result)

        # Example 3: Generate fit object when "category_data" is used.
        fit_obj3 = OneHotEncodingFit(data=titanic_data,
                                     category_data=cat_data,
                                     target_column_names="column_name",
                                     categories_column="category",
                                     is_input_dense=True,
                                     target_column=["sex", "embarked", "name"],
                                     category_counts=[2, 4, 6],
                                     other_column="other")
        # Print the result DataFrame.
        print(fit_obj3.result)

        # Example 4: Generate fit object when "approach" is set to 'LIST'.
        fit_obj4 = OneHotEncodingFit(data=titanic_data,
                                     is_input_dense=True,
                                     approach="list",
                                     categorical_values=['male','female'],
                                     target_column=["sex"],
                                     other_column="other")
        # Print the result DataFrame.
        print(fit_obj4.result)
    """