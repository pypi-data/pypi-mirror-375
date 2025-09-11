def ClassificationEvaluator(data=None,
                            observation_column=None,
                            prediction_column=None,
                            num_labels=None,
                            labels=None,
                            **generic_arguments):
    """
    DESCRIPTION:
        In classification problems, a confusion matrix is used to visualize the
        performance of a classifier. The confusion matrix contains predicted labels
        represented across the row-axis and actual labels represented across the column-axis.
        Each cell in the confusion matrix corresponds to the count of occurrences
        of labels in the test data. The ClassificationEvaluator() function evaluate
        and emits various metrics of classification model based on its predictions on the data.
        Apart from accuracy, the secondary output data returns micro, macro, and weighted-averaged
        metrics of precision, recall, and F1-score values.
        Notes:
             * The function works for multi-class scenarios as well. In any case, the
               primary output data contains class-level metrics, whereas the secondary
               output data contains metrics that are applicable across classes.
             * The function works only when columns specified in 'observation_column'
               and 'prediction_column' has same teradata types.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the teradataml DataFrame, containing expected and predicted labels.
            Types: teradataml DataFrame

        observation_column:
            Required Argument.
            Specifies the column name in "data" containing observation labels.
            Types: str

        prediction_column:
            Required Argument.
            Specifies the column name in "data" containing predicted labels.
            Types: str

        num_labels:
            Optional Argument.
            Specifies the number of labels in the dataset.
            Note:
                Argument is ignored if "labels" argument is used.
            Allowed Values: 1 <= num_labels <= 512
            Types: int

        labels:
            Optional Argument.
            Specifies the list of all predicted labels in the input.
            Provide either "num_labels" argument or "labels" argument.
            Types: str OR list of str

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
        Instance of ClassificationEvaluator.
        Output teradataml DataFrames can be accessed using attribute
        references, such as  ClassificationEvaluatorObj.<attribute_name>.
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

        # Example 1 : Evaluate the classification model generated to predict the labels
        #             'crash', 'nocrash' using the predicted data.

        # Load the example data.
        load_example_data("textparser", ["complaints", "stop_words"])

        # Create teradataml DataFrame objects.
        complaints = DataFrame.from_table("complaints")
        stop_words = DataFrame.from_table("stop_words")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Tokenize the "text_column" and accumulate result by "doc_id" and "category".
        complaints_tokenized = TextParser(data=complaints,
                                          text_column="text_data",
                                          object=stop_words,
                                          remove_stopwords=True,
                                          accumulate=["doc_id", "category"])

        # Calculate the conditional probabilities for token-category pairs.
        NaiveBayesTextClassifierTrainer_out = NaiveBayesTextClassifierTrainer(data=complaints_tokenized.result,
                                                                              token_column="token",
                                                                              doc_category_column="category")

        # Print the result DataFrames.
        print(NaiveBayesTextClassifierTrainer_out.result)
        print(NaiveBayesTextClassifierTrainer_out.model_data)

        # Score the data using NaiveBayesTextClassifierPredict() on model generated by
        # NaiveBayesTextClassifier() where model_type is "MULTINOMIAL".
        nbt_predict_out = NaiveBayesTextClassifierPredict(object = NaiveBayesTextClassifierTrainer_out.model_data,
                                                          newdata = complaints_tokenized.result,
                                                          input_token_column = 'token',
                                                          accumulate="category",
                                                          doc_id_columns = 'doc_id')

        # Print the result DataFrame.
        print(nbt_predict_out.result)

        # Convert prediction column and category column to same DataType.
        predicted_data = ConvertTo(data = nbt_predict_out.result,
                                   target_columns = ["category", "prediction"],
                                   target_datatype = ["VARCHAR(charlen=20,charset=UNICODE,casespecific=NO)"])

        # Evaluate classification.
        ClassificationEvaluator_obj = ClassificationEvaluator(data=predicted_data.result,
                                                              observation_column='category',
                                                              prediction_column='prediction',
                                                              labels=['no_crash','crash'])

        # Print the result DataFrames.
        print(ClassificationEvaluator_obj.result)
        print(ClassificationEvaluator_obj.output_data)
    """
