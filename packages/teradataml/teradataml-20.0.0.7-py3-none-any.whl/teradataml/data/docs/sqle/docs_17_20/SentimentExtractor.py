def SentimentExtractor(data=None, cust_dict=None, add_dict=None, text_column=None,
                       accumulate=None, analysis_type="DOCUMENT", priority="NONE",
                       output_type="ALL", **generic_arguments):
    """
    DESCRIPTION:
        The SentimentExtractor() function uses a dictionary model
        to extract the sentiment (positive, negative, or neutral)
        of each input document or sentence.

        The dictionary model consists of WordNet, a lexical database
        of the English language, and these negation words (no, not,
        neither, never, and similar negation words).

        The function handles negated sentiments as follows:
            * -1 if the sentiment is negated (for example, "I am not happy")
            * -1 if the sentiment and a negation word are separated by one
              word (for example, "I am not very happy")
            * +1 if the sentiment and a negation word are separated by two
              or more words (for example, "I am not saying I am happy")
        Notes:
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
            * For information about PTCs, see Teradata Vantage™ - Analytics Database
              International Character Set Support.
            * This function does not support KanjiSJIS or Graphic data types.
            * Only the English language is supported.
            * The max length supported for sentiment word in the dictionary data
              is 128 characters.
            * The Max length of the sentiment_words output column is 32000 characters.
              If the sentiment_words output column value exceeds this limit, then a
              triple dot(...) displays at the end of the string.
            * The Max length of the content output column is 32000 characters;
              that is, the supported maximum length of a sentence is 32000.
            * User can have up to 10 words in a sentiment phrase.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        cust_dict:
            Optional Argument.
            Specifies the input teradataml DataFrame containing custom dictionary data,
            to use non-default custom dictionary data.
            Types: teradataml DataFrame

        add_dict:
            Optional Argument.
            Specifies the input teradataml DataFrame containing additional entries,
            to add additional entries to either "cust_dict"
            or default dictionary.
            Types: teradataml DataFrame

        text_column:
            Required Argument.
            Specifies the "data" column that contains the text data
            for sentiment analysis.
            Types: str

        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s)
            to copy to the output. By default, the function copies no
            input teradataml DataFrame columns to the output.
            Types: str OR list of Strings (str)

        analysis_type:
            Optional Argument.
            Specifies the level of analysis, whether to analyze each document
            or each sentence in a document.
            Permitted Values:
                * DOCUMENT - Analyzes each document.
                * SENTENCE - Analyzes each sentence in a document.
            Default Value: "DOCUMENT"
            Types: str

        priority:
            Optional Argument.
            Specifies the highest priority when returning results.
            Permitted Values: 
                * NONE - Provide all results the same priority.
                * NEGATIVE_RECALL - Provide the highest priority to negative
                                    results, including those with lower-confidence
                                    sentiment classifications (maximizes number of
                                    negative results returned).
                * NEGATIVE_PRECISION - Provide the highest priority to negative
                                       results with high-confidence sentiment classifications.
                * POSITIVE_RECALL - Provide the highest priority to positive results,
                                    including those with lower-confidence sentiment
                                    classifications (maximizes number of positive results returned).
                * POSITIVE_PRECISION - Provide the highest priority to positive results with high
                                       confidence sentiment classifications.
            Default Value: "NONE"
            Types: str

        output_type:
            Optional Argument.
            Specifies the kind of results to return.
            Permitted Values:
                * ALL - Returns all results.
                * POS - Returns only results with positive sentiments.
                * NEG - Returns only results with negative sentiments.
                * NEU - Returns only results with neutral sentiments.
            Default Value: "ALL"
            Types: str

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
        Instance of SentimentExtractor.
        Output teradataml DataFrames can be accessed using attribute
        references, such as SentimentExtractorObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. output_dictionary_data


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
        load_example_data("sentimentextractor", ["sentiment_extract_input",
                                                  "sentiment_word_input",
                                                  "additional_table"])

        # Create teradataml DataFrame objects.
        sentiment_extract_input = DataFrame.from_table("sentiment_extract_input")
        sentiment_word_input = DataFrame.from_table("sentiment_word_input")
        additional_table = DataFrame.from_table("additional_table")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1 : Extracting the sentiment (positive, negative, or neutral)
        #             of each input document or sentence.
        sentimentextractor_out = SentimentExtractor(text_column="review",
                                                    data=sentiment_extract_input)

        # Print the result DataFrame.
        print(sentimentextractor_out.result)
        print(sentimentextractor_out.output_dictionary_data)

        # Example 2 : Extracting the sentiment (positive, negative, or neutral)
        #             of each input document by specifying custom dictionary data
        #             and adding additional entries to custom dictionary data.
        sentimentextractor_out_1 = SentimentExtractor(text_column="review",
                                                      accumulate=['id', 'product'],
                                                      analysis_type="DOCUMENT",
                                                      priority="NONE",
                                                      output_type="ALL",
                                                      data=sentiment_extract_input,
                                                      cust_dict=sentiment_word_input,
                                                      add_dict=additional_table)

        # Print the result DataFrame.
        print(sentimentextractor_out_1.result)
        print(sentimentextractor_out_1.output_dictionary_data)

    """
