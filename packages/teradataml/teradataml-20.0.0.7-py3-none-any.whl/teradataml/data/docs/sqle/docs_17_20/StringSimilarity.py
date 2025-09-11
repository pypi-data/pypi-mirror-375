def StringSimilarity(data=None, comparison_columns=None, case_sensitive=None, accumulate=None,
                     **generic_arguments):
    """
    DESCRIPTION:
        StringSimilarity() function calculates the similarity between two
        strings, using either the Jaro, Jaro-Winkler, N-Gram, or Levenshtein
        distance.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        comparison_columns:
            Required Argument.
            Specifies pairs of input teradataml DataFrame columns that contain
            strings to be compared (column1 and column2), how to compare them
            (comparison_type), and (optionally) a constant and the name of the
            output column for their similarity (output_column). The similarity is
            a value in the range [0, 1].
            For comparison_type, use one of these values:
                * "jaro": Jaro distance.
                * "jaro_winkler": Jaro-Winkler distance (1 for an exact match, 0 otherwise).
                  If you specify this comparison type, you can specify the value of
                  factor p with constant. 0 ≤ p ≤ 0.25.
                  Default: p = 0.1
                * "n_gram": N-gram similarity.
                  If you specify this comparison type, you can specify the value of N with
                  constant.
                  Default: N = 2
                * "LD": Levenshtein distance
                  The number of edits needed to transform one string into the other,
                  where edits include insertions, deletions, or substitutions of
                  individual characters.
                * "LDWS": Levenshtein distance without substitution.
                  Number of edits needed to transform one string into the other using only
                  insertions or deletions of individual characters.
                * "OSA": Optimal string alignment distance.
                  Number of edits needed to transform one string into the other.
                  Edits are insertions, deletions, substitutions, or transpositions of
                  characters. A substring can be edited only once.
                * "DL": Damerau-Levenshtein distance.
                  Like OSA, except that a substring can be edited any number of times.
                * "hamming": Hamming distance.
                  Number of positions where corresponding characters differ (that is,
                  minimum number of substitutions needed to transform one string into the
                  other) for strings of equal length, otherwise -1 for strings of unequal
                  length.
                * "LCS": Longest common substring.
                  Length of longest substring common to both strings.
                * "jaccard": Jaccard index-based comparison.
                * "cosine": Cosine similarity.
                * "soundexcode": Only for English strings. -1 if either string has a
                  non-English character, otherwise, 1 if their soundex codes are the same
                  and 0 otherwise.
            You can specify a different comparison_type for every pair of columns.
            The default output_column is "sim_i", where i is the sequence number of the
            column pair.
            Types: str OR list of Strings (str)

        case_sensitive:
            Optional Argument.
            Specifies whether string comparison is case-sensitive. The default
            value is False. You can specify either one value for all pairs or
            one value for each pair. If you specify one value for each pair, then
            the ith value applies to the ith pair.
            Types: bool OR list of bools

        accumulate:
            Optional Argument.
            Specifies the names of input teradataml DataFrame columns to be
            copied to the output.
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
                These generic arguments are supported by teradataml if the underlying SQL Engine   
                function supports, else an exception is raised.

    RETURNS:
        Instance of StringSimilarity.
        Output teradataml DataFrames can be accessed using attribute
        references, such as StringSimilarityObj.<attribute_name>.
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
        load_example_data("stringsimilarity", ["strsimilarity_input"])

        # Create teradataml DataFrame object.
        strsimilarity_input = DataFrame.from_table("strsimilarity_input")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Creating teradataml dataframe by calculating the
        #            similarity between two strings.
        obj = StringSimilarity(data = strsimilarity_input,
                               comparison_columns=['jaro (src_text1, tar_text) AS jaro1_sim',
                                                   'LD (src_text1, tar_text) AS ld1_sim',
                                                   'n_gram (src_text1, tar_text, 2) AS ngram1_sim',
                                                   'jaro_winkler (src_text1, tar_text, 0.1) AS jw1_sim'],
                               case_sensitive = True,
                               accumulate = ["id","src_text1","tar_text"])

        # Print the result DataFrame.
        print(obj.result)
    """