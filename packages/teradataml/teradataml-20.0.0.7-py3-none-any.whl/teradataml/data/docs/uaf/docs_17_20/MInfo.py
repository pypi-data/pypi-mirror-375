def MInfo(data=None, data_filter_expr=None, **generic_arguments):
    """
    DESCRIPTION:
        The MInfo() function returns one row for each matrix instance found
        in the input data. Each returned row provides the following information
        about a matrix:
            * Row index data type
            * Starting row index value
            * Ending row index value
            * Number of row index entries
            * Indicator that the matrix is regular (discrete) or irregular along
              row index
            * Row index sample interval for regular series or average sample
              interval for irregular series
            * Column index data type
            * Starting column index value
            * Ending column index value
            * Number of column index entries
            * Indicator that the matrix is regular (discrete) or irregular along
              column index
            * Column index sample interval for regular series or average sample
              interval for irregular series
            * Content type
            * Minimum sample magnitude
            * Maximum sample magnitude
            * Average sample magnitude
            * Number of NULL values
            * Indicator matrix is well formed or malformed


    PARAMETERS:
        data:
            Required Argument.
            Specifies a collection of logical matrixes.
            These matrixes can be regular or irregular. Their indexing
            mechanisms can be time or space.
            Types: TDMatrix

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
        Instance of MInfo.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as MInfo_obj.<attribute_name>.
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
        df = DataFrame.from_table("ocean_buoys2")

        # Create teradataml TDMatrix object.
        res = TDMatrix(data=df,
                       id=['ocean_name', 'buoyid'],
                       row_index='TD_TIMECODE',
                       column_index = 'space',
                       row_index_style="TIMECODE",
                       column_index_style="SEQUENCE",
                       payload_field='jsoncol.Measure.salinity',
                       payload_content='REAL')

        # Example 1 : Displays a result set containing metadata about each matrix.
        #             The function returns one row per matrix processed. In
        #             addition, each input payload produces the output variables
        #             for MIN_MAG, MAX_MAG and AVG_MAG. The output varies depending
        #             on the number of input payloads.
        uaf_out = MInfo(data=res)

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    