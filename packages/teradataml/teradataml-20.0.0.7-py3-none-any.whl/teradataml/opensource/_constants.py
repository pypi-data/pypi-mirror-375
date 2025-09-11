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
# This file contains constants needed for the opensource packages.
# 
# ################################################################## 

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from teradataml import BLOB, VARCHAR

_SKL_MODULES = ["sklearn.calibration", "sklearn.cluster", "sklearn.compose", "sklearn.covariance",
                "sklearn.decomposition", "sklearn.discriminant_analysis",
                "sklearn.dummy", "sklearn.ensemble", "sklearn.feature_extraction", "sklearn.feature_selection",
                "sklearn.gaussian_process", "sklearn.impute", "sklearn.isotonic", "sklearn.kernel_approximation",
                "sklearn.kernel_ridge", "sklearn.linear_model", "sklearn.manifold", "sklearn.mixture",
                "sklearn.model_selection", "sklearn.multiclass", "sklearn.multioutput", "sklearn.naive_bayes",
                "sklearn.neighbors", "sklearn.neural_network", "sklearn.preprocessing", "sklearn.random_projection",
                "sklearn.semi_supervised", "sklearn.svm", "sklearn.tree", "sklearn.pipeline", "sklearn.cross_decomposition",
                "sklearn.gaussian_process.kernels", "sklearn.metrics"]
_LIGHTGBM_MODULES = ["lightgbm.basic", "lightgbm.callback", "lightgbm.compat", "lightgbm.engine", "lightgbm.sklearn"]
# "lightgbm.cv", "lightgbm.dask",

class OpenSourcePackage(Enum):
    SKLEARN = "sklearn"
    LIGHTGBM = "lightgbm"

    @classmethod
    def values(cls):
        return [item.value for item in cls]


_packages_verified_in_vantage = {} # Used to ensure check for python and python packages done only once per package.

@dataclass
class OpensourceModels:
    """Dataclass for Opensource Models details."""
    is_default_partition_value: bool  # Whether partition value is default or not.
    partition_file_prefix: str
    model: Any # Either individual model or pandas dataframe of models with partition columns.
    pos_args: Tuple[Any] = tuple() # Positional arguments used for model creation.
    key_args: Dict[str, Any] = field(default_factory=dict) # Keyword arguments used for model creation.
    fit_partition_columns_non_default: Optional[str] = None  # Columns used for partitioning.
    osml_module: Optional[str] = None # Module of corresponding wrapper class.
    osml_class: Optional[str] = None # Corresponding wrapper class name.

# Model table details used by opensource BYOM.
_OSML_MODELS_TABLE_NAME = "opensourceml_models"
_OSML_MODELS_PRIMARY_INDEX = "model_id"
_OSML_ADDITIONAL_COLUMN_TYPES = {"package": VARCHAR(128)} # sklearn or keras etc
_OSML_MODELS_TABLE_COLUMNS_TYPE_DICT = {"model_id": VARCHAR(128), "model": BLOB()}