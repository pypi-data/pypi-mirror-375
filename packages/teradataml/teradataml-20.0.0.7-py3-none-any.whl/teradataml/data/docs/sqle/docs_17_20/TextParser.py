def TextParser(data=None, object=None, text_column=None, enforce_token_limit=False,
               convert_to_lowercase=True, stem_tokens=False, remove_stopwords=False,
               accumulate=None, delimiter=" \t\n\f\r", delimiter_regex=None,
               punctuation=r"!#$%&()*+,-./:;?@\^_`{|}~", token_col_name=None,
               doc_id_column=None, list_positions=False, token_frequency=False,
               output_by_word=True, **generic_arguments):
    """
    DESCRIPTION:
        The TextParser() function can parse text and perform the following operations:
            * Tokenize the text in the specified column
            * Remove the punctuations from the text and convert the text to lowercase
            * Remove stop words from the text and convert the text to their root forms
            * Create a row for each word in the output dataframe
            * Perform stemming; that is, the function identifies the common root form of a word
              by removing or replacing word suffixes
            
            Notes:
                * The stems resulting from stemming may not be actual words. For example, the stem
                  for 'communicate' is 'commun' and the stem for 'early' is 'earli'
                  (trailing 'y' is replaced by 'i').
                * This function requires the UTF8 client character set.
                * This function does not support Pass Through Characters (PTCs).
                * For information about PTCs, see Teradata Vantage™ - Analytics Database International
                   Character Set Support.
                * This function does not support KanjiSJIS or Graphic data types.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        object:
            Optional Argument.
            Specifies the teradataml DataFrame containing stop words.
            Types: teradataml DataFrame

        text_column:
            Required Argument.
            Specifies the name of the input data column whose contents are to be tokenized.
            Types: str

        enforce_token_limit:
            Optional Argument.
            Specifies whether to throw an informative error when finding token larger than
            64K/32K or silently discard those larger tokens.
            Default Value: False
            Types: bool

        convert_to_lowercase:
            Optional Argument.
            Specifies whether to convert the text in "text_column" to lowercase.
            Default Value: True
            Types: bool

        stem_tokens:
            Optional Argument.
            Specifies whether to convert the text in "text_column" to their root forms.
            Default Value: False
            Types: bool

        remove_stopwords:
            Optional Argument.
            Specifies whether to remove stop words from the text in "text_column" before
            parsing.
            Default Value: False
            Types: bool

        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
            output. By default, the function copies no input teradataml
            DataFrame columns to the output.
            Types: str OR list of Strings (str)

        delimiter:
            Optional Argument.
            Specifies the word delimiter to apply to the text in the specified column in the 
            "text_column" element.
            Default Value: " \\t\\n\\f\\r"
            Types: str

        delimiter_regex:
            Optional Argument.
            Specifies a Perl Compatible regular expression that represents the word delimiter.
            Types: str

        punctuation:
            Optional Argument.
            Specifies the punctuation characters to replace with a space in the input text.
            Default Value: "!#$%&()*+,-./:;?@\\^_`{|}~"
            Types: str

        token_col_name:
            Optional Argument.
            Specifies the name for the output column that contains the individual words from
            the text of the specified column in the "text_column" element.
            Types: str

        doc_id_column:
            Optional Argument.
            Specifies the name of the column that uniquely identifies a row in the input table.
            Types: str

        list_positions:
            Optional Argument.
            Specifies whether to output the positions of a word in list form.
            Default Value: False
            Types: bool
        
        token_frequency:
            Optional Argument.
            Specifies whether to output the frequency for each token.
            Default Value: False
            Types: bool

        output_by_word:
            Optional Argument.
            Specifies whether to output each token in a separate row or all tokens in one.
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
        Instance of TextParser.
        Output teradataml DataFrames can be accessed using attribute
        references, such as TextParserObj.<attribute_name>.
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
        load_example_data("textparser", ["complaints", "stop_words"])

        # Create teradataml DataFrame objects.
        complaints = DataFrame.from_table("complaints")
        stop_words = DataFrame.from_table("stop_words")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1 : Remove all the stop words from "text_data" column
        #             and accumulate it by "doc_id" column.
        TextParser_out = TextParser(data=complaints,
                                    text_column="text_data",
                                    object=stop_words,
                                    remove_stopwords=True,
                                    accumulate="doc_id")

        # Print the result DataFrame.
        print(TextParser_out.result)

        # Example 2 : Convert words in "text_data" column into their root forms.
        TextParser_out = TextParser(data=complaints,
                                    text_column="text_data",
                                    convert_to_lowercase=True,
                                    stem_tokens=True)

        # Print the result DataFrame.
        print(TextParser_out.result)

        # Example 3 : Tokenize  words in "text_data" column using delimiter regex,
        #             convert tokens to lowercase and output token positions in a list format
        TextParser_out = TextParser(data=complaints,
                                    text_column="text_data",
                                    doc_id_column="doc_id",
                                    delimeter_regex="[ \t\f\r\n]+",
                                    list_positions=True,
                                    convert_to_lowercase=True,
                                    output_by_word=False)
 
        # Print the result DataFrame.
        print(TextParser_out.result)
    """