# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# Secondary Owner:
#
# This file implements _Plot, which is used to generate plot's on
# teradataml DataFrames.
#
# ##################################################################
import os
from sqlalchemy import text
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import get_connection
from teradataml.dataframe.sql import ColumnExpression
from teradataml.options.configure import configure
from teradataml.utils.validators import _Validators
from teradataml.options.display import display
from teradataml.plot.axis import Axis
from teradataml.plot.figure import Figure


class _Plot:
    def __init__(self, x, y, scale=None, kind='line', **kwargs):
        """
        DESCRIPTION:
            Generate plots on teradataml DataFrame. Following type of plots
            are supported, which can be specified using argument "kind":
                * bar plot
                * corr plot
                * line plot
                * mesh plot
                * scatter plot
                * wiggle plot

        PARAMETERS:
            x:
                Required Argument.
                Specifies a DataFrame column to use for the x-axis data.
                Types: teradataml DataFrame Column

            y:
                Required Argument.
                Specifies DataFrame column(s) to use for the y-axis data.
                Types: teradataml DataFrame Column OR list of teradataml DataFrame Columns.

            scale:
                Optional Argument.
                Specifies DataFrame column(s) to use for scale data to
                wiggle and mesh plots.
                Note:
                    "scale" is significant for wiggle and mesh plots. Ignored for other
                    type of plots.
                Types: teradataml DataFrame Column OR list of teradataml DataFrame Columns.

            kind:
                Optional Argument.
                Specifies the kind of plot.
                Permitted Values:
                    * 'line'
                    * 'bar'
                    * 'scatter'
                    * 'corr'
                    * 'wiggle'
                    * 'mesh'
                Default Value: line
                Types: str

            ax:
                Optional Argument.
                Specifies the axis for the plot.
                Types: Axis

            cmap:
                Optional Argument.
                Specifies the name of the colormap to be used for plotting.
                Note:
                    * Significant only when corresponding type of plot is mesh or geometry.
                    * Ignored for other type of plots.
                Permitted Values:
                    * All the colormaps mentioned in below URLs are supported.
                        * https://matplotlib.org/stable/tutorials/colors/colormaps.html
                        * https://matplotlib.org/cmocean/
                Types: str

            color:
                Optional Argument.
                Specifies the color for the plot.
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
                Types: str

            figure:
                Optional Argument.
                Specifies the figure for the plot.
                Types: Figure

            figsize:
                Optional Argument.
                Specifies the size of the figure in a tuple of 2 elements. First
                element represents width of plot image in pixels and second
                element represents height of plot image in pixels.
                Default Value: (640, 480)
                Types: tuple

            figtype:
                Optional Argument.
                Specifies the type of the image to generate.
                Permitted Values:
                    * 'png'
                    * 'jpg'
                    * 'svg'
                Default Value: 'png'
                Types: str

            figdpi:
                Optional Argument.
                Specifies the dots per inch for the plot image.
                Note:
                    * Valid range for "dpi" is: 72 <= dpi <= 300.
                    * This argument is not applicable for SVG Type image.
                Default Value: 100 for PNG and JPG Type image.
                Types: int

            grid_color:
                Optional Argument.
                Specifies the color of the grid. By default, grid is generated with
                Gray color.
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
                Types: str

            grid_format:
                Optional Argument.
                Specifies the format for the grid.
                Types: str

            grid_linestyle:
                Optional Argument.
                Specifies the line style of the grid.
                Permitted Values:
                    * -
                    * --
                    * -.
                Default Value: -
                Types: str

            grid_linewidth:
                Optional Argument.
                Specifies the line width of the grid.
                Note:
                    Valid range for "grid_linewidth" is: 0.5 <= grid_linewidth <= 10.
                Default Value: 0.8
                Types: int OR float

            heading:
                Optional Argument.
                Specifies the heading for the plot.
                Types: str

            legend:
                Optional Argument.
                Specifies the legend(s) for the Plot.
                Types: str OR list of str

            legend_style:
                Optional Argument.
                Specifies the location for legend to display on Plot image.
                Permitted Values:
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
                Types: str

            linewidth:
                Optional Argument.
                Specifies the line width for the plot.
                Note:
                    Valid range for "linewidth" is: 0.5 <= linewidth <= 10.
                Default Value: 0.8
                Types: int OR float

            marker:
                Optional Argument.
                Specifies the type of the marker to be used.
                Permitted Values:
                    All the markers mentioned in https://matplotlib.org/stable/api/markers_api.html
                    are supported.
                Types: str

            markersize:
                Optional Argument.
                Specifies the size of the marker.
                Note:
                    Valid range for "markersize" is: 1 <= markersize <= 20.
                Default Value: 6
                Types: int OR float

            position:
                Optional Argument.
                Specifies the position of the axis in the figure. Accepts a tuple
                of two elements where first element represents the row and second
                element represents column.
                Default Value: (1, 1)
                Types: tuple

            span:
                Optional Argument.
                Specifies the span of the axis in the figure. Accepts a tuple
                of two elements where first element represents the row and second
                element represents column.
                For Example,
                    Span of (2, 1) specifies the Axis occupies 2 rows and 1 column
                    in Figure.
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

            series_identifier:
                Optional Argument.
                Specifies the teradataml DataFrame Column which represents the
                identifier for the data. As many plots as distinct "series_identifier"
                are generated in a single Axis.
                For example:
                    consider the below data in teradataml DataFrame.
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
                Types: teradataml DataFrame Column.

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
                    "vmin" Significant only for Mesh and Geometry Plot.
                Types: int OR float

            vmax:
                Optional Argument.
                Specifies the upper range of the color map. By default, the range is
                derived from data and color codes are assigned accordingly.
                Note:
                    "vmax" Significant only for Mesh and Geometry Plot.
                For example:
                    Assuming user wants to use colormap 'matter' and derive the colors for
                    values which are in between 1 and 100.
                       Note: colormap 'matter' starts with Pale Yellow and ends with Violet.
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

            wiggle_fill:
                Optional Argument.
                Specifies whether to fill the wiggle area or not. By default, the right
                positive half of the wiggle is not filled. If specified as True, wiggle
                area is filled.
                Note:
                    Applicable only for the wiggle plot.
                Default Value: False
                Types: bool

            wiggle_scale:
                Optional Argument.
                Specifies the scale of the wiggle. By default, the amplitude of wiggle is scaled
                relative to RMS of the first payload.  In certain cases, it can lead to excessively
                large wiggles. Use SCALE to adjust the relative size of the wiggle.
                Note:
                    Applicable only for the wiggle and mesh plots.
                Types: int OR float

            ignore_nulls:
                Optional Argument.
                Specifies whether to delete rows with null values or not present in 'x', 'y' and
                'scale' params.
                Default Value: False
                Types: bool


        RAISES:
            TeradataMlException

        EXAMPLES:
            # Examples added in DataFrame.plot().
        """
        self.x = x
        self.y = y
        self.scale = scale
        self.kind = kind

        arg_info_matrix = []

        if self.kind != "geometry":
            arg_info_matrix.append(["x", self.x, False, (ColumnExpression), True])

        arg_info_matrix.append(["y", self.y, False, (ColumnExpression, list, tuple), True])
        arg_info_matrix.append(["scale", self.scale, True, ColumnExpression, True])

        # Permitted values for kind.
        kind_permitted_values = ["bar", "corr", "line", "mesh", "scatter", "wiggle",
                                 "geometry"]

        arg_info_matrix.append(["kind", self.kind, True, (str),
                                True, kind_permitted_values])

        # Extract figure and figure related arguments from kwargs.
        self.figure = kwargs.get("figure")
        self.figsize = kwargs.get("figsize", (640, 480))
        self.figtype = kwargs.get("figtype", "png")
        self.figdpi = kwargs.get("figdpi", None)

        # Default value for 'figdpi' is 100 for figtype='png' and figtype='jpg'.
        if self.figtype in ["png", "jpg"] and self.figdpi is None:
            self.figdpi = 100

        arg_info_matrix.append(["figure", self.figure, True, (Figure), False])

        figtype_permitted_values = ["png", "jpg", "svg"]
        arg_info_matrix.append(["figtype", self.figtype, True,
                                (str), True, figtype_permitted_values])
        arg_info_matrix.append(["figsize", self.figsize, True, (tuple), True])
        arg_info_matrix.append(["figdpi", self.figdpi, True, (int), True])

        # Extract wiggle_fill and wiggle_scale from parameters.
        self.wiggle_fill = kwargs.pop("wiggle_fill", None)
        self.wiggle_scale = kwargs.pop("wiggle_scale", None)

        arg_info_matrix.append((["wiggle_fill", self.wiggle_fill, True, (bool)]))
        arg_info_matrix.append((["wiggle_scale", self.wiggle_scale, True, (int, float)]))

        # 'wiggle_scale' is applicable only for Mesh and Wiggle plot.
        _Validators._validate_dependent_argument("wiggle_scale", self.wiggle_scale,
                                                         "kind", None if self.kind not in ['wiggle', 'mesh'] else self.kind, "kind='wiggle' or kind='mesh'")

        # 'wiggle_fill' is applicable only for wiggle plot.
        _Validators._validate_dependent_argument("wiggle_fill", self.wiggle_fill,
                                                     "kind", None if self.kind != "wiggle" else self.kind,  "kind='wiggle'")

        # Argument validations.
        _Validators._validate_function_arguments(arg_info_matrix)

        # 'figdpi' is applicable only for "png" and "jpg" type only.
        _Validators._validate_dependent_argument("figdpi", self.figdpi,
                                                     "figtype", None if self.figtype not in ["png", "jpg"] else self.figtype, "figtype='png' or figtype='jpg'")

        # Argument range check.
        _Validators._validate_argument_range(self.figdpi, "figdpi",
                                             lbound=72, lbound_inclusive=True,
                                             ubound=300, ubound_inclusive=True)

        # Get figure. If user did not pass, create a default one.
        # self.figure = kwargs.get("figure")
        if self.figure is None:
            self.figure = Figure()
        self._figure = self.figure

        self.axis = kwargs.get("ax", None)
        # If axis is not passed, generate a default one.
        if self.axis is None:
            self.axis = Axis(kind=kind, **kwargs)
        else:
            # If user passes axes, i.e., for subplot, add additional params
            # which is passed as kwargs.
            self.axis.set_params(kind=kind, **kwargs)

        # Set the axis data.
        self.axis._set_data(x, y, scale=scale)

        # Add the axis to figure.
        self._figure._add_axis(self.axis)
        self._query = None
        self._plot_image_data = None
        self.heading = kwargs.get("heading")
        _Validators._validate_input_columns_not_empty(self.heading, "heading")
        self.__params = kwargs

    def __eq__(self, other):
        """
        DESCRIPTION:
            Magic method to check if two Plot objects are equal or not.
            If all the associated parameters are same, then two Plot objects
            are equal. Else, they are not equal.

        PARAMETERS:
            other:
                Required Argument.
                Specifies the object of Plot.
                Types: Plot

        RETURNS:
            bool

        RAISES:
            None.

        EXAMPLES:
            >>> _Plot() == _Plot()
        """

        # Check whether x and y are same or not.
        # If two plots to be same, their data and plot parameters to be same.
        if self.x.compile() != other.x.compile():
            return False

        self_y = (self.y, ) if isinstance(self.y, ColumnExpression) else self.y
        other_y = (other.y, ) if isinstance(other.y, ColumnExpression) else other.y

        if len(self_y) != len(other_y):
            return False

        for self_col, other_col in zip(self_y, other_y):
            if self_col.compile() != other_col.compile():
                return False

        # Validate plot parameters are same or not.
        attrs = ["scale", "kind",
                 "figsize", "figtype", "figdpi",
                 "heading", "wiggle_fill", "wiggle_scale",
                 "axis", "figure"]

        for attr in attrs:
            if getattr(self, attr) == getattr(other, attr):
                continue
            else:
                return False

        return True

    def _execute_query(self):
        """
        DESCRIPTION:
            Internal function to execute the Plot Query.

        EXAMPLES:
            >>> _plot._execute_query()
        """
        if self._plot_image_data is None:
            query = self._get_query()

            res = get_connection().execute(text(query))
            self._plot_image_data = res.fetchone().IMAGE

    def show_query(self):
        """
        DESCRIPTION:
            Function to display the query used to generate Plot.

        EXAMPLES:
            # Example - Create a DataFrame and plot the data using DataFrame.plot.
            #           And, display the query.
            # Load the data.
            >>> load_example_data("movavg", "ibm_stock")
            # Create DataFrame.
            >>> ibm_stock = DataFrame("ibm_stock")
            # Display the query.
            >>> plot = ibm_stock.plot(x=ibm_stock.period, y=ibm_stock.stockprice)
            >>> plot.show_query()
        """
        return self._get_query()

    def show(self):
        """
        DESCRIPTION:
            Function to show the plot in the console. The function displays plot
            in either on the console or in a new window based on the option 'inline_plot'.
            * If the console is IPython console, the plot is displayed on the console
              when the option 'inline_plot' is set to True. If the option 'inline_plot'
              is set to False, plot is displayed on new window.
            * If the console is regular Python console and not an IPython console,
              then plot is displayed on a new window irrespective of option 'inline_plot'.
            Note:
                Displaying the plot in a new window requires an additional Python module
                tkinter. One needs to install it manually since teradataml does not install
                it by default.

        EXAMPLES:
            # Example 1 - Generate a line plot and display it in the console.
            >>> load_example_data("movavg", "ibm_stock")
            # Set the option to display the plot in the console.
            >>> from teradataml import configure
            >>> configure.inline_plot = True
            # Create DataFrame.
            >>> ibm_stock = DataFrame("ibm_stock")
            # Generate the plot
            >>> plot = ibm_stock.plot(x=ibm_stock.period, y=ibm_stock.stockprice)
            >>> plot.show()

            # Example 2 - Generate a bar plot and display it in a new window.
            >>> load_example_data("movavg", "ibm_stock")
            # Set the option to display the plot in a new window.
            >>> from teradataml import configure
            >>> configure.inline_plot = False
            # Create DataFrame.
            >>> ibm_stock = DataFrame("ibm_stock")
            # Generate the plot
            >>> plot = ibm_stock.plot(x=ibm_stock.period, y=ibm_stock.stockprice, kind="bar")
            >>> plot.show()
        """
        if self._plot_image_data is None:
            self._execute_query()

        # If user choose for inline plot, then check if Python console supports
        # inline plotting or not. If not supports, then go for outline plot.
        if configure.inline_plot is None:
            try:
                if __IPYTHON__:
                    self._show_inline_plot()
            except NameError:
                    self._show_outline_plot()
        else:
            self._show_inline_plot() if configure.inline_plot else self._show_outline_plot()

    def _repr_html_(self):
        """
        DESCRIPTION:
            Function to display the Plot in for iPython rich display.
        """
        self.show()

    def _show_inline_plot(self):
        """
        DESCRIPTION:
            Internal function to display the plot in the console.

        EXAMPLES:
            # Example - Create a DataFrame and plot the data using DataFrame.plot.
            #           And, display it in same console.
            # Load the data.
            >>> load_example_data("movavg", "ibm_stock")
            # Create DataFrame.
            >>> ibm_stock = DataFrame("ibm_stock")
            # Generate plot and display it in console.
            >>> plot = ibm_stock.plot(x=ibm_stock.period, y=ibm_stock.stockprice)
            >>> plot._show_inline_plot()
        """
        from IPython.display import display as dsp, Image
        dsp(Image(data=self._plot_image_data))

    def _show_outline_plot(self):
        """
        DESCRIPTION:
            Internal function to display the plot in a new window.

        EXAMPLES:
            # Example - Create a DataFrame and plot the data using DataFrame.plot.
            #           And, display it in a new window.
            # Load the data.
            >>> load_example_data("movavg", "ibm_stock")
            # Create DataFrame.
            >>> ibm_stock = DataFrame("ibm_stock")
            # Generate plot and display it in console.
            >>> plot = ibm_stock.plot(x=ibm_stock.period, y=ibm_stock.stockprice)
            >>> plot._show_outline_plot()
        """
        try:
            import tkinter as tk
            root = tk.Tk()
            file_format = self._figure.image_type
            canvas = tk.Canvas(width=self._figure.width, height=self._figure.height)
            canvas.pack()
            img = tk.PhotoImage(data=self._plot_image_data, format=file_format)
            canvas.create_image(0, 0, anchor=tk.NW, image=img)
            root.wm_iconbitmap(os.path.join(UtilFuncs._get_tdml_directory(), "data", "teradata_icon.ico"))
            root.wm_title('teradataml plot')
            root.mainloop()
        except ModuleNotFoundError:
            print("Install module 'tkinter' to display the plot.")

    def _get_query(self):
        """
        DESCRIPTION:
            Internal function to get the query.

        EXAMPLES:
            >>> plot._get_query()
        """

        if not self._query:

            from teradataml.plot.query_generator import PlotQueryGenerator
            _series_spec = []
            _plot_params = []
            func_other_args = {}

            _id = 1
            # Every figure has one or more axis. And, every axis contains
            # plot data and axis parameters.
            for axis in self._figure.get_axes():

                if axis._has_data():
                    _virtual_table, _spec, _plot_param = axis._get_plot_data()
                    _plot_param["ID"] = _id
                    _series_spec.append(_spec)

                    # Update the wiggle parameters.
                    if self.kind.lower() == "wiggle":
                        _wiggle_params = {}
                        if self.wiggle_fill is not None:
                            _wiggle_params["FILL"] =  1 if self.wiggle_fill else 0

                        if self.wiggle_scale is not None:
                            _wiggle_params["SCALE"] =  self.wiggle_scale

                        if _wiggle_params:
                            _plot_param["WIGGLE"] = _wiggle_params

                    _plot_params.append(_plot_param)
                    _id = _id + 1

            dpi = self.__params.get("figdpi") if self.__params.get("figdpi") else self._figure.dpi
            height = self.__params.get("figsize")[1] if self.__params.get("figsize") else self._figure.height
            width = self.__params.get("figsize")[0] if self.__params.get("figsize") else self._figure.width
            type_ = self.__params.get("figtype") if self.__params.get("figtype") else self._figure.image_type

            # teradataml maintains layout as rows and columns. However,
            # SQL maintains it as columns and rows. Hence, reverse the layout.
            layout = self._figure.layout[::-1]
            func_other_args.update({"LAYOUT": layout,
                                    "PLOTS": _plot_params,
                                    "DPI": dpi,
                                    "IMAGE": "'{}'".format(type_),
                                    "WIDTH": width,
                                    "HEIGHT": height
                                    })

            heading = self.heading if self.heading is not None else self._figure.heading
            if heading:
                func_other_args["TITLE"] = "'{}'".format(heading)

            query_generator = PlotQueryGenerator(function_name="TD_PLOT",
                                                 func_input_args=", \n".join(_series_spec),
                                                 func_input_filter_expr_args=None,
                                                 func_output_args=None,
                                                 func_other_args=func_other_args)

            self._query = query_generator._get_display_uaf()

        return self._query

    def save(self, file_name, dir=None):
        """
        Function to save the plot to an image.

        PARAMETERS:
            file_name:
                Required Argument.
                Specifies the name of the image file.
                Note:
                    Do not mention the extension for the filename.
                Types: str

            dir:
                Optional Argument.
                Specifies the absolute path of the directory to store the plot image.
                Types: str

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Example 1: Generate a scatter plot and store it in current directory.
            # Load the data.
            >>> load_example_data("movavg", "ibm_stock")
            # Create DataFrame.
            >>> ibm_stock = DataFrame("ibm_stock")
            # Generate plot.
            >>> plot = ibm_stock.plot(x=ibm_stock.period, y=ibm_stock.stockprice)
            >>> plot.save("example1")

            # Example 2: Generate a scatter plot and store it in temp directory.
            # Load the data.
            >>> load_example_data("movavg", "ibm_stock")
            # Create DataFrame.
            >>> ibm_stock = DataFrame("ibm_stock")
            # Generate plot.
            >>> plot = ibm_stock.plot(x=ibm_stock.period, y=ibm_stock.stockprice)
            >>> # Store in temp directory.
            >>> from tempfile import gettempdir
            >>> plot.save("example2", dir=gettempdir())
        """
        # TODO: Check for the existance of 'dir'.
        type_ = self.__params.get("figtype") if self.__params.get("figtype") else self._figure.image_type
        file_name = "{}.{}".format(file_name, type_)
        if dir:
            file_name = os.path.join(dir, file_name)

        # Execute the query if it is not executed already.
        self._execute_query()

        # Store the image.
        with open(file_name, "wb") as fp:
            fp.write(self._plot_image_data)
