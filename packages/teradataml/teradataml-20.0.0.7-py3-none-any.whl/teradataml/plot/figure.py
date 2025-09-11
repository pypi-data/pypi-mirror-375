# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# Secondary Owner:
#
# This file implements Figure, which is used for plotting. Figure holds all
# the properties related to image such as height, width etc.
#
# ##################################################################

from teradataml.utils.validators import _Validators

class Figure:
    def __init__(self, width=640, height=480, dpi=100, image_type="png", heading=None, layout=(1, 1)):
        """
        Create a new figure for the plot.

        PARAMETERS:
            width:
                Optional Argument.
                Specifies the width of the figure in pixels.
                Default Value: 640
                Notes:
                     * Valid range for "width" is: 400 <= width <= 4096.
                     * Total number of pixels in output image, i.e., the product of "width"
                       and "height" should not exceed 4000000.
                Types: int

            height:
                Optional Argument.
                Specifies the height of the figure in pixels.
                Default Value: 480
                Notes:
                     * Valid range for "height" is: 400 <= height <= 4096.
                     * Total number of pixels in output image, i.e., the product of "width"
                       and "height" should not exceed 4000000.
                Types: int

            dpi:
                Optional Argument.
                Specifies the number of dots per inch for the output image.
                Note:
                    * Valid range for "dpi" is: 72 <= width <= 300.
                Default Value: 100 for PNG and JPG Type image.
                Types: int

            image_type:
                Optional Argument.
                Specifies the type of output image.
                Default Value: PNG
                Permitted Values:
                    * png
                    * jpeg
                    * svg
                Types: str

            heading:
                Optional Argument.
                Specifies the heading for the plot.
                Types: str

            layout:
                Optional Argument.
                Specifies the layout for the plot. Element 1 represents rows
                and element 2 represents columns.
                Default Value: (1, 1)
                Types: tuple

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Example 1: Create a Figure object with height and width as 500
            #            pixels and 600 pixels respectively.
            >>> from teradataml import Figure
            >>> figure = Figure(height=500, width=600)
            >>>
            # Example 2: Create a Figure object with default height and width along
            #            with heading as 'Plot Heading'.
            >>> from teradataml import Figure
            >>> figure = Figure(heading="Plot Heading")
            >>>
        """
        awu_matrix = []
        awu_matrix.append(["height", height, True, int])
        awu_matrix.append(["width", width, True, int])
        awu_matrix.append(["dpi", dpi, True, int])
        awu_matrix.append(["image_type", image_type, True, str, True, ["png", "jpg", "svg"]])
        awu_matrix.append(["heading", heading, True, str, True])
        awu_matrix.append(["layout", layout, True, tuple, True])

        # Validate argument types.
        _Validators._validate_function_arguments(awu_matrix)

        # Validate range.
        _args_ranges = [(height, "height", 400, 4096), (width, "width", 400, 4096), (dpi, "dpi", 72, 300)]
        for _arg, _arg_name, lbound, ubound in _args_ranges:
            _Validators._validate_argument_range(
                _arg, _arg_name, lbound, lbound_inclusive=True, ubound=ubound, ubound_inclusive=True)

        self.__params = {"height": height,
                         "width": width,
                         "dpi": dpi,
                         "image_type": image_type,
                         "heading": heading,
                         "layout": layout
                         }

        self._plot_axis = {}

    def __eq__(self, other):
        """
        DESCRIPTION:
            Magic method to check if two Figure objects are equal or not.
            If all the associated parameters are same, then two Figure objects
            are equal. Else, they are not equal.

        PARAMETERS:
            other:
                Required Argument.
                Specifies the object of Figure.
                Types: Figure

        RETURNS:
            bool

        RAISES:
            None.

        EXAMPLES:
            >>> Figure() == Figure()
        """
        attrs = ["width", "height", "image_type", "dpi", "heading",
                 "layout"]

        for attr in attrs:
            if getattr(self, attr) == getattr(other, attr):
                continue
            else:
                return False

        return True

    @property
    def height(self):
        """
        DESCRIPTION:
            Returns the height of the figure.

        EXAMPLES:
            # Access the height of the figure.
            >>> from teradataml import Figure
            >>> figure = Figure(600)
            >>> figure.height
            600
            >>>
        """
        return self.__params["height"]

    @height.setter
    def height(self, value):
        """
        DESCRIPTION:
            Sets the height of the figure.

        EXAMPLES:
            >>> from teradataml import Figure
            >>> figure = Figure()
            # Example: Set the height for an existing figure object.
            >>> figure.height = 800
            >>> figure.height
            800
            >>>
        """
        awu_matrix = []
        awu_matrix.append(["height", value, True, int])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        _Validators._validate_argument_range(
            value, "height", 400, lbound_inclusive=True, ubound=4096, ubound_inclusive=True)

        self.__params["height"] = value

    @property
    def width(self):
        """
        DESCRIPTION:
            Returns the width of the figure.

        EXAMPLES:
            # Access the width of the figure.
            >>> from teradataml import Figure
            >>> figure = Figure(width=600)
            >>> figure.width
            600
            >>>
        """
        return self.__params["width"]

    @width.setter
    def width(self, value):
        """
        DESCRIPTION:
            Sets the width of the figure.

        EXAMPLES:
            >>> from teradataml import Figure
            >>> figure = Figure()
            # Example: Set the width for an existing figure object.
            >>> figure.width = 800
            >>> figure.width
            800
            >>>
        """
        awu_matrix = []
        awu_matrix.append(["width", value, True, int])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        _Validators._validate_argument_range(
            value, "width", 400, lbound_inclusive=True, ubound=4096, ubound_inclusive=True)

        self.__params["width"] = value

    @property
    def image_type(self):
        """
        DESCRIPTION:
            Returns the type of image for the corresponding figure.

        EXAMPLES:
            # Access the type of image from the Figure object.
            >>> from teradataml import Figure
            >>> figure = Figure()
            >>> figure.image_type
            'png'
            >>>
        """
        return self.__params["image_type"]

    @image_type.setter
    def image_type(self, type_):
        """
        DESCRIPTION:
            Sets the type of the image for the corresponding figure.

        EXAMPLES:
            >>> from teradataml import Figure
            >>> figure = Figure()
            # Example: Set the type of image for existing figure object.
            >>> figure.image_type = "jpeg"
            >>> figure.image_type
            'jpeg'
            >>>
        """
        awu_matrix = []
        awu_matrix.append(["image_type", type_, True, str, True, ["png", "jpeg", "svg"]])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        self.__params["image_type"] = type_

    @property
    def dpi(self):
        """
        DESCRIPTION:
            Returns the dots per inch for the corresponding figure.

        EXAMPLES:
            # Access the dpi for the Figure object.
            >>> from teradataml import Figure
            >>> figure = Figure()
            >>> figure.dpi
            100
            >>>
        """
        return self.__params["dpi"]

    @dpi.setter
    def dpi(self, value):
        """
        DESCRIPTION:
            Sets the dots per inch for the corresponding figure.

        EXAMPLES:
            # Access the dpi for the Figure object.
            >>> from teradataml import Figure
            >>> figure = Figure()
            >>> figure.dpi = 120
            >>> figure.dpi
            120
            >>>
        """
        awu_matrix = []
        awu_matrix.append(["dpi", value, True, int])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        _Validators._validate_argument_range(
            value, "dpi", 72, lbound_inclusive=True, ubound=300, ubound_inclusive=True)

        self.__params["dpi"] = value

    @property
    def heading(self):
        """
        DESCRIPTION:
            Returns the heading for the corresponding figure.

        EXAMPLES:
            # Access the heading for the Figure object.
            >>> from teradataml import Figure
            >>> figure = Figure(heading="Plot Heading")
            >>> figure.heading
            'Plot Heading'
            >>>
        """
        return self.__params["heading"]

    @heading.setter
    def heading(self, value):
        """
        DESCRIPTION:
            Sets the heading for the corresponding figure.

        EXAMPLES:
            # Set the heading for the Figure object.
            >>> from teradataml import Figure
            >>> figure = Figure()
            >>> figure.heading = "Plot Heading"
            >>> figure.heading
            'Plot Heading'
            >>>
        """

        awu_matrix = []
        awu_matrix.append(["heading", value, True, str, True])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        self.__params["heading"] = value

    @property
    def layout(self):
        """
        DESCRIPTION:
            Returns the layout for the corresponding figure.

        EXAMPLES:
            # Access the layout for the Figure object.
            >>> from teradataml import Figure
            >>> figure = Figure()
            >>> figure.layout
            (1, 1)
            >>>
        """
        return self.__params["layout"]

    @layout.setter
    def layout(self, value):
        """
        DESCRIPTION:
            Sets the layout for the corresponding figure.

        EXAMPLES:
            # Set the layout for the Figure object.
            >>> from teradataml import Figure
            >>> figure = Figure()
            >>> figure.layout = (1, 3)
            >>> figure.layout
            (1, 3)
            >>>
        """
        awu_matrix = []
        awu_matrix.append(["layout", value, True, tuple, True])

        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        self.__params["layout"] = value

    def _add_axis(self, axis):
        """
        DESCRIPTION:
            Internal function to add the axis to the Figure object.

        PARAMETERS:
            axis:
                Required Argument.
                Specifies the object of Axis.
                Types: Axis

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            self._add_axis(axis)
        """
        self._plot_axis[axis.position] = axis

    def get_axes(self):
        """
        DESCRIPTION:
            Function to get the all the axes which are associated with the
            corresponding Figure.

        RETURNS:
            An iterator. Every element of iterator is an Axis or SubAxis object.

        RAISES:
            None.

        EXAMPLES:
            >>> from teradataml import Figure
            >>> figure = Figure()
            >>> axis = list(figure.get_axes())
        """
        for axis in self._plot_axis.values():
            yield axis
