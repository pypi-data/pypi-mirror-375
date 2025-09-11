def MultivarRegr(data=None, data_filter_expr=None, variables_count=None,
                 weights=False, formula=None, algorithm=None, coeff_stats=False,
                 conf_int_level=0.9, model_stats=False, residuals=False,
                 **generic_arguments):
    """
    DESCRIPTION:
        The MultivarRegr() function is a multivariate linear regression function.
        Using a formula that defines the relationship between the explanatory
        variable and multiple response variables, it fits data to a multidimensional surface.


    PARAMETERS:
        data:
            Required Argument.
            Specifies series with payload characteristics as follows:
                * Payload content value is MULTIVAR_REAL.
                * Payload field value has "variables_count" required fields (response
                  variable followed by explanatory variables).
            Types: TDSeries

        data_filter_expr:
            Optional Argument.
            Specifies filter expression for "data".
            Types: ColumnExpression

        variables_count:
            Required Argument.
            Specifies how many parameters are present in the payload. For
            linear regression with no weighting, there are 2 variables (the response
            variable and the explanatory variable). For linear regression with weighting,
            there are 3 variables (the response variable, the explanatory variable, and
            the weights).
            Types: int

        weights:
            Optional Argument.
            Specifies whether a third series is present in MULTIVAR series-specifications.
            The third series is interpreted as a series of weights that can be used to
            perform a weighted least-squares regression solution.
            When set to False, no third series is present, otherwise it is present.
            Default Value: False
            Types: bool

        formula:
            Required Argument.
            Specifies the relationship between the explanatory variable and the response variables.
            Types: str

        algorithm:
            Required Argument.
            Specifies algorithm used for the regression.
            Permitted Values:
                1. QR: means that QR decomposition is used for the regression.
                2. PSI: means that pseudo-inverse based on singular value
                   decomposition (SVD) is used to solve the regression.
            Types: str

        coeff_stats:
            Optional Argument.
            Specifies whether to include coefficient statistics columns in the output or not.
            When set to False, coefficient statistics columns are not returned in the output,
            otherwise columns are returned in the output.
            Default Value: False
            Types: bool

        conf_int_level:
            Optional Argument.
            Specifies the confidence interval level value used for coefficient statistics
            calculation.
            The value should be greater than 0 and less than 1.
            Note:
                Applicable only when "coeff_stats" is set to 1.
            Default Value: 0.9
            Types: int OR float

        model_stats:
            Optional Argument.
            Specifies whether to generate the optional model statistics.
            The generated result set can be retrieved using the attribute
            fitmetadata of the function output. When set to False, function
            does not generate the statistics, otherwise generates it.
            Default Value: False
            Types: bool

        residuals:
            Optional Argument.
            Specifies whether to generate the tertiary (residuals) layer.
            The generated result set can be retrieved using the attribute
            fitresiduals of the function output. when set to False, function
            does not generate the residual data, otherwise generates it.
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
        Instance of MultivarRegr.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as MultivarRegr_obj.<attribute_name>.
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
        load_example_data("uaf", ["house_values"])

        # Create teradataml DataFrame object.
        df = DataFrame.from_table("house_values")

        # Create teradataml TDSeries object.
        data_series_df = TDSeries(data=df,
                                  id="cityid",
                                  row_index="TD_TIMECODE",
                                  payload_field=["house_val","salary","mortgage"],
                                  payload_content="MULTIVAR_REAL")

        # Example 1 : Execute multivariate regression function to identify the degree of
        #             linearity the explanatory variable and multiple response variables.
        #             Generate the model statistics and residual data as well.
        uaf_out = MultivarRegr(data=data_series_df,
                               variables_count=3,
                               weights=False,
                               formula="Y = B0 + B1*X1 + B2*X2",
                               algorithm='QR',
                               coeff_stats=True,
                               model_stats=True,
                               residuals=True)

        # Print the result DataFrames.
        print(uaf_out.result)
        print(uaf_out.fitmetadata)
        print(uaf_out.fitresiduals)
    
    """
    