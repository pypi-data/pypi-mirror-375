"""
Copyright (c) 2024 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements the core framework that allows user to use Teradata Enterprise Feature Store.
"""
import os.path
import operator
import random
from functools import reduce
from sqlalchemy import literal_column
from teradataml.context.context import get_connection, _get_current_databasename
from teradataml.common.constants import SQLConstants, AccessQueries
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.dataframe.sql import _SQLColumnExpression as Col
from teradataml.dbutils.dbutils import _create_database, _create_table, db_drop_table, execute_sql, Grant, Revoke, \
                                       _update_data, _delete_data, db_transaction, db_list_tables, _insert_data, \
    _is_trigger_exist, db_drop_view, _get_quoted_object_name
from teradataml.store.feature_store.constants import *
from teradataml.store.feature_store.mind_map import _TD_FS_MindMap_Template
from teradataml.store.feature_store.models import *
from teradataml.store.feature_store.constants import _FeatureStoreDFContainer
from teradataml.common.sqlbundle import SQLBundle
from teradataml.utils.validators import _Validators
from teradataml.store.feature_store.utils import _FSUtils


class FeatureStore:
    """Class for FeatureStore."""

    def __init__(self,
                 repo,
                 data_domain=None,
                 check=True):
        """
        DESCRIPTION:
            Method to create FeatureStore in teradataml.
            Note:
                * One should establish a connection to Vantage using create_context()
                  before creating a FeatureStore object.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the repository name.
                Types: str.

        data_domain:
            Optional Argument.
            Specifies the data domain to which FeatureStore points to.
            Note:
                * If not specified, then default database name is considered as data domain.
            Types: str

        check:
            Optional Argument.
            Specifies whether to check the existence of the Feature store DB objects or not.
            When set to True, the method checks for the existence of Feature store DB objects.
            Otherwise, the method does not verify the existence of Feature store DB objects.
            Default Value: True
            Types: bool

        RETURNS:
            Object of FeatureStore.

        RAISES:
            None

        EXAMPLES:
            # Example 1: Create an instance of FeatureStore for repository 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            >>> fs.setup()
            True
            
            >>> fs
            VantageFeatureStore(abc)-v2.0.0
        """
        argument_validation_params = []
        argument_validation_params.append(["repo", repo, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        connection = get_connection()
        if connection is None:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                      MessageCodes.CONNECTION_FAILURE)

        # Do not validate the existance of repo as it consumes a network call.
        self.__repo = repo
        self.__version = ""

        # Declare SQLBundle to use it further.
        self.__sql_bundle = SQLBundle()

        # Store all the DF's here so no need to create these every time.
        self.__df_container = {}

        # Store the table names here. Then use this where ever required.
        self.__table_names = EFS_DB_COMPONENTS

        # Declare getter's for getting the corresponding DataFrame's using _FeatureStoreDFContainer directly.
        # Only keep the lambda functions that are actually used in the codebase
        self.__get_features_df = lambda : _FeatureStoreDFContainer.get_df("feature", self.__repo, self.__data_domain)
        self.__get_features_wog_df = lambda : _FeatureStoreDFContainer.get_df("feature_wog", self.__repo, self.__data_domain)
        self.__get_archived_features_df = lambda : _FeatureStoreDFContainer.get_df("feature_staging", self.__repo, self.__data_domain)
        self.__get_feature_group_df = lambda : _FeatureStoreDFContainer.get_df("feature_group", self.__repo, self.__data_domain)
        self.__get_archived_feature_group_df = lambda : _FeatureStoreDFContainer.get_df("feature_group_staging", self.__repo, self.__data_domain)
        self.__get_entity_df = lambda : _FeatureStoreDFContainer.get_df("entity", self.__repo, self.__data_domain)
        self.__get_archived_entity_df = lambda : _FeatureStoreDFContainer.get_df("entity_staging", self.__repo, self.__data_domain)
        self.__get_data_source_df = lambda : _FeatureStoreDFContainer.get_df("data_source", self.__repo, self.__data_domain)
        self.__get_archived_data_source_df = lambda : _FeatureStoreDFContainer.get_df("data_source_staging", self.__repo, self.__data_domain)
        self.__get_dataset_catalog_df = lambda : _FeatureStoreDFContainer.get_df("dataset_catalog", self.__repo, self.__data_domain)
        self.__get_data_domain_df = lambda : _FeatureStoreDFContainer.get_df("data_domain", self.__repo, self.__data_domain)
        self.__get_feature_process_df = lambda : _FeatureStoreDFContainer.get_df("feature_process", self.__repo, self.__data_domain)
        self.__get_features_metadata_df = lambda : _FeatureStoreDFContainer.get_df("feature_metadata", self.__repo, self.__data_domain)
        self.__get_feature_info_df = lambda: _FeatureStoreDFContainer.get_df("feature_info", self.__repo, self.__data_domain)
        self.__get_dataset_features_df = lambda: _FeatureStoreDFContainer.get_df("dataset_features", self.__repo, self.__data_domain)
        self.__get_feature_runs_df = lambda : _FeatureStoreDFContainer.get_df("feature_runs", self.__repo, self.__data_domain)
        self.__get_without_valid_period_df = lambda df: df.drop(columns=['ValidPeriod'])
        self.__get_feature_version = lambda: _FeatureStoreDFContainer.get_df("feature_version", self.__repo, self.__data_domain)

        self.__good_status = "Good"
        self.__bad_status = "Bad"
        self.__repaired_status = "Repaired"

        self.__data_domain = data_domain if data_domain is not None else _get_current_databasename()

        self.__repo_exists = connection.dialect._get_database_names(connection, self.__repo)

        if check:
            return self.__validate_repo_exists()
        else:
            # If check is False, then do not check for the existence of DB objects.
            self.__add_data_domain()

    def __validate_repo_exists(self):
        """
        Validate the repository.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            ValueError: If the repo is invalid.
        """
        # Check whether the repo exists or not.
        if not self.__repo_exists:
            print("Repo {} does not exist. Run FeatureStore.setup() " \
                  "to create the repo and setup FeatureStore.".format(self.__repo))
            return

        # Check whether all the EFS tables exist or not.
        existing_tabs = db_list_tables(schema_name=self.__repo, object_name='_efs%')
        if not existing_tabs.empty:
            existing_tables = set(existing_tabs['TableName'].tolist())
            all_tables_exist = all(val in existing_tables for val in EFS_TABLES.values())
        else:
            all_tables_exist = False
        # Check whether all the EFS triggers exist or not.
        all_triggers_exist, num_trigger_exist = _is_trigger_exist(self.__repo, list(EFS_TRIGGERS.values()))

        # Check whether all the EFS tables and triggers exist or not.
        # If exists, then insert the data domain name into _efs_data_domain table.
        if all_tables_exist and all_triggers_exist:
            self.__add_data_domain()
            # If all the tables and triggers are available, then
            # FeatureStore is ready to use.
            print("FeatureStore is ready to use.")
        # All table and triggers does not exist.
        # If the count of tables and triggers is 0, then
        # FeatureStore is not setup.
        elif num_trigger_exist == 0 and len(existing_tabs) == 0:
            print("FeatureStore is not setup(). Run FeatureStore.setup() to setup FeatureStore.")
        else:
            print("Some of the feature store objects are missing. Run FeatureStore.repair() to create missing objects.")

    @property
    def data_domain(self):
        """
        DESCRIPTION:
            Get the data domain.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Example 1: Use existing FeatureStore 'vfs_v1' to get the data domain.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='test_domain')
            FeatureStore is ready to use.
            >>> fs.data_domain
            'test_domain'
        """
        return self.__data_domain

    @data_domain.setter
    def data_domain(self, value):
        """
        DESCRIPTION:
            Set the data domain.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the data domain name.
                Types: str.

        RETURNS:
            None.

        RAISES:
            None

        EXAMPLES:
            # Example 1: Create or use existing FeatureStore for repository 'abc' and
            #            then change the data domain to 'xyz'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('abc')
            FeatureStore is ready to use.

            # Set the data domain to 'xyz'.
            >>> fs.data_domain = 'xyz'

            # Get the data domain.
            >>> fs.data_domain
            'xyz'
        """
        argument_validation_params = []
        argument_validation_params.append(["value", value, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Set the data domain value.
        self.__data_domain = value
        self.__add_data_domain()

    def __add_data_domain(self):
        """
        DESCRIPTION:
            Internal method to add the data domain.

        PARAMETERS:
            data_domain:
                Required Argument.
                Specifies the data domain name.
                Types: str.

        RETURNS:
            None.

        RAISES:
            None

        EXAMPLES:
            >>> self.__add_data_domain()
        """
        # Add the data domain to the EFS_DATA_DOMAINS table.
        _insert_data(table_name=self.__table_names['data_domain'],
                     schema_name=self.__repo,
                     values=(self.__data_domain, dt.utcnow()),
                     columns=["name", "created_time"],
                     ignore_errors=[2801])

    @property
    def repo(self):
        """
        DESCRIPTION:
            Get the repository.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Example 1: Get the repository name from FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            
            # Get the repository name.
            >>> fs.repo
            'vfs_v1'
        """
        return self.__repo

    @repo.setter
    def repo(self, value):
        """
        DESCRIPTION:
            Set the repository.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the repository name.
                Types: str.

        RETURNS:
            None.

        RAISES:
            None

        EXAMPLES:
            # Example 1: Create a FeatureStore for repository 'abc' and
            #            then change the repository to 'xyz'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('abc')
            FeatureStore is ready to use.

            # Get the repository name.
            >>> fs.repo
            'abc'

            # Set the repository to 'xyz'.
            >>> fs.repo = 'xyz'
            >>> fs.repo
            'xyz'
        """
        argument_validation_params = []
        argument_validation_params.append(["value", value, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        # remove all entries from container so they will be automatically
        # point to new repo for subsequent API's.
        self.__repo_exists = get_connection().dialect._get_database_names(get_connection(), 
                                                                          value)
        self.__validate_repo_exists()

        self.__df_container.clear()

        self.__version = None

        # Set the repo value.
        self.__repo = value

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for FeatureStore object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            # Setup FeatureStore for this repository.
            >>> fs.setup()
            
            # Get the string representation of FeatureStore.
            >>> fs
            'VantageFeatureStore(vfs_v1)-v2.0.0'

        """
        s = "VantageFeatureStore({})".format(self.__repo)
        try:
            version = "-v{}".format(self.__get_version())
        except Exception as e:
            version = ""
        return "{}{}".format(s, version)

    def __get_version(self):
        """
        DESCRIPTION:
            Internal method to get the FeatureStore version.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        if not self.__version:
            sql = "SELECT version FROM {}.{}".format(self.__repo, self.__table_names['version'])
            self.__version = next(execute_sql(sql))[0]
        return self.__version

    @staticmethod
    def list_repos() -> DataFrame:
        """
        DESCRIPTION:
            Function to list down the repositories.

        PARAMETERS:
            None

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Example 1: List all the FeatureStore repositories using FeatureStore class.
            >>> FeatureStore.list_repos()
                repos
            0  vfs_v1

            # Example 2: List all the FeatureStore repositories using FeatureStore object.
            >>> fs = FeatureStore('vfs_v1')
            FeatureStore is ready to use.
            
            >>> fs.list_repos()
                repos
            0  vfs_v1

        """
        return DataFrame.from_query("select distinct DataBaseName as repos from dbc.tablesV where TableName='{}'".format(
            EFS_DB_COMPONENTS['version']))

    def setup(self, perm_size='10e9', spool_size='10e8'):
        """
        DESCRIPTION:
            Function to setup all the required objects in Vantage for the specified
            repository.
            Note:
                The function checks whether repository exists or not. If not exists,
                it first creates the repository and then creates the corresponding tables.
                Hence make sure the user with which is it connected to Vantage
                has corresponding access rights for creating DataBase and creating
                tables in the corresponding database.

        PARAMETERS:
            perm_size:
                Optional Argument.
                Specifies the number of bytes to allocate to FeatureStore "repo"
                for permanent space.
                Note:
                    Exponential notation can also be used.
                Default Value: 10e9
                Types: str or int

            spool_size:
                Optional Argument.
                Specifies the number of bytes to allocate to FeatureStore "repo"
                for spool space.
                Note:
                    Exponential notation can also be used.
                Default Value: 10e8
                Types: str or int

        RETURNS:
            bool

        RAISES:
            TeradatamlException

        EXAMPLES:
            # Example 1: Setup FeatureStore for repository 'vfs_v1'.
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            >>> fs
            VantageFeatureStore(vfs_v1)-v2.0.0

            # Example 2: Setup FeatureStore for repository 'vfs_v2' with custom perm_size and spool_size.
            # Create FeatureStore for repo 'vfs_v2'.
            >>> fs = FeatureStore("vfs_v2")
            Repo vfs_v2 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            # Setup FeatureStore for this repository.
            >>> fs.setup(perm_size='50e6', spool_size='50e6')
            True

            >>> fs
            VantageFeatureStore(vfs_v2)-v2.0.0

        """
        # If repo does not exist, then create it.
        if not self.__repo_exists:
            _create_database(self.__repo, perm_size, spool_size)

        # Check whether version table exists or not. If exist, assume all
        # tables are available.
        all_tables_exist = get_connection().dialect.has_table(
            get_connection(), self.__table_names['version'], schema=self.__repo)

        if not all_tables_exist:
            # Create the object tables.
            for table_spec, table_name in EFS_TABLES.items():
                execute_sql(table_spec.format(self.__repo, table_name))
            # Create the Triggers.
            for trigger_spec, trg_name in EFS_TRIGGERS.items():
                alter_name = trg_name.split('_trg')[0]
                insert_name = self.__repo+'.'+alter_name+'_staging'
                execute_sql(trigger_spec.format(self.__repo, trg_name,
                                                alter_name, insert_name))

            # Create feature versions view.
            sql = EFS_FEATURE_VERSION.format(self.__repo,
                                             EFS_DB_COMPONENTS['feature_version'],
                                             self.__repo,
                                             self.__table_names['feature_process']
                                             )
            execute_sql(sql)

            # After the setup is done, populate the version.
            insert_model = "insert into {}.{} values (?, ?);".format(self.__repo, self.__table_names['version'])
            execute_sql(insert_model, (EFS_VERSION_, datetime.datetime.now()))

            # Create the data domain in _efs_data_domain table.
            self.__add_data_domain()

        if self.__repo_exists and all_tables_exist:
            print("EFS is already setup for the repo {}.".format(self.__repo))

        # Set the repo_exists to True
        self.__repo_exists = True
        return True

    @property
    def grant(self):
        """
        DESCRIPTION:
            Grants access on FeatureStore.
            Note:
                One must have admin access to grant access.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            OperationalError

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v2'.
            >>> fs = FeatureStore("vfs_v2")
            Repo vfs_v2 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore. 

            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Grant read access on FeatureStore to user 'BoB'.
            >>> fs.grant.read('BoB')
            True

            # Example 2: Grant write access on FeatureStore to user 'BoB'.
            >>> fs.grant.write('BoB')
            True

            # Example 3: Grant read and write access on FeatureStore to user 'BoB'.
            >>> fs.grant.read_write('BoB')
            True

        """
        return Grant(objects=AccessQueries,
                     database=self.__repo)

    @property
    def revoke(self):
        """
        DESCRIPTION:
            Revokes access on FeatureStore.
            Note:
                One must have admin access to revoke access.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            OperationalError

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Revoke read access on FeatureStore from user 'BoB'.
            >>> fs.revoke.read('BoB')
            True

            # Example 2: Revoke write access on FeatureStore from user 'BoB'.
            >>> fs.revoke.write('BoB')
            True

            # Example 3: Revoke read and write access on FeatureStore from user 'BoB'.
            >>> fs.revoke.read_write('BoB')
            True
        """
        return Revoke(objects=AccessQueries,
                      database=self.__repo)

    def repair(self):
        """
        DESCRIPTION:
            Repairs the existing repo.
            Notes:
                 * The method checks for the corresponding missing database objects which are
                   required for FeatureStore. If any of the database object is not available,
                   then it tries to create the object.
                 * The method repairs only the underlying tables and not data inside the
                   corresponding table.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            # Example 1: Repair FeatureStore repo 'vfs_v1'.
            # Create FeatureStore for repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            # Setup FeatureStore for this repository.
            >>> fs.setup()

            # Drop the data_source_staging table to simulate the missing object.
            >>> from teradataml import db_drop_table
            >>> db_drop_table(schema_name='vfs_v1', table_name=EFS_DB_COMPONENTS['data_source_staging'])

            # Verify the missing object by creating FeatureStore again.
            >>> fs = FeatureStore("vfs_v1")
            Some of the feature store objects are missing. Run FeatureStore.repair() to create missing objects.

            >>> fs.repair()
            Successfully repaired the following objects: _efs_data_source_staging
            True
        """
        # Check whether the repo exists or not.    
        if not self.__repo_exists:
            print("Repo '{}' does not exist. Run FeatureStore.setup() " \
                  "to create the repo and setup FeatureStore.".format(self.__repo))
            return False
        
        # Get all existing EFS tables in the repo
        existing_tabs = db_list_tables(schema_name=self.__repo, object_name='_efs%')
        existing_tables = set(existing_tabs['TableName'].tolist())

        # Get non-existing tables in the order of EFS_TABLES.values()
        non_existing_tables = {
                                table_spec: table_name
                                for table_spec, table_name in EFS_TABLES.items()
                                if table_name not in existing_tables
                              }

        # Get all existing EFS triggers in the repo
        sql = SQLBundle()._get_sql_query(SQLConstants.SQL_LIST_TRIGGERS).format(self.__repo, '_efs%')
        existing_triggers = {row[0] for row in execute_sql(sql).fetchall()}

        # Get non-existing triggers in the order of EFS_TRIGGERS.values()
        non_existing_triggers = {
                                 trigger_spec: trigger_name
                                 for trigger_spec, trigger_name in EFS_TRIGGERS.items()
                                 if trigger_name not in existing_triggers
                                }

        # Check if feature_version view exists (it shows up in existing_tables from db_list_tables)
        feature_version_exists = self.__table_names['feature_version'] in existing_tables

        # Return False only if all tables, triggers, and views exist
        if not non_existing_tables and not non_existing_triggers and feature_version_exists:
            print("repo '{}' is ready to use and do not need any repair.".format(self.__repo))
            return False

        failed_creation = []
        created = []
        # Iterating over EFS_TABLES based on the non-existing tables
        for table_spec, table_name in non_existing_tables.items():
            try:
                execute_sql(table_spec.format(self.__repo, table_name))
                created.append(table_name)
            except Exception as e:
                # If any table creation fails, then add it to the failed list
                failed_creation.append((f"Table '{table_name}'", str(e)))

        # Iterating over EFS_TRIGGERS based on the non-existing triggers
        for trigger_spec, trigger_name in non_existing_triggers.items():
            alter_name = trigger_name.split('_trg')[0]
            insert_name = self.__repo + '.' + alter_name + '_staging'
            try:
                execute_sql(trigger_spec.format(self.__repo, trigger_name,
                                                alter_name, insert_name))
                created.append(trigger_name)
            except Exception as e:
                # If any trigger creation fails, then add it to the failed list
                failed_creation.append((f"Trigger '{trigger_name}'", str(e)))

        # Create feature versions view if it doesn't exist
        if not feature_version_exists:
            try:
                sql = EFS_FEATURE_VERSION.format(self.__repo,
                                                 EFS_DB_COMPONENTS['feature_version'],
                                                 self.__repo,
                                                 self.__table_names['feature_process'])
                execute_sql(sql)
                created.append(EFS_DB_COMPONENTS['feature_version'])
            except Exception as e:
                failed_creation.append((f"View '{EFS_DB_COMPONENTS['feature_version']}'", str(e)))

        # If any of the table or trigger creation fails, then return False
        if failed_creation:
            print("The following objects could not be repaired:")
            for obj, reason in failed_creation:
                print(f"  - {obj}: {reason}")
            return False

        print("Successfully repaired the following objects: {}".format(", ".join(created)))
        return True

    def list_features(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the features.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective features or archived features.
                When set to False, effective features in FeatureStore are listed,
                otherwise, archived features are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Create teradataml DataFrame.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True
            
            # Create a FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name='sales',
            ...                                  entity_columns='accounts',
            ...                                  df=df,
            ...                                  timestamp_column='datetime')
            # Apply the FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Example 1: List all the effective Features in the repo 'vfs_v1'.
            >>> fs.list_features()
                            id column_name description  tags data_type feature_type  status               creation_time modified_time group_name
            name data_domain                                                                                                                      
            Apr  ALICE         4         Apr        None  None    BIGINT   CONTINUOUS  ACTIVE  2025-07-28 03:17:31.262501          None      sales
            Jan  ALICE         2         Jan        None  None    BIGINT   CONTINUOUS  ACTIVE  2025-07-28 03:17:30.056273          None      sales
            Mar  ALICE         3         Mar        None  None    BIGINT   CONTINUOUS  ACTIVE  2025-07-28 03:17:30.678060          None      sales
            Feb  ALICE         1         Feb        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 03:17:29.403242          None      sales

            # Example 2: List all the archived Features in the repo 'vfs_v1'.
            # Note: Feature can only be archived when it is not associated with any Group.
            #       Let's remove Feature 'Feb' from FeatureGroup.
            >>> fg.remove_feature(fs.get_feature('Feb'))
            True
            
            # Apply the modified FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Archive Feature 'Feb'.
            >>> fs.archive_feature('Feb')
            Feature 'Feb' is archived.
            True

            # List all the archived Features in the repo 'vfs_v1'.
            >>> fs.list_features(archived=True)
               id name data_domain column_name description  tags data_type feature_type  status               creation_time modified_time               archived_time group_name
            0   1  Feb       ALICE         Feb        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 03:17:29.403242          None  2025-07-28 03:19:58.950000      sales
            >>>
        """
        return self.__get_archived_features_df() if archived else self.__get_features_df()

    def list_entities(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the entities.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective entities or archived entities.
                When set to False, effective entities in FeatureStore are listed,
                otherwise, archived entities are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create teradataml DataFrame.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name='sales',
            ...                                  entity_columns='accounts',
            ...                                  df=df,
            ...                                  timestamp_column='datetime')
            # Apply the FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Example 1: List all the effective Entities in the repo 'vfs_v1'.
            >>> fs.list_entities()
                              description               creation_time               modified_time entity_column
            name  data_domain                                                                                  
            sales ALICE              None  2025-07-28 03:17:31.558796  2025-07-28 03:19:41.233953      accounts
            >>>

            # Example 2: List all the archived Entities in the repo 'vfs_v1'.
            # Note: Entity cannot be archived if it is a part of FeatureGroup.
            #       First create another Entity, and update FeatureGroup with
            #       other Entity. Then archive Entity 'sales'.
            >>> entity = Entity('store_sales', columns=df.accounts)
            # Update new entity to FeatureGroup.
            >>> fg.apply(entity)
            True

            # Update FeatureGroup to FeatureStore. This will update Entity
            #    from 'sales' to 'store_sales' for FeatureGroup 'sales'.
            >>> fs.apply(fg)
            True

            # Let's archive Entity 'sales' since it is not part of any FeatureGroup.
            >>> fs.archive_entity('sales')
            Entity 'sales' is archived.
            True
            >>>

            # List the archived entities.
            >>> fs.list_entities(archived=True)
                                    description               creation_time modified_time entity_column
            name        data_domain                                                                    
            store_sales ALICE              None  2025-07-28 03:23:40.322424          None      accounts
            >>>
        """
        return self.__get_archived_entity_df() if archived else self.__get_entity_df()

    def list_data_sources(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the Data Sources.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective data sources or archived data sources.
                When set to False, effective data sources in FeatureStore are listed,
                otherwise, archived data sources are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, FeatureStore, load_example_data
            # Create teradataml DataFrame.
            >>> load_example_data("dataframe", "admissions_train")
            >>> admissions = DataFrame("admissions_train")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create DataSource using teradataml DataFrame.
            >>> ds = DataSource(name='admissions', source=admissions)
            # Apply the DataSource to FeatureStore.
            >>> fs.apply(ds)
            True

            # Example 1: List all the effective DataSources in the repo 'vfs_v1'.
            >>> fs.list_data_sources()
                                   description timestamp_column                            source               creation_time               modified_time
            name       data_domain                                                                                                                       
            admissions ALICE              None             None  select * from "admissions_train"  2025-07-28 03:26:53.507807                        None

            # Example 2: List all the archived DataSources in the repo 'vfs_v1'.
            # Let's first archive the DataSource.
            >>> fs.archive_data_source('admissions')
            DataSource 'admissions' is archived.
            True

            # List archived DataSources.
            >>> fs.list_data_sources(archived=True)
                     name data_domain description timestamp_column                            source               creation_time modified_time               archived_time
            0  admissions       ALICE        None             None  select * from "admissions_train"  2025-07-28 03:26:53.507807          None  2025-07-28 03:28:17.160000
            >>>
        """
        return self.__get_archived_data_source_df() if archived else self.__get_data_source_df()

    def list_feature_groups(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            List all the FeatureGroups.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to list effective feature groups or archived feature groups.
                When set to False, effective feature groups in FeatureStore are listed,
                otherwise, archived feature groups are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import FeatureGroup, FeatureStore, load_example_data
            # Create teradataml DataFrame.
            >>> load_example_data("dataframe", "admissions_train")
            >>> admissions=DataFrame("admissions_train")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create a FeatureGroup from DataFrame.
            >>> fg = FeatureGroup.from_DataFrame("admissions", df=admissions, entity_columns='id')
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Example 1: List all the effective FeatureGroups in the repo 'vfs_v1'.
            >>> fs.list_feature_groups()
                                   description data_source_name  entity_name               creation_time               modified_time
            name       data_domain                                                                                                  
            admissions ALICE              None       admissions   admissions  2025-07-28 03:30:04.115331                        None

            # Example 2: List all the archived FeatureGroups in the repo 'vfs_v1'.
            # Let's first archive the FeatureGroup.
            >>> fs.archive_feature_group("admissions")
            True

            # List archived FeatureGroups.
            >>> fs.list_feature_groups(archived=True)
                     name data_domain description data_source_name entity_name               creation_time modified_time               archived_time
            0  admissions       ALICE        None       admissions  admissions  2025-07-28 03:30:04.115331          None  2025-07-28 03:31:04.550000
            >>>
        """
        return self.__get_archived_feature_group_df() if archived else self.__get_feature_group_df()

    def list_data_domains(self) -> DataFrame:
        """
        DESCRIPTION:
            Lists all the data domains.

        PARAMETERS:
            None

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            # Example 1: List all the data domains in the repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1' with data_domain 'd1'.
            >>> fs = FeatureStore("vfs_v1", data_domain='d1')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            # List all the data domains in the repo 'vfs_v1'.
            >>> fs.list_data_domains()
                 name                created_time
            0      d1  2025-04-30 11:21:40.123456
        """
        return self.__get_data_domain_df()

    def list_feature_processes(self, archived=False) -> DataFrame:
        """
        DESCRIPTION:
            Lists all the feature processes.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to retrieve archived feature processes or not.
                When set to True, archived feature processes in FeatureStore are listed.
                Otherwise, all feature processes are listed.
                Default Value: False
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            # Example 1: List all the feature processes in the repo 'vfs_v1'.
            >>> from teradataml import FeatureStore

            # Create FeatureStore 'vfs_v1' or use existing one.
            >>> fs = FeatureStore("vfs_v1")
            FeatureStore is ready to use.

            # Load the sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a feature process.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' started.
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' completed.

            # List all the feature processes in the repo 'vfs_v1'.
            >>> fs.list_feature_processes()
                                                 description data_domain       process_type data_source entity_id       feature_names feature_ids                     valid_start                      valid_end
            process_id
            5747082b-4acb-11f0-a2d7-f020ffe7fe09                   sales  denormalized view     "sales"  accounts  Apr, Feb, Jan, Mar        None  2025-06-16 16:02:55.260000+00:  9999-12-31 23:59:59.999999+00:
        
            # Example 2: List all the archived feature processes in the repo 'vfs_v1'.

            # Let's check the archived feature processes before archiving feature process.
            >>> fs.list_feature_processes(archived=True)
            process_id start_time end_time status filter as_of_start as_of_end failure_reason

            # Archive the feature process by passing the process_id.
            >>> fs.archive_feature_process('5747082b-4acb-11f0-a2d7-f020ffe7fe09')
            Feature 'Feb' is archived from table 'FS_T_6003dc24_375e_7fd6_46f0_eeb868305c4a'.
            Feature 'Feb' is archived from metadata.
            Feature 'Jan' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Jan' is archived from metadata.
            Feature 'Mar' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Mar' is archived from metadata.
            Feature 'Apr' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Apr' is archived from metadata.
            FeatureProcess with process id '5747082b-4acb-11f0-a2d7-f020ffe7fe09' is archived.
            True

            # List all the archived feature processes in the repo 'vfs_v1'.
            >>> fs.list_feature_processes(archived=True)
                                                 description data_domain       process_type data_source entity_id       feature_names feature_ids                     valid_start                      valid_end
            process_id
            5747082b-4acb-11f0-a2d7-f020ffe7fe09                   sales  denormalized view     "sales"  accounts  Apr, Feb, Jan, Mar        None  2025-06-16 16:02:55.260000+00:  2025-06-16 16:04:32.260000+00:

        """
        validate_params = []
        validate_params.append(["archived", archived, True, bool, True])
        # Validate argument types
        _Validators._validate_function_arguments(validate_params)

        f_process_df = self.__get_without_valid_period_df(self.__get_feature_process_df())
        f_process_df = f_process_df[f_process_df.data_domain == self.__data_domain]

        if archived:
            # Filter out the active feature process. Only archived features are returned.
            f_process_df = f_process_df[(Col("valid_end") <= Col('current_timestamp'))]

        return f_process_df

    def list_feature_runs(self):
        """
        DESCRIPTION:
            Lists all the feature runs in the FeatureStore.

        PARAMETERS:
            None

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            # Example 1: List all the feature runs in the repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            
            # Create a FeatureStore 'vfs_v1' or use existing one.
            >>> fs = FeatureStore("vfs_v1")
            FeatureStore is ready to use.

            # Load the sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a feature process.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='test_domain',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Mar', 'Apr'])
            >>> fp.run(filters=[df.accounts=='Alpha Co', "accounts='Jones LLC'"])
            Process '11b62599-692f-11f0-ad19-f020ffe7fe09' started.
            Ingesting the features for filter 'accounts = 'Alpha Co'' to catalog.
            Ingesting the features for filter 'accounts='Jones LLC'' to catalog.
            Process '11b62599-692f-11f0-ad19-f020ffe7fe09' completed.
            True

            # List all the feature runs in the repo 'vfs_v1'.
            >>> fs.list_feature_runs()
                                              process_id  data_domain                  start_time                    end_time     status                                       filter as_of_start as_of_end failure_reason
            run_id                                                                                                                                                                        
            1       11b62599-692f-11f0-ad19-f020ffe7fe09  test_domain  2025-07-25 08:12:13.001968  2025-07-25 08:12:13.001968  completed  accounts = 'Alpha Co', accounts='Jones LLC'        None      None           None
        """
        return self.__get_feature_runs_df()

    def list_dataset_catalogs(self) -> DataFrame:
        """
        DESCRIPTION:
            Lists all the dataset catalogs.

        PARAMETERS:
            None

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            # Example 1: List all the dataset catalogs in the repo 'vfs_v1'.
            >>> from teradataml import FeatureStore

            # Create FeatureStore 'vfs_v1' or use existing one.
            >>> fs = FeatureStore("vfs_v1", data_domain='sales')
            FeatureStore is ready to use.

            # Load the sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a feature process.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' started.
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' completed.

            # create a dataset catalog.
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                 'Jan': '5747082b-4acb-11f0-a2d7-f020ffe7fe09',
            ...                                 'Feb': '5747082b-4acb-11f0-a2d7-f020ffe7fe09'},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List all the dataset catalogs in the repo 'vfs_v1'.
            >>> fs.list_dataset_catalogs()
                                                 data_domain        name entity_name database_name                        description                      valid_start                        valid_end
            id
            4f763a7b-8920-448c-87af-432e7d36c9cb       sales  ds_jan_feb    accounts        vfs_v1  Dataset with Jan and Feb features  2025-06-16 16:15:17.577637+00:  9999-12-31 23:59:59.999999+00:
        """
        return self.__get_without_valid_period_df(self.__get_dataset_catalog_df())

    def get_feature(self, name):
        """
        DESCRIPTION:
            Retrieve the feature.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the feature to get.
                Types: str

        RETURNS:
            Feature.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Create DataFrame on sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017

            # Create a FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create Feature for column 'Mar' with name 'sales_mar'.
            >>> feature = Feature('sales_mar', column=df.Mar)

            # Apply the Feature to FeatureStore.
            >>> fs.apply(feature)
            True

            # Get the feature 'sales_mar' from repo 'vfs_v1'.
            >>> feature = fs.get_feature('sales_mar')
            >>> feature
            Feature(name=sales_mar)
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Check if the feature exists in the current data domain.
        df = self.__get_features_wog_df()
        df = df[(df['name'] == name) &
                (df['data_domain'] == self.__data_domain)]

        # If no records found, check if the feature exists in any domain.
        if df.shape[0] == 0:
            res = _FSUtils._get_data_domains(self.__repo, name, 'feature')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "Feature", "name '{}'".format(name),
                                                 self.__data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "Feature", "name '{}'".format(name), 
                                                 self.__data_domain)
            raise TeradataMlException(error_msg, msg_code)
        
        return Feature._from_df(df)

    def get_group_features(self, group_name):
        """
        DESCRIPTION:
            Get the Features from the given feature group name.

        PARAMETERS:
            group_name:
                Required Argument.
                Specifies the name of the group the feature belongs to.
                Types: str

        RETURNS:
            List of Feature objects.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            
            # Create DataFrame on sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True
            
            # Create FeatureGroup with name 'sales' from DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(
            ...    name="sales", df=df, entity_columns="accounts", timestamp_column="datetime")
            # Apply the FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Get all the features belongs to the group 'sales' from repo 'vfs_v1'.
            >>> features = fs.get_group_features('sales')
            >>> features
            [Feature(name=Jan), Feature(name=Feb), Feature(name=Apr), Feature(name=Mar)]
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["group_name", group_name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Select active features.
        features_df = self.__get_features_df()
        features_df = features_df[((features_df.status != FeatureStatus.INACTIVE.name) & 
                                   (features_df.group_name == group_name) &
                                   (features_df.data_domain == self.__data_domain))]

        # Check if a feature with that group name exists or not. If not, raise error.
        if features_df.shape[0] == 0:
            res = _FSUtils._get_data_domains(self.__repo, group_name, 'group_features')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "Features", "group name '{}'".format(group_name),
                                                 self.__data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "Features", "group name '{}'".format(group_name),
                                                 self.__data_domain)
            raise TeradataMlException(error_msg, msg_code)

        return Feature._from_df(features_df)

    def get_feature_group(self, name):
        """
        DESCRIPTION:
            Retrieve the FeatureGroup using name.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the feature group to be retrieved.
                Types: str

        RETURNS:
            Object of FeatureGroup

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Create DataFrame on sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create FeatureGroup with name 'sales' from DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(
            ...    name="sales", df=df, entity_columns="accounts", timestamp_column="datetime")
            # Apply the FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # Get FeatureGroup with group name 'sales' from repo 'vfs_v1'.
            >>> fg = fs.get_feature_group('sales')
            >>> fg
            FeatureGroup(sales, features=[Feature(name=Jan), Feature(name=Feb), Feature(name=Apr), Feature(name=Mar)], entity=Entity(name=sales), data_source=DataSource(name=sales))
            >>>
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = self.list_feature_groups()
        df = df[(df['name'] == name) &
                (df['data_domain'] == self.__data_domain)]

        # Check if a feature group with that name exists or not. If not, raise error.
        if df.shape[0] == 0:
            res = _FSUtils._get_data_domains(self.__repo, name, 'feature_group')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "FeatureGroup", "name '{}'".format(name),
                                                 self.__data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "FeatureGroup", "name '{}'".format(name),
                                                 self.__data_domain)
            raise TeradataMlException(error_msg, msg_code)

        return FeatureGroup._from_df(df,
                                     self.__repo,
                                     self.__get_features_df(),
                                     self.__get_entity_df(),
                                     self.__get_data_source_df(),
                                     data_domain=self.__data_domain
                                     )

    def get_entity(self, name):
        """
        DESCRIPTION:
            Get the entity from feature store.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the entity.
                Types: str

        RETURNS:
            Object of Entity.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, Entity, FeatureStore, load_example_data
            # Create DataFrame on admissions data.
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create Entity for column 'id' with name 'admissions_id'.
            >>> entity = Entity(name='admissions_id', description="Entity for admissions", columns=df.id)
            # Apply the Entity to FeatureStore 'vfs_v1'.
            >>> fs.apply(entity)
            True

            # Get the Entity 'admissions_id' from repo 'vfs_v1'
            >>> entity = fs.get_entity('admissions_id')
            >>> entity
            Entity(name=admissions_id)
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = self.__get_entity_df()
        df = df[(df['name'] == name) &
                (df['data_domain'] == self.__data_domain)]

        # Check if entity with that name exists or not. If not, raise error.
        if df.shape[0] == 0:
            res = _FSUtils._get_data_domains(self.__repo, name, 'entity')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "Entity", "name '{}'".format(name),
                                                 self.__data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "Entity", "name '{}'".format(name),
                                                 self.__data_domain)
            raise TeradataMlException(error_msg, msg_code)
        
        return Entity._from_df(df)

    def get_data_source(self, name):
        """
        DESCRIPTION:
            Get the data source from feature store.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the data source.
                Types: str

        RETURNS:
            Object of DataSource.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            # Create DataFrame on admissions data.
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create DataSource using DataFrame 'df' with name 'admissions'.
            >>> ds = DataSource('admissions', source=df)
            # Apply the DataSource to FeatureStore 'vfs_v1'.
            >>> fs.apply(ds)
            True

            # Get the DataSource 'admissions' from repo 'vfs_v1'
            >>> ds = fs.get_data_source('admissions')
            >>> ds
            DataSource(name=admissions)
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, (str), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = self.__get_data_source_df()
        df = df[(df['name'] == name) &
                (df['data_domain'] == self.__data_domain)]

        # Check if a data source with that name exists or not. If not, raise error.
        if df.shape[0] == 0:
            res = _FSUtils._get_data_domains(self.__repo, name, 'data_source')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "DataSource", "name '{}'".format(name),
                                                self.__data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "DataSource", "name '{}'".format(name),
                                                 self.__data_domain)
            raise TeradataMlException(error_msg, msg_code)

        return DataSource._from_df(df)
    
    def get_feature_process(self, object, entity=None, features=None, description=None):
        """
        DESCRIPTION:
            Retrieves the FeatureProcess object.

        PARAMETERS:
            object:
                Required Argument.
                Specifies the source to ingest feature values. It can be one of the following:
                    * teradataml DataFrame
                    * Feature group
                    * Process id
                Notes:
                     * If "object" is of type teradataml DataFrame, then "entity"
                       and "features" should be provided.
                     * If "object" is of type str, then it is considered as
                       as process id of an existing FeatureProcess and reruns the
                       process. Entity and features are taken from the existing
                       feature process. Hence, the arguments "entity" and "features"
                       are ignored.
                     * If "object" is of type FeatureGroup, then entity and features
                       are taken from the FeatureGroup. Hence, the arguments "entity"
                       and "features" are ignored.
                Types: DataFrame or FeatureGroup or str

            entity:
                Optional Argument.
                Specifies Entity for DataFrame.
                Notes:
                     * Ignored when "object" is of type FeatureGroup or str.
                     * If a string or list of strings is provided, then "object" should
                       have these columns in it.
                     * If Entity object is provided, then associated columns in Entity
                       object should be present in DataFrame.
                Types: Entity or str or list of str

            features:
                Optional Argument.
                Specifies list of features to be considered in feature process. Feature
                ingestion takes place only for these features.
                Note:
                    * Ignored when "object" is of type FeatureGroup or str.
                Types: Feature or list of Feature or str or list of str.

            description:
                Optional Argument.
                Specifies description for the FeatureProcess.
                Types: str

        RETURNS:
            FeatureProcess

        RAISES:
            None.

        EXAMPLES:
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Load the admissions data to Vantage.
            >>> from teradataml import DataFrame, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            >>> admission_df = DataFrame("admissions_train")

            >>> fp = FeatureProcess(repo='vfs_v1',
            ...                     data_domain='d1',
            ...                     object=admission_df,
            ...                     entity='id',
            ...                     features=['stats', 'programming', 'admitted'])
            >>> fp.run()
            Process '0d365f08-66b0-11f0-88ff-b0dcef8381ea' started.
            Process '0d365f08-66b0-11f0-88ff-b0dcef8381ea' completed.

            >>> fs.get_feature_process(object='0d365f08-66b0-11f0-88ff-b0dcef8381ea')
            FeatureProcess(repo=vfs_v1, data_domain=d1, process_id=0d365f08-66b0-11f0-88ff-b0dcef8381ea)
        """
        return FeatureProcess(repo=self.__repo,
                              data_domain=self.__data_domain,
                              object=object, 
                              entity=entity, 
                              features=features,
                              description=description
                              )

    def get_feature_catalog(self):
        """
        DESCRIPTION:
            Retrieves FeatureCatalog based on the feature store's repo and data domain.

        PARAMETERS:
            None.

        RETURNS:
            FeatureCatalog

        RAISES:
            None.

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore('vfs_v1')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Load the sales data to Vantage.
            from teradataml import load_example_data
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a feature process.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' started.
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' completed.

            # Get FeatureCatalog from FeatureStore.
            >>> fs.get_feature_catalog()
            FeatureCatalog(repo=vfs_v1, data_domain=sales)
        """
        return FeatureCatalog(repo=self.__repo,
                              data_domain=self.__data_domain)

    def get_data_domain(self):
        """
        DESCRIPTION:
            Retrieves DataDomain based on the feature store's repo and data domain.

        PARAMETERS:
            None

        RETURNS:
            DataDomain

        RAISES:
            None.

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore('vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()

            # Get DataDomain from FeatureStore.
            >>> fs.get_data_domain()
            DataDomain(repo=vfs_v1, data_domain=sales)
        """
        return DataDomain(repo=self.__repo,
                          data_domain=self.__data_domain)

    def get_dataset_catalog(self):
        """
        DESCRIPTION:
            Retrieves DatasetCatalog based on the feature store's repo and data domain.

        PARAMETERS:
            None.

        RETURNS:
            DatasetCatalog

        RAISES:
            None.

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore('vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()

            # Load the sales data to Vantage.
            >>> from teradataml import load_example_data
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a feature process.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' started.
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' completed.
            True

            # Build the dataset.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                 'Jan': fp.process_id,
            ...                                 'Feb': fp.process_id},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # Get DatasetCatalog from FeatureStore.
            >>> fs.get_dataset_catalog()
            DatasetCatalog(repo=vfs_v1, data_domain=sales)
        """
        return DatasetCatalog(repo=self.__repo,
                              data_domain=self.__data_domain)

    def set_features_inactive(self, names):
        """
        DESCRIPTION:
            Mark the feature status as 'inactive'. Note that, inactive features are
            not available for any further processing. Set the status as 'active' with
            "set_features_active()" method.

        PARAMETERS:
            names:
                Required Argument.
                Specifies the name(s) of the feature(s).
                Types: str OR list of str

        RETURNS:
            bool

        RAISES:
            teradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            # Create DataFrame on admissions data.
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create FeatureGroup from DataFrame df.
            >>> fg = FeatureGroup.from_DataFrame(name='admissions', df=df, entity_columns='id')
            # Apply the FeatureGroup to FeatureStore 'vfs_v1'.
            >>> fs.apply(fg)
            True

            # Get FeatureGroup 'admissions' from FeatureStore.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=programming), Feature(name=admitted), Feature(name=stats), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))

            # Example 1: Set the Feature 'programming' inactive.
            # Set the Feature 'programming' inactive.
            >>> fs.set_features_inactive('programming')
            True

            # Get FeatureGroup again after setting feature inactive.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=stats), Feature(name=admitted), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))

        """
        return self.__set_active_inactive_features(names, active=False)

    def set_features_active(self, names):
        """
        DESCRIPTION:
            Mark the feature status as active. Set the status as 'inactive' with
            "set_features_inactive()" method. Note that, inactive features are
            not available for any further processing.

        PARAMETERS:
            names:
                Required Argument.
                Specifies the name(s) of the feature(s).
                Types: str OR list of str

        RETURNS:
            bool

        RAISES:
            teradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            # Create DataFrame on admissions data.
            >>> load_example_data("dataframe", "admissions_train")
            >>> df = DataFrame("admissions_train")
            >>> df
               masters   gpa     stats programming  admitted
            id
            34     yes  3.85  Advanced    Beginner         0
            32     yes  3.46  Advanced    Beginner         0
            11      no  3.13  Advanced    Advanced         1
            40     yes  3.95    Novice    Beginner         0
            38     yes  2.65  Advanced    Beginner         1
            36      no  3.00  Advanced      Novice         0
            7      yes  2.33    Novice      Novice         1
            26     yes  3.57  Advanced    Advanced         1
            19     yes  1.98  Advanced    Advanced         0
            13      no  4.00  Advanced      Novice         1

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create FeatureGroup from DataFrame df.
            >>> fg = FeatureGroup.from_DataFrame(name='admissions', df=df, entity_columns='id')
            # Apply the FeatureGroup to FeatureStore 'vfs_v1'.
            >>> fs.apply(fg)
            True

            # Get FeatureGroup 'admissions' from FeatureStore.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=programming), Feature(name=admitted), Feature(name=stats), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))
            
            # Example 1: Set the Feature 'programming' inactive.
            # Set the Feature 'programming' inactive.
            >>> fs.set_features_inactive('programming')
            True

            # Get FeatureGroup again after setting feature inactive.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=stats), Feature(name=admitted), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))

            # Mark Feature 'programming' from 'inactive' to 'active'.
            >>> fs.set_features_active('programming')
            # Get FeatureGroup again after setting feature active.
            >>> fg = fs.get_feature_group('admissions')
            >>> fg
            FeatureGroup(admissions, features=[Feature(name=masters), Feature(name=programming), Feature(name=admitted), Feature(name=stats), Feature(name=gpa)], entity=Entity(name=admissions), data_source=DataSource(name=admissions))
            >>>
        """
        return self.__set_active_inactive_features(names, active=True)

    def __set_active_inactive_features(self, names, active):
        """
        DESCRIPTION:
            Internal function to either active or inactive features.

        PARAMETERS:
            names:
                Required Argument.
                Specifies the name the feature.
                Types: str OR list of str

        RETURNS:
            bool

        RAISES:
            teradataMLException

        EXAMPLES:
            # Example 1: Archive the feature 'feature1' in the repo
            #            'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            >>> fs.__archive_unarchive_features(name='feature1')
            True
            >>>
        """
        names = UtilFuncs._as_list(names)

        argument_validation_params = []
        argument_validation_params.append(["names", names, False, (str, list), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        status = FeatureStatus.ACTIVE.name if active else FeatureStatus.INACTIVE.name

        is_set = True
        if status == FeatureStatus.INACTIVE.name:
            # Get the joined df of '_efs_features' and '_efs_features_metadata'.
            feature_info_df = self.__get_feature_info_df()
            metadata_features = [feature.name for feature in feature_info_df.itertuples()]

            # Form a list of user provided feature names which are
            # present in catalog and not present in catalog.
            catalog_features = []
            non_catalog_features = []
            for name in names:
                if name in metadata_features:
                    catalog_features.append(name)
                else:
                    non_catalog_features.append(name)

            # If user provided all names are present in catalog.
            if len(catalog_features) == len(names):
                print("Feature(s) '{}' entries exists in feature catalog, cannot be set "
                      "to inactive.".format(", ".join(catalog_features)))
                return False
            # If some of the user provided features present in catalog.
            elif len(catalog_features) > 0:
                print("Feature(s) '{}' entries exists in feature catalog, cannot be set "
                      "to inactive.".format(", ".join(catalog_features)))
                is_set = is_set and False

            # Assign feature names list which are not present in catalog.
            names = non_catalog_features

        _update_data(table_name=self.__table_names['feature'],
                     schema_name=self.__repo,
                     update_columns_values={"status": status},
                     update_conditions={"name": names}
                     )

        return is_set

    def apply(self, object):
        """
        DESCRIPTION:
            Register objects to repository.
            Note:
                * If the object is an Entity or FeatureGroup and the same entity or feature group is already 
                  registered in the repository, it is not updated. 
                * If the entity or feature group is associated with any feature process, an error is raised 
                  while modifying these objects.

        PARAMETERS:
            object:
                Required Argument.
                Specifies the object to update the repository.
                Types: Feature OR DataSource OR Entity OR FeatureGroup.

        RETURNS:
            bool.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import FeatureStore, DataFrame, load_example_data
            # Create DataFrame on sales data.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: create a Feature for column 'Feb' from 'sales' DataFrame
            #            and register with repo 'vfs_v1'.
            >>> # Create Feature.
            >>> from teradataml import Feature
            >>> feature = Feature('sales:Feb', df.Feb)
            >>> # Register the above Feature with repo.
            >>> fs.apply(feature)
            True
            >>>

            # Example 2: create Entity for 'sales' DataFrame and register
            #            with repo 'vfs_v1'.
            >>> # Create Entity.
            >>> from teradataml import Entity
            >>> entity = Entity('sales:accounts', df.accounts)
            >>> # Register the above Entity with repo.
            >>> fs.apply(entity)
            True
            >>>

            # Example 3: create DataSource for 'sales' DataFrame and register
            #            with repo 'vfs_v1'.
            >>> # Create DataSource.
            >>> from teradataml import DataSource
            >>> ds = DataSource('Sales_Data', df)
            >>> # Register the above DataSource with repo.
            >>> fs.apply(ds)
            True
            >>>

            # Example 4: create FeatureStore with all the objects
            #            created in above examples and register with
            #            repo 'vfs_v1'.
            >>> # Create FeatureGroup.
            >>> from teradataml import FeatureGroup
            >>> fg = FeatureGroup('Sales',
            ...                   features=feature,
            ...                   entity=entity,
            ...                   data_source=data_source)
            >>> # Register the above FeatureStore with repo.
            >>> fs.apply(fg)
            True
        """
        argument_validation_params = []
        argument_validation_params.append(["name", object, False, (Feature, Entity, DataSource, FeatureGroup)])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        return object.publish(self.__repo, self.__data_domain)

    def get_data(self, process_id=None, entity=None, features=None,
                 dataset_name=None, as_of=None, include_historic_records=False):
        """
        DESCRIPTION:
            Returns teradataml DataFrame which has entities and feature values.
            Method generates dataset from following -
            * process_id
            * entity and features
            * dataset_name

        PARAMETERS:
            process_id:
                Optional Argument.
                Either "process_id", "entity" and "features", "dataset_name" is mandatory.
                Specifies the process id of an existing feature process.
                Types: str

            entity:
                Optional Argument.
                Specifies the name of the Entity or Object of Entity
                to be considered in the dataset.
                Types: str or Entity.

            features:
                Optional Argument.
                Specifies the names of Features and the corresponding feature version
                to be included in the dataset.
                Notes:
                     * Key is the name of the feature and value is the version of the
                       feature.
                     * Look at FeatureCatalog.list_feature_versions() to get the list of
                       features and their versions.
                Types: dict

            dataset_name:
                Optional Argument.
                Specifies the dataset name.
                Types: str

            as_of:
                Optional Argument.
                Specifies the time to retrieve the Feature Values instead of
                retrieving the latest values.
                Notes:
                    * Applicable only when "process_id" is passed to the function.
                    * Ignored when "dataset_name" is passed.
                Types: str or datetime.datetime

            include_historic_records:
                Optional Argument.
                Specifies whether to include historic data in the dataset.
                Note:
                    * If "as_of" is specified, then the "include_historic_records" argument is ignored.
                Default Value: False.
                Types: bool.


        RETURNS:
            teradataml DataFrame.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureStore, load_example_data
            # Create DataFrame on sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017

            >>> repo = 'vfs_v1'
            >>> data_domain = 'sales'
            >>> fs = FeatureStore(repo=repo, data_domain=data_domain)
            FeatureStore is ready to use.

            # Example 1: Get the data from process_id.
            >>> fp = FeatureProcess(repo=repo,
            ...                     data_domain=data_domain,
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb'])
            >>> fp.run()
            Process '1e9e8d64-6851-11f0-99c5-a30631e77953' started.
            Process '1e9e8d64-6851-11f0-99c5-a30631e77953' completed.
            True

            >>> fs.get_data(process_id=fp.process_id)
                 accounts    Feb    Jan
            0    Alpha Co  210.0  200.0
            1    Blue Inc   90.0   50.0
            2   Jones LLC  200.0  150.0
            3  Orange Inc  210.0    NaN
            4  Yellow Inc   90.0    NaN
            5     Red Inc  200.0  150.0

            # Example 2: Get the data from entity and features.
            >>> fs.get_data(entity='accounts', features={'Jan': fp.process_id})
                 accounts    Jan
            0    Alpha Co  200.0
            1    Blue Inc   50.0
            2   Jones LLC  150.0
            3  Orange Inc    NaN
            4  Yellow Inc    NaN
            5     Red Inc  150.0

            # Example 3: Get the data from dataset name.
            >>> dc = DatasetCatalog(repo=repo, data_domain=data_domain)
            >>> dc.build_dataset(entity='accounts',
            ...                  selected_features={'Jan': fp.process_id,
            ...                                     'Feb': fp.process_id},
            ...                  view_name='test_get_data',
            ...                  description='Dataset with Jan and Feb')
            >>> fs.get_data(dataset_name='test_get_data')
                 accounts    Feb    Jan
            0    Alpha Co  210.0  200.0
            1    Blue Inc   90.0   50.0
            2   Jones LLC  200.0  150.0
            3  Orange Inc  210.0    NaN
            4  Yellow Inc   90.0    NaN
            5     Red Inc  200.0  150.0


            # Example 4: Get the data from Entity and Features, where entity
            #            object and feature objects passed to the entity and
            #            features arguments.
            >>> # Create features.
            >>> feature1 = Feature('sales:Mar',
            ...                    df.Mar,
            ...                    feature_type=FeatureType.CATEGORICAL)

            >>> feature2 = Feature('sales:Apr',
            ...                    df.Apr,
            ...                    feature_type=FeatureType.CONTINUOUS)

            >>> # Create entity.
            >>> entity = Entity(name='accounts_entity', columns=['accounts'])

            >>> fp1 = FeatureProcess(repo=repo,
            ...                      data_domain=data_domain,
            ...                      object=df,
            ...                      entity=entity,
            ...                      features=[feature1, feature2])
            >>> fp1.run()
            Process '5522c034-684d-11f0-99c5-a30631e77953' started.
            Process '5522c034-684d-11f0-99c5-a30631e77953' completed.
            True

            >>> fs.get_data(entity=entity, features={feature1.name: fp1.process_id,
            ...                                      feature2.name: fp1.process_id})
                 accounts  sales:Mar  sales:Apr
            0    Alpha Co      215.0      250.0
            1    Blue Inc       95.0      101.0
            2   Jones LLC      140.0      180.0
            3  Orange Inc        NaN      250.0
            4  Yellow Inc        NaN        NaN
            5     Red Inc      140.0        NaN

            # Example 5: Get the data for the time passed by the user via the as_of argument.
            >>> import time
            >>> from datetime import datetime as dt, date as d

            # Retrieve the record where accounts == 'Blue Inc'.
            >>> df_test = df[df['accounts'] == 'Blue Inc']
            >>> df_test
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017

            # Example updates the data. Hence, creating a new table to avoid modifying the existing tables data.
            >>> df_test.to_sql('sales_test', if_exists='replace')
            >>> test_df = DataFrame('sales_test')
            >>> test_df
               accounts   Feb  Jan  Mar  Apr  datetime
            0  Blue Inc  90.0   50   95  101  17/01/04

            >>> # Create a feature process.
            >>> fp = FeatureProcess(repo=repo,
            ...                     data_domain=data_domain,
            ...                     object=test_df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb'])

            >>> # Run the feature process
            >>> fp.run()
            Process '6cb49b4b-79d4-11f0-8c5e-b0dcef8381ea' started.
            Process '6cb49b4b-79d4-11f0-8c5e-b0dcef8381ea' completed.
            True

            >>> # Running the same process more than once to demonstrate how user can
            >>> # retrieve specific version of Features using argument 'as_of'.
            >>> # Wait for 20 seconds. Then update the data. Then run again.
            >>> time.sleep(20)
            >>> execute_sql("update sales_test set Jan = Jan * 10, Feb = Feb * 10")
            TeradataCursor uRowsHandle=269 bClosed=False

            >>> # Run the feature process again.
            >>> fp.run()
            Process '6cb49b4b-79d4-11f0-8c5e-b0dcef8381ea' started.
            Process '6cb49b4b-79d4-11f0-8c5e-b0dcef8381ea' completed.
            True

            >>> # Then again wait for 20 seconds. Then update the data. Then run again.
            >>> time.sleep(20)
            >>> execute_sql("update sales_test set Jan = Jan * 10, Feb = Feb * 10")
            TeradataCursor uRowsHandle=397 bClosed=False

            >>> # Run the feature process again.
            >>> fp.run()
            Process '6cb49b4b-79d4-11f0-8c5e-b0dcef8381ea' started.
            Process '6cb49b4b-79d4-11f0-8c5e-b0dcef8381ea' completed.
            True

            # Retrieve specific version of Features at '2025-08-15 12:37:23'
            >>> as_of_time = dt(2025, 8, 15, 12, 37, 23)

            >>> # time passed to as_of in datetime.datetime format.
            >>> fs.get_data(process_id=fp.process_id,
            ...             as_of=as_of_time)
               accounts    Feb  Jan
            0  Blue Inc  900.0  500

            >>> # time passed to as_of in string format.
            >>> fs.get_data(process_id=fp.process_id,
            ...             as_of=as_of_time.strftime('%Y-%m-%d %H:%M:%S'))
               accounts    Feb  Jan
            0  Blue Inc  900.0  500

            # Example 6: Get the data for the time passed by the user via the as_of argument
            #            by sourcing entity and features.
            >>> # time passed to as_of in datetime.datetime format.
            >>> fs.get_data(entity='accounts',
            ...             features={'Feb': fp.process_id,
            ...                       'Jan': fp.process_id},
            ...             as_of=as_of_time)
               accounts    Feb  Jan
            0  Blue Inc  900.0  500

            >>> # time passed to as_of in string format.
            >>> fs.get_data(entity='accounts',
            ...             features={'Feb': fp.process_id,
            ...                       'Jan': fp.process_id},
            ...             as_of=as_of_time.strftime('%Y-%m-%d %H:%M:%S'))
               accounts    Feb  Jan
            0  Blue Inc  900.0  500

            # Example 7: Get the latest data for the given process_id.
            >>> fs.get_data(process_id=fp.process_id, include_historic_records=False)
               accounts     Feb   Jan
            0  Blue Inc  9000.0  5000

            # Example 8: Get the historic data for the given process_id.
            >>> fs.get_data(process_id=fp.process_id, include_historic_records=True)
               accounts     Feb   Jan
            0  Blue Inc  9000.0  5000
            1  Blue Inc    90.0    50
            2  Blue Inc    90.0  5000
            3  Blue Inc   900.0   500
            4  Blue Inc   900.0  5000
            5  Blue Inc   900.0    50
            6  Blue Inc    90.0   500
            7  Blue Inc  9000.0    50
            8  Blue Inc  9000.0   500

            # Example 9: Get the latest data for the given feature.
            >>> fs.get_data(entity='accounts', features={'Feb': fp.process_id}, include_historic_records=False)
               accounts     Feb
            0  Blue Inc  9000.0

            # Example 10: Get the historic data for the given feature.
            >>> fs.get_data(entity='accounts', features={'Feb': fp.process_id}, include_historic_records=True)
               accounts     Feb
            0  Blue Inc   900.0
            1  Blue Inc    90.0
            2  Blue Inc  9000.0

        """
        # Validate argument types
        args = []
        args.append(["process_id", process_id, True, (str), True])
        args.append(["entity", entity, True, (Entity, str), True])
        args.append(["features", features, True, (dict), True])
        args.append(["dataset_name", dataset_name, True, (str), True])
        args.append(["as_of", as_of, True, (str, dt), True])
        args.append(["include_historic_records", include_historic_records, True, (bool)])

        _Validators._validate_function_arguments(args)

        # Validate mutually exclusive arguments.
        _Validators._validate_mutually_exclusive_argument_groups({"process_id": process_id},
                                                                 {"dataset_name": dataset_name},
                                                                 {"entity": entity, "features": features})

        # Validate whether entity and features are mutually inclusive.
        _Validators._validate_mutually_inclusive_arguments(entity, "entity",
                                                           features, "features")

        # Validate at least one argument is passed.
        _Validators._validate_any_argument_passed({"process_id": process_id,
                                                   "entity' and 'features": entity,
                                                   "dataset_name": dataset_name})

        # If user pass view, return DataFrame directly.
        if dataset_name:
            return DataFrame(in_schema(self.__repo, dataset_name))

        if process_id:
            entity, features = (
                self.__get_entity_and_features_from_process_id(process_id))

        # Genarate the view name.
        view_name = UtilFuncs._generate_temp_table_name(databasename=self.__repo)

        # When as_of is not None, get all the data instead of only latest.
        if as_of:
            include_historic_records = True

        # Create the DatasetCatalog and build dataset on top of it.
        dc = DatasetCatalog(repo=self.__repo, data_domain=self.__data_domain)
        dataset = dc._build_dataset(
            entity, features,
            include_historic_records=include_historic_records,
            include_time_series=True if as_of else False,
            view_name=view_name,
            temporary=True)

        if as_of:
            return self.__filter_dataset_by_as_of(dataset, entity, list(features.keys()), as_of)
        return dataset

    def __get_entity_and_features_from_process_id(self, process_id):
        """
        DESCRIPTION:
            Internal function to get entity_columns, feature_columns, and s
            elected_features using process_id.

        PARAMETERS:
              process_id:
                Required Argument.
                Specifies the process id of FeatureProcess.
                Types: str

        RETURNS:
              entity_id, selected_features

        RAISES:
            None

        EXAMPLES:
            >>> fs.__get_entity_and_features_from_process_id('123-acd')
        """
        feature_ver = self.__get_feature_version()
        feature_ver = feature_ver[feature_ver["feature_version"] == process_id]

        # Check if a feature with that process id exists or not. If not, raise error.
        if feature_ver.shape[0] == 0:
            res = _FSUtils._get_data_domains(self.__repo, process_id, 'feature_version')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "Feature", "process id '{}'".format(process_id),
                                                 self.__data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "Feature", "process id '{}'".format(process_id),
                                                 self.__data_domain)
            raise TeradataMlException(error_msg, msg_code)

        selected_features = {}
        for f_ver in feature_ver.itertuples():
            entity_id = f_ver.entity_id
            selected_features[f_ver.feature_name] = process_id
        return entity_id, selected_features

    def __filter_dataset_by_as_of(self, dataset, entity_column, features_column_list, as_of):
        """
        DESCRIPTION:
            Internal function to filter the dataset using as_of and
            return only required columns.

        PARAMETERS:
            dataset:
                Required Argument.
                Specifies the teradataml DataFrame.
                Types: teradataml DataFrame

            entity_column:
                Required Argument.
                Specifies the column name of entity.
                Types: str

            features_column_list:
                Required Argument.
                Specifies the list of feature columns list.
                Types: list of str

            as_of:
                Required Argument.
                Specifies the time to retrieve the Feature Values instead of
                retrieving the latest values.
                Notes:
                    * Applicable only when "process_id" is passed to the function.
                    * Ignored when "dataset_name" is passed.
                Types: str or datetime.datetime

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> load_examples_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> fs.__filter_dataset_by_as_of(df, "accounts", ["Jan", "Feb"], datetime.datetime(2025, 1, 1))

        """
        conditions = [
            (dataset[f"{f}_start_time"] <= as_of) & (as_of <= dataset[f"{f}_end_time"])
            for f in features_column_list
        ]
        combined_condition = reduce(operator.and_, conditions)
        required_columns = UtilFuncs._as_list(entity_column) + features_column_list
        return dataset[combined_condition].select(required_columns)

    def __get_feature_group_names(self, name, type_):
        """
        DESCRIPTION:
            Internal function to get the associated group names for
            Feature or DataSource OR Entity.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the Feature or DataSource or Entity.
                Types: str

            type_:
                 Required Argument.
                 Specifies the type of the objects stored in feature store.
                 Permitted Values:
                    * feature
                    * data_source
                    * entity
                 Types: str

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            >>> self.__get_feature_group_names('admissions', 'data_source')
        """
        if type_ == "feature":
            df = self.__get_features_df()
            return [rec.group_name for rec in df[df.name == name].itertuples() if rec.group_name is not None]
        elif type_ == "data_source":
            df = self.__get_feature_group_df()
            return [rec.name for rec in df[df.data_source_name == name].itertuples()]
        elif type_ == "entity":
            df = self.__get_feature_group_df()
            return [rec.name for rec in df[df.entity_name == name].itertuples()]

    def __remove_obj(self, name, type_, action="archive"):
        """
        DESCRIPTION:
            Internal function to get the remove Feature or DataSource OR
            Entity from repo.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the Feature or DataSource or Entity.
                Types: str

            type_:
                 Required Argument.
                 Specifies the type of "name".
                 Types: str
                 Permitted Values:
                    * feature
                    * data_source
                    * entity

            action:
                 Optional Argument.
                 Specifies whether to remove from staging tables or not.
                 When set to True, object is removed from staging tables.
                 Otherwise, object is fetched from regular tables.
                 Default Value: True
                 Types: bool

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> self.__remove_obj('admissions', 'data_source')
        """
        _vars = {
            "data_source": {"class": DataSource, "error_msg": "Update these FeatureGroups with other DataSources"},
            "entity": {"class": Entity, "error_msg": "Update these FeatureGroups with other Entities"},
            "feature": {"class": Feature, "error_msg": "Remove the Feature from FeatureGroup"},
        }
        c_name_ = _vars[type_]["class"].__name__
        argument_validation_params = []
        argument_validation_params.append([type_, name, False, (str, _vars[type_]["class"]), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        # Extract the name if argument is class type.
        if isinstance(name, _vars[type_]["class"]):
            name = name.name

        # Get the feature info DataFrame.
        feature_info_df = self.__get_feature_info_df()

        # Before removing it, check if it is associated with any FeatureGroup.
        # If yes, raise error. Applicable only for Archive.
        if action == "archive":
            feature_groups = self.__get_feature_group_names(name, type_)
            if feature_groups:
                feature_groups = ", ".join(("'{}'".format(fg) for fg in feature_groups))
                message = ("{} '{}' is associated with FeatureGroups {}. {} and try deleting again.".format(
                    c_name_, name, feature_groups, _vars[type_]["error_msg"]))
                raise TeradataMlException(Messages.get_message(
                    MessageCodes.FUNC_EXECUTION_FAILED, '{}_{}'.format(action, type_), message),
                    MessageCodes.FUNC_EXECUTION_FAILED)
            # Check if the feature or entity exists in Feature metadata table.
            # If yes, then raise error. Applicable only for Archive.
            info_checks = {
            'feature': ('name', MessageCodes.EFS_FEATURE_IN_CATALOG),
            'entity': ('entity_name', MessageCodes.EFS_ENTITY_IN_CATALOG)
            }
            if type_ in info_checks:
                col, error_code = info_checks[type_]
                validate_df = feature_info_df[feature_info_df[col].isin([name])]
                if validate_df.shape[0] > 0:        
                    if type_ == "entity":
                        related_features = [feature.name for feature in validate_df.itertuples()]
                        features = ", ".join(("'{}'".format(f) for f in related_features))
                        err_msg = Messages.get_message(error_code,
                                                       name,
                                                       features)
                    else:
                        err_msg = Messages.get_message(error_code,
                                                       name)
                    raise TeradataMlException(err_msg, error_code)

            stg_table = _FeatureStoreDFContainer.get_df("{}_staging".format(type_), self.__repo, self.__data_domain)
            stg_table = stg_table[stg_table.name == name]
            if stg_table.shape[0] > 0:
                print("{} '{}' is already archived.".format(c_name_, name))
                return False

        # Validation for delete action - ensure object is already archived
        if action == "delete":
            # Check if object exists in main table (not archived)
            main_table_name = self.__table_names[type_]
            main_df = _FeatureStoreDFContainer.get_df(type_, self.__repo, self.__data_domain)
            existing_records = main_df[(main_df["name"] == name)]
            
            if existing_records.shape[0] > 0:
                error_code = MessageCodes.EFS_DELETE_BEFORE_ARCHIVE
                error_msg = Messages.get_message(error_code,
                                                 c_name_,
                                                 name,
                                                 type_)
                raise TeradataMlException(error_msg, error_code)

        if type_ == "entity":
            res = self._remove_entity(name, action)
        else:
            table_name = self.__table_names[type_]
            if action == "delete":
                table_name = self.__table_names["{}_staging".format(type_)]

            res = _delete_data(table_name=table_name,
                               schema_name=self.__repo,
                               delete_conditions=(Col("name") == name) &
                                                 (Col("data_domain") == self.__data_domain)
                               )

        if res == 1:
            print("{} '{}' is {}d.".format(c_name_, name, action))
            return True
        else:
            print("{} '{}' does not exist to {}.".format(c_name_, name, action))
            return False

    @db_transaction
    def _remove_entity(self, name, action):
        """
        DESCRIPTION:
            Internal function to get the remove Entity from repo.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the Entity.
                Types: str

            action:
                 Required Argument.
                 Specifies whether to remove from staging tables or not.
                 When set to "delete", Entity is removed from staging tables.
                 Otherwise, Entity is removed from regular tables.
                 Types: str

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> self._remove_entity('admissions', 'delete')
        """
        ent_table = self.__table_names["entity"]
        ent_table_xref = self.__table_names["entity_xref"]
        if action == "delete":
            ent_table = self.__table_names["entity_staging"]
            ent_table_xref = self.__table_names["entity_staging_xref"]

        # remove it from xref table first.
        _delete_data(table_name=ent_table_xref,
                     schema_name=self.__repo,
                     delete_conditions=(Col("entity_name") == name) &
                                       (Col("data_domain") == self.__data_domain)
                     )

        # remove from entity table.
        res = _delete_data(table_name=ent_table,
                           schema_name=self.__repo,
                           delete_conditions=(Col("name") == name) &
                                             (Col("data_domain") == self.__data_domain)
                           )

        return res

    def archive_data_source(self, data_source):
        """
        DESCRIPTION:
            Archives DataSource from repository. Note that archived DataSource
            is not available for any further processing. Archived DataSource can be 
            viewed using "list_data_sources(archived=True)" method.

        PARAMETERS:
            data_source:
                Required Argument.
                Specifies either the name of DataSource or Object of DataSource
                to archive from repository.
                Types: str OR DataSource

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore
            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Archive the DataSource 'sales_data' in the repo 'vfs_v1' using DataSource object.
            # Create a DataSource using SELECT statement.
            >>> ds = DataSource(name="sales_data", source="select * from sales")
            # Apply DataSource to FeatureStore.
            >>> fs.apply(ds)
            True

            # List the available DataSources.
            >>> fs.list_data_sources()
                                   description timestamp_column               source               creation_time modified_time
            name       data_domain                                                                                            
            sales_data ALICE              None             None  select * from sales  2025-07-28 04:24:48.117827          None

            # Archive DataSource with name "sales_data".
            >>> fs.archive_data_source("sales_data")
            DataSource 'sales_data' is archived.
            True

            # List the available DataSources after archive.
            >>> fs.list_data_sources(archived=True)
                     name data_domain description timestamp_column               source               creation_time modified_time               archived_time
            0  sales_data       ALICE        None             None  select * from sales  2025-07-28 04:24:48.117827          None  2025-07-28 04:25:55.430000

            # Example 2: Archive the DataSource 'sales_data' in the repo 'vfs_v1' using DataSource name.
            # Create a DataSource using teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")
            >>> ds2 = DataSource(name="sales_data_df", source=df)

            # Apply DataSource to FeatureStore.
            >>> fs.apply(ds2)
            True

            # Archive DataSource with name "sales_data_df".
            >>> fs.archive_data_source("sales_data_df")
            DataSource 'sales_data_df' is archived.
            True

            # List the available DataSources after archive.
            >>> fs.list_data_sources(archived=True)
            name data_domain description timestamp_column               source               creation_time modified_time               archived_time
            0  sales_data       ALICE        None             None  select * from sales  2025-07-28 04:24:48.117827          None  2025-07-28 04:25:55.430000
            1  sales_data_df    ALICE        None             None  select * from sales  2025-07-28 04:26:10.123456          None  2025-07-28 04:26:45.456789


        """
        return self.__remove_obj(name=data_source, type_="data_source")

    def delete_data_source(self, data_source):
        """
        DESCRIPTION:
            Removes the archived DataSource from repository.

        PARAMETERS:
            data_source:
                Required Argument.
                Specifies either the name of DataSource or Object of DataSource
                to remove from repository.
                Types: str OR DataSource

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, DataSource, FeatureStore, load_example_data
            # Create teradataml DataFrame.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Create DataSource with source as teradataml DataFrame.
            >>> ds = DataSource(name="sales_data", source=df)
            # Apply the DataSource to FeatureStore.
            >>> fs.apply(ds)
            True

            # Let's first archive the DataSource.
            >>> fs.archive_data_source("sales_data")
            DataSource 'sales_data' is archived.
            True

            # Delete DataSource with name "sales_data".
            >>> fs.delete_data_source("sales_data")
            DataSource 'sales_data' is deleted.
            True

            # List the available DataSources after delete.
            >>> fs.list_data_sources()
            Empty DataFrame
            Columns: [description, timestamp_column, source, creation_time, modified_time]
            Index: []
        """
        return self.__remove_obj(name=data_source, type_="data_source", action="delete")

    def archive_feature(self, feature):
        """
        DESCRIPTION:
            Archives Feature from repository. Note that archived Feature
            is not available for any further processing. Archived Feature can be
            viewed using "list_features(archived=True)" method.

        PARAMETERS:
            feature:
                Required Argument.
                Specifies either the name of Feature or Object of Feature
                to archive from repository.
                Types: str OR Feature

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Feature, FeatureStore
            # Create teradataml DataFrame.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            Example 1: Archive the Feature 'sales_data_Feb' in the repo 'vfs_v1' using Feature object.
            # Create Feature for Column 'Feb'.
            >>> feature = Feature(name="sales_data_Feb", column=df.Feb)
            # Apply the Feature to FeatureStore.
            >>> fs.apply(feature)
            True

            # List the available Features.
            >>> fs.list_features()
                                        id column_name description  tags data_type feature_type  status               creation_time modified_time group_name
            name           data_domain                                                                                                                      
            sales_data_Feb ALICE         1         Feb        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 04:41:01.641026          None       None

            # Archive Feature with name "sales_data_Feb".
            >>> fs.archive_feature(feature=feature)
            Feature 'sales_data_Feb' is archived.
            True

            # List the available archived Features.
            >>> fs.list_features(archived=True)
               id            name data_domain column_name description  tags data_type feature_type  status               creation_time modified_time               archived_time group_name
            0   1  sales_data_Feb       ALICE         Feb        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 04:41:01.641026          None  2025-07-28 04:41:35.600000       None

            # Example 2: Archive the Feature 'sales_data_Feb' in the repo 'vfs_v1' using feature name.
            # Create Feature for Column 'Jan'.
            >>> feature2 = Feature(name="sales_data_Jan", column=df.Jan)
            # Apply the Feature to FeatureStore.
            >>> fs.apply(feature2)
            True

            # Archive Feature with name "sales_data_Jan".
            >>> fs.archive_feature(feature="sales_data_Jan")
            Feature 'sales_data_Jan' is archived.
            True

            # List the available archived Features.
            >>> fs.list_features(archived=True)
               id            name data_domain column_name description  tags data_type feature_type  status               creation_time modified_time               archived_time group_name
            0   1  sales_data_Feb       ALICE         Feb        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 04:41:01.641026          None  2025-07-28 04:41:35.600000       None
            1   2  sales_data_Jan       ALICE         Jan        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 04:42:01.641026          None  2025-07-28 04:43:35.600000       None

        """
        return self.__remove_obj(name=feature, type_="feature")

    def delete(self, force=False):
        """
        DESCRIPTION:
            Removes the FeatureStore and its components from repository.
            Notes:
                 * The function removes all the associated database objects along with data.
                   Be cautious while using this function.
                 * The function tries to remove the underlying Database also once
                   all the Feature Store objects are removed.
                 * The user must have permission on the database used by this Feature Store
                    * to drop triggers.
                    * to drop the tables.
                    * to drop the Database.
                 * If the user lacks any of the mentioned permissions, Teradata recommends
                   to not use this function.

        PARAMETERS:
            force:
                Optional Argument.
                Specifies whether to forcefully delete feature store or not.
                When set to True, delete() method proceeds to drop objects
                even if previous step is errored. Otherwise, delete() method
                raises the exception at the first error and do not proceed to
                remove other objects.
                Defaults: False
                Types: bool

        RETURNS:
            bool.

        RAISES:
            None

        EXAMPLES:
            # Setup FeatureStore for repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.

            # Setup FeatureStore.
            >>> fs.setup()
            True

            # Delete the FeatureStore and all its components.
            >>> fs.delete()
            The function removes Feature Store and drops the corresponding repo also. Are you sure you want to proceed? (Y/N): Y
            True

            # Forcefully delete the FeatureStore and all its components.
            >>> fs.delete(force=True)
            The function removes Feature Store and drops the corresponding repo also. Are you sure you want to proceed? (Y/N): Y
            True
        """
        _args = []
        _args.append(["force", force, True, (bool)])
        # Validate argument types
        _Validators._validate_function_arguments(_args)

        confirmation = input("The function removes Feature Store and drops the "
                             "corresponding repo also. Are you sure you want to proceed? (Y/N): ")

        if confirmation in ["Y", "y"]:
            return self.__drop_feature_store_objects(force=force)

        return False

    def __drop_feature_store_objects(self, force=False):
        """
        DESCRIPTION:
            Removes the FeatureStore and it's components from repository.

        PARAMETERS:
            repo_name:
                Required Argument.
                Specifies the name of the repository.
                Types: str

            force:
                Optional Argument.
                Specifies whether to forcefully delete feature store or not.
                When set to True, delete() method proceeds to drop objects
                even if previous step is errored. Otherwise, delete() method
                raises the exception at the first error and do not proceed to
                remove other objects.
                Defaults: False.
                Types: bool

        RETURNS:
            bool
        """
        # Drop all the tables and staging tables.
        tables_ = [
            self.__table_names["group_features"],
            self.__table_names["feature_group"],
            self.__table_names['feature'],
            self.__table_names['entity_xref'],
            self.__table_names['entity'],
            self.__table_names['data_source'],
            self.__table_names['feature_process'],
            self.__table_names['feature_runs'],
            self.__table_names['feature_metadata'],
            self.__table_names['dataset_catalog'],
            self.__table_names['dataset_features'],
            self.__table_names['data_domain'],
            self.__table_names['version']
        ]

        tables_stg_ = [
            self.__table_names['feature_staging'],
            self.__table_names["entity_staging"],
            self.__table_names["entity_staging_xref"],
            self.__table_names["data_source_staging"],
            self.__table_names["feature_group_staging"],
            self.__table_names["group_features_staging"]
        ]

        # Drop all the triggers first. So that tables can be dropped.
        ignr_errors = 'all' if force else None
        for trigger in EFS_TRIGGERS.values():
            execute_sql("drop trigger {}.{}".format(self.__repo, trigger),
                        ignore_errors=ignr_errors)

        # Drop the views first.
        views_ = [EFS_DB_COMPONENTS['feature_version']]
        for view in views_:
            db_drop_view(view, schema_name=self.__repo, suppress_error=force)

        # Drop datesets.
        # Used EFS_DB_COMPONENTS['dataset_catalog'] because it contains all the datasets.
        # The get_df methods are filtered by data_domain, hence they don't show all datasets.
        for dataset in DataFrame(in_schema(self.__repo, EFS_DB_COMPONENTS['dataset_catalog'])).itertuples():
            db_drop_view(dataset.name, schema_name=self.__repo, suppress_error=force)

        # Drop all the Feature tables.
        dropped_tab = set()
        # Used EFS_DB_COMPONENTS['feature_metadata'] because it contains all the features.
        # The get_df methods are filtered by data_domain, hence they don't show all features.
        for rec in DataFrame(in_schema(self.__repo, EFS_DB_COMPONENTS['feature_metadata'])).itertuples():
            # Avoid dropping the same table again.
            dropped_tab.add(rec.table_name)

        for table in dropped_tab:
            db_drop_table(table, schema_name=self.__repo, suppress_error=force)

        for table in (tables_ + tables_stg_):
            db_drop_table(table, schema_name=self.__repo, suppress_error=force)

        execute_sql(f"DROP DATABASE {self.__repo}")

        return True

    def delete_feature(self, feature):
        """
        DESCRIPTION:
            Removes the archived Feature from repository.

        PARAMETERS:
            feature:
                Required Argument.
                Specifies either the name of Feature or Object of Feature
                to remove from repository.
                Types: str OR Feature

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Feature, FeatureStore
            # Create teradataml DataFrame.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Delete the Feature 'sales_data_Feb' in the repo 'vfs_v1' using Feature object.
            # Create Feature for Column 'Feb'.
            >>> feature = Feature(name="sales_data_Feb", column=df.Feb)
            # Add the feature created above in the feature store.
            >>> fs.apply(feature)
            True

            # List the available Features.
            >>> fs.list_features()
                                        id column_name description  tags data_type feature_type  status               creation_time modified_time group_name
            name           data_domain                                                                                                                      
            sales_data_Feb ALICE         1         Feb        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 04:49:55.827391          None       None

            # Let's first archive the Feature.
            >>> fs.archive_feature(feature=feature)
            Feature 'sales_data_Feb' is archived.
            True

            # Delete Feature with name "sales_data_Feb".
            >>> fs.delete_feature(feature=feature)
            Feature 'sales_data_Feb' is deleted.
            True

            # List the available Features after delete.
            >>> fs.list_features()
            Empty DataFrame
            Columns: [id, column_name, description, tags, data_type, feature_type, status, creation_time, modified_time, group_name]
            Index: []

            Example 2: Delete the Feature 'sales_data_Feb' in the repo 'vfs_v1' using feature name.
            # Create Feature for Column 'Jan'.
            >>> feature2 = Feature(name="sales_data_Jan", column=df.Jan)
            # Add the feature created above in the feature store.
            >>> fs.apply(feature2)
            True

            # List the available Features.
            >>> fs.list_features()
                                        id column_name description  tags data_type feature_type  status               creation_time modified_time group_name
            name           data_domain
            sales_data_Jan ALICE         2         Jan        None  None     FLOAT   CONTINUOUS  ACTIVE  2025-07-28 04:50:55.827391          None       None

            # Let's first archive the Feature using feature name.
            >>> fs.archive_feature(feature="sales_data_Jan")
            Feature 'sales_data_Jan' is archived.
            True

            # Delete Feature with name "sales_data_Jan".
            >>> fs.delete_feature(feature="sales_data_Jan")
            Feature 'sales_data_Jan' is deleted.
            True
        """
        return self.__remove_obj(name=feature, type_="feature", action="delete")

    def archive_entity(self, entity):
        """
        DESCRIPTION:
            Archives Entity from repository. Note that archived Entity
            is not available for any further processing. Archived Entity can be
            viewed using "list_entities(archived=True)" method.

        PARAMETERS:
            entity:
                Required Argument.
                Specifies either the name of Entity or Object of Entity
                to remove from repository.
                Types: str OR Entity

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Entity, FeatureStore
            # Create teradataml DataFrame.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Archive the Entity 'sales_data' in the repo 'vfs_v1' using Entity name.
            # Create Entity using teradataml DataFrame Column.
            >>> entity = Entity(name="sales_data", columns=df.accounts)
            # Apply the entity to FeatureStore.
            >>> fs.apply(entity)
            True

            # List all the available entities.
            >>> fs.list_entities()
                                   description               creation_time modified_time entity_column
            name       data_domain                                                                    
            sales_data ALICE              None  2025-07-28 04:54:34.687139          None      accounts

            # Archive Entity with name "sales_data".
            >>> fs.archive_entity(entity=entity.name)
            Entity 'sales_data' is archived.
            True

            # List the entities after archive.
            >>> fs.list_entities(archived=True)
                     name data_domain description               creation_time modified_time               archived_time entity_column
            0  sales_data       ALICE        None  2025-07-28 04:54:34.687139          None  2025-07-28 04:55:46.750000      accounts

            # Example 2: Archive the Entity 'sales_data' in the repo 'vfs_v1' using Entity object.
            # Create Entity using teradataml DataFrame Column.
            >>> entity2 = Entity(name="sales_data_df", columns=df.accounts)
            # Apply the entity to FeatureStore.
            >>> fs.apply(entity2)
            True

            # Archive Entity with Entity object.
            >>> fs.archive_entity(entity=entity2)
            Entity 'sales_data_df' is archived.
            True

            # List the entities after archive.
            >>> fs.list_entities(archived=True)
                     name data_domain description               creation_time modified_time               archived_time entity_column
            0  sales_data       ALICE        None  2025-07-28 04:54:34.687139          None  2025-07-28 04:55:46.750000      accounts
            1  sales_data_df    ALICE        None  2025-07-28 04:56:01.123456          None  2025-07-28 04:57:35.456789      accounts

        """
        return self.__remove_obj(name=entity, type_="entity")

    def delete_entity(self, entity):
        """
        DESCRIPTION:
            Removes archived Entity from repository.

        PARAMETERS:
            entity:
                Required Argument.
                Specifies either the name of Entity or Object of Entity
                to delete from repository.
                Types: str OR Entity

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, Entity, FeatureStore
            # Create teradataml DataFrame.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Delete the Entity 'sales_data' in the repo 'vfs_v1' using Entity name.
            # Create Entity using teradataml DataFrame Column.
            >>> entity = Entity(name="sales_data", columns=df.accounts)
            # Apply the entity to FeatureStore.
            >>> fs.apply(entity)
            True

            # List all the available entities.
            >>> fs.list_entities()
                                      description               creation_time modified_time entity_column
            name       data_domain
            sales_data ALICE                 None  2025-07-28 04:58:01.123456          None      accounts

            # Let's first archive the entity.
            >>> fs.archive_entity(entity=entity.name)
            Entity 'sales_data' is archived.
            True

            # Delete Entity with name "sales_data".
            >>> fs.delete_entity(entity=entity.name)
            Entity 'sales_data' is deleted.
            True

            # List the entities after delete.
            >>> fs.list_entities()
            Empty DataFrame
            Columns: [id, column_name, description, tags, data_type, feature_type, status, creation_time, modified_time, group_name]
            Index: []

            Example 2: Delete the Entity 'sales_data' in the repo 'vfs_v1' using Entity object.
            # Create Entity using teradataml DataFrame Column.
            >>> entity2 = Entity(name="sales_data_df", columns=df.accounts)
            # Apply the entity to FeatureStore.
            >>> fs.apply(entity2)
            True

            # List all the available entities.
            >>> fs.list_entities()
                                         description               creation_time modified_time entity_column
            name       data_domain
            sales_data_df ALICE                 None  2025-07-28 04:59:14.325456          None      accounts

            # Let's first archive the entity.
            >>> fs.archive_entity(entity=entity2)
            Entity 'sales_data_df' is archived.
            True

            # Delete Entity with Entity object.
            >>> fs.delete_entity(entity=entity2)
            Entity 'sales_data_df' is deleted.
            True
        """
        return self.__remove_obj(name=entity, type_="entity", action="delete")

    def __get_features_where_clause(self, features):
        """
        Internal function to prepare a where clause on features df.
        """
        col_expr = Col("name") == features[0]
        for feature in features[1:]:
            col_expr = ((col_expr) | (Col("name") == feature))
        col_expr = col_expr & (Col("data_domain") == self.__data_domain)
        return col_expr

    def archive_feature_group(self, feature_group):
        """
        DESCRIPTION:
            Archives FeatureGroup from repository. Note that archived FeatureGroup
            is not available for any further processing. Archived FeatureGroup can be
            viewed using "list_feature_groups(archived=True)" method.
            Note:
                The function archives the associated Features, Entity and DataSource
                if they are not associated with any other FeatureGroups.

        PARAMETERS:
            feature_group:
                Required Argument.
                Specifies either the name of FeatureGroup or Object of FeatureGroup
                to archive from repository.
                Types: str OR FeatureGroup

        RETURNS:
            bool.

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureGroup, FeatureStore
            # Create teradataml DataFrame.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1", data_domain="d1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Archive the FeatureGroup 'sales' in the repo 'vfs_v1' using FeatureGroup name.
            # Create FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name="sales", entity_columns="accounts", df=df, timestamp_column="datetime")
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # List all the available FeatureGroups.
            >>> fs.list_feature_groups()
                              description data_source_name entity_name               creation_time modified_time
            name  data_domain                                                                                   
            sales d1                 None            sales       sales  2025-07-28 05:00:19.780453          None

            # Archive FeatureGroup with name "sales".
            >>> fs.archive_feature_group(feature_group='sales')
            FeatureGroup 'sales' is archived.
            True

            # List all the available FeatureGroups after archive.
            >>> fs.list_feature_groups(archived=True)
                name data_domain description data_source_name entity_name               creation_time modified_time               archived_time
            0  sales          d1        None            sales       sales  2025-07-28 05:00:19.780453          None  2025-07-28 05:02:04.100000

            # Example 2: Archive the FeatureGroup 'sales' in the repo 'vfs_v1' using FeatureGroup object.
            # Create FeatureGroup from teradataml DataFrame.
            >>> fg2 = FeatureGroup.from_DataFrame(name="sales_df", entity_columns="accounts", df=df, timestamp_column="datetime")
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg2)
            True

            # Archive FeatureGroup with FeatureGroup object.
            >>> fs.archive_feature_group(feature_group=fg2)
            FeatureGroup 'sales_df' is archived.
            True

            # List all the available FeatureGroups after archive.
            >>> fs.list_feature_groups(archived=True)
                name data_domain description data_source_name entity_name               creation_time modified_time               archived_time
            0  sales          d1        None            sales       sales  2025-07-28 05:00:19.780453          None  2025-07-28 05:02:04.100000
            1  sales_df       d1        None            sales       sales  2025-07-28 05:02:01.123456          None  2025-07-28 05:03:35.456789
        """
        argument_validation_params = []
        argument_validation_params.append(["feature_group", feature_group, False, (str, FeatureGroup), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        feature_group_name = feature_group if isinstance(feature_group, str) else feature_group.name

        stg_table = _FeatureStoreDFContainer.get_df("feature_group_staging", self.__repo, self.__data_domain)
        stg_table = stg_table[stg_table.name == feature_group_name]
        if stg_table.shape[0] > 0:
            print("{} '{}' is already archived.".format('FeatureGroup', feature_group_name))
            return False

        # Check if FeatureGroup is related to any FeatureProcess
        feature_process_df = self.list_feature_processes()
        related_processes = feature_process_df[(feature_process_df['data_source'] == feature_group_name)]
        
        if related_processes.shape[0] > 0:
            process_ids = [fp.process_id for fp in related_processes.itertuples()]
            related_process_ids = "feature process(es) {}".format(process_ids)
            err_code = MessageCodes.EFS_OBJ_IN_FEATURE_PROCESS
            err_msg = Messages.get_message(err_code, 
                                           'FeatureGroup',
                                           feature_group_name, 
                                           related_process_ids,
                                           "feature process(es)",
                                           "FeatureStore.archive_feature_process() and FeatureStore.delete_feature_process()",
                                           )
            raise TeradataMlException(err_msg, err_code)

        fg = self.get_feature_group(feature_group_name) if isinstance(feature_group, str) else feature_group

        fg_df = self.list_feature_groups()

        # Find out shared Features. Extract the features which are mapped to
        # other groups. They can not be deleted.
        feature_names = [f.name for f in fg.features]
        features_df = self.list_features()
        col_expr = self.__get_features_where_clause(feature_names)
        features_df = features_df[((features_df.group_name != fg.name) & (col_expr))]
        shared_features = [f.name for f in features_df.drop_duplicate('name').itertuples()]
        feature_names_to_remove = [f for f in feature_names if f not in shared_features]

        # Find out shared Entities. If entity is not shared, then update 'entity_name'
        # to update value.
        entity_name = None
        ent = fg_df[((fg_df.entity_name == fg.entity.name) & (fg_df.name != fg.name))]
        recs = ent.shape[0]
        if recs == 0:
            entity_name = fg.entity.name

        # Find out shared DataSources. If datasource is not shared, then update 'data_source_name'.
        data_source_name = None
        ds_df = fg_df[((fg_df.data_source_name == fg.data_source.name) & (fg_df.name != fg.name))]
        recs = ds_df.shape[0]
        if recs == 0:
            data_source_name = fg.data_source.name

        res = self._archive_feature_group(fg.name, feature_names_to_remove, entity_name, data_source_name)

        if res == 1:
            print("FeatureGroup '{}' is archived.".format(feature_group_name))
            return True

        print("FeatureGroup '{}' not exist to archive.".format(feature_group_name))
        return False

    @db_transaction
    def _archive_feature_group(self, group_name, feature_names, entity_name, data_source_name):
        """
        DESCRIPTION:
            Internal method to archive FeatureGroup from repository.

        PARAMETERS:
            group_name:
                Required Argument.
                Specifies the name of FeatureGroup to archive from repository.
                Types: str

            feature_names:
                Required Argument.
                Specifies the name of Features to archive from repository.
                Types: list

            entity_name:
                Required Argument.
                Specifies the name of Entity to archive from repository.
                Types: str

            data_source_name:
                Required Argument.
                Specifies the name of DataSource to archive from repository.
                Types: str

        RETURNS:
            bool.

        RAISES:
            OperationalError

        EXAMPLES:
            >>> self._archive_feature_group("group1", ["feature1"], "entity_name", None)
        """
        # Remove data for FeatureGroup from Xref table.
        # This allows to remove data from other tables.
        res = _delete_data(schema_name=self.__repo,
                           table_name=self.__table_names["group_features"],
                           delete_conditions=(Col("group_name") == group_name) &
                                             (Col("group_data_domain") == self.__data_domain)
                           )

        # Remove FeatureGroup.
        res = _delete_data(schema_name=self.__repo,
                           table_name=self.__table_names["feature_group"],
                           delete_conditions=(Col("name") == group_name) &
                                             (Col("data_domain") == self.__data_domain)
                           )

        # Remove Features.
        if feature_names:
            _delete_data(schema_name=self.__repo,
                         table_name=self.__table_names["feature"],
                         delete_conditions=self.__get_features_where_clause(feature_names)
                         )

        # Remove entities.
        if entity_name:
            _delete_data(schema_name=self.__repo,
                         table_name=self.__table_names["entity_xref"],
                         delete_conditions=(Col("entity_name") == entity_name) &
                                           (Col("data_domain") == self.__data_domain)
                         )

            _delete_data(schema_name=self.__repo,
                         table_name=self.__table_names["entity"],
                         delete_conditions=(Col("name") == entity_name) &
                                           (Col("data_domain") == self.__data_domain)
                         )

        # Remove DataSource.
        if data_source_name:
            _delete_data(schema_name=self.__repo,
                         table_name=self.__table_names["data_source"],
                         delete_conditions=(Col("name") == data_source_name) &
                                           (Col("data_domain") == self.__data_domain)
                         )

        return res

    @db_transaction
    def delete_feature_group(self, feature_group):
        """
        DESCRIPTION:
            Removes archived FeatureGroup from repository.
            Note:
                Unlike 'archive_feature_group()', this function does not delete the
                associated Features, Entity and DataSource. One should delete those
                using 'delete_feature()', 'delete_entity()' and 'delete_data_source()'.

        PARAMETERS:
            feature_group:
                Required Argument.
                Specifies either the name of FeatureGroup or Object of FeatureGroup
                to delete from repository.
                Types: str OR FeatureGroup

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import DataFrame, FeatureGroup, FeatureStore
            # Create teradataml DataFrame.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1", data_domain="d1")
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Example 1: Delete the FeatureGroup 'sales' in the repo 'vfs_v1' using FeatureGroup name.
            # Create FeatureGroup from teradataml DataFrame.
            >>> fg = FeatureGroup.from_DataFrame(name="sales", entity_columns="accounts", df=df, timestamp_column="datetime")
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg)
            True

            # List all the available FeatureGroups.
            >>> fs.list_feature_groups()
                              description data_source_name entity_name               creation_time modified_time
            name  data_domain                                                                                   
            sales d1                 None            sales       sales  2025-07-28 05:00:19.780453          None

            # Archive FeatureGroup with name "sales".
            >>> fs.archive_feature_group(feature_group='sales')
            FeatureGroup 'sales' is archived.
            True

            # Delete FeatureGroup with name "sales".
            >>> fs.delete_feature_group(feature_group='sales')
            FeatureGroup 'sales' is deleted.
            True

            # List all the available FeatureGroups after delete.
            >>> fs.list_feature_groups()
            Empty DataFrame
            Columns: [description, data_source_name, entity_name, creation_time, modified_time]
            Index: []

            Example 2: Delete the FeatureGroup 'sales' in the repo 'vfs_v1' using FeatureGroup object.
            # Create FeatureGroup from teradataml DataFrame.
            >>> fg2 = FeatureGroup.from_DataFrame(name="sales", entity_columns="accounts", df=df, timestamp_column="datetime")
            # Apply FeatureGroup to FeatureStore.
            >>> fs.apply(fg2)
            True

            # Archive FeatureGroup with FeatureGroup object.
            >>> fs.archive_feature_group(feature_group=fg2)
            FeatureGroup 'sales' is archived.
            True

            # Delete FeatureGroup with FeatureGroup object.
            >>> fs.delete_feature_group(feature_group=fg2)
            FeatureGroup 'sales' is deleted.
            True
        """
        argument_validation_params = []
        argument_validation_params.append(["feature_group", feature_group, False, (str, FeatureGroup), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        fg_name = feature_group if isinstance(feature_group, str) else feature_group.name

        # Validation for delete action - ensure FeatureGroup is already archived
        main_fg_df = self.__get_feature_group_df()
        existing_records = main_fg_df[main_fg_df["name"] == fg_name]
        
        if existing_records.shape[0] > 0:
            error_code = MessageCodes.EFS_DELETE_BEFORE_ARCHIVE
            error_msg = Messages.get_message(
                                            error_code,
                                            'FeatureGroup',
                                            fg_name,
                                            'feature_group')
            raise TeradataMlException(error_msg, error_code)

        # Remove data for FeatureGroup.
        _delete_data(table_name=self.__table_names["group_features_staging"],
                     schema_name=self.__repo,
                     delete_conditions=(Col("group_name") == fg_name) &
                                       (Col("group_data_domain") == self.__data_domain)
                     )

        res = _delete_data(table_name=self.__table_names["feature_group_staging"],
                           schema_name=self.__repo,
                           delete_conditions=(Col("name") == fg_name) &
                                             (Col("data_domain") == self.__data_domain)
                           )

        if res == 1:
            print("FeatureGroup '{}' is deleted.".format(fg_name))
            return True

        print("FeatureGroup '{}' does not exist to delete.".format(fg_name))
        return False

    @property
    def version(self):
        """
        DESCRIPTION:
            Get the FeatureStore version.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Example 1: Get the version of FeatureStore version for
            #            the repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('vfs_v1')
            FeatureStore is ready to use.

            # Get the version of FeatureStore.
            >>> fs.version
            '2.0.0'
        """
        if self.__version is None:
            self.__version = self.__get_version()
        return self.__version

    def list_feature_catalogs(self) -> DataFrame:
        """
        DESCRIPTION:
            Lists all the feature catalogs.

        PARAMETERS:
            None

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            # Example 1: List all the feature catalogs in the repo 'vfs_v1'.
            >>> from teradataml import FeatureStore

            # Create FeatureStore for the repo 'vfs_v1' or use existing one.
            >>> fs = FeatureStore("vfs_v1")
            FeatureStore is ready to use.

            # Load the sales data.
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a feature process.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' started.
            Process '5747082b-4acb-11f0-a2d7-f020ffe7fe09' completed.

            # List all the feature catalogs in the repo 'vfs_v1'.
            >>> fs.list_feature_catalogs()
                        data_domain  feature_id                                 table_name                     valid_start                      valid_end
            entity_name
            accounts          sales           2  FS_T_918e1cb4_c6bc_6d38_634d_7b9fe53e2a63  2025-06-16 16:02:49.481245+00:  9999-12-31 23:59:59.999999+00:
            accounts          sales      100001  FS_T_e84ff803_3d5c_4793_cd72_251c780fffe4  2025-06-16 16:02:49.481245+00:  9999-12-31 23:59:59.999999+00:
            accounts          sales           1  FS_T_918e1cb4_c6bc_6d38_634d_7b9fe53e2a63  2025-06-16 16:02:49.481245+00:  9999-12-31 23:59:59.999999+00:
            accounts          sales      200001  FS_T_918e1cb4_c6bc_6d38_634d_7b9fe53e2a63  2025-06-16 16:02:49.481245+00:  9999-12-31 23:59:59.999999+00:
        """
        df = self.__get_without_valid_period_df(self.__get_features_metadata_df())
        return df[df.data_domain==self.__data_domain]

    def archive_feature_process(self, process_id):
        """
        DESCRIPTION:
            Archives the FeatureProcess with the given process_id.
            Notes:
                 * Archived FeatureProcess is not available for any further processing.
                 * Archived FeatureProcess can be viewed using `FeatureStore.list_feature_processes(archived=True)`.
                   method.
                 * Same feature can be ingested by multiple processes. If feature associated with
                   process "process_id" is also associated with other processes, then this
                   function only archives the feature values associated with the process "process_id". Else
                   it archives the feature from the feature catalog. Look at `FeatureCatalog.archive_features()`.
                   for more details.

        PARAMETERS:
            process_id:
                Required Argument.
                Specifies the ID of the FeatureProcess to archive from repository.
                Types: str

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            # Create a teradataml DataFrame.
            >>> from teradataml import DataFrame, FeatureProcess, FeatureStore
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'repo'.
            >>> fs = FeatureStore("repo", data_domain='sales')
            Repo repo does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo='repo',
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '2a014f2d-6b71-11f0-aeda-f020ffe7fe09' started.
            Process '2a014f2d-6b71-11f0-aeda-f020ffe7fe09' completed.

            # List the available FeatureProcesses.
            >>> fs.list_feature_processes()
                                                 description data_domain       process_type data_source entity_id       feature_names feature_ids                     valid_start                       valid_end
            process_id                                                                                                                                                                                           
            2a014f2d-6b71-11f0-aeda-f020ffe7fe09                   sales  denormalized view     "sales"  accounts  Apr, Feb, Jan, Mar        None  2025-07-28 05:10:34.760000+00:  9999-12-31 23:59:59.999999+00:

            # Example: Archive the FeatureProcess with process_id '2a014f2d-6b71-11f0-aeda-f020ffe7fe09'.
            >>> fs.archive_feature_process("2a014f2d-6b71-11f0-aeda-f020ffe7fe09")
            Feature 'Jan' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Jan' is archived from metadata.
            Feature 'Feb' is archived from table 'FS_T_6003dc24_375e_7fd6_46f0_eeb868305c4a'.
            Feature 'Feb' is archived from metadata.
            Feature 'Mar' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Mar' is archived from metadata.
            Feature 'Apr' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Apr' is archived from metadata.
            FeatureProcess with process id '2a014f2d-6b71-11f0-aeda-f020ffe7fe09' is archived.
            True
        """
        argument_validation_params = []
        argument_validation_params.append(["process_id", process_id, True, str, True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        features = self.__validate_feature_process(process_id)
        if features is False:
            return False

        feature_details = FeatureCatalog._get_feature_details(
            self.__repo, self.__data_domain, features)

        # Get the shared features.
        shared_features = FeatureCatalog._get_shared_features(self.__repo, self.__data_domain)

        # Remove the features from the feature metadata table.
        return self.__remove_feature_process(
            process_id, features, feature_details, shared_features)

    def delete_feature_process(self, process_id):
        """
        DESCRIPTION:
            Deletes the archived feature process from feature store with the given process_id.
            Notes:
                 * One feature can be ingested by multiple processes. If feature associated with
                   process "process_id" is also ingested by other processes, then "delete_feature_process()"
                   function only deletes the feature values associated with the process "process_id". Else
                   it deletes the feature from the feature catalog. Look at 'FeatureCatalog.delete_features()'
                   for more details.

        PARAMETERS:
            process_id:
                Required Argument.
                Specifies the ID of the FeatureProcess to delete from repository.
                Types: str

        RETURNS:
            bool

        RAISES:
            TeradataMLException, TypeError, ValueError

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            # Create a teradataml DataFrame.
            >>> from teradataml import DataFrame, FeatureProcess, FeatureStore
            >>> df = DataFrame("sales")

            # Create FeatureStore for repo 'repo'.
            >>> fs = FeatureStore("repo", data_domain='sales')
            Repo repo does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore for this repository.
            >>> fs.setup()
            True

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo='repo',
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '2a014f2d-6b71-11f0-aeda-f020ffe7fe09' started.
            Process '2a014f2d-6b71-11f0-aeda-f020ffe7fe09' completed.

            # List the available FeatureProcesses.
            >>> fs.list_feature_processes()
                                                 description data_domain       process_type data_source entity_id       feature_names feature_ids                     valid_start                       valid_end
            process_id                                                                                                                                                                                           
            2a014f2d-6b71-11f0-aeda-f020ffe7fe09                   sales  denormalized view     "sales"  accounts  Apr, Feb, Jan, Mar        None  2025-07-28 05:10:34.760000+00:  9999-12-31 23:59:59.999999+00:

            # Example: Archive the FeatureProcess with process_id '2a014f2d-6b71-11f0-aeda-f020ffe7fe09'.
            >>> fs.archive_feature_process("2a014f2d-6b71-11f0-aeda-f020ffe7fe09")
            Feature 'Jan' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Jan' is archived from metadata.
            Feature 'Feb' is archived from table 'FS_T_6003dc24_375e_7fd6_46f0_eeb868305c4a'.
            Feature 'Feb' is archived from metadata.
            Feature 'Mar' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Mar' is archived from metadata.
            Feature 'Apr' is archived from table 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'.
            Feature 'Apr' is archived from metadata.
            FeatureProcess with process id '2a014f2d-6b71-11f0-aeda-f020ffe7fe09' is archived.
            True

            # Example: Delete the FeatureProcess with process_id '2a014f2d-6b71-11f0-aeda-f020ffe7fe09'.
            >>> fs.delete_feature_process('2a014f2d-6b71-11f0-aeda-f020ffe7fe09')
            Feature 'Feb' deleted successfully from table 'FS_T_e84ff803_3d5c_4793_cd72_251c780fffe4'.
            Feature 'Jan' deleted successfully from table 'FS_T_918e1cb4_c6bc_6d38_634d_7b9fe53e2a63'.
            Feature 'Mar' deleted successfully from table 'FS_T_918e1cb4_c6bc_6d38_634d_7b9fe53e2a63'.
            Feature 'Apr' deleted successfully from table 'FS_T_918e1cb4_c6bc_6d38_634d_7b9fe53e2a63'.
            FeatureProcess with process_id '2a014f2d-6b71-11f0-aeda-f020ffe7fe09' is deleted.
            True

            # List the available FeatureProcesses after delete.
            >>> fs.list_feature_processes()
            Empty DataFrame
            Columns: [description, data_domain, process_type, data_source, entity_id, feature_names, feature_ids, valid_start, valid_end]
            Index: []
        """
        argument_validation_params = []
        argument_validation_params.append(["process_id", process_id, True, str, True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Before archive check if the specified process id is existed or not.
        features = self.__validate_feature_process(process_id, type_='delete')
        if features is False:
            return False

        feature_details = FeatureCatalog._get_feature_details(
            self.__repo, self.__data_domain, features)

        # Get the shared features.
        shared_features = FeatureCatalog._get_shared_features(self.__repo, self.__data_domain)

        return self.__remove_feature_process(
            process_id, features, feature_details, shared_features, type_='delete')

    @db_transaction
    def __remove_feature_process(self,
                                 process_id,
                                 process_features,
                                 feature_details,
                                 shared_features,
                                 type_='archive'):
        """
        DESCRIPTION:
            Internal function to remove the FeatureProcess from repository.
            It also removes the associated features from the feature table.

        PARAMETERS:
            process_id:
                Required Argument.
                Specifies the ID of the FeatureProcess to remove from repository.
                Types: str

            feature_details:
                Required Argument.
                Specifies the list of features to remove from repository.
                Types: list of namedtuple

            type_:
                Optional Argument.
                Specifies the type of removal. Allowed values are 'archive' and 'delete'.
                Default value is 'archive'.
                Types: str

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> self.__remove_feature_process("5747082b-4acb-11f0-a2d7-f020ffe7fe09",
            ... process_features=[namedtuple('feature_', ['name', 'id', 'table_name'])('sales_data_Feb', 1, 'FS_T_12345')],
            ... type_='archive')
        """
        temporal_clause = 'CURRENT VALIDTIME'
        delete_condition = (Col("process_id") == process_id)
        if type_ == 'delete':
            temporal_clause = None

        fc = FeatureCatalog(self.__repo, self.__data_domain)
        res1 = fc._remove_features(process_features, feature_details, type_=='archive', shared_features, process_id)

        # Remove it from feature process table.
        res = _delete_data(table_name=self.__table_names["feature_process"],
                           schema_name=self.__repo,
                           delete_conditions=delete_condition,
                           temporal_clause=temporal_clause
                           )

        if res >= 1:
            print("FeatureProcess with process id '{}' is {}d.".format(process_id, type_))
            return res1 & True

        print("FeatureProcess with process id '{}' does not exist to {}.".format(process_id, type_))
        return res1 & False

    def __validate_feature_process(self, process_id, type_='archive'):
        """
        DESCRIPTION:
            Internal function to validate if the feature process is existed or not.
            Also, the function checks if the process is archived or not.

        PARAMETERS:
            process_id:
                Required Argument.
                Specifies the ID of the FeatureProcess to validate.
                Types: str

            type_:
                Optional Argument.
                Specifies the type of validation. Allowed values are 'archive' and 'delete'.
                Default value is 'archive'.
                Types: str

        RETURNS:
            list or bool.
            False if process does not exist or archived.
            list if all validations are passed.

        RAISES:
            TeradatamlException

        EXAMPLES:
            >>> # Validate the feature process with process_id '5747082b-4acb-11f0-a2d7-f020ffe7fe09'.
            >>> fs.__validate_feature_process(process_id='5747082b-4acb-11f0-a2d7-f020ffe7fe09')
            (['sales_data_Feb', 'sales_data_Jan'], ['sales_data_Mar', 'sales_data_Apr'])
        """
        # Extract process type, data source, entity_id, feature_names from given process id.
        sql = EFS_ARCHIVED_RECORDS.format("feature_names",
                                          '"{}"."{}"'.format(self.__repo,
                                                             self.__table_names["feature_process"]),
                                          "PROCESS_ID = '{}' AND DATA_DOMAIN = '{}'".
                                          format(process_id, self.__data_domain))

        feature_names = set()
        all_archived = True
        any_one_not_archived = False
        for rec in execute_sql(sql):
            is_archived = rec[1] == 1
            all_archived = all_archived and is_archived
            any_one_not_archived = any_one_not_archived or (not is_archived)
            feature_names.update([f.strip() for f in rec[0].split(",")])

        # Not raising error to align with the behavior of other methods.
        if not feature_names:
            print("FeatureProcess with process id '{}' does not exist.".format(process_id))
            return False

        # Check if feature is already archived or not.
        if type_ == 'archive' and all_archived:
            # All records valid end date should be less than current timestamp in such case.
            print("FeatureProcess with process id '{}' is already archived.".format(process_id))
            return False

        # For delete, check if the process is archived or not first.
        if type_ == 'delete' and any_one_not_archived:
            print("FeatureProcess with process id '{}' is not archived. "
                  "First archive the process and then delete it.".format(process_id))
            return False

        # Check if feature is associated with any dataset or not.
        dataset_features_df = self.__get_dataset_features_df()
        # Validate the feature names.
        _Validators._validate_features_not_in_efs_dataset(
            df=dataset_features_df[(dataset_features_df['data_domain'] == self.__data_domain)],
            feature_names=list(feature_names),
            action='archived')

        return feature_names
    
    def remove_data_domain(self):
        """
        DESCRIPTION:
            Removes the data domain from the FeatureStore and all associated objects.
            
            Notes:
                * This operation permanently deletes all objects, tables, and views tied to the data domain.
                * There is no archival or built‑in recovery, all deletions are irreversible.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> from teradataml import FeatureStore
            # Create a new FeatureStore or use an existing one.
            >>> fs = FeatureStore("repo", data_domain="sales")
            FeatureStore is ready to use.

            # Remove the data domain 'sales' and all associated objects.
            >>> fs.remove_data_domain()
            The function will remove the data domain 'sales' and all associated objects. Are you sure you want to proceed? (Y/N): Y
            Data domain 'sales' is removed from the FeatureStore.
            True
        """
        confirmation = input("The function will remove the data domain '{}' and" \
                             " all associated objects. Are you sure you want to proceed? (Y/N): ".format(self.__data_domain))

        if confirmation not in ["Y", "y"]:
            return False

        # Get the views to drop related to the data domain.
        dataset_features_df = self.__get_dataset_features_df()
        filtered_dataset_features_df = dataset_features_df[dataset_features_df['data_domain'] == self.__data_domain].itertuples()
        views_to_drop = list({rec.feature_view for rec in filtered_dataset_features_df})

        # Get the tables to drop related to the data domain.
        features_metadata_df = self.__get_features_metadata_df()
        filtered_features_metadata_df = features_metadata_df[features_metadata_df['data_domain'] == self.__data_domain].itertuples()
        tables_to_drop = list({rec.table_name for rec in filtered_features_metadata_df})

        res = db_transaction(self.__remove_data_domain)()
        
        # Drop the views related to the data domain.
        for view in views_to_drop:
            try:
                execute_sql(f"DROP VIEW {_get_quoted_object_name(schema_name=self.__repo, object_name=view)}")
            except Exception as e:
                print(f"Error dropping view {view}: {e}")
        # Drop the tables related to the data domain.
        for table in tables_to_drop:
            try:
                execute_sql(f"DROP TABLE {_get_quoted_object_name(schema_name=self.__repo, object_name=table)}")
            except Exception as e:
                print(f"Error dropping table {table}: {e}")

        return True

    def __remove_data_domain(self):
        """
        DESCRIPTION:
            Internal method to remove the data domain from the FeatureStore and all associated objects.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> fs.__remove_data_domain()
        """
        # TO remove data domain from the FeatureStore, we need to:
        # 1. Remove data domain entries from the dataset catalog and dataset features.
        # 2. Remove data domain entries from the feature metadata.
        # 3. Remove data domain entries from the feature processes.
        # 4. Remove data_domain entries from feature groups, group features, and their staging tables.
        # 5. Remove data_domain entries from features and their staging tables.
        # 6. Remove data_domain entries from entities, entity xref, and their staging tables.
        # 7. Remove data_domain entries from data sources and their staging tables.
        # 8. Remove data_domain entries from data_domain table.

        # 1. Remove data domain entries from the dataset catalog and dataset features.
        _delete_data(
            table_name=self.__table_names['dataset_catalog'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.__data_domain)
        )

        _delete_data(
            table_name=self.__table_names['dataset_features'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.__data_domain)
        )

        # 2. Remove data domain entries from the feature metadata.
        _delete_data(
            table_name=self.__table_names['feature_metadata'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.__data_domain)
        )

        # 3. Remove data_domain entries from the feature processes.
        _delete_data(
            table_name=self.__table_names['feature_process'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.__data_domain)
        )

        # 4. Remove data_domain entries from feature groups, group features, and their staging tables.
        _delete_data(
            table_name=self.__table_names['group_features'],
            schema_name=self.__repo,
            delete_conditions=((Col("group_data_domain") == self.__data_domain))
        )
        _delete_data(
            table_name=self.__table_names['feature_group'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.__data_domain)
        )

        _delete_data(
            table_name=self.__table_names["group_features_staging"],
            schema_name=self.__repo,
            delete_conditions=(Col("group_data_domain") == self.__data_domain))

        _delete_data(
            table_name=self.__table_names["feature_group_staging"],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.__data_domain)
        )

        # 5. Remove data_domain entries from features and their staging tables.
        _delete_data(
            table_name=self.__table_names['feature'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )

        _delete_data(
            table_name=self.__table_names['feature_staging'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )

        # 6. Remove data_domain entries from entities, entity xref, and their staging tables.
        _delete_data(
            table_name=self.__table_names['entity_xref'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )
        _delete_data(
            table_name=self.__table_names['entity'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )

        _delete_data(
            table_name=self.__table_names['entity_staging'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )

        _delete_data(
            table_name=self.__table_names['entity_staging_xref'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )

        # 7. Remove data_domain entries from data sources and their staging tables.
        _delete_data(
            table_name=self.__table_names['data_source'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )

        _delete_data(
            table_name=self.__table_names['data_source_staging'],
            schema_name=self.__repo,
            delete_conditions=(Col("data_domain") == self.data_domain)
        )

        # 8. Remove data_domain entries from data_domain table.
        _delete_data(
            table_name=self.__table_names['data_domain'],
            schema_name=self.__repo,
            delete_conditions=(Col("name") == self.__data_domain)
        )

        print(f"Data domain '{self.__data_domain}' is removed from the FeatureStore.")
        return True

    def mind_map(self, feature_process=None):
        """
        DESCRIPTION:
            Returns a visual mind map of the FeatureStore, showing data sources,
            feature processes, feature catalog, and dataset catalog, with dependencies
            illustrated by curves.
            Note:
                Works only in Jupyter Notebook or similar environments that support HTML rendering.

        PARAMETERS:
            feature_process:
                Optional Argument.
                Specifies the feature process to filter the mind map. When specified,
                only the feature process and its related data sources, features, and datasets
                is displayed.
                Notes:
                     * mind_map() display only the features which are associated with the
                       feature process for the datasets also. For example, if Dataset is associated
                       with Feature1, Feature2 and Feature1 is ingested by FeatureProcess1 and
                       Feature2 is ingested by FeatureProcess2, then mind_map() displays the
                       Dataset with Feature1 only if "feature_process" is set to FeatureProcess1.
                     * If "feature_process" is not specified, then mind_map() displays all the
                       feature processes, data sources, features, and datasets in the FeatureStore.
                Types: str OR list of str

        RETURNS:
            None (displays HTML visualization)

        RAISES:
            TypeError

        EXAMPLES:
            # Example 1: Display the mind map of the FeatureStore with all feature processes.
            >>> from teradataml import DataFrame, FeatureStore
            >>> load_example_data("dataframe", "sales")
            # Create DataFrame.
            >>> sales_df = DataFrame("sales")
            >>> admissions_df = DataFrame("admissions")

            # Create a FeatureStore for the repo 'vfs_v1'.
            >>> fs = FeatureStore("vfs_v1", data_domain='Analytics')
            FeatureStore is ready to use.

            # Create a feature process to ingest sales df.
            >>> fp1 = fs.get_feature_process(object=df,
            ...                              features=['Jan', 'Feb', 'Mar', 'Apr'],
            ...                              entity='accounts')
            >>> fp1.run()
            Process '7b9f76d6-562c-11f0-bb98-c934b24a960f' started.
            Process '7b9f76d6-562c-11f0-bb98-c934b24a960f' completed.
            True

            # Create a feature process to ingest admissions df.
            >>> fp2 = fs.get_feature_process(object=admissions_df,
            ...                              features=[ 'masters', 'gpa', 'stats', 'programming', 'admitted'],
            ...                              entity='id')
            >>> fp2.run()
            Process 'a5de0230-6b8e-11f0-ae70-f020ffe7fe09' started.
            Process 'a5de0230-6b8e-11f0-ae70-f020ffe7fe09' completed.

            # Example 1: Display the mind map of the FeatureStore.
            >>> fs.mind_map()

            # Example 2: Display the mind map of the FeatureStore for the sales feature process.
            >>> fs.mind_map(feature_process=fp1.process_id)

            # Example 3: Display the mind map of the FeatureStore for admissions features.
            >>> fs.mind_map(feature_process=fp2.process_id)

            # Example 4: Display the mind map of the FeatureStore for both sales and admissions feature
            #            processes.
            >>> fs.mind_map(feature_process=[fp1.process_id, fp2.process_id])
        """
        # Validate arguments
        argument_validation_params = []
        argument_validation_params.append(["feature_process", feature_process, True, (str, list), True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # 1. Declare Python variables for the mind map
        data_sources_ = set()
        feature_processes_ = set()
        features_ = set()
        datasets_ = set()
        data_source_map = {}
        feature_process_map = {}
        dataset_feature_map = {}

        sql = """
        select distinct process_id, oreplace(data_source, '"', '') as data_source, feature_names from "{}".{}
        where data_domain = '{}'
        """.format(self.__repo, EFS_DB_COMPONENTS['feature_process'], self.__data_domain)

        # If user provides feature process, filter the SQL query.
        if feature_process:
            feature_process = UtilFuncs._as_list(feature_process)
            feature_process_str = ', '.join(f"'{fp}'" for fp in feature_process)
            sql += " and process_id in ({})".format(feature_process_str)

        recs = execute_sql(sql)
        for rec in recs:
            process_id, data_source, feature_names = rec
            data_sources_.add(data_source)
            feature_processes_.add(process_id)
            feature_names = [f.strip() for f in feature_names.split(',')]
            features_.update(feature_names)

            # Populate the maps.
            if data_source not in data_source_map:
                data_source_map[data_source] = []
            data_source_map[data_source].append(process_id)

            if process_id not in feature_process_map:
                feature_process_map[process_id] = []
            feature_process_map[process_id].extend(feature_names)

        # feature process map can have duplicates.
        feature_process_map = {k: list(set(v)) for k, v in feature_process_map.items()}

        data_sources = [{"id": ds, "label": ds} for ds in data_sources_]
        feature_processes = [{"id": fp, "label": fp} for fp in feature_processes_]
        features = [{"id": f, "label": f} for f in features_]

        # Create datasets and dataset_feature_map.
        ds_sql = """
        select feature_view, feature_name from
        "{}".{}
        where data_domain = '{}'
        """.format(self.__repo, EFS_DB_COMPONENTS['dataset_features'], self.__data_domain)

        # If user provides a specific feature process, then show only those features in datasets.
        if feature_process:
            fp_str = ', '.join(f"'{fp}'" for fp in feature_process)
            ds_sql += " and feature_version IN ({})".format(fp_str)

        recs = execute_sql(ds_sql)
        for rec in recs:
            feature_view, feature_name = rec
            datasets_.add(feature_view)
            if feature_view not in dataset_feature_map:
                dataset_feature_map[feature_view] = []
            dataset_feature_map[feature_view].append(feature_name)

        datasets = [{"id": ds, "label": ds} for ds in datasets_]

        # 2. Add unique suffix to all ids in the variables
        from time import time as epoch_seconds
        suffix = f"_fs_{str(epoch_seconds()).replace('.', '_')}"

        def add_suffix_to_list(lst):
            return [dict(obj, id=obj["id"] + suffix) for obj in lst]

        def add_suffix_to_dict_keys_and_values(dct):
            return {k + suffix: [v + suffix for v in vs] for k, vs in dct.items()}

        data_sources_js = add_suffix_to_list(data_sources)
        feature_processes_js = add_suffix_to_list([obj for obj in feature_processes if not obj.get("invisible")])
        # Keep invisible objects for completeness in features, but filter for display if needed
        features_js = add_suffix_to_list(features)
        datasets_js = add_suffix_to_list(datasets)
        data_source_map_js = add_suffix_to_dict_keys_and_values(data_source_map)
        feature_process_map_js = add_suffix_to_dict_keys_and_values(feature_process_map)
        dataset_feature_map_js = add_suffix_to_dict_keys_and_values(dataset_feature_map)

        # 3. Prepare JS variable strings
        import json
        js_data_sources = json.dumps(data_sources_js)
        js_feature_processes = json.dumps(feature_processes_js)
        js_features = json.dumps(features_js)
        js_datasets = json.dumps(datasets_js)
        js_data_source_map = json.dumps(data_source_map_js)
        js_feature_process_map = json.dumps(feature_process_map_js)
        js_dataset_feature_map = json.dumps(dataset_feature_map_js)

        # 4. Get current GMT timestamp for display
        from datetime import datetime, timezone
        gmt_now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S GMT')

        # 5. Inject the JS variables, timestamp, and feature store name into the template
        html_ = _TD_FS_MindMap_Template\
            .replace("__DATA_SOURCES__", js_data_sources) \
            .replace("__FEATURE_PROCESSES__", js_feature_processes) \
            .replace("__FEATURES__", js_features) \
            .replace("__DATASETS__", js_datasets) \
            .replace("__DATA_SOURCE_MAP__", js_data_source_map) \
            .replace("__FEATURE_PROCESS_MAP__", js_feature_process_map) \
            .replace("__DATASET_FEATURE_MAP__", js_dataset_feature_map) \
            .replace("__MINDMAP_TIMESTAMP__", gmt_now) \
            .replace("__REPO__", self.__repo)\
            .replace("__DATA_DOMAIN__", self.__data_domain)

        # 7. Add the unique suffix to all element IDs in the HTML/JS
        html_ = html_.replace("_fs_i", suffix)

        from IPython.display import display, HTML
        display(HTML(html_))

