def Histogram(data=None, object=None, target_columns=None, method_type=None, nbins=1, inclusion="LEFT",
              **generic_arguments):
    """
    DESCRIPTION:
        Function calculates the frequency distribution of a data set using any of these methods:
            * Sturges
            * Scott
            * Variable-width
            * Equal-width


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        object:
            Optional Argument.
            Specifies the bin data, needed when "method_type" is set to 'EQUAL-WIDTH' or 'VARIABLE-WIDTH'.
            Types: teradataml DataFrame

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" to perform computations on.
            Types: str OR list of Strings (str)

        method_type:
            Required Argument.
            Specifies the method type to be used for histogram computation.
            Permitted Values:
                * STURGES -
                    Algorithm for calculating bin width, w:
                         w = r/(1 + log\u2082 n)
                         where:
                             w = bin width
                             r = data value range
                             n = number of elements in data set
                         Sturges algorithm performs best if data is normally distributed
                         and n is at least 30.

                * SCOTT -
                    Algorithm for calculating bin width, w:
                         w = 3.49s/(n^1/3)
                         where:
                             w = bin width
                             s = standard deviation of data values
                             n = number of elements in data set
                             r = data value range
                             Number of bins: r/w
                         Scott algorithm performs best on normally distributed data.

                * EQUAL-WIDTH -
                    Requires "object" argument, which specifies the minimum value and the maximum
                    value of the bin in column1 and column2 respectively, and the label of the bin
                    in column3. Maximum number of bins cannot exceed 3500.

                * VARIABLE-WIDTH -
                    Requires "object" argument, which specifies the minimum value of the bins
                    in column1 and the maximum value of the bins in column2.
                    Algorithm for calculating bin width, w:
                    w = (max - min)/k
                    where:
                        min = minimum value of the bins
                        max = maximum value of the bins
                        k = number of intervals into which algorithm divides data set
                        Interval boundaries: min+w, min+2w, …, min+(k-1)w
            Types: str

        nbins:
            Optional Argument, Required when "method_type" is 'Variable-Width' and 'Equal-Width'.
            Specifies the number of bins.
            Default Value: 1
            Types: int

        inclusion:
            Optional Argument.
            Specifies whether points on bin boundaries should be included in the
            bin on the left or the right.
            Default Value: "LEFT"
            Permitted Values: LEFT, RIGHT
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
                These generic arguments are supported by teradataml if the underlying
                SQLE Engine function supports, else an exception is raised.

    RETURNS:
        Instance of Histogram.
        Output teradataml DataFrames can be accessed using attribute
        references, such as HistogramObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result


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
        load_example_data("teradataml", ["titanic", "min_max_titanic"])

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")

        # Create teradataml DataFrame object for minimum and maximum value of bins
        # "Young age", "Middle Age" and, "Old Age".
        min_max_object = DataFrame.from_table("min_max_titanic")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Get the frequency distribution of a data set using 'sturges'
        #            method type for the values in column 'age'.
        obj = Histogram(data=titanic_data,
                        target_columns="age",
                        method_type="Sturges")

        # Print the result DataFrame.
        print(obj.result)

        # Example 2: Get the frequency distribution of a data set using 'variable-width'
        #            method type for the values in column 'age' with 3 number of bins.
        obj = Histogram(data=titanic_data,
                        object=min_max_object,
                        target_columns="age",
                        method_type="variable-width",
                        nbins=3)

        # Print the result DataFrame.
        print(obj.result)
    """