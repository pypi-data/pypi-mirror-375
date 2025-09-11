def H2OPredict(modeldata=None, newdata=None, accumulate=None, model_output_fields=None,
               overwrite_cached_models=None, model_type="OpenSource", enable_options=None,
               is_debug=False, **generic_arguments):
    """
    DESCRIPTION:
        The H2OPredict() function performs a prediction on each row of the input table
        using a model previously trained in H2O and then loaded into the database.
        The model uses an interchange format called MOJO and it is loaded to
        Teradata database in a table by the user as a blob.
        The model data prepared by user should have a model id for each model
        (residing as a MOJO object) created by the user.
        H2OPredict() supports Driverless AI and H2O-3 MOJO models.
        H2O Driverless AI (DAI) provides a number of transformations.
        The following transformers are available for regression and classification
        (multiclass and binary) experiments:
            * Numeric
            * Categorical
            * Time and Date
            * Time Series
            * NLP (test)
            * Image

    PARAMETERS:
        newdata:
            Required Argument.
            Specifies the input teradataml DataFrame that contains the data to be
            scored.
            Types: teradataml DataFrame

        modeldata:
            Required Argument.
            Specifies the model teradataml DataFrame to be used for scoring.
            Note:
                * Use `retrieve_byom()` to get the teradataml DataFrame that contains the model.
            Types: teradataml DataFrame

        accumulate:
            Required Argument.
            Specifies the name(s) of input teradataml DataFrame column(s)
            to copy to the output DataFrame.
            Types: str OR list of Strings (str) OR Feature OR list of Features

        model_output_fields:
            Optional Argument.
            Specifies the output fields to add as individual columns instead of the
            entire JSON output. Specify fields with a comma-separated list.
            Types: str OR list of Strings (str)

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
            Default behavior: The function does not overwrite cached models.
            Permitted Values: true, t, yes, y, 1, false, f, no, n, 0, *,
                              current_cached_model
            Types: str OR list of Strings (str)

        model_type:
            Optional Argument.
            Specifies the model type for H2O model prediction.
            Default Value: "OpenSource"
            Permitted Values: DAI, OpenSource
            Types: str OR list of Strings (str)

        enable_options:
            Optional Argument.
            Specifies feature option values to have them appear in the JSON output:
                * contributions: The contribution of each input feature
                                 towards the prediction.
                * stageProbabilities: Prediction probabilities of trees in each
                                      stage or iteration.
                * leafNodeAssignments: The leaf placements of the row in all the
                                       trees in the tree-based model.
            When the feature options are not specified, the features are considered
            false and the following values are not populated in the output JSON:
                * contributions (applies only to binomial or regression models)
                * leafNodeAssignments and stageProbabilities (applies to binomial,
                  regression, multinomial, and AnomalyDetection models)
            Permitted Values: contributions, stageProbabilities, leafNodeAssignments
            Types: str OR list of Strings (str)

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
        Instance of H2OPredict.
        Output teradataml DataFrame can be accessed using attribute
        references, such as  H2OPredictObj.<attribute_name>.
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

        # Example 1: This example scores the data on Vantage using a GLM model generated
        #            outside of Vantage. The example performs prediction with H2OPredict
        #            function using this GLM model in mojo format generated by H2O.
        #            Corresponding values are specified for the "model_type", "enable_options",
        #            "model_output_fields" and "overwrite.cached.models". This will erase
        #            entire cache.

        # Load model file into Vantage.
        model_file = os.path.join(os.path.dirname(teradataml.__file__), "data", "models", "iris_mojo_glm_h2o_model")
        save_byom("iris_mojo_glm_h2o_model", model_file, "byom_models")

        # Retrieve model.
        modeldata = retrieve_byom("iris_mojo_glm_h2o_model", table_name="byom_models")

        result = H2OPredict(newdata=iris_test,
                            newdata_partition_column='id',
                            newdata_order_column='id',
                            modeldata=modeldata,
                            modeldata_order_column='model_id',
                            model_output_fields=['label', 'classProbabilities'],
                            accumulate=['id', 'sepal_length', 'petal_length'],
                            overwrite_cached_models='*',
                            enable_options='stageProbabilities',
                            model_type='OpenSource'
                            )

        # Print the results.
        print(result.result)

        # Example 2: This example scores the data on Vantage using a XGBoost model generated
        #            outside of Vantage. The example performs prediction with H2OPredict
        #            function using this XGBoost model in mojo format generated by H2O.
        #            Corresponding values are specified for the "model_type", "enable_options",
        #            "model_output_fields" and "overwrite.cached.models". This will erase
        #            entire cache.

        # Load model file into Vantage.
        model_file = os.path.join(os.path.dirname(teradataml.__file__), "data", "models", "iris_mojo_xgb_h2o_model")
        save_byom("iris_mojo_xgb_h2o_model", model_file, "byom_models")

        # Retrieve model.
        modeldata = retrieve_byom("iris_mojo_xgb_h2o_model", table_name="byom_models")

        result = H2OPredict(newdata=iris_test,
                            newdata_partition_column='id',
                            newdata_order_column='id',
                            modeldata=modeldata,
                            modeldata_order_column='model_id',
                            model_output_fields=['label', 'classProbabilities'],
                            accumulate=['id', 'sepal_length', 'petal_length'],
                            overwrite_cached_models='*',
                            enable_options='stageProbabilities',
                            model_type='OpenSource'
                            )

        # Print the results.
        print(result.result)

        # Example 3: Example performs prediction with H2OPredict function using the licensed
        #            model in mojo format generated outside of Vantage and with id
        #            'licensed_model1'from the data 'byom_licensed_models' and associated
        #            license key stored in column 'license_key' of the table 'license'
        #            present in the schema 'mldb'.

        # Retrieve model.
        modeldata = retrieve_byom('licensed_model1',
                                  table_name='byom_licensed_models',
                                  license='license_key',
                                  is_license_column=True,
                                  license_table_name='license',
                                  license_schema_name='mldb')
        result = H2OPredict(newdata=iris_test,
                            newdata_partition_column='id',
                            newdata_order_column='id',
                            modeldata=modeldata,
                            modeldata_order_column='model_id',
                            model_output_fields=['label', 'classProbabilities'],
                            accumulate=['id', 'sepal_length', 'petal_length'],
                            overwrite_cached_models='*',
                            enable_options='stageProbabilities',
                            model_type='OpenSource'
                            )
        # Print the results.
        print(result.result)

        # Example 4: Example to show case the trace table usage using
        #            is_debug=True.

        # Create the trace table.
        crt_tbl_query = 'CREATE GLOBAL TEMPORARY TRACE TABLE BYOM_Trace \
                        (vproc_ID	BYTE(2) \
                        ,Sequence	INTEGER \
                        ,Trace_Output VARCHAR(31000) CHARACTER SET LATIN NOT CASESPECIFIC) \
                        ON COMMIT PRESERVE ROWS;'
        execute_sql(crt_tbl_query)

        # Turn on tracing for the session.
        execute_sql("SET SESSION FUNCTION TRACE USING '' FOR TABLE BYOM_Trace;")

        modeldata = retrieve_byom("iris_mojo_glm_h2o_model", table_name="byom_models")

        # Execute the H2OPredict() function using is_debug=True.
        result = H2OPredict(newdata=iris_test,
                            newdata_partition_column='id',
                            newdata_order_column='id',
                            modeldata=modeldata,
                            modeldata_order_column='model_id',
                            model_output_fields=['label', 'classProbabilities'],
                            accumulate=['id', 'sepal_length', 'petal_length'],
                            overwrite_cached_models='*',
                            enable_options='stageProbabilities',
                            model_type='OpenSource',
                            is_debug=True
                            )

        # Print the results.
        print(result.result)

        # View the trace table information.
        trace_df = DataFrame.from_table("BYOM_Trace")
        print(trace_df)

        # Turn off tracing for the session.
        execute_sql("SET SESSION FUNCTION TRACE OFF;")

    """