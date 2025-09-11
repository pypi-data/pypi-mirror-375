def ScaleFit(data=None, target_columns=None, scale_method=None, miss_value="KEEP",
             global_scale=False, multiplier='1', intercept='0', **generic_arguments):
    """
    DESCRIPTION:
        ScaleFit() function outputs statistics to input to ScaleTransform() function,
        which scales specified input DataFrame columns.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the input teradataml DataFrame column(s) for which to output statistics.
            The columns must contain numeric data in the range (-1e\u00B3\u2070\u2078, 1e\u00B3\u2070\u2078).
            Types: str OR list of Strings (str)

        scale_method:
            Required Argument.
            Specifies the scale method to be used for scaling. If one value is
            provided, it applies to all target columns. If more than one value is
            specified, scale method values applies to target columns values in the
            order specified by the user.
            ScaleTransform() function uses the location and scale values in the
            following formula to scale target column value X to scaled value X':
                X' = intercept + multiplier * ((X - location)/scale)
            "intercept" and "multiplier" arguments determine intercept and multiplier.

            In the table, Xmin, Xmax, and XMean are the minimum, maximum, and mean
            values of the target column.
            +--------------+---------------------------+-----------------+------------------------------+
            | scale_method |        Description        |     location    |            scale             |
            +--------------+---------------------------+-----------------+------------------------------+
            |    MAXABS    |  Maximum absolute value.  |        0        |         Maximum |X|          |
            |              |                           |                 |                              |
            |     MEAN     |           Mean.           |      XMean      |              1               |
            |              |                           |                 |                              |
            |   MIDRANGE   |         Midrange.         |  (Xmax+Xmin)/2  |        (Xmax-Xmin)/2         |
            |              |                           |                 |                              |
            |    RANGE     |           Range.          |       Xmin      |          Xmax-Xmin           |
            |              |                           |                 |                              |
            |   RESCALE    |  Rescale using specified  | See table after |       See table after        |
            |              | lower bound, upper bound, | RESCALE syntax. |       RESCALE syntax.        |
            |              |     or both.See syntax    |                 |                              |
            |              |     after this table.     |                 |                              |
            |              |                           |                 |                              |
            |     STD      |    Standard deviation.    |      XMean      |   √(∑((Xi - Xmean)2)/ N)     |
            |              |                           |                 |     where N is count of      |
            |              |                           |                 |        valid values.         |
            |              |                           |                 |                              |
            |     SUM      |            Sum.           |        0        |              ΣX              |
            |              |                           |                 |                              |
            |     USTD     |     Unbiased standard     |      XMean      | √(∑((Xi - Xmean)2)/ (N - 1)) |
            |              |         deviation.        |                 |     where N is count of      |
            |              |                           |                 |        valid values.         |
            +--------------+---------------------------+-----------------+------------------------------+

            RESCALE ({ lb=lower_bound | ub=upper_bound | lb=lower_bound, ub=upper_bound })
            +------------------------+-----------------------------+----------------------------+
            |                        |           location          |           scale            |
            +------------------------+-----------------------------+----------------------------+
            |    Lower bound only    |      Xmin - lower_bound     |             1              |
            |                        |                             |                            |
            |    Upper bound only    |      Xmax - upper_bound     |             1              |
            |                        |                             |                            |
            | Lower and upper bounds |     Xmin - (lower_bound/    |       (Xmax - Xmin)/       |
            |                        | (upper_bound- lower_bound)) | (upper_bound- lower_bound) |
            +------------------------+-----------------------------+----------------------------+

            Permitted Values:
                * MAXABS
                * MEAN
                * MIDRANGE
                * RANGE
                * RESCALE
                * STD
                * SUM
                * USTD
            Types: str OR list of Strings (str)

        miss_value:
            Optional Argument.
            Specifies how to process NULL values in input.
            Permitted Values:
                * KEEP: Keep NULL values.
                * ZERO: Replace each NULL value with zero.
                * LOCATION: Replace each NULL value with its location value.
            Default Value: "KEEP"
            Types: str

        global_scale:
            Optional Argument.
            Specifies whether all input columns are scaled to the same location
            and scale. When set to False, each input column is scaled separately.
            Default Value: False
            Types: bool

        multiplier:
            Optional Argument.
            Specifies one or more multiplying factors(multiplier) to apply to the input data.
            If only one multiplier is specified, it applies to all target columns.
            If a list of multipliers is specified, each multiplier applies to the
            corresponding target column.
            Default Value: "1"
            Types: str OR list of String (str)

        intercept:
            Optional Argument.
            Specifies one or more addition factors(intercept) incrementing the scaled results.
            If only one intercept specified, it applies to all target columns.
            If a list of intercepts is specified, each intercept applies to the
            corresponding target column.
            The syntax of intercept is:
                [-]{number | min | mean | max }
            where min, mean, and max are the global minimum, maximum, mean values
            in the corresponding columns. The function scales the values of min,
            mean, and max.
                For example, if intercept is "- min" and multiplier is
                1, the scaled result is transformed to a non-negative sequence
                according to this formula, where scaledmin is the scaled value:
                    X = -scaledmin + 1 * (X - location)/scale.
            Default Value: "0"
            Types: str OR list of String (str)

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
                These generic arguments are supported by teradataml if the underlying SQLE Engine
                function supports, else an exception is raised.

    RETURNS:
        Instance of ScaleFit.
        Output teradataml DataFrames can be accessed using attribute
        references, such as ScaleFitObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            1. output
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
        load_example_data("teradataml", ["scale_housing"])

        # Create teradataml DataFrame.
        scaling_house = DataFrame.from_table("scale_housing")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Create statistics to scale "lotsize" with respect to
        #            mean value of the column.
        fit_obj = ScaleFit(data=scaling_house,
                           target_columns="lotsize",
                           scale_method="MEAN",
                           miss_value="KEEP",
                           global_scale=False,
                           multiplier="1",
                           intercept="0")

        # Print the result DataFrame.
        print(fit_obj.output)
        print(fit_obj.output_data)
    """
