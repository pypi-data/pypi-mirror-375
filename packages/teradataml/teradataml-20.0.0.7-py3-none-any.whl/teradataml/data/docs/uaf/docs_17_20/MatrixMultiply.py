def MatrixMultiply(data1=None, data1_filter_expr=None, data2=None, 
                   data2_filter_expr=None, input_fmt_input_mode=None, 
                   **generic_arguments):
    """
    DESCRIPTION:
        The MatrixMultiply() function enables users to create a data series based on two matrixes.
        The source matrixes must have the same number of data points and the same
        number of wavelets.


    PARAMETERS:
        data1:
            Required Argument.
            Specifies the primary matrix.
            Types: TDMatrix

        data1_filter_expr:
            Optional Argument.
            Specifies filter expression for "data1".
            Types: ColumnExpression

        data2:
            Required Argument.
            Specifies secondary matrix of size equal to the size of "data1" matrix to be operated on.
            Types: TDMatrix

        data2_filter_expr:
            Optional Argument.
            Specifies filter expression for "data2".
            Types: ColumnExpression

        input_fmt_input_mode:
            Required Argument.
            Specifies the input mode supported by the function.
            Permitted Values:
                1. ONE2ONE: Both the primary and secondary matrix specifications contain a matrix
                            name which identifies the two matrixes in the function.
                2. MANY2ONE: The MANY specification is the primary matrix declaration. The
                             secondary matrix specification contains a matrix name that identifies the
                             single secondary matrix.
                3. MATCH: Both matrixes are defined by their respective matrix id.
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
        Instance of MatrixMultiply.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as MatrixMultiply_obj.<attribute_name>.
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
        load_example_data("uaf", ["mtx1", "mtx2"])

        # Create teradataml DataFrame objects.
        df1 = DataFrame.from_table("mtx1")
        df2 = DataFrame.from_table("mtx2")

        # Create teradataml TDMatrix objects.
        data1_matrix_df = TDMatrix(data=df1, 
                                   id='buoy_id', 
                                   row_index='row_i',
                                   column_index='column_i', 
                                   row_index_style="SEQUENCE",
                                   column_index_style="SEQUENCE", 
                                   payload_field='speed1',
                                   payload_content='REAL')

        data2_matrix_df = TDMatrix(data=df2, 
                                   id='buoy_id', 
                                   row_index='row_i',
                                   column_index='column_i', 
                                   row_index_style="SEQUENCE",
                                   column_index_style="SEQUENCE", 
                                   payload_field='speed2',
                                   payload_content='REAL')

        # Example 1 : Perform a point-wise mathematical operation against two matrixes
        #             having the same number of wavelets and having the same number of data-points
        #             within a same wavelet-point from the two matrices.
        uaf_out = MatrixMultiply(data1=data1_matrix_df,
                                 data2=data2_matrix_df,
                                 input_fmt_input_mode='MATCH')

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    