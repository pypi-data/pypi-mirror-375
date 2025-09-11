def Smoothma(data=None, data_filter_expr=None, ma=None, window=None, 
             one_sided=False, lambda1=None, weights=None, 
             well_known=None, pad=None, 
             output_fmt_index_style="NUMERICAL_SEQUENCE", 
             **generic_arguments):
    """
    DESCRIPTION:
        The Smoothma() function applies a smoothing function to a time series
        which results in a series that highlights the time series mean. For
        non-stationary time series with non-constant means, the smoothing
        function is used to create a result series. When the result series
        is subtracted from the original series, it removes the non-stationary
        mean behavior.

        User can use the new time series to build an ARIMA forecasting model.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input series.
            Note:
                * Payload content value of the series must be REAL or MULTIVAR_REAL.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies filter expression for "data".
            Types: ColumnExpression

        ma:
            Required Argument.
            Specifies the type of moving average algorithm to use.
            Permitted Values:
                * CUMULATIVE: Cumulative moving average.
                * MEAN: Simple Moving Average with the arguments "window", "one_sided",
                        "pad", "well_known", "weights".
                * MEDIAN: Simple moving median with the arguments "window", "pad".
                * EXPONENTIAL: Exponential moving average with the argument "lambda1".
            Types: str

        window:
            Optional Argument.
            Specifies the order (window size) of the moving average to be applied.
            Odd numbers use the Simple Moving Average formula. Even numbers use
            the Centered Moving Average formula.
            For example, window='6' with ma='MEAN' uses the Centered Moving average
            algorithm.
            Note:
                * Applicable only when "ma" is set to 'MEAN' or 'MEDIAN'.
            Types: int

        one_sided:
            Optional Argument.
            Specifies whether to use centering or not. When set to False, it means use
            centering, otherwise do not use centering. The last "window" entries are
            averaged to form the current entry.
            Note:
                * Applicable only when "ma" is set to 'MEAN'.
            Default Value: False
            Types: bool

        lambda1:
            Optional Argument.
            Specifies a value between 0 and 1, which represents the degree of weighting
            decrease. A higher "lambda1" has the effect of discounting older observations
            faster.
            Note:
                * Applicable only when "ma" is set to 'EXPONENTIAL'.
            Types: int OR float

        weights:
            Optional Argument.
            Specifies the list of weights to be applied when calculating the moving average.
            The weights should sum up to 1, and be symmetric. If the weights don’t sum up to 1,
            then the sum from the list of weights divides each element in the list to get
            a fraction for each element to achieve the same effect of the sum up to 1.
            The number of elements in the "weights" list must match the "window" value.
            Function uses the number of the "weights" element as the default "window"
            value if it is not specified.
            Note:
                * Applicable only when "ma" is set to 'MEAN'.
            Types: int OR float

        well_known:
            Optional Argument.
            Specifies one of the supported well-known weighted MA combinations to be applied to
            the input series.
            If "window" is not specified, then the function provides the value as follows:
                * For 3MA, "window" value is 3.
                * For 3X3MA, and H5MA, "window" value is 5.
                * For 3X5MA, "window" value is 7.
                * For H9MA, "window" value is 9.
                * For 2X12MA, and H13MA, "window" value is 13.
                * For S15MA, "window" value is 15.
                * For S21MA, "window" value is 21.
                * For H23MA, "window" value is 23.
            Notes:
                * "well_known" and "weights" must be used in a mutually exclusive fashion.
                * Applicable only to SMA.
            Permitted Values: 3MA, 5MA, 2x12MA, 3x3MA, 3x5MA,
                              S15MA, S21MA, H5MA, H9MA, H13MA, H23MA
            Types: str

        pad:
            Optional Argument.
            Specifies the produced output series has the magnitudes set to PAD value for
            an element less than "window".
            For example, pad=4.5 applies a pad value of 4.5 for a series less than "window".
            Note:
                * Applicable only when "ma" is set to 'MEAN' or 'MEDIAN'.
            Types: int, float

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Default Value: NUMERICAL_SEQUENCE
            Permitted Values: NUMERICAL_SEQUENCE, FLOW_THROUGH
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
        Instance of Smoothma.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as Smoothma_obj.<attribute_name>.
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
        load_example_data("uaf", ["orders1_12"])

        # Create teradataml DataFrame object.
        df=DataFrame.from_table("orders1_12")

        # Create teradataml TDSeries object.
        data_series_df= TDSeries(data=df,
                                 id="OrderID",
                                 row_index="SEQ",
                                 row_index_style="SEQUENCE",
                                 payload_field="Qty1",
                                 payload_content="REAL")

        # Example 1 :  Perform exponential moving average.
        uaf_out = Smoothma(data=data_series_df,
                           ma='EXPONENTIAL',
                           lambda1=0.5)

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    