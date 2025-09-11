def WriteNOS(data=None, location=None, authorization=None, stored_as="PARQUET", naming="RANGE", header=True, row_format=None,
             manifest_file=None, manifest_only=False, overwrite=False, include_ordering=None, include_hashby=None, 
             max_object_size="16MB", compression=None, **generic_arguments):
    """
    DESCRIPTION:
        WriteNOS() function enables access to write input teradataml DataFrame to external storage,
        like Amazon S3, Azure Blob storage, or Google Cloud Storage.
        You must have the EXECUTE FUNCTION privilege on TD_SYSFNLIB.WRITE_NOS.


    PARAMETERS:
        data:
            Required Argument.
            Specifies the input teradataml DataFrame.
            Types: teradataml DataFrame

        location:
            Optional Argument.
            Specifies the location value, which is a Uniform Resource Identifier
            (URI) pointing to location in the external object storage system.
            A URI identifying the external storage system in the format:
                /connector/endpoint/bucket_or_container/prefix
            The "location" string cannot exceed 2048 characters.
            Types: str

        authorization:
            Optional Argument.
            Specifies the authorization for accessing the external storage.
            Following are the options for using "authorization":
            * Passing access id and key as dictionary:
                authorization = {'Access_ID': 'access_id', 'Access_Key': 'secret_key'}
            * Passing access id and key as string in JSON format:
                authorization = '{"Access_ID":"access_id", "Access_Key":"secret_key"}'
            * Using Authorization Object:
                On any platform, authorization object can be specified as
                authorization = "[DatabaseName.]AuthorizationObjectName" 
                EXECUTE privilege on AuthorizationObjectName is needed.
            
            Below table specifies the USER (identification) and PASSWORD (secret_key) 
            for accessing external storage. The following table shows the supported 
            credentials for USER and PASSWORD (used in the CREATE AUTHORIZATION SQL command):
            +-----------------------+--------------------------+--------------------------+
            |     System/Scheme     |           USER           |         PASSWORD         |
            +-----------------------+--------------------------+--------------------------+
            |          AWS          |      Access Key ID       |    Access Key Secret     |
            |                       |                          |                          |
            |   Azure / Shared Key  |   Storage Account Name   |   Storage Account Key    |
            |                       |                          |                          |
            |  Azure Shared Access  |   Storage Account Name   |    Account SAS Token     |
            |    Signature (SAS)    |                          |                          |
            |                       |                          |                          |
            |      Google Cloud     |      Access Key ID       |    Access Key Secret     |
            |   (S3 interop mode)   |                          |                          |
            |                       |                          |                          |
            | Google Cloud (native) |       Client Email       |       Private Key        |
            |                       |                          |                          |
            |  Public access object |      <empty string>      |      <empty string>      |
            |        stores         | Enclose the empty string | Enclose the empty string |
            |                       |    in single straight    |    in single straight    |
            |                       |      quotes: USER ''     |    quotes: PASSWORD ''   |
            +-----------------------+--------------------------+--------------------------+
            When accessing GCS, Analytics Database uses either the S3-compatible connector or 
            the native Google connector, depending on the user credentials.
            Notes:
                * If using AWS IAM credentials, "authorization" can be omitted.
                * If S3 user account requires the use of physical or virtual security, 
                  session token can be used with Access_ID and Access_Key in this syntax:
                      authorization = {"Access_ID":"access_id", 
                                       "Access_Key":"secret_key",
                                       "Session_Token":"session_token"}
                  In which, the session token can be obtained using the AWS CLI. 
                  For example: 
                      aws sts get-session-token
            Types: str or dict

        stored_as:
            Optional Argument.
            Specifies the formatting style of the external data.
            PARQUET means the external data is formatted as Parquet.
            Permitted Values:
                * PARQUET
                * CSV
            Default Value: "PARQUET"
            Types: str

        naming:
            Optional Argument.
            Specifies how the objects containing the rows of data are named
            in the external storage:
            Permitted Values:
                * DISCRETE-
                    Discrete naming uses the ordering column values as part of the object
                    names in external storage. For example, if the "data_order_column"
                    has ["dateColumn", "intColumn"], the discrete form name of the objects 
                    written to external storage would include the values for those columns 
                    as part of the object name, which would look similar to this:
                        S3/ceph-s3.teradata.com/xz186000/2019-03-01/13/object_33_0_1.parquet
                    Where 2019-03-01 is the value for the first ordering column, "dateColumn", 
                    and 13 is the value for the second ordering column, "intColumn".
                    All rows stored in this external Parquet-formatted object contain those
                    two values.
                * RANGE-
                    Range naming includes part of the object name as range of values included 
                    in the partition for each ordering column.
                    For example, using the same "data_order_column" as above the object
                    names would look similar to this:
                        S3/ceph-s3.teradata.com/xz186000/2019-01-01/2019-03-02/9/10000/object_33_0_1.parquet
                    In this external Parquet-formatted object:
                        - 2019-01-01 and 2019-03-02 are the minimum and maximum values for 
                          the first ordering column, dateColumn.
                        - 9 and 10000 are the minimum and maximum values for the second 
                          ordering column, intColumn.
            Default Value: "RANGE"
            Types: str

        header:
            Optional Argument.
            Specifies wheather the first record contains the column names.
            Default Value: True
            Types: bool
        
        row_format:
            Optional Argument.
            Specifies the encoding format for the rows in the file type specified in 
            "stored_as".
            Notes:
                * For CSV data, encoding format is:
                      {"field_delimiter": "fd_value", 
                       "record_delimiter": "\\n", 
                       "character_set": "cs_value"}
                * For Parquet data, encoding format is:
                      {"character_set": "cs_value"}
                  field_delimiter:
                      Specifies the field delimiter. Default field delimiter is "," (comma). 
                      User can also specify a custom field delimiter, such as tab "\\t". 
                      The key name and "fd_value" are case-sensitive.
                  record_delimiter: 
                      Specifies the record delimiter, which is the line feed character, "\\n". 
                      The key name and "\\n" are case-sensitive.
                  character_set:
                      Specifies the field character set "UTF8" or "LATIN". 
                      The key name is case-sensitive, but "cs_value" is not.     
            Types: str or dict

        manifest_file:
            Optional Argument.
            Specifies the fully qualified path and file name where the manifest
            file is written. Use the format
                "/connector/end point/bucket_or_container/prefix/manifest_file_name"
            For example:
                "/S3/ceph-s3.teradata.com/xz186000/manifest/manifest.json"
            If "manifest_file" argument is not included, no manifest file is
            written.
            Types: str

        manifest_only:
            Optional Argument.
            Specifies wheather to write only a manifest file in external storage
            or not. No actual data objects are written to external storage when
            "manifest_only" is set to True. One must also use the "manifest_file" 
            option to create a manifest file in external storage. Use this option 
            to create a new manifest file in the event that a WriteNOS()
            fails due to a database abort or restart, or when network connectivity 
            issues interrupt and stop a WriteNOS() before all data has 
            been written to external storage. The manifest is created from the 
            teradataml DataFrame that is input to WriteNOS(). 
            The input must be a DataFrame of storage object names and sizes, with 
            one row per object.
            Note: 
                The input to WriteNOS() with "manifest_only" can itself incorporate
                ReadNOS(), similar to this, which uses function mappings for WriteNOS()
                and ReadNOS():
                    read_nos_obj = ReadNOS(return_type="NOSREAD_KEYS")
                    WriteNOS(data=read_nos_obj.result.filter(items =['Location', 'ObjectLength']),
                             manifest_file=manifest_file,
                             manifest_only=True)
            Function calls like above can be used if a WriteNOS() fails before
            it can create a manifest file. The new manifest file created using
            ReadNOS() reflects all data objects currently in the external
            storage location, and can aid in determining which data objects
            resulted from the incomplete WriteNOS(). 
            For more information, see Teradata Vantage - Native Object Store 
            Getting Started Guide.
            Default Value: False
            Types: bool

        overwrite:
            Optional Argument.
            Specifies whether an existing manifest file in external storage is
            overwritten with a new manifest file that has the same name.
            When set to False, WriteNOS() returns an error if a manifest file exists in
            external storage that is named identically to the value of
            "manifest_file".
            Note: 
                Overwrite must be used with "manifest_only" set to True.
            Default Value: False
            Types: bool

        include_ordering:
            Optional Argument.
            Specifies whether column(s) specified in argument "data_order_column" and
            their values are written to external storage.
            Types: bool

        include_hashby:
            Optional Argument.
            Specifies whether column(s) specified in argument "data_hash_column" and
            their values are written to external storage.
            Types: bool

        max_object_size:
            Optional Argument.
            Specifies the maximum output object size in megabytes, where
            maximum object size can range between 4 and 16. The default is the
            value of the DefaultRowGroupSize field in DBS Control. 
            For more information on DBS Control, see Teradata Vantage - Database
            Utilities.
            Default Value: "16MB"
            Types: str

        compression:
            Optional Argument.
            Specifies the compression algorithm used to compress the objects
            written to external storage.
            Note:
                For Parquet files the compression occurs inside parts of the parquet
                file instead of for the entire file, so the file extension on
                external objects remains '.parquet'.
            Permitted Values: GZIP, SNAPPY
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
                Analytic Database function supports it, else an exception is raised.


    RETURNS:
        Instance of WriteNOS.
        Output teradataml DataFrames can be accessed using attribute
        references, such as WriteNOSObj.<attribute_name>.
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

        # Check the list of available analytic functions.
        display_analytic_functions()

        # Load the example data.
        load_example_data("teradataml", "titanic")

        # Create teradataml DataFrame object.
        titanic_data = DataFrame.from_table("titanic")

        # Example 1: Writing the DataFrame to an AWS S3 location.
        obj =  WriteNOS(data=titanic_data,
                        location='/S3/s3.amazonaws.com/Your-Bucket/location/',
                        authorization={"Access_ID": "YOUR-ID", "Access_Key": "YOUR-KEY"},
                        stored_as='PARQUET')

        # Print the result DataFrame.
        print(obj.result)

        # Example 2: Write DataFrame to external storage with partition and order by
        #            column 'sex'.
        obj = WriteNOS(data=titanic_data,
                       location='/S3/s3.amazonaws.com/Your-Bucket/location/',
                       authorization={"Access_ID": "YOUR-ID", "Access_Key": "YOUR-KEY"}, 
                       data_partition_columns="sex",
                       data_order_columns="sex",
                       stored_as='PARQUET')

        # Print the result DataFrame.
        print(obj.result)

        # Example 3: Write DataFrame to external storage with hashing and order by
        #            column 'sex'.
        obj = WriteNOS(data=titanic_data,
                       location='/S3/s3.amazonaws.com/Your-Bucket/location/',
                       authorization={"Access_ID": "YOUR-ID", "Access_Key": "YOUR-KEY"},
                       data_hash_columns="sex",
                       data_order_columns="sex",
                       local_order_data=True,
                       include_hashing=True,
                       stored_as='PARQUET')

        # Print the result DataFrame.
        print(obj.result)

        # Example 4: Write DataFrame to external storage with max object size as 4MB.
        obj = WriteNOS(data=titanic_data,
                       location='/S3/s3.amazonaws.com/Your-Bucket/location/',
                       authorization={"Access_ID": "YOUR-ID", "Access_Key": "YOUR-KEY"}, 
                       include_ordering=True,
                       max_object_size='4MB',
                       compression='GZIP',
                       stored_as='PARQUET')

        # Print the result DataFrame.
        print(obj.result)

        # Example 5: Write DataFrame of manifest table into a manifest file.
        import pandas as pd
        obj_names = ['/S3/s3.amazonaws.com/YOUR-STORAGE-ACCOUNT/20180701/ManifestFile/object_33_0_1.parquet',
                     '/S3/s3.amazonaws.com/YOUR-STORAGE-ACCOUNT/20180701/ManifestFile/object_33_6_1.parquet',
                     '/S3/s3.amazonaws.com/YOUR-STORAGE-ACCOUNT/20180701/ManifestFile/object_33_1_1.parquet']
        obj_size = [2803, 2733, 3009]
        manifest_df = pd.DataFrame({'ObjectName':obj_names, 'ObjectSize': obj_size})
        from teradataml import copy_to_sql
        copy_to_sql(manifest_df, "manifest_df")
        manifest_df = DataFrame("manifest_df")
        obj = WriteNOS(data=manifest_df,
                       location='YOUR-STORAGE-ACCOUNT/20180701/ManifestFile2/',
                       authorization={"Access_ID": "YOUR-ID", "Access_Key": "YOUR-KEY"},
                       manifest_file='YOUR-STORAGE-ACCOUNT/20180701/ManifestFile2/manifest2.json',
                       manifest_only=True,
                       stored_as='PARQUET')

        # Print the result DataFrame.
        print(obj.result)

        # Example 7: Write teradataml DataFrame to external object store in CSV format with a header
        #            and field delimiter as '\\t' (tab).
        obj = WriteNOS(location=location,
                       authorization={"Access_ID": "YOUR-ID", "Access_Key": "YOUR-KEY"},
                       stored_as="CSV",
                       header=True,
                       row_format={"field_delimiter":"\\t", "record_delimiter":"\\n"},
                       data=titanic_data)
        
        # Print the result DataFrame.
        print(obj.result)

        # Note: 
        #   Before proceeding, verify with your database administrator that you have the 
        #   correct privileges, an authorization object, and a function mapping (for WRITE_NOS 
        #   function).
        
        # If function mapping for WRITE_NOS Analytic database function is created 
        # as 'WRITE_NOS_FM' and location and authorization object are mapped,
        # then set function mapping with teradataml options as below.
        
        # Example 8: Writing the DataFrame using function mapping.
        from teradataml.options.configure import configure
        configure.write_nos_function_mapping = "WRITE_NOS_FM"
        
        obj =  WriteNOS(data=titanic_data, stored_as='PARQUET')

        # Print the result DataFrame.
        print(obj.result)
    """