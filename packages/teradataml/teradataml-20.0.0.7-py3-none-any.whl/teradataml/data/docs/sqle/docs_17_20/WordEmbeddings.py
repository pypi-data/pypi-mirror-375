def WordEmbeddings(data=None, model=None, id_column=None, model_text_column=None,
                   model_vector_columns=None, primary_column=None, secondary_column=None,
                   operation="token-embedding", accumulate=None, convert_to_lowercase=True,
                   remove_stopwords=False, stem_tokens=False, **generic_arguments):
    """
    DESCRIPTION:
        The WordEmbeddings() function produces vectors for each piece of text and
        finds the similarity between the texts.
        Word embedding is the representation of a word in multi-dimensional
        space such that words with similar meanings have similar embedding.
        Each word is mapped to a vector of real numbers that represent the word.

        The function contains training and prediction using models. The models
        contain each possible token and its corresponding vectors. The closer
        the distance between the vectors the more the similarity. Function operations
        are token-embedding, doc-embedding, token2token-similarity, and doc2doc-similarity.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        model:
            Required Argument.
            Specifies the teradataml DataFrame which contains the model
            vectors for all the possible tokens.
            Types: teradataml DataFrame

        id_column:
            Required Argument.
            Specifies the input data column name that has the
            unique identifier for each row in the input.
            Types: str

        model_text_column:
            Required Argument.
            Specifies the column that contains the token in the "model".
            Types: str

        model_vector_columns:
            Required Argument.
            Specifies range of columns in the "model" data that contains
            real value vector.
            Types: str OR list of Strings (str)

        primary_column:
            Required Argument.
            Specifies name of the input data column that contains the text.
            Types: str

        secondary_column:
            Optional Argument.
            Specifies name of the input data column that contains the text.
            Note:
                * This field is applicable for the 'token2token-similarity' and
                  'doc2doc-similarity' operations only.
            Types: str

        operation:
            Optional Argument.
            Specifies the operation to be performed on the data.
            Permitted Values: token-embedding, doc-embedding,
                              token2token-similarity, doc2doc-similarity
            Default Value: 'token-embedding'

            Types: str

        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to
            copy to the output.
            Note:
                * This is not applicable with the 'token-embedding' operation.
            Types: str OR list of Strings (str)

        convert_to_lowercase:
            Optional Argument.
            Specifies whether to convert input data to lower case or not.
            When set to True, input data is converted to lower case.
            Otherwise, input data is not converted to lower case.
            Default Value: True
            Types: bool

        remove_stopwords:
            Optional Argument.
            Specifies whether to remove stop words from the input data.
            Note:
                * This is not applicable with the 'token2token-similarity'
                  operation.
            Default Value: False
            Types: bool

        stem_tokens:
            Optional Argument.
            Specifies whether to convert word to its root word in the input data.
            For example, convert 'going' to 'go'.
            Default Value: False
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
        Instance of WordEmbeddings.
        Output teradataml DataFrames can be accessed using attribute
        references, such as WordEmbeddingsObj.<attribute_name>.
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
        load_example_data("teradataml", ["word_embed_model","word_embed_input_table1","word_embed_input_table2"])

        # Create teradataml DataFrame objects.
        model_input = DataFrame.from_table("word_embed_model")
        data_input1 = DataFrame.from_table("word_embed_input_table1")
        data_input2 = DataFrame.from_table("word_embed_input_table2")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1 : Generate vectors for each words present in column 'doc1'
        #             using the word embedding model and 'token-embedding' operation.
        #             Each word is assigned with vectors and closer the distance
        #             between two vectors greater the similarity between two words.
        WordEmbeddings_out1 = WordEmbeddings(data = data_input1,
                                             model = model_input,
                                             id_column = "doc_id",
                                             model_text_column = "token",
                                             model_vector_columns = ["v1", "v2", "v3", "v4"],
                                             primary_column = "doc1",
                                             operation = "token-embedding"
                                             )

        # Print the result DataFrame.
        print(WordEmbeddings_out1.result)

        # Example 2 : Generate vectors for each row present in column 'doc1'
        #             using the word embedding model and 'doc-embedding' operation.
        #             Each row with para or sentence is assigned with vectors and
        #             closer the distance between two vectors greater the similarity
        #             between two para or sentence.
        WordEmbeddings_out2 = WordEmbeddings(data = data_input1,
                                             model = model_input,
                                             id_column = "doc_id",
                                             model_text_column = "token",
                                             model_vector_columns = ["v1", "v2", "v3", "v4"],
                                             primary_column = "doc1",
                                             operation = "doc-embedding",
                                             accumulate = "doc1"
                                             )

        # Print the result DataFrame.
        print(WordEmbeddings_out2.result)

        # Example 3 : Find the similarity between two columns 'token1' and 'token2' in 'data_input2',
        #             using the word embedding model and 'token2token-similarity' operation.
        WordEmbeddings_out3 = WordEmbeddings(data = data_input2,
                                             model = model_input,
                                             id_column = "token_id",
                                             model_text_column = "token",
                                             model_vector_columns = ["v1", "v2", "v3", "v4"],
                                             primary_column = "token1",
                                             secondary_column = "token2",
                                             operation = "token2token-similarity",
                                             accumulate = ["token1", "token2"]
                                             )

        # Print the result DataFrame.
        print(WordEmbeddings_out3.result)

        # Example 4 : Find the similarity between two columns 'doc1' and 'doc2' in 'data_input1',
        #             using the word embedding model and 'doc2doc-similarity' operation.
        WordEmbeddings_out4 = WordEmbeddings(data = data_input1,
                                             model = model_input,
                                             id_column = "doc_id",
                                             model_text_column = "token",
                                             model_vector_columns = ["v1", "v2", "v3", "v4"],
                                             primary_column = "doc1",
                                             secondary_column = "doc2",
                                             operation = "doc2doc-similarity",
                                             accumulate = ["doc1", "doc2"]
                                             )

        # Print the result DataFrame.
        print(WordEmbeddings_out4.result)

    """