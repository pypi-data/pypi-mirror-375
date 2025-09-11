def WindowDFFT(data=None, data_filter_expr=None, dfft_algorithm=None, 
               dfft_zero_padding_ok=True, dfft_freq_style="K_INTEGRAL", 
               dfft_hertz_sample_rate=None, dfft_human_readable=True, 
               window_size_num=None, window_size_perc=None, 
               window_overlap=0, window_is_symmetric=True, 
               window_scale=None, window_type=None, 
               window_exponential_center=None, 
               window_exponential_tau=None, window_gaussian_std=None, 
               window_general_cosine_coeff=None, 
               window_general_gaussian_shape=None, 
               window_general_gaussian_sigma=None, 
               window_general_hamming_alpha=None, 
               window_kaiser_beta=None, window_taylor_num_sidelobes=4, 
               window_taylor_sidelobe_suppression=30, 
               window_taylor_norm=True, window_tukey_alpha=None, 
               output_fmt_content=None, **generic_arguments):
    """
    DESCRIPTION:
        WindowDFFT() function applies a user-selected window to data before 
        processing it with DFFT(). Windows are used to remove 
        noise or spectral leakage. The window type is determined 
        for the specific use case based on signal frequency, 
        amplitude, strength and so on.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the time series or spatial series.
            Types: TDSeries, TDAnalyticResult

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        dfft_algorithm:
            Optional Argument.
            Specifies the user-defined algorithm that bypasses the
            internal DFFT planner, and influences the core DFFT
            algorithm associated with the primary DFFT calculation.
            Note:
            * When "dfft_algorithm" is not passed, then the internal DFFT planner selects 
              the most efficient algorithm for the operation.
            Permitted Values: COOLEY_TUKEY, SINGLETON
            Types: str

        dfft_zero_padding_ok:
            Optional Argument.
            Specifies whether to add zeros to the end of a given
            series to achieve a more efficient computation for the
            Fast Fourier Transform coefficients.
            Default Value: True
            Types: bool

        dfft_freq_style:
            Optional Argument.
            Specifies the format or values associated with the x-axis of the
            output.
            Permitted Values: 
                * K_INTEGRAL: Integer representation.
                * K_SAMPLE_RATE: Integer normalized to number entries, with ranges from -0.5 to +0.5.
                * K_RADIANS: Radian ranges from -π to +π.
                * K_HERTZ: Frequency in hertz. Must be used in conjunction with "dfft_hertz_sample_rate".
            Default Value: K_INTEGRAL
            Types: str

        dfft_hertz_sample_rate:
            Optional Argument.
            Specifies the sample rate as a floating point constant, in
            hertz. A value of 10000.0 indicates that the sample 
            points were obtained by sampling at a rate of 10,000 
            hertz.
            Note:
                * "dfft_hertz_sample_rate" is only valid with "dfft_freq_style".
            Types: float

        dfft_human_readable:
            Optional Argument.
            Specifies whether the produced output rows are in human-readable or raw form.
            Human-readable output is symmetric around 0, such as -3, -2, -1, 0, 1, 2, 3 whereas
            raw output is sequential, starting at zero, such as 0, 1, 2, 3.
            Permitted Values:
                * True: Human-readable output.
                * False: Raw output.
            Default Value: True
            Types: bool

        window_size_num:
            Optional Argument.
            Specifies the size of the window.
            Note:
               * "window_size_num" must be greater than zero.
               * "window_size_num" and "window_size_perc" are mutually exclusive.
            Types: int

        window_size_perc:
            Optional Argument.
            Specifies the size of the window within a series as a percentage.
            Note:
               * "window_size_perc" must be greater than zero.
               * "window_size_num" and "window_size_perc" are mutually exclusive.
            Types: float

        window_overlap:
            Optional Argument.
            Specifies the number of values by which the window slides down for 
            each DFFT calculation within a series.
            Note:
                * The value must be less than the window size.
                * To use fraction form, use "window_size_perc".
            Default Value: 0
            Types: int

        window_is_symmetric:
            Optional Argument.
            Specifies whether to use a symmetric or periodic window.
            Permitted Values:
                * False: Periodic
                * True: Symmetric
            Default Value: True
            Types: bool

        window_scale:
            Optional Argument.
            Specifies the spectral density type applied to the result values.
            Permitted Values: DENSITY, SPECTRUM
            Types: str

        window_type:
            Optional Argument.
            Specifies the type of window to use.
            Note: 
                * Some windows have additional options such as Taylor, in which case refer 
                  to the Taylor parameter for specific Taylor window options.
            Permitted Values: 
                * BARTHANN
                * BARTLETT, 
                * BLACKMAN,               
                * BLACKMANHARRIS, 
                * BOHMAN, 
                * BOXCAR, 
                * COSINE, 
                * EXPONENTIAL,
                * FLATTOP,
                * GAUSSIAN, 
                * GENERAL_COSINE, 
                * GENERAL_GAUSSIAN, 
                * GENERAL_HAMMING, 
                * HAMMING, HANN, 
                * KAISER, 
                * NUTTALL, 
                * PARZEN, 
                * TAYLOR, 
                * TRIANG, 
                * TUKEY
            Types: str

        window_exponential_center:
            Optional Argument.
            Specifies the center of the window. 
            It is a parameter for "window_type" as EXPONENTIAL.
            The default value is (windowSize - 1 ) / 2.
            Types: float

        window_exponential_tau:
            Optional Argument.
            Specifies the amount of window decay.
            It is a parameter for window_type as EXPONENTIAL.
            If the "window_exponential_center" is zero, then use ( windowSize - 1 ) / ln( x ) if x is the 
            fractional part of the window remaining at the end of 
            the window.
            Types: float

        window_gaussian_std:
            Optional Argument. Required if "window_type" is GAUSSIAN.
            Specifies the standard deviation of the Gaussian window.
            Types: float

        window_general_cosine_coeff:
            Optional Argument. Required if "window_type" is GENERAL_GUASSIAN.
            Specifies the list of weighing coefficients.
            Types: float, list of float

        window_general_gaussian_shape:
            Optional Argument. Required if "window_type" is GENERAL_GUASSIAN.
            specifies the gaussian shape. 
            Types: float

        window_general_gaussian_sigma:
            Optional Argument. Required if "window_type" is GENERAL_GUASSIAN.
            Specifies the standard deviation value.
            Types: float

        window_general_hamming_alpha:
            Optional Argument. Required if "window_type" is GENERAL_HAMMING.
            Specifies the value of the window coefficient.
            Types: float

        window_kaiser_beta:
            Optional Argument. Required if "window_type" is KAISER.
            Specifies the shape between the main lobe width and side
            lobe level.
            Types: float

        window_taylor_num_sidelobes:
            Optional Argument.
            Specifies the number of nearly constant level sidelobes
            adjacent to the main lobe.
            Default Value: 4
            Types: int

        window_taylor_sidelobe_suppression:
            Optional Argument.
            Specifies the suppression level of the side lobe in decibels
            relative to the DC gain of the main lobe.
            Default Value: 30
            Types: float

        window_taylor_norm:
            Optional Argument.
            Specifies the normalization factor for the Taylor window.
            Permitted Values:
                * False: For an even sized window, divides the window by the 
                         value that would occur between the two middle values.
                * True : For an odd sized window, divides the window by the 
                         largest (middle) value.
            Default Value: True
            Types: bool

        window_tukey_alpha:
            Optional Argument. Required if "window_type" is TUKEY.
            Specifies the shape of the window inside the cosine-tapered region.
            A value of 0 is a rectangular window and value of 1 is the same as a Hann window. 
            Types: float

        output_fmt_content:
            Optional Argument.
            Specifies how the Fourier coefficients should be output.
            Permitted Values: 
                * COMPLEX
                * AMPL_PHASE_RADIANS
                * AMPL_PHASE_DEGREES
                * AMPL_PHASE
                * MULTIVAR_COMPLEX
                * MULTIVAR_AMPL_PHASE_RADIANS
                * MULTIVAR_AMPL_PHASE_DEGREES
                * MULTIVAR_AMPL_PHASE
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
        Instance of WindowDFFT.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as WindowDFFT_obj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            1. result


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage, before importing the
        #        function in user space.
        #     2. User can import the function, if it is available on
        #        Vantage user is connected to.
        #     3. To check the list of UAF analytic functions available
        #        on Vantage user connected to, use
        #        "display_analytic_functions()".

        # Check the list of available UAF analytic functions.
        display_analytic_functions(type="UAF")

        # Import function WindowDFFT.
        from teradataml import WindowDFFT

        # Load the example data.
        load_example_data("uaf", ["windowdfft"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("windowdfft")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                   id="id",
                                   row_index="row_i",
                                   row_index_style="SEQUENCE",
                                   payload_field=["v2"],
                                   payload_content="REAL")

        # Example 1: Execute WindowDFFT() function to apply a window to the data before processing it with DFFT()
        #            with window_type as BOHMAN and dfft_human_readable is True.
        uaf_out = WindowDFFT(data=data_series_df,
                             window_size_num=15,
                             window_overlap=2,
                             window_type="BOHMAN",
                             window_is_symmetric=True,
                             window_scale="SPECTRUM",
                             dfft_algorithm="SINGLETON",
                             dfft_zero_padding_ok=True,
                             dfft_freq_style="K_INTEGRAL",
                             dfft_human_readable=True)

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Execute WindowDFFT() function to apply a window to the data before processing it with DFFT()
        #            with additional window parameters for window_type as GENERAL_COSINE and dfft_human_readable is False.
        uaf_out1 = WindowDFFT(data=data_series_df,
                              window_size_num=15,
                              window_overlap=2,
                              window_type="GENERAL_COSINE",
                              window_general_cosine_coeff=[2.3,3.7],
                              window_is_symmetric=True,
                              window_scale="SPECTRUM",
                              dfft_algorithm="SINGLETON",
                              dfft_zero_padding_ok=True,
                              dfft_freq_style="K_INTEGRAL",
                              dfft_human_readable=False)

        # Print the result DataFrame.
        print(uaf_out1.result)

    """
    