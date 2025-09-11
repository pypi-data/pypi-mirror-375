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
# This file contains object wrapper class for scikit-learn opensource package.
# 
# ################################################################## 

import inspect
import math
import time

import numpy
import pandas as pd
import pandas.api.types as pt
from teradatasqlalchemy.types import (BLOB, CLOB, FLOAT, INTEGER, TIMESTAMP,
                                      VARCHAR)

from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.copy_to import _get_sqlalchemy_mapping
from teradataml.opensource._base import (_FunctionWrapper,
                                         _OpenSourceObjectWrapper)
from teradataml.opensource._constants import OpenSourcePackage
from teradataml.opensource._wrapper_utils import (
    _derive_df_and_required_columns, _validate_fit_run,
    _validate_opensource_func_args)
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators


class _SkLearnObjectWrapper(_OpenSourceObjectWrapper):

    OPENSOURCE_PACKAGE_NAME = OpenSourcePackage.SKLEARN
    _pkgs = ["scikit-learn", "numpy", "scipy"]

    def __init__(self, model=None, module_name=None, class_name=None, pos_args=None, kwargs=None):

        super().__init__(model=model, module_name=module_name, class_name=class_name,
                         pos_args=pos_args, kwargs=kwargs)

        self._initialize_variables(table_name_prefix="td_sklearn_")
        if model is not None:
            self.modelObj = model
            self.module_name = model.__module__.split("._")[0]
            self.class_name = model.__class__.__name__
            # __dict__ gets all the arguments as dictionary including default ones and positional
            # args.
            self.kwargs = model.__dict__
            self.pos_args = tuple() # Kept empty as all are moved to kwargs.
        else:
            self._initialize_object()

    def _validate_args_and_get_data(self, X=None, y=None, groups=None, kwargs={},
                                    skip_either_or_that=False):
        """
        Internal function to validate arguments passed to exposed opensource APIs and return
        parent DataFrame, feature columns, label columns, group columns, data partition columns.
        """
        _validate_opensource_func_args(X=X, y=y, groups=groups,
                                       fit_partition_cols=self._fit_partition_colums_non_default,
                                       kwargs=kwargs,
                                       skip_either_or_that=skip_either_or_that)
        return _derive_df_and_required_columns(X=X, y=y, groups=groups, kwargs=kwargs,
                                        fit_partition_cols=self._fit_partition_colums_non_default)

    def _run_fit_related_functions(self,
                                   data,
                                   feature_columns,
                                   label_columns,
                                   partition_columns,
                                   func,
                                   classes=None,
                                   file_name="sklearn_fit.py"):
        """
        Internal function to run fit() and partial_fit() functions.
        """
        label_columns = self._get_columns_as_list(label_columns)

        data, new_partition_columns = self._get_data_and_data_partition_columns(data,
                                                                                feature_columns,
                                                                                label_columns,
                                                                                partition_columns)

        model_type = BLOB() if self._is_lake_system else CLOB()
        return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()]) 
                        for col in new_partition_columns] + [("model", model_type)]

        if classes:
            class_type = type(classes[0]).__name__
            classes = "--".join([str(x) for x in classes])
        else:
            classes = str(None)
            class_type = str(None)
        
        data_column_types_str, partition_indices_str, _, new_partition_columns = \
            self._get_data_col_types_and_partition_col_indices_and_types(data, new_partition_columns)

        # db_name is applicable for enterprise system.
        db_file_name = file_name if self._is_lake_system else f"./{self._db_name}/{file_name}"
        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {db_file_name} {func} {len(feature_columns)} "\
            f"{len(label_columns)} {partition_indices_str} {data_column_types_str} "\
            f"{self._model_file_name_prefix} {classes} {class_type} {self._is_lake_system}"

        # Get unique values in partitioning columns.
        self._fit_partition_unique_values = data.drop_duplicate(new_partition_columns).get_values()

        self._install_initial_model_file()

        self._model_data = self._run_script(data, script_command, new_partition_columns,
                                            return_types)

        self._assign_fit_variables_after_execution(data, new_partition_columns, label_columns)

    def partial_fit(self, X=None, y=None, classes=None, **kwargs):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        st_time = time.time()

        # "classes" argument validation.
        arg_info_matrix = []
        arg_info_matrix.append(["classes", classes, True, (list)])
        _Validators._validate_function_arguments(arg_info_matrix)

        self._is_default_partition_value_fit = True # False when the user provides partition columns.

        data, feature_columns, label_columns, _, partition_columns = \
            self._validate_args_and_get_data(X=X, y=y, groups=None, kwargs=kwargs)

        if partition_columns:
            self._is_default_partition_value_fit = False
            self._fit_partition_colums_non_default = partition_columns

        self._run_fit_related_functions(data,
                                        feature_columns,
                                        label_columns,
                                        partition_columns,
                                        inspect.stack()[0][3],
                                        classes)

        self._partial_fit_execution_time = time.time() - st_time

        return self

    def fit(self, X=None, y=None, **kwargs):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        st_time = time.time()

        self._is_default_partition_value_fit = True # False when the user provides partition columns.

        data, feature_columns, label_columns, _, partition_columns = \
            self._validate_args_and_get_data(X=X, y=y, groups=None, kwargs=kwargs)

        if partition_columns:
            self._is_default_partition_value_fit = False
            self._fit_partition_colums_non_default = partition_columns

        file_name = kwargs.pop("file_name", None)
        func_name = kwargs.pop("name", "fit")

        args = {"data": data,
                "feature_columns": feature_columns,
                "label_columns": label_columns,
                "partition_columns": partition_columns,
                "func": func_name}
        
        if file_name is not None:
            args["file_name"] = file_name

        self._run_fit_related_functions(**args)

        self._fit_execution_time = time.time() - st_time

        return self

    def set_params(self, **params):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        for key, val in params.items():
            self.kwargs[key] = val

        # Initialize with new arguments and return the class/model object.
        # set_params takes all keyword arguments and no positional arguments.
        self.__init__(None, self.module_name, self.class_name, tuple(), self.kwargs)
        return self

    # get_params() will be executed through __getattr__().

    # @_validate_fit_run
    def __getattr__(self, name):
        def __run_transform(*c, **kwargs):
            kwargs["name"] = name
            return self._transform(*c, **kwargs)

        def __run_function_needing_all_rows(*c, **kwargs):
            kwargs["name"] = name
            return self._run_function_needing_all_rows(*c, **kwargs)

        def __run_kneighbors(*c, **kwargs):
            kwargs["name"] = name
            return self._run_neighbors(*c, **kwargs)

        if name in ["score", "aic", "bic", "perplexity"]:
            # TODO: ELE-6352 - Implement error_norm() function later.
            return __run_function_needing_all_rows

        if name in ["kneighbors",
                    "radius_neighbors",
                    "kneighbors_graph",
                    "radius_neighbors_graph"]:
            return __run_kneighbors

        if name in ["predict",
                    "transform",
                    "inverse_transform",
                    "predict_proba",
                    "predict_log_proba",
                    "decision_function",
                    "score_samples",
                    "decision_path",
                    "apply",
                    "cost_complexity_pruning_path",
                    "gibbs",
                    "kneighbors_graph",
                    "radius_neighbors_graph",
                    "mahalanobis",
                    "correct_covariance",
                    "reweight_covariance",
                    "path"]:
            return __run_transform

        return super().__getattr__(name)

    def _special_handling_multimodel_(self, data, feature_columns, label_columns, partition_columns,
                                      func_name, **kwargs):
        """
        Internal function to handle multi model case for transform function for functions 
        ["SelectFpr", "SelectFdr", "SelectFwe", "SelectFromModel", "RFECV"] of feature_selection module
        and "Birch" of cluster module.
        These functions generate multiple models and when transform is applied to each model, it generates
        output with different number of columns.
        """
        skl_objs_dict = {}
        no_of_unique_partitions = len(self._fit_partition_unique_values)
        no_of_partitioning_cols = len(self._fit_partition_unique_values[0])

        # Run on 10 rows of data individually using corresponding scikit-learn objects based on paritition value
        # and get the maximum number of columns and their types.
        for i in range(no_of_unique_partitions):
            skl_objs_dict[tuple(self.modelObj.iloc[i, :no_of_partitioning_cols])] = self.modelObj.iloc[i]["model"]
        

        data = data.select(feature_columns + label_columns + partition_columns)
        ten_row_data = data.head(10).get_values()
        X = numpy.array(ten_row_data)

        # For multi-model case, model in one AMP can give more number of columns than other AMPs.
        # Returns clause can't contain different number of columns in different AMPs. Hence, taking
        # maximum number of columns and their types from all models.
        max_no_of_columns = 0
        max_col_names = []
        max_col_types = []

        def _get_input_row_without_nans(row):
            """
            `inverse_transform` should not contain NaNs. Hence, removing NaNs from the row.
            """
            X1 = []
            for _, v in enumerate(row):
                if isinstance(v, type(None)) or isinstance(v, str) or not math.isnan(v) or self.module_name == "sklearn.impute":
                    # Add to list when:
                    #  - v is None or
                    #   - v is string or
                    #   - v is not nan or
                    #   - if module is impute (which transforms nan values) even though v is nan.
                    X1.append(v)
                else:
                    # skip nan values.
                    pass
            return X1

        for i in range(X.shape[0]):
            # Run `transform` or `inverse_transform` on each row with corresponding scikit-learn model object.
            partition_values = tuple(X[i, -no_of_partitioning_cols:])
            skl_obj = skl_objs_dict[partition_values]

            X1 = X[i, :-no_of_partitioning_cols]
            # Since Nans/NULLs are added in transform for last columns where some models generated
            # less number of columns, removing Nans/NULLs from the input row for inverse_transform
            # using function _get_input_row_without_nans().
            X1 = numpy.array([_get_input_row_without_nans(X1)])

            trans_opt = getattr(skl_obj, func_name)(X1, **kwargs)

            no_of_columns = 1

            if trans_opt.shape == (X1.shape[0],):
                trans_opt = trans_opt.reshape(X1.shape[0], 1)
            
            if isinstance(trans_opt[0], numpy.ndarray) \
                    or isinstance(trans_opt[0], list) \
                    or isinstance(trans_opt[0], tuple):
                no_of_columns = len(trans_opt[0])
            
            col_names = [f"{self.class_name.lower()}_{func_name}_{(i + 1)}" for i in range(no_of_columns)]

            # Get new column sqlalchemy types for pandas df columns of transform output.
            opt_pd = pd.DataFrame(trans_opt)

            # Get output column types for each column in pandas df from the output of transform
            # type functions.
            types = {}
            for idx in range(no_of_columns):
                col = list(opt_pd.columns)[idx]

                # Only one row in trans_opt.
                if isinstance(trans_opt[0], numpy.ndarray) or isinstance(trans_opt[0], tuple) or isinstance(trans_opt[0], list):
                    type_ = type(trans_opt[0][idx])
                else:
                    # only one value in the output.
                    type_ = type(trans_opt[0])

                # If type of the output value (trans_opt) is None, then use `str` as type since
                # pandas astype() does not accept None type.
                if type_ is type(None):
                    type_ = str

                # numpy integer columns with nan values can't be typecasted using pd.astype() to int64.
                # It raises error like "Cannot convert non-finite values (NA or inf) to integer: 
                #                       Error while type casting for column '2'"
                # Hence, using pd.Int64Dtype() for integer columns with nan values.
                types[col] = type_ if type_ not in [int, numpy.int64] else pd.Int64Dtype()

            # Without this, all columns will be of object type and gets converted to VARCHAR in Vantage.
            opt_pd = opt_pd.astype(types)

            # If the datatype is not specified then check if the datatype is datetime64 and timezone is present then map it to
            # TIMESTAMP(timezone=True) else map it according to default value.
            col_types = [TIMESTAMP(timezone=True)
                        if pt.is_datetime64_ns_dtype(opt_pd.dtypes[key]) and (opt_pd[col_name].dt.tz is not None)
                        else _get_sqlalchemy_mapping(str(opt_pd.dtypes[key]))
                        for key, col_name in enumerate(list(opt_pd.columns))]

            # Different models in multi model case can generate different number of output columns for example in
            # SelectFpr. Hence, taking the model which generates maximum number of columns.
            if no_of_columns > max_no_of_columns:
                max_no_of_columns = no_of_columns
                max_col_names = col_names
                max_col_types = col_types

        return [(c_name, c_type) for c_name, c_type in zip(max_col_names, max_col_types)]

    def _execute_function_locally(self, ten_row_data, feature_columns, label_columns, openml_obj,
                                  func_name, **kwargs):
        """
        Executes a opensourceml function of the class object openml_obj" on the provided data locally.
        Parameters:
            ten_row_data (list or array-like): The input data containing rows to be processed.
            feature_columns (list): List of feature column names.
            label_columns (list): List of label column names.
            openml_obj (object): The opensourceml object on which the function is to be executed.
            func_name (str): The name of the function to be executed on the opensourceml object.
            **kwargs: Additional keyword arguments to be passed to the opensourceml function.
        Returns:
            numpy.ndarray: The transformed output from the opensource function.
        Raises:
            NotImplementedError: If the function name is "path", which is not implemented.
        """
        
        X = numpy.array(ten_row_data)

        if label_columns:
            n_f = len(feature_columns)
            n_c = len(label_columns)
            y = X[:,n_f : n_f + n_c]
            X = X[:,:n_f]
            # predict() now takes 'y' also for it to return the labels from script. Skipping 'y'
            # in local run if passed. Generally, 'y' is passed to return y along with actual output.
            try:
                trans_opt = getattr(openml_obj, func_name)(X, y, **kwargs)
            except TypeError as ex:
                # Function which does not accept 'y' like predict_proba() raises error like
                # "predict_proba() takes 2 positional arguments but 3 were given".
                trans_opt = getattr(openml_obj, func_name)(X, **kwargs)
        else:
            trans_opt = getattr(openml_obj, func_name)(X, **kwargs)

        if func_name == "path":
            raise NotImplementedError(
                "path() returns tuple of ndarrays of different shapes. Not Implemented yet."
            )

        if isinstance(trans_opt, numpy.ndarray) and trans_opt.shape == (X.shape[0],):
            trans_opt = trans_opt.reshape(X.shape[0], 1)

        return trans_opt

    def _get_return_columns_for_function_(self,
                                          data,
                                          feature_columns,
                                          label_columns,
                                          partition_columns,
                                          func_name,
                                          kwargs):
        """
        Internal function to return list of column names and their sqlalchemy types
        which should be used in return_types of Script.
        """
        if func_name == "fit_predict":
            """
            Get return columns using label_columns.
            """
            return [(f"{self.class_name.lower()}_{func_name}_{(i + 1)}",
                     data._td_column_names_and_sqlalchemy_types[col.lower()])
                    for i, col in enumerate(label_columns)]

        if func_name == "predict" and self.OPENSOURCE_PACKAGE_NAME == OpenSourcePackage.SKLEARN:
            """
            Return predict columns using either label_columns (if provided) or 
            self._fit_label_columns_types (if the function is trained using label columns).
            Otherwise run predict on ten rows of data to get the number of columns and their types
            after this if condition.
            """
            if label_columns:
                return [(f"{self.class_name.lower()}_{func_name}_{(i + 1)}",
                         data._td_column_names_and_sqlalchemy_types[col.lower()])
                             for i, col in enumerate(label_columns)]
            if self._fit_label_columns_types:
                return [(f"{self.class_name.lower()}_{func_name}_{(i + 1)}", col_type)
                        for i, col_type in enumerate(self._fit_label_columns_types)]

        ## If function is not `fit_predict`:
        #   then take one row of transform/other functions to execute in client
        #   to get number of columns in return clause and their Vantage types.

        # For paritioning columns, it will be a dataframe and getattr(modelObj, func_name) fails.
        # Just for getting the number of columns and their types, using only one model of all.
        if len(self._fit_partition_unique_values) == 1:
            # Single model case.
            skl_obj = self.modelObj
        else:
            # Multi model case.
            if (func_name in ["transform", "inverse_transform"] and \
                self.class_name in ["SelectFpr", "SelectFdr", "SelectFwe", "SelectFromModel", "RFECV", "Birch"]) or \
                (self.module_name == "lightgbm.sklearn" and self.class_name == "LGBMClassifier"):
                # Special handling for multi model case for transform function as these classes
                # generate transform output with different number of columns for each model.
                # Hence, need to add Nulls/Nans to columns which are not present in the transform output of
                # some models.
                return self._special_handling_multimodel_(data, feature_columns, label_columns,
                                                          partition_columns, func_name, **kwargs)

            skl_obj = self.modelObj.iloc[0]["model"]

        data = data.select(feature_columns + label_columns)

        ten_row_data = data.head(10).get_values()

        trans_opt = self._execute_function_locally(ten_row_data, feature_columns, label_columns,
                                                   skl_obj, func_name, **kwargs)
        
        if type(trans_opt).__name__ in ["csr_matrix", "csc_matrix"]:
            no_of_columns = trans_opt.get_shape()[1]
            trans_opt = trans_opt.toarray()
        elif isinstance(trans_opt, dict):
            raise NotImplementedError(f"Output returns dictionary {trans_opt}. NOT implemented yet.")
        elif isinstance(trans_opt[0], numpy.ndarray) \
                or isinstance(trans_opt[0], list) \
                or isinstance(trans_opt[0], tuple):
            no_of_columns = len(trans_opt[0])
        else:
            no_of_columns = 1

        # Special handling when inverse_transform of no_of_columns returns no of rows 
        # less than the no of classes. Such columns are filled with NaN values.
        # Updating number of columns here (new columns with NaN values will be added).
        if func_name == "inverse_transform" and self.class_name == "MultiLabelBinarizer":
            no_of_columns = len(self.classes_)
            for i in range(len(ten_row_data)):
                trans_opt[i] += tuple([numpy.nan] * (no_of_columns - len(trans_opt[i])))

        # Special handling required for cross_decomposition classes's transform function, which
        # takes label columns also. In this case, output is a tuple of numpy arrays - x_scores and
        # y_scores. If label columns are not provided, only x_scores are returned.
        if self.module_name == "sklearn.cross_decomposition" and func_name == "transform":
            # For cross_decomposition, output is a tuple of arrays when label columns are provided
            # along with feature columns for transform function. In this case, concatenate the
            # arrays and return the column names accordingly.
            if isinstance(trans_opt, tuple): # tuple when label_columns is provided.
                assert trans_opt[0].shape == trans_opt[1].shape,\
                    "Output arrays should be of same shape when transform/fit_transform is run "\
                    "with label columns for cross_decomposition classes.."
                first_cols = [f"x_scores_{(i + 1)}" for i in range(trans_opt[0].shape[1])]
                second_cols = [f"y_scores_{(i + 1)}" for i in range(trans_opt[1].shape[1])]
                no_of_columns = trans_opt[0].shape[1] + trans_opt[1].shape[1]
                col_names = first_cols + second_cols

                trans_opt = numpy.concatenate(trans_opt, axis=1)
            else:
                assert isinstance(trans_opt, numpy.ndarray), "When transform/fit_transform is run "\
                    "without label columns for cross_decomposition classes, "\
                    "output should be a numpy array."
                no_of_columns = trans_opt.shape[1]
                col_names =[f"x_scores_{(i + 1)}" for i in range(trans_opt.shape[1])]
        else:
            # Generate list of new column names.
            col_names = [f"{self.class_name.lower()}_{func_name}_{(i + 1)}" for i in range(no_of_columns)]

        # Get new column sqlalchemy types for pandas df columns of transform output.
        opt_pd = pd.DataFrame(trans_opt)

        # Get output column types for each column in pandas df from the output of transform
        # type functions.
        types = {}
        for idx, col in enumerate(list(opt_pd.columns)):
            types_ = []
            # Get type of column using data from all rows, in case if the column has None values.
            # 'and' of types of all values in the column with type(None) gives the type of the column.
            type_ = type(None)
            for i in range(len(trans_opt)):
                type_ = type_ and type(trans_opt[i][idx])
                types_.append(type_)
            
            # If all the values of the output (trans_opt) is None, thelen use `str` as type since
            # pandas astype() does not accept None type.
            if type_ is type(None):
                type_ = str

            # MultilabelBinarize String (non-numeric) labels containing the column having string and 
            # float values. Handling this case separately here. 
            if str in types_ and float in types_:
                types[col] = str
            # numpy integer columns with nan values can't be typecasted using pd.astype() to int64.
            # It raises error like "Cannot convert non-finite values (NA or inf) to integer: 
            #                       Error while type casting for column '2'"
            # Hence, using pd.Int64Dtype() for integer columns with nan values.
            else:
                types[col] = type_ if type_ not in [int, numpy.int64] else pd.Int64Dtype()


        # Without this, all columns will be of object type and gets converted to VARCHAR in Vantage.
        opt_pd = opt_pd.astype(types)

        # If the datatype is not specified then check if the datatype is datetime64 and timezone is present then map it to
        # TIMESTAMP(timezone=True) else map it according to default value.
        col_types = [TIMESTAMP(timezone=True)
                     if pt.is_datetime64_ns_dtype(opt_pd.dtypes[key]) and (opt_pd[col_name].dt.tz is not None)
                     else _get_sqlalchemy_mapping(str(opt_pd.dtypes[key]))
                     for key, col_name in enumerate(list(opt_pd.columns))]

        return [(c_name, c_type) for c_name, c_type in zip(col_names, col_types)]

    @_validate_fit_run
    def _run_function_needing_all_rows(self, X=None, y=None, file_name="sklearn_score.py", **kwargs):
        """
        Internal function to run functions like score, aic, bic which needs all rows and return
        one floating number as result.
        """
        st_time = time.time()

        assert kwargs["name"], "function name should be passed."
        func_name = kwargs["name"]

        # Remove 'name' to pass other kwargs to script. TODO: Not passing it now.
        kwargs.pop("name")

        data, feature_columns, label_columns, _, partition_columns = \
            self._validate_args_and_get_data(X=X, y=y, groups=None, kwargs=kwargs)

        label_columns = self._get_columns_as_list(label_columns)

        data, new_partition_columns = self._get_data_and_data_partition_columns(data,
                                                                                feature_columns,
                                                                                label_columns,
                                                                                partition_columns)

        script_file_path = f"{file_name}" if self._is_lake_system \
            else f"./{self._db_name}/{file_name}"

        data_column_types_str, partition_indices_str, _, new_partition_columns = \
            self._get_data_col_types_and_partition_col_indices_and_types(data, new_partition_columns)

        self._validate_unique_partition_values(data, new_partition_columns)

        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {script_file_path} {func_name} {len(feature_columns)} "\
            f"{len(label_columns)} {partition_indices_str} {data_column_types_str} "\
            f"{self._model_file_name_prefix} {self._is_lake_system}"

        # score, aic, bic returns float values.
        return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                        for col in new_partition_columns] + [(func_name, FLOAT())]

        # Checking the trained model installation. If not installed,
        # install it and set flag to True.
        if not self._is_trained_model_installed:
            self._install_initial_model_file()
            self._is_trained_model_installed = True

        opt = self._run_script(data, script_command, new_partition_columns, return_types)

        self._score_execution_time = time.time() - st_time

        if self._is_default_partition_value_fit:
            # For single model case, partition column is internally generated and
            # no point in returning it to the user.
            return opt.select(func_name)

        return opt

    @_validate_fit_run
    def _transform(self, X=None, y=None, file_name="sklearn_transform.py", **kwargs):
        """
        Internal function to run predict/transform and similar functions, which returns
        multiple columns. This function will return data row along with the generated
        columns' row data, unlike sklearn's functions which returns just output data.
        """
        st_time = time.time()

        assert kwargs["name"], "function name should be passed."
        func_name = kwargs["name"]

        # Remove 'name' to pass other kwargs to script. TODO: Not passing it now.
        kwargs.pop("name")

        data, feature_columns, label_columns, _, partition_columns = \
            self._validate_args_and_get_data(X=X, y=y, groups=None, kwargs=kwargs)

        data, new_partition_columns = self._get_data_and_data_partition_columns(data,
                                                                                feature_columns,
                                                                                label_columns,
                                                                                partition_columns)

        # Since kwargs are passed to transform, removing additional unrelated arguments from kwargs.
        self._remove_data_related_args_from_kwargs(kwargs)

        script_file_path = f"{file_name}" if self._is_lake_system \
            else f"./{self._db_name}/{file_name}"

        data_column_types_str, partition_indices_str, _, new_partition_columns = \
            self._get_data_col_types_and_partition_col_indices_and_types(data, new_partition_columns)

        self._validate_unique_partition_values(data, new_partition_columns)

        return_columns_python_types = None
        if self._fit_label_columns_python_types:
            return_columns_python_types = '--'.join(self._fit_label_columns_python_types)

        # Returning feature columns also along with transformed columns because we don't know the
        # mapping of feature columns to the transformed columns.
        ## 'correct_covariance()' returns the (n_features, n_features)
        if func_name == "correct_covariance":
            return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                            for col in new_partition_columns]
        else:
            return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                            for col in (new_partition_columns + feature_columns)]
        if func_name in ["predict", "decision_function"] and label_columns:
            return_types += [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                             for col in label_columns]

        output_cols_types = self._get_return_columns_for_function_(data,
                                                                   feature_columns,
                                                                   label_columns,
                                                                   new_partition_columns,
                                                                   func_name,
                                                                   kwargs)
        return_types += output_cols_types

        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {script_file_path} {func_name} {len(feature_columns)} "\
            f"{len(label_columns)} {partition_indices_str} {data_column_types_str} "\
            f"{self._model_file_name_prefix} {len(output_cols_types)} {self._is_lake_system} " \
            f"{return_columns_python_types}"

        # Checking the trained model installation. If not installed,
        # install it and set flag to True.
        if not self._is_trained_model_installed:
            self._install_initial_model_file()
            self._is_trained_model_installed = True

        opt = self._run_script(data, script_command, new_partition_columns, return_types)

        self._transform_execution_time = time.time() - st_time

        return self._get_returning_df(opt, new_partition_columns, return_types)

    def fit_predict(self, X=None, y=None, **kwargs):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        st_time = time.time()

        self._is_default_partition_value_fit = True # False when the user provides partition columns.

        data, feature_columns, label_columns, _, partition_columns = \
            self._validate_args_and_get_data(X=X, y=y, groups=None, kwargs=kwargs)

        if partition_columns:
            self._is_default_partition_value_fit = False

        data, new_partition_columns = self._get_data_and_data_partition_columns(data,
                                                                                feature_columns,
                                                                                label_columns,
                                                                                partition_columns)

        # Return label_columns also if user provides in the function call.
        return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                        for col in (new_partition_columns + feature_columns + label_columns)]

        func_name = inspect.stack()[0][3]
        if label_columns:
            return_types += self._get_return_columns_for_function_(data,
                                                                   feature_columns,
                                                                   label_columns,
                                                                   new_partition_columns,
                                                                   func_name,
                                                                   {})
        else:
            # If there are no label_columns, we will have only one
            # predicted column.
            return_types += [(f"{self.class_name.lower()}_{func_name}_1", FLOAT())]

        file_name = "sklearn_fit_predict.py"

        data_column_types_str, partition_indices_str, _, new_partition_columns = \
            self._get_data_col_types_and_partition_col_indices_and_types(data, new_partition_columns)

        script_file_name = f"{file_name}" if self._is_lake_system \
            else f"./{self._db_name}/{file_name}"
        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {script_file_name} {len(feature_columns)} "\
            f"{len(label_columns)} {partition_indices_str} {data_column_types_str} "\
            f"{self._model_file_name_prefix} {self._is_lake_system}"

        # Get unique values in partitioning columns.
        self._fit_partition_unique_values = data.drop_duplicate(new_partition_columns).get_values()

        # Checking the trained model installation. If not installed,
        # install it and flag to True.
        if not self._is_trained_model_installed:
            self._install_initial_model_file()
            self._is_trained_model_installed = True

        opt = self._run_script(data, script_command, new_partition_columns, return_types)

        self._fit_predict_execution_time = time.time() - st_time

        if self._is_default_partition_value_fit:
            # For single model case, partition column is internally generated and no point in
            # returning it to the user.

            # Extract columns from return types.
            returning_cols = [col[0] for col in return_types[len(new_partition_columns):]]
            return opt.select(returning_cols)

        return opt

    def fit_transform(self, X=None, y=None, **kwargs):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        # 'y' is not needed for transform().
        fit_obj = self.fit(X, y, **kwargs)
        kwargs["label_columns"] = None
        return fit_obj.transform(X, None, **kwargs)

    @_validate_fit_run
    def _run_neighbors(self, X=None, **kwargs):
        """
        Internal function to run functions like kneighbors, radius_neighbors, kneighbors_graph,
        radius_neighbors_graph which returns multiple columns. This function will return data row
        along with the generated columns' row data, unlike sklearn's functions which returns just
        output data.
        """
        assert kwargs["name"], "function name should be passed."
        func_name = kwargs["name"]
        kwargs.pop("name")

        if self.module_name != "sklearn.neighbors":
            raise AttributeError(f"{self.module_name+'.'+self.class_name} does not have {func_name}() method.")

        data = kwargs.get("data", None)
        partition_columns = kwargs.get("partition_columns", None)

        if not X and not partition_columns and not data:
            # If data is not passed, then run from client only.
            # TODO: decide whether to run from client or from Vantage.
            opt = super().__getattr__(func_name)(**kwargs)
            from scipy.sparse.csr import csr_matrix
            if isinstance(opt, csr_matrix):
                return opt.toarray()
            return opt

        self._is_default_partition_value_fit = True # False when the user provides partition columns.

        data, feature_columns, _, _, new_partition_columns = \
            self._validate_args_and_get_data(X=X, y=None, groups=None, kwargs=kwargs,
                                             skip_either_or_that=True)

        # Remove the kwargs data.
        self._remove_data_related_args_from_kwargs(kwargs)

        if partition_columns:
            # kwargs are passed to kneighbors function. So, removing them from kwargs.
            self._is_default_partition_value_fit = False

        # Generating new partition column name.
        data, new_partition_columns = self._get_data_and_data_partition_columns(data,
                                                                                feature_columns,
                                                                                [],
                                                                                partition_columns)

        args_str = self._get_kwargs_str(kwargs)

        file_name = "sklearn_neighbors.py"

        script_file_path = f"{file_name}" if self._is_lake_system \
            else f"./{self._db_name}/{file_name}"

        # Returning feature columns also along with new columns.
        return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                        for col in (new_partition_columns + feature_columns)]

        # `return_distance` is needed as the result is a tuple of two arrays when it is True.
        return_distance = kwargs.get("return_distance", True) # Default value is True.

        # Though new columns return numpy arrays, we are returning them as strings.
        # TODO: Will update to columns later, if requested later.
        if func_name in ['kneighbors', 'radius_neighbors']:
            if return_distance:
                return_types += [("neigh_dist", VARCHAR())]
            return_types += [("neigh_ind", VARCHAR())]
        elif func_name in ['kneighbors_graph', 'radius_neighbors_graph']:
            return_types += [("A", VARCHAR())]
        else:
            return_types += [("output", VARCHAR())]

        data_column_types_str, partition_indices_str, _, new_partition_columns = \
            self._get_data_col_types_and_partition_col_indices_and_types(data, new_partition_columns)

        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {script_file_path} {func_name} {len(feature_columns)} "\
            f"{partition_indices_str} {data_column_types_str} {self._model_file_name_prefix} {self._is_lake_system} "\
            f"{args_str}"

        # Get unique values in partitioning columns.
        self._fit_partition_unique_values = data.drop_duplicate(new_partition_columns).get_values()

        # Checking the trained model installation. If not installed,
        # install it and set flag to True.
        if not self._is_trained_model_installed:
            self._install_initial_model_file()
            self._is_trained_model_installed = True

        opt = self._run_script(data, script_command, new_partition_columns, return_types)

        return self._get_returning_df(opt, new_partition_columns, return_types)

    def split(self, X=None, y=None, groups=None, **kwargs):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        opt = self._run_model_selection("split", X=X, y=y, groups=groups,
                                        skip_either_or_that=True, kwargs=kwargs)

        # Get number of splits in the result DataFrame.
        n_splits = opt.drop_duplicate("split_id").shape[0]

        data = kwargs.get("data", None)
        feature_columns = kwargs.get("feature_columns", [])
        label_columns = self._get_columns_as_list(kwargs.get("label_columns", []))

        # If there is not X and y, get feature_columns and label_columns for "data".
        partition_columns = kwargs.get("partition_columns", [])
        feature_columns = [col for col in X.columns if col not in partition_columns] \
            if X and not data and not feature_columns else feature_columns
        label_columns = y.columns if y and not data and not label_columns else label_columns

        # Return iterator of the train and test dataframes for each split.
        for i in range(1, n_splits+1):
            train_df = opt[(opt.split_id == i) & (opt.data_type == "train")]\
                .select(partition_columns + feature_columns + label_columns)
            train_df._index_label = None
            test_df = opt[(opt.split_id == i) & (opt.data_type == "test")]\
                .select(partition_columns + feature_columns + label_columns)
            test_df._index_label = None

            yield train_df, test_df

    def get_n_splits(self, X=None, y=None, groups=None, **kwargs):
        """
        Please check the description in Docs/OpensourceML/sklearn.py.
        """
        return self._run_model_selection("get_n_splits", X=X, y=y, groups=groups,
                                         skip_either_or_that=True, kwargs=kwargs)

    def _run_model_selection(self,
                             func_name,
                             X=None,
                             y=None,
                             groups=None,
                             skip_either_or_that=False,
                             kwargs={}):
        """
        Internal function to run functions like split, get_n_splits of model selection module.
        - get_n_splits() returns number of splits as value, not as teradataml DataFrame.
        - split() returns teradataml DataFrame containing train and test data for each split
          (add partition information if the argument "partition_cols" is provided).
        """
        if self.module_name != "sklearn.model_selection":
            raise AttributeError(f"{self.module_name+'.'+self.class_name} does not "
                                 f"have {func_name}() method.")

        data = kwargs.get("data", None)

        if not X and not y and not groups and not data:
            # If data is not passed, then run from client only.
            # TODO: decide whether to run from client or from Vantage.
            return super().__getattr__(func_name)()

        self._is_default_partition_value_fit = True # False when the user provides partition columns.

        data, feature_columns, label_columns, group_columns, partition_columns = \
            self._validate_args_and_get_data(X=X, y=y, groups=groups, kwargs=kwargs,
                                             skip_either_or_that=skip_either_or_that)

        if partition_columns:
            self._is_default_partition_value_fit = False

        data, new_partition_columns = self._get_data_and_data_partition_columns(data,
                                                                                feature_columns,
                                                                                label_columns,
                                                                                partition_columns,
                                                                                group_columns)

        file_name = "sklearn_model_selection_split.py"

        script_file_path = f"{file_name}" if self._is_lake_system \
            else f"./{self._db_name}/{file_name}"

        if func_name == "split":
            # Need to generate data into splits of train and test.
            #   split_id - the column which will be used to identify the split.
            #   data_type - the column which will be used to identify whether the row is
            #               train or test row.
            return_types = [("split_id", INTEGER()), ("data_type", VARCHAR())]
            # Returning feature columns and label columns as well.
            return_types += [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                            for col in (feature_columns + label_columns)]
        else:
            # Return Varchar by default.
            # Returns Varchar even for functions like `get_n_splits` which returns large integer
            # numbers like `4998813702034726525205100` for `LeavePOut` class (when the argument
            # `p` is 28 and no of data rows is 100) as Vantage cannot scope it to INTEGER.
            return_types = [(func_name, VARCHAR())]

        return_types = [(col, data._td_column_names_and_sqlalchemy_types[col.lower()])
                        for col in new_partition_columns] + return_types

        data_column_types_str, partition_indices_str, _, new_partition_columns = \
            self._get_data_col_types_and_partition_col_indices_and_types(data, new_partition_columns)

        py_exc = UtilFuncs._get_python_execution_path()
        script_command = f"{py_exc} {script_file_path} {func_name} {len(feature_columns)} "\
            f"{len(label_columns)} {len(group_columns)} {partition_indices_str} {data_column_types_str} "\
            f"{self._model_file_name_prefix} {self._is_lake_system}"

        # Get unique values in partitioning columns.
        self._fit_partition_unique_values = data.drop_duplicate(new_partition_columns).get_values()

        # Checking the trained model installation. If not installed,
        # install it and set flag to True.
        if not self._is_trained_model_installed:
            self._install_initial_model_file()
            self._is_trained_model_installed = True

        opt = self._run_script(data, script_command, new_partition_columns, return_types)

        if func_name == "get_n_splits" and not partition_columns:
                # Return number of splits as value, not as dataframe.
                vals = execute_sql("select {} from {}".format(func_name, opt._table_name))
                opt = vals.fetchall()[0][0]

                # Varchar is returned by the script. Convert it to int.
                return int(opt)

        return opt


class _SKLearnFunctionWrapper(_FunctionWrapper):
    OPENSOURCE_PACKAGE_NAME = OpenSourcePackage.SKLEARN
    _pkgs = ["scikit-learn", "numpy", "scipy"]
    def __init__(self, module_name, func_name):
        file_type = "file_fn_sklearn"
        template_file = "sklearn_function.template"
        super().__init__(module_name, func_name, file_type=file_type, template_file=template_file)
