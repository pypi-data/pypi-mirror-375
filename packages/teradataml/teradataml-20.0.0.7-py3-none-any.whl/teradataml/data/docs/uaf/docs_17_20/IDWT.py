def IDWT(data1=None, data1_filter_expr=None, data2=None, 
         data2_filter_expr=None, wavelet=None, mode="symmetric", 
         part=None, input_fmt_input_mode=None, 
         output_fmt_index_style="NUMERICAL_SEQUENCE", 
         **generic_arguments):
    """
    DESCRIPTION:
        IDWT() is a function that performs inverse discrete wavelet transform (IDWT).

    PARAMETERS:
        data1:
            Required Argument.
            Specifies the input series. Multiple
            payloads are supported, and each payload column is 
            transformed independently. Only REAL or MULTIVAR_REAL
            payload content types are supported.
            Types: TDSeries

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Optional Argument.
            Specifies the input series. The series specifies the filter.
            It should have two payload columns corresponding to low
            and high pass filters.
            Only MULTIVAR_REAL payload content type is supported.
            Types: TDSeries

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        wavelet:
            Optional Argument.
            Specifies the name of the wavelet.
            Permitted Values:
                * Daubechies: 'db1' or 'haar', 'db2', 'db3', .... ,'db38'
                * Coiflets: 'coif1', 'coif2', ... , 'coif17'
                * Symlets: 'sym2', 'sym3', ... ,' sym20'
                * Discrete Meyer: 'dmey'
                * Biorthogonal: 'bior1.1', 'bior1.3', 'bior1.5',
                                'bior2.2', 'bior2.4', 'bior2.6',
                                'bior2.8', 'bior3.1', 'bior3.3',
                                'bior3.5', 'bior3.7', 'bior3.9',
                                'bior4.4', 'bior5.5', 'bior6.8'
                * Reverse Biorthogonal: 'rbio1.1', 'rbio1.3',
                                        'rbio1.5' 'rbio2.2',
                                        'rbio2.4', 'rbio2.6',
                                        'rbio2.8', 'rbio3.1',
                                        'rbio3.3', 'rbio3.5',
                                        'rbio3.7','rbio3.9',
                                        'rbio4.4', 'rbio5.5',
                                        'rbio6.8'
            Note:
                * If 'wavelet' is specified, do not include a second
                  input series for the function. Otherwise, include
                  a second input series to provide the filter.
                * Data type is case-sensitive.
            Types: str

        mode:
            Optional Argument.
            Specifies the signal extension mode.
            Data type is case-insensitive.
            Permitted Values:
                * symmetric, sym, symh
                * reflect, symw
                * smooth, spd, sp1
                * constant, sp0
                * zero, zpd
                * periodic, ppd
                * periodization, per
                * antisymmetric, asym, asymh
                * antireflect, asymw
            Default Value: symmetric
            Types: str

        part:
            Optional Argument.
            Specifies the indicator that the input is partial decomposition
            result.
            Note:
                Data type is case-insensitive.
            Permitted Values:
                * a - the approximation
                * d - the detail of decomposition of result.
            Types: str

        input_fmt_input_mode:
            Optional Argument.
            Specifies the input mode supported by the function.
            When there are two input series, then the input_fmt_input_mode
            specification is mandatory.
            Permitted Values:
                * ONE2ONE: Both the primary and secondary series
                           specifications contain a series name which
                           identifies the two series in the function.
                * MANY2ONE: The MANY specification is the primary series
                            declaration. The secondary series specification
                            contains a series name that identifies the single
                            secondary series.
                * MATCH: Both series are defined by their respective series
                         specification instance name declarations.
            Types: str

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Permitted Values: NUMERICAL_SEQUENCE
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
        Instance of IDWT.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as IDWT_obj.<attribute_name>.
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

        # Import function IDWT.
        from teradataml import IDWT

        # Load the example data.
        load_example_data("uaf", ["idwt_dataTable", "idwt_filterTable"])

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("idwt_dataTable")
        data2 = DataFrame.from_table("idwt_filterTable")

        # Create teradataml TDSeries objects.
        data1_series_df = TDSeries(data=data1,
                                   id="id",
                                   row_index="rowi",
                                   row_index_style="SEQUENCE",
                                   payload_field=["approx"],
                                   payload_content="REAL")

        data2_series_df = TDSeries(data=data2,
                                   id="id",
                                   row_index="seq",
                                   row_index_style="SEQUENCE",
                                   payload_field=["lo", "hi"],
                                   payload_content="MULTIVAR_REAL")


        # Example 1: Perform inverse discrete wavelet transform using 2 series as input.
        uaf_out = IDWT(data1=data1_series_df,
                       data2=data2_series_df,
                       data2_filter_expr=data2.id==1,
                       input_fmt_input_mode="MANY2ONE",
                       part='a')

        # Print the result DataFrame.
        print(uaf_out.result)

        # Example 2: Perform inverse discrete wavelet transform using 1 series as input and wavelet parameter.

        # Create teradataml TDSeries objects.
        data_series_df = TDSeries(data=data1,
                                  id="id",
                                  row_index="rowi",
                                  row_index_style="SEQUENCE",
                                  payload_field=["approx", "detail"],
                                  payload_content="MULTIVAR_REAL")

        uaf_out = IDWT(data1=data_series_df,
                       wavelet='haar')

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    