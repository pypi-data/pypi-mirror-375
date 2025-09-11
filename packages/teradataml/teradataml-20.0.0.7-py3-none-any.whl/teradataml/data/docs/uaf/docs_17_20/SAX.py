def SAX(data=None, data_filter_expr=None, window_type='GLOBAL', 
        output_type='STRING', mean=None, std_dev=None, 
        window_size=None, output_frequency=1, 
        points_per_symbol=1, symbols_per_window=1, 
        alphabet_size=4, bitmap_level=2, code_stats=0, 
        breakpoints=None, 
        output_fmt_index_style="NUMERICAL_SEQUENCE", 
        **generic_arguments):
    """
    DESCRIPTION:
        SAX() function uses Piecewise Aggregate Approximation (PAA) and 
        transform a timeseries into sequence of symbols.
        The symbols can be characters, string, and bitmap.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the time series whose value can be REAL or MULTIVAR_REAL.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        window_type:
            Optional Argument.
            Specifies the window type used in the SAX transformation.
            Default Value: GLOBAL
            Permitted Values: GLOBAL, SLIDING
            Types: str

        output_type:
            Optional Argument.
            Specifies the output format of the result.
            Default Value: STRING
            Permitted Values: STRING, BITMAP, O_CHARS
            Types: str

        mean:
            Optional Argument.
            Specifies the global mean values that used to
            calculate the SAX code for every partition.
            Note:
                * If "mean" not specified, the function calculates the mean values
                  for every partition.
                * If "mean" specifies a single value but there are multiple payloads,
                  the specified value will apply to all payloads.
                * If "mean" specifies multiple values, each value will be 
                  applied to its corresponding payload.
            Types: int, list of int, float, list of float

        std_dev:
            Optional Argument.
            Specifies the global standard deviation values that used to
            calculate the SAX code for every partition.
            Note:
                * If "std_dev" not specified, the function calculates the standard
                  deviation values for every partition.
                * If "std_dev" specifies a single value but there are multiple payloads,
                  the specified value will apply to all payloads.
                * If "std_dev" specifies multiple values, each value will be
                  applied to its corresponding payload.
            Types: int, list of int, float, list of float

        window_size:
            Optional Argument, Required if "window_type" is SLIDING.
            Specifies the size of the window used in the SAX
            transformation. Maximum value is 64000.
            Types: int

        output_frequency:
            Optional Argument.
            Specifies the number of data points that the window slides
            between successive outputs.
            Note:
                * "output_frequency" is valid only for SLIDING "window_type".
            Default Value: 1
            Types: int

        points_per_symbol:
            Optional Argument.
            Specifies the number of data points to be converted to one SAX
            symbol.
            Note:
                * "points_per_symbol" is valid for GLOBAL "window_type".
            Default Value: 1
            Types: int

        symbols_per_window:
            Optional Argument.
            Specifies the number of SAX symbols to be generated for each
            window.
            Note:
                * "symbols_per_window" is valid for SLIDING "window_type".
            Default Value: 1
            Types: int

        alphabet_size:
            Optional Argument.
            Specifies the number of symbols in the SAX alphabet. 
            The alphabet consists of letters from 'a' to 't'.
            The size of the alphabet must be less than or equal to 20 
            and greater than or equal to 2.
            Default Value: 4
            Types: int

        bitmap_level:
            Optional Argument.
            Specifies the level of the bitmap. The bitmap level
            determines the number of consecutive symbols to be
            converted to one symbol on a bitmap. 
            "bitmap_level" must be greater than or equal to 1 and less than or equal to 4.
            Default Value: 2
            Types: int

        code_stats:
            Optional Argument.
            Specifies whether to print the mean and standard deviation
            Default Value: 0
            Types: int

        breakpoints:
            Optional Argument.
            Specifies the breakpoints to form the SAX code based on "data".
            Types: int, list of int, float, list of float

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Permitted Values: NUMERICAL_SEQUENCE
            Default Value: NUMERICAL_SEQUENCE
            Types: str

        **generic_arguments:
            Specifies the generic keyword arguments of UAF functions.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the
                    function in a table or not. When set to True,
                    results are persisted in a table; otherwise,
                    results are garbage collected at the end of the
                    session.
                    Note that, when UAF function is executed, an 
                    analytic result table (ART) is created.
                    Default Value: False
                    Types: bool

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the
                    function in a volatile ART or not. When set to
                    True, results are stored in a volatile ART,
                    otherwise not.
                    Default Value: False
                    Types: bool

                output_table_name:
                    Optional Argument.
                    Specifies the name of the table to store results. 
                    If not specified, a unique table name is internally 
                    generated.
                    Types: str

                output_db_name:
                    Optional Argument.
                    Specifies the name of the database to create output 
                    table into. If not specified, table is created into 
                    database specified by the user at the time of context 
                    creation or configuration parameter. Argument is ignored,
                    if "output_table_name" is not specified.
                    Types: str


    RETURNS:
        Instance of SAX.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as SAX_obj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            1. result


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage, before importing the
        #        function in user space.
        #     2. User can import the function, if it is available on
        #        Vantage user is connected to.
        #     3. To check the list of UAF analytic functions available
        #        on Vantage user connected to, use
        #        "display_analytic_functions()".

        # Check the list of available UAF analytic functions.
        display_analytic_functions(type="UAF")

        # Import function SAX.
        from teradataml import SAX

        # Load the example data.
        load_example_data("sax", ["finance_data4"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("finance_data4")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="id",
                                  row_index="period",
                                  row_index_style="SEQUENCE",
                                  payload_field=["expenditure", "income", "investment"],
                                  payload_content="MULTIVAR_REAL")

        # Example 1: Execute SAX() function on the TDSeries to transform the
        #            time series into sequence of symbols using GLOBAL window.
        uaf_out = SAX(data=data_series_df, 
                      window_type='GLOBAL', 
                      output_type='STRING', 
                      mean=[2045.16666, 2387.41666,759.083333], 
                      std_dev=[256.612489,317.496587,113.352594], 
                      output_frequency=1, 
                      points_per_symbol=2,
                      alphabet_size=10,
                      code_stats=True)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Execute SAX() function on the TDSeries to transform the
        #            time series into sequence of symbols using SLIDING window.
        uaf_out1 = SAX(data=data_series_df, 
                       window_type='SLIDING', 
                       window_size=4,
                       symbols_per_window=5, 
                       code_stats=True)

        # Print the result DataFrame.
        print(uaf_out1.result)
    
    """
    