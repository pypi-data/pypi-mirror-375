def Attribution(data=None, data_optional=None, data_optional2=None, data_optional3=None, data_optional4=None,
                conversion_data=None, excluding_data=None, optional_data=None, model1_type=None, model2_type=None,
                event_column=None, timestamp_column=None, window_size=None, **generic_arguments):
    """
    DESCRIPTION:
        The Attribution() function is used in web page analysis, where it lets
        companies assign weights to pages before certain events, such as
        buying a product.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        data_optional:
            Optional Argument.
            Specifies the click stream data, which the function uses to compute
            attributions.
            Types: teradataml DataFrame

        data_optional2:
            Optional Argument.
            Specifies the click stream data, which the function uses to compute
            attributions.
            Types: teradataml DataFrame

        data_optional3:
            Optional Argument.
            Specifies the click stream data, which the function uses to compute
            attributions.
            Types: teradataml DataFrame

        data_optional4:
            Optional Argument.
            Specifies the click stream data, which the function uses to compute
            attributions.
            Types: teradataml DataFrame

        conversion_data:
            Required Argument.
            Specifies one varchar column (conversion_events) containing conversion
            event values.
            Types: teradataml DataFrame

        excluding_data:
            Optional Argument.
            Specifies one varchar column (excluding_events) containing excluding
            cause event values.
            Types: teradataml DataFrame

        optional_data:
            Optional Argument.
            Specifies one varchar column (optional_events) containing optional
            cause event values.
            Types: teradataml DataFrame

        model1_type:
            Required Argument.
            Specifies the type and specification of the first model.
            For example:
                +----+----------------------+
                | id |        model         |
                +----+----------------------+
                | 0  |   SEGMENT_SECONDS    |
                |    |                      |
                | 1  |   6:0.5:UNIFORM:NA   |
                |    |                      |
                | 2  | 8:0.3:LAST_CLICK:NA  |
                |    |                      |
                | 3  | 6:0.2:FIRST_CLICK:NA |
                +----+----------------------+
            Types: teradataml DataFrame

        model2_type:
            Optional Argument.
            Specifies the type and distributions of the second model.
            For example:
                +----+--------------------------------+
                | id |             model              |
                +----+--------------------------------+
                | 0  |          SEGMENT_ROWS          |
                |    |                                |
                | 1  |  3:0.5:EXPONENTIAL:0.5,SECOND  |
                |    |                                |
                | 2  | 4:0.3:WEIGHTED:0.4,0.3,0.2,0.1 |
                |    |                                |
                | 3  |      3:0.2:FIRST_CLICK:NA      |
                +----+--------------------------------+
            Types: teradataml DataFrame

        event_column:
            Required Argument.
            Specifies the name of the input column that contains the clickstream
            events.
            Types: str

        timestamp_column:
            Required Argument.
            Specifies the name of the input column that contains the timestamps
            of the clickstream events.
            Types: str

        window_size:
            Required Argument.
            Specifies how to determine the maximum window size for the
            attribution calculation: rows:K: Consider the maximum number of
            events to be attributed, excluding events of types specified in
            excluding_event_table, which means assigning attributions to at most
            K effective events before the current impact event.seconds:K:
            Consider the maximum time difference between the current impact event
            and the earliest effective event to be attributed. rows:K&seconds:K2:
            Consider both constraints and comply with the stricter one.
            Types: str

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in table or
                    not. When set to True, results are persisted in table; otherwise,
                    results are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in volatile table
                    or not. When set to True, results are stored in volatile table,
                    otherwise not.
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
                These generic arguments are supported by teradataml if the underlying
                SQLE function supports it, else an exception is raised.

    RETURNS:
        Instance of Attribution.
        Output teradataml DataFrames can be accessed using attribute
        references, such as AttributionObj.<attribute_name>.
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

        # Load the data to run the example
        load_example_data("attribution", ["attribution_sample_table1",
        "attribution_sample_table2" , "conversion_event_table",
        "optional_event_table", "model1_table", "model2_table"])

        # Create teradataml DataFrame objects
        attribution_sample_table1 = DataFrame.from_table("attribution_sample_table1")
        attribution_sample_table2 = DataFrame.from_table("attribution_sample_table2")
        conversion_event_table = DataFrame.from_table("conversion_event_table")
        optional_event_table = DataFrame.from_table("optional_event_table")
        model1_table = DataFrame.from_table("model1_table")
        model2_table = DataFrame.from_table("model2_table")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Assign attribution weights to events and channels.
        attribution_out = teradataml.Attribution(data=attribution_sample_table1,
                                                 data_partition_column="user_id",
                                                 data_order_column="time_stamp",
                                                 data_optional=attribution_sample_table2,
                                                 data_optional_partition_column='user_id',
                                                 data_optional_order_column='time_stamp',
                                                 event_column="event",
                                                 conversion_data=conversion_event_table,
                                                 optional_data=optional_event_table,
                                                 timestamp_column = "time_stamp",
                                                 window_size = "rows:10&seconds:20",
                                                 model1_type=model1_table,
                                                 model2_type=model2_table)

        # Print the results DataFrame.
        print(attribution_out.result)
    """