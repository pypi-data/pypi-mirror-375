#!/usr/bin/python
# ##################################################################
#
# Copyright 2019 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Rohit Khurd (rohit.khurd@teradata.com
# Secondary Owner: Abhinav Sahu (abhinav.sahu@teradata.com)
#
# This file implements APIs and utility functions for set operations.
# ##################################################################

import inspect, importlib
from collections import OrderedDict
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe import dataframe
from teradataml.dataframe.dataframe_utils import DataFrameUtils as df_utils
from teradataml.common.aed_utils import AedUtils
from teradataml.dataframe.sql import _MetaExpression
from teradataml.utils.validators import _Validators
from teradatasqlalchemy.dialect import dialect as td_dialect, TeradataTypeCompiler as td_type_compiler
from teradatasqlalchemy import (GEOMETRY, MBR, MBB)
from teradatasql import OperationalError

from teradataml.telemetry_utils.queryband import collect_queryband

module = importlib.import_module("teradataml")

def __validate_setop_args(df_list, awu_matrix, setop_type):
    """
    DESCRIPTION:
        Internal function to check for the validity of the input arguments.
    
    PARAMETERS:
        df_list:
            Required argument.
            Specifies the list of teradataml DataFrames.
            Types: list of teradataml DataFrames
        
        awu_matrix:
            Required argument.
            Specifies the argument is expected to be a list of arguments, expected types are 
            mentioned as type or tuple.
            
        setop_type:
            Required argument.
            Specifies the type of SET Operation to be performed.
            Types: str
    
    RAISES:
        TeradataMlException

    EXAMPLES:
        __validate_setop_args(df_list, awu_matrix, setop_type)
        
    """
    # Validate argument types
    _Validators._validate_function_arguments(awu_matrix)
    
    # Validate the number of dfs in df_list
    if len(df_list) < 2:
        raise TeradataMlException(Messages.get_message(MessageCodes.SETOP_INVALID_DF_COUNT,
                                                       setop_type), 
                                                       MessageCodes.SETOP_INVALID_DF_COUNT)
        
    # Validate if all items in df_list are DataFrames
    for i in range(len(df_list)):
        _Validators._validate_function_arguments([['df_list[{0}]'.format(i), df_list[i], 
                                                   False, (dataframe.DataFrame)]])
    
    # Validate number of columns for 'td_intersect' and 'td_minus'
    if setop_type in ['td_intersect', 'td_minus', 'td_except']:
        it = iter(df_list[i].columns for i in range(len(df_list)))
        the_len = len(next(it))
        if not all(len(l) == the_len for l in it):
            raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_DF_LENGTH),
                                      MessageCodes.INVALID_DF_LENGTH)


def __check_concat_compatibility(df_list, join, sort, ignore_index):
    """
    DESCRIPTION:
        Internal function to check if the DataFrames are compatible for concat or not.
    
    PARAMETERS:
        df_list:
            Required argument.
            Specifies the list of teradataml DataFrames to be concatenated.
            Type: list of teradataml DataFrames
    
        join:
            Required argument.
            Specifies the type of join to use in concat ('inner' or 'outer').
            Type: str
    
        sort:
            Required argument.
            Specifies a flag to determine whether the columns should be sorted while being projected.
            Type: bool
        
        ignore_index:
            Required argument.
            Specifies whether to ignore the index columns in resulting DataFrame or not.
            Types: bool

    RETURNS:
        A tuple of the following form:
        (master_column_dict, is_lazy)

        where master_column_dict is a dictionary with the column names to project as a result as the keys,
        and is of the following form:
        {
            '<col_name_1>' : {
                                 'col_present' : [True, False],
                                 'col_type': <type>
                             },
            '<col_name_2>' : {
                                 ...
                             },
            ...
        }

        The value of the keys in the dictionary is again a dictionary with the following elements:
        1. 'col_present': A list of booleans, the nth value in it indicating the columns presence in the nth DF.
                          Presence specified by True, and absence by False,
        2. 'col_type':    The teradatasqlalchemy datatype of the column in the first DF that the column is present in,

        and 'is_lazy' is a boolean which indicates whether the result DataFrame creation should be a lazy operation
        or not, based on the column type compatibility.

    RAISES:
        None

    EXAMPLES:
        columns_dict, is_lazy = __check_concat_compatibility(df_list, join, sort)
    """
    dfs_to_operate_on = df_list

    # Initialize the return objects including a variable deciding whether the execution is lazy or not.
    # The execution will be non-lazy if the types of columns are not an exact match.
    # TODO: Add a set operation type compatibility matrix for use to make this operation completely lazy
    #       https://jira.td.teradata.com/jira/browse/ELE-1913

    col_dict = OrderedDict()
    is_lazy = True

    # Iterate on all DFs to be applied for set operation.
    for df in dfs_to_operate_on:
        # Process each column in the DF of the iteration.
        for c in df._metaexpr.c:
            col_name = c.name
            # Process the column name if it is not already processed.
            # Processing of set operation is column name based so if the DF in the nth iteration had column 'xyz',
            # then the column with the same name in any DF in later iterations need not be processed.
            if col_name not in col_dict:
                # For every column, it's entry in the dictionary looks like:
                # '<column_name>' : { 'col_present' : [True, False], 'col_type': <type> }
                #   where :
                #       '<column_name>' : is the name of the column being processed.
                #
                #       It's value is yet another dictionary with keys:
                #       'col_present'   : Its value is a list of booleans, the nth value in it indicating the
                #                         columns presence in the nth DF - presence specified by True,
                #                         and absence by False.
                #       'col_type'      : Its value is the teradatasqlalchemy type of the column in the first DF
                #                         that the column is present in.

                # Generate a list of booleans, each value of it indicating the columns presence in the DF in the
                # dfs_to_operate_on list. If ignore_index is True then assign False so that we can ignore when 
                # forming dict.
                
                col_present_in_dfs = []
                for inner_df in dfs_to_operate_on:
                    col_present_in_df = None
                    if ignore_index and inner_df.index and col_name in inner_df._index_label:
                        col_present_in_df = False
                    else:
                        col_present_in_df = df_utils._check_column_exists(col_name, inner_df.columns)
                    col_present_in_dfs.append(col_present_in_df)

                if join.upper() == 'INNER':
                    # For inner join, column has to present in all DFs.
                    if all(col_present_in_dfs):
                        col_dict[col_name] = {}

                        # Get the type of the column in all the DFs.
                        col_types_in_dfs = [inner_df._metaexpr.t.c[col_name].type for inner_df in
                                            dfs_to_operate_on]

                        # Populate the 'column_present' list using the col_present_in_dfs.
                        col_dict[col_name]['col_present'] = col_present_in_dfs
                        # The type to be used for the column is the one of the first DF it is present in.
                        col_dict[col_name]['col_type'] = col_types_in_dfs[0]
                        # Column name stored with quotes if required.
                        col_dict[col_name]['name'] = c.compile()

                        # If the type of the column in all DFs is not the same, then the operation is not lazy.
                        if not all(ctype == col_dict[col_name]['col_type']
                                   for ctype in col_types_in_dfs):
                            is_lazy = False

                elif join.upper() == 'OUTER':
                    # If the column is marked as False for all DataFrames
                    if not any(col_present_in_dfs):
                        pass
                    else:
                        # For outer join, column need not be present in all DFs.
                        col_dict[col_name] = {}
                        # Get the type of the column in all the DFs. None for the DF it is not present in.
                        col_types_in_dfs = [None if not present else inner_df._metaexpr.t.c[col_name].type
                                            for (inner_df, present) in zip(dfs_to_operate_on, col_present_in_dfs)]

                        # Find the type of the column in the first DF it is present in.
                        non_none_type_to_add = next(ctype for ctype in col_types_in_dfs if ctype is not None)
    
                        # Populate the 'column_present' list using the col_present_in_dfs.
                        col_dict[col_name]['col_present'] = col_present_in_dfs
                        # The type to be used for the column is the one of the first DF it is present in.
                        col_dict[col_name]['col_type'] = non_none_type_to_add
                        # Column name stored with quotes if required.
                        col_dict[col_name]['name'] = c.compile()
    
                        # If the type of the column in all DFs is not the same, then the operation is not lazy.
                        if not all(True if ctype is None else ctype == non_none_type_to_add
                                   for ctype in col_types_in_dfs):
                            is_lazy = False

    # Sort if required
    if sort and join.upper() == 'OUTER':
        col_dict = OrderedDict(sorted(col_dict.items()))
        
    # If the result has no columns, i.e. no data
    if len(col_dict) < 1:
        raise TeradataMlException(Messages.get_message(MessageCodes.DF_WITH_NO_COLUMNS),
                                  MessageCodes.DF_WITH_NO_COLUMNS)

    return col_dict, is_lazy


def __check_setop_if_lazy(df_list):
    """
    DESCRIPTION:
        Internal function to check if the teradataml DataFrames column types are compatible for 
        any set operation or not.
    
    PARAMETERS:
        df_list:
            Required argument.
            Specifies the list of teradataml DataFrames.
            Types: list of teradataml DataFrames
    
    RETURNS:
        A boolean 'is_lazy' which indicates whether the result DataFrame creation should be a 
        lazy operation or not.

    RAISES:
        None

    EXAMPLES:
        is_lazy = __check_setop_if_lazy(df_list)
    """

    # Initialize the return variable deciding whether the execution is lazy or not.
    # The execution will be non-lazy if the types of columns are not an exact match.
    is_lazy = True

    # Take first df's metadata for columns and then iterate for column_names on first DF which 
    # has to be projected for any set operation.
    for i, col in enumerate(df_list[0]._metaexpr.t.c):
        for k in range(1, len(df_list)) :
            next_df_cols = df_list[k].columns
            next_df_type = df_list[k]._metaexpr.t.c[next_df_cols[i]].type
            if (type(next_df_type) != type(col.type)):
                is_lazy = False

    return is_lazy


def __process_operation(meta_data, is_lazy, setop_type, nodeid, index_label, index_to_use, class_name = None):
    """
    DESCRIPTION:
        Internal function to process the columns as per given nodeid and setop_type, and 
        return the result DataFrame.
            
    PARAMETERS:
        meta_data:
            Required argument.
            Specifies either a metaexpr for the first DataFrame or a dictionary with the 
            column names as dictionary keys to be projected as a result. If a dict, the value 
            of the keys in the dictionary is again a dictionary with the elements mentioning 
            column presence and its type.
            Types: _MetaExpression, OrderedDict
        
        is_lazy:
            Required argument.
            Specifies a boolean based on the column type compatibility, indicating 
            whether set operation is lazy or not. 
            Types: bool
        
        setop_type:
            Required argument.
            Specifies the type of SET Operation to be performed.
            Types: str
        
        nodeid:
            Required argument.
            node id for the teradataml DataFrame.
        
        index_label:
            Required argument.
            Specifies list of index columns for teradataml DataFrame.
            Types: list
            
        index_to_use:
            Required argument.
            Specifies column(s) which can also be part of final index_label list.
            Types: list

        class_name:
            Optional argument.
            Specifies the name of the class for the first dataframe for deciding the
            return type of the output dataframe.
            Default: None
            Types: String

    RETURNS:
        teradataml DataFrame

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>> __process_operation(meta_data, is_lazy, setop_type, concat_nodeid, index_label, index_to_use)
        
    """

    # Separate processing for concat and other set operators as concat has OrderedDict as metadata.
    if setop_type == 'concat':
        class_name = "DataFrame"
        column_info = list((col_name, meta_data[col_name]['col_type']) for col_name in meta_data)
        for col in column_info:
            if isinstance(col[1], (GEOMETRY, MBR, MBB)):
                class_name = "GeoDataFrame"
                break

        # Constructing new Metadata (_metaexpr) without DB; using dummy nodeid and get new metaexpr for nodeid.
        meta_data = UtilFuncs._get_metaexpr_using_columns(nodeid, column_info,
                                                          datalake=meta_data.datalake if isinstance(meta_data, _MetaExpression) else None) if is_lazy \
            else meta_data

    if is_lazy:
        return getattr(module, class_name)._from_node(nodeid, meta_data, index_label)
    else:
        try:
            # Execute node and get table_name to build DataFrame on.
            table_name = df_utils._execute_node_return_db_object_name(nodeid)
            return getattr(module, class_name).from_table(table_name, index_label=index_to_use)
        except TeradataMlException as err:
            # We should be here only because of failure caused in creating DF.
            # due to incompatible types, but a TeradataMLException is raised when DF creation fails.
            raise TeradataMlException(Messages.get_message(MessageCodes.SETOP_COL_TYPE_MISMATCH, setop_type),
                                      MessageCodes.SETOP_COL_TYPE_MISMATCH) from err
        except OperationalError:
            raise


@collect_queryband(queryband="concat")
def concat(df_list, join='OUTER', allow_duplicates=True, sort=False, ignore_index=False):
    """
    DESCRIPTION:
        Concatenates a list of teradataml DataFrames, GeoDataFrames, or both along the index axis.

    PARAMETERS:
        df_list:
            Required argument.
            Specifies a list of teradataml DataFrames, GeoDataFrames, or both on which the
            concatenation is to be performed.
            Types: list of teradataml DataFrames and/or GeoDataFrames

        join:
            Optional argument.
            Specifies how to handle indexes on columns axis.
            Supported values are:
            • 'OUTER': It instructs the function to project all columns from all the DataFrames.
                       Columns not present in any DataFrame will have a SQL NULL value.
            • 'INNER': It instructs the function to project only the columns common to all DataFrames.
            Default value: 'OUTER'
            Permitted values: 'INNER', 'OUTER'
            Types: str

        allow_duplicates:
            Optional argument.
            Specifies if the result of concatenation can have duplicate rows.
            Default value: True
            Types: bool

        sort:
            Optional argument.
            Specifies a flag to sort the columns axis if it is not already aligned when 
            the join argument is set to 'outer'.
            Default value: False
            Types: bool
            
        ignore_index:
            Optional argument.
            Specifies whether to ignore the index columns in resulting DataFrame or not.
            If True, then index columns will be ignored in the concat operation.
            Default value: False
            Types: bool

    RETURNS:
        teradataml DataFrame, if result does not contain any geometry data, otherwise returns teradataml GeoDataFrame.

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>> from teradataml import load_example_data
        >>> load_example_data("dataframe", "admissions_train")
        >>> load_example_data("geodataframe", ["sample_shapes"])
        >>> from teradataml.dataframe import concat
        >>>
        >>> # Default options
        >>> df = DataFrame('admissions_train')
        >>> df1 = df[df.gpa == 4].select(['id', 'stats', 'masters', 'gpa'])
        >>> df1
               stats masters  gpa
        id
        13  Advanced      no  4.0
        29    Novice     yes  4.0
        15  Advanced     yes  4.0
        >>> df2 = df[df.gpa < 2].select(['id', 'stats', 'programming', 'admitted'])
        >>> df2
               stats programming admitted
        id
        24  Advanced      Novice        1
        19  Advanced    Advanced        0
        >>> cdf = concat([df1, df2])
        >>> cdf
               stats masters  gpa programming admitted
        id
        19  Advanced    None  NaN    Advanced        0
        24  Advanced    None  NaN      Novice        1
        13  Advanced      no  4.0        None     None
        29    Novice     yes  4.0        None     None
        15  Advanced     yes  4.0        None     None
        >>>
        >>> # concat more than two DataFrames
        >>> df3 = df[df.gpa == 3].select(['id', 'stats', 'programming', 'gpa'])
        >>> df3
               stats programming  gpa
        id
        36  Advanced      Novice  3.0
        >>> cdf = concat([df1, df2, df3])
        >>> cdf
             stats masters  gpa programming  admitted
        id
        15  Advanced     yes  4.0        None       NaN
        19  Advanced    None  NaN    Advanced       0.0
        36  Advanced    None  3.0      Novice       NaN
        29    Novice     yes  4.0        None       NaN
        13  Advanced      no  4.0        None       NaN
        24  Advanced    None  NaN      Novice       1.0

        >>> # join = 'inner'
        >>> cdf = concat([df1, df2], join='inner')
        >>> cdf
               stats
        id
        19  Advanced
        24  Advanced
        13  Advanced
        29    Novice
        15  Advanced
        >>>
        >>> # allow_duplicates = True (default)
        >>> cdf = concat([df1, df2])
        >>> cdf
               stats masters  gpa programming admitted
        id
        19  Advanced    None  NaN    Advanced        0
        24  Advanced    None  NaN      Novice        1
        13  Advanced      no  4.0        None     None
        29    Novice     yes  4.0        None     None
        15  Advanced     yes  4.0        None     None
        >>> cdf = concat([cdf, df2])
        >>> cdf
               stats masters  gpa programming admitted
        id
        19  Advanced    None  NaN    Advanced        0
        13  Advanced      no  4.0        None     None
        24  Advanced    None  NaN      Novice        1
        24  Advanced    None  NaN      Novice        1
        19  Advanced    None  NaN    Advanced        0
        29    Novice     yes  4.0        None     None
        15  Advanced     yes  4.0        None     None
        >>>
        >>> # allow_duplicates = False
        >>> cdf = concat([cdf, df2], allow_duplicates=False)
        >>> cdf
               stats masters  gpa programming admitted
        id
        19  Advanced    None  NaN    Advanced        0
        29    Novice     yes  4.0        None     None
        24  Advanced    None  NaN      Novice        1
        15  Advanced     yes  4.0        None     None
        13  Advanced      no  4.0        None     None
        >>>
        >>> # sort = True
        >>> cdf = concat([df1, df2], sort=True)
        >>> cdf
           admitted  gpa masters programming     stats
        id
        19        0  NaN    None    Advanced  Advanced
        24        1  NaN    None      Novice  Advanced
        13     None  4.0      no        None  Advanced
        29     None  4.0     yes        None    Novice
        15     None  4.0     yes        None  Advanced
        >>> 
        >>> # ignore_index = True
        >>> cdf = concat([df1, df2], ignore_index=True)
        >>> cdf
              stats masters  gpa programming  admitted
        0  Advanced     yes  4.0        None       NaN
        1  Advanced    None  NaN    Advanced       0.0
        2    Novice     yes  4.0        None       NaN
        3  Advanced    None  NaN      Novice       1.0
        4  Advanced      no  4.0        None       NaN

        # Perform concatenation of two GeoDataFrames
        >>> geo_dataframe = GeoDataFrame('sample_shapes')
        >>> geo_dataframe1 = geo_dataframe[geo_dataframe.skey == 1004].select(['skey','linestrings'])
        >>> geo_dataframe1

        skey            linestrings
        1004  LINESTRING (10 20 30,40 50 60,70 80 80)

        >>> geo_dataframe2 = geo_dataframe[geo_dataframe.skey < 1010].select(['skey','polygons'])
        >>> geo_dataframe2

        skey                                                              polygons
        1009                               MULTIPOLYGON (((0 0 0,0 20 20,20 20 20,20 0 20,0 0 0)),((50 50 50,50 90 90,90 90 90,90 50 90,50 50 50)))
        1005  POLYGON ((0 0 0,0 0 20.435,0.0 20.435 0,0.0 20.435 20.435,20.435 0.0 0,20.435 0.0 20.435,20.435 20.435 0,20.435 20.435 20.435,0 0 0))
        1004                                                POLYGON ((0 0 0,0 10 20,20 20 30,20 10 0,0 0 0),(5 5 5,5 10 10,10 10 10,10 10 5,5 5 5))
        1002                                                                          POLYGON ((0 0,0 20,20 20,20 0,0 0),(5 5,5 10,10 10,10 5,5 5))
        1001                                                                                                    POLYGON ((0 0,0 20,20 20,20 0,0 0))
        1003                                                                                POLYGON ((0.6 0.8,0.6 20.8,20.6 20.8,20.6 0.8,0.6 0.8))
        1007                                                                  MULTIPOLYGON (((1 1,1 3,6 3,6 0,1 1)),((10 5,10 10,20 10,20 5,10 5)))
        1006                                                          POLYGON ((0 0 0,0 0 20,0 20 0,0 20 20,20 0 0,20 0 20,20 20 0,20 20 20,0 0 0))
        1008                                             MULTIPOLYGON (((0 0,0 20,20 20,20 0,0 0)),((0.6 0.8,0.6 20.8,20.6 20.8,20.6 0.8,0.6 0.8)))


        >>> concat([geo_dataframe1,geo_dataframe2])

        skey                                    linestrings                                 polygons
        1009                                     None                               MULTIPOLYGON (((0 0 0,0 20 20,20 20 20,20 0 20,0 0 0)),((50 50 50,50 90 90,90 90 90,90 50 90,50 50 50)))
        1005                                     None  POLYGON ((0 0 0,0 0 20.435,0.0 20.435 0,0.0 20.435 20.435,20.435 0.0 0,20.435 0.0 20.435,20.435 20.435 0,20.435 20.435 20.435,0 0 0))
        1004  LINESTRING (10 20 30,40 50 60,70 80 80)                                                                                                                                   None
        1004                                     None                                                POLYGON ((0 0 0,0 10 20,20 20 30,20 10 0,0 0 0),(5 5 5,5 10 10,10 10 10,10 10 5,5 5 5))
        1003                                     None                                                                                POLYGON ((0.6 0.8,0.6 20.8,20.6 20.8,20.6 0.8,0.6 0.8))
        1001                                     None                                                                                                    POLYGON ((0 0,0 20,20 20,20 0,0 0))
        1002                                     None                                                                          POLYGON ((0 0,0 20,20 20,20 0,0 0),(5 5,5 10,10 10,10 5,5 5))
        1007                                     None                                                                  MULTIPOLYGON (((1 1,1 3,6 3,6 0,1 1)),((10 5,10 10,20 10,20 5,10 5)))
        1006                                     None                                                          POLYGON ((0 0 0,0 0 20,0 20 0,0 20 20,20 0 0,20 0 20,20 20 0,20 20 20,0 0 0))
        1008                                     None                                             MULTIPOLYGON (((0 0,0 20,20 20,20 0,0 0)),((0.6 0.8,0.6 20.8,20.6 20.8,20.6 0.8,0.6 0.8)))

        # Perform concatenation of a DataFrame and GeoDataFrame which returns a GeoDataFrame.
        >>> normal_df=df.select(['id','stats'])
        >>> normal_df
            stats
        id
        34  Advanced
        32  Advanced
        11  Advanced
        40    Novice
        38  Advanced
        36  Advanced
        7     Novice
        26  Advanced
        19  Advanced
        13  Advanced
        >>> geo_df = geo_dataframe[geo_dataframe.skey < 1010].select(['skey', 'polygons'])
        >>> geo_df

        skey                                                                            polygons
        1003                                                                                POLYGON ((0.6 0.8,0.6 20.8,20.6 20.8,20.6 0.8,0.6 0.8))
        1008                                             MULTIPOLYGON (((0 0,0 20,20 20,20 0,0 0)),((0.6 0.8,0.6 20.8,20.6 20.8,20.6 0.8,0.6 0.8)))
        1006                                                          POLYGON ((0 0 0,0 0 20,0 20 0,0 20 20,20 0 0,20 0 20,20 20 0,20 20 20,0 0 0))
        1009                               MULTIPOLYGON (((0 0 0,0 20 20,20 20 20,20 0 20,0 0 0)),((50 50 50,50 90 90,90 90 90,90 50 90,50 50 50)))
        1005  POLYGON ((0 0 0,0 0 20.435,0.0 20.435 0,0.0 20.435 20.435,20.435 0.0 0,20.435 0.0 20.435,20.435 20.435 0,20.435 20.435 20.435,0 0 0))
        1007                                                                  MULTIPOLYGON (((1 1,1 3,6 3,6 0,1 1)),((10 5,10 10,20 10,20 5,10 5)))
        1001                                                                                                    POLYGON ((0 0,0 20,20 20,20 0,0 0))
        1002                                                                          POLYGON ((0 0,0 20,20 20,20 0,0 0),(5 5,5 10,10 10,10 5,5 5))
        1004                                                POLYGON ((0 0 0,0 10 20,20 20 30,20 10 0,0 0 0),(5 5 5,5 10 10,10 10 10,10 10 5,5 5 5))

        >>> idf = concat([normal_df, geo_df])
        >>> idf
            stats     skey   polygons
        id
        38  Advanced  None     None
        7     Novice  None     None
        26  Advanced  None     None
        17  Advanced  None     None
        34  Advanced  None     None
        13  Advanced  None     None
        32  Advanced  None     None
        11  Advanced  None     None
        15  Advanced  None     None
        36  Advanced  None     None
    >>>
    """
    concat_join_permitted_values = ['INNER', 'OUTER']

    # Below matrix is list of list, where in each row contains following elements:
    # Let's take an example of following, just to get an idea:
    #   [element1, element2, element3, element4, element5, element6]
    #   e.g.
    #       ["join", join, True, (str), True, concat_join_permitted_values]

    #   1. element1 --> Argument Name, a string. ["join" in above example.]
    #   2. element2 --> Argument itself. [join]
    #   3. element3 --> Specifies a flag that mentions argument is optional or not.
    #                   False, means required and True means optional.
    #   4. element4 --> Tuple of accepted types. (str) in above example.
    #   5. element5 --> True, means validate for empty value. Error will be raised, if empty values is passed.
    #                   If not specified, means same as specifying False.
    #   6. element6 --> A list of permitted values, an argument can accept.
    #                   If not specified, it is as good as passing None. If a list is passed, validation will be
    #                   performed for permitted values.
    awu_matrix = []
    awu_matrix.append(["df_list", df_list, False, (list)])
    awu_matrix.append(["join", join, True, (str), True, concat_join_permitted_values])
    awu_matrix.append(["allow_duplicates", allow_duplicates, False, (bool)])
    awu_matrix.append(["sort", sort, False, (bool)])
    awu_matrix.append(["ignore_index", ignore_index, False, (bool)])
    setop_type='concat'

    # Validate Set operator arguments
    __validate_setop_args(df_list, awu_matrix, setop_type)

    # Generate the columns and their type to output, and check if the evaluation has to be lazy
    master_columns_dict, is_lazy = __check_concat_compatibility(df_list, join, sort, ignore_index)

    try:
        aed_utils = AedUtils()
        
        # Set the index_label to columns in first df's index_label if it is being projected,
        # else set it to columns in second df's index_label if it is being projected, else go on till last.
        # Finally set to None if none of df's have index_label
        index_label = None
        index_to_use = None
        for df in df_list:
            if df._index_label is not None and any(ind_col in master_columns_dict for ind_col in df._index_label):
                index_label = []
                index_to_use = df._index_label
                break

        if index_to_use is not None:
            for ind_col in index_to_use:
                if ind_col in master_columns_dict:
                    index_label.append(ind_col)
                    
        # Remove index columns if 'ignore_index' is set to True from master_columns_dict
        if ignore_index and index_to_use is not None:
            index_label = None
            index_to_use = None

        col_list = []
        for i in range(len(df_list)):
            col_list.append([])

        # Now create the list of columns for each DataFrame to concatenate
        type_compiler = td_type_compiler(td_dialect)

        for col_name, value in master_columns_dict.items():
            for i in range(len(col_list)):
                # Quoting is already done for column names if column name starts with number or it is reserved keywords.
                # Here checking again if it is teradata keyword or not for quotes.
                column_name = UtilFuncs._process_for_teradata_keyword(value['name'])
                if not value['col_present'][i]:
                    col_list[i].append('CAST(NULL as {}) as {}'.format(type_compiler.process(value['col_type']), column_name))
                else:
                    col_list[i].append(column_name)

        input_table_columns = []
        for i in range(len(col_list)):
            input_table_columns.append(','.join(col_list[i]))

        concat_nodeid = aed_utils._aed_setop([df._nodeid for df in df_list], 
                                             'unionall' if allow_duplicates else 'union',
                                             input_table_columns)
        return __process_operation(master_columns_dict, is_lazy, setop_type, concat_nodeid, index_label, index_to_use)

    except TeradataMlException:
        raise
    except Exception as err:
        raise TeradataMlException(Messages.get_message(MessageCodes.SETOP_FAILED, setop_type),
                                  MessageCodes.SETOP_FAILED) from err


@collect_queryband(queryband="tdIntersect")
def td_intersect(df_list, allow_duplicates=True):
    """
    DESCRIPTION:
        Function intersects a list of teradataml DataFrames or GeoDataFrames along the index axis and
        returns a DataFrame with rows common to all input DataFrames.
        Note:
             This function should be applied to data frames of the same type: either all teradataml DataFrames,
             or all GeoDataFrames.

    PARAMETERS:
        df_list:
            Required argument.
            Specifies the list of teradataml DataFrames or GeoDataFrames on which the intersection is to be performed.
            Types: list of teradataml DataFrames or GeoDataFrames
        
        allow_duplicates:
            Optional argument.
            Specifies if the result of intersection can have duplicate rows.
            Default value: True
            Types: bool

    RETURNS:
        teradataml DataFrame when intersect is performed on teradataml DataFrames.
        teradataml GeoDataFrame when operation is performed on teradataml GeoDataFrames.

    RAISES:
        TeradataMlException, TypeError

    EXAMPLES:
        >>> from teradataml import load_example_data
        >>> load_example_data("dataframe", "setop_test1")
        >>> load_example_data("dataframe", "setop_test2")
        >>> load_example_data("geodataframe", ["sample_shapes"])
        >>> from teradataml.dataframe.setop import td_intersect
        >>>
        >>> df1 = DataFrame('setop_test1')
        >>> df1
           masters   gpa     stats programming  admitted
        id                                              
        62      no  3.70  Advanced    Advanced         1
        53     yes  3.50  Beginner      Novice         1
        69      no  3.96  Advanced    Advanced         1
        61     yes  4.00  Advanced    Advanced         1
        58      no  3.13  Advanced    Advanced         1
        51     yes  3.76  Beginner    Beginner         0
        68      no  1.87  Advanced      Novice         1
        66      no  3.87    Novice    Beginner         1
        60      no  4.00  Advanced      Novice         1
        59      no  3.65    Novice      Novice         1
        >>> df2 = DataFrame('setop_test2')
        >>> df2
           masters   gpa     stats programming  admitted
        id                                              
        12      no  3.65    Novice      Novice         1
        15     yes  4.00  Advanced    Advanced         1
        14     yes  3.45  Advanced    Advanced         0
        20     yes  3.90  Advanced    Advanced         1
        18     yes  3.81  Advanced    Advanced         1
        17      no  3.83  Advanced    Advanced         1
        13      no  4.00  Advanced      Novice         1
        11      no  3.13  Advanced    Advanced         1
        60      no  4.00  Advanced      Novice         1
        19     yes  1.98  Advanced    Advanced         0
        >>> idf = td_intersect([df1, df2])
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        64     yes  3.81  Advanced    Advanced         1
        60      no  4.00  Advanced      Novice         1
        58      no  3.13  Advanced    Advanced         1
        68      no  1.87  Advanced      Novice         1
        66      no  3.87    Novice    Beginner         1
        60      no  4.00  Advanced      Novice         1
        62      no  3.70  Advanced    Advanced         1
        >>>
        >>> idf = td_intersect([df1, df2], allow_duplicates=False)
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        64     yes  3.81  Advanced    Advanced         1
        60      no  4.00  Advanced      Novice         1
        58      no  3.13  Advanced    Advanced         1
        68      no  1.87  Advanced      Novice         1
        66      no  3.87    Novice    Beginner         1
        62      no  3.70  Advanced    Advanced         1
        >>> # intersecting more than two DataFrames
        >>> df3 = df1[df1.gpa <= 3.5]
        >>> df3
           masters   gpa     stats programming  admitted
        id                                              
        58      no  3.13  Advanced    Advanced         1
        67     yes  3.46    Novice    Beginner         0
        54     yes  3.50  Beginner    Advanced         1
        68      no  1.87  Advanced      Novice         1
        53     yes  3.50  Beginner      Novice         1
        >>> idf = td_intersect([df1, df2, df3])
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        58      no  3.13  Advanced    Advanced         1
        68      no  1.87  Advanced      Novice         1

        # Perform intersection of two GeoDataFrames.
        >>> geo_dataframe = GeoDataFrame('sample_shapes')
        >>> geo_dataframe1 = geo_dataframe[geo_dataframe.skey == 1004].select(['skey','linestrings'])
        >>> geo_dataframe1

        skey            linestrings
        1004  LINESTRING (10 20 30,40 50 60,70 80 80)
        >>> geo_dataframe2 = geo_dataframe[geo_dataframe.skey < 1010].select(['skey','linestrings'])
        >>> geo_dataframe2

        skey                        linestrings
        1009            MULTILINESTRING ((10 20 30,40 50 60),(70 80 80,90 100 110))
        1005                                         LINESTRING (1 3 6,3 0 6,6 0 1)
        1004                                LINESTRING (10 20 30,40 50 60,70 80 80)
        1002                                               LINESTRING (1 3,3 0,0 1)
        1001                                           LINESTRING (1 1,2 2,3 3,4 4)
        1003                       LINESTRING (1.35 3.6456,3.6756 0.23,0.345 1.756)
        1007                            MULTILINESTRING ((1 1,1 3,6 3),(10 5,20 1))
        1006           LINESTRING (1.35 3.6456 4.5,3.6756 0.23 6.8,0.345 1.756 8.9)
        1008  MULTILINESTRING ((1 3,3 0,0 1),(1.35 3.6456,3.6756 0.23,0.345 1.756))
        >>> td_intersect([geo_dataframe1,geo_dataframe2])

        skey            linestrings
        1004  LINESTRING (10 20 30,40 50 60,70 80 80)
    """
    awu_matrix = []
    awu_matrix.append(["df_list", df_list, False, (list)])
    awu_matrix.append(["allow_duplicates", allow_duplicates, False, (bool)])
    setop_type = 'td_intersect'
    operation = 'intersect'

    # Validate Set operator arguments
    __validate_setop_args(df_list, awu_matrix, setop_type)

    return __process_setop_operation(df_list, allow_duplicates, setop_type, operation)


@collect_queryband(queryband="tdMinus")
def td_minus(df_list, allow_duplicates=True):
    """
    DESCRIPTION:
        This function returns the resulting rows that appear in first teradataml DataFrame or GeoDataFrame
        and not in other teradataml DataFrames or GeoDataFrames along the index axis.
        Note:
             This function should be applied to data frames of the same type: either all teradataml DataFrames,
             or all GeoDataFrames.

    PARAMETERS:
        df_list:
            Required argument.
            Specifies the list of teradataml DataFrames or GeoDataFrames on which the minus
            operation is to be performed.
            Types: list of teradataml DataFrames or GeoDataFrames
        
        allow_duplicates:
            Optional argument.
            Specifies if the result of minus operation can have duplicate rows.
            Default value: True
            Types: bool

    RETURNS:
        teradataml DataFrame when operation is performed on teradataml DataFrames.
        teradataml GeoDataFrame when operation is performed on teradataml GeoDataFrames.

    RAISES:
        TeradataMlException, TypeError

    EXAMPLES:
        >>> from teradataml import load_example_data
        >>> load_example_data("dataframe", "setop_test1")
        >>> load_example_data("dataframe", "setop_test2")
        >>> load_example_data("geodataframe", ["sample_shapes"])
        >>> from teradataml.dataframe.setop import td_minus
        >>>
        >>> df1 = DataFrame('setop_test1')
        >>> df1
           masters   gpa     stats programming  admitted
        id                                              
        62      no  3.70  Advanced    Advanced         1
        53     yes  3.50  Beginner      Novice         1
        69      no  3.96  Advanced    Advanced         1
        61     yes  4.00  Advanced    Advanced         1
        58      no  3.13  Advanced    Advanced         1
        51     yes  3.76  Beginner    Beginner         0
        68      no  1.87  Advanced      Novice         1
        66      no  3.87    Novice    Beginner         1
        60      no  4.00  Advanced      Novice         1
        59      no  3.65    Novice      Novice         1
        >>> df2 = DataFrame('setop_test2')
        >>> df2
           masters   gpa     stats programming  admitted
        id                                              
        12      no  3.65    Novice      Novice         1
        15     yes  4.00  Advanced    Advanced         1
        14     yes  3.45  Advanced    Advanced         0
        20     yes  3.90  Advanced    Advanced         1
        18     yes  3.81  Advanced    Advanced         1
        17      no  3.83  Advanced    Advanced         1
        13      no  4.00  Advanced      Novice         1
        11      no  3.13  Advanced    Advanced         1
        60      no  4.00  Advanced      Novice         1
        19     yes  1.98  Advanced    Advanced         0
        >>> idf = td_minus([df1[df1.id<55] , df2])
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        51     yes  3.76  Beginner    Beginner         0
        50     yes  3.95  Beginner    Beginner         0
        54     yes  3.50  Beginner    Advanced         1
        52      no  3.70    Novice    Beginner         1
        53     yes  3.50  Beginner      Novice         1
        53     yes  3.50  Beginner      Novice         1
        >>>
        >>> idf = td_minus([df1[df1.id<55] , df2], allow_duplicates=False)
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        54     yes  3.50  Beginner    Advanced         1
        51     yes  3.76  Beginner    Beginner         0
        53     yes  3.50  Beginner      Novice         1
        50     yes  3.95  Beginner    Beginner         0
        52      no  3.70    Novice    Beginner         1
        >>> # applying minus on more than two DataFrames
        >>> df3 = df1[df1.gpa <= 3.9]
        >>> idf = td_minus([df1, df2, df3])
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        61     yes  4.00  Advanced    Advanced         1
        50     yes  3.95  Beginner    Beginner         0
        69      no  3.96  Advanced    Advanced         1

        # td_minus on GeoDataFrame
        >>> geo_dataframe = GeoDataFrame('sample_shapes')
        >>> geo_dataframe1 = geo_dataframe[geo_dataframe.skey == 1004].select(['skey','linestrings'])
        >>> geo_dataframe1
        skey        linestrings
        1004  LINESTRING (10 20 30,40 50 60,70 80 80)

        >>> geo_dataframe2 = geo_dataframe[geo_dataframe.skey < 1010].select(['skey','linestrings'])
        >>> geo_dataframe2
        skey                                linestrings
        1009            MULTILINESTRING ((10 20 30,40 50 60),(70 80 80,90 100 110))
        1005                                         LINESTRING (1 3 6,3 0 6,6 0 1)
        1004                                LINESTRING (10 20 30,40 50 60,70 80 80)
        1002                                               LINESTRING (1 3,3 0,0 1)
        1001                                           LINESTRING (1 1,2 2,3 3,4 4)
        1003                       LINESTRING (1.35 3.6456,3.6756 0.23,0.345 1.756)
        1007                            MULTILINESTRING ((1 1,1 3,6 3),(10 5,20 1))
        1006           LINESTRING (1.35 3.6456 4.5,3.6756 0.23 6.8,0.345 1.756 8.9)
        1008  MULTILINESTRING ((1 3,3 0,0 1),(1.35 3.6456,3.6756 0.23,0.345 1.756))

        >>> td_minus([geo_dataframe2,geo_dataframe1])
                                                                    linestrings
        skey
        1005                                         LINESTRING (1 3 6,3 0 6,6 0 1)
        1009            MULTILINESTRING ((10 20 30,40 50 60),(70 80 80,90 100 110))
        1002                                               LINESTRING (1 3,3 0,0 1)
        1007                            MULTILINESTRING ((1 1,1 3,6 3),(10 5,20 1))
        1008  MULTILINESTRING ((1 3,3 0,0 1),(1.35 3.6456,3.6756 0.23,0.345 1.756))
        1006           LINESTRING (1.35 3.6456 4.5,3.6756 0.23 6.8,0.345 1.756 8.9)
        1003                       LINESTRING (1.35 3.6456,3.6756 0.23,0.345 1.756)
        1001                                           LINESTRING (1 1,2 2,3 3,4 4)
    """
    awu_matrix = []
    awu_matrix.append(["df_list", df_list, False, (list)])
    awu_matrix.append(["allow_duplicates", allow_duplicates, False, (bool)])
    setop_type = 'td_except' if (inspect.stack()[3][3] and inspect.stack()[3][3] == 'td_except') else 'td_minus'
    operation = 'minus'

    # Validate Set operator arguments
    __validate_setop_args(df_list, awu_matrix, setop_type)

    return __process_setop_operation(df_list, allow_duplicates, setop_type, operation)


@collect_queryband(queryband="tdExcept")
def td_except(df_list, allow_duplicates=True):
    """
    DESCRIPTION:
        This function returns the resulting rows that appear in first teradataml DataFrame or GeoDataFrame
        and not in other teradataml DataFrames or GeoDataFrames along the index axis.
        Note:
             This function should be applied to data frames of the same type: either all teradataml DataFrames,
             or all GeoDataFrames.

    PARAMETERS:
        df_list:
            Required argument.
            Specifies the list of teradataml DataFrames or GeoDataFrames on which the except
            operation is to be performed.
            Types: list of teradataml DataFrames or GeoDataFrames
        
        allow_duplicates:
            Optional argument.
            Specifies if the result of except operation can have duplicate rows.
            Default value: True
            Types: bool

    RETURNS:
        teradataml DataFrame when operation is performed on teradataml DataFrames.
        teradataml GeoDataFrame when operation is performed on teradataml GeoDataFrames.

    RAISES:
        TeradataMlException, TypeError

    EXAMPLES:
        >>> from teradataml import load_example_data
        >>> load_example_data("dataframe", "setop_test1")
        >>> load_example_data("dataframe", "setop_test2")
        >>> load_example_data("geodataframe", ["sample_shapes"])
        >>> from teradataml.dataframe.setop import td_except
        >>>
        >>> df1 = DataFrame('setop_test1')
        >>> df1
           masters   gpa     stats programming  admitted
        id                                              
        62      no  3.70  Advanced    Advanced         1
        53     yes  3.50  Beginner      Novice         1
        69      no  3.96  Advanced    Advanced         1
        61     yes  4.00  Advanced    Advanced         1
        58      no  3.13  Advanced    Advanced         1
        51     yes  3.76  Beginner    Beginner         0
        68      no  1.87  Advanced      Novice         1
        66      no  3.87    Novice    Beginner         1
        60      no  4.00  Advanced      Novice         1
        59      no  3.65    Novice      Novice         1
        >>> df2 = DataFrame('setop_test2')
        >>> df2
           masters   gpa     stats programming  admitted
        id                                              
        12      no  3.65    Novice      Novice         1
        15     yes  4.00  Advanced    Advanced         1
        14     yes  3.45  Advanced    Advanced         0
        20     yes  3.90  Advanced    Advanced         1
        18     yes  3.81  Advanced    Advanced         1
        17      no  3.83  Advanced    Advanced         1
        13      no  4.00  Advanced      Novice         1
        11      no  3.13  Advanced    Advanced         1
        60      no  4.00  Advanced      Novice         1
        19     yes  1.98  Advanced    Advanced         0
        >>> idf = td_except([df1[df1.id<55] , df2])
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        51     yes  3.76  Beginner    Beginner         0
        50     yes  3.95  Beginner    Beginner         0
        54     yes  3.50  Beginner    Advanced         1
        52      no  3.70    Novice    Beginner         1
        53     yes  3.50  Beginner      Novice         1
        53     yes  3.50  Beginner      Novice         1
        >>>
        >>> idf = td_except([df1[df1.id<55] , df2], allow_duplicates=False)
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        54     yes  3.50  Beginner    Advanced         1
        51     yes  3.76  Beginner    Beginner         0
        53     yes  3.50  Beginner      Novice         1
        50     yes  3.95  Beginner    Beginner         0
        52      no  3.70    Novice    Beginner         1
        >>> # applying except on more than two DataFrames
        >>> df3 = df1[df1.gpa <= 3.9]
        >>> idf = td_except([df1, df2, df3])
        >>> idf
           masters   gpa     stats programming  admitted
        id                                              
        61     yes  4.00  Advanced    Advanced         1
        50     yes  3.95  Beginner    Beginner         0
        69      no  3.96  Advanced    Advanced         1

        # td_except on GeoDataFrames
        >>> geo_dataframe = GeoDataFrame('sample_shapes')
        >>> geo_dataframe1 = geo_dataframe[geo_dataframe.skey == 1004].select(['skey','linestrings'])
        >>> geo_dataframe1
        skey        linestrings
        1004  LINESTRING (10 20 30,40 50 60,70 80 80)
        
        >>> geo_dataframe2 = geo_dataframe[geo_dataframe.skey < 1010].select(['skey','linestrings'])
        >>> geo_dataframe2
        skey                                linestrings
        1009            MULTILINESTRING ((10 20 30,40 50 60),(70 80 80,90 100 110))
        1005                                         LINESTRING (1 3 6,3 0 6,6 0 1)
        1004                                LINESTRING (10 20 30,40 50 60,70 80 80)
        1002                                               LINESTRING (1 3,3 0,0 1)
        1001                                           LINESTRING (1 1,2 2,3 3,4 4)
        1003                       LINESTRING (1.35 3.6456,3.6756 0.23,0.345 1.756)
        1007                            MULTILINESTRING ((1 1,1 3,6 3),(10 5,20 1))
        1006           LINESTRING (1.35 3.6456 4.5,3.6756 0.23 6.8,0.345 1.756 8.9)
        1008  MULTILINESTRING ((1 3,3 0,0 1),(1.35 3.6456,3.6756 0.23,0.345 1.756))

        >>> td_except([geo_dataframe2,geo_dataframe1])
        skey                    linestrings
        1008  MULTILINESTRING ((1 3,3 0,0 1),(1.35 3.6456,3.6756 0.23,0.345 1.756))
        1003                       LINESTRING (1.35 3.6456,3.6756 0.23,0.345 1.756)
        1005                                         LINESTRING (1 3 6,3 0 6,6 0 1)
        1006           LINESTRING (1.35 3.6456 4.5,3.6756 0.23 6.8,0.345 1.756 8.9)
        1009            MULTILINESTRING ((10 20 30,40 50 60),(70 80 80,90 100 110))
        1001                                           LINESTRING (1 1,2 2,3 3,4 4)
        1007                            MULTILINESTRING ((1 1,1 3,6 3),(10 5,20 1))
        1002                                               LINESTRING (1 3,3 0,0 1)
    """
    return td_minus(df_list, allow_duplicates)


def __process_setop_operation(df_list, allow_duplicates, setop_type, operation):
    """
    DESCRIPTION:
        Internal function to process set opertaion and return the result DataFrame/GeoDataFrame.

    PARAMETERS:
        df_list:
            Required argument.
            Specifies the list of teradataml DataFrames/GeoDataFrames on which the except
            operation is to be performed.
            Types: list of teradataml DataFrames

        allow_duplicates:
            Optional argument.
            Specifies if the result of except operation can have duplicate rows.
            Default value: True
            Types: bool

        setop_type:
            Required argument.
            Specifies set opertaion.
            Types: str

        operation:
            Required argument.
            Specifies set opertaion name.
            Types: str

    RETURNS:
        teradataml DataFrame/GeoDataFrame

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>> __process_setop_operation(df_list, allow_duplicates, setop_type, operation)

    """

    # Check if set operation can be lazy or not
    is_lazy = __check_setop_if_lazy(df_list)

    # Get the first DataFrame's metaexpr
    first_df_metaexpr = df_list[0]._metaexpr

    try:
        aed_utils = AedUtils()
        input_table_columns = []
        for i in range(len(df_list)):
            col_list = []
            for j in range(len(df_list[i].columns)):
                col_list.append(UtilFuncs._process_for_teradata_keyword(df_list[i].columns[j]))

            input_table_columns.append(','.join(col_list))

        nodeid = aed_utils._aed_setop([df._nodeid for df in df_list],
                                      '{}all'.format(operation) if allow_duplicates else '{}'.format(operation),
                                       input_table_columns)

        # Set the index_label to columns in first df's index_label if it is not None,
        # else set it to None i.e. no index_label.
        index_label = []
        index_to_use = None
        index_to_use = df_list[0]._index_label if df_list[0]._index_label is not None else None

        if index_to_use is not None:
            index_label = index_to_use

        class_name = df_list[0].__class__.__name__
        return __process_operation(first_df_metaexpr, is_lazy, setop_type, nodeid, index_label, index_to_use, class_name)

    except TeradataMlException:
        raise
    except Exception as err:
        raise TeradataMlException(Messages.get_message(MessageCodes.SETOP_FAILED, setop_type),
                                  MessageCodes.SETOP_FAILED) from err
