def BinaryMatrixOp(data1=None, data1_filter_expr=None, data2=None, 
                   data2_filter_expr=None, math_op=None,
                   input_fmt_input_mode=None, 
                   output_fmt_index_style="NUMERICAL_SEQUENCE", 
                   **generic_arguments):
    """
    DESCRIPTION:
        The BinaryMatrixOp() function performs a point-wise mathematical
        operation on two matrices with an equal number of wavelets and for
        which corresponding wavelets have an equal number of data points.

        A point-wise operation signifies that a mathematical operation is
        performed on one sample point at a time. Allowed mathematical
        operations are addition, subtraction, multiplication and division.
        
        The BinaryMatrixOp() function takes two equally sized logical-runtime
        matrices as input - the first matrix referenced in the function call
        ("data1") is a primary matrix, whereas the second matrix referenced
        ("data2") is a secondary matrix. The significance of being a primary
        or secondary matrix in each of the allowed mathematical operation is as
        follows:
            * SUB: The secondary matrix is subtracted from the primary matrix.
            * ADD: The secondary matrix is added to the primary matrix.
            * MUL: The primary matrix is multiplied by the secondary matrix.
            * DIV: The primary matrix is divided by the secondary matrix.
        
        The result matrix produced by the BinaryMatrixOp() function is of 
        the same size, 'N * M', as of its inputs and inherits the TDMatrix
        identifier (id), from the primary matrix.
        
        The BinaryMatrixOp() function can be configured to operate in one
        of three input modes - ONE2ONE, MANY2ONE, and MATCH. These modes
        determine the number of primary matrices and number of secondary
        matrices involved in the operation, as well as determining how the
        primary and secondary matrix will be matched together.

        The common uses of BinaryMatrixOp() function are:
            * Addition:       Restore trends to a time matrix before using the
                              model for forecasting.
            * Subtraction:    Subtract trends from a time matrix to create a
                              model from it.
            * Multiplication: Apply a low pass, band pass, or high pass
                              filter to a time matrix.
            * Division:       Divide the primary matrix by the secondary matrix.


    PARAMETERS:
        data1:
            Required Argument.
            Specifies the primary matrix in the mathematical operation.
            Note:
                The matrices specified in "data1" and "data2" must have
                the same dimensions.
            Types: TDMatrix

        data1_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data1".
            Types: ColumnExpression

        data2:
            Required Argument.
            Specifies the secondary matrix in the mathematical operation.
            Note:
                The matrices specified in "data1" and "data2" must have
                the same dimensions.
            Types: TDMatrix

        data2_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data2".
            Types: ColumnExpression

        math_op:
            Required Argument.
            Specifies the mathematical operation to be performed
            between "data1" and "data2".
            Permitted Values:
                * SUB: The secondary matrix is subtracted from the primary matrix.
                       This subtracts trends from a time matrix to create a model
                       from it.
                * ADD: The secondary matrix is added to the primary matrix.
                       This restores trends to a time matrix before using the model
                       for forecasting.
                * MUL: The primary matrix is multiplied by the secondary matrix.
                       This applies a low pass, band pass, or high pass filter to
                       a time matrix.
                * DIV: The primary matrix is divided by the secondary matrix.
                       This divides the primary matrix by the secondary matrix.
            Types: str

        input_fmt_input_mode:
            Required Argument.
            Specifies the input mode supported by the function.
            Permitted Values:
                * ONE2ONE: Both the primary and secondary matrix
                           specifications contain a matrix name
                           which identifies each of the two matrices
                           in the function.
                * MANY2ONE: The MANY specification is the primary matrix
                            declaration. The secondary matrix specification
                            contains a matrix name that identifies the
                            single secondary matrix.
                * MATCH: Both matrices are defined by their respective matrix id.
            Types: str

        output_fmt_index_style:
            Optional Argument.
            Specifies the index style of the output format.
            Default Value: NUMERICAL_SEQUENCE
            Permitted Values: NUMERICAL_SEQUENCE, FLOW_THROUGH
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
        Instance of BinaryMatrixOp.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as BinaryMatrixOp_obj.<attribute_name>.
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
        load_example_data("uaf", ["binary_matrix_complex_left", "binary_matrix_complex_right"])
        load_example_data("uaf", ["binary_matrix_real_left", "binary_matrix_real_right"])

        # Create teradataml DataFrame objects.
        data1 = DataFrame.from_table("binary_matrix_complex_left")
        data2 = DataFrame.from_table("binary_matrix_complex_right")
        data3 = DataFrame.from_table("binary_matrix_real_left")
        data4 = DataFrame.from_table("binary_matrix_real_right")

        # Create teradataml TDMatrix objects.
        binary_matrix_complex_left = TDMatrix(data=data1,
                                              id="id",
                                              row_index="seq",
                                              column_index="tick",
                                              row_index_style="SEQUENCE",
                                              column_index_style="SEQUENCE",
                                              payload_field=["real_val", "imaginary_val"],
                                              payload_content="COMPLEX")

        binary_matrix_complex_right = TDMatrix(data=data2,
                                               id="id",
                                               row_index="seq",
                                               column_index="tick",
                                               row_index_style="SEQUENCE",
                                               column_index_style="SEQUENCE",
                                               payload_field=["real_val", "imaginary_val"],
                                               payload_content="COMPLEX")

        # Example 1 : Perform addition operation in MANY2ONE mode between
        #             two matrices holding COMPLEX payload.
        uaf_out_1 = BinaryMatrixOp(data1=binary_matrix_complex_left,
                                   data2=binary_matrix_complex_right,
                                   data2_filter_expr=binary_matrix_complex_right.id==1,
                                   math_op="ADD",
                                   input_fmt_input_mode="MANY2ONE")

        # Print the result DataFrame.
        print(uaf_out_1.result)

        # Example 2 : Perform multiplication operation in MATCH mode between
        #             two matrices holding REAL payload.
        # Create teradataml TDMatrix objects.
        binary_matrix_real_left = TDMatrix(data=data3,
                                           id="id",
                                           row_index="seq",
                                           column_index="tick",
                                           row_index_style="SEQUENCE",
                                           column_index_style="SEQUENCE",
                                           payload_field="a",
                                           payload_content="REAL")

        binary_matrix_real_right = TDMatrix(data=data4,
                                            id="id",
                                            row_index="seq",
                                            column_index="tick",
                                            row_index_style="SEQUENCE",
                                            column_index_style="SEQUENCE",
                                            payload_field="b",
                                            payload_content="REAL")

        uaf_out_2 = BinaryMatrixOp(data1=binary_matrix_real_left,
                                   data2=binary_matrix_real_right,
                                   math_op="MUL",
                                   input_fmt_input_mode="MATCH")

        # Print the result DataFrame.
        print(uaf_out_2.result)
    
    """
    