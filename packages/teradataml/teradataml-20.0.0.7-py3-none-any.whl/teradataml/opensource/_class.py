# ################################################################## 
# 
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Adithya Avvaru (adithya.avvaru@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# 
# Version: 1.0
# Function Version: 1.0
#
# This file contains classes for Opensource packages like sklearn, 
# lightgbm etc and their corresponding objects.
# 
# ################################################################## 

from importlib import import_module

from teradataml.opensource._constants import _LIGHTGBM_MODULES, _SKL_MODULES
from teradataml.opensource._lightgbm import (_LightgbmSklearnWrapper,
                                             _LightgbmBoosterWrapper,
                                             _LightgbmDatasetWrapper,
                                             _LightgbmFunctionWrapper)
from teradataml.opensource._sklearn import (_SKLearnFunctionWrapper,
                                            _SkLearnObjectWrapper)


class _OpenSource:
    """
    A class to extend teradataml to other open source packages like scikit-learn,
    spark, pytorch, snowflake etc.
    """

    def __init__(self):
        self._modules = None
        self._object_wrapper = None
        self._function_wrapper = None

    def _get_module_and_class_instance(self, name):
        """
        Internal function to get the module and class instance/function which will
        be passed to object/function wrapper.
        """
        class_instance = None
        module = None
        for module in self._modules:
            lib = import_module(module)
            try:
                class_instance = getattr(lib, name)
                break
            except AttributeError as ex:
                continue

        if not class_instance:
            raise ValueError(f"The class/function '{name}' does not exist in '{self.__class__.name.lower()}' modules.")

        return module, class_instance

    def __getattr__(self, name):

        def __get_module(*c, **kwargs):
            module, class_instance = self._get_module_and_class_instance(name)

            # If the attribute is a function, then return the function object.
            if type(class_instance).__name__ == "function":
                return self._function_wrapper(module_name=module, func_name=name)(*c, **kwargs)

            return self._object_wrapper(module_name=module, class_name=name,
                                        pos_args=c, kwargs=kwargs)

        return __get_module

    def deploy(self, model_name, model, replace_if_exists=False):
        """
        DESCRIPTION:
            Deploys the model to Vantage.

        PARAMETERS:
            model_name:
                Required Argument.
                Specifies the unique name of the model to be deployed.
                Types: str

            model:
                Required Argument.
                Specifies the teradataml supported opensource model object that is to be deployed.
                Currently supported models are:
                    - sklearn
                    - lightgbm
                Types: object

            replace_if_exists:
                Optional Argument.
                Specifies whether to replace the model if a model with the same name already
                exists in Vantage. If this argument is set to False and a model with the same
                name already exists, then the function raises an exception.
                Default Value: False
                Types: bool

        RETURNS:
            The opensource object wrapper.

        RAISES:
            TeradataMLException if model with "model_name" already exists and the argument
            "replace_if_exists" is set to False.

        EXAMPLES:
            ## sklearn examples.

            # Import required packages and create LinearRegression sklearn object.
            >>> from teradataml import td_sklearn
            >>> from sklearn.linear_model import LinearRegression
            >>> model = LinearRegression(normalize=True)

            # Example 1: Deploy the model to Vantage.
            >>> lin_reg = td_sklearn.deploy("linreg_model_ver_1", model)
            Model is saved.
            >>> lin_reg
            LinearRegression(normalize=True)

            # Example 2: Deploy the model to Vantage with the name same as that of model that
            #            already existed in Vantage.
            >>> lin_reg = td_sklearn.deploy("linreg_model_ver_1", model, replace_if_exists=True)
            Model is deleted.
            Model is saved.
            >>> lin_reg
            LinearRegression(normalize=True)

            ## lightgbm examples.

            # Import required packages and create LGBMClassifier lightGBM object.
            >>> from teradataml import td_lightgbm
            >>> import lightgbm as lgb
            >>> model = lgb.LGBMClassifier()

            # Example 1: Deploy the LightGBM model to Vantage.
            >>> lgb_model = td_lightgbm.deploy("lgb_model_ver_1", model)
            Model is saved.
            >>> lgb_model
            LGBMClassifier()

            # Example 2: Deploy the LightGBM model to Vantage with the name same as that of model that
            #            already existed in Vantage.
            >>> lgb_model = td_lightgbm.deploy("lgb_model_ver_1", model, replace_if_exists=True)
            Model is deleted.
            Model is saved.
            >>> lgb_model
            LGBMClassifier()

            # Example 3: Deploy LightGBM model trained locally using train() function to Vantage.
            # Create Dataset object locally, assuming pdf_x and pdf_y are the feature and label pandas
            # DataFrames.
            >>> lgbm_data = lgb.Dataset(data=pdf_x, label=pdf_y, free_raw_data=False)
            >>> lgbm_data
            <lightgbm.basic.Dataset object at ....>

            # Train the model using train() function.
            >>> model = lgb.train(params={}, train_set=lgbm_data, num_boost_round=30, valid_sets=[lgbm_data])
            [LightGBM] [Warning] Auto-choosing row-wise multi-threading, the overhead of testing was 0.000043 seconds.
            You can set `force_row_wise=true` to remove the overhead.
            And if memory is not enough, you can set `force_col_wise=true`.
            [LightGBM] [Info] Total Bins 532
            [LightGBM] [Info] Number of data points in the train set: 400, number of used features: 4
            [1]	valid_0's l2: 0.215811
            [2]	valid_0's l2: 0.188138
            [3]	valid_0's l2: 0.166146
            ...
            ...
            [29]	valid_0's l2: 0.042255
            [30]	valid_0's l2: 0.0416953

            # Deploy the model to Vantage.
            >>> lgb_model = td_lightgbm.deploy("lgb_model_ver_2", model)
            >>> lgb_model
            <lightgbm.basic.Booster object at ...>

        """
        return self._object_wrapper._deploy(model_name=model_name,
                                            model=model,
                                            replace_if_exists=replace_if_exists)

    def load(self, model_name):
        """
        DESCRIPTION:
            Loads the model from Vantage based on the interface object on which this function
            is called.
            For example, if the model in "model_name" argument is statsmodel model, then this
            function raises exception if the interface object is `td_sklearn`.

        PARAMETERS:
            model_name:
                Required Argument.
                Specifies the name of the model to be loaded.
                Types: str

        RETURNS:
            The opensource object wrapper.

        RAISES:
            TeradataMlException if model with name "model_name" does not exist.

        EXAMPLE:
            # sklearn example.
            >>> from teradataml import td_sklearn
            >>> # Load the model saved in Vantage. Note that the model is saved using
            >>> # `deploy()` of exposed interface object (like `td_sklearn`) or
            >>> # `_OpenSourceObjectWrapper` Object.
            >>> model = td_sklearn.load("linreg_model_ver_1")
            >>> model
            LinearRegression(normalize=True)

            # lightgbm example.
            >>> from teradataml import td_lightgbm
            >>> # Load the model saved in Vantage. Note that the model is saved using
            >>> # `deploy()` of exposed interface object (like `td_lightgbm`) or
            >>> # `_OpenSourceObjectWrapper` Object.
            >>> model = td_lightgbm.load("lgb_model_ver_1")
            >>> model
            LGBMClassifier()
        """
        return self._object_wrapper._load(model_name)


class Sklearn(_OpenSource):
    """
    DESCRIPTION:
        Interface object to access exposed classes and functions of scikit-learn 
        opensource package. All the classes and functions can be run and attributes 
        can be accessed using the object created by "td_sklearn" interface object.
        Refer Teradata Python Package User Guide for more information about OpenML 
        and exposed interface objects.

    PARAMETERS:
        None

    RETURNS:
        None

    EXAMPLES:
        # Load example data.
        >>> load_example_data("openml", ["test_classification", "test_prediction"])
        >>> df = DataFrame("test_classification")
        >>> df.head(3)
                       col2      col3      col4  label
        col1
        -2.560430  0.402232 -1.100742 -2.959588      0
        -3.587546  0.291819 -1.850169 -4.331055      0
        -3.697436  1.576888 -0.461220 -3.598652      0

        >>> df_test = DataFrame("test_prediction")
        >>> df_test.head(3)
                       col2      col3      col4
        col1
        -2.560430  0.402232 -1.100742 -2.959588
        -3.587546  0.291819 -1.850169 -4.331055
        -3.697436  1.576888 -0.461220 -3.598652


        # Get the feature and label data.
        >>> df_x_clasif = df.select(df.columns[:-1])
        >>> df_y_clasif = df.select(df.columns[-1])

        >>> from teradataml import td_sklearn
        >>> dt_cl = td_sklearn.DecisionTreeClassifier(random_state=0)
        >>> dt_cl
        DecisionTreeClassifier(random_state=0)

        # Set the paramaters.
        >>> dt_cl.set_params(random_state=2, max_features="sqrt")
        DecisionTreeClassifier(max_features='sqrt', random_state=2)

        # Get the paramaters.
        >>> dt_cl.get_params()
        {'ccp_alpha': 0.0,
         'class_weight': None,
         'criterion': 'gini',
         'max_depth': None,
         'max_features': 'sqrt',
         'max_leaf_nodes': None,
         'min_impurity_decrease': 0.0,
         'min_impurity_split': None,
         'min_samples_leaf': 1,
         'min_samples_split': 2,
         'min_weight_fraction_leaf': 0.0,
         'random_state': 2,
         'splitter': 'best'}

        # Train the model using fit().
        >>> dt_cl.fit(df_x_clasif, df_y_clasif)
        DecisionTreeClassifier(max_features='sqrt', random_state=2)

        # Perform prediction.
        >>> dt_cl.predict(df_test)
               col1      col2      col3      col4  decisiontreeclassifier_predict_1
        0  1.105026 -1.949894 -1.537164  0.073171                                 1
        1  1.878349  0.577289  1.795746  2.762539                                 1
        2 -1.130582 -0.020296 -0.710234 -1.440991                                 0
        3 -1.243781  0.280821 -0.437933 -1.379770                                 0
        4 -0.509793  0.492659  0.248207 -0.309591                                 1
        5 -0.345538 -2.296723 -2.811807 -1.993113                                 0
        6  0.709217 -1.481740 -1.247431 -0.109140                                 0
        7 -1.621842  1.713381  0.955084 -0.885921                                 1
        8  2.425481 -0.549892  0.851440  2.689135                                 1
        9  1.780375 -1.749949 -0.900142  1.061262                                 0

        # Perform scoring.
        >>> dt_cl.score(df_x_clasif, df_y_clasif)
           score
        0    1.0

        # Access few attributes.
        >>> dt_cl.classes_
        array([0., 1.])

        >>> dt_cl.feature_importances_
        array([0.06945187, 0.02      , 0.67786339, 0.23268474])

        >>> dt_cl.max_features_
        2
    """
    def __init__(self):
        super().__init__()
        self._modules = _SKL_MODULES
        self._object_wrapper = _SkLearnObjectWrapper
        self._function_wrapper = _SKLearnFunctionWrapper


class Lightgbm(_OpenSource):
    """
    DESCRIPTION:
        Interface object to access exposed classes and functions of lightgbm
        opensource package. All the classes and functions can be run and attributes
        can be accessed using the object created by "td_lightgbm" interface object.
        Refer Teradata Python Package User Guide for more information about OpenML
        and exposed interface objects.

    PARAMETERS:
        None

    RETURNS:
        None

    EXAMPLES:
        # Load example data.
        >>> load_example_data("openml", ["test_classification"])
        >>> df = DataFrame("test_classification")
        >>> df.head(3)
                       col2      col3      col4  label
        col1
        -2.560430  0.402232 -1.100742 -2.959588      0
        -3.587546  0.291819 -1.850169 -4.331055      0
        -3.697436  1.576888 -0.461220 -3.598652      0

        # Get the feature and label data.
        >>> df_x = df.select(df.columns[:-1])
        >>> df_y = df.select(df.columns[-1])

        >>> from teradataml import td_lightgbm

        # Example 1: Train the model using train() function.
        # Create lightgbm Dataset object.
        >>> lgbm_data = td_lightgbm.Dataset(data=df_x, label=df_y, free_raw_data=False)
        >>> lgbm_data
        <lightgbm.basic.Dataset object at ...>

        # Train the model.
        >>> model = td_lightgbm.train(params={}, train_set=lgbm_data, num_boost_round=30, valid_sets=[lgbm_data])
        [LightGBM] [Warning] Auto-choosing row-wise multi-threading, the overhead of testing was 0.000043 seconds.
        You can set `force_row_wise=true` to remove the overhead.
        And if memory is not enough, you can set `force_col_wise=true`.
        [LightGBM] [Info] Total Bins 532
        [LightGBM] [Info] Number of data points in the train set: 400, number of used features: 4
        [1]	valid_0's l2: 0.215811
        [2]	valid_0's l2: 0.188138
        [3]	valid_0's l2: 0.166146
        ...
        ...
        [29]	valid_0's l2: 0.042255
        [30]	valid_0's l2: 0.0416953
        >>> model
        <lightgbm.basic.Booster object at ...>

        # Example 2: Train the model using LGBMClassifier sklearn object.
        # Create lightgbm sklearn object.
        >>> lgbm_cl = td_lightgbm.LGBMClassifier()
        >>> lgbm_cl
        LGBMClassifier()

        # Fit/train the model using fit() function.
        >>> lgbm_cl.fit(df_x, df_y)
        LGBMClassifier()

        # Perform prediction.
        >>> lgbm_cl.predict(df_x).head(3)
               col1      col2      col3      col4  lgbmclassifier_predict_1
        0  1.105026 -1.949894 -1.537164  0.073171                         1
        1  1.878349  0.577289  1.795746  2.762539                         1
        2 -1.130582 -0.020296 -0.710234 -1.440991                         0

        # Access attributes.
        >>> lgbm_cl.feature_importances_
        array([ 0, 20, 10, 10])
    """

    def __init__(self):
        super().__init__()
        self._modules = _LIGHTGBM_MODULES
        self._object_wrapper = _LightgbmBoosterWrapper
        self._function_wrapper = _LightgbmFunctionWrapper

    def _assign_object_wrapper(self, module, class_name):
        """
        Assigns the appropriate object wrapper based on the module and class name.
        """

        if module == "lightgbm.basic" and class_name == "Booster":
            self._object_wrapper = _LightgbmBoosterWrapper

        if module == "lightgbm.basic" and class_name == "Dataset":
            self._object_wrapper = _LightgbmDatasetWrapper

        if module == "lightgbm.sklearn":
            self._object_wrapper = _LightgbmSklearnWrapper

    def __getattr__(self, name):

        def __get_module(*c, **kwargs):
            module, class_instance = self._get_module_and_class_instance(name)

            # If the attribute is a function, then return the function object.
            if type(class_instance).__name__ == "function":
                kwargs.update(zip(class_instance.__code__.co_varnames, c))

                if module == "lightgbm.callback":
                    return {"module": module, "func_name": name, "kwargs": kwargs}

                return self._function_wrapper(module_name=module, func_name=name)(**kwargs)

            kwargs.update(zip(class_instance.__init__.__code__.co_varnames[1:], c))

            all_args = {"module_name": module, "class_name": name, "kwargs": kwargs}
            self._assign_object_wrapper(module, name)

            return self._object_wrapper(**all_args)

        return __get_module

    def deploy(self, model_name, model, replace_if_exists=False):
        # Docstring of parent class also contain examples of lightgbm.
        module = model.__module__ if hasattr(model, "__module__") else None
        class_name = model.__class__.__name__ if hasattr(model, "__class__") else None

        if module is None or class_name is None:
            raise ValueError("The model object is not supported for deployment.")

        self._assign_object_wrapper(module, class_name)

        return self._object_wrapper._deploy(model_name=model_name,
                                            model=model,
                                            replace_if_exists=replace_if_exists)


td_sklearn = Sklearn()
td_lightgbm = Lightgbm()
