# -*- coding: utf-8 -*-
"""

Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: ellen.teradata@teradata.com
Secondary Owner:

This file implements the dataframe locator indexer.
"""
import numbers
import teradataml.dataframe as tdmldf
import sqlalchemy

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.constants import PythonTypes
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.common.aed_utils import AedUtils
from teradatasqlalchemy.dialect import preparer, dialect as td_dialect
from teradataml.dataframe.sql_interfaces import ColumnExpression

class _LocationIndexer():
    """
    Indexer class to access a group of rows and columns by label(s) or a boolean array for loc[].
    and to access a group of rows and columns by integer values or a boolean array for iloc[].
    """
    def __init__(self, df, integer_indexing=False):
        """
        Constructor for _LocationIndexer.

        PARAMETERS:
            df - The dataframe associated with this indexer.
            integer_indexing - If True, this indexer is for integer indexing (iloc[])
                               else this indexer is for label indexing (loc[])
                               Default value is False. 

        EXAMPLES:
            df._loc = _LocationIndexer(df)
            df._iloc = _LocationIndexer(df, integer_indexing=True)

        RAISES:

        """
        self._df = df
        self._integer_indexing = integer_indexing
        self._aed_utils = AedUtils()

    def __setitem__(self, key):
        raise NotImplementedError("Assignment using loc[] or iloc[] is not supported")

    def __getitem__(self, key):
        """
        Access a group of rows and columns by label(s) or ColumnExpression

        PARAMETERS:
            key: A single label, list of labels, or slice. 
                 A tuple containing keys for row and columns access.
                 No more than 2 keys in the tuple.
        RETURNS:
            teradataml DataFrame

        EXAMPLES:

        RAISES:
            TeradataMlException
        """
        try:
            if isinstance(key, tuple):
                return self._get_tuple_index(key, self._df)
            else:
                if self._integer_indexing:
                    return  self._get_integer_sort_index(key, self._df)
                else:
                    return  self._get_sort_index(key, self._df)
        except TeradataMlException:
            raise
        except Exception as err:
            errcode = MessageCodes.TDMLDF_INFO_ERROR
            msg = Messages.get_message(MessageCodes.TDMLDF_INFO_ERROR)
            raise TeradataMlException(msg, errcode) from err

    def _get_sort_index(self, key, df):
        """
        Access a group of rows by label(s)

        PARAMETERS:
            key: A single label, list of labels, slice, or ColumnExpression. 
            df: Parent DataFrame

        RETURNS:
            teradataml DataFrame

        EXAMPLES:

        RAISES:
            TeradataMlException
        """
        sort_col = df._get_sort_col()
        aed_utils = AedUtils()
        tdp = preparer(td_dialect)
        quoted_cols = [tdp.quote(c) for c in df.columns]
        sel_cols_str = ",".join(quoted_cols)

        if isinstance(key, tuple):
            msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format(type(key), "a single label, a list, or a slice")
            raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

        if isinstance(key, tdmldf.sql._SQLColumnExpression):
            filter_expr = key.compile()
            new_nodeid = self._aed_utils._aed_filter(df._nodeid, filter_expr)
            return df._create_dataframe_from_node(new_nodeid, df._metaexpr, df._index_label)
        elif isinstance(key, slice):
            if key.start is not None:
                df_utils._validate_sort_col_type(sort_col[1], key.start)
            if key.stop is not None:
                df_utils._validate_sort_col_type(sort_col[1], key.stop)
            
            if key.start is None and key.stop is None:
                sel_nodeid = aed_utils._aed_select(df._nodeid, sel_cols_str)
                return df._create_dataframe_from_node(sel_nodeid, df._metaexpr, df._index_label)
            elif key.start is not None and key.stop is not None:
                if sort_col[1] == PythonTypes.PY_STRING_TYPE.value:
                    filter_expr = "{0} between '{1}' and '{2}'".format(sort_col[0], key.start, key.stop)
                else:
                    filter_expr = "{0} between {1} and {2}".format(sort_col[0], key.start, key.stop)
                new_nodeid = self._aed_utils._aed_filter(df._nodeid, filter_expr)
                return df._create_dataframe_from_node(new_nodeid, df._metaexpr, df._index_label)
            elif key.start is not None:
                if sort_col[1] == PythonTypes.PY_STRING_TYPE.value:
                    filter_expr = "{0} >= '{1}'".format(sort_col[0], key.start)
                else:
                    filter_expr = "{0} >= {1}".format(sort_col[0], key.start)
                new_nodeid = self._aed_utils._aed_filter(df._nodeid, filter_expr)
                return df._create_dataframe_from_node(new_nodeid, df._metaexpr, df._index_label)
            else: #key.stop is not None:
                if sort_col[1] == PythonTypes.PY_STRING_TYPE.value:
                    filter_expr = "{0} <= '{1}'".format(sort_col[0], key.stop)
                else:
                    filter_expr = "{0} <= {1}".format(sort_col[0], key.stop)
                new_nodeid = self._aed_utils._aed_filter(df._nodeid, filter_expr)
                return df._create_dataframe_from_node(new_nodeid, df._metaexpr, df._index_label)
        else:
            df_utils._validate_sort_col_type(sort_col[1], key)
            key_list = key
            if not isinstance(key, list):
                key_list = [key_list]

            if len(key_list) == 0:
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_DROP_ARGS), MessageCodes.TDMLDF_DROP_ARGS)

            if sort_col[1] == PythonTypes.PY_STRING_TYPE.value:
                key_list = ["'{}'".format(x) for x in key_list]
            index_expr = ",".join(map(str, (key_list)))

            filter_expr = "{0} in ({1})".format(sort_col[0], index_expr)
            new_nodeid = self._aed_utils._aed_filter(df._nodeid, filter_expr)
            return df._create_dataframe_from_node(new_nodeid, df._metaexpr, df._index_label)

    def _get_integer_sort_index(self, key, df):
        """
        Access a group of rows using integer indexing

        PARAMETERS:
            key: A single integer, list of integers, or slice with integer values.
            df: Parent DataFrame

        RETURNS:
            teradataml DataFrame

        EXAMPLES:

        RAISES:
            TeradataMlException
        """
        sort_col = df._get_sort_col()
        tdp = preparer(td_dialect)
        aed_utils = AedUtils()
        sel_cols = [c for c in df.columns]
        quoted_cols = [tdp.quote(c) for c in sel_cols]

        if isinstance(key, tuple):
            msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format(type(key), "a single integer, a list of integers, or a slice")
            raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

        if isinstance(key, tdmldf.sql._SQLColumnExpression):
            msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format(type(key), "a single integer, a list of integers, or a slice")
            raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

        sel_cols_str = ",".join(quoted_cols)
        meta = sqlalchemy.MetaData()
        sel_row_num = "row_number() over (order by \"{0}\") - 1 as tdml_row_num, {1}".format(sort_col[0], sel_cols_str)

        if isinstance(key, slice):
            if key.start is not None and (not isinstance(key.start, int) or key.start < 0):
                msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(key.start, "start value", "integer >= 0")
                raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)
            if key.stop is not None and (not isinstance(key.stop, int) or key.stop <= 0):
                msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(key.stop, "stop value", "integer > 0")
                raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)

            if key.start is None and key.stop is None:
                sel_nodeid = aed_utils._aed_select(df._nodeid, sel_cols_str)
                return df._create_dataframe_from_node(sel_nodeid, df._metaexpr, df._index_label)

            if key.start is not None and key.stop is not None:
                filter_str = "tdml_row_num between {0} and {1}".format(key.start, key.stop -1)
            elif key.start is not None:
                filter_str = "tdml_row_num >= {0}".format(key.start)
            else: #key.stop is not None:
                filter_str = "tdml_row_num < {0}".format(key.stop)

            sel_nodeid = aed_utils._aed_select(df._nodeid, sel_row_num)
            fil_nodeid = aed_utils._aed_filter(sel_nodeid, filter_str)
            sel2_nodeid = aed_utils._aed_select(fil_nodeid, sel_cols_str)
            return df._create_dataframe_from_node(sel2_nodeid, df._metaexpr, df._index_label)
        else:
            key_list = key
            if not isinstance(key, list):
                key_list = [key_list]

            if len(key_list) == 0:
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_DROP_ARGS), MessageCodes.TDMLDF_DROP_ARGS)

            if all(isinstance(n, bool) for n in key_list):
                msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(key, "index value", "integer >= 0")
                raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)
            elif all(isinstance(n, int) for n in key_list):
                if any(n < 0 for n in key_list):
                    msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(key, "index value", "integer >= 0")
                    raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)
                index_expr = ",".join(map(str, (key_list)))
                filter_str = "tdml_row_num in ({0})".format(index_expr)
                sel_nodeid = aed_utils._aed_select(df._nodeid, sel_row_num)
                fil_nodeid = aed_utils._aed_filter(sel_nodeid, filter_str)
                sel2_nodeid = aed_utils._aed_select(fil_nodeid, sel_cols_str)
                return df._create_dataframe_from_node(sel2_nodeid, df._metaexpr, df._index_label)
            else:
                msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(key, "index value", "integer >= 0")
                raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)

    def _get_column_index(self, key, df):
        """
        Access a group of columns by label(s)

        PARAMETERS:
            key: A single label, list of labels, slice, or ColumnExpression.
            df: Parent DataFrame

        RETURNS:
            teradataml DataFrame

        EXAMPLES:

        RAISES:
            TeradataMlException
        """
        if isinstance(key, tuple):
            msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format(type(key), "a single label, a list, or a slice")
            raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

        columns = [c for c in df.columns]
        if isinstance(key, slice):
            if key.start is not None and not isinstance(key.start, str):
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES), 
                                        MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES)
            if key.stop is not None and not isinstance(key.stop, str):
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES), 
                                        MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES)
            if key.start is not None and key.start not in columns:
                msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL).format(key.start, columns)
                raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_COL)

            if key.stop is not None and key.stop not in columns:
                msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL).format(key.stop, columns)
                raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_COL)

            if key.start is None and key.stop is None:
                return df.select(columns)
            elif key.start is not None and key.stop is not None:
                start_index = columns.index(key.start)
                stop_index = columns.index(key.stop)
                if stop_index < start_index:
                    msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL).format(key.stop, columns)
                    raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_COL)
                key_list = columns[start_index : stop_index + 1]
            elif key.start is not None:
                start_index = columns.index(key.start)
                key_list = columns[start_index :]
            else: #key.stop is not None:
                stop_index = columns.index(key.stop)
                key_list = columns[ : stop_index + 1]

            return df.select(key_list)
        else:
            key_list = key
            if not isinstance(key, list):
                key_list = [key_list]

            if len(key_list) == 0:
                raise TeradataMlException(Messages.get_message(MessageCodes.DF_WITH_NO_COLUMNS), MessageCodes.DF_WITH_NO_COLUMNS)

            if all(isinstance(n, bool) for n in key_list):
                if len(key_list) != len(columns):
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES), 
                                        MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES)
                sel_cols = []
                for i in range (len(key_list)):
                    if key_list[i]:
                        sel_cols.append(columns[i])
                return df.select(sel_cols)
            elif all(isinstance(n, str) for n in key_list):
                return df.select(key_list)
            else:
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES), MessageCodes.TDMLDF_DROP_INVALID_COL_NAMES)

    def _get_integer_column_index(self, key, df):
        """
        Access a group of columns using integer indexing

        PARAMETERS:
            key: A single integer, list of integers, or a slice with integer values.
            df: Parent DataFrame

        RETURNS:
            teradataml DataFrame

        EXAMPLES:

        RAISES:
            TeradataMlException
        """
        if isinstance(key, tuple):
            msg = Messages.get_message(MessageCodes.TDMLDF_UNKNOWN_TYPE).format(type(key), "a single integer, a list of integers, or a slice")
            raise TeradataMlException(msg, MessageCodes.TDMLDF_UNKNOWN_TYPE)

        columns = [c for c in df.columns]
        if isinstance(key, slice):
            if key.start is not None and (not isinstance(key.start, int) or key.start < 0 or key.start >= len(columns)):
                msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL).format("start value", "0 to {}".format(len(columns) - 1))
                raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_COL)
            if key.stop is not None and (not isinstance(key.stop, int) or key.stop < 1 or key.stop > len(columns)):
                msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL).format("stop value", "1 to {}".format(len(columns)))
                raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_COL)
            
            if key.start is None and key.stop is None:
                new_key = slice(None, None, None)
            elif key.start is not None and key.stop is not None:
                new_key = slice(columns[key.start], columns[key.stop - 1], None)
            elif key.start is not None:
                new_key = slice(columns[key.start], None, None)
            else: #key.stop is not None:
                new_key = slice(None, columns[key.stop -1], None)

            return self._get_column_index(new_key, df)
        else:
            key_list = key
            if not isinstance(key, list):
                key_list = [key_list]

            if all(isinstance(n, bool) for n in key_list):
                return self._get_column_index(key, df)
            elif all(isinstance(n, int) for n in key_list):
                sel_cols = []
                for i in range (len(key_list)):
                    k = key_list[i]
                    if k < 0 or k >= len(columns):
                        msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL).format("list value", "0 to {}".format(len(columns) - 1))
                        raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_COL)
                    else:
                        sel_cols.append(columns[k])
                        
                return self._get_column_index(sel_cols, df)
            else:
                msg = Messages.get_message(MessageCodes.TDMLDF_DROP_INVALID_COL).format("list value", "0 to {}".format(len(columns) - 1))
                raise TeradataMlException(msg, MessageCodes.TDMLDF_DROP_INVALID_COL)

    def _get_tuple_index(self, key, df):
        """
        Access a group of rows and columns by label(s)

        PARAMETERS:
            key: A column name as a string or filter expression (ColumnExpression)
            df: Parent DataFrame

        RETURNS:
            teradataml DataFrame

        EXAMPLES:

        RAISES:
            TeradataMlException
        """
        if len(key) > 2:
            msg = Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(key, "for key index", "At most 2 key values for sort and/or column keys")
            raise TeradataMlException(msg, MessageCodes.INVALID_ARG_VALUE)
        if len(key) == 0: 
            sort_index = None
            column_index = [c for c in df.columns]
        elif len(key) == 1:
            sort_index = key[0]
            column_index = None
        else: #len(key) == 2
            sort_index = key[0]
            column_index = key[1]

        if sort_index is not None:
            if self._integer_indexing:
                new_df = self._get_integer_sort_index(sort_index, df)
            else:
                new_df = self._get_sort_index(sort_index, df)
        else:
            new_df = df

        if column_index is not None:
            if self._integer_indexing:
                return self._get_integer_column_index(column_index, new_df)
            else:
                return self._get_column_index(column_index, new_df)
        else:
            return new_df
