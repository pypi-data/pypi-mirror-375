"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pankajvinod.purandare@teradata.com
Secondary Owner: Mark.Sandan@teradata.com

This file implements the wrapper's around AED API's from eleCommon library.
This facilitates the teradataml library infrastructure code to call these functions
and not change anything in future, regardless, of the design changes on
AED side.
"""

import os
import platform
import re

from ctypes import c_int, c_char_p, c_char, POINTER, byref

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.constants import TeradataConstants
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.utils import UtilFuncs
from teradataml.common.constants import AEDConstants
from teradataml.common.constants import SQLPattern
from teradataml.context.aed_context import AEDContext


class AedUtils:

    def __init__(self):
        self.aed_context = AEDContext()

    def _aed_table(self, source):
        """
        This wrapper function facilitates a integration with 'aed_table',
        a C++ function, in AED library, with Python tdml library.

        This  function must be called when a Python (tdml) data frame is to be
        created using a table name.

        PARAMETERS:
            source - Fully qualified source table name i.e. dbname.tablename

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")

        RETURNS:
            A node id in DAG - AED, for a data frame.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_table.argtypes =[POINTER(c_char_p),
                                                             POINTER(c_char_p),
                                                             POINTER(c_char_p),
                                                             POINTER(c_char_p),
                                                             POINTER(c_char_p),
                                                             POINTER(c_int)
                                                 ]
        # Input arguments for 'C' function.
        arg_name = ["source"]
        arg_value = [source]
        output_table = [""]
        output_schema = [""]

        # Ouptut nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request for TABLE
            self.aed_context.ele_common_lib.aed_table(self.aed_context._arr_c(arg_name),
                                          self.aed_context._arr_c(arg_value),
                                          self.aed_context._arr_c(output_table),
                                          self.aed_context._arr_c(output_schema),
                                          nodeid_out,
                                          ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_table)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_query(self, query, temp_table_name=None):
        """
        This wrapper function facilitates a integration with 'aed_query',
        a C++ function, in AED library, with Python tdml library.

        This  function must be called when a Python (tdml) data frame is to be
        created using a SQL query.

        PARAMETERS:
            query - SQL query
            temp_table_name - Temporary table name to be used for output of aed_query node.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_query("select * from table")

        RETURNS:
            A node id in DAG - AED, for a data frame.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_query.argtypes =[POINTER(c_char_p),
                                                 POINTER(c_char_p),
                                                 POINTER(c_char_p),
                                                 POINTER(c_char_p),
                                                 POINTER(c_char_p),
                                                 POINTER(c_int)
                                                 ]

        # Input arguments for 'C' function.
        arg_name = ["source"]
        arg_value = [query]
        if temp_table_name is None:
            temp_table_name = UtilFuncs._generate_temp_table_name(prefix="query_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]
        if output_schema[0] is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_INVALID_GEN_TABLENAME,
                                                           "(aed_query) :: Received tablename as - {}".format(temp_table_name)),
                                      MessageCodes.AED_INVALID_GEN_TABLENAME)

        # Ouptut nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)

        try:
            self.aed_context.ele_common_lib.aed_query(self.aed_context._arr_c(arg_name),
                                          self.aed_context._arr_c(arg_value),
                                          self.aed_context._arr_c(output_table),
                                          self.aed_context._arr_c(output_schema),
                                          nodeid_out,
                                          ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_query)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_select(self, nodeid, select_expr, distinct=False, timestamp_expr=None):
        """
        This wrapper function facilitates a integration with 'aed_select',
        a C++ function, in AED library, with Python tdml library.

        This function must be called when a SELECT operation that is
        columns are to be selected from a Python (tdml) data frame.

        PARAMETERS:
            nodeid - A DAG node, a input to the select API.
            select_expr - Columns, to be selected from the data frame.
            distinct - Boolean, to decide addition of Distinct clause.
            timestamp_expr - A string, to specify the temporal table clause.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")

        RETURNS:
            A node id in DAG - AED select API.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_select.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int),
                                                  POINTER(c_int)
                                                  ]

        arg_name = ["projection"]
        arg_value = ["DISTINCT " + select_expr if distinct else select_expr]
        if timestamp_expr:
            arg_name.append("timestamp_expr")
            arg_value.append(timestamp_expr)

        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="select_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)

        length = self.aed_context._int_array1(len(arg_value))
        try:
            # *** AED request to select columns
            self.aed_context.ele_common_lib.aed_select(self.aed_context._arr_c([nodeid]),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           nodeid_out,
                                           length,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_select)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_aggregate(self, nodeid, aggregate_expr, operation):
        """
        This wrapper function facilitates a integration with
        'aed_aggregate', a C++ function, in AED library, with Python
        tdml library.

        This function must be called when an aggregate functions like
        MIN, MAX, AVG are to be performed on dataframe columns

        PARAMETERS:
            nodeid - String. It is a DAG node which is given as an
                     input to the aggregate API.
            aggregate_expr - String. Expressions like
                        'min(col1) as min_col1, min(col2) as min_col2'
                     or 'max(col1) as max_col1, max(col2) as max_col2'
            operation - String. Aggregate Operation to be performed on
                        the columns eg. min

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_aggregate_nodeid = AedObj._aed_aggregate(
                            aed_table_nodeid, "min(col1) as min_col1,
                            min(col2) as min_col2", operation = 'min')
            aed_aggregate_nodeid1 = AedObj._aed_aggregate(
                            aed_table_nodeid, "max(col1) as max_col1,
                            max(col2) as max_col2", operation = 'max')

        RETURNS:
            A node id in DAG - AED aggregate API.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """

        # Specify the argument types
        self.aed_context.ele_common_lib.aed_aggregate.argtypes = [POINTER(c_char_p),
                                                               POINTER(c_char_p),
                                                               POINTER(c_char_p),
                                                               POINTER(c_char_p),
                                                               POINTER(c_char_p),
                                                               POINTER(c_char_p),
                                                               POINTER(c_int)
                                                               ]
        arg_name = ["expr"]
        arg_value = [aggregate_expr]
        temp_table_name = UtilFuncs._generate_temp_table_name(
                                    prefix = "aggregate_" + operation + "_",
                                    use_default_database = True, quote = False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to get aggregate of columns
            self.aed_context.ele_common_lib.aed_aggregate(self.aed_context._arr_c([nodeid]),
                                                       self.aed_context._arr_c(arg_name),
                                                       self.aed_context._arr_c(arg_value),
                                                       self.aed_context._arr_c(output_table),
                                                       self.aed_context._arr_c(output_schema),
                                                       nodeid_out,
                                                       ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message( MessageCodes.AED_EXEC_FAILED,
                "(aed_aggregate_" + operation + ")" + str(emsg)), MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0],
                                                            nodeid_out[0].decode("utf-8"))

    def _aed_filter(self, nodeid, filter_expr):
        """
        This wrapper function facilitates a integration with 'aed_filter',
        a C++ function, in AED library, with Python tdml library.

        This function must be called when a FILTER operation that is
        results needs to filtered from a Python (tdml) data frame.

        PARAMETERS:
            nodeid - A DAG node, a input to the filter API.
            filter_expr - Expression in SQL format, to be used to filter data from the data frame.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")

        RETURNS:
            A node id in DAG - AED filter API.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_filter.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int)
                                                  ]

        arg_name = ["projection"]
        arg_value = [filter_expr]
        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="filter_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to filter
            self.aed_context.ele_common_lib.aed_filter(self.aed_context._arr_c([nodeid]),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           nodeid_out,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_filter)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_ml_query(self, inp_nodeids, query, output_tables, function_name, 
                                                               multi_query_inp_nodeids = []):
        """
        This wrapper function facilitates a integration with 'aed_ml_query',
        a C++ function, in AED library, with Python tdml library.

        This  function must be called when a Python (tdml) wrapper functions to generate
        DAG node for analytical queries.

        PARAMETERS:
            inp_nodeids - A list of input table/query nodeids.
            query - Complete SQL-MR query
            output_tables - List of output table names to be used for output of aed_ml_query node.
            function_name - Analytical function name.
            multi_query_inp_nodeids - List of input node ids which gives more than one queries on resolution.

        EXAMPLES:
            nodeid_out = self.aedObj._aed_ml_query([inp_node_id1, inp_node_id2], sqlmr_query, [stdout_table, out_table1, out_table2],
                                               "Sessionize", [inp_node_id1])

        RETURNS:
            Returns a list of node ids corresponding to each output table, starting with STDOUT table and then
            SQL-MR output tables.

        RAISES:
            teradataml exceptions:
                AED_INVALID_SQLMR_QUERY, AED_INVALID_GEN_TABLENAME, AED_EXEC_FAILED and AED_NON_ZERO_STATUS
            TypeErrors - For internal errors. For type mismatch.

        """

        if not isinstance(inp_nodeids, list) or not all(isinstance(nodeid, str) for nodeid in inp_nodeids):
            raise TypeError("AED Internal Error: 'inp_nodeids' should be of type list containing strings.")

        if not isinstance(query, str):
            raise TypeError("AED Internal Error: 'query' should be of type str.")

        if not isinstance(output_tables, list) or not all(isinstance(otab, str) for otab in output_tables):
            raise TypeError("AED Internal Error: 'output_tables' should be of type list containing strings.")

        if not isinstance(function_name, str):
            raise TypeError("AED Internal Error: 'function_name' should be of type str")

        if not isinstance(multi_query_inp_nodeids, list) or not all(isinstance(nodeid, str) 
                                                                               for nodeid in multi_query_inp_nodeids):
            raise TypeError("AED Internal Error: 'multi_query_inp_nodeids' should be of type list containing strings.")

        if not SQLPattern.SQLMR.value.match(query):
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_INVALID_SQLMR_QUERY, "query (aed_ml_query)"),
                                          MessageCodes.AED_INVALID_SQLMR_QUERY)

        # Specify the argument types
        self.aed_context.ele_common_lib.aed_ml_query.argtypes =[POINTER(c_char_p),   # Node Ids
                                                                 POINTER(c_char_p),  # arg_name
                                                                 POINTER(c_char_p),  # arg_value
                                                                 POINTER(c_char_p),  # output_table
                                                                 POINTER(c_char_p),  # output_schema
                                                                 POINTER(c_char_p),  # function_name
                                                                 POINTER(c_int),     # Num of Inputs
                                                                 POINTER(c_int),     # Num of Outputs
                                                                 POINTER(c_char_p),  # Output Node Ids
                                                                 POINTER(c_int),     # Return code
                                                                 POINTER(c_char_p),  # Input nodeids incase of multiple queries
                                                                 POINTER(c_int)      # Number of input nodeids
                                                                 ]

        # Input arguments for 'C' function.
        arg_name = ["source"]
        arg_value = [query]

        # Input and Output Lengths
        num_inputs = len(inp_nodeids)
        num_outputs = len(output_tables)
        num_input_nodes_incaseof_multiqueries = len(multi_query_inp_nodeids)

        # Ouptut nodeids
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"] * num_outputs)
        output_table_names = []
        output_schemas = []
        for index in range(num_outputs):
            output_table_names.append(UtilFuncs._extract_table_name(output_tables[index]))
            output_schemas.append(UtilFuncs._extract_db_name(output_tables[index]))
            if output_schemas[index] is None:
                raise TeradataMlException(Messages.get_message(MessageCodes.AED_INVALID_GEN_TABLENAME, "(aed_ml_query) " + output_tables[index]),
                                          MessageCodes.AED_INVALID_GEN_TABLENAME)

        # return code
        ret_code = self.aed_context._int_array1(0)


        try:
            self.aed_context.ele_common_lib.aed_ml_query(self.aed_context._arr_c(inp_nodeids),
                                             self.aed_context._arr_c(arg_name),
                                             self.aed_context._arr_c(arg_value),
                                             self.aed_context._arr_c(output_table_names),
                                             self.aed_context._arr_c(output_schemas),
                                             self.aed_context._arr_c([function_name]),
                                             self.aed_context._int_array1(num_inputs),
                                             self.aed_context._int_array1(num_outputs),
                                             nodeid_out,
                                             ret_code,
                                             self.aed_context._arr_c(multi_query_inp_nodeids), 
                                             self.aed_context._int_array1(num_input_nodes_incaseof_multiqueries))
            output_nodeids = self.aed_context._decode_list(nodeid_out)
            del nodeid_out
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_ml_query)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], output_nodeids)

    def _aed_gen_exec_queries(self, nodeid):
        """
        This wrapper function facilitates a integration with 'aed_gen_exec_queries',
        a C++ function, in AED library, with Python tdml library.

        This function must be called with DAG node id, to generate a complete DAG 
        path and the executable queries for that node.
        Most of the times, user must call _aed_get_exec_query, which will call
        this particular function too.

        PARAMETERS:
            nodeid - A DAG node id for which executable queries needs to be generated.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")
            num_nodes = AedObj._aed_gen_exec_queries(aed_filter_nodeid)

        RETURNS:
            Number of queries generated for the provided node ID.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_gen_exec_queries.argtypes = [POINTER(c_char_p),
                                                         POINTER(c_int),
                                                         POINTER(c_int)
                                                         ]

        queries_count = self.aed_context._int_array1(0)

        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to generate executable queries
            self.aed_context.ele_common_lib.aed_gen_exec_queries(self.aed_context._arr_c([nodeid]), queries_count, ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_gen_exec_queries)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], queries_count[0])

    def _aed_get_exec_querysize(self, nodeid, queries_count=None):
        """
        This wrapper function facilitates a integration with 'aed_get_exec_querysize',
        a C++ function, in AED library, with Python tdml library.

        This function is called to get the length of the queries generated for provided
        the nodeid.

        PARAMETERS:
            nodeid - A DAG node ID for which query size needs to be calculated.
            queries_count - Number of queries generated for the provided node ID.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            num_nodes = AedObj._aed_gen_dag_path(aed_select_nodeid)
            qry_size = AedObj._aed_get_exec_querysize(aed_select_nodeid, num_nodes)

        RETURNS:
            exec_query_size - Query size/s for the generated query/ies.

        RAISES:
             teradataml exceptions:
                AED_QUERY_COUNT_MISMATCH, AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_get_exec_querysize.argtypes = [POINTER(c_char_p),
                                                              POINTER(c_int),
                                                              POINTER(c_int),
                                                              POINTER(c_int)
                                                              ]
        if self._aed_is_node_executed(nodeid):
            # If node is already executed, then we do not need to run _aed_get_dag_querysize
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_NODE_ALREADY_EXECUTED, "(aed_get_exec_querysize)"),
                MessageCodes.AED_NODE_ALREADY_EXECUTED)

        # Let's validate the provided queries count
        queries_count_verify = self._aed_gen_exec_queries(nodeid)
        if queries_count is None:
            # Check if queries count for the provided node_id is given or not.
            queries_count = queries_count_verify

        elif queries_count != queries_count_verify:
            # If provided and does not match with the actual one, raise exception.
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_QUERY_COUNT_MISMATCH, "(aed_get_exec_querysize)"),
                MessageCodes.AED_QUERY_COUNT_MISMATCH)

        int_array_n = c_int * queries_count
        exec_query_size = int_array_n(0)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get executable query/ies size/s
            self.aed_context.ele_common_lib.aed_get_exec_querysize(self.aed_context._arr_c([nodeid]),
                                                                  c_int(queries_count), exec_query_size, ret_code)
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_get_exec_querysize)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        exec_query_size = [qry_size for qry_size in exec_query_size]
        return self.aed_context._validate_aed_return_code(ret_code[0], exec_query_size)

    def _aed_get_exec_query(self, nodeid, queries_count=None, exec_query_len=None):
        """
        This wrapper function facilitates a integration with 'aed_get_exec_query',
        a C++ function, in AED library, with Python tdml library.

        This function must be called when all the queries in the required node to
        be constructed and executed on Python client.

        PARAMETERS:
            nodeid - A DAG node ID for which queries are to be retrieved.
            queries_count - Number of queries generated for given nodeid.
            exec_query_len - Query size for the generated queries.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            num_nodes = AedObj._aed_get_exec_query(aed_select_nodeid)

        RETURNS:
            A list of list, where first list has strings (table/view) to be created upon execution of SQL.
            And second list has equivalent SQL queries, those needs to be executed for complete execution
            of a node.

        RAISES:
             teradataml exceptions:
                AED_QUERY_COUNT_MISMATCH, AED_NODE_QUERY_LENGTH_MISMATCH
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_get_exec_query.argtypes = [POINTER(c_char_p),
                                                           POINTER(c_int),
                                                           POINTER(c_char_p),
                                                           POINTER(c_char_p),
                                                           POINTER(c_char_p),
                                                           POINTER(c_char_p),
                                                           POINTER(c_int)
                                                           ]

        if self._aed_is_node_executed(nodeid):
            # If node is already executed, then we do not need to run _aed_get_dag_querysize
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_NODE_ALREADY_EXECUTED, "(_aed_get_exec_query)"),
                MessageCodes.AED_NODE_ALREADY_EXECUTED)

        # Validate the provided queries count.
        queries_count_verify = self._aed_gen_exec_queries(nodeid)
        if queries_count is None:
            # Check if queries count for the provided node_id is given or not.
            queries_count = queries_count_verify

        elif queries_count != queries_count_verify:
            # If provided and does not match with the actual one, raise exception.
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_QUERY_COUNT_MISMATCH, "(_aed_get_exec_query)"),
                MessageCodes.AED_QUERY_COUNT_MISMATCH)

        # Validate the provided exec query length.
        if exec_query_len is not None:
            if not isinstance(exec_query_len, list) or not all(isinstance(size, int) for size in exec_query_len):
                raise TypeError("AED Internal Error: 'exec_query_len' should be of type list containing integers.")

        exec_query_len_verify = self._aed_get_exec_querysize(nodeid, queries_count)
        if exec_query_len is None:
            exec_query_len = exec_query_len_verify

        elif exec_query_len != exec_query_len_verify:
            # If provided and does not match with the actual one, raise exception.
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_NODE_QUERY_LENGTH_MISMATCH, "(_aed_get_exec_query)"
                                     + str(exec_query_len) + " and " + str(exec_query_len_verify)),
                MessageCodes.AED_NODE_QUERY_LENGTH_MISMATCH)

        # dag_query_len contains a list of integers, for all the queries included in DAG PATH.
        # Accordingly, let's construct a query buffer.
        query_buffer = []
        for index in range(len(exec_query_len)):
            query_buffer.append(" " * exec_query_len[index])
        query_buffer = self.aed_context._arr_c(query_buffer)

        # Let's construct a table name buffer.
        table_name_buffer = self.aed_context._arr_c(
            [" " * AEDConstants.AED_DB_OBJECT_NAME_BUFFER_SIZE.value * 2] * queries_count)
        node_type_buffer = self.aed_context._arr_c(
            [" " * AEDConstants.AED_NODE_TYPE_BUFFER_SIZE.value] * queries_count)
        node_id_buffer = self.aed_context._arr_c(["00000000000000000000"] * queries_count)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to generate queries
            self.aed_context.ele_common_lib.aed_get_exec_query(self.aed_context._arr_c([nodeid]),
                                                   c_int(queries_count),
                                                   query_buffer,
                                                   table_name_buffer,
                                                   node_type_buffer,
                                                   node_id_buffer,
                                                   ret_code)
            # Decode UTF-8 strings
            table_name_buffer_out = self.aed_context._decode_list(table_name_buffer)
            del table_name_buffer
            query_buffer_out = self.aed_context._decode_list(query_buffer)
            del query_buffer
            node_type_out = self.aed_context._decode_list(node_type_buffer)
            del node_type_buffer
            node_id_out = self.aed_context._decode_list(node_id_buffer)
            del node_id_buffer

        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_get_exec_query)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], [table_name_buffer_out, query_buffer_out,
                                                                        node_type_out, node_id_out])

    def _aed_update_node_state(self, nodeid, nodestate=AEDConstants.AED_NODE_EXECUTED.value):
        """
        This wrapper function facilitates a integration with 'aed_update_node_state',
        a C++ function, in AED library, with Python tdml library.

        A function to update all the nodes in the DAG node path, when executed
        from client. This function needs to be called once all the node queries
        have been executed.

        PARAMETERS:
            nodeid - A DAG node ID for which node state has to updated.
            nodestate - Node state to which node should be updated.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            tables_queries = AedObj._aed_get_exec_query(aed_select_nodeid)
            num_nodes_updated = AedObj._aed_update_node_state(self, nodeid)

        RETURNS:
            Returns number of DAG Nodes updated.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_update_node_state.argtypes = [POINTER(c_char_p),
                                                           POINTER(c_int),
                                                           POINTER(c_int),
                                                           POINTER(c_int)
                                                           ]

        ret_code = self.aed_context._int_array1(0)
        # If num_dag_nodes is 1, then only single node will be updated.
        # So, assign num_dag_nodes to 0 (other than 1) to update all the nodes in the DAG node path.
        num_dag_nodes = self.aed_context._int_array1(0)

        if nodestate not in (AEDConstants.AED_NODE_NOT_EXECUTED.value, AEDConstants.AED_NODE_EXECUTED.value):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_INVALID_ARGUMENT, "(_aed_update_node_state)", "nodestate",
                                     [AEDConstants.AED_NODE_NOT_EXECUTED.value, AEDConstants.AED_NODE_EXECUTED.value]),
                MessageCodes.AED_INVALID_ARGUMENT)

        try:
            # # *** AED request to update node states of a DAG
            self.aed_context.ele_common_lib.aed_update_node_state(self.aed_context._arr_c([nodeid]),
                                                                  c_int(nodestate), num_dag_nodes, ret_code)
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_update_node_state)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], num_dag_nodes[0])

    def _aed_update_node_state_single(self, nodeid, nodestate=AEDConstants.AED_NODE_EXECUTED.value):
        """
        This wrapper function facilitates a integration with 'aed_update_node_state_single',
        a C++ function, in AED library, with Python tdml library.

        A function to update a node id of DAG to executed state.
        This function needs to be called when to update single node state to execute.

        PARAMETERS:
            nodeid - A DAG node ID for which node state has to updated.
            nodestate - Node state to which node should be updated.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            AedObj._aed_update_node_state_single(self, aed_select_nodeid)

        RETURNS:
            None

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_update_node_state_single.argtypes = [POINTER(c_char_p),
                                                                          POINTER(c_int),
                                                                          POINTER(c_int)
                                                                          ]

        ret_code = self.aed_context._int_array1(0)

        if nodestate not in (AEDConstants.AED_NODE_NOT_EXECUTED.value, AEDConstants.AED_NODE_EXECUTED.value):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_INVALID_ARGUMENT, "(_aed_update_node_state)", "nodestate",
                                     [AEDConstants.AED_NODE_NOT_EXECUTED.value, AEDConstants.AED_NODE_EXECUTED.value]),
                MessageCodes.AED_INVALID_ARGUMENT)

        try:
            # *** AED request to update single node state
            self.aed_context.ele_common_lib.aed_update_node_state_single(self.aed_context._arr_c([nodeid]),
                                                                  c_int(nodestate), ret_code)
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_update_node_state_single)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0])

    def _print_dag(self):
        """
        This wrapper function facilitates a integration with 'print_dag',
        a C++ function, in AED library, with Python tdml library.

        To get all node contents and print the same.

        PARAMETERS:
            None

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            AedObj._print_dag()

        RETURNS:
            None

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED
        """
        # TODO:: Needs support from AED to accept node to be printed.
        # Specify the argument types
        self.aed_context.ele_common_lib.print_dag.argtypes = []

        try:
            # *** AED request to generate DAG path
            self.aed_context.ele_common_lib.print_dag()
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(print_dag)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

    def _print_dag_path(self, nodeid):
        """
        This wrapper function facilitates a integration with 'print_dag_path',
        a C++ function, in AED library, with Python tdml library.

        Function to print complete node path for a DAG, from given nodeid.

        PARAMETERS:
            nodeid - A DAG node ID.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            AedObj._print_dag_path(aed_select_nodeid)

        RETURNS:
            None

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.print_dag_path.argtypes = [POINTER(c_char_p)]

        try:
            # *** AED request to print DAG path
            self.aed_context.ele_common_lib.print_dag_path(self.aed_context._arr_c([nodeid]))
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(print_dag_path)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

    def _aed_is_node_executed(self, nodeid):
        """
        This wrapper function facilitates a integration with 'aed_is_node_executed',
        a C++ function, in AED library, with Python tdml library.

        Function to check whether node is already executed or not.

        PARAMETERS:
            nodeid - A DAG node ID.

        RETURNS:
            True if node is executed, false if not executed.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            node_flag = AedObj._aed_is_node_executed(aed_select_nodeid) # Returns false.
            # Let's mark node as executed.
            num_nodes_updated = AedObj._aed_update_node_state(self, nodeid)
            node_flag = AedObj._aed_is_node_executed(aed_select_nodeid) # Returns True.

        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_is_node_executed.argtypes = [POINTER(c_char_p),
                                                                         POINTER(c_int),
                                                                         POINTER(c_int)]

        node_flag = self.aed_context._int_array1(0)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to check whether node is executed or not.
            self.aed_context.ele_common_lib.aed_is_node_executed(self.aed_context._arr_c([nodeid]),
                                                                 node_flag,
                                                                 ret_code
                                                                 )
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_is_node_executed)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        node_executed = True
        if node_flag[0] == AEDConstants.AED_NODE_NOT_EXECUTED.value:
            node_executed = False

        return self.aed_context._validate_aed_return_code(ret_code[0], node_executed)

    def _aed_get_tablename(self, nodeid):
        """
        This wrapper function facilitates a integration with 'aed_get_tablename',
        a C++ function, in AED library, with Python tdml library.

        Function to get table name for the provided node id..

        PARAMETERS:
            nodeid - A DAG node ID.

        RETURNS:
            Fully qualified table name. (dbname.tablename)

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            table_name = AedObj._aed_get_table(aed_table_nodeid).

        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_get_tablename.argtypes = [POINTER(c_char_p),
                                                                      POINTER(c_char_p),
                                                                      POINTER(c_char_p),
                                                                      POINTER(c_int)]
        outstr = "0" * AEDConstants.AED_DB_OBJECT_NAME_BUFFER_SIZE.value
        output_table = self.aed_context._arr_c([outstr])
        output_schema = self.aed_context._arr_c([outstr])
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get table name from node id.
            self.aed_context.ele_common_lib.aed_get_tablename(self.aed_context._arr_c([nodeid]),
                                                              output_table,
                                                              output_schema,
                                                              ret_code
                                                              )

            tablename = UtilFuncs._teradata_quote_arg(output_table[0].decode('UTF-8'), "\"", False)

            if output_schema[0].decode('UTF-8') != outstr and len(output_schema[0]) != 0:
                tablename = "{}.{}".format(UtilFuncs._teradata_quote_arg(output_schema[0].decode('UTF-8'), "\"", False),
                                           tablename)

            del outstr
            del output_schema
            del output_table
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_get_tablename)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], tablename)

    def _aed_get_source_tablename(self, nodeid):
        """
        This wrapper function facilitates a integration with 'aed_get_source_table',
        a C++ function, in AED library, with Python teradataml library.

        Function to get table name for the provided node id. In addition, It returns source table name.

        PARAMETERS:
            nodeid - A DAG node ID.

        RETURNS:
            Fully qualified table name including source table name. 

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            table_name = AedObj._aed_get_source_tablename(aed_table_nodeid)

        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_get_source_tablename.argtypes = [POINTER(c_char_p),
                                                                             POINTER(c_char_p),
                                                                             POINTER(c_char_p),
                                                                             POINTER(c_int)]
        outstr = "0" * AEDConstants.AED_DB_OBJECT_NAME_BUFFER_SIZE.value
        output_table = self.aed_context._arr_c([outstr])
        output_schema = self.aed_context._arr_c([outstr])
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get source table name from node id.
            self.aed_context.ele_common_lib.aed_get_source_tablename(self.aed_context._arr_c([nodeid]),
                                                                     output_table,
                                                                     output_schema,
                                                                     ret_code
                                                                     )

            tablename = UtilFuncs._teradata_quote_arg(output_table[0].decode('UTF-8'), "\"", False)

            if output_schema[0].decode('UTF-8') != outstr and len(output_schema[0]) != 0:
                tablename = "{}.{}".format(UtilFuncs._teradata_quote_arg(output_schema[0].decode('UTF-8'), "\"", False),
                                           tablename)

            del outstr
            del output_schema
            del output_table
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_get_source_tablename)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], tablename)

    def _aed_orderby(self, nodeid, orderby_expr):
        """
        This wrapper function facilitates a integration with 'aed_orderby',
        a C++ function, in AED library, with Python tdml library.

        This function must be called when a ORDERBY operation that is
        columns are to be ordered from a Python (tdml) data frame.

        PARAMETERS:
            nodeid - A DAG node, a input to the orderby API.
            orderby_expr - orderby expression.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_orderby(aed_table_nodeid, "col1 ASC, col2 DESC")

        RETURNS:
            A node id in DAG - AED orderby API.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_orderby.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int)
                                                  ]

        arg_name = ["orderby"]
        arg_value = [orderby_expr]
        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="orderby_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])
        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to select columns
            self.aed_context.ele_common_lib.aed_orderby(self.aed_context._arr_c([nodeid]),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           nodeid_out,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_orderby)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_join(self, left_nodeid, right_nodeid, select_expr, join_type, join_condition, l_alias=None, r_alias=None):
        """
        This wrapper function facilitates a integration with 'aed_join',
        a C++ function, in AED library, with Python tdml library.

        This function must be called when a JOIN operation that is
        two Python (tdml) data frames to be joined on a condition.

        PARAMETERS:
            left_nodeid    - A DAG node, left table to be join.
            right_nodeid   - A DAG node, right table to be join.
            select_expr    - Columns to select after performing join.
            join_type      - Type of join to perform on two tables.
            join_condition - Join condition to perform JOIN on two tables.
            l_alias        - Alias name to be added to left table.
            r_alias        - Alias name to be added to right table.


        EXAMPLES:
            aed_table1_nodeid = AedObj._aed_table("dbname.tablename1")
            aed_table2_nodeid = AedObj._aed_table("dbname.tablename2")
            aed_join_nodeid = self.aed_obj._aed_join(filter_node_id1, select_node_id1,
                                           "df1.col1 as df1_col1, df2.col1 as df2_col1, df1.col2,df2.col3",
                                           "inner",  "df1.col1 = df2.col1 and df1.col2 = df2.col3", "df1", "df2")

        RETURNS:
            A node id in DAG - AED join API.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_join.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int)
                                                  ]

        arg_name = [join_type, l_alias, r_alias, "projection"]
        arg_value = [join_condition, l_alias, r_alias, select_expr]
        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="join_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])
        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to select columns
            self.aed_context.ele_common_lib.aed_join(self.aed_context._arr_c([left_nodeid,right_nodeid]),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           nodeid_out,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_join)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_assign(self, nodeid, assign_expr,
                    drop_existing_columns = AEDConstants.AED_ASSIGN_DO_NOT_DROP_EXISITING_COLUMNS.value):
        """
        This wrapper function facilitates a integration with 'aed_assign',
        a C++ function, in AED library, with Python tdml library.

        This function must be called when evaluating SQL expressions.

        PARAMETERS:
            nodeid - A DAG node, a input to the aed_assign API.
            assign_expr - SQL expression to evaluate.
            drop_existing_columns - Whether to drop exisitng columns or not.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_assign_nodeid = AedObj._aed_assign(aed_table_nodeid,
                                                   "abs(col1) as abs_col1, upper(col2) as upper_col2", "Y")

        RETURNS:
            A node id in DAG - AED assign API.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED, AED_NON_ZERO_STATUS and AED_INVALID_ARGUMENT
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_assign.argtypes = [POINTER(c_char_p),
                                                                POINTER(c_char_p),
                                                                POINTER(c_char_p),
                                                                POINTER(c_char_p),
                                                                POINTER(c_char_p),
                                                                POINTER(c_char_p),
                                                                POINTER(c_int)
                                                                ]
        if drop_existing_columns not in (AEDConstants.AED_ASSIGN_DROP_EXISITING_COLUMNS.value,
                                         AEDConstants.AED_ASSIGN_DO_NOT_DROP_EXISITING_COLUMNS.value):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_INVALID_ARGUMENT, "(_aed_assign)", "drop_existing_columns",
                                     [AEDConstants.AED_ASSIGN_DROP_EXISITING_COLUMNS.value,
                                      AEDConstants.AED_ASSIGN_DO_NOT_DROP_EXISITING_COLUMNS.value]),
                MessageCodes.AED_INVALID_ARGUMENT)

        arg_name = ["assign", "drop_cols"]
        arg_value = [assign_expr, drop_existing_columns]
        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="assign_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])
        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to evaluate sql expressions
            self.aed_context.ele_common_lib.aed_assign(self.aed_context._arr_c([nodeid]),
                                                        self.aed_context._arr_c(arg_name),
                                                        self.aed_context._arr_c(arg_value),
                                                        self.aed_context._arr_c(output_table),
                                                        self.aed_context._arr_c(output_schema),
                                                        nodeid_out,
                                                        ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_assign)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_get_node_query_type(self, nodeid):
        """
        This wrapper function facilitates a integration with 'aed_get_node_query_type',
        a C++ function, in AED library, with Python tdml library.

        Function to get type of provided node id.

        PARAMETERS:
            nodeid - A DAG node ID.

        RETURNS:
            Node query type.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            node_type = AedObj._aed_get_node_query_type(aed_table_nodeid).

        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_get_node_query_type.argtypes = [POINTER(c_char_p),
                                                                      POINTER(c_char_p),
                                                                      POINTER(c_int)]
        outstr = "0" * AEDConstants.AED_NODE_TYPE_BUFFER_SIZE.value
        node_type_buf = self.aed_context._arr_c([outstr])
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get type of the node id.
            self.aed_context.ele_common_lib.aed_get_node_query_type(self.aed_context._arr_c([nodeid]),
                                                              node_type_buf,
                                                              ret_code
                                                              )
            node_type = node_type_buf[0].decode('UTF-8')
            del node_type_buf
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_get_node_query_type)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], node_type)

    def _aed_groupby(self, nodeid, groupby_expr, option=None):
        """
        This wrapper function facilitates a integration with 'aed_groupby',
        a C++ function, in AED library, with Python tdml library.

        This function must be called when a GROUP BY operation for specific
        columns are to be selected from a Python (tdml) data frame.

        PARAMETERS:
            nodeid - A DAG node, a input to the select API.
            groupby_expr - Columns, to be given from the data frame.
            option - Option, to be given from the GROUP BY Clause.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_groupby_nodeid = AedObj._aed_groupby(aed_select_nodeid, "col1, col2, col3")

        RETURNS:
            A node id in DAG - AED group_by API.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_groupby.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int)
                                                  ]

        arg_name = ["group by"]
        # If option is passed, add prefix of the option to the groupby_expr,
        # else, add prefix as empty string.
        if isinstance(groupby_expr, str):
            arg_value = ["{} | {}".format(option, groupby_expr)] if option \
               else ["{}| {}".format("", groupby_expr)]
        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="groupby_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to group by
            self.aed_context.ele_common_lib.aed_groupby(self.aed_context._arr_c([nodeid]),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           nodeid_out,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_groupby)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_setop(self, input_nodeids, setop_type, input_table_columns):
        """
        This wrapper function facilitates a integration with 'aed_setop',
        a C++ function, in AED library, with Python tdml library.

        This function must be called to perform set operation on
        two Python (tdml) data frames.

        PARAMETERS:
            input_nodeids  - List of DAG nodeids, input teradataml DataFrames for the set operation.
            setop_type     - Type of set operation to perform on two tables.
                             Valid values for setop_type: {union, unionall, minus, intersect}
            input_table_columns  - List of strings which contain comma seperated list of input teradataml DataFrame columns.


        EXAMPLES:
            aed_table1_nodeid = AedObj._aed_table("dbname.tablename1")
            aed_table2_nodeid = AedObj._aed_table("dbname.tablename2")
            aed_setop_nodeid = self.aed_obj._aed_setop([aed_table1_nodeid, aed_table2_nodeid],
                                           "union",  ["col1, col2", "col1, col2"])

        RETURNS:
            A node id in DAG - AED setop API.

        RAISES:
             teradataml exceptions:
                AED_SETOP_INPUT_TABLE_COLUMNS_COUNT_MISMATCH, AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        if not isinstance(input_nodeids, list) or not all(isinstance(nodeid, str) for nodeid in input_nodeids):
            msg = Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, "input_nodeids", "list containing strings")
            raise TypeError(msg, MessageCodes.UNSUPPORTED_DATATYPE)

        if not isinstance(input_table_columns, list) or not all(isinstance(columns, str) for columns in input_table_columns):
            msg = Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, "input_table_columns", "list containing strings")
            raise TypeError(msg, MessageCodes.UNSUPPORTED_DATATYPE)

        # number of input nodes
        num_inputs = len(input_nodeids)
        # Validate if number of input_nodeids is more than one
        if num_inputs < 2:
            msg = Messages.get_message(MessageCodes.AED_SETOP_INVALID_NUMBER_OF_INPUT_NODES, "(aed_setop)")
            raise TeradataMlException(msg, MessageCodes.AED_SETOP_INVALID_NUMBER_OF_INPUT_NODES)
        # Validate if length of input_table_columns is equal to number of input nodes
        if num_inputs != len(input_table_columns):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_SETOP_INPUT_TABLE_COLUMNS_COUNT_MISMATCH, "(aed_setop)"),
                MessageCodes.AED_SETOP_INPUT_TABLE_COLUMNS_COUNT_MISMATCH)

        # Specify the argument types
        self.aed_context.ele_common_lib.aed_setop.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int)
                                                  ]
        arg_name = [setop_type]
        arg_value = input_table_columns
        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="setop_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]
        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])
        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to select columns
            self.aed_context.ele_common_lib.aed_setop(self.aed_context._arr_c(input_nodeids),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           self.aed_context._int_array1(num_inputs),
                                           nodeid_out,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_setop)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_show_query_length(self, nodeid, include_all_queries = False, query_with_reference_to_top = False, query_count = None):
        """
        This wrapper function facilitates a integration of the 'aed_show_query_length'
        C++ function, in AED library, with Python tdml library.

        This is an internal function to get the length of the full SQL query/queries for 
        a DAG node representing the teradataml DataFrames and operations on them; no data 
        is moved. This call precedes the _aed_show_query call so that the developer can 
        obtain the proper amount of storage space.

        PARAMETERS:
            nodeid:
                Required Argument.
                Specifies a DAG node for which the length of the generated SQL query/queries
                is to be returned.
                Types: str

            include_all_queries:
                Optional Argument.
                Specifies a boolean indicating whether to return length of individual queries or not. 
                True, if length of the individual queries is required otherwise False.
                Default Value: False
                Types: bool

            query_with_reference_to_top:
                Optional Argument.
                Specifies a boolean flag indicating whether queries needs to be returned with reference 
                to the top node in AED, i.e., a teradataml DataFrame created from table or query.
                Default Value: False
                Types: bool

            query_count:
                Optional Argument.
                Specifies the number of queries returned for the given nodeid.
                Default Value: None
                Types: int

        EXAMPLES:
            aed_table_nodeid  = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")
            query_lengths     = AedObj._aed_show_query_length(aed_filter_nodeid, include_all_queries = True, query_count = 1)

        RETURNS:
            The resolved SQL query/queries length/s.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED, AED_NON_ZERO_STATUS,
                AED_SHOW_QUERY_MULTIPLE_OPTIONS and AED_QUERY_COUNT_MISMATCH
        """

        self.aed_context.ele_common_lib.aed_show_query_length.argtypes = [POINTER(c_char_p),
                                                              POINTER(c_int),
                                                              POINTER(c_int),
                                                              POINTER(c_int)
                                                              ]
        if include_all_queries and query_with_reference_to_top:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_SHOW_QUERY_MULTIPLE_OPTIONS, 
                      "(_aed_show_query_length)","include_all_queries", "query_with_reference_to_top"),
                MessageCodes.AED_SHOW_QUERY_MULTIPLE_OPTIONS)

        if not include_all_queries and not query_with_reference_to_top:
            # If both arguments are False then going with default option
            option = 1
            # Directly assgining 1, as only 1 query will be returned for
            # default option
            query_count_verify = 1
        elif include_all_queries:
            # If only include_all_queries is True
            option = 2
            # Making call to _aed_gen_full_dagpath to get number of
            # queries for nodeid, as it gives number of nodes in the
            # DAG path and hence the number of queries for include_all
            # _queries option
            query_count_verify = self._aed_gen_full_dagpath(nodeid)
        elif query_with_reference_to_top:
            option = 3
            # Making call to _aed_gen_queries_with_reference_to_topnode to 
            # get number of queries for nodeid, as it generates queries
            # with respect to base table/query nodes.
            query_count_verify = self._aed_gen_queries_with_reference_to_topnode(nodeid)

        # Let's validate the provided queries count.
        if query_count is not None and query_count != query_count_verify:
            # If provided and does not match with the actual one, raise exception.
            raise TeradataMlException(
                    Messages.get_message(MessageCodes.AED_QUERY_COUNT_MISMATCH, "(_aed_show_query_length)"),
                    MessageCodes.AED_QUERY_COUNT_MISMATCH)
        else:
            query_count = query_count_verify
        int_array_n = c_int * query_count
        query_sizes = int_array_n(0)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get show query size
            self.aed_context.ele_common_lib.aed_show_query_length(self.aed_context._arr_c([nodeid]), 
                                                                  c_int(option), query_sizes, ret_code)
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(_aed_show_query_length)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        query_sizes = [qry_size for qry_size in query_sizes]
        return self.aed_context._validate_aed_return_code(ret_code[0], query_sizes)

    def _aed_show_query(self, nodeid, include_all_queries = False, query_with_reference_to_top = False, query_count = None, show_query_len = None):
        """
        This wrapper function facilitates a integration of the 'aed_show_query'
        C++ function, in AED library, with Python tdml library.

        This is an internal function to get the full SQL query for a DAG node 
        representing the teradataml DataFrames and operations on them; no data is moved.

        PARAMETERS:
            nodeid:
                Required Argument.
                Specifies a DAG node for which the SQL query is to be returned.
                Types: str

            include_all_queries:
                Optional Argument.
                Specifies a boolean indicating whether to return length of individual queries or not.
                True, if length of the individual queries is required otherwise False.
                Default Value: False
                Types: bool

            query_with_reference_to_top:
                Optional Argument.
                Specifies a boolean flag indicating whether queries needs to be returned with reference
                to the top node in AED, i.e., a teradataml DataFrame created from table or query.
                Default Value: False
                Types: bool

            query_count:
                Optional Argument.
                Specifies the number of queries returned for the given nodeid.
                Default Value: None
                Types: int

            show_query_len:
                Optional Argument.
                Specifies the lengths of queries for the given nodeid.
                Default Value: None
                Types: list of ints.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")
            query = AedObj._aed_show_query(aed_filter_nodeid, include_all_queries = True, query_count = 1, show_query_len = [54])

        RETURNS:
            A list containing list of resolved SQL query/queries and list of
            nodeids.
            List of nodeids within the final list contains 0 if option chosen
            for aed_show_query is not include_all_queries option.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED, AED_NON_ZERO_STATUS, AED_NODE_QUERY_LENGTH_MISMATCH
                AED_SHOW_QUERY_MULTIPLE_OPTIONS and AED_QUERY_COUNT_MISMATCH
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_show_query.argtypes = [POINTER(c_char_p),
                                                           POINTER(c_int),
                                                           POINTER(c_char_p),
                                                           POINTER(c_char_p),
                                                           POINTER(c_int)
                                                           ]

        if include_all_queries and query_with_reference_to_top:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_SHOW_QUERY_MULTIPLE_OPTIONS, "(_aed_show_query)",
                                     "include_all_queries", "query_with_reference_to_top"),
                MessageCodes.AED_SHOW_QUERY_MULTIPLE_OPTIONS)

        # Validate the provided exec query length.
        if show_query_len is not None:
            if not isinstance(show_query_len, list) or not all(isinstance(size, int) for size in show_query_len):
                raise TypeError("AED Internal Error: 'show_query_len' should be of type list containing integers.")

        if not include_all_queries and not query_with_reference_to_top:
            # If both arguments are False then going with default option
            option = 1
            # Directly assgining 1, as only 1 query will be returned for
            # default option
            query_count_verify = 1
        elif include_all_queries:
            # If only include_all_queries is True
            option = 2
            # Making call to _aed_gen_full_dagpath to get number of
            # queries for nodeid, as it gives number of nodes in the
            # DAG path and hence the number of queries for include_all
            # _queries option
            query_count_verify = self._aed_gen_full_dagpath(nodeid)
        elif query_with_reference_to_top:
            # If only query_with_reference_to_top is True
            option = 3
            # Making call to _aed_gen_queries_with_reference_to_topnode to
            # get number of queries for nodeid, as it generates quereis
            # with respect to base table/query nodes.
            query_count_verify = self._aed_gen_queries_with_reference_to_topnode(nodeid)

        # Let's validate the provided queries count.
        if query_count is not None and query_count != query_count_verify:
            # If provided and does not match with the actual one, raise exception.
            raise TeradataMlException(
                    Messages.get_message(MessageCodes.AED_QUERY_COUNT_MISMATCH, "(_aed_show_query)"),
                    MessageCodes.AED_QUERY_COUNT_MISMATCH)
        else:
            query_count = query_count_verify

        show_query_len_verify = self._aed_show_query_length(nodeid, include_all_queries = include_all_queries, query_with_reference_to_top = query_with_reference_to_top, query_count = query_count)

        # Let's validate the provided show_query_len.
        if show_query_len is not None and show_query_len != show_query_len_verify:
            # If provided and does not match with the actual one, raise exception.
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_NODE_QUERY_LENGTH_MISMATCH, "(_aed_show_query)"
                                     + str(show_query_len) + " and " + str(show_query_len_verify)),
                MessageCodes.AED_NODE_QUERY_LENGTH_MISMATCH)
        else:
            show_query_len = show_query_len_verify

        # show_query_len contains a list of integers, for all the queries generated for given nodeid.
        # Accordingly, let's construct a query buffer.
        query_buffer = []
        for index in range(len(show_query_len)):
            query_buffer.append(" " * show_query_len[index])
        query_buffer = self.aed_context._arr_c(query_buffer)

        # Let's construct a nodeid buffer for option-2 i.e.
        # include_all_queries to match nodeids with the dataframes.
        node_id_buffer = self.aed_context._arr_c(["00000000000000000000"] * query_count)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get show_queries
            self.aed_context.ele_common_lib.aed_show_query(self.aed_context._arr_c([nodeid]),c_int(option),query_buffer,node_id_buffer,ret_code)
            # Decode UTF-8 strings
            query_buffer_out = self.aed_context._decode_list(query_buffer)
            del query_buffer
            node_id_out = self.aed_context._decode_list(node_id_buffer)
            del node_id_buffer

        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_show_query)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], [query_buffer_out, node_id_out])

    def _aed_groupby_time(self, nodeid, timebucket_duration, value_expression = '', using_timecode = '', seqno_col = '', fill = ''):
        """
        This wrapper function facilitates integration with 'aed_groupby_time',
        a C++ function in the AED library with teradataml library.

        This function must be called to specify group by time clause parameters on teradataml DataFrames 
        so that time series aggregate functions can be called on top of aed_groupby_time node.

        PARAMETERS:
            nodeid:
                A DAG node, an input to the aed_groupby_time API.

            timebucket_duration:
                Specifies the duration of each timebucket for aggregation and is used to
                assign each potential timebucket a unique number.
                Example: MINUTES(23) which is equal to 23 Minutes
                         CAL_MONTHS(5) which is equal to 5 calender months

            value_expression:
                The value_expression is a column or any expression involving columns (except for scalar subqueries).
                These expressions are used for grouping purposes not related to time.
                Example: col1

            using_timecode:
                A column expression (with an optional table name) that serves as the timecode for a non-PTI table.
                TD_TIMECODE is used implicitly for PTI tables but can also be specified explicitly by the user
                with this parameter.

            seqno_col:
                A column expression (with an optional table name) that is the sequence number. For a PTI
                table, it can be TD_SEQNO or any other column that acts as a sequence number. For a non-
                PTI table, seqno_col is a column that plays the role of TD_SEQNO (because non-PTI tables
                do not have TD_SEQNO).

            fill:
                This clause allows you to provide values for missing timebucket values.
                Possible values: NULLS, PREV / PREVIOUS, NEXT, and any numeric_constant

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_groupby_nodeid = AedObj._aed_groupby_time(aed_select_nodeid, "MINUTES(23)", "col1", "col2", "col3", "NULLS")

        RETURNS:
            A node id in DAG - AED group_by_time API.

        RAISES:
            TeradataMlException:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_groupby_time.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int)
                                                  ]

        arg_name = ["timebucket duration", "value expression", "using_timecode", "seqno_col", "fill"]
        arg_value = [timebucket_duration, value_expression, using_timecode, seqno_col, fill]
        temp_table_name = UtilFuncs._generate_temp_table_name(prefix="groupbytime_", use_default_database=True, quote=False)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to group by
            self.aed_context.ele_common_lib.aed_groupby_time(self.aed_context._arr_c([nodeid]),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           nodeid_out,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_groupby_time)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))
 
    def _aed_sample(self, nodeid, columns_expr, fracs = [], replace = False, randomize = False, case_when_then = {}, case_else = []):
        """
        This wrapper function facilitates a integration with 'aed_sample',
        a C++ function, in AED library, with Python teradataml library.

        This function must be called when a sample operation is to be performed,
        i.e. some rows are to be sampled from a teradataml DataFrame.

        PARAMETERS:
            nodeid         - A DAG node, an input to the sample API.
            columns_expr   - Columns, to be selected from the DataFrame.
                             Columns should be specified as comma seperated string.
            fracs          - This is the list of number of rows or percentage of rows 
                             in each sample.
                                Example: 
                                [0.5, 0.2, 0.1] - List of percentage of rows in each sample.
                                [10, 25, 30] - List of number of rows in each sample.
            replace        - Specifies if replacement is required or not. 
                             Boolean parameter defaults to False.
            randomize      - Specifies if randomization is required or not. 
                             Boolean parameter defaults to False.
            case_when_then - Dictionary specifying when_conditions as key and then_sample 
                             numbers as values.
                                 Example: 
                                 case_when_then = {"state = 'WI'": [0.25, 0.5], 
                                                   "state = 'CA'": 10, 
                                                   "state = 'NY'": [0.25, 0.25]}
                                 For above case_when_then, corresponding SQL query will be:
                                 'SELECT city, state, SAMPLEID 
                                  FROM stores 
                                  SAMPLE RANDOMIZED ALLOCATION 
                                  WHEN state = 'WI' THEN 0.25, 0.5 
                                  WHEN state = 'CA' THEN 10 
                                  WHEN state = 'NY' THEN 0.25, 0.25 
                                  ELSE 10 
                                  END.'

            case_else      - List specifying number of samples to be sampled when 
                             none of the conditions in key(when_conditions) of 
                             case_when_then are met.
                             For above query case_else will be like 
                             case_else = [10]

        EXAMPLES:
            aed_table_nodeid  = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_sample_nodeid = AedObj._aed_sample(aed_select_nodeid, "col1,col3", 
                                                   "100,50,70", True, False)
            
            aed_sample_nodeid = AedObj._aed_sample(aed_select_nodeid, columns_expr = 
                                                   "col1,col3", replace = True, randomize = False, 
                                                   case_when_then = {"'col1<250'&&'col2<300'": [10, 20],
                                                   "col1>250": 0.5, "col3>col1": [0.5, 0.1], "col1<col2": 10}, 
                                                   case_else = [0.5, 0.2])
            
            aed_sample_nodeid = AedObj._aed_sample(aed_select_nodeid, columns_expr = 
                                                   "col1,col3", replace = True, randomize = False, 
                                                   case_when_then = {"'col1<250'&&'col2<300'": [10, 20], 
                                                   "col1>250": 0.5, "col3>col1": [0.5, 0.1]})

        RETURNS:
            A node id in DAG - an input to AED sample API.

        RAISES:
             TeradataMLException:
                 AED_EXEC_FAILED,
                 AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_sample.argtypes =[POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_char_p),
                                                  POINTER(c_int),
                                                  POINTER(c_int)
                                                  ]

        replace = 'Y' if replace else 'N'
        randomize = 'Y' if randomize else 'N'
        
        when_list = []
        then_list = []
        for when_condition, then_sample_number in case_when_then.items():
            when_list.append(when_condition)
            then_list.append(then_sample_number)

        # when_list should be list containing strings
        if not all(isinstance(item, str) for item in when_list):
            raise TypeError(
                          Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, "Keys in case_when_then",
                          "'Strings'"), MessageCodes.UNSUPPORTED_DATATYPE)
        
        fracs_expr = ",".join(map(str, fracs))
        then_list_expr = []
        for item in then_list:
            if (isinstance(item, list)):
                then_list_expr.append(",".join(map(str, item)))
            else:
                then_list_expr.append(str(item))
        case_else_expr = ",".join(map(str, case_else))

        arg_name = ["projection", "replace", "randomize", "fracs_expr", "case_else"]
        arg_value = [columns_expr, replace, randomize, fracs_expr, case_else_expr]
        temp_table_name = UtilFuncs._generate_temp_table_name(
            prefix="sample_", use_default_database=True, quote=False, table_type=TeradataConstants.TERADATA_TABLE)
        output_table = [UtilFuncs._extract_table_name(temp_table_name)]
        output_schema = [UtilFuncs._extract_db_name(temp_table_name)]

        #Length of when list
        length_of_cond_list = self.aed_context._int_array1(len(when_list))

        # Output nodeid
        nodeid_out = self.aed_context._arr_c(["00000000000000000000"])

        # return code
        ret_code = self.aed_context._int_array1(0)
        try:
            # *** AED request to sample
            self.aed_context.ele_common_lib.aed_sample(self.aed_context._arr_c([nodeid]),
                                           self.aed_context._arr_c(arg_name),
                                           self.aed_context._arr_c(arg_value),
                                           self.aed_context._arr_c(output_table),
                                           self.aed_context._arr_c(output_schema),
                                           nodeid_out,
                                           self.aed_context._arr_c(when_list),
                                           self.aed_context._arr_c(then_list_expr),
                                           length_of_cond_list,
                                           ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_sample)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], nodeid_out[0].decode("utf-8"))

    def _aed_gen_full_dagpath(self, nodeid):
        """
        This wrapper function facilitates integration with 'aed_gen_full_dagpath',
        a C++ function, in AED library, with Python tdml library.

        This function must be called with DAG node id, when a complete DAG
        path for the node is to be generated.
        Most of the times, this api is called when user uses include_all_queries
        option to get queries, nodeid of each node in the dag path till the base or
        parent node.


        PARAMETERS:
            nodeid:
                Required Argument.
                Specifies a DAG node id for which DAG path needs to be genertaed.
                Types: str            

        EXAMPLES:
            aed_table_nodeid  = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")
            num_nodes = AedObj._aed_gen_full_dagpath(aed_filter_nodeid)

        RETURNS:
            Number of DAG nodes involved in the DAG path for the provided node ID.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_gen_full_dagpath.argtypes = [POINTER(c_char_p),
                                                         POINTER(c_int),
                                                         POINTER(c_int)
                                                         ]

        dag_node_count = self.aed_context._int_array1(0)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to generate full DAG path
            self.aed_context.ele_common_lib.aed_gen_full_dagpath(self.aed_context._arr_c([nodeid]), 
                                                                 dag_node_count, ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_gen_full_dagpath)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], dag_node_count[0])

    def _aed_gen_queries_with_reference_to_topnode(self, nodeid):
        """
        This wrapper function facilitates integration with 'aed_gen_exec_queries_with_reference_to_topnode',
        a C++ function, in AED library, with Python tdml library.

        This function must be called with DAG node id, when user wants to
        generate queries with reference to the top most node.

        Most of the times, this api is called when user uses 
        query_with_reference_to_top option in aed_show_query


        PARAMETERS:
            nodeid:
                Required Argument.
                Specifies a DAG node id for which DAG path needs to be genertaed.
                Types: str

        EXAMPLES:
            aed_table_nodeid  = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")
            num_nodes = AedObj._aed_gen_queries_with_reference_to_topnode(aed_filter_nodeid)

        RETURNS:
            Number of queries generated with reference to top node for given nodeid.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_gen_queries_with_reference_to_topnode.argtypes = [POINTER(c_char_p),
                                                         POINTER(c_int),
                                                         POINTER(c_int)
                                                         ]

        queries_count = self.aed_context._int_array1(0)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to generate queries with ref to top node
            self.aed_context.ele_common_lib.aed_gen_queries_with_reference_to_topnode(self.aed_context._arr_c([nodeid]), queries_count, ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_gen_queries_with_reference_to_topnode)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self.aed_context._validate_aed_return_code(ret_code[0], queries_count[0])

    def _aed_get_parent_node_count(self, nodeid):
        """
        This wrapper function facilitates integration with 'aed_get_parent_node_count',
        a C++ function, in AED library, with Python tdml library.

        This function must be called with DAG node id, to get number of parent nodes
        present for the given nodeid.
        Most of the times, user must call _aed_get_parent_nodeids, which will call
        this particular function too.

        PARAMETERS:
            nodeid - A DAG node id for which number of parent nodes to be determined.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")
            num_nodes = AedObj._aed_get_parent_node_count(aed_filter_nodeid)

        RETURNS:
            Number of parent nodes for the provided node ID.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_get_parent_nodes_count.argtypes = [POINTER(c_char_p),
                                                         POINTER(c_int),
                                                         POINTER(c_int)
                                                         ]
        nodes_count = self.aed_context._int_array1(0)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get number of parent nodes
            self.aed_context.ele_common_lib.aed_get_parent_nodes_count(
                                                                        self.aed_context._arr_c([nodeid]),
                                                                        nodes_count, ret_code)
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(_aed_get_parent_node_count)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)
        return self.aed_context._validate_aed_return_code(ret_code[0], nodes_count[0])


    def _aed_get_parent_nodeids(self, nodeid):
        """
        This wrapper function facilitates integration with 'aed_get_parent_nodeids',
        a C++ function, in AED library, with Python tdml library.

        This function must be called with DAG node id, to get parent nodeids
        for that node.

        PARAMETERS:
            nodeid - A DAG node id for which parent nodeids are to be returned.

        EXAMPLES:
            aed_table_nodeid = AedObj._aed_table("dbname.tablename")
            aed_select_nodeid = AedObj._aed_select(aed_table_nodeid, "col1, col2, col3")
            aed_filter_nodeid = AedObj._aed_filter(aed_select_nodeid, "col1 > col2")
            num_nodes = AedObj._aed_get_parent_nodeids(aed_filter_nodeid)

        RETURNS:
            Parent nodeids for the provided node ID.

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED and AED_NON_ZERO_STATUS
        """
        # Specify the argument types
        self.aed_context.ele_common_lib.aed_get_parent_nodeids.argtypes = [POINTER(c_char_p),
                                                         POINTER(c_char_p),
                                                         POINTER(c_int)
                                                         ]
        # Get number of parent nodes present to allocate enough memory
        number_of_parent_nodes = self._aed_get_parent_node_count(nodeid)
        parent_nodeids = self.aed_context._arr_c(["00000000000000000000"] * number_of_parent_nodes)
        ret_code = self.aed_context._int_array1(0)

        try:
            # *** AED request to get parent nodeids
            self.aed_context.ele_common_lib.aed_get_parent_nodeids(
                                                                   self.aed_context._arr_c([nodeid]),
                                                                   parent_nodeids, ret_code)
            parent_nodeids_list = self.aed_context._decode_list(parent_nodeids)
            del parent_nodeids
        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(aed_get_parent_nodeids)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)
        return self.aed_context._validate_aed_return_code(ret_code[0], parent_nodeids_list)


