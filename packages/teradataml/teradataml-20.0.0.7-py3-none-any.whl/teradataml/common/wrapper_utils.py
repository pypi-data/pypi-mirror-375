"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pankajvinod.purandare@teradata.com, mounika.kotha@teradata.com
Secondary Owner:

This file implements the core utilities those will be used by the Teradata Vantage
Analytic Function wrappers.
"""

import re
import inspect

from teradataml.common.utils import UtilFuncs
from teradataml.common.formula import Formula
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.context.context import *
from teradataml.common.aed_utils import AedUtils
from teradataml.dataframe.dataframe_utils import DataFrameUtils
from teradataml.utils.validators import _Validators
from teradataml.common.constants import SourceType, AEDConstants, ModelCatalogingConstants
import teradataml.dataframe as tdmldf
from teradatasqlalchemy.types import INTEGER, SMALLINT, BIGINT, BYTEINT, FLOAT, NUMBER, VARCHAR, BYTE

FUNCTION_PREDICTION_TYPE_MAPPER = {
    # SQLE functions
    'teradataml.analytics.sqle.DecisionTreePredict.DecisionTreePredict':
        ModelCatalogingConstants.PREDICTION_TYPE_CLASSIFICATION.value,
    'teradataml.analytics.sqle.GLMPredict.GLMPredict':
        ModelCatalogingConstants.PREDICTION_TYPE_REGRESSION.value,
    'teradataml.analytics.sqle.NaiveBayesPredict.NaiveBayesPredict':
        ModelCatalogingConstants.PREDICTION_TYPE_CLASSIFICATION.value,
    'teradataml.analytics.sqle.NaiveBayesTextClassifierPredict.NaiveBayesTextClassifierPredict':
        ModelCatalogingConstants.PREDICTION_TYPE_CLASSIFICATION.value,
    'teradataml.analytics.sqle.SVMSparsePredict.SVMSparsePredict':
        ModelCatalogingConstants.PREDICTION_TYPE_CLASSIFICATION.value
}


class AnalyticsWrapperUtils:

    def _deparse_arg_name(self,var):
        """
        Get the variable name of the calling funtcion's passed argument.
        PARAMETERS:
           var - The argument whose name has to be retrieved

        RETURNS:
            arg_name

        EXAMPLES:
            awu._validate_permitted_values(family, familyPermittedValues)
            If the variable name family has to be retrieved rather than value of the variable, then call
            arg_name = self._deparse_arg_name(arg)

        NOTE:
            This function works only for the the calling function's calling function i.e two frames higher the
            calling function.

            If awu._validate_permitted_values(family, familyPermittedValues) is tha calling function and
            retrieve_name is called in _validate_permitted_values(arg) as arg_name = self._deparse_arg_name(arg) ,
            then name "family" will be retrieved .

        """
        callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
        for var_name, var_val in callers_local_vars :
            if var_val is var:
                return var_name

        return None

    def _validate_input_columns_not_empty(self, arg, arg_name):
        """
        Function to check whether argument is empty string or not.
        PARAMETERS:
            arg - Argument value (string) to be checked whether it is empty or
                  not.
        RAISES:
            Error if argument contains empty string

        EXAMPLES:
            awu._validate_input_columns_not_empty(arg)
        """
        # This is just a wrapper around a '_validate_input_columns_not_empty' in
        # _Validators. We are keeping this functions as is, so that we can avoid updates
        # in wrappers.
        return _Validators._validate_input_columns_not_empty(arg, arg_name)

    def _validate_permitted_values(self, arg, permitted_values_list, arg_name, includeNone=True):
        """
        Function to check the permitted values for the argument.UNSUPPORTED_DATATYPE

        PARAMETERS:
            arg - Argument value (string) to be checked against permitted values
                  from the list.
            permitted_values_list - A list containing permitted values for the
                                  argument.
            includeNone - Argument value (bool) which specifies whether 'None' can
                          be included as valid value.
                          Default: True

        RAISES:
            Error if argument is not present in the list

        EXAMPLES:
            permitted_values_list = ["LOGISTIC", "BINOMIAL", "POISSON", "GAUSSIAN", "GAMMA", "INVERSE_GAUSSIAN", "NEGATIVE_BINOMIAL"]
            arg = "LOGISTIC"
            awu._validate_permitted_values(arg, permitted_values_list, argument_name, False)
        """
        # This is just a wrapper around a '_validate_permitted_values' in
        # _Validators. We are keeping this functions as is, so that we can avoid updates
        # in wrappers.
        return _Validators._validate_permitted_values(arg=arg, permitted_values=permitted_values_list,
                                               arg_name=arg_name, includeNone=includeNone)

    def __getTypeAsStr(self, type_list):
        """
        Function to convert type to string.

        PARAMETERS:
            type_list - A tuple of types or a type to be converted to string.

        RAISES:
            None

        RETURNS:
            A list of strings representing types in type_list.

        EXAMPLES:
            self.__getTypeAsStr(type_list)
        """
        type_as_str = []
        if isinstance(type_list, tuple):
            for typ in type_list:
                type_as_str.append(typ.__name__)

        if isinstance(type_list, type):
            type_as_str.append(type_list.__name__)

        return type_as_str

    def _validate_argument_types(self, arg_list):
        """
        Method to verify that the input arguments are of valid data type except for
        argument of DataFrameType.

        PARAMETERS:
           arg_list - A list
                       The argument is expected to be a list of arguments,
                       expected types are mentioned as type or tuple.
                       argInfoMatrix = []
                       argInfoMatrix.append(["data", data, False, (DataFrame)])
                       argInfoMatrix.append(["centers", centers, True, (int, list)])
                       argInfoMatrix.append(["threshold", threshold, True, (float)])

                       Old wrapper matrices, will look like:
                       Expected types are mentioned as str. No list type is supported.
                       argInfoMatrix = []
                       argInfoMatrix.append(["data", data, False, "DataFrame"])
                       argInfoMatrix.append(["centers", centers, True, "int")])
                       argInfoMatrix.append(["threshold", threshold, True, "float"])

        RAISES:
            Error if arguments are not of valid datatype

        EXAMPLES:
            awu._validate_argument_types(arg_list)
        """
        args_matrix = []
        for args in arg_list:
            if args[3] != (tdmldf.dataframe.DataFrame) and args[3] != "formula":
                args_matrix.append(args)

        return _Validators._validate_function_arguments(args_matrix)

    def _validate_formula_notation(self, formula, data, arg_name):
        """
        _validate_formula_notation method validates input argument is a formula
        or not and returns instance of formula class which contains variable
        names and it's datatypes .
        PARAMETERS:
            formula - formula passed by the user
            data - dataframe object

        RETURNS:
            An instance of formula class.

        EXAMPLES:
            Say we have a formula like:
                y ~ a + b + c + d
                The formula has two parts LHS and RHS with a left-hand side y,
                and a right-hand side, a + b + c + d
                Sometimes you want a formula that has no left-hand side, and
                you can write that as ~ x1 + x2 or even x1 + x2. The RHS
                contains a list of terms separated by '+' .

            Create an instance of formula class as below:
                formulaObject = Formula(independentVars = formula,colTypes = colDesc)

                Using formulaObject we can get the variable names in the formula and
                it's datatypes.

                formula = "admitted ~ masters + gpa + stats + programming"
                awu._validate_formula_notation(formula, df)
        """
        if isinstance(formula, Formula):
            formula = str(formula)

        formula_object = Formula(data._metaexpr, formula, arg_name)
        return formula_object

    def _get_columns_by_type(self, formula_object, data, dtypes):
        """
        Function to generate and return list of column names which are of a
        specific type.

        PARAMETERS:
            formula_object -  Contains  formula object for the argument passed by the user
                             which is generated by _validateFormulaNotation.
            data - A data frame concerning the formula.
            type -  Type of columns to be needed.

        RETURNS:
            A list of column names.

        EXAMPLES:
            awu._get_columns_by_type(formula_object, df,"all")
            awu._get_columns_by_type(formula_object, df,"categorical")
            awu._get_columns_by_type(formula_object, df,"numerical")
        """

        columns_bytype = []
        common_util = UtilFuncs()

        if dtypes == "all":
            data_types = common_util._get_all_datatypes()
            return formula_object.get_all_columns(data_types)
        elif dtypes == "categorical":
            data_types = common_util._get_categorical_datatypes()
            return formula_object.get_categorical_columns(data_types)
        elif dtypes == "numerical":
            data_types = common_util._get_numeric_datatypes()
            return formula_object.get_numerical_columns(data_types)
        elif dtypes == "numerical-all":
            data_types = common_util._get_numeric_datatypes()
            return formula_object.get_numerical_columns(data_types, all=True)

        return columns_bytype

    def _teradata_on_clause_from_dataframe(self, tdframe, lazy = True):
        """
        Function to retrieve the type of data frame and
        corresponding reference to table/view/query.

        PARAMETERS:
            tdframe - dataframe object
            lazy - Parameter to determine the type SQLMR execution.

        RETURNS:
            A dictionary containing reference to dataframe and reference type.

        EXAMPLES:
            awu._teradata_on_clause_from_dataframe(data)
            awu._teradata_on_clause_from_dataframe(data,True)
        """
        aed_utils = AedUtils()
        table_ref = {}

        table_ref['ref_type'] = SourceType.TABLE.value
        if tdframe._table_name is not None:
            # If table_name is set for the input DataFrame, that means it has already been executed
            # and table name is set.
            table_ref['ref'] = tdframe._table_name
        elif aed_utils._aed_is_node_executed(tdframe._nodeid):
            # If node executed then we shall use the underlying table name/view name
            # in a query as it's input.
            # We are here that means node is executed but table name is not set, so
            # let's get the same from AED.
            table_ref['ref'] = aed_utils._aed_get_tablename(tdframe._nodeid)
        elif aed_utils._aed_get_node_query_type(tdframe._nodeid) in \
                [AEDConstants.AED_QUERY_NODE_TYPE_ML_QUERY_MULTI_OUTPUT.value,
                 AEDConstants.AED_QUERY_NODE_TYPE_REFERENCE.value]:
            # Let's get the input node type. If it's 'AED_QUERY_NODE_TYPE_ML_QUERY_MULTI_OUTPUT' type
            # then we must execute the node. This is because the table is created for such nodes and
            # before we use these we should use the table name instead of query.
            table_ref['ref'] = aed_utils._aed_get_tablename(tdframe._nodeid)
            if not lazy:
                DataFrameUtils._execute_node_return_db_object_name(tdframe._nodeid, tdframe._metaexpr)
        else:
            # We are here, that means node is not yet executed.
            # Now we shall get the queries for the input node and use
            # the same as the input to the SQL-MR queries.
            view_names, queries, node_query_types, node_ids = aed_utils._aed_get_exec_query(tdframe._nodeid)

            # Check if input has produced multiple queries or not.
            if len(queries) > 1:
                # For input nodes when we get multiple queries, we should use the last query as
                # input query to the analytical function.
                # This means query at 0th index is the input query, this will be used in
                # SQL-MR query.
                table_ref['ref'] = [view_names[0], queries[0], node_query_types[0], node_ids[0], lazy, True]
                # If analytical function is not lazy, then we must execute all the queries
                # except the last one. Else no need to execute anything.
                if not lazy:
                    # Execute all queries in input except the last one.
                    # To do so we just have to execute the node at index 1.
                    for index in range(len(queries) - 1, 0, -1):
                        DataFrameUtils._execute_node_return_db_object_name(node_ids[index])
            else:
                table_ref['ref'] = [view_names[0], queries[0], node_query_types[0], node_ids[0], lazy, False]
            table_ref['ref_type'] = SourceType.QUERY.value

        #TODO: Add support for nested level query as in R.
        return table_ref

    def _validate_input_table_datatype(self, data, arg_name, reference_function_name=None):
        """
        Method to verify that the input table parameters of type DataFrame.

        PARAMETERS:
           data - Input table argument.
           reference_function_name - Reference class for the data.

        RAISES:
            Error if table type is not of DataFrame  or provided reference function.

        EXAMPLES:
            awu._validate_input_table_datatype(data)
        """
        if reference_function_name is not None:
            types = (tdmldf.dataframe.DataFrame, reference_function_name)
        else:
            types = (tdmldf.dataframe.DataFrame)

        if data is None:
            return True

        return _Validators._validate_function_arguments([[arg_name, data, False, types]])

    def _validate_missing_required_arguments(self,arg_list):
        """
        Method to check whether the required arguments passed to the function are missing
        or not. Only wrapper's use this function.

        PARAMETERS:
           arg_list - A list
                       The argument is expected to be a list of arguments

        RAISES:
            If any arguments are missing exception raised with missing arguments which are
            required.

        EXAMPLES:
                       An example input matrix will be:
                       arg_info_matrix = []
                       arg_info_matrix.append(["data", data, False, DataFrame])
                       arg_info_matrix.append(["centers", centers, True, int])
                       arg_info_matrix.append(["threshold", threshold, True, "float"])
                       awu = AnalyticsWrapperUtils()
                       awu._validate_missing_required_arguments(arg_info_matrix)

        """
        # This is just a wrapper around a '_validate_missing_required_arguments' in
        # _Validators. We are keeping this functions as is, so that we can avoid updates
        # in wrappers.
        return _Validators._validate_missing_required_arguments(arg_list=arg_list)

    def _create_data_set_object(self, df_input, source_type = "node", database_name = None, metaexpr = None):
        """
        This function helps to create dataframe object.

        PARAMETERS:
           df_input - Name of the table or query or node id.
           source_type - Type of dataframe object to be created.
           database_name - Database name (For future purpose).
           metaexpr - Parent metadata (Sqlalchemy Table Object).

        RETURNS:
             A dataset object of type dataframe.

        EXAMPLES:
            awu = AnalyticsWrapperUtils()
            awu._create_data_set_object("admissions_train", "table")
            awu._create_data_set_object("select * from admissions_train", "query")
            awu._create_data_set_object(1234, metaexpr)
        """
        if source_type == "node" and metaexpr is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.MISSING_ARGS, "'metaexpr' to create dataframe from node."),
                                      MessageCodes.MISSING_ARGS)

        if source_type == "query":
            return tdmldf.dataframe.DataFrame.from_query(df_input)
        elif source_type == "table":
            if database_name is not None:
                return tdmldf.dataframe.DataFrame(tdmldf.dataframe.in_schema(database_name, df_input))
            return tdmldf.dataframe.DataFrame.from_table(df_input)
        else:
            return tdmldf.dataframe.DataFrame._from_node(df_input, metaexpr)

    def _retrieve_column_info(self, df_input, parameter = None, columns = None):
        """
        Function helps to return column names and it's types for the dataframe.

        When all parameter's are None, it returns all column names and their types.

        When parameter is given, parameter is used as input columns and it's
        corresponding types are returned.

        When column is given, all column names mentioned in columns are returned
        along with their types.

        PARAMETERS:
            df_input - teradataml dataframe containing columns mentioned
                        in parameter or columns.
            parameter - A parameter passed from a wrapper script containing
                        a list of column names.
            columns - List of column names, if any specific columns from
                        input dataframe or parameter are to be selected.

        RAISES:
            N/A

        RETURNS:
            Column names and corresponding column types in zipped format.

        EXAMPLES:
            awu = AnalyticsWrapperUtils()
            # Retrieve column information for all columns in 'data' dataframe.
            awu._retrieve_column_info(data)
            # Retrieve column information for all of columns in 'accummulate' from 'data' dataframe.
            awu._retrieve_column_info(data, accummulate)
            # Retrieve column information for subset of columns in 'accummulate' from 'data' dataframe.
            awu._retrieve_column_info(data, accummulate, columns_subset)
        """
        col_names = []
        col_types = []
        if df_input is None:
            return zip(col_names, col_types)

        metaexpr = df_input._metaexpr
        
        if parameter is not None and isinstance(parameter, str):
            parameter = [parameter]
        
        if columns is not None and isinstance(columns, str):
            columns = [columns]
 
        if parameter is None and columns is None:
            # Retrieve all Column names & Types from a dataframe _metaexpr
            col_names = [c.name for c in metaexpr.c]
            col_types = [c.type for c in metaexpr.c]

            return zip(col_names, col_types)

        if parameter is not None and columns is None:
            # Retrieve all Column names & Types from a dataframe _metaexpr
            for c in metaexpr.c:
                if c.name.lower() in [col.lower() for col in parameter]:
                    col_names.append(c.name)
                    col_types.append(c.type)

            return zip(col_names, col_types)

        if parameter is not None and columns is not None:
            # Retrieve all Column names & Types from a dataframe _metaexpr
            for c in metaexpr.c:
                if c.name.lower() in [col.lower() for col in parameter] and c.name.lower() in [col.lower() for col in columns]:
                    col_names.append(c.name)
                    col_types.append(c.type)

            return zip(col_names, col_types)

        if parameter is None and columns is not None:
            # Retrieve all Column names & Types from a dataframe _metaexpr
            for c in metaexpr.c:
                if c.name.lower() in [col.lower() for col in columns]:
                    col_names.append(c.name)
                    col_types.append(c.type)

            return zip(col_names, col_types)

    def _get_json_to_sqlalchemy_mapping(self, key):
        """
            This is an internal function used to return a dictionary of all SQLAlchemy Type Mappings.
            It contains mappings from data type from JSON to SQLAlchemyTypes

            PARAMETERS:
                key - Json data type string for which SQLAlchemy Type is needed

            RETURNS:
                dictionary { json_type : SQLAlchemy Type}

            RAISES:
                N/A

            EXAMPLES:
                _get_all_sqlalchemy_mappings()

            """
        # TODO:: Add this to a new class for DataType Mapping and refactor the code elsewhere.
        json_to_sqlalchemy_types_map = {'integer': INTEGER, 'bigint': BIGINT, 'varchar': VARCHAR,
                                        'double precision': FLOAT, 'boolean': BYTEINT, 'real': FLOAT,
                                        'bytea': BYTE, 'float': FLOAT}

        return json_to_sqlalchemy_types_map.get(key.lower())

    def _validate_dataframe_has_argument_columns(self, columns, column_arg, data, data_arg,
                                                 isPartitionArg=False):
        """
        Function to check whether column names in columns are present in given dataframe or not.
        This function is used currently only for Analytics wrappers.

        PARAMETERS:
            columns - Column name (a string) or list of column names.
            column_arg - Name of the argument.
            data - teradataml DataFrame to check against for column existence.
            data_arg - DataFrame argument name in wrapper.
            isPartitionArg - A bool argument notifying, whether argument being validate is Partition argument or not.

        RAISES:
            TeradataMlException - TDMLDF_COLUMN_IN_ARG_NOT_FOUND column(s) does not exist in a dataframe.

        EXAMPLES:
            awu._validate_dataframe_has_argument_columns(self.data_sequence_column, "data_sequence_column", self.data, "data")
            awu._validate_dataframe_has_argument_columns(self.data_partition_column, "data_sequence_column", self.data, "data", true)
        """
        # This is just a wrapper around a '_validate_dataframe_has_argument_columns' in
        # _Validators. We are keeping this functions as is, so that we can avoid updates
        # in wrappers.
        _Validators._validate_dataframe_has_argument_columns(columns=columns, column_arg=column_arg,
                                                             data=data, data_arg=data_arg,
                                                             is_partition_arg=isPartitionArg)

    def _is_default_or_not(self, arg_name, arg_default_value):
        """
        Function to check if an argument's value is same as default value or not.
        If argument's value is same as default value, then return False, else True.
        
        PARAMETERS:
            arg_name - Name of the argument.
            arg_default_value - Default value of the argument.
            
        RETURNS:
                True - If argument value is different from default value.
                False - If argument value is same as default value.
            
        EXAMPLES:
            awu._check_arg_has_any_or_one(self.data_partition_column, "ANY")
        """
        if ((isinstance(arg_name,list) and len(arg_name) > 0 ) or (isinstance(arg_name,str) and arg_name != arg_default_value)):
            return True
        else:
            return False

    def __get_input_dependent_prediction_type(self, function_obj, input_data):
        """
        Function to get the prediction type of the analytic function.

        PARAMETERS:
            function_obj:
                Required Argument.
                Specifies the instance of the analytics function to get the prediction type for.
                Type: teradataml mle or sqle analytic function object.

            input_data:
                Required Argument.
                Specifies the input to the analytic function which the formula argument to the function
                points to.
                Types: teradataml DataFrame.

        RETURNS:
            A String representing the one of the following prediction types:
            * REGRESSION
            * CLASSIFICATION
            * CLUSTERING
            * OTHER

        EXAMPLES:
            # In the example here, we assume that we have created an object of the DecisionForest function, 'dfout',
            # where 'data' was the input DataFrame the function:
            prediction_type = self.__get_input_dependent_prediction_type(dfout, data)
        """
        # This list serves as a quick lookup.
        function_name_with_module = '{}.{}'.format(function_obj.__class__.__module__, function_obj.__class__.__name__)


    def _get_function_prediction_type(self, function_obj, input_data=None):
        """
        Function to get the prediction type of the analytic function when it is dependent on its input.

        PARAMETERS:
            function_obj:
                Required Argument.
                Specifies the instance of the analytics function to get the prediction type for.
                Type: teradataml mle or sqle analytic function object.

            input_data:
                Optional Argument. Required when Prediction Type is dependent on inputs to the function.
                Specifies the input to the analytic function which the formula argument to the function
                points to.
                Types: teradataml DataFrame.

        RETURNS:
            A String representing the one of the following prediction types:
            * REGRESSION
            * CLASSIFICATION
            * CLUSTERING
            * OTHER

        EXAMPLES:
            # In the example here, we assume that we have created an object of the GLM function, 'glmout1',
            # where 'data' was the input DataFrame the function:
            prediction_type = awu._get_function_prediction_type(glmout1, data)
        """
        # Mapper to map function to prediction type
        function_name_with_module = '{}.{}'.format(function_obj.__class__.__module__,
                                                   function_obj.__class__.__name__)
        try:
            return FUNCTION_PREDICTION_TYPE_MAPPER[function_name_with_module]
        except KeyError:
            return self.__get_input_dependent_prediction_type(function_obj, input_data)