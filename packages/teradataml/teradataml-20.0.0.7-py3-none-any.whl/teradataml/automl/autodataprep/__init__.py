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

# External libraries
import pandas as pd

# Teradata libraries
from teradataml import db_drop_table
from teradataml.common.constants import AutoMLConstants as aml_const
from teradataml.common.messages import Messages, MessageCodes
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml.utils.validators import _Validators

# AutoML Internal libraries
from teradataml import AutoML, TeradataMlException

class AutoDataPrep(AutoML):
    def __init__(self,
                 task_type = "Default",
                 verbose = 0,
                 **kwargs):
        """
        DESCRIPTION:
            AutoDataPrep simplifies the data preparation process by automating the different aspects of 
            data cleaning and transformation, enabling seamless exploration, transformation, and optimization of datasets.

        PARAMETERS:
            task_type:
                Optional Argument.
                Specifies the task type for AutoDataPrep, whether to apply regression OR classification
                on the provided dataset. If user wants AutoDataPrep() to decide the task type automatically, 
                then it should be set to "Default".
                Default Value: "Default"
                Permitted Values: "Regression", "Classification", "Default"
                Types: str

            verbose:
                Optional Argument.
                Specifies the detailed execution steps based on verbose level.
                Default Value: 0
                Permitted Values: 
                    * 0: prints the progress bar.
                    * 1: prints the execution steps.
                    * 2: prints the intermediate data between the execution of each step.
                Types: int

            **kwargs:
                Specifies the additional arguments for AutoDataPrep. Below
                are the additional arguments:
                    custom_config_file:
                        Optional Argument.
                        Specifies the path of JSON file in case of custom run.
                        Types: str
                    
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

        RETURNS:
            Instance of AutoDataPrep.

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Notes:
            #     1. Get the connection to Vantage to execute the function.
            #     2. One must import the required functions mentioned in
            #        the example from teradataml.
            #     3. Function raises error if not supported on the Vantage
            #        user is connected to.

            # Load the example data.
            >>> load_example_data("teradataml", "titanic")
    
            # Create teradataml DataFrames.
            >>> titanic = DataFrame.from_table("titanic")
            
            # Example 1: Run AutoDataPrep for classification problem.
            # Scenario: Titanic dataset is used to predict the survival of passengers.
           
            # Create an instance of AutoDataPrep.
            >>> aprep_obj = AutoDataPrep(task_type="Classification", verbose=2)

            # Fit the data.
            >>> aprep_obj.fit(titanic, titanic.survived)
            
            # Retrieve the data after Auto Data Preparation.
            >>> datas = aprep_obj.get_data()
        
        """
        # Initialize the AutoML object
        super().__init__(task_type=task_type, 
                         verbose=verbose, 
                         **kwargs)

        # Setting the attrubutes for AutoDataPrep
        super().__setattr__("_auto_dataprep", True)
        super().__setattr__("model_list", [])
        super().__setattr__("_phases", ["1. Feature Exploration ->",
                                        "2. Feature Engineering ->",
                                        "3. Data Preparation"])
        super().__setattr__("_progressbar_prefix", 'Auto Data Prep:')

    def fit(self,
            data,
            target_column):
        """
        DESCRIPTION:
            Function to fit the data for Auto Data Preparation.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input data to be used for Auto Data Preparation.
                Types: DataFrame

            target_column:
                Required Argument.
                Specifies the target column to be used for Auto Data Preparation.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException, ValueError

        EXAMPLES:
            # Notes:
            #     1. Get the connection to Vantage to execute the function.
            #     2. One must import the required functions mentioned in
            #        the example from teradataml.
            #     3. Function raises error if not supported on the Vantage
            #        user is connected to.

            # Load the example data.
            >>> load_example_data("teradataml", "titanic")
    
            # Create teradataml DataFrames.
            >>> titanic = DataFrame.from_table("titanic")
            
            # Example 1: Run AutoDataPrep for classification problem.
            # Scenario: Titanic dataset is used to predict the survival of passengers.
           
            # Create an instance of AutoDataPrep.
            >>> aprep_obj = AutoDataPrep(task_type="Classification", verbose=2)

            # Fit the data.
            >>> aprep_obj.fit(titanic, titanic.survived)
        
        """
        # Fit the data using AutoML object
        super().fit(data, target_column)


    def get_data(self):
        """
        DESCRIPTION:
            Function to retrieve the data after Auto Data Preparation.

        RETURNS:
             Dictionary of DataFrames containing the data after Auto Data Preparation.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Notes:
            #     1. Get the connection to Vantage to execute the function.
            #     2. One must import the required functions mentioned in
            #        the example from teradataml.
            #     3. Function raises error if not supported on the Vantage
            #        user is connected to.

            # Load the example data.
            >>> load_example_data("teradataml", "titanic")
    
            # Create teradataml DataFrames.
            >>> titanic = DataFrame.from_table("titanic")
            
            # Example 1: Run AutoDataPrep for classification problem.
            # Scenario: Titanic dataset is used to predict the survival of passengers.
           
            # Create an instance of AutoDataPrep.
            >>> aprep_obj = AutoDataPrep(task_type="Classification", verbose=2)

            # Fit the data.
            >>> aprep_obj.fit(titanic, titanic.survived)
            
            # Retrieve the data after Auto Data Preparation.
            >>> datas = aprep_obj.get_data()
        """
        # Raise error if fit is not called before get_data
        _Validators._validate_dependent_method("get_data", "fit", self._is_fit_called)
        
        datas = {}
        for  key, val in self.table_name_mapping.items():
            datas[key] = DataFrame(val)

        return datas
    
    def deploy(self, table_name):
        """
        DESCRIPTION:
            Deploy the AutoDataPrep generated data to the database,
            i.e., saves the data in the database.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the name of the table to store the information
                of deployed datasets in the database.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException, ValueError

        EXAMPLES:
            # Create an instance of the AutoDataPrep.
            # Perform fit() operation on the AutoDataPrep object.
            # Deploy the data to the table.

            From teradataml import AutoDataPrep
            # Load the example data.
            >>> load_example_data("teradataml", "titanic")
            >>> titanic = DataFrame.from_table("titanic")

            # Create an instance of AutoDataPrep.
            >>> aprep_obj = AutoDataPrep(task_type="Classification", verbose=2)

            # Fit the data.
            >>> aprep_obj.fit(titanic, titanic.survived)

            # Deploy the data to the table.
            >>> aprep_obj.deploy("table_name")
        """

        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["table_name", table_name, True, (str), True])

        # Validating the arguments
        _Validators._validate_function_arguments(arg_info_matrix)

        # Raise Error if fit is not called before deploy
        _Validators._validate_dependent_method("deploy", "fit", self._is_fit_called)

        if self.table_name_mapping is not None and \
            isinstance(self.table_name_mapping, dict):

            tab_map = {}
            # If persist is False, then generate permanent table
            if not self.kwargs.get("persist", False):
                for key, val in self.table_name_mapping.items():
                    # Perist the data
                    per_name = self._create_per_result_table(prefix='{}_'.format(self.target_column),
                                                             persist_result_table=val)
                    # Store the table name mapping
                    tab_map[key] = per_name
            else:
                # Tables are already persisted
                tab_map = self.table_name_mapping
            data = pd.DataFrame(list(tab_map.items()), columns=['Feature_Selection_Method', 'Table_Name'])

            # Save the data to the database
            copy_to_sql(df= data, table_name=table_name, if_exists="replace")
            print("Data deployed successfully to the table: ", table_name)
            return

        # Raise error if data is not found or 
        # table_name_mapping is not a dictionary/ None
        err = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                   "'deploy' method", \
                                   "Data not found to deploy.")
        raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
    
    def load(self, table_name):
        """
        DESCRIPTION:
            Loads the AutoDataPrep generated data from the database  
            in the session to use it for model training or scoring.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the name of the table containing the information
                of deployed datasets in the database.
                Types: str

        RETURNS:
            Dictionary of DataFrames containing the datas generated from AutoDataPrep.

        RAISES:
            TeradataMlException, ValueError

        EXAMPLES:
            # Create an instance of the AutoDataPrep.
            # Load the data from the table.

            # Create an instance of AutoDataPrep.
            >>> aprep_obj = AutoDataPrep()

            # Load the data from the table.
            >>> data = aprep_obj.load("table_name")

            # Retrieve the data
            >>> print(data)
        """

        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["table_name", table_name, True, (str), True])

        # Validating the arguments
        _Validators._validate_function_arguments(arg_info_matrix)

        # Load the data from the table
        load_df = DataFrame(table_name)

        data = {}
        # Load the data into dictionary
        for mtd, tab_name in load_df.get_values():
            try:
                data[mtd] = DataFrame(tab_name)
            except Exception as e:
                print(f"Error while loading {mtd} table: ", e)
                data[mtd] = None
                continue
        
        return data
    

    def delete_data(self, 
                    table_name,
                    fs_method=None):
        """
        DESCRIPTION:
            Deletes the deployed datasets from the database.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the name of the table containing the deployed datasets.
                Types: str
            
            fs_method:
                Optional Argument.
                Specifies the name of the feature selection method to delete from the
                deployed datasets.
                Default Value: None
                Permitted Values: "lasso", "rfe", "pca"
                Note:
                    * If "fs_method" is None, then method deletes all the deployed datasets.
                Types: str or list of str

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create an instance of the AutoDataPrep.
            # Fit the data.
            # Deploy the data to the table.
            # Remove the deployed data from the table.

            # Example 1: Remove the deployed data from the table within the AutoDataPrep object.

            from teradataml import AutoDataPrep
            # Load the example data.
            >>> load_example_data("teradataml", "titanic")
            >>> titanic = DataFrame.from_table("titanic")
            
            # Create an instance of AutoDataPrep.
            >>> aprep_obj = AutoDataPrep(task_type="Classification", verbose=2)

            # fit the data.
            >>> aprep_obj.fit(titanic, titanic.survived)

            # Deploy the datas to the database.
            >>> aprep_obj.deploy("table_name")

            # Remove lasso deployed data from the table.
            >>> aprep_obj.delete_data("table_name", fs_method="lasso")

            # Example 2: Remove the deployed data from the table using different instance of AutoDataPrep object.
            # Create an instance of AutoDataPrep.
            >>> aprep_obj2 = AutoDataPrep()

            # Remove lasso and pca deployed data from the table.
            >>> aprep_obj2.delete_data("table_name", fs_method=["lasso", "pca"])
        
        """
        # Appending arguments to list for validation
        arg_info_matrix = []
        arg_info_matrix.append(["table_name", table_name, False, (str), True])
        arg_info_matrix.append(["fs_method", fs_method, True, (str, list), True, aml_const.FEATURE_SELECTION_MTDS.value])

        # Validating the arguments
        _Validators._validate_function_arguments(arg_info_matrix)
        
        # Load the data from the table
        df = DataFrame(table_name)
        # Get the values from the loaded DataFrame
        values = df.get_values()

        if fs_method is None:
            # If fs_method is None, then delete all the tables
            methods = aml_const.FEATURE_SELECTION_MTDS.value
        elif isinstance(fs_method, str):
            # If fs_method is str, then convert it to list
            methods = [fs_method]
        else:
            # If fs_method is list, then use it as it is
            methods = fs_method
        # Convert the methods to lower case
        methods = [method.lower() for method in methods]
        
        filtered_data = []
        remaining_data = []
        # Filter the values based on the fs_method
        for row in values:
            if any(cond in row[0] for cond in methods):
                filtered_data.append(row)
            else:
                remaining_data.append(row)

        # Drop the tables
        err_flag = False
        for row in filtered_data:
            tab_name = row[1]
            mtd = row[0]
            try:
                db_drop_table(tab_name)
                print(f"Removed {mtd} table successfully.")
            except Exception as e:
                print(f"Error while removing {mtd} table: ", e)
                remaining_data.append(row)
                err_flag = True
                continue

        if err_flag:
            # Print message if error occured while removing deployed data
            print("Error occured while removing deployed data.")

        if len(remaining_data) > 0:
            rem_data = pd.DataFrame(remaining_data, columns=['Feature_Selection_Method', 'Table_Name'])
            # Save the data to the database
            copy_to_sql(df= rem_data, table_name=table_name, if_exists="replace")
        elif not err_flag:
            # Drop the whole table if no data is remaining
            db_drop_table(table_name)
            print("Deployed data removed successfully.")