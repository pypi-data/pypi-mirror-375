#!/usr/bin/python
# ################################################################## 
# 
# Copyright 2021 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Dhanashri Thigale (dhanashri.thigale@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# 
# Version: 1.2
# Function Version: 1.1
# 
# ################################################################## 

import inspect
import time
from teradataml.common.wrapper_utils import AnalyticsWrapperUtils
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import *
from teradataml.dataframe.dataframe import DataFrame
from teradataml.common.aed_utils import AedUtils
from teradataml.analytics.analytic_query_generator import AnalyticQueryGenerator
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.constants import TeradataConstants
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.options.display import display
from teradataml.utils.validators import _Validators

class  PMMLPredict:
    
    def __init__(self,
        modeldata = None,
        newdata = None,
        accumulate = None,
        model_output_fields = None,
        overwrite_cached_models = None,
        newdata_partition_column = "ANY",
        newdata_order_column = None,
        modeldata_order_column = None):
        """
        DESCRIPTION:
            This function is used to score data in Vantage with a model that has been
            created outside Vantage and exported to Vantage using PMML format.
        
        
        PARAMETERS:
            modeldata:
                Required Argument.
                Specifies the model teradataml DataFrame to be used for scoring.
            
            modeldata_order_column:
                Optional Argument.
                Specifies Order By columns for "modeldata".
                Values to this argument can be provided as a list, if multiple 
                columns are used for ordering.
                Types: str OR list of Strings (str)
            
            newdata:
                Required Argument.
                Specifies the input teradataml DataFrame that contains the data to be scored.
            
            newdata_partition_column:
                Optional Argument.
                Specifies Partition By columns for "newdata".
                Values to this argument can be provided as a list, if multiple 
                columns are used for partition.
                Default Value: ANY
                Types: str OR list of Strings (str)
            
            newdata_order_column:
                Optional Argument.
                Specifies Order By columns for "newdata".
                Values to this argument can be provided as a list, if multiple 
                columns are used for ordering.
                Types: str OR list of Strings (str)
            
            accumulate:
                Required Argument.
                Specifies the names of the input columns from "newdata" DataFrame
                to copy to the output DataFrame.
                Types: str OR list of Strings (str)
            
            model_output_fields:
                Optional Argument.
                Specifies the columns of the json output that the user wants to 
                specify as individual columns instead of the entire json report.
                Types: str OR list of strs
            
            overwrite_cached_models:
                Optional Argument.
                Specifies the model name that needs to be removed from the cache.
                Use * to remove all cached models.
                Types: str OR list of strs

        RETURNS:
            Instance of PMMLPredict.
            Output teradataml DataFrames can be accessed using attribute 
            references, such as PMMLPredictObj.<attribute_name>.
            Output teradataml DataFrame attribute name is:
                result
        
        
        RAISES:
            TeradataMlException, TypeError, ValueError
        
        
        EXAMPLES:
            # Note:
            # To execute BYOM functions, set 'configure.byom_install_location' to the
            # database name where BYOM functions are installed.

            # Import required libraries / functions.
            import os
            from teradataml import PMMLPredict, DataFrame, load_example_data, create_context
            from teradataml import save_byom, retrieve_byom

            # Load example data.
            load_example_data("byom", "iris_test")

            # Create teradataml DataFrame objects.
            iris_test = DataFrame.from_table("iris_test")

            # Set install location of BYOM functions.
            configure.byom_install_location = "mldb"

            # Example 1: This example runs a query with GLM model and
            # "overwrite_cached_models". This will erase entire cache.

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

            # Example 2: This example runs a query with XGBoost model and
            # "overwrite_cached_models". This will erase entire cache.

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

        """
        
        # Start the timer to get the build time
        _start_time = time.time()

        self.modeldata  = modeldata 
        self.newdata  = newdata 
        self.accumulate  = accumulate 
        self.model_output_fields  = model_output_fields 
        self.overwrite_cached_models  = overwrite_cached_models 
        self.newdata_partition_column  = newdata_partition_column
        self.newdata_order_column  = newdata_order_column 
        self.modeldata_order_column  = modeldata_order_column 
        
        # Create TeradataPyWrapperUtils instance which contains validation functions.
        self.__awu = AnalyticsWrapperUtils()
        self.__aed_utils = AedUtils()
        
        # Create argument information matrix to do parameter checking
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["modeldata", self.modeldata, False, (DataFrame)])
        self.__arg_info_matrix.append(["modeldata_order_column", self.modeldata_order_column, True, (str,list)])
        self.__arg_info_matrix.append(["newdata", self.newdata, False, (DataFrame)])
        self.__arg_info_matrix.append(["newdata_partition_column", self.newdata_partition_column, True, (str,list)])
        self.__arg_info_matrix.append(["newdata_order_column", self.newdata_order_column, True, (str,list)])
        self.__arg_info_matrix.append(["accumulate", self.accumulate, False, (str,list)])
        self.__arg_info_matrix.append(["model_output_fields", self.model_output_fields, True, (str,list)])
        self.__arg_info_matrix.append(["overwrite_cached_models", self.overwrite_cached_models, True, (str,list)])

        if inspect.stack()[1][3] != '_from_model_catalog':
            # Perform the function validations
            self.__validate()
            # Generate the ML query
            self.__form_tdml_query()
            # Execute ML query
            self.__execute()
            # Get the prediction type
            self._prediction_type = self.__awu._get_function_prediction_type(self)
        
        # End the timer to get the build time
        _end_time = time.time()
        
        # Calculate the build time
        self._build_time = (int)(_end_time - _start_time)
        
    def __validate(self):
        """
        Function to validate sqlmr function arguments, which verifies missing 
        arguments, input argument and table types. Also processes the 
        argument values.
        """
        
        # Make sure that a non-NULL value has been supplied for all mandatory arguments
        self.__awu._validate_missing_required_arguments(self.__arg_info_matrix)
        
        # Make sure that a non-NULL value has been supplied correct type of argument
        self.__awu._validate_argument_types(self.__arg_info_matrix)
        
        # Check to make sure input table types are strings or data frame objects or of valid type.
        self.__awu._validate_input_table_datatype(self.newdata, "newdata", None)
        self.__awu._validate_input_table_datatype(self.modeldata, "modeldata", None)
        
        # Check whether the input columns passed to the argument are not empty.
        # Also check whether the input columns passed to the argument valid or not.
        self.__awu._validate_input_columns_not_empty(self.accumulate, "accumulate")
        self.__awu._validate_dataframe_has_argument_columns(self.accumulate, "accumulate", self.newdata, "newdata", False)
        
        self.__awu._validate_input_columns_not_empty(self.newdata_partition_column, "newdata_partition_column")
        if self.__awu._is_default_or_not(self.newdata_partition_column, "ANY"):
            self.__awu._validate_dataframe_has_argument_columns(self.newdata_partition_column, "newdata_partition_column", self.newdata, "newdata", True)
        self.__awu._validate_input_columns_not_empty(self.newdata_order_column, "newdata_order_column")
        self.__awu._validate_dataframe_has_argument_columns(self.newdata_order_column, "newdata_order_column", self.newdata, "newdata", False)
        
        self.__awu._validate_input_columns_not_empty(self.modeldata_order_column, "modeldata_order_column")
        self.__awu._validate_dataframe_has_argument_columns(self.modeldata_order_column, "modeldata_order_column", self.modeldata, "modeldata", False)

        # Check whether configure.byom_install_location is set.
        _Validators()._validate_function_install_location_is_set(configure.byom_install_location, "Bring Your Own Model", "configure.byom_install_location")
        
    def __form_tdml_query(self):
        """
        Function to generate the analytical function queries. The function defines 
        variables and list of arguments required to form the query.
        """
        
        # Output table arguments list
        self.__func_output_args_sql_names = []
        self.__func_output_args = []
        
        # Model Cataloging related attributes.
        self._sql_specific_attributes = {}
        self._sql_formula_attribute_mapper = {}
        self._target_column = None
        self._algorithm_name = None
        
        # Generate lists for rest of the function arguments
        self.__func_other_arg_sql_names = []
        self.__func_other_args = []
        self.__func_other_arg_json_datatypes = []
        
        self.__func_other_arg_sql_names.append("Accumulate")
        self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.accumulate, "'"))
        self.__func_other_arg_json_datatypes.append("COLUMNS")
        
        if self.model_output_fields is not None:
            self.__func_other_arg_sql_names.append("ModelOutputFields")
            self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.model_output_fields, "'"))
            self.__func_other_arg_json_datatypes.append("STRING")
        
        if self.overwrite_cached_models is not None:
            self.__func_other_arg_sql_names.append("OverwriteCachedModel")
            self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.overwrite_cached_models, "'"))
            self.__func_other_arg_json_datatypes.append("STRING")
        
        
        # Declare empty lists to hold input table information.
        self.__func_input_arg_sql_names = []
        self.__func_input_table_view_query = []
        self.__func_input_dataframe_type = []
        self.__func_input_distribution = []
        self.__func_input_partition_by_cols = []
        self.__func_input_order_by_cols = []
        
        # Process newdata
        if self.__awu._is_default_or_not(self.newdata_partition_column, "ANY"):
            self.newdata_partition_column = UtilFuncs._teradata_collapse_arglist(self.newdata_partition_column, "\"")
        
        self.__table_ref = self.__awu._teradata_on_clause_from_dataframe(self.newdata, False)
        self.__func_input_distribution.append("FACT")
        self.__func_input_arg_sql_names.append("InputTable")
        self.__func_input_table_view_query.append(self.__table_ref["ref"])
        self.__func_input_dataframe_type.append(self.__table_ref["ref_type"])
        self.__func_input_partition_by_cols.append(self.newdata_partition_column)
        self.__func_input_order_by_cols.append(UtilFuncs._teradata_collapse_arglist(self.newdata_order_column, "\""))
        
        # Process modeldata
        self.__table_ref = self.__awu._teradata_on_clause_from_dataframe(self.modeldata, False)
        self.__func_input_distribution.append("DIMENSION")
        self.__func_input_arg_sql_names.append("ModelTable")
        self.__func_input_table_view_query.append(self.__table_ref["ref"])
        self.__func_input_dataframe_type.append(self.__table_ref["ref_type"])
        self.__func_input_partition_by_cols.append("NA_character_")
        self.__func_input_order_by_cols.append(UtilFuncs._teradata_collapse_arglist(self.modeldata_order_column, "\""))

        function_name = "PMMLPredict"
        # Create instance to generate SQLMR.
        self.__aqg_obj = AnalyticQueryGenerator(function_name, 
                self.__func_input_arg_sql_names, 
                self.__func_input_table_view_query, 
                self.__func_input_dataframe_type, 
                self.__func_input_distribution, 
                self.__func_input_partition_by_cols, 
                self.__func_input_order_by_cols, 
                self.__func_other_arg_sql_names, 
                self.__func_other_args, 
                self.__func_other_arg_json_datatypes, 
                self.__func_output_args_sql_names, 
                self.__func_output_args, 
                engine="ENGINE_SQL", db_name=configure.byom_install_location)
        # Invoke call to SQL-MR generation.
        self.sqlmr_query = self.__aqg_obj._gen_sqlmr_select_stmt_sql()
        
        # Print SQL-MR query if requested to do so.
        if display.print_sqlmr_query:
            print(self.sqlmr_query)
        
        # Set the algorithm name for Model Cataloging.
        self._algorithm_name = self.__aqg_obj._get_alias_name_for_function(function_name)
        
    def __execute(self):
        """
        Function to execute SQL-MR queries. 
        Create DataFrames for the required SQL-MR outputs.
        """
        # Generate STDOUT table name and add it to the output table list.
        sqlmr_stdout_temp_tablename = UtilFuncs._generate_temp_table_name(prefix="td_sqlmr_out_", use_default_database=True, gc_on_quit=True, quote=False)
        try:
            # Generate the output.
            UtilFuncs._create_view(sqlmr_stdout_temp_tablename, self.sqlmr_query)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_EXEC_SQL_FAILED, str(emsg)), MessageCodes.TDMLDF_EXEC_SQL_FAILED)
        
        # Update output table data frames.
        self._mlresults = []
        self.result = self.__awu._create_data_set_object(df_input=UtilFuncs._extract_table_name(sqlmr_stdout_temp_tablename), source_type="table", database_name=UtilFuncs._extract_db_name(sqlmr_stdout_temp_tablename))
        self._mlresults.append(self.result)
        
    def show_query(self):
        """
        Function to return the underlying SQL query.
        When model object is created using retrieve_model(), the value returned will be None.
        """
        return self.sqlmr_query
        
    def get_prediction_type(self):
        """
        Function to return the Prediction type of the algorithm.
        When model object is created using retrieve_model(), the value returned may be None.
        """
        return self._prediction_type
        
    def get_target_column(self):
        """
        Function to return the Target Column of the algorithm.
        When model object is created using retrieve_model(), the value returned may be None.
        """
        return self._target_column
        
    def get_build_time(self):
        """
        Function to return the build time of the algorithm in seconds.
        When model object is created using retrieve_model(), the value returned may be None.
        """
        return self._build_time
        
    def _get_algorithm_name(self):
        """
        Function to return the name of the algorithm.
        """
        return self._algorithm_name
        
    def _get_sql_specific_attributes(self):
        """
        Function to return the dictionary containing the SQL specific attributes of the algorithm.
        """
        return self._sql_specific_attributes
        
    @classmethod
    def _from_model_catalog(cls,
        result = None,
        **kwargs):
        """
        Classmethod which will be used by Model Cataloging, to instantiate this wrapper class.
        """
        kwargs.pop("result", None)
        
        # Model Cataloging related attributes.
        target_column = kwargs.pop("__target_column", None)
        prediction_type = kwargs.pop("__prediction_type", None)
        algorithm_name = kwargs.pop("__algorithm_name", None)
        build_time = kwargs.pop("__build_time", None)
        
        # Let's create an object of this class.
        obj = cls(**kwargs)
        obj.result  = result 
        
        # Initialize the sqlmr_query class attribute.
        obj.sqlmr_query = None
        
        # Initialize the SQL specific Model Cataloging attributes.
        obj._sql_specific_attributes = None
        obj._target_column = target_column
        obj._prediction_type = prediction_type
        obj._algorithm_name = algorithm_name
        obj._build_time = build_time
        
        # Update output table data frames.
        obj._mlresults = []
        obj.result = obj.__awu._create_data_set_object(df_input=UtilFuncs._extract_table_name(obj.result), source_type="table", database_name=UtilFuncs._extract_db_name(obj.result))
        obj._mlresults.append(obj.result)
        return obj
        
    def __repr__(self):
        """
        Returns the string representation for a  PMMLPredict class instance.
        """
        repr_string="############ STDOUT Output ############"
        repr_string = "{}\n\n{}".format(repr_string,self.result)
        return repr_string
        
