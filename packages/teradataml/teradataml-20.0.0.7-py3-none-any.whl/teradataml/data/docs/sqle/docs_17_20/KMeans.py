def KMeans(data=None, centroids_data=None, id_column=None, target_columns=None, num_clusters=None,
           seed=None, threshold=0.0395, iter_max=10, num_init=1, output_cluster_assignment=False,
           initialcentroids_method="RANDOM", **generic_arguments):
    """
    DESCRIPTION:
        The K-means() function groups a set of observations into k clusters
        in which each observation belongs to the cluster with the nearest mean
        (cluster centers or cluster centroid). This algorithm minimizes the
        objective function, that is, the total Euclidean distance of all data points
        from the center of the cluster as follows:
            1. Specify or randomly select k initial cluster centroids.
            2. Assign each data point to the cluster that has the closest centroid.
            3. Recalculate the positions of the k centroids.
            4. Repeat steps 2 and 3 until the centroids no longer move.
        The algorithm doesn't necessarily find the optimal configuration as it
        depends significantly on the initial randomly selected cluster centers.
        User can run the function multiple times to reduce the effect of this limitation.

        Also, this function returns the within-cluster-squared-sum, which user can use to
        determine an optimal number of clusters using the Elbow method.
        Notes:
            * This function doesn't consider the "data" and "centroids_data"
              input rows that have a NULL entry in the specified "target_columns".
            * The function can produce deterministic output across different machine
              configurations if user provide the "centroids_data".
            * The function randomly samples the initial centroids from the "data",
              if "centroids_data" not provided. In this case, use of "seed"
              argument makes the function output deterministic on a machine with an
              assigned configuration. However, using the "seed" argument won't guarantee
              deterministic output across machines with different configurations.
            * This function requires the UTF8 client character set for UNICODE data.
            * This function does not support Pass Through Characters (PTCs).
            * For information about PTCs, see Teradata Vantage™ - Analytics Database
              International Character Set Support.
            * This function does not support KanjiSJIS or Graphic data types.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        centroids_data:
            Optional Argument.
            Specifies the input teradataml DataFrame containing
            set of initial centroids.
            Note:
                * This argument is not required if "num_clusters" provided.
                * If provided, the function uses the initial centroids
                  from this input.
            Types: teradataml DataFrame

        id_column:
            Required Argument.
            Specifies the input data column name that has the
            unique identifier for each row in the input.
            Types: str

        target_columns:
            Required Argument.
            Specifies the name(s) of the column(s) in "data" for clustering.
            Types: str OR list of Strings (str)

        num_clusters:
            Optional Argument.
            Specifies the number of clusters to be created.
            Note:
                This argument is not required if "centroids_data" provided.
            Types: int

        seed:
            Optional Argument.
            Specifies a non-negative integer value to randomly select the initial
            cluster centroid positions from the input.
            Note:
                * This argument is not required if "centroids_data" provided.
                * Random integer value will be used for "seed", if not passed.
            Types: int

        threshold:
            Optional Argument.
            Specifies the convergence threshold. The algorithm converges if the distance
            between the centroids from the previous iteration and the current iteration
            is less than the specified value.
            Default Value: 0.0395
            Types: float OR int

        iter_max:
            Optional Argument.
            Specifies the maximum number of iterations for the K-means algorithm.
            The algorithm stops after performing the specified number of iterations
            even if the convergence criterion is not met.
            Default Value: 10
            Types: int

        num_init:
            Optional Argument.
            Specifies the number of times, the k-means algorithm will be run with different
            initial centroid seeds. The function will emit out the model having
            the least value of Total Within Cluster Squared Sum.
            Note:
                This argument is not required if "centroids_data" is provided.
            Default Value: 1
            Types: int

        output_cluster_assignment:
            Optional Argument.
            Specifies whether to output Cluster Assignment information.
            Default Value: False
            Types: bool
        
        initialcentroids_method:
            Optional Argument.
            Specifies the initialization method to be used for selecting initial set of centroids.
            Permitted Values: 'RANDOM', 'KMEANS++'
            Default Value: 'RANDOM'
            Note:
                * This argument is not required if "centroids_data" is provided.
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
        Instance of KMeans.
        Output teradataml DataFrames can be accessed using attribute
        references, such as KMeansObj.<attribute_name>.
        Output teradataml DataFrame attribute names are:
            1. result
            2. model_data


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
        load_example_data("kmeans", "computers_train1")
        load_example_data("kmeans",'kmeans_table')

        # Create teradataml DataFrame objects.
        computers_train1 = DataFrame.from_table("computers_train1")
        kmeans_tab = DataFrame('kmeans_table')

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Example 1 : Grouping a set of observations into 2 clusters in which
        #             each observation belongs to the cluster with the nearest mean.
        KMeans_out = KMeans(id_column="id",
                            target_columns=['price', 'speed'],
                            data=computers_train1,
                            num_clusters=2)

        # Print the result DataFrames.
        print(KMeans_out.result)
        print(KMeans_out.model_data)

        # Example 2 : Grouping a set of observations by specifying initial
        #             centroid data.

        # Get the set of initial centroids by accessing the group of rows
        # from input data.
        kmeans_initial_centroids_table = computers_train1.loc[[19, 97]]
        kmeans_initial_centroids = kmeans_tab.loc[[2, 4]]

        KMeans_out_1 = KMeans(id_column="id",
                              target_columns=['price', 'speed'],
                              data=computers_train1,
                              centroids_data=kmeans_initial_centroids_table)

        # Print the result DataFrames.
        print(KMeans_out_1.result)
        print(KMeans_out_1.model_data)

        # Example 3 : Grouping a set of observations into 2 clusters by
        #             specifying the number of clusters and seed value
        #             with output cluster assignment information.
        obj = KMeans(data=kmeans_tab,
             id_column='id',
             target_columns=['c1', 'c2'],
             threshold=0.0395,
             iter_max=3,
             centroids_data=kmeans_initial_centroids,
             output_cluster_assignment=True
            )
             
        # Print the result DataFrames.
        print(obj.result)

        # Example 4 : Grouping a set of observations into 3 clusters by
        #             specifying the number of clusters for initial centroids
        #             method as KMEANS++.
        obj = KMeans(data=kmeans_tab,
             id_column='id',
             target_columns=['c1', 'c2'],
             threshold=0.0395,
             iter_max=3,
             num_clusters=3,
             output_cluster_assignment=True,
             initialcentroids_method="KMEANS++"
            )
        
        # Print the result DataFrames.
        print(obj.result) 

    """
