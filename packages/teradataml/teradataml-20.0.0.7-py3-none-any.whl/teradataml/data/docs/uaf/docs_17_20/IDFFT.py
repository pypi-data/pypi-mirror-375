def IDFFT(data=None, data_filter_expr=None, human_readable=True,
          **generic_arguments):
    """
    DESCRIPTION:
        The IDFFT() function reverses the effects of the forward
        transform (DFFT() function). It takes a series containing Fourier
        Coefficients as an input, and returns the original series that
        was input into the DFFT() function to generate the coefficients.
        The Fourier Coefficients can be in either the rectangular
        (real, imaginary) or polar (amplitude, phase) formats.

        The following procedure is an example of how to use IDFFT() when
        convolving two series with digital signal processing:
            1. Use DFFT() on series 1 and series 2 to get dataframes named
               'dfftRes1' and 'dfftRes2', respectively.
            2. Use BinarySeriesOp() to do point-wise multiplication using
               'dfftRes1' and 'dfftRes2'.
            3. Use IDFFT() on the output of BinarySeriesOp() function to get
               the convolved result of the two series.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a logical-runtime series, that is,
            'a 1D array' as its input, that has been populated
            previously with Fourier Transform coefficients.
            The calculated coefficients may exist
            in either of the following forms:
                1. complex numbers - real and imaginary pairs
                2. amplitude-phase pairs
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        human_readable:
            Optional Argument.
            Specifies whether the input rows are in human-readable / plottable form,
            or if they are output in the raw-form. Human-readable
            output is symmetric around 0, such as -3, -2, -1, 0, 1, 2, 3.
            Raw output is sequential, starting at zero, such as 0, 1, 2, 3.
            When set to True the output is in human-readable form,
            otherwise the output is in raw form.
            Default Value: True
            Types: bool

        **generic_arguments:
            Specifies the generic keyword arguments of UAF functions.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the
                    function in a table or not. When set to True,
                    results are persisted in a table otherwise,
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
        Instance of IDFFT.
        Output teradataml DataFrames can be accessed using attribute
        references, such as IDFFT_obj.<attribute_name>.
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
        load_example_data("uaf", "mvdfft8")

        # Compute the complex Fourier Transform Coefficients using a
        # sequential series.

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("mvdfft8")

        # Create teradataml TDSeries object which is an input to DFFT function.
        data_series_df = TDSeries(data=data,
                                  id="sid",
                                  row_index="n_seqno",
                                  row_index_style="SEQUENCE",
                                  payload_field="magnitude1",
                                  payload_content="REAL")

        # Execute DFFT function.
        DFFT_result = DFFT(data=data_series_df,
                           human_readable=True,
                           output_fmt_content='COMPLEX')

        # Example 1: Compute the inverse fourier transform using TDAnalyticResult as input.
        # Create teradataml TDAnalyticResult object to be passed as an
        # input to IDFFT.

        idfft_art_spec = TDAnalyticResult(data=DFFT_result.result,
                                          payload_content="COMPLEX",
                                          payload_field=["REAL_MAGNITUDE1",
                                                         "IMAG_MAGNITUDE1"])

        # Execute IDFFT function.
        uaf_out = IDFFT(data=idfft_art_spec, human_readable=True)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Compute the inverse fourier transform using TDSeries as input.
        # Create a teradataml TDSeries object.

        idfft_series_spec = TDSeries(data=DFFT_result.result,
                                     id="sid",
                                     row_index="sid",
                                     row_index_style="SEQUENCE",
                                     payload_content="COMPLEX",
                                     payload_field=["REAL_MAGNITUDE1",
                                                    "IMAG_MAGNITUDE1"])

        # Execute IDFFT function.
        uaf_out = IDFFT(data=idfft_series_spec, human_readable=True)

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    