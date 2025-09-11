# -*- coding: utf-8 -*-
"""

Unpublished work.
Copyright (c) 2019 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rohit.khurd@teradata.com
Secondary Owner:

This file implements the teradataml Series.
A teradataml Series maps virtually to a single row or column of tables and views.
"""

import numbers
import inspect
import pandas as pd

from teradataml.common.aed_utils import AedUtils
from teradataml.common.constants import AEDConstants

from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.dbutils.dbutils import _execute_query_and_generate_pandas_df
from teradataml.series.series_utils import SeriesUtils as series_utils
from teradataml.common.utils import UtilFuncs
from teradataml.options.display import display

import teradataml.context.context as tdmlcntxt
from teradataml.common.constants import PythonTypes

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes


class Series:
    '''
    The teradataml Series object
    '''

    def __init__(self, axis, nodeid, col, **kw):
        """
        DESCRIPTION:
            Initialize the Series object.
            Note : Indexes for Series are currently unsupported.

        PARAMETERS:
            axis:
                Required argument.
                A specific axis to squeeze.
                Default Value: 1 (column).

            nodeid:
                Required argument.
                nodeid of the underlying teradataml DataFrame or Series object.

            col:
                Required argument.
                _SQLColumnExpression object from the underlying teradataml DataFrame or Series object.

        RAISES:
            TeradataMlException (USE_FUNCTION_TO_INSTANTIATE)
        """

        # Make sure the initialization happens only using the
        # one of the classmethods - _from_node and _from_dataframe
        if inspect.stack()[1][3] not in ['_from_dataframe', '_from_node']:
            raise TeradataMlException(Messages.get_message(
                                      MessageCodes.USE_FUNCTION_TO_INSTANTIATE).format('A teradataml Series object',
                                      'squeeze() from a teradataml.DataFrame instance.'),
                                      MessageCodes.USE_FUNCTION_TO_INSTANTIATE)

        # Required arguments
        self._axis = axis
        self._nodeid = nodeid
        self._col = col

        # Optional arguments
        self._df_orderby = kw.pop('order_by', None)
        self._df_index_label = kw.pop('index_label', None)
        self._datalake = kw.pop('datalake', None)

        # Derived attributes
        # Note that this is considering we have only one column,
        # and may change with the implementation of Row-based Series
        self._name = self._col.name
        self._col_type = UtilFuncs._teradata_type_to_python_type(self._col.type)

        # Underlying table/view name
        self._table_name = None

        try:
            self._aed_utils = AedUtils()
            self._metaexpr = UtilFuncs._get_metaexpr_using_columns(nodeid,
                                                                   zip([self._name],
                                                                       [self._col.type]),
                                                                   datalake=self._datalake)

        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(MessageCodes.SERIES_CREATE_FAIL) + str(err),
                                      MessageCodes.SERIES_CREATE_FAIL) from err

    @classmethod
    def _from_node(cls, axis, nodeid, col, df_orderby = None, df_index_label = None, **kw):
        """
        DESCRIPTION:
            Private class method for creating a teradataml Series from a nodeid, and parent metadata.

        PARAMETERS:
            axis:
                Required Argument.
                The axis of the parent Series object.
                Types : int

            nodeid:
                Required Argument.
                nodeid of the underlying teradataml Series object.
                Types : str

            col:
                Required Argument.
                The modified _SQLColumnExpression instance.
                Types : _SQLColumnExpression

            df_orderby:
                Optional Argument.
                The attribute of the underlying teradataml DataFrame listing the _order_by column/s .
                Types : str

            df_index_label:
                Optional Argument.
                Column/s used for sorting from the underlying teradataml DataFrame.
                Types : str

        EXAMPLES:
            from teradataml.series.series import Series
            s = Series._from_node(1, 1234, col)
            s = Series._from_node(1, 1234, col, ['col'], ['col'])

        RETURNS:
            teradataml Series

        RAISES:
            None

        """

        series = cls(axis,
                     nodeid,
                     col,
                     order_by = df_orderby,
                     index_label = df_index_label,
                     datalake=kw.pop("datalake", None))

        return series

    @classmethod
    def _from_dataframe(cls, df, axis = 1):
        """
        DESCRIPTION:
            Private class method for creating a teradataml Series from a teradataml DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                A teradataml DataFrame instance.

            axis:
                Optional Argument.
                A specific axis to squeeze.
                Default Value: 1 (column).

        EXAMPLES:
            from teradataml.series.series import Series
            s = Series._from_dataframe(df)
            s = Series._from_dataframe(df, 1)

        RETURNS:
            teradataml Series

        RAISES:
            TeradataMlException (USE_FUNCTION_TO_INSTANTIATE)

        """

        # TODO : Indexes are currently unsupported

        # Make sure the method is called only from DataFrame.squeeze()
        if inspect.stack()[1][3] not in ['squeeze']:
            raise TeradataMlException(Messages.get_message(
                                      MessageCodes.USE_FUNCTION_TO_INSTANTIATE).format('A teradataml Series object',
                                      'squeeze() from a teradataml.DataFrame instance.'),
                                      MessageCodes.USE_FUNCTION_TO_INSTANTIATE)

        # axis used in the DataFrame.squeeze()
        series = cls(axis,
                     df._nodeid,
                     df._metaexpr.c[0],
                     order_by=df._orderby,
                     index_label=df._index_label,
                     datalake=df._metaexpr.datalake)

        return series

    def __repr__(self):
        """
        Returns the string representation for a teradataml Series instance.
        The string contains:
            1. A default index for row numbers.
            2. At most the first max_rows rows of the series as mentioned in the note below.
            3. The name and datatype of the series.

        NOTES:
          - This makes an explicit call to get rows from the database.
          - To change number of rows to be printed set the max_rows option in options.display.display
          - Default value of max_rows is 10

        EXAMPLES:
            >>> df
               masters   gpa     stats programming admitted
            id
            22     yes  3.46    Novice    Beginner        0
            36      no  3.00  Advanced      Novice        0
            15     yes  4.00  Advanced    Advanced        1
            38     yes  2.65  Advanced    Beginner        1
            5       no  3.44    Novice      Novice        0
            17      no  3.83  Advanced    Advanced        1
            34     yes  3.85  Advanced    Beginner        0
            13      no  4.00  Advanced      Novice        1
            26     yes  3.57  Advanced    Advanced        1
            19     yes  1.98  Advanced    Advanced        0

            >>> gpa = df.select(["gpa"]).squeeze()
            >>> gpa
            0    4.00
            1    2.33
            2    3.46
            3    3.83
            4    4.00
            5    2.65
            6    3.57
            7    3.44
            8    3.85
            9    3.95
            Name: gpa, dtype: float64
        """
        # TODO : Change docstring based on implementation of RowBased Series object
        query = repr(self._metaexpr) + ' FROM ' + self._get_table_name()
        if self._df_orderby is not None:
            query += ' ORDER BY ' + self._df_orderby

        pandas_df = _execute_query_and_generate_pandas_df(query).squeeze(self._axis)
        return pandas_df.__repr__()

    def __get_sort_col(self):
        """
        Private method to retrieve sort column.
        Return the column and type in _metadata.

        PARAMETERS:
            None

        RETURNS:
            A tuple containing the column name and type of the first column in _metadata.

        RAISE:
            TeradataMlException

        EXAMPLES:
            sort_col = self.__get_sort_col()
        """
        unsupported_types = ['BLOB', 'CLOB', 'ARRAY', 'VARRAY']

        # Since indexes are currently unsupported, use the only column of df as default col for sorting
        col_name = self._name
        col_type = self._col_type

        if col_type == PythonTypes.PY_NULL_TYPE.value:
            raise TeradataMlException(Messages.get_message(MessageCodes.SERIES_INFO_ERROR),
                                      MessageCodes.SERIES_INFO_ERROR)

        sort_col_sqlalchemy_type = self._col.type
        # convert types to string from sqlalchemy type for the columns entered for sort
        sort_col_type = repr(sort_col_sqlalchemy_type).split("(")[0]
        if sort_col_type in unsupported_types:
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, sort_col_type,
                                                           "ANY, except following {}".format(unsupported_types)),
                                      MessageCodes.UNSUPPORTED_DATATYPE)

        return (col_name, col_type)

    def head(self, n=display.max_rows):
        """
        Print the first n rows of the sorted teradataml Series.
        Note: The Series is sorted on the column composing the Series object.
        The column type must support sorting.
        Unsupported types: ['BLOB', 'CLOB', 'ARRAY', 'VARRAY']

        PARAMETERS:
            n:
                Optional argument.
                Specifies the number of rows to select.
                Default Value: 10.
                Type: int

        RETURNS:
            teradataml Series

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming admitted
            id
            22     yes  3.46    Novice    Beginner        0
            36      no  3.00  Advanced      Novice        0
            15     yes  4.00  Advanced    Advanced        1
            38     yes  2.65  Advanced    Beginner        1
            5       no  3.44    Novice      Novice        0
            17      no  3.83  Advanced    Advanced        1
            34     yes  3.85  Advanced    Beginner        0
            13      no  4.00  Advanced      Novice        1
            26     yes  3.57  Advanced    Advanced        1
            19     yes  1.98  Advanced    Advanced        0

            >>> gpa = df.select(["gpa"]).squeeze()
            >>> gpa
            0    4.00
            1    2.33
            2    3.46
            3    3.83
            4    4.00
            5    2.65
            6    3.57
            7    3.44
            8    3.85
            9    3.95
            Name: gpa, dtype: float64

            >>> gpa.head()
            0    2.33
            1    3.00
            2    3.13
            3    3.44
            4    3.46
            5    3.46
            6    3.45
            7    2.65
            8    1.98
            9    1.87
            Name: gpa, dtype: float64

            >>> gpa.head(15)
            0     2.33
            1     3.00
            2     3.13
            3     3.44
            4     3.46
            5     3.46
            6     3.50
            7     3.50
            8     3.50
            9     3.52
            10    3.55
            11    3.45
            12    2.65
            13    1.98
            14    1.87
            Name: gpa, dtype: float64

            >>> gpa.head(5)
            0    2.33
            1    3.00
            2    2.65
            3    1.98
            4    1.87
            Name: gpa, dtype: float64
        """

        if self._metaexpr is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.SERIES_INFO_ERROR),
                                      MessageCodes.SERIES_INFO_ERROR)
        try:
            if not isinstance(n, numbers.Integral) or n <= 0:
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT).format("n"), MessageCodes.TDMLDF_POSITIVE_INT)

            sort_col = self.__get_sort_col()

            series = series_utils._get_sorted_nrow(self, n, sort_col[0], self._axis, asc=True)
            series._metaexpr._n_rows = n
            return series

        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(MessageCodes.SERIES_INFO_ERROR) + str(err),
                                      MessageCodes.SERIES_INFO_ERROR) from err

    def unique(self):
        """
        Return a Series object with unique values.

        PARAMETERS:
            None

        RETURNS:
            Series object with unique values.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame.from_query('select admitted from admissions_train')
            >>> s = df.squeeze(axis = 1)
            >>> s
            0    1
            1    1
            2    0
            3    0
            4    1
            5    0
            6    1
            7    0
            8    0
            9    1
            Name: admitted, dtype: object

            >>> s.unique()
            0    0
            1    1
            Name: admitted, dtype: object
        """

        if self._metaexpr is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.SERIES_INFO_ERROR),
                                      MessageCodes.SERIES_INFO_ERROR)

        try:
            kwargs = {}
            kwargs[self._name] = self._col._unique()
            (new_meta, result) = self._metaexpr._assign(drop_columns=True, **kwargs)

            # join the expressions in result
            assign_expression = ', '.join(list(map(lambda x: x[1], result)))
            new_nodeid = self._aed_utils._aed_assign(self._nodeid,
                                                     assign_expression,
                                                     AEDConstants.AED_ASSIGN_DROP_EXISITING_COLUMNS.value)

            return Series._from_node(self._axis, new_nodeid, new_meta.c[0],
                                     self._df_orderby, self._df_index_label,
                                     datalake=self._metaexpr.datalake)

        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(MessageCodes.SERIES_CREATE_FAIL) + str(err),
                                      MessageCodes.SERIES_CREATE_FAIL) from err

    def _get_table_name(self):
        """
        RETURNS:
            Underlying table_name for Series

        EXAMPLES:
            >>> gpa._get_table_name()
            'admissions_train'
        """
        if self._table_name is None:
            self._table_name = df_utils._execute_node_return_db_object_name(self._nodeid)

        return self._table_name

    @property
    def name(self):
        """
        RETURNS:
            The name of the Series

        EXAMPLES:
            >>> gpa.name
            'gpa'
        """
        return self._name

    def __gt__(self, other):
        raise NotImplementedError

    def __ge__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    def __le__(self, other):
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __invert__(self):
        raise NotImplementedError

    def __eq__(self):
        raise NotImplementedError

    def __ne__(self):
        raise NotImplementedError

    def __xor__(self):
        raise NotImplementedError

    def __add__(self):
        raise NotImplementedError

    def __mul__(self):
        raise NotImplementedError

    def __sub__(self):
        raise NotImplementedError

    def __truediv__(self):
        raise NotImplementedError

    def __floordiv__(self):
        raise NotImplementedError

    def __mod__(self):
        raise NotImplementedError
