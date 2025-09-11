#########################################################################
# Unpublished work.
# Copyright (c) 2020 by Teradata Corporation. All rights reserved.
# TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: trupti.purohit@teradata.com
# Secondary Owner: gouri.patwardhan@teradata.com
#
# This file creates a ApplyTableOperatorQueryGenerator class, which can
# be used to generate Apply Table Operator query for
# Open Analytics Framework.
#########################################################################

from teradataml.table_operators.table_operator_query_generator import TableOperatorQueryGenerator

class ApplyTableOperatorQueryGenerator(TableOperatorQueryGenerator):
    """
    This class creates a ApplyTableOperatorQueryGenerator object, which can be used to generate
    Apply Table Operator query for Open Analytics Framework.
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
        Constructor to instantiate 'ApplyTableOperatorQueryGenerator' class.

        PARAMETERS:
            function_name:
                Required Argument.
                Specifies the name of the function.
                Types: str

            func_input_arg_sql_names:
                Required Argument.
                Specifies the list of the input Argument names.
                Types: list of Strings (str)

            func_input_table_view_query:
                Required Argument.
                Specifies the list of the input argument values, with
                respect to 'func_input_arg_sql_names' which contains
                table_name or SQL (Select query).
                Types: list of Strings (str)

            func_input_dataframe_type:
                Required Argument.
                Specifies the list of the dataframe types for each input.
                Values can be "TABLE" or "QUERY".
                Types: list of Strings (str)

            func_input_distribution:
                Required Argument.
                Specifies the list containing distributions for each
                input.
                Permitted Values: "FACT", "HASH", "DIMENSION", "NONE"
                Types: list of Strings (str)

            func_input_partition_by cols:
                Required Argument.
                Specifies the list containing partition columns for
                each input, if distribution is FACT.
                Types: list of Strings (str)

            func_input_order_by_cols:
                Required Argument.
                Specifies the list of values, for each input, to be
                used order by clause.
                Types: list of Strings (str)

            func_other_arg_sql_names:
                Required Argument.
                Specifies the list of the other function arguments SQL
                name.
                Types: list of Strings (str)

            func_other_args_values:
                Required Argument.
                Specifies the list of the other function argument values,
                with respect to each member in 'func_other_arg_sql_names'.
                Types: list of Strings (str)

            func_other_arg_json_datatypes:
                Required Argument.
                Specifies the list of JSON datatypes for each member in
                'func_other_arg_sql_names'.
                Types: list of Strings (str)

            func_output_args_sql_names:
                Required Argument.
                Specifies the list of output SQL argument names.
                Types: list of Strings (str)

            func_output_args_values:
                Required Argument.
                Specifies the list of output table names for each
                output table argument in 'func_output_args_sql_names'.
                Types: list of Strings (str)

            func_input_order_by_type:
                Optional Argument.
                Specifies if it is 'local order by' or 'order by'.
                Types: str

            func_input_sort_ascending:
                Optional Argument.
                Specifies the order in which result sets are sorted.
                ASC means results are to be ordered in ascending sort order.
                DESC means results are to be ordered in descending sort order.
                This argument is ignored, if func_input_order_by_cols is empty.
                Default Value: ASC
                Permitted Values: ASC, DESC
                Types: str

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
                Types: str

        RETURNS:
            TableOperatorQueryGenerator object.

        RAISES:
            None

        EXAMPLES:
            apply_qg_obj = ApplyTableOperatorQueryGenerator(self.function_name,
                                                            self.input_sql_args,
                                                            self.input_table_qry,
                                                            self.input_df_type,
                                                            self.input_distribution,
                                                            self.input_partition_columns,
                                                            self.input_order_columns,
                                                            func_args_before_using_clause_names,
                                                            func_args_before_using_clause_values,
                                                            self.other_sql_args,
                                                            self.other_args_val,
                                                            self.output_sql_args,
                                                            self.output_args_val,
                                                            self.func_input_order_by_type,
                                                            self.func_input_sort_ascending,
                                                            self.func_input_nulls_first,
                                                            self.func_type,
                                                            self.engine="ENGINE_SQL")
        """
        super(ApplyTableOperatorQueryGenerator, self).__init__(function_name, func_input_arg_sql_names,
                 func_input_table_view_query, func_input_dataframe_type,
                 func_input_distribution, func_input_partition_by_cols,
                 func_input_order_by_cols,func_other_arg_sql_names,
                 func_other_args_values, func_other_arg_json_datatypes,
                 func_output_args_sql_names, func_output_args_values,
                 func_input_order_by_type, func_input_sort_ascending =func_input_sort_ascending,
                 func_input_nulls_first=func_input_nulls_first, func_type="FFE",
                 engine="ENGINE_SQL")

    def _gen_table_operator_invocation_sql(self):
        """
        DESCRIPTION:
            Function to generate a part of Apply table operator query.
            For Example,
            Apply (ON table_name AS InputTable1 Partition By col1 Order By col2
                   returns
                   Using
                   other_arguments_clause
            )

        PARAMETERS:
            None.

        RETURNS:
            An Apply Table Operator query.

        RAISES:
            None.

        EXAMPLES:
            apply_qg_obj = ApplyTableOperatorQueryGenerator(self.function_name,
                                                            self.input_sql_args,
                                                            self.input_table_qry,
                                                            self.input_df_type,
                                                            self.input_distribution,
                                                            self.input_partition_columns,
                                                            self.input_order_columns,
                                                            self.other_sql_args,
                                                            self.other_args_val,
                                                            self.output_sql_args,
                                                            self.output_args_val)
            apply_tblop_query = apply_qg_obj._gen_table_operator_invocation_sql()
        """
        # Generate other argument clauses that appear before the 'USING' keyword in the query.
        self.__ARG_BEFORE_USING_CLAUSE = self._generate_query_func_args_before_using_clause()

        # Generate other argument clauses.
        self.__OTHER_ARG_CLAUSE = self._generate_query_func_other_arg_sql()

        # Generate 'ON' clauses.
        self.__INPUT_ARG_CLAUSE = self._single_complete_table_ref_clause()

        invocation_sql = "{0}({1}".format(self._function_name, self.__INPUT_ARG_CLAUSE)
        return "{0}\n\t{1}\n\tUSING\n\t{2} \n)".format(invocation_sql,
                                                       self.__ARG_BEFORE_USING_CLAUSE,
                                                       self.__OTHER_ARG_CLAUSE)

    def _generate_query_func_args_before_using_clause(self):
        """
        DESCRIPTION:
            Function to generate clauses for the Apply table operator query that appear before
            'USING' keyword in the SQL. The function is specific to "returns" argument as of now.

        PARAMETERS:
            None.

        RAISES:
            None.

        RETURNS:
            A Apply table operator query's portion of clauses that appear before
            'USING' word.

        EXAMPLES:
        """
        args_sql_str = ""

        index = self._func_other_arg_sql_names.index('returns')

        # Default format of returns clause - returns(columnname datatype)
        # When returns argument is not specified, output column definition should be same as
        # input table schema. SQL syntax for this case is - returns *
        clause_pattern = "{0}\n\t{1} {2}" if self._func_other_args_values[index] == '*' else "{0}\n\t{1}({2})"

        # Generate the returns clause argument clause.
        args_sql_str = clause_pattern.format(args_sql_str,
                                             self._process_for_teradata_keyword(
                                             self._func_other_arg_sql_names[index]),
                                             self._func_other_args_values[index])

        # Once returns argument is processed, remove it from other arguments list so that it
        # will not be processed again.
        self._func_other_arg_sql_names.pop(index)
        self._func_other_args_values.pop(index)
        self._func_other_arg_json_datatypes.pop(index)

        self._QUERY_SIZE = self._QUERY_SIZE + self._get_string_size(args_sql_str)
        return args_sql_str
