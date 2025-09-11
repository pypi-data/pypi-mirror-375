#########################################################################
# Unpublished work.                                                     #
# Copyright (c) 2021 by Teradata Corporation. All rights reserved.      #
# TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET                    #
#                                                                       #
# Primary Owner: pankajvinod.purandare@teradata.com                     #
# Secondary Owner:                                                      #
#                                                                       #
# This file implements class creates a SQL-MR object, which can be      #
# used to generate SQL-MR/Analytical query in FFE syntax for Teradata.  #
#########################################################################

import os
from collections import OrderedDict
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import _get_function_mappings
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.exceptions import TeradataMlException
from teradataml.dataframe.dataframe_utils import DataFrameUtils
from teradataml.options.configure import configure
from teradataml.common.constants import TeradataReservedKeywords

# Current directory is analytics folder.
teradataml_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_folder = os.path.join(teradataml_folder, "config")

class AnalyticQueryGenerator:
    """
    This class creates a SQL-MR object, which can be used to generate
    SQL-MR/Analytical query in FFE syntax for Teradata.
    """

    def __init__(self, function_name, func_input_arg_sql_names, func_input_table_view_query, func_input_dataframe_type,
                 func_input_distribution, func_input_partition_by_cols, func_input_order_by_cols,
                 func_other_arg_sql_names, func_other_args_values, func_other_arg_json_datatypes,
                 func_output_args_sql_names, func_output_args_values, func_type="FFE",
                 engine="ENGINE_ML", db_name=None, volatile_output=False, skip_config_lookup=False,
                 func_input_local_order=None):
        """
        AnalyticalQueryGenerator constructor, to create a map-reduce object, for
        SQL-MR/Analytical query generation.

        PARAMETERS:
            function_name:
                Required Argument.
                Specifies the name of the function.

            func_input_arg_sql_names:
                Required Argument.
                Specifies the list of input SQL Argument names.

            func_input_table_view_query:
                Required Argument.
                Specifies the list of input argument values, with
                respect to 'func_input_arg_sql_names' which contains
                table_name or SQL (Select query).

            func_input_dataframe_type:
                Required Argument.
                Specifies the list of dataframe types for each input.
                Values can be "TABLE" or "QUERY".

            func_input_distribution:
                Required Argument.
                Specifies the list containing distributions for each
                input. Values can be "FACT", "DIMENSION", "NONE".

            func_input_partition_by cols:
                Required Argument.
                Specifes the list containing partition columns for
                each input, if distribution is FACT.

            func_input_order_by_cols:
                Required Argument.
                Specifies the list of values, for each input, to be
                used order by clause.

            func_other_arg_sql_names:
                Required Argument.
                Specifies the list of other function arguments SQL
                name.

            func_other_args_values:
                Required Argument.
                Specifies the list of other function argument values,
                with respect to each member in 'func_other_arg_sql_names'.

            func_other_arg_json_datatypes:
                Required Argument.
                Specifies the list of JSON datatypes for each member in
                'func_other_arg_sql_names'.

            func_output_args_sql_names:
                Required Argument.
                Specifies the list of output SQL argument names.

            func_output_args_values:
                Required Argument.
                Specifies the list of output table names for each
                output table argument in 'func_output_args_sql_names'.

            func_type:
                Required Argument. Fixed value 'FFE'.
                Kept for future purpose, to generate different syntaxes.

            engine:
                Optional Argument.
                Specifies the type of engine.
                Default Value : ENGINE_ML
                Permitted Values : ENGINE_ML, ENGINE_SQL

            db_name:
                Optional Argument.
                Specifies the install location of function. This argument will be primarily
                used for BYOM functions.
                Default Value: None

            volatile_output:
                Optional Argument.
                Specifies the table to create is Volatile or not. When set to True,
                volatile table is created, otherwise permanent table is created.
                Default Value: False
                Types: bool

            skip_config_lookup:
                Optional Argument.
                Specifies whether the Query generater should look at config files before
                generating the SQL Query or not. If set to False, Query generator validates
                whether function is supported for the corresponding vantage version by
                looking at the config file. Otherwise, the QueryGenerator generates the
                SQL without validating it.
                Default Value: False

        RETURNS:
            AnalyticalQueryGenerator object. (We can call this as map-reduce object)

        RAISES:

        EXAMPLES:
            aqg_obj = AnalyticQueryGenerator(self.function_name, self.input_sql_args,
                                             self.input_table_qry, self.input_df_type,
                                             self.input_distribution, self.input_partition_columns,
                                             self.input_order_columns, self.other_sql_args,
                                             self.other_args_val, [], self.output_sql_args,
                                             self.output_args_val, engine="ENGINE_SQL",
                                             db_name="mldb")
        """
        self.__engine = engine
        self.__function_name = function_name
        if not skip_config_lookup:
            self.__function_name = self._get_alias_name_for_function(function_name)
        self.__db_name = db_name
        if self.__db_name:
            self.__function_name = "\"{}\".{}".format(self.__db_name,
                                                      self.__function_name)
        self.__func_input_arg_sql_names = func_input_arg_sql_names
        self.__func_input_table_view_query = func_input_table_view_query
        self.__func_input_dataframe_type = func_input_dataframe_type
        self.__func_input_distribution = func_input_distribution
        self.__func_input_partition_by_cols = func_input_partition_by_cols
        self.__func_input_order_by_cols = func_input_order_by_cols
        self.__func_other_arg_sql_names = func_other_arg_sql_names
        self.__func_other_args_values = func_other_args_values
        self.__func_other_arg_json_datatypes = func_other_arg_json_datatypes
        self.__func_output_args_sql_names = func_output_args_sql_names
        self.__func_output_args_values = func_output_args_values
        self.__func_input_local_order = func_input_local_order
        self.__func_type = func_type
        self.__SELECT_STMT_FMT = "SELECT * FROM {} as sqlmr"
        self.__QUERY_SIZE = self.__get_string_size(self.__SELECT_STMT_FMT) + 20
        self.__input_arg_clause_lengths = []
        self._multi_query_input_nodes = []
        self.__volatile_output = volatile_output

    def __process_for_teradata_keyword(self, keyword):
        """
        Internal function to process Teradata Reserved keywords.
        If keyword is in list of Teradata Reserved keywords, then it'll be quoted in double quotes "keyword".

        PARAMETERS:
            keyword - A string to check whether it belongs to Teradata Reserved Keywords or not.

        RETURNS:
            A quoted string, if keyword is one of the Teradata Reserved Keyword, else str as is.

        RAISES:

        EXAMPLES:
            # Passing non-reserved returns "xyz" as is.
            keyword = self.__process_for_teradata_keyword("xyz")
            print(keyword)
            # Passing reserved str returns double-quoted str, i.e., "\"threshold\"".
            keyword = self.__process_for_teradata_keyword("threshold")
            print(keyword)

        """
        if keyword.upper() in TeradataReservedKeywords.TERADATA_RESERVED_WORDS.value:
            return UtilFuncs._teradata_quote_arg(keyword, "\"", False)
        else:
            return keyword

    def __generate_sqlmr_func_other_arg_sql(self):
        """
        Private function to generate a SQL clause for other function arguments.
        For Example,
            Step("False")
            Family("BINOMIAL")

        PARAMETERS:

        RETURNS:
            SQL string for other function arguments, as shown in example here.

        RAISES:

        EXAMPLES:
            __func_other_arg_sql_names = ["Step", "Family"]
            __func_other_args_values = ["False", "BINOMIAL"]
            other_arg_sql = self.__generate_sqlmr_func_other_arg_sql()
            # Output is as shown in example in description.

        """
        args_sql_str = ""
        for index in range(len(self.__func_other_arg_sql_names)):
            args_sql_str = "{0}\n\t{1}({2})".format(args_sql_str,
                                                    self.__process_for_teradata_keyword(
                                                        self.__func_other_arg_sql_names[index]),
                                                    self.__func_other_args_values[index])

        self.__QUERY_SIZE = self.__QUERY_SIZE + self.__get_string_size(args_sql_str)
        return args_sql_str

    def __generate_sqlmr_input_arg_sql(self, table_ref, table_ref_type, alias=None):
        """
        Private function to generate a ON clause for input function arguments.
        For Example,
            ON table_name AS InputTable
            ON (select * from table) AS InputTable

        PARAMETERS:
            table_ref - Table name or query, to be used as input.
            table_ref_type - Type of data frame.
            alias - Alias to be used for input.

        RETURNS:
            ON clause SQL string for input function arguments, as shown in example here.

        RAISES:
            TODO

        EXAMPLES:
            other_arg_sql = self.__generate_sqlmr_input_arg_sql("table_name", "TABLE", "InputTable")
            # Output is as shown in example in description.

        """
        returnSql = "\n\tON"
        if table_ref_type == "TABLE":
            returnSql = "{0} {1}".format(returnSql, table_ref)
        elif table_ref_type == "QUERY":
            returnSql = "{0} ({1})".format(returnSql, table_ref)
        else:
            #TODO raise # Error
            ""

        if alias is not None:
            returnSql = "{0} AS {1}".format(returnSql, self.__process_for_teradata_keyword(alias))

        return returnSql

    def __generate_sqlmr_output_arg_sql(self):
        """
        Private function to generate a SQL clause for output function arguments.
        For Example,
            OUT TABLE OutputTable("out_table_1")
            OUT TABLE CoefficientsTable("out_table_2")

        PARAMETERS:

        RETURNS:
            SQL string for output function arguments, as shown in example here.

        RAISES:

        EXAMPLES:
            __func_output_args_sql_names = ["OutputTable", "CoefficientsTable"]
            __func_output_args_values = ["out_table_1", "out_table_2"]
            other_arg_sql = self.__generate_sqlmr_output_arg_sql()
            # Output is as shown in example in description.

        """
        args_sql_str = ""
        volatile_table_clause = " VOLATILE" if self.__volatile_output else ""
        for index in range(len(self.__func_output_args_sql_names)):
            if self.__func_output_args_values[index] is not None:
                args_sql_str = "{0}\n\tOUT{3} TABLE {1}({2})".format(args_sql_str,
                                                                  self.__process_for_teradata_keyword(
                                                                      self.__func_output_args_sql_names[index]),
                                                                  self.__func_output_args_values[index],
                                                                  volatile_table_clause)

        self.__QUERY_SIZE = self.__QUERY_SIZE + self.__get_string_size(args_sql_str)
        return args_sql_str

    def _gen_sqlmr_select_stmt_sql(self):
        """
        Protected function to generate complete analytical query.
        For Example,
            SELECT * FROM GLM(
                input_arguments_clause
                output_arguments_clause
                USING
                other_arguments_clause
            ) as sqlmr

        PARAMETERS:

        RETURNS:
            A SQL-MR/Analytical query, as shown in example here.

        RAISES:

        EXAMPLES:
            aqg_obj = AnalyticQueryGenerator(self.function_name, self.input_sql_args, self.input_table_qry,
                                         self.input_df_type,
                                         self.input_distribution, self.input_partition_columns,
                                         self.input_order_columns,
                                         self.other_sql_args, self.other_args_val, [], self.output_sql_args,
                                         self.output_args_val)
            anly_query = aqg_obj._gen_sqlmr_select_stmt_sql()
            # Output is as shown in example in description.

        """
        return self.__SELECT_STMT_FMT.format(self._gen_sqlmr_invocation_sql())

    def _gen_sqlmr_invocation_sql(self):
        """
        Protected function to generate a part of analytical query, to be used for map-reduce functions.
        For Example,
            GLM(
                input_arguments_clause
                output_arguments_clause
                USING
                other_arguments_clause
            )

        PARAMETERS:

        RETURNS:
            A SQL-MR/Analytical query, as shown in example here.

        RAISES:

        EXAMPLES:
            aqg_obj = AnalyticQueryGenerator(self.function_name, self.input_sql_args, self.input_table_qry,
                                         self.input_df_type,
                                         self.input_distribution, self.input_partition_columns,
                                         self.input_order_columns,
                                         self.other_sql_args, self.other_args_val, [], self.output_sql_args,
                                         self.output_args_val)
            anly_query = aqg_obj._gen_sqlmr_invocation_sql()
            # Output is as shown in example in description.

        """
        self.__OUTPUT_ARG_CLAUSE = self.__generate_sqlmr_output_arg_sql()
        self.__OTHER_ARG_CLAUSE = self.__generate_sqlmr_func_other_arg_sql()
        self.__INPUT_ARG_CLAUSE = self.__single_complete_table_ref_clause()
        invocation_sql = "{0}({1}{2}".format(self.__function_name, self.__INPUT_ARG_CLAUSE, self.__OUTPUT_ARG_CLAUSE)

        if len(self.__func_other_arg_sql_names) != 0:
            invocation_sql = "{0}\n\tUSING{1}".format(invocation_sql, self.__OTHER_ARG_CLAUSE)

        invocation_sql = invocation_sql + "\n)"

        return invocation_sql

    def __single_complete_table_ref_clause(self):
        """
        Private function to generate complete ON clause for input function arguments, including
        partition by and order by clause, if any.
        For Example,
            ON table_name AS InputTable1 Partition By col1 Order By col2
            ON (select * from table) AS InputTable2 DIMENSION

        PARAMETERS:

        RETURNS:
            Complete input argument clause, SQL string for input function arguments, as shown in example here.

        RAISES:

        EXAMPLES:
            __func_input_arg_sql_names = ["InputTable1", "InputTable2"]
            __func_input_table_view_query = ["table_name", "select * from table"]
            __func_input_dataframe_type = ["TABLE", "QUERY"]
            __func_input_distribution = ["FACT", "DIMENSION"]
            __func_input_partition_by_cols = ["col1", "NA_character_"]
            __func_input_order_by_cols = ["col2", "NA_character_"]
            other_arg_sql = self.__single_complete_table_ref_clause()
            # Output is as shown in example in description.

        """
        on_clause_dict = OrderedDict()
        args_sql_str = []

        # Let's iterate over the input arguments to the analytic functions.
        # Gather all the information provided by the wrapper.
        for index in range(len(self.__func_input_arg_sql_names)):
            # Get table reference. This contains following information:
            #   table name or view name OR
            #   A list of [view_name, query, node_query_type, node_id] gathered from
            #   'aed_exec_query_output' for the input node.
            table_ref = self.__func_input_table_view_query[index]
            # Get the table reference type, which is, either "TABLE" or "QUERY"
            table_ref_type = self.__func_input_dataframe_type[index]
            # Input argument alias
            alias = self.__func_input_arg_sql_names[index]
            # Partition information
            distribution = self.__func_input_distribution[index]
            partition_col = self.__func_input_partition_by_cols[index]
            # Order clause information
            order_col = self.__func_input_order_by_cols[index]
            # Order by type information - local order by or order by
            local_order_by_type = self.__func_input_local_order[index] if self.__func_input_local_order else False
            # Get the Partition clause for the input argument.
            partition_clause = self.__gen_sqlmr_input_partition_clause(distribution, partition_col)
            # Get the Order clause for the input argument.
            order_clause = self.__gen_sqlmr_input_order_clause(order_col, local_order_by_type)

            if table_ref_type == "TABLE":
                # If table reference type is "TABLE", then let's use the table name in the query.
                on_clause = self.__generate_sqlmr_input_arg_sql(table_ref, table_ref_type, alias)
                on_clause_str = "{0}{1}{2}".format(on_clause, partition_clause, order_clause)
                args_sql_str.append(on_clause_str)
                # Update the length of the PARTITION clause.
                self.__QUERY_SIZE = self.__QUERY_SIZE + self.__get_string_size(on_clause_str)
            else:
                # Store the input argument information for the inputs, which will use query as input.
                on_clause_dict[index] = {}
                on_clause_dict[index]["PARTITION_CLAUSE"] = partition_clause
                on_clause_dict[index]["ORDER_CLAUSE"] = order_clause
                on_clause_dict[index]["ON_TABLE"] = self.__generate_sqlmr_input_arg_sql(table_ref[0], "TABLE", alias)
                on_clause_dict[index]["ON_QRY"] = self.__generate_sqlmr_input_arg_sql(table_ref[1], "QUERY", alias)
                on_clause_dict[index]["QRY_TYPE"] = table_ref[2]
                on_clause_dict[index]["NODEID"] = table_ref[3]
                on_clause_dict[index]["LAZY"] = table_ref[4]
                # If input node results in returning multiple queries save that input node
                # in '_multi_query_input_nodes' list.
                if table_ref[5]:
                    self._multi_query_input_nodes.append(table_ref[3])

        # Process OrderedDict to generate input argument clause.
        for key in on_clause_dict.keys():
            # 31000 is maximum query length supported in ON clause
            if self.__QUERY_SIZE + self.__get_string_size(on_clause_dict[key]["ON_QRY"]) <= 31000:
                on_clause_str = "{0}{1}{2}".format(on_clause_dict[key]["ON_QRY"],
                                                   on_clause_dict[key]["PARTITION_CLAUSE"],
                                                   on_clause_dict[key]["ORDER_CLAUSE"])
            else:
                # We are here means query maximum size will be exceeded here.
                # So let's add the input node to multi-query input node list, as
                # we would like execute this node as well as part of the execution.
                # Add it in the list, if we have not done it already.
                if on_clause_dict[key]["NODEID"] not in self._multi_query_input_nodes:
                    self._multi_query_input_nodes.append(on_clause_dict[key]["NODEID"])

                # Use the table name/view name in the on clause.
                on_clause_str = "{0}{1}{2}".format(on_clause_dict[key]["ON_TABLE"],
                                                   on_clause_dict[key]["PARTITION_CLAUSE"],
                                                   on_clause_dict[key]["ORDER_CLAUSE"])

                # Execute input node here, if function is not lazy.
                if not on_clause_dict[key]["LAZY"]:
                    DataFrameUtils._execute_node_return_db_object_name(on_clause_dict[key]["NODEID"])

            args_sql_str.insert(key, on_clause_str)
            # Add the length of the ON clause.
            self.__QUERY_SIZE = self.__QUERY_SIZE + self.__get_string_size(on_clause_str)

        return " ".join(args_sql_str)

    def __gen_sqlmr_input_order_clause(self, column_order, local_order_by_type):
        """
        Private function to generate complete order by clause for input function arguments.
        For Example,
            Order By col2

        PARAMETERS:
            column_order - Column to be used in ORDER BY clause. If this is "NA_character_"
                            no ORDER BY clause is generated.

            local_order_by_type - Specifies whether to generate LOCAL ORDER BY or not. When
                                  set to True, function generates LOCAL ORDER BY, otherwise
                                  function generates ORDER BY clause.

        RETURNS:
            Order By clause, as shown in example here.

        RAISES:

        EXAMPLES:
            other_arg_sql = self.__gen_sqlmr_input_order_clause("col2")
            # Output is as shown in example in description.

        """
        if column_order == "NA_character_" or column_order is None:
          return ""
        local_order = "LOCAL" if local_order_by_type else ""
        args_sql_str = "\n\t{} ORDER BY {}".format(local_order, column_order)

        # Get the length of the ORDER clause.
        self.__QUERY_SIZE = self.__QUERY_SIZE + self.__get_string_size(args_sql_str)
        return args_sql_str

    def __gen_sqlmr_input_partition_clause(self, distribution, column):
        """
        Private function to generate PARTITION BY or DIMENSION clause for input function arguments.
        For Example,
            Partition By col1
            DIMENSION

        PARAMETERS:
            distribution - Type of clause to be generated. Values accepted here are: FACT, DIMENSION, NONE
            column - Column to be used in PARTITION BY clause, when distribution is "FACT"

        RETURNS:
            Partition clause, based on the type of distribution:
                When "FACT" - PARTITION BY clause is generated.
                When "DIMENSION" - DIMENSION cluase is generated.
                When "NONE" - No clause is generated, an empty string is returned.

        RAISES:
            TODO

        EXAMPLES:
            other_arg_sql = self.__gen_sqlmr_input_partition_clause("FACT", "col1")
            # Output is as shown in example in description.

        """
        if distribution == "FACT" and column is not None:
            args_sql_str = "\n\tPARTITION BY {0}".format(column)
        elif distribution == "DIMENSION":
            args_sql_str = "\n\tDIMENSION"
        elif distribution == "HASH" and column is not None:
            args_sql_str = "\n\t HASH BY {0}".format(column)
        elif distribution == "NONE":
            return ""
        else:
            return ""
            # TODO raise error "invalid distribution type"

        # Get the length of the PARTITION clause.
        self.__QUERY_SIZE = self.__QUERY_SIZE + self.__get_string_size(args_sql_str)
        return args_sql_str

    def _get_alias_name_for_function(self, function_name):
        """
        Function to return the alias name mapped to the actual
        analytic function.

        PARAMETERS:
            function_name:
                Required Argument.
                Specifies the name of the function for which alias
                name should be returned.

        RETURNS:
            Function alias name for the given function_name.

        RAISES:
            TeradataMLException

        EXAMPLES:
            aqgObj._get_alias_name_for_function("GLM")
        """
        engine_name = UtilFuncs._get_engine_name(self.__engine)

        # Get function mappings which are already loaded during create_context or set_context.
        function_mappings = _get_function_mappings()

        try:
            return function_mappings[configure.vantage_version][engine_name][function_name.lower()]
        except KeyError as ke:
            if str(ke) == "'{}'".format(function_name.lower()):
                raise TeradataMlException(Messages.get_message(
                    MessageCodes.FUNCTION_NOT_SUPPORTED).format(configure.vantage_version),
                                          MessageCodes.FUNCTION_NOT_SUPPORTED) from ke
            else:
                raise
        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.CONFIG_ALIAS_ANLY_FUNC_NOT_FOUND).format(function_name, config_folder),
                                      MessageCodes.CONFIG_ALIAS_ANLY_FUNC_NOT_FOUND) from err

    def __get_string_size(self, string):
        return len(string.encode("utf8"))

class UAFQueryGenerator:
    def __init__(self, function_name, func_input_args, func_input_filter_expr_args, func_other_args,
                 func_output_args, func_input_fmt_args=None, func_output_fmt_args=None,
                 volatile_output=False, ctas=False):
        """
        UAFQueryGenerator constructor, for UAF query generation.

        PARAMETERS:
            function_name:
                Required Argument.
                Specifies the name of the function.

            func_input_args:
                Required Argument.
                Specifies the list of input arguments passed by the user.
                [data1, data2, data3]
                Types: list of TDSeries or list of TDMarix or list of TDGenSeries

            func_input_filter_expr_args:
                Required Argument.
                Specifies the list of filter expressions related to corresponding input argument.
                Types: list of ColumnExpressions

            func_other_args:
                Required Argument.
                Specifies the dict containing information about other arguments.
                dict contains a key value pair where:
                    key is a SQL argument name.
                    value is can be of two types:
                        An actual value passed by the user to be passed along to the function.
                        OR
                        A dict of key value pair, similar to a dict passed to the argument.

                For example,
                    In SQL:
                    NONSEASONAL()
                    FUNC_PARAMS(NONSEASONAL(MODEL_ORDER(2,0,1),ARG1(value1),
                                            NestParam(MODEL_ORDER1(2,0,1),ARG1(value1)
                                            ),
                                CONSTANT(0), ALGORITHM(MLE), COEFF_STATS(1),
                                FIT_METRICS(1), RESIDUALS(1), FIT_PERCENTAGE(80) )
                    So dict passed here is:
                    dict = {
                                "NONSEASONAL": {
                                                    "MODEL_ORDER": "2, 0, 1",
                                                    "ARG1": "Value1",
                                                    "NestParam": {
                                                                    "MODEL_ORDER": "2, 0, 1",
                                                                    "ARG1": "Value1",
                                                                 }
                                                },
                                "CONSTANT": 0,
                                "ALGORITHM": "MLE",
                                "COEFF_STATS": 1,
                                "FIT_METRICS": 1,
                                "RESIDUALS": 1,
                                "FIT_PERCENTAGE": 80
                            }
                Types: dict

            func_output_args:
                Required Argument.
                Specifies the name of the output table to be created or used in a UAF function query.
                Types: str

            func_input_fmt_args:
                Required Argument.
                Specifies the dict containing information about INPUT_FMT clause in UAF Query.
                dict contains a key value pair where:
                    key is a SQL argument name.
                    value can be of two types:
                        An actual value passed by the user to be passed along to the function.
                        OR
                        A dict of key value pair, similar to a dict passed to the arguments.
                Types: dict.

            func_output_fmt_args:
                Required Argument.
                Specifies the dict containing information about OUTPUT_FMT clause in UAF Query.
                dict contains a key value pair where:
                    key is a SQL argument name.
                    value can be of two types:
                        An actual value passed by the user to be passed along to the function.
                        OR
                        A dict of key value pair, similar to a dict passed to the argument.
                Types: dict.

            volatile_output:
                Optional Argument.
                Specifies the table to create is Volatile or not. When set to True,
                volatile table is created, otherwise permanent table is created.
                Default Value: False
                Types: bool

            ctas:
                Optional Argument.
                Specifies whether to create output table using CREATE TABLE or using
                EXECUTE FUNCTION. When set to True, output table is created using CREATE
                TABLE statement. Otherwise, output is created using EXECUTE FUNCTION INTO
                clause.
                Default Value: False
                Types: bool

        RETURNS:
            UAFQueryGenerator object. (We can call this as map-reduce object)

        RAISES:

        EXAMPLES:
            aqg_obj = UAFAnalyticQueryGenerator()
        """
        self.__function_name = function_name
        self.__func_input_args = func_input_args
        self.__func_input_filter_expr_args = func_input_filter_expr_args
        self.__func_other_args = func_other_args if func_other_args else None
        self.__func_output_args = func_output_args  if func_output_args else None
        self.__func_input_fmt_args = func_input_fmt_args if func_input_fmt_args else None
        self.__func_output_fmt_args = func_output_fmt_args if func_output_fmt_args else None
        self.__volatile_output = volatile_output
        self.__parameterised_sql = ""
        self.__parameterised_sql_values = []
        self.__non_parameterised_sql = ""
        self.__ctas = ctas

    def __generate_uaf_input_arg_sql(self):
        """
        Private function to generate SERIES_SPEC or MATRIX_SPEC or ART_SPEC
        or GENSERIES_SPEC clause along with 'WHERE' clause.
        For Example,
            SERIES_SPEC(
                TABLE_NAME(StockDataSet),
                SERIES_ID(DataSetID),
                ROW_AXIS(SEQUENCE(SeqNo)),
                PAYLOAD(FIELDS(Magnitude), CONTENT(REAL))
                    )
                WHERE DataSetID=556 AND SeqNo > 3,

            SERIES_SPEC(
                TABLE_NAME(SMOOTH_SERIES),
                SERIES_ID(DataSetID),
                ROW_AXIS(SEQUENCE(ROW_I)),
                PAYLOAD(FIELDS(Magnitude), CONTENT(REAL))
                    )
                WHERE DataSetID=556,

        PARAMETERS:
            None

        RETURNS:
            tuple, with 3 elements.
            element 1 is a string, represents the parameterised SQL clause,
            element 2 is a list, represents the values for parameterised SQL clause,
            element 3 is a string, represents the non parameterised SQL clause.

        RAISES:
            None.

        EXAMPLES:
            >>> self.__generate_sqlmr_input_arg_sql()
        """

        # If the input argument is a string instead of list of TDSeries/TDMatrix objects,
        # return the same and do not process those to get SQL expression since the string
        # itself represents the SQL expression.
        if isinstance(self.__func_input_args, str):
            return self.__func_input_args

        # Function to get the filter expression.
        _filter_expr = lambda filter: "\n  WHERE {}".format(filter.compile()) if filter else ""
        _parameterised_sql, _parameterised_sql_values, _non_parameterised_sql, seperator = "", [], "", ""

        for _arg, _arg_filter in zip(self.__func_input_args, self.__func_input_filter_expr_args):
            _sql, _values = _arg._get_sql_repr()
            _arg_filter_expr = _filter_expr(_arg_filter)
            _parameterised_sql_values = _parameterised_sql_values + _values
            _parameterised_sql = _parameterised_sql + seperator + "{} {}".format(_sql, _arg_filter_expr)
            _non_parameterised_sql = _non_parameterised_sql + seperator + "{} {}".format(_arg._get_sql_repr(True), _arg_filter_expr)
            seperator = ",\n"

        return _non_parameterised_sql

    def __generate_uaf_output_arg_sql(self):
        """
        Private function to generate output clause from output function arguments.
        For Example, ART(TABLE_NAME)

        PARAMETERS:
            None.

        RETURNS:
            str, represents a SQL clause for UAF function.

        RAISES:
            None.

        EXAMPLES:
            output_arg_sql = self.__generate_uaf_output_arg_sql()
            # Output is as shown in example in description.
        """
        if self.__ctas or self.__func_output_args is None:
            return ""
        return "INTO {}ART({})".format("VOLATILE " if self.__volatile_output else "", self.__func_output_args)

    def _get_arg_expressions(self, arg, value):
        """
        Internal function to generate the parameterised SQL clause, parameterised SQL
        value and non parameterised SQL clause for a given argument and it's value.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies the name of SQL clause.
                Types: str

            value:
                Required Argument.
                Specifies the value of SQL Clause. If the type of this argument is a dictionary,
                then the same function will be called recursively to generate the expression.
                Types: int OR str OR float OR dict

        RETURNS:
            tuple, with 3 elements.
            element 1 is a string, represents the parameterised SQL clause,
            element 2 is a list, represents the values for parameterised SQL clause.
            element 3 is a string, represents the non parameterised SQL clause.

        RAISES:
            None.

        EXAMPLES:
            self.__get_other_arg_expressions("arg1", {"arg2": {"arg3": "value3"}}})
            # Output is as shown in example in description.
        """
        if value is None:
            return "", [], ""

        if not isinstance(value, dict):
            # If value is a list, convert it to string seperated by comma.
            value = ", ".join((str(i) for i in value)) if isinstance(value, list) else value
            return "{}(?)".format(arg), [value], "{}({})".format(arg, value)

        # If it is a dictionary.
        _p_sql_clauses, _p_sql_values_l, _np_sql_clauses, seperator = "", [], "", ""

        # Loop through the dictionary and call the same function again.
        for _arg, _value in value.items():
            _p_sql, _p_sql_values, _np_sql = self._get_arg_expressions(_arg, _value)

            _p_sql_clauses = _p_sql_clauses + seperator + _p_sql
            _p_sql_values_l = _p_sql_values_l + _p_sql_values
            _np_sql_clauses = _np_sql_clauses + seperator + _np_sql

            # After the first element, every other element should pad with
            # previous elements with a comma(,).
            seperator = ", "

        # Append it with parent before returning it.
        return "{}({})".format(arg, _p_sql_clauses), _p_sql_values_l, "{}({})".format(arg, _np_sql_clauses)


    def __generate_uaf_func_params_sql(self):
        """
        Private function to generate FUNC_PARAMS clause from function arguments.
        For Example, FUNC_PARAMS(MATHOP("SUB")).

        PARAMETERS:
            None

        RETURNS:
            str, represents a SQL clause for UAF function.

        RAISES:
            None.

        EXAMPLES:
            other_arg_sql = self.__generate_uaf_func_params_sql({"MATHOP": 'SUB'})
            # Output is as shown in example in description.
        """
        _, _, func_params = self._get_arg_expressions("FUNC_PARAMS", self.__func_other_args)
        return ",\n{}".format(func_params) if func_params else func_params

    def __generate_uaf_input_fmt_arg_sql(self):
        """
        Private function to generate INPUT_FMT clause from function arguments.
        For Example, INPUT_FMT (INPUT_MODE (ONE2ONE)).

        PARAMETERS:
            None

        RETURNS:
            str, represents a SQL clause for UAF function.

        RAISES:
            None.

        EXAMPLES:
            other_arg_sql = self.__generate_uaf_input_fmt_arg_sql({"INPUT_MODE": 'ONE2ONE'})
        """
        _, _, input_fmt_sql = self._get_arg_expressions("INPUT_FMT", self.__func_input_fmt_args)
        return ",\n{}".format(input_fmt_sql) if input_fmt_sql else input_fmt_sql

    def __generate_uaf_output_fmt_arg_sql(self):
        """
        Private function to generate OUTPUT_FMT clause from function arguments.
        For Example, INPUT_FMT (OUTPUT_MODE (ONE2MANY)).

        PARAMETERS:
            None.

        RETURNS:
            str, represents a SQL clause for UAF function.

        RAISES:
            None.

        EXAMPLES:
            other_arg_sql = self.__generate_uaf_output_fmt_arg_sql({"OUTPUT_MODE": 'ONE2MANY'})
        """

        _, _, output_fmt_sql = self._get_arg_expressions("OUTPUT_FMT", self.__func_output_fmt_args)
        return ",\n{}".format(output_fmt_sql) if output_fmt_sql else output_fmt_sql

    def _get_display_uaf(self):
        """
        Private function to generate the non parameterised UAF SQL.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None.

        EXAMPLES:
            other_arg_sql = self._get_display_uaf()
        """
        input_sql = self.__generate_uaf_input_arg_sql()

        output_sql = self.__generate_uaf_output_arg_sql()

        func_params_sql = self.__generate_uaf_func_params_sql()

        input_fmt_sql = self.__generate_uaf_input_fmt_arg_sql()

        output_fmt_sql = self.__generate_uaf_output_fmt_arg_sql()

        input_sql = "{}(\n{})".format(self.__function_name, "{}{}{}{}".format(
            input_sql, func_params_sql, input_fmt_sql, output_fmt_sql))

        sql = "EXECUTE FUNCTION {} {}".format(output_sql, input_sql)
        if self.__ctas:
            on_preserve_clause = " ON COMMIT PRESERVE ROWS" if self.__volatile_output else ""
            sql = "CREATE {}TABLE {} AS ({}) WITH DATA{}".format("VOLATILE " if self.__volatile_output else "",
                                                                self.__func_output_args,
                                                                sql,
                                                                on_preserve_clause)
        return sql


class StoredProcedureQueryGenerator:
    """
    This class creates a SQL-MR object, which can be used to generate
    Stored Procedure Query Generator in FFE syntax for Teradata.
    """

    def __init__(self, function_name,
                 func_other_args_values,
                 db_name="SYSLIB"):
        """
        StoredProcedureQueryGenerator constructor, to create query for Stored Procedures.

        PARAMETERS:
            function_name:
                Required Argument.
                Specifies the name of the function.

            func_other_args_values:
                Required Argument.
                Specifies a dict in the format: {'sql_name':'value'}.

            db_name:
                Optional Argument.
                Specifies the install location of Stored Procedures.
                Default Value: SYSLIB

        RETURNS:
            StoredProcedureQueryGenerator object.

        EXAMPLES:
            aqg_obj = StoredProcedureQueryGenerator(function_name, other_sql_args, db_name="mldb")
        """
        self.__function_name = function_name

        # If the db_name is provided, append it to the stored
        # procedure function name.
        self.__db_name = db_name
        if self.__db_name:
            self.__function_name = "\"{}\".{}".format(self.__db_name,
                                                      self.__function_name)

        self.__func_other_args_values = func_other_args_values
        self.__CALL_STMT_FMT = "Call {}({})"
        self.__QUERY_SIZE = self.__get_string_size(self.__CALL_STMT_FMT) + 20


    def __generate_sqlmr_func_other_arg_sql(self):
        """
        Private function to generate a SQL clause for other function arguments.
        For Example, two paramater values of {a:False, b:"BINOMIAL"} are
        appened like: False, "BINOMIAL", in the same order.

        RETURNS:
            SQL string for other function arguments, as shown in example here.

        EXAMPLES:
            __func_other_args_values = {"a":False, "b":"BINOMIAL"}
            other_arg_sql = self.__generate_sqlmr_func_other_arg_sql()
            # Output is as shown in example in description.

        """
        args_sql_str = ','.join(map(str, self.__func_other_args_values.values()))
        self.__QUERY_SIZE = self.__QUERY_SIZE + self.__get_string_size(args_sql_str)
        return args_sql_str

    def _gen_call_stmt(self):
        """
        Protected function to generate complete  query.
        For Example,
            CALL SYSLIB.TD_FILTERFACTORY1D ('test', 'filters', 33, 'lowpass', 'blackman', NULL, 20.0, 40.0, NULL, 200, NULL);

        PARAMETERS:

        RETURNS:
            A SQL-MR/Analytical query, as shown in example here.

        RAISES:

        EXAMPLES:
            aqg_obj = StoredProcedureQueryGenerator(function_name=self._metadata.sql_function_name,
                                                    func_other_args_values=self._func_other_args,
                                                    db_name=db_name)
            anly_query = aqg_obj._gen_sqlmr_select_stmt_sql()
            # Output is as shown in example in description.

        """
        return self.__CALL_STMT_FMT.format(self.__function_name, self.__generate_sqlmr_func_other_arg_sql())

    def __get_string_size(self, string):
        return len(string.encode("utf8"))
