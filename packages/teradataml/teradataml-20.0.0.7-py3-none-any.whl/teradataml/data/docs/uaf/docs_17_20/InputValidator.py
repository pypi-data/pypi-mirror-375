def InputValidator(data=None, data_filter_expr=None, failure_mode=None,
                   **generic_arguments):
    """
    DESCRIPTION:
        The InputValidator() function validates the data and identifies
        series and matrixes that have indiscrete data.
        Discrete data is classified as follows:
            * Series data:
                * Interval is the same for row_index field.
                * No duplicate row_index field in same series.
            * Matrix data:
                * Interval is the same for row_index field.
                * Interval is the same for column_index field.
                * No duplicate row_index or no duplicate column_index in same matrix.
                * Number of rows in each series (wavelet) is the same.
                * For each series (wavelet), column_index starts from same value under row major.

    PARAMETERS:
        data:
            Required Argument.
            Specifies a logical series or a matrix to be validated.
            Types: TDSeries, TDMatrix

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        failure_mode:
            Required Argument.
            Specifies how many rows to display when the
            input instance is indiscrete.
            Permitted Values:
                * FUNC_FIRST - Lists the first row that makes the instance indiscrete.
                * FUNC_ALL - Lists all indiscrete rows.
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
        Instance of InputValidator.
        Output teradataml DataFrames can be accessed using attribute
        references, such as InputValidator_obj.<attribute_name>.
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
        load_example_data("uaf", ["buoydata_mix"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("buoydata_mix")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  row_index="TD_TIMECODE",
                                  row_index_style="TIMECODE",
                                  id=["oceanname", "buoyid"],
                                  payload_field="salinity",
                                  payload_content="REAL")

        # Example 1: Validate the input series to check if it has indiscrete data or not.
        uaf_out = InputValidator(data=data_series_df, failure_mode="FUNC_FIRST")

        # Print the result DataFrame.
        print(uaf_out.result)

    """