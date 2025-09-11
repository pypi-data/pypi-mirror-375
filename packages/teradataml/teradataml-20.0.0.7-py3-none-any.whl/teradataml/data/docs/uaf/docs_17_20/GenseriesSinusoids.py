def GenseriesSinusoids(data=None, data_filter_expr=None, periodicities=None, 
                       output_fmt_index_style="NUMERICAL_SEQUENCE", 
                       **generic_arguments):
    """
    DESCRIPTION:        
        The GenseriesSinusoids() function generates a result series
        containing a subset of the sinusoidal elements periodicities (sinusoids).
        
        User can subtract the new time series from the original time series
        by removing the periodicities. The following procedure is an
        example of how to use GenseriesSinusoids() function:
            * Use the LineSpec() or PowerSpec() function with "freq_style" argument
              set to 'K_PERIODICITY' to determine the periodicities in
              the series.
            * Use the result dataframe from the GenseriesSinusoids() function
              to view the periodicities.
            * Use GenseriesSinusoids() function with the "periodicities"
              argument and a comma-separated list of periodicities to
              exclude from the data set.
            * Use the BinarySeriesOp() function to subtract the generated series
              from the original series using "mathop" argument value as 'SUB'.
            * Use the PowerSpec() function to verify that target periodicities
              have been removed from the original series.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input time series, whose payload content
            value is 'REAL'.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        periodicities:
            Required Argument.
            Specifies the periodicity as a comma-separated list, which
            contains one or more floating point values representing 
            periodicities.
            Types: int, list of int, float, list of float
            
        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Permitted Values: NUMERICAL_SEQUENCE, FLOW_THROUGH
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
        Instance of GenseriesSinusoids.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as GenseriesSinusoids_obj.<attribute_name>.
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
        data = DataFrame.from_table("production_data")

        # Example 1: Execute the GenseriesSinusoids() function 
        #            on TDSeries input to generate a time series 
        #            containing a subset of the sinusoidal 
        #            elements periodicities, whose payload content
        #            value is REAL.

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="product_id",
                                  row_index="TD_TIMECODE",
                                  payload_field="beer_sales",
                                  payload_content="REAL")

        # Execute GenseriesSinusoids() fucntion.
        uaf_out = GenseriesSinusoids(data=data_series_df,
                                     periodicities=[0.523, 1.4367])

        # Print the result DataFrame.
        print(uaf_out.result)

    """
    