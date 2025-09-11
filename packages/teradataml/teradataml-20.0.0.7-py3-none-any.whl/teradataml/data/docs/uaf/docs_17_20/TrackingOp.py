def TrackingOp(data=None, data_filter_expr=None, distance=None, 
               speed=None, time_spent=None, metric=None, 
               **generic_arguments):
    """
    DESCRIPTION:
        The TrackingOp() function is a multi-dimensional function for geospatial data.
        It calculates the trip distance, speed, time, and so on for a trip.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a multivariate time series as an input.
            The first three fields of the payload fields must be as follows:
                * Field 1: A column or field which is a timestamp or timestamp with time zone data type.
                           The field represents the arrival time associated with the object being tracked.
                * Field 2: A column or field which is a timestamp or timestamp with time zone data type.
                           The field represents the departure time associated with the object being tracked.
                * Field 3: A column or field which is a geospatial data type that represents the location of
                           the object being tracked.
                Any number of fields may follow the first three fields, and can be any non-LOB data type.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        distance:
            Optional Argument.
            Specifies whether to calculate the track distance.
            When set to True, calculates the distance, otherwise not.
            Default Value: False
            Types: bool

        speed:
            Optional Argument.
            Specifies whether to calculate the average speed
            with the maximum and minimum values.
            When set to True, calculates the trip's average
            speed along with max and min speeds in that trip, otherwise
            no action is taken.
            Default Value: False
            Types: bool

        time_spent:
            Optional Argument.
            Specifies whether to calculate the total time for the trip.
            When set to True, calculates the total time
            spent of the trip, otherwise no action is taken.
            Default Value: False
            Types: bool

        metric:
            Optional Argument.
            Specifies the metric to be used for distance and time.
            When set to True, distance and speed should be expressed
            in kilometer and Km/Hr, otherwise distance and speed should
            be expressed in miles and miles/Hr.
            Default Value: False
            Types: bool

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
        Instance of TrackingOp.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as TrackingOp_obj.<attribute_name>.
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
        load_example_data("uaf", "train_tracking")

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("train_tracking")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id=["train_id", "schedule_date"],
                                  row_index="arrival_time",
                                  row_index_style="TIMECODE",
                                  payload_field=["arrival_time", "departure_time", "geo_tag"],
                                  payload_content="MULTIVAR_ANYTYPE")

        # Example 1 : Calculate total distance, minimum, maximum and average speed,
        #             trip_time and run_time for the train.
        uaf_out = TrackingOp(data=data_series_df,
                             distance=True,
                             speed=True,
                             time_spent=True,
                             metric=True)

        # Print the result DataFrame.
        print(uaf_out.result)
    """
    