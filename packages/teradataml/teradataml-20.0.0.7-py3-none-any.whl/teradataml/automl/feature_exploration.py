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

# Python Libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math

# Teradata libraries
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml import ColumnSummary, CategoricalSummary, GetFutileColumns
from teradataml import OutlierFilterFit, OutlierFilterTransform
from teradataml import OrdinalEncodingFit, OrdinalEncodingTransform
from teradataml.hyperparameter_tuner.utils import _ProgressBar
from teradataml.common.messages import Messages, MessageCodes
from teradataml import display as dp
from teradataml.utils.validators import _Validators
from teradataml.common.utils import UtilFuncs
from teradataml.common.garbagecollector import GarbageCollector

def _is_terminal():
    """
    DESCRIPTION:
        Common Function detects whether code is running in
        terminal/console or IPython supported environment.

    RETURNS:
        bool.
    """
    if not hasattr(_is_terminal, 'ipython_imported'):
        try:
            # Check IPython environment
            __IPYTHON__
            # Check if IPython library is installed
            from IPython.display import display, HTML
            _is_terminal.ipython_imported = True
        except (NameError, ImportError):
            # If error, then terminal
            _is_terminal.ipython_imported = False

    return not _is_terminal.ipython_imported

# # conditional import
if not _is_terminal():
    from IPython.display import display, HTML

class _FeatureExplore:
    
    def __init__(self,
                 data=None,
                 target_column=None,
                 custom_data=None,
                 verbose=0,
                 task_type='regression',
                 fraud=False,
                 churn=False,
                 cluster=False,
                 **kwargs):
        """
        DESCRIPTION:
            Internal function initializes the data, target column for feature exploration.
         
        PARAMETERS:  
            data:
                Required Argument.
                Specifies the input teradataml DataFrame for feature exploration.
                Types: teradataml Dataframe
            
            target_column:
                Required Arugment.
                Set to None for Clustering
                Specifies the name of the target column in "data".
                Types: str

            custom_data:
                Optional Argument.
                Specifies json object containing user customized input.
                Types: json object

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
                Optional Argument.
                Specifies the task type of the data.
                Default Value: 'regression'
                Permitted Values:
                    * 'regression'
                    * 'classification'
                Types: str

            fraud:
                Optional Argument.
                Specifies whether to apply fraud detection techniques.
                Default Value: False
                Types: bool

            churn:
                Optional Argument.
                Specifies whether to apply churn prediction techniques.
                Default Value: False
                Types: bool

            cluster:
                Optional Argument.
                Specifies whether to apply clustering techniques.
                Default Value: False
                Types: bool
        """
        self.data = data
        self.target_column = target_column 
        self.verbose = verbose
        self.custom_data = custom_data
        self.data_transform_dict = {}
        self.data_types = {key: value for key, value in self.data._column_names_and_types}
        self.terminal_print = _is_terminal()
        self.style = self._common_style()
        self.task_type = task_type
        
        self.fraud = fraud
        self.churn = churn
        self.cluster = cluster

    def _exploration(self,
                     **kwargs):
        """
        DESCRIPTION:
            Internal function performs following operations:
                1. Column summary of columns of the dataset
                2. Statistics of numeric columns of the dataset
                3. Categorical column summary
                4. Futile columns in the dataset
                5. Target column distribution, not applicable for Clustering task_type
                6. Outlier Percentage in numeric columns of the dataset
                7. Heatmap of Numerical Features
                8. Boxplots of Feature Distribution
                9. Countplot of Categorical features
                10.Scatterplot for selected features for Clustering task_type
        """
        numerical_columns = []
        categorical_columns= []
        date_column_list = []

        aml_phases = kwargs.get('automl_phases', None)
        self._display_heading(phase=0,
                              automl_phases=aml_phases)
        self._display_msg(msg='Feature Exploration started ...')
        
        # Detecting numerical and categorical column
        for col, d_type in self.data._column_names_and_types:
            if d_type in ['int','float']:
                numerical_columns.append(col)
            elif d_type in ['str']:
                categorical_columns.append(col)
            elif d_type in ['datetime.date','datetime.datetime']:
                date_column_list.append(col)

        # Display initial Count of data
        self._display_msg(msg = '\nData Overview:', show_data=True)
        print(f"Total Rows in the data: {self.data.shape[0]}\n"\
              f"Total Columns in the data: {self.data.shape[1]}")
        
        # Displaying date columns
        if len(date_column_list)!=0:
            self._display_msg(msg='Identified Date Columns:',
                              data=date_column_list)
        
        # Column Summary of each feature of data
        # such as null count, datatype, non null count
        self._column_summary()
        
        # Displays statistics such as mean/median/mode
        self._statistics()
        
        # Categorcial Summary and futile column detection
        if len(categorical_columns) != 0:
            categorical_obj = self._categorical_summary(categorical_columns)
            self._futile_column(categorical_obj)

        if not self.cluster:
            # Plot a graph of target column
            self._target_column_details()
        
        
        # Displays outlier percentage 
        if self.fraud or self.churn:
            outlier_method = "percentile"
            df = self._outlier_detection(numerical_columns, outlier_method)
        else:
            outlier_method = "Tukey"
            df = self._outlier_detection(outlier_method, numerical_columns)

        
        if self.fraud or self.churn or self.cluster:
            # Boxplots and Heatmap for feature distribution by target column
            self._boxplot_heatmap()
                
            # Countplots for feature distribution by target column
            self._countplot_categorical_distribution()   
        if self.cluster:
            self._scatter_plot()
            
    def _statistics(self):     
        """
        DESCRIPTION:
            Internal function displays the statistics of numeric columns such mean, mode, median.
        """
        # Statistics of numerical columns
        self._display_msg(msg='\nStatistics of Data:',
                          data=self.data.describe(),
                          show_data=True)
       
    def _column_summary(self):       
        """
        DESCRIPTION:
            Internal function displays the column summary of categorical column such as 
            datatype, null count, non null count, zero count.
        """
        dp.max_rows = self.data.shape[1]
        # Column Summary of all columns of dataset
        obj = ColumnSummary(data=self.data,
                            target_columns=self.data.columns)
        self._display_msg(msg='\nColumn Summary:',
                          data=obj.result,
                          show_data=True)
        dp.max_rows = 10
               
    def _categorical_summary(self, 
                             categorical_columns=None):
        """
        DESCRIPTION:
            Internal function display the categorical summary of categorical column such count, distinct values.

        PARAMETERS:
            categorical_columns:
                Required Argument.
                Specifies the categorical columns.
                Types: str or list of strings (str)
        
        RETURNS:
            Instance of ColumnSummary.
        """
        self._display_msg(msg='\nCategorical Columns with their Distinct values:',
                          show_data=True)
        
        # Categorical Summary of categorical columns
        obj = CategoricalSummary(data=self.data,
                                 target_columns=categorical_columns)
        
        catg_obj = obj.result[obj.result['DistinctValue'] != None]
        print("{:<25} {:<10}".format("ColumnName", "DistinctValueCount"))
        for col in categorical_columns:
            dst_val = catg_obj[catg_obj['ColumnName'] == col].size//3
            print("{:<25} {:<10}".format(col, dst_val))
        
        return obj
    
    def _futile_column(self, 
                       categorical_obj):
        """
        DESCRIPTION:
            Internal function detects the futile columns.

        PARAMETERS:
            categorical_obj:
                Required Argument.
                Specifies the instance of CategoricalSummary for futile column detection.
                Types: Instance of CategoricalSummary     
        """
        # Futile columns detection using categorical column object
        gfc_out = GetFutileColumns(data=self.data,
                                   object=categorical_obj,
                                   category_summary_column="ColumnName",
                                   threshold_value=0.7)
        
        # Extracts the futile column present in the first column
        f_cols = [i[0] for i in gfc_out.result.itertuples()]

        if len(f_cols) == 0:
            self._display_msg(inline_msg='\nNo Futile columns found.',
                              show_data=True)
        else:
            self._display_msg(msg='\nFutile columns in dataset:',
                              data=gfc_out.result,
                              show_data=True)

    def _target_column_details(self,
                               plot_data=None):
        """
        DESCRIPTION:
            Internal function displays the target column distribution of Target column/ Response column.
            
        PARAMETERS:
            plot_data:
                Optional Argument.
                Specifies the input teradataml DataFrame for plotting distribution.
                Types: teradataml Dataframe
        """
        if self._check_visualization_libraries() and not _is_terminal():
            import matplotlib.pyplot as plt
            import seaborn as sns
            if plot_data is None:
                target_data = self.data.select([self.target_column]).to_pandas()
            else:
                target_data = plot_data[[self.target_column]]
            self._display_msg(msg='\nTarget Column Distribution:',
                              show_data=True)
            plt.figure(figsize=(8, 6)) 
            # Ploting a histogram for target column
            plt.hist(target_data, bins=10, density=True, edgecolor='black')
            plt.xlabel(self.target_column)
            plt.ylabel('Density')
            plt.show()

    def _countplot_categorical_distribution(self, plot_data=None, top_n=20, max_unique_threshold=50):
        """
        DESCRIPTION:
            Function to plot count plots for categorical features based on the target column.
            Limits the number of unique categories to avoid messy visuals.

        PARAMETERS:
            plot_data: 
                Optional Argument.
                Specifies the input teradataml DataFrame for plotting distribution.
                Default Value: None. It will use entire dataset passed for training.
                Types: teradataml Dataframe

            top_n:
                Optional Argument.
                Maximum number of categories to display per feature.
                Default Value: 20
                Types: int

            max_unique_threshold:
                Optional Argument.
                Only plot features with unique values below this threshold.
                Default Value: 50
                Types: int
        """
        if self._check_visualization_libraries() and not _is_terminal():
            import matplotlib.pyplot as plt
            import seaborn as sns

            # Prepare data
            if plot_data is None:
                data = self.data.to_pandas().reset_index()
            else:
                data = plot_data

            target_column = self.target_column

            # Select categorical features
            categorical_features = data.select_dtypes(include=['object', 'category']).columns

            if not self.cluster:
                categorical_features = [col for col in categorical_features if col != target_column]

            # Filter categorical features based on unique value threshold
            categorical_features = [col for col in categorical_features if data[col].nunique() <= max_unique_threshold]

            if len(categorical_features) == 0:
                print("No categorical columns found with unique values within the threshold.")
                return

            self._display_msg(msg='\nCategorical Feature Distributions by Target Column (Count Plots):',
                              show_data=False)

            for feature in categorical_features:
                plt.figure(figsize=(10, 6))

                # Get value counts and filter top N categories
                value_counts = data[feature].value_counts()

                top_categories = value_counts.nlargest(top_n).index.tolist()

                # Remove duplicates while preserving order
                top_categories = list(dict.fromkeys(top_categories))

                # Replace less frequent categories with "Other"
                data[feature] = data[feature].apply(lambda x: x if x in top_categories else "Other")


                # Generate count plot
                if not self.cluster:
                    cntplot = sns.countplot(data=data, x=feature, hue=target_column, order=top_categories)
                else:
                    cntplot = sns.countplot(data=data, x=feature, order=top_categories)
                for p in cntplot.patches:
                    height = p.get_height()
                    if height > 0:  # Only display if height is greater than 0
                        cntplot.annotate(f'{int(height)}',
                                         (p.get_x() + p.get_width() / 2, height),
                                         ha='center', va='bottom', fontsize=10, fontweight='bold')


                if not self.cluster:
                    plt.title(f"Distribution of {feature} by {target_column}")
                else:
                    plt.title(f"Distribution of {feature}")
                plt.xlabel(feature)
                plt.ylabel("Count")
                plt.xticks(rotation=45, ha='right')  # Improve label visibility
                if not self.cluster:
                    plt.legend(title=target_column)
                plt.tight_layout()
                plt.show()
   
    def _correlation(self, data, threshold=0.1, max_features=10, min_features=2):
        """
        DESCRIPTION:
            Function to calculate the correlation values between features.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame for correlation analysis.
                Types: pandas DataFrame
                
            threshold:
                Optional Argument.
                Specifies the minimum correlation threshold for feature selection.
                Default Value: 0.1
                Types: float
                
            max_features:
                Optional Argument.
                Specifies the maximum number of features to select.
                Default Value: 10
                Types: int
                
            min_features:
                Optional Argument.
                Specifies the minimum number of features to select as fallback.
                Default Value: 2
                Types: int
        """
        import numpy as np

        numerical_features = data.select_dtypes(include=['float64', 'int64']).columns

        # For AutoML, exclude target_column from numerical features
        if not self.cluster and self.target_column in numerical_features:
            numerical_features = [col for col in numerical_features if col != self.target_column]

        total_numerical_features = len(numerical_features)

        if self.cluster:
            # Clustering: feature vs feature correlation
            corr_matrix = data[numerical_features].corr()
            # Extract upper triangle without diagonal
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            corr_vals = corr_matrix.where(mask).stack().reset_index()
            corr_vals.columns = ['Feature1', 'Feature2', 'Correlation']
            corr_vals['Abs_Correlation'] = corr_vals['Correlation'].abs()
            corr_vals = corr_vals.sort_values(by='Abs_Correlation', ascending=False)

            filtered = corr_vals[corr_vals['Abs_Correlation'] > threshold].head(max_features)
            selection_criteria = "Top Correlated Feature Pairs"

            if len(filtered) < 2:
                filtered = corr_vals.head(min(2, len(corr_vals)))
                selection_criteria = f"Top {min(2, len(corr_vals))} Correlated Feature Pairs (Fallback)"

            # Merge unique features from pairs
            selected_features = list(set(filtered['Feature1'].tolist() + filtered['Feature2'].tolist()))
            selected_features = selected_features[:max_features]  # restrict total features
            corr_matrix = data[selected_features].corr()
            
            return filtered, selected_features, corr_matrix, selection_criteria
        else:
            # AutoML: correlation with target column
            correlation_values = data[numerical_features].corrwith(data[self.target_column])
            correlation_df = correlation_values.reset_index()
            correlation_df.columns = ['Feature', 'Correlation']
            correlation_df['Abs_Correlation'] = correlation_df['Correlation'].abs()
            correlation_df = correlation_df.sort_values(by='Abs_Correlation', ascending=False)

            filtered = correlation_df[correlation_df['Abs_Correlation'] > threshold].head(max_features)
            selection_criteria = "Features above threshold correlation with target"

            if len(filtered) < 2:
                filtered = correlation_df.head(min(min_features, total_numerical_features))
                selection_criteria = f"Top {min(min_features, total_numerical_features)} Correlated Features (Fallback)"

            selected_features = filtered['Feature'].tolist() + [self.target_column]
            selected_features = list(dict.fromkeys(selected_features))  # preserve order, remove dup
            corr_matrix = data[selected_features].corr()
        
            return selected_features, corr_matrix, selection_criteria

    def _boxplot_heatmap(self, plot_data=None):
        """
        DESCRIPTION:
            Internal function to display heatmap and boxplots of selected numerical features.
            Handles both AutoML (feature vs target) and Clustering (feature vs feature).

        Parameters:
            plot_data:
                Optional Argument.
                Specifies the data to be plotted.
                Default Value: None. It will use entire dataset passed for training.
                Types: teradataml DataFrame.
        """
        if self._check_visualization_libraries() and not _is_terminal():
            import matplotlib.pyplot as plt
            import seaborn as sns
            import numpy as np
            import pandas as pd

            # Get DataFrame
            if plot_data is not None:
                data = plot_data.to_pandas().reset_index()
            else:
                # Perform ordinal encoding if needed for classification
                if not self.cluster and self.data_types.get(self.target_column) in ['str']:
                    self._ordinal_encoding([self.target_column])
                data = self.data.to_pandas().reset_index()

            if not self.cluster:
                # Get selected features and correlation matrix
                selected_features, corr_matrix, selection_criteria = self._correlation(data=data)
            else:
                filtered, selected_features, corr_matrix, selection_criteria = self._correlation(data=data)

            # Display heatmap
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=0)
            plt.figure(figsize=(8, 6))
            sns.heatmap(corr_matrix, mask=mask, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
            plt.title("Heatmap of Selected Features")
            plt.show()
            
            num_features = len(selected_features)
            self._display_msg(msg=f'\nNumber of features selected for Boxplots: {num_features}', show_data=False)
            self._display_msg(msg=f'\nSelection Criteria: {selection_criteria}', show_data=False)
            self._display_msg(msg=f'\nSelected Features: {", ".join(selected_features)}', show_data=False)
            self._display_msg(msg='\nBoxplots:', show_data=False)

            if self.cluster:
                num_plots = len(filtered)
                cols = 2 if num_plots > 1 else 1
                rows = (num_plots + cols - 1) // cols
                
                fig, axes = plt.subplots(rows, cols, figsize=(12, rows * 4))
                axes = axes.flatten() if len(filtered) > 1 else [axes]

                for i, (idx, row) in enumerate(filtered.iterrows()):
                    if i >= len(axes):
                        break  # prevent IndexError if more data than axes

                    feature_x, feature_y = row["Feature1"], row["Feature2"]
                    
                    x_unique = data[feature_x].nunique()
                    x = data[feature_x]
                    if x_unique > 20:
                        x = pd.qcut(x, q=10, duplicates='drop')
                    
                    sns.boxplot(x=x, y=data[feature_y], ax=axes[i])
                    axes[i].set_title(f"{feature_y} vs {feature_x}")
                    axes[i].set_xlabel(feature_x)
                    axes[i].set_ylabel(feature_y)
                    axes[i].tick_params(axis='x', rotation=45)
            else:
                # Prepare boxplot layout
                num_features = len(selected_features)
                cols = 2 if num_features > 1 else 1
                rows = max((num_features // 2) + (num_features % 2),1)
                
                rows = max(rows, 1)

                fig, axes = plt.subplots(rows, cols, figsize=(12, rows * 4))
                axes = axes.flatten() if num_features > 1 else [axes]
                # AutoML: Plot boxplot of feature vs target column
                for i, feature in enumerate(selected_features):
                    if feature != self.target_column:
                        sns.boxplot(x=data[self.target_column], y=data[feature], ax=axes[i])
                        axes[i].set_title(f"{feature}")
                        axes[i].set_xlabel(self.target_column)
                        axes[i].set_ylabel(feature)

            plt.tight_layout()
            plt.show()

    def _scatter_plot(self, plot_data=None, max_selected_pairs=10, threshold=0.1):
        """
        DESCRIPTION:
            Internal function to display scatterplots of selected numerical features.
            Handles Clustering (feature vs feature).
            
        PARAMETERS:
            plot_data:
                Optional Argument.
                Specifies the input teradataml dataFrame for plotting scatter plots.
                Default Value: None. It will use entire dataset passed for training.
                Types: teradataml DataFrame
                
            max_selected_pairs:
                Optional Argument.
                Specifies the maximum number of feature pairs to select for scatter plots.
                Default Value: 10
                Types: int
                
            threshold:
                Optional Argument.
                Specifies the minimum correlation threshold for feature pair selection.
                Default Value: 0.1
                Types: float
        """
        if self._check_visualization_libraries() and not _is_terminal():
            import matplotlib.pyplot as plt
            import seaborn as sns
            import numpy as np

            # Load data
            data = plot_data.to_pandas().reset_index() if plot_data is not None else self.data.to_pandas().reset_index()

            # Select numerical features
            numerical_features = data.select_dtypes(include=['float64', 'int64']).columns
            if len(numerical_features) < 2:
                print("Not enough numerical features for scatter plots.")
                return

            # Compute correlation matrix
            corr_matrix = data[numerical_features].corr()

            # Extract upper triangle (excluding diagonal)
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            corr_vals = corr_matrix.where(mask).stack().reset_index()
            corr_vals.columns = ['Feature1', 'Feature2', 'Correlation']
            corr_vals['Abs_Correlation'] = corr_vals['Correlation'].abs()

            # Sort and filter top pairs
            corr_vals = corr_vals.sort_values(by='Abs_Correlation', ascending=False)
            filtered = corr_vals[corr_vals['Abs_Correlation'] > threshold].head(max_selected_pairs)

            if len(filtered) < 2:
                filtered = corr_vals.head(min(2, len(corr_vals)))

            if len(filtered) == 0:
                print("No correlated pairs found above threshold.")
                return

            self._display_msg(msg=f"\nScatter Plots for Top Correlated Feature Pairs:", show_data=False)

            # Plot scatter plots
            for _, row in filtered.iterrows():
                feature_x, feature_y = row["Feature1"], row["Feature2"]

                plt.figure(figsize=(6, 4))
                sns.scatterplot(x=data[feature_x], y=data[feature_y], alpha=0.3)
                plt.xlabel(feature_x)
                plt.ylabel(feature_y)
                plt.title(f"Scatter Plot: {feature_x} vs {feature_y} (Corr: {row['Correlation']:.2f})")
                plt.tight_layout()
                plt.show()
  
    def _ordinal_encoding(self,
                          ordinal_columns):
        """
        DESCRIPTION:
            Function performs the ordinal encoding to categorical columns or features in the dataset.

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
        
        if len(ordinal_columns) == 1 and ordinal_columns[0] == self.target_column:
            self.target_label = ord_fit_obj

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
        new_lst = list(set(list1) - set(list2))
        return new_lst

    def _get_generic_parameters(self,
                                func_indicator=None,
                                param_name=None):
        """
        DESCRIPTION:
            Function to get generic parameters.
        
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
        volatile = self.volatile
        persist = self.persist
        if self.custom_data is not None and self.custom_data.get(func_indicator, False):
            volatile = self.custom_data[param_name].get("volatile", False)
            persist = self.custom_data[param_name].get("persist", False)

        return (volatile, persist)    

    def _check_visualization_libraries(self):
        """
        DESCRIPTION:
            Internal function Checks the availability of data visualization libraries.
            
        RETURNS:
            Boolean, True if data visualization libraries are available. Otherwise return False.
        """
        
        # Conditional import
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
        except ImportError:
            print("Install seaborn and matplotlib libraries to visualize the data.")
            return False
        
        return True
        
    def _outlier_detection(self, 
                           outlier_method,
                           column_list,
                           lower_percentile=None,
                           upper_percentile=None):
        """
        DESCRIPTION:
            Function detects the outlier in numerical column and display thier percentage.

        PARAMETERS:
            outlier_method:
                Required Argument.
                Specifies the outlier method required for outlier detection.
                Types: str

            column_list:
                Required Argument.
                Specifies the numeric columns for outlier percentage calculation.
                Types: str or list of strings (str)
                
            lower_percentile:
                Optional Argument.
                Specifies the lower percentile value for outlier detection in case of percentile method.
                Types: float
                   
            upper_percentile:
                Optional Argument.
                Specifies the upper percentile value for outlier detection in case of percentile method.
                Types: float
        
        RETURNS:
            Pandas DataFrame containing, column name with outlier percentage.

        """
        # Removing target column from the list of columns
        column_list = [col for col in column_list if col != self.target_column]

        # Performing outlier fit on the data for replacing outliers with NULL value
        fit_params = {
            "data" : self.data,
            "target_columns" : column_list,
            "outlier_method" : outlier_method,
            "lower_percentile" : lower_percentile,
            "upper_percentile" : upper_percentile,
            "replacement_value" : 'NULL'
        }
        OutlierFilterFit_out = OutlierFilterFit(**fit_params)
        transform_params = {
            "data" : self.data,
            "object" : OutlierFilterFit_out.result
        }
        # Performing outlier transformation on each column
        OutlierTransform_obj = OutlierFilterTransform(**transform_params)
        
        # Column summary of each column of the data
        fit_params = {
            "data" : OutlierTransform_obj.result,
            "target_columns" : column_list
        }
        colSummary = ColumnSummary(**fit_params)

        null_count_expr = colSummary.result.NullCount
        non_null_count_expr = colSummary.result.NonNullCount
        
        # Calculating outlier percentage
        df = colSummary.result.assign(True, 
                                      ColumnName = colSummary.result.ColumnName, 
                                      OutlierPercentage = (null_count_expr/(non_null_count_expr+null_count_expr))*100)
    
        # Displaying non-zero containing outlier percentage for columns
        df = df[df['OutlierPercentage']>0]
        if self.verbose > 0:
            print(" "*500, end='\r')
            if df.shape[0] > 0:
                self._display_msg(msg='Columns with outlier percentage :-',
                                  show_data=True)
                print(df)
            else:
                print("\nNo outlier found!")
            
        return df
    
    def _common_style(self):
        """
        DESCRIPTION:
            Internal Function sets the style tag for HTML.
        
        RETURNS:
            string containing style tag.
        
        """
        style = '''
            <style>
                .custom-div {
                    background-color: lightgray;
                    color: #000000;
                    padding: 10px;
                    border-radius: 8px;
                    box-shadow: 0 3px 4px rgba(0, 0, 0, 0.2);
                    margin-bottom: 10px;
                    text-align: center;
                }
            </style>
        '''
        return style
    
    def _display_heading(self,
                         phase=0,
                         progress_bar=None,
                         **kwargs):
        """
        DESCRIPTION:
            Internal function to print the phase of AutoML that
            completed in green color.
            
        PARAMETERS:
            phase:
                Optional Argument.
                Specifies the phase of automl that completed.
                Types: int
        
            progress_bar:
                Optional Argument.
                Specifies the _ProgressBar object.
                Types: object (_ProgressBar)
        
        RETURNS:
            None.
        """
        phases = ["1. Feature Exploration ->", " 2. Feature Engineering ->",
                 " 3. Data Preparation ->", " 4. Model Training & Evaluation"]
        # Phases of automl
        if kwargs.get('automl_phases', None) is not None:
            steps = kwargs.get('automl_phases')
        else:
            steps = phases

        # Check verbose > 0
        if self.verbose > 0:
            
            # Check if code is running in IPython enviornment
            if not self.terminal_print:
                # Highlightedt phases of automl
                highlighted_steps = "".join(steps[:phase])
                
                # Unhighlighted phases of automl
                unhighlighted_steps = "".join(steps[phase:])
                
                # Combining highlighted and unhighlighted phases
                msg = self.style + f'<br><div class="custom-div"><h3><span style="color: green;">{highlighted_steps}</span>{unhighlighted_steps}<center></h3></center></div>'
                # Displaying the msg
                if progress_bar is not None:
                    progress_bar.update(msg=msg,
                                        progress=False,
                                        ipython=True)
                else:
                    display(HTML(msg))
            else:
                try:
                    # Try to import colorama if not already imported
                    from colorama import Fore, Style, init
                    # initalize the color package
                    init()
                    
                    # Highlight the phases of automl
                    highlighted_steps = "".join([Fore.GREEN + Style.BRIGHT + step + Style.RESET_ALL for step in steps[:phase]])
                    
                    # Unhighlighted the phases of automl
                    unhighlighted_steps = "".join(steps[phase:])
                    
                    # Combining highlighted and unhighlighted phases
                    msg = f'{highlighted_steps}{unhighlighted_steps}'
                    
                except ImportError:    
                    msg = "".join(step for step in steps)
                
                if progress_bar is not None:
                    progress_bar.update(msg=msg,
                                        progress=False)
                else:
                    print(msg)
                
    def _display_msg(self,
                     msg=None, 
                     progress_bar=None,
                     inline_msg=None,
                     data=None,
                     col_lst=None,
                     show_data=False):
        """
        DESCRIPTION:
            Internal Function to print statement according to
            environment.
        
        PARAMETERS:
            msg:
                Optional Argument.
                Specifies the message to print.
                Types: str
            
            progress_bar:
                Optional Argument.
                Specifies the _ProgressBar object.
                Types: object (_ProgressBar)
                
            inline_msg:
                Optional Argument.
                Specifies the additional information to print.
                Types: str
            
            data:
                Optional Argument.
                Specifies the teradataml dataframe to print.
                Types: teradataml DataFrame
            
            col_lst:
                Optional Argument.
                Specifies the list of columns.
                Types: list of str/int/data.time
            
            show_data:
                Optional Argument.
                Specifies whether to print msg/data when verbose<2.
                Default Value: False
                Types: bool
        
        RETURNS:
            None.
                
        """
        # If verbose level is set to 2
        if self.verbose == 2:
            # If a progress bar is provided
            if progress_bar:
                # If a message is provided
                if msg:
                    # Update the progress bar with the message and either the column list or data (if they are not None)
                    progress_bar.update(msg=msg, data=col_lst if col_lst else data if data is not None else None, 
                                        progress=False, 
                                        ipython=not self.terminal_print)
                    # Displaying shape of data
                    if data is not None:
                        progress_bar.update(msg=f'{data.shape[0]} rows X {data.shape[1]} columns',
                                            progress=False,
                                            ipython=not self.terminal_print)
                # If an inline message is provided instead
                elif inline_msg:
                    # Update the progress bar with the inline message
                    progress_bar.update(msg=inline_msg, progress=False)
            # If no progress bar is provided
            else:
                # If a message is provided
                if msg:
                    # Print the message
                    print(f"{msg}")
                    # If a column list is provided
                    if col_lst:
                        # Print the column list
                        print(col_lst)
                    # If data is provided instead
                    elif data is not None:
                        # Print the data if terminal_print is True, else display the data
                        print(data) if self.terminal_print else display(data)
                # If an inline message is provided instead
                elif inline_msg:
                    # Print the inline message
                    print(f'{inline_msg}')
            # Exit the function after handling verbose level 2
            return

        # If verbose level is more than 0 and show_data is True
        if self.verbose > 0 and show_data:
            # If a progress bar and a message are provided
            if progress_bar and msg:
                # Update the progress bar with the message and data (if data is not None)
                progress_bar.update(msg=msg, data=data if data is not None else None, 
                                    progress=False, ipython=not self.terminal_print)
            # If no progress bar is provided
            else:
                # If a message is provided
                if msg:
                    # Print the message if terminal_print is True, else display the message
                    print(f'{msg}') if self.terminal_print else display(HTML(f'<h4>{msg}</h4>'))
                # If data is provided
                if data is not None:
                    # Print the data if terminal_print is True, else display the data
                    print(data) if self.terminal_print else display(data)

    @staticmethod
    def _visualize(data, 
                   target_column, 
                   plot_type=["target"],
                   length=10, 
                   breadth=8, 
                   max_features=10,
                   columns=None,
                   problem_type=None):
        """
        DESCRIPTION:
            Internal function to visualize the data using various plots such as heatmap, 
            pair plot, density, count plot, box plot, and target distribution.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame for plotting.
                Types: teradataml Dataframe

            target_column:
                Required Argument.
                Specifies the name of the target column in "data".
                Types: str

            plot_type:
                Optional Argument.
                Specifies the type of plot to be displayed.
                Default Value: "target"
                Permitted Values: 
                    * "heatmap": Displays a heatmap of feature correlations.
                    * "pair": Displays a pair plot of features.
                    * "density": Displays a density plot of features.
                    * "count": Displays a count plot of categorical features.
                    * "box": Displays a box plot of numerical features.
                    * "target": Displays the distribution of the target variable.
                    * "all": Displays all the plots.
                Types: str, list of str

            length:
                Optional Argument.
                Specifies the length of the plot.
                Default Value: 10
                Types: int

            breadth:
                Optional Argument.
                Specifies the breadth of the plot.
                Default Value: 8
                Types: int

            columns:
                Optional Argument.
                Specifies the column names to be used for plotting.
                Types: str or list of string

            max_features:
                Optional Argument.
                Specifies the maximum number of features to be used for plotting.
                Default Value: 10
                Note:
                    * It applies separately to categorical and numerical features.
                Types: int

            problem_type:
                Optional Argument.
                Specifies the type of problem.
                Permitted Values:
                    * 'regression'
                    * 'classification'
                Types: str
            
        RETURNS:
            None

        RAISES:
            TeradataMlException, ValueError, TypeError

        EXAMPLES:
            >>> _FeatureExplore._visualize(data=data,
                                           target_column="target",
                                           plot_type="heatmap",
                                           length=10,
                                           breadth=8,
                                           max_features=10,
                                           columns=["feature1", "feature2"],
                                           problem_type="regression")
        """
        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["data", data, False, (DataFrame)])
        arg_info_matrix.append(["target_column", target_column, False, (str)])
        arg_info_matrix.append(["plot_type", plot_type, True, (str, list), True, ["heatmap", "pair", "all",
                                                                                  "density", "count", "box", "target"]])
        arg_info_matrix.append(["length", length, True, (int)])
        arg_info_matrix.append(["breadth", breadth, True, (int)])
        arg_info_matrix.append(["max_features", max_features, True, (int)])
        arg_info_matrix.append(["problem_type", problem_type, True, (str), True, ["regression", "classification"]])
        arg_info_matrix.append(["columns", columns, True, (str, list)])

        # Validate argument types
        _Validators._validate_function_arguments(arg_info_matrix)

        # Validate that data has the required columns
        _Validators._validate_dataframe_has_argument_columns(target_column, "target_column", data, "data")
        _Validators._validate_dataframe_has_argument_columns(columns, "columns", data, "data")

        # Convert data to pandas DataFrame if it's a teradataml DataFrame
        cols = data.columns
        data = data.to_pandas().reset_index()
        # avoiding the index column
        data = data[cols]

        available_plots = ["target", "density", "count", "box", "pair",  "heatmap"]

        # if target_column is str
        if isinstance(target_column, str):
            data[target_column] = data[target_column].astype("category").cat.codes

        if plot_type == "all":
            plot_type = available_plots
        else:
            plot_type = UtilFuncs._as_list(plot_type)

        # Identify numerical and categorical columns
        numerical_features = data.select_dtypes(include=['number']).columns.drop(target_column).tolist()
        categorical_features = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Handle selected_columns input
        if columns:
            selected_columns = UtilFuncs._as_list(columns)
            selected_num_features = [col for col in selected_columns if col in numerical_features][:max_features]
            selected_cat_features = [col for col in selected_columns if col in categorical_features][:max_features]
        else:
            # Compute correlation with target and select top correlated numerical features
            if target_column in data.columns and pd.api.types.is_numeric_dtype(data[target_column]):
                selected_num_features = (
                    data[numerical_features]
                    .corrwith(data[target_column])
                    .abs()
                    .nlargest(max_features)
                    .index.tolist()
                )
            else:
                selected_num_features = numerical_features[:max_features]

            # Select top categorical features based on appearance
            selected_cat_features = categorical_features[:max_features]

        irrelevant_plot = []

        # Sort plot_type based on the order in available_plots
        # display univariate plots first, then bivariate, and finally multivariate
        sorted_plot_type = sorted(plot_type, key=lambda x: available_plots.index(x.lower()))

        for plot in sorted_plot_type:
            # Target Distribution
            if plot.lower() == "target":
                msg = _FeatureExplore._target_distribution(data=data,
                                                           target_column=target_column,
                                                           problem_type=problem_type,
                                                           length=length,
                                                           breadth=breadth)
            # Density Plot (for numerical features) - Grid
            elif plot.lower() == "density":
                msg = _FeatureExplore._density_plot(data=data,
                                                    length=length,
                                                    breadth=breadth,
                                                    numerical_features=selected_num_features)
            # Count Plot (for categorical features) - Grid  
            elif plot.lower() == "count":
                msg = _FeatureExplore._count_plot(data=data,
                                                  length=length,
                                                  breadth=breadth,
                                                  categorical_features=selected_cat_features)
            # Box Plot (for numerical features) - Grid 
            elif plot.lower() == "box":
                msg = _FeatureExplore._box_plot(data=data,
                                                length=length,
                                                breadth=breadth,
                                                numerical_features=selected_num_features)
            # Scatter Plot / Pair Plot
            elif plot.lower() == "pair":
                msg = _FeatureExplore._pair_plot(data=data,
                                                    target_column=target_column,
                                                    length=length,
                                                    breadth=breadth,
                                                    numerical_features=selected_num_features,
                                                    categorical_features=selected_cat_features)
            # Heatmap 
            elif plot.lower() == "heatmap":
                msg = _FeatureExplore._heatmap(data=data,
                                               target_column=target_column,
                                               length=length,
                                               breadth=breadth,
                                               numerical_features=selected_num_features)
                
            if msg:
                irrelevant_plot.append(msg)

        if irrelevant_plot:
            for msg in irrelevant_plot:
                print(msg)

    @staticmethod
    def _heatmap(data,
                 target_column,
                 length=10,
                 breadth=8,
                 numerical_features=[]):
        """
        DESCRIPTION:
            Internal function to visualize the data using heatmap.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame for plotting.
                Types: pandas Dataframe

            target_column:
                Required Argument.
                Specifies the name of the target column in "data".
                Types: str

            length:
                Optional Argument.
                Specifies the length of the plot.
                Default Value: 10
                Types: int

            breadth:
                Optional Argument.
                Specifies the breadth of the plot.
                Default Value: 8
                Types: int

            numerical_features:
                Optional Argument.
                Specifies the list of numerical features to be plotted.
                Types: list of str

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> _FeatureExplore._heatmap(data=data,
                                         target_column="target",
                                         length=10,
                                         breadth=8,
                                         numerical_features=["feature1", "feature2"])

        """
        if len(numerical_features) >= 1:
            plt.figure(figsize=(length, breadth))
            sns.heatmap(data[numerical_features + [target_column]].corr(), annot=True, cmap="coolwarm")
            plt.title("Feature Correlation Heatmap")
            plt.show()
        else:
            return f"Plot type 'heatmap' is not applicable as no numerical features are available."
    
    @staticmethod
    def _pair_plot(data,
                      target_column,
                      length=10,
                      breadth=8,
                      numerical_features=[],
                      categorical_features=[]):
        """
        DESCRIPTION:
            Internal function to visualize the data using pair plot.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame for plotting.
                Types: pandas Dataframe

            target_column:
                Required Argument.
                Specifies the name of the target column in "data".
                Types: str

            length:
                Optional Argument.
                Specifies the length of the plot.
                Default Value: 10
                Types: int

            breadth:
                Optional Argument.
                Specifies the breadth of the plot.
                Default Value: 8
                Types: int

            numerical_features:
                Optional Argument.
                Specifies the list of numerical features to be plotted.
                Types: list of str

            categorical_features:
                Optional Argument.
                Specifies the list of categorical features to be plotted.
                Types: list of str

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> _FeatureExplore._pair_plot(data=data,
                                              target_column="target",
                                              length=10,
                                              breadth=8,
                                              numerical_features=["feature1", "feature2"])

        """
        if len(numerical_features) >= 1:
            pair = sns.pairplot(data[numerical_features + [target_column]], 
                      hue=target_column if target_column in categorical_features else None)

            # Add a centered title
            pair.figure.suptitle("pair Plot", fontsize=16, y=1.02)
            plt.show()
        else:
            return f"Plot type 'pair' is not applicable as no numerical features are available."

    @staticmethod
    def _density_plot(data,
                      length=10,
                      breadth=8,
                      numerical_features=[]):
        """
        DESCRIPTION:
            Internal function to visualize the data using density plot.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame for plotting.
                Types: pandas Dataframe

            length:
                Optional Argument.
                Specifies the length of the plot.
                Default Value: 10
                Types: int

            breadth:
                Optional Argument.
                Specifies the breadth of the plot.
                Default Value: 8
                Types: int

            numerical_features:
                Optional Argument.
                Specifies the list of numerical features to be plotted.
                Types: list of str

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> _FeatureExplore._density_plot(data=data,
                                              length=10,
                                              breadth=8,
                                              numerical_features=["feature1", "feature2"])

        """
        if len(numerical_features) >= 1:
            rows = math.ceil(len(numerical_features) / 3)
            fig, axes = plt.subplots(rows, 3, figsize=(length, breadth))
            axes = axes.flatten()
            fig.suptitle("Density plot", fontsize=14)

            for i, feature in enumerate(numerical_features):
                sns.kdeplot(data[feature], fill=True, color="green", alpha=0.6, ax=axes[i])
                
            # Hide any empty subplots
            for i in range(len(numerical_features), len(axes)):
                axes[i].axis('off')
                
            plt.tight_layout()
            plt.show()
            return None
        else:
           return f"Plot type 'density' is not applicable as no numerical features are available."
        
    @staticmethod
    def _target_distribution(data,
                             target_column,
                             problem_type=None,
                             length=10,
                             breadth=8):
        """
        DESCRIPTION:
            Function visualizes the target distribution.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame for plotting.
                Types: pandas Dataframe

            target_column:
                Required Argument.
                Specifies the name of the target column in "data".
                Types: str

            problem_type:
                Optional Argument.
                Specifies the type of problem.
                Permitted Values:
                    * 'regression'
                    * 'classification'
                Types: str

            length:
                Optional Argument.
                Specifies the length of the plot.
                Default Value: 10
                Types: int

            breadth:
                Optional Argument.
                Specifies the breadth of the plot.
                Default Value: 8
                Types: int

        """
        plt.figure(figsize=(length, breadth))
        # Categorical Target
        if (problem_type is None and data[target_column].nunique() <= 20) or \
            (problem_type and problem_type.lower() == 'classification'):
            sns.countplot(x=target_column, 
                          data=data, 
                          palette="coolwarm", 
                          hue=target_column, 
                          legend=False) 
        else:  
            # Numerical Target
            sns.histplot(data[target_column], kde=True, color="blue")
        plt.title("Target Distribution")
        plt.tight_layout()
        plt.show()


    @staticmethod
    def _count_plot(data,
                    length=10,
                    breadth=8,
                    categorical_features=[]):
        """
        DESCRIPTION:
            Internal function to visualize the data using count plot.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame for plotting.
                Types: pandas Dataframe

            length:
                Optional Argument.
                Specifies the length of the plot.
                Default Value: 10
                Types: int

            breadth:
                Optional Argument.
                Specifies the breadth of the plot.
                Default Value: 8
                Types: int

            categorical_features:
                Optional Argument.
                Specifies the list of categorical features to be plotted.
                Types: list of str

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> _FeatureExplore._count_plot(data=data,
                                           length=10,
                                           breadth=8,
                                           categorical_features=["feature1", "feature2"])
        """
        if len(categorical_features) >= 1:
            rows = math.ceil(len(categorical_features) / 3)
            fig, axes = plt.subplots(rows, 3, figsize=(length, rows * 5))
            axes = axes.flatten()
            fig.suptitle("Count plot", fontsize=14)

            for i, feature in enumerate(categorical_features):
                # Get top 20 most frequent categories
                top_categories = data[feature].value_counts().nlargest(25)

                # Plot only top 20 categories
                sns.barplot(x=top_categories.index, 
                            y=top_categories.values, 
                            hue=top_categories.index,
                            palette="coolwarm", 
                            legend=False,
                            ax=axes[i])

                # Rotate labels for readability
                axes[i].tick_params(axis='x', rotation=90)  

            # Hide empty subplots
            for i in range(len(categorical_features), len(axes)):
                axes[i].axis('off')

            # Adjust layout spacing
            plt.subplots_adjust(hspace=1.5, wspace=0.3)
            plt.show()
        else:
            return f"Plot type 'count' is not applicable as no categorical features are available."
        
    @staticmethod
    def _box_plot(data,
                  length=10,
                  breadth=8,
                  numerical_features=[]):
        """
        DESCRIPTION:
            Internal function to visualize the data using box plot.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input pandas DataFrame for plotting.
                Types: pandas Dataframe

            length:
                Optional Argument.
                Specifies the length of the plot.
                Default Value: 10
                Types: int

            breadth:
                Optional Argument.
                Specifies the breadth of the plot.
                Default Value: 8
                Types: int

            numerical_features:
                Optional Argument.
                Specifies the list of numerical features to be plotted.
                Types: list of str

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> _FeatureExplore._box_plot(data=data,
                                          length=10,
                                          breadth=8,
                                          numerical_features=["feature1", "feature2"])

        """
        if len(numerical_features) >= 1:
            rows = math.ceil(len(numerical_features) / 3)
            fig, axes = plt.subplots(rows, 3, figsize=(length, breadth))
            axes = axes.flatten()
            fig.suptitle("Box plot", fontsize=14)

            for i, feature in enumerate(numerical_features):
                # Removed the hue argument and passed only the feature to x
                sns.boxplot(y=data[feature], data=data, ax=axes[i], legend=False)
                # Adjust layout to prevent label overlap
                plt.tight_layout()  
        
            # Hide any empty subplots
            for i in range(len(numerical_features), len(axes)):
                axes[i].axis('off')

            plt.show()
        else:
            return f"Plot type 'box' is not applicable as no numerical features are available."