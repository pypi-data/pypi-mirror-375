# ##################################################################
#
# Copyright 2021 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# Secondary Owner:
#
# This file implements teradataml GeoDataFrameColumn.
# teradataml GeoDataFrameColumn allows user to access individual columns
# of a teradataml GeoDataFrame and run operations on the same.
#
# ##################################################################
from sqlalchemy import text
from teradataml.common.bulk_exposed_utils import _validate_unimplemented_function
from teradataml.common.constants import GeospatialConstants
from teradataml.dataframe.sql import _SQLColumnExpression
from teradataml.dataframe.sql_function_parameters import \
    GEOSPATIAL_METHOD_PARAMETERS
from teradataml.dataframe.sql_interfaces import ColumnExpression
from teradataml.dataframe.vantage_function_types import \
                GEOSPATIAL_SQL_FUNCTION_OUTPUT_TYPE_MAPPER as gsp_func_out_map
from teradataml.geospatial.geometry_types import GeometryType
from teradataml.utils.validators import _Validators
from teradatasqlalchemy import (GEOMETRY, MBR, MBB, BLOB, CLOB)
from teradataml.telemetry_utils.queryband import collect_queryband

# Geospatial Function name mappers
geo_func_as_property = \
    GeospatialConstants.PROPERTY_TO_NO_ARG_SQL_FUNCTION_NAME.value
geo_func_as_method_no_args = \
    GeospatialConstants.METHOD_TO_NO_ARG_SQL_FUNCTION_NAME.value
geo_func_as_method_with_args = \
    GeospatialConstants.METHOD_TO_ARG_ACCEPTING_SQL_FUNCTION_NAME.value

class GeoDataFrameColumn(_SQLColumnExpression):

    def __init__(self, expression):
        """
        Initialize the GeoDataFrameColumn.

        PARAMETERS:
            expression : Required Argument.
                         A sqlalchemy.ClauseElement instance.
        """
        super(GeoDataFrameColumn, self).__init__(expression=expression)
        self.expression = expression

    def __getattr__(self, item):
        """
        Returns an attribute of the GeoDataFrame.

        PARAMETERS:
            item:
                Required Argument.
                Specifies the name of the attribute.
                Types: str

        RETURNS:
            Return the value of the named attribute of object (if found).

        EXAMPLES:
            gdf = GeoDataFrame('table')

            # You can access property of the GeoDataFrameColumn
            gdf.x

        RAISES:
            None.
        """
        # Some bool values that will be used again and again.
        as_method_no_arg = item in geo_func_as_method_no_args
        as_property = item in geo_func_as_property
        as_method_with_arg = item in geo_func_as_method_with_args

        # Validate if the function is Geospatial and is being executed on
        # the column of correct type.
        if as_property or as_method_no_arg or as_method_with_arg:
            # If a geospatial function, must be executed on the columns
            # of type ST_Geometry, MBR and MBB only.
            # Validate the same.
            if not isinstance(self.type, (GEOMETRY, MBR, MBB)):
                if (isinstance(self.type, BLOB) and item == "wkb_geom_to_sql"):
                    pass
                elif (isinstance(self.type, CLOB) and item == "wkt_geom_to_sql"):
                    pass
                else:
                    fmt_ = "Unsupported operation '{}' on column '{}' of type '{}'"
                    err_ = fmt_.format(item, self.name, str(self.type))
                    raise RuntimeError(err_)

        ### *******************************************
        # If "item" is present in any of the following 'GeospatialConstants'
        #   1. GeospatialConstants.PROPERTY_TO_NO_ARG_SQL_FUNCTION_NAME
        #   2. GeospatialConstants.METHOD_TO_ARG_ACCEPTING_SQL_FUNCTION_NAME
        #   3. GeospatialConstants.METHOD_TO_NO_ARG_SQL_FUNCTION_NAME
        # that means, it's a function that operates on Geometry Data.
        #
        # Look for such function names.
        if as_method_no_arg:
            # Geospatial functions which are exposed as method of teradataml
            # GeoDataFrameColumn but does not accept any arguments as input.
            return lambda *args, **kwargs: \
                self.__process_geospatial_method_with_no_args(func_name=item)

        # Check if Geospatial function is to be executed as property or not.
        exec_as_property = as_property and not as_method_with_arg
        if exec_as_property:
            # Geospatial functions which are exposed as property of teradataml
            # GeoDataFrameColumn.
            return self.__process_geospatial_function_property(func_name=item)

        # Rest of the functions.
        if as_method_with_arg:
            return lambda *args, **kwargs: \
                    self.__process_func_with_args(item, *args, **kwargs)

    @collect_queryband(arg_name="func_name", prefix="GDFC")
    def __process_geospatial_function_property(self, func_name):
        """
        DESCRIPTION:
            Internal function process the Geospatial function as property.
            Property means, the functions are exposed as Property of
            GeoDataFrame and GeoDataFrameColumn.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the function.
                Types: str

        RETURNS:
            ColumnExpression a.k.a GeoDataFrameColumn

        RAISES:
            None.

        EXAMPLES:
            self.__process_geospatial_function_property(func_name=item)
        """
        # Geospatial functions which are exposed as property of teradataml
        # GeoDataFrameColumn.
        function_name = geo_func_as_property[func_name](self.type)
        ufunction_name = function_name.upper()
        if ufunction_name not in ("ST_X", "ST_Y", "ST_Z", "ST_SRID"):
            out_type_ = gsp_func_out_map.get(ufunction_name, None)
        else:
            out_type_ = gsp_func_out_map[ufunction_name](None)
        return self._generate_vantage_function_call(
            func_name=function_name, col_name=self.name, property=True,
            type_=out_type_)

    @collect_queryband(arg_name="func_name", prefix="GDFC")
    def __process_geospatial_method_with_no_args(self, func_name):
        """
        DESCRIPTION:
            Internal function process the Geospatial functions which
            do not accept any argument and are exposed as method of
            GeoDataFrame and GeoDataFrameColumn.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the function.
                Types: str

        RETURNS:
            ColumnExpression a.k.a GeoDataFrameColumn

        RAISES:
            None.

        EXAMPLES:
            self.__process_geospatial_method_with_no_args(func_name=item)
        """
        # Geospatial functions which are exposed as method of teradataml
        # GeoDataFrameColumn but does not accept any arguments as input.
        function_name = geo_func_as_method_no_args[func_name](None)
        out_type_ = gsp_func_out_map.get(function_name.upper(), None)
        return self._generate_vantage_function_call(
            func_name=function_name, col_name=self.name, return_func=False,
            type_=out_type_)

    @collect_queryband(arg_name="func_name", prefix="GDFC")
    def __process_func_with_args(self, func_name, *c, **kwargs):
        """
        DESCRIPTION:
            Internal function process the Geospatial functions which
            accepts argument and are exposed as method of GeoDataFrame
            and GeoDataFrameColumn.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the function.
                Types: str

            c:
                Specifies the positional arguments of the function.

            kwargs:
                Specifies the keyword arguments of the function.

        RETURNS:
            ColumnExpression a.k.a GeoDataFrameColumn

        RAISES:
            None.

        EXAMPLES:
            self.__process_func_with_args(item, *args, **kwargs)
        """
        # Check if 'func_name' is a Geospatial function or not.
        as_method_with_arg = func_name in geo_func_as_method_with_args
        as_property = func_name in geo_func_as_property

        # Check if Geospatial function is to be executed as property or not.
        exec_as_property = (as_property and (as_method_with_arg and
                                             not c and not kwargs))
        if exec_as_property:
            # Geospatial functions which are exposed as property of teradataml
            # GeoDataFrameColumn.
            return self.__process_geospatial_function_property(func_name=func_name)

        # We are here that means, function being executed is either a
        # regular function or Geospatial function that accepts arguments.
        # Let's now proceed to process all such functions.

        # Validate the function signature first.
        if func_name.upper() in GEOSPATIAL_METHOD_PARAMETERS:
            func_params = GEOSPATIAL_METHOD_PARAMETERS[func_name.upper()]
            param_values = _validate_unimplemented_function(func_name,
                                                            func_params,
                                                            *c,
                                                            **kwargs)

            new_c = []
            awu_matrix = []
            for param in func_params:
                value = param_values[param["arg_name"]]
                # If default_value available, then parameter is Optional. For Optional
                # parameter, 3rd argument in "awu_matrix" should be True.
                is_optional = "default_value" in param
                awu_matrix.append([param["arg_name"],
                                   value,
                                   is_optional,
                                   param["exp_types"]]
                                  )

                dvalue = param.get("default_value", None)
                if isinstance(value, _SQLColumnExpression):
                    new_c.append(value.expression)
                elif isinstance(value, GeometryType):
                    new_c.append(text(value._vantage_str_()))
                elif isinstance(value, str):
                    if isinstance(param["exp_types"], type):
                        supp_types = [param["exp_types"]]
                    else:
                        supp_types = param["exp_types"]
                    #if GeometryType in supp_types or ColumnExpression in supp_types:
                    new_c.append(text(value))
                    #elif dvalue is None or dvalue != value:
                    #    new_c.append(value)
                else:
                    # Change done to support speed function.
                    if dvalue != value:
                        new_c.append(value)
                    # Old code before adding support for "speed" function.
                    #if dvalue is None or dvalue != value:
                    #    new_c.append(value)

            # Validate argument types
            _Validators._validate_function_arguments(awu_matrix)

        else:
            # Process the positional arguments passed in *c.
            # Get the actual expression.
            new_c = [item.expression if isinstance(item, _SQLColumnExpression)
                     else item for item in c]

        if as_method_with_arg:
            # A list of Geospatial Functions (Vantage SQL names), those are
            # either invoked using a column (column of type ST_Geometry, MBR,
            # MBB) or accept the first argument as column of Geometry type.
            # At least 44 functions are covered in this.
            #
            # Geospatial functions which are exposed as method of teradataml
            # GeoDataFrameColumn and accepts arguments as input.
            #
            # If function is part of the mapper(dictionary)
            # 'func_as_method_with_args', function must be executed as column
            # function and also process the arguments for such functions.
            #
            # Function with following syntax will be processed here:
            #   column.func_name(...)

            fname = geo_func_as_method_with_args[func_name](self.type)
            #cname = self.name
            cname = self.compile()
            cfunction = True
        else:
            # Function must be executed as regular SQL function call,
            # that accepts the column as argument.
            # Function with following syntax will be processed here:
            #   func_name(column, ...)
            fname = func_name
            cname = None
            cfunction = False
            new_c = (self.expression,) + tuple(new_c)
        # Extract the "type_" argument, if it is given, else set it to None.
        t_ = kwargs.get("type_", self._get_function_output_type(fname, *new_c))

        # Generate the SQL function call.
        return self._generate_vantage_function_call(fname, cname, t_, cfunction,
                                                    False, False, *new_c)

    def _get_function_output_type(self, func_name, *new_c):
        """
        Internal function that returns the data type of the output column
        of the function.

        PARAMETERS:
            func_name:
                Required Argument.
                Specifies the name of the function.
                Types: str

            *new_c:
                Optional positional arguments.
                Specifies the arguments passed to the function.

        RETURNS:
            teradatasqlalchemy type - Result column Data type for a function.

        RAISES:
            None

        EXAMPLES:
            type_o = self._get_function_output_type("ST_CONTAINS")
            type_o = self._get_function_output_type("ST_X", 1002)
        """
        # Convert the fname to upper case as mappers has key's with
        # uppercase.
        func_name = func_name.upper()
        if func_name in ("LINKID", "ST_X", "ST_Y", "ST_Z", "ST_SRID"):
            out_type_ = gsp_func_out_map[func_name](*new_c)
        else:
            out_type_ = gsp_func_out_map.get(func_name, None)

        return out_type_

    def _wrap_as_column_expression(self, new_expression):
        """
        Internal function that wraps the provided expression as
        GeoDataFrameColumn.

        PARAMETERS:
            new_expression:
                 Required Argument.
                 Specifies the expression to be returned.
                 Types: Any expression.

        RETURNS:
            GeoDataFrameColumn.

        RAISES:
            None.

        EXAMPLES:
            self._wrap_as_column_expression(getattr(func.vantage,
                                                    func_name)(*args))
        """
        return GeoDataFrameColumn(new_expression)

    @collect_queryband(queryband="GDFC_relates")
    def relates(self, geom_column, amatrix):
        """
        Please refer to Function Reference Guide for Teradata Package for Python
        on docs.teradata.com
        """
        arg_info_matrix = []
        geom_column_types = (str, ColumnExpression, GeometryType)
        arg_info_matrix.append(["geom_column", geom_column, False, geom_column_types])
        arg_info_matrix.append(["amatrix", amatrix,  False, str])
        _Validators._validate_function_arguments(arg_info_matrix)

        # Add single quote around the amatrix values as SQL accepts the argument
        # with single quote.
        amatrix = "'{}'".format(amatrix)
        return self.__process_func_with_args(
            func_name="relates", geom_column=geom_column, amatrix=amatrix)

