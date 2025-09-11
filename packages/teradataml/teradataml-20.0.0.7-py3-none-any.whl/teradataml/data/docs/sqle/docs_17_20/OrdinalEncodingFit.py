def OrdinalEncodingFit(data=None, category_data=None, target_column=None,
                       approach="AUTO", categories=None, ordinal_values=None,
                       target_column_names=None, categories_column=None,
                       ordinal_values_column=None, start_value=0, default_value=None,
                       **generic_arguments):
    """
    DESCRIPTION:
        OrdinalEncodingFit() function identifies distinct categorical
        values from the input data or a user-defined list and generates
        the distinct categorical values along with the ordinal value for
        each category.

        Notes:
            * Function requires the UTF8 client character set for UNICODE data.
            * Function does not support Pass Through Characters (PTCs).
            * Function does not support KanjiSJIS or Graphic data types.
            * The maximum number of unique categories in a particular column is 4000.
            * The maximum category length is 128 characters.
            * NULL categories are not encoded.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input data containing the categorical target column.
            Types: teradataml DataFrame

        category_data:
            Optional Argument.
            Specifies the data containing the input categories for 'LIST' approach.
            Types: teradataml DataFrame

        target_column:
            Required Argument.
            Specifies the name of the categorical input target column.
            Note:
                The maximum number of unique columns in the "target_column" argument is 2018.
            Types: str OR list of Strings (str)

        approach:
            Optional Argument.
            Specifies whether to determine categories automatically from the
            input data (AUTO approach) or determine categories from the list
            provided by user (LIST approach).
            Default Value: "AUTO"
            Permitted Values: AUTO, LIST
            Types: str

        categories:
            Optional Argument.
            Specifies the list of categories that need to be encoded in the
            desired order.
            Notes:
                * If only one target column is provided, category values
                  read from this argument. Otherwise, they read from the
                  "category_data".
                * Required, when user use the 'LIST' approach and a single
                  target column.
            Types: str OR list of strs

        ordinal_values:
            Optional Argument.
            Specifies the custom ordinal values to replace the categories,
            when user use the 'LIST' approach for encoding the categorical values.
            If user does not provide the "ordinal_values" and the "start_value",
            then by default, the first category contains the default start value
            '0', and the last category is assigned a value that is one lesser than
            the total number of categories.
            For example, if there are three categories, then the categories contain
            the values 0, 1, 2 respectively.

            However, if user only specify the ordinal values, then each ordinal value
            is associated with a categorical value. For example, if there are three categories
            and the ordinal values are 3, 4, 5 then the ordinal values are assigned to the
            respective categories.
            The OrdinalEncodingFit() function returns an error when the ordinal value
            count does not match the categorical value count or if both the ordinal
            values and the start value are provided.
            Notes:
                * User can either use the "ordinal_values" or the "start_value" argument
                  in the syntax.
                * If only one target column is provided, ordinal values are read from this argument.
                  Otherwise, they are read from the "category_data".
                * If omitted, ordinal values are generated based on the "start_value" argument.
            Types: int OR list of ints

        target_column_names:
            Required when "category_data" is used, optional otherwise.
            Specifies the "category_data" column which contains the names of the
            target columns.
            Types: str

        categories_column:
            Required when "category_data" is used, optional otherwise.
            Specifies the "category_data" column which contains the category values.
            Types: str

        ordinal_values_column:
            Required when "category_data" is used, optional otherwise.
            Specifies the "category_data" column which contains the ordinal values.
            If omitted, ordinal values will be generated based on the "start_value"
            argument.
            Types: str

        start_value:
            Optional Argument.
            Specifies the starting value for ordinal values list.
            Default Value: 0
            Types: int

        default_value:
            Optional Argument.
            Specifies the ordinal value to use when category is not found.
            Types: int

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept. Below
            are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the
                    function in a table or not. When set to True,
                    results are persisted in a table; otherwise,
                    results are garbage collected at the end of the
                    session.
                    Default Value: False
                    Types: bool

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the
                    function in a volatile table or not. When set to
                    True, results are stored in a volatile table,
                    otherwise not.
                    Default Value: False
                    Types: bool

            Function allows the user to partition, hash, order or local
            order the input data. These generic arguments are available
            for each argument that accepts teradataml DataFrame as
            input and can be accessed as:
                * "<input_data_arg_name>_partition_column" accepts str or
                    list of str (Strings)
                * "<input_data_arg_name>_hash_column" accepts str or list
                    of str (Strings)
                * "<input_data_arg_name>_order_column" accepts str or list
                    of str (Strings)
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if
                the underlying SQL Engine function supports, else an
                exception is raised.

    RETURNS:
        Instance of OrdinalEncodingFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as OrdinalEncodingFitObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
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
        load_example_data("teradataml", ["titanic","cat_table"])

        # Create teradataml DataFrame objects.
        titanic = DataFrame.from_table("titanic")
        cat_data = DataFrame.from_table("cat_table")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Identyfying distinct categorical values from the input.
        ordinal_encodingfit_res_1 = OrdinalEncodingFit(target_column='sex',
                                                       data=titanic)

        # Print the result DataFrame.
        print(ordinal_encodingfit_res_1.result)

        # Example 2: Identifying distinct categorical values from the input and
        #            returns the distinct categorical values along with the ordinal
        #            value for each category.
        ordinal_encodingfit_res_2 = OrdinalEncodingFit(target_column='sex',
                                                       approach='LIST',
                                                       categories=['category0', 'category1'],
                                                       ordinal_values=[1, 2],
                                                       start_value=0,
                                                       default_value=-1,
                                                       data=titanic)

        # Print the result DataFrame.
        print(ordinal_encodingfit_res_2.result)

        # Example 3: Provide ordinal values to "target_column" using
        #            dataset by "category_data".
        ordinal_encodingfit_res_3 = OrdinalEncodingFit(target_column=['name','sex','ticket','cabin','embarked'],
                                                       category_data=cat_data,
                                                       approach='LIST',
                                                       target_column_names="column_name",
                                                       categories_column="category",
                                                       ordinal_values_column="ordinal_value",
                                                       default_value=[-1, -10, -15, 20, 0],
                                                       data=titanic)

        # Print the result DataFrame.
        print(ordinal_encodingfit_res_3.result)

        """