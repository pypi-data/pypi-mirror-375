#!/usr/bin/python
# ################################################################## 
# 
# Copyright 2018 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# Secondary Owner: Mounika Kotha (mounika.kotha@teradata.com)
# 
# Version: 1.0
# Function Version: 1.0
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

class DecisionTreePredict:
    
    def __init__(self,
        object = None,
        newdata = None,
        attr_table_groupby_columns = None,
        attr_table_pid_columns = None,
        attr_table_val_column = None,
        output_response_probdist = False,
        accumulate = None,
        output_responses = None,
        newdata_partition_column = None,
        newdata_order_column = None,
        object_order_column = None):
        """
        DESCRIPTION:
            The DecisionTreePredict function applies a tree model to a data
            input, outputting predicted labels for each data point.
         
         
        PARAMETERS:
            object:
                Required Argument.
                Specifies the name of the teradataml DataFrame containing the output 
                model from DecisionTree.
         
            object_order_column:
                Optional Argument.
                Specifies Order By columns for object.
                Values to this argument can be provided as a list, if multiple
                columns are used for ordering.
                Types: str OR list of Strings (str)
         
            newdata:
                Required Argument.
                Specifies the name of the teradataml DataFrame containing the 
                attribute names and the values.
         
            newdata_partition_column:
                Required Argument.
                Specifies Partition By columns for newdata.
                Values to this argument can be provided as a list, if multiple
                columns are used for partition.
                Types: str OR list of Strings (str)
         
            newdata_order_column:
                Optional Argument.
                Specifies Order By columns for newdata.
                Values to this argument can be provided as a list, if multiple
                columns are used for ordering.
                Types: str OR list of Strings (str)
         
            attr_table_groupby_columns:
                Required Argument.
                Specifies the names of the columns on which newdata is
                partitioned. Each partition contains one attribute of the input data.
                Types: str OR list of Strings (str)
         
            attr_table_pid_columns:
                Required Argument.
                Specifies the names of the columns that define the data point 
                identifiers.
                Types: str OR list of Strings (str)
         
            attr_table_val_column:
                Required Argument.
                Specifies the name of the column that contains the input values.
                Types: str
         
            output_response_probdist:
                Optional Argument.
                Specifies whether to output probabilities.
                Note: 'output_response_probdist' argument can accept input value True
                      only when teradataml is connected to Vantage 1.0 Maintenance
                      Update 2 version or later.
                Default Value: False
                Types: bool
         
            accumulate:
                Optional Argument.
                Specifies the names of newdata columns to copy to the output
                teradataml DataFrame.
                Types: str OR list of Strings (str)
         
            output_responses:
                Optional Argument.
                Required if output_response_probdist is True.
                Specifies all responses in newdata.
                Types: str OR list of Strings (str)
         
        RETURNS:
            Instance of DecisionTreePredict.
            Output teradataml DataFrames can be accessed using attribute 
            references, such as DecisionTreePredictObj.<attribute_name>.
            Output teradataml DataFrame attribute name is:
                result
         
         
        RAISES:
            TeradataMlException
         
         
        EXAMPLES:
            # Load the data to run the example.
            load_example_data("DecisionTreePredict", ["iris_response_train",
                                                      "iris_attribute_test",
                                                      "iris_attribute_output"])


            # Create teradataml DataFrame.
            iris_attribute_test = DataFrame.from_table("iris_attribute_test")
            iris_response_train = DataFrame.from_table("iris_response_train")
            iris_attribute_output = DataFrame.from_table("iris_attribute_output")

            # Example 1 -
         
            # Run predict on the output of decision tree in iris_attribute_output
            decision_tree_predict_out = DecisionTreePredict(newdata=iris_attribute_test,
                                                            newdata_partition_column='pid',
                                                            object=iris_attribute_output,
                                                            attr_table_groupby_columns='attribute',
                                                            attr_table_pid_columns='pid',
                                                            attr_table_val_column='attrvalue',
                                                            accumulate='attribute',
                                                            output_response_probdist=True,
                                                            output_responses=['1', '2', '3'])
         
            # Print output dataframes
            print(decision_tree_predict_out.result)
        
        """
        
        # Start the timer to get the build time
        _start_time = time.time()
        
        self.object  = object 
        self.newdata  = newdata 
        self.attr_table_groupby_columns  = attr_table_groupby_columns 
        self.attr_table_pid_columns  = attr_table_pid_columns 
        self.attr_table_val_column  = attr_table_val_column 
        self.output_response_probdist  = output_response_probdist 
        self.accumulate  = accumulate 
        self.output_responses  = output_responses 
        self.newdata_partition_column  = newdata_partition_column 
        self.newdata_order_column  = newdata_order_column 
        self.object_order_column  = object_order_column 
        
        # Create TeradataPyWrapperUtils instance which contains validation functions.
        self.__awu = AnalyticsWrapperUtils()
        self.__aed_utils = AedUtils()
        
        # Create argument information matrix to do parameter checking
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["object", self.object, False, (DataFrame)])
        self.__arg_info_matrix.append(["object_order_column", self.object_order_column, True, (str,list)])
        self.__arg_info_matrix.append(["newdata", self.newdata, False, (DataFrame)])
        self.__arg_info_matrix.append(["newdata_partition_column", self.newdata_partition_column, False, (str,list)])
        self.__arg_info_matrix.append(["newdata_order_column", self.newdata_order_column, True, (str,list)])
        self.__arg_info_matrix.append(["attr_table_groupby_columns", self.attr_table_groupby_columns, False, (str,list)])
        self.__arg_info_matrix.append(["attr_table_pid_columns", self.attr_table_pid_columns, False, (str,list)])
        self.__arg_info_matrix.append(["attr_table_val_column", self.attr_table_val_column, False, (str)])
        self.__arg_info_matrix.append(["output_response_probdist", self.output_response_probdist, True, (bool)])
        self.__arg_info_matrix.append(["accumulate", self.accumulate, True, (str,list)])
        self.__arg_info_matrix.append(["output_responses", self.output_responses, not self.output_response_probdist, (str,list), True])
        
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
        self.__awu._validate_input_table_datatype(self.object, "object", reference_function_name=None)
        
        # Check whether the input columns passed to the argument are not empty.
        # Also check whether the input columns passed to the argument valid or not.
        self.__awu._validate_input_columns_not_empty(self.attr_table_groupby_columns, "attr_table_groupby_columns")
        self.__awu._validate_dataframe_has_argument_columns(self.attr_table_groupby_columns, "attr_table_groupby_columns", self.newdata, "newdata", False)
        
        self.__awu._validate_input_columns_not_empty(self.attr_table_pid_columns, "attr_table_pid_columns")
        self.__awu._validate_dataframe_has_argument_columns(self.attr_table_pid_columns, "attr_table_pid_columns", self.newdata, "newdata", False)
        
        self.__awu._validate_input_columns_not_empty(self.attr_table_val_column, "attr_table_val_column")
        self.__awu._validate_dataframe_has_argument_columns(self.attr_table_val_column, "attr_table_val_column", self.newdata, "newdata", False)
        
        self.__awu._validate_input_columns_not_empty(self.accumulate, "accumulate")
        self.__awu._validate_dataframe_has_argument_columns(self.accumulate, "accumulate", self.newdata, "newdata", False)
        
        self.__awu._validate_input_columns_not_empty(self.newdata_partition_column, "newdata_partition_column")
        self.__awu._validate_dataframe_has_argument_columns(self.newdata_partition_column, "newdata_partition_column", self.newdata, "newdata", True)
        
        self.__awu._validate_input_columns_not_empty(self.newdata_order_column, "newdata_order_column")
        self.__awu._validate_dataframe_has_argument_columns(self.newdata_order_column, "newdata_order_column", self.newdata, "newdata", False)
        
        self.__awu._validate_input_columns_not_empty(self.object_order_column, "object_order_column")
        self.__awu._validate_dataframe_has_argument_columns(self.object_order_column, "object_order_column", self.object, "object", False)
        
        
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
        
        self.__func_other_arg_sql_names.append("AttrTableGroupbyColumns")
        self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.attr_table_groupby_columns, "'"))
        self.__func_other_arg_json_datatypes.append("COLUMNS")
        
        self.__func_other_arg_sql_names.append("AttrTablePidColumns")
        self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.attr_table_pid_columns, "'"))
        self.__func_other_arg_json_datatypes.append("COLUMNS")
        
        self.__func_other_arg_sql_names.append("AttrTableValColumn")
        self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.attr_table_val_column, "'"))
        self.__func_other_arg_json_datatypes.append("COLUMNS")
        
        if self.accumulate is not None:
            self.__func_other_arg_sql_names.append("Accumulate")
            self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.accumulate, "'"))
            self.__func_other_arg_json_datatypes.append("COLUMNS")
        
        if self.output_response_probdist is not None and self.output_response_probdist != False:
            self.__func_other_arg_sql_names.append("OutputResponseProbDist")
            self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.output_response_probdist, "'"))
            self.__func_other_arg_json_datatypes.append("BOOLEAN")
        
        if self.output_responses is not None:
            self.__func_other_arg_sql_names.append("Responses")
            self.__func_other_args.append(UtilFuncs._teradata_collapse_arglist(self.output_responses, "'"))
            self.__func_other_arg_json_datatypes.append("STRING")
        
        
        # Declare empty lists to hold input table information.
        self.__func_input_arg_sql_names = []
        self.__func_input_table_view_query = []
        self.__func_input_dataframe_type = []
        self.__func_input_distribution = []
        self.__func_input_partition_by_cols = []
        self.__func_input_order_by_cols = []
        
        # Process newdata
        self.newdata_partition_column = UtilFuncs._teradata_collapse_arglist(self.newdata_partition_column, "\"")
        self.__table_ref = self.__awu._teradata_on_clause_from_dataframe(self.newdata, False)
        self.__func_input_distribution.append("FACT")
        self.__func_input_arg_sql_names.append("Attribute_Table")
        self.__func_input_table_view_query.append(self.__table_ref["ref"])
        self.__func_input_dataframe_type.append(self.__table_ref["ref_type"])
        self.__func_input_partition_by_cols.append(self.newdata_partition_column)
        self.__func_input_order_by_cols.append(UtilFuncs._teradata_collapse_arglist(self.newdata_order_column, "\""))
        
        # Process object
        self.__table_ref = self.__awu._teradata_on_clause_from_dataframe(self.object, False)
        self.__func_input_distribution.append("DIMENSION")
        self.__func_input_arg_sql_names.append("Model_Table")
        self.__func_input_table_view_query.append(self.__table_ref["ref"])
        self.__func_input_dataframe_type.append(self.__table_ref["ref_type"])
        self.__func_input_partition_by_cols.append("NA_character_")
        self.__func_input_order_by_cols.append(UtilFuncs._teradata_collapse_arglist(self.object_order_column, "\""))
        
        function_name = "DecisionTreePredict"
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
                skip_config_lookup=True,
                engine="ENGINE_SQL")
        # Invoke call to SQL-MR generation.
        self.sqlmr_query = self.__aqg_obj._gen_sqlmr_select_stmt_sql()
        
        # Print SQL-MR query if requested to do so.
        if display.print_sqlmr_query:
            print(self.sqlmr_query)
        
        # Set the algorithm name for Model Cataloging.
        self._algorithm_name = function_name
        
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
        When model object is created using retrieve_model(), then None is returned.
        """
        return self.sqlmr_query
        
    def get_prediction_type(self):
        """
        Function to return the Prediction type of the algorithm.
        When model object is created using retrieve_model(), then the value returned is
        as saved in the Model Catalog.
        """
        return self._prediction_type
        
    def get_target_column(self):
        """
        Function to return the Target Column of the algorithm.
        When model object is created using retrieve_model(), then the value returned is
        as saved in the Model Catalog.
        """
        return self._target_column
        
    def get_build_time(self):
        """
        Function to return the build time of the algorithm in seconds.
        When model object is created using retrieve_model(), then the value returned is
        as saved in the Model Catalog.
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
        Classmethod is used by Model Cataloging, to instantiate this wrapper class.
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
        Returns the string representation for a DecisionTreePredict class instance.
        """
        repr_string="############ STDOUT Output ############"
        repr_string = "{}\n\n{}".format(repr_string,self.result)
        return repr_string
