def DecisionTreePredict(object = None, newdata = None, attr_table_groupby_columns = None,
                        attr_table_pid_columns = None, attr_table_val_column = None,
                        output_response_probdist = False, accumulate = None,
                        output_responses = None, **generic_arguments):
    """
    DESCRIPTION:
        The DecisionTreePredict() function applies a tree model to a data
        input, outputting predicted labels for each data point.

    PARAMETERS:
        object:
            Required Argument.
            Specifies the name of the teradataml DataFrame containing the output
            model from DecisionTree() function or instance of DecisionTree.
            Types: teradataml DataFrame or DecisionTree

        newdata:
            Required Argument.
            Specifies the name of the teradataml DataFrame containing the
            attribute names and the values.
            Types: teradataml DataFrame

        attr_table_groupby_columns:
            Required Argument.
            Specifies the names of the columns on which newdata is
            partitioned. Each partition contains one attribute of the input data.
            Types: str OR list of Strings (str)

        attr_table_pid_columns:
            Required Argument.
            Specifies the names of the columns that define the data point
            identifiers.
            Types: str OR list of Strings (str)

        attr_table_val_column:
            Required Argument.
            Specifies the name of the column that contains the input values.
            Types: str

        output_response_probdist:
            Optional Argument.
            Specifies whether to output probabilities.
            Note: "output_response_probdist" argument can accept input value True
                  only when teradataml is connected to Vantage 1.0 Maintenance
                  Update 2 version or later.
            Default Value: False
            Types: bool

        accumulate:
            Optional Argument.
            Specifies the names of input_table columns to copy to the output
            teradataml DataFrame.
            Types: str OR list of Strings (str)

        output_responses:
            Optional Argument.
            Required if output_response_probdist is True.
            Specifies all responses in newdata.
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
        Instance of DecisionTreePredict.
        Output teradataml DataFrames can be accessed using attribute
        references, such as DecisionTreePredictObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result

    RAISES:
        TeradataMlException, TypeError, ValueError

    EXAMPLES:
        # Notes:
        #    1. Get the connection to Vantage, before importing the function in user space.
        #    2. User can import the function, if it is available on the Vantage user is connected to.
        #    3. To check the list of analytic functions available on the Vantage user connected to,
        #       use "display_analytic_functions()"

        # Load the example data.
        load_example_data("DecisionTreePredict", ["iris_attribute_train",
        "iris_response_train", "iris_attribute_test"])

        # Create teradataml DataFrame objects.
        iris_attribute_test = DataFrame.from_table("iris_attribute_test")
        iris_attribute_train = DataFrame.from_table("iris_attribute_train")
        iris_response_train = DataFrame.from_table("iris_response_train")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Import function DecisionTreePredict.
        from teradataml import DecisionTreePredict

        # Example 1: First train the data, i.e., create a decision tree Model and then
        #            run predict on the output of decision tree.
        td_decision_tree_out  = DecisionTree(attribute_name_columns = 'attribute',
                                             attribute_value_column = 'attrvalue',
                                             id_columns = 'pid',
                                             attribute_table = iris_attribute_train,
                                             response_table = iris_response_train,
                                             response_column = 'response',
                                             approx_splits = False,
                                             num_splits = 3,
                                             nodesize = 10,
                                             max_depth = 10,
                                             weighted = False,
                                             split_measure = "gini",
                                             output_response_probdist = False)

        # Run predict on the output of DecisionTree.
        decision_tree_predict_out = DecisionTreePredict(newdata=iris_attribute_test,
                                                        newdata_partition_column='pid',
                                                        object=td_decision_tree_out,
                                                        attr_table_groupby_columns='attribute',
                                                        attr_table_pid_columns='pid',
                                                        attr_table_val_column='attrvalue',
                                                        accumulate='pid',
                                                        output_response_probdist=False,
                                                        output_responses=['pid','attribute'])

        # Print output DataFrame.
        print(decision_tree_predict_out.result)

    """