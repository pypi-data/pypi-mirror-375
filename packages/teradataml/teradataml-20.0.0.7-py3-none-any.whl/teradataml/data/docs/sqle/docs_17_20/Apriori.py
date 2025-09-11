def Apriori(data=None, target_column=None, id_column=None, partition_columns=None,
            max_len=2, delimiter=",", is_dense_input=False, patterns_or_rules=None,
            support=0.01, **generic_arguments):
    """
    DESCRIPTION:
        The Apriori() function finds patterns and calculates different statistical metrics to
        understand the influence of the occurrence of a set of items on others.

    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        target_column:
            Required Argument.
            Specifies the input teradataml DataFrame column which contains the data to filter.
            Types: str

        id_column:
            Optional Argument.
            Specifies the name of the column that uniquely groups the items that are purchased together. 
            Applicable only when `is_dense_input` is False.
            Types: str

        partition_columns:
            Optional Argument.
            Specifies the column name(s) in the "data" to partition the input.
            Types: str or list of str

        max_len:
            Optional Argument.
            Specifies the maximum number of items in the item set. 
            "max_len" must be greater than or equal to 1 and less than or equal to 20.
            Default Value: 2
            Types: int

        delimiter:
            Optional Argument, Required when "is_dense_input" is set to True.
            Specifies a character or string that separates words in the input text.
            Default Value: ","
            Types: str


        is_dense_input:
            Optional Argument.
            Specifies whether input data is in dense format or not. 
            When set to True, function considers the  data is in dense format. 
            Otherwise function considers  data is not in dense format.
            Default Value: False
            Types: bool

        patterns_or_rules:
            Optional Argument.
            Specifies whether to emit PATTERNS or RULES as output.
            Permitted Values: "PATTERNS", "RULES"
            Types: str

        support:
            Optional Argument.
            Specifies the support value (minimum occurrence threshold) of the itemset.
            Default Value: 0.01
            Types: float

        **generic_arguments:
            Optional Argument.
            Specifies the generic keyword arguments SQLE functions accept. Below are the generic
            keyword arguments:
                persist:
                    Optional Argument.
                    Specifies whether to persist the results of the function in a table or not.
                    When set to True, results are persisted in a table; otherwise, results are
                    garbage collected at the end of the session.
                    Default Value: False
                    Types: bool
                
                volatile:
                    Optional Argument.
                    Specifies whether to put the results of the function in a volatile table or not.
                    When set to True, results are stored in a volatile table; otherwise not.
                    Default Value: False
                    Types: bool

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
        Instance of Apriori.
        Output teradataml DataFrames can be accessed using attribute references, such as AprioriObj.<attribute_name>.
        Output teradataml DataFrame attribute name is:
            result

    RAISES:
        TeradataMlException, TypeError, ValueError

    EXAMPLES:
        # Notes:
        #     1. Get the connection to Vantage to execute the function.
        #     2. One must import the required functions mentioned in the example from teradataml.
        #     3. Function will raise an error if not supported on the Vantage user is connected to.

        # Load the example data.
        load_example_data("apriori", ["trans_dense","trans_sparse"])

        # Create teradataml DataFrame objects.
        dense_table = DataFrame.from_table("trans_dense")
        sparse_table = DataFrame.from_table("trans_sparse")


        # Check the list of available analytic functions.
        display_analytic_functions()
        
        # Import function Apriori.
        from teradataml import Apriori

        # Example 1: Find patterns in the input data with DENSE DATA, PARTITION,RULES .
        Apriori_out = Apriori(data=dense_table, target_column="item",
                              partition_columns=["location"], max_len=2,
                              patterns_or_rules="rules", support=0.01)

        # Print the result DataFrame.
        print(Apriori_out.result)

        # Example 2: Find patterns in the input data with SPARSE DATA, NO PARTITIONS, PATTERNS.
        Apriori_out = Apriori(data=sparse_table, target_column="item",
                              id_column="tranid", max_len=3)
                                    
        # Print the result DataFrame.
        print(Apriori_out.result)
    """