def DFFT2(data=None, data_filter_expr=None, zero_padding_ok=True, 
          freq_style="K_INTEGRAL", hertz_sample_rate=None, 
          algorithm=None, human_readable=True, 
          output_fmt_content=None, output_fmt_row_major=True, 
          **generic_arguments):
    """
    DESCRIPTION:
        The DFFT2() function takes a matrix (two-dimensional array) as an input,
        and returns a result matrix whose elements are the computed two-dimension
        Fourier Coefficients for the input matrix.
        The coefficients can be output as complex numbers in either
        rectangular (real, imaginary) or polar (amplitude, phase) form.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a logical matrix or the output of IDFFT2 in ART Spec.
            Elements of the matrix can be either real or complex numbers.
            Types: TDMatrix, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        zero_padding_ok:
            Optional Argument.
            Specifies whether to pad zeros to the end of both the 'row-series'
            and 'column-series' to achieve a more efficient computation of
            the FFT coefficients.
            When set to True, row-series and column-series are padded,
            otherwise they are not.
            Default Value: True
            Types: bool

        freq_style:
            Optional Argument.
            Specifies format/values associated with the x-axis and y-axis
            of the output.
            Permitted Values:
                * K_INTEGRAL: Integer representation.
                * K_SAMPLE_RATE: Integer normalized to number entries,
                                 with ranges from -0.5 to +0.5.
                * K_RADIANS: Radian ranges from -π to +π.
                * K_HERTZ: Frequency in hertz. Must be used in conjunction
                           with HERTZ_SAMPLE_RATE.
            Default Value: K_INTEGRAL
            Types: str

        hertz_sample_rate:
            Optional Argument.
            Specifies a floating point constant representing the sample rate
            in hertz. A value of 10000.0 means that the sample points were
            obtained by sampling at a rate of 10,000 hertz. The hertz
            interpretation will be applied to both the row index and
            column index.
            Note:
                Applicable only when "freq_style" is set to 'K_HERTZ'.
            Types: int OR float

        algorithm:
            Optional Argument.
            Specifies the algorithm to be used for the primary DFFT
            calculation. If the argument is not provided, the
            internal DFFT planner selects the most efficient
            algorithm for the operation.
            Note:
                For best performance, do not include this parameter.
                Instead, let the internal DFFT planner select the best
                algorithm.
            Permitted Values: COOLEY_TUKEY, SINGLETON
            Types: str

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

        output_fmt_content:
            Optional Argument.
            Specifies the Fourier coefficient's output form.
                The default value is dependent on the datatype
                of the input series:
                  * A single var input generates COMPLEX output content by default.
                  * A multi var input generates MULTIVAR_COMPLEX output content by default.
                Note:
                    1. Users can use COMPLEX or MULTIVAR_COMPLEX to
                       request the Fourier coefficients in rectangular form.
                    2. AMPL_PHASE_RADIANS, AMPL_PHASE_DEGREES, AMPL_PHASE,
                       MULTIVAR_AMPL_PHASE_RADIANS, MULTIVAR_AMPL_PHASE or
                       MULTIVAR_AMPL_PHASE_DEGREES can be used to output
                       the Fourier coefficients in the polar form and to further
                       request the phase to be output in
                       radians or degrees.
                    3. AMPL_PHASE is one of the permitted
                       values, it is synonymous with AMPL_PHASE_RADIANS.
                    4. MULTIVAR_AMPL_PHASE is equivalent to
                       MULTIVAR_AMPL_PHASE_RADIANS.
                Permitted Values: COMPLEX,
                                  AMPL_PHASE_RADIANS,
                                  AMPL_PHASE_DEGREES,
                                  AMPL_PHASE,
                                  MULTIVAR_COMPLEX,
                                  MULTIVAR_AMPL_PHASE_RADIANS,
                                  MULTIVAR_AMPL_PHASE_DEGREES,
                                  MULTIVAR_AMPL_PHASE
                Types: str

        output_fmt_row_major:
            Optional Argument.
            Species whether the matrix output should be in a row-major-centric
            or column-major-centric manner.
            When set to True, the output is in row-major-centric manner,
            otherwise the output is in column-major-centric manner.
            Default Value: True
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
        Instance of DFFT2.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as DFFT2_obj.<attribute_name>.
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
        load_example_data("uaf", ["dfft2_size4_real"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("dfft2_size4_real")

        # Create teradataml TDMatrix object.
        td_matrix = TDMatrix(data=data,
                             id="buoy_id",
                             row_index="row_i",
                             row_index_style="SEQUENCE",
                             column_index="column_i",
                             column_index_style="SEQUENCE",
                             payload_field="magnitude",
                             payload_content="REAL")

        # Example 1 : Compute the two-dimension fourier transform using the
        #             input matrix with real numbers only for the matrix id 33.
        filter_expr = td_matrix.buoy_id==3
        uaf_out = DFFT2(data=td_matrix,
                        data_filter_expr=filter_expr,
                        freq_style="K_INTEGRAL",
                        human_readable=False,
                        output_fmt_content="COMPLEX")

        # Print the result DataFrame.
        print(uaf_out.result)

    """
