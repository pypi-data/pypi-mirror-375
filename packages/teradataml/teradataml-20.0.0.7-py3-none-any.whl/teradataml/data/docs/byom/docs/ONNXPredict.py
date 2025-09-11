def ONNXPredict(newdata=None, modeldata=None, accumulate=None, model_output_fields=None,
                overwrite_cached_models="false", show_model_input_fields_map=False,
                model_input_fields_map=None, is_debug=False, **generic_arguments):

    """
    DESCRIPTION:
        The ONNXPredict() function is used to score data in Vantage with a model that has
        been created outside Vantage and exported to Vantage using ONNX format.

        For classical machine learning models on structured data, Vantage has a large set
        of transformation functions in both the Vantage Analytics Library and Analytics Database
        Analytic functions. User can use these functions to prepare the input data that the
        classical machine learning models expect. However, there are no transformation or
        conversion functions in Vantage to prepare tensors for unstructured data (text,
        images, video and audio) for ONNX models. The data must be preprocessed before
        loading to Vantage to conform the tensors into a shape that the ONNX models expect.
        As long as the data is in the form expected by your ONNX model, it can be scored by
        ONNXPredict().
        ONNXPredict() supports models in ONNX format. Several training frameworks support
        native export functionality to ONNX, such as Chainer, Caffee2, and PyTorch.
        User can also convert models from several toolkits like scikit-learn, TensorFlow,
        Keras, XGBoost, H2O, and Spark ML to ONNX.


    PARAMETERS:
        newdata:
            Required Argument.
            Specifies the teradataml DataFrame containing the input test data.
            Types: teradataml DataFrame

        modeldata:
            Required Argument.
            Specifies the teradataml DataFrame containing the model data
            to be used for scoring.
            Note:
                * Use `retrieve_byom()` to get the teradataml DataFrame that contains the model.
            Types: teradataml DataFrame

        accumulate:
            Required Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to
            copy to the output.
            Types: str OR list of Strings (str) OR Feature OR list of Features

        model_output_fields:
            Optional Argument.
            Specifies the column(s) of the json output that the user wants to
            specify as individual columns instead of the entire json_report.
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
            Default Value: "false"
            Permitted Values: true, t, yes, y, 1, false, f, no, n, 0, *,
                              current_cached_model
            Types: str

        show_model_input_fields_map:
            Optional Argument.
            Specifies When set to 'True', the function does not predict the "newdata",
            instead shows the currently defined fields fully expanded.
            Example:
                If "model_input_fields_map" is x=[1:4] and "show_model_input_fields_map"
                is set to 'True', the output is returned as a varchar column:
                    model_input_fields_map='x=sepal_len,sepal_wid,petal_len,petal_wid'
            When "model_input_fields_map" is not specified, the expected default
            mapping is based on the ONNX inputs defined in the model is shown.
            When set to 'False', which is the default value the function predict the
            "newdata".
            Default Value: False
            Types: bool

        model_input_fields_map:
            Optional Argument.
            Specifies the output fields to add as individual columns instead of the
            entire JSON output.
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
        Instance of ONNXPredict.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ONNXPredictObj.<attribute_name>.
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
        from teradataml import DataFrame, load_example_data, configure, execute_sql
        from teradataml import save_byom, retrieve_byom, display_analytic_functions

        # Load the example data.
        load_example_data("byom", ["iris_test"])

        # Create teradataml DataFrame objects.
        iris_test = DataFrame("iris_test")

        # Set install location of BYOM functions.
        configure.byom_install_location = "mldb"

        # Check the list of available analytic functions.
        display_analytic_functions(type="BYOM")

        # Load model file into Vantage.
        model_file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "models")
        skl_model_file = os.path.join(model_file_path,
                                      "iris_db_dt_model_sklearn.onnx")
        skl_floattensor_model_file = os.path.join(model_file_path,
                                                  "iris_db_dt_model_sklearn_floattensor.onnx")

        # Save ONNX models.
        save_byom("iris_db_dt_model_sklearn",
                  skl_model_file, "byom_models")
        save_byom("iris_db_dt_model_sklearn_floattensor",
                  skl_floattensor_model_file, "byom_models")

        # Retrieve ONNX model.
        # The 'iris_db_dt_model_sklearn' created with each input variable mapped
        # to a single input tensor, then converted this model into ONNX format
        # with scikit-learn-onnx, and then used to predict the flower species.
        # This model trained using iris_test dataset with scikit-learn.
        skl_model = retrieve_byom("iris_db_dt_model_sklearn",
                                  table_name="byom_models")

        # The 'iris_db_dt_model_sklearn_floattensor' created by using an input array of
        # four float32 values and named float_input, then converted this model into ONNX
        # format with scikit-learn-onnx, and then used to predict the flower species.
        # This model trained using iris_test dataset with scikit-learn.
        skl_floattensor_model = retrieve_byom("iris_db_dt_model_sklearn_floattensor",
                                    table_name="byom_models")

        # Example 1: Example performs prediction with ONNXPredict function using trained
        #            'skl_model' model in onnx format generated outside of Vantage.
        ONNXPredict_out = ONNXPredict(accumulate="id",
                                      newdata=iris_test,
                                      modeldata=skl_model)

        # Print the results.
        print(ONNXPredict_out.result)


        # Example 2: Example performs prediction with ONNXPredict function using trained
        #            'skl_floattensor_model' model in onnx format generated
        #            outside of Vantage, where input DataFrame columns match the order
        #            used when generating the model, by specifying "model_input_fields_map"
        #            to define the columns.
        ONNXPredict_out1 = ONNXPredict(accumulate="id",
                                       model_output_fields="output_probability",
                                       overwrite_cached_models="*",
                                       model_input_fields_map='float_input=sepal_length, sepal_width, petal_length, petal_width',
                                       newdata=iris_test,
                                       modeldata=skl_floattensor_model)


        # Print the result DataFrame.
        print(ONNXPredict_out1.result)

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

        # Execute the ONNXPredict() function using is_debug=True.
        ONNXPredict_out2 = ONNXPredict(accumulate="id",
                                      newdata=iris_test,
                                      modeldata=skl_model,
                                      is_debug=True)

        # Print the results.
        print(ONNXPredict_out2.result)

        # View the trace table information.
        trace_df = DataFrame.from_table("BYOM_Trace")
        print(trace_df)

        # Turn off tracing for the session.
        execute_sql("SET SESSION FUNCTION TRACE OFF;")

    """
