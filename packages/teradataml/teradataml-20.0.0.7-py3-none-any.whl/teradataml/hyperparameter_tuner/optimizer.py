# ##################################################################
#
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Kesavaragavan B (kesavaragavan.b@Teradata.com)
# Secondary Owner: Pankaj Purandare (PankajVinod.Purandare@teradata.com),
#                  Pradeep Garre (pradeep.garre@teradata.com)
#
# This file implements Hyperparameter Tuning feature which is used for 
# model optimization. Optimizer contains following algorithms 
# GridSearch and RandomSearch for hyperaparameter tuning.
#
# ##################################################################

import numpy as np
import pandas as pd
import random
import time
import threading
from itertools import product
from collections import defaultdict
from teradataml import DataFrame, valib, TeradataMlException
from teradataml.common.messages import Messages, MessageCodes
from teradataml.hyperparameter_tuner.utils import _ProgressBar
from teradataml.utils.utils import _AsyncDBExecutor
from teradataml.utils.validators import _Validators
from teradataml.options.configure import configure
from teradataml.common.constants import TeradataConstants


class _BaseSearch: 
    """Base class for hyperparameter optimization."""
    
    def __init__(self, func, params):
        """
        Constructor for _BaseSearch.
        PARAMETERS:
            func:
                Required Argument.
                Specifies a teradataml analytic function.  
                Types: 
                    teradataml Analytic Functions
                        * Advanced analytic functions
                        * UAF
                        * VAL
                    Refer to display_analytic_functions() 
                    function for list of functions.

            params:
                Optional Argument.
                Specifies the parameter(s) of a teradataml function.
                Types: dict
        
        RAISES:
            TeradataMlException, TypeError, ValueError

        RETURNS:
            None

        EXAMPLES:

            >>> # Let's initialize parameters for BaseSearch.
            >>> func_params = {"data" : antiselect_input,
                               "exclude" : (['rowids','orderdate'], ['orderdate'])}

            >>> # Create instance of _BaseSearch.
            >>> bs_obj = _BaseSearch(func=Antiselect, params=func_params)
        """

        # Argument validation.
        # Validate argument types.
        awu_matrix = []
        awu_matrix.append(["params", params, True, dict, True])
        _Validators._validate_function_arguments(awu_matrix)

        # Model trainer function supports evaluation.
        self._SQLE_TRAINABLE_FUNCS = {"DecisionForest", "GLM", "GLMPerSegment",
                                      "KMeans", "KNN", "OneClassSVM", "SVM", "XGBoost", 
                                      "NaiveBayesTextClassifierTrainer"}
        
        # Data passed in fit method is sampled and internally test dataset 
        # is passed with following argument name for predictions and evaluation.
        self._TRAINABLE_FUNCS_DATA_MAPPER = {"DecisionForest": "newdata", "GLM": "newdata", 
                                             "GLMPerSegment": "newdata", "KMeans": "data", 
                                             "KNN": "test_data", "OneClassSVM": "newdata", 
                                             "SVM": "newdata", "XGBoost": "newdata", 
                                             "NaiveBayesTextClassifierTrainer": "newdata",
                                             "DecisionTree": "data", "KMeans": "data", 
                                             "LinReg": "data", "LogReg": "data", "PCA": "data",
                                             "LinearRegression": "data", "Lasso": "data",
                                             "Ridge": "data", "ARDRegression": "data",
                                             "BayesianRidge": "data", "TweedieRegressor": "data",
                                             "TheilSenRegressor": "data", "SGDRegressor": "data",
                                             "RidgeCV": "data", "RANSACRegressor": "data",
                                             "PoissonRegressor": "data", "PassiveAggressiveRegressor": "data",
                                             "OrthogonalMatchingPursuitCV": "data", "OrthogonalMatchingPursuit": "data",
                                             "MultiTaskLassoCV": "data", "MultiTaskLasso": "data",
                                             "MultiTaskElasticNetCV": "data", "MultiTaskElasticNet": "data",
                                             "LassoLarsIC": "data", "LassoLarsCV": "data", "LassoLars": "data",
                                             "LassoCV": "data", "LarsCV": "data", "Lars": "data",
                                             "HuberRegressor": "data", "GammaRegressor": "data",
                                             "ElasticNetCV": "data", "ElasticNet": "data",
                                             "LogisticRegression": "data", "RidgeClassifier": "data",
                                             "RidgeClassifierCV": "data", "SGDClassifier": "data", 
                                             "PassiveAggressiveClassifier": "data", "Perceptron": "data",
                                             "LogisticRegressionCV": "data"}

        self._UAF_TRAINABLE_FUNCS = {"ArimaEstimate", "LinearRegr", "MAMean",
                                     "MultivarRegr", "SimpleExp"}
        self._VAL_TRAINABLE_FUNCS = {"DecisionTree", "KMeans", "LinReg", "LogReg", "PCA"}

        # Unsupervised model trainer functions. These models are suitable
        # for prediction rather than evaluation.
        self.__US_TRAINABLE_FUNCS = {"KMeans", "OneClassSVM", "PCA"}

        # Evaluation approach for model evaluable functions were "True" means
        # higher the score is better, and vice versa.
        self.__func_comparator =  {'MAE': False,
                                   'MSE': False,
                                   'MSLE': False,
                                   'MAPE': False,
                                   'RMSE': False,
                                   'RMSLE': False,
                                   'ME': False,
                                   'R2': True,
                                   'EV': True,
                                   'MPE': False,
                                   'MPD': False,
                                   'MGD': False,
                                   'ACCURACY': True,
                                   'MICRO-PRECISION': True,
                                   'MICRO-RECALL': True,
                                   'MICRO-F1': True,
                                   'MACRO-PRECISION': True,
                                   'MACRO-RECALL': True,
                                   'MACRO-F1': True,
                                   'WEIGHTED-PRECISION': True,
                                   'WEIGHTED-RECALL': True,
                                   'WEIGHTED-F1': True,
                                   'SILHOUETTE': True,
                                   'CALINSKI': True,
                                   'DAVIES': True}
        
        # OpenSource ML function comparator (excluding MPD, MGD, MTD, RMSE, RMSLE)
        self.__osml_func_comparator = {k: v for k, v in self.__func_comparator.items() 
                                       if k not in ['MPD', 'MGD', 'MTD', 'RMSE', 'RMSLE']}
        
        # Linear model categorization lists for sklearn models
        self._LINEAR_REGRESSION_MODELS = {
            "ARDRegression", "BayesianRidge", "TweedieRegressor", "TheilSenRegressor", 
            "SGDRegressor", "RidgeCV", "Ridge", "RANSACRegressor", "PoissonRegressor", 
            "PassiveAggressiveRegressor", "OrthogonalMatchingPursuitCV", "OrthogonalMatchingPursuit", 
            "MultiTaskLassoCV", "MultiTaskLasso", "MultiTaskElasticNetCV", "MultiTaskElasticNet", 
            "LinearRegression", "LassoLarsIC", "LassoLarsCV", "LassoLars", "LassoCV", 
            "Lasso", "LarsCV", "Lars", "HuberRegressor", "GammaRegressor", 
            "ElasticNetCV", "ElasticNet"
        }

        self._LINEAR_CLASSIFICATION_MODELS = {
            "SGDClassifier", "RidgeClassifierCV", "RidgeClassifier", "Perceptron", 
            "PassiveAggressiveClassifier", "LogisticRegressionCV", "LogisticRegression"
        }

        self._CLUSTERING_MODELS = {
            "KMeans", "GaussianMixture"
        }
        self.__func = func
        self.__params = params
        # "self.__best_model" contains best model.
        self.__best_model = None
        # "self.__evaluation_metric" contains evaluation metric considered for 
        # evaluation.
        self.__evaluation_metric = None
        # "self.__eval_params" contains evaluation parameter will be used for
        # trained model evaluation.
        self.__eval_params = None
        # "self.__early_stop" contains expected evaluation value considered for 
        # evaluation. 
        self.__early_stop = None
        # "self._parameter_grid" contains parameter combinations.
        self._parameter_grid = None
        # "self.__best_score_" contains best model score.
        self.__best_score_ = None
        # "self.__best_model_id" contains best model ID.
        self.__best_model_id = None
        # "self.__best_params_" contains best model parameters. 
        self.__best_params_ = None
        # "__model_stats" contains "model_id" and corresponding evaluation 
        # metrics as a DataFrame.
        self.__model_stats = None
        # "self.__models" contains "model_id", "params", "accuracy", and "status"
        # will be stored as a DataFrame.
        self.__models = None
        # HPT complete execution results including "model_stats" informations recorded.
        self.__model_eval_records = list()
        # "self.__trained_models" is an internal attribute to keep track of 
        # "model_id" and the associated function objects.
        self.__trained_models = dict()
        # "__train_data" contains training data for model trainer and unsupervised 
        # model trainer functions.
        self.__train_data = None
        # "__test_data" contains testing data for model trainer function.
        self.__test_data = None
        # Default model will be used for predict and evaluate after HPT execution.
        self.__default_model = None
        # 'self.__is_finite' will indicate whether the chosen '__evaluation_metric'
        # contains 'NaN', '-inf' or 'inf' values. 
        self.__is_finite = True
        # '__is_fit_called' specifies whether a fit method is called by user. 
        # This helps 'is_running' method to identify the model training state.
        self.__is_fit_called = False
        # "__model_trainer_input_data" contains the model trainer data when input data is passed along with params. 
        self.__model_trainer_input_data = None
        # Constant name for data identifier.
        self.__DATA_ID = "data_id"
        # '__progress_bar' holds progress bar obj when verbose is set.
        self.__progress_bar = None
        # '__model_err_records' holds error messages of failed model.
        self.__model_err_records = dict()
        # '__parallel_stop_event' is used to stop threads in parallel execution.
        self.__parallel_stop_event = None
        
        
        # Set the function feature type and supported functionality.
        self.__is_sqle_function = False
        self.__is_uaf_function = False 
        self.__is_val_function = True if "valib" in str(self.__func.__module__)\
                                      else False
        self.__is_opensource_model = False
        self.__is_clustering_model = False
        self.__is_regression_model = False
        self.__is_classification_model = False
        self.model_id_counter = {}
        
        # Import sklearn wrapper class for proper type checking
        from teradataml.opensource._sklearn import _SkLearnObjectWrapper
        
        if hasattr(func, "modelObj") and isinstance(func, _SkLearnObjectWrapper):
            self.__is_opensource_model = True
            self.__is_trainable = True
            self.__is_evaluatable = True
            self.__is_predictable = True

            # Set the function name and class
            self.__func_name = func.modelObj.__class__.__name__   # e.g., 'KMeans'
            self.__func = func.__class__
            if self.__func_name in self._CLUSTERING_MODELS:
                self.__is_clustering_model = True
                self.__is_evaluatable = False
            elif self.__func_name in self._LINEAR_REGRESSION_MODELS:
                self.__is_regression_model = True
            elif self.__func_name in self._LINEAR_CLASSIFICATION_MODELS:
                self.__is_classification_model = True
        else:
            self.__func_name = func._tdml_valib_name if "_VALIB" in str(func.__class__) \
                                                     else func.__name__
            if self.__func_name in self._VAL_TRAINABLE_FUNCS and self.__is_val_function:
                # TODO: Enable these feature once merge model supports VAL functions.
                # This case is for VAL model trainer functions.
                self.__is_trainable = self.__is_evaluatable = \
                                    self.__is_predictable = False
            elif self.__func_name in self._UAF_TRAINABLE_FUNCS:
                # TODO: Enable these feature once merge model supports UAF functions.
                # This case is for UAF model trainer functions.
                self.__is_uaf_function = self.__is_trainable = \
                                        self.__is_evaluatable = False
                self.__is_predictable = False
            elif self.__func_name in self._SQLE_TRAINABLE_FUNCS:
                # This case is for SQLE model trainer functions.
                self.__is_sqle_function = self.__is_trainable = \
                self.__is_evaluatable = self.__is_predictable = True 
            else:
                # This case is for non-model trainer functions.
                self.__is_trainable = self.__is_evaluatable = \
                                    self.__is_predictable = False
        
            self.__is_evaluatable = False if not self.__is_evaluatable or \
                                    self.__func_name in self.__US_TRAINABLE_FUNCS else \
                                    True
        # Set train routine based on model type.
        # Non-model trainer routine is used for unsupervised model function training.
        self._execute_fit = self.__model_trainer_routine if self.__is_trainable \
                            and (self.__is_evaluatable or self.__is_clustering_model) else \
                            self.__non_model_trainer_routine

        # Utility lambda functions.
        # '_is_best_metrics' function is to check whether current trained model 
        # evaluation value is better than existing "self.__best_model" score.
        self._is_best_metrics = lambda curr_score: curr_score > self.__best_score_ \
                                if self.__func_comparator[self.__evaluation_metric] \
                                else curr_score < self.__best_score_
        # '_is_early_stoppable' function is to check whether HPT execution reached
        # "self.__early_stop" value.
        self._is_early_stoppable = lambda : self.__best_score_ >= self.__early_stop \
                                   if self.__func_comparator[self.__evaluation_metric] \
                                   else self.__best_score_ <= self.__early_stop
        
        # '_is_time_stoppable' function is to check whether HPT execution reached self.__timeout value.
        self._is_time_stoppable = lambda : True if time.time() - self.__start_time >= self.__timeout else False
        
        # Special case comparator for "MPE" metrics.
        # When "curr_score" argument is 'None' then lambda function checks 
        # for '_is_early_stoppable'. Otherwise, it checks for '_is_best_metrics'.
        self._spl_abs_comparator = lambda curr_score=None: \
                                   abs(curr_score) < abs(self.__best_score_) \
                                   if curr_score is not None else \
                                   abs(self.__best_score_) <= abs(self.__early_stop)

        # '_generate_model_name' function is used to create new model name 
        # for every iteration.
        self._generate_model_name = lambda iter: "{}_{}".format(\
                                    self.__func_name.upper(), str(iter))
        
        # '__is_model_training_completed' function to check whether all models are 
        # executed based on model evaluation records. Function returns true, when all
        # models are executed and evaluation reports are updated. Otherwise, 
        # returns false.
        self.__is_model_training_completed = lambda : self.__is_fit_called and \
                                                     len(self.__model_eval_records) < \
                                                     len(self._parameter_grid)

        # '_generate_dataframe_name' function is used to create new dataframe ID 
        # for given iteration.
        self._generate_dataframe_name = lambda df_name, iter: "{}_{}".format(df_name, str(iter))

        # '_get_train_data_arg' function is used to return model trainer function 
        # train argument name.
        self._get_model_trainer_train_data_arg = lambda : "train_data" if \
                                                 self.__func_name == "KNN" else "data"

        # '_get_predict_column' function is used to generate prediction column name.
        self._get_predict_column = lambda: f"{self.__func_name.lower()}_predict_1"

        if self.__is_trainable and "data" in self.__params:
            data = self.__params.pop("data")
            self.__validate_model_trainer_input_data_argument(data, False)
            self.__model_trainer_input_data = data


    def set_parameter_grid(self):
        """
        DESCRIPTION:
            Set the value of the attribute _parameter_grid.

        RETURNS:
            None

        EXAMPLES:
            >>> self.set_parameter_grid()
        """
        self._parameter_grid = self.__populate_parameter_grid()
    def get_parameter_grid(self):
        """
        DESCRIPTION:
            Returns the value of the attribute _parameter_grid.

        RETURNS:
            dict

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve parameter grid.
            >>> optimizer_obj.get_parameter_grid()
                [{'param': {'input_columns': ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 
                                             'Population', 'AveOccup', 'Latitude', 'Longitude'], 
                            'response_column': 'MedHouseVal', 'model_type': 'regression', 
                            'batch_size': 75, 'iter_max': 100, 'lambda1': 0.1, 'alpha': 0.5, 
                            'iter_num_no_change': 60, 'tolerance': 0.01, 'intercept': False,
                            'learning_rate': 'INVTIME', 'initial_data': 0.5, 'decay_rate': 0.5, 
                            'momentum': 0.6, 'nesterov': True, 'local_sgd_iterations': 1, 
                            'data': '"ALICE"."ml__select__1696593660430612"'}, 
                 'data_id': 'DF_0'}, 
                 {'param': {'input_columns': ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 
                                             'Population', 'AveOccup', 'Latitude', 'Longitude'], 
                            'response_column': 'MedHouseVal', 'model_type': 'regression', 
                            'batch_size': 75, 'iter_max': 100, 'lambda1': 0.1, 'alpha': 0.5, 
                            'iter_num_no_change': 60, 'tolerance': 0.01, 'intercept': False, 
                            'learning_rate': 'INVTIME', 'initial_data': 0.5, 'decay_rate': 0.5, 
                            'momentum': 0.6, 'nesterov': True, 'local_sgd_iterations': 1, 
                            'data': '"ALICE"."ml__select__1696593660430612"'}, 
                 'data_id': 'DF_1'}]
        """
        return self._parameter_grid

    @property
    def models(self):
        """
        DESCRIPTION:
            Returns the generated models metadata.

        RETURNS:
            pandas DataFrame

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve models metadata.
            >>> optimizer_obj.models
                  MODEL_ID DATA_ID                                         PARAMETERS STATUS       MAE
                0    SVM_3    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                1    SVM_0    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                2    SVM_1    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                3    SVM_2    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                4    SVM_4    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                5    SVM_5    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772

        """
        # All the models are stored in a dictionary '__model_eval_records'. Since 
        # "models" return a pandas DataFrame, one has to construct pandas DataFrame
        # from "__models". This construction should be done only if it is 
        # appropriate, i.e., when a new model is pushed to "__model_eval_records", 
        # only then construct the pandas Dataframe for models. Otherwise, store 
        # it and use it. Check a new model record is generated or not by 
        # comparing the number of model records present in '__model_eval_records' 
        # with existing number of records in '__models'.
        _is_models_updated = self.__models is None or \
                             len(self.__model_eval_records) != self.__models.shape[0]

        # Update the '__models' when model records are updated.
        if _is_models_updated :
            # Set the '__models' variable with models metadata.

            # Set the columns based on teradataml analytics function type.
            _df_cols = ["MODEL_ID", "PARAMETERS", "STATUS"]
            
            if self.__is_trainable:
                _df_cols.insert(1, self.__DATA_ID.upper())

            # Include evaluation metrics for model trainer functions.
            if self.__evaluation_metric:
                _df_cols.append(self.__evaluation_metric)

            # Replace the teradataml DataFrame with 'table_name'.
            # Convert "PARAMETERS" from dictionary to string datatype. 
            for index, records in enumerate(self.__model_eval_records):
                # Check whether "PARAMETERS" record contains a dictionary parameter. 
                if isinstance(records["PARAMETERS"], dict):
                    # Replace the dataframe with table name and typecast the type
                    # of model training parameters to string.
                    for key, value in records["PARAMETERS"].items():
                        if isinstance(value, DataFrame):
                            records["PARAMETERS"][key] = \
                                value._table_name
                    records["PARAMETERS"] = str(records["PARAMETERS"])

            # Create pandas dataframe for recorded evaluation report.
            self.__models = pd.DataFrame(self.__model_eval_records, 
                                         columns=_df_cols)

        return self.__models

    @property
    def best_score_(self):
        """
        DESCRIPTION:
            Returns the best score of the model out of all generated models.
            Note:
                "best_score_" is not supported for non-model trainer functions.

        RETURNS:
            String representing the best score.

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the best score.
            >>> optimizer_obj.best_score_
                2.060386
        """
        return self.__best_score_

    @property
    def best_model_id(self):
        """
        DESCRIPTION:
            Returns the model id of the model with best score.
            Note:
                "best_model_id" is not supported for non-model trainer functions.

        RETURNS:
            String representing the best model id.

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the best model id.
            >>> optimizer_obj.best_model_id
                'SVM_2'
        """
        return self.__best_model_id

    @property
    def best_params_(self):
        """
        DESCRIPTION:
            Returns the parameters used for the model with best score.
            Note:
                "best_params_" is not supported for non-model trainer functions.

        RETURNS:
            dict

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the best parameters.
            >>> optimizer_obj.best_params_
                {'input_columns': ['MedInc', 'HouseAge', 'AveRooms', 
                                  'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude'], 
                 'response_column': 'MedHouseVal', 'model_type': 'regression', 
                 'batch_size': 50, 'iter_max': 301, 'lambda1': 0.1, 'alpha': 0.5, 
                 'iter_num_no_change': 60, 'tolerance': 0.01, 'intercept': False, 
                 'learning_rate': 'INVTIME', 'initial_data': 0.5, 'decay_rate': 0.5, 
                 'momentum': 0.6, 'nesterov': True, 'local_sgd_iterations': 1, 
                 'data': '"ALICE"."ml__select__1696595493985650"'}
        """
        return self.__best_params_

    @property
    def best_model(self):
        """
        DESCRIPTION:
            Returns the best trained model obtained from hyperparameter tuning.
            Note:
                "best_model" is not supported for non-model trainer functions.

        RETURNS:
            object of trained model.

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the best model.
            >>> optimizer_obj.best_model
                ############ output_data Output ############

                   iterNum      loss       eta  bias
                0        3  2.060386  0.028868   0.0
                1        5  2.055509  0.022361   0.0
                2        6  2.051982  0.020412   0.0
                3        7  2.048387  0.018898   0.0
                4        9  2.041521  0.016667   0.0
                5       10  2.038314  0.015811   0.0
                6        8  2.044882  0.017678   0.0
                7        4  2.058757  0.025000   0.0
                8        2  2.065932  0.035355   0.0
                9        1  1.780877  0.050000   0.0


                ############ result Output ############

                                         predictor    estimate       value
                attribute
                 7                        Latitude    0.155095        None
                -9         Learning Rate (Initial)    0.050000        None
                -17                   OneClass SVM         NaN       FALSE
                -14                        Epsilon    0.100000        None
                 5                      Population    0.000000        None
                -12                       Nesterov         NaN        TRUE
                -5                             BIC   73.297397        None
                -7                           Alpha    0.500000  Elasticnet
                -3          Number of Observations   55.000000        None
                 0                     (Intercept)    0.000000        None
                
        """
        return self.__best_model
    
    @property
    def best_sampled_data_(self):
        """
        DESCRIPTION:
            Returns the best sampled data used for training the best model.
            Note:
                "best_sampled_data_" is not supported for non-model trainer functions.

        RETURNS:
            list of DataFrames.

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the best sampled data.
            >>> optimizer_obj.best_sampled_data_
                [{'data':       id  MedHouseVal    MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude
                0   5233        0.955 -0.895906  0.680467 -0.387272  -0.202806   -0.125930  2.130214 -0.754303   0.653775
                1  10661        3.839  2.724825 -1.258313  0.876263  -1.142947   -0.751004 -0.187396 -0.878298   0.852744
                2  10966        1.896  0.057849  0.343287 -0.141762  -0.664624   -0.095545  0.588981 -0.829586   0.815727
                3   3687        1.741 -0.383816 -1.679787 -0.849458   0.108000    0.718354  1.083500 -0.630308   0.593621
                4   7114        2.187 -0.245392  0.258993  0.225092  -0.205781   -0.171508 -0.035650 -0.763160   0.755573
                5   5300        3.500 -0.955800 -1.005429 -1.548811  -0.130818    2.630473 -0.601956 -0.696734   0.556604
                6    686        1.578 -0.152084 -0.078186 -0.625426  -0.513581   -0.685892 -0.533101  0.906345  -1.141575
                7   9454        0.603 -1.109609 -0.499660  0.355748   0.379188   -0.364674 -0.356799  1.827451  -1.655193
                8   5202        1.000 -0.307539  1.101940 -0.379623  -0.570271   -0.141123  0.595366 -0.754303   0.635266
                9   5769        2.568 -0.413546  0.343287 -0.922324  -0.028824    1.165456  0.031374 -0.656879   0.626012}, 
                {'newdata':      id  MedHouseVal    MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude
                0  1754        1.651 -0.026315  0.596172  0.454207  -0.027273    0.068320 -0.082765  1.017055  -1.234118
                1  3593        2.676  1.241775  0.090403  1.024283  -0.367626   -0.045626  0.252048 -0.621452   0.542722
                2  7581        1.334 -0.714880 -1.258313 -0.604140  -0.259612    3.058041  0.857406 -0.776445   0.658402
                3  8783        2.500 -0.170156  0.596172  0.163717   0.398242   -0.668529 -0.728130 -0.820729   0.621385
                4  5611        1.587 -0.712366 -0.415366 -1.275716   0.012960    0.860515  0.764870 -0.820729   0.639893
                5   244        1.117 -0.605796  1.101940 -0.160367   0.426668    1.022209  1.041018  0.946201  -1.187846}]
        """
        return self.__sampled_df_mapper[self.__best_data_id]

    @property
    def best_data_id(self):
        """
        DESCRIPTION:
            Returns the "data_id" of a sampled data used for training the best model.
            Note:
                "best_data_id" is not supported for non-model trainer functions.

        RETURNS:
            String representing the best "data_id"

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the best data id.
            >>> optimizer_obj.best_data_id
                DF_0
        """
        return self.__best_data_id

    @property
    def model_stats(self):
        """
        DESCRIPTION:
            Returns the model statistics of the model with best score.

        RETURNS:
            pandas DataFrame.

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the model stats.
            >>> optimizer_obj.model_stats
                  MODEL_ID DATA_ID                                         PARAMETERS STATUS       MAE
                0    SVM_3    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772`
                1    SVM_0    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                2    SVM_1    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                3    SVM_2    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                4    SVM_4    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                5    SVM_5    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772`

        """

        if not (self.__is_evaluatable or self.__is_clustering_model):
            # Raise error when "model_stats" attribute accessed for non-executable 
            # functions.
            err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                       "retrieve 'model_stats' attribute", 
                                       "'model_stats' attribute not applicable "\
                                       "for non-evaluatable function.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        elif len(self.__model_eval_records) == 0:
            # Raise error when no records are found.
            err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                       "retrieve 'model_stats' attribute", \
                                       "No records found in 'model_stats' " \
                                       "attribute.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)


        # All the models records are stored in a dictionary '__model_eval_records'. 
        # Since "model_stats" return a pandas DataFrame, one has to construct 
        # pandas DataFrame from "__model_stats". This construction should be done 
        # only if it is appropriate, i.e., when a new model record is pushed to 
        # "__model_eval_records", only then construct the pandas Dataframe for 
        # model_stats. Otherwise, store it and use it. Check a new model record is 
        # generated or not by comparing the number of model records present in 
        # '__model_eval_records' with existing number of records in '__model_stats'.
        _is_model_stats_updated = self.__model_stats is None or \
                                  len(self.__model_eval_records) != \
                                  self.__model_stats.shape[0]

        # Update the '__models' when model stats records are updated.
        if _is_model_stats_updated:
            # Set the '__model_stats' with model evaluation report.

            # Exclude "models" attribute specific columns.
            _df_cols = ["PARAMETERS", "STATUS", self.__DATA_ID.upper()]

            # Create pandas dataframe for recorded evaluation report by excluding
            # 'PARAMETERS' and 'STATUS' columns.
            self.__model_stats = pd.DataFrame(self.__model_eval_records).drop(\
                                 columns=_df_cols, axis=1)

        return self.__model_stats

    def is_running(self):
        """
        DESCRIPTION:
            Check whether hyperparameter tuning is completed or not. Function 
            returns True when execution is in progress. Otherwise it returns False.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            bool
        
        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the model execution status.
            >>> optimizer_obj.is_running() 
                False
        """
        # Check all models are executed based on model training records count.
        # Note: Model training records is updated at the end of execution and 
        # list append operation is thread-safe. Hence, following method works for 
        # both parallel and sequential execution.
        return self.__is_model_training_completed()

    def _add_data_label(self, arg_name=None):
        """
        DESCRIPTION:
            Internal function to label the teradataml DataFrame for model trainer 
            functions. Labels will be added for input data except dictionary 
            formatted DataFrame. Since, Dictionary formatted DataFrame contains 
            custom data labels.

        PARAMETERS:
            arg_name:
                Optional Argument.
                Specifies the model trainer argument name for unsupervised 
                model trainer functions.
                Notes:
                    * "arg_name" argument is not supported for model-trainer functions
                      (evaluatable functions). Since, argument names are 
                      added in data sampling method.
                    * "arg_name" is added to training data of unsupervised 
                      model-trainer functions.
                Types: str

        RETURNS:
            dictionary

        RAISES:
            None

        EXAMPLES:
            >>> # Example 1: tuple of DataFrame is passed.
            >>> # Assign DataFrames to be labeled.
            >>> self.__model_trainer_input_data = (DF1, DF2)
            >>> # Call '_add_data_label' method for labelling.
            >>> self._add_data_label()
               {'DF_0': DF1, 'DF_1': DF2}   
            
            >>> # Example 2: Dictionary of DataFrame is passed.
            >>> #            This test case is specific to unsupervised
            >>> #            model trainer functions.
            >>> # Assign labelled dataframes.
            >>> self.__model_trainer_input_data = {"data-1":DF1, "data-2":DF2}
            >>> # Call '_add_data_label' method to add argument name and reframe 
            >>> # the structure into generic labelled format.
            >>> self._add_data_label(arg_name="data")
               {"data-1": {'data': DF1}, "data-2": {'data': DF2} }

            >>> # Example 3: Tuple of DataFrame is passed.
            >>> #            This test case is specific to unsupervised
            >>> #            model trainer functions.
            >>> # Assign labelled dataframes.
            >>> self.__model_trainer_input_data = (DF1, DF2)
            >>> # Call '_add_data_label' method to add argument name and data 
            >>> # labels. Resulting structure contains unique data labels 
            >>> # and dictionary formatted.
            >>> # Assign labels for dataframes with data argument name.
            >>> self._add_data_label(arg_name="data")
               {"DF_0": {'data': DF1}, "DF_1": {'data': DF2} }

            >>> # Example 4: Single DataFrame is passed.
            >>> # Assign DataFrames to be labeled.
            >>> self.__model_trainer_input_data = DF1
            >>> # Call '_add_data_label' method for labelling.
            >>> self._add_data_label()
               {'DF_0': DF1}               
        """

        _labeled_data = {}
        
        if isinstance(self.__model_trainer_input_data, DataFrame):
            # Provide default data identifier "DF_0", when 
            # '__model_trainer_input_data' contains single DataFrame.
            _df_id = self._generate_dataframe_name("DF",0)
            # Record labeled data using unique data identifier.
            # Note: "arg_name" is added to data of unsupervised model-trainer 
            #       functions while adding data identifier.
            _labeled_data[_df_id] = self.__model_trainer_input_data if arg_name \
                                    is None else {arg_name: \
                                    self.__model_trainer_input_data}
        elif isinstance(self.__model_trainer_input_data, tuple):
            # Assign default data identifier sequence, when 
            # '__model_trainer_input_data' contains tuples of DataFrame.
            for _index, _data in enumerate(self.__model_trainer_input_data):
                _df_id = self._generate_dataframe_name("DF",_index)
                # Record labeled data using unique data identifier.
                # Note: "arg_name" is added to data of unsupervised model-trainer 
                #       functions while adding data identifier.
                _labeled_data[_df_id] = _data if arg_name is None else \
                                        {arg_name: _data}
        elif isinstance(self.__model_trainer_input_data, dict) and arg_name:
            # This condition updates unsupervised model trainer functions data.
            # Assign "arg_name" to all the data items when 
            # '__model_trainer_input_data' contains dictionary format DataFrame.
            # Note: Dictionary keys specifies data identifier (labels) and 
            #       values specifies DataFrame (training data).
            for _data_id in self.__model_trainer_input_data:
                _arg_name_added = {arg_name: self.__model_trainer_input_data[_data_id]}
                _labeled_data[_data_id] = _arg_name_added

        return _labeled_data

    def __perform_train_test_sampling(self, data, frac, stratify_column=None, 
                                      sample_id_column=None, sample_seed=None):
        """
        DESCRIPTION:
            Internal function to perform train test split for multiple DataFrame.
            Train Test split is use 80/20 method for sampling train and test 
            DataFrame. After sampling, parameter grid is updated with the train
            and test DataFrame. 

            Notes:
                * Sampled DataFrames are stored in following format.
                    [<Train_DF>, <Test_DF>]
                * Each sampled DataFrame mapped with unique data identifier.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the teradataml DataFrame needs to be sampled.
                Types: dictionary of DataFrame.

            frac:
                Required Argument.
                Specifies the split percentage of rows to be sampled for training 
                and testing dataset. "frac" argument value must range between (0, 1).
                Notes: 
                    * This "frac" argument is not supported for non-model trainer 
                      function.
                    * The "frac" value is considered as train split percentage and 
                      The remaining percentage is taken into account for test splitting.
                Types: float
            
            sample_seed:
                Optional Argument.
                Specifies the seed value that controls the shuffling applied
                to the data before applying the Train-Test split. Pass an int for 
                reproducible output across multiple function calls.
                Notes:
                    * When the argument is not specified, different
                      runs of the query generate different outputs.
                    * It must be in the range [0, 2147483647]
                    * Seed is supported for stratify column.
                Types: int

            stratify_column:
                Optional Argument.
                Specifies column name that contains the labels indicating
                which data needs to be stratified for TrainTest split. 
                Notes:
                    * seed is supported for stratify column.
                Types: str
            
            sample_id_column:
                Optional Argument.
                Specifies the input data column name that has the
                unique identifier for each row in the input.
                Note:
                    * Mandatory when "sample_seed" argument is present.
                Types: str

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> _labeled_df = {'DF_0': DF1, 'DF_1': DF2}
            >>> # Sample the labeled DataFrame.
            >>> self.__perform_train_test_sampling(_labeled_df)
                {'DF_0': [{'data':DF1_Train}, {'newdata':DF1_Test}],
                'DF_1': [{'data':DF2_Train}, {'newdata':DF2_Test}]}
        """
        # Validate the range of "frac" argument value.
        _Validators._validate_argument_range(arg=frac, arg_name='frac', 
                                             lbound=0.0, ubound=1.0)

        self.__sampled_df_mapper = {}
        for _data_id in data:
            # Setup train, test input data argument name according to function.
            # Apart from "KNN" function all other SQLE, and VAL function takes "data" 
            # as training input data argument.
            train_data_arg = self._get_model_trainer_train_data_arg()
            # Test input data argument name varies for all function. So retrieve
            # the stored information.
            test_data_arg = self._TRAINABLE_FUNCS_DATA_MAPPER[self.__func_name]

            # Perform sampling based on given "frac" value.
            # Consider the "frac" value as train percentage and the remaining 
            # as test percentage for train-test-split.
            train_test_sample = data[_data_id].sample(frac=[frac, round(1 - frac, 2)], 
                                                      stratify_column=stratify_column,
                                                      id_column=sample_id_column,
                                                      seed=sample_seed)
            # Represent the sample. Otherwise, split consistency is lost.
            train_test_sample.materialize()

            _sample_id = "sampleid"
            _split_value = [1, 2] 

            # Create train DataFrame.
            _train_data = train_test_sample[\
                                train_test_sample[_sample_id] == _split_value[0]].drop(\
                                _sample_id, axis = 1)
            
            # Create test DataFrame.
            _test_data = train_test_sample[\
                            train_test_sample[_sample_id] == _split_value[1]].drop(\
                            _sample_id, axis = 1)

            # Represent train and test dataset.
            _train_data.materialize()
            _test_data.materialize()
            
            # Update train and test dataset using data id with train and test 
            # arguments. Unique Data-structure to store train and test sampled 
            # data for model trainer functions.
            self.__sampled_df_mapper[_data_id] = [{train_data_arg:_train_data}, 
                                                 {test_data_arg:_test_data}]

    def __update_model_parameters(self):
        """
        DESCRIPTION:
            Internal function to update the parameter grid with multiple 
            dataframe using unique data identifiers. This function perform 
            cartesian products on parameter grid and data identifiers.
            Hence, Hyperparameter tuning is performed on all DataFrame.

            Notes:
                * This function is only applicable for model trainer functions
                  (supervised, and unsupervised models).
                * '_sampled_df_mapper' variable must contain labeled data before
                  updating parameter grid. Since, unique data identifier is added
                  to all parameters present in parameter grid.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> _labeled_df = {'DF_0': DF1, 'DF_1': DF2}
            >>> # Sample the labeled DataFrame.
            >>> self.__perform_train_test_sampling(_labeled_df)
                {'DF_0': [{'data':DF1_Train}, {'newdata':DF1_Test}],
                'DF_1': [{'data':DF2_Train}, {'newdata':DF2_Test}]}
            >>> self.__update_model_parameters()
                [
                    {'param': {'input_columns': ['age', 'survived', 'pclass'], 
                    'response_column': 'fare', 'max_depth': 10, 'lambda1': 1000.0, 
                    'model_type': 'regression', 'seed': -1, 'shrinkage_factor': 0.1, 
                    'iter_num': 2}, 
                    'data_id': 'DF_0'}, 
                    {'param': {'input_columns': ['age', 'survived', 'pclass'], 
                    'response_column': 'fare', 'max_depth': 10, 'lambda1': 1000.0, 
                    'model_type': 'regression', 'seed': -1, 'shrinkage_factor': 0.1, 
                    'iter_num': 50}, 
                    'data_id': 'DF_1'}
                ]
        """
        # Get data identifiers.
        _model_ids = self.__sampled_df_mapper.keys()    
        # Update '_parameter_grid' with data identifiers by performing 
        # cartesian product.
        self._parameter_grid = [{"param":param[0] , self.__DATA_ID:param[1]} for \
                                param in product(self._parameter_grid, _model_ids)]
        
    def __validate_model_trainer_input_data_argument(self, data, is_optional_arg=True):
        """
        DESCRIPTION:
            Internal function to validate input data of model trainer function.
            This function validates single DataFrame, multiple DataFrame, and 
            multiple DataFrame with user-defined data labels.
            Notes:
                * This function is only applicable for model trainer functions
                  (supervised, and unsupervised models).
            
        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame for model trainer function.
                Notes:
                    * "data" is a required argument for model trainer functions.
                    * "data" is ignored for non-model trainer functions.
                    * "data" can be contain single DataFrame or multiple DataFrame.
                    * Multiple DataFrame must be specified using tuple or Dictionary
                      as follow.
                      * Tuples:
                            gs.fit(data=(df1, df2), **eval_params)

                      * Dictionary:
                            gs.fit(data={"data-1":df1, "data-2":df2}, **eval_params)
                Types: teradataml DataFrame, dictionary, tuples
            
            is_optional_arg:
                Optional Argument.
                Specifies whether passed data argument value is a optional 
                argument or not.
                Default Value: True
                Types: bool

        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> self.__validate_model_trainer_input_data_argument(data, 
                    _is_optional_arg)

        """
        # Validate "data" for model trainer functions.
        arg_info_matrix = []
        if isinstance(data, tuple):
            # Validate all DataFrames present in tuples. 
            for _data in data:
                arg_info_matrix.append(["data", _data, is_optional_arg, (DataFrame)])
        elif isinstance(data, dict):
            # Validate all DataFrames present in dictionary format.
            for _data_id in data:
                arg_info_matrix.append(["data", data[_data_id], is_optional_arg, (DataFrame)])
        else:
            # Validate DataFrames.
            arg_info_matrix.append(["data", data, is_optional_arg, (DataFrame)])
        _Validators._validate_function_arguments(arg_info_matrix)
    
    def _regression_metrics(self, y_true, y_pred):
        from teradataml import td_sklearn as skl
        
        ME = skl.max_error(y_true=y_true, y_pred=y_pred)
        
        MAE = skl.mean_absolute_error(y_true=y_true, y_pred=y_pred)
        
        MSE = skl.mean_squared_error(y_true=y_true, y_pred=y_pred, squared=False)
        
        try:
            MSLE = skl.mean_squared_log_error(y_true=y_true, y_pred=y_pred)
        except:
            MSLE = "NA"
        
        MAPE = skl.mean_absolute_percentage_error(y_true=y_true, y_pred=y_pred)
        
        R2 = skl.r2_score(y_true=y_true, y_pred=y_pred)
        
        EV = skl.explained_variance_score(y_true=y_true, y_pred=y_pred)
        
        MAD = skl.median_absolute_error(y_true=y_true, y_pred=y_pred)
        
        #TODO: Support for MPD, MGD, MTD will be added in next phase.
        # Support for RMSE, RMSLE will be added after OpenSourceML scikit-learn version
        # update as it requires higher version(>1.1.3)
        """MPD = skl.mean_poisson_deviance(y_true, y_pred)
        MGD = skl.mean_gamma_deviance(y_true, y_pred)
        MTD = skl.mean_tweedie_deviance(y_true, y_pred)"""
        
        keys = ["MAE", "MSE", "MSLE", "MAPE", "R2", "EV", "ME", "MAD"]
        values = [MAE, MSE, MSLE, MAPE, R2, EV, ME, MAD]
        return dict(zip(keys, values))
    
    def _classification_metrics(self, y_true, y_pred):
        from teradataml import td_sklearn as skl
        
        # Basic classification metrics
        accuracy = skl.accuracy_score(y_true=y_true, y_pred=y_pred)
        
        # Precision, Recall, F1 (micro, macro, weighted averages)
        micro_precision = skl.precision_score(y_true=y_true, y_pred=y_pred, average='micro')
        micro_recall = skl.recall_score(y_true=y_true, y_pred=y_pred, average='micro') 
        micro_f1 = skl.f1_score(y_true=y_true, y_pred=y_pred, average='micro')
        
        macro_precision = skl.precision_score(y_true=y_true, y_pred=y_pred, average='macro')
        macro_recall = skl.recall_score(y_true=y_true, y_pred=y_pred, average='macro')
        macro_f1 = skl.f1_score(y_true=y_true, y_pred=y_pred, average='macro')
        
        weighted_precision = skl.precision_score(y_true=y_true, y_pred=y_pred, average='weighted')
        weighted_recall = skl.recall_score(y_true=y_true, y_pred=y_pred, average='weighted')
        weighted_f1 = skl.f1_score(y_true=y_true, y_pred=y_pred, average='weighted')
        
        keys = [
            "ACCURACY", "MICRO-PRECISION", "MICRO-RECALL", "MICRO-F1",
            "MACRO-PRECISION", "MACRO-RECALL", "MACRO-F1",
            "WEIGHTED-PRECISION", "WEIGHTED-RECALL", "WEIGHTED-F1"
        ]
        values = [
            accuracy, micro_precision, micro_recall, micro_f1,
            macro_precision, macro_recall, macro_f1,
            weighted_precision, weighted_recall, weighted_f1
        ]
        return dict(zip(keys, values))
    
    def fit(self, 
            data=None,
            evaluation_metric=None, 
            early_stop=None,
            frac=0.8,
            run_parallel=True,
            wait=True,
            verbose=0,
            stratify_column=None, 
            sample_id_column=None, 
            sample_seed=None,
            max_time=None,
            **kwargs):
        """
        DESCRIPTION:
            Function to run the teradataml analytic function for all sets of 
            hyperparameters. Sets of hyperparameters chosen for execution
            from the parameter grid were the parameter grid is populated 
            based on search algorithm.
            Notes:
                * In the Model trainer function, the best parameters are 
                  selected based on training results.
                * In the Non model trainer function, First execution parameter
                  set is selected as the best parameters.

        PARAMETERS:
            data:
                Optional Argument.
                Specifies the input teradataml DataFrame for model trainer function.
                Notes:
                    * DataFrame need not to be passed in fit() methods, when "data" is 
                      passed as a model hyperparameters ("params"). 
                    * "data" is a required argument for model trainer functions.
                    * "data" is ignored for non-model trainer functions.
                    * "data" can be contain single DataFrame or multiple DataFrame.
                    * One can pass multiple dataframes to "data". Hyperparameter 
                      tuning is performed on all the dataframes for every model 
                      parameter.
                    * "data" can be either a dictionary OR a tuple OR a dataframe.
                        * If it is a dictionary then Key represents the label for 
                          dataframe and Value represents the dataframe.
                        * If it is a tuple then teradataml converts it to dictionary
                          by generating the labels internally.
                        * If it is a dataframe then teradataml label it as "DF_0".
                Types: teradataml DataFrame, dictionary, tuples

            evaluation_metric:
                Optional Argument.
                Specifies the evaluation metrics to considered for model 
                evaluation.
                Notes:
                    * evaluation_metric applicable for model trainer functions.
                    * Best model is not selected when evaluation returns 
                      non-finite values.
                    * MPD, MGD, RMSE, RMSLE are not supported for OpenSourceML models.
                Permitted Values:
                    * Classification: Accuracy, Micro-Precision, Micro-Recall,
                                      Micro-F1, Macro-Precision, Macro-Recall,
                                      Macro-F1, Weighted-Precision, 
                                      Weighted-Recall,
                                      Weighted-F1.
                    * Regression: MAE, MSE, MSLE, MAPE, MPE, RMSE, RMSLE, ME, 
                                  R2, EV, MPD, MGD
                    * Clustering: SILHOUETTE
                Default Value:
                    * Classification: Accuracy
                    * Regression: MAE
                    * Clustering: SILHOUETTE
                Types: str

            early_stop:
                Optional Argument.
                Specifies the early stop mechanism value for model trainer 
                functions. Hyperparameter tuning ends model training when 
                the training model evaluation metric attains "early_stop" value.
                Note:
                    * Early stopping supports only when evaluation returns 
                      finite value.
                Types: int or float

            frac:
                Optional Argument.
                Specifies the split percentage of rows to be sampled for training 
                and testing dataset. "frac" argument value must range between (0, 1).
                Notes: 
                    * This "frac" argument is not supported for non-model trainer 
                      function.
                    * The "frac" value is considered as train split percentage and 
                      The remaining percentage is taken into account for test splitting.
                Default Value: 0.8
                Types: float
            
            run_parallel:
                Optional Argument.
                Specifies the parallel execution functionality of hyperparameter 
                tuning. When "run_parallel" set to true, model functions are 
                executed concurrently. Otherwise, model functions are executed 
                sequentially.
                Note:
                    * Early stopping is not supported when parallel run is 
                      enabled.
                Default Value: True
                Types: bool
            
            wait:
                Optional Argument.
                Specifies whether to wait for the completion of execution 
                of hyperparameter tuning or not. When set to False, hyperparameter 
                tuning is executed in the background and user can use "is_running()" 
                method to check the status. Otherwise it waits until the execution 
                is complete to return the control back to user.
                Default Value: True
                Type: bool

            verbose:
                Optional Argument.
                Specifies whether to log the model training information and display 
                the logs. When it is set to 1, progress bar alone logged in the 
                console. When it is set to 2, along with progress bar, execution 
                steps and execution time is logged in the console. When it is set 
                to 0, nothing is logged in the console. 
                Note:
                    * verbose is not significant when "wait" is 'False'.
                Default Value: 0
                Type: bool
            
            sample_seed:
                Optional Argument.
                Specifies the seed value that controls the shuffling applied
                to the data before applying the Train-Test split. Pass an int for 
                reproducible output across multiple function calls.
                Notes:
                    * When the argument is not specified, different
                      runs of the query generate different outputs.
                    * It must be in the range [0, 2147483647]
                    * Seed is supported for stratify column.
                Types: int

            stratify_column:
                Optional Argument.
                Specifies column name that contains the labels indicating
                which data needs to be stratified for TrainTest split. 
                Notes:
                    * seed is supported for stratify column.
                Types: str
            
            sample_id_column:
                Optional Argument.
                Specifies the input data column name that has the
                unique identifier for each row in the input.
                Note:
                    * Mandatory when "sample_seed" argument is present.
                Types: str

            max_time:
                Optional Argument.
                Specifies the maximum time for the completion of Hyperparameter tuning execution.
                Default Value: None
                Types: int or float

            kwargs:
                Optional Argument.
                Specifies the keyword arguments. Accepts additional arguments 
                required for the teradataml analytic function.

        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform fit() operation on the "optimizer_obj".

            >>> eval_params = {"id_column": "id",
                               "accumulate": "MedHouseVal"}
            >>> # Example 1: Passing single DataFrame for model trainer function.
            >>> optimizer_obj.fit(data=train_df,
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)
            
            >>> # Example 2: Passing multiple datasets as tuple of DataFrames for 
            >>> #            model trainer function.
            >>> optimizer_obj.fit(data=(train_df_1, train_df_2),
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)  
            
            >>> # Example 3: Passing multiple datasets as dictionary of DataFrames 
            >>> #            for model trainer function.
            >>> optimizer_obj.fit(data={"Data-1":train_df_1, "Data-2":train_df_2},
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)  

            >>> # Example 4: No data argument passed in fit() method for model trainer function.
            >>> #            Note: data argument must be passed while creating HPT object as 
            >>> #                  model hyperparameters.
            
            >>> # Define parameter space for model training with "data" argument.
            >>> params = {"data":(df1, df2),
                          "input_columns":['MedInc', 'HouseAge', 'AveRooms',
                                           'AveBedrms', 'Population', 'AveOccup',
                                           'Latitude', 'Longitude'],
                          "response_column":"MedHouseVal",
                          "model_type":"regression",
                          "batch_size":(11, 50, 75),
                          "iter_max":(100, 301),
                          "intercept":False,
                          "learning_rate":"INVTIME",
                          "nesterov":True,
                          "local_sgd_iterations":1}
            
            >>> # Create "optimizer_obj" using any search algorithm and perform 
            >>> # fit() method without any "data" argument for model trainer function.
            >>> optimizer_obj.fit(evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params) 

            >>> # Example 5: Do not pass data argument in fit() method for 
            >>> #            non-model trainer function.
            >>> #            Note: data argument must be passed while creating HPT  
            >>> #                  object as model hyperparameters.
            >>> optimizer_obj.fit() 

            >>> # Example 6: Passing "verbose" argument value '1' in fit() method to 
            >>> #            display model log.
            >>> optimizer_obj.fit(data=train_df, evaluation_metric="R2",
                                  verbose=1, **eval_params)
                completed: |████████████████████████████████████████████████████████████| 100% - 6/6
             
        """

        # Set the flag to notify fit method is called.
        self.__is_fit_called = True

        # Validate "early_stop".
        arg_info_matrix = []
        arg_info_matrix.append(["early_stop", early_stop, True, (int, float)])
        arg_info_matrix.append(["frac", frac, True, (float)])
        arg_info_matrix.append(["run_parallel", run_parallel, True, (bool)])
        arg_info_matrix.append(["wait", wait, True, (bool)])
        arg_info_matrix.append(["evaluation_metric", evaluation_metric, True, 
                                (str), True, list(self.__osml_func_comparator) 
                                if self.__is_opensource_model 
                                else list(self.__func_comparator)])
        arg_info_matrix.append(["verbose", verbose, True, (int), True, [0,1,2]])
        arg_info_matrix.append(["max_time", max_time, True, (int, float)])
 
        _Validators._validate_function_arguments(arg_info_matrix)

        # set timeout value.
        self.__timeout = max_time

        self._setting_model_trainer_data(data)

        # Set the evaluation metrics.
        if evaluation_metric is not None:
            self.__evaluation_metric = evaluation_metric.upper()
        self.__early_stop = early_stop
        if self.__is_trainable and self.__is_evaluatable and self.__is_sqle_function:
                                                           
            # When "evaluation_metric" is 'MPE' then use the spl comparators.
            if self.__evaluation_metric == "MPE":
                self._is_best_metrics = self._is_early_stoppable = self._spl_abs_comparator

            if not isinstance(self.__model_trainer_input_data, dict):
                # Sample all the labeled data for model training and testing.
                self.__perform_train_test_sampling(self._labeled_data, frac, stratify_column, 
                                                   sample_id_column, sample_seed)

            elif isinstance(self.__model_trainer_input_data, dict):
                # Sample all the custom labeled data for model training and testing.
                self.__perform_train_test_sampling(self.__model_trainer_input_data, frac, 
                                                   stratify_column, sample_id_column, 
                                                   sample_seed)
            # Update model trainer function parameter grid.
            self.__update_model_parameters()

            self.__eval_params = kwargs if self.__is_evaluatable else None

        elif self.__is_trainable and self.__is_opensource_model:

            if self.__is_clustering_model:
                self.__sampled_df_mapper = self._add_data_label("data")
                # Update model trainer function parameter grid.
                self.__update_model_parameters()
            elif self.__is_regression_model or self.__is_classification_model:                
                # Open-source regression model: perform train-test split
                
                if not isinstance(self.__model_trainer_input_data, dict):
                    self.__perform_train_test_sampling(self._labeled_data, frac, stratify_column, 
                                                    sample_id_column, sample_seed)
                elif isinstance(self.__model_trainer_input_data, dict):
                    self.__perform_train_test_sampling(self.__model_trainer_input_data, frac, 
                                                    stratify_column, sample_id_column, 
                                                    sample_seed)
                #  Set evaluation parameters for supervised models
                self.__eval_params = kwargs if self.__is_evaluatable else None
                
            self.__update_model_parameters()

        elif self.__is_trainable and not self.__is_evaluatable:
            # This condition identifies unsupervised model trainer function.
            # Let's process training data.
            # Note: All unsupervised model training data argument named as 'data'.
            # Label the data with model training argument name.
            self.__sampled_df_mapper = self._add_data_label("data")
            # Update model trainer function parameter grid.
            self.__update_model_parameters()
        # Initialize logging.
        if verbose > 0:
            self.__progress_bar = _ProgressBar(jobs=len(self._parameter_grid), verbose=verbose)

        # With VT option Parallel execution won't be possible, as it opens multiple connections.
        if not run_parallel or configure.temp_object_type == TeradataConstants.TERADATA_VOLATILE_TABLE:
            # Setting start time of Sequential execution.
            
            self.__start_time = time.time() if self.__timeout is not None else None
            # TODO: Factorize the code once parallel execution part is completed in ELE-6154 JIRA.
            # Execute all parameters from populated parameter grid for both trainable 
            # and non trainable function.
            for iter, param in enumerate(self._parameter_grid):
                self._execute_fit(model_param=param, iter=iter, **kwargs)

                # Condition to check early stop feature applicable for model
                # trainer function.
                if self.__early_stop is not None and (self.__is_evaluatable or self.__is_clustering_model):
                    if self.__is_finite and self._is_early_stoppable():
                        # Terminate HPT execution when the trained model attains the
                        # given "early_stop" value.
                        break
                    elif not self.__is_finite:
                        # Raise error because non-finite values cannot be compared 
                        # with "__early_stop" value effectively.
                        # Reset the best models and other properties before raising error.
                        self.__default_model = self.__best_model = self.__best_score_ = \
                        self.__best_model_id = self.__best_params_ = None
                        err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                            "execute 'fit()'","Early stop feature is not applicable"\
                            " when '{metric}' metric results inconsistent value.".format(
                            metric=self.__evaluation_metric))
                        raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
                if self.__timeout is not None and self._is_time_stoppable():
                    # Terminate HPT execution when the execution time exceeds the
                    # given time limit.
                    break
                    
        else:
            # TODO: Added support for early_stop feature along with concurrency in ELE-6154 JIRA.
            # Functions are executed concurrent.
            # Prepare the parameter grid for concurrent execution.
            async_exec_params = []
            for iter, param in enumerate(self._parameter_grid):
                _temp_params = {}
                _temp_params["iter"] = iter
                _temp_params["model_param"] = param
                _temp_params.update(kwargs)
                async_exec_params.append(_temp_params)
            
            # Initialize the stopping event
            self.__parallel_stop_event = threading.Event()
            # let's initialize "_AsyncDBExecutor".
            self._async_executor = _AsyncDBExecutor(wait=wait)
            # Setting start time of Parallel execution.
            self.__start_time = time.time() if self.__timeout is not None else None
            # Trigger parallel thread execution.
            self._async_executor.submit(self._execute_fit, *async_exec_params)
        
        if len(self.__model_err_records) > 0 and not kwargs.get('suppress_refer_msg', False):
            print('\nAn error occurred during Model Training.'\
                  ' Refer to get_error_log() for more details.')


    def __model_trainer_routine(self, model_param, iter, **kwargs):
        """
        DESCRIPTION:
            Internal function to perform fit, predict and evaluate operations 
            for model trainer functions. This model trainer routine supports
            for teradata analytic functions supported by merge model 
            feature.

        PARAMETERS:
            model_param:
                Required Argument.
                Specifies the model trainer arguments used for model training.
                Notes: 
                    * "model_param" contains both model training parameters 
                      and sampled data id.
                    *  Using 'param' key model training parameters are retrieved 
                       from "model_param".
                    *  Using 'data_id' key sampled data identifier is retrieved from 
                       "model_param".
                Types: dict

            iter:
                Required Argument.
                Specifies the iteration count of HPT execution for teradataml 
                analytic function.
                Types: int

            kwargs:
                Required Argument.
                Specifies the keyword arguments used for model evaluation. 
                Accepts additional required arguments for the model trainer 
                function evaluation.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> self.__model_trainer_routine(param=param, iter=iter, **kwargs)
        """
        # Define model name used for model metadata.
        
        model_name = self._generate_model_name(iter)
        # Get the unique data identifier present in "model_param".
        _data_id = model_param[self.__DATA_ID]
        # 'param' variable holds model training parameters and train dataframe. 
        # Get the model training parameters.

        if self.__is_opensource_model:
            param_outer = model_param.get("param", {})
            param = param_outer.get("param", param_outer)
            data_input = param.pop("data", None)
            param = {k: v for k, v in param.items() if k != "data"}
        else:
            param = model_param["param"]
            data_input = None

        # Check the stop_event set or not
        if self.__parallel_stop_event is not None and self.__parallel_stop_event.is_set():
            # Update the model metadata for Skip execution.
            self.__update_model_metadata(model_name, param, "SKIP", 0, 0, 0, _data_id)
            return
        
        # Retrieve the train and test data using data identifier.
        if self.__is_opensource_model:
            
            if self.__is_clustering_model:
                _train_data = self.__sampled_df_mapper[_data_id]
                _test_data = {}  # No label needed
            elif self.__is_regression_model or self.__is_classification_model:
                _train_data, _test_data = self.__sampled_df_mapper[_data_id]
                kwargs.update(_test_data)
        else:
            _train_data, _test_data =  self.__sampled_df_mapper[_data_id]
            # Update model training argument with train DataFrame.
            param.update(_train_data)
            # Update the test DataFrame for model evaluation.
            kwargs.update(_test_data)

        try:
            # Record starting time of model training.
            start_time = time.perf_counter()
            if self.__is_val_function:
                # VAL uses special framework. So, Lets create new instance 
                # using getattr method.
                self.__func = valib.__getattr__(self.__func_name)
            # Train the model.
            if self.__is_opensource_model:
                from teradataml import td_sklearn as skl
                func_class = getattr(skl, self.__func_name)  # e.g., skl.KMeans
                if self.__is_regression_model or self.__is_classification_model:
                    # Extract and remove only for regression models
                    self.__input_columns = param.pop("input_columns", None)
                    self.__response_column = param.pop("response_column", None)
                    
                func_obj = func_class(**param)  # Safely create model instance
            else:
                func_obj = self.__func(**param)
            end_time = time.perf_counter()
            training_time = round((end_time - start_time), 3)
            # Store the trained object.
            self.__trained_models[model_name] = func_obj

            if self.__is_opensource_model and self.__is_clustering_model:
                start_time_cluster = time.perf_counter()
                from teradataml import td_sklearn as skl
                feature_cols = [col for col in _train_data["data"].columns]
                func_obj.fit(data=_train_data["data"], feature_columns=feature_cols)
                pred_col = self._get_predict_column()
                result = func_obj.predict(data=_train_data["data"], feature_columns=feature_cols)
                result.materialize()
            
                silhouette = skl.silhouette_score(
                    X=result.select(feature_cols),
                    labels=result.select([pred_col])
                )
                
                calinski = skl.calinski_harabasz_score(
                    X=result.select(feature_cols),
                    labels=result.select([pred_col])
                )

                davies = skl.davies_bouldin_score(
                    X=result.select(feature_cols),
                    labels=result.select([pred_col])
                )

                columns = ["SILHOUETTE", "CALINSKI", "DAVIES"]
                eval_values = [silhouette, calinski, davies]
                eval_key_values = dict(zip(columns, eval_values))

                end_time_cluster = time.perf_counter()
                training_time_cluster = round((end_time_cluster - start_time_cluster), 3)

                if self.__evaluation_metric is None:
                    self.__evaluation_metric = "SILHOUETTE"
                
                self.__update_model_metadata(model_name, param, "PASS", training_time_cluster,
                                             end_time_cluster, start_time_cluster, _data_id, eval_key_values)
            elif self.__is_opensource_model and (self.__is_regression_model or self.__is_classification_model):                
                start_time_lin = time.perf_counter()
                train_df = _train_data["data"]
                y = train_df.select([self.__response_column])
                X = train_df.drop(columns=[self.__response_column], axis=1)
                
                func_obj.fit(X,y)
                pred_col = self._get_predict_column()
                
                output = func_obj.predict(X,y)
                
                y_true = output.select([self.__response_column])
                y_pred = output.select([pred_col])
                
                if self.__is_regression_model:
                    eval_key_values = self._regression_metrics(y_true, y_pred)
                    if self.__evaluation_metric is None:
                            self.__evaluation_metric = "MAE"
                elif self.__is_classification_model:
                    eval_key_values = self._classification_metrics(y_true, y_pred)
                    if self.__evaluation_metric is None:
                        self.__evaluation_metric = "ACCURACY"
                
                end_time_lin = time.perf_counter()
                training_time_lin = round((end_time_lin - start_time_lin), 3)
                
                self.__update_model_metadata(model_name, param, "PASS", training_time_lin,
                                                end_time_lin, start_time_lin, _data_id, eval_key_values)
            else:
                # Evaluate the trained model.
                evaluations = func_obj.evaluate(**kwargs)
                # Extract evaluations report in dictionary format.
                if "RegressionEvaluator" in type(evaluations).__name__:
                    # RegressionEvaluator results are stored under "result" attribute.
                    # "result" dataframe column names are metrics and corresponding
                    # rows are evaluation values.
                    columns = evaluations.result.keys()
                    eval_values = evaluations.result.get_values()[0]

                    # Default evaluation metric is set to "MAE" for Regression models.
                    if self.__evaluation_metric is None:
                        self.__evaluation_metric = "MAE"
                        
                else:
                    # ClassificationEvaluator results are stored under "output_data" 
                    # attribute. "output_data" dataframe 'column 1' contains metrics
                    # and 'column 2' holds corresponding evaluation values.
                    eval_report = evaluations.output_data.get_values().transpose()
                    columns = eval_report[1].astype('str')
                    columns = [column_name.upper() for column_name in columns]
                    eval_values = eval_report[2]

                    # Default evaluation metric is set to "ACCURACY" for 
                    # classification models.
                    if self.__evaluation_metric is None:
                        self.__evaluation_metric = "ACCURACY"

                # Combine columns and eval_values into a dictionary
                eval_key_values = dict(zip(columns, eval_values))
                # Update the model metadata for successful model training.
                self.__update_model_metadata(model_name, param, "PASS", 
                                             training_time, end_time, start_time,
                                             _data_id, eval_key_values)
            
            
            # Check whether self.__parallel_stop_event is None or not
            if self.__parallel_stop_event is not None:
                # SET the self.__parallel_stop_event 
                # When trained model evaluation metric value exceeds self.__early_stop
                # or When execution time exceeds self.__timeout
                if (self.__early_stop is not None and self._is_early_stoppable())\
                    or (self.__timeout is not None and self._is_time_stoppable()):
                    self.__parallel_stop_event.set()
        
        except Exception as _err_msg:
            # Record error message with corresponding "model_name".
            self.__model_err_records[model_name] = str(_err_msg)
            # Compute the failed execution time for failed training.
            end_time = time.perf_counter()
            training_time = round((end_time - start_time), 3)
            # Update the model metadata for failed execution.
            self.__update_model_metadata(model_name, param, "FAIL", training_time,
                                         end_time, start_time, _data_id)
            pass

    def __non_model_trainer_routine(self, model_param, iter, **kwargs):
        """
        DESCRIPTION:
            Internal function to perform fit operations for non-model 
            trainer functions. This is non-model trainer routine supports
            for teradata analytic functions.
            Note:
                * non-evaluatable model trainer function trained in this routine.

        PARAMETERS:
            model_param:
                Required Argument.
                Specifies the model trainer arguments used for model execution.
                Notes: 
                    * "model_param" contains both model training parameters 
                      and data id for non-evaluatable model trainer 
                      functions.
                    * Using 'param' key model training parameters are retrieved 
                      from "model_param" for non-evaluatable functions.
                    * Using 'data_id' key data identifier is retrieved from 
                      "model_param" for non-evaluatable functions.
                    * No pre-processing required in "model_param" for non-model 
                      trainer functions.
                    * Instead of data identifier DataFrame is present for 
                      non-model trainer functions.
                Types: dict

            iter:
                Required Argument.
                Specifies the iteration count of HPT execution for teradataml 
                analytic function.
                Types: int

            kwargs:
                Optional Argument.
                Specifies the keyword arguments. Accepts additional arguments 
                required for the teradataml analytic function.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> self.__non_model_trainer_routine(param=param, iter=iter, **kwargs)
        """
        # Define model name used for model metadata.
        model_name = self._generate_model_name(iter)

        # 'param' variable holds model training parameters and train dataframe. 
        param = None
        _data_id = None
        # Update model training argument with train dataframe for unsupervised models.
        if self.__is_trainable and not self.__is_evaluatable:
            # Get the model training data id.
            _data_id = model_param[self.__DATA_ID]
            # Retrieve train data using data id.
            _train_data = self.__sampled_df_mapper[_data_id]
            # Get the model training params.
            param = model_param["param"]
            # Update the params with training data.
            param.update(_train_data)
        else:
            # Initialize param for non-model trainer functions. 
            param = model_param
        # Check the stop_event set or not
        if self.__parallel_stop_event is not None and self.__parallel_stop_event.is_set():
            # Update the model metadata for Skip execution.
            self.__update_model_metadata(model_name, param, "SKIP", 0, 0, 0, _data_id)
            return
        try:
            # Record starting time of model training.
            start_time = time.perf_counter()
            if self.__is_val_function:
                # VAL uses special framework. So, Lets create new instance 
                # using getattr method.
                self.__func = valib.__getattr__(self.__func_name)

            # Train the model.
            func_obj = self.__func(**param)

            # Store the trained object.
            self.__trained_models[model_name] = func_obj
            
            # Process training time.
            end_time = time.perf_counter()
            training_time = round((end_time - start_time), 3)
            # Update the model metadata for successful model training.

            self.__update_model_metadata(model_name, param, "PASS", training_time, end_time, start_time, _data_id)
        except Exception as _err_msg:
            # Record error message with corresponding "model_name".
            self.__model_err_records[model_name] = str(_err_msg)
            # Compute the failed execution time for failed training.
            end_time = time.perf_counter()
            training_time = round((end_time - start_time), 3)
            # Update the model metadata for failed execution.
            self.__update_model_metadata(model_name, param, "FAIL", training_time, end_time, start_time, _data_id)
            pass

        if self.__parallel_stop_event is not None:
            # SET the self.__parallel_stop_event 
            # When execution time exceeds self.__timeout
            if self.__timeout is not None and self._is_time_stoppable():
                self.__parallel_stop_event.set()

    
    def __update_model_metadata(self, model_name, 
                                param,
                                status,
                                training_time,
                                end_time,
                                start_time,
                                data_id=None,
                                eval_key_values=None):
        """
        DESCRIPTION:
            Internal function to update the model evaluation details, that are
            used for "models" and "model_stats" properties.

        PARAMETERS:
            model_name:
                 Required Argument.
                 Specifies the unique model name for the training model.
                 Types: str
            
            param:
                Required Argument.
                Specifies the model trainer function parameters used for 
                model training.
                Types: dict
            
            status:
                Required Argument.
                Specifies the status of executed teradataml analytic function.
                Permitted Values: 
                    * PASS: Function result present in the vantage.
                    * FAIL: Function execution failed for the chosen parameters.
                    * SKIP: Function execution skipped for the chosen parameters.
                Types: str
            
            training_time:
                Required Argument.
                Specifies the model training time in seconds for both model trainer 
                function and non-model trainer function.
                Types: float
            
            end_time:
                Optional Argument.
                Specifies the end time of the model training.
                Types: float

            start_time:
                Optional Argument.
                Specifies the start time of the model training.
                Types: float

            data_id:
                Optional Argument.
                Specifies the unique data identifier used for model training.
                Note:
                    * "data_id" is supported for model trainer functions.
                Types: str

            eval_key_values:
                Optional Argument.
                Specifies the evaluation key values retrieved from model evaluation
                phase. This argument is a required argument for model trainer
                function.
                Types: dict.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> optimizer_obj.__update_model_metadata(self, 
                                            evaluations=evaluation_obj.result, 
                                            iter=1, params={"columns" : 
                                            ["age", "nbr_children", "income"], 
                                            "response_column" : "years_with_bank"}, 
                                            status="Present")

        """
        # Prepare model metadata.
        model_metadata = {"MODEL_ID" : model_name,
                          "PARAMETERS" : param,
                          "STATUS" : status}
        if self.__is_trainable:
            # Update "data_id" for model trainer functions. 
            model_metadata[self.__DATA_ID.upper()] = data_id

        # Format log message needs to displayed.
        _msg = "Model_id:{}, Run time:{}s, Start time:{}, End time:{}, Status:{}".format(model_name, 
                                                       training_time,
                                                       start_time,
                                                       end_time,
                                                       status)

        if status == "PASS" and (self.__is_evaluatable or self.__is_clustering_model):
            # While execution status is 'Fail' then update the evaluation result
            # with 'None' values.
            model_scores = eval_key_values
            model_metadata.update(model_scores)
            # Add additional model score to the log message.
            if self.__is_opensource_model and (self.__evaluation_metric is None or self.__evaluation_metric not in model_scores):
                if "SILHOUETTE" in model_scores:
                    self.__evaluation_metric = "SILHOUETTE"
            _msg += ",{}:{}".format(self.__evaluation_metric,round(
                                    model_scores[self.__evaluation_metric], 3))
            # Best model updation.
            # 'self.__is_finite' holds 'True' until any infinite value is seen.
            self.__is_finite = self.__is_finite and np.isfinite(model_metadata[
                                                    self.__evaluation_metric])

            # Let's check if evaluation result is finite and model is the 
            # new best model.
            if np.isfinite(model_metadata[self.__evaluation_metric]) and \
               (self.__best_score_ is None or \
                self._is_best_metrics(model_metadata[self.__evaluation_metric])):
                # Update existing best model.
                self.__default_model = self.__best_model = \
                                       self.__trained_models[model_name]
                # Update existing best score.
                self.__best_score_ = model_metadata[self.__evaluation_metric]
                # Update existing best model ID.
                self.__best_model_id = model_name
                # "self.__best_params_" contains best model parameters. 
                self.__best_params_ = param
                # "__best_data_id" contains bet data identifier used for 
                # training best model.
                self.__best_data_id = data_id

        if not self.__progress_bar is None and status != 'SKIP':
            # Update progress bar when logging is required.
            self.__progress_bar.update(msg=_msg)
        # Update "__model_eval_records" with the formatted metadata.
        self.__model_eval_records.append(model_metadata)


    def predict(self, **kwargs):
        """
        DESCRIPTION:
            Function uses model training function generated models from SQLE, 
            VAL and UAF features for predictions. Predictions are made using 
            the best trained model. Predict function is not supported for
            non-model trainer function.

        PARAMETERS:
            kwargs:
                Optional Argument.
                Specifies the keyword arguments. Accepts all merge model 
                predict feature arguments required for the teradataml 
                analytic function predictions.

        RETURNS:
            Output teradataml DataFrames can be accessed using attribute
            references, such as HPTObj.<attribute_name>.
            Output teradataml DataFrame attribute name is:
                result

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Perform prediction using "optimizer_obj".
            >>> optimizer_obj.predict(newdata=test_data, **eval_params)
                     id  prediction  MedHouseVal
                0   686    0.202843        1.578
                1  2018    0.149868        0.578
                2  1754    0.211870        1.651
                3   670    0.192414        1.922
                4   244    0.247545        1.117
        """

        # Raise TeradataMLException error when non-model trainer function
        # identifier is passed.
        if not self.__is_trainable or not self.__is_predictable:
            err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                       "execute 'predict()'","Not applicable for" \
                                       " non-model trainer analytic functions.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        
        if self.__default_model is None:
            err = Messages.get_message(MessageCodes.EXECUTION_FAILED, 
                                       "execute 'predict()'",
                                       "No model is set as default to set a "\
                                       "prediction model use the 'set_model()' function.")
            
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        
        test_data = kwargs.get("newdata", None)
        
        if self.__is_opensource_model and self.__is_clustering_model:
            if test_data is None:
                test_data = self.__sampled_df_mapper[self.__best_data_id]["data"]
            feature_columns = kwargs.get("feature_columns", None)

            # If feature columns not passed, fetch from training data
            if feature_columns is None:
                if self.__best_data_id is None:
                    err = Messages.get_message(MessageCodes.EXECUTION_FAILED, 
                                               "fetch 'feature_columns'",
                                               "No training metadata found")
            
                    raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
                training_df = self.__sampled_df_mapper[self.__best_data_id]["data"]
                training_columns = training_df.columns
                
                feature_columns = [col for col in training_columns]

            return self.__default_model.predict(data=test_data, feature_columns=feature_columns)
        elif self.__is_opensource_model and (self.__is_regression_model or self.__is_classification_model):
            if test_data is None:
                test_data = self.__sampled_df_mapper[self.__best_data_id][1]["data"]
            y_test = test_data.select([self.__response_column])
            X_test = test_data.drop(columns=[self.__response_column], axis=1)
            
            return self.__default_model.predict(X_test, y_test)
        # TODO Enable this method, once Merge model supports VAL, and UAF.
        return self.__default_model.predict(**kwargs)


    def get_input_data(self, data_id):
        """
        DESCRIPTION:
            Function to get the input data used by model trainer functions.
            Unique identifiers (data_id) is used to get the training data.
            In case of unlabeled data such as single dataframe or tuple of 
            dataframe, default unique identifiers are assigned. Hence, unlabeled
            training data is retrieved using default unique identifiers.
            Notes:
                * Function only returns input data for model trainer functions.
                * Train and Test sampled data are returned for supervised 
                  model trainer function (evaluatable functions).
                * Train data is returned for unsupervised-model trainer function 
                  (non-evaluatable functions).

        PARAMETERS:
            data_id:
                Required Argument.
                Specifies the unique data identifier used for model training.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            ValueError

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the training data.
            >>> optimizer_obj.get_input_data(data_id="DF_1")
                [{'data':       id  MedHouseVal    MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude
                0  19789        0.660 -1.154291 -0.668250  0.862203   7.021803   -1.389101 -1.106515  2.367716  -1.710719
                1  17768        1.601 -0.447350 -0.162481 -0.431952  -0.156872    2.436223  2.172854  0.755780  -1.016640
                2  19722        0.675 -0.076848  1.439120  1.805547   1.944759   -1.186169  0.326739  1.459894  -0.974996
                3  18022        3.719  1.029892  0.343287  0.635952  -0.480133   -0.914869 -0.160824  0.711496  -1.067540
                4  15749        3.500 -0.182247  1.776299 -0.364226   0.035715   -0.257239 -0.970166  0.941772  -1.294272
                5  11246        2.028 -0.294581 -0.583955 -0.265916  -0.270654    0.182266 -0.703494 -0.807444   0.764827
                6  16736        3.152  0.943735  1.439120 -0.747066  -1.036053   -1.071138 -0.678411  0.906345  -1.234118
                7  12242        0.775 -1.076758 -0.752545 -0.424517   0.460470    0.742228 -0.597809 -0.838443   1.241428
                8  14365        2.442 -0.704218  1.017646 -0.428965  -0.367301   -1.014707 -1.333045 -1.294568   1.121121
                9  18760        1.283  0.019018 -1.258313  0.754993   0.013994    0.094365  0.222254  2.195008  -1.201728}, 
                {'newdata':       id  MedHouseVal    MedInc  HouseAge  AveRooms  AveBedrms  Population  AveOccup  Latitude  Longitude
                0  16102        2.841  0.206284  1.270530 -0.248620  -0.224210   -0.059733 -0.242386  0.937344  -1.317408
                1  15994        3.586  0.306050  1.439120  0.255448  -0.334613   -0.160657 -0.426510  0.937344  -1.303526
                2  15391        2.541  0.423107 -1.595492  0.951807  -0.061005    1.955480  0.517572 -1.055434   1.236801
                3  18799        0.520 -0.677565 -0.415366  0.548756   1.254406   -0.883398 -0.534060  2.358859  -1.035149
                4  19172        1.964  0.247152 -0.162481  0.428766  -0.427459   -0.175849 -0.451380  1.238475  -1.396070
                5  18164        3.674  0.295345 -1.258313 -1.078181   0.175885    0.045531 -1.298667  0.760208  -1.099930
                6  13312        1.598  0.484475 -1.342608  0.767557  -0.229585    0.113899  0.361520 -0.692306   0.949915
                7  12342        1.590 -0.520029 -0.246776  0.973345   1.407755    2.325532 -0.406887 -0.798587   1.445024}]

        """
        # Validation.
        arg_info_matrix = []
        arg_info_matrix.append(["data_id", data_id, False, str, 
                                True, list(self.__sampled_df_mapper.keys())])

        # "data_id" argument validation.
        # "data_id" validates for argument type, and permitted values.
        _Validators._validate_function_arguments(arg_info_matrix)

        return self.__sampled_df_mapper.get(data_id)

  
    def get_model(self, model_id):
        """
        DESCRIPTION:
            Function to get the model.

        PARAMETERS:
            model_id:
                Required Argument.
                Specifies the unique identifier for model.
                Notes:
                     * Trained model results returned for model trainer functions.
                     * Executed function results returned for non-model trainer
                       functions.
                Types: str

        RETURNS:
            Object of teradataml analytic functions.
            Note:
                * Attribute references remains same as that of the function 
                  attributes.

        RAISES:
            TeradataMlException, ValueError

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the trained model.
            >>> optimizer_obj.get_model(model_id="SVM_1")
            ############ output_data Output ############

               iterNum      loss       eta  bias
            0        3  2.265289  0.028868   0.0
            1        5  2.254413  0.022361   0.0
            2        6  2.249260  0.020412   0.0
            3        7  2.244463  0.018898   0.0
            4        9  2.235800  0.016667   0.0
            5       10  2.231866  0.015811   0.0
            6        8  2.239989  0.017678   0.0
            7        4  2.259956  0.025000   0.0
            8        2  2.271862  0.035355   0.0
            9        1  2.280970  0.050000   0.0

            ############ result Output ############

                                      predictor  estimate                                   value
            attribute
            -7                           Alpha    0.50000                              Elasticnet
            -3          Number of Observations   31.00000                                    None
             5                      Population   -0.32384                                    None
             0                     (Intercept)    0.00000                                    None
            -17                   OneClass SVM        NaN                                   FALSE
            -16                         Kernel        NaN                                  LINEAR
            -1                   Loss Function        NaN  EPSILON_INSENSITIVE
             7                        Latitude    0.00000                                    None
            -9         Learning Rate (Initial)    0.05000                                    None
            -14                        Epsilon    0.10000                                    None

        """
        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(["model_id", model_id, False, str, 
                                True, list(self.__trained_models.keys())])

        # "model_id" argument validations.
        # "model_id" validates for argument type, and permitted values.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Get the trained model object of trained model.
        model_obj = self.__trained_models.get(model_id)
        # Raise teradataml exception when HPT "fit" method is not executed.
        # since "self.__trained_models" does not contain a record for retrieval.
        if model_obj is None:
            err = Messages.get_message(MessageCodes.MODEL_NOT_FOUND,
                                       model_id, ' or not created')
            raise TeradataMlException(err, MessageCodes.MODEL_NOT_FOUND)

        return model_obj
    

    def get_error_log(self, model_id):
        """
        DESCRIPTION:
            Function to get the error logs of a failed model training in the fit method.

        PARAMETERS:
            model_id:
                Required Argument.
                Specifies the unique identifier for model.
                Note:
                     * Only failed model training error log is returned.
                Types: str

        RETURNS:
            string

        RAISES:
            TypeError, ValueError

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Retrieve the error log.
            >>> optimizer_obj.get_error_log("SVM_2")
                "[Teradata][teradataml](TDML_2082) Value of 'iter_max' must be greater 
                than or equal to 1 and less than or equal to 10000000."

        """
        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(["model_id", model_id, False, str, 
                                True, list(self.__model_err_records.keys())])

        # "model_id" argument validations.
        # "model_id" validates for argument type, and permitted values.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Return the error log of failed model.
        return  self.__model_err_records.get(model_id)
        

    def set_model(self, model_id):
        """
        DESCRIPTION:
            Function to set the model to use for Prediction.

        PARAMETERS:
            model_id:
                Required Argument.
                Specifies the unique identifier for model.
                Note:
                     * Not significant for non-model trainer functions.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException, ValueError

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Set the default trained model.
            >>> optimizer_obj.set_model(model_id="SVM_1")
        """
        # Raise TeradataMLException error when non-model trainer function 
        # identifier is passed.
        if not self.__is_trainable:
            err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                      "execute 'set_model()'","Not applicable for" \
                                      " non-model trainer analytic functions.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)

        # Replace the default model with the trained model.
        self.__default_model = self.get_model(model_id)


    def evaluate(self, **kwargs):
        """
        DESCRIPTION:
            Function uses trained models from SQLE, VAL and UAF features for 
            evaluations. evaluations are made using the default trained model.
            Notes: 
                * Evaluation supported for evaluatable model-trainer functions.
                * Best model is set as default model by default.
                * Default model can be changed using "set_model()" method.

        PARAMETERS:
            kwargs:
                Optional Argument.
                Specifies the keyword arguments. Accepts additional arguments 
                required for the teradataml analytic function evaluations. 
                While "kwargs" is empty then internal sampled test dataset
                and arguments used for evaluation. Otherwise, 
                All arguments required with validation data need to be passed
                for evaluation.

        RETURNS:
            Output teradataml DataFrames can be accessed using attribute
            references, such as HPTEvaluateObj.<attribute_name>.
            Output teradataml DataFrame attribute name is:
                result

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> # Create an instance of the search algorithm called "optimizer_obj" 
            >>> # by referring "__init__()" method.
            >>> # Perform "fit()" method on the optimizer_obj to populate model records.
            >>> # Perform evaluation using best model.
            >>> optimizer_obj.evaluate(newdata=test_data, **eval_params)
                ############ result Output ############
                        MAE       MSE  MSLE        MAPE         MPE      RMSE  RMSLE        ME       R2       EV  MPD  MGD
                0  2.616772  8.814968   0.0  101.876866  101.876866  2.969001    0.0  5.342344 -4.14622 -0.14862  NaN  NaN

        """

        # Raise TeradataMLException error when non-model trainer function 
        # identifier is passed.
        if not self.__is_trainable or not self.__is_evaluatable:
            if not self.__is_clustering_model:
                err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                          "execute 'evaluate()'","Not applicable for" \
                                          " non-model trainer analytic functions.")
                raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
            else:
                err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                          "execute 'evaluate()'","Not applicable for" \
                                          " clustering model functions.")
                raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)

        if self.__default_model is None:
            err = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                      "execute 'evaluate()'",
                                      "No model is set as default to set a "\
                                      "trained model for evaluation use "\
                                      "the 'set_model()' function.")
            raise TeradataMlException(err, MessageCodes.EXECUTION_FAILED)
        if self.__is_opensource_model and (self.__is_regression_model or self.__is_classification_model):
            test_data = kwargs.get("newdata", None)
        
            if test_data is None:
                test_data = self.__sampled_df_mapper[self.__best_data_id][1]["data"]
            
            y_test = test_data.select([self.__response_column])
            X_test = test_data.drop(columns=[self.__response_column], axis=1)
            
            pred_col = self._get_predict_column()
            
            output = self.__default_model.predict(X_test,y_test)
            
            y_true = output.select([self.__response_column])
            y_pred = output.select([pred_col])
            
            if self.__is_regression_model:
                eval_key_values = self._regression_metrics(y_true, y_pred)
            elif self.__is_classification_model:
                eval_key_values = self._classification_metrics(y_true, y_pred)

            import pandas as pd
            result_df = pd.DataFrame([eval_key_values])
            return result_df
        else:
            _params = self.__eval_params if len(kwargs) == 0 else kwargs
            if self._TRAINABLE_FUNCS_DATA_MAPPER[self.__func_name] not in _params:
                _params.update(self.__sampled_df_mapper[self.__best_data_id][1])
            return self.__default_model.evaluate(**_params)


    def __populate_parameter_grid(self):
        """
        DESCRIPTION:
            Internal function to populate parameter grid with all combinations.

        PARAMETERS:
            None

        RETURNS:
            List of dictionary

        RAISES:
            None

        EXAMPLES:
            >>> self.__populate_parameter_grid()

        """
        param_pairs = []
        # Iterate all the parameters to create argument name and value pairs.
        for arg, arg_value in self.__params.items():
            temp_params = []
            if isinstance(arg_value, tuple):
                # When dictionary value type is tuple then add argument name to 
                # all the values in tuples.
                for value in arg_value:
                    temp_params.append((arg, value))
            else:
                # Add argument name to the value.
                temp_params.append((arg, arg_value))

            # Append name and value pairs to the "param_pairs".
            param_pairs.append(temp_params)

        # Return list of dictionary containing all possible combinations.
        return [dict(param) for param in product(*param_pairs)]
    
    def _data_mapping(self):
        """
            DESCRIPTION:
                Internal function to create a Cartesian product of data mapped with input columns 
                and parameter grid.

            PARAMETERS:
                None
            
            RETURNS:
                None
        """
        # Get the input columns from the params.
        input_columns = self.__params.pop("input_columns")
        # Create a list of dictionaries with data_id and input_columns
        data_mapping_list = []
        # Iterate over the labeled data and create a list of dictionaries
        for data_ids, data in self._labeled_data.items():
            # Check if all input columns are present in the data
            for input_cols in input_columns:
                if all(col in data.columns for col in input_cols):
                    data_mapping_list.append({'data_id': data_ids,
                                            'input_columns': input_cols})

        self._parameter_grid = self.__populate_parameter_grid()

        cartesian_product = product(self._parameter_grid, data_mapping_list)

        result_list = []

        # Iterate over the Cartesian product and construct the desired dictionaries
        for params, data_mapping in cartesian_product:
            result_dict = {
                'param': {**params, 'input_columns': data_mapping['input_columns']},
                self.__DATA_ID: data_mapping['data_id']
            }
            result_list.append(result_dict)

        self._parameter_grid = result_list

    
    def _setting_model_trainer_data(self,
                                    data=None):
        """
        DESCRIPTION:
            Internal function to set the model trainer input data for model 
            training. 

        PARAMETERS:
            data:
                Optional Argument.
                Specifies the input data used for model training. 
                Note:
                    * "data" argument is a required argument for model trainer 
                      function when data argument is not passed with hyperparameters.
                    * When data argument is passed with hyperparameters then 
                      "data" argument is optional.
                Types: teradataml DataFrame
        
        RETURNS:
            None

        Example:
            >>> print(self.__model_trainer_input_data)
                (   id  admitted       gpa  stats  programming  masters
                0  19         0  0.051643    0.0          0.0      1.0
                1   6         1  0.765258    0.5          0.0      1.0
                2  15         1  1.000000    0.0          0.0      1.0
                3  32         0  0.746479    0.0          0.5      1.0
                4  12         1  0.835681    1.0          1.0      0.0
                5  40         0  0.976526    1.0          0.5      1.0
                6   7         1  0.215962    1.0          1.0      1.0
                7  36         0  0.530516    0.0          1.0      0.0
                8  28         1  0.967136    0.0          0.0      0.0
                9  17         1  0.920188    0.0          0.0      0.0,    
                    id  admitted       gpa  stats  programming  masters
                0   4         1  0.765258    0.5          1.0      1.0
                1   6         1  0.765258    0.5          0.0      1.0
                2   7         1  0.215962    1.0          1.0      1.0
                3   8         1  0.812207    0.5          0.0      0.0
                4  10         1  0.863850    0.0          0.0      0.0
                5  11         1  0.591549    0.0          0.0      0.0
                6   9         1  0.915493    0.0          0.0      0.0
                7   5         0  0.737089    1.0          1.0      0.0
                8   3         1  0.859155    1.0          0.5      0.0
                9   2         0  0.887324    0.5          0.5      1.0,   
                    id  admitted       gpa  stats  programming  masters
                0  23         1  0.807512    0.0          1.0      1.0
                1  25         1  0.981221    0.0          0.0      0.0
                2  26         1  0.798122    0.0          0.0      1.0
                3  27         0  0.981221    0.0          0.0      1.0
                4  29         0  1.000000    1.0          0.5      1.0
                5  30         0  0.901408    0.0          1.0      1.0
                6  28         1  0.967136    0.0          0.0      0.0
                7  24         1  0.000000    0.0          1.0      0.0
                8  22         0  0.746479    1.0          0.5      1.0
                9  21         1  0.938967    1.0          0.5      0.0)
            
            >>> print(self._labeled_data)
                {'DF_0':        id  admitted       gpa  stats  programming  masters
                            0  26         1  0.798122    0.0          0.0      1.0
                            1  40         0  0.976526    1.0          0.5      1.0
                            2   7         1  0.215962    1.0          1.0      1.0
                            3  19         0  0.051643    0.0          0.0      1.0
                            4  15         1  1.000000    0.0          0.0      1.0
                            5  32         0  0.746479    0.0          0.5      1.0
                            6  38         1  0.366197    0.0          0.5      1.0
                            7  12         1  0.835681    1.0          1.0      0.0
                            8   6         1  0.765258    0.5          0.0      1.0
                            9  36         0  0.530516    0.0          1.0      0.0, 
                'DF_1':         id  admitted       gpa  stats  programming  masters
                            0   4         1  0.765258    0.5          1.0      1.0
                            1   6         1  0.765258    0.5          0.0      1.0
                            2   7         1  0.215962    1.0          1.0      1.0
                            3   8         1  0.812207    0.5          0.0      0.0
                            4  10         1  0.863850    0.0          0.0      0.0
                            5  11         1  0.591549    0.0          0.0      0.0
                            6   9         1  0.915493    0.0          0.0      0.0
                            7   5         0  0.737089    1.0          1.0      0.0
                            8   3         1  0.859155    1.0          0.5      0.0
                            9   2         0  0.887324    0.5          0.5      1.0, 
                'DF_2':        id  admitted       gpa  stats  programming  masters
                            0  23         1  0.807512    0.0          1.0      1.0
                            1  25         1  0.981221    0.0          0.0      0.0
                            2  26         1  0.798122    0.0          0.0      1.0
                            3  27         0  0.981221    0.0          0.0      1.0
                            4  29         0  1.000000    1.0          0.5      1.0
                            5  30         0  0.901408    0.0          1.0      1.0
                            6  28         1  0.967136    0.0          0.0      0.0
                            7  24         1  0.000000    0.0          1.0      0.0
                            8  22         0  0.746479    1.0          0.5      1.0
                            9  21         1  0.938967    1.0          0.5      0.0}
        """
        if self.__is_trainable:
            # "data" argument is a required argument for model trainer function 
            # when data argument is not passed with hyperparameters. On other side,
            # "data" argument will be optional argument when data argument 
            # is passed with hyperparameters.
            _is_optional_arg = self.__model_trainer_input_data is not None
            # validate the model trainer function 'data' argument.
            self.__validate_model_trainer_input_data_argument(data, _is_optional_arg)
            
            if not data is None:
                # '__model_trainer_input_data' is assigned with "data" argument,
                # when user passes data argument in fit() method.
                # Note: if user attempts to pass data argument in both "params" 
                # argument as hyperparameters or "data" argument in fit() 
                # method, then latest "data" argument value is considered 
                # for model training.
                self.__model_trainer_input_data = data

        if self.__is_trainable and self.__is_evaluatable and self.__is_sqle_function:
            self._labeled_data = self._add_data_label()
        elif self.__is_trainable and self.__is_evaluatable and not self.__is_clustering_model:
            self._labeled_data = self._add_data_label()


class GridSearch(_BaseSearch):
    def __init__(self, func, params):
        """
        DESCRIPTION:
            GridSearch is an exhaustive search algorithm that covers all possible
            parameter values to identify optimal hyperparameters. It works for 
            teradataml analytic functions from SQLE, BYOM, VAL and UAF features.
            teradataml GridSearch allows user to perform hyperparameter tuning for 
            all model trainer and non-model trainer functions.
            When used for model trainer functions:
                * Based on evaluation metrics search determines best model.
                * All methods and properties can be used.
            When used for non-model trainer functions:
                * Only fit() method is supported.
                * User can choose the best output as they see fit to use this.

            teradataml GridSearch also allows user to use input data as the 
            hyperparameter. This option can be suitable when the user wants to
            identify the best models for a set of input data. When user passes
            set of data as hyperparameter for model trainer function, the search
            determines the best data along with the best model based on the 
            evaluation metrics.
            Note:
                * configure.temp_object_type="VT" follows sequential execution.

        PARAMETERS:
            func:
                Required Argument.
                Specifies a teradataml analytic function from SQLE, VAL, and UAF.
                Types:
                    teradataml Analytic Functions
                        * Advanced analytic functions
                        * UAF
                        * VAL
                    Refer to display_analytic_functions() function for list of functions.

            params:
                Required Argument.
                Specifies the parameter(s) of a teradataml analytic function. 
                The parameter(s) must be in dictionary. keys refers to the 
                argument names and values refers to argument values for corresponding
                arguments. 
                Notes:
                    * One can specify the argument value in a tuple to run HPT 
                      with different arguments.
                    * Model trainer function arguments "id_column", "input_columns",
                      and "target_columns" must be passed in fit() method.
                    * All required arguments of non-model trainer function must 
                      be passed while GridSearch object creation.
                Types: dict
        
        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError, ValueError
        
        EXAMPLES:
            >>> # Example 1: Model trainer function. Performing hyperparameter-tuning 
            >>> #            on SVM model trainer function.
            
            >>> # Load the example data.
            >>> load_example_data("teradataml", ["cal_housing_ex_raw"])

            >>> # Create teradataml DataFrame objects.
            >>> data_input = DataFrame.from_table("cal_housing_ex_raw")

            >>> # Scale "target_columns" with respect to 'STD' value of the column.
            >>> fit_obj = ScaleFit(data=data_input,
                                   target_columns=['MedInc', 'HouseAge', 'AveRooms',
                                                   'AveBedrms', 'Population', 'AveOccup',
                                                'Latitude', 'Longitude'],
                                  scale_method="STD")
  
            >>> # Transform the data.
            >>> transform_obj = ScaleTransform(data=data_input,
                                               object=fit_obj.output,
                                               accumulate=["id", "MedHouseVal"])

            >>> # Define parameter space for model training.
            >>> params = {"input_columns":['MedInc', 'HouseAge', 'AveRooms',
                                          'AveBedrms', 'Population', 'AveOccup',
                                          'Latitude', 'Longitude'],
                         "response_column":"MedHouseVal",
                         "model_type":"regression",
                         "batch_size":(11, 50, 75),
                         "iter_max":(100, 301),
                         "lambda1":0.1,
                         "alpha":0.5,
                         "iter_num_no_change":60,
                         "tolerance":0.01,
                         "intercept":False,
                         "learning_rate":"INVTIME",
                         "initial_data":0.5,
                         "decay_rate":0.5,
                         "momentum":0.6,
                         "nesterov":True,
                         "local_sgd_iterations":1}

            >>> # Required argument for model prediction and evaluation.
            >>> eval_params = {"id_column": "id",
                               "accumulate": "MedHouseVal"}

            >>> # Import trainer function and optimizer.
            >>> from teradataml import SVM, GridSearch

            >>> # Initialize the GridSearch optimizer with model trainer 
            >>> # function and parameter space required for model training.
            >>> gs_obj = GridSearch(func=SVM, params=params)

            >>> # Perform model optimization for SVM function.
            >>> # Evaluation and prediction arguments are passed along with 
            >>> # training dataframe.
            >>> gs_obj.fit(data=transform_obj.result, **eval_params)

            >>> # View trained models.
            >>> gs_obj.models
                  MODEL_ID DATA_ID                                         PARAMETERS STATUS       MAE
                0    SVM_3    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                1    SVM_0    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                2    SVM_1    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                3    SVM_2    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                4    SVM_4    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                5    SVM_5    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772

            >>> # View model evaluation stats.
            >>> gs_obj.model_stats
                  MODEL_ID DATA_ID                                         PARAMETERS STATUS       MAE
                0    SVM_3    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772`
                1    SVM_0    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                2    SVM_1    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.660815
                3    SVM_2    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                4    SVM_4    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772
                5    SVM_5    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.616772`
            
            >>> # View best data, model ID and score.
            >>> print("Best data ID: ", gs_obj.best_data_id)
                Best data ID:  DF_0
            >>> print("Best model ID: ", gs_obj.best_model_id)
                Best model ID:  SVM_3
            >>> print("Best model score: ",gs_obj.best_score_)
                Best model score:  2.616772068334627
            
            >>> # Performing prediction on sampled data using best trained model.
            >>> test_data = transform_obj.result.iloc[:5]
            >>> gs_pred = gs_obj.predict(newdata=test_data, **eval_params)
            >>> print("Prediction result: \n", gs_pred.result)
                Prediction result:
                     id  prediction  MedHouseVal
                0   686    0.202843        1.578
                1  2018    0.149868        0.578
                2  1754    0.211870        1.651
                3   670    0.192414        1.922
                4   244    0.247545        1.117

            >>> # Perform evaluation using best model.
            >>> gs_obj.evaluate()
                ############ result Output ############
                        MAE       MSE  MSLE        MAPE         MPE      RMSE  RMSLE        ME       R2       EV  MPD  MGD
                0  2.616772  8.814968   0.0  101.876866  101.876866  2.969001    0.0  5.342344 -4.14622 -0.14862  NaN  NaN

            >>> # Retrieve any trained model.
            >>> gs_obj.get_model("SVM_1")
                ############ output_data Output ############

                   iterNum      loss       eta  bias
                0        3  2.060386  0.028868   0.0
                1        5  2.055509  0.022361   0.0
                2        6  2.051982  0.020412   0.0
                3        7  2.048387  0.018898   0.0
                4        9  2.041521  0.016667   0.0
                5       10  2.038314  0.015811   0.0
                6        8  2.044882  0.017678   0.0
                7        4  2.058757  0.025000   0.0
                8        2  2.065932  0.035355   0.0
                9        1  1.780877  0.050000   0.0


                ############ result Output ############

                                         predictor    estimate       value
                attribute
                 7                        Latitude    0.155095        None
                -9         Learning Rate (Initial)    0.050000        None
                -17                   OneClass SVM         NaN       FALSE
                -14                        Epsilon    0.100000        None
                 5                      Population    0.000000        None
                -12                       Nesterov         NaN        TRUE
                -5                             BIC   73.297397        None
                -7                           Alpha    0.500000  Elasticnet
                -3          Number of Observations   55.000000        None
                 0                     (Intercept)    0.000000        None

            >>> # Update the default model.
            >>> gs_obj.set_model("SVM_1")


            
            >>> # Example 2: Model trainer function. Performing hyperparameter-tuning 
            >>> #            on SVM model trainer function using unlabeled multiple-dataframe.
        
            >>> # Slicing transformed dataframe into two part to present 
            >>> # multiple-dataframe support.
            
            >>> train_df_1 = transform_obj.result.iloc[:30]
            >>> train_df_2 = transform_obj.result.iloc[30:]
            
            >>> # Initialize the GridSearch optimizer with model trainer 
            >>> # function and parameter space required for model training.
            >>> gs_obj = GridSearch(func=SVM, params=params)
            
            >>> # Perform model optimization for SVM function for 
            >>> # unlabeled multiple-dataframe support.
            >>> # Evaluation and prediction arguments are passed along with 
            >>> # training dataframe.
            >>> gs_obj.fit(data=(train_df_1, train_df_2), **eval_params)
            
            >>> # View trained models.
            >>> gs_obj.models
                MODEL_ID DATA_ID                                         PARAMETERS STATUS       MAE
                0     SVM_3    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.650505
                1     SVM_1    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.650505
                2     SVM_2    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.326521
                3     SVM_0    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.326521
                4     SVM_7    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.650505
                5     SVM_4    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.326521
                6     SVM_6    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.326521
                7     SVM_5    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.650505
                8     SVM_9    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.650505
                9    SVM_10    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.326521
                10   SVM_11    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.650505
                11    SVM_8    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.326521
            >>> # View model evaluation stats.
            >>> gs_obj.model_stats
                MODEL_ID       MAE       MSE  MSLE        MAPE  ...        ME        R2        EV  MPD  MGD
                0     SVM_3  2.650505  8.459088   0.0  159.159527  ...  5.282729 -2.930531  0.333730  NaN  NaN
                1     SVM_1  2.650505  8.459088   0.0  159.159527  ...  5.282729 -2.930531  0.333730  NaN  NaN
                2     SVM_2  2.326521  6.218464   0.0   90.629648  ...  3.776410 -6.987358 -0.034968  NaN  NaN
                3     SVM_0  2.326521  6.218464   0.0   90.629648  ...  3.776410 -6.987358 -0.034968  NaN  NaN
                4     SVM_7  2.650505  8.459088   0.0  159.159527  ...  5.282729 -2.930531  0.333730  NaN  NaN
                5     SVM_4  2.326521  6.218464   0.0   90.629648  ...  3.776410 -6.987358 -0.034968  NaN  NaN
                6     SVM_6  2.326521  6.218464   0.0   90.629648  ...  3.776410 -6.987358 -0.034968  NaN  NaN
                7     SVM_5  2.650505  8.459088   0.0  159.159527  ...  5.282729 -2.930531  0.333730  NaN  NaN
                8     SVM_9  2.650505  8.459088   0.0  159.159527  ...  5.282729 -2.930531  0.333730  NaN  NaN
                9    SVM_10  2.326521  6.218464   0.0   90.629648  ...  3.776410 -6.987358 -0.034968  NaN  NaN
                10   SVM_11  2.650505  8.459088   0.0  159.159527  ...  5.282729 -2.930531  0.333730  NaN  NaN
                11    SVM_8  2.326521  6.218464   0.0   90.629648  ...  3.776410 -6.987358 -0.034968  NaN  NaN

            
            >>> # View best data, model ID and score.
            >>> print("Best data ID: ", gs_obj.best_data_id)
                Best data ID:  DF_0
            >>> print("Best model ID: ", gs_obj.best_model_id)
                Best model ID:  SVM_2
            >>> print("Best model score: ",gs_obj.best_score_)
                Best model score:  2.3265213466885375
            
            >>> # Performing prediction on sampled data using best trained model.
            >>> test_data = transform_obj.result.iloc[:5]
            >>> gs_pred = gs_obj.predict(newdata=test_data, **eval_params)
            >>> print("Prediction result: \n", gs_pred.result)
                Prediction result:       
                     id  prediction  MedHouseVal
                0   686   -0.214558        1.578
                1  2018    0.224954        0.578
                2  1754   -0.484374        1.651
                3   670   -0.288802        1.922
                4   244   -0.097476        1.117
            
            >>> # Perform evaluation using best model.
            >>> gs_obj.evaluate()
                ############ result Output ############

                        MAE       MSE  MSLE       MAPE        MPE      RMSE  RMSLE       ME        R2        EV  MPD  MGD
                0  2.326521  6.218464   0.0  90.629648  90.629648  2.493685    0.0  3.77641 -6.987358 -0.034968  NaN  NaN

            
            >>> # Retrieve any trained model.
            >>> gs_obj.get_model("SVM_1")
                ############ output_data Output ############

                   iterNum      loss       eta  bias
                0        3  2.078232  0.028868   0.0
                1        5  2.049456  0.022361   0.0
                2        6  2.037157  0.020412   0.0
                3        7  2.028186  0.018898   0.0
                4        9  2.012801  0.016667   0.0
                5       10  2.007469  0.015811   0.0
                6        8  2.020026  0.017678   0.0
                7        4  2.063343  0.025000   0.0
                8        2  2.092763  0.035355   0.0
                9        1  2.112669  0.050000   0.0


                ############ result Output ############

                                         predictor    estimate       value
                attribute
                 7                        Latitude    0.077697        None
                -9         Learning Rate (Initial)    0.050000        None
                -17                   OneClass SVM         NaN       FALSE
                -14                        Epsilon    0.100000        None
                 5                      Population   -0.120322        None
                -12                       Nesterov         NaN        TRUE
                -5                             BIC   50.583018        None
                -7                           Alpha    0.500000  Elasticnet
                -3          Number of Observations   31.000000        None
                 0                     (Intercept)    0.000000        None

            
            >>> # Update the default model.
            >>> gs_obj.set_model("SVM_1")
            
            >>> # Example 3: Model trainer function. Performing hyperparameter-tuning
            >>> #            on SVM model trainer function using labeled multiple-dataframe.
            
            >>> # Initialize the GridSearch optimizer with model trainer
            >>> # function and parameter space required for model training.
            >>> gs_obj = GridSearch(func=SVM, params=params)
            
            >>> # Perform model optimization for SVM function for
            >>> # labeled multiple-dataframe support.
            >>> # Evaluation and prediction arguments are passed along with
            >>> # training dataframe.
            >>> gs_obj.fit(data={"Data-1":train_df_1, "Data-2":train_df_2}, **eval_params)
            
            >>> # View trained models.
            >>> gs_obj.models
                   MODEL_ID DATA_ID                                         PARAMETERS STATUS       MAE
                0     SVM_1  Data-2  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.286463
                1     SVM_3  Data-2  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.286463
                2     SVM_2  Data-1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.156109
                3     SVM_0  Data-1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.156109
                4     SVM_7  Data-2  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.286463
                5     SVM_4  Data-1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.156109
                6     SVM_5  Data-2  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.286463
                7     SVM_6  Data-1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.156109
                8    SVM_10  Data-1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.156109
                9     SVM_8  Data-1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.156109
                10    SVM_9  Data-2  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.286463
                11   SVM_11  Data-2  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.286463
            
            >>> # View model evaluation stats.
            >>> gs_obj.model_stats
                   MODEL_ID       MAE       MSE      MSLE        MAPE  ...        ME        R2        EV  MPD  MGD
                0     SVM_1  2.286463  5.721906  0.115319  120.188468  ...  3.280316 -3.436736  0.616960  NaN  NaN
                1     SVM_3  2.286463  5.721906  0.115319  120.188468  ...  3.280316 -3.436736  0.616960  NaN  NaN
                2     SVM_2  2.156109  6.986356  0.000000   97.766138  ...  4.737632 -2.195437 -0.235152  NaN  NaN
                3     SVM_0  2.156109  6.986356  0.000000   97.766138  ...  4.737632 -2.195437 -0.235152  NaN  NaN
                4     SVM_7  2.286463  5.721906  0.115319  120.188468  ...  3.280316 -3.436736  0.616960  NaN  NaN
                5     SVM_4  2.156109  6.986356  0.000000   97.766138  ...  4.737632 -2.195437 -0.235152  NaN  NaN
                6     SVM_5  2.286463  5.721906  0.115319  120.188468  ...  3.280316 -3.436736  0.616960  NaN  NaN
                7     SVM_6  2.156109  6.986356  0.000000   97.766138  ...  4.737632 -2.195437 -0.235152  NaN  NaN
                8    SVM_10  2.156109  6.986356  0.000000   97.766138  ...  4.737632 -2.195437 -0.235152  NaN  NaN
                9     SVM_8  2.156109  6.986356  0.000000   97.766138  ...  4.737632 -2.195437 -0.235152  NaN  NaN
                10    SVM_9  2.286463  5.721906  0.115319  120.188468  ...  3.280316 -3.436736  0.616960  NaN  NaN
                11   SVM_11  2.286463  5.721906  0.115319  120.188468  ...  3.280316 -3.436736  0.616960  NaN  NaN

            [12 rows x 13 columns]
            
            >>> # View best data, model ID and score.
            >>> print("Best data ID: ", gs_obj.best_data_id)
                Best data ID:  Data-1
            >>> print("Best model ID: ", gs_obj.best_model_id)
                Best model ID:  SVM_2
            >>> print("Best model score: ",gs_obj.best_score_)
                Best model score:  2.156108718480682
            
            >>> # Performing prediction on sampled data using best trained model.
            >>> test_data = transform_obj.result.iloc[:5]
            >>> gs_pred = gs_obj.predict(newdata=test_data, **eval_params)
            >>> print("Prediction result: \n", gs_pred.result)
                Prediction result:
                     id  prediction  MedHouseVal
                0   686   -0.512750        1.578
                1  2018    0.065364        0.578
                2  1754   -0.849449        1.651
                3   670   -0.657097        1.922
                4   244   -0.285946        1.117
            
            >>> # Perform evaluation using best model.
            >>> gs_obj.evaluate()
                ############ result Output ############

                        MAE       MSE  MSLE       MAPE        MPE      RMSE  RMSLE        ME        R2        EV  MPD  MGD
                0  2.156109  6.986356   0.0  97.766138  83.453982  2.643172    0.0  4.737632 -2.195437 -0.235152  NaN  NaN

            >>> # Retrieve any trained model.
            >>> gs_obj.get_model("SVM_1")
                ############ output_data Output ############

                   iterNum      loss       eta  bias
                0        3  2.238049  0.028868   0.0
                1        5  2.198618  0.022361   0.0
                2        6  2.183347  0.020412   0.0
                3        7  2.171550  0.018898   0.0
                4        9  2.154619  0.016667   0.0
                5       10  2.147124  0.015811   0.0
                6        8  2.162718  0.017678   0.0
                7        4  2.217790  0.025000   0.0
                8        2  2.257826  0.035355   0.0
                9        1  2.286324  0.050000   0.0


                ############ result Output ############

                                          predictor   estimate                                   value
                attribute
                -7                           Alpha    0.500000                              Elasticnet
                -3          Number of Observations   31.000000                                    None
                 5                      Population   -0.094141                                    None
                 0                     (Intercept)    0.000000                                    None
                -17                   OneClass SVM         NaN                                   FALSE
                -16                         Kernel         NaN                                  LINEAR
                -1                   Loss Function         NaN  EPSILON_INSENSITIVE
                 7                        Latitude    0.169825                                    None
                -9         Learning Rate (Initial)    0.050000                                    None
                -14                        Epsilon    0.100000                                    None

            >>> # Update the default model.
            >>> gs_obj.set_model("SVM_1")

           
            >>> # Example 4: Model trainer function. Performing hyperparameter-tuning
            >>> #            on SVM model trainer function by passing unlabeled
            >>> #            multiple-dataframe as model hyperparameter.
            
            >>> # Define parameter space for model training.
            >>> params = {"data":(train_df_1, train_df_2),
                          "input_columns":['MedInc', 'HouseAge', 'AveRooms',
                                          'AveBedrms', 'Population', 'AveOccup',
                                          'Latitude', 'Longitude'],
                          "response_column":"MedHouseVal",
                          "model_type":"regression",
                          "batch_size":(11, 50, 75),
                          "iter_max":(100, 301),
                          "lambda1":0.1,
                          "alpha":0.5,
                          "iter_num_no_change":60,
                          "tolerance":0.01,
                          "intercept":False,
                          "learning_rate":"INVTIME",
                          "initial_data":0.5,
                          "decay_rate":0.5,
                          "momentum":0.6,
                          "nesterov":True,
                          "local_sgd_iterations":1}
           
            >>> # Initialize the GridSearch optimizer with model trainer
            >>> # function and parameter space required for model training.
            >>> gs_obj = GridSearch(func=SVM, params=params)
            
            >>> # Perform model optimization for SVM function for
            >>> # labeled multiple-dataframe support.
            >>> # Evaluation and prediction arguments are passed along with
            >>> # training dataframe.
            >>> gs_obj.fit(**eval_params)
            
            >>> # View trained models.
            >>> gs_obj.models
                   MODEL_ID DATA_ID                                         PARAMETERS STATUS       MAE
                0     SVM_0    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.007936
                1     SVM_1    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.517338
                2     SVM_3    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.517338
                3     SVM_2    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.007936
                4     SVM_5    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.517338
                5     SVM_7    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.517338
                6     SVM_6    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.007936
                7     SVM_4    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.007936
                8     SVM_9    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.517338
                9     SVM_8    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.007936
                10   SVM_11    DF_1  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.517338
                11   SVM_10    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS  2.007936
            
            >>> # View model evaluation stats.
            >>> gs_obj.model_stats
                   MODEL_ID       MAE       MSE      MSLE        MAPE  ...        ME        R2        EV  MPD  MGD
                0     SVM_0  2.007936  5.402427  0.007669   88.199346  ...  3.981598 -6.898063 -1.003772  NaN  NaN
                1     SVM_1  2.517338  7.470182  0.000000  118.722467  ...  4.035658 -7.827958 -0.716572  NaN  NaN
                2     SVM_3  2.517338  7.470182  0.000000  118.722467  ...  4.035658 -7.827958 -0.716572  NaN  NaN
                3     SVM_2  2.007936  5.402427  0.007669   88.199346  ...  3.981598 -6.898063 -1.003772  NaN  NaN
                4     SVM_5  2.517338  7.470182  0.000000  118.722467  ...  4.035658 -7.827958 -0.716572  NaN  NaN
                5     SVM_7  2.517338  7.470182  0.000000  118.722467  ...  4.035658 -7.827958 -0.716572  NaN  NaN
                6     SVM_6  2.007936  5.402427  0.007669   88.199346  ...  3.981598 -6.898063 -1.003772  NaN  NaN
                7     SVM_4  2.007936  5.402427  0.007669   88.199346  ...  3.981598 -6.898063 -1.003772  NaN  NaN
                8     SVM_9  2.517338  7.470182  0.000000  118.722467  ...  4.035658 -7.827958 -0.716572  NaN  NaN
                9     SVM_8  2.007936  5.402427  0.007669   88.199346  ...  3.981598 -6.898063 -1.003772  NaN  NaN
                10   SVM_11  2.517338  7.470182  0.000000  118.722467  ...  4.035658 -7.827958 -0.716572  NaN  NaN
                11   SVM_10  2.007936  5.402427  0.007669   88.199346  ...  3.981598 -6.898063 -1.003772  NaN  NaN

            [12 rows x 13 columns]
            
            >>> # View best data, model ID and score.
            >>> print("Best data ID: ", gs_obj.best_data_id)
                Best data ID:  DF_0
            >>> print("Best model ID: ", gs_obj.best_model_id)
                Best model ID:  SVM_0
            >>> print("Best model score: ",gs_obj.best_score_)
                Best model score:  2.0079362549355104
            
            >>> # Performing prediction on sampled data using best trained model.
            >>> test_data = transform_obj.result.iloc[:5]
            >>> gs_pred = gs_obj.predict(newdata=test_data, **eval_params)
            >>> print("Prediction result: \n", gs_pred.result)
                Prediction result:       
                     id  prediction  MedHouseVal
                0   686   -0.365955        1.578
                1  2018    0.411846        0.578
                2  1754   -0.634807        1.651
                3   670   -0.562927        1.922
                4   244   -0.169730        1.117
            >>> # Perform evaluation using best model.
            >>> gs_obj.evaluate()
                ############ result Output ############

                        MAE       MSE      MSLE       MAPE        MPE      RMSE     RMSLE        ME        R2        EV  MPD  MGD
                0  2.007936  5.402427  0.007669  88.199346  88.199346  2.324312  0.087574  3.981598 -6.898063 -1.003772  NaN  NaN


            >>> # Retrieve any trained model.
            >>> gs_obj.get_model("SVM_1")
                ############ output_data Output ############

                   iterNum      loss       eta  bias
                0        3  2.154842  0.028868   0.0
                1        5  2.129916  0.022361   0.0
                2        6  2.118539  0.020412   0.0
                3        7  2.107991  0.018898   0.0
                4        9  2.089022  0.016667   0.0
                5       10  2.080426  0.015811   0.0
                6        8  2.098182  0.017678   0.0
                7        4  2.142030  0.025000   0.0
                8        2  2.168233  0.035355   0.0
                9        1  2.186740  0.050000   0.0

                ############ result Output ############

                                          predictor   estimate       value
                attribute
                 7                        Latitude    0.010463        None
                -9         Learning Rate (Initial)    0.050000        None
                -17                   OneClass SVM         NaN       FALSE
                -14                        Epsilon    0.100000        None
                 5                      Population   -0.348591        None
                -12                       Nesterov         NaN        TRUE
                -5                             BIC   50.585888        None
                -7                           Alpha    0.500000  Elasticnet
                -3          Number of Observations   31.000000        None
                 0                     (Intercept)    0.000000        None


            >>> # Update the default model.
            >>> gs_obj.set_model("SVM_1")
            
            >>> # Example 5: Non-Model trainer function. Performing GridSearch
            >>> #            on AntiSelect model trainer function.
            >>> # Load the example dataset.
            >>> load_example_data("teradataml", "titanic")
            
            >>> # Create teradaraml dataframe.
            >>> titanic = DataFrame.from_table("titanic")
            
            >>> # Define the non-model trainer function parameter space.
            >>> # Include input data in parameter space for non-model trainer function.
            >>> params = {"data":titanic, "exclude":(
                                            ['survived', 'name', 'age'],
                                            ["ticket", "parch", "sex", "age"])}
            
            >>> # Import non-model trainer function and optimizer.
            >>> from teradataml import Antiselect, GridSearch
            
            >>> # Initialize the GridSearch optimizer with non-model trainer
            >>> # function and parameter space required for non-model training.
            >>> gs_obj = GridSearch(func=Antiselect, params=params)
            
            >>> # Perform execution of Antiselect function.
            >>> gs_obj.fit()
            
            >>> # View trained models.
            >>> gs_obj.models
                       MODEL_ID                                         PARAMETERS STATUS
                0  ANTISELECT_1  {'data': '"titanic"', 'exclude': ['ticket', 'p...   PASS
                1  ANTISELECT_0  {'data': '"titanic"', 'exclude': ['survived', ...   PASS
            
            >>> # Retrieve any trained model using "MODEL_ID".
            >>> gs_obj.get_model("ANTISELECT_1")
                ############ result Output ############

                   passenger  survived  pclass                                                name  sibsp      fare cabin embarked
                0        162         1       2  Watt, Mrs. James (Elizabeth "Bessie" Inglis Milne)      0   15.7500  None        S
                1        591         0       3                                Rintamaki, Mr. Matti      0    7.1250  None        S
                2        387         0       3                     Goodwin, Master. Sidney Leonard      5   46.9000  None        S
                3        469         0       3                                  Scanlan, Mr. James      0    7.7250  None        Q
                4        326         1       1                            Young, Miss. Marie Grice      0  135.6333   C32        C
                5        265         0       3                                  Henry, Miss. Delia      0    7.7500  None        Q
                6        530         0       2                         Hocking, Mr. Richard George      2   11.5000  None        S
                7        244         0       3                       Maenpaa, Mr. Matti Alexanteri      0    7.1250  None        S
                8         61         0       3                               Sirayanian, Mr. Orsen      0    7.2292  None        C
                9        122         0       3                          Moore, Mr. Leonard Charles      0    8.0500  None        S

        """

        self.__params = params.copy()
        super().__init__(func=func, params=self.__params)
        # Populate parameter grid from provided parameter space.
        self.__populate_params_grid()


    def __populate_params_grid(self):
        """
        DESCRIPTION:
            Populate parameter grid based on the search algorithm. In GridSearch,
            populate all combinations of parameters.
        
        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> self.__populate_params_grid()
        """
        # Populate all parameter combinations for given "params".
        # Since GridSearch works on all parameter combinations. Set 
        # all the parameter combinations to the parameter grid.
        self._parameter_grid = self._BaseSearch__populate_parameter_grid()
        

    def fit(self, 
            data=None,
            evaluation_metric=None, 
            early_stop=None,
            frac=0.8,
            run_parallel=True,
            wait=True,
            verbose=0,
            stratify_column=None, 
            sample_id_column=None, 
            sample_seed=None,
            max_time=None,
            **kwargs):
        """
        DESCRIPTION:
            Function to perform hyperparameter tuning using GridSearch algorithm.
            Notes:
                * In the Model trainer function, the best parameters are 
                  selected based on training results.
                * In the Non model trainer function, First execution parameter
                  set is selected as the best parameters.

        PARAMETERS:
            data:
                Optional Argument.
                Specifies the input teradataml DataFrame for model trainer function.
                Notes:
                    * DataFrame need not to be passed in fit() methods, when "data" is 
                      passed as a model hyperparameters ("params"). 
                    * "data" is a required argument for model trainer functions.
                    * "data" is ignored for non-model trainer functions.
                    * "data" can be contain single DataFrame or multiple DataFrame.
                    * One can pass multiple dataframes to "data". Hyperparameter 
                      tuning is performed on all the dataframes for every model 
                      parameter.
                    * "data" can be either a dictionary OR a tuple OR a dataframe.
                        * If it is a dictionary then Key represents the label for 
                          dataframe and Value represents the dataframe.
                        * If it is a tuple then teradataml converts it to dictionary
                          by generating the labels internally.
                        * If it is a dataframe then teradataml label it as "DF_0".
                Types: teradataml DataFrame, dictionary, tuples

            evaluation_metric:
                Optional Argument.
                Specifies the evaluation metrics to considered for model 
                evaluation.
                Notes:
                    * evaluation_metric applicable for model trainer functions.
                    * Best model is not selected when evaluation returns 
                      non-finite values.
                    * MPD, MGD, RMSE, RMSLE are not supported for OpenSourceML models.
                Permitted Values:
                    * Classification: Accuracy, Micro-Precision, Micro-Recall,
                                      Micro-F1, Macro-Precision, Macro-Recall,
                                      Macro-F1, Weighted-Precision, 
                                      Weighted-Recall,
                                      Weighted-F1.
                    * Regression: MAE, MSE, MSLE, MAPE, MPE, RMSE, RMSLE, ME, 
                                  R2, EV, MPD, MGD
                    
                Default Value:
                    * Classification: Accuracy
                    * Regression: MAE
                Types: str

            early_stop:
                Optional Argument.
                Specifies the early stop mechanism value for model trainer 
                functions. Hyperparameter tuning ends model training when 
                the training model evaluation metric attains "early_stop" value.
                Note:
                    * Early stopping supports only when evaluation returns 
                      finite value.
                Types: int or float

            frac:
                Optional Argument.
                Specifies the split percentage of rows to be sampled for training 
                and testing dataset. "frac" argument value must range between (0, 1).
                Notes: 
                    * This "frac" argument is not supported for non-model trainer 
                      function.
                    * The "frac" value is considered as train split percentage and 
                      The remaining percentage is taken into account for test splitting.
                Default Value: 0.8
                Types: float
            
            run_parallel:
                Optional Argument.
                Specifies the parallel execution functionality of hyperparameter 
                tuning. When "run_parallel" set to true, model functions are 
                executed concurrently. Otherwise, model functions are executed 
                sequentially.
                Default Value: True
                Types: bool
            
            wait:
                Optional Argument.
                Specifies whether to wait for the completion of execution 
                of hyperparameter tuning or not. When set to False, hyperparameter 
                tuning is executed in the background and user can use "is_running()" 
                method to check the status. Otherwise it waits until the execution 
                is complete to return the control back to user.
                Default Value: True
                Type: bool

            verbose:
                Optional Argument.
                Specifies whether to log the model training information and display 
                the logs. When it is set to 1, progress bar alone logged in the 
                console. When it is set to 2, along with progress bar, execution 
                steps and execution time is logged in the console. When it is set 
                to 0, nothing is logged in the console. 
                Note:
                    * verbose is not significant when "wait" is 'False'.
                Default Value: 0
                Type: bool
            
            sample_seed:
                Optional Argument.
                Specifies the seed value that controls the shuffling applied
                to the data before applying the Train-Test split. Pass an int for 
                reproducible output across multiple function calls.
                Notes:
                    * When the argument is not specified, different
                      runs of the query generate different outputs.
                    * It must be in the range [0, 2147483647]
                    * Seed is supported for stratify column.
                Types: int

            stratify_column:
                Optional Argument.
                Specifies column name that contains the labels indicating
                which data needs to be stratified for TrainTest split. 
                Notes:
                    * seed is supported for stratify column.
                Types: str
            
            sample_id_column:
                Optional Argument.
                Specifies the input data column name that has the
                unique identifier for each row in the input.
                Note:
                    * Mandatory when "sample_seed" argument is present.
                Types: str

            max_time:
                Optional Argument.
                Specifies the maximum time for the completion of Hyperparameter tuning execution.
                Default Value: None
                Types: int or float

            kwargs:
                Optional Argument.
                Specifies the keyword arguments. Accepts additional arguments 
                required for the teradataml analytic function.

        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> # Create an instance of the GridSearch algorithm called "optimizer_obj" 
            >>> optimizer_obj = GridSearch(func=SVM, params=params)

            >>> eval_params = {"id_column": "id",
                               "accumulate": "MedHouseVal"}
            >>> # Example 1: Passing single DataFrame for model trainer function.
            >>> optimizer_obj.fit(data=train_df,
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)
            
            >>> # Example 2: Passing multiple datasets as tuple of DataFrames for 
            >>> #            model trainer function.
            >>> optimizer_obj.fit(data=(train_df_1, train_df_2),
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)  
            
            >>> # Example 3: Passing multiple datasets as dictionary of DataFrames 
            >>> #            for model trainer function.
            >>> optimizer_obj.fit(data={"Data-1":train_df_1, "Data-2":train_df_2},
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)  

            >>> # Example 4: No data argument passed in fit() method for model trainer function.
            >>> #            Note: data argument must be passed while creating HPT object as 
            >>> #                  model hyperparameters.
            
            >>> # Define parameter space for model training with "data" argument.
            >>> params = {"data":(df1, df2),
                          "input_columns":['MedInc', 'HouseAge', 'AveRooms',
                                           'AveBedrms', 'Population', 'AveOccup',
                                           'Latitude', 'Longitude'],
                          "response_column":"MedHouseVal",
                          "model_type":"regression",
                          "batch_size":(11, 50, 75),
                          "iter_max":(100, 301),
                          "intercept":False,
                          "learning_rate":"INVTIME",
                          "nesterov":True,
                          "local_sgd_iterations":1}
            
            >>> # Create "optimizer_obj" using GridSearch algorithm and perform 
            >>> # fit() method without any "data" argument for model trainer function.
            >>> optimizer_obj.fit(evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params) 

            >>> # Example 5: Do not pass data argument in fit() method for 
            >>> #            non-model trainer function.
            >>> #            Note: data argument must be passed while creating HPT  
            >>> #                  object as model hyperparameters.
            >>> optimizer_obj.fit() 

            >>> # Example 6: Passing "verbose" argument value '1' in fit() method to 
            >>> #            display model log.
            >>> optimizer_obj.fit(data=train_df, evaluation_metric="R2",
                                  verbose=1, **eval_params)
                completed: |████████████████████████████████████████████████████████████| 100% - 6/6

            >>> # Example 7: max_time argument is passed in fit() method.
            >>> # Model training parameters
            >>> model_params = {"input_columns":['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
            ...                 "response_column" :'species',
            ...                 "max_depth":(5,10,15),
            ...                 "lambda1" :(1000.0,0.001),
            ...                 "model_type" :"Classification",
            ...                 "seed":32,
            ...                 "shrinkage_factor":0.1,
            ...                 "iter_num":(5, 50)}
            >>>
            >>> eval_params = {"id_column": "id",
            ...                "accumulate":"species",
            ...                "model_type":'Classification',
            ...                "object_order_column":['task_index', 'tree_num', 'iter','class_num', 'tree_order']
                            }
            >>>
            >>> # Import model trainer function and optimizer.
            >>> from teradataml import XGBoost, GridSearch
            >>>
            >>> # Initialize the GridSearch optimizer with model trainer
            >>> # function and parameter space required for model training.
            >>> gs_obj = GridSearch(func=XGBoost, params=model_params)
            >>>
            >>> # fit() method with max_time argument(in seconds) for model trainer function.
            >>> gs_obj.fit(data=data, max_time=30, verbose=2, **eval_params)
                Model_id:XGBOOST_2 - Run time:33.277s - Status:PASS - ACCURACY:0.933               
                Model_id:XGBOOST_3 - Run time:33.276s - Status:PASS - ACCURACY:0.933               
                Model_id:XGBOOST_0 - Run time:33.279s - Status:PASS - ACCURACY:0.967                
                Model_id:XGBOOST_1 - Run time:33.278s - Status:PASS - ACCURACY:0.933                
                Computing: ｜⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾｜ 33% - 4/12
            >>>
            >>> # status 'SKIP' for the models which are not completed within the max_time.
            >>> gs_obj.models
                    MODEL_ID	DATA_ID	                                       PARAMETERS	STATUS	ACCURACY
                0	XGBOOST_2	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.933333
                1	XGBOOST_4	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                2	XGBOOST_5	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                3	XGBOOST_6	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                4	XGBOOST_7	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                5	XGBOOST_8	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                6	XGBOOST_9	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                7	XGBOOST_10	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                8	XGBOOST_11	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                9	XGBOOST_3	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.933333
                10	XGBOOST_0	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.966667
                11	XGBOOST_1	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.933333
        """
        
        # Set the flag to discard invalid column parameters.
        self.discard_invalid_column_params =kwargs.get("discard_invalid_column_params", False)

        if self.discard_invalid_column_params:
            # Setting model trainer input data.
            super()._setting_model_trainer_data(data)
            # Data mapping for model trainer function.
            super()._data_mapping()
            # Setting the lambda function to None.
            self._setting_model_trainer_data = lambda data: None
            self._BaseSearch__update_model_parameters = lambda: None

        # Calling baseSearch class fit method.
        super().fit(data, evaluation_metric, 
                    early_stop, frac, run_parallel,
                    wait, verbose, stratify_column, 
                    sample_id_column, sample_seed,
                    max_time, **kwargs)


class RandomSearch(_BaseSearch):
    def __init__(self, func, params, n_iter=10, **kwargs):
        """
        DESCRIPTION:
            RandomSearch algorithm performs random sampling on hyperparameter 
            space to identify optimal hyperparameters. It works for
            teradataml analytic functions from SQLE, BYOM, VAL and UAF features.
            teradataml RandomSearch allows user to perform hyperparameter tuning for 
            all model trainer and non-model trainer functions.
            When used for model trainer functions:
                * Based on evaluation metrics search determines best model.
                * All methods and properties can be used.
            When used for non-model trainer functions:
                * Only fit() method is supported.
                * User can choose the best output as they see fit to use this.

            teradataml RandomSearch also allows user to use input data as the 
            hyperparameter. This option can be suitable when the user wants to
            identify the best models for a set of input data. When user passes
            set of data as hyperparameter for model trainer function, the search
            determines the best data along with the best model based on the 
            evaluation metrics.
            Note:
                * configure.temp_object_type="VT" follows sequential execution.

        PARAMETERS:
            func:
                Required Argument.
                Specifies a teradataml analytic function from SQLE, VAL, and UAF.
                Types:
                    teradataml Analytic Functions
                        * Advanced analytic functions
                        * UAF
                        * VAL
                    Refer to display_analytic_functions() function for list of functions.

            params:
                Required Argument.
                Specifies the parameter(s) of a teradataml analytic function. 
                The parameter(s) must be in dictionary. keys refers to the 
                argument names and values refers to argument values for corresponding
                arguments. 
                Notes:
                    * One can specify the argument value in a tuple to run HPT 
                      with different arguments.
                    * Model trainer function arguments "id_column", "input_columns",
                      and "target_columns" must be passed in fit() method.
                    * All required arguments of non-model trainer function must be
                      passed while RandomSearch object creation.
                Types: dict
            
            n_iter:
                Optional Argument.
                Specifies the number of iterations random search need to be performed.
                Note:
                    * n_iter must be less than the size of parameter populations.
                Default Value: 10
                Types: int

        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError, ValueError
        
        EXAMPLES:
            >>> # Example 1: Model trainer function. Performing hyperparameter-tuning
            >>> #            on SVM model trainer function using random search algorithm.
  
            >>> # Load the example data.
            >>> load_example_data("teradataml", ["cal_housing_ex_raw"])
            
            >>> # Create teradataml DataFrame objects.
            >>> data_input = DataFrame.from_table("cal_housing_ex_raw")
            
            >>> # Scale "target_columns" with respect to 'STD' value of the column.
            >>> fit_obj = ScaleFit(data=data_input,
                                   target_columns=['MedInc', 'HouseAge', 'AveRooms',
                                                   'AveBedrms', 'Population', 'AveOccup',
                                                   'Latitude', 'Longitude'],
                                   scale_method="STD")
            
            >>> # Transform the data.
            >>> transform_obj = ScaleTransform(data=data_input,
                                               object=fit_obj.output,
                                               accumulate=["id", "MedHouseVal"])
            
            >>> # Define parameter space for model training.
            >>> # Note: These parameters create 6 models based on batch_size and iter_max.
            >>> params = {"input_columns":['MedInc', 'HouseAge', 'AveRooms',
                                           'AveBedrms', 'Population', 'AveOccup',
                                           'Latitude', 'Longitude'],
                           "response_column":"MedHouseVal",
                           "model_type":"regression",
                           "batch_size":(11, 50, 75),
                           "iter_max":(100, 301),
                           "lambda1":0.1,
                           "alpha":0.5,
                           "iter_num_no_change":60,
                           "tolerance":0.01,
                           "intercept":False,
                           "learning_rate":"INVTIME",
                           "initial_data":0.5,
                           "decay_rate":0.5,
                           "momentum":0.6,
                           "nesterov":True,
                           "local_sgd_iterations":1}
            
            >>> # Import trainer function and optimizer.
            >>> from teradataml import SVM, RandomSearch
            
            >>> # Initialize the random search optimizer with model trainer
            >>> # function and parameter space required for model training.
            >>> rs_obj = RandomSearch(func=SVM, params=params, n_iter=3)
            
            >>> # Perform model optimization for SVM function.
            >>> # Evaluation and prediction arguments are passed along with
            >>> # training dataframe.
            >>> rs_obj.fit(data=transform_obj.result, evaluation_metric="R2",
                           id_column="id", verbose=1)
                completed: |████████████████████████████████████████████████████████████| 100% - 3/3
            >>> # View trained models.
            >>> rs_obj.models
                  MODEL_ID DATA_ID                                         PARAMETERS STATUS        R2
                0    SVM_2    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS -3.668091
                1    SVM_1    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS -3.668091
                2    SVM_0    DF_0  {'input_columns': ['MedInc', 'HouseAge', 'AveR...   PASS -3.668091
            
            >>> # View model evaluation stats.
            >>> rs_obj.model_stats
                  MODEL_ID       MAE       MSE  MSLE        MAPE  ...        ME        R2        EV  MPD  MGD
                0    SVM_2  2.354167  6.715689   0.0  120.054758  ...  3.801619 -3.668091  0.184238  NaN  NaN
                1    SVM_1  2.354167  6.715689   0.0  120.054758  ...  3.801619 -3.668091  0.184238  NaN  NaN
                2    SVM_0  2.354167  6.715689   0.0  120.054758  ...  3.801619 -3.668091  0.184238  NaN  NaN

                [3 rows x 13 columns]
            
            >>> # Performing prediction on sampled data using best trained model.
            >>> test_data = transform_obj.result.iloc[:5]
            >>> rs_pred = rs_obj.predict(newdata=test_data, id_column="id")
            >>> print("Prediction result: \n", rs_pred.result)
                Prediction result:
                     id  prediction
                0   686   -0.024033
                1  2018   -0.069738
                2  1754   -0.117881
                3   670   -0.021818
                4   244   -0.187346
            
            >>> # Perform evaluation using best model.
            >>> rs_obj.evaluate()
            ############ result Output ############

                    MAE       MSE  MSLE        MAPE         MPE      RMSE  RMSLE        ME        R2        EV  MPD  MGD
            0  2.354167  6.715689   0.0  120.054758  120.054758  2.591465    0.0  3.801619 -3.668091  0.184238  NaN  NaN

            >>> # Retrieve any trained model.
            >>> rs_obj.get_model("SVM_1")
                ############ output_data Output ############

                   iterNum      loss       eta  bias
                0        3  2.012817  0.028868   0.0
                1        5  2.010455  0.022361   0.0
                2        6  2.009331  0.020412   0.0
                3        7  2.008276  0.018898   0.0
                4        9  2.006384  0.016667   0.0
                5       10  2.005518  0.015811   0.0
                6        8  2.007302  0.017678   0.0
                7        4  2.011636  0.025000   0.0
                8        2  2.014326  0.035355   0.0
                9        1  2.016398  0.050000   0.0

                ############ result Output ############

                                          predictor   estimate                                   value
                attribute
                -7                           Alpha    0.500000                              Elasticnet
                -3          Number of Observations   55.000000                                    None
                 5                      Population    0.000000                                    None
                 0                     (Intercept)    0.000000                                    None
                -17                   OneClass SVM         NaN                                   FALSE
                -16                         Kernel         NaN                                  LINEAR
                -1                   Loss Function         NaN  EPSILON_INSENSITIVE
                 7                        Latitude   -0.076648                                    None
                -9         Learning Rate (Initial)    0.050000                                    None
                -14                        Epsilon    0.100000                                    None


            >>> # View best data, model ID, score and parameters.
            >>> print("Best data ID: ", rs_obj.best_data_id)
                Best data ID:  DF_0
            >>> print("Best model ID: ", rs_obj.best_model_id)
                Best model ID:  SVM_2
            >>> print("Best model score: ", rs_obj.best_score_)
                Best model score:  -3.6680912444156455
            >>> print("Best model parameters: ", rs_obj.best_params_)
                Best model parameters:  {'input_columns': ['MedInc', 'HouseAge', 'AveRooms', 
                                        'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude'], 
                                        'response_column': 'MedHouseVal', 'model_type': 'regression', 
                                        'batch_size': 50, 'iter_max': 301, 'lambda1': 0.1, 'alpha': 0.5, 
                                        'iter_num_no_change': 60, 'tolerance': 0.01, 'intercept': False, 
                                        'learning_rate': 'INVTIME', 'initial_data': 0.5, 'decay_rate': 0.5, 
                                        'momentum': 0.6, 'nesterov': True, 'local_sgd_iterations': 1, 
                                        'data': '"ALICE"."ml__select__1696595493985650"'}
            
            >>> # Update the default model.
            >>> rs_obj.set_model("SVM_1")
            
            >>> # Example 2: Non-Model trainer function. Performing random search
            >>> #            on AntiSelect model trainer function using random
            >>> #            search algorithm.
            
            >>> # Load the example dataset.
            >>> load_example_data("teradataml", "titanic")
            
            >>> # Create teradaraml dataframe.
            >>> titanic = DataFrame.from_table("titanic")
            
            >>> # Define the non-model trainer function parameter space.
            >>> # Include input data in parameter space for non-model trainer function.
            >>> # Note: These parameters creates two model hyperparameters.
            >>> params = {"data":titanic, "exclude":(['survived', 'age'],['age'],
                                                     ['survived', 'name', 'age'],
                                                     ['ticket'],['parch'],['sex','age'],
                                                     ['survived'], ['ticket','parch'],
                                                     ["ticket", "parch", "sex", "age"])}
            
            >>> # Import non-model trainer function and optimizer.
            >>> from teradataml import Antiselect, RandomSearch
            
            >>> # Initialize the random search optimizer with non-model trainer
            >>> # function and parameter space required for non-model training.
            >>> rs_obj = RandomSearch(func=Antiselect, params=params, n_iter=4)
            
            >>> # Perform execution of Antiselect function.
            >>> rs_obj.fit()
            
            >>> # Note: Since it is a non-model trainer function model ID, score
            >>> # and parameters are not applicable here.
            >>> # View trained models.
            >>> rs_obj.models
                       MODEL_ID                                         PARAMETERS STATUS
                0  ANTISELECT_1  {'data': '"titanic"', 'exclude': ['survived', ...   PASS
                1  ANTISELECT_3  {'data': '"titanic"', 'exclude': ['ticket', 'p...   PASS
                2  ANTISELECT_2     {'data': '"titanic"', 'exclude': ['survived']}   PASS
                3  ANTISELECT_0   {'data': '"titanic"', 'exclude': ['sex', 'age']}   PASS
            
            >>> # Retrieve any trained model using "MODEL_ID".
            >>> rs_obj.get_model("ANTISELECT_0")
                ############ result Output ############

                   passenger  survived  pclass                                                name  sibsp  parch             ticket      fare cabin embarked
                0        162         1       2  Watt, Mrs. James (Elizabeth "Bessie" Inglis Milne)      0      0         C.A. 33595   15.7500  None        S
                1        591         0       3                                Rintamaki, Mr. Matti      0      0  STON/O 2. 3101273    7.1250  None        S
                2        387         0       3                     Goodwin, Master. Sidney Leonard      5      2            CA 2144   46.9000  None        S
                3        469         0       3                                  Scanlan, Mr. James      0      0              36209    7.7250  None        Q
                4        326         1       1                            Young, Miss. Marie Grice      0      0           PC 17760  135.6333   C32        C
                5        265         0       3                                  Henry, Miss. Delia      0      0             382649    7.7500  None        Q
                6        530         0       2                         Hocking, Mr. Richard George      2      1              29104   11.5000  None        S
                7        244         0       3                       Maenpaa, Mr. Matti Alexanteri      0      0  STON/O 2. 3101275    7.1250  None        S
                8         61         0       3                               Sirayanian, Mr. Orsen      0      0               2669    7.2292  None        C
                9        122         0       3                          Moore, Mr. Leonard Charles      0      0          A4. 54510    8.0500  None        S

        """

        self.__params = params.copy()
        super().__init__(func=func, params=self.__params)
        # Validate argument 'n_iter'
        awu_matrix = []
        awu_matrix.append(["n_iter", n_iter, True, int])
        _Validators._validate_positive_int(n_iter, "n_iter")
        self.set_parameter_grid()
        parameter_space = self.get_parameter_grid()
        # Validates the range of n_iter should be greater than or equal to 1 and
        # less than or equal to parameter space.
        _Validators._validate_argument_range(n_iter, "n_iter", 1, len(parameter_space), True, True)
        self._n_iter = n_iter

    def __populate_params_grid(self):
        """
        DESCRIPTION:
            Populate parameter grid based on the search algorithm. In random search,
            Random selection performed on given hyperparameters. 
        
        PARAMETERS:
            n_iter:
                Required Argument.
                Specifies number of parameters need to be sampled.
                Types: int

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> self.__populate_params_grid()
        """
        # Populate the parameter space with random and non-repetitive value
        if self.discard_invalid_column_params:
            # Defining the empty data_grouped_dict to group the parameters based on data_id.
            data_grouped_dict = defaultdict(list)
            for parameter in self._parameter_grid:
                # Extracting the data_id from the parameter.
                data_id = parameter['data_id']
                # Grouping the parameters based on data_id.
                data_grouped_dict[data_id].append(parameter)
            # Converting the grouped dictionary to list.
            data_grouped_dict = list(data_grouped_dict.values())
            parameter_grid = []
            for group in data_grouped_dict:
                # Randomly selecting the n_iter parameters from the grouped data.
                tmp = random.sample(group, self._n_iter)
                parameter_grid.extend(tmp)

            # Setting the parameter grid.
            self._parameter_grid = parameter_grid
        else:
            self._parameter_grid = random.sample(self.get_parameter_grid(), self._n_iter)
    
    def fit(self, 
            data=None,
            evaluation_metric=None, 
            early_stop=None,
            frac=0.8,
            run_parallel=True,
            wait=True,
            verbose=0,
            stratify_column=None, 
            sample_id_column=None, 
            sample_seed=None,
            max_time=None,
            **kwargs):   
        """
        DESCRIPTION:
            Function to perform hyperparameter tuning using RandomSearch algorithm.
            Notes:
                * In the Model trainer function, the best parameters are 
                  selected based on training results.
                * In the Non model trainer function, First execution parameter
                  set is selected as the best parameters.

        PARAMETERS:
            data:
                Optional Argument.
                Specifies the input teradataml DataFrame for model trainer function.
                Notes:
                    * DataFrame need not to be passed in fit() methods, when "data" is 
                      passed as a model hyperparameters ("params"). 
                    * "data" is a required argument for model trainer functions.
                    * "data" is ignored for non-model trainer functions.
                    * "data" can be contain single DataFrame or multiple DataFrame.
                    * One can pass multiple dataframes to "data". Hyperparameter 
                      tuning is performed on all the dataframes for every model 
                      parameter.
                    * "data" can be either a dictionary OR a tuple OR a dataframe.
                        * If it is a dictionary then Key represents the label for 
                          dataframe and Value represents the dataframe.
                        * If it is a tuple then teradataml converts it to dictionary
                          by generating the labels internally.
                        * If it is a dataframe then teradataml label it as "DF_0".
                Types: teradataml DataFrame, dictionary, tuples

            evaluation_metric:
                Optional Argument.
                Specifies the evaluation metrics to considered for model 
                evaluation.
                Notes:
                    * evaluation_metric applicable for model trainer functions.
                    * Best model is not selected when evaluation returns 
                      non-finite values.
                    * MPD, MGD, RMSE, RMSLE are not supported for OpenSourceML models.
                Permitted Values:
                    * Classification: Accuracy, Micro-Precision, Micro-Recall,
                                      Micro-F1, Macro-Precision, Macro-Recall,
                                      Macro-F1, Weighted-Precision, 
                                      Weighted-Recall,
                                      Weighted-F1.
                    * Regression: MAE, MSE, MSLE, MAPE, MPE, RMSE, RMSLE, ME, 
                                  R2, EV, MPD, MGD
                    
                Default Value:
                    * Classification: Accuracy
                    * Regression: MAE
                Types: str

            early_stop:
                Optional Argument.
                Specifies the early stop mechanism value for model trainer 
                functions. Hyperparameter tuning ends model training when 
                the training model evaluation metric attains "early_stop" value.
                Note:
                    * Early stopping supports only when evaluation returns 
                      finite value.
                Types: int or float

            frac:
                Optional Argument.
                Specifies the split percentage of rows to be sampled for training 
                and testing dataset. "frac" argument value must range between (0, 1).
                Notes: 
                    * This "frac" argument is not supported for non-model trainer 
                      function.
                    * The "frac" value is considered as train split percentage and 
                      The remaining percentage is taken into account for test splitting.
                Default Value: 0.8
                Types: float
            
            run_parallel:
                Optional Argument.
                Specifies the parallel execution functionality of hyperparameter 
                tuning. When "run_parallel" set to true, model functions are 
                executed concurrently. Otherwise, model functions are executed 
                sequentially.
                Default Value: True
                Types: bool
            
            wait:
                Optional Argument.
                Specifies whether to wait for the completion of execution 
                of hyperparameter tuning or not. When set to False, hyperparameter 
                tuning is executed in the background and user can use "is_running()" 
                method to check the status. Otherwise it waits until the execution 
                is complete to return the control back to user.
                Default Value: True
                Type: bool

            verbose:
                Optional Argument.
                Specifies whether to log the model training information and display 
                the logs. When it is set to 1, progress bar alone logged in the 
                console. When it is set to 2, along with progress bar, execution 
                steps and execution time is logged in the console. When it is set 
                to 0, nothing is logged in the console. 
                Note:
                    * verbose is not significant when "wait" is 'False'.
                Default Value: 0
                Type: bool
            
            sample_seed:
                Optional Argument.
                Specifies the seed value that controls the shuffling applied
                to the data before applying the Train-Test split. Pass an int for 
                reproducible output across multiple function calls.
                Notes:
                    * When the argument is not specified, different
                      runs of the query generate different outputs.
                    * It must be in the range [0, 2147483647]
                    * Seed is supported for stratify column.
                Types: int

            stratify_column:
                Optional Argument.
                Specifies column name that contains the labels indicating
                which data needs to be stratified for TrainTest split. 
                Notes:
                    * seed is supported for stratify column.
                Types: str
            
            sample_id_column:
                Optional Argument.
                Specifies the input data column name that has the
                unique identifier for each row in the input.
                Note:
                    * Mandatory when "sample_seed" argument is present.
                Types: str

            max_time:
                Optional Argument.
                Specifies the maximum time for the completion of Hyperparameter tuning execution.
                Default Value: None
                Types: int or float

            kwargs:
                Optional Argument.
                Specifies the keyword arguments. Accepts additional arguments 
                required for the teradataml analytic function.

        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> # Create an instance of the RandomSearch algorithm called "optimizer_obj" 
            >>> optimizer_obj = RandomSearch(func=SVM, params=params, n_iter=3)

            >>> eval_params = {"id_column": "id",
                               "accumulate": "MedHouseVal"}
            >>> # Example 1: Passing single DataFrame for model trainer function.
            >>> optimizer_obj.fit(data=train_df,
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)
            
            >>> # Example 2: Passing multiple datasets as tuple of DataFrames for 
            >>> #            model trainer function.
            >>> optimizer_obj.fit(data=(train_df_1, train_df_2),
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)  
            
            >>> # Example 3: Passing multiple datasets as dictionary of DataFrames 
            >>> #            for model trainer function.
            >>> optimizer_obj.fit(data={"Data-1":train_df_1, "Data-2":train_df_2},
                                  evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params)  

            >>> # Example 4: No data argument passed in fit() method for model trainer function.
            >>> #            Note: data argument must be passed while creating HPT object as 
            >>> #                  model hyperparameters.
            
            >>> # Define parameter space for model training with "data" argument.
            >>> params = {"data":(df1, df2),
                          "input_columns":['MedInc', 'HouseAge', 'AveRooms',
                                           'AveBedrms', 'Population', 'AveOccup',
                                           'Latitude', 'Longitude'],
                          "response_column":"MedHouseVal",
                          "model_type":"regression",
                          "batch_size":(11, 50, 75),
                          "iter_max":(100, 301),
                          "intercept":False,
                          "learning_rate":"INVTIME",
                          "nesterov":True,
                          "local_sgd_iterations":1}
            
            >>> # Create "optimizer_obj" using RandomSearch algorithm and perform 
            >>> # fit() method without any "data" argument for model trainer function.
            >>> optimizer_obj.fit(evaluation_metric="MAE",
                                  early_stop=70.9,
                                  **eval_params) 

            >>> # Example 5: Do not pass data argument in fit() method for 
            >>> #            non-model trainer function.
            >>> #            Note: data argument must be passed while creating HPT  
            >>> #                  object as model hyperparameters.
            >>> optimizer_obj.fit() 

            >>> # Example 6: Passing "verbose" argument value '1' in fit() method to 
            >>> #            display model log.
            >>> optimizer_obj.fit(data=train_df, evaluation_metric="R2",
                                  verbose=1, **eval_params)
                completed: |████████████████████████████████████████████████████████████| 100% - 6/6

            >>> # Example 7: max_time argument is passed in fit() method.
            >>> # Model training parameters
            >>> model_params = {"input_columns":['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
            ...                 "response_column" : 'species',
            ...                 "max_depth":(5,10,15),
            ...                 "lambda1" : (1000.0,0.001),
            ...                 "model_type" :"Classification",
            ...                 "seed":32,
            ...                 "shrinkage_factor":0.1,
            ...                 "iter_num":(5, 50)}
            >>>
            >>> eval_params = {"id_column": "id",
            ...                "accumulate": "species",
            ...                "model_type":'Classification',
            ...                "object_order_column":['task_index', 'tree_num', 'iter','class_num', 'tree_order']
            ...               }
            >>>
            >>> # Import model trainer and optimizer
            >>> from teradataml import XGBoost, RandomSearch
            >>>
            >>> # Initialize the RandomSearch optimizer with model trainer
            >>> # function and parameter space required for model training.
            >>> rs_obj = RandomSearch(func=XGBoost, params=model_params, n_iter=5)
            >>>
            >>> # fit() method with max_time argument(in seconds) for model trainer function.
            >>> rs_obj.fit(data=data, max_time=30, verbose=2, **eval_params)
                Model_id:XGBOOST_3 - Run time:28.292s - Status:PASS - ACCURACY:0.8                 
                Model_id:XGBOOST_0 - Run time:28.291s - Status:PASS - ACCURACY:0.867               
                Model_id:XGBOOST_2 - Run time:28.289s - Status:PASS - ACCURACY:0.867               
                Model_id:XGBOOST_1 - Run time:28.291s - Status:PASS - ACCURACY:0.867               
                Computing: ｜⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫿⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾⫾｜ 80% - 4/5
            >>>
            >>> # status 'SKIP' for the models which are not completed within the max_time.
            >>> rs_obj.models
                    MODEL_ID	DATA_ID	                                       PARAMETERS	STATUS	ACCURACY
                0	XGBOOST_3	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.800000
                1	XGBOOST_4	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	SKIP	NaN
                2	XGBOOST_0	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.866667
                3	XGBOOST_2	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.866667
                4	XGBOOST_1	DF_0	{'input_columns': ['sepal_length', 'sepal_widt...	PASS	0.866667
        """

        # Set discard_invalid_column_params flag.
        self.discard_invalid_column_params =kwargs.get("discard_invalid_column_params", False)

        if self.discard_invalid_column_params:
            # Setting model trainer input data
            super()._setting_model_trainer_data(data)
            # Mapping the data with input columns
            super()._data_mapping()
            # Setting the lambda function to None.
            self._setting_model_trainer_data = lambda data: None
            self._BaseSearch__update_model_parameters = lambda: None
        
        # Populate parameter grid.
        self.__populate_params_grid()

        # Calling baseSearch class fit method.
        super().fit(data, evaluation_metric, early_stop, 
                    frac, run_parallel, wait, verbose, 
                    stratify_column, sample_id_column, 
                    sample_seed, max_time, **kwargs)

