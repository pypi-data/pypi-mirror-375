def PowerTransform(data=None, data_filter_expr=None, back_transform=False, 
                   p=None, b=None, lambda1=None, 
                   output_fmt_index_style="NUMERICAL_SEQUENCE", 
                   **generic_arguments):
    """
    DESCRIPTION:
        The PowerTransform() function takes a time series or numerically-sequenced
        series and applies a power transform to the series to produce a one-dimensional
        array. The passed-in series can be either a univariate or multivariate series.
        This function is useful for transforming an input series that has heteroscedastic 
        variance into a result series that has homoscedastic variance.

        User can use the new time series to build an ARIMA forecasting model.
        
        The following procedure is an example of how to get forecast values
        for a heteroscedastic time series using PowerTransform() function:
            * Apply PowerTransform() function to the heteroscedastic time series.
            * Use the resulting homoscedastic time series to build an ARIMA forecasting model.
            * Use the model to produce the initial forecast of the homoscedastic time series.
            * Use the backward transform on the initial forecast to extract the forecast
              values for the heteroscedastic time series.


    PARAMETERS:
        data:
            Required Argument.
            Specifies an input series whose payload content value can be
            REAL or MULTIVAR_REAL.
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies the filter expression for "data".
            Types: ColumnExpression

        back_transform:
            Optional Argument.
            Specifies whether to apply back transform. 
            When set to False, black transform is not applied, otherwise it is applied.
            Default Value: False
            Types: bool

        p:
            Required Argument.
            Specifies the power to use in the transform equation.
            Types: int OR float

        b:
            Required Argument.
            Specifies the logarithm to be applied for the transform equation.
            Types: int OR float

        lambda1:
            Required Argument.
            Specifies the parameter used to decide the preferred
            power transform operation during the Box-Cox transformation.
            Types: int OR float

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
        Instance of PowerTransform.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as PowerTransform_obj.<attribute_name>.
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
        load_example_data("uaf", ["production_data"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("production_data")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="product_id",
                                  row_index="TD_TIMECODE",
                                  payload_field=["beer_sales", "wine_sales"],
                                  payload_content="MULTIVAR_REAL")

        # Example 1: The function returns the results, which transforms
        #            heteroscedastic time series to homoscedastic time series.
        uaf_out = PowerTransform(data=data_series_df,
                                 back_transform=True,
                                 p=0.0,
                                 b=0.0,
                                 lambda1=0.5)

        # Print the result DataFrame.
        print(uaf_out.result)

    """
    