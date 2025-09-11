def IDFFT2(data=None, data_filter_expr=None, human_readable=True,
           output_fmt_content=None,
           **generic_arguments):
    """
    DESCRIPTION:
        The IDFFT2() function simply reverses the 2D Fourier Transform. It
        takes either a logical matrix containing
        Fourier coefficients in the form of complex number
        elements, or, alternatively, in the form of amplitude-phase
        pair (polar form) elements as inputs. The function then runs them
        through a reverse-transform summation formula, and outputs
        the original logical matrix (original 2D array) that was
        input into the DFFT2() to generate the Fourier
        coefficients.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a logical matrix or TDAnalyticResult object on the data
            that has been populated previously with 2D Fourier Transform
            coefficients. The calculated coefficients may exist
            in either of the following forms:
                1. complex numbers - real and imaginary pairs.
                2. amplitude-phase pairs.
            Types: TDMatrix, TDAnalyticResult

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

        output_fmt_content:
            Optional Argument.
            Specifies the Fourier coefficient's output form.
            The default value is dependent on the datatype
            of the input series, a single var input
            generates COMPLEX output content by default,
            a multi var input generates
            MULTIVAR_COMPLEX output content by default.
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
        Instance of IDFFT2.
        Output teradataml DataFrames can be accessed using attribute
        references, such as IDFFT2_obj.<attribute_name>.
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
        load_example_data("uaf", ["dfft2conv_real_4_4"])

        # Compute the two-dimension fourier transform using the
        # input matrix with real numbers only for the matrix id 33.

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("dfft2conv_real_4_4")

        # Create teradataml TDMatrix object.
        td_matrix = TDMatrix(data=data,
                             id="id",
                             row_index="row_i",
                             row_index_style="SEQUENCE",
                             column_index="column_i",
                             column_index_style="SEQUENCE",
                             payload_field="magnitude",
                             payload_content="REAL")

        filter_expr = td_matrix.id==33
        dfft2 = DFFT2(data=td_matrix,
                      data_filter_expr=filter_expr,
                      freq_style="K_INTEGRAL",
                      human_readable=False,
                      output_fmt_content="COMPLEX")

        # Example 1: Compute the inverse of two-dimension fourier transform using matrix
        #            with complex numbers.

        # Create teradataml TDMatrix object.
        data_matrix_df = TDMatrix(data=dfft2.result,
                                  id="id",
                                  row_index="ROW_I",
                                  row_index_style="SEQUENCE",
                                  column_index="COLUMN_I",
                                  column_index_style="SEQUENCE",
                                  payload_field=["REAL_magnitude", "IMAG_magnitude"],
                                  payload_content="COMPLEX")

        uaf_out = IDFFT2(data=data_matrix_df, human_readable=False)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Compute the inverse of two-dimension fourier transform using
        #            TDAnalyticResult instead of matrix with complex numbers.

        # Create teradataml TDAnalyticResult object.
        art_df = TDAnalyticResult(data=dfft2.result)

        uaf_out = IDFFT2(data=art_df, human_readable=False)

        # Print the result DataFrame.
        print(uaf_out.result)

    """

