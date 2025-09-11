# ################################################################## 
# 
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Adithya Avvaru (adithya.avvaru@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# 
# Version: 1.0
# Function Version: 1.0
#
# This file contains object wrapper class for lightgbm opensource package.
# 
# ################################################################## 


import base64
import json
import os
import pickle
import warnings
from collections import OrderedDict
from importlib import import_module

import numpy
import pandas as pd
from teradatasqlalchemy import BLOB, CLOB, FLOAT

from teradataml import (_TDML_DIRECTORY, MessageCodes, Messages,
                        TeradataMlException, UtilFuncs, execute_sql)
from teradataml.opensource._base import (_FunctionWrapper,
                                         _OpenSourceObjectWrapper)
from teradataml.opensource._constants import OpenSourcePackage
from teradataml.opensource._sklearn import _SkLearnObjectWrapper
from teradataml.opensource._wrapper_utils import _generate_new_name


class _LightgbmDatasetWrapper(_OpenSourceObjectWrapper):
    """
    Internal class for Lightgbm Dataset object.
    """
    OPENSOURCE_PACKAGE_NAME = OpenSourcePackage.LIGHTGBM
    def __init__(self, model=None, module_name=None, class_name=None, kwargs=None):

        file_type = "file_fn_lightgbm"
        self._template_file = "dataset.template"
        self._pkgs = ["lightgbm", "scikit-learn", "numpy", "scipy"]
        super().__init__(model=model, module_name=module_name, class_name=class_name, kwargs=kwargs)

        self._scripts_path = os.path.join(_TDML_DIRECTORY, "data", "scripts", "lightgbm")

        self._script_file_name = _generate_new_name(type=file_type, extension="py")
        self._data_args = OrderedDict()

        self._initialize_variables(table_name_prefix="td_lightgbm_")
        if model:
            self.modelObj = model
            self.module_name = model.__module__.split("._")[0]
            self.class_name = model.__class__.__name__
            _model_init_arguments = model.__init__.__code__.co_varnames
            self.kwargs = dict((k, v) for k, v in model.__dict__.items() if k in _model_init_arguments)

            self.pos_args = tuple() # Kept empty as all are moved to kwargs.
        else:
            self.initial_args = kwargs
            self._initialize_object()
            self.__run_func_returning_objects(all_kwargs=self.kwargs, use_dummy_initial_file=True)

    def __getattr__(self, name):
        if name in ["construct"]:
            wt = self.initial_args.get("weight", None) if hasattr(self, "initial_args") else None
            if (isinstance(wt, pd.DataFrame) and wt.iloc[0]["get_weight"] is not None) or wt is not None:
                raise ValueError(f"The method '{name}' is not implemented when \"weight\" argument is provided.")

        if name in ["set_weight", "set_label"]:
            raise NotImplementedError(f"'{name}' is not implemented for Lightgbm Dataset object.\n")
        
        if name == "set_group" and isinstance(self.modelObj, pd.DataFrame):
            raise NotImplementedError("'set_group' is not implemented for Lightgbm Dataset object "\
                                    "in multi-model case as different models have different number "\
                                    "of rows and grouping them in one set of group is not possible.")

        return super().__getattr__(name)    

    def save_binary(self, file_name, save_in_vantage=False):
        """
        DESCRIPTION:
            Save the model(s) to a binary file(s). Additionally the files are saved
            to Vantage if "save_in_vantage" argument is set to True.

        PARAMETERS:
            file_name:
                Required Argument.
                Specifies the absolute path of the file name to which lightgbm Dataset
                object is to be saved to.
                Note:
                    * File name is prefixed with underscore delimitted partition column
                      values in multi-model case.
                    * File name excluding extension and file name with extension should
                      not already be present in Vantage.
                Type: str

            save_in_vantage:
                Optional Argument.
                Specifies whether to save the file in VantageCloud Enterprise or user environment
                of VantageCloud Lake.
                Default Value: False
                Type: bool

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> # Save the lightgbm Dataset object to a binary file in client.
            >>> lightgbm_dataset.save_binary("lightgbm_dataset.pickle")

            >>> # Save the lightgbm Dataset object to a binary file in client and Vantage.
            >>> lightgbm_dataset.save_binary("lightgbm_dataset.pickle", save_in_vantage=True)

        """
        _file_name = os.path.basename(file_name)
        _file_dir = os.path.dirname(file_name)
        if not isinstance(self.modelObj, pd.DataFrame):
            self.modelObj.save_binary(file_name)
            file_prefix = _file_name.split(".")[0]
            print("Model saved in client as ", file_name)
            if save_in_vantage:
                self._install_script_file(file_identifier=file_prefix,
                                          file_name=_file_name,
                                          is_binary=True,
                                          file_location=_file_dir)
                print(f"Model file {_file_name} saved in Vantage.")
        else:
            no_of_unique_partitions = len(self._fit_partition_unique_values)
            no_of_partitioning_cols = len(self._fit_partition_unique_values[0])

            print("Multiple model files in multi-model case are saved with different names"\
                  " with partition column values information delimited by underscore.")

            for i in range(no_of_unique_partitions):
                partition_join = "_".join(list(map(str, self.modelObj.iloc[i, :no_of_partitioning_cols])))
                # Split extension from file name to add partition column values before extension.
                __file_name, __file_ext = os.path.splitext(_file_name)
                __file_name = f"{__file_name}_{partition_join}{__file_ext}"
                __file_prefix = os.path.splitext(__file_name)[0] # File identifier.

                __joined_file = os.path.join(_file_dir, __file_name)
                self.modelObj.iloc[i]["model"].save_binary(__joined_file)

                if save_in_vantage:
                    self._install_script_file(file_identifier=__file_prefix,
                                              file_name=__file_name,
                                              is_binary=True,
                                              file_location=_file_dir)
                    print(f"Model file {__file_name} saved in Vantage.")

    def create_valid(self, **kwargs):
        if isinstance(self.modelObj, pd.DataFrame):
            raise NotImplementedError("'create_valid' is not implemented for Lightgbm Dataset object"\
                                      " in multi-model case.")
        return self.__run_func_returning_objects(all_kwargs=kwargs, func_name="create_valid")

    def __run_func_returning_objects(self, all_kwargs, func_name=None, use_dummy_initial_file=False):
        """
        Run the function with all the arguments passed from `td_sklearn.<function_name>` function.
        """
        kwargs = all_kwargs.copy()

        if kwargs.get("label", None) is not None:
            label_df = kwargs["label"]
            self._fit_label_columns_types = []
            self._fit_label_columns_python_types = []
            for l_c in label_df.columns:
                column_data = label_df._td_column_names_and_sqlalchemy_types[l_c.lower()]
                self._fit_label_columns_types.append(column_data)
                self._fit_label_columns_python_types.append(column_data.python_type.__name__)

        replace_dict, partition_cols = self._process_data_for_funcs_returning_objects(kwargs)

        script_file_path = f"{self._script_file_name}" if self._is_lake_system \
            else f"./{self._db_name}/{self._script_file_name}"

        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {script_file_path} {self._model_file_name_prefix} {self._is_lake_system}"

        model_type = BLOB() if self._is_lake_system else CLOB()
        return_types = [(col, self._tdml_df._td_column_names_and_sqlalchemy_types[col.lower()]) 
                        for col in partition_cols] + [("model", model_type)]

        if "reference" in kwargs.keys() and kwargs["reference"] is not None:
            # "reference" is another Dataset object which is passed as an argument.
            # It should be accessed through model file name prefix as it raises an exception
            # if we try to dump it as json -`TypeError: Object of type Dataset is not JSON serializable`.
            self.initial_args["reference"]._install_initial_model_file()
            kwargs["reference"] = self.initial_args["reference"]._model_file_name_prefix

        replace_dict.update({"<all_col_names>": str(list(self._tdml_df.columns)),
                             "<params>": json.dumps(kwargs),
                             "<module_name>": f"'{self.module_name}'",
                             "<class_name>": f"'{self.class_name}'",
                             "<func_name>": f"'{func_name}'" if func_name else "None"})

        # Generate new file in .teradataml directory and install it to Vantage.
        self._prepare_and_install_file(replace_dict=replace_dict)

        if partition_cols:
            self._fit_partition_unique_values = self._tdml_df.drop_duplicate(partition_cols).get_values()

        self._install_initial_model_file(use_dummy_initial_file=use_dummy_initial_file)

        self._model_data = self._run_script(self._tdml_df, script_command, partition_cols, return_types)
        self._model_data._index_label = None

        self._extract_model_objs(n_unique_partitions=len(self._fit_partition_unique_values),
                                 n_partition_cols=len(partition_cols))

        # File cleanup after processing.
        os.remove(self._script_file_local)
        self._remove_script_file(self._script_file_name)

        return self

    def deploy(self, model_name, replace_if_exists=False):
        raise ValueError("lightgbm Dataset object is not the model object that can be trained. "
                         "Hence, not deployable.")

class _LightgbmFunctionWrapper(_FunctionWrapper):
    OPENSOURCE_PACKAGE_NAME = OpenSourcePackage.LIGHTGBM
    def __init__(self, module_name=None, func_name=None):
        file_type = "file_fn_lightgbm"
        template_file = "lightgbm_function.template"
        self._pkgs = ["lightgbm", "scikit-learn", "numpy", "scipy"]
        self._script_file_name = _generate_new_name(type=file_type, extension="py")
        super().__init__(module_name, func_name, file_type=file_type, template_file=template_file)
        self._scripts_path = os.path.join(_TDML_DIRECTORY, "data", "scripts", "lightgbm")

    def _extract_model_objs(self, n_unique_partitions=1, n_partition_cols=1, record_eval_exists=False):
        """
        Internal function to extract lightgbm object from the model(s) depending on the number of
        partitions. When it is only one model, it is directly used as modelObj.
        When it is multiple models, it is converted to pandas DataFrame and stored in modelObj.

        PARAMETERS:
            n_unique_partitions:
                Optional Argument.
                Specifies the number of unique partitions. If this argument is greater than 1,
                then pandas DataFame is created for modelObj. Otherwise, model object is directly
                stored in modelObj.
                Type: int

            n_partition_cols:
                Optional Argument.
                Specifies the number of partition columns. Since partition columns are stored in
                the first columns of the self.model_data, this argument is used to extract model
                object and other columns (console_output) from self.model_data.
                Type: int
            
            record_eval_exists:
                Optional Argument.
                Specifies whether record_evaluation callback exists in the function call.
                If yes, then record_evaluation_result is also extracted from the model data.
                Type: bool
        
        RETURNS:
            None
        
        RAISES:
            ValueError
        
        EXAMPLES:
            >>> # Extract model object, console output and record_evaluation results from the model
            >>> # data and assign them to self.modelObj.
            >>> self._extract_model_objs(n_unique_partitions=4, n_partition_cols=2, record_eval_exists=True)

        """
        vals = execute_sql("select * from {}".format(self._model_data._table_name)).fetchall()

        # pickle will issue a caution warning, if model pickling was done with
        # different library version than used here. The following disables any warnings
        # that might otherwise show in the scriptlog files on the Advanced SQL Engine
        # nodes in this case. Yet, do keep an eye for incompatible pickle versions.
        warnings.filterwarnings("ignore")

        model_obj = None
        console_opt = None
        record_eval_result = None
        # Extract and unpickle the following:
        # - column next to partition columns - model object.
        # - column next to model object - console output.
        # - column next to console output - record_evaluation_result (if record_evaluation callback
        #   is there in input).
        for i, row in enumerate(vals):
            if self._is_lake_system:
                model_obj = pickle.loads(row[n_partition_cols])
                # console_output is stored in the column next to model object.
                console_opt = row[n_partition_cols+1].decode()
                if record_eval_exists:
                    # record_evaluation_result is stored in the column next to console_output.
                    record_eval_result = pickle.loads(row[n_partition_cols+2])
            else:
                model_obj = pickle.loads(base64.b64decode(row[n_partition_cols].partition("'")[2]))
                # console_output is stored in the column next to model object.
                console_opt = base64.b64decode(row[n_partition_cols+1].partition("'")[2]).decode()
                if record_eval_exists:
                    # record_evaluation_result is stored in the column next to console_output.
                    record_eval_result = pickle.loads(
                        base64.b64decode(row[n_partition_cols+2].partition("'")[2]))
            row[n_partition_cols] = model_obj
            row[n_partition_cols+1] = console_opt
            if record_eval_exists:
                row[n_partition_cols+2] = record_eval_result
            vals[i] = row
        if n_unique_partitions == 1:
            # Return both model object and console output for single model case.
            pdf_data = [model_obj, console_opt]
            if record_eval_exists:
                # Add record_evaluation_result to the pandas df if exists.
                pdf_data.append(record_eval_result)
            self.modelObj = pd.DataFrame([pdf_data],
                                         # First column is partition column. Hence, removed.
                                         columns=self._model_data.columns[1:])
        elif n_unique_partitions > 1:
            self.modelObj = pd.DataFrame(vals, columns=self._model_data.columns)
        else:
            ValueError("Number of partitions should be greater than 0.")

        warnings.filterwarnings("default")

    def __call__(self, **kwargs):

        if self._func_name == "cv" and kwargs.get("return_cvbooster", None):
            raise NotImplementedError("return_cvbooster argument is not supported yet.")

        train_set = kwargs.pop("train_set")

        train_set._install_initial_model_file()
        
        # Data with only partition columns to run training on correct Dataset object in
        # appropriate AMP/Node.
        data = train_set._model_data.drop(columns="model")

        kwargs["train_set"] = train_set._model_file_name_prefix
        train_part_unique_vals = train_set._fit_partition_unique_values

        partition_cols = data.columns # Because all the columns are parition columns.

        valid_sets = kwargs.pop("valid_sets", None)  
        if valid_sets:
            kwargs["valid_sets"] = []
            for _, val in enumerate(valid_sets):
                val._install_initial_model_file()
                kwargs["valid_sets"].append(val._model_file_name_prefix)
                val_part_unique_vals = val._fit_partition_unique_values

                # Make sure all datasets are partitioned on same column values.
                if not self._validate_equality_of_partition_values(train_part_unique_vals,
                                                                   val_part_unique_vals):
                    raise TeradataMlException(
                        Messages.get_message(MessageCodes.PARTITION_VALUES_NOT_MATCHING,
                                             "training", "validation"),
                        MessageCodes.PARTITION_VALUES_NOT_MATCHING
                    )

        # Handle callbacks. Check if record_evaluation callback is present.
        rec_eval_exists = False # Flag to check if record_evaluation callback exists.
        if "callbacks" in kwargs and kwargs["callbacks"] is not None:
            callbacks = kwargs["callbacks"]
            callbacks = [callbacks] if not isinstance(callbacks, list) else callbacks
            for callback in callbacks:
                if callback["func_name"] == "record_evaluation":
                    rec_eval_exists = True
                    break
    
        script_file_path = f"{self._script_file_name}" if self._is_lake_system \
            else f"./{self._db_name}/{self._script_file_name}"

        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {script_file_path}"

        _, partition_indices, partition_types, partition_cols = \
            self._get_data_col_types_and_partition_col_indices_and_types(data,
                                                                         partition_cols,
                                                                         idx_delim=None,
                                                                         types_delim=None)

        model_file_prefix = None
        if self._is_lake_system:
            model_file_prefix = self._script_file_name.replace(".py", "")

        replace_dict = {"<module_name>": self._module_name,
                        "<func_name>": self._func_name,
                        "<is_lake_system>": str(self._is_lake_system),
                        "<params>": json.dumps(kwargs),
                        "<partition_cols_indices>": str(partition_indices),
                        "<partition_cols_types>": str(partition_types),
                        "<model_file_prefix>": str(model_file_prefix)}

        self._prepare_and_install_file(replace_dict=replace_dict)

        # One additional column "console_output" containing captured console output which contain
        # training and validation logs.
        model_type = BLOB() if self._is_lake_system else CLOB()
        return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                        for col in partition_cols] + \
                            [("model", model_type), ("console_output", model_type)]

        rec_eval_col_name = "record_evaluation_result"
        if rec_eval_exists:
            # If record_evaluation result exists in callback, add it to return types and corresponding
            # output in script.
            return_types.append((rec_eval_col_name, model_type))
        
        _no_of_unique_partitions = len(train_set._fit_partition_unique_values)

        try:
            self._model_data = self._run_script(data, script_command, partition_cols, return_types)

            self._extract_model_objs(n_unique_partitions=_no_of_unique_partitions,
                                    n_partition_cols=len(partition_cols),
                                    record_eval_exists=rec_eval_exists)

        except Exception as ex:
            # File cleanup if script execution fails or unable to fetch modelObj.
            os.remove(self._script_file_local)
            self._remove_script_file(self._script_file_name)
            raise

        # File cleanup after processing.
        os.remove(self._script_file_local)
        self._remove_script_file(self._script_file_name)

        if _no_of_unique_partitions == 1:
            # If only one partition, print the console output and return the model object.
            print(self.modelObj.iloc[0]["console_output"])
            if self._func_name == "cv":
                return self.modelObj.iloc[0]["model"]
            if not rec_eval_exists:
                booster_obj = _LightgbmBoosterWrapper(model=self.modelObj.iloc[0]["model"])
            else:
                # If record_evaluation results are there, return dictionary of model object and
                # record_evaluation results.
                model_dict = {"model" : self.modelObj.iloc[0]["model"],
                              rec_eval_col_name : self.modelObj.iloc[0][rec_eval_col_name]}
                booster_obj = _LightgbmBoosterWrapper(model=model_dict, model_column_name="model")
            booster_obj._is_default_partition_value_fit = True
            booster_obj._fit_partition_unique_values = train_part_unique_vals
            booster_obj._is_model_installed = False # As model is trained and returned but not saved to Vantage.

        else:
            if self._func_name == "cv":
                return self.modelObj
            booster_obj = _LightgbmBoosterWrapper(model=self.modelObj, model_column_name="model")
            booster_obj._fit_partition_colums_non_default = partition_cols
            booster_obj._is_default_partition_value_fit = train_set._is_default_partition_value_fit

        booster_obj._fit_partition_unique_values = train_part_unique_vals
        booster_obj._is_model_installed = False # As model is trained and returned but not saved to Vantage.

        return booster_obj


# Using _SkLearnObjectWrapper as base class for _LightgbmBoosterWrapper as _transform method is not
# present in _OpenSourceObjectWrapper class.
class _LightgbmBoosterWrapper(_SkLearnObjectWrapper):
    OPENSOURCE_PACKAGE_NAME = OpenSourcePackage.LIGHTGBM
    def __init__(self, model=None, module_name=None, class_name=None, kwargs=None, model_column_name=None):
        file_type = "file_fn_lightgbm_booster"
        self._model_column_name = model_column_name
        self.record_evaluation_result = None
        self._pkgs = ["lightgbm", "scikit-learn", "numpy", "scipy"]

        if model is not None and isinstance(model, dict) and self._model_column_name in model.keys():
            self.record_evaluation_result = model["record_evaluation_result"]
            model = model[self._model_column_name] # As model is stored in dictionary with key as "train_".

        _OpenSourceObjectWrapper.__init__(self, model=model, module_name=module_name, class_name=class_name, kwargs=kwargs)

        self._scripts_path = os.path.join(_TDML_DIRECTORY, "data", "scripts", "lightgbm")

        self._script_file_name = _generate_new_name(type=file_type, extension="py")

        self._initialize_variables(table_name_prefix="td_lightgbm_")
        if model is not None:
            first_model = model
            if isinstance(model, pd.DataFrame):
                first_model = model.iloc[0][self._model_column_name]
            self.modelObj = model
            self.module_name = first_model.__module__.split("._")[0]
            self.class_name = first_model.__class__.__name__
            _model_init_arguments = first_model.__init__.__code__.co_varnames
            self.kwargs = dict((k, v) for k, v in first_model.__dict__.items() if k in _model_init_arguments)

            self.pos_args = tuple()
        
        else:
            # Create model object from new positional and keyword arguments.
            if "train_set" in self.kwargs and self.kwargs["train_set"] is not None and \
                isinstance(self.kwargs["train_set"], _LightgbmDatasetWrapper):
                self.kwargs["train_set"] = self.kwargs["train_set"].modelObj
            
            from importlib import import_module
            class_obj = getattr(import_module(self.module_name), self.class_name)
            self.modelObj = class_obj(**self.kwargs)

    @property
    def model_info(self):
        """
        DESCRIPTION:
            Get the model information along with console output for multi-model case. Only model
            object is returned for single model case.
            Note:
                This is particularly useful in multi-model case when the user want to see the console
                output of each partition.

        PARAMETERS:
            None
        
        RAISES:
            None
                
        RETURNS:
            Pandas DataFrame

        EXAMPLES:
            # Load example data.
            >>> load_example_data("openml", ["multi_model_classification"])
            >>> df = DataFrame("multi_model_classification")
            >>> df.head(3)
                           col2      col3      col4  label group_column	partition_column_1	partition_column_2
            col1
            -2.560430  0.402232 -1.100742 -2.959588      0            9	                 0	                10
            -3.587546  0.291819 -1.850169 -4.331055      0           10	                 0	                10
            -3.697436  1.576888 -0.461220 -3.598652      0           10	                 0	                11
            
            # Get the feature and label data.
            >>> df_x = df.select(["col1", "col2", "col3", "col4"])
            >>> df_y = df.select("label")

            # Partition columns for multi model case.
            >>> part_cols = ["partition_column_1", "partition_column_2"]

            ## Single model case.
            # Create lightgbm Dataset object.
            >>> lgbm_data = td_lightgbm.Dataset(data=df_x, label=df_y, free_raw_data=False)

            # Train the model.
            >>> model = td_lightgbm.train(params={}, train_set=lgbm_data,
            ...                           num_boost_round=30,
            ...                           early_stopping_rounds=50)
            >>> model # This is object of _LightgbmBoosterWrapper class.
            <lightgbm.basic.Booster object at 0x0000025BD2459160>

            ## Multi model case.
            # Create lightgbm Dataset objects for training and validation.
            >>> obj_m = td_lightgbm.Dataset(df_x, df_y, free_raw_data=False,
                                            partition_columns=part_cols)

            >>> obj_m_v = td_lightgbm.Dataset(df_x, df_y, free_raw_data=False,
                                              partition_columns=part_cols)

            # Train the models in multi model case.
            >>> model = td_lightgbm.train(params={}, train_set=obj_m,
            ...                           num_boost_round=30,
            ...                           early_stopping_rounds=50,
            ...                           valid_sets=[obj_m_v, obj_m_v])
            >>> model
            partition_column_1  partition_column_2  \
            0                   1                  11   
            1                   0                  11   
            2                   1                  10   
            3                   0                  10   

                                                        model  \
            0  <lightgbm.basic.Booster object at 0x7f2e95ffc0a0>   
            1  <lightgbm.basic.Booster object at 0x7f2e95ffc880>   
            2  <lightgbm.basic.Booster object at 0x7f2e95f852e0>   
            3  <lightgbm.basic.Booster object at 0x7f2e95f853a0>   

                                                console_output  
            0  [LightGBM] [Warning] Auto-choosing col-wise mu...  
            1  [LightGBM] [Warning] Auto-choosing row-wise mu...  
            2  [LightGBM] [Warning] Auto-choosing col-wise mu...  
            3  [LightGBM] [Warning] Auto-choosing row-wise mu...

            # Get the model information which returns the printed output as pandas
            # DataFrame containing the model information along with console output.
            >>> model_info = lightgbm_booster.model_info

            # Print console output of first partition.
            >>> print(model_info.iloc[0]["console_output"])
            [LightGBM] [Warning] Auto-choosing col-wise multi-threading, the overhead of testing was 0.000043 seconds.
            You can set `force_col_wise=true` to remove the overhead.
            [LightGBM] [Info] Total Bins 136
            [LightGBM] [Info] Number of data points in the train set: 97, number of used features: 4
            [LightGBM] [Info] Start training from score 0.556701
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [1]	valid_0's l2: 0.219637	valid_1's l2: 0.219637
            Training until validation scores don't improve for 50 rounds
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [2]	valid_0's l2: 0.196525	valid_1's l2: 0.196525
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [3]	valid_0's l2: 0.178462	valid_1's l2: 0.178462
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [4]	valid_0's l2: 0.162887	valid_1's l2: 0.162887
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [5]	valid_0's l2: 0.150271	valid_1's l2: 0.150271
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [6]	valid_0's l2: 0.140219	valid_1's l2: 0.140219
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [7]	valid_0's l2: 0.131697	valid_1's l2: 0.131697
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [8]	valid_0's l2: 0.124056	valid_1's l2: 0.124056
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [9]	valid_0's l2: 0.117944	valid_1's l2: 0.117944
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [10]	valid_0's l2: 0.11263	valid_1's l2: 0.11263
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [11]	valid_0's l2: 0.105228	valid_1's l2: 0.105228
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [12]	valid_0's l2: 0.0981571	valid_1's l2: 0.0981571
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [13]	valid_0's l2: 0.0924294	valid_1's l2: 0.0924294
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [14]	valid_0's l2: 0.0877899	valid_1's l2: 0.0877899
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [15]	valid_0's l2: 0.084032	valid_1's l2: 0.084032
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [16]	valid_0's l2: 0.080988	valid_1's l2: 0.080988
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [17]	valid_0's l2: 0.0785224	valid_1's l2: 0.0785224
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [18]	valid_0's l2: 0.0765253	valid_1's l2: 0.0765253
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [19]	valid_0's l2: 0.0750803	valid_1's l2: 0.0750803
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [20]	valid_0's l2: 0.0738915	valid_1's l2: 0.0738915
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [21]	valid_0's l2: 0.07288	valid_1's l2: 0.07288
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [22]	valid_0's l2: 0.0718676	valid_1's l2: 0.0718676
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [23]	valid_0's l2: 0.0706037	valid_1's l2: 0.0706037
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [24]	valid_0's l2: 0.0695799	valid_1's l2: 0.0695799
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [25]	valid_0's l2: 0.0687507	valid_1's l2: 0.0687507
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [26]	valid_0's l2: 0.0680819	valid_1's l2: 0.0680819
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [27]	valid_0's l2: 0.0674077	valid_1's l2: 0.0674077
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [28]	valid_0's l2: 0.0665111	valid_1's l2: 0.0665111
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [29]	valid_0's l2: 0.0659656	valid_1's l2: 0.0659656
            [LightGBM] [Warning] No further splits with positive gain, best gain: -inf
            [30]	valid_0's l2: 0.0652665	valid_1's l2: 0.0652665
            Did not meet early stopping. Best iteration is:
            [30]	valid_0's l2: 0.0652665	valid_1's l2: 0.0652665

        """
        return self.modelObj

    def __getattr__(self, name):
        def __run_transform(*c, **kwargs):
            # Lightgbm predict method takes other keyword arguments along with data related arguments.
            # Hence need to generate script dynamically instead of standard scikit-learn's
            # sklearn_transform.py file.
            self._convert_pos_args_to_kwargs_for_function(c, kwargs, name)
            self._generate_script_file_from_template_file(kwargs=kwargs,
                                                          template_file="lightgbm_class_functions.template",
                                                          func_name=name)
           
            return self._transform(**kwargs)

        # TODO: Will be added as part of ELE-7150
        if name in ["add_valid", "eval", "eval_train", "eval_valid", "refit", "set_attr", "update"]:
            raise NotImplementedError(f"{name}() function is not supported yet. Will be added in future releases.")

        # TODO: Will be added as part of ELE-7150
        if name == "model_from_string" and not self._is_default_partition_value_fit:
            # For multi model case of model_from_string() function.
            raise NotImplementedError(
                "model_from_string() function is not supported for multi model case. Will be added in future releases.")
        
        # TODO: Will be added as part of ELE-7150
        if name == "set_network":
            raise NotImplementedError(
                "set_network() function is not applicable for Teradata Vantage.")

        if name in ["predict"]:
            return __run_transform
        return super().__getattr__(name)

    def _execute_function_locally(self, ten_row_data, feature_columns, label_columns, openml_obj,
                                  func_name, **kwargs):
        """
        Function which overrides the existing _execute_function_locally method to handle ValueError
        as argument names are different in lightgbm compared to scikit-learn.
        """
        X = numpy.array(ten_row_data)

        if label_columns:
            n_f = len(feature_columns)
            n_c = len(label_columns)
            y = X[:,n_f : n_f + n_c]
            X = X[:,:n_f]
            # predict() now takes 'y' ("label" lightgbm argument) also for it to return the labels
            # from script. Skipping 'y' in local run if passed.
            # Generally, 'y' is passed to return y along with actual output.
            # Since actual lightgbm predict() does not have "label" argument and have other arguments like
            # "start_iteration" etc, local run in try block is resulting into ValueError as
            # "ValueError: The truth value of an array with more than one element is ambiguous. 
            # Use a.any() or a.all()" for "start_iteration" argument because the value for "y" is
            # taken for "start_iteration" positional argument. Hence, skipping y in local run.
            try:
                trans_opt = getattr(openml_obj, func_name)(X, y, **kwargs)
            except TypeError as _:
                # Function which does not accept 'y' like predict_proba() raises error like
                # "predict_proba() takes 2 positional arguments but 3 were given".
                trans_opt = getattr(openml_obj, func_name)(X, **kwargs)
            except ValueError as _:
                trans_opt = getattr(openml_obj, func_name)(X, **kwargs)
        else:
            trans_opt = getattr(openml_obj, func_name)(X, **kwargs)

        if isinstance(trans_opt, numpy.ndarray) and trans_opt.shape == (X.shape[0],):
            trans_opt = trans_opt.reshape(X.shape[0], 1)

        return trans_opt

    def _transform(self, **kwargs):
        # Overwriting existing _transform method to handle data related arguments and other
        # keyword arguments.

        # Extract data and label columns.
        data_df = kwargs.pop("data") # "data" is mandatory argument for predict method.
        current_dfs = [data_df]
        feature_columns = data_df.columns

        label_columns = None
        if "label" in kwargs.keys() and kwargs["label"] is not None:
            label_df = kwargs.pop("label")
            current_dfs.append(label_df)
            label_columns = label_df.columns

        file_name = kwargs.pop("file_name")
        
        from teradataml.dataframe.dataframe_utils import DataFrameUtils
        data = DataFrameUtils()._get_common_parent_df_from_dataframes(current_dfs)

        try:
            # Install initial model file and script file to Vantage.
            self._install_model_and_script_files(file_name=file_name,
                                                file_location=self._tdml_tmp_dir)

            trans_opt =  super()._transform(data=data, feature_columns=feature_columns,
                                            label_columns=label_columns, file_name=file_name,
                                            **kwargs)
        except Exception as ex:
            # File cleanup if script execution fails or unable to fetch modelObj.
            os.remove(os.path.join(self._tdml_tmp_dir, file_name))
            self._remove_script_file(file_name)
            raise

        # File cleanup after processing.
        os.remove(os.path.join(self._tdml_tmp_dir, file_name))
        self._remove_script_file(file_name)

        return trans_opt

    def __repr__(self):
        return self.modelObj.__repr__()


class _LightgbmSklearnWrapper(_SkLearnObjectWrapper):
    OPENSOURCE_PACKAGE_NAME = OpenSourcePackage.LIGHTGBM
    def __init__(self, model=None, module_name=None, class_name=None, kwargs=None):
        self._pkgs = ["lightgbm", "scikit-learn", "numpy", "scipy"]
        super().__init__(model=model, module_name=module_name, class_name=class_name, kwargs=kwargs)
        self._scripts_path = os.path.join(_TDML_DIRECTORY, "data", "scripts", "lightgbm")

    def set_params(self, **params):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        for key, val in params.items():
            self.kwargs[key] = val

        self.__init__(None, self.module_name, self.class_name, self.kwargs)
        return self

    def _process_and_run_fit_and_score_run(self, pos_args, kwargs, func_name):
        """
        Internal function to process data related arguments and other keyword arguments
        for fit and score methods.
        """
        self._convert_pos_args_to_kwargs_for_function(pos_args, kwargs, func_name)

        label_columns = kwargs["y"].columns if kwargs.get("y", None) else kwargs.get("label_columns", None)

        if func_name == "score":
            # Get partition columns from the trained model object.
            if self._fit_partition_colums_non_default is not None and "partition_columns" not in kwargs.keys():
                kwargs["partition_columns"] = self._fit_partition_colums_non_default
        if func_name == "fit":
            earlier_partition_cols = kwargs.get("partition_columns", None)
            if earlier_partition_cols:
                self._is_default_partition_value_fit = False
                self._fit_partition_colums_non_default = earlier_partition_cols
            else:
                self._is_default_partition_value_fit = True
                self._fit_partition_colums_non_default = None

        generated_script_file = _generate_new_name(type=f"file_fn_lightgbm_sklearn_{func_name}", extension="py")

        non_data_related_args = self._get_non_data_related_args_from_kwargs(kwargs)
        
        replace_dict, partition_cols = self._process_data_for_funcs_returning_objects(kwargs)

        # Update non data related arguments in replace_dict containing data related argument information.
        replace_dict.update({"<params>": json.dumps(non_data_related_args),
                             "<func_name>": f"'{func_name}'",
                             "<model_file_prefix>": f"'{self._model_file_name_prefix}'",
                             "<is_lake_system>": str(self._is_lake_system)})

        # Replace placeholders in tempate file with actual values and write to new file.
        self._read_from_template_and_write_dict_to_file(template_file="lightgbm_sklearn.template",
                                                        replace_dict=replace_dict,
                                                        output_script_file_name=generated_script_file)

        if func_name == "fit":
            # Get unique values in partitioning columns.
            self._fit_partition_unique_values = self._tdml_df.drop_duplicate(partition_cols).get_values()

        # Install initial model file and script file to Vantage.
        self._install_model_and_script_files(file_name=generated_script_file,
                                             file_location=self._tdml_tmp_dir)

        # db_name is applicable for enterprise system.
        db_file_name = generated_script_file if self._is_lake_system else f"./{self._db_name}/{generated_script_file}"
        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {db_file_name}"

        return_types = [(col, self._tdml_df._td_column_names_and_sqlalchemy_types[col.lower()])
                        for col in partition_cols] 
        if func_name == "fit":
            model_type = BLOB() if self._is_lake_system else CLOB()
            return_types += [("model", model_type)]
        if func_name == "score":
            return_types += [("score", FLOAT())]
            # Checking the trained model installation. If not installed,
            # set flag to True (as it is already installed in
            # `self._install_model_and_script_files()` call).
            if not self._is_trained_model_installed:
                self._is_trained_model_installed = True

        try:
            opt = self._run_script(data=self._tdml_df, command=script_command,
                                partition_columns=partition_cols,
                                return_types=return_types)
        except Exception as ex:
            # File cleanup if script execution fails or unable to fetch modelObj.
            os.remove(os.path.join(self._tdml_tmp_dir, generated_script_file))
            self._remove_script_file(generated_script_file)
            raise

        # File cleanup after processing.
        os.remove(os.path.join(self._tdml_tmp_dir, generated_script_file))
        self._remove_script_file(generated_script_file)

        if func_name == "fit":
            self._model_data = opt
            self._assign_fit_variables_after_execution(self._tdml_df, partition_cols, label_columns)
            return self
        
        if func_name == "score":
            if self._is_default_partition_value_fit:
                # For single model case, partition column is internally generated and
                # no point in returning it to the user.
                opt = opt.select(func_name)
            return opt

    def fit(self, *c, **kwargs):
        return self._process_and_run_fit_and_score_run(c, kwargs, "fit")

    def score(self, *c, **kwargs):
        return self._process_and_run_fit_and_score_run(c, kwargs, "score")

    def _transform(self, **kwargs):
        # Overwriting existing _transform method to handle data related arguments and other
        # keyword arguments.

        # Extract data and label columns.
        data_df = kwargs.pop("X") # "X" is mandatory argument for predict method.
        current_dfs = [data_df]
        feature_columns = data_df.columns

        label_columns = None
        if "y" in kwargs.keys() and kwargs["y"] is not None:
            label_df = kwargs.pop("y")
            current_dfs.append(label_df)
            label_columns = label_df.columns

        file_name = kwargs.pop("file_name")
        
        from teradataml.dataframe.dataframe_utils import DataFrameUtils
        data = DataFrameUtils()._get_common_parent_df_from_dataframes(current_dfs)

        try:
            # Install initial model file and script file to Vantage.
            self._install_model_and_script_files(file_name=file_name,
                                                file_location=self._tdml_tmp_dir)

            trans_opt =  super()._transform(data=data, feature_columns=feature_columns,
                                            label_columns=label_columns, file_name=file_name,
                                            **kwargs)
        except Exception as ex:
            # File cleanup if script execution fails or unable to fetch modelObj.
            os.remove(os.path.join(self._tdml_tmp_dir, file_name))
            self._remove_script_file(file_name)
            raise

        # File cleanup after processing.
        os.remove(os.path.join(self._tdml_tmp_dir, file_name))
        self._remove_script_file(file_name)

        return trans_opt
   
    def __getattr__(self, name):
        def __run_transform(*c, **kwargs):
            # Lightgbm predict method takes other keyword arguments along with data related arguments.
            # Hence need to generate script dynamically instead of standard scikit-learn's
            # sklearn_transform.py file.
            generated_script_file = _generate_new_name(type=f"file_fn_lightgbm_sklearn_{name}", extension="py")

            self._convert_pos_args_to_kwargs_for_function(c, kwargs, name)
            self._generate_script_file_from_template_file(kwargs=kwargs,
                                                          template_file="lightgbm_class_functions.template",
                                                          func_name=name,
                                                          output_script_file_name=generated_script_file)
           
            return self._transform(**kwargs)

        if name in ["predict", "predict_proba"]:
            return __run_transform
        return super().__getattr__(name)
