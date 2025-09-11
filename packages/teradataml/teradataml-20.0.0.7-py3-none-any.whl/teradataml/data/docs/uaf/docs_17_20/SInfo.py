def SInfo(data=None, data_filter_expr=None, **generic_arguments):
    """
    DESCRIPTION:
        The SInfo() function returns one row for each series instance found in
        DataFrame. Each returned row provides the following information about
        the series:
            * Index data type
            * Starting index value
            * Ending index value
            * Number of series entries
            * Indicator that the series is regular (discrete) or irregular
            * Sample interval for regular series or average sample interval for
              irregular series
            * Content type
            * Minimum sample magnitude
            * Maximum sample magnitude
            * Average of magnitudes in the series
            * Root-mean-square for each magnitude


    PARAMETERS:
        data:
            Required Argument.
            Specifies a logical series of either the regular or irregular type based on
            time or space.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies filter expression for "data".
            Types: ColumnExpression

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
        Instance of SInfo.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as SInfo_obj.<attribute_name>.
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
        load_example_data("uaf", ["ocean_buoys2"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("ocean_buoys2")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id=["ocean_name","buoyid"],
                                  row_index="TD_TIMECODE",
                                  row_index_style="TIMECODE",
                                  payload_field="jsoncol.Measure.salinity",
                                  payload_content="REAL")


        # Example 1 : Display a result set with metadata about the series.
        #             There is one output row for each series. In addition,
        #             each input payload produces the output variables for
        #             MIN, MAX, AVG and RMS. The output varies depending on
        #             the number of input payloads.
        uaf_out = SInfo(data=data_series_df)

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    