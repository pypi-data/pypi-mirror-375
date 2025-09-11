def FilterFactory1d(filter_id=None, filter_type=None,
                    window_type=None, filter_length=None,
                    transition_bandwidth=None, low_cutoff=None, 
                    high_cutoff=None, sampling_frequency=None, 
                    filter_description=None, **generic_arguments):
    """
    DESCRIPTION:
        FilterFactory1d() function creates finite impulse response (FIR)
        filter coefficients. The filters are based on certain parameters
        and stored into a common table for reuse.
        Note:
            User needs EXECUTE PROCEDURE privelge on SYSLIB

    PARAMETERS:
        filter_id:
            Required Argument.
            Specifies the filter identifier, based on filter coefficients
            stored in the table.
            Types: int

        filter_type:
            Required Argument.
            Specifies the type of filter to generate.
            Permitted Values:
                * LOWPASS - To remove frequencies above low_cutoff.
                * HIGHPASS - To remove frequencies below high_cutoff.
                * BANDPASS - To remove frequencies below low_cutoff and
                             above high_cutoff.
                * BANDSTOP - To remove frequencies between low_cutoff
                  and high_cutoff.
            Types: str

        window_type:
            Optional Argument.
            Specifies the window function to the filter that maintains a
            smooth drop-off to zero, and avoids extra artifacts in the
            frequency domain. The default is to leave the filter
            coefficients as they are, and not apply any windowing function.
            Permitted Values: BLACKMAN, HAMMING, HANNING, BARTLETT
            Types: str

        filter_length:
            Optional Argument.
            Specifies the length of the filter to generate.
            Overrides "transition_bandwidth" argument if both are supplied,
            and renders the other an optional argument.
            Default is approximately 4/("transition_bandwidth"/
            "sampling_frequency").
            Types: int

        transition_bandwidth:
            Optional Argument.
            Specifies the maximum allowed size for the range of
            frequencies for filter transitions between a passband and stopband.
            This also determines the number of coefficients to be generated.
            Value must be greater than 0.
            A smaller value produces faster drop off at the cost of more coefficients.
            Not used when "filter_length" is supplied.
            Default is bandwidth from "filter_length".
            Types: int OR float

        low_cutoff:
            Optional Argument.
            Specifies  the lower frequency that change between a passband
            and stopband occurs. It must be greater
            than 0. It is not used by default with 'HIGHPASS' filter.
            Types: int OR float

        high_cutoff:
            Optional Argument.
            Specifies the higher frequency that change
            between a passband and stopband occurs. It must be greater
            than 0 and not used by default with 'LOWPASS' filter.
            Types: int OR float

        sampling_frequency:
            Required Argument.
            Specifies the frequency that the data to be filtered was
            sampled. It must be greater than 0.
            Types: int OR float

        filter_description:
            Optional Argument.
            Specifies the description for the filter coefficients
            that contain the same filter ID. Description is only
            written to one row for each filter generated, and 
            ROW_I is 0. Default is a string describing parameters.
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

        # Import function FilterFactory1d.
        from teradataml import FilterFactory1d

        # Example 1: Create finite impulse response (FIR) filter coefficients.
        res = FilterFactory1d(filter_id = 33,
                              filter_type = 'lowpass',
                              window_type = 'blackman',
                              transition_bandwidth = 20.0,
                              low_cutoff = 40.0,
                              sampling_frequency = 200)
        print(res.result)
    
    """
    