def Silhouette(data=None, accumulate=None, id_column=None, cluster_id_column=None, target_columns=None,
               output_type="SCORE", **generic_arguments):
    """
    DESCRIPTION:
        The Silhouette() function refers to a method of interpretation and validation of consistency within
        clusters of data. The function determines how well the data is clustered among clusters.

        The silhouette value determines the similarity of an object to its cluster (cohesion) compared to
        other clusters (separation). The silhouette plot displays a measure of how close each point in one
        cluster is to the points in the neighbouring clusters and thus provides a way to assess parameters
        like the optimal number of clusters.

        The silhouette scores and its definitions are as follows:
            1: Data is appropriately clustered
            -1: Data is not appropriately clustered
            0: Datum is on the border of two natural clusters
        Notes:
            * The algorithm used in this function is of the order of N*N (where N is the number of rows). Hence,
              expect the query to run significantly longer as the number of rows increases in the input data.
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
                For information about PTCs, see Teradata Vantage™ - Analytics Database International Character Set
                Support.
            * This function does not support KanjiSJIS or Graphic data types.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        accumulate:
            Optional Argument.
            Specifies the name(s) of input teradataml DataFrame column(s) to copy to the output.
            Note:
                Applicable only when "output_type" is set to 'SAMPLE_SCORES'.
            Types: str OR list of Strings (str)

        id_column:
            Required Argument.
            Specifies the column which is the unique identifier of input rows.
            Types: str

        cluster_id_column:
            Required Argument.
            Specifies the column containing assigned cluster IDs for input data points.
            Types: str

        target_columns:
            Required Argument.
            Specifies the columns/features to be used for calculating silhouette score.
            Types: str OR list of Strings (str)

        output_type:
            Optional Argument.
            Specifies the output type or format.
            Permitted Values:
                * SCORE: Outputs Average Silhouette Score,
                * SAMPLE_SCORES: Outputs Silhouette Score for each input sample,
                * CLUSTER_SCORES: Outputs Average Silhouette Score for each cluster.
            Default Value: "SCORE"
            Types: str

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
        Instance of Silhouette.
        Output teradataml DataFrames can be accessed using attribute
        references, such as SilhouetteObj.<attribute_name>.
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
        load_example_data("teradataml", ["mobile_data"])

        # Create teradataml DataFrame objects.
        mobile_data = DataFrame.from_table("mobile_data")

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1: Find the silhouette score for each input sample.
        Silhouette_result1 = Silhouette(accumulate=['feature'],
                                        id_column="row_id",
                                        cluster_id_column="userid",
                                        target_columns='"value"',
                                        output_type="SAMPLE_SCORES",
                                        data=mobile_data)

        # Print the result DataFrame.
        print(Silhouette_result1.result)

        # Example 2: Find average silhouette score of all input samples.
        Silhouette_result2 = Silhouette(id_column="row_id",
                                        cluster_id_column="userid",
                                        target_columns=['"value"'],
                                        data=mobile_data,
                                        output_type="SCORE")

        # Print the result DataFrame.
        print(Silhouette_result2.result)

        # Example 3: Find average silhouette scores of input samples for each cluster.
        Silhouette_result3 = Silhouette(id_column="row_id",
                                        cluster_id_column="userid",
                                        target_columns=['"value"'],
                                        data=mobile_data,
                                        output_type="CLUSTER_SCORES")

        # Print the result DataFrame.
        print(Silhouette_result3.result)

    """