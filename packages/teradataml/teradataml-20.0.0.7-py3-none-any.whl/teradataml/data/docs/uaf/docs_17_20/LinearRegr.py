def LinearRegr(data=None, data_filter_expr=None, variables_count=2, 
               weights=False, formula=None, algorithm=None, 
               coeff_stats=False, conf_int_level=0.9, model_stats=False, 
               residuals=False, **generic_arguments):
    """
    DESCRIPTION:
        The LinearRegr() function is a simple linear regression function.
        It fits data to a curve using a formula that defines 
        the relationship between the explanatory variable and the 
        response variable.
        
        The following procedure is an example of how to use 
        LinearRegr() to develop an ARIMA model:
            * Determine that the series to be modeled includes a trend.
            * Use LinearRegr() to remove the trend from the series.
            * Use the "fitmetadata" attribute from the function output,
              to determine the trend by fitting the data set.
            * Use GenseriesFormula() to generate a trend series.
            * Use BinarySeriesOp() to subtract the generated trend
              from the original series.


    PARAMETERS:
        data:
            Required Argument.
            Specifies an input time series with the following payload characteristics:
                * "payload_content" value is MULTIVAR_REAL.
                * "payload_fields" has two required fields (response variable and 
                  explanatory variable, in that order) and one optional 
                  field (weights).
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies filter expression for "data".
            Types: ColumnExpression

        variables_count:
            Optional Argument.
            Specifies the number of parameters present
            in the payload. For linear regression with no weighting, 
            there are 2 parameters (the response variable and the explanatory
            variable). For linear regression with weighting, there are
            3 variables (the response variable, the explanatory variable,
            and the weights).
            Default Value: 2
            Permitted Values: 2, 3
            Types: int

        weights:
            Optional Argument.
            Specifies whether a third series is present
            in MULTIVAR series-specifications. The third series is
            interpreted as a series of weights that can be used to 
            perform a weighted least-squares regression solution.
            When set to False, no third series is present, 
            otherwise it is present.
            Default Value: False
            Types: bool

        formula:
            Required Argument.
            Specifies the formula that is to be used in the regression operation.
            The formula defines the relationship between the explanatory
            variable and the response variable and, conforms to Formula Rules.
            Note:
                Use the following link to refer the formula rules in Teradata document(func_param):
                "https://docs.teradata.com/r/4k28qKyhFXQ3DA~TULEIuw/Yp9oQ2nOzr70tKke4rCiAQ"
            Types: str

        algorithm:
            Required Argument.
            Specifies the algorithm used for the regression.
            Permitted Values:
                1. QR: means that QR decomposition is used for the regression.
                2. PSI: means that pseudo-inverse based on singular value
                   decomposition (SVD) is used to solve the regression.
            Types: str

        coeff_stats:
            Optional Argument.
            Specifies whether to include coefficient statistics columns in the results.
            When set to False, coefficient statistics columns are not included in 
            the results, otherwise, columns are included in the results.
            Default Value: False
            Types: bool

        conf_int_level:
            Optional Argument.
            Specifies the confidence interval level value used for coefficient
            statistics calculation. The value is greater than 0 and less than 1. 
            Note:
                Applicable only when "coeff_stats" is set to True.
            Default Value: 0.9
            Types: int OR float

        model_stats:
            Optional Argument.
            Specifies whether to generate the optional model statistics and
            available to access using the attribute "fitmetadata" of the function
            output. When set to True, function generates the model statistics,
            otherwise not.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies whether to generate the tertiary (residuals)
            layer and available to access using the attribute "fitresiduals" of
            the function output. When set to True, function generates the layer,
            Otherwise not.
            Default Value: False
            Types: bool

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
        Instance of LinearRegr.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as LinearRegr_obj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. fitmetadata - Available when "model_stats" is set to True, otherwise not.
            3. fitresiduals - Available when "residuals" is set to True, otherwise not.


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
        load_example_data("uaf", ["house_values2"])

        # Create teradataml DataFrame object.
        data = DataFrame.from_table("house_values2")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=data,
                                  id="cid",
                                  row_index_style="SEQUENCE",
                                  row_index="s_no",
                                  payload_field=["house_value", "salary"],
                                  payload_content="MULTIVAR_REAL")

        # Example 1: The LinearRegr() function fits TDSeries data to
        #             the curve mentioned in the "formula." It returns
        #             a result containing solved coefficients, model statistics,
        #             and residuals statistics.
        uaf_out = LinearRegr(data=data_series_df,
                             variables_count=2,
                             weights=False,
                             formula="Y=B0+B1*X1",
                             algorithm='QR',
                             model_stats=True, 
                             coeff_stats=False,
                             residuals=True)

        # Print the result DataFrames.
        print(uaf_out.result)
        # Print the model statistics result.
        print(uaf_out.fitmetadata)
        # Print the residuals statistics result.
        print(uaf_out.fitresiduals)
    
    """