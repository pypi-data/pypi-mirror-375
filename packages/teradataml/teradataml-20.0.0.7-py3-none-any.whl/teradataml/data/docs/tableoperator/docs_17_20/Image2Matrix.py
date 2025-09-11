def Image2Matrix(data=None,
                 output='gray',
                 **generic_arguments):
    """
    DESCRIPTION:
        Image2Matrix() function converts an image to a matrix.
        It converts JPEG or PNG images to matrixes with payload values being the pixel values.
        Note:
            * The image size cannot be greater than 16 MB.
            * The image should not exceed 4,000,000 pixels.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the teradataml DataFrame which has image details.
            Types: Teradataml DataFrame

        output:
            Optional Argument.
            Specifies the type of output matrix.
            Default: 'gray'
            Permitted Values:
                'gray': Converts the image to a grayscale matrix.
                'rgb': Converts the image to a RGB matrix.
            Types: str

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in table or not.
                    When set to True, results are persisted in table; otherwise, results
                    are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in volatile table or not.
                    When set to True, results are stored in volatile table, otherwise not.
                    Default Value: False
                    Types: boolean

            Function allows the user to partition, hash, order or local order the input
            data. These generic arguments are available for each argument that accepts
            teradataml DataFrame as input and can be accessed as:
                * "<input_data_arg_name>_partition_column" accepts str or list of str (Strings)
                * "<input_data_arg_name>_hash_column" accepts str or list of str (Strings)
                * "<input_data_arg_name>_order_column" accepts str or list of str (Strings)
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if the underlying Analytic Database
                function supports, else an exception is raised.

    RETURNS:
        Instance of Image2Matrix.
        Output teradataml DataFrames can be accessed using attribute
        references, such as Image2Matrix.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result

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

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Import function Image2Matrix.
        from teradataml import Image2Matrix
        import teradataml

        # Drop the image table if it is present.
        try:
            db_drop_table('imageTable')
        except:
            pass

        # Create a table to store the image data.
        execute_sql('CREATE TABLE imageTable(id INTEGER, image BLOB);')

        # Load the image data into the fileContent variable.
        file_dir = os.path.join(os.path.dirname(teradataml.__file__), "data")
        with open(os.path.join(file_dir,'peppers.png'), mode='rb') as file:
            fileContent = file.read()

        # Insert the image data into the table.
        sql = 'INSERT INTO imageTable VALUES(?, ?);'
        parameters = (1, fileContent)
        execute_sql(sql, parameters)

        # Create a DataFrame for the image table.
        imageTable = DataFrame('imageTable')

        # Example 1: Convert the image to matrix with gray values.
        image2matrix = Image2Matrix(data=imageTable.select(['id', 'image']), 
                                    output='gray')

        # Print the result DataFrame.
        print(image2matrix.result)

        # Example 2: Convert the image to matrix with rgb values.
        image2matrix2 = Image2Matrix(data=imageTable.select(['id', 'image']), 
                                     output='rgb')

        # Print the result DataFrame.
        print(image2matrix2.result)
    """
