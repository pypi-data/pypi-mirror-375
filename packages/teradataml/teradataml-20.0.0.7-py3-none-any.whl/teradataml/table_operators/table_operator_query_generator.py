#########################################################################
# Unpublished work.                                                     #
# Copyright (c) 2020 by Teradata Corporation. All rights reserved.      #
# TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET                    #
#                                                                       #
# Primary Owner: gouri.patwardhan@teradata.com                          #
# Secondary Owner: trupti.purohit@teradata.com                          #
#                                                                       #
# This file implements class creates a table operator object, which can #
# be used to generate Table Operator query for Teradata.                #
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
from teradataml.table_operators.query_generator import QueryGenerator

# Current directory is analytics folder.
teradataml_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_folder = os.path.join(teradataml_folder, "config")

class TableOperatorQueryGenerator(QueryGenerator):
    """
    This class creates a Table Operator object, which can be used to generate
    Table Operator for Teradata.
    """

    def __init__(self, function_name, func_input_arg_sql_names,
                 func_input_table_view_query, func_input_dataframe_type,
                 func_input_distribution, func_input_partition_by_cols,
                 func_input_order_by_cols,func_other_arg_sql_names,
                 func_other_args_values, func_other_arg_json_datatypes,
                 func_output_args_sql_names, func_output_args_values,
                 func_input_order_by_type, func_input_sort_ascending ="ASC",
                 func_input_nulls_first=None, func_type="FFE",
                 engine="ENGINE_SQL"):

        """
        TableOperatorQueryGenerator constructor, to create a SQL object, for
        Table Operator SQL query generation.

        PARAMETERS:
            function_name:
                Required Argument.
                Specifies the name of the function.

            func_input_arg_sql_names:
                Required Argument.
                Specifies the list of input Argument names.

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
                input. Values can be "FACT", "HASH", "DIMENSION", "NONE".

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

            func_input_order_by_type:
                Optional Argument.
                Specifies if it is 'local order by' or 'order by'.

            func_input_sort_ascending:
                Optional Argument.
                Specifies the order in which result sets are sorted.
                ASC means results are to be ordered in ascending sort order.
                DESC means results are to be ordered in descending sort order.
                This argument is ignored, if func_input_order_by_cols is empty.
                Default Value: ASC
                Permitted Values: ASC, DESC

            func_input_nulls_first:
                Optional Argument.
                Specifies whether NULLS should be displayed first or last.
                Default Value: None
                Types: bool

            func_type:
                Required Argument. Fixed value 'FFE'.
                Kept for future purpose, to generate different syntaxes.

            engine:
                Optional Argument.
                Specifies the type of engine.
                Default Value : ENGINE_SQL
                Permitted Values : ENGINE_SQL

        RETURNS:
            TableOperatorQueryGenerator object.

        RAISES:

        EXAMPLES:
            tqg_obj = TableOperatorQueryGenerator(self.function_name, self.input_sql_args,
                                             self.input_table_qry, self.input_df_type,
                                             self.input_distribution, self.input_partition_columns,
                                             self.input_order_columns, self.other_sql_args,
                                             self.other_args_val, [], self.output_sql_args,
                                             self.output_args_val, self.func_input_order_by_type,
                                             self.func_input_sort_ascending, self.func_input_nulls_first,
                                             self.func_type, self.engine="ENGINE_SQL")
        """
        self.__func_input_order_by_type = func_input_order_by_type
        self.__func_input_sort_ascending = func_input_sort_ascending
        self.__func_input_nulls_first = func_input_nulls_first

        super(TableOperatorQueryGenerator, self).__init__(function_name, func_input_arg_sql_names,
                                                          func_input_table_view_query, func_input_dataframe_type,
                                                          func_input_distribution, func_input_partition_by_cols,
                                                          func_input_order_by_cols, func_other_arg_sql_names,
                                                          func_other_args_values, func_other_arg_json_datatypes,
                                                          func_output_args_sql_names, func_output_args_values,
                                                          func_type="FFE",engine = "ENGINE_SQL")

    def _gen_table_operator_select_stmt_sql(self):
        """
        DESCRIPTION:
            Protected function to generate complete table operator query.
            For Example,
                SELECT * FROM Script(
                    input_arguments_clause
                    other_arguments_clause
                ) as sqlmr

        PARAMETERS:
            None.

        RETURNS:
            A table operator query, as shown in example here.

        RAISES:
            None.

        EXAMPLES:
            aqg_obj = TableOperatorQueryGenerator(self.function_name, self.input_sql_args,
                                             self.input_table_qry, self.input_df_type,
                                             self.input_distribution, self.input_partition_columns,
                                             self.input_order_columns, self.other_sql_args,
                                             self.other_args_val, [], self.output_sql_args,
                                             self.output_args_val, self.func_input_order_by_type,
                                             self.func_input_sort_ascending, self.func_input_nulls_first,
                                             self.func_type, self.engine="ENGINE_SQL")
            sto_statement = aqg_obj._gen_table_operator_select_stmt_sql()
            # Value of 'sto_statement' is as shown in the DESCRIPTION.
        """
        return "SELECT * FROM {} as sqlmr".format(self._gen_table_operator_invocation_sql())

    def _gen_table_operator_invocation_sql(self):
        """
        DESCRIPTION:
            Protected function to generate a part of table operator query.
            For Example,
            Script (ON table_name AS InputTable1 Partition By col1 Order By col2
                other_arguments_clause
            )

        PARAMETERS:
            None.

        RETURNS:
            A Table Operator query, as shown in example here.

        RAISES:
            None.

        EXAMPLES:
            aqg_obj = AnalyticQueryGenerator(self.function_name, self.input_sql_args, self.input_table_qry,
                                         self.input_df_type,
                                         self.input_distribution, self.input_partition_columns,
                                         self.input_order_columns,
                                         self.other_sql_args, self.other_args_val, [], self.output_sql_args,
                                         self.output_args_val)
            tblop_query = aqg_obj._gen_table_operator_invocation_sql()
            # Output is as shown in example in description.
        """

        self.__OTHER_ARG_CLAUSE = self._generate_query_func_other_arg_sql()

        self.__INPUT_ARG_CLAUSE = self._single_complete_table_ref_clause()

        invocation_sql = "{0}({1}".format(self._function_name, self.__INPUT_ARG_CLAUSE)
        if len(self._func_other_arg_sql_names) != 0:
            using_clause = ""
            # If the function is a NOS function, then USING clause is needed.
            if self._function_name.lower() in [configure.write_nos_function_mapping.lower(),
                                               configure.read_nos_function_mapping.lower(),
                                               "td_image2matrix"
                                               ]: 
                using_clause = "USING"
            invocation_sql = "{0}\n\t{1}{2}".format(invocation_sql, using_clause, self.__OTHER_ARG_CLAUSE)

        invocation_sql = invocation_sql + "\n)"

        return invocation_sql

    # TODO This method will be refactored as part of ELE-2572
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
            __func_input_arg_sql_names = ["InputTable1", "InputTable2"]
            __func_input_table_view_query = ["table_name", "select * from table"]
            __func_input_dataframe_type = ["TABLE", "QUERY"]
            __func_input_distribution = ["FACT", "DIMENSION"]
            __func_input_partition_by_cols = ["col1", "NA_character_"]
            __func_input_order_by_cols = ["col2", "NA_character_"]
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
            # Order by type information - local order by or order by
            order_by_type = None if not self.__func_input_order_by_type else self.__func_input_order_by_type[index]
            # Sort order ascending or descending information
            sort_ascending = self.__func_input_sort_ascending
            # Nulls first or last information
            nulls_first = self.__func_input_nulls_first
            # Get the Partition clause for the input argument.
            partition_clause = self.__gen_query_input_partition_clause(distribution, partition_col)
            # Get the Order clause for the input argument.
            order_clause = self.__gen_query_input_order_clause(order_by_type, order_col, sort_ascending, nulls_first)

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

    def __gen_query_input_order_clause(self, order_by_type, column_order, sort_ascending, nulls_first):
        """
        Private function to generate complete order by clause for input function arguments.
        For Example,
            Order By col2
            Local Order By col1

        PARAMETERS:
            order_by_type:
                Specifies whether input data is to be ordered locally or not.
                Order by specifies the order in which the values in a group, or partition, are sorted.
                Local Order By specifies orders qualified rows on each AMP in preparation to be input
                to a table function.
            column_order:
                Column to be used in ORDER BY clause. If this is "NA_character_" no ORDER BY clause is generated.
            sort_ascending:
                Specifies the order in which result sets are sorted.
                ASC means results are to be ordered in ascending sort order.
                DESC means results are to be ordered in descending sort order.
                This argument is ignored, if data_order_column is None.
                Default value: True which means ASC
                Types: bool
            nulls_first:
                Optional Argument
                Specifies whether NULLS are listed first or last during ordering.
                This argument is ignored, if data_order_column is None.
                Default Value: None (Not set)
                Types: bool

        RETURNS:
            Order By clause, as shown in example here.

        RAISES:

        EXAMPLES:
            other_arg_sql = self._gen_tblop_input_order_clause("col2")
            # Output is as shown in example in description.

        """
        sort_order = "ASC"
        nulls_order = ''
        if column_order == "NA_character_" or column_order is None:
          return ""
        if sort_ascending == False:
            sort_order = "DESC"
        elif isinstance(sort_ascending, list):
            sort_order = ""

        if nulls_first == True:
            nulls_order = "NULLS FIRST"
        elif nulls_first == False:
            nulls_order = "NULLS LAST"
        elif isinstance(nulls_first, list):
            nulls_order = ""

        if order_by_type == "LOCAL":
            args_sql_str = "\n\t LOCAL ORDER BY {0} {1} {2}".format(column_order, sort_order, nulls_order)
        else:
            args_sql_str = "\n\tORDER BY {0} {1} {2}".format(column_order, sort_order, nulls_order)

        # Get the length of the ORDER clause.
        self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(args_sql_str)

        return args_sql_str

    def __gen_query_input_partition_clause(self, distribution, column):
        """
        Private function to generate PARTITION BY, HASH BY or DIMENSION clause for input function arguments.
        For Example,
            Partition By col1
            Hash By col1
            DIMENSION

        PARAMETERS:
            distribution - Type of clause to be generated. Values accepted here are: FACT, HASH, DIMENSION, NONE
            column - Column to be used in PARTITION BY clause, when distribution is "FACT"

        RETURNS:
            Partition clause, based on the type of distribution:
                When "FACT" - PARTITION BY clause is generated.
                When "HASH" = HASH BY clause is generated
                When "DIMENSION" - DIMENSION clause is generated.
                When "NONE" - No clause is generated, an empty string is returned.

        RAISES:
            TODO

        EXAMPLES:
            other_arg_sql = self.__gen_query_input_partition_clause("FACT", "col1")
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

