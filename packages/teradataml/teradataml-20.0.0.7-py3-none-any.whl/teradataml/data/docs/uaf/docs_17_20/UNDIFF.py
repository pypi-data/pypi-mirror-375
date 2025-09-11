def UNDIFF(data1=None, data1_filter_expr=None, data2=None,
           data2_filter_expr=None, lag=None, differences=None,
           seasonal_multiplier=None, initial_values=None,
           input_fmt_input_mode=None, **generic_arguments):
    """
    DESCRIPTION:
        The UNDIFF() function is the reverse of the DIFF() function.
        It takes in a previously differenced series processed by DIFF(),
        and produces the original series that existed prior to the differencing.

    PARAMETERS:
        data1:
            Required Argument.
            Specifies the differenced series or TDAnalyticResult
            object created on the output of DIFF() function.
            Types: TDSeries, TDAnalyticResult

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Optional Argument.
            Specifies the original series.
            This series is needed to reconstruct the series completely.
            If the series was differenced with a lag of 1, then the initial
            value of the original series must be present for a full
            reconstruction. With a lag of 2, the initial 2 values must be present,
            and so on. If the series was differenced multiple times, then the
            initial values of the intermediate steps must be given.
            Types: TDSeries

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        lag:
            Required Argument.
            Specifies the lag between series elements.
            Value must be greater than or equal to 0.
            Types: int

        differences:
            Required Argument.
            Specifies the difference between time series elements Yt and Yt-lag.
            Value must be greater than or equal to 0.
            Types: int

        seasonal_multiplier:
            Required Argument.
            Specifies whether time series is seasonal.
            When set to 0, indicates time series is nonseasonal,
            otherwise indicates seasonal time series.
            Value must be greater than or equal to 0.
            Types: int

        initial_values:
            Optional Argument.
            Specifies the starting values for the undifferencing operation.
            Types: int, list of int, float OR list of float

        input_fmt_input_mode:
            Optional Argument.
            Specifies the input mode supported by the function.
            Permitted Values: MANY2ONE, ONE2ONE, MATCH
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
        Instance of UNDIFF.
        Output teradataml DataFrames can be accessed using attribute
        references, such as UNDIFF_obj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            1. result

    RAISES:
        TeradataMlException, TypeError, ValueError

    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        # Check the list of available UAF analytic functions.
        display_analytic_functions(type="UAF")

        # Load the example data.
        load_example_data("uaf", ["ocean_buoy2"])

        # Create teradataml DataFrame objects.
        data = DataFrame.from_table("ocean_buoy2")

        # Create teradataml TDSeries object.
        data_series = TDSeries(data=data,
                               id="buoy_id",
                               row_index="n_seq_no",
                               row_index_style= "SEQUENCE",
                               payload_field="magnitude1",
                               payload_content="REAL")

        # Transform time series into a differenced time series.
        uaf_out_1 = DIFF(data=data_series,
                         lag=1,
                         differences=1,
                         seasonal_multiplier=0)

        # Example 1 : Retrieve the original series that existed prior to the differencing
        #             by taking the differenced series processed by DIFF() as input.

        # Create teradataml TDSeries over the output generated from DIFF.
        data_series_1 = TDSeries(data=uaf_out_1.result,
                                 id="buoy_id",
                                 row_index="ROW_I",
                                 row_index_style= "SEQUENCE",
                                 payload_field="OUT_magnitude1",
                                 payload_content="REAL")

        uaf_out = UNDIFF(data1=data_series_1,
                         data2=data_series,
                         lag=1,
                         differences=1,
                         seasonal_multiplier=0,
                         input_fmt_input_mode="MATCH")

        # Print the result DataFrame.
        print(uaf_out.result)
    """
