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
# This file contains helper functions for opensource wrapper and sklearn wrapper class.
# 
# ##################################################################

import functools
import time
import uuid
from math import floor

from teradataml import TeradataMlException
from teradataml.common.aed_utils import AedUtils
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dataframe.dataframe_utils import DataFrameUtils
from teradataml.utils.validators import _Validators

aed_utils = AedUtils()
df_utils = DataFrameUtils()

def _validate_fit_run(func):
    """
    Internal function to validate if the model is fitted before calling function specified
    by "func" parameter.

    PARAMETERS:
        func    - Specifies the function to be called if the model is fitted.

    RETURNS:
        function call

    RAISES:
        TeradataMlException if model is not fitted and function is called.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        func_name = kwargs["name"]
        if not self._is_model_installed:
            raise TeradataMlException(Messages.get_message(MessageCodes.MODEL_NOT_FITTED,
                                                           func_name),
                                      MessageCodes.MODEL_NOT_FITTED)
        return func(self, *args, **kwargs)

    return wrapper

def _generate_new_name(type=None, extension=None):
    """
    Internal function to generate new column name or file name.

    PARAMETERS:
        type    - Specifies the type of the name to be generated.
                  Permitted Values: 'column', 'file'
        extension   - Specifies the extension to be added to the random file name.
                      Applicable only when type is file'

    RETURNS:
        New name as string

    RAISES:
        None
    """
    timestamp = time.time()
    tmp = "{}{}".format(floor(timestamp / 1000000),
                        floor(timestamp % 1000000 * 1000000 +
                              int(str(uuid.uuid4().fields[-1])[:10])))
    if type:
        tmp = f"{type}_{tmp}_"
    if extension:
        tmp = f"{tmp}.{extension}"
    return tmp

def _derive_df_and_required_columns(X=None, y=None, groups=None, kwargs={},
                                    fit_partition_cols=None):
    """
    Internal function to get parent teradataml DataFrame from X, y and groups and corresponding
    feature columns, label columns and group columns along with partition_columns passed
    in kwargs.

    PARAMETERS:
        X   - Specifies the teradataml DataFrame containing data related to feature columns.
        y   - Specifies the teradataml DataFrame containing data related to label columns.
        groups  - Specifies the teradataml DataFrame containing data related to group columns.
        kwargs  - Specifies the dictionary of arguments with keys:
                    - data
                    - feature_columns
                    - label_columns
                    - group_columns
                    - partition_columns
        fit_partition_cols - Specifies the partition columns fitted to the model.

    RETURNS:
        parent DataFrame, feature columns, label columns, group columns, data partition columns

    RAISES:
        TeradataMlException if columns are not from the given DataFrame "data".
    """
    data = kwargs.get("data", None)
    feature_columns = kwargs.get("feature_columns", None)
    feature_columns = UtilFuncs._as_list(feature_columns) if feature_columns else []
    label_columns = kwargs.get("label_columns", None)
    label_columns = UtilFuncs._as_list(label_columns) if label_columns else []
    group_columns = kwargs.get("group_columns", None)
    group_columns = UtilFuncs._as_list(group_columns) if group_columns else []
    partition_columns = kwargs.get("partition_columns", None)
    if partition_columns:
        partition_columns = UtilFuncs._as_list(partition_columns)
    elif fit_partition_cols:
        partition_columns = fit_partition_cols
    else:
        partition_columns = []

    if X:
        # If X is passed, then data, feature_columns, label_columns, group_columns are
        # ignored and derived from X, y, groups arguments.
        feature_columns = [col for col in X.columns if col not in partition_columns]
        all_dfs = [X]
        label_columns = []
        group_columns = []
        if y:
            all_dfs.append(y)
            label_columns = y.columns
        if groups:
            all_dfs.append(groups)
            group_columns = groups.columns

        data = df_utils._get_common_parent_df_from_dataframes(all_dfs)

    if data:
        # Execute node, if not executed already to get table name.
        if aed_utils._aed_is_node_executed(data._nodeid):
            _ = df_utils._execute_node_return_db_object_name(data._nodeid)

    # Validate if columns in "feature_columns", "label_columns" are different or not.
    if set(feature_columns).intersection(set(label_columns)):
        raise TeradataMlException(Messages.get_message(MessageCodes.ARGS_WITH_SAME_COLUMNS,
                                                       "feature_columns/X DataFrame",
                                                       "label_columns/y DataFrame",
                                                       " not"),
                                  MessageCodes.ARGS_WITH_SAME_COLUMNS)

    return data, feature_columns, label_columns, group_columns, partition_columns

def _validate_df_query_type(df, node_query_type, arg_name):
    """
    Internal function to validate if the DataFrame's node type is same as the type specified.

    PARAMETERS:
        df  - Specifies the teradataml DataFrame to be validated for node type.
        node_query_type - Specifies the type of the node to be compared with.
        arg_name - Specifies the name of the argument in which the node id is passed.

    RETURNS:
        None

    RAISES:
        TeradataMlException if node with given id is not same as the type specified.
    """
    if df and aed_utils._aed_get_node_query_type(df._nodeid) != node_query_type:
        raise TeradataMlException(Messages.get_message(MessageCodes.NODE_NOT_GIVEN_TYPE,
                                                       arg_name, node_query_type),
                                  MessageCodes.NODE_NOT_GIVEN_TYPE)

def _validate_opensource_func_args(X=None, y=None, groups=None, fit_partition_cols=None,
                                   kwargs={}, skip_either_or_that=False):
    """
    Internal function to validate arguments passed to exposed opensource APIs.

    PARAMETERS:
        X   - Specifies the teradataml DataFrame containing data related to feature columns.
        y   - Specifies the teradataml DataFrame containing data related to label columns.
        groups  - Specifies the teradataml DataFrame containing data related to group columns.
        fit_partition_cols - Specifies the partition columns fitted to the model.
        kwargs  - Specifies the dictionary of arguments with keys:
                    - data
                    - feature_columns
                    - label_columns
                    - group_columns
                    - partition_columns
        skip_either_or_that - Specifies whether to skip validation of either or that arguments.
    RETURNS:
        None

    RAISES:
        TeradataMlException if arguments' validations fail.
    """
    data = kwargs.get("data", None)
    feature_columns = kwargs.get("feature_columns", None)
    label_columns = kwargs.get("label_columns", None)
    group_columns = kwargs.get("group_columns", None)
    partition_columns = kwargs.get("partition_columns", None)

    # Argument validations
    arg_info_matrix = []
    arg_info_matrix.append(["X", X, True, (DataFrame)])
    arg_info_matrix.append(["y", y, True, (DataFrame)])
    arg_info_matrix.append(["groups", groups, True, (DataFrame)])
    arg_info_matrix.append(["partition_columns", partition_columns, True, (str, list)])
    arg_info_matrix.append(["data", data, True, (DataFrame)])
    arg_info_matrix.append(["feature_columns", feature_columns, True, (str, list)])
    arg_info_matrix.append(["label_columns", label_columns, True, (str, list)])
    arg_info_matrix.append(["group_columns", group_columns, True, (str, list)])

    # Validate argument types
    _Validators._validate_function_arguments(arg_info_matrix)

    if not skip_either_or_that and not X and not data and not feature_columns:
        raise TeradataMlException(Messages.get_message(MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT,
                                                       "X", "data and feature_columns"),
                                    MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)

    if X:
        # Validate if "X", "y" and "groups" are from select() call.
        # Whether they are from same parent or not, will be validated while parent is being
        # extracted.
        if y or groups:
            # If any one of "y" or "groups" exists, then "X" must be from select() call.
            # Otherwise, it can be from any parent or direct DataFrame.
            _validate_df_query_type(X, "select", "X")

        _validate_df_query_type(y, "select", "y")
        _validate_df_query_type(groups, "select", "groups")

        # Validate if columns in "partition_columns" argument are present in "X".
        _Validators._validate_column_exists_in_dataframe(columns=partition_columns,
                                                         metaexpr=X._metaexpr,
                                                         column_arg="partition_columns",
                                                         data_arg="X")

        if fit_partition_cols and not partition_columns and \
            not all([col in X.columns for col in fit_partition_cols]):
            # Check if fitted partition columns are present in "X" if "partition_columns" is not
            # not passed.
            msg = Messages.get_message(MessageCodes.PARTITIONING_COLS_DIFFERENT, "X")
            raise TeradataMlException(msg, MessageCodes.PARTITIONING_COLS_DIFFERENT)

    if data and not X:
        # Thse validations are required only when "X" is not passed because "data" is ignored when
        # "X" is passed.

        all_cols_list = [feature_columns, label_columns, group_columns, partition_columns]
        arg_name_list = ["feature_columns", "label_columns", "group_columns", "partition_columns"]

        for cols, arg_name in zip(all_cols_list, arg_name_list):
            # Validate if columns in these arguments are present in "data".
            _Validators._validate_column_exists_in_dataframe(columns=cols,
                                                             metaexpr=data._metaexpr,
                                                             column_arg=arg_name,
                                                             data_arg="data")

        if fit_partition_cols and not partition_columns and \
            not all([col in data.columns for col in fit_partition_cols]):
            # Check if fitted partition columns are present in "data" if "partition_columns" is not
            # not passed.
            msg = Messages.get_message(MessageCodes.PARTITIONING_COLS_DIFFERENT, "data")
            raise TeradataMlException(msg, MessageCodes.PARTITIONING_COLS_DIFFERENT)
