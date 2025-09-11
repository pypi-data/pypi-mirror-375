def DTW(data1=None, data1_filter_expr=None, data2=None, 
        data2_filter_expr=None, radius=None, distance=None, 
        warp_path=None, input_fmt_input_mode=None,
        **generic_arguments):
    """
    DESCRIPTION:
        The DTW() function measures the similarity of two time series.
        The Dynamics Time Warping (DTW) algorithm is used for space and
        time. The underlying algorithm used by DTW() function is the FastDTW
        algorithm. It is not recommended for large datasets. This algorithm
        can find the optimal, or a close to optimal warp path between two
        series, depending on the search radius used.


    PARAMETERS:
        data1:
            Required Argument.
            Specifies the first series input out of two.
            Note:
                The input series specified in "data1" and "data2" must
                have the same number of payload columns.
            Types: TDSeries

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Required Argument.
            Specifies the second series input out of two.
            Note:
                The input series specified in "data1" and "data2" must
                have the same number of payload columns.
            Types: TDSeries

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        radius:
            Optional Argument.
            Specifies the search radius for the FastDTW algorithm.
            This value should be a positive integer within the range
            0 to 1000. Using a small radius is sufficient for finding
            the optimal match. Larger value of radius can cause significant
            performance issues without providing a better result.
            Types: int

        distance:
            Optional Argument.
            Specifies the distance function to be used.
            Permitted Values:
                * EUCLIDEAN - Euclidean distance function.
                * MANHATTAN - Manhattan distance function.
                * BINARY - Binary distance function.
            Types: str

        warp_path:
            Optional Argument.
            Specifies the type of warp paths.
            Permitted Values:
                * 0 - No warp paths to be generated.
                      Only the warp distance is calculated.
                * 1 - Warp paths to be generated with WarpX and
                      WarpY output columns as the path index.
                * 2 - Warp paths to be generated with WarpX_I and
                      WarpY_I using the series 1 and series 2
                      ROW_I values at the path index.
                * 3 - Warp paths to be generated with both the
                      output columns 1 and 2.
            Types: int

        input_fmt_input_mode:
            Required Argument.
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
        Instance of DTW.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as DTW_obj.<attribute_name>.
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
        load_example_data("uaf", ["dtw_t1", "dtw_t2"])

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("dtw_t1")
        data2 = DataFrame.from_table("dtw_t2")

        # Create teradataml TDSeries objects.
        data_series_df = TDSeries(data=data1,
                                  id="id",
                                  row_index="seq",
                                  row_index_style= "TIMECODE",
                                  payload_field="v",
                                  payload_content="REAL")

        data2_series_df = TDSeries(data=data2,
                                  id="id",
                                  row_index="seq",
                                  row_index_style= "TIMECODE",
                                  payload_field="v",
                                  payload_content="REAL")

        # Example 1 : Execute DTW() function to measure the
        #             similarity between two time series.
        uaf_out = DTW(data1=data_series_df,
                      data2=data2_series_df,
                      input_fmt_input_mode='MANY2ONE',
                      warp_path=2,
                      radius=1,
                      data2_filter_expr=data2_series_df.id==1)

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    