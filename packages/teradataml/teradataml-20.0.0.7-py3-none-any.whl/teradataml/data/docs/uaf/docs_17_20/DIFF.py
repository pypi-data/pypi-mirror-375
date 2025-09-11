def DIFF(data=None, data_filter_expr=None, lag=None, 
         differences=None, seasonal_multiplier=None, 
         output_fmt_index_style="NUMERICAL_SEQUENCE", 
         **generic_arguments):
    """
    DESCRIPTION:
        The DIFF() function transforms a stationary, seasonal, or non-stationary
        time series into a differenced time series by performing both status-quo
        time series differencing, seasonal based differencing, and multiplicative
        transforms. Thus, the output of this transform function is always a new
        time series.

        The following procedure is an example of how to use DIFF() function:
            1. Detect the unit roots using DickeyFuller() function.
            2. Use DIFF() function to eliminate unit roots.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input time series with payload content as 'REAL' or 'MULTIVAR_REAL',
            or specifies the output of UNDIFF in ART Spec. When passed in a multivariate
            series, DIFF() function is executed separately against each identified series in
            the collection and produce a coalesced multivariate style analytical result set.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        lag:
            Required Argument.
            Specifies the lag between the series elements.
            It accepts positive integer value, including zero.
            Types: int

        differences:
            Required Argument.
            Specifies the difference between time series elements
            'Yt' and 'Yt-lag'. It accepts positive integer value,
            including zero.
            Types: int

        seasonal_multiplier:
            Required Argument.
            Specifies whether a time series is seasonal or not.
            It accepts positive integer value, including zero.
            When set to 0, indicates time series is nonseasonal.
            Positive value indicates it is seasonal.
            The "seasonal_multiplier determines the formula to
            be used by function to transform each input time
            series element, 'Yt', to a differenced time series
            element, 'Ydt'.
            Types: int

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
        Instance of DIFF.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as DIFF_obj.<attribute_name>.
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

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("ocean_buoy2")

        # Example 1: Execute DIFF() function with TDSeries having
        #            REAL payload content to transform time series
        #            into a differenced time series.

        # Create teradataml TDSeries object.
        data_series_df_real = TDSeries(data=data,
                                       id="buoy_id",
                                       row_index="n_seq_no",
                                       row_index_style= "SEQUENCE",
                                       payload_field="magnitude1",
                                       payload_content="REAL")

        uaf_out_1 = DIFF(data=data_series_df_real,
                         lag=1,
                         differences=2,
                         seasonal_multiplier=0)

        # Print the result DataFrame.
        print(uaf_out_1.result)

        # Example 2: Execute DIFF() function with TDSeries having
        #            MULTIVAR_REAL payload content to transform time
        #            series into a differenced time series.

        # Create teradataml TDSeries object.
        data_series_df_multivar = TDSeries(data=data,
                                           id="buoy_id",
                                           row_index="n_seq_no",
                                           row_index_style= "SEQUENCE",
                                           payload_field=["magnitude1", "magnitude2"],
                                           payload_content="MULTIVAR_REAL")

        uaf_out_2 = DIFF(data=data_series_df_multivar,
                         lag=1,
                         differences=2,
                         seasonal_multiplier=0)

        # Print the result DataFrame.
        print(uaf_out_2.result)
    
    """
    