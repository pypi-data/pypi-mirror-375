# ################################################################## 
# 
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Sweta Shaw
# Email Id: Sweta.Shaw@Teradata.com
# 
# Secondary Owner: Akhil Bisht
# Email Id: AKHIL.BISHT@Teradata.com
# 
# Version: 1.1
# Function Version: 1.0
# ##################################################################

# Python libraries
import pandas as pd
import warnings

# Teradata libraries
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml import Antiselect
from teradataml import BincodeTransform
from teradataml import ConvertTo
from teradataml import execute_sql
from teradataml import FillRowId
from teradataml import NonLinearCombineTransform
from teradataml import OneHotEncodingTransform
from teradataml import OrdinalEncodingTransform
from teradataml import RoundColumns
from teradataml import ScaleTransform
from teradataml import SimpleImputeTransform
from teradataml import TargetEncodingTransform
from teradataml import Transform, UtilFuncs, TeradataConstants
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.hyperparameter_tuner.utils import _ProgressBar
from teradataml.options.configure import configure
from teradataml.common.constants import TeradataConstants

# AutoML Internal libraries
from teradataml.automl.feature_exploration import _FeatureExplore
from teradataml.automl.feature_engineering import _FeatureEngineering


class _DataTransformation(_FeatureExplore, _FeatureEngineering):

    def __init__(self,
                 data,
                 data_transformation_params,
                 auto=True,
                 verbose=0,
                 target_column_ind=False,
                 table_name_mapping={},
                 cluster=False,
                 feature_selection_method=None):
        """
        DESCRIPTION:
            Function initializes the data, data transformation object and running mode
            for data transformation.
         
        PARAMETERS:  
            data:
                Required Argument.
                Specifies the input teradataml Dataframe for data transformation phase.
                Types: teradataml Dataframe
            
            data_transformation_params:
                Required Argument.
                Specifies the parameters for performing data transformation.
                Types: dict
            
            auto:
                Optional Argument.
                Specifies whether to run AutoML in custom mode or auto mode.
                When set to False, runs in custom mode. Otherwise, by default runs in auto mode.
                Default Value: True
                Types: bool
            
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints no details about data transformation.
                    * 1: prints the execution steps of data transformation.
                    * 2: prints the intermediate data between the each step of data transformation.
                Types: int
            
            target_column_ind:
                Optional Argument.
                Specifies whether target column is present in given dataset.
                Default Value: False
                Types: bool

            table_name_mapping:
                Optional Argument.
                Specifies the mapping of table names for the transformed data.
                Default Value: {}
                Types: dict

            cluster:
                Optional Argument.
                Specifies whether to apply clustering techniques.
                Default Value: False
                Types: bool

            feature_selection_method:
                Optional Argument.
                Specifies the feature selection method to be used.
                Default Value: None
                Types: str
        """
        self.data = data
        self.data_transformation_params = data_transformation_params
        self.auto = auto
        self.verbose = verbose
        self.target_column_ind = target_column_ind
        self.table_name_mapping = table_name_mapping
        self.data_types = {key: value for key, value in self.data._column_names_and_types}
        self.data_node_id = data._nodeid
        self.table_name_mapping[self.data_node_id] = {}

        self.cluster = cluster
        self.feature_selection_method = feature_selection_method 

    def data_transformation(self):
        """
        DESCRIPTION:
            Function to perform following tasks:
                1. Performs transformation carried out in feature engineering phase on the test data.
                2. Performs transformation carried out in data preparation phase on the test data.
        
        RETURNS:
            Table name mapping for the transformed data.
        """
        # Initializing Feature Exploration
        _FeatureExplore.__init__(self,
                                 data=self.data,
                                 target_column=None,
                                 verbose=self.verbose,
                                 cluster=self.cluster)
        # Initializing Feature Engineering
        _FeatureEngineering.__init__(self,
                                     data=self.data,
                                     target_column=None,
                                     model_list=None,
                                     verbose=self.verbose,
                                     cluster=self.cluster)
        
        self._display_msg(msg="Data Transformation started ...", show_data=True)
        # Extracting target column details and type whether it is classification or not
        self.data_target_column = self.data_transformation_params.get("data_target_column")
        self.classification_type = self.data_transformation_params.get("classification_type", False)
        
        # Setting number of jobs for progress bar based on mode of execution
        jobs = 9 if self.cluster else (10 if self.auto else 15)
        self.progress_bar = _ProgressBar(jobs=jobs, verbose=2, prefix='Transformation Running:')
        
        # Performing transformation carried out in feature engineering phase    
        self.feature_engineering_transformation()
        
        # Performing transformation carried out in data preparation phase
        self.data_preparation_transformation(feature_selection_method=self.feature_selection_method)
        self._display_msg(msg="Data Transformation completed.", show_data=True)

        return self.table_name_mapping

    def feature_engineering_transformation(self):
        """
        DESCRIPTION:
            Function performs transformation carried out in feature engineering phase
            on test data using parameters from data_transformation_params.
        """
        self._display_msg(msg="Performing transformation carried out in feature engineering phase ...", 
                          show_data=True,
                          progress_bar=self.progress_bar)

        # Performing default transformation for both auto and custom mode 
        self._preprocess_transformation()
        self.progress_bar.update()
        
        self._futile_column_handling_transformation()
        self.progress_bar.update()
        
        # Handling target column transformation
        if not self.cluster:
            if self.target_column_ind and self.classification_type:
                self._handle_target_column_transformation()
        self.progress_bar.update()

        self._date_column_handling_transformation()
        self.progress_bar.update()

        # Performing transformation according to run mode
        if self.auto:
            self._missing_value_handling_transformation()
            self.progress_bar.update()
            
            self._categorical_encoding_transformation()
            self.progress_bar.update()
        else:
            self._custom_missing_value_handling_transformation()
            self.progress_bar.update()
            
            self._custom_bincode_column_transformation()
            self.progress_bar.update()
            
            self._custom_string_column_transformation()
            self.progress_bar.update()
            
            self._custom_categorical_encoding_transformation()
            self.progress_bar.update()
            
            self._custom_mathematical_transformation()
            self.progress_bar.update()
            
            self._custom_non_linear_transformation()
            self.progress_bar.update()
            
            self._custom_anti_select_column_transformation()
            self.progress_bar.update()

    def data_preparation_transformation(self, feature_selection_method=None):
        """
        DESCRIPTION:
            Function performs transformation carried out in data preparation phase
            on test data using parameters from data_transformation_params.
        """
        self._display_msg(msg="Performing transformation carried out in data preparation phase ...", 
                          show_data=True,
                          progress_bar=self.progress_bar)
        
        # Handling features transformed from feature engineering phase
        self._handle_generated_features_transformation()
        self.progress_bar.update()

        # Performing transformation including feature selection using lasso, rfe and pca
        # followed by scaling
        if not self.cluster:
            self._feature_selection_lasso_transformation()
            self.progress_bar.update()
        
            self._feature_selection_rfe_transformation()
            self.progress_bar.update()

            self._feature_selection_pca_transformation()
            self.progress_bar.update()
        else:
            self._feature_selection_pca_transformation()
            self.progress_bar.update()

            self._feature_selection_non_pca_transformation()
            self.progress_bar.update()

    def _preprocess_transformation(self):
        """
        DESCRIPTION:
            Function drops irrelevent columns and adds id column.
        """
        # Extracting irrelevant column list
        columns_to_be_removed = self.data_transformation_params.get("drop_irrelevant_columns", None)
        if columns_to_be_removed:
            self.data = self.data.drop(columns_to_be_removed, axis=1)
            self._display_msg(msg="\nUpdated dataset after dropping irrelevant columns :",
                              data=self.data,
                              progress_bar=self.progress_bar)

        # Adding id column
        self.data = FillRowId(data=self.data, row_id_column='id').result

    def _futile_column_handling_transformation(self):
        """
        DESCRIPTION:
            Function drops futile columns from dataset.
        """
        # Extracting futile column list
        futile_cols = self.data_transformation_params.get("futile_columns", None)
        if futile_cols:
            self.data = self.data.drop(futile_cols, axis=1)
            self._display_msg(msg="\nUpdated dataset after dropping futile columns :", 
                              data=self.data,
                              progress_bar=self.progress_bar)

    def _date_column_handling_transformation(self):
        """
        DESCRIPTION:
            Function performs transformation on date columns and generates new columns.
        """
        # Extracting date columns
        self.date_column_list = self.data_transformation_params.get("date_columns",None)
        if self.date_column_list:
            # Dropping rows with null values in date columns
            self.data = self.data.dropna(subset=self.date_column_list)
            # Extracting unique date columns for dropping
            drop_unique_date_columns = self.data_transformation_params.get("drop_unique_date_columns",None)
            if drop_unique_date_columns:
                self.data = self.data.drop(drop_unique_date_columns, axis=1)
                # Updated date column list after dropping irrelevant date columns
                self.date_column_list = [item for item in self.date_column_list if item not in drop_unique_date_columns]

            if len(self.date_column_list) != 0:
                # Extracting date components parameters for new columns generation
                new_columns=self._fetch_date_component()
            
                # Extracting irrelevant date component columns for dropping  
                drop_extract_date_columns = self.data_transformation_params.get("drop_extract_date_columns", None)
                if drop_extract_date_columns:
                    self.data = self.data.drop(drop_extract_date_columns, axis=1)
                    new_columns = [item for item in new_columns if item not in drop_extract_date_columns]
                
                self._display_msg(msg='Updated list of newly generated features from existing date features :',
                                  col_lst=new_columns)
                self._display_msg(msg="\nUpdated dataset after transforming date columns :", 
                                  data=self.data,
                                  progress_bar=self.progress_bar)

    def _missing_value_handling_transformation(self):
        """
        DESCRIPTION:
            Function performs missing value handling by dropping columns and imputing columns.
        """
        # Extracting missing value containing columns to be dropped            
        drop_cols = self.data_transformation_params.get("drop_missing_columns", None)
        if drop_cols:
            self.data = self.data.drop(drop_cols, axis=1)
            self._display_msg(msg="\nUpdated dataset after dropping missing value containing columns : ", 
                              data=self.data,
                              progress_bar=self.progress_bar)

        # Extracting imputation columns and fit object for missing value imputation
        imputation_cols = self.data_transformation_params.get("imputation_columns", None)
        if imputation_cols:
            sm_fit_obj = self.data_transformation_params.get("imputation_fit_object")
            ## Workaround done for bug https://teradata-pe.atlassian.net/browse/TDAF-15617.
            #partition_column = self.data_transformation_params.get("imputation_partition_column", None)
            
            params = {"data" : self.data,
                      "object" : sm_fit_obj
                      }
            
            # if partition_column is not None:
            #     params["data_partition_column"] = partition_column
            #     params["object_partition_column"] = partition_column
            
            # imputing column using fit object
            self.data = SimpleImputeTransform(**params).result

            self._display_msg(msg="\nUpdated dataset after imputing missing value containing columns :", 
                              data=self.data,
                              progress_bar=self.progress_bar)

        # Handling rest null, its temporary solution. It subjects to change based on input.
        dropped_data = self.data.dropna()
        dropped_count = self.data.shape[0] - dropped_data.shape[0]
        if dropped_count > 0:
            self._display_msg(msg="\nFound additional {} rows that contain missing values :".format(dropped_count),
                              data=self.data,
                              progress_bar=self.progress_bar)
            self.data = dropped_data
            self._display_msg(msg="\nUpdated dataset after dropping additional missing value containing rows :", 
                              data=self.data,
                              progress_bar=self.progress_bar)

    def _custom_missing_value_handling_transformation(self):
        """
        DESCRIPTION:
            Function performs missing value handling by dropping columns and imputing
            columns based on user input.
        """
        # Extracting custom missing value containing columns to be dropped
        drop_col_list = self.data_transformation_params.get("custom_drop_missing_columns", None)
        if drop_col_list:
            self.data = self.data.drop(drop_col_list, axis=1)
            self._display_msg(msg="\nUpdated dataset after dropping customized missing value containing columns :", 
                              data=self.data,
                              progress_bar=self.progress_bar)

        # Extracting custom imputation columns and fit object for missing value imputation
        custom_imp_ind = self.data_transformation_params.get("custom_imputation_ind", False)  
        if custom_imp_ind:
            sm_fit_obj = self.data_transformation_params.get("custom_imputation_fit_object")
            # imputing column using fit object 
            self.data = SimpleImputeTransform(data=self.data, 
                                              object=sm_fit_obj).result
            self._display_msg(msg="\nUpdated dataset after imputing customized missing value containing columns :",
                              data=self.data,
                              progress_bar=self.progress_bar)
        # Handling rest with default missing value handling    
        self._missing_value_handling_transformation()

    def _custom_bincode_column_transformation(self):
        """
        DESCRIPTION:
            Function performs bincode transformation on columns based on user input.
        """
        # Extracting custom bincode columns and fit object for bincode transformation
        custom_bincode_ind = self.data_transformation_params.get("custom_bincode_ind", False)    
        if custom_bincode_ind:
            # Handling bincode transformation for Equal-Width
            custom_eql_bincode_col = self.data_transformation_params.get("custom_eql_bincode_col", None)
            custom_eql_bincode_fit_object = self.data_transformation_params.get("custom_eql_bincode_fit_object", None)
            if custom_eql_bincode_col:
                # Extracting accumulate columns
                accumulate_columns = self._extract_list(self.data.columns, custom_eql_bincode_col)
                # Adding transform parameters for performing binning with Equal-Width.
                eql_transform_params={
                    "data" : self.data,
                    "object" : custom_eql_bincode_fit_object,
                    "accumulate" : accumulate_columns,
                    "persist" : True,
                    "display_table_name" : False   
                }
                self.data = BincodeTransform(**eql_transform_params).result
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
                self._display_msg(msg="\nUpdated dataset after performing customized equal width bin-code transformation :",
                                  data=self.data,
                                  progress_bar=self.progress_bar)

            # Hnadling bincode transformation for Variable-Width
            custom_var_bincode_col = self.data_transformation_params.get("custom_var_bincode_col", None)
            custom_var_bincode_fit_object = self.data_transformation_params.get("custom_var_bincode_fit_object", None)
            if custom_var_bincode_col:
                # Extracting accumulate columns
                accumulate_columns = self._extract_list(self.data.columns, custom_var_bincode_col)
                # Adding transform parameters for performing binning with Variable-Width.
                var_transform_params = {
                    "data" : self.data,
                    "object" : custom_var_bincode_fit_object,
                    "object_order_column" : "TD_MinValue_BINFIT",
                    "accumulate" : accumulate_columns,
                    "persist" : True,
                    "display_table_name" : False   
                }
                self.data = BincodeTransform(**var_transform_params).result
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
                self._display_msg(msg="\nUpdated dataset after performing customized variable width bin-code transformation :",
                                  data=self.data,
                                  progress_bar=self.progress_bar)

    def _custom_string_column_transformation(self):
        """
        DESCRIPTION:
            Function performs string column transformation on categorical columns based on user input.
        """
        # Extracting custom string manipulation columns and fit object for performing string manipulation
        custom_string_manipulation_ind = self.data_transformation_params.get("custom_string_manipulation_ind", False)
        if custom_string_manipulation_ind:            
            custom_string_manipulation_param = self.data_transformation_params.get('custom_string_manipulation_param', None)
            # Performing string manipulation for each column
            for target_col,transform_val in custom_string_manipulation_param.items():            
                self.data = self._str_method_mapping(target_col, transform_val)
            self._display_msg(msg="\nUpdated dataset after performing customized string manipulation :",
                              data=self.data,
                              progress_bar=self.progress_bar)

    def _categorical_encoding_transformation(self):
        """
        DESCRIPTION:
            Function performs default encoding transformation i.e, one-hot on categorical columns.
        """
        # Extracting one hot encoding parameters for performing encoding
        one_hot_encoding_ind = self.data_transformation_params.get("one_hot_encoding_ind", False)    
        one_hot_encoding_fit_obj = self.data_transformation_params.get("one_hot_encoding_fit_obj", None)
        one_hot_encoding_drop_list = self.data_transformation_params.get("one_hot_encoding_drop_list", None)
        if one_hot_encoding_ind:
            # Adding transform parameters for performing encoding
            for fit_obj in one_hot_encoding_fit_obj.values():
                transform_params = {
                        "data" : self.data, 
                        "object" : fit_obj, 
                        "is_input_dense" : True,
                        "persist" : True,
                        "display_table_name" : False
                    }
                # Performing one hot encoding transformation
                self.data = OneHotEncodingTransform(**transform_params).result
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
            # Dropping old columns after encoding        
            self.data = self.data.drop(one_hot_encoding_drop_list, axis=1)  
            self._display_msg(msg="\nUpdated dataset after performing categorical encoding :",
                              data=self.data,
                              progress_bar=self.progress_bar)
            return

        # AutoFraud Routine
        auto_target_encoding_ind = self.data_transformation_params.get("auto_target_encoding_ind", False)    
        auto_target_encoding_fit_obj = self.data_transformation_params.get("auto_target_encoding_fit_obj", None)
        target_encoding_accumulate_columns = self.data_transformation_params.get("target_encoding_accumulate_columns")
        
        if auto_target_encoding_ind:
            # Adding transform parameters for performing encoding
            transform_params = {
                    "data" : self.data, 
                    "object" : auto_target_encoding_fit_obj,
                    "accumulate" : target_encoding_accumulate_columns,
                    "is_input_dense" : True,
                    "persist" : True,
                    "display_table_name" : False
                }
            
            # Performing one hot encoding transformation
            self.data = TargetEncodingTransform(**transform_params).result

            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(self.data._table_name)     
            
            self._display_msg(msg="\nUpdated dataset after performing categorical encoding :",
                              data=self.data,
                              progress_bar=self.progress_bar)
            
    def _custom_categorical_encoding_transformation(self):
        """
        DESCRIPTION:
            Function performs custom encoding transformation on categorical columns based on user input.
        """
        # Extracting custom encoding parameters for performing encoding
        custom_categorical_encoding_ind = self.data_transformation_params.get("custom_categorical_encoding_ind", False)
        if custom_categorical_encoding_ind:
            # Extracting parameters for ordinal encoding
            custom_ord_encoding_fit_obj = self.data_transformation_params.get("custom_ord_encoding_fit_obj", None)
            custom_ord_encoding_col = self.data_transformation_params.get("custom_ord_encoding_col", None)
            if custom_ord_encoding_col:
                # Extracting accumulate columns
                accumulate_columns = self._extract_list(self.data.columns, custom_ord_encoding_col)
                # Adding transform parameters for performing encoding
                transform_params = {
                    "data" : self.data,
                    "object" : custom_ord_encoding_fit_obj,
                    "accumulate" : accumulate_columns,
                    "persist" : True,
                    "display_table_name" : False
                }
                # Performing ordinal encoding transformation
                self.data = OrdinalEncodingTransform(**transform_params).result
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
            # Extracting parameters for target encoding
            custom_target_encoding_ind = self.data_transformation_params.get("custom_target_encoding_ind", False)
            custom_target_encoding_fit_obj = self.data_transformation_params.get("custom_target_encoding_fit_obj", None)
            if custom_target_encoding_ind:
                warn_cols = []
                for col, tar_fit_obj in custom_target_encoding_fit_obj.items():
                    # Extracting accumulate columns
                    accumulate_columns = self._extract_list(self.data.columns, [col])
                    # Adding transform parameters for performing encoding
                    transform_params = {
                        "data" : self.data,
                        "object" : tar_fit_obj,
                        "accumulate" : accumulate_columns,
                        "persist" : True,
                        "display_table_name" : False                
                    }
                    # Performing target encoding transformation
                    self.data = TargetEncodingTransform(**transform_params).result
                    # Adding transformed data containing table to garbage collector
                    GarbageCollector._add_to_garbagecollector(self.data._table_name)
                    if self.data[self.data[col] == -1].shape[0] > 0:
                        warn_cols.append(col)
                
                # Checking for unseen values in target encoding columns
                if len(warn_cols) > 0:
                    warnings.warn(message=f"Unseen categorical values found in test data column(s): {warn_cols}. \
                                  This may cause inaccurate predictions. Consider retraining the model with updated data.",
                                  stacklevel=0)

            self._display_msg(msg="\nUpdated dataset after performing customized categorical encoding :",
                              data=self.data,
                              progress_bar=self.progress_bar)

        # Handling rest with default categorical encoding transformation    
        self._categorical_encoding_transformation()

    def _custom_mathematical_transformation(self):
        """
        DESCRIPTION:
            Function performs custom mathematical transformation on numerical columns based on user input.
        """
        # Extracting custom mathematical transformation parameters for performing transformation
        custom_mathematical_transformation_ind = self.data_transformation_params.get("custom_mathematical_transformation_ind", False)
        if custom_mathematical_transformation_ind:
            # Extracting parameters for performing numapply transformation
            custom_numapply_transformation_param = self.data_transformation_params.get("custom_numapply_transformation_param", None)
            # Checking if numapply transformation param is present
            if custom_numapply_transformation_param:
                # Performing transformation for each column
                for col, transform_val in custom_numapply_transformation_param.items():
                    self.data = self._numapply_transformation(col,transform_val)

            # Extracting parameters for performing numerical transformation
            custom_numerical_transformation_fit_object = self.data_transformation_params.get("custom_numerical_transformation_fit_object", None)
            # Checking if numerical transformation fit object is present
            if custom_numerical_transformation_fit_object:
                # Extracting id columns for performing transformation
                custom_numerical_transformation_id_columns = self.data_transformation_params.get("custom_numerical_transformation_id_columns", None)
                # Checking for target column presence and handling id columns accordingly
                if not self.target_column_ind and \
                    self.data_target_column in custom_numerical_transformation_id_columns:
                    custom_numerical_transformation_id_columns = self._extract_list(
                                                                custom_numerical_transformation_id_columns, 
                                                                [self.data_target_column])

                # Adding transform parameters for transformation
                transform_params={
                    "data" : self.data,
                    "object" : custom_numerical_transformation_fit_object,
                    "id_columns" : custom_numerical_transformation_id_columns,
                    "persist" :True,
                    "display_table_name" : False
                }
                # Peforming transformation on target columns
                self.data = Transform(**transform_params).result
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
            self._display_msg(msg="\nUpdated dataset after performing customized mathematical transformation :",
                              data=self.data,
                              progress_bar=self.progress_bar)

    def _custom_non_linear_transformation(self):
        """
        DESCRIPTION:
            Function performs custom non-linear transformation on numerical columns based on user input.
        """
        # Extracting custom non-linear transformation parameters for performing transformation
        custom_non_linear_transformation_ind = self.data_transformation_params.get("custom_non_linear_transformation_ind", False)
        if custom_non_linear_transformation_ind:
            # Extracting fit object for non-linear transformation
            fit_obj_list = self.data_transformation_params['custom_non_linear_transformation_fit_object']
            for comb, fit_obj in fit_obj_list.items():
                # Adding transform params for transformation   
                transform_params = {
                    "data" : self.data,
                    "object" : fit_obj,
                    "accumulate" : self.data.columns,
                    "persist" : True,
                    "display_table_name" : False
                }
                # Performing transformation
                self.data = NonLinearCombineTransform(**transform_params).result
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
            self._display_msg(msg="\nUpdated dataset after performing customized non-linear transformation :",
                              data=self.data,
                              progress_bar=self.progress_bar)

    def _custom_anti_select_column_transformation(self):
        """
        DESCRIPTION:
            Function performs custom anti-select transformation on columns based on user input.
        """
        # Extracting custom anti-select transformation parameters for performing transformation
        custom_anti_select_columns_ind = self.data_transformation_params.get("custom_anti_select_columns_ind", False)
        if custom_anti_select_columns_ind:
            # Extracting anti-select column list
            anti_select_list = self.data_transformation_params.get("custom_anti_select_columns",None)
            if anti_select_list:
                fit_params = {
                    "data" : self.data,
                    "exclude" : anti_select_list
                }
                # Performing transformation for given user input
                self.data = Antiselect(**fit_params).result
                self._display_msg(msg="\nUpdated dataset after performing customized anti-selection :",
                                  data=self.data,
                                  progress_bar=self.progress_bar)

    def _handle_generated_features_transformation(self):
        """
        DESCRIPTION:
            Function performs rounding up transformation on generated features 
            from feature engineering phase.
        """
        # Extracting list of columns to be rounded
        round_columns = self.data_transformation_params.get("round_columns", None)
        if round_columns:
            # Checking for target column presence and handling list accordingly
            if not self.target_column_ind and self.data_target_column in round_columns:
                round_columns = self._extract_list(round_columns, [self.data_target_column])

            # Extracting accumulate columns
            accumulate_columns = self._extract_list(self.data.columns,round_columns)
            # Performing rounding up on target column upto 4 precision digit
            fit_params = {
                "data" : self.data,
                "target_columns" : round_columns,
                "precision_digit" : 4,
                "accumulate" : accumulate_columns,
                "persist" : True,
                "display_table_name" : False}
            self.data = RoundColumns(**fit_params).result
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(self.data._table_name)
            
    def _handle_target_column_transformation(self):
        """
        DESCRIPTION:
            Function performs encoding and datatype transformation on target column
            for classification problem.
        """
        # Fetching target column encoding indicator and fit object
        
        target_col_encode_ind = self.data_transformation_params.get("target_col_encode_ind", False)
    
        if target_col_encode_ind:
            # Extracting ordinal encoding fit object for target column
            target_col_ord_encoding_fit_obj = self.data_transformation_params.get("target_col_ord_encoding_fit_obj", None)
            if target_col_ord_encoding_fit_obj:
                # Extracting accumulate columns
                accumulate_columns = self._extract_list(self.data.columns, [self.data_target_column])
                # Adding transform parameters for performing encoding
                transform_params = {
                    "data" : self.data,
                    "object" : target_col_ord_encoding_fit_obj,
                    "accumulate" : accumulate_columns,
                    "persist" : True,
                    "display_table_name" : False
                }
                # Performing ordinal encoding transformation
                self.data = OrdinalEncodingTransform(**transform_params).result
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
        
        self._display_msg(msg="\nUpdated dataset after performing target column transformation :",
                          data=self.data,
                          progress_bar=self.progress_bar)

    def _extract_and_display_features(self, feature_type, feature_list):
        """
        DESCRIPTION:
            Function performs extraction of features using feature_list and target column indicator.
        
        PARAMETERS:
            feature_type:
                Required Argument.
                Specifies the type of feature selection.
                Types: str
            
            feature_list:
                Required Argument.
                Specifies the list of features to be selected.
                Types: list
            
        RETURNS:
            Teradataml dataframe with selected features.
        """
        # Checking for target column presence and handling list accordingly
        if not self.target_column_ind and self.data_target_column in feature_list:
            feature_list = self._extract_list(feature_list, [self.data_target_column])
        
        # Creating dataframe with selected features
        feature_df = self.data[feature_list]
        
        # Displaying feature dataframe
        self._display_msg(msg=f"\nUpdated dataset after performing {feature_type} feature selection:",
                          data=feature_df,
                          progress_bar=self.progress_bar)

        # Returning feature dataframe
        return feature_df

    def _feature_selection_lasso_transformation(self):
        """
        DESCRIPTION:
            Function performs feature selection using lasso followed by scaling.
        """
        # Extracting features selected by lasso in data preparation phase
        lasso_features = self.data_transformation_params.get("lasso_features", None)
        lasso_df = self._extract_and_display_features("Lasso", lasso_features)

        # Performing feature scaling
        # Extracting fit object and columns for scaling
        lasso_scale_fit_obj = self.data_transformation_params.get("lasso_scale_fit_obj", None)
        lasso_scale_col = self.data_transformation_params.get("lasso_scale_col", None)
        # Extracting accumulate columns
        if lasso_scale_fit_obj is not None:
            accumulate_cols = self._extract_list(lasso_df.columns, lasso_scale_col)
            # Scaling dataset
            lasso_df = ScaleTransform(data=lasso_df,
                        object=lasso_scale_fit_obj,
                        accumulate=accumulate_cols).result
            # Displaying scaled dataset
            self._display_msg(msg="\nUpdated dataset after performing scaling on Lasso selected features :",
                              data=lasso_df,
                              progress_bar=self.progress_bar)

        # Uploading lasso dataset to table for further use
        table_name = UtilFuncs._generate_temp_table_name(prefix="lasso_test", 
                                                         table_type = TeradataConstants.TERADATA_TABLE)
        # If configure.temp_object_type="VT", _generate_temp_table_name() retruns the
        # table name in fully qualified format.
        table_name = UtilFuncs._extract_table_name(table_name)
        # Storing table name mapping for lasso dataset
        self.table_name_mapping[self.data_node_id]["lasso_test"] = table_name
        # In the case of the VT option, the table was being persisted, so the VT condition is being checked. 
        is_temporary = configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE
        copy_to_sql(df = lasso_df, table_name= table_name, if_exists="replace", temporary=is_temporary)

    def _feature_selection_rfe_transformation(self):
        """
        DESCRIPTION:
            Function performs feature selection using rfe followed by scaling.
        """
        # Extracting features selected by rfe in data preparation phase
        rfe_features = self.data_transformation_params.get("rfe_features", None)
        rfe_df = self._extract_and_display_features("RFE", rfe_features)

        # Renaming rfe columns
        rfe_rename_column = self.data_transformation_params.get("rfe_rename_column", None)
        if rfe_rename_column:
            new_col_name = {f'r_{col}': rfe_df[col] for col in rfe_rename_column}
            rfe_df = rfe_df.assign(drop_columns=False, **new_col_name)
            rfe_df = rfe_df.drop(rfe_rename_column, axis=1)

        # Performing feature scaling
        # Extracting fit object and columns for scaling
        rfe_scale_fit_obj = self.data_transformation_params.get("rfe_scale_fit_obj", None)
        rfe_scale_col = self.data_transformation_params.get("rfe_scale_col", None)

        if rfe_scale_fit_obj is not None:
            # Extracting accumulate columns
            accumulate_cols = self._extract_list(rfe_df.columns, rfe_scale_col)
            # Scaling on rfe dataset
            rfe_df = ScaleTransform(data=rfe_df,
                                    object=rfe_scale_fit_obj,
                                    accumulate=accumulate_cols).result
            # Displaying scaled dataset
            self._display_msg(msg="\nUpdated dataset after performing scaling on RFE selected features :",
                              data=rfe_df,
                              progress_bar=self.progress_bar)    

        # Uploading rfe dataset to table for further use
        table_name = UtilFuncs._generate_temp_table_name(prefix="rfe_test", 
                                                         table_type = TeradataConstants.TERADATA_TABLE)
        # If configure.temp_object_type="VT", _generate_temp_table_name() retruns the
        # table name in fully qualified format.
        table_name = UtilFuncs._extract_table_name(table_name)
        # Storing table name mapping for rfe dataset
        self.table_name_mapping[self.data_node_id]["rfe_test"] = table_name
        # In the case of the VT option, the table was being persisted, so the VT condition is being checked. 
        is_temporary = configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE
        copy_to_sql(df = rfe_df, table_name= table_name, if_exists="replace", temporary=is_temporary)

    def _feature_selection_pca_transformation(self):
        """
        DESCRIPTION:
            Function performs feature scaling followed by feature selection using pca.
        """
        # Extracting fit object and column details for perfroming feature scaling
        pca_scale_fit_obj = self.data_transformation_params.get("pca_scale_fit_obj", None)
        pca_scale_col = self.data_transformation_params.get("pca_scale_col", None)
        
        pca_scaled_df = self.data
        if pca_scale_fit_obj is not None:
            # Extracting accumulate columns
            accumulate_cols = self._extract_list(self.data.columns, pca_scale_col)
            # Scaling on pca dataset
            pca_scaled_df = ScaleTransform(data=self.data,
                                           object=pca_scale_fit_obj,
                                           accumulate=accumulate_cols).result
            # Displaying scaled dataset
            self._display_msg(msg="\nUpdated dataset after performing scaling for PCA feature selection :",
                              data=pca_scaled_df,
                              progress_bar=self.progress_bar)

        # Convert to pandas dataframe for applying pca
        pca_scaled_pd = pca_scaled_df.to_pandas().reset_index()
        # Extracting pca fit instance for applying pca
        pca_fit_instance = self.data_transformation_params.get("pca_fit_instance", None)
        # Extracting columns for applying pca  
        pca_fit_columns = self.data_transformation_params.get("pca_fit_columns", None)

        # drop id column and target column if present
        drop_col = ['id']
        if self.target_column_ind:
            drop_col.append(self.data_target_column)
        pca_df = pca_scaled_pd.drop(columns=drop_col, axis=1)
        
        # Rearranging columns to match the order used during PCA fitting to 
        # avoid issues during PCA transformation.
        pca_df = pca_df[pca_fit_columns]

        # Applying pca on scaled dataset
        pca_df = pca_fit_instance.transform(pca_df)
        # Converting to pandas dataframe
        pca_df  = pd.DataFrame(pca_df)
        # Renaming pca columns
        pca_new_column = self.data_transformation_params.get("pca_new_column", None)
        pca_df.rename(columns=pca_new_column, inplace=True)
        # Adding id column to pca dataframe
        pca_df = pd.concat([pca_scaled_pd.reset_index(drop=True)['id'], pca_df.reset_index(drop=True)], axis=1)
        # Adding target column to pca dataframe if present
        if self.target_column_ind: 
            pca_df[self.data_target_column] = pca_scaled_pd[self.data_target_column].reset_index(drop=True)
        # Displaying pca dataframe
        self._display_msg(msg="\nUpdated dataset after performing PCA feature selection :",
                          data=pca_df.head(10),
                          progress_bar=self.progress_bar)

        # Uploading pca dataset to table for further use
        table_name = UtilFuncs._generate_temp_table_name(prefix="pca_test", 
                                                         table_type = TeradataConstants.TERADATA_TABLE)
        # If configure.temp_object_type="VT", _generate_temp_table_name() retruns the
        # table name in fully qualified format.
        table_name = UtilFuncs._extract_table_name(table_name)
        # Storing table name mapping for pca dataset
        self.table_name_mapping[self.data_node_id]["pca_test"] = table_name
        # In the case of the VT option, the table was being persisted, so the VT condition is being checked. 
        is_temporary = configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE
        copy_to_sql(df = pca_df, table_name=table_name, if_exists="replace", temporary=is_temporary)
        
    def _feature_selection_non_pca_transformation(self):
        """
        DESCRIPTION:
            Function performs feature scaling on raw data for non-PCA clustering models.
        """
        self._display_msg(msg="\nRunning Non-PCA feature selection transformation for clustering...",
                          show_data=True,
                          progress_bar=self.progress_bar)

        # Extracting fit object and columns for scaling
        non_pca_scale_fit_obj = self.data_transformation_params.get("non_pca_scale_fit_obj", None)
        non_pca_scale_col = self.data_transformation_params.get("non_pca_scale_col", None)

        if non_pca_scale_fit_obj is not None and non_pca_scale_col is not None:
            accumulate_cols = self._extract_list(self.data.columns, non_pca_scale_col)

            # Scaling dataset
            scaled_df = ScaleTransform(data=self.data,
                                       object=non_pca_scale_fit_obj,
                                       accumulate=accumulate_cols).result

            # Displaying scaled dataset
            self._display_msg(msg="\nUpdated dataset after performing Non-PCA scaling for clustering:",
                              data=scaled_df,
                              progress_bar=self.progress_bar)

            # Uploading non_pca dataset to SQL
            table_name = UtilFuncs._generate_temp_table_name(prefix="non_pca_test",
                                                             table_type=TeradataConstants.TERADATA_TABLE)
            self.table_name_mapping[self.data_node_id]["non_pca_test"] = table_name
            copy_to_sql(df=scaled_df, table_name=table_name, if_exists="replace")
        else:
            print(" Missing non_pca_scale_fit_obj or non_pca_scale_col in data transformation params.")
