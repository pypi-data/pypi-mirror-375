"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com, gouri.patwardhan@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements the helper methods and classes which are required to
process In-DB Functions.
"""

from teradataml.options.configure import configure
from teradataml.analytics.json_parser.json_store import _JsonStore
from teradataml.analytics.json_parser.metadata import _AnlyFuncMetadata, _AnlyFuncMetadataUAF
from teradataml.common.constants import TeradataAnalyticFunctionTypes, TeradataAnalyticFunctionInfo
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
import json, os, importlib
from teradataml import UtilFuncs
from teradataml.common.formula import Formula
from teradataml.utils.validators import _Validators
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils

# Map to store IN-DB function type and JSON directory for current database version.
func_type_json_version = {}
module = importlib.import_module("teradataml")

def _get_json_data_from_tdml_repo():
    """
    DESCRIPTION:
        An internal function to parse the json files stored in teradataml repo. This function,
        first checks whether the version of json store is same as database version.
        If both versions are same, it then returns an empty list, i.e., the framework
        will neither parse the json files nor generate the SQLE functions. Otherwise cleans
        the json store and parses the json files in the corresponding directory and adds
        the json data to json store.

    PARAMETERS:
        None.

    RAISES:
        None.

    RETURNS:
        An iterator of _AnlyFuncMeta object OR list

    EXAMPLES:
        >>> _get_json_data_from_tdml_repo()
    """

    # Check if the json store version is matched with Vantage database version. If
    # both versions are matched, then the json store has data available so no need
    # to parse again.
    if configure.database_version != _JsonStore.version:
        # Json store version is different from database version. So, json's should
        # be parsed again. Before parsing the json, first clean the json store.
        _JsonStore.clean()

        # Set the json store version to current database version.
        _JsonStore.version = configure.database_version

        # Clean existing map between IN-DB function type and corresponding JSON directory.
        func_type_json_version.clear()

        # Load the mapping information for all analytic functions which are version dependent into _JsonStore.
        _load_anlyfuncs_jsons_versions_info()

        json_file_directories = __get_json_files_directory()

        # For the corresponding database version, if teradataml does not have any json
        # files, then return an empty list. So framework will not attach any SQLE function
        # to teradataml.
        if not json_file_directories:
            return []

        # Read the directory, parse the json file and add the _AnlyFuncMeta object to json store
        # and yield the same.
        for json_file_directory_list in json_file_directories:
            # Get the function type
            func_type = json_file_directory_list[1]
            # Get the json directory
            json_file_directory = json_file_directory_list[0]

            # Get the appropriate metadata class.
            metadata_class = getattr(TeradataAnalyticFunctionInfo, func_type).value.get("metadata_class",
                                                                                        "_AnlyFuncMetadata")
            metadata_class = eval(metadata_class)

            for json_file in os.listdir(json_file_directory):
                file_path = os.path.join(json_file_directory, json_file)
                with open(file_path, encoding="utf-8") as fp:
                    json_data = json.load(fp)
                    metadata = metadata_class(json_data, file_path, func_type=func_type)

                    # Functions which do not need to participate in IN-DB Framework
                    # should not be stored in _JsonStore.
                    if metadata.func_name in _JsonStore._functions_to_exclude:
                        continue
                    _JsonStore.add(metadata)
                    yield metadata

    # If both database version and json store version are same, return an empty list so that
    # framework will not attach any SQLE function to teradataml.
    else:
        return []


def _load_anlyfuncs_jsons_versions_info():
    """
    DESCRIPTION:
        Function populates following information for analytic functions:
            * Lowest supported version.
            * Parent directory containing JSONs.
            * Nearest matching JSON directory for a particular database version.

    PARAMETERS:
        None

    RETURNS:
        None

    RAISES:
        None

    EXAMPLES:
        >>> _load_anlyfuncs_jsons_versions_info()
    """
    # Import the required package.
    import re
    # Get the closest matching JSON directory out of all directories corresponding
    # to JSONs of different version.
    # First remove any letters present in the version
    temp_db_version = re.sub(r'[a-zA-Z]', r'', configure.database_version)
    db_version = float(temp_db_version[:5])
    for func_info in TeradataAnalyticFunctionInfo:
        func_type = func_info.value["func_type"]
        func_base_version = func_info.value["lowest_version"]
        parent_dir = UtilFuncs._get_data_directory(dir_name="jsons",
                                                   func_type=func_info)
        if func_base_version:
            if db_version >= float(func_base_version):
                closest_version = _get_closest_version_json_dir(parent_dir, db_version)
                if closest_version:
                    func_type_json_version[func_type] = closest_version


def __get_json_files_directory():
    """
    DESCRIPTION:
        An internal function to get the corresponding directory name, which
        contains the json files.

    PARAMETERS:
        None.

    RAISES:
        None.

    RETURNS:
        list

    EXAMPLES:
        >>> __get_json_files_directory()
    """
    # If function has version specific JSON directory, return it by using mapping information in
    # _Jsonstore else return common JSON directory.
    for func_info in TeradataAnalyticFunctionInfo:
        if func_info.value["lowest_version"]:
            # Check if current function type is allowed on connected Vantage version or not.
            if func_info.value["func_type"] in func_type_json_version.keys():
                # If function type is SQLE and db_version is 20.00, then add 17.20 JSON directory.
                if func_type_json_version[func_info.value["func_type"]] == '20.00' and  \
                   func_info.value["func_type"] == 'sqle':
                    yield [UtilFuncs._get_data_directory(dir_name="jsons", func_type=func_info,
                                                         version='17.20'),
                                                         func_info.name]
                yield [UtilFuncs._get_data_directory(dir_name="jsons", func_type=func_info,
                                                     version=func_type_json_version[func_info.value["func_type"]]),
                                                     func_info.name] 
        else:
            yield [UtilFuncs._get_data_directory(dir_name="jsons", func_type=func_info), func_info.name]


def _get_closest_version_json_dir(parent_dir, database_version):
    """
    DESCRIPTION:
        Internal function to get the nearest matching JSON directory for a database
        version from the available JSON directories for the functions.

    PARAMETERS:
        parent_dir:
            Required Argument.
            Specifies the parent dirctory for JSONs of all teradataml version.
            Types: str

        database_version:
            Required Argument.
            Specifies the database version.
            Types: float

    RAISES:
        None.

    RETURNS:
        str

    EXAMPLES:
        >>> _get_closest_version_json_dir("path_to_teradataml/teradataml/analytics/jsons/sqle", 17.10)
    """
    # Get the exact matching JSON directory name for current database version.
    # If matching directory exists, return it.
    matching_dir = format(database_version, '.2f')
    if matching_dir in os.listdir(parent_dir):
        return matching_dir

    # If exact matching JSON directory is not found,
    # return the directory corresponding to the closest lower version.
    # List all the directories, not the files, and collect lower versions only.
    lower_versions = (json_dir for json_dir in os.listdir(parent_dir)
                      if (os.path.isdir(os.path.join(parent_dir, json_dir))
                          and float(json_dir) <= database_version))

    # If generator generates non-empty list, return max of all versions from that list,
    # else while an empty list is passed to max() it throws ValueError, so return None.
    try:
        return max(lower_versions)
    except ValueError:
        return None

def _process_paired_functions():
    """
    DESCRIPTION:
        Process and reads the paired function json.

    PARAMETERS:
        None.

    RETURNS:
        None.
    """

    json_path = os.path.join(UtilFuncs._get_data_directory(), "jsons", "paired_functions.json")
    with open(json_path, encoding="utf8") as fp:
        _json = json.load(fp)

    _available_functions, _ = _JsonStore._get_function_list()
    for func_type, funcs in _json.items():
        # ToDo: Add support for VAL functions
        if func_type == "VAL":
            continue
        # Set all paired functions for SQLE and UAF.
        for func in funcs:
            # Check if function is existed in JSonStore or not. If exists, only
            # then process it.
            if func in _available_functions:
                metadata = _JsonStore.get_function_metadata(func)
                metadata.set_paired_functions(funcs.get(func))

class _UAF_paired_function:
    """
    Parent class for _Inverse, _Convolve, _Forecast and _Validate.
    """
    def _process_arguments(self, function_relation, **kwargs):
        """
        DESCRIPTION:
            Method instantiate the reference function based on 'function_relation'.

        PARAMETERS:
            function_relation:
                defines which method to instantiate.

            **kwargs:
                Keyword arguments passed based on 'function_relation'.

        RETURNS:
            object of the reference function.
        """
        metadata = _JsonStore.get_function_metadata(self.__class__.__name__)
        paired_functions = metadata.get_paired_functions()
        paired_function = \
            [fun_relation for fun_relation in paired_functions
             if fun_relation.function_relation == function_relation][0]
        reference_function = paired_function.reference_function
        for _inp, _out in paired_function.arguments:
            kwargs[_inp] = getattr(self, _out)
        input_art_spec = {'data': kwargs[paired_function.input_arguments[0]]}
        if self.__class__.__name__ == "SeasonalNormalize":
            input_art_spec['layer'] = "ARTMETADATA"
        kwargs[paired_function.input_arguments[0]] = \
            getattr(module, "TDAnalyticResult")(**input_art_spec)
        return getattr(module, reference_function)(**kwargs)


class _Convolve(_UAF_paired_function):
    """
    class to convolve the uaf function.
    """
    def convolve(self, **kwargs):
        """
        DESCRIPTION:
            Method to convolve the uaf function used by instance created from below functions:
                * DFFT
                * DFFT2

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the convolve method.
                Notes:
                    * Every function can have different arguments.
                    * This arguments are based on inverse functions.

        RETURNS:
            object of the reference function.

        EXAMPLE:
            load_example_data("uaf", ["dfft2conv_real_4_4"])
            data = DataFrame.from_table("dfft2conv_real_4_4")
            td_matrix = TDMatrix(data=data,
                                 id="id",
                                 row_index="row_i",
                                 row_index_style="SEQUENCE",
                                 column_index="column_i",
                                 column_index_style="SEQUENCE",
                                 payload_field="magnitude",
                                 payload_content="REAL")
            filter_expr = td_matrix.id==33
            dfft2_out = DFFT2(data=td_matrix,
                              data_filter_expr=filter_expr,
                              freq_style="K_INTEGRAL",
                              human_readable=False,
                              output_fmt_content="COMPLEX")
            convolve_output = dfft2_out.convolve(conv="HR_TO_RAW",
                                                 output_fmt_content="AMPL_PHASE_RADIANS")
        """
        return self._process_arguments("convolve", **kwargs)

class _Inverse(_UAF_paired_function):
    """
    class to inverse the effects of uaf function.
    """
    def inverse(self, **kwargs):
        """
        DESCRIPTION:
            Method to inverse the effect of uaf function used by instance created from below functions:
                * DIFF
                * UNDIFF
                * DFFT
                * IDFFT
                * DFFT2
                * IDFFT2
                * SeasonalNormalize

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the inverse method.
                Notes:
                    * Every function can have different arguments.
                    * This arguments are based on inverse functions.

        RETURNS:
            object of the reference function.

        EXAMPLE:
            load_example_data("uaf", "mvdfft8")
            data = DataFrame.from_table("mvdfft8")
            data_series_df = TDSeries(data=data,
                                 id="sid",
                                 row_index="n_seqno",
                                 row_index_style="SEQUENCE",
                                 payload_field="magnitude1",
                                 payload_content="REAL")
            DFFT_result = DFFT(data=data_series_df,
                           human_readable=True,
                           output_fmt_content='COMPLEX')
            inverse_output = DFFT_result.inverse()
        """
        return self._process_arguments("inverse", **kwargs)


class _Forecast(_UAF_paired_function):
    """
    Class to forecast the model trainer object
    """
    def forecast(self, **kwargs):
        """
        DESCRIPTION:
            Method to forecast the model trainer object and instantiate
            the reference function.

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the forecast method.
                Notes:
                    * Every function can have different arguments.
                    * This arguments are based on forecast functions.

        RETURNS:
            object of the reference function which are:
            * result

        EXAMPLE:
            load_example_data("uaf", ["timeseriesdatasetsd4"])
            data = DataFrame.from_table("timeseriesdatasetsd4")
            data_series_df = TDSeries(data=data,
                                      id="dataset_id",
                                      row_index="seqno",
                                      row_index_style="SEQUENCE",
                                      payload_field="magnitude",
                                      payload_content="REAL")
            arima_estimate_op = ArimaEstimate(data1=data_series_df,
                                              nonseasonal_model_order=[2,0,0],
                                              constant=False,
                                              algorithm="MLE",
                                              coeff_stats=True,
                                              fit_metrics=True,
                                              residuals=True,
                                              fit_percentage=100)
            arima_estimate_op.forecast(forecast_periods=2)
        """
        return self._process_arguments("forecast", **kwargs)

class _Validate(_UAF_paired_function):
    """
    Class to validate the model trainer object
    """
    def validate(self, **kwargs):
        """
        DESCRIPTION:
            Method to validate the model trainer object and instantiate
            the reference function.

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the validate method.
                Note:
                    * Every function can have different arguments.
                    * This arguments are based on validate functions.

        RETURNS:
            object of the reference function which are:
            * result
            * fitmetadata
            * fitresiduals
            * model

        EXAMPLE:
            load_example_data("uaf", ["timeseriesdatasetsd4"])
            data = DataFrame.from_table("timeseriesdatasetsd4")
            data_series_df = TDSeries(data=data,
                                      id="dataset_id",
                                      row_index="seqno",
                                      row_index_style="SEQUENCE",
                                      payload_field="magnitude",
                                      payload_content="REAL")
            arima_estimate_op = ArimaEstimate(data1=data_series_df,
                                              nonseasonal_model_order=[2,0,0],
                                              constant=False,
                                              algorithm="MLE",
                                              coeff_stats=True,
                                              fit_metrics=True,
                                              residuals=True,
                                              fit_percentage=80)
            arima_estimate_op.validate(residuals=True)
        """
        return self._process_arguments("validate", **kwargs)

class _Transform:
    def transform(self, **kwargs):
        """
        DESCRIPTION:
            Method to transform the model trainer object and instantiate
            the reference function.

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the transform method.

        RETURNS:
            object of the reference function.

        EXAMPLES:
            fit_df = Fit(data=iris_input,
                         object=transformation_df,
                         object_order_column='TargetColumn'
                         )

            fit_df.transform(data=iris_input)
        """
        metadata = _JsonStore.get_function_metadata(self.__class__.__name__)
        paired_functions = metadata.get_paired_functions()
        paired_function = [f for f in paired_functions if f.function_relation == "transform"][0]
        reference_function = paired_function.reference_function
        for _inp, _out in paired_function.arguments:
            kwargs[_inp] = getattr(self, _out)
        return getattr(module, reference_function)(**kwargs)

class _Predict:
    def predict(self, **kwargs):
        """
        DESCRIPTION:
            Method to predict the model trainer object and instantiate
            the reference function.

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the transform method.

        RETURNS:
            object of the reference function.

        EXAMPLE:
            svm_obj = SVM(data=transform_obj.result,
                           input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                          'AveBedrms', 'Population', 'AveOccup',
                                          'Latitude', 'Longitude'],
                           response_column="MedHouseVal",
                           model_type="Regression"
                           )

            svm_obj.predict(newdata = transform_obj.result,
                            id_column = "id"
                            )
        """
        metadata = _JsonStore.get_function_metadata(self.__class__.__name__)
        paired_functions = metadata.get_paired_functions()
        paired_function = [f for f in paired_functions if f.function_relation == "predict"][0]
        reference_function = paired_function.reference_function
        for _inp, _out in paired_function.arguments:
            kwargs[_inp] = getattr(self, _out)
        return getattr(module, reference_function)(**kwargs)


class _KNNPredict:
    def predict(self, **kwargs):
        """
        DESCRIPTION:
            Method to predict the KNN model trainer object and instantiate
            the reference function.

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the transform method.

        RETURNS:
            object of the reference function.

        EXAMPLE:
            KNN_out = KNN(train_data=computers_train1_encoded.result.iloc[:100],
                      test_data=computers_train1_encoded.result.iloc[10:],
                      id_column="id",
                      input_columns=["screen", "price", "speed", "hd"],
                      model_type="REGRESSION",
                      response_column="computer_category_special")

            res = KNN_out.evaluate(test_data=computers_train1_encoded.result.iloc[10:])
        """
        params = {"test_data": kwargs.get("test_data"),
                  "id_column": self.id_column,
                  "train_data": self.train_data,
                  "input_columns": self.input_columns,
                  "response_column": kwargs.get("response_column", self.response_column),
                  # Retrieve the accumulate value from kwargs if available.
                  # otherwise, no accumulation will occur.
                  "accumulate": kwargs.get("accumulate")
                  }

        # KNN works in a different way. predict calls the same function with test data along with
        # the arguments passed to the actual function. The above parameters are required
        # arguments so we expect them to be available in output of KNN. However, the below
        # ones are optional arguments. They can be available or not based on user input. So, before
        # passing those to KNN again, check whether that argument is passed or not.
        optional_args = ["model_type", "k", "voting_weight",
                         "tolerance", "output_prob", "output_responses",
                         "emit_neighbors", "emit_distances"]

        for optional_arg in optional_args:
            if hasattr(self, optional_arg):
                params[optional_arg] = getattr(self, optional_arg)

        return getattr(module, "KNN")(**params)


class _Evaluate:
    """
    DESCRIPTION:
        Implements the Classification and Regression evaluator.
    """
    _accumulate_args = {"NaiveBayesTextClassifierTrainer": "doc_category_column"}

    # Mapper for mapping function names with argument names
    _evaluator_function_mapper = {"DecisionForest": "tree_type",
                                  "GLM": "family",
                                  "GLMPerSegment": "family",
                                  "SVM": "model_type",
                                  "XGBoost": "model_type"}

    def is_classification_model(self, **kwargs):
        """
        DESCRIPTION:
            Returns True if the model is classification model or regression model.

        PARAMETERS:
            **kwargs:
                Keyword arguments to access the model_type.

        RETURNS:
            Boolean.
        """
        is_classification_model = False

        # NaiveBayesTextClassifierTrainer takes Multinomial, Bernoulli as input
        # both comes under classification evaluator
        if self.get_function_name() == "NaiveBayesTextClassifierTrainer":
            return True
        # name of argument is model_type for most of the functions but for some it is different
        if "model_type" not in kwargs and "tree_type" not in kwargs:
            arg_name = self.get_arg_name()
            model_type = getattr(self.obj, arg_name)
            if self.get_function_name() == "DecisionForest":
                kwargs["tree_type"] = model_type
            else:
                kwargs["model_type"] = model_type

        if  ("model_type" in kwargs and (kwargs["model_type"].lower() == "binomial" or kwargs["model_type"].lower() == "classification")) \
            or ( "tree_type" in kwargs and kwargs["tree_type"].lower() == "classification"):
            is_classification_model = True

        return is_classification_model

    def get_function_name(self):
        """
        DESCRIPTION:
            Function to get the name of the analytic function.

        PARAMETERS:
            None.

        RETURNS:
            str.

        """
        return self.__class__.__name__

    def get_response_column(self):
        """
        DESCRIPTION:
            Function to get the argument name for response column. For some functions
            argument name storing the response column is different, it can
            be fetched from the '_accumulate_arg' mapping.

        PARAMETER:
            None.

        RETURNS:
            str.
        """
        # By default it is 'response_column' but some functions require different names.
        return self._accumulate_args.get(self.get_function_name(), "response_column")



    def get_arg_name(self):
        """
        DESCRIPTION:
            Function to get the argument name for model type. For some functions argument
            name can be different, and it can be fetched using the '_evaluator_function_mapper'
            mapping.

        PARAMETER:
            None.

        RETURNS:
            String representing the argument name.
        """
        return self._evaluator_function_mapper.get(self.get_function_name(), "model_type")

    def evaluate(self, **kwargs):
        """
        DESCRIPTION:
            Method to evaluate the model trainer object, using
            either the classification or regression evaluator and
            instantiate the reference function.

        PARAMETER:
            **kwargs:
                Keyword arguments for specified for evaluate method.

        RETURNS:
            Attribute of Classification Evaluator or Regression Evaluator

        EXAMPLE:
            svm_obj = SVM(data=transform_obj.result,
                           input_columns=['MedInc', 'HouseAge', 'AveRooms',
                                          'AveBedrms', 'Population', 'AveOccup',
                                          'Latitude', 'Longitude'],
                           response_column="MedHouseVal",
                           model_type="Regression"
                           )

            svm_obj.evaluate(newdata = transform_obj.result,
                             id_column = "id"
                             )
        """

        response_column_arg_name = self.get_response_column()
        if hasattr(self.obj, response_column_arg_name):
            response_column = getattr(self.obj, response_column_arg_name)
        else:
            # Created formula object to access the response column property of the formula.
            formula_object = Formula(kwargs["newdata"]._metaexpr, getattr(self.obj, "formula"), "formula")
            response_column = formula_object.response_column

        # Populate 'accumulate' for predict function so that it will be available in output DataFrame.
        if "accumulate" not in kwargs:
            # In case accumulate is not specified by the user set the accumulate as response column.
            kwargs["accumulate"] = response_column
        elif response_column not in kwargs["accumulate"]:
            # Checking if accumulate is passed, and it is not having response column then append response column
            # to the list of values passed to accumulate.
            if isinstance(kwargs["accumulate"], str):
                kwargs["accumulate"] = [kwargs["accumulate"]]
            kwargs["accumulate"].append(response_column)

        predict = self.predict(**kwargs)
        is_classification_model = self.is_classification_model(**kwargs)

        if is_classification_model:

            kwargs["observation_column"] = response_column
            kwargs["prediction_column"] = "Prediction" if "Prediction" in predict.result.columns else "prediction"

            # Update the num_labels by the number of unique values if
            # Labels are not passed.
            if "labels" not in kwargs:
                kwargs["num_labels"] = predict.result.drop_duplicate(kwargs["observation_column"]).shape[0]

            kwargs["data"] = predict.result

            return getattr(module, "ClassificationEvaluator")(**kwargs)
        else:

            # Include the two missing metrics FSTAT and AR2, if the user did not pass the freedom_degrees and
            # independent_features_num then appropriate error message should be displayed.

            # If metrics is specified as "fstat" and "ar2".
            if 'metrics' in kwargs:
                metrics_list = [kwargs.get("metrics")] if isinstance(kwargs.get("metrics"), str) else kwargs.get("metrics")
                metrics_lower_case = {metric : metric.lower() for metric in metrics_list}

                if "fstat" in metrics_lower_case.values():
                    _Validators._validate_dependent_argument("FSTAT", kwargs.get("metrics"),
                                                             "freedom_degrees", kwargs.get("freedom_degrees"))

                if "ar2" in metrics_lower_case.values():
                    _Validators._validate_dependent_argument("AR2", kwargs.get("metrics"),
                                                             "independent_features_num",
                                                             kwargs.get("independent_features_num"))

            if kwargs.get("metrics") is None:
                # If metrics is not specified then evaluate for all metrics except "fstat" and "ar2".
                metrics_list = ['MAE', 'MSE', 'MSLE', 'MAPE', 'MPE', 'RMSE', 'RMSLE', 'R2', 'EV', 'ME', 'MPD',
                                'MGD']
                # If the dependent and optional argument "independent_features_num" is specified then evaluate for AR2
                # also.
                if kwargs.get("independent_features_num") is not None:
                    metrics_list.append("AR2")
                # If the dependent and optional argument "freedom_degrees" is specified then evaluate for FSTAT also.
                if kwargs.get("freedom_degrees") is not None:
                    metrics_list.append("FSTAT")
                kwargs["metrics"] = metrics_list

            kwargs["data"] = predict.result
            kwargs["observation_column"] = response_column
            # The column name for predict result is "Prediction" in some cases and "prediction" in others.
            kwargs["prediction_column"] = "Prediction" if "Prediction" in predict.result.columns else "prediction"

            return getattr(module, "RegressionEvaluator")(**kwargs)


def _get_associated_parent_classes(func_name):
    # By this time, context is established.
    json_path = os.path.join(UtilFuncs._get_data_directory(), "jsons", "paired_functions.json")
    with open(json_path) as fp:
        paired_functions = json.load(fp)
    # Get the paired functions for func_name
    paired_functions = [funcs.get(func_name) for _, funcs in paired_functions.items() if funcs.get(func_name, False)]
    # paired_func_dict uses mapping between class and model trainer object.
    paired_func_dict = {"predict": _Predict, "transform": _Transform,
                        "evaluate": _Evaluate, "forecast": _Forecast,
                        "validate": _Validate, "convolve": _Convolve,
                        "inverse": _Inverse}
    # If paired_functions is empty return empty list
    if not paired_functions:
        return []
    # As there are multiple model trainer object one function can use running a loop to iterate
    for paired_function in paired_functions[0]:

        # KNN needs a special handling for predict. So, returning a specific class for KNN.
        if func_name == "KNN" and paired_function == "predict":
            yield _KNNPredict
        # Here returning class which is used as parent class for func_name.
        if paired_function in paired_func_dict:
            yield paired_func_dict[paired_function]
