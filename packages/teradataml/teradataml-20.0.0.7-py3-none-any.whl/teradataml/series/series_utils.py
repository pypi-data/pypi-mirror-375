# -*- coding: utf-8 -*-
"""

Unpublished work.
Copyright (c) 2019 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rohit.khurd@teradata.com
Secondary Owner:

This file implements util functions of series.
"""

from teradataml.common.aed_utils import AedUtils
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils

from teradatasqlalchemy.dialect import preparer, dialect as td_dialect
import teradataml.dataframe as tdmldf


# TODO - Need to write unit testcases for these functions
class SeriesUtils:

    @staticmethod
    def _get_sorted_nrow(s, n, sort_col, axis, asc=True):
        """
        Internal Utility function that returns a teradataml Series containing n rows
        of the Series. The Series is sorted on the first column.

        PARAMETERS:
            s:  teradataml Series
            n:   Specifies the number of rows to select.
                 Type: int
            sort_col: The column to sort on.
                 Type: str
            axis : The axis used to use the DataFrame into a Series object.
            asc: (optional) - Specifies sort order.
                 If True, sort in ascending order.
                 If False, sort in descending order.
                 The default value is True.
                 Type: boolean

        RETURNS:
            teradataml Series

        EXAMPLES:
            SeriesFrameUtils._get_sorted_nrow(s, 10, 'col1')
            SeriesFrameUtils._get_sorted_nrow(s, 20, 'col1', asc=True)
            SeriesFrameUtils._get_sorted_nrow(s, 20, 'col1', 1, asc=True)
            SeriesFrameUtils._get_sorted_nrow(s, 30, 'col1', asc=False)

        """
        tdp = preparer(td_dialect)
        aed_utils = AedUtils()

        sort_order = "asc"
        if not asc:
            sort_order = "desc"

        # Note: This is considering only column based Series
        quoted_cols = [tdp.quote(s._name)]
        sel_cols_str = ",".join(quoted_cols)
        sel_row_num = "row_number() over (order by \"{0}\" {1}) - 1 as tdml_row_num, {2}".format(sort_col, sort_order, sel_cols_str)
        filter_str = "tdml_row_num < {0}".format(n)
        sel_nodeid = aed_utils._aed_select(s._nodeid, sel_row_num)
        fil_nodeid = aed_utils._aed_filter(sel_nodeid, filter_str)
        sel2_nodeid = aed_utils._aed_select(fil_nodeid, sel_cols_str)
        new_df = tdmldf.dataframe.DataFrame._from_node(sel2_nodeid, s._metaexpr, s._df_index_label)
        new_df._orderby = s._df_orderby
        return new_df.squeeze(axis)
