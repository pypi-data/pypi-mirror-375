#########################################################################
# Unpublished work.                                                     #
# Copyright (c) 2020 by Teradata Corporation. All rights reserved.      #
# TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET                    #
#                                                                       #
# Primary Owner: Gouri.Patwardhan@teradata.com                          #
# Secondary Owner: Trupti.Purohit@teradata.com                          #
#                                                                       #
# This file implements class for SQL query generation.                   #
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

# Current directory is table_operators folder.
teradataml_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_folder = os.path.join(teradataml_folder, "config")

class QueryGenerator:
    """
    This class creates a Query object, which can be used to generate
    SQL-MR/Analytical query in FFE syntax for Teradata or Table Operator queries for Vantage
    """

    def __init__(self, function_name, func_input_arg_sql_names, func_input_table_view_query, func_input_dataframe_type,
                 func_input_distribution, func_input_partition_by_cols, func_input_order_by_cols,
                 func_other_arg_sql_names, func_other_args_values, func_other_arg_json_datatypes,
                 func_output_args_sql_names, func_output_args_values, func_type="FFE",
                 engine="ENGINE_ML"):

        """
        QueryGenerator constructor, to create a table operator object, for
        Table Operator query generation.

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
                input. Values can be "FACT", "HASH", DIMENSION", "NONE".

            func_input_partition_by cols:
                Required Argument.
                Specifes the list containing partition columns for
                each input, if distribution is FACT or HASH.

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

        RETURNS:
            Table Operator object.

        RAISES:

        EXAMPLES:
            aqg_obj = QueryGenerator(self.function_name, self.input_sql_args,
                                             self.input_table_qry, self.input_df_type,
                                             self.input_distribution, self.input_partition_columns,
                                             self.input_order_columns, self.other_sql_args,
                                             self.other_args_val, [], self.output_sql_args,
                                             self.output_args_val, engine="ENGINE_SQL")
        """
        self._engine = engine
        self._function_name = self._get_alias_name_for_function(function_name)
        self._func_input_arg_sql_names = func_input_arg_sql_names
        self._func_input_table_view_query = func_input_table_view_query
        self._func_input_dataframe_type = func_input_dataframe_type
        self._func_input_distribution = func_input_distribution
        self._func_input_partition_by_cols = func_input_partition_by_cols
        self._func_input_order_by_cols = func_input_order_by_cols
        self._func_other_arg_sql_names = func_other_arg_sql_names
        self._func_other_args_values = func_other_args_values
        self._func_other_arg_json_datatypes = func_other_arg_json_datatypes
        self._func_output_args_sql_names = func_output_args_sql_names
        self._func_output_args_values = func_output_args_values
        self._func_output_args_values = func_type
        self._SELECT_STMT_FMT = "SELECT * FROM {} as sqlmr"
        self._QUERY_SIZE = self._get_string_size(self._SELECT_STMT_FMT) + 20
        self._input_arg_clause_lengths = []
        self._multi_query_input_nodes = []


    def _process_for_teradata_keyword(self, keyword):
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
        TERADATA_RESERVED_WORDS = ["INPUT", "THRESHOLD", "CHECK", "SUMMARY", "HASH", "METHOD"]
        if keyword.upper() in TERADATA_RESERVED_WORDS:
            return UtilFuncs._teradata_quote_arg(keyword, "\"", False)
        else:
            return keyword

    def _generate_query_func_other_arg_sql(self):
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
            _func_other_arg_sql_names = ["Step", "Family"]
            _func_other_args_values = ["False", "BINOMIAL"]
            other_arg_sql = self._generate_tblop_func_other_arg_sql()
            # Output is as shown in example in description.

        """
        args_sql_str = ""
        for index in range(len(self._func_other_arg_sql_names)):
            args_sql_str = "{0}\n\t{1}({2})".format(args_sql_str,
                                                    self._process_for_teradata_keyword(
                                                        self._func_other_arg_sql_names[index]),
                                                    self._func_other_args_values[index])

        self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(args_sql_str)
        return args_sql_str

    def _generate_tblop_input_arg_sql(self, table_ref, table_ref_type, alias=None):
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
            other_arg_sql = self._generate_tblop_input_arg_sql("table_name", "TABLE", "InputTable")
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
            returnSql = "{0} AS {1}".format(returnSql, self._process_for_teradata_keyword(alias))

        return returnSql

    def _generate_tblop_output_arg_sql(self):
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
            _func_output_args_sql_names = ["OutputTable", "CoefficientsTable"]
            _func_output_args_values = ["out_table_1", "out_table_2"]
            other_arg_sql = self._generate_tblop_output_arg_sql()
            # Output is as shown in example in description.

        """
        args_sql_str = ""
        for index in range(len(self._func_output_args_sql_names)):
            if self._func_output_args_values[index] is not None:
                args_sql_str = "{0}\n\tOUT TABLE {1}({2})".format(args_sql_str,
                                                                  self._process_for_teradata_keyword(
                                                                      self._func_output_args_sql_names[index]),
                                                                  self._func_output_args_values[index])

        self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(args_sql_str)
        return args_sql_str

    def _single_complete_table_ref_clause(self):
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
            _func_input_arg_sql_names = ["InputTable1", "InputTable2"]
            _func_input_table_view_query = ["table_name", "select * from table"]
            _func_input_dataframe_type = ["TABLE", "QUERY"]
            _func_input_distribution = ["FACT", "DIMENSION"]
            _func_input_partition_by_cols = ["col1", "NA_character_"]
            _func_input_order_by_cols = ["col2", "NA_character_"]
            other_arg_sql = self._single_complete_table_ref_clause()
            # Output is as shown in example in description.

        """
        on_clause_dict = OrderedDict()
        args_sql_str = []
        # Let's iterate over the input arguments to the analytic functions.
        # Gather all the information provided by the wrapper.
        for index in range(len(self._func_input_arg_sql_names)):
            # Get table reference. This contains following information:
            #   table name or view name OR
            #   A list of [view_name, query, node_query_type, node_id] gathered from
            #   'aed_exec_query_output' for the input node.
            table_ref = self._func_input_table_view_query[index]
            # Get the table reference type, which is, either "TABLE" or "QUERY"
            table_ref_type = self._func_input_dataframe_type[index]
            # Input argument alias
            alias = self._func_input_arg_sql_names[index]
            # Partition information
            distribution = self._func_input_distribution[index]
            partition_col = self._func_input_partition_by_cols[index]
            # Order clause information
            order_col = self._func_input_order_by_cols[index]
            # Get the Partition clause for the input argument.
            partition_clause = self.__gen_tblop_input_partition_clause(distribution, partition_col)
            # Get the Order clause for the input argument.
            order_clause = self.__gen_tblop_input_order_clause(order_by_type, order_col, sort_ascending, nulls_first)

            if table_ref_type == "TABLE":
                # If table reference type is "TABLE", then let's use the table name in the query.
                on_clause = self._generate_tblop_input_arg_sql(table_ref, table_ref_type, alias)
                on_clause_str = "{0}{1}{2}".format(on_clause, partition_clause, order_clause)
                args_sql_str.append(on_clause_str)
                # Update the length of the PARTITION clause.
                self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(on_clause_str)
            else:
                # Store the input argument information for the inputs, which will use query as input.
                on_clause_dict[index] = {}
                on_clause_dict[index]["PARTITION_CLAUSE"] = partition_clause
                on_clause_dict[index]["ORDER_CLAUSE"] = order_clause
                on_clause_dict[index]["ON_TABLE"] = self._generate_tblop_input_arg_sql(table_ref[0], "TABLE", alias)
                on_clause_dict[index]["ON_QRY"] = self._generate_tblop_input_arg_sql(table_ref[1], "QUERY", alias)
                on_clause_dict[index]["QRY_TYPE"] = table_ref[2]
                on_clause_dict[index]["NODEID"] = table_ref[3]
                on_clause_dict[index]["LAZY"] = table_ref[4]
                # If input node results in returning multiple queries save that input node
                # in '_multi_query_input_nodes' list.
                if table_ref[5]:
                    self._multi_query_input_nodes.append(table_ref[3])

        # Process OrderedDict to generate input argument clause.
        for key in on_clause_dict.keys():
            if self._QUERY_SIZE + self._get_string_size(on_clause_dict[key]["ON_QRY"]) <= 900000:
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

            args_sql_str.append(on_clause_str)

            # Add the length of the ON clause.
            self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(on_clause_str)

        return " ".join(args_sql_str)

    def __gen_tblop_input_order_clause(self, order_by_type, column_order, sort_ascending, nulls_first):
        """
        Private function to generate complete order by clause for input function arguments.
        For Example,
            Order By col2

        PARAMETERS:
            column_order - Column to be used in ORDER BY clause. If this is "NA_character_"
                            no ORDER BY clause is generated.

        RETURNS:
            Order By clause, as shown in example here.

        RAISES:

        EXAMPLES:
            other_arg_sql = self._gen_tblop_input_order_clause("col2")
            # Output is as shown in example in description.

        """
        sort_order = "ASC"
        nulls_order = None
        if column_order == "NA_character_" or column_order is None:
          return ""
        if sort_ascending == False:
            sort_order = "DESC"

        if nulls_first == True:
            nulls_order = "NULLS FIRST"
        elif nulls_first == False:
            nulls_order = "NULLS LAST"

        if order_by_type == "LOCAL":
            args_sql_str = "\n\t LOCAL ORDER BY {0} {1} {2}".format(column_order, sort_order, nulls_order)
        else:
            args_sql_str = "\n\tORDER BY {0} {1} {2}".format(column_order, sort_order, nulls_order)

        # Get the length of the ORDER clause.
        self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(args_sql_str)

        return args_sql_str

    def __gen_tblop_input_partition_clause(self, distribution, column):
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
                When "DIMENSION" - DIMENSION clause is generated.
                When "NONE" - No clause is generated, an empty string is returned.

        RAISES:
            TODO

        EXAMPLES:
            other_arg_sql = self.__gen_tblop_input_partition_clause("FACT", "col1")
            # Output is as shown in example in description.

        """
        if distribution == "FACT" and column is not None:
            args_sql_str = "\n\tPARTITION BY {0}".format(column)
        elif distribution == "FACT" and column is None:
            args_sql_str = "\n\tPARTITION BY ANY"
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
        self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(args_sql_str)
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
        # If function is a nos function, then alias name is same as function name or function mapping name.
        if "ReadNOS".lower() == function_name.lower():
            return configure.read_nos_function_mapping.upper()
        elif "WriteNOS".lower() == function_name.lower():
            return configure.write_nos_function_mapping.upper()
        # If Table Operator function is IMAGE2MATRIX, then return alias name as TD_IMAGE2MATRIX.
        elif "IMAGE2MATRIX".lower() == function_name.lower():
            return "TD_IMAGE2MATRIX"
        elif "Script".lower() == function_name.lower():
            return "Script"
        elif "Apply".lower() == function_name.lower():
            return "Apply"

    def _get_string_size(self, string):
        return len(string.encode("utf8"))
