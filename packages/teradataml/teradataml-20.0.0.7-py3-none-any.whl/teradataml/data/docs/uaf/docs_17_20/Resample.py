def Resample(data=None, data_filter_expr=None, timecode_start_value=None,
             timecode_duration=None, sequence_start_value=None,
             sequence_duration=None, interpolate=None, weight=None,
             spline_params_method="NOT_A_KNOT", spline_params_yp1=0.0,
             spline_params_ypn=0.0, output_fmt_index_style='FLOW_THROUGH',  **generic_arguments):
    """
    DESCRIPTION:
        The Resample() function transforms an irregular time series into a
        regular time series. It can also be used to alter the sampling interval
        for a time series.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the irregular time series that is to be altered.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        timecode_start_value:
            Optional Argument.
            Specifies the first sampling index to interpolate.
            Note:
                Provide either arguments "timecode_start_value" and
                "timecode_duration", or arguments "sequence_start_value"
                and "sequence_duration".
            Types: str

        timecode_duration:
            Optional Argument.
            Specifies the sampling interval associated with the result series.
            Note:
                Provide either arguments "timecode_start_value" and
                "timecode_duration", or arguments "sequence_start_value"
                and "sequence_duration".
            Permitted Values:
                * CAL_YEARS
                * CAL_MONTHS
                * CAL_DAYS
                * WEEKS
                * DAYS
                * HOURS
                * MINUTES
                * SECONDS
                * MILLISECONDS
                * MICROSECONDS
            Types: str

        sequence_start_value:
            Optional Argument.
            Specifies the first sampling index to interpolate.
            Note:
                Provide either arguments "timecode_start_value" and
                "timecode_duration", or arguments "sequence_start_value"
                and "sequence_duration".
            Types: int OR float

        sequence_duration:
            Optional Argument.
            Specifies the sampling interval associated with the result series.
            Note:
                Provide either arguments "timecode_start_value" and
                "timecode_duration", or arguments "sequence_start_value"
                and "sequence_duration".
            Types: int OR float

        interpolate:
            Required Argument.
            Specifies the interpolation strategies.
            Permitted Values:
                * LINEAR
                * LAG
                * LEAD
                * WEIGHTED
                * SPLINE
            Types: str

        weight:
            Optional Argument.
            Specifies the interpolated weighted value.
            Note:
                * Applicable only when "interpolate" set to 'WEIGHTED'.
                * The interpolated value is calculated as: Y_t  =  Y_{t_LEFT} * (1 - WEIGHT) + (Y-{t_RIGHT} * WEIGHT).
            Types: int OR float

        spline_params_method:
            Optional Argument.
            Specifies the type of spline method to use.
            Note:
                * Applicable only when "interpolate" set to 'SPLINE'.
            Permitted Values:
                * CLAMPED
                * NATURAL
                * NOT_A_KNOT
            Default Value: NOT_A_KNOT
            Types: str

        spline_params_yp1:
            Optional Argument.
            Specifies the value of the first derivative for the left boundary
            condition.
            Notes:
                * Used only when "interpolate" set to 'SPLINE'.
                * Used only when "spline_params_method" set to 'CLAMPED'.
            Default Value: 0.0
            Types: int OR float

        spline_params_ypn:
            Optional Argument.
            Specifies the value of the first derivative for the right boundary
            condition.
            Notes:
                * Used only when "interpolate" set to 'SPLINE'.
                * Used only when "spline_params_method" set to 'CLAMPED'.
            Default Value: 0.0
            Types: int OR float

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Permitted Values: NUMERICAL_SEQUENCE, FLOW_THROUGH
            Default Value: FLOW_THROUGH
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
        Instance of Resample.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as Resample_obj.<attribute_name>.
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
        load_example_data("uaf", ["production_data"])

        # Create teradataml DataFrame object.
        production_data = DataFrame.from_table("production_data")

        # Example 1 : Execute function to transform irregular time series into
        #             regular time series when row index style is "SEQUENCE".
        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=production_data,
                                  id="product_id",
                                  row_index_style="SEQUENCE",
                                  row_index="TD_SEQNO",
                                  payload_field="beer_sales",
                                  payload_content="REAL")

        # Execute Resample for TDSeries.
        uaf_out1 = Resample(data=data_series_df,
                            interpolate='LINEAR',
                            sequence_start_value=0.0,
                            sequence_duration=1.0)

        # Print the result DataFrame.
        print(uaf_out1.result)

        # Example 2 : Execute function to transform irregular time series into
        #             regular time series when row index style is "TIMECODE".
        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=production_data,
                                  id="product_id",
                                  row_index_style="TIMECODE",
                                  row_index="TD_TIMECODE",
                                  payload_field="beer_sales",
                                  payload_content="REAL")

        # Execute Resample for TDSeries.
        uaf_out2 = Resample(data=data_series_df,
                            interpolate='LINEAR',
                            timecode_start_value="TIMESTAMP '2021-01-01 00:00:00'",
                            timecode_duration="MINUTES(30)")

        # Print the result DataFrame.
        print(uaf_out2.result)
    
    """
    