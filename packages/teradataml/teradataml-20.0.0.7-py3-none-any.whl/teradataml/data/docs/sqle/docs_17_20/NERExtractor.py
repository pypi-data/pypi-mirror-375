def NERExtractor(data=None, user_defined_data=None, rules_data=None, text_column=None,
                 input_language="EN", show_context=0, accumulate=None,
                 **generic_arguments):
    """
    DESCRIPTION:
        NERExtractor() performs Named Entity Recognition (NER) on input text 
        according to user-defined dictionary words or regular expression (regex) patterns.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        user_defined_data:
            Required Argument.
            Specifies the teradataml DataFrame which contains user defined words and the corresponding entity label.
            Types: teradataml DataFrame

        rules_data:
            Required Argument.
            Specifies the teradataml DataFrame which contains user-defined regex patterns and the corresponding entity label.
            Types: teradataml DataFrame

        text_column:
            Required Argument.
            Specifies the name of the teradataml DataFrame column that will be used for NER search.
            Types: str

        input_language:
            Optional Argument.
            Specifies the language of input text.
            Default Value: "EN"
            Types: str

        show_context:
            Optional Argument.
            Specifies the number of words before and after the matched entity. If leading or trailing
            words are less than "show_context", then ellipsis (...) are added. Must be a positive value
            less than 10.
            Default Value: 0
            Types: int

        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to copy to the output.
            table to output.
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
        Instance of NERExtractor.
        Output teradataml DataFrames can be accessed using attribute references, such as TDNERExtractorObj.<attribute_name>.
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
        load_example_data("tdnerextractor", ["ner_input_eng", "ner_dict", "ner_rule"])

        # Create teradataml DataFrame objects.
        df = DataFrame.from_table("ner_input_eng")
        user_defined_words = DataFrame.from_table("ner_dict")
        rules = DataFrame.from_table("ner_rule")

          
        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function NERExtractor.
        from teradataml import NERExtractor

        # Example 1: Perform Named Entity Recognition (NER) using Rules and Dict with Accumulate.
        NER_out = NERExtractor(data=df,
                               user_defined_data=user_defined_words,
                               rules_data=rules,
                               text_column=["txt"],
                               input_language="en",
                               show_context=3,
                               accumulate=["id"])

        # Print the result DataFrame.
        print(NER_out.result)
    """