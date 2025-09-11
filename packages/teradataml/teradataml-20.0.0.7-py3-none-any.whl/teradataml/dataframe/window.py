"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements the core framework that allows user to execute any Vantage Window Functions.
"""

from teradataml.utils.validators import _Validators
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from sqlalchemy import desc, nullsfirst, nullslast
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.utils import UtilFuncs
from teradataml.utils.dtypes import _Dtypes
from teradataml.telemetry_utils.queryband import collect_queryband


class Window:
    """ A class for executing window functions. """
    def __init__(self,
                 object,
                 partition_columns=None,
                 order_columns=None,
                 sort_ascending=True,
                 nulls_first=None,
                 window_start_point=None,
                 window_end_point=None,
                 ignore_window=False):
        """
        DESCRIPTION:
            Constructor for Window class.

        PARAMETERS:
            object:
                Required Argument.
                Specifies where the window object is initiated from.
                Window object can be initiated from either teradataml DataFrame
                or a column in a teradataml DataFrame.
                Types: teradataml DataFrame, _SQLColumnExpression

            partition_columns:
                Optional Argument.
                Specifies the name(s) of the column(s) over which the ordered
                aggregate function executes by partitioning the rows.
                Such a grouping is static.
                Notes:
                     1. If this argument is not specified, then the entire data
                        from teradataml DataFrame, constitutes a single
                        partition, over which the ordered aggregate function
                        executes.
                     2. "partition_columns" does not support CLOB and BLOB type
                        of columns.
                        Refer 'DataFrame.tdtypes' to get the types of the
                        columns of a teradataml DataFrame.
                Types: str OR list of Strings (str) OR ColumnExpression OR list of ColumnExpressions

            order_columns:
                Optional Argument.
                Specifies the name(s) of the column(s) to order the rows in a
                partition, which determines the sort order of the rows over
                which the function is applied.
                Note:
                    "order_columns" does not support CLOB and BLOB type
                    of columns.
                    Refer 'DataFrame.tdtypes' to get the types of the
                    columns of a teradataml DataFrame.
                Types: str OR list of Strings (str) OR ColumnExpression OR list of ColumnExpressions

            sort_ascending:
                Optional Argument.
                Specifies whether column ordering should be in ascending or
                descending order.
                Default Value: True (ascending)
                Note:
                    When "order_columns" argument is not specified, argument
                    is ignored.
                Types: bool

            nulls_first:
                Optional Argument.
                Specifies whether null results are to be listed first or last
                or scattered.
                Default Value: None
                Note:
                    When "order_columns" argument is not specified, argument is
                    ignored.
                Types: bool

            window_start_point:
                Optional Argument.
                Specifies a starting point for a window. Based on the integer
                value, n, starting point of the window is decided.
                    * If 'n' is negative, window start point is n rows
                      preceding the current row/data point.
                    * If 'n' is positive, window start point is n rows
                      following the current row/data point.
                    * If 'n' is 0, window start at current row itself.
                    * If 'n' is None, window start as Unbounded preceding,
                      i.e., all rows before current row/data point are
                      considered.
                Notes:
                     1. Value passed to this should always satisfy following condition:
                        window_start_point <= window_end_point
                     2. Following functions does not require any window to
                        perform window aggregation. So, "window_start_point" is
                        insignificant for below functions:
                        * cume_dist
                        * rank
                        * dense_rank
                        * percent_rank
                        * row_number
                        * lead
                        * lag
                Default Value: None
                Types: int

            window_end_point:
                Optional Argument.
                Specifies an end point for a window. Based on the integer value,
                n, starting point of the window is decided.
                    * If 'n' is negative, window end point is n rows preceding
                      the current row/data point.
                    * If 'n' is positive, window end point is n rows following
                      the current row/data point.
                    * If 'n' is 0, window end's at current row itself.
                    * If 'n' is None, window end's at Unbounded following,
                      i.e., all rows before current row/data point are
                      considered.
                Notes:
                     1. Value passed to this should always satisfy following condition:
                        window_start_point <= window_end_point
                     2. Following functions does not require any window to
                        perform window aggregation. So, "window_end_point" is
                        insignificant for below functions:
                        * cume_dist
                        * rank
                        * dense_rank
                        * percent_rank
                        * row_number
                        * lead
                        * lag
                Default Value: None
                Types: int

            ignore_window:
                Optional Argument.
                Specifies a flag to ignore parameters related to creating
                window ("window_start_point", "window_end_point") and use other
                arguments, if specified.
                When set to True, window is ignored, i.e., ROWS clause is not
                included.
                When set to False, window will be created, which is specified
                by "window_start_point" and "window_end_point" parameters.
                Default Value: False
                Types: bool

        RAISES:
            TypeError OR ValueError

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = Window(object = df)

            # Create a window from a teradataml DataFrame column.
            window = Window(object = df.Feb)
        """
        self.__object = object
        self.__partition_columns = partition_columns
        self.__order_columns = order_columns
        self.__sort_ascending = sort_ascending
        self.__nulls_first = nulls_first
        self.__window_start_point = window_start_point
        self.__window_end_point = window_end_point
        self.__ignore_window = ignore_window

        from teradataml.dataframe.dataframe import DataFrame, DataFrameGroupBy
        from teradataml.dataframe.sql import _SQLColumnExpression

        awu_matrix = []
        awu_matrix.append(["object", object, False, (DataFrame, _SQLColumnExpression)])
        awu_matrix.append(["partition_columns", partition_columns, True, (str, list, _SQLColumnExpression), True])
        awu_matrix.append(["order_columns", order_columns, True, (str, list, _SQLColumnExpression), True])
        awu_matrix.append(["sort_ascending", sort_ascending, True, bool])
        awu_matrix.append(["nulls_first", nulls_first, True, (bool, type(None))])
        awu_matrix.append(["window_start_point", window_start_point, True, int])
        awu_matrix.append(["window_end_point", window_end_point, True, int])
        awu_matrix.append(["ignore_window", ignore_window, True, bool])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        # Check "window_end_point" is always greater than or equal to "window_start_point".
        if window_start_point is not None and window_end_point is not None and\
                window_start_point > window_end_point:
            raise ValueError(Messages.get_message(MessageCodes.INT_ARGUMENT_COMPARISON,
                                                  "window_end_point",
                                                  "greater than or equal",
                                                  "window_start_point"))

        self.__is_window_on_tdml_column = isinstance(self.__object, _SQLColumnExpression)

        # Variable to check if the Window object is initiated on DataFrameGroupBy.
        self.__is_window_on_tdml_groupby_dataframe = isinstance(
            self.__object, DataFrameGroupBy)

        # A variable to decide whether the output columns should contain
        # unsupported sort columns or not.
        self.__sort_check_required = self.__partition_columns is None and self.__order_columns is None

        # Check whether columns mentioned in "partition_columns" are existed in
        # teradataml DataFrame and supports sorting.
        if partition_columns:
            self.__validate_window_columns(partition_columns, "partition_columns")

        # Check whether columns mentioned in "order_columns" are existed in
        # teradataml DataFrame and supports sorting.
        if order_columns:
            self.__validate_window_columns(order_columns, "order_columns")

        # Raise Error, if the Column is of type CLOB or BLOB, and window has no
        # "partition_columns" and no "order_columns".
        if self.__is_window_on_tdml_column and self.__sort_check_required and \
                type(self.__object.type) in _Dtypes._get_sort_unsupported_data_types():
            raise TeradataMlException(Messages.get_message(MessageCodes.EXECUTION_FAILED,
                                                           "create Window",  "Window with"
                                                           " no 'partition_columns' and no 'order_columns' "
                                                           "on {} type of Column({}) is unsupported."
                                                           "".format(self.__object.type, self.__object.name)),
                                                           MessageCodes.EXECUTION_FAILED)

        self.__aggregate_functions = ['sum',
                                      'avg',
                                      'mean',
                                      'corr',
                                      'count',
                                      'covar_pop',
                                      'covar_samp',
                                      'cume_dist',
                                      'dense_rank',
                                      'first_value',
                                      'last_value',
                                      'lag',
                                      'lead',
                                      'max',
                                      'min',
                                      'percent_rank',
                                      'rank',
                                      'regr_avgx',
                                      'regr_avgy',
                                      'regr_count',
                                      'regr_intercept',
                                      'regr_r2',
                                      'regr_slope',
                                      'regr_sxx',
                                      'regr_sxy',
                                      'regr_syy',
                                      'row_number',
                                      'std',
                                      'var'
                                      ]

        # Some Window Aggregate functions do not accept ROWS clause.
        # Maintaining all such functions here so while constructing the ROWS
        # clause, below variable can be checked and take appropriate action.
        self.__no_rows_clause_functions = {"cume_dist",
                                           "rank",
                                           "dense_rank",
                                           "percent_rank",
                                           "row_number",
                                           "lead",
                                           "lag"}

        # Some Window Aggregate functions do not accept Column as a parameter
        # for the function. So, while running window aggregate functions on
        # DataFrame, it is not required to trigger these functions on all the
        # columns in the DataFrame as result is same for all the columns.
        self.__no_column_arg_functions = {"cume_dist",
                                          "rank",
                                          "dense_rank",
                                          "percent_rank",
                                          "row_number"}

    def __repr__(self):
        """
        DESCRIPTION:
            String representation of Window Object.

        RETURNS:
            str.

        RAISES:
            None.

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = Window(object = df)
            print(window)

        """
        return "{} [partition_columns={}, order_columns={}, sort_ascending={}, nulls_first={}, " \
               "window_start_point={}, window_end_point={}, ignore_window={}]".format(self.__class__.__name__,
                                                                                      self.__partition_columns,
                                                                                      self.__order_columns,
                                                                                      self.__sort_ascending,
                                                                                      self.__nulls_first,
                                                                                      self.__window_start_point,
                                                                                      self.__window_end_point,
                                                                                      self.__ignore_window)

    def __getattr__(self, item):
        """
        DESCRIPTION:
            Magic Method to call the corresponding window function.
            Window class do not implement the exact methods but whenever any attribute
            is referred by Window Object, this function gets triggered.
            Based on the input method, corresponding expression is processed.

        PARAMETERS:
            item:
                Required Argument.
                Name of the window function.
                Types: str

        RETURNS:
            A function, which actually process the corresponding SQL window function.

        EXAMPLES:
            # Create a window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = Window(object = df)
            window.mean()
        """
        if item not in self.__aggregate_functions:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__,
                                                                            item))
        return lambda *args, **kwargs: \
            self.__process_window_aggregates(item, *args, **kwargs)

    def __process_window_aggregates(self, func_name, *args, **kwargs):
        """
        Description:
            Function to process the window expression. All window functions are actually
            processed in this function and generates a DataFrame or _SQLColumnExpression
            according to the Window class.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the window function.
                Types: str

            args:
                Optional Argument.
                Specifies the positional arguments to be passed to the window function.
                Types: Tuple

            kwargs:
                Optional Argument.
                Specifies the keyword arguments to be passed to the window function.
                Types: Dictionary

        RETURNS:
            Either a new teradataml DataFrame or an _SQLColumnExpression, according to Window class.

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = Window(object = df)
            window.__process_window_aggregates("mean")
        """

        # sqlalchemy Over clause accepts 3 parameters to frame the SQL query:
        # partition_by, order_by & rows.
        from teradataml.dataframe.sql import ColumnExpression
        window_properties = {"window_function": func_name,
                             "partition_by": [col if isinstance(col, str) else col.expression for col
                                              in UtilFuncs._as_list(self.__partition_columns)
                                              if col is not None],
                             "order_by": [col.expression if isinstance(col, ColumnExpression) else col for col
                                          in UtilFuncs._as_list(self.__generate_sqlalchemy_order_by_syntax())
                                          if col is not None],
                             "rows": (self.__window_start_point,
                                      self.__window_end_point
                                      ),
                             "is_window_aggregate": True
                             }

        # If "window_properties" do not have key "rows", then _SQLColumnExpression
        # do not construct ROWS clause. So, removing "rows" either if window to be
        # ignored or if function does not require ROWS clause.
        if self.__ignore_window or (func_name in self.__no_rows_clause_functions):
            window_properties.pop("rows")

        if self.__is_window_on_tdml_column:
            aggregate_function = getattr(self.__object, func_name)
            kwargs.update({"window_properties": window_properties})
            return aggregate_function(*args, **kwargs)
        else:
            return self.__process_dataframe_window_aggregate(func_name, *args, **kwargs)

    def __validate_window_columns(self, columns_in_window, window_arg_name):
        """
        DESCRIPTION:
            Validates, whether the columns mentioned in Window class is
            available in teradataml DataFrame or not. And if available, it
            then checks for types, which do not support sorting, in
            "partition_columns" and "order_columns".

        PARAMETERS:
            columns_in_window:
                Required Argument.
                Specifies the column names mentioned in either
                "partition_columns" or "order_columns".
                Types: str OR list of Strings (str)

            window_arg_name:
                Required Argument.
                Specifies the name of the argument which is being validated.
                Types: str

        RAISES:
            ValueError

        RETURNS:
            None

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = Window(object = df)
            window.__validate_window_columns("Feb", "partition_columns")
            window.__validate_window_columns("Feb", "order_columns")
        """
        from teradataml.common.utils import UtilFuncs
        window_columns = UtilFuncs._as_list(columns_in_window)
        if self.__is_window_on_tdml_column:
            _Validators._validate_columnexpression_dataframe_has_columns(window_columns,
                                                                         window_arg_name,
                                                                         self.__object
                                                                         )
        else:
            columns_in_expression = []
            for col in window_columns:
                if isinstance(col, str):
                    columns_in_expression.append(col)
                else:
                    columns_in_expression = columns_in_expression + col._all_columns
            _Validators._validate_dataframe_has_argument_columns(columns_in_expression,
                                                                 window_arg_name,
                                                                 self.__object,
                                                                 'teradataml'
                                                                 )

        columns = UtilFuncs._get_all_columns(self.__object,
                                             self.__is_window_on_tdml_column)

        # Validate invalid types.
        _Validators._validate_invalid_column_types(
            columns, window_arg_name, window_columns, _Dtypes._get_sort_unsupported_data_types())

    @collect_queryband(arg_name="func_name", prefix="DF_WinAgg")
    def __process_dataframe_window_aggregate(self, func_name, *args, **kwargs):
        """
        Description:
            Function processes window aggregate function on a teradataml
            DataFrame, by following below steps:
                * Same window aggregate function is executed on each supported
                  column of the teradataml DataFrame.
                * Each generated window aggregate _SQLColumnExpression is
                  passed as input to DataFrame.assign() function.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the window function.
                Types: str

            args:
                Optional Argument.
                Specifies the positional arguments to be passed to the window function.
                Types: Tuple

            kwargs:
                Optional Argument.
                Specifies the keyword arguments to be passed to the window function.
                Types: Dictionary

        RETURNS:
            teradataml DataFrame.

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = df.window()
            window.__process_dataframe_window_aggregate("mean")
        """

        new_columns = self.__get_columns_and_expressions(func_name,
                                                         *args,
                                                         **kwargs)

        # If __sort_check_required is True, then "new_columns" contains
        # the valid original columns.
        if self.__sort_check_required:
            return self.__object.assign(drop_columns=True, **new_columns)
        return self.__object.assign(**new_columns)

    def __get_columns_and_expressions(self, func_name, *args, **kwargs):
        """
        Description:
            Function to get the column name and corresponding _SQLColumnExpression,
            for a given window aggregate function. This function validates
            whether window aggregate function is valid for a column or not, and
            only if it is valid, then it returns the column name and
            _SQLColumnExpression.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the window function.
                Types: str

            args:
                Optional Argument.
                Specifies the positional arguments to be passed to the window function.
                Types: Tuple

            kwargs:
                Optional Argument.
                Specifies the keyword arguments to be passed to the window function.
                Types: Dictionary

        RETURNS:
            dict

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = df.window()
            window.__get_columns_and_expressions("mean")
        """

        # Dict to hold the columns to be projected, when partition and order
        # columns are None.
        original_columns = {}

        # Dict to hold the new window agg columns to be projected.
        new_columns = {}

        # If window is initiated on DataFrame, then every column should
        # be checked if it can participate in window aggregation. However,
        # if window is on DataFrameGroupBy object, then only grouping columns
        # should participate in window aggregation.
        columns = self.__object._metaexpr.c
        if self.__is_window_on_tdml_groupby_dataframe:
            columns = self.__object._get_groupby_columns_expression()

        column_names = []
        for column in columns:
            column_names.append(column.name)
            # By Default, window aggregates sort on "order_columns" and
            # "partition_columns". If both are not specified, window aggregates
            # sorts on all columns in DataFrame. Thus, remove columns of types
            # that does not support sorting.
            if self.__sort_check_required and type(column.type) in \
                    _Dtypes._get_sort_unsupported_data_types():
                continue
            else:
                try:
                    # Grouping columns are not dropping even though "drop_columns"
                    # set to True in DataFrame.assign(). So, skipping the column addition
                    # in such cases as adding the column results in duplicate columns
                    # in DataFrame.
                    if self.__sort_check_required and not self.__is_window_on_tdml_groupby_dataframe:
                        original_columns[column.name] = column
                    window = column.window(partition_columns=self.__partition_columns,
                                           order_columns=self.__order_columns,
                                           sort_ascending=self.__sort_ascending,
                                           nulls_first=self.__nulls_first,
                                           window_start_point=self.__window_start_point,
                                           window_end_point=self.__window_end_point,
                                           ignore_window=self.__ignore_window)

                    # For the functions which does not accept column as a parameter,
                    # do not trigger aggregate function on all columns. Triggering
                    # on one column is enough.
                    if func_name in self.__no_column_arg_functions:
                        if not new_columns:
                            sql_column_expression = getattr(window, func_name)(*args, **kwargs)
                            new_columns["{}_{}".format("col", func_name)] = sql_column_expression
                    else:
                        sql_column_expression = getattr(window, func_name)(*args, **kwargs)
                        new_columns["{}_{}".format(column.name, func_name)] = sql_column_expression
                except RuntimeError:
                    # RuntimeError being raised, if, a window aggregate function is
                    # applied on an un-supported column.
                    pass

        # Raise the error. Window aggregate does not support the columns in the
        # DataFrame.
        if not new_columns:
            raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_AGGREGATE_UNSUPPORTED,
                                                           ",".join(column_names),
                                                           func_name),
                                      MessageCodes.TDMLDF_AGGREGATE_UNSUPPORTED)
        new_columns.update(original_columns)
        return new_columns

    def __generate_sqlalchemy_order_by_syntax(self):
        """
        Description:
            Function to get the order_by clause, which can be sourced to
            sqlalchemy Over clause. sqlalchemy Over clause which accepts only
            order_by, and thus, the information about nulls_first &
            sort_ascending needs to be embedded with order_by clause.

        RETURNS:
            An Object of type sqlalchemy element.

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = df.window()
            window.__generate_sqlalchemy_order_by_syntax()
        """

        # Check if order_columns is None. If it is None, No need to consider
        # sort_ascending & nulls_first.
        if self.__order_columns is None:
            return

        from teradataml.common.utils import UtilFuncs
        from teradataml.dataframe.sql import ColumnExpression
        order_by = UtilFuncs._as_list(self.__order_columns)
        wrap_order_by = lambda sqlalc_func: [sqlalc_func(ele) if not isinstance(ele, ColumnExpression) else ele for
                                             ele in order_by]
        if not self.__sort_ascending:
            order_by = wrap_order_by(desc)

        if self.__nulls_first is None:
            return order_by

        if self.__nulls_first is True:
            order_by = wrap_order_by(nullsfirst)
        else:
            order_by = wrap_order_by(nullslast)

        return order_by

    def __dir__(self):
        """
        DESCRIPTION:
            Function returns the attributes and/or names of the methods of the
            Window object.

        RETURNS:
            list of Strings (str).

        EXAMPLES:
            # Create a window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            window = Window(object = df)
            dir(window)
        """

        # Since Window class do not implement the exact methods, lookup for
        # the available methods, do not return the Aggregate functions.
        # So Overwriting this with teradata supporting Aggregate functions.
        return [attr for attr in super(self.__class__, self).__dir__()] + \
               self.__aggregate_functions