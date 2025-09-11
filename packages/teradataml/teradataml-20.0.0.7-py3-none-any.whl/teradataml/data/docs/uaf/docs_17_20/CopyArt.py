def CopyArt(data=None, database_name = None,
            table_name = None, map_name = None,
            **generic_arguments):
    """
    DESCRIPTION:
        CopyArt() function creates a copy of an existing analytics result table (ART).

    PARAMETERS:
        data:
            Required Argument.
            Specifies the ART data to be copied.
            Types: DataFrame

        database_name:
            Required Argument.
            Specifies the name of the destination database for copied ART.
            Types: str

        table_name:
            Required Argument.
            Specifies the name of the destination table for copied ART.
            Types: str

        map_name:
            Optional Argument.
            Specifies the name of the map for the destination ART.
            By default, it refers to the map of the 'data'.
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
        Instance of CopyArt.
        Output teradataml DataFrames can be accessed using attribute
        references, such as obj.<attribute_name>.
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

        # Import function CopyArt.
        from teradataml import CopyArt, AutoArima

        # Load the example data.
        load_example_data("uaf", ["blood2ageandweight"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("blood2ageandweight")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="PatientID",
                                  row_index="SeqNo",
                                  row_index_style="SEQUENCE",
                                  payload_field="BloodFat",
                                  payload_content="REAL")

        # Execute AutoArima function to create ART.
        uaf_out = AutoArima(data=data_series_df,
                            start_pq_nonseasonal=[1, 1],
                            seasonal=False,
                            constant=True,
                            algorithm="MLE",
                            fit_percentage=80,
                            stepwise=True,
                            nmodels=7,
                            fit_metrics=True,
                            residuals=True)

        # Example 1: Execute CopyArt function to copy ART to a destination table name
        #            with persist option.
        res = CopyArt(data=uaf_out.result,
                      database_name="alice",
                      table_name="copied_table",
                      persist=True)
        print(res.result)

        # Example 2: Execute CopyArt function to copy ART to a destination table name.
        res = CopyArt(data=uaf_out.result,
                      database_name="alice",
                      table_name="copied_table2")

        # Print the result DataFrame.
        print(res.result)

        # Example 3: Copy ART to a destination table name using uaf object.
        res = uaf_out.copy(database_name="alice",
                           table_name="copied_table3")

        # Print the result DataFrame.
        print(res.result)

    """