def DataikuPredict(modeldata=None, newdata=None, accumulate=None, model_output_fields=None,
                   overwrite_cached_models=False, is_debug=False, **generic_arguments):
    """
    DESCRIPTION:
        The DataikuPredict() function is used to score data in Vantage
        with a model that has been created outside Vantage and exported
        to Vantage using Dataiku format.

    PARAMETERS:
        modeldata:
            Required Argument.
            Specifies the model teradataml DataFrame to be used for
            scoring.
            Types: teradataml DataFrame

        newdata:
            Required Argument.
            Specifies the input teradataml DataFrame that contains
            the data to be scored.
            Types: teradataml DataFrame

        accumulate:
            Required Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to
            copy to the output. By default, the function copies all input
            teradataml DataFrame columns to the output.
            Types: str OR list of Strings (str) OR Feature OR list of Features

        model_output_fields:
            Optional Argument.
            Specifies the columns of the json output that the user wants
            to specify as individual columns instead of the entire json
            report.
            Types: str OR list of Strings (str)

        overwrite_cached_models:
            Optional Argument.
            Specifies the model name that needs to be removed from the cache.
            If a model is loaded into the memory of the node fits in the cache,
            it stays in the cache until being evicted to make space for another
            model that needs to be loaded. Therefore, a model can remain in the
            cache even after completion of function call. Other queries that
            use the same model can use it, saving the cost of reloading it
            into memory. User may overwrite a cached model only when it has been
            updated, to make sure that the Predict function uses the updated
            model instead of the cached model.
            Note:
                Do not use the "overwrite_cached_models" argument except when trying
                to replace a previously cached model. This applies to any model type
                (PMML, H2O Open Source, DAI, ONNX, and Dataiku). Using this argument
                in other cases, including in concurrent queries or multiple times
                within a short period of time, may lead to an OOM error from garbage
                collection not being fast enough.
            Permitted Values:
                'current_cached_model', '*', 'true', 't', 'yes', '1', 'false', 'f', 'no',
                 'n', or '0'.
            Default Values: "false"
            Types: bool

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
        Instance of DataikuPredict.
        Output teradataml DataFrame can be accessed using attribute
        references, such as  DataikuPredictObj.<attribute_name>.
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
        load_example_data("byom", "iris_test")

        # Create teradataml DataFrame objects.
        iris_test = DataFrame.from_table("iris_test")

        # Set install location of BYOM functions.
        configure.byom_install_location = "mldb"

        # Check the list of available analytic functions.
        display_analytic_functions(type="BYOM")

        # Load model file into Vantage.
        model_file = os.path.join(os.path.dirname(teradataml.__file__), "data",
                                  "models", "dataiku_iris_data_ann_thin")
        save_byom("dataiku_iris_data_ann_thin", model_file, "byom_models")

        # Retrieve model.
        modeldata = retrieve_byom("dataiku_iris_data_ann_thin", table_name="byom_models")

        # Example 1: Score data in Vantage with a model that has
        #            been created outside the Vantage by removing all the
        #            all cached models.
        DataikuPredict_out_1 = DataikuPredict(newdata=iris_test,
                                              modeldata=modeldata,
                                              accumulate=['id', 'sepal_length', 'petal_length'],
                                              overwrite_cached_models="*")

        # Print the results.
        print(DataikuPredict_out_1.result)
        
        # Example 2: Example to show case the trace table usage using
        #            is_debug=True.

        # Create the trace table.
        crt_tbl_query = 'CREATE GLOBAL TEMPORARY TRACE TABLE BYOM_Trace \
                        (vproc_ID	BYTE(2) \
                        ,Sequence	INTEGER \
                        ,Trace_Output VARCHAR(31000) CHARACTER SET LATIN NOT CASESPECIFIC) \
                        ON COMMIT PRESERVE ROWS;'
        execute_sql(crt_tbl_query)

        # Turn on the session function.
        execute_sql("SET SESSION FUNCTION TRACE USING '' FOR TABLE BYOM_Trace;")

        # Execute the DataikuPredict() function using is_debug=True.
        DataikuPredict_out_2 = DataikuPredict(newdata=iris_test,
                                              modeldata=modeldata,
                                              accumulate=['id', 'sepal_length', 'petal_length'],
                                              overwrite_cached_models="*",
                                              is_debug=True)

        # Print the results.
        print(DataikuPredict_out_2.result)

        # View the trace table information.
        trace_df = DataFrame.from_table("BYOM_Trace")
        print(trace_df)

        # Turn off the session function
        execute_sql("SET SESSION FUNCTION TRACE OFF;")
    """