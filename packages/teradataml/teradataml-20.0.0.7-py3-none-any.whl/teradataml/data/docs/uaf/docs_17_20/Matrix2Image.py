def Matrix2Image(data=None, data_filter_expr=None, image="PNG", type=None, 
                 colormap="viridis", range=None, red=None, green=None, 
                 blue=None, flip_x=False, flip_y=False, 
                 input_fmt_input_mode=None, 
                 output_fmt_index_style="NUMERICAL_SEQUENCE", 
                 **generic_arguments):
    """
    DESCRIPTION:
        Matrix2Image() function converts a matrix to an image.
        The conversion produces an image using color maps.
        The color image produced by Matrix2Image() is limited to
        8-bit color depth.
        In previous versions, Plot() with MESH option was used to
        convert a matrix to an image. Plot() is limited to a
        single payload.
        Matrix2Image() can combine three payloads to create RGB
        color images.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input matrix.
            Multiple payloads are supported, and each
            payload column is transformed independently.
            Only REAL or MULTIVAR_REAL payload content types are supported.
            Types: TDMatrix

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        image:
            Optional Argument.
            Specifies the image output format.
            It can be PNG or JPG.
            Permitted Values: PNG, JPG
            Default Value: PNG
            Types: str

        type:
            Optional Argument.
            Specifies the type of the image. It can be GRAY, RGB
            or COLORMAP.
                * GRAY has a single payload, the output
                  image is a gray scale image.
                * RGB has three payloads corresponding to RED, GREEN and BLUE channels,
                  the output image is a RGB color image.
                * COLORMAP has a single payload. The output image is a RGB color image.
            Note:
                If there is a single payload, then the default
                type is GRAY. If there are three payloads, then the
                default type is RGB.
            Permitted Values: GRAY, RGB, COLORMAP
            Types: str

        colormap:
            Optional Argument.
            Specifies the colormap to use when the "type" is
            COLORMAP. The values correspond to the colormap of
            Plot(). If not specified, then the default colormap is
            "viridis". The value is case-sensitive.
            Default Value: viridis
            Types: str

        range:
            Optional Argument.
            Specifies the range of the single payload value to be
            scaled. By default, the MIN and MAX values of the
            payload are used as the range. Used when "type" is 'GRAY'
            or 'COLORMAP'.
            Types: int, list of int, float, list of float

        red:
            Optional Argument.
            Specifies the range of the first payload value. By
            default, the MIN and MAX values of the payload are 
            used as the range. It is only used when "type" is 'RGB'.
            Types: int, list of int, float, list of float

        green:
            Optional Argument.
            Specifies the range of the second payload value.By
            default, the MIN and MAX values of the payload are 
            used as the range. It is only used when "type" is 'RGB'.
            Types: int, list of int, float, list of float

        blue:
            Optional Argument.
            Specifies the range of the third payload value. By
            default, the MIN and MAX values of the payload are 
            used as the range. It is only used when "type" is 'RGB'.
            Types: int, list of int, float, list of float

        flip_x:
            Optional Argument.
            Specifies the indicator to flip the image horizontally.
            When set to True, flip the image otherwise, do not
            flip the image.
            Default Value: False
            Types: bool

        flip_y:
            Optional Argument.
            Specifies the indicator to flip the image vertically.
            When set to True, flip the image otherwise,
            do not flip the image.
            Default Value: False
            Types: bool

        input_fmt_input_mode:
            Optional Argument.
            Specifies the input mode supported by the function.
            When there are two input series, then the "input_fmt_input_mode" .
            specification is mandatory.
            Permitted Values:
                * ONE2ONE: Both the primary and secondary series specifications
                           contain a series name which identifies the two series
                            in the function.
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
        Instance of Matrix2Image.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as Matrix2Image_obj.<attribute_name>.
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

        # Import function Matrix2Image.
        from teradataml import Matrix2Image

        # Convert the image to matrix using 'TD_IMAGE2MATRIX' using output as gray.
        import teradataml
        # Drop the image table, matrixTable, matrixTable_rgb if it is present.
        try:
            db_drop_table('imageTable')
            db_drop_table('matrixTable')
            db_drop_table('matrixTable_rgb')
        except:
            pass

        execute_sql('CREATE TABLE imageTable(id INTEGER, image BLOB);')

        file_dir = os.path.join(os.path.dirname(teradataml.__file__), "data")
        with open(os.path.join(file_dir,'peppers.png'), mode='rb') as file:
            fileContent = file.read()

        sql = 'INSERT INTO imageTable VALUES(?, ?);'
        parameters = (1, fileContent)
        execute_sql(sql, parameters)

        execute_sql("CREATE TABLE matrixTable AS (SELECT * FROM TD_IMAGE2MATRIX ( ON (SELECT id, image FROM imageTable) USING OUTPUT ('gray')) t) WITH DATA PRIMARY INDEX (id, y, x);")
        data = DataFrame('matrixTable')

        # Create teradataml TDMatrix object.
        data_matrix_df = TDMatrix(data=data,
                                  id="id",
                                  row_index="Y",
                                  column_index="X",
                                  row_index_style="SEQUENCE",
                                  column_index_style="SEQUENCE",
                                  payload_field="GRAY",
                                  payload_content="REAL"
                                  )

        # Example 1: Generate Gray Scale Image Output with Fixed Range.
        uaf_out = Matrix2Image(data=data_matrix_df,
                               range=[0,255])

        # Print the result DataFrame.
        print(uaf_out.result)


        # Example 2: Generate Gray Scale Image Output with Automatic Range.
        uaf_out = Matrix2Image(data=data_matrix_df)

        # Print the result DataFrame.
        print(uaf_out.result)


        # Example 3: Generate Colormap Image Output.
        uaf_out = Matrix2Image(data=data_matrix_df,
                               type='colormap',
                               colormap='viridis',
                               range=[0,255])

        # Print the result DataFrame.
        print(uaf_out.result)

        # Convert the image to matrix using 'TD_IMAGE2MATRIX' using output as 'rgb'.
        execute_sql("CREATE TABLE matrixTable_rgb AS (SELECT * FROM TD_IMAGE2MATRIX ( ON (SELECT id, image FROM imageTable) USING OUTPUT ('rgb')) t) WITH DATA PRIMARY INDEX (id, y, x);")

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("matrixTable_rgb")

        # Create teradataml TDMatrix object.
        data_matrix_df = TDMatrix(data=data,
                                  id="id",
                                  row_index="Y",
                                  column_index="X",
                                  row_index_style="SEQUENCE",
                                  column_index_style="SEQUENCE",
                                  payload_field=["RED", "BLUE", "GREEN"],
                                  payload_content="MULTIVAR_REAL"
                                  )

        # Example 4: Generate RGB Image Output with All Channels Range Fixed.
        uaf_out = Matrix2Image(data=data_matrix_df,
                               red=[0,255],
                               green=[0,255],
                               blue=[0,255])

        # Print the result DataFrame.
        print(uaf_out.result)


        # Example 5: Generate RGB Image Output with Automatic Range for All Channels.
        uaf_out = Matrix2Image(data=data_matrix_df)

        # Print the result DataFrame.
        print(uaf_out.result)
    
    """
    