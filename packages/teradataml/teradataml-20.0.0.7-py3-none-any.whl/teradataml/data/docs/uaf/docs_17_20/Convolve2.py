def Convolve2(data1=None, data1_filter_expr=None, data2=None, 
              data2_filter_expr=None,
              input_fmt_input_mode=None, **generic_arguments):
    """
    DESCRIPTION:
        The Convolve2() function uses two matrices as input. One matrix is
        the image in pixels, and the other matrix is the filter.
        Smaller images with results sets smaller than 128 by 128
        use summation. Larger images use the Discrete Fast Fourier
        Transform (DFFT) method.


    PARAMETERS:
        data1:
            Required Argument.
            Specifies the matrix for the image to be filtered.
            The matrices have the following characteristics:
                1. The matrix can have any supported payload content as mentioned below:
                    * REAL
                    * COMPLEX
                    * MULTIVAR_REAL
                    * MULTIVAR_COMPLEX
                2. The following combinations are supported for
                   MULTIVAR varieties:
                    * For all MULTIVAR types: Both multivariate matrixes
                      are of the same content type, and both matrixes have 
                      the same number of payload fields.
                    * For MULTIVAR_REAL: One input is a MULTIVAR content matrix
                      having greater than one payload field, and the other matrix
                      is a REAL content series having just one payload field.
                    * For the MULTIVAR_COMPLEX: One input is a MULTIVAR content
                      matrix having greater than one pair of fields, and
                      the other matrix is a MULTIVAR content of the same 
                      type having just one pair of payload fields.
            Types: TDMatrix

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Required Argument.
            Specifies the actual filter kernel matrix for filtering image.
            The matrices have the following characteristics:
                1. The matrix can have any supported payload content as mentioned below:
                    * REAL
                    * COMPLEX
                    * MULTIVAR_REAL
                    * MULTIVAR_COMPLEX
                2. The following combinations are supported for
                   MULTIVAR varieties:
                    * For all MULTIVAR types: Both multivariate matrixes
                      are of the same content type, and both matrixes have 
                      the same number of payload fields.
                    * For MULTIVAR_REAL: One input is a MULTIVAR content matrix
                      having greater than one payload field, and the other matrix
                      is a REAL content series having just one payload field.
                    * For the MULTIVAR_COMPLEX: One input is a MULTIVAR content
                      matrix having greater than one pair of fields, and
                      the other matrix is a MULTIVAR content of the same 
                      type having just one pair of payload fields.
            Types: TDMatrix

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        input_fmt_input_mode:
            Required Argument.
            Specifies the input mode supported by the function.
            Permitted Values:
                1. ONE2ONE: Both the primary and secondary matrix
                   specifications contain a matrix name which identifies
                   the two matrixes in the function.
                2. MANY2ONE: The MANY specification is the primary matrix
                   declaration. The secondary matrix specification contains
                   a matrix name that identifies the single secondary matrix.
                3. MATCH: Both matrixes are defined by their respective
                   matrix specification MATRIX_ID declarations.
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
        Instance of Convolve2.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as Convolve2_obj.<attribute_name>.
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
        load_example_data("uaf", ["Convolve2ValidLeft", "Convolve2RealsLeft"])

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("Convolve2ValidLeft")
        data2 = DataFrame.from_table("Convolve2ValidLeft")
        data3 = DataFrame.from_table("Convolve2RealsLeft")
        data4 = DataFrame.from_table("Convolve2RealsLeft")

        # Example 1: Apply the Convolve2() function when payload fields of two matrices
        #            are the different to convolve two matrices into a new source 
        #            image matrix.

        # Create teradataml TDMatrix objects with different payload fields.
        data1_matrix_df = TDMatrix(data=data1,
                                   id='id',
                                   row_index_style="sequence",
                                   row_index='row_i',
                                   column_index_style="sequence",
                                   column_index='column_i',
                                   payload_field=["B"],
                                   payload_content="REAL")

        data2_matrix_df = TDMatrix(data=data2,
                                   id='id',
                                   row_index_style="sequence",
                                   row_index='row_i',
                                   column_index_style="sequence",
                                   column_index='column_i',
                                   payload_field=["A"],
                                   payload_content="REAL")

        # Convolve the "data1_matrix_df" and "data2_matrix_df" matrices using the Convolve2() function.
        uaf_out1 = Convolve2(data1=data1_matrix_df,
                             data2=data2_matrix_df,
                             input_fmt_input_mode="MATCH")

        # Print the result DataFrame.
        print(uaf_out1.result)

        # Example 2: Apply the Convolve2() function when payload fields of two matrices
        #            are the same to convolve two matrices into a new source image matrix 

        # Create teradataml TDMatrix objects with same payload fields.
        data3_matrix_df = TDMatrix(data=data3,
                                   id='id',
                                   row_index_style="sequence",
                                   row_index='row_seq',
                                   column_index_style="sequence",
                                   column_index='col_seq',
                                   payload_field=["A"],
                                   payload_content="REAL")

        data4_matrix_df = TDMatrix(data=data4,
                                   id='id',
                                   row_index_style="sequence",
                                   row_index='row_seq',
                                   column_index_style="sequence",
                                   column_index='col_seq',
                                   payload_field=["A"],
                                   payload_content="REAL")
                                   
        # Convolve the "data3_matrix_df" and "data4_matrix_df" matrices using the Convolve2() function.
        uaf_out2 = Convolve2(data1=data3_matrix_df,
                             data2=data4_matrix_df,
                             input_fmt_input_mode="MATCH")

        # Print the result DataFrame.
        print(uaf_out2.result)
    """
    