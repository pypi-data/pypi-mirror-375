"""
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: akhil.bhist@teradata.com

This file implements the utilities required for Teradata Enterprise Feature Store.
"""
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.store.feature_store.constants import EFS_DB_COMPONENTS
from teradataml.utils.utils import execute_sql
from collections import defaultdict


class _FSUtils:
    """
    Utility class for Feature Store operations.
    """

    @staticmethod
    def _get_entities_from_entity_df(df):
        """
        DESCRIPTION:
            Extracts entities from the entity DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the DataFrame containing entity information with
                columns 'entity_name' and 'entity_column'.
                Types: teradataml DataFrame.

        Returns:
            list: A list of entities.

        EXAMPLE:
            >>> from teradataml.store.feature_store.utils import _FSUtils
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore('my_repo')
            >>> df = fs.list_entities()
            >>> entities = _FSUtils._get_entities_from_entity_df(df)
            >>> print(entities)
            [Entity(name='customer', columns=['id', 'name'])]
        """
        from teradataml.store.feature_store.models import Entity
        # Store Entity name vs Columns. One Entity can have multiple columns.
        entity_columns = defaultdict(list)
        for row in df.itertuples():
            entity_columns[row.entity_name].append(row.entity_column)

        return [Entity(name=name, columns=columns) for name, columns in entity_columns.items()]

    @staticmethod
    def _get_archived_features_from_catalog(repo, data_domain):
        """
        DESCRIPTION:
            Retrieves archived features from the catalog.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the repository name.
                Type: str.

            data_domain:
                Required Argument.
                Specifies the data domain for which archived features are to be retrieved.
                Type: str.

        Returns:
            set

        EXAMPLE:
            >>> from teradataml.store.feature_store.utils import _FSUtils
            >>> archived_features = _FSUtils._get_archived_features_from_catalog('my_repo', 'finance')
            >>> print(archived_features)
            {'feature1', 'feature2', ...}
        """
        features_tbl = EFS_DB_COMPONENTS['feature']
        catalog_tbl = EFS_DB_COMPONENTS['feature_metadata']

        sql = """
        select name 
            from "{repo}"."{feature_tbl}" b, "{repo}"."{catalog}" a
        where a.feature_id = b.id
        and a.data_domain = b.data_domain
        and a.valid_end < current_timestamp
        and a.data_domain = '{data_domain}'
        """.format(
            repo=repo,
            feature_tbl=features_tbl,
            catalog=catalog_tbl,
            data_domain=data_domain
        )

        return {rec[0] for rec in execute_sql(sql)}

    @staticmethod
    def _get_open_feature_process(repo, data_domain, process_id):
        """
        DESCRIPTION:
            Retrieves the open feature process for a process id
            in a given repository and data domain.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the repository name.
                Type: str.

            data_domain:
                Required Argument.
                Specifies the data domain for which the open feature process is to be retrieved.
                Type: str.

            process_id:
                Required Argument.
                Specifies the process ID for which the open feature process is to be retrieved.
                Type: str.

        Returns:
            dict: A dictionary containing the open feature process details.

        EXAMPLE:
            >>> from teradataml.store.feature_store.utils import _FSUtils
            >>> open_process = _FSUtils._get_open_feature_process('my_repo', 'finance')
            >>> print(open_process)
            {'process_id': 123, ...}
        """
        sql = """
              CURRENT VALIDTIME
              SELECT PROCESS_TYPE, DATA_SOURCE, ENTITY_ID, FEATURE_NAMES FROM 
              "{}"."{}" WHERE 
              PROCESS_ID = '{}' AND DATA_DOMAIN = '{}'
              """.format(repo,
                         EFS_DB_COMPONENTS['feature_process'],
                         process_id, data_domain
                         )

        recs = execute_sql(sql).fetchone()

        if not recs:
            res = _FSUtils._get_data_domains(repo, process_id, 'feature_process')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "Feature process", "id '{}'".\
                                                 format(process_id), data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "Feature process", "id '{}'".\
                                                 format(process_id), data_domain)
            raise TeradataMlException(error_msg, msg_code)
        return {
            "process_id": process_id,
            "process_type": recs[0],
            "data_source": recs[1],
            "entity_id": recs[2],
            "feature_names": [f.strip() for f in recs[3].split(",")]
        }

    @staticmethod
    def _is_entity_exists_in_fc(entity_name, repo, data_domain,
                                description, columns):
        """
        DESCRIPTION:
        Checks if an entity exists in the Feature Catalog (feature_metadata table).

        PARAMETERS:
            entity_name:
                Required Argument.
                Specifies the entity name to check for existence.
                Type: str.

            repo:
                Required Argument.
                Specifies the repository name.
                Type: str.

            data_domain:
                Required Argument.
                Specifies the data domain for which the entity existence is to be checked.
                Type: str.

            description:
                Required Argument.
                Specifies the description of the entity.
                Type: str.

            columns:
                Required Argument.
                Specifies the column names of the entity.
                Type: list of str.

        Returns:
            str: The existence status of the entity.


        EXAMPLE:
            >>> from teradataml.store.feature_store.utils import _FSUtils
            >>> exists = _FSUtils._is_entity_exists_in_fc('e1', 'my_repo', 'finance', 'description', ['col1', 'col2'])
            >>> print(exists)
            "exists"
        """
        # Retrieve entity columns with description for entity name that exists in features_metadata.
        query = """
            SELECT 
                entxrf.entity_name,
                entxrf.entity_column,
                ent.description
            FROM "{0}"._efs_entity_xref entxrf
            JOIN "{0}"._efs_entity ent
                ON entxrf.entity_name = ent.name
            AND entxrf.data_domain = ent.data_domain
            WHERE entxrf.data_domain = '{1}'
            AND EXISTS (
                    SELECT 1
                    FROM "{0}"._efs_features_metadata fm
                    WHERE fm.data_domain = entxrf.data_domain
                    AND fm.entity_name = entxrf.entity_name
                    AND fm.entity_name = '{2}'
            );
            """.format(repo, data_domain, entity_name)

        records = execute_sql(query).fetchall()

        # If Records are not found, it means the entity is new and needs to be inserted.
        if not records:
            return "insert"

        for rec in records:
            # Check if the column or description is different than the existing record
            # If either the column or description is different, return "modify"
            if rec[1] not in columns or rec[2] != description:
                return "modify"

        # If no changes are found, return "exists"
        return "exists"

    # Check if an entity exists in the Feature Store (entity table)
    _is_entity_exists_in_fs = staticmethod(
        lambda entity_name, repo, data_domain: _FSUtils._get_count_from_table(
            EFS_DB_COMPONENTS['entity'], repo, data_domain, f"name = '{entity_name}'") > 0
    )

    # Check if a feature group exists in the Feature Store (feature_group table)
    _is_fg_exists_in_fs = staticmethod(
        lambda fg_name, repo, data_domain: _FSUtils._get_count_from_table(
            EFS_DB_COMPONENTS['feature_group'], repo, data_domain, f"name = '{fg_name}'") > 0
    )

    # Check if a feature group is referenced in any feature process (feature_process table)
    _is_fg_exists_in_fp = staticmethod(
        lambda fg_name, repo, data_domain: _FSUtils._get_count_from_table(
            EFS_DB_COMPONENTS['feature_process'], repo, data_domain, f"data_source = '{fg_name}' AND process_type='feature group'") > 0
    )

    @staticmethod
    def _get_count_from_table(table_name, repo, data_domain, condition=None):
        """
        DESCRIPTION:
            Retrieves records count from a specified table in the repository.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the name of the table to retrieve records from.
                Type: str.

            repo:
                Required Argument.
                Specifies the repository name.
                Type: str.

            data_domain:
                Required Argument.
                Specifies the data domain for filtering records.
                Type: str.

            condition:
                Optional Argument.
                Specifies additional conditions for filtering records.
                Type: str.

        Returns:
            int: The count of records in the specified table.

        EXAMPLE:
            >>> from teradataml.store.feature_store.utils import _FSUtils
            >>> _FSUtils._get_count_from_table(EFS_DB_COMPONENTS['feature'], 'my_table', 'my_repo')
            100
        """
        sql = f'SELECT * FROM "{repo}"."{table_name}" WHERE data_domain = \'{data_domain}\''
        if condition:
            sql += f' AND {condition}'
        return execute_sql(sql).rowcount

    @staticmethod
    def _get_sql_query_for_type(type_):
        """
        DESCRIPTION:
            Gets the SQL query template to retrieve data domains in which an object exists.

        PARAMETERS:
            type_:
                Required Argument.
                Specifies the type of object to query.
                Permitted Values: 'feature', 'entity', 'data_source', 'feature_group', 
                                  'group_features', 'feature_process', 'dataset', 'feature_version',
                                  'ds_entity'
                Types: str

        Returns:
            str: SQL query template

        EXAMPLE:
            >>> from teradataml.store.feature_store.utils import _FSUtils
            >>> sql_template = _FSUtils._get_sql_query_for_type('feature')
            >>> print(sql_template)
            'SELECT * FROM "{repo}"._efs_features WHERE name = '{object}''
        """
        # Mapping of types to their table names and column names
        table_column_mapping = {
            'feature': (EFS_DB_COMPONENTS['feature'], 'name'),
            'entity': (EFS_DB_COMPONENTS['entity'], 'name'),
            'data_source': (EFS_DB_COMPONENTS['data_source'], 'name'),
            'feature_group': (EFS_DB_COMPONENTS['feature_group'], 'name'),
            'group_features': (EFS_DB_COMPONENTS['group_features'], 'group_name'),
            'feature_process': (EFS_DB_COMPONENTS['feature_process'], 'process_id'),
            'dataset': (EFS_DB_COMPONENTS['dataset_catalog'], 'id'),
            'feature_version': (EFS_DB_COMPONENTS['feature_version'], 'feature_version'),
            'ds_entity': (EFS_DB_COMPONENTS['feature_version'], 'entity_id'),
        }
        
        table_name, column_name = table_column_mapping[type_]
        # For group_features, use group_data_domain to fetch the data domain
        domain_column = 'group_data_domain' if type_ == 'group_features' else 'data_domain'
        
        return f'SELECT {domain_column} FROM "{{repo}}".{table_name} WHERE {column_name} = \'{{object}}\''

    @staticmethod
    def _get_data_domains(repo, name, type_):
        """
        DESCRIPTION:
            Get the data domains where an object exists within the specified repository.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the repository name.
                Types: str

            name:
                Required Argument.
                Specifies the name of the object to retrieve information for.
                Types: str

            type_:
                Required Argument.
                Specifies the type of object to query.
                Permitted Values: 'feature', 'entity', 'data_source', 'feature_group', 
                                  'group_features', 'feature_process', 'dataset', 'feature_version',
                                  'ds_entity'
                Types: str

        Returns:
            list: A list of data domains where the object exists.
                  If the object does not exist, an empty list is returned.

        EXAMPLE:
            >>> from teradataml.store.feature_store.utils import _FSUtils
            >>> available_domains = _FSUtils._get_data_domains('my_repo', 'feature1', 'feature')
            >>> print(available_domains)
            ['finance', 'marketing']
        """
        # Get SQL query template for the specified type
        sql_template = _FSUtils._get_sql_query_for_type(type_)

        # Format the SQL query with repo and object
        sql = sql_template.format(repo=repo, object=name)

        res = execute_sql(sql).fetchall()
        if not res: # Return empty list if no results found
            return []
        
        # Get the data domains from the result set.
        available_domains = list(set(rec[0] for rec in res))
        return available_domains
