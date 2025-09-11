def GenseriesFormula(data=None, data_filter_expr=None, formula=None, 
                     estimate_mode=False, 
                     output_fmt_index_style="NUMERICAL_SEQUENCE", 
                     **generic_arguments):
    """
    DESCRIPTION:
        The GenseriesFormula() function allows you to define and apply
        a formula to generate a time series. This function has many use
        cases, including the ability to generate a series that is 
        subtracted from a non-stationary series to make it stationary,
        and to estimate beyond the sample data points.

        The following procedure is an example of how to use the
        GenseriesFormula() function:
            * Determine that the series to be modeled includes
              a trend.
            * Use LinearRegr() function to remove the trend from 
              the series.
            * Use the "fitmetadata" attribute from the function output,
              to determine the trend by fitting the data set.
            * Use GenseriesFormula() function to generate a
              trend series.
            * Use BinarySeriesOp() function to subtract the
              generated trend from the original series.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input time series or self-generating
            time series.
            Notes:
                * Series specification is a time series or 
                  spatial series. Series can be REAL or MULTIVAR_REAL.
                * Generated series specification uses a self-generated series.
            Types: TDSeries, TDGenseries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        formula:
            Required Argument.
            Specifies the formula to apply to the input time series.
            The formula represents the trend or periodicity in the input time 
            series and conforms to formula rules.
            
            If you specify generated series, TDGenSeries, the formula
            can have only one explanatory variable. The function assigns
            the starting value to the explanatory variable.
            Note:
                Use the following link to refer the formula rules in
                Teradata document:
                "https://docs.teradata.com/r/Teradata-VantageTM-Unbounded-Array-Framework-Time-Series-Reference/Mathematic-Operators-and-Functions/Formula-Rules"
            Types: str

        estimate_mode:
            Optional Argument.
            Specifies whether to include the input parameters in the results.
            When set to True, function includes input parameters in the results,
            otherwise does not include.
            Default Value: False
            Types: bool

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
        Instance of GenseriesFormula.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as GenseriesFormula_obj.<attribute_name>.
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

        from teradataml import FLOAT, INTEGER

        # Load the example data.
        load_example_data("uaf", ["production_data2"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("production_data2")

        # Example 1: Execute the GenseriesFormula() function on TDSeries input 
        #            for index style 'FLOW_THROUGH' to generate a time series.
        #            New time series with the same type as the series
        #            specification payload content value.
        # Create teradataml TDSeries object.
        data_series_df_1 = TDSeries(data=data,
                                    id="product_id",
                                    row_index="TD_TIMECODE",
                                    payload_field="beer_sales",
                                    payload_content="REAL")

        # Execute GenseriesFormula for TDSeries.
        uaf_out_1 =  GenseriesFormula(data=data_series_df_1,
                                      formula="Y = 2.0*X1 + SIN(X1)",
                                      output_fmt_index_style='FLOW_THROUGH')

        # Print the result DataFrame.
        print(uaf_out_1.result)

        # Example 2: Execute the GenseriesFormula() function on TDGenSeries input 
        #            for index style value 'NUMERICAL_SEQUENCE' and TDGenSeries
        #            data types as FLOAT to generate a time series.
        #            Functions returns new time series with the same type as 
        #            the generated series specification payload content value.
        #            TDGenSeries datatypes is float.
        # Create teradataml TDGenSeries object.
        data_series_df_2 = TDGenSeries(instances = {"BuoyID": 3},
                                       data_types = FLOAT(),
                                       start=0.0,
                                       offset=1.0,
                                       num_entries=5)

        # Execute GenseriesFormula for TDGenSeries.
        uaf_out_2 =  GenseriesFormula(data=data_series_df_2,
                                      formula="Y = 3.0 + 8.0*X1",
                                      output_fmt_index_style='NUMERICAL_SEQUENCE')

        # Print the result DataFrame.
        print(uaf_out_2.result)

        # Example 3: Execute the GenseriesFormula() function on TDGenSeries input 
        #            for index style value 'NUMERICAL_SEQUENCE' and TDGenSeries
        #            data types as INTEGER to generate a time series.
        #            Functions returns new time series with the same type as 
        #            the generated series specification payload content value.
        #            TDGenSeries datatypes is integer.
        # Create teradataml TDGenSeries object.
        data_series_df_3 = TDGenSeries(instances = {"BuoyID": 3},
                                       data_types = INTEGER(),
                                       start=0,
                                       offset=1,
                                       num_entries=5)

        # Execute GenseriesFormula for TDGenSeries.
        uaf_out_3 =  GenseriesFormula(data=data_series_df_3,
                                      formula="Y = 3.0 + 8.0*X1",
                                      output_fmt_index_style='NUMERICAL_SEQUENCE')

        # Print the result DataFrame.
        print(uaf_out_3.result)

    """
    