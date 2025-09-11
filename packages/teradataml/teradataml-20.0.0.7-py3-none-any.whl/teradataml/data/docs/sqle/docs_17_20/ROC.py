def ROC(data=None, probability_column=None, observation_column=None, model_id_column=None, positive_class='1',
        num_thresholds=50, auc=True, gini=True, **generic_arguments):
    """
    DESCRIPTION:
        The Receiver Operating Characteristic (ROC) function accepts
        a set of prediction-actual pairs for a binary classification
        model and calculates the following values for a range
        of discrimination thresholds:
            * True positive rate (TPR)
            * False positive rate (FPR)
            * The area under the ROC curve (AUC)
            * Gini coefficient
        A receiver operating characteristic (ROC) curve shows the
        performance of a binary classification model as its discrimination
        threshold varies. For a range of thresholds, the curve plots the
        true positive rate against the false-positive rate.
        Notes:
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
              For information about PTCs, see Teradata Vantage™ - Analytics Database
              International Character Set Support.
            * This function does not support KanjiSJIS or Graphic data types.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame that contains the
            prediction-actual pairs for a binary classifier.
            Types: teradataml DataFrame

        probability_column:
            Required Argument.
            Specifies the input column in "data" that contains
            the predictions.
            Types: str

        observation_column:
            Required Argument.
            Specifies the input column in "data" that contains
            the actual classes.
            Types: str

        model_id_column:
            Optional Argument.
            Specifies the input column in "data" that contains the
            model or partition identifiers for the ROC curves.
            Types: str

        positive_class:
            Optional Argument.
            Specifies the label of the positive class.
            Default Value: '1'
            Types: str

        num_thresholds:
            Optional Argument.
            Specifies the number of threshold for the function to use. The
            "num_threshold" must be in the range [1, 10000]. The
            function uniformly distributes the thresholds between 0 and 1.
            Default Value: 50
            Types: int

        auc:
            Optional Argument.
            Specifies whether the function displays the AUC calculated from the
            ROC values(thresholds, false positive rates, and true positive rates).
            Default Value: True
            Types: bool

        gini:
            Optional Argument.
            Specifies whether the function displays the gini coefficient
            calculated from the ROC values.
            The Gini coefficient is an inequality measure among the values of
            a frequency distribution. A Gini coefficient of 0 indicates that
            all values are the same. The closer the Gini coefficient is to 1,
            the more unequal are the values in the distribution.
            Default Value: True
            Types: bool

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
        Instance of ROC.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ROCObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
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
        load_example_data("roc", ["roc_input"])

        # Create teradataml DataFrame objects.
        roc_input = DataFrame.from_table("roc_input")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1 : Calculating True-Positive Rate (TPR), False-Positive Rate (FPR),
        #             Area Under the ROC Curve (AUC), Gini Coefficient for a range
        #             of discrimination thresholds.
        roc_out = ROC(probability_column="probability",
                      observation_column="observation",
                      model_id_column="model_id",
                      positive_class="1",
                      data=roc_input)


        # Print the result DataFrame.
        print(roc_out.result)
        print(roc_out.output_data)

    """
