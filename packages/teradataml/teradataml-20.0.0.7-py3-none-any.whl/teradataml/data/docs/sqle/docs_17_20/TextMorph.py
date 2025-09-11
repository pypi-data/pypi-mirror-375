def TextMorph(data=None, word_column=None, pos=None,
              single_output=False, postag_column=None,
              accumulate=None, **generic_arguments):
    """
    DESCRIPTION:
        TextMorph() function generate morphs of given words in the input dataset.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        word_column:
            Required Argument.
            Specifies the name of the input column that contains words for which morphs are to be generated.
            Types: str

        pos:
            Optional Argument.
            Specifies the part of speech (POS) to output.
            Permitted Values: "NOUN", "VERB", "ADV", "ADJ"
            Types: str or list of str

        single_output:
            Optional Argument.
            Specifies whether to output only one morph for each word. If set to `False`, 
            the function outputs all morphs for each word.
            Default Value: False
            Types: bool

        postag_column:
            Optional Argument.
            Specifies the name of the  column in data that contains the part-of-speech (POS) 
            tags of the words, output by the function TD_POSTagger.
            Types: str

        accumulate:
            Optional Argument.
            Specifies the names of the input columns to copy to the output table.
            Types: str or list of str

        **generic_arguments:
            Optional Argument.
            Specifies the generic keyword arguments SQLE functions accept. Below are the generic
            keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or not.
                    When set to True, results are persisted in a table; otherwise, results are
                    garbage collected at the end of the session.
                    Default Value: False
                    Types: bool
                
                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table or not.
                    When set to True, results are stored in a volatile table; otherwise not.
                    Default Value: False
                    Types: bool

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
        Instance of TextMorph.
        Output teradataml DataFrames can be accessed using attribute references, such as TDTextMorphObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result

    RAISES:
        TeradataMlException, TypeError, ValueError

    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in the example from teradataml.
        #     3. Function will raise an error if not supported on the Vantage user is connected to.

        # Load the example data.
        load_example_data("textmorph", ["words_input","pos_input"])

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("words_input")
        data2 = DataFrame.from_table("pos_input")
        
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function TextMorph.
        from teradataml import TextMorph

        # Example 1: Generate morphs for words in the input dataset.
        TextMorph_out = TextMorph(data=data1,
                                  word_column="data2",
                                  pos=["noun", "verb"],
                                  single_output=True,
                                  accumulate=["id"])

        # Print the result DataFrame.
        print(TextMorph_out.result)

        Example 2 : Generate morphs for words in the input dataset with POS tags.
        TextMorph_pos = TextMorph(data=data2,
                                  word_column="word",
                                  postag_column="pos_tag",
                                  accumulate=["id","pos_tag"])

        # Print the result DataFrame.
        print(TextMorph_pos.result)
    """