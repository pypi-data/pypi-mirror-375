"""
Copyright (c) 2020 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Rohit.Khurd@teradata.com
Secondary Owner:

teradataml Model Cataloging utilities
-------------------------------------
The teradataml Model Cataloging utility functions provide internal utilities that
the Model Cataloging APIs make use of.
"""
import importlib
import warnings
import pandas as pd
import re

from teradataml.common.constants import ModelCatalogingConstants as mac,\
    FunctionArgumentMapperConstants as famc
from teradataml.common.constants import TeradataConstants
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.utils import UtilFuncs
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.context.context import get_connection, get_context, _get_current_databasename
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.catalog.function_argument_mapper import _argument_mapper
from teradataml.common.sqlbundle import SQLBundle
from teradataml.utils.utils import execute_sql
from teradatasqlalchemy import CLOB
from teradatasqlalchemy.dialect import preparer, dialect as td_dialect
from sqlalchemy.sql.expression import select, case as case_when
from sqlalchemy import func


def __get_arg_sql_name_from_tdml(function_arg_map, arg_type, name):
    """
    DESCRIPTION:
        Internal function to find SQL equivalent name for given teradataml name.

    PARAMETERS:
        function_arg_map:
            Required Argument.
            The teradataml-sql map for the function obtained using function_argument_mapper.
            Types: dict

        arg_type:
            Required Argument.
            Specifies a string representing the type of lookup, one of the keys in the function argument map.
            Acceptable values: 'arguments', 'inputs', 'outputs'
            Types: str

        name:
            Required Argument.
            Specifies the teradataml input, output, or argument name to lookup.
            Types: str

    RETURNS:
        A String representing the SQL equivalent name for the teradataml name passed as input.

    EXAMPLES:
        >>> sql_name = __get_arg_sql_name_from_tdml(function_arg_map, arg_type, name)
    """
    if name in function_arg_map[arg_type][famc.TDML_TO_SQL.value]:
        sql_name = function_arg_map[arg_type][famc.TDML_TO_SQL.value][name]

        if isinstance(sql_name, dict):
            sql_name = sql_name[famc.TDML_NAME.value]

        if isinstance(sql_name, list):
            sql_name = sql_name[0]

        return sql_name

    # No SQL name found for given teradataml input name
    return None


def __get_arg_tdml_name_from_sql(function_arg_map, arg_type, name):
    """
    DESCRIPTION:
        Internal function to find teradataml equivalent name and type, if any, for given SQL name.

    PARAMETERS:
        function_arg_map:
            Required Argument.
            The teradataml-sql map for the function obtained using function_argument_mapper.
            Types: dict

        arg_type:
            Required Argument.
            Specifies a string representing the type of lookup, one of the keys in the function argument map.
            Acceptable values: 'arguments', 'inputs', 'outputs'
            Types: str

        name:
            Required Argument.
            Specifies the SQL input, output, or argument name to lookup.
            Types: str

    RETURNS:
        * A String representing the teradataml equivalent name for the SQL name when arg_type
          is 'inputs' or 'outputs'.
        * A dictionary with tdml_name and tdml_type for the SQL name when arg_type
          is 'arguments'.


    EXAMPLES:
        >>> tdml_name = __get_arg_tdml_name_from_sql(function_arg_map, arg_type, name)
    """
    if name in function_arg_map[arg_type][famc.SQL_TO_TDML.value]:
        tdml_name = function_arg_map[arg_type][famc.SQL_TO_TDML.value][name]

        # Check for alternate names.
        if isinstance(tdml_name, dict) and famc.ALTERNATE_TO.value in tdml_name:
            alternate_to = function_arg_map[arg_type][famc.SQL_TO_TDML.value][name][
                famc.ALTERNATE_TO.value]
            tdml_name = function_arg_map[arg_type][famc.SQL_TO_TDML.value][alternate_to]

        if isinstance(tdml_name, list):
            tdml_name = tdml_name[0]

        return tdml_name

    # No teradataml name found for given teradataml input name
    return None


def __get_model_inputs_outputs(model, function_arg_map):
    """
    DESCRIPTION:
        Internal function to get input and output information of the model to be saved.

    PARAMETERS:
        model:
            Required Argument.
            The model (analytic function object instance) to be saved.
            Types: teradataml Analytic Function object

        function_arg_map:
            Required Argument.
            The teradataml-sql map for the function obtained using function_argument_mapper.
            Types: dict

    RETURNS:
        A tuple of two dictionaries, and a list:
        * The first containing input information.
        * The second containing output information.
        * The list containing names of tables to remove entries from GC for.

    EXAMPLE:
        >>> inputs, outputs, tables_to_not_gc = __get_model_inputs_outputs(model, function_arg_map)
    """
    input_json = {}
    output_json = {}
    remove_tables_entries_from_gc = []

    # First, let's identify the output DataFrames
    output_tables = [df._table_name for df in model._mlresults]

    for key in model.__dict__:
        if not key.startswith('_'):
            member = getattr(model, key)
            # The DataFrame is input if it is not output
            if isinstance(member, DataFrame):
                if member._table_name not in output_tables:
                    # Populate the input dictionary
                    # We construct a dictionary of the following form:
                    # { "<schema_name> :
                    #     { "<table_name>" :
                    #         { "nrows": <num_rows>,
                    #           "ncols": <num_cols>,
                    #           "input_name": <SQL name for the input>,
                    #           "client_specific_input_name": <tdml name for the input>
                    #         },
                    #         ...
                    #     }
                    # }
                    tdp = preparer(td_dialect)
                    nrows, ncols = member.shape
                    db_schema = UtilFuncs._extract_db_name(member._table_name)
                    # Add quotes around the DB name in case we are getting it using _get_current_databasename().
                    db_schema = tdp.quote(_get_current_databasename()) if db_schema is None else db_schema
                    db_table_name = UtilFuncs._extract_table_name(member._table_name)

                    if db_schema not in input_json:
                        input_json[db_schema] = {}
                    input_json[db_schema][db_table_name] = {}
                    input_json[db_schema][db_table_name]["nrows"] = int(nrows)
                    input_json[db_schema][db_table_name]["ncols"] = ncols
                    input_json[db_schema][db_table_name]["input_name"] = __get_arg_sql_name_from_tdml(function_arg_map,
                                                                                                      arg_type=famc.INPUTS.value,
                                                                                                      name=key)
                    input_json[db_schema][db_table_name]["client_specific_input_name"] = key
                else:
                    # Populate the output dictionary
                    # We construct a dictionary of the following form:
                    # { "<Output SQL Name> :
                    #     { "table_name": "<Database qualified name of the table>",
                    #       "client_specific_name": "<TDML specific name of the output>"
                    #     },
                    #     ...
                    # }

                    # teradataml Analytic functions models can be of two types:
                    #   1. Non-lazy OR
                    #   2. Lazy
                    # When model is non-lazy, that means model tables are already present/created on the system.
                    # When model is lazy, it may happen that model tables are yet to be evaluated/created.
                    # So first, let's make sure that model is evaluated, i.e., model tables are created,
                    # if they are not created already.
                    #
                    if member._table_name is None:
                        member._table_name = df_utils._execute_node_return_db_object_name(member._nodeid,
                                                                                          member._metaexpr)
                    output_table_name = member._table_name
                    if __is_view(output_table_name):
                        # If output table is not of type table, which means it's a view.
                        # So instead of using view name for persisting, we must materialize the same.
                        #
                        # To do so, let's just generate another temporary table name. One can notice, when
                        # we generate the temporary table name, we set the following flag 'gc_on_quit=True'.
                        # One can say, why to mark it for GC, when we are going to persist it.
                        # Only reason we added it for GC, so that, if in case anything goes wrong from the point
                        # we create the table to the end of the model saving, later this will be GC'ed as
                        # model saving had failed. Later we remove entry from GC, when model info is saved in
                        # MC tables and model is persisted in table.
                        #
                        output_table_name = UtilFuncs._generate_temp_table_name(prefix="td_saved_model_",
                                                                                use_default_database=True,
                                                                                gc_on_quit=True, quote=False,
                                                                                table_type=TeradataConstants.TERADATA_TABLE)

                        base_query = SQLBundle._build_base_query(member._table_name)
                        crt_table_query = SQLBundle._build_create_table_with_data(output_table_name, base_query)
                        UtilFuncs._execute_ddl_statement(crt_table_query)

                    # Append the name of the table to remove entry from GC.
                    remove_tables_entries_from_gc.append(output_table_name)

                    sql_name = __get_arg_sql_name_from_tdml(function_arg_map, arg_type=famc.OUTPUTS.value, name=key)
                    output_json[sql_name] = {}
                    output_json[sql_name]["table_name"] = output_table_name
                    output_json[sql_name]["client_specific_name"] = key

    return input_json, output_json, remove_tables_entries_from_gc


def __check_if_client_specific_use(key, function_arg_map, is_sql_name=False):
    """
    DESCRIPTION:
        Internal function to check if the argument corresponds to a client-only specific argument.

    PARAMETERS:
        key:
            Required Argument.
            The teradataml or SQL argument name to check for.
            Types: str

        function_arg_map:
            Required Argument.
            The teradataml-sql map for the function obtained using function_argument_mapper.
            Types: dict

        is_sql_name:
            Optional Argument.
            Specifies a boolean value indicating whether the key is a SQL or teradataml key.
            Types: bool
            Default Value: False

    RETURNS:
        A tuple containing:
        * A boolean value indicating whether the argument is or has:
            - a client-only specific argument: True
            - else False
        * A string specifying whether it is used in sequence_column ('used_in_sequence_by') or formula ('used_in_formula')

    EXAMPLES:
        >>> client_only, where_used = __check_if_client_specific_use(key, function_arg_map, is_sql_name=False)
    """
    # Let's assume SQL Name was passed
    sql_name = key

    if not is_sql_name:
        if key in function_arg_map[famc.ARGUMENTS.value][famc.TDML_TO_SQL.value]:
            sql_name = __get_arg_sql_name_from_tdml(function_arg_map, arg_type=famc.ARGUMENTS.value, name=key)
        else:
            # No SQL name found for given teradataml input name
            return False, None

    if isinstance(sql_name, dict):
        sql_name = sql_name[famc.TDML_NAME.value]

    if isinstance(sql_name, list):
        sql_name = sql_name[0]

    # Check if SQL name is an alternate name
    sql_block = function_arg_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][sql_name]
    if famc.ALTERNATE_TO.value in sql_block:
        alternate_to = function_arg_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][sql_name][famc.ALTERNATE_TO.value]
        sql_block = function_arg_map[famc.ARGUMENTS.value][famc.SQL_TO_TDML.value][alternate_to]

    # Check and return boolean indicating if it is a formula or sequence_input_by argument
    if famc.USED_IN_SEQUENCE_INPUT_BY.value in sql_block:
        return True, famc.USED_IN_SEQUENCE_INPUT_BY.value
    elif famc.USED_IN_FORMULA.value in sql_block:
        return True, famc.USED_IN_FORMULA.value
    else:
        return False, None

def __check_if_model_exists(name, created=False, accessible=False,
                            raise_error_if_exists=False, raise_error_if_model_not_found=False):
    """
    DESCRIPTION:
        Internal function to check if model with model_name, exists or not.

    PARAMETERS:
        name:
            Required Argument.
            Specifies the name of the model to check whether it exists or not.
            Types: str

        created:
            Optional Argument.
            Specifies whether to check if the model exists and is created by the user.
            Default Value: False (Check for all models)
            Types: bool

        accessible:
            Optional Argument.
            Specifies whether to check if the model exists and is accessible by the user.
            Default Value: False (Check for all models)
            Types: bool

        raise_error_if_exists:
            Optional Argument.
            Specifies the flag to decide whether to raise error when model exists or not.
            Default Value: False (Do not raise exception)
            Types: bool

        raise_error_if_model_not_found:
            Optional Argument.
            Specifies the flag to decide whether to raise error when model is found or not.
            Default Value: False (Do not raise exception)
            Types: bool

    RETURNS:
        None.

    RAISES:
        TeradataMlException - MODEL_ALREADY_EXISTS, MODEL_NOT_FOUND

    EXAMPLES:
        >>> meta_df = __check_if_model_exists("glm_out")
    """
    # Get the DataFrame for the Models metadata table.
    if created:
        current_user = __get_current_user()
        models_meta_df = DataFrame(in_schema(mac.MODEL_CATALOG_DB.value, mac.MODELS.value))
        models_meta_df = models_meta_df[models_meta_df[mac.CREATED_BY.value].str.lower() == current_user.lower()]
    elif accessible:
        models_meta_df = DataFrame(in_schema(mac.MODEL_CATALOG_DB.value, mac.MODELSX.value))
    else:
        models_meta_df = DataFrame(in_schema(mac.MODEL_CATALOG_DB.value, mac.MODELS.value))

    # Get the model created by current client user, using teradataml, with name as model_name.
    model_name = models_meta_df.Name

    # Filter Expression.
    if name is not None:
        models_meta_df = models_meta_df[model_name == name]

    num_rows = models_meta_df.shape[0]

    if raise_error_if_exists:
        if num_rows == 1 and name is not None:
            # If model with name 'name' already exists.
            raise TeradataMlException(Messages.get_message(MessageCodes.MODEL_ALREADY_EXISTS,
                                                           name),
                                      MessageCodes.MODEL_ALREADY_EXISTS)

    if raise_error_if_model_not_found:
        if num_rows == 0:
            if not created:
                # 'name' MODEL_NOT_FOUND
                raise TeradataMlException(Messages.get_message(MessageCodes.MODEL_NOT_FOUND,
                                                               name, ''),
                                          MessageCodes.MODEL_NOT_FOUND)
            else:
                # 'name' MODEL_NOT_FOUND or not created by user.
                raise TeradataMlException(Messages.get_message(MessageCodes.MODEL_NOT_FOUND,
                                                               name, ' or not created by user'),
                                          MessageCodes.MODEL_NOT_FOUND)

def __get_current_user(conn=None):
    """
    DESCRIPTION:
        Internal function to return the current Vantage user

    PARAMETERS:
        conn:
            Optional Argument,
            The underlying SQLAlchemy engine for the connection.
            Types: SQLAlchemy engine

    RETURNS:
        A string representing the name of the current database user.

    EXAMPLE:
        >>> current_user = __get_current_user()
    """
    if conn is None:
        conn = get_connection()

    return execute_sql('select user').fetchall()[0][0]


def __get_like_filter_expression_on_col(metaexpr, column_name, like):
    """
    DESCRIPTION:
        Internal function to get the filter expression on column_name containing string matching with like.
        (Case insensitive matching)

    PARAMETERS:
        metaexpr:
            Required Argument.
            Specifies the teradataml DataFrame meta data.
            Types: _MetaExpression

        column_name:
            Required Argument.
            Specifies the column name which is to be used in filter expression.
            Types: str

        like:
            Required Argument.
            Specifies the pattern to be matched in filter expression.
            Types: str

    RETURNS:
        _SQLColumnExpression object

    RAISES:
        None

    EXAMPLES:
        >>> filter_expression = __get_like_filter_expression_on_col(models_meta_df._metaexpr,
        ...                                                         mmc.MMT_COL_model_class.value,
        ...                                                         function_name)
    """
    return metaexpr._filter(0, 'like', [column_name], like = like, match_arg='i')


def __get_wrapper_class(model_engine, model_class):
    """
    DESCRIPTION:
        Internal function to the wrapper class that can be executed to create the instance of the
        model_class from engine specified in model_engine.

    PARAMETERS:
        model_engine:
            Required Argument.
            Model engine string 'ML Engine' or 'Advanced SQL Engine'.
            Types: str

        model_class:
            Required Argument.
            Model class string for the analytical function wrapper.
            Types: str

    RETURNS:
        A wrapper CLASS

    RAISES:
        ValueError - When invalid engine is passed.
        AttributeError - When model_class wrapper function, does is not from model_engine.

    EXAMPLES:
        >>> __get_wrapper_class("SQL Engine", "GLM")
    """
    if model_engine == mac.MODEL_ENGINE_ADVSQL.value:
        module_name = "teradataml.analytics.sqle"
    else:
        raise ValueError("Invalid Engine found in Model Cataloging table.")

    wrapper_module = importlib.import_module(module_name)

    return getattr(wrapper_module, model_class)


from teradataml.dataframe.dataframe import DataFrame, in_schema
