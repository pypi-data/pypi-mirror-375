def BinarySeriesOp(data1=None, data1_filter_expr=None, data2=None,
                   data2_filter_expr=None, math_op=None,
                   input_fmt_input_mode=None,
                   output_fmt_index_style="NUMERICAL_SEQUENCE",
                   **generic_arguments):
    """
    DESCRIPTION:
        The BinarySeriesOp() function performs a point wise mathematical
        operation on two time series of equal size.
        The principal mathematical operation can be
        subtraction, addition, multiplication and division.
        It is called a point wise operation because it performs
        the mathematical operation one sample point at a time.

        For example, if the mathematical operation being performed is
        subtraction, then for two series each with N sample points,
        a new series is generated in which:
            * ResultSeries1 =  MinuendSeries1 - SubtrahendSeries1
            * ResultSeries2 =  MinuendSeries2 - SubtrahendSeries2
            * ResultSeries3 =  MinuendSeries3 -SubtrahendSeries3
            ... up to ...
            * ResultSeriesN  = MinuendSeriesN  - SubtrahendSeriesN.

        The result series/1D array produced by the BinarySeriesOp()
        is of the same size 'N' as its inputs.

        BinarySeriesOp() takes two equally sized logical-runtime series
        as input:
            * The first series referenced in the function call as "data1"
              is referred as the primary series.
            * The second series referenced in the function call as "data2"
              is referred as the secondary series.
        The result series always inherits the identifiers,
        series_id from the primary series.

        The BinarySeriesOp() function can be configured to
        operate in one of three input modes - ONE2ONE, MANY2ONE,
        and MATCH. These modes determine the number of primary
        series and number of secondary series involved in the
        operation, as well as determining how the primary and
        secondary series will be matched together.

        Common uses of BinarySeriesOp() are:
            1. Subtracting trends from a time series to create a model from it.
            2. Restoring trends to a time series before using the model for
               forecasting.
            3. As a building block to formulate more complex
               functions.

        For example, convolving in the time domain is point-wise multiplication
        in the frequency domain.
        The following procedure is an example of how
        to use BinarySeriesOp() to convolve two series with
        digital signal processing:
            1. Use DFFT() function on series 1 and series 2 to get dataframes
               named 'dfftRes1' and 'dfftRes2', respectively.
            2. Use BinarySeriesOp() to do point-wise multiplication
               using 'dfftRes1' and 'dfftRes2'.
            3. Use IDFFT() on the output of BinarySeriesOp() to get the
               convolved result of the two series.

    PARAMETERS:
        data1:
            Required Argument.
            Specifies the primary series in the mathematical operation.
            The first input is measured against the second input.
            This series must have the same size as that of the
            second input series specified in "data2".
            Input values are REAL and MUTLIVAR_REAL.
            Function supports one input being univariate and the other being
            multivariate. In particular, the following combinations are
            supported:
                1. For all MULTIVAR varieties: Both multivariate series
                   are of the same content type and both series have
                   the same number of payload fields.
                2. For MULTIVAR_REAL: One input is a MULTIVAR content series
                   having greater than one payload field and the other series
                   is a REAL content series having just one payload field.
                3. For the MULTIVAR_AMPL_PHASE and MULTIVAR_COMPLEX varieties:
                   One input is a MULTIVAR content series having greater than one
                   pair of fields and the other series is a MULTIVAR content of
                   the same type having one pair of payload fields.
            Types: TDSeries

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Required Argument.
            Specifies the secondary series of equal size to be operated on.
            This series must have the same size as that of the
            first input series specified in "data1".
            Input values are REAL and MUTLIVAR_REAL.
            Function supports one input being univariate and the other being
            multivariate. In particular, the following combinations are
            supported:
                1. For all MULTIVAR varieties: Both multivariate series
                   are of the same content type and both series have
                   the same number of payload fields.
                2. For MULTIVAR_REAL: One input is a MULTIVAR content series
                   having greater than one payload field and the other series
                   is a REAL content series having just one payload field.
                3. For the MULTIVAR_AMPL_PHASE and MULTIVAR_COMPLEX varieties:
                   One input is a MULTIVAR content series having greater than one
                   pair of fields and the other series is a MULTIVAR content of
                   the same type having one pair of payload fields.
            Types: TDSeries

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        math_op:
            Required Argument.
            Specifies the mathematical operation to be performed
            between the series passed in "data1" and "data2".
            Permitted Values:
                SUB: Subtract trends from a time series to create a model from it.
                     The series in "data2" is subtracted from the series
                     in "data1".
                ADD: Restore trends to a time series before using the model for forecasting.
                MUL: Apply a low pass, band pass, or high pass filter to a time series.
                DIV: The series in "data1" is divided by the series
                     in "data2".
            Types: str

        input_fmt_input_mode:
            Required Argument.
            Specifies the input mode supported by the function.
            Permitted Values:
                * ONE2ONE: Both the primary and secondary series
                           specifications contain a series name
                           which identifies the two series in the function.
                * MANY2ONE: The MANY specification is the primary series declaration.
                            The secondary series specification contains a series name
                            that identifies the single secondary matrix.
                * MATCH: Both series are defined by their respective
                         series id declarations.
            Types: str

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
        Instance of BinarySeriesOp.
        Output teradataml DataFrames can be accessed using attribute
        references, such as BinarySeriesOp_obj.<attribute_name>.
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
        load_example_data("uaf", ["binary_complex_left", "binary_complex_right"])

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("binary_complex_left")
        data2 = DataFrame.from_table("binary_complex_right")

        # Create teradataml TDSeries objects.
        data1_series_df = TDSeries(data=data1,
                                   id="id",
                                   row_index="seq",
                                   row_index_style="SEQUENCE",
                                   payload_field=["real_val", "imaginary_val"],
                                   payload_content="COMPLEX")

        data2_series_df = TDSeries(data=data2,
                                   id="id",
                                   row_index="seq",
                                   row_index_style= "SEQUENCE",
                                   payload_field=["real_val", "imaginary_val"],
                                   payload_content="COMPLEX")

        # Form the filter expressions to filter the series with id=1.
        data1_filter_expr=data1_series_df.id==1
        data2_filter_expr=data2_series_df.id==1

        # Example 1: Perform addition of two time series of equal size.
        uaf_out = BinarySeriesOp(data1=data1_series_df,
                                 data1_filter_expr=data1_filter_expr,
                                 data2=data2_series_df,
                                 data2_filter_expr=data2_filter_expr,
                                 math_op="ADD",
                                 input_fmt_input_mode="MANY2ONE")

        # Print the result DataFrame.
        print(uaf_out.result)

    """
