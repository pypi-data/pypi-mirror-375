# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# Secondary Owner:
#
# This file implements Query generator for TD_Plot function.
# TD_PLOT SQL mainly follows UAF syntax however it needs
# additional elements. So, using UAFQueryGenerator as a parent class
# PlotQueryGenerator is devoloped to construct SQL for TD_Plot.
#
# ##################################################################

from teradataml.analytics.analytic_query_generator import UAFQueryGenerator

class PlotQueryGenerator(UAFQueryGenerator):

    def _get_arg_expressions(self, arg, value):
        """
        Internal function to generate the parameterised SQL clause, parameterised SQL
        value and non parameterised SQL clause for a given argument and it's value.

        PARAMETERS:
            arg:
                Required Argument.
                Specifies the name of SQL clause.
                Types: str

            value:
                Required Argument.
                Specifies the value of SQL Clause. If the type of this argument is a dictionary,
                then the same function will be called recursively to generate the expression.
                Types: int OR str OR float OR dict

        RETURNS:
            tuple, with 3 elements.
            element 1 is a string, represents the parameterised SQL clause,
            element 2 is a list, represents the values for parameterised SQL clause.
            element 3 is a string, represents the non parameterised SQL clause.

        RAISES:
            None.

        EXAMPLES:
            self.__get_other_arg_expressions("arg1", {"arg2": {"arg3": "value3"}}})
            # Output is as shown in example in description.
        """
        if value is None:
            return "", [], ""

        if isinstance(value, (str, int, float)):
            return "", [], "{}({})".format(arg, value)

        if isinstance(value, tuple):
            return "", [], "{}({})".format(arg, ", ".join(map(str, value)))

        # Loop through the dictionary/list and call the same function again.
        _np_sql_clauses, seperator = "", ""

        # For both list and dictionary, the function should be called recursively to
        # construct the SQL. However, for list, there wont be any key. So, generate a
        # iterator in such a way, it should give two elements - for list, the element
        # 1 should be empty string since list do not have any key and element 2 should
        # be elements of list. Where as for dict, element 1 should be a key and element
        # 2 should be value of key.
        _iter = (("", i) for i in value) if isinstance(value, list) else value.items()

        for _arg, _value in _iter:
            _, _, _np_sql = self._get_arg_expressions(_arg, _value)

            _np_sql_clauses = _np_sql_clauses + seperator + _np_sql

            # After the first element, every other element should pad with
            # previous elements with a comma(,).
            seperator = ", "

        # If value is a list, append the parent with square brackets.
        # Else, append the parent with regular brackets.
        _s = "{}[{}]"  if isinstance(value, list) else "{}({})"
        # TODO: If possible, format the SQL with spaces and new lines.
        return "", [], _s.format(arg, _np_sql_clauses)
