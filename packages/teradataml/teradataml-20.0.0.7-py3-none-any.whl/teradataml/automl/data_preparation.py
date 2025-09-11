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
import numpy as np
import pandas as pd
import time
import warnings

# Teradata libraries
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml import OutlierFilterFit, OutlierFilterTransform
from teradataml import RoundColumns, TeradataMlException
from teradataml import ScaleFit, ScaleTransform
from teradataml import UtilFuncs, TeradataConstants
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.messages import Messages, MessageCodes
from teradataml.utils.validators import _Validators
from teradataml import configure, INTEGER
from teradataml.common.constants import TeradataConstants


class _DataPreparation:
    
    def __init__(self, 
                 data=None, 
                 target_column=None, 
                 verbose=0,
                 excluded_columns=None,
                 custom_data=None,
                 data_transform_dict=None,
                 task_type="Regression",
                 **kwargs):
        """
        DESCRIPTION:
            Function initializes the data, target column and columns datatypes
            for data preparation.
         
        PARAMETERS:  
            data:
                Required Argument.
                Specifies the input teradataml Dataframe for data preparation phase.
                Types: teradataml Dataframe
            
            target_column:
                Required Argument.
                Specifies the name of the target column in "data".
                Types: str
            
            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar and leaderboard
                    * 1: prints the execution steps of AutoML.
                    * 2: prints the intermediate data between the execution of each step of AutoML.
                Types: int
            
            excluded_columns:
                Required Argument.
                Specifies the columns should be excluded from any processing.
                Types: str or list of strings (str)

            custom_data:
                Optional Argument.
                Specifies json object containing user customized input.
                Types: json object
            
            data_transform_dict:
                Optional Argument.
                Specifies the parameters for data transformation.
                Types: dict
            
            task_type:
                Required Argument.
                Specifies the task type for AutoML, whether to apply regresion OR classification
                on the provived dataset.
                Default Value: "Regression"
                Permitted Values: "Regression", "Classification"
                Types: str

            **kwargs:
                Specifies the additional arguments for data preparation. Below
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

                    seed:
                        Optional Argument.
                        Specifies the random seed for reproducibility.
                        Default Value: 42
                        Types: int
                    
                    automl_phases:
                        Optional Argument.
                        Specifies the phase of AutoML to be executed.
                        Default Value: None
                        Types: str or list of str.
                    
                    cluster:
                        Optional Argument.
                        Specifies whether to run data preparation for handling clustering.
                        Default Value: False
                        Types: bool

                    imbalance_handling_method:
                        Optional Argument.
                        Specifies which imbalance handling method to use.
                        Default Value: "SMOTE"
                        Permitted Values: "SMOTE", "ADASYN", "SMOTETomek", "NearMiss"
                        Types: str

        """
        self.data = data
        self.target_column = target_column
        self.verbose = verbose
        self.excluded_columns = excluded_columns
        self.data_transform_dict = data_transform_dict
        self.custom_data = custom_data
        self.task_type = task_type
        self.volatile = kwargs.get("volatile", False)
        self.persist = kwargs.get("persist", False)
        self.aml_phases = kwargs.get("automl_phases", None)
        self.cluster = kwargs.get('cluster', False)
        self._data_sampling_method = kwargs.get("imbalance_handling_method", "SMOTE")
        
        # Setting default value for auto run mode
        self._scale_method_reg = "STD"
        self._scale_method_cls = "RANGE"
        self._scale_method_clust = "STD"
        
        self.data_types = {key: value for key, value in self.data._column_names_and_types}
        self.seed = kwargs.get("seed", 42)
        # np.random.seed() affects the random number generation in numpy and sklearn
        # setting this changes the global state of the random number generator
        # hence, setting the seed only if it is not None
        if kwargs.get("seed") is not None:
            np.random.seed(self.seed)
  
        self.data_mapping = kwargs.get("data_mapping", {})
        
    def data_preparation(self, 
                         auto=True):
        """
        DESCRIPTION:
            Function to perform following tasks:-
                1. Performs outlier processing and transformation on dataset.
                2. Performs feature selection using RFE, PCA, and Lasso.
                3. Performs feature scaling.
         
        PARAMETERS:  
            auto:
                Optional Argument.
                Specifies whether to run AutoML in custom mode or auto mode.
                When set to False, runs in custom mode. Otherwise, by default runs in auto mode.
                Default Value: True
                Types: bool    
        
        RETURNS:
             list of lists containing, feature selected by rfe, pca and lasso.  
        """
        self._display_heading(phase=2,
                              progress_bar=self.progress_bar,
                              automl_phases=self.aml_phases)
        self._display_msg(msg='Data preparation started ...',
                          progress_bar=self.progress_bar)
        # Setting user value in case of custom running mode
        if not auto:
            self._set_custom_scaling_method()
            self._set_custom_sampling()
        
        # Handling float type features before processing with feature selection and scaling
        training_data = self._handle_generated_features()
        self.progress_bar.update()

        # Handling ouliers in dataset
        self._handle_outliers(auto)
        self.progress_bar.update()

        # Temporary Pulling data for feature selection 
        # Will change after sto
        
        # Checking for data imbalance    
        if not self.cluster:
            if self._check_data_imbalance(training_data):
                training_data = self._data_sampling(training_data)
        self.progress_bar.update()
        
        # Sorting the data based on id to 
        # remove any shuffling done by sampling
        training_data = training_data.sort_values(by='id')

        if not self.cluster:
            # Performing feature selection using lasso followed by scaling  
            self._feature_selection_Lasso(training_data)
            self._scaling_features(feature_selection_mtd="lasso")
            self.progress_bar.update()
            
            # Performing feature selection using rfe followed by scaling      
            self._feature_selection_RFE(training_data)
            self._scaling_features(feature_selection_mtd="rfe")
            self.progress_bar.update()
        else:
            self._scaling_features(feature_selection_mtd="Non_pca")
            self.progress_bar.update()

        # Performing scaling followed by feature selection using pca     
        self._scaling_features(feature_selection_mtd="pca")
        self._feature_selection_PCA()
        self.progress_bar.update()

        if not self.cluster:
            return [self.rfe_feature, self.lasso_feature, self.pca_feature], self.data_transform_dict, self.data_mapping
        else:
            return [self.non_pca_feature, self.pca_feature], self.data_transform_dict, self.data_mapping

    def _handle_outliers(self,
                         auto):
        """
        DESCRIPTION:
            Function to handle existing outliers in dataset based on running mode.
        """
        if auto:
            self._outlier_processing()
        else:
            self._custom_outlier_processing()

    def _check_data_imbalance(self, 
                              data):
        """
        DESCRIPTION:
            Internal function calculate and checks the imbalance in dataset 
            in case of classification.
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame.
                Types: teradataml Dataframe
        """
        pass
    
    def _data_sampling(self,
                       data):
        """
        DESCRIPTION:
            Function to handle data imbalance in dataset using sampling techniques 
            in case of classification.
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame.
                Types: pandas Dataframe.
        """
        pass
    
    def _set_custom_sampling(self):
        """
        DESCRIPTION:
             Internal Function to handle customized data sampling for imbalance dataset.
        """
        pass
    
    def _outlier_handling_techniques(self):
        """
        DESCRIPTION:
           Function determines the handling techniques[drop rows/impute values] for outlier columns in the dataset.
        """
        columns_to_drop_rows = []
        columns_to_impute = []
        # Keeping default method for outlier detection "Tukey"
        outlier_method = "Tukey"
        
        # List of columns for outlier processing.
        # Excluding target column and excluded columns from outlier processing
        outlier_columns = [col for col in self.data.columns if col not in self.excluded_columns + ['id', self.target_column]]
        
        if len(outlier_columns) != 0:
            # Detecting outlier percentage in each columns
            outlier_percentage_df = self._outlier_detection(outlier_method, outlier_columns)

            # Outlier Handling techniques
            for i in outlier_percentage_df.itertuples():
                # Column Name
                col = i[0]
                # Outlier value
                value = i[1]
                if self.cluster:
                    if value > 0.0:
                        columns_to_impute.append(col)
                else:
                    # Dropping rows
                    if value > 0.0  and value <= 8.0 :
                        columns_to_drop_rows.append(col)
                    elif value> 8.0 and value <= 25.0:
                        columns_to_impute.append(col)
            
        return columns_to_drop_rows, columns_to_impute

    def _outlier_handling(self,
                          target_columns,
                          outlier_method,
                          replacement_value):
        """
        DESCRIPTION:
            Function to handle outlier for target column based outlier method and replacement value.

        PARAMETERS:
            target_columns:
                Required Argument.
                Specifies the target columns required for outlier handling.
                Types: str or list of strings (str)
        
            outlier_method:
                Required Argument.
                Specifies the outlier method required for outlier handling.
                Types: str
                   
            replacement_value:
                Optional Argument.
                Specifies the value required in case of outlier replacement.
                Types: str, float
        
        RETURNS:
            Pandas DataFrame containing, column name with outlier percentage.

        """

        # Setting volatile and persist parameters for Outlier handling function
        volatile, persist = self._get_generic_parameters(func_indicator='OutlierFilterIndicator',
                                                         param_name='OutlierFilterParam')

        # Performing fit on dataset for outlier handling
        fit_params = {
            "data" : self.data,
            "target_columns" : target_columns,
            "outlier_method" : outlier_method,
            "replacement_value" : replacement_value,
            "volatile" : volatile,
            "persist" : persist
        }
        outlier_fit_out = OutlierFilterFit(**fit_params)
        # Performing transform on dataset for outlier handling
        transform_params = {
            "data" : self.data,
            "object" : outlier_fit_out.result,
            "persist" : True
        }

        # Disabling print if persist is True by default
        if not volatile and not persist:
            transform_params["display_table_name"] = False

        if volatile:
            transform_params["volatile"] = True
            transform_params["persist"] = False
        self.data = OutlierFilterTransform(**transform_params).result

        if not volatile and not persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(self.data._table_name)

        # Returning outlier fit object to store in data mapping dictionary
        return outlier_fit_out

    def _outlier_processing(self):
        """
        DESCRIPTION:
            Function performs outlier processing on dataset. It identifies and handle outliers in the dataset.
                
        """
        self._display_msg(msg="\nOutlier preprocessing ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        start_time = time.time()
        
        # List of columns for dropping rows or imputing 
        columns_to_drop_rows, columns_to_impute = self._outlier_handling_techniques()
        # Keeping default method for outlier handling "Tukey"
        outlier_handling_method = "Tukey"

        # Dropping rows 
        if len(columns_to_drop_rows) !=0:
            self._display_msg(msg="Deleting rows of these columns:",
                              col_lst=columns_to_drop_rows,
                              progress_bar=self.progress_bar)
            target_columns=columns_to_drop_rows
            replacement_strategy = "DELETE"
            fit_obj = self._outlier_handling(target_columns, outlier_handling_method, replacement_strategy)
            self.data_mapping['fit_outlier_delete_output'] = fit_obj.output_data._table_name
            self.data_mapping['fit_outlier_delete_result'] = self.data._table_name
            self.data_mapping['outlier_filtered_data'] = self.data._table_name
            self._display_msg(msg="Sample of dataset after removing outlier rows:",
                              data=self.data,
                              progress_bar=self.progress_bar)
        
        # Imputing Median value in place of outliers
        if len(columns_to_impute) != 0:
            self._display_msg(msg="median inplace of outliers:",
                              col_lst=columns_to_impute,
                              progress_bar=self.progress_bar)
            target_columns=columns_to_impute
            replacement_strategy = "MEDIAN"
            fit_obj = self._outlier_handling(target_columns, outlier_handling_method, replacement_strategy)
            self.data_mapping['fit_outlier_impute_output'] = fit_obj.output_data._table_name
            self.data_mapping['fit_outlier_impute_result'] = fit_obj.result._table_name
            self.data_mapping['outlier_imputed_data'] = self.data._table_name
            self._display_msg(msg="Sample of dataset after performing MEDIAN inplace:",
                              data=self.data,
                              progress_bar=self.progress_bar)

        if len(columns_to_drop_rows) == 0 and len(columns_to_impute) == 0:
            self._display_msg(msg='Analysis indicates not outlier in the dataset. No Action Taken.',
                              progress_bar=self.progress_bar)
            
        end_time = time.time()
        self._display_msg("Time Taken by Outlier processing: {:.2f} sec ".format(end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)

    def _custom_outlier_processing(self):
        """
        DESCRIPTION:
            Function to perform outlier processing on dataset based on user input.
                
        """
        self._display_msg(msg="\nStarting customized outlier processing ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        outlier_filter_input = self.custom_data.get("OutlierFilterIndicator", False) 
        # Checking user input for outlier filtering   
        if outlier_filter_input:
            # List of columns for outlier processing.
            target_columns = [col for col in self.data.columns if col not in self.excluded_columns]
            # Checking user input for outlier detection method
            outlier_method = self.custom_data.get("OutlierFilterMethod", None)
            if outlier_method == 'PERCENTILE':
                lower_percentile = self.custom_data.get("OutlierLowerPercentile", None)
                upper_percentile = self.custom_data.get("OutlierUpperPercentile", None)
                if lower_percentile and upper_percentile:
                    # Detecting outlier percentage for each columns
                    outlier_df = self._outlier_detection(outlier_method=outlier_method, column_list=target_columns, \
                        lower_percentile=lower_percentile, upper_percentile=upper_percentile)
            else:
                # Detecting outlier percentage for each column in case of other than percentile method
                outlier_df = self._outlier_detection(outlier_method=outlier_method, column_list=target_columns)
                                              
            # Checking for rows if outlier containing columns exist
            if outlier_df.shape[0]:
                # Checking user input list for outlier handling
                outlier_transform_list = self.custom_data.get("OutlierFilterParam", None).copy()
                if outlier_transform_list:
                    volatile = outlier_transform_list.pop("volatile", False)
                    persist = outlier_transform_list.pop("persist", False)
                    # Checking user input for outlier handling
                    _Validators._validate_dataframe_has_argument_columns(list(outlier_transform_list.keys()), "OutlierFilterParam",
                                                                         self.data, "outlier_data")

                    for target_col, transform_val in outlier_transform_list.items():
                        # Fetching replacement value
                        replacement_value = transform_val["replacement_value"]
                        # Performing outlier handling
                        fit_obj = self._outlier_handling(target_col, outlier_method, replacement_value)
                        self.data_mapping[f'fit_{target_col}_outlier_output'] = fit_obj.output_data._table_name
                        self.data_mapping[f'fit_{target_col}_outlier_result'] = fit_obj.result._table_name
                        self.data_mapping[f'{target_col}_outlier_treated_data'] = self.data._table_name
                        self._display_msg(msg="Sample of dataset after performing custom outlier filtering",
                                          data=self.data,progress_bar=self.progress_bar)
                else:
                    self._display_msg(inline_msg="No information provided for feature transformation in outlier handling.",
                                      progress_bar=self.progress_bar)
            else:
                self._display_msg(inline_msg="No oultiers found in dataset after applying the selected method.",
                                  progress_bar=self.progress_bar)
        else:
            self._display_msg(inline_msg="No information provided for customized outlier processing. AutoML will proceed with default settings.",
                              progress_bar=self.progress_bar)
            # Performing default handling for outliers
            if not self.cluster:
                self._outlier_processing()

    # function for getting value of "K" in k folds cross validation
    def _num_of_folds(self, rows=None):
        """
        DESCRIPTION:
            Function to determine the number of folds for cross-validation 
            based on the number of rows in the dataset.
        PARAMETERS:
            rows:
                Required Argument.
                Specifies the number of rows in the dataset.
                Types: int
        RETURNS:
            int, number of folds to be used for cross-validation.
        """
        num_of_folds = lambda rows: 2 if rows > 20000 else (4 if 1000 < rows <= 20000 else 10)
        return num_of_folds(rows)
    
    def _feature_selection_PCA(self):
        """
        DESCRIPTION:
             Function performs Principal Component Analysis (PCA) for feature selection. 
             It reduces the dimensionality of the dataset by identifying and retaining the most informative features.
        """
        self._display_msg(msg="\nDimension Reduction using pca ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        # Required imports for PCA
        from sklearn.decomposition import PCA
        
        start_time = time.time()

        # Temporary Pulling data for feature selection
        pca_train = DataFrame.from_table(self.data_mapping['pca_train']).to_pandas()
 
        # Drop unnecessary columns and store the result
        if not self.cluster:
            train_data = pca_train.drop(columns=['id', self.target_column], axis=1)
        else:
            train_data = pca_train.drop(columns=['id'], axis=1)

        # Initialize and fit PCA
        pca = PCA(random_state=self.seed)
        pca.fit(train_data)

        # Find the number of components for PCA
        variance = pca.explained_variance_ratio_
        n = np.argmax(np.cumsum(variance) >= 0.95) + 1

        # Create a new instance of PCA with the optimal number of components
        pca = PCA(n_components=n, random_state=self.seed)

        # Apply PCA on dataset
        X_train_pca = pca.fit_transform(train_data)
        
        # storing instance of PCA in data transformation dictionary
        self.data_transform_dict["pca_fit_instance"] = pca
        self.data_transform_dict["pca_fit_columns"] = train_data.columns.tolist()
        
        #converting the numarray into dataframes
        train_df = pd.DataFrame(X_train_pca)
        
        #creating names for combined columns 
        column_name = {col: 'col_'+str(i) for i,col in enumerate(train_df.columns)}
        
        # storing the new column names in data transformation dictionary
        self.data_transform_dict['pca_new_column'] = column_name
        
        #renaming them 
        train_df = train_df.rename(columns=column_name)
        
        # adding the id column [PCA does not shuffle the dataset]
        train_df = pd.concat([pca_train.reset_index(drop=True)['id'], train_df.reset_index(drop=True)], axis=1)
        
        # merging target column with new data
        if not self.cluster:
            train_df[self.target_column] = pca_train[self.target_column].reset_index(drop=True)
            self.pca_feature = train_df.drop(columns=['id', self.target_column], axis=1).columns.tolist()
        else:
            self.pca_feature = train_df.drop(columns=['id'], axis=1).columns.tolist()
        
        self._display_msg(msg="PCA columns:",
                          col_lst=self.pca_feature,
                          progress_bar=self.progress_bar)
        end_time = time.time()
        self._display_msg(msg="Total time taken by PCA: {:.2f} sec  ".format( end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)
        
        # Pushing the data in database
        self.copy_dataframe_to_sql(train_df, 'pca', self.persist)
 
    def _feature_selection_RFE(self,
                               data=None):
        """
        DESCRIPTION:
             Function performs Recursive Feature Elimination (RFE) for feature selection. 
             It identifies a subset of the most relevant features in the dataset.
             
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input train pandas DataFrame.
                Types: pandas Dataframe   
        """
        self._display_msg(msg="\nFeature selection using rfe ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        
        # Required imports for RFE   
        from sklearn.feature_selection import RFECV
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.model_selection import StratifiedKFold

        start_time = time.time()
        # Regression
        is_classification = self.is_classification_type()
        # Getting the value of k in k-fold cross-validation
        folds = self._num_of_folds(data.shape[0])

        # Suppressing warnings generated by pandas and sklearn
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')

            # Random forest for RFE model
            RFModel = RandomForestRegressor if not is_classification else RandomForestClassifier
            rf = RFModel(n_estimators=100, random_state=self.seed)

            # Determine the scoring metric based on the number of unique classes
            score = 'r2' if not self.is_classification_type() \
                    else 'roc_auc' if self.data.drop_duplicate(self.target_column).size == 2 else 'f1_macro'

            # # Instantiate StratifiedKFold with shuffling for classification
            cv = folds if not self.is_classification_type() \
                    else StratifiedKFold(n_splits=folds, shuffle=False)

            # Define the RFE with cross-validation
            rfecv = RFECV(rf, cv=cv, scoring=score)

            # Prepare data
            train_data = data.drop(columns=['id',self.target_column], axis=1)
            train_target = data[self.target_column]

            # Fit the RFE using cv
            rfecv.fit(train_data, train_target)

            # Extract the features
            features = train_data.columns[rfecv.support_].tolist()

            self._display_msg(msg="feature selected by RFE:",
                            col_lst=features,
                            progress_bar=self.progress_bar)
            features.append(self.target_column)
            features.insert(0,'id')
            
            selected_rfe_df = data[features]
            
            # storing the rfe selected features in data transformation dictionary
            self.data_transform_dict['rfe_features'] = features
            
            columns_to_rename = [col for col in selected_rfe_df.columns if col not in ['id', self.target_column]]
            new_column = {col: f'r_{col}' for col in columns_to_rename}
            self.excluded_columns.extend([new_column[key] for key in self.excluded_columns if key in new_column])
            
            selected_rfe_df.rename(columns=new_column, inplace=True)
        
        # storing the rename column list in data transformation dictionary
        self.data_transform_dict['rfe_rename_column'] = columns_to_rename
        
        end_time = time.time()
        self._display_msg(msg="Total time taken by feature selection: {:.2f} sec  ".format( end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)
        self.rfe_feature = selected_rfe_df.drop(columns=['id',self.target_column], axis=1).columns.tolist()

        # Pushing data into database
        self.copy_dataframe_to_sql(selected_rfe_df, 'rfe', self.persist)
        
    def _feature_selection_Lasso(self,
                                 data=None):
        """
        DESCRIPTION:
            Function performs Lasso Regression for feature selection.
            It helps in identifing and retaining the most important features while setting less important ones to zero.
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input train pandas DataFrame.
                Types: pandas Dataframe

        """
        start_time = time.time()
        self._display_msg(msg="\nFeature selection using lasso ...",
                          progress_bar=self.progress_bar,
                          show_data=True)
        
        # Required imports for Lasso
        from sklearn.model_selection import GridSearchCV
        from sklearn.linear_model import Lasso
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold

        # Getting the value k in k-fold cross-validation
        num_folds = self._num_of_folds(data.shape[0])

        # Prepare data
        train_features = data.drop(columns=['id',self.target_column], axis=1)
        train_target = data[self.target_column]

        # Suppressing warnings generated by pandas and sklearn
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')

            # Determine the estimator and parameters based on the type of problem
            if self.is_classification_type():
                if self.data.drop_duplicate(self.target_column).size == 2:
                    scoring_metric = 'roc_auc'
                else:
                    scoring_metric = 'f1_macro'
                estimator = LogisticRegression(solver='saga', penalty='l2', multi_class='auto', random_state=self.seed)
                parameters = {'C':[0.00001,0.0001,0.001,0.01,0.05,0.1,10,100,1000], 'max_iter': [100, 500]}
            else:
                estimator = Lasso(random_state=self.seed)
                parameters = {'alpha':[0.00001,0.0001,0.001,0.01,0.05,0.1,10,100,1000], 'max_iter': [100, 500]}
                scoring_metric = "r2"

            if self.is_classification_type():
                cv = StratifiedKFold(n_splits=5, shuffle=False)
            else:
                cv = num_folds

            # Applying hyperparameter tuning and optimizing score
            hyperparameter_search = GridSearchCV(estimator, parameters, cv=cv, refit=True, 
                                                 scoring=scoring_metric, verbose=0)

            # Fitting the best result from hyperparameter
            hyperparameter_search.fit(train_features, train_target)

            # Extracting the important estimators
            feature_importance = np.abs(hyperparameter_search.best_estimator_.coef_)

        # Extracting feature using estimators whose importance > 0 
        if self.is_classification_type():
            selected_feature_indices = np.where(np.any(feature_importance > 0, axis=0))[0]
            selected_features = np.array(train_features.columns)[selected_feature_indices]
            important_features = list(set(selected_features))
        else:
            important_features = np.array(train_features.columns)[feature_importance>0].tolist()

        self._display_msg(msg="feature selected by lasso:",
                        col_lst=important_features,
                        progress_bar=self.progress_bar)

        important_features = ['id'] + important_features + [self.target_column]
        selected_lasso_df = data[important_features]

        # Storing the lasso selected features in data transformation dictionary
        self.data_transform_dict['lasso_features'] = important_features

        # Calculate the elapsed time
        end_time = time.time()
        self._display_msg(msg="Total time taken by feature selection: {:.2f} sec  ".format( end_time - start_time),
                        progress_bar=self.progress_bar,
                        show_data=True)
        self.lasso_feature = selected_lasso_df.drop(columns=['id',self.target_column], axis=1).columns.tolist()

        self.copy_dataframe_to_sql(selected_lasso_df, 'lasso', self.persist)

    def copy_dataframe_to_sql(self, 
                              data,
                              prefix,
                              persist):
        """
        DESCRIPTION:
            Function to copy dataframe to SQL with generated table name.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame.
                Types: pandas Dataframe

            prefix:
                Required Argument.
                Specifies the prefix for the table name.
                Types: str

            persist:
                Required Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Types: bool
        """
        # Generating table names
        train_table_name = UtilFuncs._generate_temp_table_name(prefix='{}_train'.format(prefix), 
                                                               table_type = TeradataConstants.TERADATA_TABLE,
                                                               gc_on_quit=not persist)
        # If configure.temp_object_type="VT", _generate_temp_table_name() retruns the
        # table name in fully qualified format.
        train_table_name = UtilFuncs._extract_table_name(train_table_name)

        # Storing the table names in the table name mapping dictionary
        self.data_mapping['{}_train'.format(prefix)] = train_table_name

        # In the case of the VT option, the table was being persisted, so the VT condition is being checked. 
        is_temporary = configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE
        # Pushing data into database
        if self.is_classification_type():
            copy_to_sql(df=data, table_name=train_table_name, temporary=is_temporary, if_exists="replace", types={f'{self.target_column}': INTEGER})
        else:
            copy_to_sql(df=data, table_name=train_table_name, if_exists="replace", temporary=is_temporary)
        
    def _scaling_features_helper(self, 
                                 data=None,  
                                 feature_selection_mtd=None):
        """
        DESCRIPTION:
            This function selects the features on which feature scaling should be applied.
            
        PARAMETERS:
            data:
                Required Argument.
                Specifies the data on which feature scaling will be applied.
                Types: teradataml Dataframe
            
            feature_selection_mtd:
                Required Argument.
                Specifies the feature selection algorithm used.
                Types: str
                
        RETURNS:
            scl_col:
                list containing, the scaled columns.   
        """
        columns_to_scale = []
        
        # Iterating over the columns
        for col in data.columns:
            # Selecting columns that will be scaled 
            # Exculding target_col and columns with single value
            if col not in ['id', self.target_column] and \
            data.drop_duplicate(col).size > 1:
                columns_to_scale.append(col)
        
        if feature_selection_mtd == "lasso":
            self.lasso_feature = columns_to_scale
        elif feature_selection_mtd == "rfe":
            self.rfe_feature = columns_to_scale
        elif feature_selection_mtd == "pca":
            self.pca_feature = columns_to_scale
        elif feature_selection_mtd == "raw_scaled":
            self.raw_scaled_feature = columns_to_scale
        else:
            self.non_pca_feature = columns_to_scale
        
        columns_to_scale = [col for col in columns_to_scale if col not in self.excluded_columns]
        return columns_to_scale

    def _scaling_features(self,
                          feature_selection_mtd=None):
        """
        DESCRIPTION:
            Function performs feature scaling on columns present inside the dataset 
            using scaling methods [RANGE/ABS/STD/USTD/MEAN/MIDRANGE/RESCALE].
            
        PARAMETERS:
            feature_selection_mtd:
                Required Argument.
                Specifies the feature selection algorithm used.
                Types: str 
        """
        
        feature_selection_mtd = feature_selection_mtd.lower()
        self._display_msg(msg="\nscaling Features of {} data ...".format(feature_selection_mtd),
                          progress_bar=self.progress_bar,
                          show_data=True)
        
        start_time = time.time()
        data_to_scale = None
        
        if not self.cluster:
            if self.is_classification_type():
                scale_method = self._scale_method_cls
            else:
                scale_method = self._scale_method_reg
        else:
            scale_method = self._scale_method_clust

        # Loading data for feature scaling based of feature selection method
        if feature_selection_mtd == 'rfe':
            data_to_scale = DataFrame(self.data_mapping['rfe_train'])
        elif feature_selection_mtd == 'lasso':
            data_to_scale = DataFrame(self.data_mapping['lasso_train'])
        elif feature_selection_mtd == 'raw_scaled':
            data_to_scale = DataFrame(self.data_mapping['raw_scaled_train'])
        else:
            data_to_scale = self.data

        # Setting volatile and persist parameters for ScaleFit and ScaleTransform functions
        volatile, persist = self._get_generic_parameters(func_indicator='FeatureScalingIndicator',
                                                         param_name='FeatureScalingParam')

        # List of columns that will be scaled
        scale_col= self._scaling_features_helper(data_to_scale, feature_selection_mtd)
        
        if len(scale_col) != 0:
            self._display_msg(msg="columns that will be scaled: ",
                              col_lst=scale_col,
                              progress_bar=self.progress_bar)

            # Scale Fit
            fit_obj = ScaleFit(data=data_to_scale,
                               target_columns=scale_col,
                               scale_method=scale_method,
                               volatile=volatile,
                               persist=persist)
            
            self.data_mapping[f'fit_scale_{feature_selection_mtd}_output'] = fit_obj.output_data._table_name
            self.data_mapping[f'fit_scale_{feature_selection_mtd}_result'] = fit_obj.output._table_name

            # storing the scale fit object and columns in data transformation dictionary
            self.data_transform_dict['{}_scale_fit_obj'.format(feature_selection_mtd)] = fit_obj.output
            self.data_transform_dict['{}_scale_col'.format(feature_selection_mtd)] = scale_col
            
            # List of columns to copy to the output generated by scale transform
            accumulate_cols = list(set(data_to_scale.columns) - set(scale_col))
            
            # Scaling dataset
            transform_obj = ScaleTransform(data=data_to_scale,
                                           object=fit_obj,
                                           accumulate=accumulate_cols)
            scaled_df = transform_obj.result
            
            self._display_msg(msg="Dataset sample after scaling:",
                              data=scaled_df,
                              progress_bar=self.progress_bar)
        else:
            # No columns to scale, Original data will be used
            scaled_df = data_to_scale
            self._display_msg(msg="No columns to scale.",
                              progress_bar=self.progress_bar)

        self.copy_dataframe_to_sql(scaled_df, feature_selection_mtd, persist)

        if self.cluster and feature_selection_mtd == "non_pca":
            self.data_mapping["non_pca_train"] = scaled_df._table_name
        elif self.cluster and feature_selection_mtd == "raw_scaled":
            self.data_mapping["raw_scaled_train"] = scaled_df._table_name

        end_time = time.time()
        self._display_msg(msg="Total time taken by feature scaling: {:.2f} sec".format( end_time - start_time),
                          progress_bar=self.progress_bar,
                          show_data=True)

    def _set_custom_scaling_method(self):
        """
        DESCRIPTION:
            Function to perform feature scaling based on user input.
             
        """ 
        # Fetching user input for performing customized scaling 
        feature_scaling_input = self.custom_data.get("FeatureScalingIndicator", False) 
        # Checking user input for feature scaling    
        if feature_scaling_input:
            # Extracting scaling method
            custom_scaling_params = self.custom_data.get("FeatureScalingParam", None)
            if custom_scaling_params:
                custom_scaling_method = custom_scaling_params.get("FeatureScalingMethod", None)
                if custom_scaling_method is None:
                    self._display_msg(inline_msg="No information provided for customized scaling method. AutoML will continue with default option.",
                                    progress_bar=self.progress_bar)
                else:
                    if self.cluster:
                        self._scale_method_cluster = custom_scaling_method
                    elif self.is_classification_type():
                        self._scale_method_cls = custom_scaling_method
                    else:
                        self._scale_method_reg = custom_scaling_method
        else:
            self._display_msg(inline_msg="No information provided for performing customized feature scaling. Proceeding with default option.",
                              progress_bar=self.progress_bar)

    
    def _handle_generated_features(self):
        """
        DESCRIPTION:
            Function to handle newly generated float features. It will round them upto 4 digit after decimal point.

        RETURNS:
            Pandas DataFrame containing, rounded up float columns.
        """
        # Assigning data to target dataframe
        target_df = self.data            
        # Detecting list of float columns on target dataset
        float_columns =[col for col, d_type in target_df._column_names_and_types if d_type in ["float", "decimal.Decimal"]]

        if len(float_columns) == 0:
            cols = target_df.columns
            # Doing reset index to get index column
            df = target_df.to_pandas().reset_index()

            # Returning the dataframe with cols
            # to avoid extra columns generated by reset_index()
            return df[cols]
        # storing the column details for round up in data transformation dictionary
        self.data_transform_dict["round_columns"] = float_columns
        # Extracting accumulate columns
        accumulate_columns = self._extract_list(target_df.columns,float_columns)
        # Performing rounding up on target column upto 4 precision digit
        fit_params = {
            "data" : target_df,
            "target_columns" : float_columns,
            "precision_digit" : 4,
            "accumulate" : accumulate_columns,
            "persist" : True}

        # Disabling print if persist is True by default
        if not self.volatile and not self.persist:
            fit_params["display_table_name"] = False
       
        if self.volatile:
            fit_params["volatile"] = True
            fit_params["persist"] = False

        transform_output = RoundColumns(**fit_params).result
        self.data_mapping['round_columns_data'] = transform_output._table_name
        if not self.volatile and not self.persist:
            # Adding transformed data containing table to garbage collector
            GarbageCollector._add_to_garbagecollector(transform_output._table_name)
        cols = transform_output.columns
        df = transform_output.to_pandas().reset_index()
        df = df[cols]
        return df