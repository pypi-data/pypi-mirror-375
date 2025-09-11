def Histogram(data=None, object=None, target_columns=None, method_type=None, nbins=1, inclusion="LEFT",
              groupby_columns=None, **generic_arguments):
    """
    DESCRIPTION:
        The Histogram() function calculates the frequency distribution of a data set
        using any of these methods:
            * Sturges
            * Scott
            * Variable-width
            * Equal-width

        Notes:
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
            * This function does not support KanjiSJIS or Graphic data types.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        object:
            Required when "method_type" is 'VARIABLE-WIDTH', optional otherwise.
            Specifies the bin data.
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

                * VARIABLE-WIDTH -
                    Requires "object" argument, which specifies the minimum value and the
                    maximum value of the bin.
                    When one target column is specified, specify the minimum value
                    in column1 in "object" data , maximum value in column2 in "object"
                    data, and label of the bin in column3.
                    When more than one target column is specified, specify the
                    column name present in "target_column" attribute in column1
                    in "object" data, minimum value in column2 in "object" data,
                    maximum value in column3 in "object" data, and the label of
                    the bin in column4 in "object" data.
                    Note:
                        * The maximum number of bins cannot exceed 10000 per column.

                * EQUAL-WIDTH -
                    Algorithm for calculating bin width, w:
                    w = (max - min)/k
                    where:
                        min = minimum value of the bins
                        max = maximum value of the bins
                        k = number of intervals into which algorithm divides data set
                        Interval boundaries: min+w, min+2w, …, min+(k-1)w
                    "object" argument is optional.
                    When "object" data is omitted, Histogram() function internally computes
                    the min value and max value from the input data for the target columns.
                    When "object" data is specified, the user can specify in the following
                    manner:
                        * When one target column is specified, specify min value in column1
                          in "object" data and max value in column2 in "object" data.
                        * When more than one target column is specified, specify the
                          column name present in "target_column" attribute in column1
                          in "object" data, min value in column2 in "object" data,
                          and max value in column3 in "object" data.
            Types: str

        nbins:
            Required when "method_type" is 'VARIABLE-WIDTH' and 'EQUAL-WIDTH',
            optional otherwise.
            Specifies the number of bins.
            Notes:
                * When only one value is specified, it is applied to all the target columns.
                  Otherwise, the number of "nbins" values must be equal to the number of
                  target columns.
                * The maximum "nbins" value is 10000.
            Default Value: 1
            Types: int OR list of ints

        inclusion:
            Optional Argument.
            Specifies whether points on bin boundaries should be included in the
            bin on the left or the right.
            Note:
                * When only one value is specified, it is applied to all the target columns.
                  Otherwise, the number of "inclusion" values must be equal to the number
                  of target columns.
            Default Value: "LEFT"
            Permitted Values: LEFT, RIGHT
            Types: str OR list of Strings (str)

        groupby_columns:
            Optional Argument.
            Specifies the names of the input data columns that contain the group
            values for binning.
            Notes:
                * This argument must not have columns that are already specified
                  in "target_columns".
                * This argument does not support range.
                * The maximum number of unique columns in the "groupby_columns"
                  argument is 2042.
            Types: str OR list of Strings (str)

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

        # Example 1: Get the frequency distribution of a data set using 'STURGES'
        #            method type for the values in column 'age'.
        obj1 = Histogram(data=titanic_data,
                         target_columns="age",
                         method_type="STURGES")

        # Print the result DataFrame.
        print(obj1.result)

        # Example 2: Get the frequency distribution of a data set using 'VARIABLE-WIDTH'
        #            method type for the values in column 'age' with 3 number of bins.
        obj2 = Histogram(data=titanic_data,
                         object=min_max_object,
                         target_columns="age",
                         method_type="VARIABLE-WIDTH",
                         nbins=3)

        # Print the result DataFrame.
        print(obj2.result)

        # Example 3: Get the frequency distribution of a data set with respect
        #            to 'sex' column using 'EQUAL-WIDTH' method type for the
        #            values in column 'age' and 'fare' with 3 and 2 number
        #            of bins respectively.
        obj3 = Histogram(data=titanic_data,
                         target_columns=["age", "fare"],
                         method_type="EQUAL-WIDTH",
                         nbins=[3,2],
                         groupby_columns=["sex"])

        # Print the result DataFrame.
        print(obj3.result)
    """