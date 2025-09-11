def NPath(data1=None, mode=None, pattern=None, symbols=None, result=None, filter=None,
          data2=None, data3=None, data4=None, data5=None, data6=None, data7=None,
          data8=None, data9=None, data10=None, **generic_arguments):
    """
    DESCRIPTION:
    The NPath() function scans a set of rows, looking for patterns that you
    specify. For each set of input rows that matches the pattern, NPath
    produces a single output row. The function provides a flexible
    pattern-matching capability that lets you specify complex patterns in
    the input data and define the values that are output for each matched
    input set.


    PARAMETERS:
        data1:
            Required Argument.
            Specifies the input teradataml DataFrame containing the input data set.
            Types: teradataml DataFrame

        mode:
            Required Argument.
            Specifies the pattern-matching mode:
                * OVERLAPPING:
                    The function finds every occurrence of the pattern in
                    the partition, regardless of whether it is part of a previously
                    found match. Therefore, one row can match multiple symbols in a
                    given matched pattern.
                * NONOVERLAPPING:
                    The function begins the next pattern search at the
                    row that follows the last pattern match. This is the default
                    behavior of many commonly used pattern matching utilities, including
                    the UNIX grep utility.
            Permitted Values: OVERLAPPING, NONOVERLAPPING
            Types: str

        pattern:
            Required Argument.
            Specifies the pattern for which the function searches. You compose
            pattern with the symbols that you define in the symbols argument,
            operators, and parentheses.
            When patterns have multiple operators, the function applies
            them in order of precedence, and applies operators of equal
            precedence from left to right. To specify that a subpattern must
            appear a specific number of times, use the Range-Matching
            Feature.
            The basic pattern operators in decreasing order of precedence
                "pattern", "pattern.", "pattern?", "pattern*", "pattern+",
                "pattern1.pattern2", "pattern1|pattern2", "^pattern", "pattern$"
            To force the function to evaluate a subpattern first, enclose it in parentheses.
            Example:
                ^A.(B|C)+.D?.X*.A$
                The preceding pattern definition matches any set of rows
                whose first row starts with the definition of symbol A,
                followed by a non-empty sequence of rows, each of which
                meets the definition of either symbol B or C, optionally
                followed by one row that meets the definition of symbol D,
                followed by any number of rows that meet the definition of
                symbol X, and ending with a row that ends with the definition of symbol A.
            You can use parentheses to define precedence rules. Parentheses are
            recommended for clarity, even where not strictly required.
            Types: str

        symbols:
            Required Argument.
            Specifies the symbols that appear in the values of the pattern and
            result arguments. The col_expr is an expression whose value is a
            column name, symbol is any valid identifier, and symbol_predicate is
            a SQL predicate (often a column name).
            For example, the 'symbols' argument for analyzing website visits might
            look like this:
                Symbols
                (
                 pagetype = "homepage" AS H,
                 pagetype <> "homepage" AND  pagetype <> "checkout" AS PP,
                 pagetype = "checkout" AS CO
                )
            The symbol is case-insensitive; however, a symbol of one or two
            uppercase letters is easy to identify in patterns.
            If col_expr represents a column that appears in multiple input
            DataFrames, then you must qualify the ambiguous column name with
            the SQL name corresponding to it's teradataml DataFrame name.
            For example:
                Symbols
                (
                 input1.pagetype = "homepage" AS H,
                 input1.pagetype = "thankyou" AS T,
                 input2.adname = "xmaspromo" AS X,
                 input2.adname = "realtorpromo" AS R
                )
            The mapping from teradataml DataFrame name to its corresponding SQL name
            is as shown below:
                * data1: input1
                * data2: input2
                * data3: input3
            You can create symbol predicates that compare a row to a previous
            or subsequent row, using a LAG or LEAD operator.
            LAG Expression Syntax:
                { current_expr operator LAG (previous_expr, lag_rows [, default]) |
                LAG (previous_expr, lag_rows [, default]) operator current_expr }
            LAG and LEAD Expression Rules:
                • A symbol definition can have multiple LAG and LEAD expressions.
                • A symbol definition that has a LAG or LEAD expression cannot have an OR operator.
                • If a symbol definition has a LAG or LEAD expression and the input
                  is not a table, you must create an alias of the input query.
            Types: str OR list of Strings (str)

        result:
            Required Argument.
            Specifies the output columns. The col_expr is an expression whose value
            is a column name; it specifies the values to retrieve from the
            matched rows. The function applies aggregate function to these
            values.
            Supported aggregate functions:
                • SQL aggregate functions are [AVG, COUNT, MAX, MIN, SUM].
                • ML Engine nPath sequence aggregate functions.
            The function evaluates this argument once for every matched pattern
            in the partition (that is, it outputs one row for each pattern match).
            Note:
                For col_expr representing a column that appears in multiple input
                DataFrames, you must qualify the ambiguous column name with the SQL
                name corresponding to it's teradataml DataFrame name. Please see the
                description of the 'symbols' parameter for the mapping from teradataml
                DataFrame name to the SQL name.
            Types: str OR list of Strings (str)

        filter:
            Optional Argument.
            Specifies filters to impose on the matched rows. The function
            combines the filter expressions using the AND operator.
            The filter_expression syntax is:
                symbol_expression comparison_operator symbol_expression
            The two symbol expressions must be type-compatible.
            The symbol_expression syntax is:
                { FIRST | LAST }(column_with_expression OF [ANY](symbol[,...]))
            The column_with_expression cannot contain the operator AND or OR, and
            all its columns must come from the same input. If the function has
            multiple inputs, then column_with_expression and symbol must come
            from the same input.
            The comparison_operator is either <, >, <=, >=, =, or <>.
            Note:
                For column_with_expression representing a column that appears in
                multiple input DataFrames, you must qualify the ambiguous column name with
                the SQL name corresponding to it's teradataml DataFrame name. Please see
                the description of the 'symbols' parameter for the mapping from teradataml
                DataFrame name to the SQL name.
            Types: str OR list of Strings (str)

        data2:
            Optional Arguments.
            Specifies the additional optional input teradataml DataFrames containing the input data.
            Types: teradataml DataFrame

        data3:
            Optional Arguments.
            Specifies the additional optional input teradataml DataFrames containing the input data.
            Types: teradataml DataFrame

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or not.
                    When set to True, results are persisted in a table; otherwise, results
                    are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table or not.
                    When set to True, results are stored in a volatile table, otherwise not.
                    Default Value: False
                    Types: boolean

            Function allows the user to partition, hash, order or local order the input
            data. These generic arguments are available for each argument that accepts
            teradataml DataFrame as input and can be accessed as:
                * "<input_data_arg_name>_partition_column" accepts str or list of str (Strings)
                * "<input_data_arg_name>_hash_column" accepts str or list of str (Strings)
                * "<input_data_arg_name>_order_column" accepts str or list of str (Strings)
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if the underlying SQL Engine
                function supports, else an exception is raised.

    RETURNS:
        Instance of NPath.
        Output teradataml DataFrames can be accessed using attribute
        references, such as NPathObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        # Load example data.
        load_example_data("NPath",["impressions","clicks2", "tv_spots", "clickstream"])

        # Create input teradataml dataframes.
        impressions = DataFrame.from_table("impressions")
        clicks2 = DataFrame.from_table("clicks2")
        tv_spots = DataFrame.from_table("tv_spots")
        clickstream = DataFrame.from_table("clickstream")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Search for pattern '(imp|tv_imp)*.click' in the provided
        #           data(impressions, clicks2, tv_spots).

        # Run NPath function with the required patterns to get the rows which
        # have specified pattern. Rows that matches the pattern.
        obj = NPath(data1=impressions,
                    data1_partition_column='userid',
                    data1_order_column='ts',
                    data2=clicks2,
                    data2_partition_column='userid',
                    data2_order_column='ts',
                    data3=tv_spots,
                    data3_partition_column='ts',
                    data3_order_column='ts',
                    result=['COUNT(* of imp) as imp_cnt','COUNT(* of tv_imp) as tv_imp_cnt'],
                    mode='nonoverlapping',
                    pattern='(imp|tv_imp)*.click',
                    symbols=['true as imp','true as click','true as tv_imp'])

        # Print the result DataFrame.
        print(obj.result)

        # Example 2: Search for pattern 'home.clickview*.checkout' in the provided
        #           data set clickstream.

        # Run NPath function with the required patterns to get the rows which
        # has specified pattern and filter the rows with the filter,
        # where filter and result have ML Engine nPath sequence aggregate functions
        # like 'FIRST', 'COUNT' and 'LAST'.
        obj = NPath(data1=clickstream,
                    data1_partition_column='userid',
                    data1_order_column='clicktime',
                    result=['FIRST(userid of ANY(home, checkout, clickview)) AS userid',
                            'FIRST (sessionid of ANY(home, checkout, clickview)) AS sessioinid',
                            'COUNT (* of any(home, checkout, clickview)) AS cnt',
                            'FIRST (clicktime of ANY(home)) AS firsthome',
                            'LAST (clicktime of ANY(checkout)) AS lastcheckout'],
                    mode='nonoverlapping',
                    pattern='home.clickview*.checkout',
                    symbols=["pagetype='home' AS home",
                             "pagetype <> 'home' AND pagetype <> 'checkout' AS clickview",
                             "pagetype='checkout' AS checkout"],
                    filter = "FIRST (clicktime OF ANY (home)) <"
                             "FIRST (clicktime of any(checkout))")

        # Print the result DataFrame.
        print(obj.result)
    """