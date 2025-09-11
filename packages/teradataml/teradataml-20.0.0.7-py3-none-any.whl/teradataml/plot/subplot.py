# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# Secondary Owner:
#
# This file implements subplots function, which is used for sub-plotting.
#
# ##################################################################
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.plot.figure import Figure
from teradataml.plot.axis import AxesSubplot
from teradataml.utils.validators import _Validators



def subplots(nrows=None, ncols=None, grid=None):
    """
    DESCRIPTION:
        Function to create a figure and a set of subplots. The function
        makes it convenient to create common layouts of subplots, including
        the enclosing figure object.

    PARAMETERS:
        nrows:
            Required when "grid" is not used, optional otherwise.
            Specifies the number of rows of the subplot grid.
            Notes:
                 * Provide either "grid" argument or "nrows" and "ncols" arguments.
                 * "nrows" and "ncols" are mutually inclusive.
            Types: int

        ncols:
            Optional Argument.
            Specifies the number of columns of the subplot grid.
            Notes:
                 * Provide either "grid" argument or "nrows" and "ncols" arguments.
                 * "nrows" and "ncols" are mutually inclusive.
            Types: int

        grid:
            Required when "nrows" and "ncols" are not used, optional otherwise.
            Specifies grid for subplotting. The argument is useful when one or more
            subplot occupies more than one unit of space in figure.
            For example:
                "grid" {(1,1): (1, 1), (1,2): (1,1), (2, 1): (1, 2)} makes 3 subplots
                in a figure.
                * The first subplot which is positioned at first row and first column
                  occupies one row and one column in the figure.
                * The second subplot which is positioned at first row and second column
                  occupies one row and one column in the figure.
                * The third subplot which is positioned at second row and first column
                  occupies one row and two columns in the figure. Thus, the third subplot
                  occupies the entire second row of subplot.
            Notes:
                 * Provide either "grid" argument or "nrows" and "ncols" arguments.
                 * "nrows" and "ncols" are mutually inclusive.
            Types: dict, both keys and values are tuples.

    RETURNS:
        tuple, with two elements. First element represents the object of Figure and
        second element represents list of objects of AxesSubplot.
        Note:
            The default width and height in figure object is 640 and 480 pixels
            respectively. However, in case of subplotting, the default width and
            height is 1920 and 1080 respectively.

    RAISES:
        TeradataMlException

    EXAMPLES:
        # Example 1: This example creates a figure with subplot with scatter plots.

        # Load example data.
        >>> load_example_data("uaf", "house_values")

        # Create teradataml DataFrame objects.
        >>> house_values = DataFrame("house_values")

        # Import subplots.
        >>> from teradataml subplots

        # This will help to create a figure with 2 subplots in 1 row.
        # fig and axes is passed to plot().
        >>> fig, axes = subplots(nrows=1, ncols=2)

        # Print the DataFrame.
        >>> print(house_values)
                               TD_TIMECODE  house_val    salary  mortgage
        cityid
        33      2020-07-01 08:00:00.000000    66000.0   29000.0     0.039
        33      2020-04-01 08:00:00.000000    80000.0   22000.0     0.029
        33      2020-05-01 08:00:00.000000   184000.0   49000.0     0.030
        33      2020-06-01 08:00:00.000000   320000.0  112000.0     0.017
        33      2020-09-01 08:00:00.000000   195000.0   72000.0     0.049
        33      2020-10-01 08:00:00.000000   134000.0   89000.0     0.045
        33      2020-11-01 08:00:00.000000   198000.0   49000.0     0.052
        33      2020-08-01 08:00:00.000000   144000.0   74000.0     0.034
        33      2020-03-01 08:00:00.000000   220000.0   76000.0     0.035
        33      2020-02-01 08:00:00.000000   144000.0   50000.0     0.040

        # Create plot with house_val, salary and salary and mortgage.
        >>> plot = house_values.plot(x=house_values.house_val, y=house_values.salary,
                                  ax=axes[0], figure=fig, kind="scatter",
                                  xlim=(100000,250000), ylim=(25000, 100000),
                                  title="Scatter plot of House Val v/s Salary",
                                  color="green")
        >>> plot = house_values.plot(x=house_values.salary, y=house_values.mortgage,
                                  ax=axes[1], figure=fig, kind="scatter",
                                  title="Scatter plot of House Val v/s Mortgage",
                                  color="red")

        # Show the plot.
        >>> plot.show()

        Example 2:
        # Subplot with grid. This will generate a figure with 2 subplots in first row
        # first column and second column respectively and 1 subplot in second row.
        >>> fig, axes = subplots(grid = {(1, 1): (1, 1), (1, 2): (1, 1),
                                         (2, 1): (1, 2)})

        # Print the DataFrame.
        >>> print(house_values)
                               TD_TIMECODE  house_val    salary  mortgage
        cityid
        33      2020-07-01 08:00:00.000000    66000.0   29000.0     0.039
        33      2020-04-01 08:00:00.000000    80000.0   22000.0     0.029
        33      2020-05-01 08:00:00.000000   184000.0   49000.0     0.030
        33      2020-06-01 08:00:00.000000   320000.0  112000.0     0.017
        33      2020-09-01 08:00:00.000000   195000.0   72000.0     0.049
        33      2020-10-01 08:00:00.000000   134000.0   89000.0     0.045
        33      2020-11-01 08:00:00.000000   198000.0   49000.0     0.052
        33      2020-08-01 08:00:00.000000   144000.0   74000.0     0.034
        33      2020-03-01 08:00:00.000000   220000.0   76000.0     0.035
        33      2020-02-01 08:00:00.000000   144000.0   50000.0     0.040

        # Create plot with house_val, salary and salary and mortgage.
        >>> plot = house_values.plot(x=house_values.house_val, y=house_values.salary,
                                  ax=axes[0], figure=fig, kind="scatter",
                                  title="Scatter plot of House Val v/s Salary",
                                  color="green")
        >>> plot = house_values.plot(x=house_values.salary, y=house_values.mortgage,
                                  ax=axes[1], figure=fig, kind="scatter",
                                  title="Scatter plot of Salary v/s Mortgage",
                                  color="red")
        >>> plot = house_values.plot(x=house_values.salary, y=house_values.mortgage,
                                  ax=axes[2], figure=fig, kind="scatter",
                                  title="Scatter plot of House Val v/s Mortgage",
                                  color="blue")
        # Show the plot.
        >>> plot.show()
    """
    # Create the arg info matrix.
    awu_matrix = []
    awu_matrix.append(["nrows", nrows, True, int])
    awu_matrix.append(["ncols", ncols, True, int])
    awu_matrix.append(["grid", grid, True, (dict)])

    # Validate argument types.
    _Validators._validate_function_arguments(awu_matrix)

    # If grid is None, only nrows or ncols cannot be specified.
    # Both nrows and ncols should be specified.
    if grid is None:
        if (nrows is not None and ncols is None) or \
                (nrows is None and ncols is not None):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.MUST_PASS_ARGUMENT, "nrows", "ncols"),
                MessageCodes.MUST_PASS_ARGUMENT)
    else:
        # Both grid, nrows and ncols cannot be specified.
        if any(x is not None for x in [nrows, ncols]):
            raise TeradataMlException(
                Messages.get_message(MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT,
                                     "nrows' and 'ncols", "grid"),
                MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)

    # Either grid or nrows/ncols must be specified.
    if all(x is not None for x in [nrows, ncols, grid]):
        raise TeradataMlException(
            Messages.get_message(MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT,
                                 "nrows' and 'ncols", "grid"),
            MessageCodes.EITHER_THIS_OR_THAT_ARGUMENT)

    _sub_axis = []
    # Since it is a subplot, make sure to provide a figure with larger size.
    figure = Figure(width=1920, height=1080)
    # grid is a dictionary, with keys as position and values as span. Both
    # represents tuples.
    if grid is not None:
        _min, _max = 1, 1
        for position, span in grid.items():
            _axis = AxesSubplot(position=position, span=span)
            figure._add_axis(_axis)
            _sub_axis.append(_axis)

            # Layout should be mix/max of position and span elements.
            _min = max(_min, position[0], span[0])
            _max = max(_max, position[1], span[1])

        _layout = (_min, _max)

    else:
        _layout = (nrows, ncols)
        for row in range(1, nrows+1):
            for col in range(1, ncols+1):
                position = (row, col)
                _axis = AxesSubplot(position=(row, col))
                figure._add_axis(_axis)
                _sub_axis.append(_axis)
    figure.layout = _layout
    return figure, _sub_axis
