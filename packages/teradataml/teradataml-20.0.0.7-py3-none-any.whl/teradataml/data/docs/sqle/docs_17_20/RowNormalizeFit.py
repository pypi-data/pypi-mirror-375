def RowNormalizeFit(data=None, target_columns=None, approach="UNITVECTOR", base_column=None,
                    base_value=None, **generic_arguments):
    """
    DESCRIPTION:
        RowNormalizeFit() function outputs a DataFrame containing parameters and specified input columns
        to input to RowNormalizeTransform() function, which normalizes the input columns row-wise.

        
    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame
            
        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" to normalize.
            Types: str OR list of Strings (str)
            
        approach:
            Optional Argument.
            Specifies the method to use for row wise normalization.
            Permitted Values:
                * UNITVECTOR - X' = X / (sqrt (Σ\u1D62ϵ\u208D\u2081, \u2099\u208E X\u1D62\u00B2))
                * FRACTION - X' = X / (Σ\u1D62ϵ\u208D\u2081, \u2099\u208E X\u1D62)
                * PERCENTAGE - X' = X*100 / (Σ\u1D62ϵ\u208D\u2081, \u2099\u208E X\u1D62)
                * INDEX - X' = V + ((X - B) / B) * 100
                In the normalizing formulas:
                    X' is the normalized value.
                    X is the original value.
                    B is the value in the base column.
                    V is the base value.
            Default Value: "UNITVECTOR"
            Types: str
            
        base_column:
            Required when "approach" is set to 'INDEX', ignored otherwise.
            Specifies the base column to be used in INDEX "approach" formula.
            Types: str
            
        base_value:
            Required when "approach" is set to 'INDEX', ignored otherwise.
            Specifies the base value to be used in INDEX "approach" formula.
            Types: float OR int

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept.
            Below are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or not.
                    When set to True, results are persisted in a table; otherwise, results
                    are garbage collected at the end of the session.
                    Default Value: False
                    Types: boolean

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table or not.
                    When set to True, results are stored in a volatile table, otherwise not.
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
                These generic arguments are supported by teradataml if the underlying
                SQL Engine function supports, else an exception is raised.

        
    RETURNS:
        Instance of RowNormalizeFit.
        Output teradataml DataFrames can be accessed using attribute 
        references, such as RowNormalizeFitObj.<attribute_name>.
        Output teradataml DataFrame attribute name are:
            1. output_data
            2. output
    
    
    RAISES
        TeradataMlException, TypeError, ValueError
    
    
    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        # Load the example data.
        load_example_data("teradataml", ["numerics"])

        # Create teradataml DataFrame object.
        numerics = DataFrame.from_table("numerics")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Create fit object to normalize ""smallint_col" and "integer_col"
        #            columns using "INDEX" approach, "integer_col" as base column
        #            and base value as 100.0.
        fit_obj = RowNormalizeFit(data=numerics,
                                  target_columns=["integer_col", "smallint_col"],
                                  approach="INDEX",
                                  base_column="integer_col",
                                  base_value=100.0)

        # Print the result DataFrame.
        print(fit_obj.output)
        print(fit_obj.output_data)
    """