"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements several classes for representing the input, output and other
arguments of analytic functions. These are used by IN-DB SQLE analytic framework
for parsing and storing the JSON details of each argument of each function.
File implements classes for following:
    * Analytic Function Argument Base
    * Analytic Function Input Argument
    * Analytic Function Output Argument
    * Analytic Function Other Argument
"""
import re
from teradataml.analytics.json_parser import PartitionKind
from teradataml.utils.dtypes import _Dtypes
from teradataml.utils.validators import _Validators
from teradataml.common.messages import Messages, MessageCodes
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.utils import UtilFuncs
from teradataml.analytics.json_parser import UAFJsonFields as SJF
from teradataml.dataframe.dataframe import TDSeries, TDMatrix, TDAnalyticResult, TDGenSeries


class _DependentArgument:
    """
    Class to hold the information about dependent argument.
    """
    def __init__(self, sql_name, type, operator, right_operand):
        """
        DESCRIPTION:
            Constructor for the class.

        PARAMETERS:
            sql_name:
                Required Argument.
                Specifies the name of the dependent argument in SQL.
                Types: str

            type:
                Required Argument.
                Specifies the type of the dependent argument. Dependent argument
                type can be input_tables or arguments or output_tables.
                Types: str

            operator:
                Required Argument.
                Specifies the comparision operators for dependent argument.
                Types: str

            right_operand:
                Required Argument.
                Specifies the value to be used for comparing the dependent argument
                using 'operator'.
                Types: str
        """
        self.sql_name = sql_name
        self.operator = operator
        self.right_operand = right_operand
        self.type = type

    def is_required(self, arg_value):
        """
        DESCRIPTION:
            Check if argument is required or not based on the value of dependent argument.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the value of dependent argument passed by the user.
                Types: str or int or bool or float or list

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            _DependentArgument("MethodType", "arguments", "=", "EQUAL-WIDTH").is_required("EQUAL-WIDTH")
        """
        if self.operator == "=":
            return arg_value == self.right_operand
        elif self.operator == ">=":
            return arg_value >= self.right_operand
        elif self.operator == ">":
            return arg_value > self.right_operand
        elif self.operator == "<=":
            return arg_value <= self.right_operand
        elif self.operator == "<":
            return arg_value < self.right_operand
        elif self.operator == "IN":
            return arg_value in self.right_operand
        elif self.operator == "NOT IN":
            return arg_value not in self.right_operand
        else:
            msg_code = MessageCodes.EXECUTION_FAILED
            raise TeradataMlException(
                Messages.get_message(msg_code,
                                     "parse the dependent argument '{}'".format(self.sql_name),
                                     "Operator '{}' is not implemented".format(self.operator)),
                msg_code)


class _AnlyFuncArgumentBase(object):
    """
    Class to hold the basic/common information about all the arguments.
    """
    def __init__(self, sql_name, is_required, sql_description, lang_description, lang_name, use_in_r):
        """
        DESCRIPTION:
            Constructor for the class.

        PARAMETERS:
            sql_name:
                Required Argument.
                Specifies the name of the argument in SQL.
                Types: str

            is_required:
                Required Argument.
                Specifies whether the argument is required or not.
                Types: bool

            sql_description:
                Required Argument.
                Specifies the description of argument in SQL.
                Types: str

            lang_description:
                Required Argument.
                Specifies the description of the argument, which needs to be exposed
                to user.
                Types: str

            lang_name:
                Required Argument.
                Specifies the name of the argument to be exposed to user.
                Types: str

            use_in_r:
                Required Argument.
                Specifies whether argument should be used in client or not.
                Types: bool
        """
        self.__sql_name = sql_name
        self.__is_required = is_required
        self.__sql_description = sql_description
        self.__description = lang_description
        self.__name = lang_name
        self.__use_in_r = use_in_r

        awu_matrix = []
        awu_matrix.append(["sql_name", sql_name, False, (str,), True])
        awu_matrix.append(["is_required", is_required, False, (bool,)])
        awu_matrix.append(["sql_description", sql_description, False, (str,), True])
        awu_matrix.append(["lang_description", lang_description, False, (str,), True])
        awu_matrix.append(["lang_name", lang_name, False, (str,), True])
        awu_matrix.append(["use_in_r", use_in_r, False, (bool,)])

        # Validate argument types.
        _Validators._validate_function_arguments(awu_matrix)
        self.is_empty_value_allowed = lambda: True
        self.is_output_column = lambda: False
        self.get_r_default_value = lambda: None

    # Getters
    def get_sql_name(self):
        """
        DESCRIPTION:
            Get SQL name of the argument.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Get the argument name used in SQL Query.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            argument_base.get_sql_name()
        """
        return self.__sql_name

    def is_required(self):
        """
        DESCRIPTION:
            Check if argument is required or not.

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            # Check whether the argument is a mandatory or not for Analytic function.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            if argument_base.is_required():
                print("Required")
        """
        return self.__is_required

    def get_sql_description(self):
        """
        DESCRIPTION:
            Get SQL description of the argument.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Get the description of the argument with respect to SQL.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            argument_base.get_sql_description()
        """
        return self.__sql_description

    def get_lang_description(self):
        """
        DESCRIPTION:
            Get client specific description name of the argument.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Get the description of the argument with respect to Python.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            argument_base.get_lang_description()
        """
        return self.__description

    def get_lang_name(self):
        """
        DESCRIPTION:
            Get client specific name of the argument.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Get the argument name, which is exposed to user.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            argument_base.get_lang_name()
        """
        return self.__name

    def use_in_r(self):
        """
        DESCRIPTION:
            Check if argument should be used in client function or not.

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Check whether argument is used in R or not.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            if argument_base.use_in_r():
                print("Yes")
        """
        return self.__use_in_r

    @staticmethod
    def get_regex_sql_name(sql_name, match_name, arg_names):
        """
        DESCRIPTION:
            Get SQL name of the argument by matching the given pattern.

        PARAMETERS:
            sql_name:
                Required Argument.
                Specifies the name of the argument in SQL.
                Types: str

            match_name:
                Required Argument.
                Specifies the match name which will be replaced
                by the SQL name.
                Types: str

            arg_names:
                Required Argument.
                Specifies the list of python argument name.
                Types: list

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            # Get the argument name used in SQL Query.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            argument_base.get_regex_sql_name("Abc_*", "const_", ["const_num", "const_min_length"])
        """
        sql_names = [key.replace(match_name, sql_name)
                     for key in arg_names if key.startswith(match_name)]

        return sql_names

    @staticmethod
    def get_regex_matched_arguments(arg_name, **kwargs):
        """
        DESCRIPTION:
            Get client specific name of the argument by matching given pattern.

        PARAMETERS:
            arg_name:
                Required Argument.
                Specifies the name of the argument.
                Types: list

            kwargs:
                Required Argument.
                Specifies the user provided arguments.
                Types: dict

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            # Get the argument name, which is exposed to user.
            from teradataml.analytics.json_parser.argument import _AnlyFuncArgumentBase
            argument_base = _AnlyFuncArgumentBase("sql_name", True, "SQL Description", "Python Description", "name", True)
            argument_base.get_regex_matched_arguments("const_*", newdata=DataFrame(df), const_num=2, const_min_length=81)
        """
        pattern = re.compile("{}{}".format('^', arg_name))
        arg_names = [key for key in kwargs if pattern.match(key)]

        return arg_names

class _AnlyFuncInput(_AnlyFuncArgumentBase):
    """
    Class to hold the information about input argument.
    """

    def __init__(self,
                 sql_name,
                 is_required,
                 sql_description,
                 lang_description,
                 lang_name,
                 use_in_r,
                 r_order_num,
                 datatype="TABLE_NAME",
                 required_input_kind=None,
                 partition_by_one=False,
                 partition_by_one_inclusive=False,
                 is_ordered=False,
                 is_local_ordered=False,
                 hash_by_key=False,
                 allows_lists=False,
                 r_formula_usage=False,
                 alternate_sql_name=None):
        """
        Constructor for generating an object of Analytic Function Argument from
        JSON for arguments accepting input table.

        PARAMETERS:
            sql_name:
                Required Argument.
                Specifies the name of the argument in SQL.
                Types: str

            is_required:
                Required Argument.
                Specifies whether the argument is required or not.
                Types: bool

            sql_description:
                Required Argument.
                Specifies the description of argument in SQL.
                Types: str

            lang_description:
                Required Argument.
                Specifies the description of the argument, which needs to be exposed
                to user.
                Types: str

            lang_name:
                Required Argument.
                Specifies the name of the argument to be exposed to user.
                Types: str

            use_in_r:
                Required Argument.
                Specifies whether argument should be used in client or not.
                Types: bool

            r_order_num:
                Required Argument.
                Specifies the ordering sequence of the argument for R function call.
                Types: integer

            datatype:
                Optional Argument.
                Specifies the datatype for output table.
                Permitted Values: table_name, table_alias
                Default Value: table_name
                Types: str

            required_input_kind:
                Optional Argument.
                Specifies the kind of input.
                Permitted Values: partition_by_key, partition_by_any, or dimension
                Default Value: None
                Types: str or list of str

            partition_by_one:
                Optional Argument.
                Specifies that for partition_by_key input kind, the key should be
                "Partition by 1". If this argument is set to true and
                "partition_by_one_inclusive" is set to False, the function only accepts
                "Partition by 1" but not "Partition by key".
                Default Value: False
                Types: bool

            partition_by_one_inclusive:
                Optional Argument.
                Specifies that for partition_by_key input kind, the function accepts both
                "Partition by 1" and "Partition by key". This argument can be set to True
                only if "required_input_kind" has partition_by_key, partition_by_any.
                Default Value: False
                Types: bool

            is_ordered:
                Optional Argument.
                Specifies that the table must be input with an "Order by" clause.
                Default Value: False
                Types: bool

            is_local_ordered:
                Optional Argument.
                Specifies whether the table supports LOCAL ORDER BY clause or not.
                Default Value: False
                Types: bool

            hash_by_key:
                Optional Argument.
                Specifies whether data is grouped according to the HASH BY clause.
                Default Value: False
                Types: bool

            allow_lists:
                Optional Argument.
                Specifies whether the argument accepts list of values. If false, the
                argument can only accept a single value.
                Default Value: False
                Types: bool

            r_formula_usage:
                Optional Argument.
                Specifies if the argument contains a formula.
                Default Value: False
                Types: bool

            alternate_sql_name:
                Optional Argument.
                Specifies alternate names for the argument.
                Default Value: None
                Types: str or list of str
        """

        # Call Abstract class constructor
        super().__init__(sql_name, is_required, sql_description, lang_description,
                         lang_name,
                         use_in_r)

        # Process other parameters of input table argument.
        self.__required_input_kind = required_input_kind
        self.__partition_by_one = partition_by_one
        self.__partition_by_one_inclusive = partition_by_one_inclusive
        self.__is_ordered = is_ordered
        self.__is_local_ordered = is_local_ordered
        self.__hash_by_key = hash_by_key
        self.__datatype = datatype
        self.__allows_lists = allows_lists
        self.__r_formula_usage = r_formula_usage
        self.__r_order_num = r_order_num
        self.__alternate_sql_name = alternate_sql_name

        # Create argument information matrix to do parameter checking
        self.__arg_info_matrix = []
        required_input_kind_permitted_values = ["PartitionByKey", "PartitionByAny", "Dimension"]
        self.__arg_info_matrix.append(
            ["required_input_kind", self.__required_input_kind, True, (list, str), True,
             required_input_kind_permitted_values])
        self.__arg_info_matrix.append(
            ["partition_by_one", self.__partition_by_one, True, (bool)])
        self.__arg_info_matrix.append(
            ["partition_by_one_inclusive", self.__partition_by_one_inclusive, True, (bool)])
        self.__arg_info_matrix.append(["is_ordered", self.__is_ordered, True, (bool)])
        self.__arg_info_matrix.append(["is_local_ordered", self.__is_local_ordered, True, (bool)])
        self.__arg_info_matrix.append(["hash_by_key", self.__hash_by_key, True, (bool)])
        self.__arg_info_matrix.append(
            ["datatype", self.__datatype, False, (str), True, ["table_name", "table_alias"]])
        self.__arg_info_matrix.append(["r_order_num", self.__r_order_num, False, (int), True])
        self.__arg_info_matrix.append(["allows_lists", self.__allows_lists, True, (bool)])
        self.__arg_info_matrix.append(["alternate_sql_name", self.__alternate_sql_name, True, (list, str)])
        self.__arg_info_matrix.append(["r_formula_usage", self.__r_formula_usage, True, (bool)])
        # Perform the function validations
        self.__validate()
        self.get_default_value = lambda: None
        self.get_permitted_values = lambda: None
        self._only_partition_by_one = lambda: \
            self.__partition_by_one and not self.__partition_by_one_inclusive

    def __validate(self):
        """
        DESCRIPTION:
            Function to validate arguments, which verifies missing arguments,
            input argument.
        """
        # Validate argument types.
        _Validators._validate_function_arguments(self.__arg_info_matrix)

    # Getters.
    def get_required_input_kind(self):
        """
        DESCRIPTION:
        Function to get the required_input_kind argument.
        """
        return self.__required_input_kind

    def get_python_type(self):
        """
        DESCRIPTION:
            Function to get the python type of argument.
        """
        from teradataml.dataframe.dataframe import DataFrame
        return DataFrame

    def is_reference_function_acceptable(self):
        """
        DESCRIPTION:
            Function to check if argument accepts reference function name or not.
        """
        return self.get_lang_name().lower() in ("object", "modeldata")

    def is_partition_by_one(self):
        """
        DESCRIPTION:
            Function to check whether partition_by_one is True or False.
        """
        return self.__partition_by_one

    def is_partition_by_one_inclusive(self):
        """
        DESCRIPTION:
            Function to check whether partition_by_one_inclusive is True or False.
        """
        return self.__partition_by_one_inclusive

    def is_ordered(self):
        """
        DESCRIPTION:
            Function to check whether input table has an order by clause.
        """
        return self.__is_ordered

    def is_local_ordered(self):
        """
        DESCRIPTION:
            Check whether input supports LOCAL ORDER BY clause or not.
        """
        return self.__is_local_ordered

    def hash_by_key(self):
        """
        DESCRIPTION:
            Check whether input supports HASH BY KEY clause or not.
        """
        return self.__hash_by_key

    def get_data_type(self):
        """
        DESCRIPTION:
             Function to get the datatype of the argument.
        """
        return self.__datatype

    def allows_lists(self):
        """
        DESCRIPTION:
            Function to check if argument accepts lists or not.
        """
        return self.__allows_lists

    def get_r_formula_usage(self):
        """
        DESCRIPTION:
            Function to check if argument is part of a formula or not.
        """
        return self.__r_formula_usage

    def get_r_order_number(self):
        """
        DESCRIPTION:
            Function to get the order number of the argument.
        """
        return self.__r_order_num

    def get_alternate_sql_name(self):
        """
        DESCRIPTION:
            Function to get the alternate SQL name of the argument.
        """
        return self.__alternate_sql_name

    def _get_partition_column_required_kind(self):
        """
        DESCRIPTION:
            Function to determine if the input table is partitioned by a column or ANY or 1
            or data distribution is DIMENSION. This function follows below steps and derives
            partition column kind.
                * The input_table is partitioned by a key, if requireInputKind == PartitionByKey
                  and partitionByOne == False.
                * The input_table is partitioned by 1/key, if requireInputKind == PartitionByKey,
                  partitionByOneInclusive == True and partitionByOne == True.
                * The input_table is partitioned by 1 only, if partitionByOneInclusive == False
                  and partitionByOne=true.
                * The input_table is partitioned by ANY/key, if requireInputKind == PartitionByKey
                  and requireInputKind == PartitionByAny.
                * The input_table is partitioned by ANY only, if requireInputKind == PartitionByAny.
                * The input_table is distributed by either DIMENSION or partitioned by key, if
                  requireInputKind == PartitionByKey and requireInputKind == DIMENSION.
                * The input_table is distributed by either DIMENSION or partitioned by ANY/key, if
                  requireInputKind == PartitionByKey and requireInputKind == PartitionByAny and
                  requireInputKind == DIMENSION.

        RAISES:
            None

        RETURNS:
            enum of type teradataml.analytics.json_parser.PartitionKind

        EXAMPLES:
            self._get_partition_column_required_kind()
        """
        is_partition_by_key, is_partition_by_any, is_partition_by_one, is_dimension = [False]*4

        # Input table is partitioned by 1 ONLY when partitionByOneInclusive is false and
        # partitionByOne is true.
        if self.__partition_by_one and not self.__partition_by_one_inclusive:
            is_partition_by_one = True
        else:
            for input_kind in self.__required_input_kind:
                if input_kind == "Dimension":
                    is_dimension = True
                # If requiredInputKind has PartitionByKey and partitionByOneInclusive and
                # partitionByOne is True then input table is partitioned by 1 or Key.
                # Else input table is partitioned by Key Only.
                elif input_kind == "PartitionByKey":
                    if self.__partition_by_one_inclusive and self.__partition_by_one:
                        is_partition_by_one = True
                        is_partition_by_key = True
                    else:
                        is_partition_by_key = True
                elif input_kind == "PartitionByAny":
                    is_partition_by_any = True

        if is_dimension:
            if is_partition_by_key and is_partition_by_any:
                return PartitionKind.DIMENSIONKEYANY
            elif is_partition_by_key and not is_partition_by_any:
                return PartitionKind.DIMENSIONKEY
            else:
                return PartitionKind.DIMENSION
        else:
            if is_partition_by_key and not is_partition_by_any and not is_partition_by_one:
                return PartitionKind.KEY
            elif is_partition_by_key and is_partition_by_any:
                return PartitionKind.ANY
            elif not is_partition_by_key and is_partition_by_any:
                return PartitionKind.ANYONLY
            elif is_partition_by_one and is_partition_by_key:
                return PartitionKind.ONE
            elif is_partition_by_one and is_partition_by_key:
                return PartitionKind.ONEONLY

    def _get_default_partition_column_kind(self):
        """ Returns the default Parition Type based on requiredInputKind parameter in json file. """
        required_column_kind = UtilFuncs._as_list(self.__required_input_kind)[0]

        if required_column_kind == "PartitionByAny":
            return PartitionKind.ANY
        elif required_column_kind == "Dimension":
            return PartitionKind.DIMENSION
        elif required_column_kind == "PartitionByOne":
            return PartitionKind.ONE
        else:
            return None

    '''
    @staticmethod
    def _get_default_partition_by_value(partition_kind):
        """
        DESCRIPTION:
            Function to get the default value for partition column kind.

        PARAMETERS:
            partition_kind:
                Required Argument.
                Specifies input table partition type.

        RAISES:
            None

        RETURNS:
            str OR int

        EXAMPLES:
            self._get_default_partition_by_value(PartitionKind.KEY)
        """
        if partition_kind == PartitionKind.KEY or partition_kind == PartitionKind.DIMENSIONKEY:
            return None
        elif partition_kind == PartitionKind.ONE or partition_kind == PartitionKind.ONEONLY:
            return 1
        elif partition_kind == PartitionKind.ANY or partition_kind == PartitionKind.ANYONLY or \
                partition_kind == PartitionKind.DIMENSIONKEYANY:
            return "ANY"
    '''

    def _only_partition_by_any(self):
        """
        DESCRIPTION:
            Check partition column supports only Partition By Any.

        RAISES:
            None

        RETURNS:
            bool

        EXAMPLES:
            self._only_partition_by_any()
        """
        if isinstance(self.__required_input_kind, str):
            return self.__required_input_kind == "PartitionByAny"
        return self.__required_input_kind == ["PartitionByAny"]


class _AnlyFuncOutput(_AnlyFuncArgumentBase):
    """
    Class to hold the information about output argument.
    """

    def __init__(self,
                 sql_name,
                 is_required,
                 sql_description,
                 lang_description,
                 lang_name,
                 use_in_r,
                 r_order_num,
                 datatype="TABLE_NAME",
                 is_output_table=True,
                 allows_lists=False,
                 output_schema=None,
                 alternate_sql_name=None,
                 support_volatility=False,
                 is_required_dependent_argument=None):
        """
        Constructor for generating an object of Analytic Function Argument from
        JSON for arguments accepting output table information.

        PARAMETERS:
            sql_name:
                Required Argument.
                Specifies the name of the argument in SQL.
                Types: str

            is_required:
                Required Argument.
                Specifies whether the argument is required or not.
                Types: bool

            sql_description:
                Required Argument.
                Specifies the description of argument in SQL.
                Types: str

            lang_description:
                Required Argument.
                Specifies the description of the argument, which needs to be exposed
                to user.
                Types: str

            lang_name:
                Required Argument.
                Specifies the name of the argument to be exposed to user.
                Types: str

            use_in_r:
                Required Argument.
                Specifies whether argument should be used in client or not.
                Types: bool

            r_order_num:
                Required Argument.
                Specifies the ordering sequence of the argument for R function call.
                Types: integer

            datatype:
                Optional Argument.
                Specifies the datatype for output table.
                Permitted Values: table_name, table_alias
                Default Value: table_name
                Types: str

            is_output_table:
                Optional Argument.
                Specifies whether the argument clause has an output table name.
                Default Value: True
                Types: bool

            allow_lists:
                Optional Argument.
                Specifies whether the argument accepts list of values. If false, the
                argument can only accept a single value.
                Default Value: False
                Types: bool

            output_schema:
                Optional Argument.
                Specifies the output schema of the function.
                Default Value: None
                Types: str

            alternate_sql_name:
                Optional Argument.
                Specifies alternate names for the argument.
                Default Value: None
                Types: str or list of str

            support_volatility:
                Optional Argument.
                Specifies whether the output table support VOLATILE table or not.
                Default Value: False
                Types: bool
        """

        # Call super class constructor to initialize basic parameters.
        super().__init__(sql_name, is_required, sql_description, lang_description,
                         lang_name,
                         use_in_r)

        self.__r_order_num = r_order_num
        self.__allows_lists = allows_lists
        self.__output_schema = output_schema
        self.__alternate_sql_name = alternate_sql_name
        self.__is_output_table = is_output_table
        self.__datatype = datatype
        self.__support_volatility = support_volatility
        # Create argument information matrix to do parameter checking
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["r_order_num", self.__r_order_num, False, int, True])
        self.__arg_info_matrix.append(["allows_lists", self.__allows_lists, True, bool])
        self.__arg_info_matrix.append(["output_schema", self.__output_schema, True, str, True])
        self.__arg_info_matrix.append(["alternate_sql_name", self.__alternate_sql_name, True, (list, str)])
        self.__arg_info_matrix.append(["is_output_table", self.__is_output_table, True, bool])
        self.__arg_info_matrix.append(
            ["datatype", self.__datatype, True, str, True, ["table_name", "table_alias"]])
        self.__arg_info_matrix.append(["support_volatility", self.__support_volatility, True, bool])
        self.__arg_info_matrix.append(
            ["is_required_dependent_argument", is_required_dependent_argument, True, _DependentArgument])

        # Perform the function validations
        self.__validate()
        self.is_volatility_supported = lambda : self.__support_volatility
        self.get_is_required_dependent_argument = lambda : is_required_dependent_argument

    def __validate(self):
        """
        DESCRIPTION:
            Function to validate arguments, which verifies missing arguments,
            input argument.
        """
        # Validate argument types.
        _Validators._validate_function_arguments(self.__arg_info_matrix)

    # Getters
    def get_data_type(self):
        """
        DESCRIPTION:
             Function to get the datatype of the argument.
        """
        return self.__datatype

    def is_output_table(self):
        """
        DESCRIPTION:
            Function to check if argument represents output table or not.
        """
        return self.__is_output_table

    def get_r_order_number(self):
        """
        DESCRIPTION:
            Function to get the order number of the argument.
        """
        return self.__r_order_num

    def allows_lists(self):
        """
        DESCRIPTION:
            Function to check if argument accepts lists or not.
        """
        return self.__allows_lists

    def get_output_schema(self):
        """
        DESCRIPTION:
            Function to get the output schema of the argument.
        """
        return self.__output_schema

    def get_alternate_sql_name(self):
        """
        DESCRIPTION:
            Function to get the alternate SQL name of the argument.
        """
        return self.__alternate_sql_name


class _AnlyFuncArgument(_AnlyFuncArgumentBase):
    """
    Class to hold the information about analytic function argument.
    """

    def __init__(self,
                 sql_name,
                 is_required,
                 sql_description,
                 lang_description,
                 lang_name,
                 use_in_r,
                 r_order_num,
                 datatype,
                 default_value=None,
                 permitted_values=None,
                 lower_bound=None,
                 lower_bound_type=None,
                 upper_bound=None,
                 upper_bound_type=None,
                 allow_nan=False,
                 required_length=0,
                 match_length_of_argument=None,
                 allows_lists=False,
                 allow_padding=False,
                 r_formula_usage=False,
                 r_default_value=None,
                 target_table=None,
                 target_table_lang_name=None,
                 check_duplicate=False,
                 allowed_types=None,
                 allowed_type_groups=None,
                 is_output_column=False,
                 alternate_sql_name=None,
                 regex_match=False,
                 match_name=None):
        """
        Constructor for generating an object of Analytic Function Argument from
        JSON for other arguments.

        PARAMETERS:
            sql_name:
                Required Argument.
                Specifies the name of the argument in SQL.
                Types: str

            is_required:
                Required Argument.
                Specifies whether the argument is required or not.
                Types: bool

            sql_description:
                Required Argument.
                Specifies the description of argument in SQL.
                Types: str

            lang_description:
                Required Argument.
                Specifies the description of the argument, which needs to be exposed
                to user.
                Types: str

            lang_name:
                Required Argument.
                Specifies the name of the argument to be exposed to user.
                Types: str

            use_in_r:
                Required Argument.
                Specifies whether argument should be used in client or not.
                Types: bool

            r_order_num:
                Required Argument.
                Specifies the ordering sequence of the argument.
                Types: integer

            datatype:
                Required Argument.
                Specifies the datatype for argument.
                Types: str OR list of str

            default_value:
                Optional Argument.
                Specifies the default value for argument.
                Types: str OR int OR float OR bool

            permitted_values:
                Optional Argument.
                Specified the permitted values for argument.
                Types: list OR str OR float OR int

            lower_bound:
                Optional Argument.
                Specifies the lower bound value for argument.
                Types: int OR float

            lower_bound_type:
                Optional Argument.
                Specifies whether "lower_bound" is inclusive or exclusive.
                Permitted Values: INCLUSIVE, EXCLUSIVE
                Types: str

            upper_bound:
                Optional Argument.
                Specifies the upper bound value for argument.
                Types: int OR float

            upper_bound_type:
                Optional Argument.
                Specifies whether "upper_bound" is inclusive or exclusive.
                Permitted Values: INCLUSIVE, EXCLUSIVE
                Types: str

            allow_nan:
                Optional Argument.
                Specifies whether argument accepts None or not.
                Default Value: False
                Types: bool

            allows_lists:
                Optional Argument.
                Specifies whether argument accepts a list of values or not.
                Default Value: False
                Types: bool

            match_length_of_argument:
                Optional Argument.
                Specifies whether length of "allow_lists" should be checked or not.
                Default Value: False
                Types: bool

            required_length:
                Optional Argument.
                Specifies if the list must be the same length as the list specified
                in argument clause.
                Default Value: 0
                Types: int

            allow_padding:
                Optional Argument.
                Specifies whether to add padding to argument or not. When set to True,
                user submitted value will be padded into a list equal to the required
                length.
                Default Value: False
                Types: bool

            r_formula_usage:
                Optional Argument.
                Specifies whether argument is part of formula.
                Default Value: False
                Types: bool

            r_default_value:
                Optional Argument.
                Specifies the default value of the argument.
                Types: str OR int OR float

            target_table:
                Optional Argument.
                Specifies the name of the input table that the input column
                should be found in (Only applicable for datatype COLUMNS or COLUMN_NAMES)
                Types: str OR list of str

            target_table_lang_name:
                Optional Argument.
                Specifies the lang name of the input table that the input column
                should be found in (Only applicable for datatype COLUMNS or COLUMN_NAMES)
                Types: str

            check_duplicate:
                Optional Argument.
                Specifies whether duplicate columns should be checked in input
                or not (Only applicable for datatype COLUMNS or COLUMN_NAMES).
                Default Value: False
                Types: bool

            allowed_types:
                Optional Argument.
                Specifies SQL types that are allowed (Only applicable for datatype
                COLUMNS or COLUMN_NAMES).
                Types: str OR list of str

            allowed_type_groups:
                Optional Argument.
                Species the group of SQL types that are allowed.
                    * NUMERIC for all numeric types.
                    * STRING for all char/varchar types.
                    * GROUPTYPE for any type except double or float.
                Types: list of str

            is_output_column:
                Optional Argument.
                Specifies whether argument is output column or not.
                Default Value: False
                Types: bool

            alternate_sql_name:
                Optional Argument.
                Specifies alternate names for the argument.
                Types: str or list of str

            regex_match:
                Optional Argument.
                Specifies whether argument is regular expression or not.
                Default Value: False
                Types: bool

            match_name:
                Optional Argument.
                Specifies the name to match against the user provided arguments.
                Types: str
        """

        # Call super class constructor to initialize basic parameters.
        super().__init__(sql_name, is_required, sql_description, lang_description, lang_name, use_in_r)

        # Initialize rest of the parameters for the Arguments class.
        self.__default_value = default_value
        self.__permitted_values = permitted_values
        self.__lower_bound = lower_bound
        self.__lower_bound_type = lower_bound_type
        self.__upper_bound = upper_bound
        self.__upper_bound_type = upper_bound_type
        self.__allow_nan = allow_nan
        self.__required_length = required_length
        self.__match_length_of_argument = match_length_of_argument
        self.__datatype = datatype
        self.__allows_lists = allows_lists
        self.__allow_padding = allow_padding
        self.__r_formula_usage = r_formula_usage
        self.__r_default_value = r_default_value
        self.__target_table = target_table
        self.__target_table_lang_name = target_table_lang_name
        self.__check_duplicate = check_duplicate
        self.__allowed_types = allowed_types
        self.__allowed_type_groups = allowed_type_groups
        self.__r_order_num = r_order_num
        self.__is_output_column = is_output_column
        self.__alternate_sql_name = alternate_sql_name
        self.__regex_match = regex_match
        self.__match_name = match_name

        awu_matrix = []
        awu_matrix.append(["r_order_num", r_order_num, False, int])
        awu_matrix.append(["datatype", datatype, False, (list, str), True])
        awu_matrix.append(["default_value", default_value, True, (int, str, bool, float)])
        awu_matrix.append(["permitted_values", permitted_values, True, (list, str, int, float)])
        awu_matrix.append(["lower_bound", lower_bound, True, (int, float)])
        awu_matrix.append(["lower_bound_type", lower_bound_type, True, str, True, ["INCLUSIVE", "EXCLUSIVE"]])
        awu_matrix.append(["upper_bound", upper_bound, True, (int, float)])
        awu_matrix.append(["upper_bound_type", upper_bound_type, True, str, True, ["INCLUSIVE", "EXCLUSIVE"]])
        awu_matrix.append(["allow_nan", allow_nan, True, bool])
        awu_matrix.append(["allows_lists", allows_lists, True, bool])
        awu_matrix.append(["match_length_of_argument", match_length_of_argument, True, bool])
        awu_matrix.append(["required_length", required_length, True, int])
        awu_matrix.append(["allow_padding", allow_padding, True, bool])
        awu_matrix.append(["r_formula_usage", r_formula_usage, True, bool])
        awu_matrix.append(["r_default_value", r_default_value, True, (int, float, str)])
        awu_matrix.append(["target_table", target_table, True, (list, str)])
        awu_matrix.append(["target_table_lang_name", target_table_lang_name, True, str])
        awu_matrix.append(["check_duplicate", check_duplicate, True, bool])
        awu_matrix.append(["allowed_types", allowed_types, True, (list, str)])
        awu_matrix.append(["allowed_type_groups", allowed_type_groups, True, (list, str)])
        awu_matrix.append(["is_output_column", is_output_column, True, bool])
        awu_matrix.append(["alternate_sql_name", alternate_sql_name, True, (list, str)])
        awu_matrix.append(["regex_match", regex_match, True, bool])
        awu_matrix.append(["match_name", match_name, True, str, True])

        # Validate argument types.
        _Validators._validate_function_arguments(awu_matrix)

        # Validate lower bound is greater than upper bound.
        # _validate_argument_range validates whether lower bound is less than upper bound
        # or not if argument is None.
        _Validators._validate_argument_range(
            arg_name="dummy", arg=None, lbound=self.__lower_bound, ubound=self.__upper_bound)

        # Getters.
        self.get_r_order_number = lambda: self.__r_order_num
        self.get_data_type = lambda: self.__datatype
        self.get_default_value = lambda: self.__default_value
        self.get_permitted_values = lambda: self.__permitted_values
        self.get_lower_bound = lambda: self.__lower_bound
        self.get_lower_bound_type = lambda: self.__lower_bound_type
        self.get_upper_bound = lambda: self.__upper_bound
        self.get_upper_bound_type = lambda: self.__upper_bound_type
        self.is_nan_allowed = lambda: self.__allow_nan
        self.get_required_length = lambda: self.__required_length
        self.get_match_length_of_argument = lambda: self.__match_length_of_argument
        self.is_lists_allowed = lambda: self.__allows_lists
        self.is_padding_required = lambda: self.__allow_padding
        self.is_argument_a_formula = lambda: self.__r_formula_usage
        self.get_r_default_value = lambda: self.__r_default_value
        self.get_target_table = lambda: self.__target_table
        self.get_target_table_lang_name = lambda: self.__target_table_lang_name
        self.check_duplicate = lambda: self.__check_duplicate
        self.get_allowed_types = lambda: self.__allowed_types
        self.get_allowed_type_groups = lambda: self.__allowed_type_groups
        self.is_output_column = lambda: self.__is_output_column
        self.get_alternate_sql_name = lambda: self.__alternate_sql_name
        self.is_empty_value_allowed = lambda: not self.is_column_argument()
        self.regex_match = lambda: self.__regex_match
        self.match_name = lambda: self.__match_name

    def get_python_type(self):
        """
        DESCRIPTION:
            Get equivalent Python type for the JSON datatype for an argument.

        PARAMETERS:
            None

        RETURNS:
            type.

        RAISES:
            None

        EXAMPLES:
            self.get_python_type(arg1="string", arg2="db", arg3=2)
        """
        py_types = tuple()

        # If multiple datatype's allowed, return the tuple of all allowed python types.
        if isinstance(self.__datatype, list):
            for td_type in self.__datatype:
                py_type = _Dtypes._anly_json_type_to_python_type(td_type)

                # If py_type is not a tuple, convert to a tuple.
                py_types = py_types + ((py_type, ) if not isinstance(py_type, tuple) else py_type)
        else:
            py_type = _Dtypes._anly_json_type_to_python_type(self.__datatype)
            py_types = py_type if isinstance(py_type, tuple) else (py_type, )

        # If lists are allowed, add list type also.
        if self.__allows_lists and (list not in py_types):
            py_types = py_types + (list, )

        return  py_types

    def is_column_argument(self):
        """
        DESCRIPTION:
            Function checks if the argument accepts column as input or not.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            self.is_column_argument()
        """
        # __datatype can be either string or list.
        if isinstance(self.__datatype, list):
            datatype = (datatype.lower() for datatype in self.__datatype)
        else:
            datatype = self.__datatype.lower()
        return "column" in datatype


class _AnlyFuncArgumentBaseUAF(object):
    """ Class to hold the basic/common information about all the arguments."""
    def __init__(self, data_type, description, lang_name, is_required=False):
        """
        DESCRIPTION:
            Constructor for the class.

        PARAMETERS:
             data_type:
                 Required Argument.
                 Specifies the data type an argument can accept.
                 Type: str

             description:
                 Required Argument.
                 Specifies the argument description.
                 Type: str or List

             lang_name:
                 Required Argument.
                 Specifies the name of the argument to be exposed to user.
                 Type: str

            is_required:
                Optional Argument.
                Specifies whether the argument is required or not.
                Default Value: False
                Types: bool

        """
        self.__data_type = data_type
        self.__description = description
        self.__lang_name = lang_name
        self.__is_required = is_required

        # Getters
        self.get_data_type = lambda: self.__data_type
        self.get_description = lambda: self.__description
        self.get_lang_name = lambda: self.__lang_name
        self.is_required = lambda: self.__is_required
        self.is_empty_value_allowed = lambda: True
        self.is_output_column = lambda: False
        self.get_r_default_value = lambda: None

        # Validation
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["type", self.__data_type, False, (list, str), True])
        self.__arg_info_matrix.append(["description", self.__description, False, (list, str)])
        self.__arg_info_matrix.append(["lang_name", self.__lang_name, False, str])
        self.__arg_info_matrix.append(["optional", self.__is_required, True, bool])

        _Validators._validate_function_arguments(self.__arg_info_matrix)
        self.is_empty_value_allowed = lambda: True
        self.is_output_column = lambda: False
        self.get_permitted_values = lambda: None

        # Combining list to string.
        self.__description = ''.join(description)

    def is_column_argument(self):
        """
        DESCRIPTION:
            Function checks if the argument accepts column as input or not.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            self.is_column_argument()
        """
        # __datatype can be either string or list.
        if isinstance(self.__data_type, list):
            datatype = (datatype.lower() for datatype in self.__data_type)
        else:
            datatype = self.__data_type.lower()
        return "column" in datatype

    def get_python_type(self):
        """
        DESCRIPTION:
            Get equivalent Python type for the JSON datatype for an argument.

        PARAMETERS:
            None

        RETURNS:
            type.

        RAISES:
            None

        EXAMPLES:
            self.get_python_type(arg1="string", arg2="db", arg3=2)
        """
        py_types = tuple()
        supp_data_types = UtilFuncs._as_list(self.__data_type)
        # If multiple datatype's allowed, return the tuple of all allowed Python types.
        for td_type in supp_data_types:
            py_type = _Dtypes._anly_json_type_to_python_type(td_type)

            # If py_type is not a tuple, convert to a tuple.
            py_types = py_types + ((py_type,) if not isinstance(py_type, tuple) else py_type)

        # If lists are allowed, add list type also.
        if self.is_lists_allowed() and (list not in py_types):
            py_types = py_types + (list,)
        return py_types
    
    def set_is_required(self, value):
        """
        DESCRIPTION:
            Setter function to set if argument is required or not.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            self.set_is_required(True)
        """
        self.__is_required = value


class _AnlyFuncInputUAF(_AnlyFuncArgumentBaseUAF):
    """ Class to hold the information about input argument of UAF."""
    def __init__(self, data_type, description, lang_name, is_required=False):
       """
        DESCRIPTION:
           Constructor for the class.

        PARAMETERS:
            data_type:
                Required Argument.
                Specifies the data type an input argument can accept.
                Type: str

            description:
                Required Argument.
                Specifies the input argument description.
                Type: Str or List

            lang_name:
                Required Argument.
                Specifies the name of the argument to be exposed to user.
                Type: str

            is_required:
                Optional Argument.
                Specifies whether the argument is required or not.
                Default Value: False
                Type: bool
       """

       # Call Abstract class constructor
       super().__init__(data_type, description, lang_name, is_required)
       self.get_default_value = lambda: None
       self.is_lists_allowed = lambda: False


class _AnlyFuncOutputUAF(_AnlyFuncArgumentBaseUAF):
    """ Class to hold the information about output argument of UAF."""
    def __init__(self, data_type, description, lang_name, layer_name,
                 primary_layer=False, result_table_column_types=None, is_required=False):
        """
         DESCRIPTION:
            Constructor for the class.

         PARAMETERS:
             description:
                 Required Argument.
                 Specifies the output argument description.
                 Type: str or List

             data_type:
                 Required Argument.
                 Specifies data type an output argument can accept.
                 Type: str

             lang_name:
                 Required Argument.
                 Specifies the name of the argument to be exposed to user.
                 Type: str

            primary_layer:
                 Optional Argument.
                 Specifies whether the layer is primary or not.
                 Default Value: False
                 Type: bool

            layer_name:
                 Required Argument.
                 Specifies the name of the output layer.
                 Type:str

            result_table_column_types:
                Optional Argument
                Specifies the column types for the result table.
                Type: List or str

            is_required:
                 Optional Argument.
                 Specifies whether the argument is required or not.
                 Default Value: False
                 Type: bool
        """

        # Call Abstract class constructor
        super().__init__(data_type, description, lang_name, is_required)
        # Process other parameters of output table argument.
        self.__result_table_column_types = result_table_column_types
        self.__primary_layer = primary_layer
        self.__layer_name = layer_name

        # Getters
        self.get_result_table_column_types = lambda: self.__result_table_column_types
        self.get_primary_layer = lambda : self.__primary_layer
        self.get_layer_name = lambda : self.__layer_name

        # Validation
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["result_table_column_types", self.__result_table_column_types, True, (list, str)])
        self.__arg_info_matrix.append(["primary_layer", self.__primary_layer, True, bool])
        self.__arg_info_matrix.append(["layer_name", self.__layer_name, False, str])
        _Validators._validate_function_arguments(self.__arg_info_matrix)


class _AnlyFuncArgumentUAF(_AnlyFuncArgumentBaseUAF):
    """Class to hold the information about the other function parameters."""

    def __init__(self, data_type, description, name, is_required=False, permitted_values=None,
                 lower_bound=None, upper_bound=None, lower_bound_type=None, upper_bound_type=None,
                 check_duplicates=False, list_type=None, allow_nan=None, lang_name=None,
                 default_value=None, required_length=0, nested_param_list=None,
                 is_nested=False, parent=None, has_nested=False):
        """
         DESCRIPTION:
            Constructor for the class.

         PARAMETERS:
             description:
                 Required Argument.
                 Specifies the argument description.
                 Type: str or List

             name:
                 Required Argument.
                 Specifies the SQL name of the argument.
                 Type: str

             data_type:
                 Required Argument.
                 Specifies the data type for the argument.
                 Type: str

             is_required:
                 Optional Argument.
                 Specifies whether the argument is required or not.
                 Default Value: False
                 Types: bool

             permitted_values:
                Optional Argument.
                 Specifies the permitted values for the particular argument.
                 Type: List

             lower_bound:
                 Optional Argument.
                 Specifies the lower bound for the particular argument.
                 Type: int or float

             upper_bound:
                 Optional Argument.
                 Specifies the upper bound for the particular argument.
                 Type: int or float

             lower_bound_type:
                 Optional Argument.
                 Specifies whether the lower bound is inclusive or not.
                 Type: str

             upper_bound_type:
                 Optional Argument.
                 Specifies whether the upper bound is inclusive or not.
                 Type: str

             check_duplicates:
                 Optional Argument
                 Specifies if the argument checks for duplicate values.
                 Type: bool

             list_type:
                 Optional Argument.
                 Specifies the type of the list in the argument.
                 Type: str

            allow_nan:
                Required Argument.
                Specifies whether nan values are allowed or not.
                Type: bool

            is_required:
                Optional Argument.
                Specifies whether the argument is required or not .
                Type: bool

            lang_name:
                Optional Argument.
                Specifies the name of the argument to be exposed to user.
                Type: str

            default_value:
                Optional Argument.
                Specifies the default value of the particular argument.
                Type: int or str or float

            required_length:
                Optional Argument.
                Specifies if the list must be the same length as the list specified
                in argument clause.
                Types: int

            nested_params_json:
                Optional Argument.
                Specifies the json object for nested_params argument.
                Type: List

            is_nested:
                Optional Argument.
                Specifies whether the argument is a nested argument or not.
                Default Value: False
                Type: bool

            parent:
                Optional Argument.
                Specifies the name of the parent incase of nested argument.
                Default Value: None
                Type: str or None

            has_nested:
                Optional Argument.
                Specifies whether the argument has nested_params or not.
                Default Value:False
                Type: bool

        """
        # Call Abstract class constructor
        super().__init__(data_type, description, lang_name, is_required)

        # Process other parameters of arguments.
        self.__name = name
        self.__data_type = self.get_data_type()
        self.__permitted_values = permitted_values
        self.__default_value = default_value
        self.__r_default_value = None
        self.__allow_nan = allow_nan
        self.__lower_bound = lower_bound
        self.__upper_bound = upper_bound
        self.__lower_bound_type = lower_bound_type
        self.__upper_bound_type = upper_bound_type
        self.__check_duplicates = check_duplicates
        self.__required_length = required_length
        self.__parent = parent
        self.__is_nested = is_nested
        self.__has_nested = has_nested
        self.__allows_lists = False
        self.__match_length_of_arguments = False

        # Creating a list for nested params
        self.__nested_param_list = nested_param_list

        # Getters
        self.get_name = lambda: self.__name
        self.get_data_type = lambda: self.__data_type
        self.get_permitted_values = lambda: self.__permitted_values
        self.get_default_value = lambda: self.__default_value
        self.get_r_default_value = lambda: self.__r_default_value
        self.is_nan_allowed = lambda: self.__allow_nan
        self.get_parent = lambda: self.__parent
        self.get_lower_bound = lambda: self.__lower_bound
        self.get_upper_bound = lambda: self.__upper_bound
        self.get_lower_bound_type = lambda: self.__lower_bound_type
        self.get_upper_bound_type = lambda: self.__upper_bound_type
        self.get_check_duplicates = lambda: self.__check_duplicates
        self.get_required_length = lambda: self.__required_length
        self.get_nested_param_list = lambda: self.__nested_param_list
        self.get_is_nested = lambda: self.__is_nested
        self.get_has_nested = lambda: self.__has_nested
        self.is_lists_allowed = lambda: self.__allows_lists
        self.get_match_length_of_arguments = lambda: self.__match_length_of_arguments

        # In order to make it similar to variables of SQLE functions if the data_type is list
        # we are setting allows_list=True and data_type to the data_type of the list elements.
        if self.get_data_type() == "list":
            self.__allows_lists = True
            self.__data_type = list_type

        # Validation
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["name", self.__name, True, str])
        self.__arg_info_matrix.append(["permitted_values", self.__permitted_values, True, list])
        self.__arg_info_matrix.append(["default_value", self.__default_value, True, (int, str, float, bool, list)])
        self.__arg_info_matrix.append(["r_default_value", self.__r_default_value, True, (int, str, float, bool, list)])
        self.__arg_info_matrix.append(["allow_nan", self.__allow_nan, True, bool])
        self.__arg_info_matrix.append(["lower_bound", self.__lower_bound, True, (int, float)])
        self.__arg_info_matrix.append(["upper_bound", self.__upper_bound, True, (int, float)])
        self.__arg_info_matrix.append(["lower_bound_type", self.__lower_bound_type, True, str])
        self.__arg_info_matrix.append(["upper_bound_type", self.__upper_bound_type, True, str])
        self.__arg_info_matrix.append(["check_duplicates", self.__check_duplicates, True, bool])
        self.__arg_info_matrix.append(["list_size", self.__required_length, True, (int, str)])

        _Validators._validate_function_arguments(self.__arg_info_matrix)

        # Validate whether lower bound is less than upper bound.
        _Validators._validate_argument_range(arg_name="dummy", arg=None, lbound=self.__lower_bound,
                                             ubound=self.__upper_bound)
        # Validate whether lower_bound and lower_bound_type are mutually inclusive.
        _Validators._validate_mutually_inclusive_arguments(lower_bound, "lower_bound", lower_bound_type, "lower_bound_type")
        # Validate whether upper_bound and upper_bound_type are mutually inclusive.
        _Validators._validate_mutually_inclusive_arguments(upper_bound, "upper_bound", upper_bound_type, "upper_bound_type")

        # In order to make it similar to variables of SQLE functions, if get_required_length specifies
        # a value we set match_length_of_arguments which will validate the length of the arguments
        if not isinstance(self.__required_length, str) and self.get_required_length() > 0:
            self.__match_length_of_arguments = True

        # If the argument is an int type and permitted values are 0 and 1, then we should consider it as boolean.
        if "INTEGER" in self.__data_type.upper() and self.__permitted_values is not None\
                and set(self.__permitted_values) == {0, 1}:
            self.__data_type = "BOOLEAN"
            self.__permitted_values = None
            self.set_is_required(False)
            if self.__default_value is not None:
                self.__default_value = bool(self.__default_value)
            else:
                self.__r_default_value = False             

    def get_python_type(self):
        """
        DESCRIPTION:
            Get equivalent Python type for the JSON datatype for an argument.

        PARAMETERS:
            None

        RETURNS:
            type.

        RAISES:
            None

        EXAMPLES:
            self.get_python_type(arg1="string", arg2="db", arg3=2)
        """
        py_types = tuple()

        # If multiple datatype's allowed, return the tuple of all allowed python types.
        if isinstance(self.__data_type, list):
            for td_type in self.__data_type:
                py_type = _Dtypes._anly_json_type_to_python_type(td_type)

                # If py_type is not a tuple, convert to a tuple.
                py_types = py_types + ((py_type,) if not isinstance(py_type, tuple) else py_type)
        else:
            py_type = _Dtypes._anly_json_type_to_python_type(self.__data_type)
            py_types = py_type if isinstance(py_type, tuple) else (py_type,)

        # If argument is float and int is not in the list of valid types, then add int to the list.
        if float in py_types and int not in py_types:
            py_types = (int,) + py_types
            
        # If lists are allowed, add list type also.
        if self.__allows_lists and (list not in py_types):
            py_types = py_types + (list,)

        return py_types
