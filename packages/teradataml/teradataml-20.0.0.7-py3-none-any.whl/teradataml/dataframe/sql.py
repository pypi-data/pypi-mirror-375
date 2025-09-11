# -*- coding: utf-8 -*-
"""

Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Mark.Sandan@teradata.com
Secondary Owner:

"""
#  This module deals with creating SQLEngine expressions
#  for tables and columns as well as sql for displaying 
#  the DataFrame. The objects in this module are internal 
#  and implement the interfaces in sql_interfaces.py
import warnings

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.constants import TeradataConstants, \
    SQLFunctionConstants, TDMLFrameworkKeywords, GeospatialConstants
from teradataml.options.configure import configure
from teradataml.options.display import display
from teradataml.utils.dtypes import _Dtypes
from teradataml.utils.validators import _Validators
from teradataml.dataframe.vantage_function_types import _get_function_expression_type
from teradatasqlalchemy.types import _TDType
from .sql_interfaces import TableExpression, ColumnExpression
from sqlalchemy.sql.elements import BinaryExpression, ClauseElement, Grouping, ClauseList
try:
    from sqlalchemy.sql.elements import ExpressionClauseList
except ImportError:
    pass
from sqlalchemy.sql.functions import GenericFunction, Function
from sqlalchemy import (Table, Column, literal, MetaData, func, or_, and_, literal_column, null)
from sqlalchemy.sql.expression import text, case as case_when
import functools
import sqlalchemy as sqlalc

import re

from teradatasqlalchemy.dialect import dialect as td_dialect, compiler as td_compiler, TeradataTypeCompiler as td_type_compiler
from teradatasqlalchemy import (INTEGER, SMALLINT, BIGINT, BYTEINT, DECIMAL, FLOAT, NUMBER)
from teradatasqlalchemy import (DATE, TIME, TIMESTAMP)
from teradatasqlalchemy import (BYTE, VARBYTE, BLOB)
from teradatasqlalchemy import (CHAR, VARCHAR, CLOB)
from teradatasqlalchemy import (INTERVAL_DAY, INTERVAL_DAY_TO_HOUR, INTERVAL_DAY_TO_MINUTE,
                                INTERVAL_DAY_TO_SECOND, INTERVAL_HOUR, INTERVAL_HOUR_TO_MINUTE,
                                INTERVAL_HOUR_TO_SECOND, INTERVAL_MINUTE, INTERVAL_MINUTE_TO_SECOND,
                                INTERVAL_MONTH, INTERVAL_SECOND, INTERVAL_YEAR,
                                INTERVAL_YEAR_TO_MONTH)
from teradatasqlalchemy import (PERIOD_DATE, PERIOD_TIME, PERIOD_TIMESTAMP)
from teradatasqlalchemy import XML, GEOMETRY
from teradataml.telemetry_utils.queryband import collect_queryband
import decimal
import datetime as dt
from teradataml.dataframe.window import Window
from teradataml.common.bulk_exposed_utils import _validate_unimplemented_function
from teradataml.common.utils import UtilFuncs


def _resolve_value_to_type(value, **kw):
    """
    DESCRIPTION:
        Internal function for coercing python literals to sqlalchemy_terdata types
        or retrieving the derived type of ColumnExpression

    PARAMETERS:
        value: a python literal type or ColumnExpression instance
        **kw: optional parameters
            len_: a length for the str type

    RETURNS:
        result: sqlalchemy TypeEngine derived type or ColumnExpression derived type

    Note:
        - Currently the supported literal types are str/float/int/decimal
          since these are being rendered already by teradatasqlalchemy

        - Mainly used in assign when passing literal values to be literal columns
    """
    length = kw.get('len_', configure.default_varchar_size)

    type_map = {
        str: VARCHAR(length, charset = 'UNICODE'),
        bytes: VARBYTE(length),
        int: INTEGER(),
        float: FLOAT(),
        bool: BYTEINT(),
        decimal.Decimal: DECIMAL(38,37),
        dt.date: DATE(),
        dt.datetime: TIMESTAMP(),
        dt.time: TIME()
    }

    result = type_map.get(type(value))

    if isinstance(value, ColumnExpression):
        result = value.type
    return result

def _handle_sql_error(f):
    """
    DESCRIPTION:
        This decorator wraps python special methods that generate SQL for error handling.
        Any error messages or error codes involving sql generating methods
        can be considered here.

    PARAMETERS:
        A function or method that generates sql

    EXAMPLES:
        @_handle_sql_error
        def __and__(self, other)
    """
    @functools.wraps(f)
    def binary(*args, **kw):

        self_ = None
        other_ = None

        if len(args) == 2:
            self_, other_ = args

        # Used to determine whether multiple dataframes are given in _SQLColumnExpression.
        multiple_dataframes = False

        try:
            if self_ is not None and other_ is not None and\
                isinstance(self_, ColumnExpression) and\
                isinstance(other_, ColumnExpression) and\
                self_.table is not None and other_.table is not None:

                # If table names or schema names are different or has_multiple_dataframes flag
                # is True for any of the two _SQLColumnExpressions.
                if self_.table.name != other_.table.name or\
                    self_.table.schema != other_.table.schema or\
                    self_.get_flag_has_multiple_dataframes() == True or\
                    other_.get_flag_has_multiple_dataframes() == True:

                    multiple_dataframes = True

            # If _SQLColumnExpressions have NULL tables (ie at later levels of a multi level
            # expression).
            elif isinstance(self_, ColumnExpression) and\
                isinstance(other_, ColumnExpression) and\
                self_.table is None and other_.table is None:

                multiple_dataframes = self_.get_flag_has_multiple_dataframes() | \
                                      other_.get_flag_has_multiple_dataframes()

            res = f(*args, **kw)
            # Assign True or False to resultant _SQLColumnExpression based on previous two
            # _SQLColumnExpressions.
            res.set_flag_has_multiple_dataframes(multiple_dataframes)
            res.original_column_expr = [self_, other_]

        except Exception as err:
            errcode = MessageCodes.TDMLDF_INFO_ERROR
            msg = Messages.get_message(errcode)
            raise TeradataMlException(msg, errcode) from err

        return res

    return binary

class _MetaExpression(object):
    """
    The _MetaExpression contains the TableExpression and provides the DataFrame with metadata
    from the underlying Table as well as methods for translating and generating SQL.

    The main responsibility of this class is to translate sql expressions internally in DataFrame.
    Other responsibilities are delegated to the underlying TableExpression.

    This class is internal.
    """

    def __init__(self, table, **kw):
        """
        PARAMETERS:
            table: the table to use for TableExpression

            kw: kwargs for implementation specific TableExpressions/ColumnExpressions
              - dialect: an implementation of a SQLAlchemy Dialect
        """

        self._dialect = kw.get('dialect', td_dialect())
        self.__t = _SQLTableExpression(table, **kw)
        self._is_persist = kw.get("is_persist", False)

    def __getattr__(self, key):
        """
        DESCRIPTION:
            Retrieve an attribute from _MetaExpression or the underlying TableExpression

        PARAMETERS:
            key: attribute name

        RAISES:
            AttributeError if attribute can't be found
        """
        try:
            res = getattr(self.__t, key)
        except AttributeError:
            raise AttributeError('Unable to find attribute: %s' % key)
        return res

    @property
    def _n_rows(self):
        return self.__t._n_rows

    @_n_rows.setter
    def _n_rows(self, value):
        """Use n number of rows for print() instead of display.max_rows for this metaexpr. If 0, display.max_rows is used"""
        if not isinstance(value, int) or value <= 0:
            raise ValueError('n_rows must be a positive int.')

        self.__t._n_rows = value

    def __repr__(self):
      return repr(self.__t)

    def _get_table_expr(self):
        return self.__t


class _PandasTableExpression(TableExpression):

    def _assign(self, drop_columns, **kw):
        """
        DESCRIPTION:
            Internal method for DataFrame.assign
            Generates the new select list ColumnExpressions and
            provides an updated _SQLTableExpression for the new _MetaExpression

        PARAMETERS:
            drop_columns (optional):  bool If True, drop columns that are not specified in assign. The default is False.
            kw: keyword, value pairs
                    - keywords are the column names.
                    - values can be column arithmetic expressions and int/float/string literals.

        RAISES:
            ValueError when a value that is callable is given in kwargs


        See Also
        --------
            DataFrame.assign


        Returns
        -------
        result : -Updated _SQLTableExpression
                 -list of compiled ColumnExpressions

        Note: This method assumes that the values in each key of kw
              are valid types (supported python literals or ColumnExpressions)
        """
        compiler = td_compiler(td_dialect(), None)
        current = {c.name for c in self.c}

        assigned_expressions = []

        existing = [(c.name, c) for c in self.c]
        new = [(label, expression) for label, expression in kw.items() if label not in current]
        new = sorted(new, key=lambda x: x[0])

        for alias, expression in existing + new:
            if drop_columns and alias not in kw:
                continue

            else:
                expression = kw.get(alias, expression)
                if isinstance(expression, ClauseElement):
                    expression = _SQLColumnExpression(expression)

                type_ = _resolve_value_to_type(expression)

                if not isinstance(expression, ColumnExpression):
                    # wrap literals. See DataFrame.assign for valid literal values
                    if expression == None:
                        expression = _SQLColumnExpression(null())
                    else:
                        expression = _SQLColumnExpression(literal(expression,
                                                                  type_=type_))

                aliased_expression = compiler.visit_label(expression.expression.label(alias),
                                                        within_columns_clause=True,
                                                        include_table = False,
                                                        literal_binds = True)
                assigned_expressions += [(alias, aliased_expression, type_)]

        if len(assigned_expressions) >= TeradataConstants['TABLE_COLUMN_LIMIT'].value:
            raise ValueError('Maximum column limit reached')

        cols = (Column(name, type_) for name, expression, type_ in assigned_expressions)
        t = Table(self.name, MetaData(), *cols)

        return (_SQLTableExpression(t), assigned_expressions)


    def _filter(self, axis, op, index_labels, **kw):
        """
        DESCRIPTION:
            Subset rows or columns of dataframe according to labels in the specified index.

        PARAMETERS:
            axis: int
                1 for columns to filter
                0 for rows to filter

            op: string
                A string representing the way to index.
                This parameter is used along with axis to get the correct expression.

            index_labels: list or iterable of string
                contains column names/labels of the DataFrame

            **kw: keyword arguments
                items: None or a list of strings
                like: None or a string representing a substring
                regex: None or a string representing a regex pattern

                optional keywords:
                match_args: string of characters to use for REGEXP_SUBSTR

        RETURNS:
            tuple of two elements:
                Either a tuple of (list of str, 'select') if axis == 1
                Or a tuple of (list of ColumnExpressions, 'where') if axis == 0

        Note:
            Implementation outline:

            axis == 1 (column based filter)

                items - [colname for colname in colnames if colname in items]
                like - [colname for colname in colnames if like in colname]
                regex - [colname for colname in colnames if re.search(regex, colname) is not None]

            axis == 0 (row value based filter on index)

                items - WHERE index IN ( . . . )
                like -  same as regex except the string (kw['like']) is a substring pattern
                regex - WHERE REGEXP_SUBSTR(index, regex, 1, 1, 'c')


        EXAMPLES:

            # self is a reference to DataFrame's _metaexpr.
            # This method is usually called from the DataFrame.
            # Suppose the DataFrame has columns ['a', 'b', 'c'] in its index:

            # select columns given in items list
            self._filter(1, 'items', ['a', 'b', 'c'], items = ['a', 'b'])

            # select columns matching like pattern (index_labels is ignored)
            self._filter(1, 'like', ['a', 'b', 'c'], like = 'substr')

            # select columns matching regex pattern (index_labels is ignored)
            self._filter(1, 'regex', ['a', 'b', 'c'], regex = '[0|1]')

            # select rows where index column(s) are in items list
            self._filter(0, 'items', ['a', 'b', 'c'], items = [('a', 'b', 'c')])

            # select rows where index column(s) match the like substring
            self._filter(0, 'like', ['a', 'b', 'c'], like = 'substr')

            # select rows where index column(s) match the regex pattern
            self._filter(0, 'regex', ['a', 'b', 'c'], regex = '[0|1]')
        """

        impls = dict({

            ('like', 1):  lambda col: kw['like'] in col.name,

            ('regex', 1): lambda col: re.search(kw['regex'], col.name) is not None,

            ('items', 0): lambda colexp, lst: colexp.in_(lst),

            ('like', 0):  lambda colexp: func.regexp_substr(colexp, kw['like'], 1, 1,
                                                            kw.get('match_arg', 'c')) != None,

            ('regex', 0): lambda colexp: func.regexp_substr(colexp, kw['regex'], 1, 1,
                                                            kw.get('match_arg', 'c')) != None
        }
        )

        filtered_expressions = []
        filter_ = impls.get((op, axis))
        is_char_like = lambda x: isinstance(x, CHAR) or\
                                 isinstance(x, VARCHAR) or\
                                 isinstance(x, CLOB)
        if axis == 1:

            # apply filtering to columns and then select()
            if op == 'items':
                for col in kw['items']:
                    filtered_expressions += [col]

            else:
                for col in self.c:
                    if filter_(col):
                        filtered_expressions += [col.name]

        else:
            # filter based on index values
            # apply filtering to get appropriate ColumnExpression then __getitem__()

            if op == 'items':

                if len(index_labels) == 1:

                    # single index case
                    for c in self.c:
                        if c.name in index_labels:

                            expression = c.expression
                            filtered_expressions += [filter_(expression, kw['items'])]

                else:

                    # multi index case
                    items_by_position = zip(*kw['items'])

                    # traverse in the order given by index_label
                    for index_col, item in zip(index_labels, items_by_position):
                        for c in self.c:
                            if c.name == index_col:
                                expression = c.expression
                                filtered_expressions += [filter_(expression, item)]

            else:

                var_size = kw.get('varchar_size', configure.default_varchar_size)
                for c in self.c:
                    if c.name in index_labels:

                        expression = c.expression
                        if not is_char_like(expression.type):
                            # need to cast to char-like operand for REGEXP_SUBSTR
                            expression = expression.cast(type_ = VARCHAR(var_size))

                        filtered_expressions += [filter_(expression)]

            if axis == 0:

                if op == 'items' and len(index_labels) > 1:

                    # multi index item case is a conjunction
                    filtered_expressions = _SQLColumnExpression(and_(*filtered_expressions))

                else:
                    filtered_expressions = _SQLColumnExpression(or_(*filtered_expressions))

        return filtered_expressions


class _SQLTableExpression(_PandasTableExpression):
    """
        This class implements TableExpression and is contained
        in the _MetaExpressions class

        It handles:
            - SQL generation for the table or all it's columns
            - DataFrame metadata access using a sqlalchemy.Table

      This class is internal.
    """
    def __init__(self, table, **kw):

        """
        DESCRIPTION:
            Initialize the _SQLTableExpression

        PARAMETERS:
            table : A sqlalchemy.Table
            kw**: a dict of optional parameters
                - column_order: a collection of string column names
                                in the table to be ordered in the c attribute
        """

        self.t = table
        if 'column_order' in kw:
            # Use DataFrame.columns to order the columns in the metaexpression
            columns = []
            for c in kw['column_order']:
                name = c.strip()
                # Get case-insensitive column names from Table object.
                col = table.c.get(name, table.c.get(name.lower(), table.c.get(name.upper())))

                if col is None:
                    raise ValueError('Reflected column names do not match those in DataFrame.columns')

                columns.append(_SQLColumnExpression(col))
            self.c = columns

        else:
            self.c = [_SQLColumnExpression(c) for c in table.c]

        self._n_rows = 0
        self._datalake = kw.get('datalake', None)

    @property
    def c(self):
        """
        Returns the underlying collection of _SQLColumnExpressions
        """
        return self.__c

    @c.setter
    def c(self, collection):
        """
        Set the underlying map of _SQLColumnExpressions

        PARAMETERS:
            collection: a dict of _SQLColumnExpressions

        """
        is_sql_colexpression = lambda x: isinstance(x, _SQLColumnExpression)
        valid_collection = isinstance(collection, list) and\
                         len(collection) > 0 and\
                         all(map(is_sql_colexpression, collection))

        if (not valid_collection):
            raise ValueError("collection must be a non empty list of _SQLColumnExpression instances. Got {}".format(collection))


        self.__c = collection

    @property
    def name(self):
        """
        Returns the name of the underlying SQLAlchemy Table
        """
        return self.t.name

    @property
    def t(self):
        """
        Returns the underlying SQLAlchemy Table
        """
        return self.__t

    @t.setter
    def t(self, table):
        """
        Set the underlying SQLAlchemy Table

        PARAMETERS:
            table : A sqlalchemy.Table
        """
        if (not isinstance(table, Table)):
            raise ValueError("table must be a sqlalchemy.Table")

        self.__t = table

    @property
    def datalake(self):
        """
        Returns the underlying datalake information
        """
        return self._datalake

    def __repr__(self):
        """
        Returns a SELECT TOP string representing the underlying table.
        For representation purposes:
            - the columns are cast into VARCHAR
            - certain numeric columns are first rounded
            - character-like columns are unmodified
            - byte-like columns are called with from_bytes to show them as ASCII


        Notes:
            - The top integer is taken from teradataml.options
            - The rounding value for numeric types is taken from teradataml.options
            - from_bytes is called on byte-like columns to represent them as ASCII encodings
              See from_bytes for more info on different encodings supported:
              Teradata® Database SQL Functions, Operators, Expressions, and Predicates, Release 16.20

        """
        # TODO: refactor this to be in the ColumnExpression instances
        single_quote = literal_column("''''")
        from_bytes = lambda c: ('b' + single_quote + func.from_bytes(c, display.byte_encoding) + single_quote).label(c.name)
        display_decimal = lambda c: func.round(c, display.precision).cast(type_ = DECIMAL(38, display.precision)).label(c.name)
        display_number = lambda c: func.round(c, display.precision).label(c.name)

        # By default for BLOB data, display only first 10 characters following 3 dot characters.
        # If display option "blob_length" is set to None, then display all the data in the BLOB column.
        blob_substr = lambda c: func.substr(c, 0, display.blob_length)
        dots = "..."
        if display.blob_length is None:
            blob_substr = lambda c: func.substr(c, 0)
            dots = ""
        blob_expression = lambda c: func.from_bytes(blob_substr(c), display.byte_encoding) + dots
        display_blob = lambda c: ('b' + single_quote + blob_expression(c) + single_quote).label(c.name)

        compiler = td_compiler(td_dialect(), None)
        cast_expr = lambda c, var_size: c.cast(type_ = VARCHAR(var_size)).label(c.name)

        max_rows = display.max_rows
        if self._n_rows > 0:
            max_rows = self._n_rows

        res = 'select top {} '.format(max_rows)
        expressions = []
        interval_types= _Dtypes._get_interval_data_types()
        datetime_period_types = _Dtypes._get_datetime_period_data_types()

        for c in self.c:
            if isinstance(c.type, (CHAR, VARCHAR, CLOB, FLOAT, INTEGER, SMALLINT,
                                   BIGINT, BYTEINT, XML)):
                expression = c.expression.label(c.name)
            elif isinstance(c.type, (BYTE, VARBYTE)):
                expression = from_bytes(c.expression)
            elif isinstance(c.type, BLOB):
                expression = display_blob(c.expression)
            elif isinstance(c.type, DECIMAL):
                expression = display_decimal(c.expression)
            elif isinstance(c.type, NUMBER):
                expression = display_number(c.expression)
            elif isinstance(c.type, tuple(datetime_period_types)):
                expression = cast_expr(c.expression, 30)
            # Change the size as INTERVAL_DAY_TO_SECOND(4, 6) is failing.
            elif isinstance(c.type, tuple(interval_types)):
                expression = cast_expr(c.expression, 25)
            elif isinstance(c.type, GEOMETRY):
                expression = cast_expr(c.expression, display.geometry_column_length) if \
                    display.geometry_column_length is not None else c.expression.label(c.name)
            else:
                expression = cast_expr(c.expression,
                                       configure.default_varchar_size)

            expressions.append(compiler.visit_label(expression,
                                                within_columns_clause=True,
                                                include_table = False,
                                                literal_binds = True))

        return res + ', '.join(expressions)

class _LogicalColumnExpression(ColumnExpression):

    """
        The _LogicalColumnExpression implements the logical special methods
        for _SQLColumnExpression.
    """
    def __get_other_expr(self, other):
        """
        Internal function to get the SQL expression of the object.

        PARAMETERS:
            other:
                Required Argument.
                Specifies a python literal, ColumnExpression or GeometryType.
                Types: bool, float, int, str, ColumnExpression, GeometryType

        RETURNS:
            Expression as string

        RAISES:
            None

        EXAMPLES:
            expr = self.__get_other_expr(other)
        """
        from teradataml.geospatial.geometry_types import GeometryType
        from sqlalchemy import text
        if isinstance(other, _SQLColumnExpression):
            expr = other.expression
        elif isinstance(other, GeometryType):
            expr = text(other._vantage_str_())
        else:
            expr = other

        return expr

    def __coerce_to_text(self, other):
        """
        Internal function to coerce to text, using SQLAlchemy text(), a string literal passed as an argument.

        PARAMETERS:
            other: A python literal or another ColumnExpression.

        RETURNS:
            Python literal coerced to text if the input is a string literal, else the input argument itself.
        """
        if isinstance(other, str):
            return text(other)
        return other

    @_handle_sql_error
    def __and__(self, other):
        """
        Compute the logical AND between two ColumnExpressions using &.
        The logical AND operator is an operator that performs a logical
        conjunction on two statements.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students who got the admission (i.e., admitted = 1)
            #            and has GPA greater than 3.5.
            >>> df[(df.gpa > 3.5) & (df.admitted == 1)]
               masters   gpa     stats programming  admitted
            id
            21      no  3.87    Novice    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            3       no  3.70    Novice    Beginner         1
            20     yes  3.90  Advanced    Advanced         1
            37      no  3.52    Novice      Novice         1
            35      no  3.68    Novice    Beginner         1
            12      no  3.65    Novice      Novice         1
            18     yes  3.81  Advanced    Advanced         1
            17      no  3.83  Advanced    Advanced         1
            23     yes  3.59  Advanced      Novice         1


        """
        other = self.__coerce_to_text(other)
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression & expr)
        return res

    @_handle_sql_error
    def __rand__(self, other):
        """
        Compute the reverse of logical AND between two ColumnExpressions using &.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students who got the admission (i.e., admitted = 1)
            #            and has GPA greater than 3.5.
            >>> df[(df.gpa > 3.5) & (df.admitted == 1)]
               masters   gpa     stats programming  admitted
            id
            21      no  3.87    Novice    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            3       no  3.70    Novice    Beginner         1
            20     yes  3.90  Advanced    Advanced         1
            37      no  3.52    Novice      Novice         1
            35      no  3.68    Novice    Beginner         1
            12      no  3.65    Novice      Novice         1
            18     yes  3.81  Advanced    Advanced         1
            17      no  3.83  Advanced    Advanced         1
            23     yes  3.59  Advanced      Novice         1
        """
        return self & other

    @_handle_sql_error
    def __or__(self, other):
        """
        Compute the logical OR between two ColumnExpressions using |.
        The logical OR operator is an operator that performs a
        inclusive disjunction on two statements.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa greater than
            #            3.5 or 'Advanced' programming skills.
            >>> df[(df.gpa > 3.5) | (df.programming == "Advanced")]
               masters   gpa     stats programming  admitted
            id
            30     yes  3.79  Advanced      Novice         0
            40     yes  3.95    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            37      no  3.52    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            20     yes  3.90  Advanced    Advanced         1
            35      no  3.68    Novice    Beginner         1
            14     yes  3.45  Advanced    Advanced         0
        """
        other = self.__coerce_to_text(other)
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression | expr)
        return res

    @_handle_sql_error
    def __ror__(self, other):
        """
        Compute the reverse of logical OR between two ColumnExpressions using |.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa greater than
            #            3.5 or 'Advanced' programming skills.
            >>> df[(df.gpa > 3.5) | (df.programming == "Advanced")]
               masters   gpa     stats programming  admitted
            id
            30     yes  3.79  Advanced      Novice         0
            40     yes  3.95    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            37      no  3.52    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            20     yes  3.90  Advanced    Advanced         1
            35      no  3.68    Novice    Beginner         1
            14     yes  3.45  Advanced    Advanced         0
        """
        return self | other

    @_handle_sql_error
    def __invert__(self):
        """
        Compute the logical NOT of ColumnExpression using ~.

        PARAMETERS:
            None

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get the negation of gpa not equal to 3.44 or
            #            admitted equal to 1.
            >>> df[~((df.gpa != 3.44) | (df.admitted == 1))]
                         id masters   gpa   stats  admitted
            programming
            Novice        5      no  3.44  Novice         0
        """
        return _SQLColumnExpression(~self.expression)

    @_handle_sql_error
    def __gt__(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values greater than the other or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all the students with gpa greater than 3.
            >>> df[df.gpa > 3]
               masters   gpa     stats programming  admitted
            id
            14     yes  3.45  Advanced    Advanced         0
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            3       no  3.70    Novice    Beginner         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            37      no  3.52    Novice      Novice         1
            1      yes  3.95  Beginner    Beginner         0
            31     yes  3.50  Advanced    Beginner         1

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure greater than 400 and investment
            #            greater than 170.
            >>> df[(df.expenditure > 400) & (df.investment > 170)]
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        expr = self.__get_other_expr(other)
        res = _SQLColumnExpression(self.expression > expr)
        return res

    @_handle_sql_error
    def __lt__(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values less than the other or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa less than 3.
            >>> df[df.gpa < 3]
               masters   gpa     stats programming  admitted
            id
            24      no  1.87  Advanced      Novice         1
            19     yes  1.98  Advanced    Advanced         0
            38     yes  2.65  Advanced    Beginner         1
            7      yes  2.33    Novice      Novice         1

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure less than 440 and
            #            income greater than 180.
            >>> df[(df.expenditure < 440) & (df.income > 180)]
               start_time_column end_time_column  expenditure  income  investment
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0
        """
        expr = self.__get_other_expr(other)
        res = _SQLColumnExpression(self.expression < expr)
        return res

    @_handle_sql_error
    def __ge__(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values greater than or equal to the other or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa greater than
            #            or equal to 3.
            >>> df[df.gpa >= 3]
               masters   gpa     stats programming  admitted
            id
            30     yes  3.79  Advanced      Novice         0
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            37      no  3.52    Novice      Novice         1
            14     yes  3.45  Advanced    Advanced         0

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure greater than or equal to 450 and
            #            investment is greater than or equal to 200.
            >>> df[(df.expenditure >= 450) & (df.investment >= 200)]
               start_time_column end_time_column  expenditure  income  investment
            id
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        expr = self.__get_other_expr(other)
        res = _SQLColumnExpression(self.expression >= expr)
        return res

    @_handle_sql_error
    def __le__(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values less than or equal to the other or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa less than or
            #            equal to 3.
            >>> df[df.gpa <= 3]
               masters   gpa     stats programming  admitted
            id
            24      no  1.87  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            19     yes  1.98  Advanced    Advanced         0
            38     yes  2.65  Advanced    Beginner         1
            7      yes  2.33    Novice      Novice         1

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure less than or equal to
            #            500 and income less than or equal to 480.
            >>> df[(df.expenditure <= 500) & (df.income <= 480)]
               start_time_column end_time_column  expenditure  income  investment
            id
            2           67/06/30        07/07/10        421.0   465.0       179.0
            1           67/06/30        07/07/10        415.0   451.0       180.0
        """
        expr = self.__get_other_expr(other)
        res = _SQLColumnExpression(self.expression <= expr)
        return res

    @_handle_sql_error
    def __xor__(self, other):
        """
        Compute the logical XOR between two ColumnExpressions using ^.
        The logical XOR operator is an operator that performs a
        exclusive disjunction on two statements.

        PARAMETERS:
            other:
                Required Argument.
                Specifies another ColumnExpression.
                Types: ColumnExpression

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa is greater
            #            than 3.5 or programming skills are 'Advanced'.
            >>> df[(df.gpa > 3.5) ^ (df.programming == "Advanced")]
               masters   gpa     stats programming  admitted
            id
            14     yes  3.45  Advanced    Advanced         0
            40     yes  3.95    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            37      no  3.52    Novice      Novice         1
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            2      yes  3.76  Beginner    Beginner         0
            35      no  3.68    Novice    Beginner         1
            29     yes  4.00    Novice    Beginner         0
            30     yes  3.79  Advanced      Novice         0
        """
        other = self.__coerce_to_text(other)
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression((self.expression | expr) & ~(self.expression & expr))
        return res

    @_handle_sql_error
    def __rxor__(self, other):
        """
        Compute the reverse of logical XOR between two ColumnExpressions using ^.

        PARAMETERS:
            other:
                Required Argument.
                Specifies another ColumnExpression.
                Types: ColumnExpression

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa greater than
            #            3.5 or programming skills are 'Advanced'.
            >>> df[(df.gpa > 3.5) ^ (df.programming == "Advanced")]
               masters   gpa     stats programming  admitted
            id
            14     yes  3.45  Advanced    Advanced         0
            40     yes  3.95    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            37      no  3.52    Novice      Novice         1
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            2      yes  3.76  Beginner    Beginner         0
            35      no  3.68    Novice    Beginner         1
            29     yes  4.00    Novice    Beginner         0
            30     yes  3.79  Advanced      Novice         0
        """
        return self ^ other

    @_handle_sql_error
    def __eq__(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values equal to the other.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa equal to 3.44.
            >>> df[df.gpa == 3.44]
               masters   gpa   stats programming  admitted
            id
            5       no  3.44  Novice      Novice         0

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure equal to 415 or income equal to 509.
            >>> df[(df.expenditure == 415) | (df.income == 509)]
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        expr = self.__get_other_expr(other)
        res = _SQLColumnExpression(self.expression == expr)
        return res

    @_handle_sql_error
    def __ne__(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values not equal to the other.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            24      no  1.87  Advanced      Novice         1
            39     yes  3.75  Advanced    Beginner         0
            30     yes  3.79  Advanced      Novice         0

            # Example 1: Get all students with gpa not equal to 3.44.
            >>> df[df.gpa != 3.44]
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            24      no  1.87  Advanced      Novice         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            3       no  3.70    Novice    Beginner         1
            30     yes  3.79  Advanced      Novice         0

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure not equal to 415 or income
            #            not equal to 400.
            >>> df[(df.expenditure != 415) | (df.income != 400)]
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        expr = self.__get_other_expr(other)
        res = _SQLColumnExpression(self.expression != expr)
        return res


class _ArithmeticColumnExpression(ColumnExpression):

    """
        The _ArithmeticColumnExpression implements the arithmetic special methods
        for _SQLColumnExpression.
    """

    @_handle_sql_error
    def __add__(self, other):
        """
        Compute the sum between two ColumnExpressions using +.
        This is also the concatenation operator for string-like columns.

        PARAMETERS:
            other :
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Add 100 to the expenditure amount and assign the final amount
            #            to new column 'total_expenditure'.
            >>> df.assign(total_expenditure=df.expenditure + 100)
               start_time_column end_time_column  expenditure  income  investment  total_expenditure
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0              534.0
            2           67/06/30        07/07/10        421.0   465.0       179.0              521.0
            1           67/06/30        07/07/10        415.0   451.0       180.0              515.0
            5           67/06/30        07/07/10        459.0   509.0       211.0              559.0
            4           67/06/30        07/07/10        448.0   493.0       192.0              548.0

            # Example 2: Add expenditure amount to the investment amount and assign the
            #            final amount to new column 'total_investmet'.
            >>> df.assign(total_investmet=df.expenditure + df.investment)
               start_time_column end_time_column  expenditure  income  investment  total_investmet
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0                        619.0
            2           67/06/30        07/07/10        421.0   465.0       179.0                        600.0
            1           67/06/30        07/07/10        415.0   451.0       180.0                        595.0
            5           67/06/30        07/07/10        459.0   509.0       211.0                        670.0
            4           67/06/30        07/07/10        448.0   493.0       192.0                        640.0
        """
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression + expr)
        return res

    @_handle_sql_error
    def __radd__(self, other):
        """
        Compute the rhs sum between two ColumnExpressions using +

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Add 100 to the expenditure amount and assign the final amount
            #            to new column 'total_expenditure'.
            >>> df.assign(total_expenditure=df.expenditure + 100)
               start_time_column end_time_column  expenditure  income  investment  total_expenditure
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0              534.0
            2           67/06/30        07/07/10        421.0   465.0       179.0              521.0
            1           67/06/30        07/07/10        415.0   451.0       180.0              515.0
            5           67/06/30        07/07/10        459.0   509.0       211.0              559.0
            4           67/06/30        07/07/10        448.0   493.0       192.0              548.0

            # Example 2: Add expenditure amount to the investment amount and assign the
            #            final amount to new column 'total_investmet'.
            >>> df.assign(total_investmet=df.expenditure + df.investment)
               start_time_column end_time_column  expenditure  income  investment  total_investmet
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0                        619.0
            2           67/06/30        07/07/10        421.0   465.0       179.0                        600.0
            1           67/06/30        07/07/10        415.0   451.0       180.0                        595.0
            5           67/06/30        07/07/10        459.0   509.0       211.0                        670.0
            4           67/06/30        07/07/10        448.0   493.0       192.0                        640.0
        """
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(expr + self.expression)
        return res

    @_handle_sql_error
    def __sub__(self, other):
        """
        Compute the difference between two ColumnExpressions using -
        Note:
            * Difference between two timestamp columns return value in seconds.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
            >>> load_example_data("uaf", "Convolve2RealsLeft")
            >>> timestamp_df = DataFrame("Convolve2RealsLeft")
            >>> timestamp_df
                row_seq                  row_i_time  col_seq               column_i_time    A     B     C     D
            id
            1         1  2018-08-08 08:02:00.000000        0  2018-08-08 08:00:00.000000  1.3  10.3  20.3  30.3
            1         1  2018-08-08 08:02:00.000000        1  2018-08-08 08:02:00.000000  1.4  10.4  20.4  30.4
            1         0  2018-08-08 08:00:00.000000        1  2018-08-08 08:02:00.000000  1.2  10.2  20.2  30.2
            1         0  2018-08-08 08:00:00.000000        0  2018-08-08 08:00:00.000000  1.1  10.1  20.1  30.1

            # Example 1: Subtract 100 from the income amount and assign the final amount
            #            to new column 'remaining_income'.
            >>> df.assign(remaining_income=df.income - 100)
               start_time_column end_time_column  expenditure  income  investment  remaining_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0             385.0
            2           67/06/30        07/07/10        421.0   465.0       179.0             365.0
            1           67/06/30        07/07/10        415.0   451.0       180.0             351.0
            5           67/06/30        07/07/10        459.0   509.0       211.0             409.0
            4           67/06/30        07/07/10        448.0   493.0       192.0             393.0

            # Example 2: Subtract investment amount from the income amount and assign the
            #            final amount to new column 'remaining_income'.
            >>> df.assign(remaining_income=df.income - df.investment)
               start_time_column end_time_column  expenditure  income  investment  remaining_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0             300.0
            2           67/06/30        07/07/10        421.0   465.0       179.0             286.0
            1           67/06/30        07/07/10        415.0   451.0       180.0             271.0
            5           67/06/30        07/07/10        459.0   509.0       211.0             298.0
            4           67/06/30        07/07/10        448.0   493.0       192.0             301.0

            # Example 3: Subtract 2 timestamp columns and assign to new column 'seconds'.
            >>> timestamp_df.assign(seconds = timestamp_df.row_i_time-timestamp_df.column_i_time)
                row_seq                  row_i_time  col_seq               column_i_time    A     B     C     D  seconds
            id
            1         1  2018-08-08 08:02:00.000000        0  2018-08-08 08:00:00.000000  1.3  10.3  20.3  30.3    120.0
            1         1  2018-08-08 08:02:00.000000        1  2018-08-08 08:02:00.000000  1.4  10.4  20.4  30.4      0.0
            1         0  2018-08-08 08:00:00.000000        1  2018-08-08 08:02:00.000000  1.2  10.2  20.2  30.2   -120.0
            1         0  2018-08-08 08:00:00.000000        0  2018-08-08 08:00:00.000000  1.1  10.1  20.1  30.1      0.0

        """
        if isinstance(self._type, TIMESTAMP) and isinstance(other._type, TIMESTAMP):
            s = """
                (CAST((CAST({0} AS DATE)-CAST({1} AS DATE)) AS FLOAT) * 86400) +
                ((EXTRACT(HOUR FROM {0}) - EXTRACT(HOUR FROM {1})) * 3600) +
                ((EXTRACT(MINUTE FROM {0}) - EXTRACT(MINUTE FROM {1})) * 60) +
                ((EXTRACT(SECOND FROM {0}) - EXTRACT(SECOND FROM {1})))
                """.format(self.compile(), other.compile())
            return _SQLColumnExpression(literal_column(s, type_ = FLOAT))

        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression - expr)
        return res

    @_handle_sql_error
    def __rsub__(self, other):
        """
        Compute the difference between two ColumnExpressions using -.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Subtract 100 from the income amount and assign the final amount
            #            to new column 'remaining_income'.
            >>> df.assign(remaining_income=df.income - 100)
               start_time_column end_time_column  expenditure  income  investment  remaining_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0             385.0
            2           67/06/30        07/07/10        421.0   465.0       179.0             365.0
            1           67/06/30        07/07/10        415.0   451.0       180.0             351.0
            5           67/06/30        07/07/10        459.0   509.0       211.0             409.0
            4           67/06/30        07/07/10        448.0   493.0       192.0             393.0

            # Example 2: Subtract investment amount from the income amount and assign the
            #            final amount to new column 'remaining_income'.
            >>> df.assign(remaining_income=df.income - df.investment)
               start_time_column end_time_column  expenditure  income  investment  remaining_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0             300.0
            2           67/06/30        07/07/10        421.0   465.0       179.0             286.0
            1           67/06/30        07/07/10        415.0   451.0       180.0             271.0
            5           67/06/30        07/07/10        459.0   509.0       211.0             298.0
            4           67/06/30        07/07/10        448.0   493.0       192.0             301.0
        """
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(expr - self.expression)
        return res

    @_handle_sql_error
    def __mul__(self, other):
        """
        Compute the product between two ColumnExpressions using *.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Increase the income for each id by 10 % and assign increased
            #            income to new column 'increased_income'.
            >>> df.assign(increased_income=df.income + df.income * 0.1)
               start_time_column end_time_column  expenditure  income  investment  increased_income
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0             496.1
            4           67/06/30        07/07/10        448.0   493.0       192.0             542.3
            2           67/06/30        07/07/10        421.0   465.0       179.0             511.5
            3           67/06/30        07/07/10        434.0   485.0       185.0             533.5
            5           67/06/30        07/07/10        459.0   509.0       211.0             559.9

            # Example 2: Filter out the rows after increasing the income by 10% is greater than 500.
            >>> df[(df.income + df.income * 0.1) > 500]
               start_time_column end_time_column  expenditure  income  investment
            id
            2           67/06/30        07/07/10        421.0   465.0       179.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression * expr)
        return res

    @_handle_sql_error
    def __rmul__(self, other):
        """
        Compute the product between two ColumnExpressions using *.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            # Example 1: Double the income and assign increased
            #            income to new column 'double_income'.
             >>> df.assign(double_income=df.income * 2)
               start_time_column end_time_column  expenditure  income  investment  double_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0          970.0
            2           67/06/30        07/07/10        421.0   465.0       179.0          930.0
            1           67/06/30        07/07/10        415.0   451.0       180.0          902.0
            5           67/06/30        07/07/10        459.0   509.0       211.0         1018.0
            4           67/06/30        07/07/10        448.0   493.0       192.0          986.0

            # Example 2: Filter out the rows after increasing the income by 10% is greater than 500.
            >>> df[(df.income + df.income * 0.1) > 500]
               start_time_column end_time_column  expenditure  income  investment
            id
            2           67/06/30        07/07/10        421.0   465.0       179.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        return self * other

    @_handle_sql_error
    def __truediv__(self, other):
        """
        Compute the division between two ColumnExpressions using /.

        PARAMETERS:
            other :
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

           # Example 1: Divide the income by 2 and assign the final amount to new column 'half_income'.
            >>> df.assign(half_income=df.income / 2)
               start_time_column end_time_column  expenditure  income  investment  half_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0        242.5
            2           67/06/30        07/07/10        421.0   465.0       179.0        232.5
            1           67/06/30        07/07/10        415.0   451.0       180.0        225.5
            5           67/06/30        07/07/10        459.0   509.0       211.0        254.5
            4           67/06/30        07/07/10        448.0   493.0       192.0        246.5

            # Example 2: Calculate the percent of investment of income and assign the
            #            final amount to new column 'percent_inverstment_'.
            >>> df.assign(percent_inverstment_=df.investment * 100 / df.income)
               start_time_column end_time_column  expenditure  income  investment  percent_inverstment_
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0             38.144330
            2           67/06/30        07/07/10        421.0   465.0       179.0             38.494624
            1           67/06/30        07/07/10        415.0   451.0       180.0             39.911308
            5           67/06/30        07/07/10        459.0   509.0       211.0             41.453831
            4           67/06/30        07/07/10        448.0   493.0       192.0             38.945233
        """

        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression / expr)
        return res

    @_handle_sql_error
    def __rtruediv__(self, other):
        """
        Compute the division between two ColumnExpressions using /.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

           # Example 1: Divide the income by 2 and assign the divided income to new column 'divided_income'.
            >>> df.assign(divided_income=df.income / 2)
               start_time_column end_time_column  expenditure  income  investment  divided_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0           242.5
            2           67/06/30        07/07/10        421.0   465.0       179.0           232.5
            1           67/06/30        07/07/10        415.0   451.0       180.0           225.5
            5           67/06/30        07/07/10        459.0   509.0       211.0           254.5
            4           67/06/30        07/07/10        448.0   493.0       192.0           246.5

            # Example 2: Calculate the percent of investment of income and assign the
            #            final amount to new column 'divided_income'.
            >>> df.assign(divided_income=df.investment * 100 / df.income)
               start_time_column end_time_column  expenditure  income  investment  divided_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0       38.144330
            2           67/06/30        07/07/10        421.0   465.0       179.0       38.494624
            1           67/06/30        07/07/10        415.0   451.0       180.0       39.911308
            5           67/06/30        07/07/10        459.0   509.0       211.0       41.453831
            4           67/06/30        07/07/10        448.0   493.0       192.0       38.945233
        """
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(expr / self.expression)
        return res

    @_handle_sql_error
    def __floordiv__(self, other):
        """
        Compute the floor division between two ColumnExpressions using //.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Divide the income by 2 and assign the divided income to
            #            new column 'divided_income'.
            >>> df.assign(divided_income=df.income // 2)
               start_time_column end_time_column  expenditure  income  investment  divided_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0           242.0
            2           67/06/30        07/07/10        421.0   465.0       179.0           232.0
            1           67/06/30        07/07/10        415.0   451.0       180.0           225.0
            5           67/06/30        07/07/10        459.0   509.0       211.0           254.0
            4           67/06/30        07/07/10        448.0   493.0       192.0           246.0

            # Example 2: Calculate the percent of investment of income and assign the
            #            final amount to new column 'percent_inverstment'.
            >>> df.assign(percent_inverstment=df.investment * 100 // df.income)
               start_time_column end_time_column  expenditure  income  investment  percent_inverstment
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0                 38.0
            2           67/06/30        07/07/10        421.0   465.0       179.0                 38.0
            1           67/06/30        07/07/10        415.0   451.0       180.0                 39.0
            5           67/06/30        07/07/10        459.0   509.0       211.0                 41.0
            4           67/06/30        07/07/10        448.0   493.0       192.0                 38.0
        """
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression // expr)
        return res

    @_handle_sql_error
    def __rfloordiv__(self, other):
        """
        Compute the floor division between two ColumnExpressions using //.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Divide the income by 2 and assign the divided income
            #            to new column 'divided_income'.
            >>> df.assign(divided_income=c1 // 2)

            # Example 2: Calculate the percent of investment of income and assign the
            #            final output to new column 'percent_inverstment_'.
            >>> df.assign(percent_inverstment_=df.investment * 100 // df.income)
        """
        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(expr // self.expression)
        return res

    @_handle_sql_error
    def __mod__(self, other):
        """
        Compute the MOD between two ColumnExpressions using %.

        PARAMETERS:
            other :
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Calculate the reminder by taking mod of 2 on income and assign the
            #            reminder to new column 'reminder'.
            >>> df.assign(reminder=df.income.mod(2))
               start_time_column end_time_column  expenditure  income  investment   reminder
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0        1.0
            2           67/06/30        07/07/10        421.0   465.0       179.0        1.0
            1           67/06/30        07/07/10        415.0   451.0       180.0        1.0
            5           67/06/30        07/07/10        459.0   509.0       211.0        1.0
            4           67/06/30        07/07/10        448.0   493.0       192.0        1.0
        """

        expr = other.expression if isinstance(other, _SQLColumnExpression) else other
        res = _SQLColumnExpression(self.expression % expr)
        return res

    @_handle_sql_error
    def __rmod__(self, other):
        """
        Compute the MOD between two ColumnExpressions using %.
        Note: string types already override the __mod__ . We cannot override it
              if the string type is the left operand.

        PARAMETERS:
            other :
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression

        RETURNS:
            ColumnExpression, Python literal

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression.

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Calculate the reminder by taking mod of 2 on income and assign the
            #            reminder to new column 'reminder'.
            >>> df.assign(reminder=df.income.mod(2))
               start_time_column end_time_column  expenditure  income  investment   reminder
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0        1.0
            2           67/06/30        07/07/10        421.0   465.0       179.0        1.0
            1           67/06/30        07/07/10        415.0   451.0       180.0        1.0
            5           67/06/30        07/07/10        459.0   509.0       211.0        1.0
            4           67/06/30        07/07/10        448.0   493.0       192.0        1.0
        """

        expr = other.expression if isinstance(other, _SQLColumnExpression) else other

        if type(expr) is str:
            raise ValueError('MOD with string literals as the left operand is unsupported')

        res = _SQLColumnExpression(expr % self.expression)
        return res

    @_handle_sql_error
    def __neg__(self):
        """
        Compute the unary negation of the ColumnExpressions using -.

        PARAMETERS:
            None

        RETURNS:
            _SQLColumnExpression

        RAISES:
            Exception
                A TeradataMlException gets thrown if SQLAlchemy
                throws an exception when evaluating the expression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Negate the values in the column 'gpa' and assign those
            #           values to new column 'negate_gpa'.
            >>> df.assign(negate_gpa=-df.gpa)
               masters   gpa     stats programming  admitted  negate_gpa
            id
            5       no  3.44    Novice      Novice         0       -3.44
            34     yes  3.85  Advanced    Beginner         0       -3.85
            13      no  4.00  Advanced      Novice         1       -4.00
            40     yes  3.95    Novice    Beginner         0       -3.95
            22     yes  3.46    Novice    Beginner         0       -3.46
            19     yes  1.98  Advanced    Advanced         0       -1.98
            36      no  3.00  Advanced      Novice         0       -3.00
            15     yes  4.00  Advanced    Advanced         1       -4.00
            7      yes  2.33    Novice      Novice         1       -2.33
            17      no  3.83  Advanced    Advanced         1       -3.83

            # Example 2: Filter out the rows by taking negation of gpa not equal to 3.44 or
            #            admitted equal to 1.
            >>> df[~((df.gpa != 3.44) | (df.admitted == 1))]
                         id masters   gpa   stats  admitted
            programming
            Novice        5      no  3.44  Novice         0

        """

        res = _SQLColumnExpression(-self.expression)
        return res


# Accessor classes
class _StringMethods(object):
    """
    A class for implementing string methods for string-like ColumnExpressions
    This accessor class should only be used from the str property of a ColumnExpression

    This class is internal.
    """
    def __init__(self, c):
        """
            PARAMETERS:
                c: A ColumnExpression instance

        """
        self.c = c

    @collect_queryband(queryband="DFC_lower")
    def lower(self):
        """
        Convert character column values to lowercase.
        REFERENCE:
            SQL Functions, Operators, Expressions, and Predicates
            Chapter 26 String Operators and Functions

        PARAMETERS:
            None

        RETURNS:
            A str Series with values lowercased

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017

            >>> accounts = df['accounts']

            # Example 1: Convert the 'account' column values to lower case.
            >>> df.assign(drop_columns = True, lower = df.accounts.str.lower())
                    lower
            0  orange inc
            1    blue inc
            2  yellow inc
            3     red inc
            4   jones llc
            5    alpha co
        """
        res = _SQLColumnExpression(
                func.lower(
                  self.c.expression,
                  type_ = self.c.type
                )
               )
        return res

    @collect_queryband(queryband="DFC_contains")
    def contains(self, pattern, case = True, na = None, **kw):
        """
        Search the pattern or substring in the column.

        PARAMETERS:
            pattern:
                Required Argument.
                Specifies a literal value or ColumnExpression. Use ColumnExpression
                when comparison is done based on values inside ColumnExpression or
                based on a ColumnExpression function. Else, use literal value.
                Note:
                     Argument supports regular expressions too.
                Types: str OR ColumnExpression

            case:
                Optional Argument.
                Specifies the case-sentivity match.
                When True, case-sensitive matches, otherwise case-sensitive does not matches.
                Default value: True
                Types: bool

            na:
                Optional Argument.
                Specifies an optional fill value for NULL values in the column
                Types: bool, str, or numeric python literal.

            **kw:
                Optional Argument.
                Specifies optional parameters to pass to regexp_substr
                match_arg:
                    A string of characters to use for the match_arg parameter for REGEXP_SUBSTR
                    See the Reference for more information about the match_arg parameter.
                Note:
                     Specifying match_arg overrides the case parameter


        RETURNS:
            A numeric Series of values where:
                - Nulls are replaced by the fill parameter
                - A 1 if the value matches the pattern or else 0
            The type of the series is upcasted to support the fill value, if specified.

        EXAMPLES:
            >>> load_example_data("sentimentextractor", "additional_table")
            >>> df = DataFrame("additional_table")
            >>> df
                            polarity_strength
            sentiment_word
            'integral'                      1
            'eagerness'                     1
            'fearfully'                    -1
            irregular'                     -1
            'upgradable'                    1
            'rupture'                      -1
            'imperfect'                    -1
            'rejoicing'                     1
            'comforting'                    1
            'obstinate'                    -1

            >>> sentiment_word = df["sentiment_word"]

            # Example 1: Check if 'in' string is present or not in values in
            #            column 'sentiment_word'.
            >>> df.assign(drop_columns = True,
                         Name = sentiment_word,
                         has_in = sentiment_word.str.contains('in'))
                       Name has_in
            0    'integral'      1
            1   'eagerness'      0
            2   'fearfully'      0
            3    irregular'      0
            4  'upgradable'      0
            5     'rupture'      0
            6   'imperfect'      0
            7   'rejoicing'      1
            8  'comforting'      1
            9   'obstinate'      1

             # Example 2: Check if accounts column contains 'Er' string by ignoring
             #            case sensitivity and specifying a literal for null values.
             >>> df.assign(drop_columns = True,
                           Name = sentiment_word,
                           has_er = sentiment_word.str.contains('ER', case=False, na = 'no value'))
                        Name has_er
             0    'integral'      0
             1   'eagerness'      1
             2   'fearfully'      0
             3    irregular'      0
             4  'upgradable'      0
             5     'rupture'      0
             6   'imperfect'      1
             7   'rejoicing'      0
             8  'comforting'      0
             9   'obstinate'      0

            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017

            # Example 3: Get the all the accounts where accounts has 'Inc' string.
            >>> df[accounts.str.contains('Inc') == True]
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017

            # Example 4: Get all the accounts where accounts does not
            #            have 'Inc' string.
            >>> df[accounts.str.contains('Inc') == False]
                         Feb  Jan  Mar  Apr    datetime
            accounts
            Jones LLC  200.0  150  140  180  04/01/2017
            Alpha Co   210.0  200  215  250  04/01/2017

            # Example 5: Get all the accounts where accounts has 'Inc' by
            #            specifying numeric literals for True (1).
            >>> df[accounts.str.contains('Inc') == 1]
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017

            #Example 6: Get all the accounts where accounts has 'Inc' by
            #           specifying numeric literals for False (0).
            >>> df[accounts.str.contains('Inc') == 0]
                         Feb  Jan  Mar  Apr    datetime
            accounts
            Jones LLC  200.0  150  140  180  04/01/2017
            Alpha Co   210.0  200  215  250  04/01/2017

            >>> load_example_data("ntree", "employee_table")
            >>> df = DataFrame("employee_table")
            >>> df
                   emp_name  mgr_id mgr_name
            emp_id
            200         Pat   100.0      Don
            300       Donna   100.0      Don
            400         Kim   200.0      Pat
            500        Fred   400.0      Kim
            100         Don     NaN       NA

            # Example 7: Get all the employees whose name has managers name.
            >>> df[df.emp_name.str.contains(df.mgr_name) == True]
            >>> df
                   emp_name  mgr_id mgr_name
            emp_id
            300       Donna     100      Don
        """
        if not isinstance(pattern, (str, ColumnExpression)):
            raise TypeError('str.contains requires the pattern parameter to be a string.')

        if not isinstance(case, bool):
            raise TypeError('str.contains requires the case parameter to be True or False.')

        match_arg = kw.get('match_arg', 'c' if case else 'i')
        regexp_substr = func.regexp_substr(
                           self.c.expression,
                           pattern.expression if isinstance(pattern, ColumnExpression) else pattern, 1, 1,
                           match_arg)

        expr = case_when((regexp_substr == None, 0), else_ = 1)
        expr = case_when((self.c.expression == None, na), else_ = expr)

        if na is not None:

            # na should be numeric or string-like or bool
            if not isinstance(na, (str, float, int, decimal.Decimal, bool)):
                raise TypeError('str.contains requires the na parameter to be a numeric, string, or bool literal.')

            # the resulting type is the type of the na (if not None), otherwise BYTEINT
            type_ = _resolve_value_to_type(na, len_ = len(na) if isinstance(na, str) else None)
            expr.type = type_

        return _SQLColumnExpression(expr)

    @collect_queryband(queryband="DFC_strip")
    def strip(self):
        """
        Remove leading and trailing whitespace.
        REFERENCE:
            SQL Functions, Operators, Expressions, and Predicates
            Chapter 26 String Operators and Functions

        PARAMETERS:
            None

        RETURNS:
            A str Series with leading and trailing whitespace removed

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017

            >>> accounts = df['accounts']

            # create a column with some whitespace
            >>> wdf = df.assign(drop_columns = True,
                              accounts = accounts,
                              w_spaces = '\n ' + accounts + '\v\f \t')
            >>> wdf

                                  w_spaces
            accounts
            Blue Inc      \n Blue Inc

             \t
            Orange Inc  \n Orange Inc

             \t
            Red Inc        \n Red Inc

             \t
            Yellow Inc  \n Yellow Inc

             \t
            Jones LLC    \n Jones LLC

             \t
            Alpha Co      \n Alpha Co

             \t

            # Example 1: Strip the leading and trailing whitespace.
            >>> wdf.assign(drop_columns = True,
                         wo_wspaces = wdf.w_spaces.str.strip())

               wo_wspaces
            0    Blue Inc
            1  Orange Inc
            2     Red Inc
            3  Yellow Inc
            4   Jones LLC
            5    Alpha Co
        """
        whitespace = '\n \t\r\v\f'
        res = func.rtrim(
                func.ltrim(
                    self.c.expression,
                    whitespace
                ),
                whitespace, type_ = self.c.type
              )

        return _SQLColumnExpression(res)

class _SeriesColumnExpression(ColumnExpression):

    """
        The _SeriesColumnExpression implements the pandas.Series methods
        for _SQLColumnExpression.
    """

    @property # TODO: consider making this a cached property
    def str(self):
        """
        The string accessor.
        Upon validation, returns a reference to a _StringMethods instance
        """
        if not isinstance(self.type, (CHAR, VARCHAR, CLOB)):
            raise AttributeError('The str accessor is only valid for string-like columns (CHAR, VARCHAR, or CLOB).')

        elif isinstance(getattr(self, '_SeriesColumnExpression__str', None), _StringMethods):
            return self.__str

        # otherwise, initialize the accessor
        self.str = _StringMethods(self)
        return self.__str

    @str.setter
    def str(self, accessor):
        """
        """
        if isinstance(accessor, _StringMethods):
            self.__str = accessor

        # otherwise, just ignore

    @collect_queryband(queryband="DFC_gt")
    def gt(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values greater than the other or not.

        PARAMETERS:
            other :
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Get all the students with gpa greater than 3.
            >>> df[df.gpa.gt(3)]
               masters   gpa     stats programming  admitted
            id
            3       no  3.70    Novice    Beginner         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            15     yes  4.00  Advanced    Advanced         1
            30     yes  3.79  Advanced      Novice         0
            14     yes  3.45  Advanced    Advanced         0
            31     yes  3.50  Advanced    Beginner         1
            37      no  3.52    Novice      Novice         1
            1      yes  3.95  Beginner    Beginner         0

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure greater than 400 and investment
            #            greater than 170.
            >>> df[(df.expenditure.gt(400)) & (df.investment.gt(170))]
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        return self > other

    @collect_queryband(queryband="DFC_ge")
    def ge(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values greater than or equal to the other or not.

        PARAMETERS:
            other :
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Get all the students with gpa greater than
            #            or equal to 3.
            >>> df[df.gpa.ge(3)]
               masters   gpa     stats programming  admitted
            id
            3       no  3.70    Novice    Beginner         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            30     yes  3.79  Advanced      Novice         0
            14     yes  3.45  Advanced    Advanced         0
            37      no  3.52    Novice      Novice         1
            1      yes  3.95  Beginner    Beginner         0

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure greater than or equal to 450 and
            #            investment is greater than or equal to 200.
            >>> df[(df.expenditure.ge(450)) & (df.investment.ge(200))]
               start_time_column end_time_column  expenditure  income  investment
            id
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        return self >= other

    @collect_queryband(queryband="DFC_lt")
    def lt(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values less than the other or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Get all the students with gpa less than 4.
            >>> df[df.gpa.lt(4)]
               masters   gpa     stats programming  admitted
            id
            5       no  3.44    Novice      Novice         0
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            19     yes  1.98  Advanced    Advanced         0
            36      no  3.00  Advanced      Novice         0
            30     yes  3.79  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            17      no  3.83  Advanced    Advanced         1

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure less than 440 and
            #            income greater than 180.
            >>> df[(df.expenditure.lt(440)) & (df.income.lt(180))]
               start_time_column end_time_column  expenditure  income  investment
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0
        """
        return self < other

    @collect_queryband(queryband="DFC_le")
    def le(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values less than or equal to other or not.

        PARAMETERS:
        other:
            Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Get all the students with gpa less than
            #              or equal to 3.
            >>> df[df.gpa.le(3)]
               masters   gpa     stats programming  admitted
            id
            36      no  3.00  Advanced      Novice         0
            24      no  1.87  Advanced      Novice         1
            38     yes  2.65  Advanced    Beginner         1
            19     yes  1.98  Advanced    Advanced         0
            7      yes  2.33    Novice      Novice         1

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure less than or equal to
            #            500 and income less than or equal to 480.
            >>> df[(df.expenditure.le(500)) & (df.income.le(480))]
               start_time_column end_time_column  expenditure  income  investment
            id
            2           67/06/30        07/07/10        421.0   465.0       179.0
            1           67/06/30        07/07/10        415.0   451.0       180.0
        """
        return self <= other

    @collect_queryband(queryband="DFC_eq")
    def eq(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values equal to other or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Get all the students with gpa equal to 3.
            >>> df[df.gpa.eq(3)]
               masters  gpa     stats programming  admitted
            id
            36      no  3.0  Advanced      Novice         0

            # Example 2: Get all the students with gpa equal to 3 and
            #            admitted values equal to 0.
            >>> df[c1.eq(3) & c2.eq(0)]
               masters  gpa     stats programming  admitted
            id
            36      no  3.0  Advanced      Novice         0

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure equal to 415 or income equal to 509.
            >>> df[(df.expenditure.eq(415)) | (df.income.eq(509))]
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        return self == other

    @collect_queryband(queryband="DFC_ne")
    def ne(self, other):
        """
        Compare the ColumnExpressions to check if one ColumnExpression
        has values not equal to other.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Get all the students with gpa values not equal to 3.44.
            >>> df[df.gpa.ne(3.44)]
               masters   gpa     stats programming  admitted
            id
            24      no  1.87  Advanced      Novice         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            19     yes  1.98  Advanced    Advanced         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            7      yes  2.33    Novice      Novice         1
            17      no  3.83  Advanced    Advanced         1

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Get all rows with expenditure not equal to 415 or income
            #            not equal to 400.
            >>> df[(df.expenditure.ne(415)) | (df.income.ne(400))]
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        return self != other

    @collect_queryband(queryband="DFC_add")
    def add(self, other):
        """
        Compute the addition between two ColumnExpressions.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Add 100 to the expenditure amount and assign the final amount
            #            to new column 'total_expenditure'.
            >>> df.assign(total_expenditure=df.expenditure.add(100))
               start_time_column end_time_column  expenditure  income  investment  total_expenditure
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0              534.0
            2           67/06/30        07/07/10        421.0   465.0       179.0              521.0
            1           67/06/30        07/07/10        415.0   451.0       180.0              515.0
            5           67/06/30        07/07/10        459.0   509.0       211.0              559.0
            4           67/06/30        07/07/10        448.0   493.0       192.0              548.0

            # Example 2: Filter the rows where the income left after the investment is more than 300.
            >>> df[df.income.sub(df.investment) > 300]
               start_time_column end_time_column  expenditure  income  investment
            id
            4           67/06/30        07/07/10        448.0   493.0       192.0        """
        return self + other

    @collect_queryband(queryband="DFC_sub")
    def sub(self, other):
        """
        Compute the subtraction between two ColumnExpressions.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Subtract 100 from the income amount and assign the final amount
            #            to new column 'remaining_income'.
            >>> df.assign(remaining_income=df.income - 100)
               start_time_column end_time_column  expenditure  income  investment  remaining_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0             385.0
            2           67/06/30        07/07/10        421.0   465.0       179.0             365.0
            1           67/06/30        07/07/10        415.0   451.0       180.0             351.0
            5           67/06/30        07/07/10        459.0   509.0       211.0             409.0
            4           67/06/30        07/07/10        448.0   493.0       192.0             393.0

            # Example 2: Filter the rows where the income left after the investment is more than 300.
            >>> df[df.income.sub(df.investment) > 300]
               start_time_column end_time_column  expenditure  income  investment
            id
            4           67/06/30        07/07/10        448.0   493.0       192.0
        """
        return self - other

    @collect_queryband(queryband="DFC_mul")
    def mul(self, other):
        """
        Compute the multiplication between two ColumnExpressions.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            7      yes  2.33    Novice      Novice         1
            19     yes  1.98  Advanced    Advanced         0

            # Example 1: Increase the GPA for each student by 10 % and assign
            #            increased income to new column 'increased_gpa'.
            >>> df.assign(increased_gpa=df.gpa + df.gpa.mul(0.1))
               masters   gpa     stats programming  admitted  increased_gpa
            id
            22     yes  3.46    Novice    Beginner         0          3.806
            26     yes  3.57  Advanced    Advanced         1          3.927
            5       no  3.44    Novice      Novice         0          3.784
            17      no  3.83  Advanced    Advanced         1          4.213
            13      no  4.00  Advanced      Novice         1          4.400
            19     yes  1.98  Advanced    Advanced         0          2.178
            36      no  3.00  Advanced      Novice         0          3.300
            15     yes  4.00  Advanced    Advanced         1          4.400
            34     yes  3.85  Advanced    Beginner         0          4.235
            38     yes  2.65  Advanced    Beginner         1          2.915

            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 2: Calculate the percent of investment done of total income and assign the
            #            final amount to new column 'percentage_investment'.
            >>> df.assign(percentage_investment=(df.investment.mul(100)).div(df.income))
               start_time_column end_time_column  expenditure  income  investment  percentage_investment
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0              38.144330
            2           67/06/30        07/07/10        421.0   465.0       179.0              38.494624
            1           67/06/30        07/07/10        415.0   451.0       180.0              39.911308
            5           67/06/30        07/07/10        459.0   509.0       211.0              41.453831
            4           67/06/30        07/07/10        448.0   493.0       192.0              38.945233

            # Example 3: Filter out the rows after doubling income is greater than 1000.
            >>> df[(df.income * 2) > 1000]
               start_time_column end_time_column  expenditure  income  investment  double_income
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0          970.0
            2           67/06/30        07/07/10        421.0   465.0       179.0          930.0
            1           67/06/30        07/07/10        415.0   451.0       180.0          902.0
            5           67/06/30        07/07/10        459.0   509.0       211.0         1018.0
            4           67/06/30        07/07/10        448.0   493.0       192.0          986.0
        """
        return self * other

    @collect_queryband(queryband="DFC_div")
    def div(self, other):
        """
        Compute the division between two ColumnExpressions.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Calculate the percent of investment of income and assign the
            #            divided amount to new column 'percentage_investment'.
            >>> df.assign(percentage_investment=(df.investment.mul(100)).truediv(df.income))
               start_time_column end_time_column  expenditure  income  investment  percentage_investment
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0              38.144330
            2           67/06/30        07/07/10        421.0   465.0       179.0              38.494624
            1           67/06/30        07/07/10        415.0   451.0       180.0              39.911308
            5           67/06/30        07/07/10        459.0   509.0       211.0              41.453831
            4           67/06/30        07/07/10        448.0   493.0       192.0              38.945233

            # Example 2: Filter out the rows after diving income amount by 2 is less than 240.
            >>> df[(df.income.div(2)) < 240]
               start_time_column end_time_column  expenditure  income  investment
            id
            2           67/06/30        07/07/10        421.0   465.0       179.0
            1           67/06/30        07/07/10        415.0   451.0       180.0
        """
        return self.truediv(other)

    @collect_queryband(queryband="DFC_truediv")
    def truediv(self, other):
        """
        Compute the true-division between two ColumnExpressions.

        PARAMETERS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Calculate the percent of investment of income and assign the
            #            final amount to new column 'percentage_investment'.
            >>> df.assign(percentage_investment=(df.investment.mul(100)).truediv(df.income))
               start_time_column end_time_column  expenditure  income  investment  percentage_investment
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0              38.144330
            2           67/06/30        07/07/10        421.0   465.0       179.0              38.494624
            1           67/06/30        07/07/10        415.0   451.0       180.0              39.911308
            5           67/06/30        07/07/10        459.0   509.0       211.0              41.453831
            4           67/06/30        07/07/10        448.0   493.0       192.0              38.945233

            # Example 2: Filter out the rows after diving income amount by 2 is less than 240.
            >>> df[(df.income.truediv(2)) < 240]
               start_time_column end_time_column  expenditure  income  investment
            id
            2           67/06/30        07/07/10        421.0   465.0       179.0
            1           67/06/30        07/07/10        415.0   451.0       180.0
        """
        return self / other

    @collect_queryband(queryband="DFC_floordiv")
    def floordiv(self, other):
        """
        Compute the floor-division between two ColumnExpressions.

        PARAMETRS:
            other:
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Calculate the percent of investment of income and assign the
            #            final amount to new column 'percentage_investment'.
            >>> df.assign(percentage_investment=(df.investment.mul(100)).floordiv(df.income))
               start_time_column end_time_column  expenditure  income  investment  percentage_investment
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0                   38.0
            2           67/06/30        07/07/10        421.0   465.0       179.0                   38.0
            1           67/06/30        07/07/10        415.0   451.0       180.0                   39.0
            5           67/06/30        07/07/10        459.0   509.0       211.0                   41.0
            4           67/06/30        07/07/10        448.0   493.0       192.0                   38.0

            # Example 2: Filter out the rows after diving income amount by 2 is less than 240.
            >>> df[(df.income.floordiv(2)) < 240]
               start_time_column end_time_column  expenditure  income  investment
            id
            2           67/06/30        07/07/10        421.0   465.0       179.0
            1           67/06/30        07/07/10        415.0   451.0       180.0
        """
        return self // other

    @collect_queryband(queryband="DFC_mod")
    def mod(self, other):
        """
        Compute the mod between two ColumnExpressions.

        PARAMETERS:
            other :
                Required Argument.
                Specifies Python literal or another ColumnExpression.
                Types: ColumnExpression, Python literal

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("burst", "finance_data")
            >>> df = DataFrame("finance_data")
            >>> df
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0

            # Example 1: Calculate the reminder by taking mod of 2 on income and assign the
            #            reminder to new column 'reminder_'.
            >>> df.assign(reminder_=df.income.mod(2))
               start_time_column end_time_column  expenditure  income  investment  reminder_
            id
            3           67/06/30        07/07/10        434.0   485.0       185.0        1.0
            2           67/06/30        07/07/10        421.0   465.0       179.0        1.0
            1           67/06/30        07/07/10        415.0   451.0       180.0        1.0
            5           67/06/30        07/07/10        459.0   509.0       211.0        1.0
            4           67/06/30        07/07/10        448.0   493.0       192.0        1.0

            Example 2: Filter out the rows where left over reminder of income is greater than 0.
            >>> df[df.income.mod(2) > 0]
               start_time_column end_time_column  expenditure  income  investment
            id
            1           67/06/30        07/07/10        415.0   451.0       180.0
            4           67/06/30        07/07/10        448.0   493.0       192.0
            2           67/06/30        07/07/10        421.0   465.0       179.0
            3           67/06/30        07/07/10        434.0   485.0       185.0
            5           67/06/30        07/07/10        459.0   509.0       211.0
        """
        return self % other

    @collect_queryband(queryband="DFC_isna")
    def isna(self):
        """
        Test for NA values

        PARAMETERS:
            None

        RETURNS:
            When used with assign() function, newly assigned column contains
            A boolean Series of numeric values:
              - 1 if value is NA (None)
              - 0 if values is not NA
            Otherwise returns ColumnExpression, also known as, teradataml DataFrameColumn.

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Example 1: Filter out the NA values from 'Mar' column.
            >>> df[df.Mar.isna() == 1]
                          Feb   Jan   Mar    Apr    datetime
            accounts
            Orange Inc  210.0  None  None  250.0  04/01/2017
            Yellow Inc   90.0  None  None    NaN  04/01/2017

            # Filter out the non-NA values from 'Mar' column.
            >>> df[df.Mar.isna() == 0]
                         Feb  Jan  Mar    Apr    datetime
            accounts
            Blue Inc    90.0   50   95  101.0  04/01/2017
            Red Inc    200.0  150  140    NaN  04/01/2017
            Jones LLC  200.0  150  140  180.0  04/01/2017
            Alpha Co   210.0  200  215  250.0  04/01/2017

            # Example 2: Filter out the NA values from 'Mar' column using boolean True.
            >>> df[df.Mar.isna() == True]
                          Feb   Jan   Mar    Apr    datetime
            accounts
            Orange Inc  210.0  None  None  250.0  04/01/2017
            Yellow Inc   90.0  None  None    NaN  04/01/2017

            # Filter out the non-NA values from 'Mar' column using boolean False.
            >>> df[df.Mar.isna() == False]
                         Feb  Jan  Mar    Apr    datetime
            accounts
            Blue Inc    90.0   50   95  101.0  04/01/2017
            Red Inc    200.0  150  140    NaN  04/01/2017
            Jones LLC  200.0  150  140  180.0  04/01/2017
            Alpha Co   210.0  200  215  250.0  04/01/2017

            # Example 3: Assign the tested values to dataframe as a column.
            >>> df.assign(isna_=df.Mar.isna())
                          Feb    Jan    Mar    Apr    datetime isna_
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017     0
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017     1
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017     0
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017     1
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017     0
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017     0

        """
        res = _SQLColumnExpression(
                case_when(
                        (self.expression != None, 0),
                        else_ = 1
                )
            )
        return res

    @collect_queryband(queryband="DFC_isnull")
    def isnull(self):
        """
        Test for NA values. Alias for isna()

        PARAMETERS:
            None

        RETURNS:
            When used with assign() function, newly assigned column contains
            A boolean Series of numeric values:
              - 1 if value is NA (None)
              - 0 if values is not NA
            Otherwise returns ColumnExpression, also known as, teradataml DataFrameColumn.

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Example 1: Filter out the NA values from 'Mar' column.
            >>> df[df.Mar.isnull() == 1]
                          Feb   Jan   Mar    Apr    datetime
            accounts
            Orange Inc  210.0  None  None  250.0  04/01/2017
            Yellow Inc   90.0  None  None    NaN  04/01/2017

            # Filter out the non-NA values from 'Mar' column.
            >>> df[df.Mar.isnull() == 0]
                         Feb  Jan  Mar    Apr    datetime
            accounts
            Blue Inc    90.0   50   95  101.0  04/01/2017
            Red Inc    200.0  150  140    NaN  04/01/2017
            Jones LLC  200.0  150  140  180.0  04/01/2017
            Alpha Co   210.0  200  215  250.0  04/01/2017

            # Example 2: Filter out the NA values from 'Mar' column using boolean True.
            >>> df[df.Mar.isnull() == True]
                          Feb   Jan   Mar    Apr    datetime
            accounts
            Orange Inc  210.0  None  None  250.0  04/01/2017
            Yellow Inc   90.0  None  None    NaN  04/01/2017

            # Filter out the non-NA values from 'Mar' column using boolean False.
            >>> df[df.Mar.isnull() == False]
                         Feb  Jan  Mar    Apr    datetime
            accounts
            Blue Inc    90.0   50   95  101.0  04/01/2017
            Red Inc    200.0  150  140    NaN  04/01/2017
            Jones LLC  200.0  150  140  180.0  04/01/2017
            Alpha Co   210.0  200  215  250.0  04/01/2017

            # Example 3: Assign the tested values to dataframe as a column.
            >>> df.assign(isnull_=df.Mar.isnull())
                          Feb    Jan    Mar    Apr    datetime isnull_
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017     0
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017     1
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017     0
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017     1
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017     0
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017     0
        """
        return self.isna()

    @collect_queryband(queryband="DFC_notna")
    def notna(self):
        """
        Test for non NA values
        The boolean complement of isna()

        PARAMETERS:
            None

        RETURNS:
            When used with assign() function, newly assigned column contains
            A boolean Series of numeric values:
              - 1 if value is NA (None)
              - 0 if values is not NA
            Otherwise returns ColumnExpression, also known as, teradataml DataFrameColumn.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")

            # Test for NA values on dataframe by using 0 and 1.
            >>> df[df.gpa.notna() == 1]
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0

            >>> df[df.gpa.notna() == 0]
            Empty DataFrame
            Columns: [masters, gpa, stats, programming, admitted]
            Index: []

            # Test for NA values on dataframe by using False and True.
            >>> df[df.gpa.notna() == True]
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0

            >>> df[df.gpa.notna() == False]
            Empty DataFrame
            Columns: [masters, gpa, stats, programming, admitted]
            Index: []

            # Assign the tested values to dataframe as a column.
            >>> df.assign(notna_=df.gpa.notna())
               masters   gpa     stats programming  admitted notna_
            id
            22     yes  3.46    Novice    Beginner         0      1
            36      no  3.00  Advanced      Novice         0      1
            15     yes  4.00  Advanced    Advanced         1      1
            38     yes  2.65  Advanced    Beginner         1      1
            5       no  3.44    Novice      Novice         0      1
            17      no  3.83  Advanced    Advanced         1      1
            34     yes  3.85  Advanced    Beginner         0      1
            13      no  4.00  Advanced      Novice         1      1
            26     yes  3.57  Advanced    Advanced         1      1
            19     yes  1.98  Advanced    Advanced         0      1
        """
        res = _SQLColumnExpression(
                case_when(
                        (self.expression != None, 1),
                        else_ = 0
                )
            )

        return res

    @collect_queryband(queryband="DFC_notnull")
    def notnull(self):
        """
        Alias for notna().Test for non NA values
        The boolean complement of isna()

        PARAMETERS:
            None

        RETURNS:
            When used with assign() function, newly assigned column contains
            A boolean Series of numeric values:
              - 1 if value is NA (None)
              - 0 if values is not NA
            Otherwise returns ColumnExpression, also known as, teradataml DataFrameColumn.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")

            >>> df[df.gpa.notnull() == 1]
               masters   gpa     stats programming  admitted
            id
            5       no  3.44    Novice      Novice         0
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            40     yes  3.95    Novice    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            19     yes  1.98  Advanced    Advanced         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            7      yes  2.33    Novice      Novice         1
            17      no  3.83  Advanced    Advanced         1

            >>> df[df.gpa.notnull() == 0]
            Empty DataFrame
            Columns: [masters, gpa, stats, programming, admitted]
            Index: []

            # alternatively, True and False can be used
            >>> df[df.gpa.notnull() == True]
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            13      no  4.00  Advanced      Novice         1
            19     yes  1.98  Advanced    Advanced         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            38     yes  2.65  Advanced    Beginner         1

            >>> df[df.gpa.notnull() == False]
            Empty DataFrame
            Columns: [masters, gpa, stats, programming, admitted]
            Index: []

            # Assign the tested values to dataframe as a column.
            >>> df.assign(notnull_=df.gpa.notnull())
               masters   gpa     stats programming  admitted notnull_
            id
            22     yes  3.46    Novice    Beginner         0       1
            26     yes  3.57  Advanced    Advanced         1       1
            5       no  3.44    Novice      Novice         0       1
            17      no  3.83  Advanced    Advanced         1       1
            13      no  4.00  Advanced      Novice         1       1
            19     yes  1.98  Advanced    Advanced         0       1
            36      no  3.00  Advanced      Novice         0       1
            15     yes  4.00  Advanced    Advanced         1       1
            34     yes  3.85  Advanced    Beginner         0       1
            38     yes  2.65  Advanced    Beginner         1       1
        """
        return self.notna()

    def _unique(self):
        """
        Private method to return _SQLColumnExpression with DISTINCT applied on it.

        NOTE : This operation is valid only when the resultant _MetaExpression has
               just this one _SQLColumnExpression. All other operations will fail with
               a database error given the nature of the DISTINCT keyword.

               For example:
               >>> df = DataFrame("admissions_train") # a multi-column table
               >>> # Filter operations will fail
               >>> df = df[df.gpa._unique() > 2.00]
               >>> # Assign operations resulting in multiple columns
               >>> df.assign(x = df.gpa._unique())

               The following however is fine since it return only the one column
               with DISTINCT applied to it

               >>> df.assign(drop_columns = True, x = df.gpa._unique())

        PARAMETERS:
            None

        RETURNS:
            _SQLColumnExpression

        EXAMPLES:
            df = DataFrame(...)
            c1 = df.c1
            c1.unique()
        """
        res = _SQLColumnExpression(
                    self.expression.distinct()
              )

        return res

    @collect_queryband(queryband="DFC_isin")
    def isin(self, values=None):
        """
        Function to check for the presence of values in a column.

        PARAMETERS:
            values:
                Required Argument.
                Specifies the list of values to check for their presence in the column.
                in the provided set of values.
                Types: list

        RETURNS:
            _SQLColumnExpression

        RAISES:
            TypeError - If invalid type of values are passed to argument 'values'.
            ValueError - If None is passed to argument 'values'.

        EXAMPLES:
            >>> load_example_data("dataframe","admissions_train")
            >>> df = DataFrame('admissions_train')
            >>> df
               masters   gpa     stats programming  admitted
            id
            15     yes  4.00  Advanced    Advanced         1
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            17      no  3.83  Advanced    Advanced         1
            13      no  4.00  Advanced      Novice         1
            38     yes  2.65  Advanced    Beginner         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            34     yes  3.85  Advanced    Beginner         0
            40     yes  3.95    Novice    Beginner         0
            >>>

            # Example 1: Filter results where gpa values are in any of these following values:
            #            4.0, 3.0, 2.0, 1.0, 3.5, 2.5, 1.5
            >>> df[df.gpa.isin([4.0, 3.0, 2.0, 1.0, 3.5, 2.5, 1.5])]
               masters  gpa     stats programming  admitted
            id
            31     yes  3.5  Advanced    Beginner         1
            6      yes  3.5  Beginner    Advanced         1
            13      no  4.0  Advanced      Novice         1
            4      yes  3.5  Beginner      Novice         1
            29     yes  4.0    Novice    Beginner         0
            15     yes  4.0  Advanced    Advanced         1
            36      no  3.0  Advanced      Novice         0
            >>>

            # Example 2: Filter results where stats values are neither 'Novice' nor 'Advanced'
            >>> df[~df.stats.isin(['Novice', 'Advanced'])]
               masters   gpa     stats programming  admitted
            id
            1      yes  3.95  Beginner    Beginner         0
            2      yes  3.76  Beginner    Beginner         0
            8       no  3.60  Beginner    Advanced         1
            4      yes  3.50  Beginner      Novice         1
            6      yes  3.50  Beginner    Advanced         1
            >>>
        """
        # If 'values' is None or not specified, raise an Exception
        if values is None:
            raise ValueError(Messages.get_message(MessageCodes.MISSING_ARGS, 'values'))

        if not isinstance(values, list):
            raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, 'values', 'list'))

        return _SQLColumnExpression(self.expression.in_(values))


class _AggregateColumnExpresion(ColumnExpression):
    """
    A class for implementing aggregate methods for ColumnExpressions.
    This class contains several methods that can work as regular aggregates as well as
    time series aggregates.
    This class is internal.
    """

    original_expressions = []

    def __validate_operation(self, name, as_time_series_aggregate=False, describe_op=False,
                                   **kwargs):
        """
        DESCRIPTION:
            Internal function used by aggregates to validate whether column supports
            the aggregate operation or not.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the aggregate function/operation.
                Types: str

            as_time_series_aggregate:
                Optional Argument.
                Specifies a flag that decides whether the aggregate operation is time
                series aggregate or regular aggregate.
                Default Values: False (Regular Aggregate)
                Types: bool

            describe_op:
                Optional Argument.
                Specifies a flag that decides whether the aggregate operation being
                run is for describe operation or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
            None.

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            self.__validate_operation(func_obj.name, describe_op=describe_op, **kwargs)
        """
        is_window_aggregate = kwargs.get("window_properties", {})

        # sqlalchemy func.any_func().name returns different results for
        # different functions i.e.
        # >>> func.count().name
        # 'count'
        # >>> func.COUNT().name
        # 'count'
        # >>> func.msum().name
        # 'msum'
        # >>> func.MSUM().name
        # 'MSUM'
        # >>>
        # Since unsupported types mapper looks for lowercase names, converting
        # all to lowercase.
        name = name.lower()
        if not describe_op:
            unsupported_types = _Dtypes._get_unsupported_data_types_for_aggregate_operations(name,
                                                                                             as_time_series_aggregate,
                                                                                             is_window_aggregate)
        else:
            unsupported_types = _Dtypes._get_unsupported_data_types_for_describe_operations(name)
        if type(self.type) in unsupported_types:
            raise RuntimeError(
                "Unsupported operation '{}' on column '{}' of type '{}'".format(name, self.name, str(self.type)))

    def __generate_function_call_object(self, func_obj, *args, **kwargs):
        """
        DESCRIPTION:
            Internal function used by aggregates to generate actual function call using
            sqlalchemy FunctionGenerator.

        PARAMETERS:
            func_obj:
                Required Argument.
                Specifies the sqlalchemy FunctionGenerator object to be used generate
                actual function call.
                Types: sqlalchemy FunctionGenerator

            distinct:
                Optional Argument.
                Specifies a flag that decides whether the aggregate operation should consider
                duplicate rows or not.
                Default Values: False
                Types: bool

            skipna:
                Optional Argument.
                Specifies a flag that decides whether the aggregate operation should skip
                null values or not.
                Default Values: False
                Types: bool

            describe_op:
                Optional Argument.
                Specifies a flag that decides whether the aggregate operation being
                run is for describe operation or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
            _SQLColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            self.__generate_function_call_object(func.count, distinct=distinct, skipna=skipna, **kwargs)
        """

        from teradataml.dataframe.sql_function_parameters import NO_DEFAULT_PARAM_FUNCTIONS

        expr = self

        if kwargs.pop("skipna", False):
            expr = self.notna()

        default_args = [expr.expression]
        if kwargs.pop("distinct", False):
            default_args = [expr.expression.distinct()]

        # Most of the Aggregate functions take first parameter as, the column
        # on which the Aggregate function is being applied. However, few
        # functions (e.g. rank, quantile) do not accept first parameter as
        # corresponding column. So, if the function is of such type, do not
        # pass the column expression as first argument.
        if func_obj().name.upper() in NO_DEFAULT_PARAM_FUNCTIONS:
            default_args = []

        args = default_args + [arg.expression if isinstance(arg, _SQLColumnExpression)
                                     else arg for arg in args]

        # Check for window parameters in kwargs.
        window_properties = kwargs.get("window_properties", {})

        # Check within_group parameters in kwargs.
        within_group_properties = kwargs.get("within_group", {})

        get_quoted_cols = UtilFuncs._process_for_teradata_keyword
        if window_properties:
            func_obj = func_obj(*args).over(partition_by=get_quoted_cols(window_properties.get("partition_by")),
                                            rows=window_properties.get("rows"),
                                            order_by=get_quoted_cols(window_properties.get("order_by"))
                                            )
        elif within_group_properties:
            func_obj = func_obj(*args).within_group(get_quoted_cols(within_group_properties.get("order_by")))
        else:
            func_obj = func_obj(*args)

        # Remove describe_op from kwargs as it will passed as positional
        # argument.
        describe_op = kwargs.pop("describe_op", False)
        return self.__process_function_call_object(func_obj, describe_op, **kwargs)

    def __process_function_call_object(self, func_obj, describe_op=False, **kwargs):
        """
        DESCRIPTION:
            Internal function used by aggregates to process actual function call generated
            using sqlalchemy FunctionGenerator.
            This functions:
                1. Validates whether aggregate operation for the column is supported or not.
                2. Creates a new _SQLColumnExpression.
                3. Identifies the output column type for the aggregate function.

        PARAMETERS:
            func_obj:
                Required Argument.
                Specifies the sqlalchemy FunctionGenerator object to be used generate
                actual function call.
                Types: sqlalchemy FunctionGenerator

            describe_op:
                Optional Argument.
                Specifies a flag that decides whether the aggregate operation being
                run is for describe operation or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
            _SQLColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            self.__process_function_call_object(func_obj, describe_op, **kwargs)
        """
        # Perform validations for the function to check if operation is valid or not.
        if isinstance(func_obj, sqlalc.sql.elements.Over) or \
                isinstance(func_obj, sqlalc.sql.elements.WithinGroup):
            func_name = func_obj.element.name
        else:
            func_name = func_obj.name
        self.__validate_operation(func_name, describe_op=describe_op, **kwargs)

        # Add self to original expression lists.
        self.original_expressions.append(self)

        # Set _SQLColumnExpression type
        new_expression_type = _get_function_expression_type(func_obj, self.expression, **kwargs)
        columnExpression = _SQLColumnExpression(func_obj, type=new_expression_type)
        if describe_op:
            columnExpression = columnExpression.cast(NUMBER())
        return columnExpression

    @collect_queryband(arg_name="python_func_name", prefix="DFC")
    def __process_column_expression(self, func_name, *args, **kwargs):
        """
        Description:
            Function to process the aggregate expression. This function first
            checks the argument types passed to aggregate function is expected
            or not. If the argument types are expected, then this function combines
            positional arguments and keyword arguments to positional arguments,
            and then pass to the sql aggregate function.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the aggregate function.
                Types: str

            args:
                Optional Argument.
                Specifies the positional arguments to be passed to the aggregate function.
                Types: Tuple

            kwargs:
                Optional Argument.
                Specifies the keyword arguments to be passed to the aggregate function.
                Types: Dictionary

        RETURNS:
            An _SQLColumnExpression.

        EXAMPLES:
            # Create a Window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            df.Feb.__process_column_expression("corr", df.Feb.Mar)
        """

        from teradataml.dataframe.sql_function_parameters import SQL_AGGREGATE_FUNCTION_ADDITIONAL_PARAMETERS, \
            SQL_FUNCTION_ADDITIONAL_PARAMETERS, SINGLE_QUOTE_FUNCTIONS
        from teradataml.common.utils import UtilFuncs

        func_params = []
        if func_name in SQL_AGGREGATE_FUNCTION_ADDITIONAL_PARAMETERS:
            func_params = SQL_AGGREGATE_FUNCTION_ADDITIONAL_PARAMETERS.get(func_name)
        elif func_name in SQL_FUNCTION_ADDITIONAL_PARAMETERS:
            func_params = SQL_FUNCTION_ADDITIONAL_PARAMETERS.get(func_name)

        # Validation should be done against user passed function name i.e., on
        # Python function name, not on SQL function name.
        python_func_name = kwargs.pop("python_func_name")

        # If the call is from DataFrame, i.e., df.col.aggregate_function(),
        # then argument check would have happened at DataFrame itself. So,
        # argument type check can be skipped and all the function parameters will
        # be available in kwargs.
        if kwargs.get("call_from_df"):
            kw = kwargs
        else:
            # Validate the arguments before proceeding further and convert the
            # positional arguments and keyword arguments to keyword arguments.
            kw = _validate_unimplemented_function(python_func_name, func_params, *args, **kwargs)

        args_ = tuple()
        awu_matrix = []
        for func_param in func_params:
            arg = kw[func_param["arg_name"]]
            # If default_value available, then parameter is Optional. For Optional
            # parameter, 3rd argument in "awu_matrix" should be True.
            is_optional = "default_value" in func_param
            awu_matrix.append([func_param["arg_name"],
                               arg,
                               is_optional,
                               func_param["exp_types"]]
                              )


            arg = UtilFuncs._as_list(arg)

            expression = lambda col: text(col) if isinstance(col, str) else col

            if func_name in SINGLE_QUOTE_FUNCTIONS:
                # Certain string functions, require the str argument to be quoted so that it is
                # treated as a str in sql query.
                expression = lambda col: '{0}'.format(text(col)) if isinstance(col, str) else col

            for a in arg:
                args_ = args_ + (expression(a), )

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        func_obj = getattr(func, func_name)

        return self.__generate_function_call_object(func_obj, *args_, **kwargs)

    def __getattr__(self, func_name):
        """
        DESCRIPTION:
            Magic Method to call the corresponding aggregate function.

        PARAMETERS:
            func_name:
                Required Argument.
                Name of the aggregate function.
                Types: str

        RETURNS:
            A function, which actually process the corresponding aggregate function.

        EXAMPLES:
            # Create a window from a teradataml DataFrame.
            from teradataml import *
            load_example_data("dataframe","sales")
            df = DataFrame.from_table('sales')
            df.Feb.corr(df.Feb.Mar)
        """
        # Check aggregate function is available or not. If available, process the corresponding
        # function. Else, let python decide what to do, using __getattribute__.
        sql_func_name = ""
        if func_name in SQLFunctionConstants.AGGREGATE_FUNCTION_MAPPER.value:
            sql_func_name = SQLFunctionConstants.AGGREGATE_FUNCTION_MAPPER.value.get(func_name)
        else:
            sql_func_name = SQLFunctionConstants.SQL_FUNCTION_MAPPER.value.get(func_name)

        if not sql_func_name:
            return self.__getattribute__(func_name)

        return lambda *args, **kwargs:\
            self.__process_column_expression(sql_func_name, *args, python_func_name=func_name, **kwargs)

    @collect_queryband(queryband="DFC_count")
    def count(self, distinct=False, skipna=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the number of values in a column.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            skipna:
                Optional Argument.
                Specifies a flag that decides whether to skip null values or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the count of the values in 'gpa' column.
            # Execute count() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> count_column = admissions_train.gpa.count()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, count_=count_column)
            >>> df
               count_
            0      40
            >>>

            # Example 2: Get the count of the distinct values in 'gpa' column
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute count() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> count_column = admissions_train.gpa.count(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(count_=count_column)
            >>> df
              programming  count_
            0    Advanced      15
            1      Novice      11
            2    Beginner      11
            >>>
        """
        return self.__generate_function_call_object(func.count, distinct=distinct, skipna=skipna, **kwargs)

    @collect_queryband(queryband="DFC_kurtosis")
    def kurtosis(self, distinct=False, **kwargs):
        """
        DESCRIPTION:
            Function returns kurtosis value for a column.
            Kurtosis is the fourth moment of the distribution of the standardized
            (z) values. It is a measure of the outlier (rare, extreme observation)
            character of the distribution as compared with the normal, Gaussian
            distribution.
                * The normal distribution has a kurtosis of 0.
                * Positive kurtosis indicates that the distribution is more
                  outlier-prone than the normal distribution.
                * Negative kurtosis indicates that the distribution is less
                  outlier-prone than the normal distribution.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the kurtosis of the values in 'gpa' column.
            # Execute kurtosis() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> kurtosis_column = admissions_train.gpa.kurtosis()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, kurtosis_=kurtosis_column)
            >>> df
               kurtosis_
            0   4.052659
            >>>

            # Example 2: Get the kurtosis of the distinct values in 'gpa' column
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute kurtosis() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> kurtosis_column = admissions_train.gpa.kurtosis(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(kurtosis_=kurtosis_column)
            >>> df
              programming  kurtosis_
            0    Advanced   8.106762
            1      Novice   1.420745
            2    Beginner   5.733691
            >>>
        """
        return self.__generate_function_call_object(func.kurtosis, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_first")
    def first(self, **kwargs):
        """
        DESCRIPTION:
            Function returns oldest value, determined by the timecode, for each group
            in a column.
            Note:
                This can only be used as Time Series Aggregate function.

        PARAMETERS:
            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            >>> # Load the example datasets.
            ... load_example_data("dataframe", ["ocean_buoys"])

            >>> # Create the required DataFrames.
            ... # DataFrame on non-sequenced PTI table
            ... ocean_buoys = DataFrame("ocean_buoys")

            >>> ocean_buoys_grpby1 = ocean_buoys.groupby_time(timebucket_duration="2cd",
            ...                                               value_expression="buoyid", fill="NULLS")

            >>> ocean_buoys_grpby1.temperature.first()
        """
        return self.__generate_function_call_object(func.first)

    @collect_queryband(queryband="DFC_last")
    def last(self, **kwargs):
        """
        DESCRIPTION:
            Function returns newest value, determined by the timecode, for each group
            in a column.
            Note:
                This can only be used as Time Series Aggregate function.

        PARAMETERS:
            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            >>> # Load the example datasets.
            ... load_example_data("dataframe", ["ocean_buoys"])

            >>> # Create the required DataFrames.
            ... # DataFrame on non-sequenced PTI table
            ... ocean_buoys = DataFrame("ocean_buoys")

            >>> ocean_buoys_grpby1 = ocean_buoys.groupby_time(timebucket_duration="2cd",
            ...                                               value_expression="buoyid", fill="NULLS")

            >>> ocean_buoys_grpby1.temperature.last()
        """
        return self.__generate_function_call_object(func.last)

    @collect_queryband(queryband="DFC_mad")
    def mad(self, constant_multiplier=None, **kwargs):
        """
        DESCRIPTION:
            Function returns the median of the set of values defined as the
            absolute value of the difference between each value and the median
            of all values in each group.

            Formula for computing MAD is as follows:
                MAD = b * Mi(|Xi - Mj(Xj)|)

                Where,
                    b       = Some numeric constant. Default value is 1.4826.
                    Mj(Xj)  = Median of the original set of values.
                    Xi      = The original set of values.
                    Mi      = Median of absolute value of the difference between
                              each value in Xi and the Median calculated in Mj(Xj).

            Note:
                1. This function is valid only on columns with numeric types.
                2. Null values are not included in the result computation.
                3. This can only be used as Time Series Aggregate function.

        PARAMETERS:
            constant_multiplier:
                Optional Argument.
                Specifies a numeric values to be used as constant multiplier
                (b in the above formula). It should be any numeric value
                greater than or equal to 0.
                Note:
                    When this argument is not used, Vantage uses 1.4826 as
                    constant multiplier.
                Default Values: None
                Types: int or float

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            >>> # Load the example datasets.
            ... load_example_data("dataframe", ["ocean_buoys", "ocean_buoys_seq", "ocean_buoys_nonpti"])

            # Example 1: Calculate Median Absolute Deviation for all columns over 1 calendar day of
            #            timebucket duration. Use default constant multiplier.
            #            No need to pass any arguments.

            >>> # Create the required DataFrames.
            ... # DataFrame on non-sequenced PTI table
            ... ocean_buoys = DataFrame("ocean_buoys")

            >>> ocean_buoys_grpby1 = ocean_buoys.groupby_time(timebucket_duration="1cd",value_expression="buoyid", fill="NULLS")
            >>> ocean_buoys_grpby1.temperature.mad()

            # Example 2: Calculate MAD values using 2 as constant multiplier for all the columns
            #            in ocean_buoys_seq DataFrame on sequenced PTI table.

            >>> # DataFrame on sequenced PTI table
            ... ocean_buoys_seq = DataFrame("ocean_buoys_seq")

            >>> ocean_buoys_seq_grpby1 = ocean_buoys_seq.groupby_time(timebucket_duration="CAL_DAYS(2)", value_expression="buoyid", fill="NULLS")
            >>> constant_multiplier_columns = {2: "*"}
            >>> ocean_buoys_seq_grpby1.temperature.mad(constant_multiplier_columns)

        """
        if constant_multiplier:
            func_obj = func.mad(constant_multiplier, self.expression)
        else:
            func_obj = func.mad(self.expression)
        return self.__process_function_call_object(func_obj)

    @collect_queryband(queryband="DFC_max")
    def max(self, distinct=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the maximum value for a column.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the maximum value in 'gpa' column.
            # Execute max() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> max_column = admissions_train.gpa.max()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, max_=max_column)
            >>> df
               max_
            0   4.0
            >>>

            # Example 2: Get the maximum value from the distinct values in 'gpa' column
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute max() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> max_column = admissions_train.gpa.max(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(max_=max_column)
            >>> df
              programming  max_
            0    Beginner   4.0
            1    Advanced   4.0
            2      Novice   4.0
            >>>
        """
        return self.__generate_function_call_object(func.max, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_mean")
    def mean(self, distinct=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the average value for a column.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the mean value of 'gpa' column.
            # Execute mean() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> mean_column = admissions_train.gpa.mean()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, mean_=mean_column)
            >>> df
                mean_
            0  3.54175
            >>>

            # Example 2: Get the mean of the distinct values in 'gpa' column
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute mean() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> mean_column = admissions_train.gpa.mean(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(mean_=mean_column)
            >>> df
              programming     mean_
            0    Beginner  3.651818
            1    Advanced  3.592667
            2      Novice  3.294545
            >>>
        """
        # TODO:: Validate if below lines of code is needed or not.
        if self.type in [INTEGER, DECIMAL]:
            return _SQLColumnExpression(self).cast(FLOAT).mean()

        return self.__generate_function_call_object(func.avg, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_median")
    def median(self, distinct=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the median value for a column.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the median value of 'gpa' column.
            # Execute median() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> median_column = admissions_train.gpa.median()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, median_=median_column)
            >>> df
               min_
            0  3.69

            # Example 2: Get the median of the distinct values in 'gpa' column.
            # Execute median() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> median_column = admissions_train.gpa.median(distict=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, median_=median_column)
            >>> df
               median_
            0     3.69

            # Example 3: Get the median value in 'gpa' column for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute median() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> median_column = admissions_train.gpa.median()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(median_=median_column)
            >>> df
              programming  median_
            0    Advanced     3.76
            1      Novice     3.52
            2    Beginner     3.75
            >>>
        """
        return self.__generate_function_call_object(func.median, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_min")
    def min(self, distinct=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the minimum value for a column.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the minimum value in 'gpa' column.
            # Execute min() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> min_column = admissions_train.gpa.min()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, min_=min_column)
            >>> df
               min_
            0  1.87

            # Example 2: Get the minimum value from the distinct values in 'gpa' column
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute min() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> min_column = admissions_train.gpa.min(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(min_=min_column)
            >>> df
              programming  min_
            0    Advanced  1.98
            1      Novice  1.87
            2    Beginner  2.65
            >>>
        """
        return self.__generate_function_call_object(func.min, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_mode")
    def mode(self, **kwargs):
        """
        DESCRIPTION:
            Function to get the mode value for a column.
            Note:
                This can only be used as Time Series Aggregate function.

        PARAMETERS:
            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            >>> # Load the example datasets.
            ... load_example_data("dataframe", ["ocean_buoys", "ocean_buoys_seq", "ocean_buoys_nonpti"])

            # Example 1: Executing mode function on DataFrame column created on non-sequenced PTI table.
            >>> # Create the required DataFrames.
            ... # DataFrame on non-sequenced PTI table
            ... ocean_buoys = DataFrame("ocean_buoys")

            >>> ocean_buoys_grpby1 = ocean_buoys.groupby_time(timebucket_duration="10m",
            ...                                               value_expression="buoyid", fill="NULLS")
            >>> ocean_buoys_grpby1.temperature.mode()

        """
        return self.__generate_function_call_object(func.mode)

    @collect_queryband(queryband="DFC_percentile")
    def percentile(self, percentile, distinct=False, interpolation="LINEAR",
                   as_time_series_aggregate=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the percentile values for a column.

        PARAMETERS:
            percentile:
                Required Argument.
                Specifies the desired percentile value to calculate.
                It should be between 0 and 1, both inclusive.
                Types: float

            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Note: "distinct" is insignificant if percentile is calculated
                      as regular aggregate i.e., "as_time_series_aggregate" is
                      set to False.
                Default Values: False
                Types: bool

            interpolation:
                Optional Argument.
                Specifies the interpolation type to use to interpolate the result value when the
                desired result lies between two data points.
                The desired result lies between two data points, i and j, where i<j. In this case,
                the result is interpolated according to the permitted values.
                Permitted Values for time series aggregate:
                    * LINEAR: Linear interpolation.
                        The result value is computed using the following equation:
                            result = i + (j - i) * (di/100)MOD 1
                        Specify by passing "LINEAR" as string to this parameter.
                    * LOW: Low value interpolation.
                        The result value is equal to i.
                        Specify by passing "LOW" as string to this parameter.
                    * HIGH: High value interpolation.
                        The result value is equal to j.
                        Specify by passing "HIGH" as string to this parameter.
                    * NEAREST: Nearest value interpolation.
                        The result value is i if (di/100 )MOD 1 <= .5; otherwise, it is j.
                        Specify by passing "NEAREST" as string to this parameter.
                    * MIDPOINT: Midpoint interpolation.
                         The result value is equal to (i+j)/2.
                         Specify by passing "MIDPOINT" as string to this parameter.
                Permitted Values for regular aggregate:
                    * LINEAR: Linear interpolation.
                        Percentile is calculated after doing linear interpolation.
                    * None:
                        Percentile is calculated with no interpolation.
                Default Values: "LINEAR"
                Types: str

            as_time_series_aggregate:
                Optional Argument.
                Specifies a flag that decides whether percentiles are being calculated
                as regular aggregate or time series aggregate. When it is set to False, it'll
                be executed as regular aggregate, if set to True; then it is used as time series
                aggregate.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", ["admissions_train", "ocean_buoys"])
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>
            # Create a DataFrame on 'ocean_buoys' table.
            >>> ocean_buoys = DataFrame("ocean_buoys")
            >>> ocean_buoys
                                   TD_TIMECODE  salinity  temperature
            buoyid
            1       2014-01-06 09:02:25.122200        55         78.0
            44      2014-01-06 10:00:24.333300        55         43.0
            44      2014-01-06 10:00:25.122200        55         43.0
            2       2014-01-06 21:01:25.122200        55         80.0
            2       2014-01-06 21:03:25.122200        55         82.0
            0       2014-01-06 08:00:00.000000        55         10.0
            0       2014-01-06 08:08:59.999999        55          NaN
            0       2014-01-06 08:09:59.999999        55         99.0
            2       2014-01-06 21:02:25.122200        55         81.0
            44      2014-01-06 10:00:24.000000        55         43.0
            >>>

            # Example 1: Calculate the 25th percentile of temperature in ocean_buoys table,
            #            with LINEAR interpolation.
            >>> ocean_buoys_grpby1 = ocean_buoys.groupby_time(timebucket_duration="10m", value_expression="buoyid", fill="NULLS")
            >>> ocean_buoys_grpby1.assign(True, temperature_percentile_=ocean_buoys_grpby1.temperature.percentile(0.25))
               temperature_percentile_
            0                       43
            >>>

            # Example 2: Calculate the 35th percentile of gpa in admissions_train table,
            #            with LINEAR interpolation.
            >>> admissions_train_grpby = admissions_train.groupby("admitted")
            >>> admissions_train_grpby.assign(True, percentile_cont_=admissions_train_grpby.gpa.percentile(0.35))
               admitted  percentile_cont_
            0         0             3.460
            1         1             3.565
            >>>

            # Example 3: Calculate the 45th percentile of gpa in admissions_train table,
            #            with no interpolation.
            >>> admissions_train_grpby = admissions_train.groupby("admitted")
            >>> admissions_train_grpby.assign(True, percentile_disc_=admissions_train_grpby.gpa.percentile(0.35, interpolation=None))
               admitted  percentile_disc_
            0         0              3.46
            1         1              3.57
            >>>
        """
        # Argument validations
        awu_matrix = []
        awu_matrix.append(["percentile", percentile, False, (int, float)])
        awu_matrix.append(["distinct", distinct, True, (bool)])

        # "interpolation" expected values are different for regular aggregates
        # and time series aggregates. So, creating a seperate validation
        # parameters.
        if as_time_series_aggregate:
            awu_matrix.append(["interpolation", interpolation, True, (str), True,
                              ["LINEAR", "LOW", "HIGH", "NEAREST", "MIDPOINT"]])
        else:
            awu_matrix.append(["interpolation", interpolation, True, (str, type(None)), True,
                               ["LINEAR", None]])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        _Validators._validate_argument_range(
            percentile, "percentile", lbound=0, ubound=1, lbound_inclusive=True, ubound_inclusive=True)

        # Performing percentile for Regular Aggregate.
        # SQL Equivalent: """percentile_cont({}) within group order by {}"""
        if not as_time_series_aggregate:

            # Since default value for interpolation is LINEAR, Perform
            # PERCENTILE_CONT by default. If no interpolation specified, then
            # perform PERCENTILE_DISC.
            percentile_func = func.percentile_cont
            if interpolation is None:
                percentile_func = func.percentile_disc

            order_by = self.expression
            # Cast order by column to Number for Describe operation.
            if kwargs.get("describe_op"):
                order_by = self.cast(NUMBER()).expression

            return self.__generate_function_call_object(
                percentile_func, percentile, within_group={"order_by": order_by}, **kwargs)

        # Performing percentile for Time Series Aggregate.
        # SQL Equivalent: """percentile([DISTINCT] column, percentile [interpolation])"""
        return self.__generate_function_call_object(
            func.percentile, percentile*100, text(interpolation), distinct=distinct)

    @collect_queryband(queryband="DFC_skew")
    def skew(self, distinct=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the skewness of the distribution for a column.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Calculate the skewness of the distribution for values in 'gpa' column.
            # Execute skew() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> skew_column = admissions_train.gpa.skew()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, skew_=skew_column)
            >>> df
                  skew_
            0 -2.058969
            >>>

            # Example 2: Calculate the skewness of the distribution for distinct values in
            #            'gpa' column for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute skew() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> skew_column = admissions_train.gpa.skew(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(skew_=skew_column)
            >>> df
              programming     skew_
            0    Beginner -2.197710
            1    Advanced -2.647604
            2      Novice -1.459620
            >>>
        """
        return self.__generate_function_call_object(func.skew, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_sum")
    def sum(self, distinct=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the sum of values in a column.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Calculate the sum of the values in 'gpa' column.
            # Execute sum() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> sum_column = admissions_train.gpa.sum()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, sum_=sum_column)
            >>> df
                sum_
            0  141.67
            >>>

            # Example 2: Calculate the sum of the distinct values in'gpa' column
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute sum() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> sum_column = admissions_train.gpa.sum(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(sum_=sum_column)
            >>> df
              programming   sum_
            0    Beginner  40.17
            1    Advanced  53.89
            2      Novice  36.24
            >>>
        """
        return self.__generate_function_call_object(func.sum, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_std")
    def std(self, distinct=False, population=False, **kwargs):
        """
        DESCRIPTION:
            Function to get the sample or population standard deviation for values in a column.
            The standard deviation is the second moment of a distribution.
                * For a sample, it is a measure of dispersion from the mean of that sample.
                * For a population, it is a measure of dispersion from the mean of that population.
            The computation is more conservative for the population standard deviation
            to minimize the effect of outliers on the computed value.
            Note:
                1. When there are fewer than two non-null data points in the sample used
                   for the computation, then std returns None.
                2. Null values are not included in the result computation.
                3. If data represents only a sample of the entire population for the
                   column, Teradata recommends to calculate sample standard deviation,
                   otherwise calculate population standard deviation.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            population:
                Optional Argument.
                Specifies whether to calculate standard deviation on entire population or not.
                Set this argument to True only when the data points represent the complete
                population. If your data represents only a sample of the entire population for the
                column, then set this variable to False, which will compute the sample standard
                deviation. As the sample size increases, even though the values for sample
                standard deviation and population standard deviation approach the same number,
                you should always use the more conservative sample standard deviation calculation,
                unless you are absolutely certain that your data constitutes the entire population
                for the column.
                Default Value: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the sample standard deviation for values in 'gpa' column.
            # Execute std() function on teradataml DataFrameColumn to generate the ColumnExpression.
            >>> std_column = admissions_train.gpa.std()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, std_=std_column)
            >>> df
                   std_
            0  0.513764
            >>>

            # Example 2: Get the population standard deviation for values in 'gpa' column.
            # Execute std() function on teradataml DataFrameColumn to generate the ColumnExpression.
            # To calculate population standard deviation we must set population=True.
            >>> std_column = admissions_train.gpa.std(population=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, std_=std_column)
            >>> df
                   std_
            0  0.507301
            >>>

            # Example 3: Get the sample standard deviation for distinct values in 'gpa' column
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute std() function on teradataml DataFrameColumn to generate the ColumnExpression.
            # We will consider DISTINCT values for the columns while calculating the standard deviation value.
            >>> std_column = admissions_train.gpa.std(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(std_=std_column)
            >>> df
              programming      std_
            0    Beginner  0.372151
            1    Advanced  0.502415
            2      Novice  0.646736
            >>>
        """
        if population:
            return self.__generate_function_call_object(func.stddev_pop, distinct=distinct, **kwargs)
        else:
            return self.__generate_function_call_object(func.stddev_samp, distinct=distinct, **kwargs)

    @collect_queryband(queryband="DFC_unique")
    def unique(self, **kwargs):
        """
        DESCRIPTION:
            Function to get the number of unique values in a column.

        PARAMETERS:
            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame('admissions_train')
            >>> s1 = df.select(['gpa']).squeeze()
            >>> s1
            0    4.00
            1    3.57
            2    3.44
            3    1.98
            4    4.00
            5    3.95
            6    2.33
            7    3.46
            8    3.00
            9    2.65

            >>> s1.unique()
            0    3.65
            1    1.98
            2    3.55
            3    3.71
            4    3.13
            5    1.87
            6    3.44
            7    4.00
            8    3.96
            9    3.46
            Name: gpa, dtype: float64
        """
        # Check if it is describe operation or not.
        describe_op = False
        if "describe_op" in kwargs.keys():
            describe_op = kwargs["describe_op"]

        if describe_op:
            # If a describe operation function name is used as "unique" to retrieve unsupported types.
            self.__validate_operation(name="unique", describe_op=describe_op)
        return self.count(True)

    @collect_queryband(queryband="DFC_var")
    def var(self, distinct=False, population=False, **kwargs):
        """
        DESCRIPTION:
            Returns sample or population variance for values in a column.
                * The variance of a population is a measure of dispersion from the
                  mean of that population.
                * The variance of a sample is a measure of dispersion from the mean
                  of that sample. It is the square of the sample standard deviation.
            Note:
                1. When there are fewer than two non-null data points in the sample used
                   for the computation, then var returns None.
                2. Null values are not included in the result computation.
                3. If data represents only a sample of the entire population for the
                   columns, Teradata recommends to calculate sample variance,
                   otherwise calculate population variance.

        PARAMETERS:
            distinct:
                Optional Argument.
                Specifies a flag that decides whether to consider duplicate values in
                a column or not.
                Default Values: False
                Types: bool

            population:
                Optional Argument.
                Specifies whether to calculate variance on entire population or not.
                Set this argument to True only when the data points represent the complete
                population. If your data represents only a sample of the entire population
                for the columns, then set this variable to False, which will compute the
                sample variance. As the sample size increases, even though the values for
                sample variance and population variance approach the same number, but you
                should always use the more conservative sample standard deviation calculation,
                unless you are absolutely certain that your data constitutes the entire
                population for the columns.
                Default Value: False
                Types: bool

            kwargs:
                Specifies optional keyword arguments.

        RETURNS:
             ColumnExpression, also known as, teradataml DataFrameColumn.

        NOTES:
             * One must use DataFrame.assign() when using the aggregate functions on
               ColumnExpression, also known as, teradataml DataFrameColumn.
             * One should always use "drop_columns=True" in DataFrame.assign(), while
               running the aggregate operation on teradataml DataFrame.
             * "drop_columns" argument in DataFrame.assign() is ignored, when aggregate
               function is operated on DataFrame.groupby().

        RAISES:
            RuntimeError - If column does not support the aggregate operation.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>
            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Get the sample variance for values in 'gpa' column.
            # Execute var() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> var_column = admissions_train.gpa.var()
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, var_=var_column)
            >>> df
                   var_
            0  0.263953

            # Example 2: Get the population variance for values in 'gpa' column.
            # Execute var() function on teradataml DataFrameColumn to generate the ColumnExpression.
            # To calculate population variance we must set population=True.
            >>> var_column = admissions_train.gpa.var(population=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df = admissions_train.assign(True, var_=var_column)
            >>> df
                   var_
            0  0.257354
            >>>

            # Example 3: Get the sample variance for distinct values in 'gpa' column.
            #            for each level of programming.
            # Note:
            #   When assign() is run after DataFrame.groupby(), the function ignores
            #   the "drop_columns" argument.
            # Execute var() function using teradataml DataFrameColumn to generate the ColumnExpression.
            >>> var_column = admissions_train.gpa.var(distinct=True)
            # Pass the generated ColumnExpression to DataFrame.assign(), to run and produce the result.
            >>> df=admissions_train.groupby("programming").assign(var_=var_column)
            >>> df
              programming      var_
            0    Advanced  0.252421
            1      Novice  0.418267
            2    Beginner  0.138496
            >>>
        """
        if population:
            return self.__generate_function_call_object(func.var_pop, distinct=distinct, **kwargs)
        else:
            return self.__generate_function_call_object(func.var_samp, distinct=distinct, **kwargs)


class _SQLColumnExpression(_LogicalColumnExpression,
                           _ArithmeticColumnExpression,
                           _SeriesColumnExpression,
                           _AggregateColumnExpresion):
    """
    _SQLColumnExpression is used to build Series/Column manipulations into SQL.
    It represents a column from a Table or an expression involving some operation
    between columns and other literals.

    These objects are created from _SQLTableExpression or from operations
    involving other _SQLColumnExpressions.

    They behave like sqlalchemy.Column objects when accessed from the SQLTableExpression.
    Thus you can access certain common attributes (decorated with property) specified by
    the ColumnExpression interface. Otherwise, the attributes refer to expressions.
    In this case, None is returned if an attribute is not found in the expression.

    This class is internal.
    """

    def __init__(self, expression, **kw):
        """
        Initialize the ColumnExpression

        PARAMETERS:
            expression : Required Argument.
                         A sqlalchemy.ClauseElement instance.

        """
        if isinstance(expression, str):
            expression = literal_column(expression)
        self.kw = kw
        self.expression = expression
        self.type = kw.get("type", expression.type if expression is not None else kw.get("udf_type"))
        # Initial ColumnExpression has only one dataframe and hence
        # __has_multiple_dataframes = False.
        # eg: df1.col1, df2.col2
        self.__has_multiple_dataframes = False
        self.__names = []
        self._udf = kw.get("udf", None)
        self._udf_args = kw.get("udf_args", None)
        self._env_name = kw.get("env_name", None)
        self._delimiter = kw.get("delimiter", None)
        self._quotechar = kw.get("quotechar", None)
        self._udf_script = kw.get("udf_script", None)
        self.alias_name = self.compile() if (self._udf or self._udf_script) is None else None
        self._debug = kw.get("debug", False)

    @property
    def expression(self):
        """
        A reference to the underlying column expression.

        PARAMETERS:
            None

        RETURNS:
            sqlalchemy.sql.elements.ColumnClause

        RAISE:
            None

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df.gpa.expression
            Column('gpa', FLOAT(), table=<admissions_train>, nullable=False)
        """
        return self.__expression

    @expression.setter
    def expression(self, expression):
        """
        Sets a reference to the underlying column expression.
        """
        self.__expression = expression

    def get_flag_has_multiple_dataframes(self):
        """
        Returns whether the underlying column expression uses multiple dataframes or not.
        If column expression has only one dataframe, this function returns False; otherwise True.
        """
        return self.__has_multiple_dataframes

    def set_flag_has_multiple_dataframes(self, has_multiple_dataframes):
        """
        Sets __has_multiple_dataframes True or False based on the argument has_multiple_dataframes.
        """
        if (not isinstance(has_multiple_dataframes, bool)):
            raise ValueError('_SQLColumnExpression requires a boolean type argument '
                         'has_multiple_dataframes')
        self.__has_multiple_dataframes = has_multiple_dataframes

    @property
    def original_column_expr(self):
        """
        Returns a list of original ColumnExpression.
        """
        return self.original_expressions

    @original_column_expr.setter
    def original_column_expr(self, expression):
        """
        Sets the original_column_expr property to a list of ColumnExpressions.
        """
        if not isinstance(expression, list):
            raise ValueError('_SQLColumnExpression requires a list type argument '
                         'expression')
        self.original_expressions = expression

    @property
    def type(self):
        """
        Returns the underlying sqlalchemy type of the current expression.

        PARAMETERS:
            None

        RETURNS:
            teradatasqlalchemy.types

        RAISE:
            None

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df.gpa.type
            FLOAT()
        """
        if self._type is not None:
            return self._type
        else:
            return self.expression.type

    @type.setter
    def type(self, value):
        """
        Setter for type property of _SQLColumnExpression.
        Allows to set the column expression type.
        """
        if value is None:
            self._type = self.expression.type
        else:
            self._type = value

        from teradataml.dataframe.vantage_function_types import \
            _retrieve_function_expression_type

        # If user passes a sqlalchemy expression, then teradataml do not know the type and
        # so self.kw do not have the expected type. Only then, the type should be derived
        # from  _retrieve_function_expression_type. Other wise, do not do any thing.
        #   Ex - when expression is res_col=df[col].sum(), teradataml is intelligent enough to
        #        predict the output type and corresponding type will be available in self.kw.
        #        If expression is func.sum(df[col].expression), teradataml do not know the type
        #        so retrieve it using _retrieve_function_expression_type
        if isinstance(self.expression, sqlalc.sql.functions.sum) and "type" not in self.kw:
            self._type = _retrieve_function_expression_type(self.expression)

        if not isinstance(self._type, _TDType):
            # If value is either SQLAlchemy NullType or any of SQLAlchemy type, then retrieve the
            # type for function expression from SQLAlchemy expression and input arguments.
            # sqlalc.sql.type_api.TypeEngine is grand parent class to all SQLAlchemy data types.
            # Hence checking if self._type is instance of that class.
            if isinstance(self._type, sqlalc.sql.sqltypes.NullType) or \
                    isinstance(self._type, sqlalc.sql.type_api.TypeEngine):
                if isinstance(self.expression, sqlalc.sql.elements.Over) \
                        or isinstance(self.expression, sqlalc.sql.functions.Function):
                    self._type = _retrieve_function_expression_type(self.expression)

    @property
    def name(self):
        """
        Returns the underlying name attribute of self.expression or None
        if the expression has no name. Note that the name may also refer to
        an alias or label() in sqlalchemy

        PARAMETERS:
            None

        RETURNS:
            str

        RAISE:
            None

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df.gpa.name
            gpa
        """
        return getattr(self.expression, 'name', None)

    @property
    def table(self):
        """
        Returns the underlying table attribute of the sqlalchemy.Column

        PARAMETERS:
            None

        RETURNS:
            str

        RAISE:
            None

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df.gpa.table
            Table('admissions_train', MetaData(bind=Engine(teradatasql://alice:***@sdt61582.labs.teradata.com)),
            Column('id', INTEGER(), table=<admissions_train>, nullable=False), Column('masters', VARCHAR(length=5,
            charset='LATIN'), table=<admissions_train>, nullable=False), Column('gpa', FLOAT(), table=<admissions_train>,
            nullable=False), Column('stats', VARCHAR(length=30, charset='LATIN'), table=<admissions_train>, nullable=False),
            Column('programming', VARCHAR(length=30, charset='LATIN'), table=<admissions_train>, nullable=False),
            Column('admitted', INTEGER(), table=<admissions_train>, nullable=False), schema=None)

        """
        return getattr(self.expression, 'table', None)

    def compile(self, *args, **kw):
        """
        Calls the compile method of the underlying sqlalchemy.Column
        """
        kw_new = dict({'dialect': td_dialect(),
                       'compile_kwargs':
                           {
                                'include_table': False,
                                'literal_binds': True
                           }
                       })
        if len(kw) != 0:
            kw_new.update(kw)
        return str(self.expression.compile(*args, **kw_new))

    def compile_label(self, label):
        """
        DESCRIPTION:
            Compiles expression with label, by calling underlying sqlalchemy methods.

        PARAMETERS:
            label:
                Required Argument.
                Specifies the label to be used to alias the compiled expression.
                Types: str

        RAISES:
            None.

        RETURNS:
            string - compiled expression.

        EXAMPLES:
            self.compile_label("col1")
        """
        compiler = td_compiler(td_dialect(), None)
        aliased_expression = compiler.visit_label(self.expression.label(label),
                                                  within_columns_clause=True,
                                                  include_table=False,
                                                  literal_binds=True)
        return aliased_expression

    @collect_queryband(queryband="DFC_fillna")
    def fillna(self, value):
        """
        DESCRIPTION:
            Function replaces every occurrence of NA value in column
            with the "value". Use this function either to replace or remove
            NA from Column.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the replacement value for null values in the column.
                Types: str or int or float or ColumnExpression

        RAISES:
            TeradataMlException

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017

            # Example 1: Fill the null value in column 'Mar'
            #            with the the specified value.
            >>> df.assign(Mar = df.Mar.fillna(1))
                          Feb    Jan  Mar    Apr    datetime
            accounts
            Red Inc     200.0  150.0  140    NaN  04/01/2017
            Alpha Co    210.0  200.0  215  250.0  04/01/2017
            Yellow Inc   90.0    NaN    1    NaN  04/01/2017
            Jones LLC   200.0  150.0  140  180.0  04/01/2017
            Blue Inc     90.0   50.0   95  101.0  04/01/2017
            Orange Inc  210.0    NaN    1  250.0  04/01/2017
        """
        if isinstance(value, type(self)):
            value = value.expression
        return case_when((self.expression == None, value), else_=self.expression)

    @collect_queryband(queryband="DFC_concat")
    def concat(self, separator, *columns):
        """
        DESCRIPTION:
            Function to concatenate the columns with a separator.

        PARAMETERS:
            separator:
                Required Argument.
                Specifies the string to be used as a separator between two concatenated columns.
                Note:
                    This argument is ignored when no column is specified.
                Types: str

            columns:
                Optional Argument.
                Specifies the name(s) of the columns or ColumnExpression(s) to concat on.
                Types: str OR ColumnExpression OR ColumnExpressions

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>>

            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train = DataFrame("admissions_train")
            >>> admissions_train
               masters   gpa     stats programming  admitted
            id
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            15     yes  4.00  Advanced    Advanced         1
            38     yes  2.65  Advanced    Beginner         1
            5       no  3.44    Novice      Novice         0
            17      no  3.83  Advanced    Advanced         1
            34     yes  3.85  Advanced    Beginner         0
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            >>>

            # Example 1: Concatenate the columns "stats" and "programming" with out any seperator.
            >>> df = admissions_train.assign(concat_gpa_=admissions_train.stats.concat("", admissions_train.programming))
            >>> print(df)
                masters   gpa     stats programming  admitted        new_column
            id
            34     yes  3.85  Advanced    Beginner         0  AdvancedBeginner
            32     yes  3.46  Advanced    Beginner         0  AdvancedBeginner
            11      no  3.13  Advanced    Advanced         1  AdvancedAdvanced
            40     yes  3.95    Novice    Beginner         0    NoviceBeginner
            38     yes  2.65  Advanced    Beginner         1  AdvancedBeginner
            36      no  3.00  Advanced      Novice         0    AdvancedNovice
            7      yes  2.33    Novice      Novice         1      NoviceNovice
            26     yes  3.57  Advanced    Advanced         1  AdvancedAdvanced
            19     yes  1.98  Advanced    Advanced         0  AdvancedAdvanced
            13      no  4.00  Advanced      Novice         1    AdvancedNovice
            >>>

            # Example 2: Concatenate the columns "programming", "gpa" and "masters" with '_'.
            >>> df = admissions_train.assign(new_column=admissions_train.programming.concat("_", admissions_train.gpa, "masters"))
            >>> print(df)
               masters   gpa     stats programming  admitted                           new_column
            id
            34     yes  3.85  Advanced    Beginner         0  Beginner_ 3.85000000000000E 000_yes
            32     yes  3.46  Advanced    Beginner         0  Beginner_ 3.46000000000000E 000_yes
            11      no  3.13  Advanced    Advanced         1   Advanced_ 3.13000000000000E 000_no
            40     yes  3.95    Novice    Beginner         0  Beginner_ 3.95000000000000E 000_yes
            38     yes  2.65  Advanced    Beginner         1  Beginner_ 2.65000000000000E 000_yes
            36      no  3.00  Advanced      Novice         0     Novice_ 3.00000000000000E 000_no
            7      yes  2.33    Novice      Novice         1    Novice_ 2.33000000000000E 000_yes
            26     yes  3.57  Advanced    Advanced         1  Advanced_ 3.57000000000000E 000_yes
            19     yes  1.98  Advanced    Advanced         0  Advanced_ 1.98000000000000E 000_yes
            13      no  4.00  Advanced      Novice         1     Novice_ 4.00000000000000E 000_no
        """
        awu_matrix = []
        awu_matrix.append(["separator", separator, False, (str), False])
        for column in columns:
            awu_matrix.append(["columns", column, True, (str, ColumnExpression), True])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        get_expr = lambda col: col.expression if not isinstance(col, str) else getattr(self._parent_df, col).expression
        columns_ = [get_expr(self)]
        if columns:
            for column in columns:
                columns_ = columns_ + [separator, get_expr(column)]
        # Below condition is edge case condition for func.concat method,
        # It seems when last argument is ColumnExpression, i.e., df.column1+df.column2
        # it raises error so to handle that below condition is added.
        columns_.append("")

        return _SQLColumnExpression(func.concat(*columns_))

    @collect_queryband(queryband="DFC_cast")
    def cast(self, type_ = None, format = None, timezone = None):
        """
        DESCRIPTION:
            Apply the CAST SQL function to the column with the type specified.

            NOTE: This method can currently be used only with 'filter' and
                  'assign' methods of teradataml DataFrame.

        PARAMETERS:
            type_:
                Required Argument.
                Specifies a teradatasqlalchemy type or an object of a teradatasqlalchemy type
                that the column needs to be cast to.
                Default value: None
                Types: teradatasqlalchemy type or object of teradatasqlalchemy type

            format:
                Optional Argument.
                Specifies a variable length string containing formatting characters
                that define the display format for the data type.
                Formats can be specified for columns that have character, numeric, byte,
                DateTime, Period or UDT data types.
                Note:
                    * Teradata supports different formats. Look at 'Formats' section in
                      "SQL-Data-Types-and-Literals" in Vantage documentation for additional
                      details.
                Default value: None
                Types: str

            timezone:
                Optional Argument.
                Specifies the timezone string.
                Check "SQL-Date-and-Time-Functions-and-Expressions" in
                Vantage documentation for supported timezones.
                Type: ColumnExpression or str.

        RETURNS:
            ColumnExpression

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data("dataframe","admissions_train")
            >>> df = DataFrame('admissions_train')
            >>> df
               masters   gpa     stats programming  admitted
            id
            13      no  4.00  Advanced      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            19     yes  1.98  Advanced    Advanced         0
            15     yes  4.00  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            7      yes  2.33    Novice      Novice         1
            22     yes  3.46    Novice    Beginner         0
            36      no  3.00  Advanced      Novice         0
            38     yes  2.65  Advanced    Beginner         1
            >>> df.dtypes
            id               int
            masters          str
            gpa            float
            stats            str
            programming      str
            admitted         int

            >>> dataframe_dict = {"id": [100, 200,300],
            >>> "timestamp_col": ['1000-01-10 23:00:12-02:00', '2015-01-08 13:00:00+12:00', '2014-12-10 10:00:35-08:00'],
            >>> "timezone_col": ["GMT", "America Pacific", "GMT+10"]}
            >>> pandas_df = pd.DataFrame(dataframe_dict)
            >>> copy_to_sql(pandas_df, table_name = 'new_table', if_exists = 'replace')
            >>> df1 = DataFrame("new_table")
            >>> df1
            id              timestamp_col     timezone_col
            300  2014-12-10 10:00:35-08:00           GMT+10
            200  2015-01-08 13:00:00+12:00  America Pacific
            100  1000-01-10 23:00:12-02:00              GMT
            >>> df1.dtypes
            id               int
            timestamp_col    str
            timezone_col     str

            # Example 1: Let's try creating a new DataFrame casting 'id' column (of type INTEGER) to VARCHAR(5),
            #            an object of a teradatasqlalchemy type.
            >>> from teradatasqlalchemy import VARCHAR
            >>> new_df = df.assign(char_id = df.id.cast(type_=VARCHAR(5)))
            >>> new_df
               masters   gpa     stats programming  admitted char_id
            id
            5       no  3.44    Novice      Novice         0       5
            34     yes  3.85  Advanced    Beginner         0      34
            13      no  4.00  Advanced      Novice         1      13
            40     yes  3.95    Novice    Beginner         0      40
            22     yes  3.46    Novice    Beginner         0      22
            19     yes  1.98  Advanced    Advanced         0      19
            36      no  3.00  Advanced      Novice         0      36
            15     yes  4.00  Advanced    Advanced         1      15
            7      yes  2.33    Novice      Novice         1       7
            17      no  3.83  Advanced    Advanced         1      17
            >>> new_df.dtypes
            id               int
            masters          str
            gpa            float
            stats            str
            programming      str
            admitted         int
            char_id          str

            # Example 2:  Now let's try creating a new DataFrame casting 'id' column (of type INTEGER) to VARCHAR,
            #             a teradatasqlalchemy type.
            >>> new_df_2 = df.assign(char_id = df.id.cast(type_=VARCHAR))
            >>> new_df_2
               masters   gpa     stats programming  admitted char_id
            id
            5       no  3.44    Novice      Novice         0       5
            34     yes  3.85  Advanced    Beginner         0      34
            13      no  4.00  Advanced      Novice         1      13
            40     yes  3.95    Novice    Beginner         0      40
            22     yes  3.46    Novice    Beginner         0      22
            19     yes  1.98  Advanced    Advanced         0      19
            36      no  3.00  Advanced      Novice         0      36
            15     yes  4.00  Advanced    Advanced         1      15
            7      yes  2.33    Novice      Novice         1       7
            17      no  3.83  Advanced    Advanced         1      17
            >>> new_df_2.dtypes
            id               int
            masters          str
            gpa            float
            stats            str
            programming      str
            admitted         int
            char_id          str

            # Example 3: Let's try filtering some data with a match on a column cast to another type,
            #            an object of a teradatasqlalchemy type.
            >>> df[df.id.cast(VARCHAR(5)) == '1']
               masters   gpa     stats programming  admitted
            id
            1      yes  3.95  Beginner    Beginner         0

            # Example 4: Now let's try the same, this time using a teradatasqlalchemy type.
            >>> df[df.id.cast(VARCHAR) == '1']
               masters   gpa     stats programming  admitted
            id
            1      yes  3.95  Beginner    Beginner         0

            # Example 5: Let's try creating a new DataFrame casting 'timestamp_col' column (of type VARCHAR) to TIMESTAMP,
            #            using format.
            >>> new_df1 = df1.assign(new_col = df1.timestamp_col.cast(TIMESTAMP, format='Y4-MM-DDBHH:MI:SSBZ'))
            id              timestamp_col     timezone_col              new_col
            300  2014-12-10 10:00:35-08:00           GMT+10  2014-12-10 18:00:35
            200  2015-01-08 13:00:00+12:00  America Pacific  2015-01-08 01:00:00
            100  1000-01-10 23:00:12-02:00              GMT  1000-01-11 01:00:12
            >>> new_df1.tdtypes
            id                             int
            timestamp_col                  str
            timezone_col                   str
            new_col          datetime.datetime

            # Example 6: Let's try creating a new DataFrame casting 'id' column (of type INTEGER) to VARCHAR,
            #            using format.
            >>> new_df2 = df1.assign(new_col = df1.id.cast(VARCHAR, format='zzz.zz'))
            id              timestamp_col     timezone_col new_col
            300  2014-12-10 10:00:35-08:00           GMT+10  300.00
            200  2015-01-08 13:00:00+12:00  America Pacific  200.00
            100  1000-01-10 23:00:12-02:00              GMT  100.00
            >>> new_df2.dtypes
            id               int
            timestamp_col    str
            timezone_col     str
            new_col          str

            # Example 7: Let's try creating a new DataFrame casting 'timestamp_with_timezone' column (of type TIMESTAMP) to
            #            TIMESTAMP WITH TIMEZONE, with offset 'GMT+10'.
            >>> new_df3 = new_df1.assign(timestamp_with_timezone = new_df1.new_col.cast(TIMESTAMP(timezone=True), timezone='GMT+10'))
            id              timestamp_col     timezone_col              new_col         timestamp_with_timezone
            300  2014-12-10 10:00:35-08:00           GMT+10  2014-12-10 18:00:35  2014-12-11 04:00:35.000000+10:00
            200  2015-01-08 13:00:00+12:00  America Pacific  2015-01-08 01:00:00  2015-01-08 11:00:00.000000+10:00
            100  1000-01-10 23:00:12-02:00              GMT  1000-01-11 01:00:12  1000-01-11 11:00:12.000000+10:00
            >>> new_df3.dtypes
            id                                       int
            timestamp_col                            str
            timezone_col                             str
            new_col                    datetime.datetime
            timestamp_with_timezone    datetime.datetime
        """
        # Validating Arguments
        arg_type_matrix = []
        arg_type_matrix.append(["format", format , True, (str), True])
        arg_type_matrix.append(["timezone", timezone, True, (str, ColumnExpression, int, float), True])
        _Validators._validate_function_arguments(arg_type_matrix)

        # If type_ is None or not specified, raise an Exception
        if type_ is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.MISSING_ARGS, 'type_'),
                                      MessageCodes.MISSING_ARGS)

        # Check that the type_ is a valid teradatasqlalchemy type
        if not UtilFuncs._is_valid_td_type(type_):
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, 'type_',
                                                           'a valid teradatasqlalchemy type'),
                                      MessageCodes.UNSUPPORTED_DATATYPE)
        expression = func.cast(self.expression, type_=type_).label(self.name)
        if format or timezone:
            # Casting to VARCHAR or CHAR with format require this type of query
            # CAST((CAST (F1 AS FORMAT 'format_str')) AS [CHAR|VARCHAR])
            if isinstance(type_, (VARCHAR, CHAR)) or (isinstance(type_, type) and issubclass(type_, (VARCHAR, CHAR))):
                expression = func.cast(literal_column("""CAST({} AS FORMAT '{}')""".format(self.compile(), format)), type_=type_)
            else:
                # Compile _TDType to string
                type_compiler = td_type_compiler(td_dialect)
                type_expression = type_compiler.process(type_) if not isinstance(type_, type) else type_compiler.process(type_())
                # Create a query with format and timezone string
                # CAST(TIMESTAMP "column_name" AS "_TDType" FORMAT "format" AT TIMEZONE "timezone_str")
                format =  " FORMAT '{}'".format(format) if format else ""
                if timezone and isinstance(timezone, _SQLColumnExpression):
                    timezone = _SQLColumnExpression(literal_column(f' AT TIME ZONE {timezone.compile()}')).compile()
                elif timezone:
                    timezone = _SQLColumnExpression(literal_column(_SQLColumnExpression._timezone_string(timezone))).compile()
                else:
                    timezone = ""
                expression = literal_column("""CAST({} AS {}{}{})""".format(self.compile(), type_expression, timezone, format), type_=type_)
        return _SQLColumnExpression(expression)

    def __hash__(self):
        return hash(self.expression)

    def __dir__(self):
        # currently str is the only accessor
        # if we end up adding more, consider making this
        # list an instance attribute (i.e self._accessors) of the class
        accessors = ['str']
        attrs = {x for x in dir(type(self)) if not x.startswith('_') and x not in accessors}

        if isinstance(self.type, (CLOB, CHAR, VARCHAR)):
            return attrs | set(['str']) # str accessor is only visible for string-like columns

        return attrs

    # TODO - For future to enable execution of other functions with bulk exposure approach.
    '''
    def __getattr__(self, item):
        """
        Returns an attribute of the _SQLColumnExpression.

        PARAMETERS:
            name: the name of the attribute.

        RETURNS:
            _SQLColumnExpression

        EXAMPLES:
            df = DataFrame('table')
            df.column.lead()
        """
        # We can implement this logic in _SQLColumnExpression, that will allow
        # us to achieve "Generic Vantage SQL Function Support".
        # TODO::
        #   Add a check that skips executing Aggregate functions via this.
        return lambda *args, **kwargs: \
            self.__process_unimplemented_functions(item, *args, **kwargs)
    '''

    def _generate_vantage_function_call(self, func_name, col_name=None,
                                        type_=None, column_function=True,
                                        property=False, return_func=False,
                                        *args):
        """
        Internal function that generates a Vantage SQL function call.
        Function makes use of GenericFunciton from sqlalchemy to generate
        the function call.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the SQL function name to be executed.
                Types: str

            col_name:
                Optional Argument.
                Specifies the column name to use for executing the function.
                Types: str

            type_:
                Optional Argument.
                Specifies the output type of the function that it'll result
                in when executed.
                Types: teradatasqlalchemy.types

            column_function:
                Optional Argument.
                Specifies whether the SQL function is executed as
                'column.func_name()' or 'func_name(column)'. This parameter
                must be set to True, is SQL function syntax is
                'column.func_name()', otherwise must be set to False.
                Default Value: True
                Types: bool

            property:
                Optional Argument.
                Specifies whether the function being executed is exposed as
                property or method of a class. When set to True, it is
                exposed as property, otherwise method.
                Default Value: False
                Types: bool

            return_func:
                Optional Argument.
                Specifies whether to return the function object or not,
                instead of returning the _SQLColumnExpression.
                When set to True, returns the Function object (sqlalchemy).
                Default Value: False
                Types: bool

            *args:
                Specifies the SQL function function arguments.

        Returns:
            _SQLColumnExpression when "return_func" is False, otherwise
            sqlalchemy.sql.elements.Function object is returned.

        RAISES:
            None

        EXAMPLES:
            self._generate_vantage_function_call(
                func_name="function_name", col_name="col_name", return_func=True,
                type_=INTEGER())
        """
        from sqlalchemy.sql.functions import GenericFunction
        from sqlalchemy.sql.elements import quoted_name
        from sqlalchemy.exc import SAWarning

        # Catch and ignore SAWarning from sqlalchemy, which is thrown for
        # registering the function again with Generic function.
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=SAWarning)

            # A class that allows us to create a GenericFunction and
            # it's associated attributes.
            class VantageGeneric(GenericFunction):
                # Set the output type for the function.
                if type_ is not None:
                    type = type_
                else:
                    # If user has not passed any type, then set it to
                    # NullType().
                    type = sqlalc.sql.sqltypes.NullType()
                # Boolean flag to treat function as an instance method.
                function_has_col_caller = column_function
                # Generate the function syntax based on whether the
                # function is column function or not.
                if column_function:
                    name = quoted_name("{}.{}".format(col_name, func_name),
                                       False)
                    # Dynamic function gets called on teradataml._SQLColumnExpression type object.
                    # 'expression' attribute of _SQLColumnExpression object holds
                    # corresponding SQLAlchemy.Expression type object.
                    # SQLAlchemy.Expression type object should be available from FunctionElement.
                    # This 'func_caller' attribute points to that Expression object.
                    func_caller = self.expression
                else:
                    name = quoted_name(func_name, False)

                # Identifier to access the function with.
                identifier = func_name
                package = "vantage"

        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()

        # Invoke the function and return the results.
        if property:
            return self._wrap_as_column_expression(getattr(func.vantage,
                                                           func_name)())
        else:
            if return_func:
                #return getattr(func.vantage, func_name)
                return self._wrap_as_column_expression(getattr(func.vantage,
                                                               func_name))
            else:
                return self._wrap_as_column_expression(getattr(func.vantage,
                                                               func_name)(*args))

    def _wrap_as_column_expression(self, new_expression):
        """
        Internal function that wraps the provided expression as
        _SQLColumnExpression.

        PARAMETERS:
            new_expression:
                 Required Argument.
                 Specifies the expression to be returned.
                 Types: Any expression.

        RETURNS:
            _SQLColumnExpression.

        RAISES:
            None.

        EXAMPLES:
            self._wrap_as_column_expression(getattr(func.vantage,
                                                    func_name)(*args))
        """
        return _SQLColumnExpression(new_expression)

    '''
    def __process_unimplemented_functions(self, *c, **kwargs):
        """ TODO: Execute function that are not implemented. Future. """

        # Process the positional arguments passed in *c.
        new_c = [item.expression if isinstance(item, _SQLColumnExpression)
                 else item for item in c]

        # Extract the "type_" argument, if it is given, else set it to None.
        t_ = kwargs.get("type_", None)
        if t_ is None:
            # If "type_" is not passed, let's extract from the function name
            # and expression using the pre-defined vantage function output
            # type mappers.
            from teradataml.dataframe.vantage_function_types import \
                _retrieve_function_expression_type
            t_ = _retrieve_function_expression_type(self.expression)

        # Set some parameters to be passed to
        # '_generate_vantage_function_call()' function.
        cname = None
        cfunction = False
        new_c = (self.expression,) + tuple(new_c)

        # This returns quoted name, we should use quoted_name = False while
        # generating call.
        fname = ".".join(self.__names)

        # Generate the SQL function call.
        return self._generate_vantage_function_call(fname, cname, t_, cfunction,
                                                    False, False, *new_c)
    '''

    def __getitem__(self, key):
        """ Function to make _SQLColumnExpression subscriptable. """
        if isinstance(key, str):
            return getattr(self, key)

    @collect_queryband(queryband="DFC_window")
    def window(self,
               partition_columns=None,
               order_columns=None,
               sort_ascending=True,
               nulls_first=None,
               window_start_point=None,
               window_end_point=None,
               ignore_window=False):
        """
        DESCRIPTION:
            This function generates Window object on a teradataml DataFrame Column to run
            window aggregate functions.
            Function allows user to specify window for different types of
            computations:
                * Cumulative
                * Group
                * Moving
                * Remaining
            By default, window with Unbounded Preceding and Unbounded following
            is considered for calculation.
            Note:
                If both "partition_columns" and "order_columns" are None, then
                Window cannot be created on CLOB and BLOB type of columns.

        PARAMETERS:
            partition_columns:
                Optional Argument.
                Specifies the name(s) of the column(s) over which the ordered
                aggregate function executes by partitioning the rows. Such a
                grouping is static.
                Notes:
                     1. If this argument is not specified, then the entire data
                        from teradataml DataFrame, constitutes a single
                        partition, over which the ordered aggregate function
                        executes.
                     2. "partition_columns" does not support CLOB and BLOB type
                        of columns.
                        Refer 'DataFrame.tdtypes' to get the types of the
                        columns of a teradataml DataFrame.
                     3. "partition_columns" supports only columns specified in
                        groupby function, if Column is from DataFrameGroupBy.
                Types: str OR list of Strings (str)

            order_columns:
                Optional Argument.
                Specifies the name(s) of the column(s) to order the rows in a
                partition, which determines the sort order of the rows over
                which the function is applied.
                Notes:
                    1. "order_columns" does not support CLOB and BLOB type of
                       columns.
                       Refer 'DataFrame.tdtypes' to get the types of the columns
                       of a teradataml DataFrame.
                    2. "order_columns" supports only columns specified in
                        groupby function, if Column is from DataFrameGroupBy.
                    3. When ColumnExpression(s) is(are) passed to "order_columns", then the
                       corresponding expression takes precedence over arguments
                       "sort_ascending" and "nulls_first". Say, ColumnExpression is col1, then
                       1. col1.asc() or col.desc() is effective irrespective of "sort_ascending".
                       2. col1.nulls_first() or col.nulls_last() is effective irrespective of "nulls_first".
                       3. Any combination of above two take precedence over "sort_ascending" and "nulls_first".
                Types: str OR list of Strings (str) OR ColumnExpression OR list of ColumnExpressions

            sort_ascending:
                Optional Argument.
                Specifies whether column ordering should be in ascending or
                descending order.
                Default Value: True (ascending)
                Notes:
                     * When "order_columns" argument is not specified, argument
                       is ignored.
                     * When ColumnExpression(s) is(are) passed to "order_columns", then the
                       argument is ignored.
                Types: bool

            nulls_first:
                Optional Argument.
                Specifies whether null results are to be listed first or last
                or scattered.
                Default Value: None
                Notes:
                     * When "order_columns" argument is not specified, argument
                       is ignored.
                     * When "order_columns" is a ColumnExpression(s), this argument
                       is ignored.
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
            TypeError, ValueError

        RETURNS:
            An object of type Window.

        EXAMPLES:
            # Example 1: Create a window on a teradataml DataFrame column.
            >>> load_example_data("dataframe","sales")
            >>> df = DataFrame.from_table('sales')
            >>> window = df.Feb.window()
            >>>

            # Example 2: Create a cumulative (expanding) window with rows
            #            between unbounded preceding and 3 preceding with
            #            "partition_columns" and "order_columns" argument with
            #            default sorting.
            >>> window = df.Feb.window(partition_columns=df.Feb,
            ...                        order_columns=[df.Feb, df.datetime],
            ...                        window_start_point=None,
            ...                        window_end_point=-3)
            >>>

            # Example 3: Create a moving (rolling) window with rows between
            #            current row and 3 following with sorting done on 'Feb',
            #            'datetime' columns in descending order and
            #            "partition_columns" argument.
            >>> window = df.Feb.window(partition_columns=df.Feb,
            ...                        order_columns=[df.Feb.desc(), df.datetime.desc()],
            ...                        window_start_point=0,
            ...                        window_end_point=3)
            >>>

            # Example 4: Create a remaining (contracting) window with rows
            #            between current row and unbounded following with
            #            sorting done on 'Feb', 'datetime' columns in ascending
            #            order and NULL values in 'Feb', 'datetime'
            #            columns appears at last.
            >>> window = df.Feb.window(partition_columns="Feb",
            ...                        order_columns=[df.Feb.nulls_first(), df.datetime.nulls_first()],
            ...                        window_start_point=0,
            ...                        window_end_point=None
            ...                        )
            >>>

            # Example 5: Create a grouping window, with sorting done on 'Feb',
            #            'datetime' columns in ascending order and NULL values
            #            in 'Feb', 'datetime' columns appears at last.
            >>> window = df.Feb.window(partition_columns=df.Feb,
            ...                        order_columns=[df.Feb.desc().nulls_last(), df.datetime.desc().nulls_last()],
            ...                        window_start_point=None,
            ...                        window_end_point=None
            ...                        )
            >>>

            # Example 6: Create a window on a teradataml DataFrame column, which
            #            ignores all the parameters while creating window.
            >>> window = df.Feb.window(partition_columns=df.Feb,
            ...                        order_columns=[df.Feb.desc().nulls_last(), df.datetime.desc().nulls_last()],
            ...                        ignore_window=True
            ...                        )
            >>>

            # Example 7: Perform sum of Feb and attach new column to the
            # DataFrame.
            >>> window = df.Feb.window()
            >>> df.assign(feb_sum=window.sum())
                          Feb    Jan    Mar    Apr    datetime  feb_sum
            accounts
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017   1000.0
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017   1000.0
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017   1000.0
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017   1000.0
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017   1000.0
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017   1000.0
            >>>

            # Example 8: Perform min and max operations on column Apr and
            # attach both the columns to the DataFrame.
            >>> window = df.Apr.window()
            >>> df.assign(apr_min=window.min(), apr_max=window.max())
                          Feb    Jan    Mar    Apr    datetime  apr_max  apr_min
            accounts
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017      250      101
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017      250      101
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017      250      101
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017      250      101
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017      250      101
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017      250      101
            >>>

            # Example 9: Perform count and max operations on column accounts in
            # teradataml DataFrame, which is grouped by 'accounts', and attach
            # column to DataFrame.
            >>> df = df.groupby("accounts")
            >>> window = df.accounts.window()
            >>> df.assign(accounts_max=window.max(), accounts_count=window.count())
                 accounts  accounts_count accounts_max
            0   Jones LLC               6   Yellow Inc
            1     Red Inc               6   Yellow Inc
            2  Yellow Inc               6   Yellow Inc
            3  Orange Inc               6   Yellow Inc
            4    Blue Inc               6   Yellow Inc
            5    Alpha Co               6   Yellow Inc
            >>>
        """
        return Window(object=self,
                        partition_columns=partition_columns,
                        order_columns=order_columns,
                        sort_ascending=sort_ascending,
                        nulls_first=nulls_first,
                        window_start_point=window_start_point,
                        window_end_point=window_end_point,
                        ignore_window=ignore_window)

    @collect_queryband(queryband="DFC_desc")
    def desc(self):
        """
        DESCRIPTION:
            Generates a new _SQLColumnExpression which sorts the actual
            expression in Descending Order.
            Note:
                This function is supported only while sorting the Data. This
                function is neither supported in projection nor supported in
                filtering the Data.

        RAISES:
            None

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe","sales")
            >>> df = DataFrame.from_table('sales')

            >>> load_example_data("dataframe","sales")
            >>> df = DataFrame.from_table('sales')

            # Sorts the Data on column accounts in ascending order and column
            # Feb in descending order, then calculates moving average by dropping
            # the input DataFrame columns on the window of size 2.
            >>> df.mavg(width=2, sort_columns=[df.accounts, df.Feb.desc()], drop_columns=True)
               mavg_Feb  mavg_Jan  mavg_Mar  mavg_Apr mavg_datetime
            0     145.0     100.0     117.5     140.5    04/01/2017
            1     205.0     150.0     140.0     250.0    04/01/2017
            2     145.0     150.0     140.0       NaN    04/01/2017
            3     205.0     150.0     140.0     215.0    04/01/2017
            4     150.0     125.0     155.0     175.5    04/01/2017
            5     210.0     200.0     215.0     250.0    04/01/2017
        """
        return _SQLColumnExpression(self.expression.desc().label(self.name))

    @collect_queryband(queryband="DFC_asc")
    def asc(self):
        """
        DESCRIPTION:
            Generates a new _SQLColumnExpression which sorts the actual
            expression in Ascending Order.
            Note:
                This function is supported only while sorting the Data. This
                function is neither supported in projection nor supported in
                filtering the Data.

        RAISES:
            None

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe","sales")
            >>> df = DataFrame.from_table('sales')

            # Sorts the Data on column accounts in ascending order and column
            # Feb in descending order, then calculates moving average by dropping
            # the input DataFrame columns on the window of size 2.
            >>> df.mavg(width=2, sort_columns=[df.accounts, df.Feb.desc()], drop_columns=True)
               mavg_Feb  mavg_Jan  mavg_Mar  mavg_Apr mavg_datetime
            0     145.0     100.0     117.5     140.5    04/01/2017
            1     205.0     150.0     140.0     250.0    04/01/2017
            2     145.0     150.0     140.0       NaN    04/01/2017
            3     205.0     150.0     140.0     215.0    04/01/2017
            4     150.0     125.0     155.0     175.5    04/01/2017
            5     210.0     200.0     215.0     250.0    04/01/2017
        """
        return _SQLColumnExpression(self.expression.asc().label(self.name))

    @collect_queryband(queryband="DFC_nullsFirst")
    def nulls_first(self):
        """
        DESCRIPTION:
            Generates a new _SQLColumnExpression which displays NULL values first.
            Note:
                The function can be applied only in conjunction with "asc" or "desc".

        RAISES:
            None

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe","sales")
            >>> df = DataFrame.from_table('sales')

            # Sorts the Data on column accounts in ascending order and column
            # Feb in descending order, then calculates moving average by dropping
            # the input DataFrame columns on the window of size 2.
            >>> df.mavg(width=2, sort_columns=[df.accounts.desc().nulls_first()], drop_columns=True)
               mavg_Feb  mavg_Jan  mavg_Mar  mavg_Apr mavg_datetime
            0     145.0     100.0     117.5     140.5    04/01/2017
            1     205.0     150.0     140.0     250.0    04/01/2017
            2     145.0     150.0     140.0       NaN    04/01/2017
            3     205.0     150.0     140.0     215.0    04/01/2017
            4     150.0     125.0     155.0     175.5    04/01/2017
            5     210.0     200.0     215.0     250.0    04/01/2017
        """
        return _SQLColumnExpression(self.expression.nulls_first().label(self.name))

    @collect_queryband(queryband="DFC_nullsLast")
    def nulls_last(self):
        """
        DESCRIPTION:
            Generates a new _SQLColumnExpression which displays NULL values last.
            Note:
                The function can be applied only in conjunction with "asc" or "desc".

        RAISES:
            None

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe","sales")
            >>> df = DataFrame.from_table('sales')

            # Sorts the Data on column accounts in ascending order and column
            # Feb in descending order, then calculates moving average by dropping
            # the input DataFrame columns on the window of size 2.
            >>> df.mavg(width=2, sort_columns=[df.accounts.asc().nulls_last(), df.Feb.desc().nulls_last()], drop_columns=True)
               mavg_Feb  mavg_Jan  mavg_Mar  mavg_Apr mavg_datetime
            0     145.0     100.0     117.5     140.5    04/01/2017
            1     205.0     150.0     140.0     250.0    04/01/2017
            2     145.0     150.0     140.0       NaN    04/01/2017
            3     205.0     150.0     140.0     215.0    04/01/2017
            4     150.0     125.0     155.0     175.5    04/01/2017
            5     210.0     200.0     215.0     250.0    04/01/2017
        """
        return _SQLColumnExpression(self.expression.nulls_last().label(self.name))

    @collect_queryband(queryband="DFC_distinct")
    def distinct(self):
        """
        DESCRIPTION:
            Generates a new _SQLColumnExpression which removes the duplicate
            rows while processing the function.
            Note:
                This function is supported only in Projection. It is neither
                supported in sorting the records nor supported in filtering
                the records.

        RAISES:
            None

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> from teradataml import *
            >>> load_example_data("dataframe","sales")
            >>> df = DataFrame.from_table('sales')
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            >>>
            >>> df.assign(drop_columns=True, distinct_feb=df.Feb.distinct())
               distinct_feb
            0         210.0
            1          90.0
            2         200.0
            >>>
        """
        return _SQLColumnExpression(self.expression.distinct().label(self.name))

    def _format_ilike_like_args(self, other, escape_char=None):
        """
            DESCRIPTION:
                Internal function to validate and format the arguments passed to
                'ilike' and 'like' functions.

            PARAMETERS:
                other:
                    Required Argument.
                    Specifies a string to match.
                    Types: str OR ColumnExpression

                escape_char:
                    Optional Argument.
                    Specifies the escape character to be used in the pattern.
                    Types: str with one character

            RETURNS:
                tuple

            EXAMPLES:
                self._format_ilike_like_args(other='A!%', escape_char='!')
        """
        # Validate the arguments.
        arg_validate = []
        arg_validate.append(["other", other, False, (str, ColumnExpression), True])
        arg_validate.append(["escape_char", escape_char, True, (str), True])
        _Validators._validate_function_arguments(arg_validate)

        # Format the arguments for ilike/like function.
        other  = "{}".format(other.compile()) if isinstance(other, ColumnExpression) else "'{}'".format(other)
        escape = " ESCAPE '{}'".format(escape_char) if escape_char is not None else ""
        return other, escape

    @collect_queryband(queryband="DFC_ilike")
    def ilike(self, other, escape_char=None):
        """
        DESCRIPTION:
            Function which is used to match the pattern.

        PARAMETERS:
            other:
                Required Argument.
                Specifies a string to match. String match is case insensitive.
                Types: str OR ColumnExpression

            escape_char:
                Optional Argument.
                Specifies the escape character to be used in the pattern.
                Types: str with one character

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load example data.
            >>> load_example_data("teradataml", "pattern_matching_data")
            >>> df = DataFrame('pattern_matching_data')
                       data     pattern     level
            id                                   
            5       prod_01    prod_01%  Beginner
            8      log%2024        l_g%  Beginner
            2     user%2025     user!%%  Beginner
            6       prod%v2     prod!_%    Novice
            4   data%backup     data@%%  Advanced
            10     backup_9  restore!_9  Beginner
            7      log_file   log^_file  Advanced
            1    user_Alpha     user!_%  Advanced
            3     data_2024          d%    Novice
            9     temp_file    temp!__%    Novice

            # Example 1: Find out the records which starts with 'A' in the column 'level'.
            >>> df = df[df.level.ilike('A%')]
            >>> df
                       data    pattern     level
            id                                  
            4   data%backup    data@%%  Advanced
            7      log_file  log^_file  Advanced
            1    user_Alpha    user!_%  Advanced
            >>>

            # Example 2: Create a new Column with values as -
            #            1 if value of column 'level' starts with 'n' and third letter is 'v',
            #            0 otherwise. Ignore case.
            >>> from sqlalchemy.sql.expression import case as case_when
            >>> df.assign(new_col = case_when((df.level.ilike('n_v%').expression, 1), else_=0))
                       data     pattern     level new_col
            id                                           
            3     data_2024          d%    Novice       1
            1    user_Alpha     user!_%  Advanced       0
            8      log%2024        l_g%  Beginner       0
            2     user%2025     user!%%  Beginner       0
            10     backup_9  restore!_9  Beginner       0
            9     temp_file    temp!__%    Novice       1
            6       prod%v2     prod!_%    Novice       1
            5       prod_01    prod_01%  Beginner       0
            4   data%backup     data@%%  Advanced       0
            7      log_file   log^_file  Advanced       0
            >>>

            # Example 3: Find out the records where the value in the 'data' column 
            #            matches the pattern specified in the 'pattern' column.
            >>> df = df[df.data.ilike(df.pattern)]
            >>> df
                     data   pattern     level
            id                               
            3   data_2024        d%    Novice
            8    log%2024      l_g%  Beginner
            5     prod_01  prod_01%  Beginner
            >>>

            # Example 4: Find out the records where the value in the 'data' column
            #            matches the pattern specified in the 'pattern' column considering the
            #            escape character as '!'.
            >>> df = df[df.data.ilike(df.pattern, escape_char='!')]
            >>> df
                      data   pattern     level
            id                                
            8     log%2024      l_g%  Beginner
            9    temp_file  temp!__%    Novice
            3    data_2024        d%    Novice
            2    user%2025   user!%%  Beginner
            1   user_Alpha   user!_%  Advanced
            5      prod_01  prod_01%  Beginner
            >>>
        """
        # Validate and format arguments
        other, escape = self._format_ilike_like_args(other, escape_char)        
        return _SQLColumnExpression(
            literal_column("{} (NOT CASESPECIFIC) LIKE {}{}".format(self.compile(), other, escape)))

    @collect_queryband(queryband="DFC_like")
    def like(self, other, escape_char=None):
        """
        DESCRIPTION:
            Function which is used to match the pattern.

        PARAMETERS:
            other:
                Required Argument.
                Specifies a string to match. String match is case sensitive.
                Types: str OR ColumnExpression

            escape_char:
                Optional Argument.
                Specifies the escape character to be used in the pattern.
                Types: str with one character

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load example data.
            >>> load_example_data("teradataml", "pattern_matching_data")
            >>> df = DataFrame('pattern_matching_data')
                       data     pattern     level
            id                                   
            5       prod_01    prod_01%  Beginner
            8      log%2024        l_g%  Beginner
            2     user%2025     user!%%  Beginner
            6       prod%v2     prod!_%    Novice
            4   data%backup     data@%%  Advanced
            10     backup_9  restore!_9  Beginner
            7      log_file   log^_file  Advanced
            1    user_Alpha     user!_%  Advanced
            3     data_2024          d%    Novice
            9     temp_file    temp!__%    Novice

            # Example 1: Find out the records which starts with 'A' in the column 'level'.
            >>> df = df[df.level.like('A%')]
            >>> df
                       data    pattern     level
            id                                  
            4   data%backup    data@%%  Advanced
            7      log_file  log^_file  Advanced
            1    user_Alpha    user!_%  Advanced
            >>>

            # Example 2: Create a new Column with values as -
            #            1 if value of column 'stats' starts with 'N' and third letter is 'v',
            #            0 otherwise. Do not ignore case.
            >>> from sqlalchemy.sql.expression import case as case_when
            >>> df.assign(new_col = case_when((df.level.like('N_v%').expression, 1), else_=0))
                       data     pattern     level new_col
            id                                           
            3     data_2024          d%    Novice       1
            1    user_Alpha     user!_%  Advanced       0
            8      log%2024        l_g%  Beginner       0
            2     user%2025     user!%%  Beginner       0
            10     backup_9  restore!_9  Beginner       0
            9     temp_file    temp!__%    Novice       1
            6       prod%v2     prod!_%    Novice       1
            5       prod_01    prod_01%  Beginner       0
            4   data%backup     data@%%  Advanced       0
            7      log_file   log^_file  Advanced       0
            >>>

            # Example 3: Find out the records where the value in the 'data' column 
            #            matches the pattern specified in the 'pattern' column.
            >>> df = df[df.data.like(df.pattern)]
            >>> df
                     data   pattern     level
            id                               
            3   data_2024        d%    Novice
            8    log%2024      l_g%  Beginner
            5     prod_01  prod_01%  Beginner
            >>>

            # Example 4: Find out the records where the value in the 'data' column
            #            matches the pattern specified in the 'pattern' column considering the
            #            escape character as '!'.
            >>> df = df[df.data.like(df.pattern, escape_char='!')]
            >>> df
                      data   pattern     level
            id                                
            8     log%2024      l_g%  Beginner
            9    temp_file  temp!__%    Novice
            3    data_2024        d%    Novice
            2    user%2025   user!%%  Beginner
            1   user_Alpha   user!_%  Advanced
            5      prod_01  prod_01%  Beginner
            >>>
        """
        # Validate and format arguments
        other, escape = self._format_ilike_like_args(other, escape_char)        
        return _SQLColumnExpression(
            literal_column("{} (CASESPECIFIC) LIKE {}{}".format(self.compile(), other, escape)))

    def rlike(self, pattern, case_sensitive=True):
        """
        DESCRIPTION:
            Function to match a string against a regular expression pattern.

        PARAMETERS:
            pattern:
                Required Argument.
                Specifies a regular expression pattern to match against the column values.
                Note:
                    The pattern follows POSIX regular expression syntax.
                Type: str OR ColumnExpression

            case_sensitive:
                Optional Argument.
                Specifies whether the pattern matching is case-sensitive.
                When set to False, the function ignores case sensitivity and matches 
                the regex. Otherwise, function considers case sensitivity while matching regex.
                Default: True
                Type: bool

        RAISES:
            TeradataMlException

        RETURNS:
            ColumnExpression

        EXAMPLES:
            >>> load_example_data("dataframe","admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
                masters    gpa      stats programming  admitted
            id
            13      no     4.00  Advanced      Novice         1
            26     yes     3.57  Advanced    Advanced         1
            5       no     3.44    Novice      Novice         0
            19     yes     1.98  Advanced    Advanced         0
            15     yes     4.00  Advanced    Advanced         1
            40     yes     3.95    Novice    Beginner         0
            7      yes     2.33    Novice      Novice         1
            22     yes     3.46    Novice    Beginner         0
            36      no     3.00  Advanced      Novice         0
            38     yes     2.65  Advanced    Beginner         1
            
            # Example 1: Find records whose 'stats' column contains 'van'.
            >>> result = df[df.stats.rlike('.*van.*')]
            >>> result
                masters     gpa     stats  programming  admitted
            id
            13      no     4.00  Advanced      Novice         1
            26     yes     3.57  Advanced    Advanced         1
            34     yes     3.85  Advanced    Beginner         0
            19     yes     1.98  Advanced    Advanced         0
            15     yes     4.00  Advanced    Advanced         1
            36      no     3.00  Advanced      Novice         0
            38     yes     2.65  Advanced    Beginner         1

            # Example 2: Find records whose 'stats' column ends with 'ced'.
            >>> result = df[df.stats.rlike('.*ced$')]
            >>> result
               masters   gpa     stats programming  admitted
            id                                              
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            30     yes  3.79  Advanced      Novice         0
            28      no  3.93  Advanced    Advanced         1
            16      no  3.70  Advanced    Advanced         1
            14     yes  3.45  Advanced    Advanced         0
            
            # Example 3: Case-insensitive search for records containing 'NOVICE'.
            >>> result = df[df.stats.rlike('NOVICE', case_sensitive=False)]
            >>> result
               masters   gpa   stats programming  admitted
            id                                            
            12      no  3.65  Novice      Novice         1
            40     yes  3.95  Novice    Beginner         0
            7      yes  2.33  Novice      Novice         1
            5       no  3.44  Novice      Novice         0
            22     yes  3.46  Novice    Beginner         0
            37      no  3.52  Novice      Novice         1
        """
        # Validate arguments
        arg_validate = []
        arg_validate.append(["pattern", pattern, False, (str, ColumnExpression), True])
        arg_validate.append(["case_sensitive", case_sensitive, True, (bool), True])
        _Validators._validate_function_arguments(arg_validate)

        if isinstance(pattern, ColumnExpression):
            pattern = pattern.expression

        # Set the case sensitivity modifier based on the parameter.
        case_modifier = 'c' if case_sensitive else 'i'
        return _SQLColumnExpression(
            func.regexp_similar(self.expression, pattern, case_modifier) == 1,
            type=INTEGER())

    @collect_queryband(queryband="DFC_startswith")
    def startswith(self, other):
        """
        DESCRIPTION:
            Function to check whether the column value starts with the specified value or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies a string literal or ColumnExpression to match.
                Types: str OR ColumnExpression

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            >>> load_example_data("ntree", "employee_table")
            >>> df = DataFrame("employee_table")
            >>> df
                   emp_name  mgr_id mgr_name
            emp_id
            200         Pat   100.0      Don
            300       Donna   100.0      Don
            400         Kim   200.0      Pat
            500        Fred   400.0      Kim
            100         Don     NaN       NA

            # Example 1: Find out the employees whose name starts with their managers name.
            >>> df[df.emp_name.startswith(df.mgr_name)]
                   emp_name  mgr_id mgr_name
            emp_id
            300       Donna     100      Don

            # Example 2: Find out the employees whose manager name starts with Don.
            >>> df[df.mgr_name.startswith('Don')]
                   emp_name  mgr_id mgr_name
            emp_id
            300       Donna     100      Don
            200         Pat     100      Don

            # Example 3: Create a new column with values as
            #            1, if employees manager name starts with 'Don'.
            #            0, else.
            >>> df.assign(new_col=case_when((df.mgr_name.startswith('Don').expression, 1), else_=0))
                   emp_name  mgr_id mgr_name new_col
            emp_id
            300       Donna   100.0      Don       1
            500        Fred   400.0      Kim       0
            100         Don     NaN       NA       0
            400         Kim   200.0      Pat       0
            200         Pat   100.0      Don       1
        """
        return _SQLColumnExpression(
            self.regexp_instr(other, 1, 1, 0).expression == 1,
            type=INTEGER)

    @collect_queryband(queryband="DFC_endswith")
    def endswith(self, other):
        """
        DESCRIPTION:
            Function to check whether the column value ends with the specified value or not.

        PARAMETERS:
            other:
                Required Argument.
                Specifies a string literal or ColumnExpression to match.
                Types: str OR ColumnExpression

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            >>> load_example_data("ntree", "employee_table")
            >>> df = DataFrame("employee_table")
            >>> df = df.assign(new_col = 'on')
                   emp_name  mgr_id mgr_name new_col
            emp_id
            300       Donna   100.0      Don      on
            500        Fred   400.0      Kim      on
            100         Don     NaN       NA      on
            400         Kim   200.0      Pat      on
            200         Pat   100.0      Don      on

            # Example 1: Find out the employees whose manager name ends
            #            with values in column 'new_col'.
            >>> df[df.mgr_name.endswith(df.new_col)]
                   emp_name  mgr_id mgr_name new_col
            emp_id
            300       Donna     100      Don      on
            200         Pat     100      Don      on

            # Example 2: Find out the employees whose name starts with
            #            'D' and ends with 'n'.
            >>> df[df.emp_name.startswith('D') & df.emp_name.endswith('n')]
                   emp_name mgr_id mgr_name new_col
            emp_id
            100         Don   None       NA      on

            # Example 3: Create a new column with values as
            #            1, if employees manager name ends with 'im'.
            #            0, else.
            >>> df.assign(new_col=case_when((df.mgr_name.endswith('im').expression, 1), else_=0))
                   emp_name  mgr_id mgr_name new_col
            emp_id
            300       Donna   100.0      Don       0
            500        Fred   400.0      Kim       1
            100         Don     NaN       NA       0
            400         Kim   200.0      Pat       0
            200         Pat   100.0      Don       0
        """
        return _SQLColumnExpression(
            self.regexp_instr(other, 1, 1, 1).expression == self.length().expression+1,
            type=INTEGER)

    @collect_queryband(queryband="DFC_substr")
    def substr(self, start_pos, length):
        """
        DESCRIPTION:
            Function to get substring from column.

        PARAMETERS:
            start_pos:
                Required Argument.
                Specifies starting position to extract string from column.
                Note:
                    Index position starts with 1 instead of 0.
                Types: int OR ColumnExpression

            length:
                Required Argument.
                Specifies the length of the string to extract from column.
                Types: int OR ColumnExpression

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            >>> load_example_data("ntree", "employee_table")
            >>> df = DataFrame("employee_table")
                   emp_name  mgr_id mgr_name
            emp_id
            200         Pat   100.0      Don
            300       Donna   100.0      Don
            400         Kim   200.0      Pat
            500        Fred   400.0      Kim
            100         Don     NaN       NA

            # Example 1: Create a new column by extracting the first 3 letters
            #            from column emp_name.
            >>> df.assign(new_column = df.emp_name.substr(1,3))
                   emp_name  mgr_id mgr_name new_column
            emp_id
            200         Pat   100.0      Don        Pat
            300       Donna   100.0      Don        Don
            400         Kim   200.0      Pat        Kim
            500        Fred   400.0      Kim        Fre
            100         Don     NaN       NA        Don

            # Example 2: Find out the employees whose first three letters
            #            in their name is 'Fre'.
            >>> df[df.emp_name.substr(1,3) == 'Fre']
                   emp_name  mgr_id mgr_name new_col
            emp_id
            500        Fred     400      Kim      on

            # Example 3: Create a new column by passing ColumnExpression as
            #            start_pos and length.
            >>> df.assign(new_column = df.emp_name.substr(df.emp_id, df.mgr_id))
                     emp_name  mgr_id mgr_name new_column
            emp_id
            1         Pat   2      Don        Pa

        """
        # Handle cases where start_pos or length are ColumnExpressions.
        start_pos_expr = start_pos.expression if isinstance(start_pos, _SQLColumnExpression) else start_pos
        length_expr = length.expression if isinstance(length, _SQLColumnExpression) else length

        return _SQLColumnExpression(func.substr(self.expression, start_pos_expr, length_expr),
                                    type=self.type)

    def count_delimiters(self, delimiter):
        """
        DESCRIPTION:
            Function to count the total number of occurrences of a specified delimiter.

        PARAMETERS:
            delimiter:
                Required Argument.
                Specifies the delimiter to count in the column values.
                Types: str

        RETURNS:
            ColumnExpression.

        EXAMPLES:
        # Load sample data
        >>> load_example_data("dataframe", "admissions_train")
        >>> df = DataFrame("admissions_train")
        
        # Create a DataFrame with a column containing delimiters.
        >>> df1 = df.assign(delim_col = 'ab.c.def.g')
        >>> df1
           masters   gpa     stats programming  admitted   delim_col
        id                                                          
        38     yes  2.65  Advanced    Beginner         1  ab.c.def.g
        7      yes  2.33    Novice      Novice         1  ab.c.def.g
        26     yes  3.57  Advanced    Advanced         1  ab.c.def.g
        
        # Example 1: Count the number of periods in column 'delim_col'.
        >>> res = df1.assign(dot_count = df1.delim_col.count_delimiters('.'))
        >>> res
           masters   gpa     stats programming  admitted   delim_col  dot_count
        id                                                                     
        38     yes  2.65  Advanced    Beginner         1  ab.c.def.g          3
        7      yes  2.33    Novice      Novice         1  ab.c.def.g          3
        26     yes  3.57  Advanced    Advanced         1  ab.c.def.g          3

        # Example 2: Count multiple delimiters in a string.
        >>> df2 = df.assign(delim_col = 'a,b;c;d-e')
        >>> res = df2.assign(
        ...     comma_count = df2.delim_col.count_delimiters(','),
        ...     semicolon_count = df2.delim_col.count_delimiters(';'),
        ...     colon_count = df2.delim_col.count_delimiters(':'),
        ...     dash_count = df2.delim_col.count_delimiters('-')
        ... )
        >>> res
           masters   gpa     stats programming  admitted  delim_col colon_count comma_count dash_count  semicolon_count
        id                                                                                                                
        38     yes  2.65  Advanced    Beginner         1  a,b;c;d-e           0           1          1                2
        7      yes  2.33    Novice      Novice         1  a,b;c;d-e           0           1          1                2
        26     yes  3.57  Advanced    Advanced         1  a,b;c;d-e           0           1          1                2
        5       no  3.44    Novice      Novice         0  a,b;c;d-e           0           1          1                2
        """
        
        # Validate arguments
        arg_validate = []
        arg_validate.append(["delimiter", delimiter, False, (str), True])
        _Validators._validate_function_arguments(arg_validate)
        
        # Calculate the count by comparing the original string length 
        # with the length after removing all delimiters.
        expression = (func.characters(self.expression) - func.characters(
            func.oreplace(self.expression, delimiter, '')))// func.characters(delimiter)

        return _SQLColumnExpression(expression, type=INTEGER())
    
    @collect_queryband(queryband="DFC_substringIndex")
    def substring_index(self, delimiter, count):
        """
        DESCRIPTION:
            Function to return the substring from a column before a specified 
            delimiter, up to a given occurrence count.
            
        PARAMETERS:
            delimiter:
                Required Argument.
                Specifies the delimiter string to split the column values.
                Types: str

            count:
                Required Argument.
                Specifies the number of occurrences of the delimiter to consider.
                If positive, the substring is extracted from the start of the string.
                If negative, the substring is extracted from the end of the string.
                If zero, an empty string is returned.
                Types: int
        
        RAISES:
            TeradataMlException

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe","admissions_train")
            >>> df = DataFrame('admissions_train')

            # Create a new column 'delim_col' with string.
            >>> df1 = df.assign(delim_col = 'ab.c.def.g')
            >>> df1
               masters   gpa     stats programming  admitted   delim_col
            id                                                          
            38     yes  2.65  Advanced    Beginner         1  ab.c.def.g
            7      yes  2.33    Novice      Novice         1  ab.c.def.g
            26     yes  3.57  Advanced    Advanced         1  ab.c.def.g
            5       no  3.44    Novice      Novice         0  ab.c.def.g
            3       no  3.70    Novice    Beginner         1  ab.c.def.g
            22     yes  3.46    Novice    Beginner         0  ab.c.def.g
            1      yes  3.95  Beginner    Beginner         0  ab.c.def.g
            17      no  3.83  Advanced    Advanced         1  ab.c.def.g
            15     yes  4.00  Advanced    Advanced         1  ab.c.def.g
            34     yes  3.85  Advanced    Beginner         0  ab.c.def.g

            # Example 1: Create a new column 'new_column' by extracting the substring
                         based on positive count.
            >>> res = df1.assign(new_column = df1.delim_col.substring_index('.', 2))
            >>> res
               masters   gpa     stats programming  admitted   delim_col new_column
            id                                                                     
            34     yes  3.85  Advanced    Beginner         0  ab.c.def.g       ab.c
            32     yes  3.46  Advanced    Beginner         0  ab.c.def.g       ab.c
            11      no  3.13  Advanced    Advanced         1  ab.c.def.g       ab.c
            30     yes  3.79  Advanced      Novice         0  ab.c.def.g       ab.c
            28      no  3.93  Advanced    Advanced         1  ab.c.def.g       ab.c
            16      no  3.70  Advanced    Advanced         1  ab.c.def.g       ab.c
            35      no  3.68    Novice    Beginner         1  ab.c.def.g       ab.c
            40     yes  3.95    Novice    Beginner         0  ab.c.def.g       ab.c
            19     yes  1.98  Advanced    Advanced         0  ab.c.def.g       ab.c

            # Example 2: Create a new column 'new_column' by extracting the substring
                         based on negative count.
            >>> res = df1.assign(new_column = df1.delim_col.substring_index('.', -3))
            >>> res
               masters   gpa     stats programming  admitted   delim_col new_column
            id                                                                     
            34     yes  3.85  Advanced    Beginner         0  ab.c.def.g    c.def.g
            32     yes  3.46  Advanced    Beginner         0  ab.c.def.g    c.def.g
            11      no  3.13  Advanced    Advanced         1  ab.c.def.g    c.def.g
            30     yes  3.79  Advanced      Novice         0  ab.c.def.g    c.def.g
            28      no  3.93  Advanced    Advanced         1  ab.c.def.g    c.def.g
            16      no  3.70  Advanced    Advanced         1  ab.c.def.g    c.def.g
            35      no  3.68    Novice    Beginner         1  ab.c.def.g    c.def.g
            40     yes  3.95    Novice    Beginner         0  ab.c.def.g    c.def.g
            19     yes  1.98  Advanced    Advanced         0  ab.c.def.g    c.def.g

            # Example 3: Create a new column 'new_column' by extracting the substring
                         with 2-character delimiter based on positive count.
            >>> res = df1.assign(new_column = df1.delim_col.substring_index('c.d', 1))
            >>> res
               masters   gpa     stats programming  admitted   delim_col new_column
            id                                                                     
            34     yes  3.85  Advanced    Beginner         0  ab.c.def.g        ab.
            32     yes  3.46  Advanced    Beginner         0  ab.c.def.g        ab.
            11      no  3.13  Advanced    Advanced         1  ab.c.def.g        ab.
            30     yes  3.79  Advanced      Novice         0  ab.c.def.g        ab.
            28      no  3.93  Advanced    Advanced         1  ab.c.def.g        ab.
            16      no  3.70  Advanced    Advanced         1  ab.c.def.g        ab.
            35      no  3.68    Novice    Beginner         1  ab.c.def.g        ab.
            40     yes  3.95    Novice    Beginner         0  ab.c.def.g        ab.

        """
        # Validate arguments
        arg_validate = []
        arg_validate.append(["delimiter", delimiter, False, (str), True])
        arg_validate.append(["count", count, False, (int), True])
        _Validators._validate_function_arguments(arg_validate)

        # Create the SQL expression for substring_index.
        if count == 0:
            return _SQLColumnExpression(literal(""), type=self.type)
            
        elif count > 0:
            # For positive count, return substring before the nth occurrence.
            position = func.instr(self.expression, delimiter, 1, count)
            # Handle the case where the delimiter is not found.
            expression = case_when((position == 0, self.expression),
                                    else_=func.substring(self.expression, 1, position - 1))
        else:
            # For negative count, we need to find substring after the (total - |count|)th delimiter
            # First, get the total number of delimiters
            total_delimiters = self.count_delimiters(delimiter).expression
            
            # Calculate the position to start from (convert negative count to positive position).
            position = total_delimiters + count + 1
            
            # Handle the case where the absolute negative count exceeds the total number of delimiters.
            expression = case_when((position > 0,
                                    # Get substring after the nth occurrence from the beginning.
                                    func.substring(self.expression, 
                                                   func.instr(self.expression, delimiter, 1, position) + len(delimiter),
                                                   func.characters(self.expression))),
                                    else_=self.expression)
            
        return _SQLColumnExpression(expression, type=self.type)

    @collect_queryband(queryband="DFC_replace")
    def replace(self, to_replace, value=None):
        """
        DESCRIPTION:
            Function replaces every occurrence of "to_replace" in the column
            with the "value". Use this function to replace a value from string.
            Note:
                The function replaces value in a string column only when it
                matches completely. If you want to replace a value in a string
                column with only a portion of the string, then use function
                oreplace.

        PARAMETERS:
            to_replace:
                Required Argument.
                Specifies a ColumnExpression or a literal that the function
                searches for values in the Column. Use ColumnExpression when
                you want to match the condition based on a DataFrameColumn
                function, else use literal.
                Note:
                    Only ColumnExpressions generated from DataFrameColumn
                    functions are supported. BinaryExpressions are not supported.
                    Example: Consider teradataml DataFrame has two columns COL1, COL2.
                             df.COL1.abs() is supported but df.COL1 == df.COL2 is not
                             supported.
                Supported column types: CHAR, VARCHAR, FLOAT, INTEGER, DECIMAL
                Types: ColumnExpression OR int OR float OR str OR dict

            value:
                Required argument when "to_replace" is not a dictionary. Optional otherwise.
                Specifies a ColumnExpression or a literal that replaces
                the "to_replace" in the column. Use ColumnExpression when
                you want to replace based on a DataFrameColumn function, else
                use literal.
                Notes:
                     * Argument is ignored if "to_replace" is a dictionary.
                     * Only ColumnExpressions generated from DataFrameColumn
                       functions are supported. BinaryExpressions are not supported.
                       Example: Consider teradataml DataFrame has two columns COL1, COL2.
                                df.COL1.abs() is supported but df.COL1 == df.COL2 is not
                                supported.
                Supported column types: CHAR, VARCHAR, FLOAT, INTEGER, DECIMAL
                Types: ColumnExpression OR int OR float OR str

        RAISES:
            TeradataMlException

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "chi_sq")

            # Create a DataFrame on 'chi_sq' table.
            >>> df = DataFrame("chi_sq")
            >>> print(df)
                    dem  rep
            gender
            female    6    9
            male      8    5

            # Example 1: Create a new column 'new_column' by replacing all the
            #            occurances of 'male' with 'man' in Column 'gender'.
            >>> res = df.assign(new_column = df.gender.replace("male", "man"))
            >>> print(res)
                    dem  rep new_column
            gender
            male      8    5        man
            female    6    9     female

            # Example 2: Create a new Column 'new_column' by replacing all the
            #            occurances of 5 with square root of 5 in Column 'rep'.
            >>> print(df.assign(new_column = df.rep.replace(5, df.rep.sqrt())))
                    dem  rep  new_column
            gender
            male      8    5    2.236068
            female    6    9    9.000000

            # Example 3: Create a new Column 'new_column' by replacing all the
            #            occurances of 5 with square root of 5 and 9 with
            #            the values of Column 'dem' in Column 'rep'.
            >>> print(df.assign(new_column = df.rep.replace({5: df.rep.sqrt(), 9:df.dem})))
                    dem  rep  new_column
            gender
            male      8    5    2.236068
            female    6    9    6.000000

            # Example 4: Create a new Column 'new_column' by replacing all the
            #            the values of Column 'rep' with it's square root.
            >>> print(df.assign(new_column = df.rep.replace({df.rep: df.rep.sqrt()})))
                    dem  rep  new_column
            gender
            female    6    9    3.000000
            male      8    5    2.236068
        """
        _validation_matrix = []

        _validation_matrix.append(["to_replace", to_replace, True, (int, float, str, dict, _SQLColumnExpression), True])
        _validation_matrix.append(["value", value, True, (int, float, str, _SQLColumnExpression)])
        _Validators._validate_function_arguments(_validation_matrix)

        # Convert to dictionary if it is not a dictionary.
        if not isinstance(to_replace, dict):
            to_replace = {to_replace: value}

        exp = []
        for f_, t_ in to_replace.items():
            f_ = f_.expression if isinstance(f_, _SQLColumnExpression) else f_
            t_ = t_.expression if isinstance(t_, _SQLColumnExpression) else t_
            exp.append((self.expression == f_, t_))

        expression = case_when(*exp, else_=self.expression)
        return _SQLColumnExpression(expression, type=self.type)

    def _get_sql_columns(self, *columns):
        """
        DESCRIPTION:
            Get the list of columns names.

        PARAMETERS:
            *columns:
                Required Argument.
                Specifies the name(s) of the columns or ColumnExpression(s)
                as positional arguments.
                At least one positional argument is required.
                Types: str OR int OR float OR ColumnExpression OR ColumnExpressions

        RETURNS:
            list

        EXAMPLES:
            self._get_sql_columns(df.price, df.lotsize, df.bedrooms)

        """
        arg_info_matrix = []
        expected_data_types = (str, int, float, ColumnExpression)

        get_expr = lambda col: col.expression if isinstance(col, ColumnExpression)\
            else col
        columns_ = [get_expr(self)]

        for column in columns:
            arg_info_matrix.append(["columns", column, False, expected_data_types, True])
            columns_ = columns_ + [get_expr(column)]

        _Validators._validate_function_arguments(arg_info_matrix)

        return columns_

    @collect_queryband(queryband="DFC_greatest")
    def greatest(self, *columns):
        """
        DESCRIPTION:
            Get the greatest values from the given columns.
            Note:
                * All of the input columns type must be of same data
                  type or else the types must be compatible.

        PARAMETERS:
            *columns:
                Specifies the name(s) of the columns or ColumnExpression(s)
                as positional arguments.
                At least one positional argument is required.
                Types: str OR int OR float OR ColumnExpression OR ColumnExpressions

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("glmpredict", "housing_test")
            >>>

            # Create a DataFrame on 'housing_test' table.
            >>> df = DataFrame("housing_test")
            >>> df = df.select(["sn", "price", "lotsize", "bedrooms", "bathrms", "stories"])
            >>> df
                   price  lotsize  bedrooms  bathrms  stories
            sn
            364  72000.0  10700.0         3        1        2
            13   27000.0   1700.0         3        1        2
            459  44555.0   2398.0         3        1        1
            463  49000.0   2610.0         3        1        2
            260  41000.0   6000.0         2        1        1
            177  70000.0   5400.0         4        1        2
            53   68000.0   9166.0         2        1        1
            440  69000.0   6862.0         3        1        2
            255  61000.0   4360.0         4        1        2
            301  55000.0   4080.0         2        1        1
            >>>

            # Example 1: Find the greatest values in the columns "price" and "lotsize".
            >>> gt_df = df.assign(gt_col=df.price.greatest(df.lotsize))
            >>> gt_df
                   price  lotsize  bedrooms  bathrms  stories   gt_col
            sn
            364  72000.0  10700.0         3        1        2  72000.0
            13   27000.0   1700.0         3        1        2  27000.0
            459  44555.0   2398.0         3        1        1  44555.0
            463  49000.0   2610.0         3        1        2  49000.0
            260  41000.0   6000.0         2        1        1  41000.0
            177  70000.0   5400.0         4        1        2  70000.0
            53   68000.0   9166.0         2        1        1  68000.0
            440  69000.0   6862.0         3        1        2  69000.0
            255  61000.0   4360.0         4        1        2  61000.0
            301  55000.0   4080.0         2        1        1  55000.0
            >>>

            # Example 2: Find the greatest values in the columns "price", "lotsize" and 70000.0.
            >>> gt_df = df.assign(gt_col=df.price.greatest(df.lotsize, 70000))
            >>> gt_df
                   price  lotsize  bedrooms  bathrms  stories   gt_col
            sn
            364  72000.0  10700.0         3        1        2  72000.0
            13   27000.0   1700.0         3        1        2  70000.0
            459  44555.0   2398.0         3        1        1  70000.0
            463  49000.0   2610.0         3        1        2  70000.0
            260  41000.0   6000.0         2        1        1  70000.0
            177  70000.0   5400.0         4        1        2  70000.0
            53   68000.0   9166.0         2        1        1  70000.0
            440  69000.0   6862.0         3        1        2  70000.0
            255  61000.0   4360.0         4        1        2  70000.0
            301  55000.0   4080.0         2        1        1  70000.0
            >>>

        """
        cols = self._get_sql_columns(*columns)

        return _SQLColumnExpression(func.greatest(*cols),
                                    type=cols[0].type)

    @collect_queryband(queryband="DFC_least")
    def least(self, *columns):
        """
        DESCRIPTION:
            Get the least values from the given columns.
            Note:
                * All of the input columns type must be of same data
                  type or else the types must be compatible.

        PARAMETERS:
            *columns:
                Specifies the name(s) of the columns or ColumnExpression(s)
                as positional arguments.
                At least one positional argument is required.
                Types: str or int or float or ColumnExpression OR ColumnExpressions

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("glmpredict", "housing_test")
            >>>

            # Create a DataFrame on 'housing_test' table.
            >>> df = DataFrame("housing_test")
            >>> df = df.select(["sn", "price", "lotsize", "bedrooms", "bathrms", "stories"])
            >>> df
                   price  lotsize  bedrooms  bathrms  stories
            sn
            364  72000.0  10700.0         3        1        2
            13   27000.0   1700.0         3        1        2
            459  44555.0   2398.0         3        1        1
            463  49000.0   2610.0         3        1        2
            260  41000.0   6000.0         2        1        1
            177  70000.0   5400.0         4        1        2
            53   68000.0   9166.0         2        1        1
            440  69000.0   6862.0         3        1        2
            255  61000.0   4360.0         4        1        2
            301  55000.0   4080.0         2        1        1
            >>>

            # Example 1: Find the least values in the columns "price" and "lotsize".
            >>> lt_df = df.assign(lt_col=df.price.least(df.lotsize))
            >>> lt_df
                   price  lotsize  bedrooms  bathrms  stories   lt_col
            sn
            364  72000.0  10700.0         3        1        2  10700.0
            13   27000.0   1700.0         3        1        2   1700.0
            459  44555.0   2398.0         3        1        1   2398.0
            463  49000.0   2610.0         3        1        2   2610.0
            260  41000.0   6000.0         2        1        1   6000.0
            177  70000.0   5400.0         4        1        2   5400.0
            53   68000.0   9166.0         2        1        1   9166.0
            440  69000.0   6862.0         3        1        2   6862.0
            255  61000.0   4360.0         4        1        2   4360.0
            301  55000.0   4080.0         2        1        1   4080.0
            >>>

            # Example 2: Find the least values in the columns "price", "lotsize" and 70000.0.
            >>> lt_df = df.assign(lt_col=df.price.least(df.lotsize, 70000))
            >>> lt_df
                   price  lotsize  bedrooms  bathrms  stories   lt_col
            sn
            260  41000.0   6000.0         2        1        1   6000.0
            38   67000.0   5170.0         3        1        4   5170.0
            364  72000.0  10700.0         3        1        2  10700.0
            301  55000.0   4080.0         2        1        1   4080.0
            459  44555.0   2398.0         3        1        1   2398.0
            177  70000.0   5400.0         4        1        2   5400.0
            53   68000.0   9166.0         2        1        1   9166.0
            440  69000.0   6862.0         3        1        2   6862.0
            13   27000.0   1700.0         3        1        2   1700.0
            469  55000.0   2176.0         2        1        2   2176.0
            >>>

        """
        cols = self._get_sql_columns(*columns)

        return _SQLColumnExpression(func.least(*cols),
                                    type=cols[0].type)

    @collect_queryband(queryband="DFC_cbrt")
    def cbrt(self):
        """
        DESCRIPTION:
            Function to compute cube root of the column.
            Note:
                Function computes cuberoot for column only when it's values are positive.
                Else, the function fails.

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml","titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            265         NaN    7.7500
            530        23.0   11.5000
            122         NaN    8.0500
            591        35.0    7.1250
            387         1.0   46.9000
            734        23.0   13.0000
            795        25.0    7.8958
            >>>

            # Example 1: Compute cuberoot values in "fare" and pass it as input to
            #           DataFrame.assign().
            >>> cbrt_df = df.assign(fare_cbrt=df.fare.cbrt())
            >>> print(cbrt_df)
                        age      fare  fare_cbrt
            passenger
            326        36.0  135.6333   5.137937
            183         9.0   31.3875   3.154416
            652        18.0   23.0000   2.843867
            40         14.0   11.2417   2.240151
            774         NaN    7.2250   1.933211
            366        30.0    7.2500   1.935438
            509        28.0   22.5250   2.824153
            795        25.0    7.8958   1.991279
            61         22.0    7.2292   1.933586
            469         NaN    7.7250   1.976816
            >>>
        """
        return (self.ln()/3).exp()

    @collect_queryband(queryband="DFC_hex")
    def hex(self):
        """
        DESCRIPTION:
            Function to compute the Hexadecimal from decimal for the column.

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml","titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            265         NaN    7.7500
            530        23.0   11.5000
            122         NaN    8.0500
            591        35.0    7.1250
            387         1.0   46.9000
            734        23.0   13.0000
            795        25.0    7.8958
            >>>

            # Example 1: Converts values in "age" decimal to hexadecimal and pass it as input to
            #            DataFrame.assign().
            >>> hex_df = df.assign(age_in_hex=df.age.hex())
            >>> print(hex_df)
                        age    fare age_in_hex
            passenger
            530        23.0  11.500         17
            591        35.0   7.125         23
            387         1.0  46.900          1
            856        18.0   9.350         12
            244        22.0   7.125         16
            713        48.0  52.000         30
            448        34.0  26.550         22
            122         NaN   8.050       None
            734        23.0  13.000         17
            265         NaN   7.750       None
            >>>
        """
        return self.to_byte('base10').from_byte('base16')

    @collect_queryband(queryband="DFC_unhex")
    def unhex(self):
        """
        DESCRIPTION:
            Function to compute the decimal from Hexadecimal for the column.

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml","titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            265         NaN    7.7500
            530        23.0   11.5000
            122         NaN    8.0500
            591        35.0    7.1250
            387         1.0   46.9000
            734        23.0   13.0000
            795        25.0    7.8958
            >>>

            # create a "age_in_hex" column which contains hexadecimal values
            >>> hex_df = df.assign(age_in_hex=df.age.hex())
            >>> print(hex_df)
                        age    fare age_in_hex
            passenger
            530        23.0  11.500         17
            591        35.0   7.125         23
            387         1.0  46.900          1
            856        18.0   9.350         12
            244        22.0   7.125         16
            713        48.0  52.000         30
            448        34.0  26.550         22
            122         NaN   8.050       None
            734        23.0  13.000         17
            265         NaN   7.750       None
            >>>

            # Example 1: Converts values in "age_in_hex" hexadecimal to decimal and pass it as input to
            #            DataFrame.assign().
            >>> unhex_df = hex_df.assign(age_in_decimal=hex_df.age_in_hex.unhex())
            >>> print(unhex_df)
                        age      fare age_in_hex age_in_decimal
            passenger
            326        36.0  135.6333         24             36
            183         9.0   31.3875          9              9
            652        18.0   23.0000         12             18
            40         14.0   11.2417          E             14
            774         NaN    7.2250       None           None
            366        30.0    7.2500         1E             30
            509        28.0   22.5250         1C             28
            795        25.0    7.8958         19             25
            61         22.0    7.2292         16             22
            469         NaN    7.7250       None           None
            >>>
        """
        return  self.to_byte('base16').from_byte('base10')

    @collect_queryband(queryband="DFC_toByte")
    def to_byte(self, encoding='base10'):
        """
        DESCRIPTION:
            The function decodes a sequence of characters in a given
            encoding into a sequence of bits.
            Note:
                * By default, consider DataFrame column as 'base10' and encodes
                  into a sequence of bits.

        PARAMETERS:
            encoding:
                Optional Argument.
                Specifies encoding "to_byte" uses to return the sequence of characters
                specified by column.
                The following encodings are supported:
                    * BaseX
                    * BaseY
                    * Base64M (MIME)
                    * ASCII
                    where X is a power of 2 (for example, 2, 8, 16) and
                    Y is not a power of 2 (for example, 10 and 36).
                Default Value: 'base10'
                Types: str

        Returns:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "bytes_table")

            # Create a DataFrame on 'bytes_table' table.
            >>> df = DataFrame("bytes_table")
            >>> print(df)
                   byte_col      varbyte_col             blob_col
            id_col
            2         b'61'  b'616263643132'  b'6162636431323233'
            1         b'62'      b'62717765'  b'3331363136323633'
            0         b'63'      b'627A7863'  b'3330363136323633'

            # Example 1: Converts values in "id_col" to bytes and pass it as input to
            #           DataFrame.assign().
            >>> byte_df = df.assign(byte_col = df.id_col.to_byte())
            >>> print(byte_df)
                    byte_col      varbyte_col             blob_col   byte_col
            id_col
            2         b'61'      b'627A7863'  b'6162636431323233...'  b'2'
            1         b'62'  b'616263643132'  b'3331363136323633...'  b'1'
            0         b'63'      b'62717765'  b'3330363136323633...'   b''
            >>>
        """
        arg_validate = []
        arg_validate.append(["encoding", encoding, True, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)

        expression_=self.expression
        if not isinstance(self.type, VARCHAR):
            expression_ = self.cast(type_=VARCHAR).expression

        expression_=func.to_bytes(expression_, encoding)
        return  _SQLColumnExpression(expression_, type=VARBYTE())

    @collect_queryband(queryband="DFC_fromByte")
    def from_byte(self, encoding='base10'):
        """
        DESCRIPTION:
            The function encodes a sequence of bits into a sequence of characters.
            Note:
                * By default it converts a sequence of bits to 'base10', which is decimal.

        PARAMETERS:
            encoding:
                Optional Argument.
                Specifies encoding "from_byte" uses to encode the sequence of characters
                specified by column.
                The following encodings are supported:
                    * BaseX
                    * BaseY
                    * Base64M (MIME)
                    * ASCII
                    where X is a power of 2 (for example, 2, 8, 16) and
                    Y is not a power of 2 (for example, 10 and 36).
                Default Value: 'base10'
                Types: str

        Returns:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "bytes_table")

            # Create a DataFrame on 'bytes_table' table.
            >>> df = DataFrame("bytes_table")
            >>> print(df)
                   byte_col      varbyte_col             blob_col
            id_col
            2         b'61'  b'616263643132'  b'6162636431323233'
            1         b'62'      b'62717765'  b'3331363136323633'
            0         b'63'      b'627A7863'  b'3330363136323633'

            # Example 1: Converts values in "byte_col" to decimal and pass it as input to
            #           DataFrame.assign().
            >>> decimal_df = df.assign(decimal_col = df.byte_col.from_byte())
            >>> print(decimal_df)
                    byte_col      varbyte_col             blob_col decimal_col
            id_col
            2         b'61'      b'627A7863'  b'6162636431323233...'  97
            1         b'62'  b'616263643132'  b'3331363136323633...'  98
            0         b'63'      b'62717765'  b'3330363136323633...'  99
            >>>
        """
        arg_validate = []
        arg_validate.append(["encoding", encoding, True, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)
        expression_=func.from_bytes(self.expression, encoding)
        return  _SQLColumnExpression(expression_, type=VARCHAR())

    @collect_queryband(queryband="DFC_hypot")
    def hypot(self, other):
        """
        DESCRIPTION:
            Function to compute the hypotenuse.

        PARAMETERS:
            other:
                Required Argument.
                Specifies DataFrame column for calculation of hypotenuse.
                Types: int or float or str or ColumnExpression

        Returns:
            ColumnExpression

        Examples:
            # Load the data to run the example.
            >>> load_example_data("teradataml","titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            265         NaN    7.7500
            530        23.0   11.5000
            122         NaN    8.0500
            591        35.0    7.1250
            387         1.0   46.9000
            734        23.0   13.0000
            795        25.0    7.8958
            >>>

            # Example 1: compute hypotenuse of two columns fare and age.
            >>> hypot_df = df.assign(hypot_column=df.fare.hypot(titanic.age))
            >>> print(hypot_df)
                        age      fare  hypot_column
            passenger
            326        36.0  135.6333    140.329584
            183         9.0   31.3875     32.652338
            652        18.0   23.0000     29.206164
            40         14.0   11.2417     17.954827
            774         NaN    7.2250           NaN
            366        30.0    7.2500     30.863611
            509        28.0   22.5250     35.935715
            795        25.0    7.8958     26.217240
            61         22.0    7.2292     23.157317
            469         NaN    7.7250           NaN
            >>>
        """
        arg_validate = []
        arg_validate.append(["other", other, False, (int, float, str, ColumnExpression), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)

        if isinstance(other, str):
            other = getattr(self._parent_df, other)

        return ((self * self) + (other * other)).sqrt()

    def format(self, formatter):
        """
        DESCRIPTION:
            Function to format the values in column based on formatter.

        PARAMETERS:
            formatter:
                Required Argument.
                Specifies a variable length string containing formatting characters
                that define the display format for the data type.
                Formats can be specified for columns that have character, numeric, byte,
                DateTime, Period or UDT data types.
                Note:
                    If the "formatter" does not include a sign character or a signed zoned decimal character,
                    then the sign for a negative value is discarded and the output is displayed as a positive
                    number.

                Types: str

                Following tables provide information about different formatters on numeric and
                date/time type columns:
                      The formatting characters determine whether the output of numeric data is considered
                      to be monetary or non-monetary. Numeric information is considered to be monetary if the
                      "formatter" contains a currency symbol.
                      Note:
                          Formatting characters are case insensitive.
                      The result of a formatted numeric string is right-justified.
                    +--------------------------------------------------------------------------------------------------+
                    |    formatter                                   description                                       |
                    +--------------------------------------------------------------------------------------------------+
                    |    G              Invokes the currency grouping rule defined by CurrencyGroupingRule in the SDF. |
                    |                   The value of CurrencyGroupSeparator in the current SDF is copied to the output |
                    |                   string to separate groups of digits to the left of the currency radix separator|
                    |                   ,according to the currency grouping rule defined by CurrencyGroupingRule.      |
                    |                   Grouping applies to only the integer portion of floating numbers.              |
                    |                   The G must appear as the first character in a "formatter".                     |
                    |                   A currency character, such as L or C, must also appear in the "formatter".     |
                    |                   If the "formatter" does not contain the letter G, no grouping is               |
                    |                   done on the output string.                                                     |
                    |                   The G cannot appear in a "formatter" that contains any of the following        |
                    |                   characters:                                                                    |
                    |                       * ,                                                                        |
                    |                       * .                                                                        |
                    |                       * /                                                                        |
                    |                       * :                                                                        |
                    |                       * S                                                                        |
                    |                   Examples:                                                                      |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    -12345678.90       'G--(8)D9(2)'         -12,345,678.90    |          |
                    |                       |    1234567890         'G-(10)9'             1.234.567.890     |          |
                    |                       |    9988.77            'GLLZ(I)D9(F)'        $9,988.77         |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    /              Insertion characters.                                                          |
                    |                                                                                                  |
                    |    :              Copied to output string where they appear in the "formatter".                  |
                    |                                                                                                  |
                    |    %              The % insertion character cannot appear in a "formatter" that contains S,      |
                    |                   and cannot appear between digits in a "formatter" that contains G, D, or E.    |
                    |                   For example, GL9999D99% is valid, but L9(9)D99%E999 is not.                    |
                    |                                                                                                  |
                    |                   The / and : insertion characters cannot appear in a "formatter" that           |
                    |                   contains any of the following characters:                                      |
                    |                        * G                                                                       |
                    |                        * D                                                                       |
                    |                        * S                                                                       |
                    |                   Examples:                                                                      |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    1234567891         '9(8)/9(2)'           12345678/91       |          |
                    |                       |    1234567891         '9(8):9(2)'           12345678:91       |          |
                    |                       |    1234567891         '9(8)%9(2)'           12345678%91       |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    B             Insertion character.                                                            |
                    |                  A blank space is copied to the output string wherever a B appears in the FORMAT |
                    |                  phrase.                                                                         |
                    |                  B cannot appear between digits in a "formatter" that contains G, D, or E.       |
                    |                  For example, GNB99D99 is valid, but G9(9)BD99 is not.                           |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    998877.66         '-Z(I)BN'              998878 US Dollars |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    +             Sign characters.                                                                |
                    |                                                                                                  |
                    |    -             These characters can appear at the beginning or end of a format string,         |
                    |                  but cannot appear between Z or 9 characters, or between repeated currency       |
                    |                  characters. One sign character places the edit character in a fixed position    |
                    |                  for the output string.                                                          |
                    |                  If two or more of these characters are present, the sign floats (moves to the   |
                    |                  position just to the left of the number as determined by the stated structure). |
                    |                  Repeated sign characters must appear to the left of formatting characters       |
                    |                  consisting of a combination of the radix and any 9 formatting characters.       |
                    |                                                                                                  |
                    |                  If a group of repeated sign characters appears in a "formatter" with a group    |
                    |                  of repeated Z characters or a group of repeated currency characters or both, the|
                    |                  groups must be contiguous. For example, +++$$$ZZZ.                              |
                    |                  One trailing sign character can occur to the right of any digits, and can       |
                    |                  combine with B and one currency character or currency sign. For example,        |
                    |                  G9(I)B+L. The trailing sign character for a mantissa cannot appear to the right |
                    |                  of the exponent.                                                                |
                    |                  For example, 999D999E+999+ is invalid.                                          |
                    |                                                                                                  |
                    |                  The + translates to + or - as appropriate; the - translates to - or blank.      |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    0034567890         '--(8)D9(2)'           34567890.00      |          |
                    |                       |    -0034567890        '++(8)D9(2)'          -34567890.00      |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |    $             Currency signs:                                                                 |
                    |                  * $ means Dollar sign.                                                          |
                    |    £             * £ means Pound sterling.                                                       |
                    |                  * ¥ means Yen sign.                                                             |
                    |    ¥             * ¤ means general currency sign.                                                |
                    |                                                                                                  |
                    |    ¤             A currency sign cannot appear between Z or 9 formatting characters, or between  |
                    |                  repeated sign characters.                                                       |
                    |                  One currency sign places the edit character in a fixed position for the output  |
                    |                  string.                                                                         |
                    |                  If a result is formatted using a single currency sign with Zs for               |
                    |                  zero-suppressed decimal digits (for example, £ZZ9.99), blanks can occur between |
                    |                  the currency sign and the leftmost nonzero digit of the number.                 |
                    |                                                                                                  |
                    |                  If the same currency sign appears more than once, the sign floats to the right, |
                    |                  leaving no blanks between it and the leftmost digit.                            |
                    |                                                                                                  |
                    |                  A currency sign cannot appear in the same phrase with a currency character,     |
                    |                  such as L.                                                                      |
                    |                  If + or - is present, the currency character cannot precede it.                 |
                    |                                                                                                  |
                    |                  If a group of repeated currency signs appears in a "formatter" with a group of  |
                    |                  repeated sign characters or a group of repeated Z characters or both, the groups|
                    |                  must be contiguous. For example, +++$$$ZZZ.                                     |
                    |                                                                                                  |
                    |                  One currency sign can occur to the right of any digits, and can combine with B  |
                    |                  and one trailing sign character. For example, G9(I)B+$.                         |
                    |                                                                                                  |
                    |                  A currency sign cannot appear to the right of an exponent. For example,         |
                    |                  999D999E+999B+$ is invalid.                                                     |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    1                 '$(5).9(2)'            $1.00             |          |
                    |                       |    .069              '$$9.99'               $0.07             |          |
                    |                       |    1095              '$$9.99'               ******            |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    L             Currency characters.                                                            |
                    |                  The value of the corresponding currency string in the current SDF is copied to  |
                    |    C             the output string whenever the character appears in the "formatter".            |
                    |                      * L in a "formatter" is interpreted as the currency symbol and the value    |
                    |    N                   of the Currency string in the SDF is copied to the output string.         |
                    |                      * C in a "formatter" is interpreted as the ISO currency symbol and the      |
                    |    O                   value of the ISOCurrency string in the SDF is copied to the output        |
                    |                        string.                                                                   |
                    |                      * N in a "formatter" is interpreted as the full currency name, such as Yen  |
                    |    U                   or Kroner, and the value of the CurrencyName string in the SDF is copied  |
                    |                        to the output string.                                                     |
                    |    A                 * O in a "formatter" is interpreted as the dual currency symbol and the     |
                    |                        value of the DualCurrency string in the SDF is copied to the output       |
                    |                        string.                                                                   |
                    |                      * U in a "formatter" is interpreted as the dual ISO currency symbol and     |
                    |                        the value of the DualISOCurrency string in the SDF is copied to the       |
                    |                        output string.                                                            |
                    |                      * A in a "formatter" is interpreted as the full dual currency name,         |
                    |                        such as Euro, and the value of the DualCurrencyName string in the SDF     |
                    |                        is copied to the output string.                                           |
                    |                                                                                                  |
                    |                  A currency character cannot appear between Z or 9 formatting characters, or     |
                    |                  between repeated sign characters.                                               |
                    |                  If the same currency character appears more than once, the value that is        |
                    |                  copied to the output string floats to the right, leaving no blanks between it   |
                    |                  and the leftmost digit. Repeated characters must be contiguous, and must appear |
                    |                  to the left formatting characters consisting of a combination of the radix and  |
                    |                  any 9 formatting characters.                                                    |
                    |                                                                                                  |
                    |                  If a group of repeated currency characters appears in a "formatter" with a      |
                    |                  group of repeated sign characters or a group of repeated Z characters or both,  |
                    |                  the groups must be contiguous. For example, +++LLLZZZ.                          |
                    |                  A currency character cannot appear in the same phrase with any of the following |
                    |                  characters:                                                                     |
                    |                      * other currency characters                                                 |
                    |                      * a currency sign, such as $ or £                                           |
                    |                      * ,                                                                         |
                    |                      * .                                                                         |
                    |                  One currency character can occur to the right of any digits, and can combine    |
                    |                  with B and one trailing sign character. For example, G9(I)B+L.                  |
                    |                                                                                                  |
                    |                  A currency character cannot appear to the right of an exponent. For example,    |
                    |                  999D999E+999B+L is invalid.                                                     |
                    |                  Examples:                                                                       |
                    |                       +----------------------------------------------------------------+         |
                    |                       |    data               formatter             result             |         |
                    |                       +----------------------------------------------------------------+         |
                    |                       |    9988.77            'GLLZ(I)D9(F)'        $9,988.77          |         |
                    |                       |    9988.77            'GCBZ(4)D9(F)'        USD 9,988.77       |         |
                    |                       |    9988.77            'GNBZ(4)D9(F)'        US Dollars 9,988.77|         |
                    |                       +----------------------------------------------------------------+         |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    V             Implied decimal point position.                                                 |
                    |                  Internally, the V is recognized as a decimal point to align the numeric value   |
                    |                  properly for calculation.                                                       |
                    |                  Because the decimal point is implied, it does not occupy any space in storage   |
                    |                  and is not included in the output.                                              |
                    |                  V cannot appear in a "formatter" that contains the 'D' radix symbol or          |
                    |                  the '.' radix character.                                                        |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    128.457            '999V99'              12846             |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    Z             Zero-suppressed decimal digit.                                                  |
                    |                  Translates to blank if the digit is zero and preceding digits are also zero.    |
                    |                                                                                                  |
                    |                  A Z cannot follow a 9.                                                          |
                    |                                                                                                  |
                    |                  Repeated Z characters must appear to the left of any combination of the radix   |
                    |                  and any 9 formatting characters.                                                |
                    |                                                                                                  |
                    |                  The characters to the right of the radix cannot be a combination of 9 and Z     |
                    |                  characters; they must be all 9s or all Zs. If they are all Zs, then the         |
                    |                  characters to the left of the radix must also be all Zs.                        |
                    |                                                                                                  |
                    |                  If a group of repeated Z characters appears in a "formatter" with a group of    |
                    |                  repeated sign characters, the group of Z characters must immediately follow     |
                    |                  the group of sign characters. For example, --ZZZ.                               |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    1.3451             'zz.z'                1.3               |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    9             Decimal digit (no zero suppress).                                               |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    0034567890         '9999999999'           0034567890       |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    E             For exponential notation.                                                       |
                    |                                                                                                  |
                    |                  Defines the end of the mantissa and the start of the exponent.                  |
                    |                                                                                                  |
                    |                  The exponent consists of one optional + or - sign character followed by one or  |
                    |                  more 9 formatting characters.                                                   |
                    |                  Examples:                                                                       |
                    |                       +-------------------------------------------------------------------+      |
                    |                       |    data                     formatter             result          |      |
                    |                       +-------------------------------------------------------------------+      |
                    |                       |1095                     '9.99E99'             1.10E03             |      |
                    |                       |1.74524064372835e-2 '-9D99999999999999E-999'  1.74524064372835E-002|      |
                    |                       +-------------------------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    CHAR(n)       For more than one occurrence of a character, where CHAR can be one of the       |
                    |                  following:                                                                      |
                    |                      * - (sign character)                                                        |
                    |                      * +                                                                         |
                    |                      * Z                                                                         |
                    |                      * 9                                                                         |
                    |                      * $                                                                         |
                    |                      * ¤                                                                         |
                    |                      * ¥                                                                         |
                    |                      * £                                                                         |
                    |                  and n can be:                                                                   |
                    |                      * an integer constant                                                       |
                    |                      * I                                                                         |
                    |                      * F                                                                         |
                    |                  If n is F, CHAR can only be Z or 9.                                             |
                    |                                                                                                  |
                    |                  If n is an integer constant, the (n) notation means that the character repeats n|
                    |                  number of times. For the meanings of I and F, see the definitions later in this |
                    |                  table.                                                                          |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    0034567890         'z(8)D9(2)'           34567890.00       |          |
                    |                       |    -0034567890        '+z(8)D9(2)'          -34567890.00      |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    ,             Currency grouping character.                                                    |
                    |                  The comma is inserted only if a digit has already appeared.                     |
                    |                                                                                                  |
                    |                  The comma is interpreted as the currency grouping character regardless of the   |
                    |                  value of the CurrencyGroupSeparator in the SDF.                                 |
                    |                                                                                                  |
                    |                  The comma cannot appear in a "formatter" that contains any of the following     |
                    |                  characters:                                                                     |
                    |                      * G                                                                         |
                    |                      * D                                                                         |
                    |                      * L                                                                         |
                    |                      * C                                                                         |
                    |                      * O                                                                         |
                    |                      * U                                                                         |
                    |                      * N                                                                         |
                    |                      * A                                                                         |
                    |                      * S                                                                         |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    0034567890         'z(7),z'              3456789,0         |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    .             Currency radix character.                                                       |
                    |                  The period is interpreted as the currency radix character, regardless of the    |
                    |                  value of the CurrencyRadixSeparator in the SDF, and is copied to the output     |
                    |                  string.                                                                         |
                    |                                                                                                  |
                    |                  The period cannot appear in a "formatter" that contains any of the following    |
                    |                  characters:                                                                     |
                    |                      * G                                                                         |
                    |                      * D                                                                         |
                    |                      * L                                                                         |
                    |                      * V                                                                         |
                    |                      * C                                                                         |
                    |                      * O                                                                         |
                    |                      * U                                                                         |
                    |                      * N                                                                         |
                    |                      * A                                                                         |
                    |                      * S                                                                         |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    0034567890         'z(8).z'              34567890.0        |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    D             Radix symbol.                                                                   |
                    |                  The value of CurrencyRadixSeparator in the current SDF is copied to the output  |
                    |                  string whenever a D appears in the "formatter".                                 |
                    |                  A currency symbol, such as a dollar sign or yen sign, must also appear in the   |
                    |                  "formatter".                                                                    |
                    |                  The D cannot appear in a "formatter" that contains any of the following         |
                    |                  characters:                                                                     |
                    |                      * ,                                                                         |
                    |                      * .                                                                         |
                    |                      * /                                                                         |
                    |                      * :                                                                         |
                    |                      * S                                                                         |
                    |                      * V                                                                         |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    0034567890         '--(8)D9(2)'           34567890.00      |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    I             The number of characters needed to display the integer portion of numeric and   |
                    |                  integer data.                                                                   |
                    |                                                                                                  |
                    |                  I can only appear as n in the CHAR(n) character sequence (see the definition of |
                    |                  CHAR(n) earlier in this table), where CHAR can be:                              |
                    |                      * - (sign character)                                                        |
                    |                      * +                                                                         |
                    |                      * Z                                                                         |
                    |                      * 9                                                                         |
                    |                      * $                                                                         |
                    |                      * ¤                                                                         |
                    |                      * ¥                                                                         |
                    |                      * £                                                                         |
                    |                  CHAR(I) can only appear once, and is valid for the following types:             |
                    |                      * DECIMAL/NUMERIC                                                           |
                    |                      * BYTEINT                                                                   |
                    |                      * SMALLINT                                                                  |
                    |                      * INTEGER                                                                   |
                    |                      * BIGINT                                                                    |
                    |                 The value of I is resolved during the formatting of the monetary numeric data.   |
                    |                 The value is obtained from the declaration of the data type. For example, I is   |
                    |                 eight for the DECIMAL(10,2) type.                                                |
                    |                                                                                                  |
                    |                 If CHAR(F) also appears in the "formatter", CHAR(F) must appear to the right of  |
                    |                 CHAR(I), and one of the following characters must appear between CHAR(I) and     |
                    |                 CHAR(F):                                                                         |
                    |                     * D                                                                          |
                    |                     * .                                                                          |
                    |                     * V                                                                          |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    000000.42         'Z(I)D9(F)'            .42               |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |    F             The number of characters needed to display the fractional portion of            |
                    |                  numeric data.                                                                   |
                    |                  F can only appear as n in the CHAR(n) character sequence                        |
                    |                  (see the definition of CHAR(n) earlier in this table),                          |
                    |                  where CHAR can be:                                                              |
                    |                      * Z                                                                         |
                    |                      * 9                                                                         |
                    |                  CHAR(F) is valid for the DECIMAL/NUMERIC data type.                             |
                    |                                                                                                  |
                    |                  The value of F is resolved during the formatting of the monetary numeric data.  |
                    |                  The value is obtained from the declaration of the data type. For example,       |
                    |                  F is two for the DECIMAL(10,2) type.                                            |
                    |                                                                                                  |
                    |                  A value of zero for F displays no fractional precision for the data; however,   |
                    |                  the value of CurrencyRadixSeparator in the current SDF is copied to the output  |
                    |                  string if a D appears in the "formatter".                                       |
                    |                                                                                                  |
                    |                  CHAR(F) can appear only once. If CHAR(I) also appears in the "formatter",       |
                    |                  CHAR(F) must appear to the right of CHAR(I), and one of the following characters|
                    |                  must appear between CHAR(I) and CHAR(F):                                        |
                    |                      * D                                                                         |
                    |                      * .                                                                         |
                    |                      * V                                                                         |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    000000.42         'Z(I)D9(F)'            .42               |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    -             Dash character.                                                                 |
                    |                  Used when storing numbers such as telephone numbers, social security numbers,   |
                    |                  and account numbers.                                                            |
                    |                                                                                                  |
                    |                  A dash appears after the first digit and before the last digit, and is treated  |
                    |                  as an embedded dash rather than a sign character. A dash cannot follow any of   |
                    |                  these characters:                                                               |
                    |                      * .                                                                         |
                    |                      * ,                                                                         |
                    |                      * +                                                                         |
                    |                      * G                                                                         |
                    |                      * N                                                                         |
                    |                      * A                                                                         |
                    |                      * C                                                                         |
                    |                      * L                                                                         |
                    |                      * O                                                                         |
                    |                      * U                                                                         |
                    |                      * D                                                                         |
                    |                      * V                                                                         |
                    |                      * S                                                                         |
                    |                      * E                                                                         |
                    |                      * $                                                                         |
                    |                      * ¤                                                                         |
                    |                      * £                                                                         |
                    |                      * ¥                                                                         |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    0034567890         '--(8)D9(2)'           34567890.00      |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    S             Signed Zoned Decimal character.                                                 |
                    |                  Defines signed zoned decimal input as a numeric data type and displays numeric  |
                    |                  output as signed zone decimal character strings.                                |
                    |                                                                                                  |
                    |                  When converting signed zone decimal input to a numeric data type, the final     |
                    |                  character is converted as follows:                                              |
                    |                  * Last character = { or 0, then the numeric conversion is n … 0                 |
                    |                  * Last character = A or 1, then the numeric conversion is n … 1                 |
                    |                  * Last character = B or 2, then the numeric conversion is n … 2                 |
                    |                  * Last character = C or 3, then the numeric conversion is n … 3                 |
                    |                  * Last character = D or 4, then the numeric conversion is n … 4                 |
                    |                  * Last character = E or 5, then the numeric conversion is n … 5                 |
                    |                  * Last character = F or 6, then the numeric conversion is n … 6                 |
                    |                  * Last character = G or 7, then the numeric conversion is n … 7                 |
                    |                  * Last character = H or 8, then the numeric conversion is n … 8                 |
                    |                  * Last character = I or 9, then the numeric conversion is n … 9                 |
                    |                  * Last character = }, then the numeric conversion is -n … 0                     |
                    |                  * Last character = J, then the numeric conversion is -n … 1                     |
                    |                  * Last character = K, then the numeric conversion is -n … 2                     |
                    |                  * Last character = L, then the numeric conversion is -n … 3                     |
                    |                  * Last character = M, then the numeric conversion is -n … 4                     |
                    |                  * Last character = N, then the numeric conversion is -n … 5                     |
                    |                  * Last character = O, then the numeric conversion is -n … 6                     |
                    |                  * Last character = P, then the numeric conversion is -n … 7                     |
                    |                  * Last character = Q, then the numeric conversion is -n … 8                     |
                    |                  * Last character = R, then the numeric conversion is -n … 9                     |
                    |                                                                                                  |
                    |                  When displaying numeric output as signed zone decimal character strings,        |
                    |                  the final character indicates the sign, as follows:                             |
                    |                                                                                                  |
                    |                  If the final data digit is 0, then the final result digit is displayed as:      |
                    |                  * { if the result is a positive number                                          |
                    |                  * } if the result is a negative number                                          |
                    |                  If the final data digit is 1, then the final result digit is displayed as:      |
                    |                  * A if the result is a positive number                                          |
                    |                  * J if the result is a negative number                                          |
                    |                  If the final data digit is 2, then the final result digit is displayed as:      |
                    |                  * B if the result is a positive number                                          |
                    |                  * K if the result is a negative number                                          |
                    |                  If the final data digit is 3, then the final result digit is displayed as:      |
                    |                  * C if the result is a positive number                                          |
                    |                  * L if the result is a negative number                                          |
                    |                  If the final data digit is 4, then the final result digit is displayed as:      |
                    |                  * D if the result is a positive number                                          |
                    |                  * M if the result is a negative number                                          |
                    |                  If the final data digit is 5, then the final result digit is displayed as:      |
                    |                  * E if the result is a positive number                                          |
                    |                  * N if the result is a negative number                                          |
                    |                  If the final data digit is 6, then the final result digit is displayed as:      |
                    |                  * F if the result is a positive number                                          |
                    |                  * O if the result is a negative number                                          |
                    |                  If the final data digit is 7, then the final result digit is displayed as:      |
                    |                  * G if the result is a positive number                                          |
                    |                  * P if the result is a negative number                                          |
                    |                  If the final data digit is 8, then the final result digit is displayed as:      |
                    |                  * H if the result is a positive number                                          |
                    |                  * Q if the result is a negative number                                          |
                    |                  If the final data digit is 9, then the final result digit is displayed as:      |
                    |                  * I if the result is a positive number                                          |
                    |                  * R if the result is a negative number                                          |
                    |                                                                                                  |
                    |                  The S must follow the last decimal digit in the "formatter". It cannot appear   |
                    |                  in the same phrase with the following characters.                               |
                    |                    * %                                                                           |
                    |                    * +                                                                           |
                    |                    * :                                                                           |
                    |                    * /                                                                           |
                    |                    * -                                                                           |
                    |                    * ,                                                                           |
                    |                    * .                                                                           |
                    |                    * Z                                                                           |
                    |                    * E                                                                           |
                    |                    * D                                                                           |
                    |                    * G                                                                           |
                    |                    * F                                                                           |
                    |                    * N                                                                           |
                    |                    * A                                                                           |
                    |                    * C                                                                           |
                    |                    * L                                                                           |
                    |                    * U                                                                           |
                    |                    * O                                                                           |
                    |                    * $                                                                           |
                    |                    * ¤                                                                           |
                    |                    * £                                                                           |
                    |                    * ¥                                                                           |
                    |                  Examples:                                                                       |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    data               formatter             result            |          |
                    |                       +---------------------------------------------------------------+          |
                    |                       |    -1095              '99999S'              0109N             |          |
                    |                       |    1095               '99999S'              0109E             |          |
                    |                       +---------------------------------------------------------------+          |
                    +--------------------------------------------------------------------------------------------------+

                    A "formatter" that defines fewer positions than are required by numeric values causes
                    the data to be returned as follows:
                        * Asterisks appear when the integer portion cannot be accommodated.
                        * When only the integer portion can be accommodated, any digits to the right of the least
                        significant digit are either truncated (for an integer value) or rounded (for a floating,
                        number, or decimal value).

                    Rounding is based on “Round to the Nearest” mode, as illustrated by the following process.
                        * Let B represent the actual result.
                        * Let A and C represent the nearest bracketing values that can be represented, such that
                          A < B < C.
                        * The determination as to whether A or C is the represented result is made as follows:
                            * When possible, the result is the value nearest to B.
                            * If A and C are equidistant (for example, the fractional part is exactly .5),
                              the result is the even number.


                * Date type FORMAT to SPECIFIC FORMAT
                  The date and time formatting characters in a "formatter" determine the output of
                  DATE, TIME, and TIMESTAMP teradatasqlalchemy types information.

                Following tables provide information about different formatters on
                date type columns:
                    +--------------------------------------------------------------------------------------------------+
                    |    formatter                                          description                                |
                    +--------------------------------------------------------------------------------------------------+
                    |    MMMM                                Represent the month as a full month name, such as         |
                    |                                        November.                                                 |
                    |    M4                                  Valid names are specified by LongMonths in the            |
                    |                                        current SDF.                                              |
                    |                                        M4 is equivalent to MMMM, and is preferable to allow for a|
                    |                                        shorter, unambiguous format string.                       |
                    |                                                                                                  |
                    |                                        You cannot specify M4 in a format that also has M3 or MM. |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4'           JANUARY              | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    MMM                                 Represent the month as an abbreviated month name, such as |
                    |                                        'Apr' for April.                                          |
                    |    M3                                  Valid names are specified by ShortMonths in the current   |
                    |                                        SDF.                                                      |
                    |                                                                                                  |
                    |                                        M3 is equivalent to MMM, and is preferable to allow for a |
                    |                                        shorter, unambiguous format string.                       |
                    |                                                                                                  |
                    |                                        You cannot specify MMM in a format that also has MM.      |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4'           Jan                  | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    MM                                  Represent the month as two numeric digits.                |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'MM'           01                   | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    DDD                                 Represent the date as the sequential day in the year,     |
                    |                                        using three numeric digits, such as '032' as February 1.  |
                    |                                                                                                  |
                    |    D3                                  D3 is equivalent to DDD, and allows for a shorter format  |
                    |                                        string.                                                   |
                    |                                        You cannot specify DDD or D3 in a format that also has DD.|
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/02/13       'D3'           044                  | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    DD                                  Represent the day of the month as two numeric digits.     |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'DD'           16                   | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    YYYY                                Represent the year as four numeric digits.                |
                    |                                                                                                  |
                    |    Y4                                  Y4 is equivalent to YYYY, and allows for a shorter format |
                    |                                        string.                                                   |
                    |                                                                                                  |
                    |                                        You cannot specify YYYY or Y4 in a format that also has   |
                    |                                        YY.                                                       |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'Y4'           2019                 | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    YY                                  Represent the year as two numeric digits.                 |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'YY'           19                   | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    EEEE                                Represent the day of the week using the full name,        |
                    |                                        such as Thursday.                                         |
                    |                                                                                                  |
                    |    E4                                  Valid names are specified by LongDays in the current SDF. |
                    |                                                                                                  |
                    |                                        E4 is equivalent to EEEE, and allows for a shorter format |
                    |                                        string.                                                   |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'E4'           Wednesday            | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    EEE                                 Represent the day of the week as an abbreviated name, such|
                    |                                        as 'Mon' for Monday.                                      |
                    |    E3                                  Valid abbreviations are specified by ShortDays in the     |
                    |                                        current SDF.                                              |
                    |                                        E3 is equivalent to EEE, and allows for a shorter format  |
                    |                                        string.                                                   |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'E3'            Wed                 | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    /                                   Slash separator.                                          |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase.                                                   |
                    |                                        This is the default separator for Teradata dates.         |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4/E3'        January/Wed          | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    B                                   Blank representation separator.                           |
                    |                                                                                                  |
                    |    b                                   Use this instead of a space to represent a blank.         |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4BE3'        JANUARY Wed          | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    ,                                   Comma separator.                                          |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase.                                                   |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4,E3'        January,Wed          | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    :                                   Colon separator.                                          |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase.                                                   |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4:E3'        January:Wed          | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    .                                   Period separator.                                         |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase.                                                   |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4.E3'        January.Wed          | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    -                                   Dash separator.                                           |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase.                                                   |
                    |                                        This is the default separator for ANSI dates.             |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'M4-E3'        January-Wed          | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    9                                   Decimal digit.                                            |
                    |                                        This formatting character can only be used with separators|
                    |                                        less than 0x009F.                                         |
                    |                                                                                                  |
                    |                                        The 9(n) notation can be used for more than one occurrence|
                    |                                        of this character, where n is an integer constant and     |
                    |                                        means that the '9' repeats n number of times.             |
                    |                                                                                                  |
                    |                                        This formatting character is for DATE and PERIOD(DATE)    |
                    |                                        types only and cannot appear as a date formatting         |
                    |                                        character for PERIOD(TIMESTAMP) and TIMESTAMP types.      |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       '999999'       190116               | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    Z                                   Zero-suppressed decimal digit.                            |
                    |                                        This formatting character can only be used with separators|
                    |                                        less than 0x009F.                                         |
                    |                                                                                                  |
                    |                                        The Z(n) notation can be used for more than one occurrence|
                    |                                        of this character, where n is an integer constant and     |
                    |                                        means that the 'Z' repeats n number of times.             |
                    |                                                                                                  |
                    |                                        This formatting character is for DATE and PERIOD(DATE)    |
                    |                                        types only and cannot appear as a date formatting         |
                    |                                        character for PERIOD(TIMESTAMP) and TIMESTAMP types.      |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data           formatter      result               | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    19/01/16       'ZZZZZZ'       190116               | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+

                Following tables provide information about different formatters on
                time type columns:
                    +--------------------------------------------------------------------------------------------------+
                    |    formatter                                    description                                      |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    HH                                  Represent the hour as two numeric digits.                 |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                      formatter      result    | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 08:00:00.000000   'HH'           08        | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    MI                                  Represent the minute as two numeric digits.               |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HH:MI'        13:20    | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    SS                                  Represent the second as two numeric digits.               |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter   result      | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HH.MI.SS'  13.20.53    | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    S(n)                                Number of fractional seconds.                             |
                    |                                                                                                  |
                    |    S(F)                                Replace n with a number between 0 and 6, or use F for the |
                    |                                        number of characters needed to display the fractional     |
                    |                                        seconds precision.                                        |
                    |                                                                                                  |
                    |                                        The value of F is resolved during the formatting of the   |
                    |                                        TIME or TIMESTAMP data. The value is obtained from the    |
                    |                                        fractional seconds precision in the declaration of the    |
                    |                                        data type. For example, F is two for the TIME(2) type.    |
                    |                                                                                                  |
                    |                                        A value of zero for F displays no radix symbol and no     |
                    |                                        fractional precision for the data.                        |
                    |                                        The S(F) formatting characters must follow a D formatting |
                    |                                        character or a . separator character.                     |
                    |                                                                                                  |
                    |                                        A value of n that is less than the PERIOD(TIME),          |
                    |                                        PERIOD(TIMESTAMP), TIME or TIMESTAMP fractional second    |
                    |                                        precision produces an error.                              |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |2020-07-01 13:20:53.64+03:00:'HH:MI:SSDS(F)'13:20:53.64| |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    D                                   Radix symbol.                                             |
                    |                                        The value of RadixSeparator in the current SDF is copied  |
                    |                                        to the output string whenever a D appears in the FORMAT   |
                    |                                        phrase.                                                   |
                    |                                                                                                  |
                    |                                        Separator characters, such as . or :, can also appear in  |
                    |                                        the "formatter", but only if they do not match the value  |
                    |                                        of RadixSeparator.                                        |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |2020-07-01 13:20:53.64+03:00:'HH:MI:SSDS(F)'13:20:53.64| |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    T                                   Represent time in 12-hour format instead of 24-hour       |
                    |                                        format. The appropriate time of day, as specified by AMPM |
                    |                                        in the current SDF is copied to the output string         |
                    |                                        where a T appears in the "formatter".                     |
                    |                                                                                                  |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |2020-07-01 13:20:53.64+03:00:'HH:MI:SSBT'01:20:53 Nachm| |
                    |                                        |                              (Nachm is German for PM.)| |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    Z                                   Time zone.                                                |
                    |                                        The Z controls the placement of the time zone in the      |
                    |                                        output of PERIOD(TIME), PERIOD(TIMESTAMP), TIME and       |
                    |                                        TIMESTAMP data, and can only appear at the beginning or   |
                    |                                        end of the time formatting characters.                    |
                    |                                                                                                  |
                    |                                        For example, the following statement uses a "formatter"   |
                    |                                        that includes a Z before the time formatting characters:  |
                    |                                                                                                  |
                    |                                            SELECT CURRENT_TIMESTAMP                              |
                    |                                            (FORMAT 'YYYY-MM-DDBZBHH:MI:SS.S(6)');                |
                    |                                            If the PERIOD(TIME), PERIOD(TIMESTAMP), TIME or       |
                    |                                            TIMESTAMP teradatasqlalchemy types contains time zone |
                    |                                            data, the time zone is copied to the output string.   |
                    |                                            The time zone format  is +HH:MI or -HH:MI, depending  |
                    |                                            on the time zone hour displacement.                   |
                    |                                        Examples:                                                 |
                    |                                    +------------------------------------------------------------+|
                    |                                    |    data                       formatter         result     ||
                    |                                    +------------------------------------------------------------+|
                    |                                    |2020-07-01 13:20:53.64+03:00:  'HH:MI:SSDS(F)Z'  13:20:53.64||
                    |                                    |                                                      +03:00||
                    |                                    +------------------------------------------------------------+|
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    :                                   Colon separator.                                          |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase. This is the default separator for ANSI time.      |
                    |                                                                                                  |
                    |                                        This character cannot appear in the "formatter" if the    |
                    |                                        value of RadixSeparator in the current SDF is a colon.    |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HH:MI'        13:20    | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    .                                   Period separator.                                         |
                    |                                        This can also be used to indicate the fractional seconds. |
                    |                                                                                                  |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase.                                                   |
                    |                                                                                                  |
                    |                                        This character cannot appear in the "formatter" if the    |
                    |                                        value of RadixSeparator in the current SDF is a period.   |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter   result      | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HH.MI.SS'  13.20.53    | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    -                                   Dash separator.                                           |
                    |                                        Copied to output string where it appears in the FORMAT    |
                    |                                        phrase.                                                   |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HH-MI'        13-20    | |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    h                                   Hour separator.                                           |
                    |                                        A lowercase h character is copied to the output string.   |
                    |                                                                                                  |
                    |                                        The h formatting character must follow the HH formatting  |
                    |                                        characters.                                               |
                    |                                                                                                  |
                    |                                        This character cannot appear in the "formatter" if the    |
                    |                                        value of RadixSeparator in the current SDF is a lowercase |
                    |                                         h character.                                             |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HHhMImSSs'    13h20m53s| |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    m                                   Minute separator.                                         |
                    |                                        A lowercase m character is copied to the output string.   |
                    |                                                                                                  |
                    |                                        The m formatting character must follow the MI formatting  |
                    |                                        characters.                                               |
                    |                                                                                                  |
                    |                                        This character cannot appear in the "formatter" if the    |
                    |                                        value of RadixSeparator in the current SDF is a lowercase |
                    |                                        m character.                                              |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HHhMImSSs'    13h20m53s| |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    s                                   Second separator.                                         |
                    |                                        A lowercase s character is copied to the output string.   |
                    |                                                                                                  |
                    |                                        The s formatting character must follow SS or SSDS(F)      |
                    |                                        formatting characters.                                    |
                    |                                                                                                  |
                    |                                        This character cannot appear in the "formatter" if the    |
                    |                                        value of RadixSeparator in the current SDF is a lowercase |
                    |                                        s character.                                              |
                    |                                        Examples:                                                 |
                    |                                        +-------------------------------------------------------+ |
                    |                                        |    data                       formatter      result   | |
                    |                                        +-------------------------------------------------------+ |
                    |                                        | 2020-07-01 13:20:53.64+03:00: 'HHhMImSSs'    13h20m53s| |
                    |                                        +-------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+
                    |                                                                                                  |
                    |    B                                  Blank representation separator.                            |
                    |                                                                                                  |
                    |    b                                  Use this instead of a space to represent a blank.          |
                    |                                                                                                  |
                    |                                       This character cannot appear in the "formatter" if the     |
                    |                                       value of RadixSeparator in the current SDF is a blank.     |
                    |                                        Examples:                                                 |
                    |                                 +--------------------------------------------------------------+ |
                    |                                 | data                           formatter           result    | |
                    |                                 +--------------------------------------------------------------+ |
                    |                                 | 2020-07-01 13:20:53.64+03:00:  'MM/DD/YYBHH:MIBT'  07/01/20  | |
                    |                                 |                                                    01:20 PM  | |
                    |                                 +--------------------------------------------------------------+ |
                    +--------------------------------------------------------------------------------------------------+

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>> load_example_data("uaf", "stock_data")

            # Create a DataFrame on 'admissions_train' table.
            >>> admissions_train=DataFrame("admissions_train")
            >>> admissions_train
                masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            30     yes  3.79  Advanced      Novice         0
            28      no  3.93  Advanced    Advanced         1
            16      no  3.70  Advanced    Advanced         1
            9       no  3.82  Advanced    Advanced         1
            13      no  4.00  Advanced      Novice         1
            15     yes  4.00  Advanced    Advanced         1
            17      no  3.83  Advanced    Advanced         1
            >>>

            # Example 1: Round the 'age' column upto 1 decimal values.
            >>> format_df = admissions_train.assign(format_column=admissions_train.gpa.format("zz.z"))
            >>> format_df
                masters   gpa     stats programming  admitted format_column
            id
            38     yes  2.65  Advanced    Beginner         1           2.6
            7      yes  2.33    Novice      Novice         1           2.3
            26     yes  3.57  Advanced    Advanced         1           3.6
            5       no  3.44    Novice      Novice         0           3.4
            3       no  3.70    Novice    Beginner         1           3.7
            22     yes  3.46    Novice    Beginner         0           3.5
            24      no  1.87  Advanced      Novice         1           1.9
            36      no  3.00  Advanced      Novice         0           3.0
            19     yes  1.98  Advanced    Advanced         0           2.0
            40     yes  3.95    Novice    Beginner         0           4.0
            >>>



            # Create a DataFrame on 'stock_data' table.
            >>> stock_data=DataFrame("stock_data")
            >>> stock_data
                         seq_no timevalue  magnitude
            data_set_id
            556               3  19/01/16     61.080
            556               5  19/01/30     63.810
            556               6  19/02/06     63.354
            556               7  19/02/13     63.871
            556               9  19/02/27     61.490
            556              10  19/03/06     61.524
            556               8  19/02/20     61.886
            556               4  19/01/23     63.900
            556               2  19/01/09     61.617
            556               1  19/01/02     60.900
            >>>

            # Example 2: change the format of 'timevalue' column.
            >>> format_df = stock_data.assign(format_column=stock_data.timevalue.format('MMMBDD,BYYYY'))
            >>> format_df
                        seq_no timevalue  magnitude format_column
            data_set_id
            556               3  19/01/16     61.080  Jan 16, 2019
            556               5  19/01/30     63.810  Jan 30, 2019
            556               6  19/02/06     63.354  Feb 06, 2019
            556               7  19/02/13     63.871  Feb 13, 2019
            556               9  19/02/27     61.490  Feb 27, 2019
            556              10  19/03/06     61.524  Mar 06, 2019
            556               8  19/02/20     61.886  Feb 20, 2019
            556               4  19/01/23     63.900  Jan 23, 2019
            556               2  19/01/09     61.617  Jan 09, 2019
            556               1  19/01/02     60.900  Jan 02, 2019
            >>>
        """
        arg_validate = []
        arg_validate.append(["formatter", formatter, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)

        return _SQLColumnExpression(func.cast(literal_column("({} (format '{}'))".format(self.compile(), formatter))
                                              , VARCHAR()))

    def trim(self, expression=" "):
        """
        DESCRIPTION:
            Function trims the string values in the column.

        PARAMETERS:
            expression:
                Optional Argument.
                Specifies a ColumnExpression of a string column or a string literal to
                be trimmed. If "expression" is specified, it must be the same data type
                as string values in column.
                Default Value: ' '
                Type: str or ColumnExpression

        RAISES:
            TypeError, ValueError, TeradataMlException

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")

            # Create a DataFrame on 'admissions_train' table.
            >>> df = DataFrame("admissions_train")
            >>> df
                masters   gpa     stats programming  admitted
            id
            38     yes  2.65  Advanced    Beginner         1
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            3       no  3.70    Novice    Beginner         1
            22     yes  3.46    Novice    Beginner         0
            24      no  1.87  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            19     yes  1.98  Advanced    Advanced         0
            40     yes  3.95    Novice    Beginner         0

            # Example 1: Trim "Begi" from the strings in column "programing".
            >>> res = df.assign(trim_col = df.programming.trim("Begi"))
            >>> res
                masters   gpa     stats programming  admitted  trim_col
            id
            38     yes  2.65  Advanced    Beginner         1      nner
            7      yes  2.33    Novice      Novice         1     Novic
            26     yes  3.57  Advanced    Advanced         1  Advanced
            5       no  3.44    Novice      Novice         0     Novic
            3       no  3.70    Novice    Beginner         1      nner
            22     yes  3.46    Novice    Beginner         0      nner
            24      no  1.87  Advanced      Novice         1     Novic
            36      no  3.00  Advanced      Novice         0     Novic
            19     yes  1.98  Advanced    Advanced         0  Advanced
            40     yes  3.95    Novice    Beginner         0      nner

            # Example 2: Filter the rows where values in the column "programming" result
            #            in "nner" after it is trimmed with 'Begi'.
            >>> df[df.programming.trim("Begi") == "nner"]
                masters   gpa     stats programming  admitted
            id
            3       no  3.70    Novice    Beginner         1
            1      yes  3.95  Beginner    Beginner         0
            39     yes  3.75  Advanced    Beginner         0
            34     yes  3.85  Advanced    Beginner         0
            35      no  3.68    Novice    Beginner         1
            31     yes  3.50  Advanced    Beginner         1
            29     yes  4.00    Novice    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            22     yes  3.46    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1

            # Example 3: Trim string in "programing" column using "masters" column as argument.
            >>> res = df.assign(trim_col = df.programming.trim(df.masters))
            >>> res
                masters   gpa     stats programming  admitted  trim_col
            id
            38     yes  2.65  Advanced    Beginner         1  Beginner
            7      yes  2.33    Novice      Novice         1     Novic
            26     yes  3.57  Advanced    Advanced         1  Advanced
            17      no  3.83  Advanced    Advanced         1  Advanced
            34     yes  3.85  Advanced    Beginner         0  Beginner
            13      no  4.00  Advanced      Novice         1    Novice
            32     yes  3.46  Advanced    Beginner         0  Beginner
            11      no  3.13  Advanced    Advanced         1  Advanced
            15     yes  4.00  Advanced    Advanced         1  Advanced
            36      no  3.00  Advanced      Novice         0    Novice

        """
        arg_validate = []
        arg_validate.append(["expression", expression, True, (str, ColumnExpression), False])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)

        if isinstance(expression, ColumnExpression):
            expression=expression.expression
        return _SQLColumnExpression(func.rtrim(func.ltrim(self.expression, expression), expression), type=VARCHAR())

    def to_char(self, formatter=None):
        """
        DESCRIPTION:
            Converts numeric type or datetype to character type.

        PARAMETERS:
            formatter:
                Optional Argument.
                Specifies the format for formatting the values of the column.
                Type: str OR ColumnExpression 
                Notes:
                   * If 'formatter' is omitted, numeric values is converted to a string exactly
                     long enough to hold its significant digits.
                   * Get the supported formatters using `get_formatters("CHAR")` function.


        RAISES:
            TypeError, ValueError, TeradataMlException

        Returns:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "tochar_data")

            # Create a DataFrame on 'tochar_data' table.
            >>> df = DataFrame("tochar_data")
            >>> df
                int_col  float_col  date_col int_format float_format date_format
            id                                                                  
            3      1314     123.46  03/09/17       XXXX          TM9          DY
            0      1234     234.56  03/09/17      9,999        999D9       MM-DD
            2       789     123.46  03/09/17       0999       9999.9         DAY
            1       456     234.56  03/09/17       $999      9.9EEEE        CCAD

            >>> df.tdtypes
            COLUMN NAME	                                   TYPE
            id                                        INTEGER()
            int_col                                   INTEGER()
            float_col                                   FLOAT()
            date_col                                     DATE()
            int_format      VARCHAR(length=20, charset='LATIN')
            float_format    VARCHAR(length=20, charset='LATIN')
            date_format     VARCHAR(length=20, charset='LATIN')

            # Example 1: Convert 'int_col' column to character type.
            >>> res = df.assign(int_col = df.int_col.to_char())
            >>> res
                int_col  float_col  date_col int_format float_format date_format
            id                                                                 
            0     1234     234.56  03/09/17      9,999        999D9       MM-DD
            3     1314     123.46  03/09/17       XXXX          TM9          DY
            2      789     123.46  03/09/17       0999       9999.9         DAY
            1      456     234.56  03/09/17       $999      9.9EEEE        CCAD

            >>> res.tdtypes
            COLUMN NAME	                                   TYPE
            id                                        INTEGER()
            int_col                                   VARCHAR()
            float_col                                   FLOAT()
            date_col                                     DATE()
            int_format      VARCHAR(length=20, charset='LATIN')
            float_format    VARCHAR(length=20, charset='LATIN')
            date_format     VARCHAR(length=20, charset='LATIN')

            # Example 2: Convert 'float_col' column to character type in '$999.9' format.
            >>> res = df.assign(char_col = df.float_col.to_char('$999.9'))
            >>> res
                int_col  float_col  date_col int_format float_format date_format char_col
            id                                                                           
            0      1234     234.56  03/09/17      9,999        999D9       MM-DD   $234.6
            3      1314     123.46  03/09/17       XXXX          TM9          DY   $123.5
            2       789     123.46  03/09/17       0999       9999.9         DAY   $123.5
            1       456     234.56  03/09/17       $999      9.9EEEE        CCAD   $234.6

            # Example 3: Convert 'date_col' column to character type in 'YYYY-DAY-MONTH' format
            >>> res = df.assign(char_col = df.date_col.to_char('YYYY-DAY-MONTH'))
            >>> res
                int_col  float_col  date_col int_format float_format date_format                  char_col
            id                                                                                            
            3      1314   123.4600  03/09/17       XXXX          TM9          DY  1903-THURSDAY -SEPTEMBER
            0      1234   234.5600  03/09/17      9,999        999D9       MM-DD  1903-THURSDAY -SEPTEMBER
            2       789   123.4600  03/09/17       0999       9999.9         DAY  1903-THURSDAY -SEPTEMBER
            1       456   234.5600  03/09/17       $999      9.9EEEE        CCAD  1903-THURSDAY -SEPTEMBER

            # Example 4: Convert 'int_col' column to character type in 'int_format' column format.
            >>> res = df.assign(char_col = df.int_col.to_char(df.int_format))
            >>> res
                int_col  float_col  date_col int_format float_format date_format char_col
            id                                                                           
            0      1234     234.56  03/09/17      9,999        999D9       MM-DD    1,234
            3      1314     123.46  03/09/17       XXXX          TM9          DY      522
            2       789     123.46  03/09/17       0999       9999.9         DAY     0789
            1       456     234.56  03/09/17       $999      9.9EEEE        CCAD     $456

            # Example 5: Convert 'float_col' column to character type in 'float_format' column format.
            >>> res = df.assign(char_col = df.float_col.to_char(df.float_format))
            >>> res
                int_col  float_col  date_col int_format float_format date_format   char_col
            id                                                                             
            2       789     123.46  03/09/17       0999       9999.9         DAY      123.5
            3      1314     123.46  03/09/17       XXXX          TM9          DY     123.46
            1       456     234.56  03/09/17       $999      9.9EEEE        CCAD    2.3E+02
            0      1234     234.56  03/09/17      9,999        999D9       MM-DD      234.6

            # Example 4: Convert 'date_col' column to character type in 'date_format' column format.
            >>> res = df.assign(char_col = df.date_col.to_char(df.date_format))
            >>> res
                int_col  float_col  date_col int_format float_format date_format   char_col
            id                                                                             
            0      1234     234.56  03/09/17      9,999        999D9       MM-DD      09-17
            3      1314     123.46  03/09/17       XXXX          TM9          DY        THU
            2       789     123.46  03/09/17       0999       9999.9         DAY   THURSDAY 
            1       456     234.56  03/09/17       $999      9.9EEEE        CCAD       20AD

        """
        arg_validate = []
        arg_validate.append(["formatter", formatter, True, (str, ColumnExpression), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)

        _args=[self.expression]
        if formatter:
            formatter = formatter.expression if isinstance(formatter, ColumnExpression) else formatter
            _args.append(formatter)
        return _SQLColumnExpression(func.to_char(*_args), type=VARCHAR())
    
    def to_number(self, formatter=None):
        """
        DESCRIPTION:
            Converts a string-like representation of a number to NUMBER type.
            
        PARAMETERS:
            formatter:
                Optional Argument.
                Specifies a variable length string containing formatting characters
                that define the format of the columns.
                Type: str OR ColumnExpression
                Notes:
                    * If 'formatter' is omitted, numeric values is converted to a string exactly
                      long enough to hold its significant digits.
                    * Get the supported formatters using `get_formatters("NUMERIC")` function.
                    
        RAISES:
            TypeError, ValueError, TeradataMlException
            
        RETURNS:
            ColumnExpression
            
        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "to_num_data")

            # Create a DataFrame on 'to_num_data' table.
            >>> df = DataFrame("to_num_data")
            >>> df
            price col_format
            $1234      $9999
            USD123      C999
            78.12      99.99

            #  Example 1: Convert 'price' column to number type without passing any formatter.
            >>> res = df.assign(new_col=df.price.to_number())
            >>> res
            price col_format  new_col
            $1234      $9999      NaN
            USD123      C999      NaN
            78.12      99.99    78.12

            #  Example 2: Convert 'price' column to number type by passing formatter as string.
            >>> res = df.assign(new_col=df.price.to_number('99.99'))
            >>> res
            price col_format  new_col
            $1234      $9999      NaN
            USD123      C999      NaN
            78.12      99.99    78.12

            #  Example 3: Convert 'price' column to number type by passing formatter as ColumnExpression.
            >>> res = df.assign(new_col=df.price.to_number(df.col_format))
            >>> res
            price col_format  new_col
             $1234     $9999     1234
            USD123      C999      123
             78.12     99.99    78.12

            >>> df.tdtypes
            price	    VARCHAR(length=20, charset='LATIN')
            col_format	VARCHAR(length=20, charset='LATIN')
            new_col	                               NUMBER()
      
        """

        arg_validate = []
        arg_validate.append(["formatter", formatter, True, (str, ColumnExpression), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)
        
        _args = [self.expression]
        if formatter is not None:
            formatter = formatter.expression if isinstance(formatter, ColumnExpression) else formatter
            _args.append(formatter)

        return _SQLColumnExpression(func.to_number(*_args), type=NUMBER())

    def to_date(self, formatter=None):
        """
        DESCRIPTION:
            Convert a string-like representation of a DATE or PERIOD type to Date type.

        PARAMETERS:
            formatter:
                Optional Argument.
                Specifies a variable length string containing formatting characters
                that define the format of column.
                Type: str
                Notes:
                    * If "formatter" is omitted, the following default date format is used: 'YYYY-MM-DD'
                    * Get the supported formatters using `get_formatters("DATE")` function.
                    
        RAISES:
            TypeError, ValueError, TeradataMlException

        Returns:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("uaf", "stock_data")

            # Create a DataFrame on 'stock_data' table.
            >>> df = DataFrame("stock_data")
            >>> df
                        seq_no timevalue  magnitude
            data_set_id
            556               3  19/01/16     61.080
            556               5  19/01/30     63.810
            556               6  19/02/06     63.354
            556               7  19/02/13     63.871
            556               9  19/02/27     61.490
            556              10  19/03/06     61.524
            556               8  19/02/20     61.886
            556               4  19/01/23     63.900
            556               2  19/01/09     61.617
            556               1  19/01/02     60.900

            # create new_column "timevalue_char" using to_char().
            >>> new_df = df.assign(timevalue_char=df.timevalue.to_char('DD-MON-YYYY'))
            >>> new_df
                            seq_no timevalue  magnitude timevalue_char
            data_set_id
            556               3  19/01/16     61.080    16-JAN-2019
            556               5  19/01/30     63.810    30-JAN-2019
            556               6  19/02/06     63.354    06-FEB-2019
            556               7  19/02/13     63.871    13-FEB-2019
            556               9  19/02/27     61.490    27-FEB-2019
            556              10  19/03/06     61.524    06-MAR-2019
            556               8  19/02/20     61.886    20-FEB-2019
            556               4  19/01/23     63.900    23-JAN-2019
            556               2  19/01/09     61.617    09-JAN-2019
            556               1  19/01/02     60.900    02-JAN-2019

            # Example 1: convert "timevalue_char" column to DATE type.
            >>> res = new_df.assign(timevalue_char=new_df.timevalue_char.to_date('DD-MON-YYYY'))
            >>> res
                        seq_no timevalue  magnitude timevalue_char
            data_set_id
            556               3  19/01/16     61.080       19/01/16
            556               5  19/01/30     63.810       19/01/30
            556               6  19/02/06     63.354       19/02/06
            556               7  19/02/13     63.871       19/02/13
            556               9  19/02/27     61.490       19/02/27
            556              10  19/03/06     61.524       19/03/06
            556               8  19/02/20     61.886       19/02/20
            556               4  19/01/23     63.900       19/01/23
            556               2  19/01/09     61.617       19/01/09
            556               1  19/01/02     60.900       19/01/02
            >>> res.tdtypes
            column            type
            data_set_id       INTEGER()
            seq_no            INTEGER()
            timevalue            DATE()
            magnitude           FLOAT()
            timevalue_char       DATE()
        """
        arg_validate = []
        arg_validate.append(["formatter", formatter, True, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(arg_validate)

        _args = [self.expression]
        if formatter:
            _args.append(formatter)
        return _SQLColumnExpression(func.to_date(*_args), type=DATE())
    
    def trunc(self, expression=0, formatter=None):
        """
        DESCRIPTION:
            Function to truncate the values inside the column based on formatter.
            Numeric type column:
                Function returns the values in column truncated places_value (expression) places to the right or left
                of the decimal point.
                trunc() functions as follows:
                    * It truncates places_value places to the right of the decimal point if
                      places_value is positive.
                    * It truncates (makes 0) places_value places to the left of the decimal
                      point if places_value is negative.
                    * It truncates to 0 places if places_value is zero or is omitted.
                    * If numeric_value or places_value is NULL, the function returns NULL.
            Date type column:
               Function truncates date type based on the format specified by formatter.
               Example:
                   First example truncates data to first day of the week.
                   Second example truncates data to beginning of the month.
                   +------------------------------------------+
                   |    data            formatter       result|
                   +------------------------------------------+
                   |    19/01/16        'D'           19/01/13|
                   |    19/02/27        'MON'         19/02/01|
                   +------------------------------------------+
        PARAMETERS:
            expression:
                Optional Argument.
                Specifies to truncate the "expression" number of digits.
                Note:
                    This argument applicable only for Numeric columns.
                Default Value: 0
                Types: ColumnExpression OR int

            formatter:
                Optional Argument.
                Specifies a literal string to truncate the values of column.
                If 'formatter' is omitted, date_value is truncated to the nearest day.
                Type: str
                Note:
                    * This argument applicable only for Date type columns.
                * Various formatter given below:
                    +--------------------------------------------------------------------------------------------------+
                    |    FORMATTER                        DESCRIPTION                                                  |
                    +--------------------------------------------------------------------------------------------------+
                    |    CC                                                                                            |
                    |    SCC                              One year greater than the first two digits of a 4-digit year.|
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/01/16        CC                  01/01/01    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    SYYY                                                                                          |
                    |    YYYY                                                                                          |
                    |    YEAR                                                                                          |
                    |    SYEAR                            Year. Returns a value of 1, the first day of the year.       |
                    |    YYY                                                                                           |
                    |    YY                                                                                            |
                    |    Y                                                                                             |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/01/16        CC                  19/01/01    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    IYYY                                                                                          |
                    |    IYY                              ISO year                                                     |
                    |    IY                                                                                            |
                    |    I                                                                                             |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/01/16        CC                  18/12/31    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    MONTH                                                                                         |
                    |    MON                              Month. Returns a value of 1, the first day of the month.     |
                    |    MM                                                                                            |
                    |    RM                                                                                            |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/02/16        RM                  19/02/01    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    Q                                Quarter. Returns a value of 1, the first day of the quarter. |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/02/16        Q                  19/01/01     |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    WW                               Same day of the week as the 1st day of the year.             |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/02/16        WW                  19/02/15    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    IW                               Same day of the week as the first day of the ISO year.       |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/02/16        RM                  19/02/14    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    W                                Same day of the week as the first day of the month.          |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/02/16        W                  19/02/15     |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    DDD                                                                                           |
                    |    DD                               Day.                                                         |
                    |    J                                                                                             |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/02/16        DDD                 19/02/16    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    DAY                                                                                           |
                    |    DY                               Starting day of the week.                                    |
                    |    D                                                                                             |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/01/16        DAY                  19/02/13   |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    HH                                                                                            |
                    |    HH12                             Hour.                                                        |
                    |    HH24                                                                                          |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data            formatter           result      |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 19/02/16        HH                  19/02/16    |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+
                    |    MI                               Minute.                                                      |
                    |                                     Example:                                                     |
                    |                                         +-------------------------------------------------+      |
                    |                                         | data                       formatter  result    |      |
                    |                                         +-------------------------------------------------+      |
                    |                                         | 2016-01-06 09:08:01.000000    MI      16/01/06  |      |
                    |                                         +-------------------------------------------------+      |
                    +--------------------------------------------------------------------------------------------------+

        RAISES:
            TypeError, ValueError, TeradataMlException

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to execute the example.
            >>> load_example_data("dataframe", "admissions_train")
            >>> load_example_data("uaf", "stock_data")

            # Create a DataFrame on 'admissions_train' table.
            >>> df = DataFrame("admissions_train").iloc[:4]
            >>> df
               masters   gpa     stats programming  admitted
            id
            3       no  3.70    Novice    Beginner         1
            4      yes  3.50  Beginner      Novice         1
            2      yes  3.76  Beginner    Beginner         0
            1      yes  3.95  Beginner    Beginner         0

            # Create a DataFrame on 'stock_data' table.
            >>> df1 = DataFrame("stock_data")
            >>> df1
                        seq_no timevalue  magnitude
            data_set_id
            556               3  19/01/16     61.080
            556               5  19/01/30     63.810
            556               6  19/02/06     63.354
            556               7  19/02/13     63.871
            556               9  19/02/27     61.490
            556              10  19/03/06     61.524
            556               8  19/02/20     61.886
            556               4  19/01/23     63.900
            556               2  19/01/09     61.617
            556               1  19/01/02     60.900

            # Example 1: Truncate the value of 'gpa' to 0 decimal place and 1 decimal place.
            >>> res = df.assign(col = df.gpa.trunc(),
                                   col_1 = df.gpa.trunc(1))
            >>> res
               masters   gpa     stats programming  admitted  col  col_1
            id
            3       no  3.70    Novice    Beginner         1  3.0    3.7
            4      yes  3.50  Beginner      Novice         1  3.0    3.5
            2      yes  3.76  Beginner    Beginner         0  3.0    3.7
            1      yes  3.95  Beginner    Beginner         0  3.0    3.9

            # Example 2: Get the records with gpa > 3.7 by rounding the gpa to single decimal point.
            >>> df[df.gpa.trunc(1) > 3.7]
               masters   gpa     stats programming  admitted
            id
            1      yes  3.95  Beginner    Beginner         0

            # Example 3: Truncate the value of 'timevalue' to beginning of the month.
            >>> res=df1.assign(timevalue=df1.timevalue.trunc(formatter="MON"))
            >>> res
                            seq_no timevalue  magnitude time_value
            data_set_id
            556               3  19/01/16     61.080   19/01/01
            556               5  19/01/30     63.810   19/01/01
            556               6  19/02/06     63.354   19/02/01
            556               7  19/02/13     63.871   19/02/01
            556               9  19/02/27     61.490   19/02/01
            556              10  19/03/06     61.524   19/03/01
            556               8  19/02/20     61.886   19/02/01
            556               4  19/01/23     63.900   19/01/01
            556               2  19/01/09     61.617   19/01/01
            556               1  19/01/02     60.900   19/01/01

        """
        numeric_types=[INTEGER, SMALLINT, BIGINT, BYTEINT, DECIMAL, FLOAT, NUMBER]
        _args = [self.expression]
        if type(self.type) in numeric_types:
            if isinstance(expression, ColumnExpression):
                _args.append(expression.expression)
            else:
                _args.append(expression)
        elif formatter:
            _args.append(formatter)
        return _SQLColumnExpression(func.trunc(*_args))

    def __get_columns(self, col_expr):
        """
        DESCRIPTION:
            Function to get the columns involved in a sqlalchemy expression.

        PARAMETERS:
            col_expr:
                Required Argument.
                Specifies the sqlalchemy expression.
                Types: BinaryExpression OR Grouping OR GenericFunction OR ClauseList OR Column

        RAISES:
            None

        RETURNS:
            list

        EXAMPLES:
            >>> self.__get_columns(self.expression)
        """
        # If it is a column, return the name of the column.
        if isinstance(col_expr, Column):
            return [col_expr.name]

        # Every other type exposes a method to retrieve the children. Recursively, walk through all
        # the childs till a Column or a Bind Parameter is reached.
        elif isinstance(col_expr, (BinaryExpression, Grouping, GenericFunction, ClauseList, Function)):
            res = []
            for c in col_expr.get_children():
                res = res + self.__get_columns(c)
            return res
        else:
            try:
                if isinstance(col_expr, ExpressionClauseList):
                    res = []
                    for c in col_expr.get_children():
                        res = res + self.__get_columns(c)
                    return res
            except NameError:
                pass
        # If the child is a Bind Parameter, return empty string.
        return []

    @property
    def _all_columns(self):
        """
        DESCRIPTION:
            A property to get the columns involved in ColumnExpression.

        RAISES:
            None

        RETURNS:
            list

        EXAMPLES:
            >>> self._all_columns
        """
        return list(set(self.__get_columns(self.expression)))

    def _get_sqlalchemy_tables(self, expression):
        """
        DESCRIPTION:
            Internal function to get the corresponding SQLAlchemy tables involved
            in an expression.

        RAISES:
            None

        RETURNS:
            list

        EXAMPLES:
            >>> self._get_sqlalchemy_tables(expression)
        """

        # check if it is a sqlalchemy Column or not.
        if isinstance(expression, Column):
            return [expression.table]

        result = []
        if hasattr(expression, "get_children"):
            for obj in expression.get_children():
                result = result + self._get_sqlalchemy_tables(obj)
            return list(set(result))

        return []
    
    def alias(self, name):
        """
        DESCRIPTION:
            Function to returns this column with aliased name.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the column name.
                Type: str 

        RAISES:
            TypeError, ValueError

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "admissions_train")

            # Create a DataFrame on 'admissions_train' table.
            >>> df = DataFrame("admissions_train")
            >>> df
                masters   gpa     stats programming  admitted
            id
            38     yes  2.65  Advanced    Beginner         1
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            5       no  3.44    Novice      Novice         0
            3       no  3.70    Novice    Beginner         1
            22     yes  3.46    Novice    Beginner         0
            24      no  1.87  Advanced      Novice         1
            36      no  3.00  Advanced      Novice         0
            19     yes  1.98  Advanced    Advanced         0
            40     yes  3.95    Novice    Beginner         0

            # Example 1: Alias the resultant column after aggregation with "count_program".
            >>> res = df.agg(df.programming.count().alias("count_program"))
            >>> res
               count_program
            0             40

        """
        
        # Validate argument types
        arg_type_matrix = [["name", name , True, (str), True]]
        _Validators._validate_function_arguments(arg_type_matrix)

        self.alias_name = name
        return self
    
    @staticmethod
    def _timezone_string(value):
        """
        DESCRIPTION:
            Function to return timezone string in correct format.

        PARAMETERS:
            value:
                Required Argument.
                Specifies timezone string.
                Types: str, int , float

        RETURNS:
            bool
        """
        if isinstance(value, (float, int)):
            return " AT TIME ZONE {}".format(value)
        if value.upper() not in ['LOCAL']:
            return " AT TIME ZONE '{}'".format(value)
        return " AT {}".format(value)

    def to_timestamp(self, format=None, type_=TIMESTAMP, timezone=None):
        """
        DESCRIPTION:
            Converts string or integer to a TIMESTAMP data type or TIMESTAMP WITH
            TIME ZONE data type.
            Note:
                * POSIX epoch conversion is implicit in the "to_timestamp" when column
                  is integer type. POSIX epoch is the number of seconds that have elapsed
                  since midnight Coordinated Universal Time (UTC) of January 1, 1970.

        PARAMETERS:
            format:
                Specifies the format of string column.
                Argument is not required when column is integer type, Otherwise Required.
                For valid 'format' values, see documentation on
                "to_date" or "help(df.col_name.to_date)".
                Type: ColumnExpression or str

            type_:
                Optional Argument.
                Specifies a TIMESTAMP type or an object of a
                TIMESTAMP type that the column needs to be cast to.
                Default value: TIMESTAMP
                Permitted Values: TIMESTAMP data type
                Types: teradatasqlalchemy type or object of teradatasqlalchemy type

            timezone:
                Optional Argument.
                Specifies the timezone string.
                For valid timezone strings, user should check Vantage documentation.
                Type: ColumnExpression or str.

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "timestamp_data")

            # Create a DataFrame on 'timestamp_data' table.
            >>> df = DataFrame("timestamp_data")
            >>> df
            id                timestamp_col  timestamp_col1                         format_col     timezone_col
            2  2015-01-08 00:00:12.2+10:00     45678910234  YYYY-MM-DD HH24:MI:SS.FF6 TZH:TZM           GMT+10
            1             2015-01-08 13:00          878986                 YYYY-MM-DD HH24:MI  America Pacific
            0        2015-01-08 00:00:12.2          123456          YYYY-MM-DD HH24:MI:SS.FF6              GMT

            >>> df.tdtypes
            id                                          INTEGER()
            timestamp_col     VARCHAR(length=30, charset='LATIN')
            timestamp_col1                               BIGINT()
            format_col        VARCHAR(length=30, charset='LATIN')
            timezone_col      VARCHAR(length=30, charset='LATIN')

            # Example 1: Convert Epoch seconds to timestamp.
            >>> df.select(['id','timestamp_col1']).assign(col = df.timestamp_col1.to_timestamp())
            id  timestamp_col1                         col
            2     45678910234  3417-07-05 02:10:34.000000
            1          878986  1970-01-11 04:09:46.000000
            0          123456  1970-01-02 10:17:36.000000

            # Example 2: Convert timestamp string to timestamp with timezone in
            #            format mentioned in column "format_col".
            >>> df.select(['id', 'timestamp_col', 'format_col']).assign(col = df.timestamp_col.to_timestamp(df.format_col, TIMESTAMP(timezone=True)))
            id                timestamp_col                         format_col                             col
            2  2015-01-08 00:00:12.2+10:00  YYYY-MM-DD HH24:MI:SS.FF6 TZH:TZM  2015-01-08 00:00:12.200000+10:00
            1             2015-01-08 13:00                 YYYY-MM-DD HH24:MI  2015-01-08 13:00:00.000000+00:00
            0        2015-01-08 00:00:12.2          YYYY-MM-DD HH24:MI:SS.FF6  2015-01-08 00:00:12.200000+00:00

            # Example 3: Convert Epoch seconds to timestamp with timezone in 'GMT+2' location.
            >>> df.select(['id', 'timestamp_col1', 'format_col']).assign(col = df.timestamp_col1.to_timestamp(df.format_col, TIMESTAMP(timezone=True), 'GMT+2'))
            id  timestamp_col1                         format_col                             col
            2     45678910234  YYYY-MM-DD HH24:MI:SS.FF6 TZH:TZM  3417-07-05 04:10:34.000000+02:00
            1          878986                 YYYY-MM-DD HH24:MI  1970-01-11 06:09:46.000000+02:00
            0          123456          YYYY-MM-DD HH24:MI:SS.FF6  1970-01-02 12:17:36.000000+02:00

        """
        # Validating Arguments
        arg_type_matrix = []
        arg_type_matrix.append(["format", format , True, (str, ColumnExpression), True])
        arg_type_matrix.append(["timezone", timezone, True, (str, ColumnExpression, int, float), True])
        _Validators._validate_function_arguments(arg_type_matrix)

        if not UtilFuncs._is_valid_td_type(type_):
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, 'type_',
                                                           'a valid teradatasqlalchemy type'),
                                      MessageCodes.UNSUPPORTED_DATATYPE)

        _format = format.expression if isinstance(format, _SQLColumnExpression) else format
        _params = [self.expression, _format]
        # format is not required when column is of below types.
        if isinstance(self._type, (BYTEINT, SMALLINT, INTEGER, BIGINT)):
            _params.pop()
        # Use to_timestamp_tz when below 3 conditions are true.
        # Resultant query will be Example:
        # TO_TIMESTAMP('2015-10-08 00:00:12.2') or TO_TIMESTAMP_TZ('2015-10-08 00:00:12.2+03:00') based on type_
        _fun = getattr(func, "to_timestamp_tz") if isinstance(type_, TIMESTAMP) and type_.timezone and len(_params) == 2 \
            else getattr(func, "to_timestamp")
        if not timezone:
            return _SQLColumnExpression(_fun(*_params), type=type_)

        # If user uses timezone generate query with time zone.
        # Resultant query will be Example:
        # TO_TIMESTAMP('2015-10-08 00:00:12.2') at time zone 'America Alaska',
        # TO_TIMESTAMP_TZ('2015-10-08 00:00:12.2+03:00') at time zone 'America Alaska'.
        if isinstance(timezone, _SQLColumnExpression):
            _timezone_expr = _SQLColumnExpression(literal_column(f' AT TIME ZONE {timezone.compile()}')).compile()
        else:
            _timezone_expr = _SQLColumnExpression(literal_column(_SQLColumnExpression._timezone_string(timezone))).compile()
        return _SQLColumnExpression(_SQLColumnExpression(_fun(*_params)).compile() + _timezone_expr, type=type_)

    def extract(self, value, timezone=None):
        """
        DESCRIPTION:
            Extracts a single specified field from any DateTime, Interval or timestamp value,
            converting it to an exact numeric value.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the field which needs to be extracted.
                Permitted Values: YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, TIMEZONE_HOUR, TIMEZONE_MINUTE
                Note:
                    * Permitted Values are case insensitive.
                Type: str

            timezone:
                Optional Argument.
                Specifies the timezone string.
                For valid timezone strings, user should check Vantage documentation.
                Type: ColumnExpression or str.

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("uaf", "Traindata")

            # Create a DataFrame on 'Traindata' table.

            >>> temp_df = DataFrame("Traindata")
            >>> df = temp_df.select(["seq_no", "schedule_date", "arrivalTime"])
            >>> df
                    schedule_date          arrivalTime
            seq_no
            26          16/03/26  2016-03-26 12:33:05
            24          16/03/26  2016-03-26 12:25:06
            3           16/03/26  2016-03-26 10:52:05
            22          16/03/26  2016-03-26 12:18:01
            20          16/03/26  2016-03-26 12:10:06
            18          16/03/26  2016-03-26 12:04:01
            8           16/03/26  2016-03-26 11:15:06
            17          16/03/26  2016-03-26 11:56:06
            15          16/03/26  2016-03-26 11:45:00
            13          16/03/26  2016-03-26 11:33:00
            11          16/03/26  2016-03-26 11:26:00

            # Example 1: Extract year from column 'schedule_date'.
            >>> df.assign(col = df.schedule_date.extract('YEAR'))
                    schedule_date          arrivalTime   col
            seq_no
            26          16/03/26  2016-03-26 12:33:05  2016
            24          16/03/26  2016-03-26 12:25:06  2016
            3           16/03/26  2016-03-26 10:52:05  2016
            22          16/03/26  2016-03-26 12:18:01  2016
            20          16/03/26  2016-03-26 12:10:06  2016
            18          16/03/26  2016-03-26 12:04:01  2016
            8           16/03/26  2016-03-26 11:15:06  2016
            17          16/03/26  2016-03-26 11:56:06  2016
            15          16/03/26  2016-03-26 11:45:00  2016
            13          16/03/26  2016-03-26 11:33:00  2016
            11          16/03/26  2016-03-26 11:26:00  2016

            # Example 2: Extract hour from column 'arrivalTime'.
            >>> df.assign(col = df.arrivalTime.extract('HOUR'))
                    schedule_date          arrivalTime col
            seq_no
            26          16/03/26  2016-03-26 12:33:05  12
            24          16/03/26  2016-03-26 12:25:06  12
            3           16/03/26  2016-03-26 10:52:05  10
            22          16/03/26  2016-03-26 12:18:01  12
            20          16/03/26  2016-03-26 12:10:06  12
            18          16/03/26  2016-03-26 12:04:01  12
            8           16/03/26  2016-03-26 11:15:06  11
            17          16/03/26  2016-03-26 11:56:06  11
            15          16/03/26  2016-03-26 11:45:00  11

            # Example 3: Extract hour from column 'arrivalTime' with offset '-11:00'.
            >>> df.assign(col = df.arrivalTime.extract('HOUR', '-11:00'))
                    schedule_date          arrivalTime col
            seq_no
            26          16/03/26  2016-03-26 12:33:05   1
            24          16/03/26  2016-03-26 12:25:06   1
            3           16/03/26  2016-03-26 10:52:05  23
            22          16/03/26  2016-03-26 12:18:01   1
            20          16/03/26  2016-03-26 12:10:06   1
            18          16/03/26  2016-03-26 12:04:01   1
            8           16/03/26  2016-03-26 11:15:06   0
            17          16/03/26  2016-03-26 11:56:06   0
            15          16/03/26  2016-03-26 11:45:00   0

            # Example 4: Extract hour from column 'arrivalTime' with offset 10.
            >>> df.assign(col = df.arrivalTime.extract('HOUR', 10))
                    schedule_date          arrivalTime col
            seq_no
            26          16/03/26  2016-03-26 12:33:05  22
            24          16/03/26  2016-03-26 12:25:06  22
            3           16/03/26  2016-03-26 10:52:05  20
            22          16/03/26  2016-03-26 12:18:01  22
            20          16/03/26  2016-03-26 12:10:06  22
            18          16/03/26  2016-03-26 12:04:01  22
            8           16/03/26  2016-03-26 11:15:06  21
            17          16/03/26  2016-03-26 11:56:06  21
            15          16/03/26  2016-03-26 11:45:00  21
            13          16/03/26  2016-03-26 11:33:00  21
            11          16/03/26  2016-03-26 11:26:00  21
        """
        # Validating Arguments
        arg_type_matrix = []
        arg_type_matrix.append(["value", value , True, (str), True])
        arg_type_matrix.append(["timezone", timezone, True, (str, ColumnExpression, int, float), True])
        _Validators._validate_function_arguments(arg_type_matrix)

        # If user doesn't provide timezone simply use extract functionality.
        if not timezone:
            return _SQLColumnExpression(func.extract(value, self.expression))

        # If user uses timezone generate query with time zone.
        if isinstance(timezone, _SQLColumnExpression):
            _timezone_expr = _SQLColumnExpression(literal_column(f' AT TIME ZONE {timezone.compile()}')).compile()
        else:
            _timezone_expr = _SQLColumnExpression(literal_column(_SQLColumnExpression._timezone_string(timezone))).compile()
        return _SQLColumnExpression(func.extract(value, literal_column('({}{})'.format(self.compile(), _timezone_expr))))

    def to_interval(self, value=None, type_=INTERVAL_DAY_TO_SECOND):
        """
        DESCRIPTION:
            Converts a numeric value or string value into an INTERVAL_DAY_TO_SECOND or INTERVAL_YEAR_TO_MONTH value.

        PARAMETERS:
            value:
                Optional, when column type is VARCHAR or CHAR, otherwise required.
                Specifies the unit of value for numeric value.
                when type_ is INTERVAL_DAY_TO_SECOND permitted values:
                    * DAY, HOUR, MINUTE, SECOND
                when type_ is INTERVAL_YEAR_TO_MONTH permitted values:
                    * YEAR, MONTH
                Note:
                    * Permitted Values are case insensitive.
                Type: str or ColumnExpression

            type_:
                Optional Argument.
                Specifies a teradatasqlalchemy type or an object of a teradatasqlalchemy type
                that the column needs to be cast to.
                Default value: TIMESTAMP
                Permitted Values: INTERVAL_DAY_TO_SECOND or INTERVAL_YEAR_TO_MONTH type.
                Types: teradatasqlalchemy type or object of teradatasqlalchemy type

        Returns:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "interval_data")

            # Create a DataFrame on 'interval_data' table.
            >>> df = DataFrame("interval_data")
            >>> df
            id  int_col value_col value_col1        str_col1 str_col2
            2      657    MINUTE      MONTH           PT73H    -P14M
            3     1234    SECOND      MONTH    100 04:23:59    06-10
            1      240      HOUR       YEAR  P100DT4H23M59S  P100Y4M
            0       20       DAY       YEAR    100 04:23:59    04-10

            >>> df.tdtypes
            id                                      INTEGER()
            int_col                                  BIGINT()
            value_col     VARCHAR(length=30, charset='LATIN')
            value_col1    VARCHAR(length=30, charset='LATIN')
            str_col1      VARCHAR(length=30, charset='LATIN')
            str_col2      VARCHAR(length=30, charset='LATIN')


            # Example 1: Convert "int_col" column to INTERVAL_DAY_TO_SECOND with value
            #            provided in "value_col".
            >>> df.assign(col = df.int_col.to_interval(df.value_col))
            id  int_col value_col value_col1        str_col1 str_col2                    col
            2      657    MINUTE      MONTH           PT73H    -P14M      0 10:57:00.000000
            3     1234    SECOND      MONTH    100 04:23:59    06-10      0 00:20:34.000000
            1      240      HOUR       YEAR  P100DT4H23M59S  P100Y4M     10 00:00:00.000000
            0       20       DAY       YEAR    100 04:23:59    04-10     20 00:00:00.000000

            # Example 2: Convert int_col to INTERVAL_YEAR_TO_MONTH when value = 'MONTH'.
            >>> df.assign(col = df.int_col.to_interval('MONTH', INTERVAL_YEAR_TO_MONTH))
            id  int_col value_col value_col1        str_col1 str_col2       col
            2      657    MINUTE      MONTH           PT73H    -P14M     54-09
            3     1234    SECOND      MONTH    100 04:23:59    06-10    102-10
            1      240      HOUR       YEAR  P100DT4H23M59S  P100Y4M     20-00
            0       20       DAY       YEAR    100 04:23:59    04-10      1-08

            # Example 3: Convert string column "str_col1" to INTERVAL_DAY_TO_SECOND.
            >>> df.assign(col = df.str_col1.to_interval())
            id  int_col value_col value_col1        str_col1 str_col2                    col
            2      657    MINUTE      MONTH           PT73H    -P14M      3 01:00:00.000000
            3     1234    SECOND      MONTH    100 04:23:59    06-10    100 04:23:59.000000
            1      240      HOUR       YEAR  P100DT4H23M59S  P100Y4M    100 04:23:59.000000
            0       20       DAY       YEAR    100 04:23:59    04-10    100 04:23:59.000000

            # Example 4: Convert string column "str_col2" to INTERVAL_DAY_TO_MONTH.
            >>> df.assign(col = df.str_col2.to_interval(type_=INTERVAL_YEAR_TO_MONTH))
            id  int_col value_col value_col1        str_col1 str_col2       col
            2      657    MINUTE      MONTH           PT73H    -P14M     -1-02
            3     1234    SECOND      MONTH    100 04:23:59    06-10      6-10
            1      240      HOUR       YEAR  P100DT4H23M59S  P100Y4M    100-04
            0       20       DAY       YEAR    100 04:23:59    04-10      4-10

        """
        # Validating Arguments
        arg_type_matrix = []
        arg_type_matrix.append(["value", value , True, (str, ColumnExpression), True])
        _Validators._validate_function_arguments(arg_type_matrix)

        if not UtilFuncs._is_valid_td_type(type_):
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, 'type_',
                                                           'a valid teradatasqlalchemy type'),
                                      MessageCodes.UNSUPPORTED_DATATYPE)

        # When column type is string, use either to_dsinterval or to_yminterval function based on "type_".
        if isinstance(self._type, (VARCHAR, CHAR)):
            _fun = (getattr(func, "to_dsinterval")) if isinstance(type_, INTERVAL_DAY_TO_SECOND)\
                or (isinstance(type_, type) and issubclass(type_, INTERVAL_DAY_TO_SECOND)) \
                else (getattr(func, "to_yminterval"))
            return _SQLColumnExpression(_fun(self.expression), type=type_)

        # When column type is integer or float type, use either numtodsinterval or numtoyminterval
        # function based on "type_".
        _fun = (getattr(func, "numtodsinterval")) if isinstance(type_, INTERVAL_DAY_TO_SECOND) \
            or (isinstance(type_, type) and issubclass(type_, INTERVAL_DAY_TO_SECOND))\
            else (getattr(func, "numtoyminterval"))
        value = value.expression if isinstance(value, _SQLColumnExpression) else value
        return _SQLColumnExpression(_fun(self.expression, value), type=type_)

    def parse_url(self, url_part, key=None):
        """
        DESCRIPTION:
            Extracts a specific part from the URL.

        PARAMETERS:
            url_part:
                Required Argument.
                Specifies which part to be extracted.
                Permitted Values: HOST, PATH, QUERY, REF, PROTOCOL, FILE, AUTHORITY, USERINFO
                Type: str or ColumnExpression

            key:
                Optional Argument.
                Specifies the key to be used for extracting the value from the query string.
                Note:
                    * Applicable only when url_part is set to 'QUERY'.
                Type: str or ColumnExpression

        Returns:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "url_data")

            # Create a DataFrame on 'url_data' table.
            >>> df = DataFrame("url_data")
            >>> df
                                                                        urls       part     query_key
            id                                                                                       
            3                                       https://www.facebook.com       HOST  facebook.com
            8             http://example.com/api?query1=value1&query2=value2      QUERY        query1
            6              smtp://user:password@smtp.example.com:21/file.txt   USERINFO      password
            4   https://teracloud-pod-services-pod-account-service.dummyvalu      QUERY          None
            0                                   http://example.com:8080/path       FILE          path
            2   https://example.net/path4/path5/path6?query4=value4#fragment        REF     fragment3
            1                                      ftp://example.net:21/path       PATH          path
            5                        http://pg.example.ml/path150#fragment90  AUTHORITY    fragment90
            7                                         https://www.google.com   PROTOCOL    google.com

            # Example 1: Extract components from column 'urls' using column 'part'.
            >>> df.assign(col = df.urls.parse_url(df.part))
                                                                        urls       part     query_key                          col
            id                                                                                                                    
            3                                       https://www.facebook.com       HOST  facebook.com             www.facebook.com
            8             http://example.com/api?query1=value1&query2=value2      QUERY        query1  query1=value1&query2=value2
            6              smtp://user:password@smtp.example.com:21/file.txt   USERINFO      password                user:password
            4   https://teracloud-pod-services-pod-account-service.dummyvalu      QUERY          None                         None
            0                                   http://example.com:8080/path       FILE          path                        /path
            2   https://example.net/path4/path5/path6?query4=value4#fragment        REF     fragment3                     fragment
            1                                      ftp://example.net:21/path       PATH          path                        /path
            5                        http://pg.example.ml/path150#fragment90  AUTHORITY    fragment90                pg.example.ml
            7                                         https://www.google.com   PROTOCOL    google.com                        https
            
            # Example 2: Extract components from column 'urls' using 'part' and
            #            'query_key' column.
            >>> df.assign(col = df.urls.parse_url(df.part, df.query_key))
                                                                        urls       part     query_key     col
            id                                                                                               
            3                                       https://www.facebook.com       HOST  facebook.com    None
            8             http://example.com/api?query1=value1&query2=value2      QUERY        query1  value1
            6              smtp://user:password@smtp.example.com:21/file.txt   USERINFO      password    None
            4   https://teracloud-pod-services-pod-account-service.dummyvalu      QUERY          None    None
            0                                   http://example.com:8080/path       FILE          path    None
            2   https://example.net/path4/path5/path6?query4=value4#fragment        REF     fragment3    None
            1                                      ftp://example.net:21/path       PATH          path    None
            5                        http://pg.example.ml/path150#fragment90  AUTHORITY    fragment90    None
            7                                         https://www.google.com   PROTOCOL    google.com    None

            # Extract components from column 'urls' using 'part' and 'query_key' str.
            >>> df.assign(col = df.urls.parse_url('QUERY', 'query2'))
                                                                        urls       part     query_key     col
            id                                                                                               
            3                                       https://www.facebook.com       HOST  facebook.com    None
            8             http://example.com/api?query1=value1&query2=value2      QUERY        query1  value2
            6              smtp://user:password@smtp.example.com:21/file.txt   USERINFO      password    None
            4   https://teracloud-pod-services-pod-account-service.dummyvalu      QUERY          None    None
            0                                   http://example.com:8080/path       FILE          path    None
            2   https://example.net/path4/path5/path6?query4=value4#fragment        REF     fragment3    None
            1                                      ftp://example.net:21/path       PATH          path    None
            5                        http://pg.example.ml/path150#fragment90  AUTHORITY    fragment90    None
            7                                         https://www.google.com   PROTOCOL    google.com    None
        """

        # Validating Arguments
        arg_type_matrix = []
        arg_type_matrix.append(["url_part", url_part, False, (str, ColumnExpression), True])
        arg_type_matrix.append(["key", key, True, (str, ColumnExpression), True])
        _Validators._validate_function_arguments(arg_type_matrix)

        # If key is provided and url_part is QUERY, then use regex to extract the value.
        if key is not None:
            query_expr = _SQLColumnExpression(func.regexp_substr(func.regexp_substr(self.expression, 
                '[?&]' + (key.expression if isinstance(key, _SQLColumnExpression) else key) + '=([^&]*)'), '[^=]*$'), type=VARCHAR())
            # If url_part is a column expression, then use case statement to extract the value.
            if isinstance(url_part, _SQLColumnExpression):
                whens = [(url_part == 'HOST', None),
                    (url_part == 'PATH', None ),
                    (url_part == 'QUERY', query_expr),
                    (url_part == 'REF', None),
                    (url_part == 'PROTOCOL', None),
                    (url_part == 'FILE',None),
                    (url_part == 'AUTHORITY', None),
                    (url_part == 'USERINFO', None)]

                from teradataml.dataframe.sql_functions import case
                return case(whens)
            
            # If url_part is a string, then return the query expression directly.
            if isinstance(url_part, str) and url_part == 'QUERY':
                return query_expr
         
        # Regex pattern used to extract 'url_part' is '^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?'.
        # teradataml does not support regex grouping hence in some cases first used 'regex_replace' and
        # then 'regex_substr' or vice-versa.
        _part_to_extract_dict = {'HOST': _SQLColumnExpression(
                                     func.regexp_replace(func.regexp_substr(self.expression, '//([^/?#]*)'), r'(//[^/?#]+@)|(//)|(:\d+)', ''),
                                        type=VARCHAR()),
                                 'PATH': _SQLColumnExpression(func.regexp_substr(
                                     func.regexp_replace(self.expression, '^(([^:/?#]+):)?(//([^/?#]*))?', ''),
                                     '([^?#]*)'), type=VARCHAR()),
                                 'QUERY': _SQLColumnExpression(func.ltrim(func.regexp_substr(
                                     func.regexp_replace(self.expression, '^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)', ''),
                                     r'\?([^#]*)'), '?'), type=VARCHAR()),
                                 'REF': _SQLColumnExpression(func.ltrim(func.regexp_substr(
                                     func.regexp_replace(self.expression,
                                                         r'^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?', ''),
                                     '(#(.*))'), '#'), type=VARCHAR()),
                                 'PROTOCOL': _SQLColumnExpression(
                                     func.rtrim(func.regexp_substr(self.expression, '^(([^:/?#]+):)'), ':'),
                                     type=VARCHAR()),
                                 'FILE': _SQLColumnExpression(func.regexp_substr(
                                     func.regexp_replace(self.expression, '^(([^:/?#]+):)?(//([^/?#]*))?', ''),
                                     r'([^?#]*)(\?([^#]*))?'), type=VARCHAR()),
                                 'AUTHORITY': _SQLColumnExpression(
                                     func.ltrim(func.regexp_substr(self.expression, '//([^/?#]*)'), '//'),
                                     type=VARCHAR()),
                                 'USERINFO': _SQLColumnExpression(func.rtrim(func.ltrim(
                                     func.regexp_substr(func.regexp_substr(self.expression, '//([^/?#]*)'),
                                                        '//[^/?#]+@'), '/'), '@'), type=VARCHAR())
                                 }

        if isinstance(url_part, str):
            return _part_to_extract_dict[url_part]

        whens = [(url_part == 'HOST', _part_to_extract_dict['HOST']),
                 (url_part == 'PATH', _part_to_extract_dict['PATH'] ),
                 (url_part == 'QUERY', _part_to_extract_dict['QUERY']),
                 (url_part == 'REF', _part_to_extract_dict['REF']),
                 (url_part == 'PROTOCOL', _part_to_extract_dict['PROTOCOL']),
                 (url_part == 'FILE', _part_to_extract_dict['FILE']),
                 (url_part == 'AUTHORITY', _part_to_extract_dict['AUTHORITY']),
                 (url_part == 'USERINFO', _part_to_extract_dict['USERINFO'])]

        from teradataml.dataframe.sql_functions import case
        return case(whens)

    def log(self, base):
        """
        DESCRIPTION:
            Returns the logarithm value of the column with respect to 'base'.

        PARAMETERS:
            base:
                Required Argument.
                Specifies base of logarithm.
                Type: int or float or ColumnExpression

        Returns:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            265         NaN    7.7500
            530        23.0   11.5000
            122         NaN    8.0500
            591        35.0    7.1250
            387         1.0   46.9000
            734        23.0   13.0000
            795        25.0    7.8958
            >>>

            # Example 1: Compute log values for column 'fare' using base as column 'age'.
            >>> log_df = df.assign(fare_log=df.fare.log(df.age))
            >>> print(log_df)
                        age      fare  fare_log
            passenger
            326        36.0  135.6333  1.370149
            183         9.0   31.3875  1.568529
            652        18.0   23.0000  1.084807
            40         14.0   11.2417  0.916854
            774         NaN    7.2250       NaN
            366        30.0    7.2500  0.582442
            509        28.0   22.5250  0.934704
            795        25.0    7.8958  0.641942
            61         22.0    7.2292  0.639955
            469         NaN    7.7250       NaN
            >>>
        """
        # Validating Arguments
        arg_type_matrix = []
        arg_type_matrix.append(["base", base, False, (int, float, ColumnExpression), True])
        _Validators._validate_function_arguments(arg_type_matrix)

        # Handling cases when 'base' or 'self' column values are zero or when denominator is zero
        from teradataml.dataframe.sql_functions import case

        if not isinstance(base, _SQLColumnExpression):
            whens = case([((self != 0) & (_SQLColumnExpression(literal(base)).ln() != 0),
                           (self.ln() / _SQLColumnExpression(literal(base)).ln()).cast(FLOAT))])
        else:
            whens = case([((self != 0) & (base != 0) & (base.ln() != 0),
                           (self.ln() / base.ln()).cast(FLOAT))])

        return whens

    def isnan(self):
        """
        DESCRIPTION:
            Function evaluates a variable or expression to determine if the
            floating-point argument is a NaN (Not-a-Number) value. When a database
            table contains a NaN value, the data is undefined and unrepresentable
            in floating-point arithmetic. For example, division by 0, or the square root
            of a negative number would return a NaN result.

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml","titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            40         14.0   11.2417
            774         NaN    7.2250
            366        30.0    7.2500
            509        28.0   22.5250
            795        25.0    7.8958
            61         22.0    7.2292
            469         NaN    7.7250
            >>>

            # Example 1: Find whether 'fare' column contains NaN values or not.
            >>> nan_df = df.assign(nanornot = df.fare.isnan())
            >>> print(nan_df)
                        age      fare nanornot
            passenger
            326        36.0  135.6333        0
            183         9.0   31.3875        0
            652        18.0   23.0000        0
            40         14.0   11.2417        0
            774         NaN    7.2250        0
            366        30.0    7.2500        0
            509        28.0   22.5250        0
            795        25.0    7.8958        0
            61         22.0    7.2292        0
            469         NaN    7.7250        0
            >>>
        """
        return _SQLColumnExpression(literal_column(f"TD_ISNAN({self.compile()})"), type=INTEGER)

    def isinf(self):
        """
        DESCRIPTION:
            Function evaluates a variable or expression to determine if the
            floating-point argument is an infinite number. This function determines
            if a database table contains positive or negative infinite values.

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml","titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            40         14.0   11.2417
            774         NaN    7.2250
            366        30.0    7.2500
            509        28.0   22.5250
            795        25.0    7.8958
            61         22.0    7.2292
            469         NaN    7.7250
            >>>

            # Example 1: Find whether 'fare' column contains infinity values or not.
            >>> inf_df = df.assign(infornot = df.fare.isinf())
            >>> print(inf_df)
                        age      fare infornot
            passenger
            326        36.0  135.6333        0
            183         9.0   31.3875        0
            652        18.0   23.0000        0
            40         14.0   11.2417        0
            774         NaN    7.2250        0
            366        30.0    7.2500        0
            509        28.0   22.5250        0
            795        25.0    7.8958        0
            61         22.0    7.2292        0
            469         NaN    7.7250        0
            >>>
        """
        return _SQLColumnExpression(literal_column(f"TD_ISINF({self.compile()})"), type=INTEGER)

    def isfinite(self):
        """
        DESCRIPTION:
            Function evaluates a variable or expression to determine if
            it is a finite floating value. A finite floating value is not
            a NaN (Not a Number) value and is not an infinity value.

        RETURNS:
            ColumnExpression.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml","titanic")

            # Create a DataFrame on 'titanic' table.
            >>> titanic = DataFrame.from_table('titanic')
            >>> df = titanic.select(["passenger", "age", "fare"])
            >>> print(df)
                        age      fare
            passenger
            326        36.0  135.6333
            183         9.0   31.3875
            652        18.0   23.0000
            40         14.0   11.2417
            774         NaN    7.2250
            366        30.0    7.2500
            509        28.0   22.5250
            795        25.0    7.8958
            61         22.0    7.2292
            469         NaN    7.7250
            >>>

            # Example 1: Find whether 'fare' column contains finite values or not.
            >>> finite_df = df.assign(finiteornot = df.fare.isfinite())
            >>> print(finite_df)
                        age    fare finiteornot
            passenger
            530        23.0  11.500           1
            591        35.0   7.125           1
            387         1.0  46.900           1
            856        18.0   9.350           1
            244        22.0   7.125           1
            713        48.0  52.000           1
            448        34.0  26.550           1
            122         NaN   8.050           1
            734        23.0  13.000           1
            265         NaN   7.750           1
            >>>

        """
        return _SQLColumnExpression(literal_column(f"TD_ISFINITE({self.compile()})"), type=INTEGER)
    
    def between(self, lower, upper):
        """
        DESCRIPTION:
            Evaluates whether the column value is between the lower and upper bounds.
            The lower and upper bounds are inclusive.

        PARAMETERS:
            lower:
                Required Argument.
                Specifies the lower bound value.
                Type: ColumnExpression or str or int or float
            
            upper:
                Required Argument.
                Specifies the upper bound value.
                Type: ColumnExpression or str or int or float

        RETURNS:
            ColumnExpression

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> print(df)
                        Feb    Jan    Mar    Apr    datetime
            accounts                                          
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017

            # Example 1: Check if column 'Feb' is between 100 and 200.
            >>> new_df = df[df.Feb.between(100, 200)]
            >>> print(new_df)
                       Feb    Jan  Mar  Apr    datetime
            accounts                                     
            Jones LLC  200.0  150  140  180.0  04/01/2017
            Red Inc    200.0  150  140    NaN  04/01/2017

            # Example 2: Check if column 'datetime' is between '01-01-2017' and '30-01-2017'.
            >>> new_df = df[df.datetime.between('01-01-2017', '30-01-2017')]
            >>> print(new_df)
                        Feb    Jan    Mar    Apr    datetime
            accounts                                          
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017           
        """
        return _SQLColumnExpression(self.expression.between(lower, upper))

    def begin(self):
        """
        DESCRIPTION:
            Retrieves the beginning date or timestamp from a PERIOD column.

        PARAMETERS:
            None.

        RETURNS:
            ColumnExpression.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "Employee_roles")

            # Create a DataFrame on 'employee_roles' table.
            >>> df = DataFrame("employee_roles")

            # Extract the starting date from the period column 'role_validity_period'
            # and assign it to a new column.
            >>> df = df.assign(start_date_col = df['role_validity_period'].begin())
            EmployeeID	    EmployeeName     Department      Salary	      role_validity_period	 start_date_col
                     1	        John Doe             IT     100.000	  ('20/01/01', '24/12/31')	       20/01/01
                     2	      Jane Smith             DA     200.000	  ('20/01/01', '99/12/31') 	       20/01/01
                     3	             Bob      Marketing     330.000	  ('25/01/01', '99/12/31')	       25/01/01
                     3	             Bob          Sales     300.000	  ('24/01/01', '24/12/31')	       24/01/01

        """
        _Validators._validate_period_column_type(self._type)
        element_type = DATE if isinstance(self._type, PERIOD_DATE) else TIMESTAMP
        return _SQLColumnExpression(literal_column(f"BEGIN({self.compile()})"), type = element_type)

    def end(self):
        """
        DESCRIPTION:
            Retrieves the ending date or timestamp from a PERIOD column.

        PARAMETERS:
            None.

        RETURNS:
            ColumnExpression.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Load the data to run the example.
            >>> load_example_data("teradataml", "Employee_roles")

            # Create a DataFrame on 'employee_roles' table.
            >>> df = DataFrame("employee_roles")

            # Extract the ending date from the period column 'role_validity_period'
            # and assign it to a new column.
            >>> df = df.assign(end_date_col = df['role_validity_period'].end())
            EmployeeID	  EmployeeName   Department      Salary	       role_validity_period	    end_date_col
                     1	      John Doe	         IT     100.000	   ('20/01/01', '24/12/31')	        24/12/31
                     2	    Jane Smith	         DA     200.000	   ('20/01/01', '99/12/31')	        99/12/31
                     3	           Bob	  Marketing     330.000	   ('25/01/01', '99/12/31')	        99/12/31
                     3	           Bob	      Sales     300.000	   ('24/01/01', '24/12/31')	        24/12/31

        """
        _Validators._validate_period_column_type(self._type)
        element_type = DATE if isinstance(self._type, PERIOD_DATE) else TIMESTAMP
        return _SQLColumnExpression(literal_column(f"END({self.compile()})"), type = element_type)