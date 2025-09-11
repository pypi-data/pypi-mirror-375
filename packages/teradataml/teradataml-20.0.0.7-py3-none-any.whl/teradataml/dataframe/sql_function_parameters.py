#!/usr/bin/python
# ##################################################################
#
# Copyright 2021 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
#
# Version: 1.0
# Function Version: 1.0
#
# ##################################################################

from teradataml.dataframe.sql_interfaces import ColumnExpression
from collections import OrderedDict
from teradataml.geospatial.geometry_types import GeometryType
import datetime as dt


# Function to generate Individual parameter structure.
def _generate_param_structure(param_name, param_type, **kwargs):
    """
    DESCRIPTION:
        Generates the structure for a parameter.

    PARAMETERS:
        param_name:
            Required Argument.
            Specifies the name of the Parameter.
            Types: str

        param_type:
            Required Argument.
            Specifies the type of Parameter.
            Types: Any Type or Tuple of Types.

        kwargs:
            Optional Argument.
            Specifies optional keyword arguments.
            Types: dict

    RAISES:
        None

    RETURNS:
        dict.

    EXAMPLES:
        generate_param_structure("column", _SQLColumnExpression)
        generate_param_structure("width", 5)
    """
    param_struct = {"arg_name": param_name,
                    "exp_types": param_type}

    if "default_value" in kwargs:
        default_value = kwargs["default_value"]
        # If default value is a string, this should be guarded with single
        # quotes as strings should be guarded with single quotes in function
        # signature.
        param_struct["default_value"] = "'{}'".format(default_value) if isinstance(default_value, str) \
                                        else default_value

    return param_struct


# Different type of Aggregate functions accepts different types of parameters,
# However, specific category functions accepts similar parameters, i.e., csum
# and msum, both accepts first parameter as width and second parameter as
# expression. So, constructing the parameter structures and using the structure
# for aggregate functions.
#
# expected_types: Value of the 'expected_types' key represents the expected type
#                 of the parameter.
# param_name: Value of the 'param_name' key represents the expected name
#             of the parameter.
# default_value: Value of the 'default_value' key represents the default value
#                of the parameter.
#                Note: "default_value" should be always a keyword argument.

opt_int_param = lambda arg_name, def_val: _generate_param_structure(arg_name, int, default_value=def_val)
opt_str_param = lambda arg_name, def_val: _generate_param_structure(arg_name, str, default_value=def_val)
req_str_expr_param = lambda arg_name: _generate_param_structure(arg_name, (ColumnExpression, str))
opt_int_expr_param = lambda arg_name, def_val: _generate_param_structure(arg_name, (ColumnExpression, int), default_value=def_val)
opt_str_expr_param = lambda arg_name, def_val: _generate_param_structure(arg_name, (ColumnExpression, str), default_value=def_val)
req_int_expr_param = lambda arg_name: _generate_param_structure(arg_name, (ColumnExpression, int))

_params_column_structure = [_generate_param_structure("expression", (ColumnExpression, int, float, str))]
_params_width_sort_columns_structure = [_generate_param_structure("width", int),
                                        _generate_param_structure("sort_columns",
                                                                 (ColumnExpression, list, str))
                                       ]
quantile_parameter_structure = [_generate_param_structure("quantile_literal", int),
                                _generate_param_structure("sort_columns",
                                                         (ColumnExpression, list, str))
                               ]
_params_width_sort_column_structure = [_generate_param_structure("width", int),
                                       _generate_param_structure("sort_column",
                                                                 (ColumnExpression, str))
                                      ]
_params_columns_structure = [_generate_param_structure("sort_columns",
                                                    (ColumnExpression, list, str))]

_lead_lag_params_structure = [opt_int_param("offset_value", 1),
                              _generate_param_structure(
                                  "default_expression", (ColumnExpression, int, float, str), default_value=None)]
_percentile_param_structure = [_generate_param_structure("percentile", (int, float)),
                               _generate_param_structure("interpolation", (type(None), str), default_value="LINEAR"),
                               _generate_param_structure("describe_op", (bool), default_value=False)
                               ]

_expr_param_structure = [_generate_param_structure("expression", (ColumnExpression, int, float))]

_widthbucket_param_structure = [_generate_param_structure("min", (float, int)),
                                _generate_param_structure("max", (float, int)),
                                _generate_param_structure("numBucket", (float, int))]

_edit_distance_param_structure = [req_str_expr_param("expression"), opt_int_param("ci", 1),
                                  opt_int_param("cd", 1), opt_int_param("cs", 1),
                                  opt_int_param("ct", 1)]

_ltrim_rtrim_param_structure = [opt_str_expr_param("expression", ' ')]

_index_param_structure = [req_str_expr_param("expression")]

_instr_param_structure = [req_str_expr_param("expression"),
                          opt_int_param("position", 1),
                          opt_int_param("occurence", 1)]

_left_right_param_structure = [req_int_expr_param("length")]

_locate_param_structure = [req_str_expr_param("expression"), opt_int_param("n1", 1)]

_lpad_rpad_param_structure = [req_int_expr_param("length"),
                              opt_str_expr_param("fill_string", ' ')]

_ngram_param_structure = [req_str_expr_param("expression"),
                          _generate_param_structure("length", (int)),
                          _generate_param_structure("position", (int), default_value=1)]

_nvp_param_structure = [req_str_expr_param("name_to_search"), opt_str_param("name_delimiters", "&"),
                        opt_str_param("value_delimiters", "="), opt_int_param("occurrence", 1)]

_oreplace_otranslate_param_structure = [req_str_expr_param("expression"),
                                        opt_str_expr_param("replace_string", " ")]


_byte_param_structure = [req_int_expr_param("bit_mask")]
_setbit_param_structure = [req_int_expr_param("target_bit"), opt_int_expr_param("target_value", 1)]
_subbistr_param_structure = [req_int_expr_param("position"), req_int_expr_param("num_bits")]
_countset_param_structure = [opt_int_expr_param("target_value", 1)]

__regexp_string = req_str_expr_param("regexp_string")
__position = opt_int_expr_param("position", 1)
__occurrence = lambda def_val: opt_int_expr_param("occurence", def_val)
__match = opt_str_expr_param("match", None)

_regexp_instr_param_structure = [__regexp_string, __position, __occurrence(1), opt_int_expr_param("return_opt", 0), __match]
_regexp_replace_param_structure = [__regexp_string, req_str_expr_param("replace_string"), __position, __occurrence(0), __match]
_regexp_similar_param_structure = [__regexp_string, __match]
_regexp_substr_param_structure = [__regexp_string, __position, __occurrence(1), __match]

_expression_calendar_param_structure = [_generate_param_structure("calendar_name", str, default_value="Teradata"),
                                        _generate_param_structure("expression2", (ColumnExpression), default_value=None)]

_calendar_name_param_structure = [_generate_param_structure("calendar_name", str, default_value="Teradata")]

_day_value_param_structure = [_generate_param_structure("day_value", str)]

_expression_param_structure = [_generate_param_structure("expression", (ColumnExpression))]

_expression_int_param_structure = [_generate_param_structure("expression", (ColumnExpression,int))]
# Most of the Aggregate functions take first parameter as the column on which the
# Aggregate function is being applied. However, few functions do not accept
# first parameter as the corresponding column. All such functions should be
# kept in NO_DEFAULT_PARAM_FUNCTIONS.
# e.g: SQL Function expression for Correlation is CORR(expression1, expression2)
#      and the corresponding teradataml notation is df.col1.corr(col2). Here,
#      expression1 represents col1 & expression2 represents col2. So, col1 is the
#      default first parameter. However, for QUANTILE, it's SQL function
#      expression is QUANTILE(integer, expression) and corresponding teradataml
#      notation is df.col.quantile(x, col2). Notice that, first parameter for
#      quantile function is not the column on which the function is being applied
#      and thus, quantile should be kept in NO_DEFAULT_PARAM_FUNCTIONS.
# Notes:
#     1. The function names specified here are SQL function names, not
#        Python function names.
#     2. SQL Function must be in UPPERCASE.
NO_DEFAULT_PARAM_FUNCTIONS = ["QUANTILE", "RANK", "CUME_DIST", "DENSE_RANK",
                              "PERCENT_RANK", "ROW_NUMBER", "PERCENTILE_CONT",
                              "PERCENTILE_DISC"]

# Stores the additional parameters of the aggregate sql function. By default,
# most aggregate functions take first argument as column on which aggregate
# function is being applied. So, param structure do not store that column.
# Param structure stores only additional parameters.
# e.g: SQL aggregate function corr takes two columns as input. Since, first
#      column is a default parameter, param structure stores only the details
#      about second parameter and thus corr is mapped to _params_column_structure,
#      which stores only one parameter structure.
# Notes:
#     1. If function takes no additional parameters, then do not make entry for
#        the corresponding aggregate function or keep an empty list as structure.
#     2. Key in the below dictionary represents the name of the SQL function,
#        not the name of python function.
#     3. SQL Function must be in UPPERCASE.
SQL_AGGREGATE_FUNCTION_ADDITIONAL_PARAMETERS = {
    "CORR": _params_column_structure,
    "COVAR_POP": _params_column_structure,
    "COVAR_SAMP": _params_column_structure,
    "REGR_AVGX": _params_column_structure,
    "REGR_AVGY": _params_column_structure,
    "REGR_COUNT": _params_column_structure,
    "REGR_INTERCEPT": _params_column_structure,
    "REGR_R2": _params_column_structure,
    "REGR_SLOPE": _params_column_structure,
    "REGR_SXX": _params_column_structure,
    "REGR_SXY": _params_column_structure,
    "REGR_SYY": _params_column_structure,
    "CUME_DIST": [],
    "DENSE_RANK": [],
    "LAG": _lead_lag_params_structure,
    "LEAD": _lead_lag_params_structure,
    "PERCENT_RANK": [],
    "PERCENTILE": _percentile_param_structure,
    "RANK": [],
    "ROW_NUMBER": [],
    "FIRST_VALUE": [],
    "LAST_VALUE": [],
    "CSUM": _params_columns_structure,
    "QUANTILE": quantile_parameter_structure,
    "MSUM": _params_width_sort_columns_structure,
    "MAVG": _params_width_sort_columns_structure,
    "MDIFF": _params_width_sort_columns_structure,
    "MLINREG": _params_width_sort_column_structure
}

SQL_FUNCTION_ADDITIONAL_PARAMETERS = {
    # Maths function
    "MOD": _expr_param_structure,
    "POWER": _expr_param_structure,
    "ROUND": _expr_param_structure,
    "WIDTH_BUCKET": _widthbucket_param_structure,

    # Trigonometric function
    "ATAN2": _expr_param_structure,

    # String Functions
    "EDITDISTANCE": _edit_distance_param_structure,
    "INDEX": _index_param_structure,
    "INSTR": _instr_param_structure,
    "LEFT": _left_right_param_structure,
    "LOCATE": _locate_param_structure,
    "LPAD": _lpad_rpad_param_structure,
    "LTRIM": _ltrim_rtrim_param_structure,
    "NGRAM": _ngram_param_structure,
    "NVP": _nvp_param_structure,
    "OREPLACE": _oreplace_otranslate_param_structure,
    "OTRANSLATE": _oreplace_otranslate_param_structure,
    "RTRIM": _ltrim_rtrim_param_structure,
    "RIGHT": _left_right_param_structure,
    "RPAD": _lpad_rpad_param_structure,

    # Byte Functions
    "BITAND": _byte_param_structure,
    "BITOR": _byte_param_structure,
    "BITXOR": _byte_param_structure,
    "COUNTSET": _countset_param_structure,
    "GETBIT": _byte_param_structure,
    "ROTATELEFT": _byte_param_structure,
    "ROTATERIGHT": _byte_param_structure,
    "SHIFTLEFT": _byte_param_structure,
    "SHIFTRIGHT": _byte_param_structure,
    "SETBIT": _setbit_param_structure,
    "SUBBITSTR": _subbistr_param_structure,

    # Regular Expression Functions
    "REGEXP_INSTR": _regexp_instr_param_structure,
    "REGEXP_REPLACE": _regexp_replace_param_structure,
    "REGEXP_SIMILAR": _regexp_similar_param_structure,
    "REGEXP_SUBSTR": _regexp_substr_param_structure,

    # Date Time Functions
    "td_week_begin": _expression_calendar_param_structure,
    "td_week_end": _expression_calendar_param_structure,
    "td_sunday": _expression_calendar_param_structure,
    "td_monday": _expression_calendar_param_structure,
    "td_tuesday": _expression_calendar_param_structure,
    "td_wednesday": _expression_calendar_param_structure,
    "td_thursday": _expression_calendar_param_structure,
    "td_friday": _expression_calendar_param_structure,
    "td_saturday": _expression_calendar_param_structure,
    "DayNumber_Of_Week": _calendar_name_param_structure,
    "td_month_begin": _expression_calendar_param_structure,
    "td_month_end": _expression_calendar_param_structure,
    "DayNumber_Of_Month": _calendar_name_param_structure,
    "DayOccurrence_Of_Month": _calendar_name_param_structure,
    "WeekNumber_Of_Month": _calendar_name_param_structure,
    "td_year_begin": _expression_calendar_param_structure,
    "td_year_end": _expression_calendar_param_structure,
    "DayNumber_Of_Year": _calendar_name_param_structure,
    "WeekNumber_Of_Year": _calendar_name_param_structure,
    "MonthNumber_Of_Year": _calendar_name_param_structure,
    "td_quarter_begin": _expression_calendar_param_structure,
    "td_quarter_end": _expression_calendar_param_structure,
    "WeekNumber_Of_Quarter": _calendar_name_param_structure,
    "MonthNumber_Of_Quarter": _calendar_name_param_structure,
    "QuarterNumber_Of_Year": _calendar_name_param_structure,
    "DayNumber_Of_Calendar": _calendar_name_param_structure,
    "WeekNumber_Of_Calendar": _calendar_name_param_structure,
    "MonthNumber_Of_Calendar": _calendar_name_param_structure,
    "QuarterNumber_Of_Calendar": _calendar_name_param_structure,
    "YearNumber_Of_Calendar": _calendar_name_param_structure,
    "next_day": _day_value_param_structure,
    "months_between": _expression_param_structure,
    "add_months": _expression_int_param_structure,
    "oadd_months": _expression_int_param_structure
}

# When the argument for the following function is specified as str,
# in that case it should be quoted using single quotes so that it is
# treated as a string.
SINGLE_QUOTE_FUNCTIONS = {
    "EDITDISTANCE", "LTRIM", "LOCATE", "RTRIM", "INDEX", "INSTR", "LEFT", "RIGHT",
    "LOCATE", "LPAD", "RPAD", "NGRAM", "NVP", "OREPLACE", "OTRANSLATE",
    "REGEXP_INSTR", "REGEXP_REPLACE", "REGEXP_SIMILAR", "REGEXP_SUBSTR", "td_week_begin",
    "td_week_end", "td_sunday", "td_monday", "td_tuesday", "td_wednesday", "td_thursday",
    "td_friday", "td_saturday", "DayNumber_Of_Week", "td_month_begin", "td_month_end", "DayNumber_Of_Month",
    "DayOccurrence_Of_Month", "WeekNumber_Of_Month", "td_year_begin", "td_year_end",
    "DayNumber_Of_Year", "WeekNumber_Of_Year", "MonthNumber_Of_Year", "td_quarter_begin",
    "td_quarter_end", "WeekNumber_Of_Quarter", "MonthNumber_Of_Quarter", "QuarterNumber_Of_Year",
    "DayNumber_Of_Calendar", "WeekNumber_Of_Calendar", "MonthNumber_Of_Calendar", "QuarterNumber_Of_Calendar",
    "YearNumber_Of_Calendar", "next_day"
}

_get_param_struct = lambda x: \
    [_generate_param_structure(e, x.get(e, None)[0],
                               default_value=x.get(e, None)[1])
     if isinstance(x.get(e, None), list)
     else _generate_param_structure(e, x.get(e, None))
     for e in x]

# Variables for supported types tuples.
_bool_column_types = (bool, str, ColumnExpression)
_float_column_types = (float, str, ColumnExpression)
_float_int_column_types = (float, int, str, ColumnExpression)
_geometry_column_types = (str, ColumnExpression, GeometryType)
_int_column_types = (int, str, ColumnExpression)
_str_column_types = (str, ColumnExpression)

# Call parameter constructor for function accepting only "geom_column" argument.
_geom_column_only = _get_param_struct({"geom_column": _geometry_column_types})

# This dictionary maps teradataml name of the Geospatial function to
# the list containing exposed argument names and their parameter
# structure.
#
# The value of this mapper, which is list a list of dictionary containing
# argument names and their parameter structure. Argument names are
# "Pythonic argument names". This helps us in identifying and supporting the
# functions to accept both positional as well as keyword arguments,
# for our "Bulk Exposure Approach" of Geospatial functions.
#
# Note:
#   Entries in this dictionary should be made for each entry in
#   'METHOD_TO_ARG_ACCEPTING_SQL_FUNCTION_NAME'.
GEOSPATIAL_METHOD_PARAMETERS = {
    ## *** Minimum Bounding Type Methods *** ##
    "INTERSECTS": _geom_column_only,

    ## *** ST_Geometry Methods *** ##
    "BUFFER": _get_param_struct({"distance": _float_column_types}),
    "CONTAINS": _geom_column_only,
    "CROSSES": _geom_column_only,
    "DIFFERENCE": _geom_column_only,  # M
    "DISJOINT": _geom_column_only,
    "DISTANCE": _geom_column_only,  # M
    "DISTANCE_3D": _geom_column_only,  # M
    "GEOM_EQUALS": _geom_column_only,
    "INTERSECTION": _geom_column_only,
    "INTERSECT":  _geom_column_only,
    "MAKE_2D": _get_param_struct({"validate": [_bool_column_types, False]}),
    "OVERLAPS": _geom_column_only,
    "RELATES": _get_param_struct({"geom_column": _geometry_column_types,
                                  "amatrix": (str)}),
    "SIMPLIFY": _get_param_struct({"tolerance": _float_column_types}),
    "SYM_DIFFERENCE": _geom_column_only,  # M
    "TOUCHES": _geom_column_only,
    "TRANSFORM": _get_param_struct(OrderedDict([('to_wkt_srs', _str_column_types),
                                                ('from_wkt_srs', _str_column_types),
                                                ('to_srsid', [_int_column_types, -12345])
                                                ])),
    "UNION": _geom_column_only,
    "WITHIN": _geom_column_only,
    "WKB_GEOM_TO_SQL": _get_param_struct({"column": _str_column_types}),  # M
    "WKT_GEOM_TO_SQL": _get_param_struct({"column": _str_column_types}),  # M
    "SET_SRID": _get_param_struct({"srid": _int_column_types}),

    ## *** Geometry Type ST_Point Methods *** ##
    "SET_X": _get_param_struct({"xcoord": _float_int_column_types}),
    "SET_Y": _get_param_struct({"ycoord": _float_int_column_types}),
    "SET_Z": _get_param_struct({"zcoord": _float_int_column_types}),
    "SPHERICAL_BUFFER": _get_param_struct({"distance": _float_int_column_types,
                                           "radius": [_float_int_column_types, 6371000.0]}),  # M
    "SPHERICAL_DISTANCE": _get_param_struct({"geom_column": _geometry_column_types}),  # M
    "SPHEROIDAL_BUFFER": _get_param_struct({"distance": _float_int_column_types,
                                            "semimajor": [(float, int), 6378137.0],
                                            "invflattening": [(float, int), 298.257223563]}),  # M
    "SPHEROIDAL_DISTANCE": _get_param_struct({"geom_column": _geometry_column_types,
                                              "semimajor": [(float, int), 6378137.0],
                                              "invflattening": [(float, int), 298.257223563]}),  # M

    ## *** Geometry Type ST_LineString Methods *** ##
    "LINE_INTERPOLATE_POINT": _get_param_struct({"proportion": _float_column_types}),
    "POINT": _get_param_struct({"position": _int_column_types}),

    ## *** Geometry Type ST_Polygon Methods *** ##
    "EXTERIOR": _get_param_struct({"curve": _geometry_column_types}),
    "INTERIORS": _get_param_struct({"position": _int_column_types}),

    ## *** Geometry Type ST_GeomCollection Methods *** ##
    "GEOM_COMPONENT": _get_param_struct({"position": _int_column_types}),

    ## *** Geometry Type ST_Geomsequence Methods *** ##
    "CLIP": _get_param_struct({"start_timestamp": (str),
                               "end_timestamp": (str)}),
    "GET_USER_FIELD": _get_param_struct({"field_index": _int_column_types,
                                         "index": _int_column_types}),
    "POINT_HEADING": _get_param_struct({"index": _int_column_types}),
    "GET_LINK": _get_param_struct({"index": _int_column_types}),
    "SET_LINK": _get_param_struct({"index": _int_column_types, "link_id": (float)}),
    "SPEED": _get_param_struct({"index": [_int_column_types, None], "begin_index": [_int_column_types, None],
                                "end_index": [_int_column_types, None]}),

    ## *** Filtering Functions and Methods *** ##
    "INTERSECTS_MBB": _geom_column_only,
    "MBB_FILTER": _geom_column_only,
    "MBR_FILTER": _geom_column_only,
    "WITHIN_MBB": _geom_column_only
}