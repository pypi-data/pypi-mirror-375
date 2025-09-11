import datetime
import enum
import numbers
import os
import pandas as pd
from pathlib import Path
import re
from sqlalchemy import func
from teradataml.common.constants import TeradataConstants, PTITableConstants, PythonTypes, DataFrameTypes
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import MessageCodes, Messages
from teradataml.utils.dtypes import _Dtypes, _DtypesMappers, _ListOf, _TupleOf
from teradataml.options.configure import configure
from teradataml.dataframe.sql_interfaces import ColumnExpression
from functools import wraps, reduce
from teradatasqlalchemy import (PERIOD_DATE, PERIOD_TIMESTAMP)

from teradataml.utils.internal_buffer import _InternalBuffer


def skip_validation():
    """
    DESCRIPTION:
        Define for skipping the validation.

    PARAMETERS:
        None

    EXAMPLES:
        @skip_validation(skip_all=True)
        def validation_func(): ...

    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # If "skip_all" flag is set to False,
            # skip all validation execution.
            if not _Validators.skip_all:
                return func(*args, **kwargs)

        return wraps(func)(wrapper)

    return decorator


class _Validators:
    """
    A class containing set of utilities that can be used for validations of various kinds.
    Currently, this facilitates the validations done for:
        1. Analytic function execution engine: (_validate_engine)
        2. Validation for the vantage_version: (_validate_vantage_version)
        3. Validate whether argument has passed with empty string or not: (_validate_input_columns_not_empty)
        4. Validate for permitted values of the argument: (_validate_permitted_values)
        5. Validate function arguments. (_validate_function_arguments) This specifically validates for
            1. Argument types check.
            2. Argument is empty or not.
            3. Permitted values check.
        6. Validate for missing required arguments.
        7. Validate column exists in a DataFrame or not. (_validate_column_exists_in_dataframe)
        8. Validate required arguments are missing or not. (_validate_missing_required_arguments)
        9. Validate whether function install location is set.
        10. Validate whether the table exist in the schema or not
        11. Validate whether the given file is not empty, given absolute file path.
        12. Validate whether "arg1" and "arg2" are mutually inclusive.
    """

    # "skip_all" specifies to skip all the executions.
    skip_all = False

    @staticmethod
    @skip_validation()
    def __getTypeAsStr(type_list):
        """
        Function to convert type to string.

        PARAMETERS:
            type_list
                Required Argument.
                A tuple of types or a type to be converted to string.

        RAISES:
            None

        RETURNS:
            A list of strings representing types in type_list.

        EXAMPLES:
            _Validators.__getTypeAsStr(type_list)
        """
        type_as_str = []
        if isinstance(type_list, tuple):
            for typ in type_list:
                if isinstance(typ, tuple):
                    for typ1 in typ:
                        type_as_str.append(typ1.__name__)
                elif isinstance(typ, (_ListOf, _TupleOf)):
                    type_as_str.append(str(typ))
                elif typ is pd.DataFrame:
                    type_as_str.append("pandas DataFrame")
                elif typ.__name__ == "DataFrame":
                    type_as_str.append("teradataml DataFrame")
                else:
                    type_as_str.append(typ.__name__)

        if isinstance(type_list, type):
            if type_list is pd.DataFrame:
                type_as_str.append("pandas DataFrame")
            elif type_list.__name__ == "DataFrame":
                type_as_str.append("teradataml DataFrame")
            else:
                type_as_str.append(type_list.__name__)

        if isinstance(type_list, (_ListOf, _TupleOf)):
            type_as_str.append(str(type_list))

        return type_as_str

    @staticmethod
    @skip_validation()
    def _check_isinstance(obj, class_or_tuple):
        """
        Function checks whether an object is an instance of a class.

        PARAMETER
            obj:
                Required Argument.
                Specifies the object to check instance of.

            class_or_tuple:
                Required Argument.
                Specifies the type or tuple of types to check instance against.

        RAISES:
            None.

        RETURNS:
            True, if obj is instance of class_or_tuple

        EXAMPLES:
            _Validators._check_isinstance(obj, (int, list, str))
        """
        # If obj is of type bool and type to check against contains int, then we  must
        # check/validate the instance as type(obj) == class_or_tuple.
        # bool is subclass of int, hence isinstance(True, int) will always return true.
        # And we would like to return false, as bool is not a int.
        if not isinstance(obj, bool):
            # If obj of any type other than bool, then we shall use "isinstance()"
            # to perform type checks.
            return isinstance(obj, class_or_tuple)

        else:
            # 'obj' is of type bool.
            if isinstance(class_or_tuple, tuple):
                if int not in class_or_tuple:
                    # If class_or_tuple is instance of tuple and int is not in class_or_tuple
                    # use "isinstance()" to validate type check for obj.
                    return isinstance(obj, class_or_tuple)
                else:
                    return type(obj) in class_or_tuple

            else:  # isinstance(class_or_tuple, type):
                if int != class_or_tuple:
                    # If class_or_tuple is instance of type and class_or_tuple is not an int
                    # use "isinstance()" to validate type check for obj.
                    return isinstance(obj, class_or_tuple)
                else:
                    return type(obj) == class_or_tuple

    @staticmethod
    @skip_validation()
    def _validate_columnexpression_dataframe_has_columns(columns,
                                                         arg_name,
                                                         column_expression):
        """
        DESCRIPTION:
                Function to check whether column name(s) available in dataframe
                or not from a given column. This function is used currently
                only for Window Aggregates.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the name or list of names of columns to be validated
                for existence.
                Types: str or List of strings or ColumnExpression or list of ColumnExpression

            arg_name:
                Required Argument.
                Specifies the name of the argument.
                Types: str

            column_expression:
                Required Argument.
                Specifies teradataml DataFrame Column to check against for
                column existence.
                Types: ColumnExpression

        RAISES:
            ValueError

        RETURNS:
            bool

        EXAMPLES:
            _Validators._validate_dataframe_has_argument_columns_from_column(self.data_sequence_column,
                                                                            "data_sequence_column",
                                                                            self.data.col)
        """
        if not columns:
            return True
        from teradataml.common.utils import UtilFuncs
        # Converting columns to a list if string is passed.
        if not isinstance(columns, list):
            columns = [columns]

        df_columns = UtilFuncs._all_df_columns(column_expression)

        # Let's validate existence of each column one by one.
        columns_ = []
        for column in columns:
            if isinstance(column, str):
                columns_.append(column)
            else:
                columns_ = columns_ + UtilFuncs._all_df_columns(column)

        # Let's validate existence of each column one by one.
        for column_name in columns_:
            # If column name does not exist in DataFrame of a column, raise the exception.
            if column_name not in df_columns:
                message = "{}. Check the argument '{}'".format(sorted(df_columns), arg_name)
                raise ValueError(Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL,
                                                      column_name,
                                                      message
                                                      ))
        return True

    @staticmethod
    @skip_validation()
    def _validate_invalid_column_types(all_columns, column_arg, columns_to_check, invalid_types):
        """
        DESCRIPTION:
            Function to validate the invalid types for "columns_to_check" from "all_columns".

        PARAMETERS:
            all_columns:
                Required Argument.
                Specifies the ColumnExpressions.
                Types: List of ColumnExpression

            column_arg:
                Required Argument.
                Specifies the name of the argument.
                Types: str

            columns_to_check:
                Required Argument.
                Specifies columns to check for invalid types.
                Types: str OR list of str OR ColumnExpression OR list of ColumnExpression

            invalid_types:
                Required Argument.
                Specifies list of invalid teradata types to check against "columns".
                Types: list

        RAISES:
            ValueError

        RETURNS:
            bool

        EXAMPLES:
            _Validators._validate_invalid_column_types(columns, column_arg, invalid_types)
        """
        columns_and_types = {c.name.lower(): type(c.type) for c in all_columns}
        get_col_type = lambda column: columns_and_types[column.lower()].__name__ if isinstance(
            column, str) else column.type.__class__.__name__

        invalid_types = ["{}({})".format(column if isinstance(column, str) else column.name, get_col_type(column))
                         for column in columns_to_check if get_col_type(column)
                         in [t.__name__ for t in _Dtypes._get_sort_unsupported_data_types()]
                         ]

        if invalid_types:
            invalid_column_types = (col_type.__name__ for col_type in
                                    _Dtypes._get_sort_unsupported_data_types())
            error_message = Messages.get_message(MessageCodes.INVALID_COLUMN_DATATYPE,
                                                 ", ".join(invalid_types),
                                                 column_arg,
                                                 "Unsupported",
                                                 ", ".join(invalid_column_types))

            raise ValueError(error_message)

        return True

    @staticmethod
    @skip_validation()
    def _validate_dataframe_has_argument_columns(columns, column_arg, data, data_arg, is_partition_arg=False,
                                                 case_insensitive=False):
        """
        Function to check whether column names in columns are present in given dataframe or not.
        This function is used currently only for Analytics wrappers.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies name or list of names of columns to be validated for existence.
                Types: str or List of strings

            column_arg:
                Required Argument.
                Specifies the name of the argument.
                Types: str

            data:
                Required Argument.
                Specifies teradataml DataFrame to check against for column existence.
                Types: teradataml DataFrame

            data_arg:
                Required Argument.
                Specifies the name of the dataframe argument.
                Types: str

            is_partition_arg:
                Optional Argument.
                Specifies a bool argument notifying, whether argument being validate is
                Partition argument or not.
                Types: bool

            case_insensitive:
                Optional Argument.
                Specifies a bool argument notifying, whether to check column names
                in case-insensitive manner or not.
                Default Value: False
                Types: bool

        RAISES:
            TeradataMlException - TDMLDF_COLUMN_IN_ARG_NOT_FOUND column(s) does not exist in a dataframe.

        EXAMPLES:
            _Validators._validate_dataframe_has_argument_columns(self.data_sequence_column, "data_sequence_column", self.data, "data")
            _Validators._validate_dataframe_has_argument_columns(self.data_partition_column, "data_sequence_column", self.data, "data", true)
        """
        if is_partition_arg and columns is None:
            return True

        if columns is None:
            return True

        _Validators._validate_dependent_argument(column_arg, columns, data_arg, data)

        # Converting columns to a list if string is passed.
        if not isinstance(columns, list) and columns is not None:
            columns = [columns]

        total_columns = []

        for column in columns:
            for separator in TeradataConstants.RANGE_SEPARATORS.value:
                if column is None:
                    total_columns.append(column)
                elif column[0] == "-":
                    # If column has exclude operator "-".
                    # For example incase of "-[50]", let database handle validation.
                    if re.match(r'-\[\d+\]', column) is not None:
                        continue
                    total_columns.append(column[1:])
                elif column.count(separator) == 1:
                    # Following cases can occur:
                    # '3:5' or 'colA:colE'
                    # ':4' or ':columnD' specifies all columns up to and including the column with index 4(or columnD).
                    # '4:' or 'columnD:' specifies the column with index 4(or columnD) and all columns after it.
                    # ':' specifies all columns in the table.

                    try:
                        # Check if it's a single column with one separator. For e.g. column:A.
                        # If yes, just continue.
                        _Validators._validate_column_exists_in_dataframe(column, data._metaexpr,
                                                                         case_insensitive=case_insensitive)
                        continue
                    except:
                        # User has provided range value.
                        column_names = column.split(separator)
                        if (len(column_names) == 2 and
                                any([column_names[0].isdigit(), column_names[1].isdigit()]) and
                                not all([column_names[0].isdigit(), column_names[1].isdigit()]) and
                                not "" in column_names):
                            # Raises Exception if column range has mixed types. For e.g. "4:XYZ".
                            err_msg = Messages.get_message(MessageCodes.MIXED_TYPES_IN_COLUMN_RANGE)
                            raise ValueError(err_msg.format(column_arg))

                        for col in column_names:
                            if not col.isdigit() and col != "":
                                total_columns.append(col)

                elif column.count(separator) > 1:
                    continue
                else:
                    total_columns.append(column)

        return _Validators._validate_column_exists_in_dataframe(total_columns, data._metaexpr, column_arg=column_arg,
                                                                data_arg=data_arg, case_insensitive=case_insensitive)

    @staticmethod
    @skip_validation()
    def _validate_column_exists_in_dataframe(columns, metaexpr, case_insensitive=False, column_arg=None,
                                             data_arg=None, for_table=False):
        """
        Method to check whether column or list of columns exists in a teradataml DataFrame or not.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies name or list of names of columns to be validated for existence.
                Types: str or List of strings

            metaexpr:
                Required Argument.
                Specifies a teradataml DataFrame metaexpr to be validated against.
                Types: MetaExpression

            case_insensitive:
                Optional Argument.
                Specifies a flag, that determines whether to check for column existence in
                case_insensitive manner or not.
                Default Value: False (Case-Sensitive lookup)
                Types: bool

            column_arg:
                Optional Argument.
                Specifies the name of the argument.
                Types: str

            data_arg:
                Optional Argument.
                Specifies the name of the dataframe argument or name of the table.
                Types: str

            for_table:
                Optional Argument.
                Specifies whether error should be raised against table or DataFrame, i.e.,
                when columns are not available and "for_table" is set to False, then
                exception message mentions column(s) not available in DataFrame. When
                columns are not available and "for_table" is set to true, then exception
                message mentions column(s) not available in Table.
                Types: str

        RAISES:
            ValueError
                TDMLDF_DROP_INVALID_COL - If columns not found in metaexpr.

        RETURNS:
            None

        EXAMPLES:
            _Validators._validate_column_exists_in_dataframe(["col1", "col2"], self.metaexpr)

        """
        if columns is None:
            return True

        # If just a column name is passed, convert it to a list.
        if isinstance(columns, str):
            columns = [columns]

        # Constructing New unquoted column names for selected columns ONLY using Parent _metaexpr
        if case_insensitive:
            # If lookup has to be a case-insensitive then convert the
            # metaexpr columns name to lower case.
            unquoted_df_columns = [c.name.replace('"', "").lower() for c in metaexpr.c]
        else:
            unquoted_df_columns = [c.name.replace('"', "") for c in metaexpr.c]

        # Let's validate existence of each column one by one.
        for column_name in columns:
            if column_name is None:
                column_name = str(column_name)

            case_based_column_name = column_name.lower() if case_insensitive else column_name

            # If column name does not exist in metaexpr, raise the exception
            if not case_based_column_name.replace('"', "") in unquoted_df_columns:
                if column_arg and data_arg:
                    raise ValueError(Messages.get_message(MessageCodes.TDMLDF_COLUMN_IN_ARG_NOT_FOUND,
                                                          column_name,
                                                          column_arg,
                                                          data_arg,
                                                          "Table" if for_table else "DataFrame"))
                else:
                    raise ValueError(Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL,
                                                          column_name,
                                                          sorted([c.name.replace('"', "") for c in metaexpr.c])))

        return True

    @staticmethod
    @skip_validation()
    def _validate_engine(engine):
        """
        Function to validate whether the argument engine is supported or not.

        PARAMETERS:
            engine:
                Required Argument.
                Specifies the type of the engine.

        RETURNS:
            True, if engine is supported.

        RAISES:
            TeradataMLException

        EXAMPLES:
            _Validators._validate_engine("ENGINE_SQL")
        """
        supported_engines = TeradataConstants.SUPPORTED_ENGINES.value
        if engine not in supported_engines.keys():
            raise TeradataMlException(Messages.get_message(
                MessageCodes.CONFIG_ALIAS_ENGINE_NOT_SUPPORTED).format(engine,
                                                                       ", ".join(supported_engines.keys())),
                                      MessageCodes.CONFIG_ALIAS_ENGINE_NOT_SUPPORTED)

        return True

    @staticmethod
    @skip_validation()
    def _validate_function_arguments(arg_list, skip_empty_check=None):
        """
        Method to verify that the input arguments are of valid data type except for
        argument of DataFrameType.

        PARAMETERS:
            arg_list:
                Required Argument.
                Specifies a list of arguments, expected types are mentioned as type or tuple.
                       argInfoMatrix = []
                       argInfoMatrix.append(["data", data, False, (DataFrame)])
                       argInfoMatrix.append(["centers", centers, True, (int, list)])
                       argInfoMatrix.append(["threshold", threshold, True, (float)])
                Types: List of Lists
            skip_empty_check:
                Optional Argument.
                Specifies column name and values for which to skip check.
                Types: Dictionary specifying column name to values mapping.

        RAISES:
            Error if arguments are not of valid datatype

        EXAMPLES:
            _Validators._validate_function_arguments(arg_list)
        """
        # arg_list is list of list, where each inner list can have maximum 6 elements
        # and must have minimum (first) 4 elements:
        # Consider following inner list.
        #   [element1, element2, element3, element4, element5, element6]
        #   Corresponds to:
        #   [<1_arg_name>, <2_arg_value>, <3_is_optional>, <4_tuple_of_accepted_types>,
        #    <5_empty_not_allowed>, <6_list_of_permitted_values>]
        #   e.g.
        #       arg_list = [["join", join, True, (str), True, concat_join_permitted_values]]
        #   1. element1 --> Argument Name, a string. ["join" in above example.]
        #   2. element2 --> Argument itself. [join]
        #   3. element3 --> Specifies a flag that mentions if argument is optional or not.
        #                   False means required argument and True means optional argument.
        #   4. element4 --> Tuple of accepted types. (str) in above example.
        #   5. element5 --> True, means validate for empty value. Error will be raised, if empty values are passed.
        #                   If not specified, argument value will not be validated for empty value.
        #   6. element6 --> A list of permitted values, an argument can accept.
        #                   If not specified, argument value will not be validated against any permitted values.
        #                   If a list is passed, validation will be performed for permitted values.
        invalid_arg_names = []
        invalid_arg_types = []

        type_check_failed = False

        for args in arg_list:
            num_args = len(args)
            if not isinstance(args[0], str):
                raise TypeError("First element in argument information matrix should be str.")

            if not isinstance(args[2], bool):
                raise TypeError("Third element in argument information matrix should be bool.")

            if not (isinstance(args[3], tuple) or isinstance(args[3], type) or
                    isinstance(args[3], (_ListOf, _TupleOf)) or isinstance(args[3], enum.EnumMeta)):
                err_msg = "Fourth element in argument information matrix should be a 'tuple of types' or 'type' type."
                raise TypeError(err_msg)

            if num_args >= 5:
                if not isinstance(args[4], bool):
                    raise TypeError("Fifth element in argument information matrix should be bool.")

            #
            # Let's validate argument types.
            #
            # Verify datatypes for arguments which are required or the optional arguments are not None
            if (args[2] == True and args[1] is not None) or (args[2] == False):
                # Validate the types of argument, if expected types are instance of tuple or type
                dtype_list = _Validators.__getTypeAsStr(args[3])

                if isinstance(args[3], tuple) and list in args[3]:
                    # If list of data types contain 'list', which means argument can accept list of values.
                    dtype_list.remove('list')
                    valid_types_str = ", ".join(dtype_list) + " or list of values of type(s): " + ", ".join(
                        dtype_list)

                    if isinstance(args[1], list):
                        # If argument contains list of values, check each value.
                        for value in args[1]:
                            # If not valid datatype add invalid_arg to dictionary and break
                            if not _Validators._check_isinstance(value, args[3]):
                                invalid_arg_names.append(args[0])
                                invalid_arg_types.append(valid_types_str)
                                type_check_failed = True
                                break
                    elif not _Validators._check_isinstance(args[1], args[3]):
                        # Argument is not of type list.
                        invalid_arg_names.append(args[0])
                        invalid_arg_types.append(valid_types_str)
                        type_check_failed = True

                elif isinstance(args[3], tuple):
                    # Argument can accept values of multiple types, but not list.
                    valid_types_str = " or ".join(dtype_list)
                    if not _Validators._check_isinstance(args[1], args[3]):
                        invalid_arg_names.append(args[0])
                        invalid_arg_types.append(valid_types_str)
                        type_check_failed = True
                else:
                    # Argument can accept values of single type.
                    valid_types_str = " or ".join(dtype_list)
                    if not _Validators._check_isinstance(args[1], args[3]):
                        invalid_arg_names.append(args[0])
                        invalid_arg_types.append(valid_types_str)
                        type_check_failed = True

                #
                # Validate the arguments for empty value
                #
                if not type_check_failed and len(args) >= 5:
                    if args[4]:
                        _Validators._validate_input_columns_not_empty(args[1], args[0], skip_empty_check)

                #
                # Validate the arguments for permitted values
                #
                if not type_check_failed and len(args) >= 6:
                    if args[5] is not None:
                        _Validators._validate_permitted_values(args[1], args[5], args[0], supported_types=args[3])

        if type_check_failed:
            if len(invalid_arg_names) != 0:
                raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                     invalid_arg_names, invalid_arg_types))

        return True

    @staticmethod
    @skip_validation()
    def _validate_input_columns_not_empty(arg, arg_name, skip_empty_check=None):
        """
        Function to check whether argument is empty string or not.

        PARAMETERS:
            arg:
                Required Argument.
                Argument value (string) to be checked whether it is empty or not.
            skip_empty_check:
                Optional Argument.
                Specifies column name and values for which to skip check.
                Types: Dictionary specifying column name to values mapping.
                Example: When '\n', '\t' are valid values for argument 'arg_name', this check should be skipped.

        RAISES:
            Error if argument contains empty string

        EXAMPLES:
            _Validators._validate_input_columns_not_empty(arg)
        """
        if isinstance(arg, str):
            if not (skip_empty_check and arg_name in skip_empty_check.keys() and arg in skip_empty_check[arg_name]):
                if ((len(arg.strip()) == 0)):
                    raise ValueError(Messages.get_message(MessageCodes.ARG_EMPTY, arg_name))

        if isinstance(arg, list):
            if len(arg) == 0:
                raise ValueError(Messages.get_message(MessageCodes.ARG_EMPTY, arg_name).replace("empty string", "an empty list"))

            for col in arg:
                if not (skip_empty_check and arg_name in skip_empty_check.keys() and col in skip_empty_check[arg_name]):
                    if isinstance(col, str):
                        if (not (col is None)) and (len(col.strip()) == 0):
                            raise ValueError(Messages.get_message(MessageCodes.ARG_EMPTY, arg_name))
        return True

    @staticmethod
    @skip_validation()
    def _validate_missing_required_arguments(arg_list):
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
        miss_args = []
        for args in arg_list:
            '''
            Check for missing arguments which are required. If args[2] is false
            the argument is required.
            The following conditions are true :
                1. The argument should not be None and an empty string.
            then argument is required which is missing and Raises exception.
            '''
            if args[2] == False and args[1] is None:
                miss_args.append(args[0])

        if len(miss_args) > 0:
            raise TeradataMlException(Messages.get_message(MessageCodes.MISSING_ARGS, miss_args),
                                      MessageCodes.MISSING_ARGS)
        return True

    @staticmethod
    @skip_validation()
    def _validate_permitted_values(arg, permitted_values, arg_name, case_insensitive=True, includeNone=True, supported_types=None):
        """
        Function to check the permitted values for the argument.

        PARAMETERS:
            arg:
                Required Argument.
                Argument value to be checked against permitted values from the list.
                Types: string

            permitted_values:
                Required Argument.
                A list of strings/ints/floats containing permitted values for the argument.
                Types: string

            arg_name:
                Required Argument.
                Name of the argument to be printed in the error message.
                Types: string

            case_insensitive:
                Optional Argument.
                Specifies whether values in permitted_values could be case sensitive.
                Types: bool

            includeNone:
                Optional Argument.
                Specifies whether 'None' can be included as valid value.
                Types: bool

            supported_types:
                Optional Argument.
                Specifies the supported datatypes for the argument.
                Types: str

        RAISES:
            Error if argument is not present in the list

        EXAMPLES:
            permitted_values = ["LOGISTIC", "BINOMIAL", "POISSON", "GAUSSIAN", "GAMMA", "INVERSE_GAUSSIAN", "NEGATIVE_BINOMIAL"]
            arg = "LOGISTIC"
            _Validators._validate_permitted_values(arg, permitted_values, argument_name)
        """
        # validating permitted_values type which has to be a list.
        _Validators._validate_function_arguments([["permitted_values", permitted_values, False, (list)]])

        if case_insensitive:
            permitted_values = [item.upper() if isinstance(item, str) else item for item in permitted_values]

        # Validate whether argument has value from permitted values list or not.
        if not isinstance(arg, list) and arg is not None:
            arg = [arg]

        if arg is not None:
            # Getting arguments in uppercase to compare with 'permitted_values'
            arg_upper = []
            for element in arg:
                if element is None:
                    # If element is None, then we shall add a string "None"
                    if includeNone:
                        continue
                    arg_upper.append(str(element))
                elif isinstance(element, str):
                    # If element is of type str, then we will convert it to upper case.
                    if case_insensitive:
                        arg_upper.append(element.upper())
                    else:
                        arg_upper.append(element)
                else:
                    # For any other type of element, we will keep it as is.
                    arg_upper.append(element)

            # Form the list of datatypes not present in the datatypes of permitted_values.
            add_types = ()
            if supported_types is not None:
                # Convert type and tuple to list.
                supported_types = [supported_types] if isinstance(supported_types, type) else supported_types
                # Form a list for types which are not there in type of permitted_values.
                add_types = tuple(set(list(supported_types)) - set(list(map(type, permitted_values))) - set([list]))
                # Remove the arguments from arg_upper which are an instance of the add_types.
                if len(add_types) > 0:
                    [arg_upper.remove(arg) for arg in arg_upper if isinstance(arg, add_types)]

            # If any of the arguments in 'arg_upper' not in 'permitted_values',
            # then, raise exception
            upper_invalid_values = list(set(arg_upper).difference(set(permitted_values)))

            if len(upper_invalid_values) > 0:
                # Getting actual invalid arguments (non-upper)
                invalid_values = []
                for element in arg:
                    if element is None:
                        if includeNone:
                            continue
                        invalid_values.append(str(element))
                    elif isinstance(element, str) and element.upper() in upper_invalid_values:
                        invalid_values.append(element)
                    elif element in upper_invalid_values:
                        invalid_values.append(element)
                invalid_values.sort()

                # Concatenate the message for datatypes not present in datatypes of permitted_values.
                if len(add_types) > 0:
                    add_types = _Validators.__getTypeAsStr(add_types)
                    add_types = " or ".join(add_types)
                    permitted_values = "{} {}".format(permitted_values, "or any values of type {}".format(add_types))

                raise ValueError(
                    Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                         ', '.join([str(item) if not isinstance(item, str) else item for item in invalid_values]),
                                         arg_name, permitted_values))
        # If any of the arguments doesn't want to include None as valid value
        # then, raise exception.
        else:
            if not includeNone:
                raise ValueError(
                    Messages.get_message(MessageCodes.INVALID_ARG_VALUE, None,
                                         arg_name, permitted_values), MessageCodes.INVALID_ARG_VALUE)
        # Returns True when arg is None or there is no Exception
        return True

    @staticmethod
    @skip_validation()
    def _validate_positive_int(arg, arg_name, lbound=0, ubound=None, lbound_inclusive=False):
        """
        Validation to check arg values is a positive int.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies the number to be validated for positive INT.
                Types: int

            arg_name:
                Required Argument.
                Specifies the name of the argument to be printed in error message.
                Types: str

            lbound:
                Optional Argument.
                Specifies the lower bound value for arg.
                Note: Value provided to this argument is exclusive, i.e., if value provided
                      to this argument 10, then error will be raised for any value of arg <= 10.
                      It can be made inclusive, if lbound_inclusive is set to 'True'.
                Types: int

            ubound:
                Optional Argument.
                Specifies the upper bound value for arg.
                Note: Value provided to this argument is inclusive, i.e., if value provided
                      to this argument 10, then error will be raised for any value of arg > 10.
                Types: int

            lbound_inclusive:
                Optional Argument.
                Specifies a boolean flag telling API whether to lbound value is inclusive or not.
                Types: bool

        RAISES:
            ValueError - If arg is not a positive int.

        RETURNS:
            True - If success

        EXAMPLES:
            # Validate n for value > 0
            _Validators._validate_positive_int(n, "n")
            # Validate n for value > 0 and value <= 32767
            _Validators._validate_positive_int(n, "n", ubound="32767")
        """
        if arg is None:
            return True

        if ubound is None:
            if lbound_inclusive:
                if not isinstance(arg, numbers.Integral) or arg < lbound:
                    raise ValueError(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT).format(arg_name, "greater than or equal to"))
            else:
                if not isinstance(arg, numbers.Integral) or arg <= lbound:
                    raise ValueError(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT).format(arg_name, "greater than"))
        else:
            if not isinstance(arg, numbers.Integral) or arg <= lbound or arg > ubound:
                raise ValueError(Messages.get_message(MessageCodes.TDMLDF_LBOUND_UBOUND).format(
                    arg_name, "greater than {}".format(lbound),
                    " and less than or equal to {}".format(ubound)))

        return True

    @staticmethod
    @skip_validation()
    def _validate_argument_range(arg,
                                 arg_name,
                                 lbound=None,
                                 ubound=None,
                                 lbound_inclusive=False,
                                 ubound_inclusive=False):
        """
        DESCRIPTION:
            Validation to check arg is in specified range.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies the number to be validated for range check.
                Types: int

            arg_name:
                Required Argument.
                Specifies the name of the argument to be printed in error message.
                Types: str

            lbound:
                Optional Argument.
                Specifies the lower bound value for arg.
                Note:
                    Value provided to this argument is exclusive, i.e., if
                    value provided to this argument 10, then error will be
                    raised for any value of arg < 10. It can be made inclusive,
                    if lbound_inclusive is set to 'True'.
                Types: int OR float

            ubound:
                Optional Argument.
                Specifies the upper bound value for arg.
                Note:
                    Value provided to this argument is exclusive, i.e., if
                    value provided to this argument 10, then error will be
                    raised for any value of arg > 10. It can be made inclusive,
                    if ubound_inclusive is set to 'True'.
                Types: int OR float

            lbound_inclusive:
                Optional Argument.
                Specifies whether lbound value is inclusive or not. When set to True,
                value is inclusive, otherwise exclusive.
                Default Value: False
                Types: bool

            ubound_inclusive:
                Optional Argument.
                Specifies whether ubound value is inclusive or not. When set to True,
                value is inclusive, otherwise exclusive.
                Default Value: False
                Types: bool

        RAISES:
            ValueError - If arg is not in the specified range.

        RETURNS:
            True - If success

        EXAMPLES:
            # Validate n for value in between of 10 and 20.
            _Validators._validate_argument_range(n, 10, 20)
        """
        if lbound is None and ubound is None:
            return True

        # Raise error if lower bound is greater than upper bound.
        if lbound is not None and ubound is not None and (lbound > ubound):
            raise ValueError("Lowerbound value '{}' must be less than upperbound value '{}'.".format(lbound, ubound))

        # If argument is None, do not validate the argument.
        if arg is None:
            return True

        is_arg_in_lower_bound, is_arg_in_upper_bound = True, True
        lbound_msg, ubound_msg = "", ""

        # Check for lower bound.
        if lbound is not None:
            if lbound_inclusive:
                is_arg_in_lower_bound = arg >= lbound
                lbound_msg = "greater than or equal to {}".format(lbound)
            else:
                is_arg_in_lower_bound = arg > lbound
                lbound_msg = "greater than {}".format(lbound)

        # Check for upper bound.
        if ubound is not None:
            if ubound_inclusive:
                is_arg_in_upper_bound = arg <= ubound
                ubound_msg = "less than or equal to {}".format(ubound)
            else:
                is_arg_in_upper_bound = arg < ubound
                ubound_msg = "less than {}".format(ubound)

        if not (is_arg_in_lower_bound and is_arg_in_upper_bound):
            # If both lower bound and upper bound error messages available, append 'and' to
            # upper bound message.
            if lbound_msg and ubound_msg:
                ubound_msg = " and {}".format(ubound_msg)
            raise ValueError(
                Messages.get_message(MessageCodes.TDMLDF_LBOUND_UBOUND).format(arg_name, lbound_msg, ubound_msg))

        return True

    @staticmethod
    @skip_validation()
    def _validate_vantage_version(vantage_version):
        """
        Function to verify whether the given vantage_version is
        supported or not.

        PARAMETERS:
            vantage_version:
                Required Argument.
                Specifies the vantage version.

        RETURNS:
            True, if the current vantage version is supported or not.

        RAISES:
            TeradataMLException

        EXAMPLES:
            _Validators._validate_vantage_version("vantage1.0")
        """
        supported_vantage_versions = TeradataConstants.SUPPORTED_VANTAGE_VERSIONS.value

        # Raise exception if the vantage version is not supported.
        if vantage_version not in supported_vantage_versions.keys():
            err_ = Messages.get_message(MessageCodes.CONFIG_ALIAS_VANTAGE_VERSION_NOT_SUPPORTED). \
                format(vantage_version, ", ".join(supported_vantage_versions.keys()))
            raise TeradataMlException(err_,
                                      MessageCodes.CONFIG_ALIAS_VANTAGE_VERSION_NOT_SUPPORTED)

        return True

    @staticmethod
    @skip_validation()
    def _validate_timebucket_duration(timebucket_duration, timebucket_duration_arg_name='timebucket_duration'):
        """
        Internal function to validate timeduration_bucket specified when creating a
        Primary Time Index (PTI) table.

        PARAMETERS:
            timebucket_duration:
                Specifies the timebucket_duration passed to a function().
                Types: str

            timebucket_duration_arg_name:
                Specifies the name of the argument to be displayed in the error message.
                Types: str

        RETURNS:
            True if the value is valid.

        RAISES:
            ValueError or TeradataMlException when the value is invalid.

        EXAMPLES:
            _Validators._validate_timebucket_duration('HOURS(2)')
            _Validators._validate_timebucket_duration('2hours')
            _Validators._validate_timebucket_duration('ayear') # Invalid
        """
        # Return True is it is not specified or is None since it is optional
        if timebucket_duration is None:
            return True

        # Check if notation is formal or shorthand (beginning with a digit)
        if timebucket_duration[0].isdigit():
            valid_timebucket_durations = PTITableConstants.VALID_TIMEBUCKET_DURATIONS_SHORTHAND.value
            pattern_to_use = PTITableConstants.PATTERN_TIMEBUCKET_DURATION_SHORT.value
            normalized_timebucket_duration = timebucket_duration.lower()
        else:
            valid_timebucket_durations = PTITableConstants.VALID_TIMEBUCKET_DURATIONS_FORMAL.value
            pattern_to_use = PTITableConstants.PATTERN_TIMEBUCKET_DURATION_FORMAL.value
            normalized_timebucket_duration = timebucket_duration.upper()

        for timebucket_duration_notation in valid_timebucket_durations:
            pattern = re.compile(pattern_to_use.format(timebucket_duration_notation))
            match = pattern.match(normalized_timebucket_duration)
            if match is not None:
                n = int(match.group(1))
                _Validators._validate_positive_int(n, "n", ubound=32767)

                # Looks like the value is valid
                return True

        # Match not found
        raise ValueError(Messages.get_message(
            MessageCodes.INVALID_ARG_VALUE).format(timebucket_duration, timebucket_duration_arg_name,
                                                   'a valid time unit of format time_unit(n) or it\'s short hand '
                                                   'equivalent notation'))

    @staticmethod
    @skip_validation()
    def _validate_column_type(df, col, col_arg, expected_types, raiseError=True):
        """
        Internal function to validate the type of an input DataFrame column against
        a list of expected types.

        PARAMETERS
            df:
                Required Argument.
                Specifies the input teradataml DataFrame which has the column to be tested
                for type.
                Types: teradataml DataFrame

            col:
                Required Argument.
                Specifies the column in the input DataFrame to be tested for type.
                Types: str

            col_arg:
                Required Argument.
                Specifies the name of the argument used to pass the column name.
                Types: str

            expected_types:
                Required Argument.
                Specifies a list of teradatasqlalchemy datatypes that the column is
                expected to be of type.
                Types: list of teradatasqlalchemy types

            raiseError:
                Optional Argument.
                Specifies a boolean flag that decides whether to raise error or just return True or False.
                Default Values: True, raise exception if column is not of desired type.
                Types: bool

        RETURNS:
            True, when the column is of an expected type.

        RAISES:
            TeradataMlException, when the column is not one of the expected types.

        EXAMPLES:
            _Validators._validate_column_type(df, timecode_column, 'timecode_column', PTITableConstants.VALID_TIMECODE_DATATYPES)
        """
        if not any(isinstance(df[col].type, t) for t in expected_types):
            if raiseError:
                raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_COLUMN_TYPE).
                                          format(col_arg, df[col].type, ' or '.join(expected_type.__visit_name__
                                                                                    for expected_type in expected_types)),
                                          MessageCodes.INVALID_COLUMN_TYPE)
            else:
                return False

        return True

    @staticmethod
    @skip_validation()
    def _validate_aggr_operation_unsupported_datatype(operation, columns, td_column_names_and_types):
        """
        Internal function to validate the for unsupported data types of an input DataFrame column for
        an aggreagate function.

        PARAMETERS
            operation:
                Required Argument.
                Specifies the name of the aggregate operation.
                Types: str

            columns:
                Required Argument.
                Specifies the column names to be validated for datatype check.
                Types: str

            td_column_names_and_types:
                Required Argument.
                Specifies the input teradataml DataFrames column name to SQLAlchemy type mapper.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException, when the columns is not one of the expected types.

        EXAMPLES:
            _Validators._validate_aggr_operation_unsupported_datatype(operation, columns, td_column_names_and_types):
        """
        # Check if the user provided columns has unsupported datatype for aggregate operation or not.
        # Get the list of unsupported types for aggregate function.
        unsupported_types = _Dtypes._get_unsupported_data_types_for_aggregate_operations(operation)
        invalid_columns = []

        for column in columns:
            if isinstance(td_column_names_and_types[column.lower()], tuple(unsupported_types)):
                invalid_columns.append(
                    "({0} - {1})".format(column, td_column_names_and_types[column.lower()]))

        if len(invalid_columns) > 0:
            invalid_columns.sort()  # helps in catching the columns in
            # lexicographic order
            error = MessageCodes.TDMLDF_AGGREGATE_UNSUPPORTED.value.format(
                ", ".join(invalid_columns), operation)
            msg = Messages.get_message(MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR). \
                format(error)
            raise TeradataMlException(msg, MessageCodes.TDMLDF_AGGREGATE_COMBINED_ERR)

    @staticmethod
    @skip_validation()
    def _validate_str_arg_length(arg_name, arg_value, op, length):
        """
        Internal function to validate the length of a string passed as an argument.

        PARAMETERS
            arg_name:
                Required Argument.
                Specifies the name of the argument for which we need to validate the value length.
                Types: str

            arg_value:
                Required Argument.
                Specifies the value passed to the argument.
                Types: str

            op:
                Required Argument.
                Specifies the type of check, and can be one of:
                * LT - Less than
                * LE - less than or equal to
                * GT - greater than
                * GE - greater than or equal to
                * EQ - equal to
                * NE - not equal to
                Types: str
                Permitted Values: ['LT', 'LE', 'GT', 'GE', 'EQ', 'NE']

            length:
                Required Argument.
                Specifies the length against which the 'op' check for the argument value length will be made.
                Types: int

        RETURNS:
            None

        RAISES:
            ValueError.

        EXAMPLES:
            _Validators._validate_str_arg_length("name", "The value", 10):
        """
        return _Validators._validate_arg_length(arg_name=arg_name, arg_value=arg_value, op=op, length=length)

    @staticmethod
    @skip_validation()
    def _validate_arg_length(arg_name, arg_value, op, length):
        """
        Internal function to validate the length of an argument.

        PARAMETERS
            arg_name:
                Required Argument.
                Specifies the name of the argument for which we need to validate the value length.
                Types: str

            arg_value:
                Required Argument.
                Specifies the value passed to the argument.
                Types: str or list or tuple or set or dict

            op:
                Required Argument.
                Specifies the type of check, and can be one of:
                * LT - Less than
                * LE - less than or equal to
                * GT - greater than
                * GE - greater than or equal to
                * EQ - equal to
                * NE - not equal to
                Types: str
                Permitted Values: ['LT', 'LE', 'GT', 'GE', 'EQ', 'NE']

            length:
                Required Argument.
                Specifies the length against which the 'op' check for the argument value length will be made.
                Types: int

        RETURNS:
            None

        RAISES:
            ValueError.

        EXAMPLES:
            _Validators._validate_arg_length("name", [1, 2, 3], 3):
        """
        # Check if the length of the string value for the argument is acceptable.
        # First, check if op is an acceptable operation.
        acceptable_op = {'LT': int.__lt__,
                         'LE': int.__le__,
                         'GT': int.__gt__,
                         'GE': int.__ge__,
                         'EQ': int.__eq__,
                         'NE': int.__ne__
                         }
        if op not in acceptable_op:
            raise ValueError(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                  op, "op", acceptable_op))

        # Format the error message with the substring based on the op type.
        errors = {'LT': "less than {}",
                  'LE': "less than or equal to {}",
                  'GT': "greater than {}",
                  'GE': "greater than or equal to {}",
                  'EQ': "equal to {}",
                  'NE': "not equal to {}"
                  }
        if not acceptable_op[op](len(arg_value), length):
            if isinstance(arg_value, str):
                 raise ValueError(Messages.get_message(MessageCodes.INVALID_LENGTH_STRING_ARG,
                                                  arg_name, errors[op].format(length)))
            raise ValueError(Messages.get_message(MessageCodes.INVALID_LENGTH_ARG, type(arg_value).__name__,
                                                  arg_name, errors[op].format(length)))
        return True

    @staticmethod
    @skip_validation()
    def _validate_file_exists(file_path):
        """
        DESCRIPTION:
            Function to validate whether the path specified is a file and if it exists.
            Supports both single file path (str) and list of file paths.
        PARAMETERS:
            file_path:
                Required Argument.
                Specifies the path of the file or list of file paths.
                Types: str or list of str
        RETURNS:
            True, if all paths are files and exist.
        RAISES:
            TeradataMLException
        EXAMPLES:
            Example 1: When a single file path is specified.
            >>> _Validators._validate_file_exists("/data/mapper.py")
            Example 2: When a list of file paths is specified.
            >>> _Validators._validate_file_exists(["/data/mapper.py", "/data/other.py"])
        """
        file_paths = [file_path] if isinstance(file_path, str) else file_path
        invalid_paths = []
        
        # Validate if each file path exists and is a file.
        for fp in file_paths:
            if not Path(fp).exists() or not os.path.isfile(fp):
                invalid_paths.append(fp)
        
        # If any of the file paths is invalid, raise an exception.
        if invalid_paths:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.INPUT_FILE_NOT_FOUND).format(", ".join(invalid_paths)),
                MessageCodes.INPUT_FILE_NOT_FOUND)
    
        return True

    @staticmethod
    @skip_validation()
    def _validate_mutually_exclusive_arguments(arg1, err_disp_arg1_name, arg2,
                                               err_disp_arg2_name, skip_all_none_check=False):
        """
        DESCRIPTION:
            Function to validate whether "arg1" and "arg2" are mutually exclusive.

        PARAMETERS:
            arg1:
                Required Argument.
                Specifies the value of argument1.
                Types: Any

            err_disp_arg1_name:
                Required Argument.
                Specifies the name of argument1.
                Types: str

            arg2:
                Required Argument.
                Specifies the value of argument2.
                Types: Any

            err_disp_arg2_name:
                Required Argument.
                Specifies the name of argument2.
                Types: str

            skip_all_none_check:
                Optional Argument.
                Specifies whether to skip check when arg1 and arg2 both are None.
                Default Value: False
                Types: bool

        RETURNS:
            True, if either arg1 or arg2 is None or both are None.

        RAISES:
            TeradataMLException
            
        EXAMPLES:
            _Validators._validate_mutually_exclusive_arguments(arg1, "arg1", arg2, "arg2")
                """
        both_args_none = arg1 is None and arg2 is None
        if skip_all_none_check:
            both_args_none = False

        # Either both the arguments are specified or both are None.
        if all([arg1, arg2]) or both_args_none:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT, err_disp_arg1_name,
                err_disp_arg2_name), MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)
        return True

    @staticmethod
    @skip_validation()
    def _validate_mutually_exclusive_argument_groups(*arg_groups, all_falsy_check=False,
                                                     empty_check=False,
                                                     return_all_falsy_status=False):
        """
        DESCRIPTION:
            Function to validate mutual exclusiveness of group of arguments.

        PARAMETERS:
            *arg_groups:
                Specifies variable length argument list where each argument in list is a dictionary
                representing one group of arguments which should be mutually exclusive from
                other groups of arguments. Each dictionary contains key-value pairs for argument
                name and its value.

            all_falsy_check:
                Optional Argument.
                Specifies whether to throw Teradataml Exception when all arguments in all argument
                groups hold Falsy/null values.
                Default Value: False
                Types: bool

            empty_check:
                Optional Argument.
                Specifies whether to treat empty values like empty string and empty list as None or not.
                When set to True, empty string and empty list are treated as None.
                Default Value: False
                Types: bool

            return_all_falsy_status:
                Optional Argument.
                Specifies whether to return the boolean flag which states if all arguments in all argument
                groups hold Falsy/null values.
                Default Value: False
                Types: bool

        RETURNS:
            * When "return_all_falsy_status" is True:
                * True: If all arguments in all argument groups hold Falsy/null values.
                * False: If all arguments in all argument groups do not hold Falsy/null values.
            * When "return_all_falsy_status" is False:
                None
        RAISES:
            TeradataMLException

        EXAMPLES:
            # Example 1: When groups of arguments are not mutually exclusive.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": "arg1"},
            ...                                                          {"arg2": "arg2"},
            ...                                                          {"arg3": "arg3", "arg4": "arg4"})
            [Teradata][teradataml](TDML_2061) Provide either '['arg1']' argument(s) or '['arg2']' argument(s) or '['arg3', 'arg4']' argument(s).

            # Example 2: When groups of arguments are mutually exclusive.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": None},
            ...                                                          {"arg2": None},
            ...                                                          {"arg3": "arg3", "arg4": "arg4"})

            # Example 3: When all groups of arguments hold falsy values
            #          and "all_falsy_check" is set to True.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": None},
            ...                                                          {"arg2": None},
            ...                                                          {"arg3": None, "arg4": None},
            ...                                                          all_falsy_check=True)
            [Teradata][teradataml](TDML_2061) Provide either '['arg1']' argument(s) or '['arg2']' argument(s) or '['arg3', 'arg4']' argument(s).

            # Example 4: When all groups of arguments hold falsy values
            #            and "all_falsy_check" is set to False.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": None},
            ...                                                          {"arg2": None},
            ...                                                          {"arg3": None, "arg4": None})

            # Example 5: When all groups of arguments hold falsy values
            #            and "all_falsy_check" is set to False and
            #            "return_all_falsy_status" is set to True.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": None},
            ...                                                          {"arg2": None},
            ...                                                          {"arg3": None, "arg4": None},
            ...                                                          return_all_falsy_status=True)
            True

            # Example 6: When groups of arguments are mutually exclusive
            #            considering empty list and empty string as falsy values.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": ""},
            ...                                                          {"arg2": []},
            ...                                                          {"arg3": "arg3", "arg4": "arg4"},
            ...                                                          empty_check=True)

            # Example 7: When all groups of arguments hold falsy values
            #            considering empty list and empty string as falsy values
            #            and "all_falsy_check" is set to True.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": ""},
            ...                                                          {"arg2": []},
            ...                                                          {"arg3": [], "arg4": None},
            ...                                                          {"arg5": "", "arg6": None},
            ...                                                          empty_check=True,
            ...                                                          all_falsy_check=True)
            TeradataMlException: [Teradata][teradataml](TDML_2061) Provide either '['arg1']' argument(s) or '['arg2']' argument(s) or '['arg3', 'arg4']' argument(s) or '['arg5', 'arg6']' argument(s).

            # Example 8: When groups of arguments are not mutually exclusive
            #            considering empty list and empty string as valid values.
            >>> _Validators._validate_mutually_exclusive_argument_groups({"arg1": ""},
            ...                                                          {"arg2": []},
            ...                                                          {"arg3": "arg3", "arg4": "arg4"})
            TeradataMlException: [Teradata][teradataml](TDML_2061) Provide either '['arg1']' argument(s) or '['arg2']' argument(s) or '['arg3', 'arg4']' argument(s).

        """
        all_groups_falsy = True
        mutually_exclusive_groups = True
        non_falsy_groups = []
        for arg_grp in arg_groups:
            if empty_check:
                # Treat empty string and empty list as falsy Value.
                is_group_falsy = not any(arg_grp.values())
            else:
                # Treat only None as falsy Value.
                is_group_falsy = not any(value is not None for value in arg_grp.values())
            if not is_group_falsy:
                non_falsy_groups.append(arg_grp)

                # Current group is having non-falsy values and already traversed
                # group(s) also has(have) non-falsy values. So set "mutually_exclusive_groups" to False.
                if not all_groups_falsy:
                    mutually_exclusive_groups = False

            all_groups_falsy = all_groups_falsy and is_group_falsy

        # Raise error if any one of the below-mentioned conditions is True:
        # More than one group has non-falsy values.
        # All groups have all falsy values and "all_falsy_check" is True.
        if not mutually_exclusive_groups or (all_falsy_check and all_groups_falsy):
            if not non_falsy_groups:
                non_falsy_groups = [str(list(arg_grp.keys())) for arg_grp in arg_groups]
            else:
                non_falsy_groups = [str(list(non_falsy_group.keys())) for non_falsy_group in non_falsy_groups]
            error_msg = Messages.get_message(
                MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT, str(non_falsy_groups[0]),
                "' argument(s) or \'".join(non_falsy_groups[1:]))

            raise TeradataMlException(error_msg, MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)

        if return_all_falsy_status:
            return all_groups_falsy

    @staticmethod
    @skip_validation()
    def _validate_mutually_inclusive_n_arguments(**kwargs):
        """
        DESCRIPTION:
            Function to validate mutual inclusiveness of group of arguments.

        PARAMETERS:
            **kwargs:
                Specifies variable number of keyword arguments which are to be
                validated for mutual inclusiveness.

        RETURNS:
            True, if arguments are mutually inclusive.

        RAISES:
            TeradataMLException

        EXAMPLES:
            Example 1: When all arguments have non-None values.
            >>> _Validators._validate_mutually_inclusive_n_arguments(arg1="arg1", arg2="arg2",
            ...                                                      arg3="arg3", arg4="arg4")
            True

            Example 2: When one of the arguments is empty string.
            >>> _Validators._validate_mutually_inclusive_n_arguments(arg1="arg1", arg2="arg2",
            ...                                                      arg3="arg3", arg4="")
            TeradataMlException

            Example 3: When one of the arguments is None.
            >>> _Validators._validate_mutually_inclusive_n_arguments(arg1="arg1", arg2=None,
            ...                                                      arg3="arg3", arg4="arg4")
            TeradataMlException
        """
        # TODO: Handling of falsy values can be done in more appropriate way by
        #  differentiating None/empty string/empty list.
        if all(arg_value for arg, arg_value in kwargs.items()):
            return True
        else:
            arg_list = list(kwargs.keys())
            message = Messages.get_message(MessageCodes.MUST_PASS_ARGUMENT,
                                           arg_list[0], " and ".join(arg_list[1:]))
            raise TeradataMlException(message, MessageCodes.MUST_PASS_ARGUMENT)

    @staticmethod
    @skip_validation()
    def _validate_unexpected_column_type(df, col, col_arg, unexpected_types, check_exist=True, raise_error=True,
                                         case_insensitive=False):
        """
        Internal function to validate the column existence and type of an input DataFrame column against
        a list of unexpected types.

        PARAMETERS
            df:
                Required Argument.
                Specifies the input teradataml DataFrame which has the column(s) to be tested
                for type.
                Types: teradataml DataFrame

            col:
                Required Argument.
                Specifies the column(s) in the input DataFrame to be tested for type.
                Types: str (or) ColumnExpression (or) List of strings(str)
                       or ColumnExpressions

            col_arg:
                Required Argument.
                Specifies the name of the argument used to pass the column(s) name.
                Types: str

            unexpected_types:
                Required Argument.
                Specifies unsupported teradatasqlalcehmy datatypes for the column is
                unexpected to be of type.
                Types: list of SQLAlchemy types

            check_exist:
                Optional Argument.
                Specifies a boolean flag that decides whether to check for column is
                existed in DataFrame or not.
                Default Values: True, raise exception if column is not of desired type.
                Types: bool

            raise_error:
                Optional Argument.
                Specifies a boolean flag that decides whether to raise error or just return True or False.
                Default Values: True, raise exception if column is not of desired type.
                Types: bool

        RETURNS:
            True, when the columns is of an expected type.

        RAISES:
            TeradataMlException, when the columns is not one of the expected types.

        EXAMPLES:
            _Validators._validate_unexpected_column_type(
            df, timecode_column, 'timecode_column', PTITableConstants.VALID_TIMECODE_DATATYPES)
        """

        columns = [col] if not isinstance(col, list) else col

        # Converting "unexpected_types" to tuple as isinstance can accept Tuple
        # of types too.
        unexpected_types = tuple(unexpected_types)

        for col in columns:
            # Get the name of the column if "col" is ColumnExpression.
            if not isinstance(col, str):
                col = col.name

            # Check for column existence.
            if check_exist:
                _Validators._validate_column_exists_in_dataframe(col, df._metaexpr, case_insensitive=case_insensitive)

            if isinstance(df[col].type, unexpected_types):
                if raise_error:
                    invalid_column_types = (col_type.__name__ for col_type in
                                            unexpected_types)
                    error_message = Messages.get_message(MessageCodes.INVALID_COLUMN_DATATYPE,
                                                         col,
                                                         col_arg,
                                                         "Unsupported",
                                                         ", ".join(invalid_column_types))
                    raise TeradataMlException(error_message, MessageCodes.INVALID_COLUMN_DATATYPE)

                else:
                    return False

        return True

    @staticmethod
    @skip_validation()
    def _validate_dependent_argument(dependent_arg, dependent_arg_value, independent_arg, independent_arg_value,
                                     msg_arg_value=None):
        """
        DESCRIPTION:
            Function validates if an independent argument is specified or not when
            dependent argument is specified. Raises error, if independent argument
            is not specified and dependent argument is specified, otherwise returns True.

        PARAMETERS:
            dependent_arg:
                Required Argument.
                Specifies the name of dependent argument.
                Types: String

            dependent_arg_value:
                Required Argument.
                Specifies the value of dependent argument.
                Types: Any

            independent_arg:
                Required Argument.
                Specifies the name of independent argument.
                Types: String

            independent_arg_value:
                Required Argument.
                Specifies the value of independent argument.
                Types: Any

            msg_arg_value:
                Optional Argument.
                Specifies the independent argument value to be printed in message
                instead of "(not None)".
                Types: String

        RETURNS:
            True, when the independent argument is present for the dependent
            argument.

        RAISES:
            TeradataMlException, when independent argument is not specified and
            dependent argument is specified.

        EXAMPLES:
            _Validators._validate_dependent_argument("dependent_arg_name", admissions_train,
                                                     "independent_arg_name", None)
            _Validators._validate_dependent_argument("dependent_arg_name", None,
                                                     "independent_arg_name", admissions_train)
            _Validators._validate_dependent_argument("dependent_arg_name", admissions_train,
                                                     "independent_arg_name", admissions_train)
            _Validators._validate_dependent_argument("dependent_arg_name", admissions_train,
                                                     "independent_arg_name", admissions_train,
                                                     "arg_val")
        """
        if dependent_arg_value is not None and independent_arg_value is None:
            error_code = MessageCodes.DEPENDENT_ARGUMENT
            error_msg = Messages.get_message(error_code, dependent_arg, independent_arg)
            if msg_arg_value is None:
                raise TeradataMlException(error_msg, error_code)
            else:
                raise TeradataMlException(error_msg.replace("(not None)", "as '{}'".format(msg_arg_value)),
                                          MessageCodes.DEPENDENT_ARGUMENT)
        return True
    
    @staticmethod
    @skip_validation()
    def _validate_unsupported_argument(arg, arg_name):
        """
        DESCRIPTION:
            Validation to reject unsupported arguments.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies the value passed for the argument that is unsupported.
                Types: any

            arg_name:
                Required Argument.
                Specifies the name of the argument to be printed in error message.
                Types: str

        RAISES:
            ValueError, If arg is not None, indicating an unsupported argument was used.

        RETURNS:
            True, If the argument is not provided (i.e., None), allowing execution to proceed.

        EXAMPLES:
            _Validators._validate_unsupported_argument(kwargs.get("task_type", None), "task_type")
            _Validators._validate_unsupported_argument(kwargs.get("is_fraud", None), "is_fraud")
            _Validators._validate_unsupported_argument(kwargs.get("is_churn", None), "is_churn")
        """
        error_code = MessageCodes.UNSUPPORTED_ARGUMENT
        error_msg = Messages.get_message(error_code, arg_name, arg_name)
        if arg is not None:
            raise TeradataMlException(error_msg, error_code)
        return True

    @staticmethod
    @skip_validation()
    def _validate_dependent_method(dependent_mtd, independent_mtd, independent_mtd_calls):
        """
        DESCRIPTION:
            Function validates if an independent method has been called before a dependent method.
            Raises an error if the independent method is not called before the dependent method is called,
            otherwise, returns True.

        PARAMETERS:
            dependent_mtd:
                Required Argument.
                Specifies the name of dependent method.
                Types: String

            independent_mtd:
                Required Argument.
                Specifies the name of independent method.
                Types: String or List of Strings

            independent_mtd_calls:
                Required Argument.
                Specifies the flag to check whether independent method is called or not.
                Types: bool or List of bool

        RETURNS:
            True, when the independent method is called before the dependent method.

        RAISES:
            TeradataMlException, when independent method is not called before the
            dependent method.

        EXAMPLES:
            _Validators._validate_dependent_method("dependent_method", "independent_method", False)
            _Validators._validate_dependent_method("dependent_method", "independent_method", True)
            _Validators._validate_dependent_method("dependent_method", ["independent_method1", "independent_method2"], [False, False])
        """
        # Check if all independent method calls are False
        independent_mtd_calls = [independent_mtd_calls] \
        if not isinstance(independent_mtd_calls, list) else independent_mtd_calls
        all_false = all(not value for value in independent_mtd_calls)

        # Check if any of the independent method is called before dependent method
        if dependent_mtd and all_false:
            error_code = MessageCodes.DEPENDENT_METHOD

            if isinstance(independent_mtd, str):
                independent_mtd = [independent_mtd]
            independent_mtd = ' or '.join(f"'{item}'" for item in independent_mtd)   

            error_msg = Messages.get_message(error_code, independent_mtd, dependent_mtd)
            raise TeradataMlException(error_msg, error_code)
        return True

    @staticmethod
    @skip_validation()
    def _validate_py_type_for_td_type_conversion(py_type, py_type_arg_name):
        """
        DESCRIPTION:
            Function to validate python type, which needs to be converted to TD Type.
            This function checks whether the python type can be converted to a TD
            type or not. If PY type is not able to convert TD Type, it then raises
            an error.

        PARAMETERS:
            py_type:
                Required Argument.
                Specifies the python type.
                Types: Any

            py_type_arg_name:
                Required Argument.
                Specifies the name of argument which holds python variable.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMLException

        EXAMPLES:
            _Validators._validate_py_type_for_td_type_conversion(int, "arg1")
        """
        if py_type not in _DtypesMappers.PY_TD_MAPPER:
            error_code = MessageCodes.UNSUPPORTED_DATATYPE
            error_msg = Messages.get_message(
                error_code, py_type_arg_name, '[{}]'.format(", ".join((t.__name__ for t in _DtypesMappers.PY_TD_MAPPER))))
            raise TeradataMlException(error_msg, error_code)

    @staticmethod
    @skip_validation()
    def _validate_function_install_location_is_set(option, function_type, option_name):
        """
         DESCRIPTION:
             Function to validate whether install location for functions is set.

         PARAMETERS:
             option:
                 Required Argument.
                 Specifies the configuration option value to validate.
                 Types: str

             function_type:
                 Required Argument.
                 Specifies the type of function to check installed location for.
                 Types: str

            option_name:
                 Required Argument.
                 Specifies the configuration option name.
                 Types: str

         RETURNS:
             None

         RAISES:
             TeradataMLException

         EXAMPLES:
             _Validators._validate_function_install_location_is_set(
             configure.byom_install_location,
             "Bring Your Own Model",
             "configure.byom_install_location")
         """
        # Check whether an empty string is passed to "option".
        _Validators._validate_input_columns_not_empty(option, option_name)

        if option is None:
            message = Messages.get_message(MessageCodes.UNKNOWN_INSTALL_LOCATION,
                                           "{} functions".format(function_type),
                                           "option '{}'".format(option_name))
            raise TeradataMlException(message, MessageCodes.MISSING_ARGS)

    @staticmethod
    @skip_validation()
    def _check_table_exists(conn, table_name,
                            schema_name,
                            raise_error_if_does_not_exists=True,
                            additional_error=''):
        """
        DESCRIPTION:
            Check whether table specified exists or not.

        PARAMETERS:
            raise_error_if_does_not_exists:
                Optional Argument.
                Specifies the flag to decide whether to raise error when table name specified does not exist.
                Default Value: True (Raise exception)
                Types: bool

            additional_error:
                Optional Argument.
                Specifies the additional error message to display along with standard message.
                Default Value: ''
                Types: String

        RAISES:
            TeradataMlException.

        RETURNS:
            True, if table exists, else False.

        EXAMPLES:
            >>>  _check_table_exists('model_table_name','model_schema_name')
        """

        # Check whether table exists on the system or not.
        table_exists = conn.dialect.has_table(conn, table_name=table_name,
                                              schema=schema_name, table_only=True)

        # If tables exists, return True.
        if table_exists:
            return True

        # We are here means the specified table does not exist.
        # Let's raise error if 'raise_error_if_does_not_exists' set to True.
        if raise_error_if_does_not_exists:
            # Raise error, as the specified table_name does not exist.
            # TABLE_DOES_NOT_EXIST
            raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_DOES_NOT_EXIST,
                                                           schema_name, table_name, additional_error),
                                      MessageCodes.TABLE_DOES_NOT_EXIST)
        return False

    @staticmethod
    @skip_validation()
    def _check_empty_file(file_path):
        """
        Description:
            Function to validate whether the given file is not empty,
            given absolute file path.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute file path of the file.
                Types: str

        RETURNS:
            Boolean

        RAISES:
            TeradataMlException

        EXAMPLES:
            _check_empty_file("/abc/xyz.txt")
        """

        if os.stat(file_path).st_size == 0:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.EMPTY_FILE,
                                     "{}".format(file_path)),
                MessageCodes.EMPTY_FILE)
        return True

    @staticmethod
    @skip_validation()
    def _validate_mutually_inclusive_arguments(arg1, err_disp_arg1_name, arg2,
                                               err_disp_arg2_name):
        """
        DESCRIPTION:
            Function to validate whether "arg1" and "arg2" are mutually inclusive.

        PARAMETERS:
            arg1:
                Required Argument.
                Specifies the value of argument1.
                Types: Any

            err_disp_arg1_name:
                Required Argument.
                Specifies the name of argument1.
                Types: str

            arg2:
                Required Argument.
                Specifies the value of argument2.
                Types: Any

            err_disp_arg2_name:
                Required Argument.
                Specifies the name of argument2.
                Types: str

        RETURNS:
            True, if both arg1 and arg2 are present or both are None.

        RAISES:
            TeradataMLException

        EXAMPLES:
            _Validators._validate_mutually_inclusive_arguments(arg1, "arg1", arg2, "arg2")
                """
        both_args_none = arg1 is None and arg2 is None
        #  If below handles 0 value.
        #  0 turns to False using bool(0) but 0 is a valid value and should return True.
        arg1 = True if arg1 == 0 else bool(arg1)
        arg2 = True if arg2 == 0 else bool(arg2)

        # Either both the arguments are specified or both are None.
        if not (all([arg1, arg2]) or both_args_none):
            arg_order = [err_disp_arg1_name, err_disp_arg2_name] if arg1 \
                else [err_disp_arg2_name, err_disp_arg1_name]
            raise TeradataMlException(Messages.get_message(
                MessageCodes.DEPENDENT_ARGUMENT, arg_order[0],
                arg_order[1]), MessageCodes.DEPENDENT_ARGUMENT)
        return True

    @staticmethod
    @skip_validation()
    def _validate_file_extension(file_path, extension):
        """
        DESCRIPTION:
            Function to validate whether the file has a specified extension.

            PARAMETERS:
                file_path:
                    Required Argument.
                    Specifies the file path or file name.
                    Types: str

                extension:
                    Required Argument.
                    Specifies the extension of the file.
                    Types: str OR list of Strings (str)

            RETURNS:
                True, if the file has specified extension.

            RAISES:
                TeradataMLException

            EXAMPLES:

                _Validators._validate_file_extension("/data/mapper.py",".py")
                _Validators._validate_file_extension("ml__demoenv_requirements_1605727131624097.txt",".txt")
        """
        extension = extension if isinstance(extension, list) else [extension]
        file_extension = file_path.lower().split('.')[-1]
        if file_extension not in extension:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.UNSUPPORTED_FILE_EXTENSION).format("{}".format(extension)),
                MessageCodes.UNSUPPORTED_FILE_EXTENSION)

        return True

    @staticmethod
    @skip_validation()
    def _validate_argument_is_not_None(arg, arg_name, additional_error="", reverse=False):
        """
        DESCRIPTION:
            Check whether the argument provided is not None.
            If parameter reverse is set to True, the validation is reversed to
            check whether argument provided is None.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies the argument to be validated.
                Types: str

            arg_name:
                Required Argument.
                Specifies the name of the argument to be printed in error message.
                Types: str

            additional_error:
                Optional Argument.
                Specifies the additional error message to display along with standard message.
                Default value=""
                Types: str

            reverse:
                Optional Argument.
                Specifies whether to reverse the validation.
                Returns True if arg is None, False if arg is not None.
                Default value=False
                Types: bool


        RAISES:
            ValueError.

        RETURNS:
            True, if the argument is not None, else False.

        EXAMPLES:
            >>>  _validate_argument_is_not_None(table_name, "table_name", additional_error)
        """
        if not reverse:
            # Raise an error if the argument is None.
            if arg is None:
                raise ValueError(Messages.get_message(MessageCodes.ARG_NONE, arg_name, "None", additional_error))
            return True
        else:
            # Raise an error if the argument is not None.
            if arg is not None:
                raise ValueError(Messages.get_message(MessageCodes.ARG_NONE, arg_name,
                                                      "provided {}".format(additional_error), ""))
            return True

    @staticmethod
    @skip_validation()
    def _validate_dataframe(df, raise_error=True):
        """
        This is an internal function checks whether the dataframe is none
        or not. If not none then checks the dataframe type and length of columns.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the dataframe.
                Types: pandas.DataFrame or teradataml.dataframe.dataframe.DataFrame

            raise_error:
                Optional Argument.
                Specifies whether to raise an exception or not.
                Default Values: True
                Types: bool

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            _validate_dataframe(df)

        """
        from teradataml.dataframe import dataframe as tdmldf

        valid = False
        if df is not None:
            if isinstance(df, pd.DataFrame) and len(df.columns) > 0:
                valid = True
            elif isinstance(df, tdmldf.DataFrame) and len(df._metaexpr.c) > 0:
                valid = True
            else:
                valid = False

        if raise_error and not valid:
            raise TeradataMlException(Messages.get_message(MessageCodes.IS_NOT_VALID_DF),
                                      MessageCodes.IS_NOT_VALID_DF)

    @staticmethod
    @skip_validation()
    def _validate_column_value_length(argument_name, argument_value, allowed_length,
                                      operation='perform the operation'):
        """
        DESCRIPTION:
            Function to validate length of string against permitted value.

        PARAMETERS:
            argument_name:
                Required Argument.
                Specifies the name of the argument whose value
                will be checked against permitted length.
                This is used while raising an error.
                Types: str.

            argument_value:
                Required Argument.
                Specifies the string whose length will be checked against permitted length.
                Types: str.

            allowed_length:
                Required Argument.
                Specifies the allowed length for argument value.
                Types: int.

            operation:
                Optional Argument.
                Specifies the name of operation which will fail, if this check fails.
                Default value: 'perform the operation'.
                Types: str.

        RETURNS:
            None.

        RAISES:
            TeradataMlException - EXECUTION_FAILED, ValueError

        EXAMPLES:
            >>> _validate_column_value_length("Description", "KMeans model", 150, "save the model")
        """
        try:
            _Validators._validate_str_arg_length(argument_name, argument_value, 'LE', allowed_length)
        except ValueError:
            error_code = MessageCodes.EXECUTION_FAILED
            error_msg = Messages.get_message(
                error_code, operation,
                'Length of argument {0} ({1}) is more than the allowed length ({2}).'
                .format(argument_name, len(argument_value), allowed_length))
            raise TeradataMlException(error_msg, error_code)
        return True

    @staticmethod
    @skip_validation()
    def _validate_list_lengths_equal(list1, arg_name1, list2, arg_name2):
        """
        DESCRIPTION:
            Check if length of the lists is same or not.

        PARAMETERS:
            list1:
                Required Argument.
                Specifies the first list to check the length against "list2".
                Types: list

            arg_name1:
                Required Argument.
                Specifies the name of the argument that accepts "list1" as input.
                This is used while raising an error.
                Types: str

            list2:
                Required Argument.
                Specifies the second list to check the length against "list1".
                Types: list

            arg_name2:
                Required Argument.
                Specifies the name of the argument that accepts "list2" as input.
                This is used while raising an error.
                Types: str

        RETURNS:
            None.

        RAISES:
            ValueError

        EXAMPLES:
            _Validators._validate_list_lengths_equal(self.coordinates, "coordinates",
                                                     self.timestamps, "timestamps")
        """
        if len(list1) != len(list2):
            # Raise error, if length of both lists is not same.
            err_ = Messages.get_message(MessageCodes.INVALID_LENGTH_ARGS,
                                        "'{}' and '{}'".format(arg_name1, arg_name2))
            raise ValueError(err_)
        return True

    @staticmethod
    @skip_validation()
    def _validate_dict_argument_key_value(arg_name, arg_dict, key_types=None, value_types=None,
                                          key_permitted_values=None, value_permitted_values=None,
                                          value_empty_string=True):
        """
        DESCRIPTION:
            Internal function to validate type and permitted values
            for keys and values in a dictionary argument.

        PARAMETERS:
            arg_name:
                Required Argument.
                Specifies the name of the dictionary argument.
                Types: str

            arg_dict:
                Required Argument.
                Specifies the dictonary value of "arg_name".
                Types: dict

            key_types:
                Optional Argument.
                Specifies the types, 'keys' of the "arg_dict" can take.
                Types: Any type or tuple of types

            value_types:
                Optional Argument.
                Specifies the types, 'values' assigned to 'keys' of
                "arg_dict" can take.
                Types: Any type or tuple of types

            key_permitted_values:
                Optional Argument.
                Specifies the permitted values for the 'keys' of "arg_dict".
                Types: list

            value_permitted_values:
                Optional Argument.
                Specifies the permitted values for the 'values' assgined to 'keys' 
                of "arg_dict".
                Types: list
            
            value_empty_string:
                Optional Argument.
                Specifies the whether 'values' assigned to 'keys' of "arg_dict"
                can accept empty string.
                Set to True, dictionary value with empty string is accepted.
                Set to False, dictionary value with empty string is not accepted.
                Default Value: True
                Types: bool

        RETURNS:
            bool

        RAISES:
            TypeError, ValueError

        EXAMPLES:
            _Validators._validate_dict_argument_key_value("name", {"a":3, "b":4}, (str), (int))
            _Validators._validate_dict_argument_key_value(arg_name="columns", arg_dict=columns,
                                                          key_types=(ColumnExpression, _TupleOf(ColumnExpression)),
                                                          value_types=(str, int, float, NoneType))

        """
        info_matrix = []
        dict_keys_list = set()
        from teradataml.common.utils import UtilFuncs

        try:
            for key, value in arg_dict.items():
                # Validate duplicate keys exists or not.
                # If keys are not of type tuple, convert it to tuple.
                keys_list = (key,) if not isinstance(key, tuple) else key

                # If duplicate key exists raise exception. E.g.
                # di = {("key1", "key2"): "my_keys1",
                #       ("key1", "key3"): "my_keys2",
                #       "key2"          :  "my_keys3"}
                for k in keys_list:
                    # If ColumnExpression, get the column name.
                    if isinstance(k, ColumnExpression):
                        k_name, name = k.name, "ColumnExpression(s)"
                    else:
                        k_name, name = k, "Key names"

                    # If duplicate key exists raise exception.
                    if k_name in dict_keys_list:
                        raise TeradataMlException(Messages.get_message(
                            MessageCodes.DUPLICATE_DICT_KEYS_NAMES,
                            name, arg_name),
                            MessageCodes.DUPLICATE_PARAMETER)
                    else:
                        dict_keys_list.add(k_name)

                # Append "keys" and "values" into arg info matrix for type validation.
                if key_types is not None:
                    info_matrix.append(["<dict_key>", key, True, key_types, True])

                if value_types is not None:
                    info_matrix.append(
                        ["<dict_value>", value, True, value_types, not value_empty_string])

                # Validate permitted values for both "key" and "value" if permitted values
                # are provided.
                if key_permitted_values is not None:
                    _Validators._validate_permitted_values(arg=key,
                                                           permitted_values=key_permitted_values,
                                                           arg_name="<dict_key>",
                                                           case_insensitive=False,
                                                           includeNone=True)

                if value_permitted_values is not None:
                    _Validators._validate_permitted_values(arg=value,
                                                           permitted_values=value_permitted_values,
                                                           arg_name="<dict_value>",
                                                           case_insensitive=False,
                                                           includeNone=True)

            if key_types is not None or value_types is not None:
                # Validate types using already existing validator.
                _Validators._validate_function_arguments(info_matrix)

        except ValueError as ve:
            # Catch ValueError raised by '_validate_permitted_values' to
            # raise proper error message for dictionary argument.
            if "TDML_2007" in str(ve):
                permitted_values = value_permitted_values
                err_str = "value"
                err_val = value
                if "<dict_key>" in str(ve):
                    permitted_values = key_permitted_values
                    err_str = "key"
                    err_val = key
                raise ValueError(
                    Messages.get_message(MessageCodes.INVALID_DICT_ARG_VALUE, err_val,
                                         err_str, arg_name, permitted_values))

            # Catch ValueError raised by '_validate_function_arguments'
            # for empty string value.
            elif "TDML_2004" in str(ve):
                err_str = "Key" if "<dict_key>" in str(ve) else "Value"
                raise ValueError(
                    Messages.get_message(MessageCodes.DICT_ARG_KEY_VALUE_EMPTY,
                                         err_str, arg_name))

        except TypeError as te:
            # Catch TypeError raised by '_validate_function_arguments' to
            # raise proper error message for dictionary argument.
            permitted_types = value_types
            err_str = "value"
            if "<dict_key>" in str(te):
                permitted_types = key_types
                err_str = "key"

            permitted_types = [''.join(_Validators.__getTypeAsStr(kv_type))
                               if isinstance(kv_type, (_TupleOf, _ListOf)) else
                               kv_type.__name__ for kv_type in permitted_types]

            raise TypeError(
                Messages.get_message(MessageCodes.UNSUPPORTED_DICT_KEY_VALUE_DTYPE, err_str,
                                     arg_name, permitted_types))

        return True

    @staticmethod
    @skip_validation()
    def _validate_http_response(http_response, valid_status_code, error_msg):
        """
        DESCRIPTION:
            Internal function to validate the HTTP response.

        PARAMETERS:
            http_response:
                Required Argument.
                Specifies the response object recieved from HTTP request.
                Types: requests.models.Response OR httpx.Response

            valid_status_code:
                Required Argument.
                Specifies the HTTP response code of a request.
                Types: int

            error_msg:
                Required Argument.
                Specifies the error message to be displayed when response code is
                not equal to "valid_status_code".
                Types: str

        RETURNS:
            bool

        RAISES:
            TeradatamlException

        EXAMPLES:
            _Validators._validate_http_response(resp, 200, "test1")
        """
        if http_response.status_code != valid_status_code:
            err_ = Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                        error_msg,
                                        "Error-details: ({}){}".format(http_response.status_code, http_response.text))
            raise TeradataMlException(err_, MessageCodes.EXECUTION_FAILED)

        return True

    @staticmethod
    @skip_validation()
    def _validate_module_presence(module_name, function_name):
        """
        DESCRIPTION:
            Check if module being imported is present.

        PARAMETERS:
            module_name:
                Required Argument.
                Specifies the name of the module to import.
                Types: str

            function_name:
                Required Argument.
                Specifies the name of the function from where module is imported.
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataMlException

        EXAMPLES:
            _Validators._validate_module_presence("docker", "setup_sandbox_env")
        """
        import importlib

        try:
            importlib.import_module(module_name, package=None)
        except Exception as err:
            message = \
                Messages.get_message(
                    MessageCodes.IMPORT_PYTHON_PACKAGE,
                    module_name, module_name, function_name)
            raise TeradataMlException(message,
                                      MessageCodes.IMPORT_PYTHON_PACKAGE)
        return True

    @staticmethod
    @skip_validation()
    def _validate_ipaddress(ip_address):
        """
        DESCRIPTION:
            Check if ipaddress is valid.
        PARAMETERS:
            ip_address:
                Required Argument.
                Specifies the ip address to be validated.
                Types: str
        RETURNS:
            None.
        RAISES:
            TeradataMlException
        EXAMPLES:
            _Validators._validate_ipaddress("190.132.12.15")
        """
        import ipaddress

        try:
            ipaddress.ip_address(ip_address)
        except Exception as err:
            raise ValueError(Messages.get_message(
                MessageCodes.INVALID_ARG_VALUE).format(ip_address, "ip_address",
                                                       'of four numbers (each between 0 and 255) separated by periods'))

        return True

    @staticmethod
    @skip_validation()
    def _check_auth_token(func_name):
        """
        DESCRIPTION:
            Check if the user has set the authentication token.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the function name where the authentication token is required.
                Types: str

        RAISES:
            TeradataMLException

        RETURNS:
            None.

        EXAMPLES:
            >>> _Validators._check_auth_token("udf")
        """
        if _InternalBuffer.get("auth_token") is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.SET_REQUIRED_PARAMS, \
                                                           'Auth Token', func_name,
                                                           'set_auth_token'),
                                      MessageCodes.SET_REQUIRED_PARAMS)

        return True

    @staticmethod
    def _check_required_params(arg_value, arg_name, caller_func_name, target_func_name):
        """
        DESCRIPTION:
            Check if the required argument is not None.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the argument value to be
                checked for non None values.
                Types: str, float, int, bool

            arg_name:
                Required Argument.
                Specifies the argument name.
                Types: str

            caller_func_name:
                Required Argument.
                Specifies the function name which calls this function.
                This is required for the error message.
                Types: str

            target_func_name:
                Required Argument.
                Specifies the function name which the user needs to call
                so that the error is fixed.
                This is required for the error message.
                Types: str

        RAISES:
            TeradataMLException

        RETURNS:
            True.

        EXAMPLES:
            >>> _Validators._check_required_params("udf", "arg_name")
        """
        if arg_value is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.SET_REQUIRED_PARAMS, \
                                                           arg_name, caller_func_name,
                                                           target_func_name),
                                      MessageCodes.SET_REQUIRED_PARAMS)
        return True

    @staticmethod
    def _valid_list_length(arg_value, arg_name, required_length):
        """
        DESCRIPTION:
            Check if the argument has length matching the required length.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the argument value.
                Types: _ListOf

            arg_name:
                Required Argument.
                Specifies the argument name.
                Types: str

            required_length:
                Required Argument.
                Specifies the required list length.
                Types: int

        RAISES:
            TeradataMlException

        RETURNS:
            True.

        EXAMPLES:
            >>> _Validators._valid_list_length(["udf", "udf1"], "arg_name", 2)
        """
        if (isinstance(arg_value, list) and len(arg_value) != required_length) or \
                (not isinstance(arg_value, list)):
            raise TeradataMlException(Messages.get_message(
                MessageCodes.INVALID_LIST_LENGTH).format(arg_name,
                                                         required_length),
                                      MessageCodes.INVALID_LIST_LENGTH)
        return True

    @staticmethod
    @skip_validation()
    def _validate_non_empty_list_or_valid_selection(arg_list, arg_name):
        """
        DESCRIPTION:
            Validation to ensure that the given list-type argument is not empty or contains only invalid entries
            like None, '', 'None', etc.

        PARAMETERS:
            arg_list:
                Required Argument.
                Specifies the list or iterable for validation.
                Types: list

            arg_name:
                Required Argument.
                Specifies the argument name.
                Types: str

        RAISES:
            ValueError - If the list is None, empty, or contains only invalid values.

        RETURNS:
            True - If validation passes (non-empty and has valid entries).

        EXAMPLES:
        >>> _Validators._validate_non_empty_list_or_valid_selection(self.model_list, "List of models")
        """

        error_code = MessageCodes.LIST_SELECT_NONE_OR_EMPTY
        if not arg_list or all(x in [None, "None", ""] for x in arg_list):
            raise TeradataMlException(Messages.get_message(error_code).format(arg_name), error_code)
        return True

    @staticmethod
    def _validate_temporal_table_type(df_type, api_type='method', api_name='as_of'):
        """
        DESCRIPTION:
            Function to validate temporal table type.

        PARAMETERS:
            df_type:
                Required Argument.
                Specifies the type of temporal table.
                Types: str

            api_type:
                Required Argument.
                Specifies the type of API.
                Types: str

            api_name:
                Required Argument.
                Specifies the name of API.
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Validators._validate_temporal_table_type('method', 'as_of')
        """
        if df_type not in (DataFrameTypes.VALID_TIME_VIEW.name,
                           DataFrameTypes.TRANSACTION_TIME_VIEW.name,
                           DataFrameTypes.BI_TEMPORAL_VIEW.name,
                           DataFrameTypes.BI_TEMPORAL.name,
                           DataFrameTypes.TRANSACTION_TIME.name,
                           DataFrameTypes.VALID_TIME.name,
                           DataFrameTypes.VALID_TIME_VOLATILE_TABLE.name,
                           DataFrameTypes.TRANSACTION_TIME_VOLATILE_TABLE.name,
                           DataFrameTypes.BI_TEMPORAL_VOLATILE_TABLE.name
                           ):
            raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_USAGE,
                                                           api_type,
                                                           "'{}'".format(api_name),
                                                           "when underlying table or view is temporal type"),
                                      MessageCodes.INVALID_USAGE)

    @staticmethod
    def _validate_as_of_arguments(df_type, argument_name='valid_time'):
        """
        DESCRIPTION:
            Function to validate arguments passed for method as_of.
            One can not pass argument 'valid_time' for a transaction time table
            One can not pass argument 'transaction_time' for a valid time table.
            Both the validations are done in this validator.

        PARAMETERS:
            df_type:
                Required Argument.
                Specifies the type of temporal table.
                Types: str

            argument_name:
                Optional Argument.
                Specifies the name of the argument.
                Default Value: 'valid_time'
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Validators._validate_temporal_table_type('method', 'as_of')
        """
        valid_types = (
                DataFrameTypes.TRANSACTION_TIME_VIEW.name,
                DataFrameTypes.TRANSACTION_TIME.name,
                DataFrameTypes.TRANSACTION_TIME_VOLATILE_TABLE.name
        )
        table_type = 'transaction time dimension'

        if argument_name == 'valid_time':
            valid_types = (DataFrameTypes.VALID_TIME_VIEW.name,
                           DataFrameTypes.VALID_TIME.name,
                           DataFrameTypes.VALID_TIME_VOLATILE_TABLE.name
                           )
            table_type = 'valid time dimension'

        bi_temporal_types = (
                DataFrameTypes.BI_TEMPORAL_VIEW.name,
                DataFrameTypes.BI_TEMPORAL.name,
                DataFrameTypes.BI_TEMPORAL_VOLATILE_TABLE.name
        )

        # Raise error only if it is not a bitemporal table.
        if (df_type not in bi_temporal_types) and (df_type not in valid_types):
            raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_USAGE,
                                                           'argument',
                                                           "'{}'".format(argument_name),
                                                           "when underlying table or view is in {}".format(table_type)),
                                      MessageCodes.INVALID_USAGE)

    @staticmethod
    def _validate_period_column_type(column_type):
        """
        DESCRIPTION:
            Function to validate the type of a period column.

        PARAMETERS:
            column_type:
                Required Argument.
                Specifies the type of the column to be validated.
                Types: Any

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            _Validators._validate_period_column_type(PERIOD_DATE)
        """
        if not isinstance(column_type, (PERIOD_DATE, PERIOD_TIMESTAMP)):
            raise TeradataMlException(
                Messages.get_message(
                    MessageCodes.INVALID_COLUMN_TYPE
                ).format(
                    "period column",
                    type(column_type).__name__,
                    "PERIOD_DATE or PERIOD_TIMESTAMP"
                ),
                MessageCodes.INVALID_COLUMN_TYPE
            )
    @staticmethod
    @skip_validation()
    def _validate_features_not_in_efs_dataset(df,
                                              feature_names,
                                              action):
        """
        DESCRIPTION:
            Function to validate whether the feature names provided
            are not present in the EFS dataset.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the EFS dataset dataframe.
                Types: teradataml.dataframe.dataframe.DataFrame

            feature_names:
                Required Argument.
                Specifies the feature names to be validated.
                Types: str or list of str

            action:
                Required Argument.
                Specifies the action to be performed.
                Permitted Values: 'archived', 'deleted'
                Types: str

        RETURNS:
            True, if the feature names are not present in the EFS dataset.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> _Validators._validate_features_not_in_efs_dataset(df, ["feature1", "feature2"], "delete")
        """
        if isinstance(feature_names, str):
            feature_names = [feature_names]

        invalid_df = df[(df['feature_name'].isin(feature_names))]

        if invalid_df.shape[0] > 0:
            names = set()
            datasets = set()
            for feature in invalid_df.itertuples():
                names.add(feature.feature_name)
                datasets.add(feature.dataset_id)
            datasets_str = ", ".join(f"'{dataset}'" for dataset in datasets)
            name_str = ", ".join(f"'{name}'" for name in names)

            error_code = MessageCodes.EFS_FEATURE_IN_DATASET
            error_msg = Messages.get_message(error_code,
                                             name_str,
                                             datasets_str,
                                             action)
            raise TeradataMlException(error_msg, error_code)

        return True

    @staticmethod
    def _validate_dataset_ids_not_in_efs(df, ids, data_domain, repo):
        """
        DESCRIPTION:
            Function to validate whether the dataset ids provided
            are not present in the EFS.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the EFS dataset dataframe.
                Types: teradataml.dataframe.dataframe.DataFrame

            ids:
                Required Argument.
                Specifies the dataset ids to be validated.
                Types: str or list of str

            data_domain:
                Required Argument.
                Specifies the data domain for the feature process.
                Types: str

            repo:
                Required Argument.
                Specifies the repository to be used for validation.
                Types: str

        RETURNS:
            True, if the dataset ids are not present in the EFS.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> _Validators._validate_features_not_in_efs_dataset(df, ["12-dek-3e3-dek"], "d1")
        """
        from teradataml.common.utils import UtilFuncs
        id_list_flag = False if isinstance(ids, str) else True
        list_ids = UtilFuncs._as_list(ids)

        # Check if the dataset ids are present in the domain.
        df = df[(df['id'].isin(list_ids)) &
                (df['data_domain'] == data_domain)]
        matched_ids = [i.id for i in df.select("id").itertuples()]
        # Get the list of dataset ids that are not present in the domain.
        missing_ids = [i for i in list_ids if i not in matched_ids] 

        # If there are ids that are not present in the domain,
        # raise an exception with appropriate error message.
        if len(missing_ids) > 0:
            if id_list_flag:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "Dataset", "id(s): {}".format(missing_ids),
                                                 data_domain) + " Use DatasetCatalog.list_datasets() to list valid dataset ids."
            else:
                # Check if the dataset id is present in any other domain.
                from teradataml.store.feature_store.utils import _FSUtils
                res = _FSUtils._get_data_domains(repo, ids, 'dataset')
                if res:
                    msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                    error_msg = Messages.get_message(msg_code, "Dataset", "id '{}'".format(ids),
                                                    data_domain, res)
                else:
                    msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                    error_msg = Messages.get_message(msg_code, "Dataset", "id '{}'".format(ids),
                                                    data_domain)
            raise TeradataMlException(error_msg, msg_code)

        return True


    @staticmethod
    @skip_validation()
    def _validate_duplicate_objects(objects, type_="features", arg_name='features'):
        """
        DESCRIPTION:
            Function to validate that there are no duplicate objects in the provided list.

        PARAMETERS:
            objects:
                Required Argument.
                Specifies the objects to validate for duplicates.
                Types: list or tuple

            type_:
                Optional Argument.
                Specifies the type of objects being validated.
                Default Value: "features"
                Types: str

            arg_name:
                Optional Argument.
                Specifies the name of the argument being validated.
                Default Value: "features"
                Types: str

        RAISES:
            TeradataMlException

        Returns:
            bool

        EXAMPLES:
            >>> load_examples_data('dataframe', 'sales')
            >>> df = DataFrame('sales')

            # Example 1: Validate duplicate features in the list.
            >>> feature1 = Feature("Jan", df.Jan)
            >>> _Validators._validate_duplicate_objects([feature1, 'Jan', 'Feb'])

            # Example 2: Validate duplicate datetime.datetime objects in tuple.
            >>> t = datetime.datetime(2025, 1, 1, 0, 0, 1)
            >>> td = datetime.date(2025, 1, 1)
            >>> _Validators._validate_duplicate_objects((td, td.strftime('%Y-%m-%d %H:%M:%S'), t))
        """
        from teradataml.common.utils import UtilFuncs
        from teradataml.store.feature_store.models import Feature
        seen = set()
        duplicates = set()

        if isinstance(objects, (list, tuple)):
            for obj in objects:
                if isinstance(obj, Feature):
                    name = obj.column_name
                elif isinstance(obj, (datetime.datetime, datetime.date)):
                    name = obj.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    name = obj

                if name in seen:
                    duplicates.add(name)
                else:
                    seen.add(name)

            if len(duplicates) > 0:
                msg = "{} in {}".format(
                    ", ".join(["'{}'".format(duplicate) for duplicate in sorted(duplicates)]),
                    "'{}' argument".format(arg_name)
                )
                raise TeradataMlException(
                    Messages.get_message(
                        MessageCodes.DF_DUPLICATE_VALUES,
                        type_,
                        msg
                    ),
                    MessageCodes.DF_DUPLICATE_VALUES)

        return True

    @staticmethod
    @skip_validation()
    def _validate_duplicate_values(df, columns, arg_name, columns_arg='entity column(s)'):
        """
        DESCRIPTION:
            Function to validate that there are no duplicate records in the DataFrame
            based on the specified columns.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the DataFrame to validate for duplicates.
                Types: teradataml DataFrame

            columns:
                Required Argument.
                Specifies the columns to check for duplicates.
                Types: str or list of str

            arg_name:
                Required Argument.
                Specifies the name of the argument being validated.
                Types: str
                
            columns_arg:
                Optional Argument.
                Specifies the name of the columns argument.
                Default Value: 'entity column(s)'
                Types: str

        RAISES:
            TeradataMlException

        Returns:
            bool

        EXAMPLES:
            >>> _Validators._validate_duplicate_records(df, ['col1', 'col2'], 'columns')
        """
        columns = [columns] if isinstance(columns, str) else columns
        df_ = df.groupby(columns).assign(total_rows_=func.count('*'))
        duplicate_recs = df_[df_.total_rows_ > 1].shape[0]

        if duplicate_recs > 0:
            msg = "in {} {} provided in argument {}".format(
                columns_arg,
                ", ".join(["'{}'".format(col) for col in columns]),
                "'{}'".format(arg_name)
            )
            raise TeradataMlException(
                Messages.get_message(
                    MessageCodes.DF_DUPLICATE_VALUES,
                    "values in {}".format(columns_arg),
                    msg
                ),
                MessageCodes.DF_DUPLICATE_VALUES)

        return True

    @staticmethod
    @skip_validation()
    def _validate_null_values(df, 
                              columns, 
                              arg_name, 
                              columns_arg='entity column(s)', 
                              operation='ingesting the features'):
        """
        DESCRIPTION:
            Function to validate that there are no null values in the specified columns
            of the DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the DataFrame to validate for null values.
                Types: teradataml DataFrame

            columns:
                Required Argument.
                Specifies the columns to check for null values.
                Types: str or list of str

            arg_name:
                Required Argument.
                Specifies the name of the argument being validated.
                Types: str
                
            columns_arg:
                Optional Argument.
                Specifies the name of the columns argument.
                Default Value: 'entity column(s)'
                Types: str
                
            operation:
                Optional Argument.
                Specifies the operation being performed.
                Default Value: 'ingesting the features'
                Types: str

        RAISES:
            TeradataMlException

        Returns:
            bool

        EXAMPLES:
            >>> _Validators._validate_null_values(df, ['col1', 'col2'], 'columns')
        """
        columns = [columns] if isinstance(columns, str) else columns
        col_expr = (df[columns[0]] == None)
        for column in columns[1:]:
            col_expr = col_expr | (df[column] == None)

        null_count = df[col_expr].shape[0]

        if null_count > 0:
            msg = "in {} {} provided in argument {}".format(
                columns_arg,
                ", ".join(["'{}'".format(col) for col in columns]),
                "'{}'".format(arg_name)
            )
            raise TeradataMlException(
                Messages.get_message(
                    MessageCodes.DF_NULL_VALUES,
                    columns_arg,
                    operation,
                    msg
                ),
                MessageCodes.DF_NULL_VALUES)

        return True

    @staticmethod
    @skip_validation()
    def _validate_archived_features(features_to_validate, archived_features, msg=""):
        """
        DESCRIPTION:
            Function to validate that the features are already archived or not.
            If archived, it raises an exception.

        PARAMETERS:
            features_to_validate:
                Required Argument.
                Specifies the features to be validated for archiving.
                Types: list of str

            archived_features:
                Required Argument.
                Specifies the set of already archived features.
                Types: set of str

            msg:
                Optional Argument.
                Specifies the additional message to be displayed in the exception.
                Default Value: ""
                Types: str

        RAISES:
            TeradataMlException

        Returns:
            bool

        EXAMPLES:
            >>> _Validators._validate_archived_features(['feature1', 'feature2'], {'feature1'})
        """
        features_to_validate = [features_to_validate] if isinstance(features_to_validate, str) \
            else features_to_validate
        archived_features = [f for f in features_to_validate if f in archived_features]

        if archived_features:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.FEATURES_ARCHIVED,
                                     ", ".join("'{}'".format(f) for f in archived_features),
                                     msg
                                     ),
                MessageCodes.FEATURES_ARCHIVED)

        return True

    @staticmethod
    @skip_validation()
    def _validate_any_argument_passed(args_dict):
        """
        DESCRIPTION:
            Check if any value in the argument dictionary is not None.
            If all values are None, raise an exception.

        PARAMETERS:
            args_dict:
                Required Argument.
                Specifies the argument to value dictionary to check.
                Types: dict

        RAISES:
            TeradataMlException

        Returns:
            bool

        EXAMPLES:
            >>> _Validators._validate_any_argument_passed({"arg1": None, "arg2": "abc"})
        """
        if all(value is None for value in args_dict.values()):
            msg_code = MessageCodes.EITHER_ANY_ARGUMENT
            argument_description = " or ".join(["'{}'".format(key) for key in args_dict.keys()])
            error_msg = Messages.get_message(msg_code, argument_description)
            raise TeradataMlException(error_msg, msg_code)

        return True
