def ONNXEmbeddings(newdata=None, modeldata=None, tokenizerdata=None, accumulate=None, model_output_tensor=None,
                   encode_max_length=512, show_model_properties=False, output_column_prefix="emb_",
                   output_format="VARBYTE(3072)", overwrite_cached_models="false", is_debug=False,
                   enable_memory_check=False, **generic_arguments):
    """
    DESCRIPTION:
        The ONNXEmbeddings() function is used to calculate embeddings values in
        Vantage with a HuggingFace model that has been created outside Vantage
        and exported to Vantage using ONNX format.

    PARAMETERS:
        newdata:
            Required Argument.
            Specifies the input teradataml DataFrame that contains
            the data to be scored.
            Types: teradataml DataFrame

        modeldata:
            Required Argument.
            Specifies the model teradataml DataFrame to be used for
            scoring.
            Note:
                * Use `retrieve_byom()` to get the teradataml DataFrame that contains the model.
            Types: teradataml DataFrame

        tokenizerdata:
            Required Argument.
            Specifies the tokenizer teradataml DataFrame
            which contains the tokenizer json file.
            Types: teradataml DataFrame

        accumulate:
            Required Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to
            copy to the output. By default, the function copies all input
            teradataml DataFrame columns to the output.
            Types: str OR list of Strings (str) OR Feature OR list of Features

        model_output_tensor:
            Required Argument.
            Specifies the column of the model's possible output fields
            that the user wants to calculate and output.
            Types: str

        encode_max_length:
            Optional Argument.
            Specifies the maximum length of the tokenizer output token
            encodings(only applies for models with symbolic dimensions).
            Default Value: 512
            Types: int

        show_model_properties:
            Optional Argument.
            Specifies the default or expanded "model_input_fields_map" based on
            input model for defaults or "model_input_fields_map" for expansion.
            Default Value: False
            Types: bool

        output_column_prefix:
            Optional Argument.
            Specifies the column prefix for each of the output columns
            when using float32 "output_format".
            Default Value: "emb_"
            Types: str

        output_format:
            Optional Argument.
            Specifies the output format for the model embeddings output.
            Default Value: "VARBYTE(3072)"
            Types: str

        overwrite_cached_models:
            Optional Argument.
            Specifies the model name that needs to be removed from the cache.
            When a model loaded into the memory of the node fits in the cache,
            it stays in the cache until being evicted to make space for another
            model that needs to be loaded. Therefore, a model can remain in the
            cache even after the completion of function execution. Other functions
            that use the same model can use it, saving the cost of reloading it
            into memory. User should overwrite a cached model only when it is updated,
            to make sure that the Predict function uses the updated model instead
            of the cached model.
            Note:
                Do not use the "overwrite_cached_models" argument except when user
                is trying to replace a previously cached model. Using the argument
                in other cases, including in concurrent queries or multiple times
                within a short period of time lead to an OOM error.
            Default Value: "false"
            Permitted Values: true, t, yes, y, 1, false, f, no, n, 0, *,
                              current_cached_model
            Types: str

        is_debug:
            Optional Argument.
            Specifies whether debug statements are added to a trace table or not.
            When set to True, debug statements are added to a trace table that must
            be created beforehand.
            Notes:
                * Only available with BYOM version 3.00.00.02 and later.
                * To save logs for debugging, user can create an error log by using
                  the is_debug=True parameter in the predict functions.
                  A database trace table is used to collect this information which
                  does impact performance of the function, so using small data input
                  sizes is recommended.
                * To generate this log, user must do the following:
                      1. Create a global trace table with columns vproc_ID BYTE(2),
                         Sequence INTEGER, Trace_Output VARCHAR(31000)
                      2. Turn on session function tracing:
                           SET SESSION FUNCTION TRACE USING '' FOR TABLE <trace_table_name_created_in_step_1>;
                      3. Execute function with "is_debug" set to True.
                      4. Debug information is logged to the table created in step 1.
                      5. To turn off the logging, either disconnect from the session or
                         run following SQL:
                           SET SESSION FUNCTION TRACE OFF;
                      The trace table is temporary and the information is deleted if user
                      logs off from the session. If long term persistence is necessary,
                      user can copy the table to a permanent table before leaving the
                      session.
            Default Value: False
            Types: bool

        enable_memory_check:
            Optional Argument.
            Specifies whether there is enough native memory for large models.
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
                  list of str (Strings) or PartitionKind
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
        Instance of ONNXEmbeddings.
        Output teradataml DataFrame can be accessed using attribute
        references, such as  ONNXEmbeddings.<attribute_name>.
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
        #     4. To execute BYOM functions, set 'configure.byom_install_location' to the
        #        database name where BYOM functions are installed.

        # Import required libraries / functions.
        import os, teradataml
        from teradataml import get_connection, DataFrame
        from teradataml import save_byom, retrieve_byom, load_example_data
        from teradataml import configure, display_analytic_functions, execute_sql

        # Load example data.
        load_example_data("byom", "amazon_reviews_25")

        # Create teradataml DataFrame objects.
        amazon_reviews_25 = DataFrame.from_table("amazon_reviews_25")

        # Assigning txt column name to rev_txt column.
        amazon_reviews_25 = amazon_reviews_25.assign(txt=amazon_reviews_25.rev_text)

        # Set install location of BYOM functions.
        configure.byom_install_location = "td_mldb"

        # Check the list of available analytic functions.
        display_analytic_functions(type="BYOM")

        # Retrieve model.
        modeldata = retrieve_byom("bge-small-en-v1.5", table_name="onnx_models")
        tokenizerdata = retrieve_byom("bge-small-en-v1.5", table_name="embeddings_tokenizers")

        # Assigning tokenizer_id, tokenizer to model_id, model in embeddings_tokenizers.
        tokenizerdata_a1 = tokenizerdata.assign(tokenizer_id=tokenizerdata.model_id)
        tokenizerdata_a2 = tokenizerdata_a1.assign(tokenizer=tokenizerdata_a1.model)

        # Example 1: Calculate embedding values in Vantage with a bge-small-en-v1.5
        #            model that has been created outside the Vantage by removing all
        #            the all cached models.
        ONNXEmbeddings_out_1 = ONNXEmbeddings(modeldata=modeldata,
                                              tokenizerdata=tokenizerdata_a2.select(['tokenizer_id', 'tokenizer']),
                                              newdata=amazon_reviews_25.select(["rev_id", "txt"]),
                                              accumulate='rev_id',
                                              model_output_tensor='sentence_embedding'
                                              )

        # Print the results.
        print(ONNXEmbeddings_out_1.result)

        # Example 2: Showcasing the model properties of bge-small-en-v1.5 model that has been
        #            created outside the Vantage by showcasing.
        ONNXEmbeddings_out_2 = ONNXEmbeddings(modeldata=modeldata,
                                              tokenizerdata=tokenizerdata_a2.select(['tokenizer_id', 'tokenizer']),
                                              newdata=amazon_reviews_25.select(["rev_id", "txt"]),
                                              accumulate='rev_id',
                                              model_output_tensor='sentence_embedding',
                                              show_model_properties=True
                                              )

        # Print the results.
        print(ONNXEmbeddings_out_2.result)
    """