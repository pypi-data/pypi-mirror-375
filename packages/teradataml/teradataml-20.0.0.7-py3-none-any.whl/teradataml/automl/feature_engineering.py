# ################################################################## 
# 
# Copyright 2025 Teradata. All rights reserved.
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
import time
import json
import re

# Teradata libraries
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml import Antiselect
from teradataml import BincodeFit, BincodeTransform
from teradataml import CategoricalSummary, ColumnSummary, ConvertTo, GetFutileColumns, FillRowId
from teradataml import Fit, Transform
from teradataml import NonLinearCombineFit, NonLinearCombineTransform
from teradataml import NumApply
from teradataml import OneHotEncodingFit, OneHotEncodingTransform
from teradataml import OrdinalEncodingFit, OrdinalEncodingTransform
from teradataml import SimpleImputeFit, SimpleImputeTransform
from teradataml import StrApply
from teradataml import TargetEncodingFit, TargetEncodingTransform
from sqlalchemy import literal_column
from teradatasqlalchemy import INTEGER
from teradataml import display
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.dataframe.sql_functions import case
from teradataml.hyperparameter_tuner.utils import _ProgressBar
from teradataml.utils.validators import _Validators
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import TeradataConstants
from teradataml.options.configure import configure


class _FeatureEngineering:
    
    def __init__(self,
                 data,
                 target_column,
                 model_list,
                 verbose=0,
                 task_type="Regression",
                 custom_data=None,
                 **kwargs):
        """
        DESCRIPTION:
            Function initializes the data, target column and columns datatypes
            for feature engineering.
         
        PARAMETERS:  
            data:
                Required Argument.
                Specifies the input teradataml DataFrame for feature engineering.
                Types: teradataml Dataframe
            
            target_column:
                Required Argument.
                Specifies the name of the target column in "data"..
                Types: str
            
            model_list:
                Required Argument.
                Specifies the list of models to be used for model training.
                Types: list
            
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int

            task_type:
                Required Argument.
                Specifies the task type for AutoML, whether to apply regresion OR classification OR clustering
                on the provived dataset.
                Default Value: "Regression"
                Permitted Values: "Regression", "Classification", "Clustering"
                Types: str

            custom_data:
                Optional Argument.
                Specifies json object containing user customized input.
                Types: json object

            **kwargs:
                Specifies the additional arguments for feature engineering. Below
                are the additional arguments:
                    volatile:
                        Optional Argument.
                        Specifies whether to put the interim results of the
                        functions in a volatile table or not. When set to
                        True, results are stored in a volatile table,
                        otherwise not.
                        Default Value: False
                        Types: bool

                    persist:
                        Optional Argument.
                        Specifies whether to persist the interim results of the
                        functions in a table or not. When set to True,
                        results are persisted in a table; otherwise,
                        results are garbage collected at the end of the
                        session.
                        Default Value: False
                        Types: bool

                    cluster:
                        Optional Argument.
                        Specifies whether to apply clustering techniques.
                        Default Value: False
                        Types: bool
                    
                    progress_prefix:
                        Optional Argument.
                        Specifies the prefix for the progress bar messages.
                        Default Value: None
                        Types: str.

                    automl_phases:
                        Optional Argument.
                        Specifies the phase of AutoML to be executed.
                        Default Value: None
                        Types: str or list of str.

                    auto_dataprep:
                        Optional Argument.
                        Specifies whether to run AutoDataPrep workflow.
                        Default Value: False
                        Types: bool
        """
        # Instance variables
        self.data = data
        self.target_column = target_column
        self.model_list = model_list
        self.verbose = verbose
        self.task_type = task_type
        self.custom_data = custom_data
        self.excluded_cols=[]
        self.data_types = {key: value for key, value in self.data._column_names_and_types} 
        self.target_label = None
        
        self.one_hot_obj_count = 0
        self.is_classification_type = lambda: self.task_type.upper() == 'CLASSIFICATION'
        self.persist = kwargs.get('persist', False)
        self.volatile = kwargs.get('volatile', False) or (configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE and self.persist is False)
        self.cluster = kwargs.get('cluster', False)

        self.data_mapping = {}
        self.progress_prefix = kwargs.get('progress_prefix', None)
        self.aml_phases = kwargs.get('automl_phases', None)
        self.auto_dataprep = kwargs.get('auto_dataprep', False)

    # Method for doing feature engineering on data -> adding id, removing futile col, imputation, encoding(one hot)
    def feature_engineering(self, 
                            auto=True):
        """
        DESCRIPTION:
            Function performs following operations :-
                1. Removes futile columns/features from dataset.
                2. Detects the columns with missing values.
                3. Performs imputation on these columns with missing values.
                4. Detects categorical columns and perform encoding on those columns.
         
        PARAMETERS:   
            auto:
                Optional Argument.
                Specifies whether to run AutoML in custom mode or auto mode.
                When set to False, runs in custom mode. Otherwise, by default runs in auto mode.
                Default Value: True
                Types: boolean
                
        Returns:
             tuple, First element represents teradataml DataFrame,
             second element represents list of columns which are not participating in outlier tranformation.
        """
        # Assigning number of base jobs for progress bar.
        if self.cluster:
            base_jobs = 11 if auto else 15
        else:
            base_jobs = 12 if auto else 17
        
        # Updating model list based on distinct value of target column for classification type
        if self.is_classification_type():
            if self.data.drop_duplicate(self.target_column).size > 2:
                unsupported_models = ['svm', 'glm']  # Models that don't support multiclass
                for model in unsupported_models:
                    if model in self.model_list:
                        self._display_msg(inline_msg="\nMulti-class classification is "
                                          "not supported by {} model. Skipping {} model."
                                          .format(model, model))
                self.model_list = [model for model in self.model_list if model not in unsupported_models]
        
        # After filtering models like glm/svm due to multiclass
        if not self.auto_dataprep:
            _Validators._validate_non_empty_list_or_valid_selection(self.model_list, "List of models")

        # Updating number of jobs for progress bar based on number of models.
        jobs = base_jobs + len(self.model_list)
        self.progress_bar = _ProgressBar(jobs=jobs, 
                                         verbose=2, 
                                         prefix=self.progress_prefix) 

        self._display_heading(phase=1, 
                              progress_bar=self.progress_bar,
                              automl_phases=self.aml_phases)
        
        self._display_msg(msg='Feature Engineering started ...', 
                          progress_bar=self.progress_bar)
        
        # Storing target column to data transform dictionary
        # Setting target column for supervised learning, for clustering it will be None.
        if not self.cluster:
            self.data_transform_dict['data_target_column'] = self.target_column
        else:
            self.data_transform_dict['data_target_column'] = None
    
        # Storing target column encoding indicator to data transform dictionary
        if "target_col_encode_ind" not in self.data_transform_dict:
            self.data_transform_dict["target_col_encode_ind"] = False
        
        
        # Storing task type to data transform dictionary
        if not self.cluster:
            self.data_transform_dict['classification_type'] = self.is_classification_type()
        else:
            self.data_transform_dict['classification_type'] = False
        # Storing params for performing one hot encoding
        self.data_transform_dict['one_hot_encoding_fit_obj'] = {}
        self.data_transform_dict['one_hot_encoding_drop_list'] = []

        if auto:
            self._remove_duplicate_rows()
            self.progress_bar.update()
            
            self._remove_futile_columns()
            self.progress_bar.update()
            
            self._handle_date_columns()
            self.progress_bar.update()
            
            self._handling_missing_value()
            self.progress_bar.update()
            
            self._impute_missing_value()
            self.progress_bar.update()
            
            self._encoding_categorical_columns()
            self.progress_bar.update()
            
        else:
            self._remove_duplicate_rows()
            self.progress_bar.update()
            
            self._anti_select_columns()
            self.progress_bar.update()

            self._remove_futile_columns()
            self.progress_bar.update()

            self._handle_date_columns()
            self.progress_bar.update()
            
            self._custom_handling_missing_value()
            self.progress_bar.update()
            
            self._bin_code_transformation()
            self.progress_bar.update()
            
            self._string_manipulation()
            self.progress_bar.update()
            
            self._custom_categorical_encoding()
            self.progress_bar.update()
            
            self._mathematical_transformation()
            self.progress_bar.update()
            
            self._non_linear_transformation()
            self.progress_bar.update()
               
        return self.data, self.excluded_cols, self.target_label, self.data_transform_dict, self.data_mapping
    
    def _extract_list(self,
                      list1,
                      list2):
        """
        DESCRIPTION:
            Function to extract elements from list1 which are not present in list2.
            
        PARAMETERS:
            list1:
                Required Argument.
                Specifies the first list for extracting elements from.
                Types: list
                
            list2:
                Required Argument.
                Specifies the second list to get elements for avoiding in first list while extracting.
                Types: list
                
        RETURN:
            Returns extracted elements in form of list.
            
        """
        # Ensure list1 and list2 are lists, default to empty list if None
        if list1 is None:
            list1 = []
        if list2 is None:
            list2 = []
        new_lst = list(set(list1) - set(list2))
        return new_lst
    
    def _remove_duplicate_rows(self):
        """
        DESCRIPTION:
            Function to handles duplicate rows present in dataset.
        
        """
        self._display_msg(msg="\nHandling duplicate records present in dataset ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        start_time = time.time()
        rows = self.data.shape[0]
        self.data=self.data.drop_duplicate(self.data.columns)
        if rows != self.data.shape[0]:
            self._display_msg(msg=f'Updated dataset sample after removing {rows-self.data.shape[0]} duplicate records:',
                              data=self.data,
                              progress_bar=self.progress_bar)
            self._display_msg(inline_msg=f"Remaining Rows in the data: {self.data.shape[0]}\n"\
                                  f"Remaining Columns in the data: {self.data.shape[1]}",
                              progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Analysis completed. No action taken.",
                              progress_bar=self.progress_bar)   

        end_time = time.time()
        self._display_msg(msg="Total time to handle duplicate records: {:.2f} sec  ".format(end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)
        
    def _get_distinct_count(self):
        """
        DESCRIPTION:
            Function to get distinct count for all features and store it in dictionary for further use.
        """
        # Count of distinct value in each column
        counts = self.data.select(self.data.columns).count(distinct=True)
        
        # Dict containing disctinct value in each column
        self.counts_dict = next(counts.itertuples())._asdict()
    
    def _preprocess_data(self):
        """
        DESCRIPTION:
            Function replaces the existing id column or adds the new id column and
            removes columns with sinlge value/same values in the dataset.
        """
        # Get distinct value in each column
        self._get_distinct_count()
        
        # Columns to removed if
        # id column detected or count of distinct value = 1
        columns_to_be_removed = [col for col in self.data.columns if col.lower() == 'id' or self.counts_dict[f'count_{col}'] == 1]

        # Removing id column, if exists
        if len(columns_to_be_removed) != 0:
            self.data = self.data.drop(columns_to_be_removed, axis=1)
            # Storing irrelevant column list in data transform dictionary
            self.data_transform_dict['drop_irrelevant_columns'] = columns_to_be_removed
            
        # Adding id columns
        obj = FillRowId(data=self.data, row_id_column='id')

        self.data = obj.result
            
    def _remove_futile_columns(self):
        """
        DESCRIPTION:
            Function removes the futile columns from dataset. 
        """
        self._display_msg(msg="\nHandling less significant features from data ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        start_time = time.time()
        
        self._preprocess_data()
        
        # Handling string type target column in classification
        # Performing Ordinal Encoding 
        if not self.cluster:
            if self.data_types[self.target_column] in ['str']:
                self._ordinal_encoding([self.target_column])
    
        # Detecting categorical columns
        categorical_columns = [col for col, d_type in self.data._column_names_and_types if d_type == 'str']

        # Detecting and removing futile columns, if categorical_column exists
        if len(categorical_columns) != 0:
            
            obj = CategoricalSummary(data=self.data, 
                                     target_columns=categorical_columns,
                                     volatile=self.volatile,
                                     persist=self.persist)
            
            gfc_out = GetFutileColumns(data=self.data, 
                                       object=obj, 
                                       category_summary_column="ColumnName",
                                       threshold_value =0.7,
                                       volatile=self.volatile,
                                       persist=self.persist)
            
            # Extracting Futile columns
            f_cols = [row[0] for row in gfc_out.result.itertuples()]

            self.data_mapping['categorical_summary'] = obj.result._table_name
            self.data_mapping['futile_columns'] = gfc_out.result._table_name

            if len(f_cols) == 0:
                self._display_msg(inline_msg="Analysis indicates all categorical columns are significant. No action Needed.",
                                  progress_bar=self.progress_bar)
            else:

                self.data = self.data.drop(f_cols, axis=1)
                # Storing futile column list in data transform dictionary
                self.data_transform_dict['futile_columns'] = f_cols

                if self.persist:
                    table_name = UtilFuncs._generate_temp_table_name(table_type=TeradataConstants.TERADATA_TABLE,
                                                                     gc_on_quit=False)
                    self.data.to_sql(table_name)
                else:
                    self.data.materialize()

                self.data_mapping['data_without_futile_columns'] = self.data._table_name
                self._display_msg(msg='Removing Futile columns:',
                                  col_lst=f_cols,
                                  progress_bar=self.progress_bar)
                self._display_msg(msg='Sample of Data after removing Futile columns:',
                                  data=self.data,
                                  progress_bar=self.progress_bar)
        end_time= time.time()
        self._display_msg(msg="Total time to handle less significant features: {:.2f} sec  ".format( end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)
        
    def _fetch_date_component(self):
        """
        DESCRIPTION:
            Function to fetch day of week, week of month, month of quarter, quarter of year
            component from date column. Generate weekend and month half details from day of week and
            week of month columns respectively. Convert quarter of year and month of quarter
            component columns to VARCHAR.
        
        RETURNS:
            List of newly generated date component features.
        """
        # List for storing newly generated date component features
        new_date_components=[]
        # Extracting weekend, month, quarter details information from date columns
        date_component_param={}
        for col in self.date_column_list: 
            # Generating new column names for extracted date components
            weekend_col = f'{col}_weekend'
            month_half_col = f'{col}_month_half'
            month_of_quarter_col=f'{col}_month_of_quarter'
            quarter_of_year_col=f'{col}_quarter_of_year'
            
            date_component_param =  {
                **date_component_param,
                weekend_col: case([(self.data[col].day_of_week().isin([1, 7]), 'yes')], else_='no'),
                month_half_col: case([(self.data[col].week_of_month().isin([1, 2]), 'first_half')], else_='second_half'),
                month_of_quarter_col: self.data[col].month_of_quarter(),
                quarter_of_year_col: self.data[col].quarter_of_year()
            }
            # Storing newly generated date component month and quarter columns.
            # Skipping day of week and week of month columns as they will be used 
            # later for extracting weekend and month part details.
            new_date_components.extend([weekend_col, month_half_col, month_of_quarter_col, quarter_of_year_col])
        # Adding new date component columns to dataset
        self.data=self.data.assign(**date_component_param)
        # Dropping date columns as different component columns are extracted.     
        self.data = self.data.drop(self.date_column_list, axis=1)
        
        # Converting remaining component columns to VARCHAR 
        # So that it will be treated as categorical columns
        remaining_component_columns = [col for col in self.data.columns if re.search('month_of_quarter|quarter_of_year'+"$", col)]
        accumulate_columns = self._extract_list(self.data.columns, remaining_component_columns)
        convertto_params = {
                            "data" : self.data,
                            "target_columns" : remaining_component_columns,
                            "target_datatype" : ["VARCHAR(charlen=20,charset=UNICODE,casespecific=NO)"],
                            "accumulate" : accumulate_columns,
                            "persist" : True
                            }
        # Disabling display table name if persist is True by default
        if not self.volatile and not self.persist:
            convertto_params["display_table_name"] = False
            
        # Setting persist to False if volatile is True
        if self.volatile:
            convertto_params["persist"] = False
            convertto_params["volatile"] = True

        # returning dataset after performing string manipulation                 
        self.data = ConvertTo(**convertto_params).result

        # IF volatile is False and persist is False
        if not self.volatile and not self.persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(self.data._table_name)
        return new_date_components
  
    def _handle_date_columns_helper(self):
        
        """
        DESCRIPTION:
            Function for dropping irrelevent date features. Perform Extraction of different
            component from revelent date features and transform them.
        """
        
        # Dropping missing value for all date columns
        self._display_msg(msg="\nDropping missing values for:",
                          col_lst=self.date_column_list,
                          progress_bar=self.progress_bar)

        self.data = self.data.dropna(subset=self.date_column_list)
     
        # Date columns list eligible for dropping from dataset
        drop_date_cols = []     
        
        # Checking for unique valued date columns
        for col in self.date_column_list:
            if self.data.drop_duplicate(col).size == self.data.shape[0]:
                drop_date_cols.append(col)
                
        if len(drop_date_cols) != 0:
            self.data = self.data.drop(drop_date_cols, axis=1)
            # Storing unique date column list in data transform dictionary
            self.data_transform_dict['drop_unique_date_columns'] = drop_date_cols
            self._display_msg(msg='Dropping date features with all unique value:',
                              col_lst = drop_date_cols,
                              progress_bar=self.progress_bar)
            # Updated date column list after dropping irrelevant date columns
            self.date_column_list = [item for item in self.date_column_list if item not in drop_date_cols]
        
        if len(self.date_column_list) != 0:
            
            # List for storing newly generated date component features
            new_columns=self._fetch_date_component()
            self._display_msg(msg='List of newly generated features from existing date features:',
                              col_lst=new_columns,
                              progress_bar=self.progress_bar)
            # Dropping columns with all unique values or single value
            drop_cols=[]
            for col in new_columns:
                distinct_rows = self.data.drop_duplicate(col).size
                if  distinct_rows == self.data.shape[0]:
                    drop_cols.append(col)
                    self._display_msg(msg='Dropping features with all unique values:',
                                      col_lst=col,
                                      progress_bar=self.progress_bar)
                    
                elif distinct_rows == 1:
                    drop_cols.append(col)
                    self._display_msg(msg='Dropping features with single value:',
                                      col_lst=col,
                                      progress_bar=self.progress_bar)

            # Dropping columns from drop_cols list
            if len(drop_cols) != 0:
                self.data = self.data.drop(drop_cols, axis=1)
                # Storing extract date component list for drop in data transform dictionary
                self.data_transform_dict['drop_extract_date_columns'] = drop_cols        
                # Extracting all newly generated columns    
                new_columns = [item for item in new_columns if item not in drop_cols]
            
                self._display_msg(msg='Updated list of newly generated features from existing date features :',
                                  col_lst=new_columns,
                                  progress_bar=self.progress_bar)
            
            self._display_msg(msg='Updated dataset sample after handling date features:',
                              data=self.data,
                              progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="No useful date feature found",
                              progress_bar=self.progress_bar)
             
    def _handle_date_columns(self):
        
        """
        DESCRIPTION:
            Function to handle date columns in dataset if any. 
            Perform relevent transformation by extracting different components, i.e., Day , Month and Year.
        """
        self._display_msg(msg="\nHandling Date Features ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        start_time = time.time()
        
        self.date_column_list = [col for col, d_type in self.data._column_names_and_types \
                               if d_type in ["datetime.date","datetime.datetime"]]
                 
        if len(self.date_column_list) == 0:
            self._display_msg(inline_msg="Analysis Completed. Dataset does not contain any feature related to dates. No action needed.",
                              progress_bar=self.progress_bar)
        else:
            # Storing date column list in data transform dictionary
            self.data_transform_dict['date_columns'] = self.date_column_list
            self._handle_date_columns_helper()
            if self.persist:
                table_name = UtilFuncs._generate_temp_table_name(table_type=TeradataConstants.TERADATA_TABLE,
                                                                 gc_on_quit=False)
                self.data.to_sql(table_name)
            else:
                self.data.materialize()
            self.data_mapping['data_after_date_handling'] = self.data._table_name
        
        end_time = time.time()
        self._display_msg(msg="Total time to handle date features: {:.2f} sec\n".format(end_time-start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)         

    def _missing_count_per_column(self):
        """
        DESCRIPTION:
            Function finds and returns a dictnoary containing list of columns
            with missing values.
         
        Returns:
            dict, keys represent column names and
            values represent the missing value count for corresponding column.
        """
        
        # Removing rows with missing target column value
        if not self.cluster:
            self.data = self.data.dropna(subset=[self.target_column])

        params = {
            "data": self.data,
            "target_columns": self.data.columns,
            "persist": True,
            "display_table_name": False
        }
        
        obj = ColumnSummary(**params)

        # Adding transformed data containing table to garbage collector
        GarbageCollector._add_to_garbagecollector(obj.result._table_name)
        
        cols_miss_val={}
        # Iterating over each row in the column summary result
        for row in obj.result.itertuples():
            # Checking if the third element of the row (missing values count) is greater than 0
            if row[3] > 0:
                # If so, add an entry to the 'cols_miss_val' dictionary
                # Key: column name (first element of the row)
                # Value: count of missing values in the column (third element of the row)
                cols_miss_val[row[0]] = row[3]
        
        return cols_miss_val
 
    def _handling_missing_value(self):
        """
        DESCRIPTION:
            Function detects the missing values in the each feature of dataset,
            then performs these operation based on condition :-
                1. deleting rows from columns/feature
                2. dropping columns from dataset  
        """
        self._display_msg(msg="\nChecking Missing values in dataset ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        start_time = time.time()
        
        # Flag for missing values
        msg_val_found=0
        
        #num of rows
        d_size = self.data.shape[0]

        delete_rows = []
        drop_cols = []
        self.imputation_cols = {}

        cols_miss_val = self._missing_count_per_column()

        if len(cols_miss_val) != 0:
            self._display_msg(msg="Columns with their missing values:",
                              col_lst=cols_miss_val,
                              progress_bar=self.progress_bar)
        
        # Get distinct value in each column
        self._get_distinct_count()
        
        # Iterating over columns with missing values
        for col,val in  cols_miss_val.items():
            
            # Drop col, if count of missing value > 60%
            if val > .6*d_size:
                drop_cols.append(col)
                continue
            
            # For clustering tasks, all columns with missing values are sent directly to imputation
            if self.cluster:
                self.imputation_cols[col] = val
                continue

            if self.data_types[col] in ['float', 'int']:
                corr_df = self.data[col].corr(self.data[self.target_column])
                corr_val = self.data.assign(True, corr_=corr_df)
                related = next(corr_val.itertuples())[0]
                
                # Delete row, if count of missing value < 2% and 
                # Relation b/w target column and numeric column <= .25
                if val < .02*d_size and related <= .25:
                    delete_rows.append(col)
                    continue

            elif self.data_types[col] in ['str']:
                # Delete row, if count of missing value < 4%
                if val < .04*d_size:
                    delete_rows.append(col)
                    continue
                # Drop col, if unique count of column > 75%
                elif self.counts_dict[f'count_{col}'] > .75*(d_size-val):
                    drop_cols.append(col)
                    continue
                    
            # Remaining column for imputation
            self.imputation_cols[col] = val
            # Storing columns with missing value for imputation in data transform dictionary
            self.data_transform_dict['imputation_columns'] = self.imputation_cols

        if len(delete_rows) != 0:
            rows = self.data.shape[0]
            self.data = self.data.dropna(subset=delete_rows)
            msg_val_found=1
            self._display_msg(msg='Deleting rows of these columns for handling missing values:',
                              col_lst=delete_rows,
                              progress_bar=self.progress_bar)
            self._display_msg(msg=f'Sample of dataset after removing {rows-self.data.shape[0]} rows:',
                              data=self.data,
                              progress_bar=self.progress_bar)
            
        if len(drop_cols) != 0:
            self.data = self.data.drop(drop_cols, axis=1)
            msg_val_found=1
            # Storing columns with missing value for drop in data transform dictionary
            self.data_transform_dict['drop_missing_columns'] = drop_cols
            self._display_msg(msg='Dropping these columns for handling missing values:',
                              col_lst=drop_cols,
                              progress_bar=self.progress_bar)
            self._display_msg(msg=f'Sample of dataset after removing {len(drop_cols)} columns:',
                              data=self.data,
                              progress_bar=self.progress_bar)
        
        if len(self.imputation_cols) == 0 and msg_val_found ==0:
            self._display_msg(inline_msg="Analysis Completed. No Missing Values Detected.",
                              progress_bar=self.progress_bar)
            
        end_time = time.time()
        self._display_msg(msg="Total time to find missing values in data: {:.2f} sec  ".format( end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)

    def _impute_helper(self):
        """
        DESCRIPTION:
            Function decides the imputation methods [mean/ median/ mode] for columns with missing values
            on the basis of skewness of column in the dataset.
        
        RETURNS:
            A tuple containing,
            col_stat (name of columns with missing value)
            stat (imputation method for respective columns)
        """
        col_stat = []
        stat = []
        
        # Converting o/p of skew() into dictonary with key as column name and value as skewness value
        df = self.data.skew()
        skew_data = next(df.itertuples())._asdict()
        
        # Iterating over columns with missing value
        for key, val in self.imputation_cols.items():
            
            col_stat.append(key)
            if self.data_types[key] in ['float', 'int', 'decimal.Decimal']:
                val = skew_data[f'skew_{key}']
                # Median imputation method, if abs(skewness value) > 1
                if abs(val) > 1:
                    stat.append('median')
                # Mean imputation method, if abs(skewness value) <= 1
                else:
                    stat.append('mean')     
            # Mode imputation method, if categorical column
            elif self.data_types[key] in ['str']:
                stat.append('mode')
        
        self._display_msg(msg="Columns with their imputation method:",
                          col_lst=dict(zip(col_stat, stat)),
                          progress_bar=self.progress_bar)
        
        return col_stat, stat

    def _impute_missing_value(self):
        """
        DESCRIPTION:
            Function performs the imputation on columns/features with missing values in the dataset.
        """
        
        start_time = time.time()
        self._display_msg(msg="\nImputing Missing Values ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        
        if len(self.imputation_cols) != 0:
            
            # List of columns and imputation Method
            col_stat, stat = self._impute_helper()
            
            fit_obj = SimpleImputeFit(data=self.data, 
                                      stats_columns=col_stat, 
                                      stats=stat,
                                      volatile=self.volatile,
                                      persist=self.persist)
            
            # Storing fit object for imputation in data transform dictionary
            self.data_transform_dict['imputation_fit_object'] = fit_obj.output
            sm = SimpleImputeTransform(data=self.data, 
                                       object=fit_obj,
                                       volatile=self.volatile,
                                       persist=self.persist)
            
            self.data = sm.result
            self.data_mapping['fit_simpleimpute_output'] = fit_obj.output_data._table_name 
            self.data_mapping['fit_simpleimpute_result'] = fit_obj.output._table_name
            self.data_mapping['data_without_missing_values'] = self.data._table_name
            self._display_msg(msg="Sample of dataset after Imputation:",
                              data=self.data,
                              progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Analysis completed. No imputation required.",
                              progress_bar=self.progress_bar)
              
        end_time = time.time()
        self._display_msg(msg="Time taken to perform imputation: {:.2f} sec  ".format(end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)
   
    def _custom_handling_missing_value(self):
        """
        DESCRIPTION:
            Function to perform customized missing value handling for features based on user input.
            
        """
        # Fetching user input for performing missing value handling
        missing_handling_input = self.custom_data.get("MissingValueHandlingIndicator", False)
        
        if missing_handling_input:
            # Fetching parameters required for performing
            missing_handling_param = self.custom_data.get("MissingValueHandlingParam", None)
            if missing_handling_param:
                # Fetching user input for different methods missing value handling
                drop_col_ind = missing_handling_param.get("DroppingColumnIndicator", False)
                drop_row_ind = missing_handling_param.get("DroppingRowIndicator", False)
                impute_ind = missing_handling_param.get("ImputeMissingIndicator", False)
                volatile = missing_handling_param.pop("volatile", False)
                persist = missing_handling_param.pop("persist", False)
                # Checking for user input if all methods indicator are false or not
                if not any([drop_col_ind, drop_row_ind, impute_ind]):  
                    self._display_msg(inline_msg="No method information provided for performing customized missing value handling. \
                        AutoML will proceed with default missing value handling method.",
                                      progress_bar=self.progress_bar)
                    
                else:
                    # Checking user input for dropping missing value columns
                    if drop_col_ind:
                        drop_col_list = missing_handling_param.get("DroppingColumnList", [])
                        # Storing customcolumns with missing value for drop in data transform dictionary
                        self.data_transform_dict["custom_drop_missing_columns"] = drop_col_list
                        if len(drop_col_list):
                            # Checking for column present in dataset or not
                            _Validators._validate_dataframe_has_argument_columns(drop_col_list, "DroppingColumnList", self.data, "df")

                            self._display_msg(msg="\nDropping these columns for handling customized missing value:",
                                              col_lst=drop_col_list,
                                              progress_bar=self.progress_bar)
                            self.data = self.data.drop(drop_col_list, axis=1)
                        else:
                            self._display_msg(inline_msg="No information provided for dropping missing value containing columns.",
                                              progress_bar=self.progress_bar)

                    # Checking user input for dropping missing value rows    
                    if drop_row_ind:
                        drop_row_list = missing_handling_param.get("DroppingRowList", [])
                        if len(drop_row_list):
                            # Checking for column present in dataset or not
                            _Validators._validate_dataframe_has_argument_columns(drop_row_list, "DroppingRowList", self.data, "df")

                            self._display_msg(msg="Dropping missing rows in these columns for handling customized missing value:",
                                              col_lst=drop_row_list,
                                              progress_bar=self.progress_bar)
                            self.data = self.data.dropna(subset = drop_row_list)
                        else:
                            self._display_msg(inline_msg="No information provided for dropping missing value containing rows.",
                                              progress_bar=self.progress_bar)
                    # Checking user input for missing value imputation 
                    if impute_ind:
                        stat_list = missing_handling_param.get("StatImputeList", None)
                        stat_method = missing_handling_param.get("StatImputeMethod", None)
                        literal_list = missing_handling_param.get("LiteralImputeList", None)
                        literal_value = missing_handling_param.get("LiteralImputeValue", None)

                        # Checking for column present in dataset or not
                        _Validators._validate_dataframe_has_argument_columns(stat_list, "StatImputeList", self.data, "df")

                        _Validators._validate_dataframe_has_argument_columns(literal_list, "LiteralImputeList", self.data, "df")
                        
                        # Creating fit params    
                        fit_param = {
                            "data" : self.data,
                            "stats_columns" : stat_list,
                            "stats" : stat_method,
                            "literals_columns" : literal_list,
                            "literals" : literal_value,
                            "volatile" : volatile,
                            "persist" : persist
                        }
                        # Fitting on dataset
                        fit_obj = SimpleImputeFit(**fit_param)
                        # Storing custom fit object for imputation in data transform dictionary
                        self.data_transform_dict["custom_imputation_ind"] = True
                        self.data_transform_dict["custom_imputation_fit_object"] = fit_obj.output
                        # Creating transform params
                        transform_param = {
                            "data" : self.data,
                            "object" : fit_obj.output,
                            "persist" : True
                        }
                        # Disabling display table name if persist is True by default
                        if not volatile and not persist:
                            transform_param["display_table_name"] = False

                        if volatile:
                            transform_param["volatile"] = True
                            transform_param["persist"] = False
                        # Updating dataset with transform result
                        self.data = SimpleImputeTransform(**transform_param).result

                        self.data_mapping['fit_simpleimpute_output'] = fit_obj.output_data._table_name 
                        self.data_mapping['fit_simpleimpute_result'] = fit_obj.output._table_name
                        self.data_mapping['data_without_missing_values'] = self.data._table_name

                        if not volatile and not persist:
                            # Adding transformed data containing table to garbage collector
                            GarbageCollector._add_to_garbagecollector(self.data._table_name)                 
                        self._display_msg(msg="Updated dataset sample after performing customized missing value imputation:",
                                          data=self.data,
                                          progress_bar=self.progress_bar)
            else:
                self._display_msg(inline_msg="No information provided for performing customized missing value handling. \
                        AutoML will proceed with default missing value handling method.",
                                  progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Proceeding with default option for missing value imputation.",
                              progress_bar=self.progress_bar)
            
        # Proceeding with default method for handling remaining missing values
        self._display_msg(inline_msg="Proceeding with default option for handling remaining missing values.",
                          progress_bar=self.progress_bar)
        self._handling_missing_value()
        self._impute_missing_value()   

    def _bin_code_transformation(self):
        """
        DESCRIPTION:
            Function to perform customized binning on features based on user input.
            
        """
        # Fetching user input for performing bin code transformation.
        bin_code_input = self.custom_data.get("BincodeIndicator", False)
         
        if bin_code_input:
            # Storing custom bin code transformation indicator in data transform dictionary
            self.data_transform_dict['custom_bincode_ind'] = True
            # Fetching list required for performing transfomation.
            extracted_col = self.custom_data.get("BincodeParam", None)
            if not extracted_col:
                self._display_msg(inline_msg="BincodeParam is empty. Skipping customized bincode transformation.",
                                  progress_bar=self.progress_bar)
            else:
                # Creating list for storing column and binning informartion for performing transformation 
                equal_width_bin_list  = []
                equal_width_bin_columns  = []
                var_width_bin_list = []
                var_width_bin_columns  = []
                volatile = extracted_col.pop("volatile", False)
                persist = extracted_col.pop("persist", False)

                # Checking for column present in dataset or not
                _Validators._validate_dataframe_has_argument_columns(list(extracted_col.keys()), "BincodeParam", self.data, "df")
                
                for col,transform_val in extracted_col.items():
                    # Fetching type of binning to be performed 
                    bin_trans_type = transform_val["Type"]
                    # Fetching number of bins to be created
                    num_bin = transform_val["NumOfBins"]
                    # Checking for bin types and adding details into lists for binning
                    if bin_trans_type == "Equal-Width":
                        bins = num_bin
                        equal_width_bin_list.append(bins)
                        equal_width_bin_columns.append(col)
                    elif bin_trans_type == "Variable-Width":
                        var_width_bin_columns.append(col)
                        bins = num_bin
                        for i in range(1, bins+1):
                            # Forming binning name as per expected input
                            temp="Bin_"+str(i)
                            # Fetching required details for variable type binning
                            minval = transform_val[temp]["min_value"]
                            maxval = transform_val[temp]["max_value"]
                            label = transform_val[temp]["label"]
                            # Appending information of each bin             
                            var_width_bin_list.append({ "ColumnName":col, "MinValue":minval, "MaxValue":maxval, "Label":label})
                # Checking column list for performing binning with Equal-Width.
                if len(equal_width_bin_columns) != 0:
                    # Adding fit parameter for performing binning with Equal-Width.
                    fit_params={
                        "data" : self.data,
                        "target_columns": equal_width_bin_columns,
                        "method_type" : "Equal-Width",
                        "nbins" : bins,
                        "volatile" : volatile,
                        "persist" : persist
                    }
                    eql_bin_code_fit = BincodeFit(**fit_params)
                    # Storing fit object and column list for Equal-Width binning in data transform dictionary
                    self.data_transform_dict['custom_eql_bincode_col'] = equal_width_bin_columns
                    self.data_transform_dict['custom_eql_bincode_fit_object'] = eql_bin_code_fit.output
                    # Extracting accumulate columns
                    accumulate_columns = self._extract_list(self.data.columns, equal_width_bin_columns)
                    # Adding transform parameters for performing binning with Equal-Width.
                    eql_transform_params = {
                        "data" : self.data,
                        "object" : eql_bin_code_fit.output,
                        "accumulate" : accumulate_columns,
                        "persist" : True
                    }
                    # Disabling display table name if persist is True by default
                    if not volatile and not persist:
                        eql_transform_params["display_table_name"] = False
                        
                    if volatile:
                        eql_transform_params["volatile"] = True
                        eql_transform_params["persist"] = False
                    self.data = BincodeTransform(**eql_transform_params).result
                    if not volatile and not persist:
                        # Adding transformed data containing table to garbage collector
                        GarbageCollector._add_to_garbagecollector(self.data._table_name)

                    self.data_mapping['fit_eql_width'] = eql_bin_code_fit.output._table_name
                    self.data_mapping['eql_width_bincoded_data'] = self.data._table_name

                    self._display_msg(msg="\nUpdated dataset sample after performing Equal-Width binning :-",
                                      data=self.data,
                                      progress_bar=self.progress_bar)
                else:
                    self._display_msg(inline_msg="No information provided for Equal-Width Transformation.",
                                      progress_bar=self.progress_bar)
                    
                if len(var_width_bin_columns) != 0:
                    # Creating pandas dataframe and then teradata dataframe for storing binning information
                    var_bin_table = pd.DataFrame(var_width_bin_list, columns=["ColumnName", "MinValue", "MaxValue", "Label"])
                    self._display_msg(msg="Variable-Width binning information:-",
                                      data=var_bin_table,
                                      progress_bar=self.progress_bar)
                    copy_to_sql(df=var_bin_table, table_name="automl_bincode_var_fit", temporary=True)
                    var_fit_input = DataFrame.from_table("automl_bincode_var_fit")
                    fit_params = {
                        "data" : self.data,
                        "fit_data": var_fit_input,
                        "fit_data_order_column" : ["MinValue", "MaxValue"],
                        "target_columns": var_width_bin_columns,
                        "minvalue_column" : "MinValue",
                        "maxvalue_column" : "MaxValue",
                        "label_column" : "Label",
                        "method_type" : "Variable-Width",
                        "label_prefix" : "label_prefix",
                        "volatile" : volatile,
                        "persist" : persist
                    }
                    var_bin_code_fit = BincodeFit(**fit_params)
                    # Storing fit object and column list for Variable-Width binning in data transform dictionary
                    self.data_transform_dict['custom_var_bincode_col'] = var_width_bin_columns
                    self.data_transform_dict['custom_var_bincode_fit_object'] = var_bin_code_fit.output
                    accumulate_columns = self._extract_list(self.data.columns, var_width_bin_columns)
                    var_transform_params = {
                        "data" : self.data,
                        "object" : var_bin_code_fit.output,
                        "object_order_column" : "TD_MinValue_BINFIT",
                        "accumulate" : accumulate_columns,
                        "persist" : True
                    }
                    # Disabling display table name if persist is True by default
                    if not volatile and not persist:
                        var_transform_params["display_table_name"] = False
                    
                    if volatile:
                        var_transform_params["volatile"] = True
                        var_transform_params["persist"] = False
                    self.data = BincodeTransform(**var_transform_params).result
                    self.data_mapping['fit_var_width'] = var_bin_code_fit.output._table_name
                    self.data_mapping['var_width_bincoded_data'] = self.data._table_name
                    if not volatile and not persist:
                        # Adding transformed data containing table to garbage collector
                        GarbageCollector._add_to_garbagecollector(self.data._table_name)
                    self._display_msg(msg="Updated dataset sample after performing Variable-Width binning:",
                                      data=self.data,
                                      progress_bar=self.progress_bar)
                else:
                    self._display_msg(inline_msg="No information provided for Variable-Width Transformation.",
                                      progress_bar=self.progress_bar)            
        else:
            self._display_msg(inline_msg="No information provided for Variable-Width Transformation.",
                              progress_bar=self.progress_bar)

    def _string_manipulation(self):
        """
        DESCRIPTION:
            Function to perform customized string manipulations on categorical features based on user input.
                    
        """
        # Fetching user input for performing string manipulation.
        str_mnpl_input = self.custom_data.get("StringManipulationIndicator", False)
        # Checking user input for string manipulation on categrical features.
        if str_mnpl_input:
            # Storing custom string manipulation indicator in data transform dictionary
            self.data_transform_dict['custom_string_manipulation_ind'] = True
            # Fetching list required for performing operation.
            extracted_col = self.custom_data.get("StringManipulationParam", None).copy()
            if not extracted_col:
                self._display_msg(inline_msg="No information provided for performing string manipulation.",
                                  progress_bar=self.progress_bar)
            else:
                volatile = extracted_col.pop("volatile", False)
                persist = extracted_col.pop("persist", False)
                # Checking for column present in dataset or not
                _Validators._validate_dataframe_has_argument_columns(list(extracted_col.keys()), "StringManipulationParam", self.data, "df")

                for target_col,transform_val in extracted_col.items():                
                    self.data = self._str_method_mapping(target_col, transform_val)
                # Storing custom string manipulation parameters in data transform dictionary
                self.data_transform_dict['custom_string_manipulation_param'] = extracted_col
                
                self._display_msg(msg="Updated dataset sample after performing string manipulation:",
                                  data=self.data,
                                  progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Skipping customized string manipulation.",
                              progress_bar=self.progress_bar)
 
    def _str_method_mapping(self,
                            target_col,
                            transform_val):
        """
        DESCRIPTION:
            Function to map customized parameters according to passed method and 
            performs string manipulation on categorical features.
            
        PARAMETERS:
            target_col:
                Required Argument.
                Specifies feature for applying string manipulation.
                Types: str
                
            transform_val:
                Required Argument.
                Specifies different parameter require for applying string manipulation.
                Types: dict
        
        RETURNS:
                Dataframe containing transformed data after applying string manipulation.
        
        """
        # Creating list of features for accumulating while performing string manipulation on certain features
        accumulate_columns = self._extract_list(self.data.columns, [target_col])
        
        # Fetching required parameters from json object
        string_operation = transform_val["StringOperation"]

        # Setting volatile and persist parameters for performing string manipulation
        volatile, persist = self._get_generic_parameters(func_indicator="StringManipulationIndicator",
                                                         param_name="StringManipulationParam")

        # Storing general parameters for performing string transformation
        fit_params = {
            "data" : self.data,
            "target_columns" : target_col,
            "string_operation" : string_operation,
            "accumulate" : accumulate_columns,
            "inplace" : True,
            "persist" : True
        }
        # Disabling display table name if persist is True by default
        if not volatile and not persist:
            fit_params["display_table_name"] = False

        if volatile:
            fit_params["volatile"] = True
            fit_params["persist"] = False

        # Adding additional parameters based on string operation type           
        if string_operation in ["StringCon", "StringTrim"]:
            string_argument = transform_val["String"] 
            fit_params = {**fit_params, 
                          "string" : string_argument}
        elif string_operation == "StringPad":
            string_argument = transform_val["String"]
            string_length = transform_val["StringLength"]
            fit_params = {**fit_params, 
                          "string" : string_argument, 
                          "string_length" : string_length}       
        elif string_operation == "Substring":
            string_index = transform_val["StartIndex"]
            string_length = transform_val["StringLength"]
            fit_params = {**fit_params, 
                          "start_index" : string_index,
                          "string_length" : string_length}
        
        # returning dataset after performing string manipulation                 
        transform_output = StrApply(**fit_params).result
        if not volatile and not persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(transform_output._table_name)
        self.data_mapping['string_manipulated_data'] = transform_output._table_name
        return transform_output
              
    def _one_hot_encoding(self, 
                          one_hot_columns, 
                          unique_counts):
        """
        DESCRIPTION:
            Function performs the one hot encoding to categorcial columns/features in the dataset.
         
        PARAMETERS:
            one_hot_columns: 
                  Required Argument.
                  Specifies the categorical columns for which one hot encoding will be performed.
                  Types: str or list of strings (str)
            
            unique_counts:
                  Required Argument.
                  Specifies the unique counts in the categorical columns.
                  Types: int or list of integer (int)     
        """
        # TD function will add extra column_other in onehotEncoding, so 
        # initailizing this list to remove those extra columns 
        drop_lst = [ele + "_other" for ele in one_hot_columns]

        # Setting volatile and persist parameters for performing encoding
        volatile, persist = self._get_generic_parameters(func_indicator="CategoricalEncodingIndicator",
                                                         param_name="CategoricalEncodingParam")

        # Adding fit parameters for performing encoding
        fit_params = {
            "data" : self.data,
            "approach" : "auto",
            "is_input_dense" : True,
            "target_column" : one_hot_columns,
            "category_counts" : unique_counts,
            "other_column" : "other",
            "volatile" : volatile,
            "persist" : persist
        }
        # Performing one hot encoding fit on target columns
        fit_obj = OneHotEncodingFit(**fit_params)
        # Storing indicator, fit object and column drop list for one hot encoding in data transform dictionary
        self.data_transform_dict['one_hot_encoding_ind'] = True
        self.data_transform_dict['one_hot_encoding_fit_obj'].update({self.one_hot_obj_count : fit_obj.result})
        self.data_transform_dict['one_hot_encoding_drop_list'].extend(drop_lst)
        self.one_hot_obj_count = self.one_hot_obj_count + 1
        # Adding transform parameters for performing encoding
        transform_params = {
            "data" : self.data, 
            "object" : fit_obj.result, 
            "is_input_dense" : True,
            "persist" : True
        }
        # Disabling display table name if persist is True by default
        if not volatile and not persist:
            transform_params["display_table_name"] = False
        
        # Setting persist to False if volatile is True
        if volatile:
            transform_params["volatile"] = True
            transform_params["persist"] = False
        
        # Performing one hot encoding transformation
        transform_output = OneHotEncodingTransform(**transform_params).result

        if not volatile and not persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(transform_output._table_name)
        self.data = transform_output.drop(drop_lst, axis=1)
        self.data.materialize()
        self.data_mapping['one_hot_encoded_data'] = transform_output._table_name
        self.data_mapping['fit_ohe_result'] = fit_obj.result._table_name

    def _ordinal_encoding(self,
                          ordinal_columns):
        """
        DESCRIPTION:
            Function performs the ordinal encoding to categorcial columns or features in the dataset.
         
        PARAMETERS:
            ordinal_columns: 
                Required Argument.
                Specifies the categorical columns for which ordinal encoding will be performed.
                Types: str or list of strings (str)
        """
        # Setting volatile and persist parameters for performing encoding
        volatile, persist = self._get_generic_parameters(func_indicator="CategoricalEncodingIndicator",
                                                         param_name="CategoricalEncodingParam")

        # Adding fit parameters for performing encoding
        fit_params = {
            "data" : self.data,
            "target_column" : ordinal_columns,
            "volatile" : volatile,
            "persist" : persist
        }
        # Performing ordinal encoding fit on target columns
        ord_fit_obj = OrdinalEncodingFit(**fit_params)
        # Storing fit object and column list for ordinal encoding in data transform dictionary
        if ordinal_columns[0] != self.target_column:
            self.data_transform_dict["custom_ord_encoding_fit_obj"] = ord_fit_obj.result
            self.data_transform_dict['custom_ord_encoding_col'] = ordinal_columns
        else:
            self.data_transform_dict['target_col_encode_ind'] = True
            self.data_transform_dict['target_col_ord_encoding_fit_obj'] = ord_fit_obj.result
        # Extracting accumulate columns
        accumulate_columns = self._extract_list(self.data.columns, ordinal_columns)
        # Adding transform parameters for performing encoding
        transform_params = {
            "data" : self.data,
            "object" : ord_fit_obj.result,
            "accumulate" : accumulate_columns,
            "persist" : True
        }
        # Disabling display table name if persist is True by default
        if not volatile and not persist:
            transform_params["display_table_name"] = False

        # Setting persist to False if volatile is True
        if volatile:
            transform_params["volatile"] = True
            transform_params["persist"] = False
        # Performing ordinal encoding transformation
        self.data = OrdinalEncodingTransform(**transform_params).result

        if not volatile and not persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(self.data._table_name)
        
        self.data_mapping['fit_ordinal_output'] = ord_fit_obj.output_data._table_name
        self.data_mapping['fit_ordinal_result'] = ord_fit_obj.result._table_name
        self.data_mapping['ordinal_encoded_data'] = self.data._table_name

        if len(ordinal_columns) == 1 and ordinal_columns[0] == self.target_column:
            self.target_label = ord_fit_obj
        
    def _target_encoding(self,
                         target_encoding_list):
        """
        DESCRIPTION:
            Function performs the target encoding to categorcial columns/features in the dataset.
         
        PARAMETERS:
            target_encoding_list: 
                  Required Argument.
                  Specifies the categorical columns for which target encoding will be performed.
                  Types: str or list of strings (str)
        """
        # Fetching all columns on which target encoding will be performed.
        target_columns = list(target_encoding_list.keys())
        # Checking for column present in dataset or not
        _Validators._validate_dataframe_has_argument_columns(target_columns, "TargetEncodingList", self.data, "df")
        # Finding distinct values and counts for columns.
        cat_sum = CategoricalSummary(data=self.data,
                                    target_columns=target_columns)
        category_data = cat_sum.result.groupby("ColumnName").count()
        category_data = category_data.assign(drop_columns=True,
                                            ColumnName=category_data.ColumnName,
                                            CategoryCount=category_data.count_DistinctValue)
        # Storing indicator and fit object for target encoding in data transform dictionary
        self.data_transform_dict["custom_target_encoding_ind"] = True
        self.data_transform_dict["custom_target_encoding_fit_obj"] = {}

        # Setting volatile and persist parameters for performing encoding
        volatile, persist = self._get_generic_parameters(func_indicator="CategoricalEncodingIndicator",
                                                         param_name="CategoricalEncodingParam")
        
        # Fetching required argument for performing target encoding
        for col,transform_val in target_encoding_list.items():
            encoder_method = transform_val["encoder_method"]
            response_column = transform_val["response_column"]
            # Adding fit parameters for performing encoding
            fit_params = {
                "data" : self.data,
                "category_data" : category_data,
                "encoder_method" : encoder_method,
                "target_columns" : col,
                "response_column" : response_column,
                "default_values": -1,
                "volatile" : volatile,
                "persist" : persist
                }
            if encoder_method == "CBM_DIRICHLET":
                num_distinct_responses=transform_val["num_distinct_responses"]
                fit_params = {**fit_params, 
                            "num_distinct_responses" : num_distinct_responses}
            # Performing target encoding fit on target columns
            tar_fit_obj = TargetEncodingFit(**fit_params)
            # Storing each column fit object for target encoding in data transform dictionary
            self.data_transform_dict["custom_target_encoding_fit_obj"].update({col : tar_fit_obj.result})
            # Extracting accumulate columns
            accumulate_columns = self._extract_list(self.data.columns, [col])
            # Adding transform parameters for performing encoding
            transform_params = {
                "data" : self.data,
                "object" : tar_fit_obj,
                "accumulate" : accumulate_columns,
                "persist" : True  
            }
            
            # Disabling display table name if persist is True by default
            if not volatile and not persist:
                transform_params["display_table_name"] = False
            
            if volatile:
                transform_params["volatile"] = True
                transform_params["persist"] = False
            # Performing ordinal encoding transformation
            self.data = TargetEncodingTransform(**transform_params).result
            if not volatile and not persist:
                # Adding transformed data containing table to garbage collector
                GarbageCollector._add_to_garbagecollector(self.data._table_name)
            self.data_mapping[f'fit_{col}_target_output'] = tar_fit_obj.output_data._table_name
            self.data_mapping[f'fit_{col}_target_result'] = tar_fit_obj.result._table_name
            self.data_mapping[f'{col}_target_encoded_data'] = self.data._table_name
    
    def _encoding_categorical_columns(self):
        """
        DESCRIPTION:
            Function detects the categorical columns and performs encoding on categorical columns in the dataset.
        """
        self._display_msg(msg="\nPerforming encoding for categorical columns ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        start_time = time.time()
        
        ohe_col = []
        unique_count = []

        # List of columns before one hot
        col_bf_ohe = self.data.columns
        
        # Get distinct value in each column
        self._get_distinct_count()
        
        # Detecting categorical columns with thier unique counts
        for col, d_type in self.data._column_names_and_types:
            if d_type in ['str']:
                ohe_col.append(col)
                unique_count.append(self.counts_dict[f'count_{col}'])

        if len(ohe_col) != 0:
            self._one_hot_encoding(ohe_col, unique_count)

            self._display_msg(msg="ONE HOT Encoding these Columns:",
                              col_lst=ohe_col,
                              progress_bar=self.progress_bar)
            self._display_msg(msg="Sample of dataset after performing one hot encoding:",
                              data=self.data,
                              progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Analysis completed. No categorical columns were found.",
                              progress_bar=self.progress_bar)
        
        # List of columns after one hot
        col_af_ohe = self.data.columns
        
        # List of excluded columns from outlier processing and scaling
        self.excluded_cols= self._extract_list(col_af_ohe, col_bf_ohe)
        
        end_time = time.time()
        self._display_msg(msg="Time taken to encode the columns: {:.2f} sec".format( end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)

    def _custom_categorical_encoding(self):
        """
        DESCRIPTION:
            Function to perform specific encoding on the categorical columns based on user input.
            if validation fails, default encoding is getting performed on all remaining categorical columns.
        """
        self._display_msg(msg="\nStarting Customized Categorical Feature Encoding ...",
                          progress_bar=self.progress_bar)
        cat_end_input = self.custom_data.get("CategoricalEncodingIndicator", False)
        # Checking user input for categorical encoding
        if cat_end_input:
            # Storing custom categorical encoding indicator in data transform dictionary
            self.data_transform_dict["custom_categorical_encoding_ind"] = True
            # Fetching user input list for performing 
            encoding_list = self.custom_data.get("CategoricalEncodingParam", None).copy()
            if encoding_list:
                volatile = encoding_list.pop("volatile", False)
                persist = encoding_list.pop("persist", False)
                onehot_encode_ind = encoding_list.get("OneHotEncodingIndicator", False)
                ordinal_encode_ind = encoding_list.get("OrdinalEncodingIndicator", False)
                target_encode_ind = encoding_list.get("TargetEncodingIndicator", False)
                # Checking if any of categorical encoding technique indicator 
                if not any([onehot_encode_ind, ordinal_encode_ind, target_encode_ind]):  
                    self._display_msg(inline_msg="No information provided for any type of customized categorical encoding techniques. AutoML will proceed with default encoding technique.",
                                      progress_bar=self.progress_bar)
                else:
                    if onehot_encode_ind:
                        unique_count = []
                        ohe_list = encoding_list.get("OneHotEncodingList", None)
                        # Checking for empty list
                        if not ohe_list:
                            self._display_msg(inline_msg="No information provided for customized one hot encoding technique.",
                                              progress_bar=self.progress_bar)
                        else:
                            # Checking for column present in dataset or not
                            _Validators._validate_dataframe_has_argument_columns(ohe_list, "OneHotEncodingList", self.data, "df")

                            # Keeping track for existing columns before apply one hot encoding
                            col_bf_ohe = self.data.columns
                            # Detecting categorical columns with their unique counts
                            for col in ohe_list:
                                unique_count.append(self.data.drop_duplicate(col).size)
                            # Performing one hot encoding   
                            self._one_hot_encoding(ohe_list, unique_count)
                            # Keeping track for new columns after apply one hot encoding
                            col_af_ohe = self.data.columns
                            # Fetching list of columns on which outlier processing should not be applied
                            self.excluded_cols.extend(self._extract_list(col_af_ohe, col_bf_ohe))
                            
                            self._display_msg(msg="Updated dataset sample after performing one hot encoding:",
                                              data=self.data,
                                              progress_bar=self.progress_bar)
                            
                    if ordinal_encode_ind:
                        ord_list = encoding_list.get("OrdinalEncodingList", None)
                        # Checking for empty list
                        if not ord_list:
                            self._display_msg(inline_msg="No information provided for customized ordinal encoding technique.",
                                              progress_bar=self.progress_bar)
                        else:
                            # Checking for column present in dataset or not
                            _Validators._validate_dataframe_has_argument_columns(ord_list, "OrdinalEncodingList", self.data, "df")
                            
                            # Performing ordinal encoding
                            self._ordinal_encoding(ord_list)
                            self._display_msg(msg="Updated dataset sample after performing ordinal encoding:",
                                              data=self.data,
                                              progress_bar=self.progress_bar)

                    if target_encode_ind:
                        if self.cluster:
                            self._display_msg(inline_msg="Target Encoding is not applicable for clustering. Skipping it.",
                                              progress_bar=self.progress_bar)
                        else:
                            tar_list = encoding_list.get("TargetEncodingList", None)
                            if not tar_list:
                                self._display_msg(inline_msg="No information provided for customized target encoding technique.",
                                                  progress_bar=self.progress_bar)
                            else:    
                                # Performing target encoding
                                self._target_encoding(tar_list)
                                self._display_msg(msg="Updated dataset sample after performing target encoding:",
                                                  data=self.data,
                                                  progress_bar=self.progress_bar)
            else:
                self._display_msg(inline_msg="No input provided for performing customized categorical encoding. AutoML will proceed with default encoding technique.",
                                  progress_bar=self.progress_bar)               
        else:
            self._display_msg(inline_msg="AutoML will proceed with default encoding technique.",
                              progress_bar=self.progress_bar)
            
        # Performing default encoding on remaining categorical columns   
        self._encoding_categorical_columns()

    def _numapply_transformation(self, target_col, transform_val): 
        """
        DESCRIPTION:
            Function to perform different numerical transformations using NumApply on numerical features based on user input.

        PARAMETERS:
            target_col:
                Required Argument.
                Specifies the numerical column for which transformation will be performed.
                Types: str

            transform_val:
                Required Argument.
                Specifies different parameter require for applying numerical transformation.
                Types: dict     
        """
        # Fetching columns for accumulation
        accumulate_columns = self._extract_list(self.data.columns, [target_col])
        apply_method = transform_val["apply_method"]

        # Setting volatile and persist parameters for performing transformation
        volatile, persist = self._get_generic_parameters(func_indicator="MathameticalTransformationIndicator",
                                                         param_name="MathameticalTransformationParam")
        # Adding fit parameters for performing transformation
        fit_params={
            "data": self.data,
            "target_columns" : target_col,
            "apply_method" : apply_method,
            "inplace" : True,
            "persist" :True,
            "accumulate" : accumulate_columns
        }
        # Disabling display table name if persist is True by default
        if not volatile and not persist:
            fit_params["display_table_name"] = False
        
        if volatile:
            fit_params["volatile"] = True
            fit_params["persist"] = False
        # Adding addition details for fit parameters in case of SIGMOID transformation
        if apply_method == "sigmoid":
            sigmoid_style=transform_val["sigmoid_style"]
            fit_params = {**fit_params, "sigmoid_style" : sigmoid_style}
        # Performing transformation on target columns
        transform_output = NumApply(**fit_params).result
        if not volatile and not persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(transform_output._table_name)
        return transform_output
  
    def _numerical_transformation(self, target_columns, num_transform_data, volatile, persist):
        """
        DESCRIPTION:
            Function to perform different numerical transformations using Fit and Transform on numerical features based on user input.
                    
        """
        # Adding fit parameters for transformation
        fit_params={
            "data" : self.data,
            "object" : num_transform_data,
            "object_order_column" : "TargetColumn",
            "volatile" : volatile,
            "persist" : persist
        }
        # Peforming fit with all arguments.
        num_fit_obj = Fit(**fit_params)
        # Fetching all numerical columns
        numerical_columns = [col for col, d_type in self.data._column_names_and_types if d_type in ["int","float"]]
        # Extracting id columns where transformation should not affect numerical columns
        id_columns = self._extract_list(numerical_columns,target_columns)
        # Storing fit object and id column list for numerical transformation in data transform dictionary
        self.data_transform_dict['custom_numerical_transformation_fit_object'] = num_fit_obj.result
        self.data_transform_dict['custom_numerical_transformation_id_columns'] = id_columns
        # Adding transform parameters for transformation
        transform_params={
            "data" : self.data,
            "object" : num_fit_obj.result,
            "id_columns" : id_columns,
            "persist" :True
        }
        # Disabling display table name if persist is True by default
        if not volatile and not persist:
            transform_params["display_table_name"] = False
        
        if volatile:
            transform_params["volatile"] = True
            transform_params["persist"] = False
        # Peforming transformation on target columns
        self.data = Transform(**transform_params).result
        if not volatile and not persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(self.data._table_name)
        
        self.data_mapping['fit_numerical_result'] = num_fit_obj.result._table_name
        self.data_mapping['numerical_transformed_data'] = self.data._table_name
        self._display_msg(msg="Updated dataset sample after applying numerical transformation:",
                          data=self.data,
                          progress_bar=self.progress_bar)
    
    def _mathematical_transformation(self):
        """
        DESCRIPTION:
            Function to perform different mathematical transformations (i.e., log, pow,
            exp, sininv, sigmoid) on numerical features based on user input.
        """
        self._display_msg(msg="\nStarting customized mathematical transformation ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        
        mat_transform_input = self.custom_data.get("MathameticalTransformationIndicator", False)
        # Checking user input for mathematical transformations
        if mat_transform_input:
            # Extracting list required for mathematical transformations
            mat_transform_list = self.custom_data.get("MathameticalTransformationParam", None).copy()
            
            if mat_transform_list:
                volatile = mat_transform_list.pop("volatile", False)
                persist = mat_transform_list.pop("persist", False)
                # Checking for column present in dataset or not
                _Validators._validate_dataframe_has_argument_columns(list(mat_transform_list.keys()), 
                                                                     "MathameticalTransformationParam", self.data, "df")

                # List of storing target columns and mathematical transformation information
                transform_data=[]
                target_columns=[]
                # Storing custom mathematical transformation indicator in data transform dictionary
                self.data_transform_dict['custom_mathematical_transformation_ind'] = True
                # Storing custom numapply transformation parameters in data transform dictionary
                self.data_transform_dict['custom_numapply_transformation_param'] = {}

                for col, transform_val in mat_transform_list.items():
                    apply_method=transform_val["apply_method"]
                    if apply_method in (["sininv","sigmoid"]):
                        # Applying numapply transformation
                        self.data = self._numapply_transformation(col,transform_val)
                        self.data_mapping[f'{apply_method}_transformed_data'] = self.data._table_name
                        self._display_msg(msg="Updated dataset sample after applying numapply transformation:",
                                          data=self.data,
                                          progress_bar=self.progress_bar)
                        # Updating parameter details for each column
                        self.data_transform_dict['custom_numapply_transformation_param'].update({col:transform_val})
                    else:
                        # Handling specific scenarios for log and pow transformation
                        parameters=""
                        if apply_method == "log":
                            base = transform_val["base"]
                            parameters = json.dumps({"base":base})
                        elif apply_method == "pow":
                            exponent = transform_val["exponent"]
                            parameters = json.dumps({"exponent":exponent})
                        target_columns.append(col)
                        transform_data.append({"TargetColumn":col, "DefaultValue":1, "Transformation":apply_method, "Parameters":parameters})
                # Checking for transformation data
                if len(transform_data):
                    # Coverting into pandas and then teradata dataframe for performing further opration
                    transform_data = pd.DataFrame(transform_data, columns=["TargetColumn", "DefaultValue", "Transformation", "Parameters"]) 
                    self._display_msg(msg="Numerical transformation information :-",
                                      data=transform_data,
                                      progress_bar=self.progress_bar)
                    copy_to_sql(df=transform_data, table_name="automl_num_transform_data", temporary=True)
                    num_transform_data = DataFrame.from_table("automl_num_transform_data") 
                    # Applying transformation using Fit/Transform functions
                    self._numerical_transformation(target_columns, num_transform_data, volatile, persist)
                    # Storing custom numerical transformation parameters and column list in data transform dictionary
                    self.data_transform_dict['custom_numerical_transformation_col'] = target_columns
                    self.data_transform_dict['custom_numerical_transformation_params'] = num_transform_data
            else:
                self._display_msg(inline_msg="No input provided for performing customized mathematical transformation.",
                                  progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Skipping customized mathematical transformation.",
                              progress_bar=self.progress_bar)

    def _non_linear_transformation(self):
        """
        DESCRIPTION:
            Function to perform customized non-linear transformation on numerical features based on user input.
            
        """
        self._display_msg(msg="\nStarting customized non-linear transformation ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        nl_transform_input = self.custom_data.get("NonLinearTransformationIndicator", False)
        # Checking user input for non-linear transformation
        if nl_transform_input:
            nl_transform_list = self.custom_data.get("NonLinearTransformationParam", None)
            # Extracting list required for non-linear transformation
            if nl_transform_list:
                volatile = nl_transform_list.pop("volatile", False)
                persist = nl_transform_list.pop("persist", False)
                total_combination = len(nl_transform_list)
                # Generating all possible combination names
                possible_combination = ["Combination_"+str(counter) for counter in range(1,total_combination+1)]
                self._display_msg(msg="Possible combination :",
                                  col_lst=possible_combination,
                                  progress_bar=self.progress_bar)
                # Storing custom non-linear transformation indicator in data transform dictionary
                self.data_transform_dict['custom_non_linear_transformation_ind'] = True
                # Storing custom non-linear transformation fit object in data transform dictionary
                self.data_transform_dict['custom_non_linear_transformation_fit_object'] = {}
                # print("Possible combination :",possible_combination)
                # Performing transformation for each combination
                for comb, transform_val in nl_transform_list.items():
                    if comb in possible_combination:
                        target_columns = transform_val["target_columns"]
                        # Checking for column present in dataset or not
                        _Validators._validate_dataframe_has_argument_columns(target_columns, 
                                                                             "target_columns", self.data, "df")

                        formula = transform_val["formula"]
                        result_column = transform_val["result_column"]
                        # Adding fit params for transformation
                        fit_param = {
                            "data" : self.data,
                            "target_columns" : target_columns,
                            "formula" : formula,
                            "result_column" : result_column,
                            "volatile" : volatile,
                            "persist" : persist
                        }
                        # Performing fit on dataset
                        fit_obj = NonLinearCombineFit(**fit_param)
                        # Updating it for each non-linear combination
                        self.data_transform_dict['custom_non_linear_transformation_fit_object'].update({comb:fit_obj.result})
                        # Adding transform params for transformation   
                        transform_params = {
                            "data" : self.data,
                            "object" : fit_obj,
                            "accumulate" : self.data.columns,
                            "persist" : True
                        }
                        # Disabling display table name if persist is True by default
                        if not volatile and not persist:
                            transform_params["display_table_name"] = False
                        
                        if volatile:
                            transform_params["volatile"] = True
                            transform_params["persist"] = False
                        self.data = NonLinearCombineTransform(**transform_params).result

                        self.data_mapping[f'fit_nonlinear_{comb}_output'] = fit_obj.output_data._table_name
                        self.data_mapping[f'fit_nonlinear_{comb}_result'] = fit_obj.result._table_name
                        self.data_mapping['non_linear_transformed_data'] = self.data._table_name

                        if not volatile and not persist:
                            # Adding transformed data containing table to garbage collector
                            GarbageCollector._add_to_garbagecollector(self.data._table_name)
                    else:
                        self._display_msg(inline_msg="Combinations are not as per expectation.",
                                          progress_bar=self.progress_bar)
                self._display_msg(msg="Updated dataset sample after performing non-liner transformation:",
                                  data=self.data,
                                  progress_bar=self.progress_bar)                  
            else:
                self._display_msg(inline_msg="No information provided for performing customized non-linear transformation.",
                                  progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Skipping customized non-linear transformation.",
                              progress_bar=self.progress_bar)   
            
    def _anti_select_columns(self):
        """
        DESCRIPTION:
            Function to remove specific features from dataset based on user input.
                    
        """
        self._display_msg(msg="\nStarting customized anti-select columns ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        anti_select_input = self.custom_data.get("AntiselectIndicator", False) 
        # Checking user input for anti-select columns    
        if anti_select_input:
            anti_select_params = self.custom_data.get("AntiselectParam", None)
            if anti_select_params:
                # Extracting list required for anti-select columns
                anti_select_list = anti_select_params.get("excluded_columns", None)
                volatile = anti_select_params.get("volatile", False)
                persist = anti_select_params.get("persist", False)
                if(anti_select_list):
                    if all(item in self.data.columns for item in anti_select_list):
                        # Storing custom anti-select columns indicator and column list in data transform dictionary
                        self.data_transform_dict['custom_anti_select_columns_ind'] = True
                        self.data_transform_dict['custom_anti_select_columns'] = anti_select_list
                        fit_params = {
                            "data" : self.data,
                            "exclude" : anti_select_list,
                            "volatile" : volatile,
                            "persist" : persist
                        }
                        # Performing transformation for given user input
                        self.data = Antiselect(**fit_params).result
                        self._display_msg(msg="Updated dataset sample after performing anti-select columns:",
                                        data=self.data,
                                        progress_bar=self.progress_bar)
                    else:
                        self._display_msg(msg="Columns provided in list are not present in dataset:",
                                        col_lst=anti_select_list,
                                        progress_bar=self.progress_bar)         
            else:
                self._display_msg(inline_msg="No information provided for performing anti-select columns operation.",
                                  progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="Skipping customized anti-select columns.",
                              progress_bar=self.progress_bar)
            
    def _get_generic_parameters(self,
                                func_indicator=None,
                                param_name=None):
        """
        DESCRIPTION:
            Function to set generic parameters.
        
        PARAMETERS:     
            func_indicator:
                Optional Argument.
                Specifies the name of function indicator.
                Types: str
                
            param_name:
                Optional Argument.
                Specifies the name of the param which contains generic parameters.
                Types: str

        RETURNS:
            Tuple containing volatile and persist parameters.
        """
        # Prioritizing persist argument and then volatile
        persist = self.persist
        volatile = self.volatile or (configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE and persist is False)
        if self.custom_data is not None and self.custom_data.get(func_indicator, False):
            volatile = self.custom_data[param_name].get("volatile", False)
            persist = self.custom_data[param_name].get("persist", False)

        return (volatile, persist)
