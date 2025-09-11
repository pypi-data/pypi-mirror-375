"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements the Row for teradataml DataFrame.
"""


class _Row:
    """ Class for representing a row in teradataml DataFrame. """
    def __init__(self, columns, values):
        """
        DESCRIPTION:
            Constructor for creating Row object.

        PARAMETERS:
            columns:
                Required Argument.
                Specifies the name(s) of the columns for the corresponding
                teradataml DataFrame.
                Types: list

            values:
                Required Argument.
                Specifies the corresponding values for the columns.
                Types: list

        RAISES:
            None

        EXAMPLES:

            # Example 1: Create a Row for columns 'a', 'b', 'c' and corresponding values 'p', 'q', 'r'.
            >>> from teradataml.utils.utils import Row
            >>> row = Row(columns=['a', 'b', 'c'], values=['p', 'q', 'r'])
        """
        self.__data = dict(zip(columns, values))
        self.__values = values

        # Create a function _asdict similar to namedtuple._asdict
        self._asdict = lambda: self.__data

    def __getattr__(self, item):
        """
        DESCRIPTION:
            Retrieve the corresponding value for column
            using dot(.) notation.

        PARAMETERS:
            item:
                Required Argument.
                Specifies name of the column.
                Types: str

        RETURNS:
            str OR int OR float OR datetime

        EXAMPLES:
            >>> row = Row(columns=['a', 'b', 'c'], values=['p', 'q', 'r'])
            >>> row.a
        """
        # Check if item is a valid column or not. If yes, proceed. Otherwise raise error.
        if item in self.__data:
            return self.__data[item]

        raise AttributeError("'Row' object has no attribute '{}'".format(item))

    def __getitem__(self, item):
        """
        DESCRIPTION:
            Retrieve the corresponding value for column
            using square bracket([]) notation.

        PARAMETERS:
            item:
                Required Argument.
                Specifies the name or the index of the column.
                Types: str

        RETURNS:
            str OR int OR float OR datetime

        EXAMPLES:
            >>> row = Row(columns=['a', 'b', 'c'], values=['p', 'q', 'r'])
            >>> row['a']
            'p'
            >>> row[1]
            'q'
        """
        # User's can retrieve the value of a column either by using name of the
        # column or by index of column position.
        if isinstance(item, int):

            # Check if sourced index is valid or not.
            if item >= len(self.__values):
                raise IndexError("tuple index out of range")

            return self.__values[item]

        # If it is a string, retrieve it from here. Otherwise, raise error.
        if item in self.__data:
            return self.__data[item]

        raise AttributeError("'Row' object has no attribute '{}'".format(item))

    def __dir__(self):
        """
        DESCRIPTION:
            Provide the suggestions for column names.

        PARAMETERS:
            None

        RETURNS:
            tuple

        EXAMPLES:
            >>> row = Row(columns=['a', 'b', 'c'], values=['p', 'q', 'r'])
            >>> dir(row)
        """
        return tuple(col for col in self.__data)

    def __str__(self):
        """
        DESCRIPTION:
            Returns the string representation of _Row object.

        PARAMETERS:
            None

        RETURNS:
            tuple

        EXAMPLES:
            >>> row = Row(columns=['a', 'b', 'c'], values=['p', 'q', 'r'])
            >>> print(row)
        """
        return self.__repr__()

    def __repr__(self):
        """
        DESCRIPTION:
            Returns the string representation of _Row object.

        PARAMETERS:
            None

        RETURNS:
            tuple

        EXAMPLES:
            >>> row = Row(columns=['a', 'b', 'c'], values=['p', 'q', 'r'])
            >>> print(row)
        """
        columns_values = ", ".join(("{}={}".format(col, repr(val)) for col, val in self.__data.items()))
        return "Row({})".format(columns_values)