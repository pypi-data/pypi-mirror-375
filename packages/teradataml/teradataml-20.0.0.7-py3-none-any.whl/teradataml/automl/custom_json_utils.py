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

import json
from teradataml.common.constants import AutoMLConstants

class _GenerateCustomJson:
    
    def __init__(self, cluster=False):
        """
        DESCRIPTION:
            Function initializes the data and flags for custom JSON file generation.

        PARAMETERS:
            cluster:
                Optional Argument.
                Specifies whether to apply clustering techniques.
                Default Value: False
                Types: bool
        """
        # Initializing data dictionary for storing custom parameters
        self.data = {}
        # Initializing first time execution flag variables for each phase
        self.fe_flag = {index : False for index in range(1, 8)}
        self.de_flag = {index : False for index in range(1, 5)}
        self.mt_flag = {index : False for index in range(1, 2)}
        self.cluster = cluster
    
    def _process_list_input(self, 
                            input_data, 
                            value_type='str',
                            allowed_values=None):
        """
        DESCRIPTION:
            Function processes input data contaning one or more than one, expected 
            to be comma separated and converts them into list of specified type.
        
        PARAMETERS:
            input_data:
                Required Argument.
                Specifies the input data to be processed.
                Types: str
        
            value_type:
                Optional Argument.
                Specifies the type of value present in input data.
                Default Value: "str"
                Types: str
            
            allowed_values:
                Optional Argument.
                Specifies the list of allowed values for input data.
                Default Value: None
                Types: list

        RETURNS:
            List containing values of specified type.
        
        RAISES:
            ValueError: If input data is empty or not valid.
        """
        
        while True:
            try:
                # Checking if input is empty
                if not input_data.strip():
                    raise ValueError("\nInput data cannot be empty. "
                                     "Please provide a valid comma separated input.")       
                # Processing multi-valued input data
                if value_type == 'int':
                    result = [int(value.strip()) for value in input_data.split(',')]
                elif value_type == 'float':
                    result = [float(value.strip()) for value in input_data.split(',')]
                elif value_type == 'bool':
                    result = []
                    for value in input_data.split(','):
                        if value.strip().lower() not in ['true', 'false']:
                            raise ValueError("\nInvalid input. Please provide a valid input from 'True' or 'False'.")
                        else:
                            result.append(True if value.strip().lower() == 'true' else False)
                else:
                    result = [value.strip() for value in input_data.split(',')]
                    
                if allowed_values:
                    for value in result:
                        if value not in allowed_values:
                            raise ValueError(f"\nInvalid input {value}. "
                                             f"Please provide a valid input from {allowed_values}.")
                return result
            # Handling exceptions for invalid input
            except ValueError as msg:
                print(f"\n**ERROR:** {msg}")
                # Ask the user to try again
                input_data = input("\nEnter the correct input: ")

    def _process_single_input(self, 
                             input_data, 
                             value_type='str',
                             allowed_values=None):
        """
        DESCRIPTION:
            Function processes the input data containing only single value and 
            converts it into specified type.
            
        PARAMETERS:
            input_data:
                Required Argument.
                Specifies the input data to be processed.
                Types: str
        
            value_type:
                Optional Argument.
                Specifies the type of value present in input data.
                Default Value: "str"
                Types: str
            
        RETURNS:
            Value of specified type.
        
        RAISES:
            ValueError: If input data is empty or not valid.
        """
        while True:
            try:
                # Checking if input is empty
                if not input_data.strip():
                    raise ValueError("\nInput data cannot be empty. "
                                    "Please provide a valid input.")
                # Processing single value input data
                if value_type == 'int':
                    result = int(input_data)
                elif value_type == 'float':
                    result = float(input_data)
                elif value_type == 'bool':
                    result = True if input_data.lower() == 'true' else False
                else:
                    result = input_data
                
                if allowed_values:
                    if result not in allowed_values:
                        raise ValueError(f"\nInvalid input {result}. "
                                        f"Please provide a valid input from {allowed_values}.")
                return result
            # Handling exceptions for invalid input
            except ValueError as msg:
                print(f"\n**ERROR:** {msg}")
                # Ask the user to try again
                input_data = input("\nEnter the correct input: ")
                
    def _generate_custom_json(self):
        """
        DESCRIPTION:
            Function collects customized user input using prompt for feature enginnering,
            data preparation and model training phases.

        RETURNS:
            Dictionary containing custom parameters to generate custom JSON file for AutoML.
        """
        
        print("\nGenerating custom config JSON for AutoML ...")
        
        customize_options = {
            1: 'Customize Feature Engineering Phase',
            2: 'Customize Data Preparation Phase',
            3: 'Customize Model Training Phase',
            4: 'Generate custom json and exit'
            }
        
        while True:
            
            print(f"\nAvailable main options for customization with corresponding indices: ")
            print("-"*80)
            for index, options in customize_options.items():
                print(f"\nIndex {index}: {options}")
            print("-"*80)
            # Mapping each index to corresponding functionality
            custom_method_map = {
                1: self._get_customize_input_feature_engineering,
                2: self._get_customize_input_data_preparation,
                3: self._get_customize_input_model_training
            }
            
            # Taking required input for customizing feature engineering, data preparation and model training phases
            phase_idx = self._process_single_input(
                input("\nEnter the index you want to customize: "), 
                'int', list(customize_options.keys()))
            # Checking if user wants to exit
            if phase_idx == 4:
                print("\nGenerating custom json and exiting ...")
                break
            else:
                # Processing each functionality for customization
                # Getting exit flag to exit from main menu
                exit_flag = custom_method_map[phase_idx]()
                if exit_flag:
                    break
        
        print("\nProcess of generating custom config file for AutoML has been completed successfully.")
        # Returning custom parameters
        return self.data

    def _get_customize_input_feature_engineering(self):
        """
        DESCRIPTION:
            Function takes user input for different functionalities to customize 
            feature engineering phase.
        """
        
        print("\nCustomizing Feature Engineering Phase ...")
        # Available options for customization of feature engineering phase
        fe_customize_options = {
            1: 'Customize Missing Value Handling',
            2: 'Customize Bincode Encoding',
            3: 'Customize String Manipulation',
            4: 'Customize Categorical Encoding',
            5: 'Customize Mathematical Transformation',
            6: 'Customize Nonlinear Transformation',
            7: 'Customize Antiselect Features',
            8: 'Back to main menu',
            9: 'Generate custom json and exit'
            }
        
        while True:
                    
            print(f"\nAvailable options for customization of feature engineering phase with corresponding indices: ")
            print("-"*80)
            for index, options in fe_customize_options.items():
                print(f"\nIndex {index}: {options}")
            print("-"*80)
            # Mapping each index to corresponding functionality
            fe_method_map = {
                1: self._get_customize_input_missing_value_handling,
                2: self._get_customize_input_bin_code_encoding,
                3: self._get_customize_input_string_manipulation,
                4: self._get_customize_input_categorical_encoding,
                5: self._get_customize_input_mathematical_transformation,
                6: self._get_customize_input_nonlinear_transformation,
                7: self._get_customize_input_antiselect
            }
        
            # Taking required input for customizing feature engineering
            fe_phase_idx = self._process_list_input(
                input("\nEnter the list of indices you want to customize in feature engineering phase: "), 
                'int', list(fe_customize_options.keys()))
            
            # Setting back_key and exit_key
            fe_back_key, fe_exit_key = 8, 9
            # Flag variable to back to main menu
            fe_exit_to_main_flag = False
            # Flag variable to exit from main menu
            # Handling the scenario when input contains both index 8 and 9
            fe_exit_from_main_flag = fe_exit_key in fe_phase_idx

            # Processing each functionality for customization in sorted order  
            for index in sorted(fe_phase_idx):
                if index == fe_back_key or index == fe_exit_key:
                    fe_exit_to_main_flag = True
                    if index == fe_exit_key:
                        fe_exit_from_main_flag = True 
                    break
                fe_method_map[index](self.fe_flag[index])
                self.fe_flag[index] = True
            # Checking if user wants to return to main menu
            if fe_exit_to_main_flag:
                print("\nCustomization of feature engineering phase has been completed successfully.")
                break
        # Returning flag to exit from main menu
        return fe_exit_from_main_flag

    def _get_customize_input_data_preparation(self):
        """
        DESCRIPTION:
            Function takes user input for different functionalities to customize 
            data preparation phase.
        """
        print("\nCustomizing Data Preparation Phase ...")
        # Available options for customization of data preparation phase
        if self.cluster:
            dp_customize_options = {
                1: 'Customize Outlier Handling',
                2: 'Customize Feature Scaling',
                3: 'Back to main menu',
                4: 'Generate custom json and exit'
            }
        else:
            dp_customize_options = {
                1: 'Customize Data Imbalance Handling',
                2: 'Customize Outlier Handling',
                3: 'Customize Feature Scaling',
                4: 'Back to main menu',
                5: 'Generate custom json and exit'
                }
        
        while True:
        
            print(f"\nAvailable options for customization of data preparation phase with corresponding indices: ")
            print("-"*80)
            for index, options in dp_customize_options.items():
                print(f"\nIndex {index}: {options}")
            print("-"*80)
            # Mapping each index to corresponding functionality
            if self.cluster:
                de_method_map = {
                    1: self._get_customize_input_outlier_handling,
                    2: self._get_customize_input_feature_scaling
                }
                de_back_key, de_exit_key = 3, 4
            else:
                de_method_map = {
                    1: self._get_customize_input_data_imbalance_handling,
                    2: self._get_customize_input_outlier_handling,
                    3: self._get_customize_input_feature_scaling
                }
                de_back_key, de_exit_key = 4, 5
            # Taking required input for customizing data preparation.
            dp_phase_idx = self._process_list_input(
                input("\nEnter the list of indices you want to customize in data preparation phase: "),
                'int', list(dp_customize_options.keys()))
            
            # Setting back_key and exit_key
            
            # Flag variable to back to main menu
            de_exit_to_main_flag = False
            # Flag variable to exit from main menu
            # Handling the scenario when input contains both back_key and exit_key
            de_exit_from_main_flag = de_exit_key in dp_phase_idx
            
            # Processing each functionality for customization in sorted order
            for index in sorted(dp_phase_idx):
                if index == de_back_key or index == de_exit_key:
                    de_exit_to_main_flag = True
                    if index == de_exit_key:
                        de_exit_from_main_flag = True
                    break
                de_method_map[index](self.de_flag[index])
                self.de_flag[index] = True
            # Checking if user wants to return to main menu
            if de_exit_to_main_flag:
                print("\nCustomization of data preparation phase has been completed successfully.")
                break
        # Returning flag to exit from main menu
        return de_exit_from_main_flag
    
    def _get_customize_input_model_training(self):
        """
        DESCRIPTION:
            Function takes user input for different functionalities to customize
            model training phase.
        """
        print("\nCustomizing Model Training Phase ...")
        # Available options for customization of model training phase
        mt_customize_options = {
            1: 'Customize Model Hyperparameter',
            2: 'Back to main menu',
            3: 'Generate custom json and exit'
            }

        while True:
            
            print(f"\nAvailable options for customization of model training phase with corresponding indices: ")
            print("-"*80)
            for index, options in mt_customize_options.items():
                print(f"\nIndex {index}: {options}")
            print("-"*80)
            
            # Taking required input for customizing model training.
            mt_phase_idx = self._process_list_input(
                input("\nEnter the list of indices you want to customize in model training phase: "), 
                'int', list(mt_customize_options.keys()))
                        
            # Flag variable to back to main menu
            mt_exit_to_main_flag = False
            # Flag variable to exit from main menu
            # Handling the scenario when input contains both index 2 and 3
            mt_exit_from_main_flag = 3 in mt_phase_idx
            
            # Processing each functionality for customization in sorted order    
            for index in sorted(mt_phase_idx):
                if index == 1:
                    self._get_customize_input_model_hyperparameter(self.mt_flag[index])
                elif index == 2 or index == 3:
                    mt_exit_to_main_flag = True
                    if index == 3:
                        mt_exit_from_main_flag = True
                    break
                self.mt_flag[index] = True
            # Checking if user wants to return to main menu    
            if mt_exit_to_main_flag:
                print("\nCustomization of model training phase has been completed successfully.")
                break
        # Returning flag to exit from main menu
        return mt_exit_from_main_flag
    
    def _set_generic_arguement(self,
                               func_name):
        """
        DESCRIPTION:
            Internal Function to set generic arguments for each functionality.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of functionality for which generic arguments are to be set.
                Types: str
        """
        generic_flag = {
            0: 'Default',
            1: 'volatile',
            2: 'persist'
        }
        print("\nAvailable options for generic arguments: ")
        for index, method in generic_flag.items():
            print(f"Index {index}: {method}")
        inp = self._process_list_input(
                input("\nEnter the indices for generic arguments : "), 'int')[0]
        if inp == 0:
            return
        if inp == 1:
            self.data[func_name]['volatile'] = True
        elif inp == 2:
            self.data[func_name]['persist'] = True
    
    def _get_customize_input_missing_value_handling(self, 
                                                    first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for missing value handling.
        
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool
        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated missing value handling customization. "
                  "Overwriting the previous input.")
            
        print("\nCustomizing Missing Value Handling ...")
        # Setting indicator for missing value handling
        self.data['MissingValueHandlingIndicator'] = True
        print("\nProvide the following details to customize missing value handling:")
        # Setting parameters for missing value handling
        self.data['MissingValueHandlingParam'] = {}
        
        missing_handling_methods = {1: 'Drop Columns',
                                    2: 'Drop Rows',
                                    3: 'Impute Missing values'}
        
        print("\nAvailable missing value handling methods with corresponding indices: ")
        for index, method in missing_handling_methods.items():
            print(f"Index {index}: {method}")
            
        missing_handling_methods_idx = self._process_list_input(
            input("\nEnter the list of indices for missing value handling methods : "), 
            'int', list(missing_handling_methods.keys()))
        
        for index in missing_handling_methods_idx:
            if index == 1:
                # Setting indicator for dropping columns with missing values
                self.data['MissingValueHandlingParam']['DroppingColumnIndicator'] = True
                drop_col_list = self._process_list_input(
                    input("\nEnter the feature or list of features for dropping columns with missing values: "))
                self.data['MissingValueHandlingParam']['DroppingColumnList'] = drop_col_list
            elif index == 2:                    
                self.data['MissingValueHandlingParam']['DroppingRowIndicator'] = True
                drop_row_list = self._process_list_input(
                    input("\nEnter the feature or list of features for dropping rows with missing values: "))
                self.data['MissingValueHandlingParam']['DroppingRowList'] = drop_row_list
            elif index == 3:
                self.data['MissingValueHandlingParam']['ImputeMissingIndicator'] = True
                
                impute_methods = {1: 'Statistical Imputation',
                                  2: 'Literal Imputation'}
                print("\nAvailable missing value imputation methods with corresponding indices: ")
                for index, method in impute_methods.items():
                    print(f"Index {index}: {method}")
                
                impute_methods_idx = self._process_list_input(
                    input("\nEnter the list of corresponding index missing value imputation methods you want to use: "), 
                    'int', list(impute_methods.keys()))
                
                for index in impute_methods_idx:
                    if index == 1:
                        stat_imp_list = self._process_list_input(
                            input("\nEnter the feature or list of features for imputing missing values using statistic values: "))
                        self.data['MissingValueHandlingParam']['StatImputeList'] = stat_imp_list
                        
                        # Displaying available statistical imputation methods
                        stat_methods = {1: 'min',
                                        2: 'max',
                                        3: 'mean',
                                        4: 'median',
                                        5: 'mode'}
                        print("\nAvailable statistical methods with corresponding indices:")
                        for index, method in stat_methods.items():
                            print(f"Index {index}: {method}")

                        self.data['MissingValueHandlingParam']['StatImputeMethod'] = []
                        # Setting statistical imputation methods for features    
                        for feature in stat_imp_list:
                            method_idx = self._process_single_input(
                                input(f"\nEnter the index of corresponding statistic imputation "
                                      f"method for feature {feature}: "), 
                                'int', list(stat_methods.keys()))
                            self.data['MissingValueHandlingParam']['StatImputeMethod'].append(stat_methods[method_idx])
                    elif index == 2:
                        literal_imp_list = self._process_list_input(
                            input("\nEnter the feature or list of features for imputing missing values "
                                "using a specific value(Literal): "))
                        # Setting list of features for imputing missing values using specific literal value
                        self.data['MissingValueHandlingParam']['LiteralImputeList'] = literal_imp_list
                        self.data['MissingValueHandlingParam']['LiteralImputeValue'] = []
                        for feature in literal_imp_list:
                            # Setting specific literal value for imputing missing values for each feature
                            literal_value = self._process_single_input(
                                input(f"\nEnter the specific literal value for imputing missing "
                                      f"values for feature {feature}: "))
                            self.data['MissingValueHandlingParam']['LiteralImputeValue'].append(literal_value)
        # Setting generic arguments
        self._set_generic_arguement(func_name='MissingValueHandlingParam')
        print("\nCustomization of missing value handling has been completed successfully.")
        
    def _get_customize_input_bin_code_encoding(self,
                                               first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for performing binning on features.
            
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated bincode encoding customization. "
                  "Overwriting the previous input.")
            
        print("\nCustomizing Bincode Encoding ...")
        # Setting indicator for binning
        self.data['BincodeIndicator'] = True
        print("\nProvide the following details to customize binning and coding encoding:")
        self.data['BincodeParam'] = {}

        # Displaying available binning methods
        binning_methods = {1: 'Equal-Width', 
                           2: 'Variable-Width'}
        print("\nAvailable binning methods with corresponding indices:")
        for index, method in binning_methods.items():
            print(f"Index {index}: {method}")

        # Setting parameters for binning
        binning_list = self._process_list_input(input("\nEnter the feature or list of features for binning: "))
        if binning_list:
            for feature in binning_list:
                # Setting parameters for binning each feature
                self.data['BincodeParam'][feature] = {}
                bin_method_idx = self._process_single_input(
                    input(f"\nEnter the index of corresponding binning method for feature {feature}: "), 
                    'int', list(binning_methods.keys()))

                # Setting binning method and number of bins for each feature
                self.data['BincodeParam'][feature]["Type"] = binning_methods[bin_method_idx]
                num_of_bin = self._process_single_input(
                    input(f"\nEnter the number of bins for feature {feature}: "), 'int')
                self.data['BincodeParam'][feature]["NumOfBins"] = num_of_bin
                
                # Setting parameters for each bin of feature in case of variable width binning
                if bin_method_idx == 2:
                    value_type = {
                            1: 'int',
                            2: 'float'
                        }
                    print("\nAvailable value type of feature for variable binning with corresponding indices:")
                    for index, v_type in value_type.items():
                        print(f"Index {index}: {v_type}")
                    # Setting parameters for each bin of feature
                    for num in range(1, num_of_bin+1):
                        print(f"\nProvide the range for bin {num} of feature {feature}: ")
                        bin_num="Bin_"+str(num)
                        self.data['BincodeParam'][feature][bin_num] = {}
                            
                        # Setting bin value type for corresponding bin
                        bin_value_type_idx = self._process_single_input(
                            input(f"\nEnter the index of corresponding value type of feature {feature}: "),
                            'int', list(value_type.keys()))
                        
                        bin_value_type = value_type[bin_value_type_idx]
                        
                        # Setting minimum value for corresponding bin
                        self.data['BincodeParam'][feature][bin_num]['min_value'] = self._process_single_input(
                            input(f"\nEnter the minimum value for bin {num} of feature {feature}: "), 
                            bin_value_type)
                        # Setting maximum value for corresponding bin
                        self.data['BincodeParam'][feature][bin_num]['max_value'] = self._process_single_input(
                            input(f"\nEnter the maximum value for bin {num} of feature {feature}: "), 
                            bin_value_type)
                        # Setting label for corresponding bin
                        self.data['BincodeParam'][feature][bin_num]['label'] = self._process_single_input(
                            input(f"\nEnter the label for bin {num} of feature {feature}: "))
            self._set_generic_arguement(func_name='BincodeParam')

        print("\nCustomization of bincode encoding has been completed successfully.")          
            
    def _get_customize_input_string_manipulation(self,
                                                 first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for string manipulation.
        
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated string manipulation customization. "
                  "Overwriting the previous input.")

        print("\nCustomizing String Manipulation ...")
        # Setting indicator for string manipulation
        self.data['StringManipulationIndicator'] = True
        print("\nProvide the following details to customize string manipulation:")
        self.data['StringManipulationParam'] = {}
        # Displaying available string manipulation methods
        string_methods = {1: 'ToLower', 
                          2: 'ToUpper', 
                          3: 'StringCon', 
                          4: 'StringPad', 
                          5: 'Substring'}
        print("\nAvailable string manipulation methods with corresponding indices:")
        for index, method in string_methods.items():
            print(f"Index {index}: {method}")

        # Setting parameters for string manipulation
        str_mnpl_list = self._process_list_input(
            input("\nEnter the feature or list of features for string manipulation: "))
        # Processing each feature
        if str_mnpl_list:
            for feature in str_mnpl_list:
                # Setting parameters for string manipulation each feature
                self.data['StringManipulationParam'][feature] = {}
                str_mnpl_method_idx = self._process_single_input(
                    input(f"\nEnter the index of corresponding string manipulation " 
                          f"method for feature {feature}: "), 'int', list(string_methods.keys()))
                self.data['StringManipulationParam'][feature]["StringOperation"] = \
                    string_methods[str_mnpl_method_idx]
                # Setting required parameters specific to each string manipulation method
                if str_mnpl_method_idx in [3, 4]:
                    str_mnpl_string = self._process_single_input(
                        input(f"\nEnter the string value required for string manipulation "
                              f"operation for feature {feature}: "))
                    self.data['StringManipulationParam'][feature]["String"] = str_mnpl_string

                if str_mnpl_method_idx in [4, 5]:
                    str_mnpl_length = self._process_single_input(
                        input(f"\nEnter the length value required for string manipulation "
                              f"operation for feature {feature}: "), 'int')
                    self.data['StringManipulationParam'][feature]["StringLength"] = str_mnpl_length

                if str_mnpl_method_idx == 5:
                    str_mnpl_start = self._process_single_input(
                        input(f"\nEnter the start value required for string manipulation "
                              f"operation for feature {feature}: "), 'int')
                    self.data['StringManipulationParam'][feature]["StartIndex"] = str_mnpl_start
        
        self._set_generic_arguement(func_name='StringManipulationParam')
        print("\nCustomization of string manipulation has been completed successfully.")

    def _get_customize_input_categorical_encoding(self,
                                                  first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for categorical encoding.
            
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated categorical encoding customization. "
                  "Overwriting the previous input.")
            
        print("\nCustomizing Categorical Encoding ...")
        # Setting indicator for categorical encoding
        self.data['CategoricalEncodingIndicator'] = True
        print("\nProvide the following details to customize categorical encoding:")
        # Setting parameters for categorical encoding
        self.data['CategoricalEncodingParam'] = {}
        
        encoding_methods = {1: 'OneHotEncoding',
                            2: 'OrdinalEncoding',
                            3: 'TargetEncoding'}
        
        print("\nAvailable categorical encoding methods with corresponding indices:")
        for index, method in encoding_methods.items():
            print(f"Index {index}: {method}")
        
        encoding_methods_idx = self._process_list_input(
            input("\nEnter the list of corresponding index categorical encoding methods you want to use: "), 
            'int', list(encoding_methods.keys()))
        
        for index in encoding_methods_idx:
            if index == 1:
                # Setting indicator for OneHotEncoding
                self.data['CategoricalEncodingParam']['OneHotEncodingIndicator'] = True
                # Setting parameters for OneHotEncoding
                one_hot_list = self._process_list_input(
                    input("\nEnter the feature or list of features for OneHotEncoding: "))
                self.data['CategoricalEncodingParam']['OneHotEncodingList'] = one_hot_list
            elif index == 2:
                # Setting indicator for OrdinalEncoding
                self.data['CategoricalEncodingParam']['OrdinalEncodingIndicator'] = True
                # Setting parameters for OrdinalEncoding
                ordinal_list = self._process_list_input(
                    input("\nEnter the feature or list of features for OrdinalEncoding: "))
                self.data['CategoricalEncodingParam']['OrdinalEncodingList'] = ordinal_list
            elif index == 3:
                # Setting indicator for TargetEncoding
                self.data['CategoricalEncodingParam']['TargetEncodingIndicator'] = True
                target_end_list = self._process_list_input(input("\nEnter the feature or list of features for TargetEncoding: "))
                # Setting parameters for TargetEncoding
                self.data['CategoricalEncodingParam']['TargetEncodingList'] = {}
                target_end_methods = {1: 'CBM_BETA',
                                      2: 'CBM_DIRICHLET',
                                      3: 'CBM_GAUSSIAN_INVERSE_GAMMA'}
                print("\nAvailable target encoding methods with corresponding indices:")
                for index, method in target_end_methods.items():
                    print(f"Index {index}: {method}")

                # Setting parameters specific to each feature and corresponding method    
                for feature in target_end_list:
                    self.data['CategoricalEncodingParam']['TargetEncodingList'][feature] = {}
                    end_method_idx = self._process_single_input(
                        input(f"\nEnter the index of target encoding method for feature {feature}: "), 
                        'int', list(target_end_methods.keys()))
                    # Setting target encoding method for each feature
                    self.data['CategoricalEncodingParam']['TargetEncodingList'][feature]["encoder_method"] = \
                        target_end_methods[end_method_idx]

                    # Setting response column for target encoding method
                    response_column = self._process_single_input(
                        input(f"\nEnter the response column for target encoding method for feature {feature}: "))
                    self.data['CategoricalEncodingParam']['TargetEncodingList'][feature]["response_column"] = \
                        response_column

                    # Getting specific parameter in case of CBM_DIRICHLET method
                    if end_method_idx == 2:
                        num_distinct_responses = self._process_single_input(
                            input(f"\nEnter the distinct count of response column "
                                  f"for target encoding method for feature {feature}: "), 'int')
                        self.data['CategoricalEncodingParam']['TargetEncodingList'][feature]["num_distinct_responses"] = \
                            num_distinct_responses
        
        self._set_generic_arguement(func_name='CategoricalEncodingParam')
        print("\nCustomization of categorical encoding has been completed successfully.")
            
    def _get_customize_input_mathematical_transformation(self,
                                                         first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for mathematical transformation.
            
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated mathematical transformation customization. "
                  "Overwriting the previous input.")
        
        print("\nCustomizing Mathematical Transformation ...")
        # Setting indicator for mathematical transformation
        self.data['MathameticalTransformationIndicator'] = True
        print("\nProvide the following details to customize mathematical transformation:")
        # Setting parameters for mathematical transformation
        self.data['MathameticalTransformationParam'] = {}
        mat_trans_methods = {1: 'sigmoid', 
                             2: 'sininv', 
                             3: 'log', 
                             4: 'pow', 
                             5: 'exp'}
        print("\nAvailable mathematical transformation methods with corresponding indices:")
        for index, method in mat_trans_methods.items():
            print(f"Index {index}: {method}")

        mat_trans_list = self._process_list_input(
            input("\nEnter the feature or list of features for mathematical transformation: "))
        if mat_trans_list:
            for feature in mat_trans_list:
                # Setting parameters for mathematical transformation specific to each feature
                self.data['MathameticalTransformationParam'][feature] = {}
                mat_trans_method_idx = self._process_single_input(
                    input(f"\nEnter the index of corresponding mathematical "
                          f"transformation method for feature {feature}: "), 
                    'int', list(mat_trans_methods.keys()))

                self.data['MathameticalTransformationParam'][feature]["apply_method"] = \
                    mat_trans_methods[mat_trans_method_idx]
                # Setting required parameters specific to each mathematical transformation method
                if mat_trans_method_idx == 1 :
                    sigmoid_style = self._process_single_input(
                        input(f"\nEnter the sigmoid style required for mathematical "
                              f"transformation for feature {feature}: "))
                    self.data['MathameticalTransformationParam'][feature]["sigmoid_style"] = \
                        sigmoid_style

                if mat_trans_method_idx == 3:
                    base = self._process_single_input(
                        input(f"\nEnter the base value required for mathematical "
                              f"transformation for feature {feature}: "), 'int')
                    self.data['MathameticalTransformationParam'][feature]["base"] = base

                if mat_trans_method_idx == 4:
                    exponent = self._process_single_input(
                        input(f"\nEnter the exponent value required for mathematical "
                              f"transformation for feature {feature}: "), 'int')
                    self.data['MathameticalTransformationParam'][feature]["exponent"] = exponent
        
        self._set_generic_arguement(func_name='MathameticalTransformationParam')
        print("\nCustomization of mathematical transformation has been completed successfully.")

    def _get_customize_input_nonlinear_transformation(self,
                                                      first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for nonlinear transformation.
        
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool
        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated nonlinear transformation customization. "
                  "Overwriting the previous input.")

        print("\nCustomizing Nonlinear Transformation ...")
        # Setting indicator for nonlinear transformation
        self.data['NonLinearTransformationIndicator'] = True
        print("\nProvide the following details to customize nonlinear transformation:")
        # Setting parameters for nonlinear transformation
        self.data['NonLinearTransformationParam'] = {}

        # Getting total number of non-linear combinations
        total_combinations = self._process_single_input(
            input("\nEnter number of non-linear combination you want to make: "), 'int')
        for num in range(1, total_combinations+1):
            print(f"\nProvide the details for non-linear combination {num}:")
            # Creating combination name and setting parameters for each combination
            combination = "Combination_"+str(num)
            self.data['NonLinearTransformationParam'][combination] = {}
            target_columns = self._process_list_input(
                input(f"\nEnter the list of target feature/s for non-linear combination {num}: "))
            self.data['NonLinearTransformationParam'][combination]["target_columns"] = target_columns
            
            formula = self._process_single_input(
                input(f"\nEnter the formula for non-linear combination {num}: "))
            self.data['NonLinearTransformationParam'][combination]["formula"] = formula
            
            result_column = self._process_single_input(
                input(f"\nEnter the resultant feature for non-linear combination {num}: "))
            self.data['NonLinearTransformationParam'][combination]["result_column"] = result_column

        self._set_generic_arguement(func_name='NonLinearTransformationParam')
        print("\nCustomization of nonlinear transformation has been completed successfully.")

    def _get_customize_input_antiselect(self,
                                        first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for antiselect features.
        
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool
        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated nonlinear antiselect customization. "
                  "Overwriting the previous input.")
            
        print("\nCustomizing Antiselect Features ...")
        # Setting indicator and parameter for antiselect
        self.data['AntiselectIndicator'] = True
        self.data['AntiselectParam'] = {}
        self.data['AntiselectParam']['excluded_columns'] = self._process_list_input(
            input("\nEnter the feature or list of features for antiselect: "))

        self._set_generic_arguement(func_name='AntiselectParam')
        print("\nCustomization of antiselect features has been completed successfully.")
    
    def _get_customize_input_data_imbalance_handling(self,
                                                     first_execution_flag):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for data imbalance handling.

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated data imbalance handling customization. "
                  "Overwriting the previous input.")
        
        print("\nCustomizing Data Imbalance Handling ...")
        # Setting indicator for data imbalance handling
        self.data['DataImbalanceIndicator'] = True
        sampling_methods = {1: 'SMOTE', 
                            2: 'NearMiss'}
        print("\nAvailable data sampling methods with corresponding indices:")
        for index, method in sampling_methods.items():
            print(f"Index {index}: {method}")
            
        sampling_mthd_idx = self._process_single_input(
            input("\nEnter the corresponding index data imbalance handling method: "), 
            'int', list(sampling_methods.keys()))
        # Setting parameters for data imbalance handling
        self.data['DataImbalanceMethod'] = sampling_methods[sampling_mthd_idx]
        
        print("\nCustomization of data imbalance handling has been completed successfully.")
  
    def _get_customize_input_outlier_handling(self,
                                              first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for outlier handling.
        
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated outlier handling customization. "
                  "Overwriting the previous input.")
            keys_to_remove = ['OutlierLowerPercentile', 'OutlierUpperPercentile', 'OutlierFilterMethod', 'OutlierFilterParam']
            for key in keys_to_remove:
                if key in self.data:
                    del self.data[key]
            
        
        print("\nCustomizing Outlier Handling ...")

        apply_outlier_options = {1: 'Yes', 2: 'No'}
        print("\nDo you want to apply outlier filtering?")
        for idx, val in apply_outlier_options.items():
            print(f"Index {idx}: {val}")

        user_choice = self._process_single_input(
            input("\nEnter the index of your choice (1 for Yes, 2 for No): "),
            'int',
            list(apply_outlier_options.keys())
        )

        if user_choice == 2:
            self.data['OutlierFilterIndicator'] = False
            print("\nSkipping outlier filtering as per user choice.")
            return
        
        # Setting indicator for outlier handling
        self.data['OutlierFilterIndicator'] = True
        outlier_methods = {1: 'percentile', 
                           2: 'tukey', 
                           3: 'carling'}
        print("\nAvailable outlier detection methods with corresponding indices:")
        for index, method in outlier_methods.items():
            print(f"Index {index}: {method}")

        # Setting parameters for outlier handling
        outlier_mthd_idx = self._process_single_input(
            input("\nEnter the corresponding index oulier handling method: "), 
            'int', list(outlier_methods.keys()))

        self.data['OutlierFilterMethod'] = outlier_methods[outlier_mthd_idx]
        # Setting parameters specific to method 'percentile'
        if outlier_mthd_idx == 1:
            self.data['OutlierLowerPercentile'] = self._process_single_input(
                input("\nEnter the lower percentile value for outlier handling: "), 'float')
            self.data['OutlierUpperPercentile'] = self._process_single_input(
                input("\nEnter the upper percentile value for outlier handling: "), 'float')

        # Setting parameters for outlier filteration
        self.data['OutlierFilterParam'] = {}
        outlier_list = self._process_list_input(
            input("\nEnter the feature or list of features for outlier handling: "))
        
        replacement_method = {
            1: 'delete',
            2: 'median',
            3: 'Any Numeric Value'
        }
        
        print("\nAvailable outlier replacement methods with corresponding indices:")
        for index, value in replacement_method.items():
            print(f"Index {index}: {value}")

        # Setting parameters specific to each feature
        for feature in outlier_list:
            self.data['OutlierFilterParam'][feature] = {}
            replacement_method_idx = self._process_single_input(
                input(f"\nEnter the index of corresponding replacement method for feature {feature}: "),
                'int', list(replacement_method.keys()))
            
            if replacement_method_idx != 3:
                # Setting replacement method specific to each feature
                self.data['OutlierFilterParam'][feature]["replacement_value"] = replacement_method[replacement_method_idx]
            else:
                replacement_value_types = {1: 'int', 
                                           2: 'float'}
                print("\nAvailable outlier replacement value types with corresponding indices:")
                for index, value in replacement_value_types.items():
                    print(f"Index {index}: {value}")
                
                replacement_value = input(f"\nEnter the replacement value for handling outlier for feature {feature}: ")

                value_type_idx = self._process_single_input(
                    input(f"\nEnter the index of corresponding replacement value type for feature {feature}: "),
                    'int', list(replacement_value_types.keys()))

                # Setting replacement_value specific to each feature
                self.data['OutlierFilterParam'][feature]["replacement_value"] = \
                self._process_single_input(replacement_value, replacement_value_types[value_type_idx])

        self._set_generic_arguement(func_name='OutlierFilterParam')
        print("\nCustomization of outlier handling has been completed successfully.")
        
    def _get_customize_input_feature_scaling(self,
                                             first_execution_flag=False):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for feature scaling.
        
        PARAMETERS:
            first_execution_flag:
                Optional Argument.
                Specifies the flag to check if the function is called for the first time.
                Default Value: False
                Types: bool

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated feature scaling customization. "
                  "Overwriting the previous input.")

        # Setting indicator for feature scaling
        self.data['FeatureScalingIndicator'] = True
        scaling_methods = {1: 'maxabs', 
                           2: 'mean', 
                           3: 'midrange',
                           4: 'range',
                           5: 'rescale',
                           6: 'std',
                           7: 'sum',
                           8: 'ustd'}
        self.data['FeatureScalingParam'] = {}
        # Displaying available methods for scaling
        print("\nAvailable feature scaling methods with corresponding indices:")
        for index, value in scaling_methods.items():
            print(f"Index {index}: {value}")
            
        # Setting parameters for feature scaling
        scaling_methods_idx = self._process_single_input(
            input("\nEnter the corresponding index feature scaling method: "), 
            'int', list(scaling_methods.keys()))
        
        # Handling for 'rescale' method
        if scaling_methods_idx != 5:
            self.data['FeatureScalingParam']['FeatureScalingMethod'] = scaling_methods[scaling_methods_idx]
        else:
            rescaling_params = {
                1: 'lower-bound',
                2: 'upper-bound'
            }
            # Displaying available params for rescaling 
            print("\nAvailable parameters required for rescaling with corresponding indices :")
            for index, value in rescaling_params.items():
                print(f"Index {index}: {value}")
            
            rescaling_params_type = {1: 'int',
                                     2: 'float'}
            # Displaying available params types for rescaling 
            print("\nAvailable value types for rescaling params with corresponding indices:")
            for index, param_type in rescaling_params_type.items():
                print(f"Index {index}: {param_type}")     
            scaling_param_idx_list = self._process_list_input(
                input("\nEnter the list of parameter indices for performing rescaling : "),
                'int', list(rescaling_params.keys()))
            # Setting parameters for lower bound and upper bound
            lb = 0
            ub = 0
            for param_idx in scaling_param_idx_list:
                # Taking required input for lower bound
                if param_idx == 1:
                    lower_bound = input("\nEnter value for lower bound :")
                    value_type_idx = self._process_single_input(
                        input("\nEnter the index of corresponding value type of lower bound :"),
                        'int', list(rescaling_params_type.keys()))
                    lb = self._process_single_input(lower_bound, rescaling_params_type[value_type_idx])
                # Taking required input for upper bound
                elif param_idx == 2:
                    upper_bound = input("\nEnter value for upper bound :")
                    value_type_idx = self._process_single_input(
                        input("\nEnter the index of corresponding value type of upper bound :"),
                        'int', list(rescaling_params_type.keys()))
                    ub = self._process_single_input(upper_bound, rescaling_params_type[value_type_idx])
            # Creating string structure of 'rescale' method as per user input
            if lb and ub:
                scale_method = f'rescale(lb={lb}, ub={ub})'
            elif lb:
                scale_method = f'rescale(lb={lb})'
            elif ub:
                scale_method = f'rescale(ub={ub})'
            # Setting parameters for feature scaling
            self.data['FeatureScalingParam']['FeatureScalingMethod'] = scale_method 
        
        self._set_generic_arguement(func_name='FeatureScalingParam')
        print("\nCustomization of feature scaling has been completed successfully.")
    
    def _get_allowed_hyperparameters(self, model_name):
        """
        DESCRIPTION:
            Function to get allowed hyperparameters for different models.
        
        PARAMETERS:
            model_name:
                Required Argument.
                Specifies the model for which allowed hyperparameters are required.
                Types: str.
        
        RETURNS:
            Allowed hyperparameters for model.
        """
        # Setting allowed common hyperparameters for tree like model
        if self.cluster:
            allowed_hyperparameters_kmeans ={
                1 : 'n_clusters',
                2 : 'init',
                3 : 'max_iter',
            }
            allowed_hyperparameters_gaussian_mixture ={
                1 : 'n_components',
                2 : 'covariance_type',
                3 : 'max_iter',
            }
            allowed_hyperparameters = {
                'KMeans' : allowed_hyperparameters_kmeans,
                'GaussianMixture' : allowed_hyperparameters_gaussian_mixture,
            }
        else:    
            allowed_common_hyperparameters_tree_model ={
                1 : 'min_impurity',
                2 : 'max_depth',
                3 : 'min_node_size',
            }
            # Setting allowed hyperparameters for xgbooost model
            allowed_hyperparameters_xgboost = { 
                **allowed_common_hyperparameters_tree_model,
                4 : 'shrinkage_factor',
                5 : 'iter_num'
            }
            # Setting allowed hyperparameters for decision forest model
            allowed_hyperparameters_decision_forest = {
                **allowed_common_hyperparameters_tree_model,
                4 : 'num_trees'
            }
            # Setting allowed hyperparameters for knn model
            allowed_hyperparameters_knn = {
                0 : 'k'
            }
            # Setting allowed hyperparameters for svm model
            allowed_hyperparameters_svm = {
                1 : 'alpha',
                2 : 'learning_rate',
                3 : 'initial_eta',
                4 : 'momentum',
                5 : 'iter_num_no_change',
                6 : 'iter_max',
                7 : 'batch_size'
            }
            # Setting allowed hyperparameters for glm model
            allowed_hyperparameters_glm = {
                **allowed_hyperparameters_svm,
                8 : 'tolerance',
                9 : 'nesterov',
                10 : 'intercept',
                11 : 'local_sgd_iterations'
            }
            # Setting allowed hyperparameters for different models
            allowed_hyperparameters = {
                'xgboost' : allowed_hyperparameters_xgboost,
                'decision_forest' : allowed_hyperparameters_decision_forest,
                'knn' : allowed_hyperparameters_knn,
                'svm' : allowed_hyperparameters_svm,
                'glm' : allowed_hyperparameters_glm
            }
        return allowed_hyperparameters[model_name]
    
    def _get_allowed_hyperparameters_types(self, hyperparameter):
        """
        DESCRIPTION:
            Function to map allowed hyperparameter types for different hyperparameters.
        
        PARAMETERS:
            hyperparameter:
                Required Argument.
                Specifies the hyperparamter for which allowed types are required.
                Types: str.

        RETURNS:
            Allowed hyperparameters types for hyperparameter.
        """
        # Setting allowed hyperparameters types for different hyperparameters
        if self.cluster:
            allowed_hyperparameters_types = {
                'n_clusters': 'int',
                'init': 'str',
                'max_iter': 'int',
                'n_components': 'int',
                'covariance_type': 'str'
            }
        else:
            allowed_hyperparameters_types = {
                'min_impurity' : 'float',
                'max_depth' : 'int',
                'min_node_size' : 'int',
                'shrinkage_factor' : 'float',
                'iter_num' : 'int',
                'num_trees' : 'int',
                'k' : 'int',
                'alpha' : 'float',
                'learning_rate' : 'str',
                'initial_eta' : 'float',
                'momentum' : 'float',
                'iter_num_no_change' : 'int',
                'iter_max' : 'int',
                'batch_size' : 'int',
                'tolerance' : 'float',
                'nesterov' : 'bool',
                'intercept' : 'bool',
                'local_sgd_iterations' : 'int'
            }
        return allowed_hyperparameters_types[hyperparameter]
    
    def _get_customize_input_model_hyperparameter(self,
                                                  first_execution_flag):
        """
        DESCRIPTION:
            Function takes user input to generate custom json paramaters for model hyperparameter.
        
        PARAMETERS:
            first_execution_flag:
                Required Argument.
                Specifies the flag to check if the function is called for the first time.
                Types: bool.

        """
        if first_execution_flag:
            print("\nWARNING : Reinitiated model hyperparameter customization. "
                  "Overwriting the previous input.")
            
        print("\nCustomizing Model Hyperparameter ...")
        # Setting indicator for model hyperparameter tuning
        self.data['HyperparameterTuningIndicator'] = True
        self.data['HyperparameterTuningParam'] = {}
        if self.cluster:
            # Create numbered mapping for clustering models
            all_models = {i+1: model for i, model in enumerate(AutoMLConstants.CLUSTERING_MODELS.value)}
        else:
            # Create numbered mapping for supervised models
            all_models = {i+1: model for i, model in enumerate(AutoMLConstants.SUPERVISED_MODELS.value)}
        # Displaying available models for hyperparameter tuning
        print("\nAvailable models for hyperparameter tuning with corresponding indices:")
        for index, model in all_models.items():
            print(f"Index {index}: {model}")
            
        update_methods = {1: 'ADD', 
                          2: 'REPLACE'}

        # Getting list of models for hyperparameter tuning    
        model_idx_list = self._process_list_input(
            input("\nEnter the list of model indices for performing hyperparameter tuning: "), 
            'int', list(all_models.keys()))
        
        for model_index in model_idx_list:
            # Setting parameters for hyperparameter tuning specific to each model
            model_name = all_models[model_index]
            self.data['HyperparameterTuningParam'][model_name] = {}
            
            # Getting list of hyperparameters for each model
            allowed_hyperparameters = self._get_allowed_hyperparameters(model_name)
            print(f"\nAvailable hyperparameters for model '{model_name}' with corresponding indices:")
            for index, hyperparameter in allowed_hyperparameters.items():
                print(f"Index {index}: {hyperparameter}")
                
            model_hyperparameter_list_idx = self._process_list_input(
                input(f"\nEnter the list of hyperparameter indices for model '{model_name}': "),
                'int', list(allowed_hyperparameters.keys()))
            
            # Setting parameters for each hyperparameter of model
            for hyperparameter in model_hyperparameter_list_idx:
                hyperparameter_name = allowed_hyperparameters[hyperparameter]
                self.data['HyperparameterTuningParam'][model_name][hyperparameter_name] = {}

                self._display_example_hyperparameter(hyperparameter_name)
                
                hyperparameter_value = input(f"\nEnter the list of value for hyperparameter "
                                                f"'{hyperparameter_name}' for model '{model_name}': ")
                
                hyperparameter_type = self._get_allowed_hyperparameters_types(hyperparameter_name)

                # Setting hyperparameter value specific to each hyperparameter
                self.data['HyperparameterTuningParam'][model_name][hyperparameter_name]["Value"] = \
                    self._process_list_input(hyperparameter_value, hyperparameter_type)
                
                # Displaying available update methods for hyperparameter tuning
                print("\nAvailable hyperparamters update methods with corresponding indices:")
                for index, method in update_methods.items():
                    print(f"Index {index}: {method}")
                
                method_idx = self._process_single_input(
                    input(f"\nEnter the index of corresponding update method for hyperparameters "
                        f"'{hyperparameter_name}' for model '{model_name}': "), 'int', list(update_methods.keys()))
                
                # Setting update method for hyperparameter
                self.data['HyperparameterTuningParam'][model_name][hyperparameter_name]["Method"] = \
                    update_methods[method_idx]
        
        print("\nCustomization of model hyperparameter has been completed successfully.")

    def _display_example_hyperparameter(self, hyperparameter_name):
        """
        DESCRIPTION:
            Function to display example hyperparameter values for different hyperparameters.
            
        PARAMETERS:
            hyperparameter_name:
                Required Argument.
                Specifies the hyperparameter for which example values are required.
                Types: str      
        """
        # Setting example hyperparameter values for different hyperparameters
        if self.cluster:
            example_hyperparameters = {
                'n_clusters': ([2, 3, 4], 'int'),
                'init': (['k-means++', 'random'], 'str'),
                'max_iter': ([100, 300], 'int'),
                'n_components': ([2, 3, 4], 'int'),
                'covariance_type': (['full', 'tied', 'diag', 'spherical'], 'str')
            }
        else:
            example_hyperparameters = {
                'min_impurity' : ([0.1,0.6], 'float'),
                'max_depth' : ([1,5,10], 'int'),
                'min_node_size' : ([1,20,100], 'int'),
                'num_trees' : ([10,50,100], 'int'),
                'k' : ([5,25,100], 'int'),
                'shrinkage_factor': ([0.1,0.5,1.0], 'float'),
                'alpha' : ([0.1,0.5,1.0], 'float'),
                'learning_rate' : (['constant','optimal','invtime','adaptive'], 'str'),
                'initial_eta' : ([0.05,0.1], 'float'),
                'momentum' : ([0.65,0.95], 'float'),
                'iter_num_no_change' : ([25,50,100], 'int'),
                'iter_max' : ([10,100,300], 'int'),
                'batch_size' : ([10,50,100], 'int'),
                'tolerance' : ([0.0001,0.01], 'float'),
                'nesterov' : (['true','false'], 'bool'),
                'intercept' : (['true','false'], 'bool'),
                'local_sgd_iterations' : ([10,25,50], 'int'),
                'iter_num' : ([10,50,100], 'int')
            }

        print(f"\nExample values for hyperparameter '{hyperparameter_name}' :")
        if hyperparameter_name in example_hyperparameters:
            values = example_hyperparameters[hyperparameter_name]

            # Setting example values for hyperparameter
            if all(isinstance(x, str) for x in values[0]):
                example_value = ', '.join(f"'{s}'" for s in values[0])
            else:
                example_value = ', '.join(map(str, values[0]))
            
            # Displaying example values for hyperparameter
            print(f"* Sample value : {example_value}")

            # Displaying example type for hyperparameter
            print(f"* Type : {values[1]}")

