def IQR(data=None, data_filter_expr=None, stat_metrics=False, 
        output_fmt_index_style="NUMERICAL_SEQUENCE", 
        **generic_arguments):
    """
    DESCRIPTION:
        Anomaly detection identifies data points, events and observations that
        deviate from the normal behavior of the data set.
        Anomalous data can indicate critical incidents, such as a change in
        consumer behavior or observations that are suspicious.
        Anomalies in data are also called standard deviations, outliers, noise,
        novelties, and exceptions.

        IQR() uses interquartile range for anomaly detection. Any data point
        that falls outside of 1.5 times of an interquartile range below
        the first quartile and above the third quartile is considered an outlier.
        The IQR() function creates a two-layered ART table.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the time series whose value can be REAL or MULTIVAR_REAL.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        stat_metrics:
            Optional Argument.
            Specifies the indicator for the secondary layer
            to indicate the number of outliers.
            Default Value: False
            Types: bool

        output_fmt_index_style:
            Optional Argument.
            Specifies the INDEX_STYLE of the output format.
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
        Instance of IQR.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as IQR_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. statsdata
            3. fitmetadata


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

        # Load the example data.
        load_example_data("uaf", ["real_values"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("real_values")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                   id="id",
                                   row_index="TD_TIMECODE",
                                   payload_field="val",
                                   payload_content="REAL")

        # Example 1: Detect which and how many values are considered outliers.
        uaf_out = IQR(data=data_series_df,
                      stat_metrics=True)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.statsdata)
    
    """
    