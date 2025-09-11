def Convolve(data1=None, data1_filter_expr=None, data2=None, 
             data2_filter_expr=None, algorithm=None, 
             input_fmt_input_mode=None, **generic_arguments):
    """
    DESCRIPTION:
        The Convolve() function applies a series representing a
        digital filter to a time series by convolving the two series. 
        The digital filter can be of any type such as low-pass, band-pass,
        band-reject, high-pass, and so on.

        User can use digital filters to separate time series that
        have been combined and to restore time series that have 
        become distorted.


    PARAMETERS:
        data1:
            Required Argument.
            Specifies the time series to be filtered.
            The time series have the following TDSeries characteristics.
                1. "payload_content" must have one of these values:
                    * REAL
                    * COMPLEX
                    * MULTIVAR_REAL
                    * MULTIVAR_COMPLEX
                2. The two time series must have the same "payload_content" value
                   and number of payload fields, with these exceptions:
                    * One can have "payload_content" value 'MULTIVAR_REAL' and
                      multiple payload fields and the other can have
                      "payload_content" value REAL and one payload field.
                    * When both have the "payload_content" value 'MULTIVAR_COMPLEX',
                      one can have multiple pairs of payload fields and
                      the other can have a single pair of payload fields.
            Types: TDSeries

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Required Argument.
            Specifies the actual filter kernel.
            The time series have the following TDSeries characteristics.
                1. "payload_content" must have one of these values:
                    * REAL
                    * COMPLEX
                    * MULTIVAR_REAL
                    * MULTIVAR_COMPLEX
                2. The two time series must have the same "payload_content" value
                   and number of payload fields, with these exceptions:
                    * One can have "payload_content" value 'MULTIVAR_REAL' and
                      multiple payload fields and the other can have
                      "payload_content" value REAL and one payload field.
                    * When both have the "payload_content" value 'MULTIVAR_COMPLEX',
                      one can have multiple pairs of payload fields and
                      the other can have a single pair of payload fields.
            Types: TDSeries

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        algorithm:
            Optional Argument.
            Specifies the options to use for convolving.
            By default, the function selects the best option based
            on the number of entries present in the two inputs,
            and their types ( REAL, COMPLEX, and so on.)
            CONV_SUMMATION only supports:
                * REAL, REAL
                * REAL, MULTIVAR_REAL
                * MULTIVAR_REAL, REAL
                * MULTIVAR_REAL, MULTIVAR_REAL
            Note:
                * This parameter is usually used for testing.
                  If this parameter is not included, the internal
                  planning logic selects the best option based on
                  the number of entries present in the two inputs,
                  and their types ( REAL, COMPLEX, and so on.)
            Permitted Values: CONV_SUMMATION, CONV_DFFT
            Types: str

        input_fmt_input_mode:
            Required Argument.
            Specifies the input mode supported by the function.
            Permitted Values: 
                1. ONE2ONE: Both the data1 and data2 series
                   specifications contain a series name which identifies
                   the two series in the function.
                2. MANY2ONE: The MANY specification is the data1 series
                   declaration. The data2 series specification contains
                   a series name that identifies the single data2 series.
                3. MATCH: Both series are defined by their respective
                   series specification instance name declarations.
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
        Instance of Convolve.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as Convolve_obj.<attribute_name>.
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
        load_example_data("uaf", ["xconvolve_complex_leftmulti", "hconvolve_complex_rightmulti",
                                  "xconvolve_complex_left", "hconvolve_complex_right"])

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("xconvolve_complex_leftmulti")
        data2 = DataFrame.from_table("hconvolve_complex_rightmulti")
        data3 = DataFrame.from_table("xconvolve_complex_left")
        data4 = DataFrame.from_table("hconvolve_complex_right")

        # Example 1: Execute Convolve() function to convolve two series into new time series using "CONV_DFFT" 
        #            algorithm. 
        #            Note:
        #               The two input time series "payload_content" are 'MULTIVAR_COMPLEX' and the resultant
        #               time series "payload_content" is 'MULTIVAR_COMPLEX'.

        # Create teradataml TDSeries objects for "payload_content" with the value 'MULTIVAR_COMPLEX'.
        data1_series_df = TDSeries(data=data1,
                                   id="id",
                                   row_index_style="sequence",
                                   row_index="seq",
                                   payload_field=["a_real", "a_imag", "b_real", "b_imag", "c_real", "c_imag"],
                                   payload_content="MULTIVAR_COMPLEX")
        data2_series_df = TDSeries(data=data2,
                                   id="id",
                                   row_index_style="sequence",
                                   row_index="seq",
                                   payload_field=["a_real", "a_imag", "b_real", "b_imag", "c_real", "c_imag"],
                                   payload_content="MULTIVAR_COMPLEX")
        # Convolve the "data1_series_df" and "data2_series_df" series using the Convolve() function.
        uaf_out1 = Convolve(data1=data1_series_df,
                            data2=data2_series_df,
                            algorithm="CONV_DFFT",
                            input_fmt_input_mode="MATCH")

        # Print the result DataFrame.
        print(uaf_out1.result)

        # Example 2: Execute Convolve() function to convolve two series into new time series using "CONV_SUMMATION" 
        #            algorithm.
        #            Note:
        #               The two input time series "payload_content" are 'MULTIVAR_REAL' and the resultant
        #               time series "payload_content" is 'MULTIVAR_COMPLEX'.

        # Create teradataml TDSeries objects for "payload_content" with the value 'MULTIVAR_REAL'.
        data3_series_df = TDSeries(data=data3,
                                   id="id",
                                   row_index_style="sequence",
                                   row_index="seq",
                                   payload_field=["a_real", "a_imag"],
                                   payload_content="MULTIVAR_REAL")

        data4_series_df = TDSeries(data=data4,
                                   id="id",
                                   row_index_style="sequence",
                                   row_index="seq",
                                   payload_field=["a_real", "a_imag"],
                                   payload_content="MULTIVAR_REAL")
        # Convolve the "data3_series_df" and "data4_series_df" series using the Convolve() function.
        uaf_out2 = Convolve(data1=data3_series_df,
                            data2=data4_series_df,
                            algorithm="CONV_SUMMATION",
                            input_fmt_input_mode="MATCH")

        # Print the result DataFrame.
        print(uaf_out2.result)
    """
    