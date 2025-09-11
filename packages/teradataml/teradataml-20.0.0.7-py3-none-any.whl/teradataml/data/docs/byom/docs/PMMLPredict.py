def PMMLPredict(newdata=None, modeldata=None, accumulate=None,
                model_output_fields=None, overwrite_cached_models=None,
                is_debug=False, **generic_arguments):
    """
    DESCRIPTION:
        The function transforms the input data during model training as part
        of a pipeline. The generated model, stored in XML format, includes
        the preprocessing steps. During model prediction, the transformations are
        applied to the input data and the transformed data is scored by the PMMLPredict().

        PMML supports the following input data transformations:
            * Normalization: Scales continuous or discrete input values to specified range.
                             Python Function: MinMaxScaler
            * Discretization: Maps continuous input values to discrete values.
                              Python Function: CutTransformer
            * Value Mapping: Maps discrete input values to other discrete values.
                             Python Functions: StandardScalar, LabelEncoder
            * Function Mapping: Maps input values to values derived from applying a function.
                                Python Function: FunctionTransformer

        PMMLPredict() function supports the following external models:
            * Anomaly Detection
            * Association Rules
            * Cluster
            * General Regression
            * k-Nearest Neighbors
            * Naive Bayes
            * Neural Network
            * Regression
            * Ruleset
            * Scorecard
            * Random Forest
            * Decision Tree
            * Vector Machine
            * Multiple Models


    PARAMETERS:
        newdata:
            Required Argument.
            Specifies the input teradataml DataFrame that contains the data to be scored.
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
            Specifies the scoring fields to output as individual columns
            instead of outputting the JSON string that contains all the
            scoring output fields.
            User should not specify "model_output_fields" that is not in the
            JSON string, otherwise system will throw an error.
            Default behavior: The function outputs the JSON string that contains
                              all the output fields in the output data column
                              json_report.
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
        Instance of PMMLPredict.
        Output teradataml DataFrames can be accessed using attribute
        references, such as PMMLPredictObj.<attribute_name>.
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
        from teradataml import DataFrame, load_example_data, create_context, execute_sql
        from teradataml import save_byom, retrieve_byom, configure, display_analytic_functions

        # Load example data.
        load_example_data("byom", "iris_test")

        # Create teradataml DataFrame objects.
        iris_test = DataFrame.from_table("iris_test")

        # Set install location of BYOM functions.
        configure.byom_install_location = "mldb"

        # Check the list of available analytic functions.
        display_analytic_functions(type="BYOM")

        # Example 1: This example scores the data on Vantage using a GLM model generated
        #            outside of Vantage. The example performs prediction with PMMLPredict
        #            function using this GLM model in PMML format generated by open source
        #            model. Corresponding values are specified for the "overwrite_cached_models".
        #            This will erase entire cache.

        # Load model file into Vantage.
        model_file = os.path.join(os.path.dirname(teradataml.__file__), "data", "models", "iris_db_glm_model.pmml")
        save_byom("iris_db_glm_model", model_file, "byom_models")

        # Retrieve model.
        modeldata = retrieve_byom("iris_db_glm_model", table_name="byom_models")

        result = PMMLPredict(
                modeldata = modeldata,
                newdata = iris_test,
                accumulate = ['id', 'sepal_length', 'petal_length'],
                overwrite_cached_models = '*',
                )

        # Print the results.
        print(result.result)

        # Example 2: This example scores the data on Vantage using a XGBoost model generated
        #            outside of Vantage. The example performs prediction with PMMLPredict
        #            function using this XGBoost model in PMML format generated by open source
        #            model. Corresponding values are specified for the "overwrite_cached_models".
        #            This will erase entire cache.


        # Load model file into Vantage.
        model_file = os.path.join(os.path.dirname(teradataml.__file__), "data", "models", "iris_db_xgb_model.pmml")
        save_byom("iris_db_xgb_model", model_file, "byom_models")

        # Retrieve model.
        modeldata = retrieve_byom("iris_db_xgb_model", table_name="byom_models")

        result = PMMLPredict(
                modeldata = modeldata,
                newdata = iris_test,
                accumulate = ['id', 'sepal_length', 'petal_length'],
                overwrite_cached_models = '*',
                )

        # Print the results.
        print(result.result)

        # Example 3: Example to show case the trace table usage using
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

        modeldata = retrieve_byom("iris_db_glm_model", table_name="byom_models")

        # Execute the PMMLPredict() function using is_debug=True.
        result = PMMLPredict(
                modeldata = modeldata,
                newdata = iris_test,
                accumulate = ['id', 'sepal_length', 'petal_length'],
                overwrite_cached_models = '*',
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