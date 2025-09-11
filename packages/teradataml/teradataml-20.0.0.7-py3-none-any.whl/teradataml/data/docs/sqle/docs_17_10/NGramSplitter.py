def NGramSplitter(data=None, text_column=None, delimiter=" ", grams=None, overlapping=True, to_lower_case=True,
                  punctuation="`~#^&*()-", reset=".,?!", total_gram_count=False, total_count_column="totalcnt",
                  accumulate=None, n_gram_column="ngram", num_grams_column="n", frequency_column="frequency",
                  **generic_arguments):
    """
    DESCRIPTION:
        The NGramSplitter function tokenizes (splits) an input stream of text and
        outputs n multigrams (called n-grams) based on the specified
        delimiter and reset parameters. NGramSplitter provides more flexibility than
        standard tokenization when performing text analysis. Many two-word
        phrases carry important meaning (for example, "machine learning")
        that unigrams (single-word tokens) do not capture. This, combined
        with additional analytical techniques, can be useful for performing
        sentiment analysis, topic identification and document classification.

        Note: This function is only available when teradataml is connected
              to Vantage 1.1 or later versions.


    PARAMETERS:
        data:
            Required Argument.
            Specifies input teradataml DataFrame, where each row contains a document
            to be tokenized. The input teradataml DataFrame can have additional rows,
            some or all of which the function returns in the output table.
            Types: teradataml DataFrame

        text_column:
            Required Argument.
            Specifies the name of the column that contains the input text. The column
            must have a SQL string data type.
            Types: str

        delimiter:
            Optional Argument.
            Specifies a character or string that separates words in the input text. The
            default value is the set of all whitespace characters which includes
            the characters for space, tab, newline, carriage return and some
            others.
            Default Value: "[\\s]+"
            Types: str

        grams:
            Required Argument.
            Specifies the length, in words, of each n-gram (that is, the value of n).
            A value_range has the syntax integer1 - integer2, where integer1 <= integer2.
            The values of n, integer1, and integer2 must be positive.
            Types: str

        overlapping:
            Optional Argument.
            Specifies a Boolean value that specifies whether the function allows
            overlapping n-grams. When this value is "true" (the default), each
            word in each sentence starts an n-gram, if enough words follow it (in
            the same sentence) to form a whole n-gram of the specified size. For
            information on sentences, see the description of the reset argument.
            Default Value: True
            Types: bool

        to_lower_case:
            Optional Argument.
            Specifies a Boolean value that specifies whether the function converts all
            letters in the input text to lowercase.
            Default Value: True
            Types: bool

        punctuation:
            Optional Argument.
            Specifies a string that specifies the punctuation characters for the function
            to remove before evaluating the input text.
            Default Value: "`~#^&*()-"
            Types: str

        reset:
            Optional Argument.
            Specifies a string that specifies the character or string that ends a sentence.
            At the end of a sentence, the function discards any partial n-grams and searches
            for the next n-gram at the beginning of the next sentence. An n-gram
            cannot span two sentences.
            Default Value: ".,?!"
            Types: str

        total_gram_count:
            Optional Argument.
            Specifies whether the function returns the total
            number of ngrams in the document (that is, in the row). If you
            specify "true", then the name of the returned column is specified by
            the total_count_column argument.
            Note: The total number of n-grams is not necessarily the number
            of unique ngrams.
            Default Value: False
            Types: bool

        total_count_column:
            Optional Argument.
            Specifies the name of the column to return if the value of the total_gram_count
            argument is True.
            Default Value: "totalcnt"
            Types: str

        accumulate:
            Optional Argument.
            Specifies the names of the columns to return for each n-gram. These columns
            cannot have the same names as those specified by the arguments ngram,
            num_grams_column, and total_count_column. By default, the function
            returns all input columns for each n-gram.
            Types: str OR list of Strings (str)

        n_gram_column:
            Optional Argument.
            Specifies the name of the column that is to contain the generated n-grams.
            Default Value: "ngram"
            Types: str

        num_grams_column:
            Optional Argument.
            Specifies the name of the column that is to contain the length of n-gram (in
            words).
            Default Value: "n"
            Types: str

        frequency_column:
            Optional Argument.
            Specifies the name of the column that is to contain the count of each unique
            n-gram (that is, the number of times that each unique n-gram appears
            in the document).
            Default Value: "frequency"
            Types: str

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
                function supports, else an exception is raised.


    RETURNS:
        Instance of NGramSplitter.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ngramsplitterObj.<attribute_name>.
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
        load_example_data("ngrams", ["paragraphs_input"])

        # Create teradataml DataFrame object.
        paragraphs_input = DataFrame.from_table("paragraphs_input")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Creating teradataml dataframe by calculating the
        #            similarity between two strings.
        obj = NGramSplitter(data=paragraphs_input,
                            text_column='paratext',
                            n_gram_column='ngram',
                            num_grams_column='n',
                            frequency_column='frequency',
                            total_count_column='totalcnt',
                            grams='4-6',
                            overlapping=True,
                            to_lower_case=True,
                            delimiter=' ',
                            punctuation='`~#^&*()-',
                            reset='.,?!',
                            total_gram_count=False)

        # Print the result DataFrame.
        print(obj.result)


    """