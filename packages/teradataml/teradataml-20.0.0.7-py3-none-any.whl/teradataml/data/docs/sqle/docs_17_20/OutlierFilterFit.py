def OutlierFilterFit(data=None, target_columns=None, group_columns=None, lower_percentile=0.05, upper_percentile=0.95,
                    iqr_multiplier=1.5, outlier_method="PERCENTILE", replacement_value="DELETE", remove_tail="BOTH",
                    percentile_method="PERCENTILEDISC", **generic_arguments):
    """
    DESCRIPTION:
        The OutlierFilterFit() function calculates the lower_percentile,
        upper_percentile, count of rows and median for all the "target_columns"
        provided by the user. These metrics for each column helps the
        function OutlierTransform() detect outliers in the input table. It also
        stores parameters from arguments into a FIT table used during
        transformation.
        Notes:
            * This function requires the UTF8 client character set for
              UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
            * For information about PTCs, see Teradata Vantage™ - Analytics
              Database International Character Set Support.
            * This function does not support KanjiSJIS or Graphic data types.
            * This function does not support "data_partition_column" and "data_order_column" 
              if the corresponding Vantage version is greater than or equal to 17.20.03.20.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" for which
            to compute the metrics.
            Types: str OR list of Strings (str)

        group_columns:
            Optional Argument.
            Specifies the input data column for which stats calculation needs to
            be grouped together.
            Types: str

        lower_percentile:
            Optional Argument.
            Specifies lower range of percentile to be used to detect if value is
            outlier or not.
            Default Value: 0.05
            Types: int

        upper_percentile:
            Optional Argument.
            Specifies upper range of percentile to be used to detect if value is
            outlier or not.
            Default Value: 0.95
            Types: int

        iqr_multiplier:
            Optional Argument.
            Specifies the multiplier of interquartile range for "Tukey" filtering.
            Default Value: 1.5
            Types: int

        outlier_method:
            Optional Argument.
            Specifies the method for filtering the outliers.
            Permitted Values:
                * PERCENTILE - [min_value, max_value].
                * TUKEY - [Q1 - k*(Q3-Q1), Q1 + k*(Q3-Q1)]
                          where:
                            Q1 = 25th quartile of data
                            Q3 = 75th quartile of data
                            k = interquantile range multiplier (see "iqr_multiplier")
                * CARLING - Q2 ± c*(Q3-Q1)
                            where:
                                Q2 = median of data
                                Q1 = 25th quartile of data
                                Q3 = 75th quartile of data
                                c = (17.63*r - 23.64) / (7.74*r - 3.71)
                                r = count of rows in group_columns if you specify "group_columns",
                                    otherwise count of rows in "data"
            Default Value: "PERCENTILE"
            Types: str

        replacement_value:
            Optional Argument.
            Specifies the method to handle outliers.
            Permitted Values:
                * DELETE - Do not copy row to output DataFrame.
                * NULL - Copy row to output DataFrame, replacing each outlier with NULL.
                * MEDIAN - Copy row to output DataFrame, replacing each outlier with median
                           value for its group.
                * REPLACEMET VALUE - Copy row to output DataFrame, replacing each outlier with
                                      a replacement value. Replacement value must be numeric.
            Default Value: "DELETE"
            Types: str, int, float

        remove_tail:
            Optional Argument.
            Specifies the tail of the distribution to remove.
            Permitted Values:
                * LOWER - The lower tail.
                * UPPER - The upper tail.
                * BOTH - Both tails.
            Default Value: "BOTH"
            Types: str

        percentile_method:
            Optional Argument.
            Specifies the teradata percentile methods to be used for calculating
            the upper and lower percentiles of the "target_columns".
            Permitted Values:
                * PERCENTILECONT - Considering continuous distribution.
                * PERCENTILEDISC - Considering discrete distibution.
            Default Value: "PERCENTILEDISC"
            Types: str

        **generic_arguments:
            Specifies the generic keyword arguments SQLE functions accept. Below
            are the generic keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the
                    function in a table or not. When set to True,
                    results are persisted in a table; otherwise,
                    results are garbage collected at the end of the
                    session.
                    Default Value: False
                    Types: bool

                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the
                    function in a volatile table or not. When set to
                    True, results are stored in a volatile table,
                    otherwise not.
                    Default Value: False
                    Types: bool

            Function allows the user to partition, hash, order or local
            order the input data. These generic arguments are available
            for each argument that accepts teradataml DataFrame as
            input and can be accessed as:
                * "<input_data_arg_name>_partition_column" accepts str or
                  list of str (Strings)
                * "<input_data_arg_name>_hash_column" accepts str or list
                  of str (Strings)
                * "<input_data_arg_name>_order_column" accepts str or list
                  of str (Strings)
                * "local_order_<input_data_arg_name>" accepts boolean
            Note:
                These generic arguments are supported by teradataml if
                the underlying SQL Engine function supports, else an
                exception is raised.

    RETURNS:
        Instance of OutlierFilterFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as OutlierFilterFitObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. output_data


    RAISES:
        TeradataMlException, TypeError, ValueError


    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in
        #        the example from teradataml.
        #     3. Function will raise error if not supported on the Vantage
        #        user is connected to.

        # Load the example data.
        load_example_data("teradataml", ["titanic"])

        # Create teradataml DataFrame objects.
        titanic_data = DataFrame.from_table("titanic")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Generating fit object to find outlier values in column "fare".
        OutlierFilterFit_out = OutlierFilterFit(data = titanic_data,
                                                target_columns = "fare")

        # Print the result DataFrame.
        print(OutlierFilterFit_out.result)
        print(OutlierFilterFit_out.output_data)

    """
