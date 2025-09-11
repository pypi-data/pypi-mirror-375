# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# Secondary Owner:
#
# This file implements Axis, which is used for plotting. Axis holds all
# the properties related to axis such as grid color, x-axis label, y-axis
# label etc.
#
# ##################################################################

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.sql import ColumnExpression
from teradataml.plot.constants import MapType
from teradataml.utils.validators import _Validators


class Axis:
    def __init__(self, **kwargs):
        """
        Constructor for Axis.

        PARAMETERS:
            cmap:
                Optional Argument.
                Specifies the name of the colormap to be used for plotting.
                Notes:
                     * Significant only when corresponding type of plots is mesh or geometry.
                     * Ignored for other type of plots.
                Permitted Values:
                    * All the colormaps mentioned in below URL's are supported.
                        * https://matplotlib.org/stable/tutorials/colors/colormaps.html
                        * https://matplotlib.org/cmocean/
                Types: str

            color:
                Optional Argument.
                Specifies the color for the plot.
                Note:
                    Hexadecimal color codes are not supported.
                Permitted Values:
                    * blue
                    * orange
                    * green
                    * red
                    * purple
                    * brown
                    * pink
                    * gray
                    * olive
                    * cyan
                    * Apart from above mentioned colors, the colors mentioned in
                      https://xkcd.com/color/rgb are also supported.
                Default Value: blue
                Types: str OR list of str

            grid_color:
                Optional Argument.
                Specifies the color of the grid. By default, grid is generated with
                Gray69(#b0b0b0) color.
                Note:
                    Hexadecimal color codes are not supported.
                Permitted Values:
                    * 'blue'
                    * 'orange'
                    * 'green'
                    * 'red'
                    * 'purple'
                    * 'brown'
                    * 'pink'
                    * 'gray'
                    * 'olive'
                    * 'cyan'
                    * Apart from above mentioned colors, the colors mentioned in
                      https://xkcd.com/color/rgb are also supported.
                Default Value: 'gray'
                Types: str

            grid_format:
                Optional Argument.
                Specifies the format for the grid.
                Types: str

            grid_linestyle:
                Optional Argument.
                Specifies the line style of the grid.
                Default Value: -
                Permitted Values:
                    * -
                    * --
                    * -.
                Types: str

            grid_linewidth:
                Optional Argument.
                Specifies the line width of the grid.
                Note:
                    Valid range for "grid_linewidth" is: 0.5 <= grid_linewidth <= 10.
                Default Value: 0.8
                Types: int OR float

            legend:
                Optional Argument.
                Specifies the legend(s) for the Plot.
                Types: str OR list of str

            legend_style:
                Optional Argument.
                Specifies the location for legend to display on Plot image. By default,
                legend is displayed at upper right corner.
                    * 'upper right'
                    * 'upper left'
                    * 'lower right'
                    * 'lower left'
                    * 'right'
                    * 'center left'
                    * 'center right'
                    * 'lower center'
                    * 'upper center'
                    * 'center'
                Default Value: 'upper right'
                Types: str

            linestyle:
                Optional Argument.
                Specifies the line style for the plot.
                Permitted Values:
                    * -
                    * --
                    * -.
                    * :
                Default Value: -
                Types: str OR list of str

            linewidth:
                Optional Argument.
                Specifies the line width for the plot.
                Note:
                    Valid range for "linewidth" is: 0.5 <= linewidth <= 10.
                Default Value: 0.8
                Types: int OR float OR list of int OR list of float

            marker:
                Optional Argument.
                Specifies the type of the marker to be used.
                Permitted Values:
                    All the markers mentioned in https://matplotlib.org/stable/api/markers_api.html
                    are supported.
                Types: str OR list of str

            markersize:
                Optional Argument.
                Specifies the size of the marker.
                Note:
                    Valid range for "markersize" is: 1 <= markersize <= 20.
                Default Value: 6
                Types: int OR float OR list of int OR list of float

            position:
                Optional Argument.
                Specifies the position of the axis in the Figure. 1st element
                represents the row and second element represents column.
                Default Value: (1, 1)
                Types: tuple

            reverse_xaxis:
                Optional Argument.
                Specifies whether to reverse tick values on x-axis or not.
                Default Value: False
                Types: bool

            reverse_yaxis:
                Optional Argument.
                Specifies whether to reverse tick values on y-axis or not.
                Default Value: False
                Types: bool

            span:
                Optional Argument.
                Specifies the span of the axis in the Figure. 1st element
                represents the row and second element represents column.
                For Example,
                    Span of (2, 1) specifies the Axis occupies 2 rows and 1 column
                    in Figure.
                Default Value: (1, 1)
                Types: tuple

            series_identifier:
                Optional Argument.
                Specifies the teradataml GeoDataFrame Column which represents the
                identifier for the data. As many plots as distinct "series_identifier"
                are generated in a single Axis.
                For example:
                    consider the below data in teradataml GeoDataFrame.
                           ID   x   y
                        0  1    1   1
                        1  1    2   2
                        2  2   10  10
                        3  2   20  20
                    If "series_identifier" is not specified, simple plot is
                    generated where every 'y' is plotted against 'x' in a
                    single plot. However, specifying "series_identifier" as 'ID'
                    generates two plots in a single axis. One plot is for ID 1
                    and another plot is for ID 2.
                Types: teradataml GeoDataFrame Column.

            title:
                Optional Argument.
                Specifies the title for the Axis.
                Types: str

            xlabel:
                Optional Argument.
                Specifies the label for x-axis.
                Notes:
                     * When set to empty string, label is not displayed for x-axis.
                     * When set to None, name of the x-axis column is displayed as
                       label.
                Types: str

            xlim:
                Optional Argument.
                Specifies the range for xtick values.
                Types: tuple

            xtick_format:
                Optional Argument.
                Specifies how to format tick values for x-axis.
                Types: str

            ylabel:
                Optional Argument.
                Specifies the label for y-axis.
                Notes:
                     * When set to empty string, label is not displayed for y-axis.
                     * When set to None, name of the y-axis column(s) is displayed as
                       label.
                Types: str

            ylim:
                Optional Argument.
                Specifies the range for ytick values.
                Types: tuple

            ytick_format:
                Optional Argument.
                Specifies how to format tick values for y-axis.
                Types: str

            vmin:
                Optional Argument.
                Specifies the lower range of the color map. By default, the range
                is derived from data and color codes are assigned accordingly.
                Note:
                    "vmin" significant only for Mesh and Geometry Plot.
                Types: int OR float

            vmax:
                Optional Argument.
                Specifies the upper range of the color map. By default, the range is
                derived from data and color codes are assigned accordingly.
                Note:
                    "vmax" significant only for Mesh and Geometry Plot.
                For example:
                    Assuming user wants to use colormap 'matter' and derive the colors for
                    values which are in between 1 and 100.
                    Note:
                        Colormap 'matter' starts with Pale Yellow and ends with Violet.
                    * If "colormap_range" is not specified, then range is derived from
                      existing values. Thus, colors are represented as below in the whole range:
                      * 1 as Pale Yellow.
                      * 100 as Violet.
                    * If "colormap_range" is specified as -100 and 100, the value 1 is at middle of
                      the specified range. Thus, colors are represented as below in the whole range:
                      * -100 as Pale Yellow.
                      * 1 as Orange.
                      * 100 as Violet.
                Types: int OR float

        EXAMPLES:
            # Example 1: Create an Axis with marker as 'Pentagon'.
            >>> from teradataml import Axis
            >>> ax = Axis(marker="p")

            # Example 2: Create an Axis which does not have x-tick values
            #            and y-tick values but it should have grid.
            #            Note that the grid lines should be in the format of '-.'
            >>> from teradataml import Axis
            >>> ax = Axis(xtick_format="", ytick_format="", grid_linestyle="-.")

            # Example 3: Create an Axis which should plot only for the values
            #            between -10 to 100 on x-axis.
            >>> from teradataml import Axis
            >>> ax = Axis(xlim=(-10, 100))

            # Example 4: Create an Axis which should display legend at upper left
            #            corner and it should disable both x and y axis labels.
            >>> from teradataml import Axis
            >>> ax = Axis(legend_style="upper left", xlabel="", ylabel="")

            # Example 5: Create an Axis to format the y-axis tick values to
            #            display up to two decimal points. Also, use the color
            #            'dark green' for plotting.
            #            Note: Consider y-axis data has 5 digit floating numbers.
            >>> from teradataml import Axis
            >>> ax = Axis(ytick_format="99999.99", color='dark green')

        RAISES:
            TeradataMlException
        """
        self.__params = {**kwargs}

        self.__x_axis_data = []
        self.__y_axis_data = []
        self.__scale_data = []

        arg_info_matrix = []

        # Retrieve arg value from corresponding property.
        arg_info_matrix.append((["ignore_nulls", self.ignore_nulls, True, bool]))

        arg_info_matrix.append((["cmap", self.cmap, True, (str), True]))

        arg_info_matrix.append((["grid_color", self.grid_color, True, (str), True]))

        arg_info_matrix.append((["grid_format", self.grid_format, True, (str), True]))

        arg_info_matrix.append((["grid_linestyle", self.grid_linestyle, True, (str),
                                 True, ['-', '--', '-.']]))

        arg_info_matrix.append((["grid_linewidth", self.grid_linewidth, True, (int, float)]))

        arg_info_matrix.append((["legend", self.legend, True, (str, list), True]))

        permitted_legend_style = ['upper right', 'upper left', 'lower right',
                                  'lower left', 'right', 'center left',
                                  'center right', 'lower center',
                                  'upper center', 'center']
        arg_info_matrix.append((["legend_style", self.legend_style, True,
                                 (str), True, permitted_legend_style]))

        arg_info_matrix.append((["linestyle", self.linestyle, True, (str, list),
                                 True, ['-', '--', '-.', ':']]))

        arg_info_matrix.append((["linewidth", self.linewidth, True, (int, float, list), True]))

        arg_info_matrix.append((["marker", self.marker, True, (str, list), True]))

        arg_info_matrix.append((["markersize", self.markersize, True, (int, float, list)]))

        arg_info_matrix.append((["position", self.position, True, (tuple)]))

        arg_info_matrix.append((["span", self.span, True, (tuple)]))

        arg_info_matrix.append((["reverse_xaxis", self.reverse_xaxis, True, (bool)]))

        arg_info_matrix.append((["reverse_yaxis", self.reverse_yaxis, True, (bool)]))

        series_identifier = kwargs.get("series_identifier")
        arg_info_matrix.append((["series_identifier", series_identifier, True,
                                 (ColumnExpression)]))

        arg_info_matrix.append((["color", self.color, True, (str, list), True]))

        arg_info_matrix.append((["title", self.title, True, (str), True]))

        arg_info_matrix.append((["xlabel", self.xlabel, True, (str), False]))

        arg_info_matrix.append((["ylabel", self.ylabel, True, (str), False]))

        arg_info_matrix.append((["xlim", self.xlim, True, (tuple)]))

        arg_info_matrix.append((["ylim", self.ylim, True, (tuple)]))

        arg_info_matrix.append((["xtick_format", self.xtick_format, True, (str)]))

        arg_info_matrix.append((["ytick_format", self.ytick_format, True, (str)]))

        arg_info_matrix.append((["vmin", self.vmin, True, (int, float)]))
        arg_info_matrix.append((["vmax", self.vmax, True, (int, float)]))

        # 'vmin' and 'vmax' is applicable only for Mesh and Geometry plot.
        if self.kind.lower() not in ['geometry', 'mesh']:
            if self.vmin is not None:
                _Validators._validate_dependent_argument("vmin", self.vmin,
                                                         "kind", None, "'geometry' or 'mesh'")
            if self.vmax is not None:
                _Validators._validate_dependent_argument("vmax", self.vmax,
                                                        "kind", None, "'geometry' or 'mesh'")

        # Argument validations.
        # Skip empty check for 'xlabel', 'ylabel'.
        _Validators._validate_function_arguments(
            arg_info_matrix,
            skip_empty_check={"xlabel": [''], "ylabel": ['']}
        )

        # Argument range check.
        _Validators._validate_argument_range(self.grid_linewidth, "grid_linewidth",
                                             0.5, lbound_inclusive=True,
                                             ubound=10, ubound_inclusive=True)
        # Convert linewidth to list
        linewidth = UtilFuncs._as_list(self.linewidth)
        [_Validators._validate_argument_range(lw, "linewidth",
                                              0.5, lbound_inclusive=True,
                                              ubound=10, ubound_inclusive=True)
         for lw in linewidth]

        # Convert markersize to list
        markersize = UtilFuncs._as_list(self.markersize)
        [_Validators._validate_argument_range(ms, "markersize",
                                              1, lbound_inclusive=True,
                                              ubound=20, ubound_inclusive=True)
         for ms in markersize]

        self.__series_options = kwargs.get("series_options")  # Specifies SQL element - ID_SEQUENCE

        # Get the series identifier. If it is a column expression, get the column name from it.
        self.series_identifier = kwargs.get("series_identifier")
        if not isinstance(self.series_identifier, str) and self.series_identifier is not None:
            self.series_identifier = self.series_identifier.name

    def __eq__(self, other):
        """
        DESCRIPTION:
            Magic method to check if two Axis objects are equal or not.
            If all the associated parameters are same, then two Axis objects
            are equal. Else, they are not equal.

        PARAMETERS:
            other:
                Required Argument.
                Specifies the object of Axis.
                Types: Axis

        RETURNS:
            bool

        RAISES:
            None.

        EXAMPLES:
            >>> Axis() == Axis()
        """
        attrs = ["cmap", "color", "grid_color",
                 "grid_format", "grid_linestyle", "grid_linewidth",
                 "legend", "legend_style", "linestyle",
                 "linewidth", "marker", "markersize", "position",
                 "span", "reverse_xaxis", "reverse_yaxis", "series_identifier",
                 "title", "xlabel", "xlim", "xtick_format", "ylabel", "ylim", "ytick_format",
                 "vmin", "vmax", "ignore_nulls", "kind"]

        for attr in attrs:
            if getattr(self, attr) == getattr(other, attr):
                continue
            else:
                return False

        return True

    def __get_param(self, param):
        """
        DESCRIPTION:
            Internal function to get the parameter from private variable __params.

        PARAMETERS:
            param:
                Required Argument.
                Specifies the name of the parameter.
                Types: str

        RETURNS:
            str OR int OR float OR list

        RAISES:
            None.

        EXAMPLES:
            self.__get_param("xlim")
        """
        return self.__params.get(param)

    def __set_param(self, param_name, param_value):
        """
        DESCRIPTION:
            Internal function to set the parameter.

        PARAMETERS:
            param_name:
                Required Argument.
                Specifies the name of the parameter.
                Types: str

            param_value:
                Required Argument.
                Specifies the value for the parameter mentioned in "param_name".
                Types: str OR int OR float OR list

        RETURNS:
            bool

        RAISES:
            None.

        EXAMPLES:
            self.__set_param("xlim", (1, 100))
        """
        self.__params[param_name] = param_value
        return True

    @property
    def ignore_nulls(self):
        """ Getter for argument "ignore_nulls". """
        return self.__get_param("ignore_nulls")

    @ignore_nulls.setter
    def ignore_nulls(self, value):
        """ Setter for argument "ignore_nulls". """
        return self.__set_param("ignore_nulls", value)

    @property
    def cmap(self):
        """ Getter for argument "cmap". """
        return self.__get_param("cmap")

    @cmap.setter
    def cmap(self, value):
        """ Setter for argument "cmap". """
        return self.__set_param("cmap", value)

    @property
    def vmin(self):
        """ Getter for argument "vmin". """
        return self.__get_param("vmin")

    @vmin.setter
    def vmin(self, value):
        """ Setter for argument "vmin". """
        return self.__set_param("vmin", value)

    @property
    def vmax(self):
        """ Getter for argument "vmax". """
        return self.__get_param("vmax")

    @vmax.setter
    def vmax(self, value):
        """ Setter for argument "vmax". """
        return self.__set_param("vmax", value)

    @property
    def grid_color(self):
        """ Getter for argument "grid_color". """
        return self.__get_param("grid_color")

    @grid_color.setter
    def grid_color(self, value):
        """ Setter for argument "grid_color". """
        return self.__set_param("grid_color", value)

    @property
    def grid_format(self):
        """ Getter for argument "grid_format". """
        return self.__get_param("grid_format")

    @grid_format.setter
    def grid_format(self, value):
        """ Setter for argument "grid_format". """
        return self.__set_param("grid_format", value)

    @property
    def grid_linestyle(self):
        """ Getter for argument "grid_linestyle". """
        return self.__get_param("grid_linestyle")

    @grid_linestyle.setter
    def grid_linestyle(self, value):
        """ Setter for argument "grid_linestyle". """
        return self.__set_param("grid_linestyle", value)

    @property
    def grid_linewidth(self):
        """ Getter for argument "grid_linewidth". """
        return self.__get_param("grid_linewidth")

    @grid_linewidth.setter
    def grid_linewidth(self, value):
        """ Setter for argument "grid_linewidth". """
        return self.__set_param("grid_linewidth", value)

    @property
    def legend(self):
        """ Getter for argument "legend". """
        return self.__get_param("legend")

    @legend.setter
    def legend(self, value):
        """ Setter for argument "legend". """
        return self.__set_param("legend", value)

    @property
    def legend_style(self):
        """ Getter for argument "legend_style". """
        return self.__get_param("legend_style")

    @legend_style.setter
    def legend_style(self, value):
        """ Setter for argument "legend_style". """
        return self.__set_param("legend_style", value)

    @property
    def linestyle(self):
        """ Getter for argument "linestyle". """
        return self.__get_param("linestyle")

    @linestyle.setter
    def linestyle(self, value):
        """ Setter for argument "linestyle". """
        return self.__set_param("linestyle", value)

    @property
    def linewidth(self):
        """ Getter for argument "linewidth". """
        return self.__get_param("linewidth")

    @linewidth.setter
    def linewidth(self, value):
        """ Setter for argument "linewidth". """
        return self.__set_param("linewidth", value)

    @property
    def marker(self):
        """ Getter for argument "marker". """
        return self.__get_param("marker")

    @marker.setter
    def marker(self, value):
        """ Setter for argument "marker". """
        return self.__set_param("marker", value)

    @property
    def markersize(self):
        """ Getter for argument "markersize". """
        return self.__get_param("markersize")

    @markersize.setter
    def markersize(self, value):
        """ Setter for argument "markersize". """
        return self.__set_param("markersize", value)

    @property
    def reverse_xaxis(self):
        """ Getter for argument "reverse_xaxis". """
        return self.__get_param("reverse_xaxis")

    @reverse_xaxis.setter
    def reverse_xaxis(self, value):
        """ Setter for argument "reverse_xaxis". """
        return self.__set_param("reverse_xaxis", value)

    @property
    def reverse_yaxis(self):
        """ Getter for argument "reverse_yaxis". """
        return self.__get_param("reverse_yaxis")

    @reverse_yaxis.setter
    def reverse_yaxis(self, value):
        """ Setter for argument "reverse_yaxis". """
        return self.__set_param("reverse_yaxis", value)

    @property
    def color(self):
        """ Getter for argument "color". """
        return self.__get_param("color")

    @color.setter
    def color(self, value):
        """ Setter for argument "color". """
        return self.__set_param("color", value)

    @property
    def xlabel(self):
        """ Getter for argument "xlabel". """
        return self.__get_param("xlabel")

    @xlabel.setter
    def xlabel(self, value):
        """ Setter for argument "xlabel". """
        return self.__set_param("xlabel", value)

    @property
    def xlim(self):
        """ Getter for argument "xlim". """
        return self.__get_param("xlim")

    @xlim.setter
    def xlim(self, value):
        """ Setter for argument "xlim". """
        return self.__set_param("xlim", value)

    @property
    def xtick_format(self):
        """ Getter for argument "xtick_format". """
        return self.__get_param("xtick_format")

    @xtick_format.setter
    def xtick_format(self, value):
        """ Setter for argument "xtick_format". """
        return self.__set_param("xtick_format", value)

    @property
    def ylabel(self):
        """ Getter for argument "ylabel". """
        return self.__get_param("ylabel")

    @ylabel.setter
    def ylabel(self, value):
        """ Setter for argument "ylabel". """
        return self.__set_param("ylabel", value)

    @property
    def ylim(self):
        """ Getter for argument "ylim". """
        return self.__get_param("ylim")

    @ylim.setter
    def ylim(self, value):
        """ Setter for argument "ylim". """
        return self.__set_param("ylim", value)

    @property
    def ytick_format(self):
        """ Getter for argument "ytick_format". """
        return self.__get_param("ytick_format")

    @ytick_format.setter
    def ytick_format(self, value):
        """ Setter for argument "ytick_format". """
        return self.__set_param("ytick_format", value)

    @property
    def title(self):
        """ Getter for argument "title". """
        return self.__get_param("title")

    @title.setter
    def title(self, value):
        """ Setter for argument "title". """
        return self.__set_param("title", value)

    @property
    def kind(self):
        """ Getter for argument "kind". """
        _k = self.__get_param("kind")
        return _k if _k is not None else "line"

    @kind.setter
    def kind(self, value):
        """ Setter for argument "kind". """
        return self.__set_param("kind", value)

    @property
    def position(self):
        """ Getter for argument "position". """
        _p = self.__get_param("position")
        return (1, 1) if _p is None else _p

    @position.setter
    def position(self, value):
        """ Setter for argument "position". """
        return self.__set_param("position", value)

    @property
    def span(self):
        """ Getter for argument "span". """
        _s = self.__get_param("span")
        return (1, 1) if _s is None else _s

    @span.setter
    def span(self, value):
        """ Setter for argument "span". """
        return self.__set_param("span", value)

    def set_params(self, **kwargs):
        """
        DESCRIPTION:
            Function to set the parameters for Axis object.

        PARAMETERS:
            **kwargs:
                Keyword arguments passed to the method, i.e., set_params.
                All the arguments supported for Axis object are supported here.
                Refer to 'Axis' documentation for arguments supported by it.

        RETURNS:
             True, if successful.

        EXAMPLES:
            # Create a default Axis object.
            >>> from teradataml import Axis
            >>> ax = Axis()

            # Example 1: Disable x-axis label for an existing Axis object.
            >>> ax.set_params(xlabel="")

            # Example 2: Set the title for an existing Axis object. Also, disable
            #            x-tick values.
            >>> ax.set_params(title="Title", xtick_values="")
        """
        self.__params.update(kwargs)
        return True

    def _set_data(self, x, y, scale=None):
        """
        DESCRIPTION:
            Internal function to set the x-axis and y-axis data to Axis object.

        PARAMETERS:
            x:
                Required Argument.
                Specifies the x-axis data.
                Types: teradataml DataFrame Column

            y:
                Required Argument.
                Specifies the y-axis data.
                Types: teradataml DataFrame Column OR list of teradataml DataFrame Column.

            scale:
                Optional Argument.
                Specifies the scale data which is required for wiggle and mesh plots.
                Note:
                    "scale" is significant for wiggle and mesh plots. Ignored for other
                    type of plots.
                Types: teradataml DataFrame Column OR list of teradataml DataFrame Column.

        EXAMPLES:
            >>> ax = Axis()
            >>> ax._set_data(df.col1, [df.col2, df.col3])
        """
        # Before setting the data, clear it first.
        self.__clear_axis_data()

        y = UtilFuncs._as_list(y)

        # Make sure number of columns mentioned in x-axis is
        # same as number of columns mentioned in y-axis.
        x = UtilFuncs._as_list(x)
        if len(x) != len(y):
            x = x * len(y)

        scale = UtilFuncs._as_list(scale)

        self.__x_axis_data.extend(x)
        self.__y_axis_data.extend(y)
        self.__scale_data.extend(scale)

    def __clear_axis_data(self):
        """
        DESCRIPTION:
            Internal function to clear the axis data.

        RETURNS:
            bool

        EXAMPLES:
            >>> ax = Axis()
            >>> ax._Axis__clear_axis_data()
        """
        self.__x_axis_data.clear()
        self.__y_axis_data.clear()
        self.__scale_data.clear()

        return True

    def _has_data(self):
        """
        DESCRIPTION:
            Internal function to check whether axis is associated with data or not.

        RETURNS:
            bool

        EXAMPLES:
            >>> ax = Axis()
            >>> ax._has_data()
        """
        return bool(self.__x_axis_data)

    def __repr__(self):
        """
        DESCRIPTION:
            String representation of Axis Object.

        RETURNS:
            str.

        RAISES:
            None.

        EXAMPLES:
            # Create an Axis Object.
            >>> from teradataml import Axis
            >>> axis = Axis()
            >>> print(axis)
        """
        return "{}(position={}, span={})".format(self.__class__.__name__, self.position, self.span)

    def _get_plot_data(self):
        """
        DESCRIPTION:
            Internal function to get the plot data. The function, which is called from Plot object
            gets all the corresponding information to generate the plot.

        RETURNS:
            tuple, with 3 elements.
                * element 1 represents again a tuple - 2nd element represents a SELECT statement
                  and 1st element represents a string which is the alias table name of SELECT
                  statement. It is necessary to get the alias table name also as series spec
                  references alias table names.
                * element 2 represents either a series spec or matrix spec in string format.
                * element 3 represents a dictionary with all the parameters for Plot.

        RAISES:
            None.

        EXAMPLES:
            >>> from teradataml import Axis
            >>> axis = Axis()
            >>> axis._get_plot_data()
        """

        # TODO: Run only once and store this information. Also, df.concat is a costly operation.
        #  Will be implemented with ELE-5803.
        _virtual_table, _spec = self.__get_matrix_spec() if self.kind in (MapType.MESH.value, MapType.WIGGLE.value) \
            else self.__get_series_spec()

        return (_virtual_table, _spec, self._get_params())

    def __get_series_spec(self):
        """
        DESCRIPTION:
            Internal function to generate TDSeries Spec.
            * If user pass 'series_id' by using the argument "series_identifier", then consider 'series_id'
              as "series_identifier", x-axis data for 'row_axis' and y-axis data for 'payload_field' in
              TDSeries object. Both, 'row_index_style' and 'payload_content' can be derived
              programatically using __get_index_style() and __get_payload_content() respectively.
            * If user do not pass 'series_id', then the function constructs the series spec as below:
              * walk through x-axis and y-axis data.
              * Construct a new teradataml DataFrame by generating a new column for ID field
                along with x and y axis columns.
                * ID Column value can be either str or float or int. Since the column will be
                  used as legend if user do not specify the legend, make sure ID Column value
                  is Y-Axis column name. This makes a very good user experience in Composite plots.
                * For geometry and corr plot, y axis can be a tuple. In such cases, make sure to generate
                  the ID Column Value with all the columns mentioned in tuple.
                  * Note that, if it is tuple, Columns mentioned in tuple can have same name. Make
                    sure to generate the ID Column value as a unique value.
                * With the above information, i.e, ID Column, x-axis data and y-axis data, construct a
                  new teradataml DataFrame.
              * Repeat the above process if user pass multiple ColumnExpression(s) for y-axis data and
                concatenate the generated DataFrame with previously generated DataFrame vertically.

        RAISES:
            TeradatamlException - If all the ColumnExpression(s) mentioned in y-axis are of not same type.

        RETURNS:
            tuple

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__get_series_spec()
        """
        from teradataml.dataframe.dataframe import TDSeries

        if self.series_identifier:
            # Remove null values from DataFrame
            if self.ignore_nulls:
                _df = self.__x_axis_data[0]._parent_df
                _subset = [column_name.name for column_name in self.__y_axis_data]
                _subset.append(self.__x_axis_data[0].name)
                _df = _df.dropna(how='any', subset=_subset)

            # Execute the node and create the table in Vantage.
            if self.__y_axis_data[0]._parent_df._table_name is None:
                # Assuming all the columns are from same DataFrame.
                self.__y_axis_data[0]._parent_df.materialize()

            series = TDSeries(data=_df if self.ignore_nulls else self.__x_axis_data[0]._parent_df,
                              id=self.series_identifier,
                              row_index=self.__x_axis_data[0].name,
                              row_index_style=self.__get_index_style(self.__x_axis_data[0]),
                              payload_field=self.__y_axis_data[0].name,
                              payload_content=self.__get_payload_content(self.__y_axis_data[0]))
            return "", series._get_sql_repr(True)

        # Since user does not pass series identifier, convert the data in to TDSeries spec.
        _index = 1
        _previous_df = None

        # Loop through every element and concatenate the dataframes vertically, i.e.,
        # using UNION ALL clause.
        for index, (_x, _y) in enumerate(zip(self.__x_axis_data, self.__y_axis_data)):
            _df = _y._parent_df if not isinstance(_y, tuple) else _y[0]._parent_df
            # For correlated and geometry graph, user can pass two params for PAYLOAD FIELD.
            if isinstance(_y, tuple):
                # Generate the id_column name programatically. This appears at legend
                # if legend is shown. So, build it meaningfully.
                _id_column = "{}_{}_{}".format(_y[0].compile(), _y[1].compile(), _index)
                columns = {"y_identifier":UtilFuncs._replace_special_chars(_id_column), "id":index, "x":_x, "y1":_y[0], "y2":_y[1]}
                payload_field = ["y1", "y2"]
            else:
                columns = {"y_identifier":UtilFuncs._replace_special_chars(_y.compile()), "id":index, "x":_x, "y":_y}
                payload_field = "y"

            _df = _df.assign(**columns, drop_columns=True)
            # Concatenate with previous DataFrame.
            if _previous_df:
                # TODO: Note that concat is a very costly operation. Infact, it is very very slow.
                #  Consider generating VIRTUAL tables or UNPIVOT.
                #  Will be addressed with ELE-5808.
                _df = _previous_df.concat(_df)

            _previous_df = _df
            # Flatten the DataFrame.
            _index = _index + 1
        # Remove null values from DataFrame
        if self.ignore_nulls:
            _df = _df.dropna()
        _df.materialize()
        series = TDSeries(data=_df,
                          id="id",
                          row_index="x",
                          row_index_style=self.__get_index_style(_df.x),
                          payload_field=payload_field,
                          payload_content=self.__get_payload_content(self.__y_axis_data[0]))

        # TODO: Should return a virtual table at first element if required.
        #  Will be addressed with ELE-5808.
        return "", series._get_sql_repr(True)

    def __get_matrix_spec(self):
        """
        DESCRIPTION:
            Internal function to generate TDMatrix Spec.
            * If user pass 'matrix_id' by using the argument "series_identifier", then consider 'matrix_id'
              as "series_identifier", x-axis data for 'row_axis' and y-axis data for 'column_axis' and
              scale data for 'payload_field' in TDMatrix object. Both, 'row_index_style' and 'payload_content'
              can be derived programatically using __get_index_style() and __get_payload_content()
              respectively.
            * If user do not pass 'matrix_id', then the function constructs the matrix spec as below:
              * walk through x-axis, y-axis and scale data.
              * Construct a new teradataml DataFrame by generating a new column for ID field
                * ID Column value can be either str or float or int. Since the column will be
                  used as legend if user do not specify the legend, make sure ID Column value
                  is Y-Axis column name. This makes a very good user experience in Composite plots.
                * With the above information, i.e, ID Column, x-axis data, y-axis data and scale data,
                  construct a new teradataml DataFrame.
              * Repeat the above process if user pass multiple ColumnExpression(s) for y-axis data and
                concatenate the generated DataFrame with previously generated DataFrame vertically.

        RAISES:
            TeradatamlException - If all the ColumnExpression(s) mentioned in y-axis are of not same type.

        RETURNS:
            tuple

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__get_matrix_spec()
        """
        from teradataml.dataframe.dataframe import TDMatrix

        if self.series_identifier:
            # Remove null values from DataFrame
            if self.ignore_nulls:
                _df = self.__x_axis_data[0]._parent_df
                _subset = [column_name.name for column_name in self.__y_axis_data]
                _subset.append(self.__x_axis_data[0].name)
                _subset.extend(column_name.name for column_name in self.__scale_data)
                _df = _df.dropna(how='any', subset=_subset)

            # Execute the node and create the table/view in Vantage.
            if self.__y_axis_data[0]._parent_df._table_name is None:
                self.__y_axis_data[0]._parent_df.materialize()

            matrix = TDMatrix(data=_df if self.ignore_nulls else self.__x_axis_data[0]._parent_df,
                              id=self.series_identifier,
                              row_index=self.__x_axis_data[0].name,
                              row_index_style=self.__get_index_style(self.__x_axis_data[0]),
                              column_index=self.__y_axis_data[0].name,
                              column_index_style=self.__get_index_style(self.__y_axis_data[0]),
                              payload_field=self.__scale_data[0].name,
                              payload_content=self.__get_payload_content(self.__scale_data[0]))
            return "", matrix._get_sql_repr(True)

        # Since user do not pass matrix identifier, convert the data in to TDMatrix spec.
        _previous_df = None
        for index, (_x, _y, _data) in enumerate(zip(self.__x_axis_data, self.__y_axis_data, self.__scale_data)):
            _df = _x._parent_df
            columns = {"y_identifier": UtilFuncs._replace_special_chars(_y.compile()), "id":index, "x": _x, "y": _y, "data": _data}
            _df = _df.assign(**columns, drop_columns=True)
            if _previous_df:
                # TODO: Note that concat is a very costly operation. Infact, it is very very slow.
                #  Consider generating VIRTUAL tables or UNPIVOT.
                #  Will be addressed with ELE-5808.
                _df = _previous_df.concat(_df)

            _previous_df = _df
        # Remove null values from DataFrame
        if self.ignore_nulls:
            _df = _df.dropna()
        _df.materialize()
        matrix = TDMatrix(data=_df,
                          id="id",
                          row_index="x",
                          row_index_style=self.__get_index_style(_df.x),
                          column_index="y",
                          column_index_style=self.__get_index_style(_df.y),
                          payload_field="data",
                          payload_content="REAL")

        # TODO: Should return a virtual table at first element if required.
        #  Will be addressed with ELE-5808.
        return "", matrix._get_sql_repr(True)

    def __get_index_style(self, _x):
        """
        DESCRIPTION:
            Internal function to generate the value for argument "row_index_style"
            in TDSeries/TDMatrix objects.

        PARAMETERS:
            _x:
               Required Argument.
               Specifies the ColumnExpression of x-axis data.
               Types: teradataml ColumnExpression.

        RETURNS:
            str

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__get_index_style()
        """
        if UtilFuncs._teradata_type_to_python_type(_x.type) in ('int', 'float', 'str'):
            return "SEQUENCE"
        return "TIMECODE"

    def __get_payload_content(self, _y):
        """
        DESCRIPTION:
            Internal function to generate the value for argument "payload_content"
            in TDSeries/TDMatrix objects.

        PARAMETERS:
            _y:
               Required Argument.
               Specifies the ColumnExpression of y-axis data.
               Note that y-axis can be a list of ColumnExpression(s) also.
               Since all the Columns are concatenated vertically, every column
               type should be same. So, deriving "payload_content" value for 1st
               element is suffice.
               Types: teradataml ColumnExpression.

        RETURNS:
            str

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__get_payload_content()
        """
        # If y-axis is a tuple, return MULTIVAR_ANYTYPE.
        if self.kind == MapType.GEOMETRY.value:
            return "MULTIVAR_ANYTYPE"

        if self.kind == MapType.CORR.value:
            return "MULTIVAR_REAL" if isinstance(_y, tuple) else "REAL"

        return "REAL"

    @staticmethod
    def __get_color_code(color):
        """
        DESCRIPTION:
            Internal function to get the string for a color which is recognised by TD_PLOT.

        RETURNS:
            str

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__get_color_code("orange")
        """
        default_colors = {'blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan'}
        return "tab:{}".format(color) if color in default_colors else "xkcd:{}".format(color)

    def __get_series_parameters(self):
        """
        DESCRIPTION:
            Internal function to generate the parameters for individual Series.

        RETURNS:
            list

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__get_series_parameters()
        """
        _series_params = []
        for index in range(len(self.__y_axis_data)):
            _series_param = {"ID": index+1}
            color = self._get_series_param(self.color, index)
            if color:
                _series_param["COLOR"] = "'{}'".format(self.__get_color_code(color))

            line_style = self._get_series_param(self.linestyle, index)
            self.__update_plot_params(_series_param, "LINESTYLE", line_style)

            line_width = self._get_series_param(self.linewidth, index)
            self.__update_plot_params(_series_param, "LINEWIDTH", line_width)

            marker = self._get_series_param(self.marker, index)
            self.__update_plot_params(_series_param, "MARKER", marker)

            marker_size = self._get_series_param(self.markersize, index)
            self.__update_plot_params(_series_param, "MARKERSIZE", marker_size)

            # If user pass legend name use it. Else, derive it from Y-Axis.
            # Legend is not applicable for wiggle and mesh plots.
            if self.kind not in (MapType.MESH.value, MapType.WIGGLE.value):
                legend_name = self._get_series_param(self.legend, index)
                if legend_name:
                    _series_param["NAME"] = "'{}'".format(legend_name)
                else:
                    columns = self.__y_axis_data[index] if isinstance(self.__y_axis_data[index], tuple) else \
                        [self.__y_axis_data[index]]
                    columns = [UtilFuncs._replace_special_chars(col.compile()) for col in columns]
                    _series_param["NAME"] = "'{}'".format(" / ".join(columns))

            _series_params.append(_series_param)
        return _series_params

    def _get_params(self):
        """
        DESCRIPTION:
            Internal function to generate the parameters for the plot.

        RETURNS:
            dict

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis_get_params()
        """
        func_params = {"CELL": (self.position[1], self.position[0]),
                       "SPAN": (self.span[1], self.span[0]),
                       "TYPE": "'{}'".format(self.kind),
                       "XLABEL": "'{}'".format(self.get_xaxis_label()),
                       "YLABEL": "'{}'".format(self.get_yaxis_label()),
                       "SERIES": self.__get_series_parameters()
                       }

        self.__update_plot_params(func_params, "TITLE", self.title)
        self.__update_plot_params(func_params, "XFORMAT", self.xtick_format)
        self.__update_plot_params(func_params, "YFORMAT", self.ytick_format)
        self.__update_plot_params(func_params, "XRANGE", self.xlim)
        self.__update_plot_params(func_params, "YRANGE", self.ylim)

        if self.reverse_xaxis is True:
            func_params["FLIPX"] = 1

        if self.reverse_yaxis is True:
            func_params["FLIPY"] = 1

        # For subplot or multiple series, make sure to populate legend.
        # For mainplot, leave it to user's choice.
        if self._is_sub_plot() or self.series_identifier or (len(self.__y_axis_data) > 1) and \
                self.kind not in (MapType.MESH.value, MapType.WIGGLE.value):
            func_params["LEGEND"] = "'{}'".format("best" if not self.legend_style else self.legend_style)
        else:
            self.__update_plot_params(func_params, "LEGEND", self.legend_style)

        # Populate GRID parameters.
        if self.grid_format or self.grid_color or self.grid_linestyle or self.grid_linewidth:
            _grid_params = {}
            self.__update_plot_params(_grid_params, "COLOR", self.__get_color_code(self.grid_color))
            self.__update_plot_params(_grid_params, "FORMAT", self.grid_format)
            self.__update_plot_params(_grid_params, "LINESTYLE", self.grid_linestyle)
            self.__update_plot_params(_grid_params, "LINEWIDTH", self.grid_linewidth)
            func_params["GRID"] = _grid_params

        # Populate color map parameters.
        if self.cmap or self.vmin:
            # TODO: User should control the COLORBAR. Expose a parameter to user.
            _color_map_params = {"COLORBAR": 1}
            self.__update_plot_params(_color_map_params, "RANGE", None if self.vmin is None else (self.vmin, self.vmax))
            self.__update_plot_params(_color_map_params, "NAME", self.cmap)
            func_params["COLORMAP"] = _color_map_params

        return func_params

    @staticmethod
    def __update_plot_params(func_params, plot_param, value):
        """
        DESCRIPTION:
            Internal function to update the Plot parameter.
            The function check whether "value" is None or not. If None,
            no action from this function on "func_params". Else, "func_params"
            is updated with "plot_param".

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__update_plot_params({}, "a", "b")
        """
        if value is not None:
            func_params[plot_param] = "'{}'".format(value) if isinstance(value, str) else value

    @staticmethod
    def _get_series_param(param, index):
        """
        DESCRIPTION:
            Internal function to get the series parameter.
            User can pass a list of values or a single value for series parameter's.
            The function get's the corresponding element based on the index. If
            element is not found, the function returns a None.

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis_get_series_param(["a"], 1)
        """
        try:
            return UtilFuncs._as_list(param)[index]
        except IndexError:
            return None

    def get_xaxis_label(self):
        """
        DESCRIPTION:
            The function generates the x-axis label based on user input. If user specifies x-axis
            label, the function returns the same. Otherwise, the function generates the x-axis
            label from x-axis Column Name.

        RETURNS:
            str

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis().get_xaxis_label()
        """
        return self.xlabel if self.xlabel is not None else self.__get_label([self.__x_axis_data[0]])

    def get_yaxis_label(self):
        """
        DESCRIPTION:
            The function generates the y-axis label based on user input. If user specifies y-axis
            label, the function returns the same. Otherwise, the function generates the y-axis
            label from y-axis Column Name.

        RETURNS:
            str

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis().get_yaxis_label()
        """
        return self.ylabel if self.ylabel is not None else self.__get_label(self.__y_axis_data)

    @staticmethod
    def __get_label(data):
        """
        DESCRIPTION:
            Internal function to generate the label.

        RETURNS:
            str

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._Axis__get_label()
        """
        _rpl_spcl_chars = UtilFuncs._replace_special_chars
        # For correlation graph and GeoSpatial, user can pass a tuple of columns. Basically,
        # the SERIES_SPEC accepts 2 values for FIELD column.
        if isinstance(data[0], tuple):
            # If it is a tuple, it has only two elements, both represents DataFrame columns.
            # Generate the label based on two column names.
            return " / ".join(
                ("{} - {}".format(_rpl_spcl_chars(c[0].compile()), _rpl_spcl_chars(c[1].compile())) for c in data))

        return " / ".join((_rpl_spcl_chars(c_name.compile()) for c_name in data))

    def _is_sub_plot(self):
        """
        DESCRIPTION:
            Internal function to check if the Axis is for subplot or not.

        RETURNS:
            bool

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._is_sub_plot()
        """
        return False


class AxesSubplot(Axis):
    def _is_sub_plot(self):
        """
        DESCRIPTION:
            Internal function to check if the Axis is for subplot or not.

        RETURNS:
            bool

        EXAMPLES:
            >>> from teradataml import Axis
            >>> Axis()._is_sub_plot()
        """
        return True
