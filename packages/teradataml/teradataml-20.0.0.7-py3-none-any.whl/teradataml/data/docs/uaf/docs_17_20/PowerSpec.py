def PowerSpec(data=None, data_filter_expr=None, freq_style=None, 
              hertz_sample_rate=None, zero_padding_ok=True, 
              algorithm=None, incrfourier_interval_length=None, 
              incrfourier_spacing_interval=None, 
              window_name=None, window_param=None, 
              **generic_arguments):
    """
    DESCRIPTION:
        The PowerSpec() function converts a series from the time or spatial
        domain to the frequency domain in order to facilitate frequency
        domain analysis. Its calculations serve to estimate the correct
        power spectrum associated with the series.

        The following procedure is an example of how to use POWERSPEC:
            * Use ArimaEstimate() to identify spectral candidates.
            * Use ArimaValidate() to validate spectral candidates.
            * Use PowerSpec() with "freq_style" argument set to 'K_PERIODICITY'
              to perform spectral analysis.
            * Use DataFrame.plot() to plot the results.
            * Compute the test statistic.
            * Use SignifPeriodicities() on the periodicities of interest.
              More than one periodicities can be entered using the Periodicities
              argument.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the time or spatial domain series.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        freq_style:
            Optional Argument.
            Specifies the axis scale. Following are the description of styles:
                * FREQ_STYLE (FK) : It is 1/P
                * FREQ_STYLE (WK) : It is 2π/P
                * FREQ_STYLE (PERIODICITY) : It is N/k.
            Permitted Values: K_INTEGRAL, K_SAMPLE_RATE, K_RADIANS, 
                              K_HERTZ, K_PERIODICITY
            Types: str

        hertz_sample_rate:
            Optional Argument.
            Specifies floating point constant representing the sample
            rate, in hertz. A value of 10000.0 indicates that the sample
            points were obtained by sampling at a rate of 10,000 hertz.
            Note:
                * Only used with "freq_style" set to 'K_HERTZ'.
            Types: int OR float

        zero_padding_ok:
            Optional Argument.
            Specifies whether to add zeros to the end of a given
            series to achieve a more efficient computation of
            the FFT coefficients. When set to True, zeros are added, 
            otherwise not. 
            Default Value: True
            Types: bool

        algorithm:
            Optional Argument.
            Specifies algorithm to calculate the power spectrum.
            Permitted Values:
                * AUTOCOV : Use the Fourier Cosine of the Auto covariance
                            approach.
                * AUTOCORR : Use the Fourier Cosine of the Auto correlation
                             approach.
                * FOURIER : Use the Fourier Transform approach.
                * INCRFOURIER : Use the Incremental Fourier Transform
                                approach.
            Types: str

        incrfourier_interval_length:
            Optional Argument.
            Specifies interval sampling lengths (L).
            Note:
                * Only valid when "algorithm" is set to 'INCRFOURIER'.
            Types: int

        incrfourier_spacing_interval:
            Optional Argument.
            Specifies the spacing interval (K).
            Note:
                * Only valid when "algorithm" is set to 'INCRFOURIER'.
            Types: int

        window_name:
            Optional Argument.
            Specifies a smoothing window.
            Permitted Values:
                * NONE : Do not apply a smoothing window.
                         This translates into the application of
                         a square wave window, which has a magnitude of '1.0'
                         for the whole duration of the window.
                * TUKEY : Apply a Tukey smoothing window with the supplied
                          alpha value. Must be used with "window_param". 
                * BARTLETT : Apply a Bartlett smoothing window.
                * PARZEN : Apply a Parzen smoothing window.
                * WELCH : Apply a Welch smoothing window.
            Types: str

        window_param:
            Optional Argument.
            Specifies the sample rate, in hertz. Value of 10000.0 indicates
            the sample points were obtained by sampling at a rate of 10,000
            hertz.
            Note:
                * Use when "window_name" is set to 'TUKEY'.
            Types: int OR float

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
        Instance of PowerSpec.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as PowerSpec_obj.<attribute_name>.
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
        load_example_data("uaf", ["test_river2"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("test_river2")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data, id="buoy_id",
                                  row_index="n_seq_no",
                                  row_index_style="SEQUENCE",
                                  payload_field="magnitude",
                                  payload_content="REAL")

        # Example 1 : Converting a series from the time domain to the frequency
        #             domain using AUTOCORR algorithm and window name as Tukey.
        uaf_out = PowerSpec(data=data_series_df,
                            freq_style="K_SAMPLE_RATE",
                            algorithm="AUTOCORR",
                            window_name="TUKEY",
                            window_param=0.5)

        # Print the result DataFrame.
        print(uaf_out.result)
    """
