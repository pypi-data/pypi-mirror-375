#!/usr/bin/python
# ##################################################################
#
# Copyright 2021 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# Secondary Owner:
#
# This file contains the implementation of Geometry types for
# Teradata Geospatial data types. These implementation allows user
# to create the singlton item like a literal that can be used in
# any Geospatial function call.
#
# ##################################################################
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.utils.dtypes import _str_list, _int_list, \
    _int_float_list, _int_float_tuple_list
from teradataml.utils.validators import _Validators
VANTAGE_EMPTY_GEOM_FMT = "EMPTY"

class GeometryType(object):
    """ Base class for Geospatial Geometry Types. """

    def __init__(self, *args):
        """ Constructor for Geometry object. """
        self._is_empty = True
        self.coordinates = VANTAGE_EMPTY_GEOM_FMT
        self._str_fmt = "{} {}"

        if args and args[0] is not None:
            self._is_empty = False
            self.coordinates = []
            self._str_fmt = "{}{}"

    def __str__(self):
        """ Return String Representation for a Geometry object. """
        return self._str_fmt.format(self.__class__.__name__,
                                    self._coords_vantage_fmt)

    def _vantage_str_(self):
        """ Return Vantage String Representation for a Geometry object. """
        return "new ST_Geometry('{}')".format(str(self))

    @property
    def coords(self):
        """ Returns the coordinates of the Geometry object. """
        return self.coordinates

    @property
    def geom_type(self):
        """ Returns the type of a Geometry. """
        return self.__class__.__name__

    def __getattr__(self, item):
        """"""
        # TODO::
        #   Add a code to create a table with ST_Geometry column and insert
        #   the value for the Geometry object in the same, when any
        #   Geospatial function is executed.
        #   Creating table and then GeoDataFrame on top of the created table,
        #   will enable us to execute any Geospatial function on the
        #   Geometry Type Object and return the results, just like shapely
        #   library does.
        #   Doing this will not require any additional things to be implemented.
        #   This is what the workflow should look like when any function
        #   (geospatial) executed on any of the Geometry Types object:
        #   1. We will enter this function, validate that the function being
        #      executed is Geospatial.
        #   2. Check if self._geodf is set or not. If set go to 4.
        #   3. If not set, then create a table with geospatial data type
        #      (ST_GEOMETRY) column.
        #       i. Get the table name from UtilFuncs get table name
        #          functionality. Should be GCed at the end.
        #       ii. Insert the User passed data in the table.
        #       iii. Set the self._geodf to the GeoDataFrame() on the created
        #            table.
        #   4. If set, then just call the function on the self._geodf.
        #      For example, self._geodf.<func_name>(...)
        "TODO"

class Point(GeometryType):
    """
    Class Point enables end user to create an object for the single Point
    using the coordinates. Allows user to use the same in GeoDataFrame
    manipulation and processing.
    """
    def __init__(self, *coordinates):
        """
        DESCRIPTION:
            Enables end user to create an object for the single Point
            using the coordinates. Allows user to use the same in GeoDataFrame
            manipulation and processing using any Geospatial function.

        PARAMETERS:
            *coordinates:
                Optional Argument.
                Specifies the coordinates of a Point. Coordinates must be
                specified in positional fashion.
                If coordinates are not passed, an object for empty point is
                created.
                When coordinates are passed, one must pass either 2 or 3
                values to define a Point in 2-dimentions or 3-dimentions.
                Types: int, float

        RETURNS:
            Point

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Point

            # Example 1: Create a Point in 2D, using x and y coordinates.
            >>> p1 = Point(0, 20)
            >>> # Print the coordinates.
            >>> print(p1.coords)
            (0, 20)
            >>> # Print the geometry type.
            >>> p1.geom_type
            'Point'
            >>>

            # Example 2: Create a Point in 3D, using x, y and z coordinates.
            >>> p2 = Point(0, 20, 30)
            >>> # Print the coordinates.
            >>> print(p2.coords)
            (0, 20, 30)
            >>>

            # Example 3: Create an empty Point.
            >>> pe = Point()
            >>> # Print the coordinates.
            >>> print(pe.coords)
            EMPTY
            >>>
        """
        super(Point, self).__init__(*coordinates)

        if len(coordinates) == 1 and isinstance(coordinates[0], tuple):
            # Create a Point by directly passing a tuple.
            coordinates = coordinates[0]
        elif len(coordinates) > 3 or len(coordinates) == 1:
            # TODO - Error handling.
            raise Exception("Must pass 2 or 3 coordinates.")

        if not self._is_empty:
            for co in coordinates:
                arg_info = [["coordinates", co, False, (int, float)]]
                _Validators()._validate_function_arguments(arg_info)

            self.x = coordinates[0]
            self.y = coordinates[1]
            self.z = None
            if len(coordinates) == 3:
                self.z = coordinates[2]

    @property
    def coords(self):
        """ Returns the coordinates of the Point Geometry object. """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return (self.x, self.y) if self.z is None else (
            self.x, self.y, self.z)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the Point Geometry object in Vantage format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return "({})".format(" ".join(map(str, self.coords)))

class LineString(GeometryType):
    """
    Class LineString enables end user to create an object for the single
    LineString using the coordinates. Allows user to use the same in
    GeoDataFrame manipulation and processing.
    """
    def __init__(self, coordinates=None):
        """
        DESCRIPTION:
            Enables end user to create an object for the single LineString
            using the coordinates. Allows user to use the same in GeoDataFrame
            manipulation and processing using any Geospatial function.

        PARAMETERS:
            coordinates:
                Optional Argument.
                Specifies the coordinates of a Line. While passing coordinates
                for a line, one must always pass coordinates in list of either
                two-tuples for 2D or list of three-tuples for 3D.
                Argument also accepts list of Points as well instead of tuples.
                If coordinates are not passed, an object for empty line is
                created.
                Types: List of
                        a. Point geometry objects or
                        b. two-tuple of int or float or
                        c. three-tuple of int or float or
                        d. Mix of any of the above.

        RETURNS:
            LineString

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Point, LineString

            # Example 1: Create a LineString in 2D, using x and y coordinates.
            >>> l1 = LineString([(0, 0), (0, 20), (20, 20)])
            >>> # Print the coordinates.
            >>> print(l1.coords)
            [(0, 0), (0, 20), (20, 20)]
            >>> # Print the geometry type.
            >>> l1.geom_type
            'LineString'
            >>>

            # Example 2: Create a LineString in 3D, using x, y and z coordinates.
            >>> l2 = LineString([(0, 0, 1), (0, 1, 3), (1, 3, 6), (3, 3, 6),
            ...                  (3, 6, 1), (6, 3, 3), (3, 3, 0)])
            >>> # Print the coordinates.
            >>> print(l1.coords)
            [(0, 0), (0, 20), (20, 20)]
            >>>

            # Example 3: Create a LineString using Point geometry objects.
            # Create some Points in 2D, using x and y coordinates.
            >>> p1 = Point(0, 20)
            >>> p2 = Point(0, 0)
            >>> p3 = Point(20, 20)
            >>> l3 = LineString([p1, p2, p3])
            >>> # Print the coordinates.
            >>> print(l3.coords)
            [(0, 20), (0, 0), (20, 20)]
            >>>

            # Example 4: Create a LineString using mix of Point geometry objects
            #            and coordinates.
            >>> p1 = Point(0, 20)
            >>> p2 = Point(20, 20)
            >>> l4 = LineString([(0, 0), p1, p2, (20, 0)])
            >>> # Print the coordinates.
            >>> print(l4.coords)
            [(0, 0), (0, 20), (20, 20), (20, 0)]
            >>>

            # Example 5: Create an empty LineString.
            >>> le = LineString()
            >>> # Print the coordinates.
            >>> print(le.coords)
            EMPTY
            >>>
        """
        super(LineString, self).__init__(coordinates)
        if coordinates is not None:
            # Argument validations.
            arg_info = [["coordinates", coordinates, False, (list, Point, tuple)]]
            _Validators()._validate_function_arguments(arg_info)

            # List of two-tuples or three-tuples or Point or mix.
            for co in coordinates:
                if isinstance(co, Point):
                    self.coordinates.append(co.coords)
                else:
                    # Validate coordinates
                    Point(*co)
                    self.coordinates.append(co)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the LineString Geometry object in Vantage format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return "({})".format(
                ", ".join(map(lambda x: " ".join(map(str, x)), self.coords)))

class Polygon(GeometryType):
    """
    Class Polygon enables end user to create an object for the single Polygon
    using the coordinates. Allows user to use the same in GeoDataFrame
    manipulation and processing.
    """
    def __init__(self, coordinates=None):
        """
        DESCRIPTION:
            Enables end user to create an object for the single Polygon
            using the coordinates. Allows user to use the same in GeoDataFrame
            manipulation and processing using any Geospatial function.

        PARAMETERS:
            coordinates:
                Optional Argument.
                Specifies the coordinates of a polygon. While passing coordinates
                for a polygon, one must always pass coordinates in list of either
                two-tuples for 2D or list of three-tuples for 3D.
                Argument also accepts list of Point and/or LineString as well
                instead of tuples.
                If coordinates are not passed, an object for empty polygon is
                created.
                Types: List of
                        a. two-tuple of int or float or
                        b. three-tuple of int or float or
                        c. Point geometry objects or
                        d. LineString geometry objects or
                        e. Mix of any of the above.

        RETURNS:
            Polygon

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Point, LineString, Polygon

            # Example 1: Create a Polygon in 2D, using x and y coordinates.
            >>> go1 = Polygon([(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)])
            >>> # Print the coordinates.
            >>> print(go1.coords)
            [(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)]
            >>> # Print the geometry type.
            >>> go1.geom_type
            'Polygon'
            >>>

            # Example 2: Create a Polygon in 3D, using x, y and z coordinates.
            >>> go2 = Polygon([(0, 0, 0), (0, 0, 20), (0, 20, 0), (0, 20, 20),
            ...                       (20, 0, 0), (20, 0, 20), (20, 20, 0), (20, 20, 20),
            ...                       (0, 0, 0)])
            >>> # Print the coordinates.
            >>> print(go2.coords)
            [(0, 0, 0), (0, 0, 20), (0, 20, 0), (0, 20, 20), (20, 0, 0), (20, 0, 20), (20, 20, 0), (20, 20, 20), (0, 0, 0)]
            >>>

            # Example 3: Create a Polygon using Point geometry objects.
            # Create Point objects in 2D, using x and y coordinates.
            >>> p1 = Point(0, 0)
            >>> p2 = Point(0, 20)
            >>> p3 = Point(20, 20)
            >>> p4 = Point(20, 0)
            >>> go3 = Polygon([p1, p2, p3, p4, p1])
            >>> # Print the coordinates.
            >>> print(go3.coords)
            [(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)]
            >>>

            # Example 4: Create a Polygon using LineString geometry objects.
            # Create some LineString objects in 2D, using x and y coordinates.
            >>> l1 = LineString([(0, 0), (0, 20), (20, 20)])
            >>> l2 = LineString([(20, 0), (0, 0)])
            >>> go4 = Polygon([l1, l2])
            >>> # Print the coordinates.
            >>> print(go4.coords)
            [(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)]
            >>>

            # Example 5: Create a Polygon using mix of Point, LineString
            #            geometry objects and coordinates.
            >>> p1 = Point(0, 0)
            >>> l1 = LineString([p1, (0, 20), (20, 20)])
            >>> go5 = Polygon([l1, (20, 0), p1])
            >>> # Print the coordinates.
            >>> print(go5.coords)
            [(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)]
            >>>

            # Example 6: Create an empty Polygon.
            >>> poe = Polygon()
            >>> # Print the coordinates.
            >>> print(poe.coords)
            EMPTY
            >>>
        """
        super(Polygon, self).__init__(coordinates)
        if coordinates is not None:
            # Argument validation.
            acc_types = (list, Point, LineString, tuple)
            arg_info = [["coordinates", coordinates, False, acc_types]]
            _Validators()._validate_function_arguments(arg_info)

            # List of two-tuples or three-tuples or LineString or Point or mix.
            for co in coordinates:
                if isinstance(co, (Point)):
                    self.coordinates.append(co.coords)
                elif isinstance(co, LineString):
                    for lco in co.coords:
                        self.coordinates.append(lco)
                else:
                    # Validate individual coordinates passed.
                    Point(*co)
                    self.coordinates.append(co)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the Polygon Geometry object in Vantage format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return "(({}))".format(
                ", ".join(map(lambda x: " ".join(map(str, x)), self.coords)))

class MultiPoint(GeometryType):
    """
    Class MultiPoint enables end user to create an object holding multiple
    Point geometry objects. Allows user to use the same in GeoDataFrame
    manipulation and processing.
    """
    def __init__(self, points=None):
        """
        DESCRIPTION:
            Enables end user to create an object holding the multiple Point
            geometry objects. Allows user to use the same in GeoDataFrame
            manipulation and processing using any Geospatial function.

        PARAMETERS:
            points:
                Optional Argument.
                Specifies the list of points. If no points are passed, an object
                for empty MultiPoint is created.
                Types: List of Point objects

        RETURNS:
            MultiPoint

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Point, MultiPoint

            # Example 1: Create a MultiPoint in 2D, using x and y coordinates.
            >>> p1 = Point(0, 0)
            >>> p2 = Point(0, 20)
            >>> p3 = Point(20, 20)
            >>> p4 = Point(20, 0)
            >>> go1 = MultiPoint([p1, p2, p3, p4, p1])
            >>> # Print the coordinates.
            >>> print(go1.coords)
            [(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)]
            >>> # Print the geometry type.
            >>> print(go1.geom_type)
            MultiPoint
            >>>

            # Example 2: Create an empty MultiPoint.
            >>> poe = MultiPoint()
            >>> # Print the coordinates.
            >>> print(poe.coords)
            EMPTY
            >>>
        """
        super(MultiPoint, self).__init__(points)
        if points is not None:
            # Argument validation.
            acc_types = (list, Point)
            arg_info = [["points", points, False, acc_types]]
            _Validators()._validate_function_arguments(arg_info)

            self.points = points
            for po in points:
                self.coordinates.append(po.coords)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the MultiPoint Geometry object in Vantage
        format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return "({})".format(
                ", ".join([pnt._coords_vantage_fmt for pnt in self.points]))

class MultiLineString(GeometryType):
    """
    Class MultiLineString enables end user to create an object holding multiple
    LineString geometry objects. Allows user to use the same in GeoDataFrame
    manipulation and processing.
    """
    def __init__(self, lines=None):
        """
        DESCRIPTION:
            Enables end user to create an object holding the multiple LineString
            geometry objects. Allows user to use the same in GeoDataFrame
            manipulation and processing using any Geospatial function.

        PARAMETERS:
            lines:
                Optional Argument.
                Specifies the list of lines. If no lines are passed, an object
                for empty MultiLineString is created.
                Types: List of LineString objects

        RETURNS:
            MultiLineString

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import LineString, MultiLineString

            # Example 1: Create a MultiLineString in 2D, using x and y coordinates.
            >>> l1 = LineString([(1, 3), (3, 0), (0, 1)])
            >>> l2 = LineString([(1.35, 3.6456), (3.6756, 0.23), (0.345, 1.756)])
            >>> go1 = MultiLineString([l1, l2])
            >>> # Print the coordinates.
            >>> print(go1.coords)
            [[(1, 3), (3, 0), (0, 1)], [(1.35, 3.6456), (3.6756, 0.23), (0.345, 1.756)]]
            >>> # Print the geometry type.
            >>> print(go1.geom_type)
            MultiLineString
            >>>

            # Example 2: Create an empty MultiLineString.
            >>> mls = MultiLineString()
            >>> # Print the coordinates.
            >>> print(mls.coords)
            EMPTY
            >>>
        """
        super(MultiLineString, self).__init__(lines)
        if lines is not None:
            # Argument validation.
            acc_types = (list, LineString)
            arg_info = [["lines", lines, False, acc_types]]
            _Validators()._validate_function_arguments(arg_info)

            self.lines = lines
            for po in lines:
                self.coordinates.append(po.coords)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the MultiLineString Geometry object in
        Vantage format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return "({})".format(
                ", ".join([line._coords_vantage_fmt for line in self.lines]))

class MultiPolygon(GeometryType):
    """
    Class MultiPolygon enables end user to create an object holding multiple
    Polygon geometry objects. Allows user to use the same in GeoDataFrame
    manipulation and processing.
    """
    def __init__(self, polygons=None):
        """
        DESCRIPTION:
            Enables end user to create an object holding the multiple Polygon
            geometry objects. Allows user to use the same in GeoDataFrame
            manipulation and processing using any Geospatial function.

        PARAMETERS:
            polygons:
                Optional Argument.
                Specifies the list of polygons. If no polygons are passed, an
                object for empty MultiPolygon is created.
                Types: List of Polygon objects

        RETURNS:
            MultiPolygon

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Polygon, MultiPolygon

            # Example 1: Create a MultiPolygon in 2D, using x and y coordinates.
            >>> po1 = Polygon([(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)])
            >>> po2 = Polygon([(0.6, 0.8), (0.6, 20.8), (20.6, 20.8), (20.6, 0.8), (0.6, 0.8)])
            >>> go1 = MultiPolygon([po1, po2])
            >>> # Print the coordinates.
            >>> print(go1.coords)
            [[(0, 0), (0, 20), (20, 20), (20, 0), (0, 0)], [(0.6, 0.8), (0.6, 20.8), (20.6, 20.8), (20.6, 0.8), (0.6, 0.8)]]
            >>> # Print the geometry type.
            >>> print(go1.geom_type)
            MultiPolygon
            >>>

            # Example 2: Create an empty MultiPolygon.
            >>> poe = MultiPolygon()
            >>> # Print the coordinates.
            >>> print(poe.coords)
            EMPTY
            >>>
        """
        super(MultiPolygon, self).__init__(polygons)
        if polygons is not None:
            # Argument validation.
            acc_types = (list, Polygon)
            arg_info = [["polygons", polygons, False, acc_types]]
            _Validators()._validate_function_arguments(arg_info)

            self.polygons = polygons
            for po in polygons:
                self.coordinates.append(po.coords)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the MultiPolygon Geometry object in Vantage
        format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return "({})".format(
                ", ".join([pnt._coords_vantage_fmt for pnt in self.polygons]))

class GeometryCollection(GeometryType):
    """
    Class GeometryCollection enables end user to create an object for the
    single GeometryCollection, i.e., collection of different geometry objects
    using the geometries. This allows user to use the same in GeoDataFrame
    manipulation and processing.
    """
    def __init__(self, geometries=None):
        """
        DESCRIPTION:
            Enables end user to create an object holding the multiple types of
            geometry objects. Allows user to use the same in GeoDataFrame
            manipulation and processing using any Geospatial function.

        PARAMETERS:
            geoms:
                Optional Argument.
                Specifies the list of different geometry types.
                If no geometries are are passed, an object for empty
                GeometryCollection is created.
                Types: List of geometry objects of types:
                        1. Point
                        2. LineString
                        3. Polygon
                        4. MultiPoint
                        5. MultiLineString
                        6. MultiPolygon
                        7. GeometryCollection
                        8. Mixture of any of these.

        RETURNS:
            GeometryCollection

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Point, LineString, Polygon, MultiPoint,
            ...    MultiLineString, MultiPolygon, GeometryCollection

            # Example 1: Create a GeometryCollection object with all geometries.
            >>> # Create Point objects.
            >>> p1 = Point(1, 1)
            >>> p2 = Point()
            >>> p3 = Point(6, 3)
            >>> p4 = Point(10, 5)
            >>> p5 = Point()
            >>>
            >>> # Create LineString Objects.
            >>> l1 = LineString([(1, 3), (3, 0), (0, 1)])
            >>> l2 = LineString([(1.35, 3.6456), (3.6756, 0.23), (0.345, 1.756)])
            >>> l3 = LineString()
            >>>
            >>> # Create Polygon Objects.
            >>> po1 = Polygon([(0, 0, 0), (0, 0, 20), (0, 20, 0), (0, 20, 20),
            ...        (20, 0, 0), (20, 0, 20), (20, 20, 0), (20, 20, 20),
            ...        (0, 0, 0)])
            >>> po2 = Polygon([(0, 0, 0), (0, 0, 20.435), (0, 20.435, 0),
            ...        (0, 20.435, 20.435), (20.435, 0, 0), (20.435, 0, 20.435),
            ...        (20.435, 20.435, 0), (20.435, 20.435, 20.435),
            ...        (0, 0, 0)])
            >>> po3 = Polygon()
            >>>
            >>> # Create MultiPolygon Object.
            >>> mpol = MultiPolygon([po1, Polygon(), po2])
            >>>
            >>> # Create MultiLineString Object.
            >>> mlin = MultiLineString([l1, l2, l3])
            >>>
            >>> # Create MultiPoint Object.
            >>> mpnt = MultiPoint([p1, p2, p3, p4, p5])
            >>>
            >>> # Create a GeometryCollection object.
            >>> gc1 = GeometryCollection([p1, p2, l1, l3, po2, po3, po1, mpol, mlin, mpnt])
            >>> # Print the coordinates.
            >>> print(gc1.coords)
            [(1, 1), 'EMPTY', [(1, 3), (3, 0), (0, 1)], 'EMPTY', [(0, 0, 0), (0, 0, 20.435), (0, 20.435, 0), (0, 20.435, 20.435), (20.435, 0, 0), (20.435, 0, 20.435), (20.435, 20.435, 0), (20.435, 20.435, 20.435), (0, 0, 0)], 'EMPTY', [(0, 0, 0), (0, 0, 20), (0, 20, 0), (0, 20, 20), (20, 0, 0), (20, 0, 20), (20, 20, 0), (20, 20, 20), (0, 0, 0)], [[(0, 0, 0), (0, 0, 20), (0, 20, 0), (0, 20, 20), (20, 0, 0), (20, 0, 20), (20, 20, 0), (20, 20, 20), (0, 0, 0)], 'EMPTY', [(0, 0, 0), (0, 0, 20.435), (0, 20.435, 0), (0, 20.435, 20.435), (20.435, 0, 0), (20.435, 0, 20.435), (20.435, 20.435, 0), (20.435, 20.435, 20.435), (0, 0, 0)]], [[(1, 3), (3, 0), (0, 1)], [(1.35, 3.6456), (3.6756, 0.23), (0.345, 1.756)], 'EMPTY'], [(1, 1), 'EMPTY', (6, 3), (10, 5), 'EMPTY']]
            >>> # Print the geometry type.
            >>> print(gc1.geom_type)
            GeometryCollection
            >>>

            # Example 2: Create an empty GeometryCollection.
            >>> gc2 = GeometryCollection()
            >>> # Print the coordinates.
            >>> print(gc2.coords)
            EMPTY
            >>>
        """
        super(GeometryCollection, self).__init__(geometries)
        if geometries is not None:
            # Argument validation.
            acc_types = (list, Point, LineString, Polygon, MultiPoint,
                         MultiLineString, MultiPolygon, GeometryCollection)
            arg_info = [["geometries", geometries, False, acc_types]]
            _Validators()._validate_function_arguments(arg_info)

            self.geometries = geometries
            for geo in geometries:
                self.coordinates.append(geo.coords)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the GeometryCollection Geometry object in
        Vantage format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            return "({})".format(
                ", ".join(map(str, self.geometries)))

class GeoSequence(LineString):
    """
    Class GeoSequence enables end user to create an object for the
    LineString geometry objects with tracking information such as
    timestamp. This allows user to use the same in GeoDataFrame
    manipulation and processing.
    """
    def __init__(self, coordinates=None, timestamps=None, link_ids=None,
                 user_field_count=0, user_fields=None):
        """
        DESCRIPTION:
            Enables end user to create an object holding the LineString
            geometry objects with tracking information such as timestamps.
            Allows user to use the same in GeoDataFrame manipulation and
            processing using any Geospatial function.

        PARAMETERS:
            coordinates:
                Optional Argument.
                Specifies the list of coordinates of a Point. While passing
                coordinates, one must always pass coordinates in list of either
                two-tuples for 2D or list of three-tuples for 3D.
                Argument also accepts list of Points as well instead of tuples.
                If coordinates are not passed, an object for empty line is
                created.
                Types: List of
                        a. Point geometry objects or
                        b. two-tuple of int or float or
                        c. three-tuple of int or float or
                        d. Mix of any of the above.

            timestamps:
                Optional Argument.
                Specifies the list of timestamp values for each coordinate with
                the following format:
                    yyyy-mm-dd hh:mi:ss.ms
                The first timestamp value is associated with the first point, the
                second timestamp value is associated with the second point, and
                so forth.
                Note:
                    You must specify n timestamp values, where n is the number of
                    points in the geosequence.
                Types: list of strings

            link_ids:
                Optional Argument.
                Specifies the list of values for the ID of the link on the road
                network for a point in the geosequence.
                This value is reserved for a future release.
                The first link ID value is associated with the first point, the
                second link ID value is associated with the second point, and
                so forth.
                Note:
                    You must specify n link ID values, where n is the number of
                    points in the geosequence.
                Types: list of ints

            user_field_count:
                Optional Argument.
                Specifies the value that represents the number of user field
                elements for each point in the geosequence.
                A value of 0 indicates that no user field elements appear after
                count in the character string.
                Default Value: 0
                Types: int

            user_fields:
                Optional Argument.
                Specifies the list of user field tuples that represents a value to
                associated with a point. For example, certain tracking systems may
                associate velocity, direction, and acceleration values with each point.
                Note:
                    1. You must specify count groups of n user field values (where n is
                       the number of points in the geosequence).
                    2. The first group provides the first user field values for each point,
                       the second group provides the second user field values for each point,
                       and so forth.
                    3. Each group can be formed using a tuple.
                Types: list of tuples of ints or floats

        RETURNS:
            GeoSequence

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Point, GeoSequence

            # Example 1: Create a GeoSequence with 2D points and no user fields.
            >>> coordinates = [(1, 3), (3, 0), (0, 1)]
            >>> timestamps = ["2008-03-17 10:34:03.53", "2008-03-17 10:38:25.21", "2008-03-17 10:41:41.48"]
            >>> link_ids = [1001, 1002, 1003]
            >>> gs1 = GeoSequence(coordinates=coordinates, timestamps=timestamps, link_ids=link_ids)
            >>> gs1.coords
            [(1, 3), (3, 0), (0, 1)]
            >>> str(gs1)
            'GeoSequence((1 3, 3 0, 0 1), (2008-03-17 10:34:03.53, 2008-03-17 10:38:25.21, 2008-03-17 10:41:41.48), (1001, 1002, 1003), (0))'
            >>>

            # Example 2: Create a GeoSequence with 3D points and 2 user fields.
            #            Note that coordinates can be provided as tuple of ints/floats
            #            or Point objects.
            >>> p1 = (3, 0, 6)
            >>> coordinates = [(1, 3, 6), p1, (6, 0, 1)]
            >>> timestamps = ["2008-03-17 10:34:03.53", "2008-03-17 10:38:25.21", "2008-03-17 10:41:41.48"]
            >>> link_ids = [1001, 1002, 1003]
            >>> user_fields = [(1, 2), (3, 4), (5, 6)]
            >>> gs2 = GeoSequence(coordinates=coordinates, timestamps=timestamps, link_ids=link_ids,
            ...                   user_field_count=2, user_fields=user_fields)
            >>> gs2.coords
            [(1, 3, 6), (3, 0, 6), (6, 0, 1)]
            >>> str(gs2)
            'GeoSequence((1 3 6, 3 0 6, 6 0 1), (2008-03-17 10:34:03.53, 2008-03-17 10:38:25.21, 2008-03-17 10:41:41.48), (1001, 1002, 1003), (2, 1, 2, 3, 4, 5, 6))'
            >>>

            # Example 3: Create an empty GeoSequence.
            >>> gs3 = GeoSequence()
            >>> # Print the coordinates.
            >>> print(gc3.coords)
            EMPTY
            >>>
        """
        self.timestamps = timestamps
        self.user_field_count = user_field_count
        self.link_ids = link_ids
        self.user_fields = user_fields

        super(GeoSequence, self).__init__(coordinates)
        all_args_provided = all([coordinates, self.timestamps, self.link_ids])
        any_args_provided = any([coordinates, self.timestamps, self.link_ids])

        if any_args_provided:
            if not all_args_provided:
                raise ValueError("Either provide all (coordinates, timestamps, link_ids) or None.")

        if all_args_provided:
            arg_info = []
            arg_info.append(["timestamps", self.timestamps, True, _str_list])
            arg_info.append(["link_ids", self.link_ids, True, _int_list])
            arg_info.append(["user_field_count", self.user_field_count, True, int])
            arg_info.append(["user_fields", self.user_fields, True,
                             (_int_float_tuple_list, _int_float_list)])
            _Validators()._validate_function_arguments(arg_info)

            _Validators._validate_list_lengths_equal(self.coordinates, "coordinates",
                                                     self.timestamps, "timestamps")
            _Validators._validate_list_lengths_equal(self.coordinates, "coordinates",
                                                     self.link_ids, "link_ids")
            if self.user_fields is not None:
                _Validators._validate_list_lengths_equal(self.coordinates, "coordinates",
                                                         self.user_fields, "user_fields")

                for uf in self.user_fields:
                    if isinstance(uf, tuple):
                        if len(uf) != self.user_field_count:
                            err_ = Messages.get_message(MessageCodes.GEOSEQ_USER_FIELD_NUM)
                            raise ValueError(err_)

    @property
    def _coords_vantage_fmt(self):
        """
        Returns the coordinates of the GeometryCollection Geometry object in
        Vantage format.
        """
        if self._is_empty:
            return VANTAGE_EMPTY_GEOM_FMT
        else:
            coords = "({})".format(
                ", ".join(map(lambda x: " ".join(map(str, x)),
                              self.coords)))
            ts = "({})".format(", ".join(self.timestamps))
            ids = "({})".format(", ".join(map(str, self.link_ids)))
            ufs = [self.user_field_count]
            if self.user_fields is not None:
                for uf in self.user_fields:
                    if not isinstance(uf, tuple):
                        ufs.append(uf)
                    else:
                        ufs.append(", ".join(map(str, list(uf))))

            uf = "({})".format(", ".join(map(str, ufs)))
        return "({}, {}, {}, {})".format(coords, ts, ids, uf)
        