"""
Copyright (c) 2024 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements constants required for Teradata Enterprise Feature Store.
"""

from teradatasqlalchemy.types import *
from enum import Enum

# Template for creating the triggers on
# corresponding tables.

# Tables for storing the data domains.
EFS_DATA_DOMAINS="""
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        created_time TIMESTAMP(6)
        )
    UNIQUE PRIMARY INDEX (name);
"""


# Tables for storing the features.
EFS_FEATURES = """
    CREATE MULTISET TABLE {0}.{1}
        (
        id INTEGER,
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        column_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        tags VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_type VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_type VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        status VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES _efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain)
    UNIQUE INDEX (id);
"""

EFS_FEATURES_STAGING="""
    CREATE MULTISET TABLE {0}.{1}
        (
        id INTEGER,
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        column_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        tags VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_type VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_type VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        status VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6)
        )
    NO PRIMARY INDEX ;
"""

EFS_FEATURES_TRG="""
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.id, DeletedRow.name, DeletedRow.data_domain, DeletedRow.column_name, DeletedRow.description, DeletedRow.tags, DeletedRow.data_type, DeletedRow.feature_type, DeletedRow.status, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

EFS_GROUP_FEATURES = """
    CREATE MULTISET TABLE {0}.{1}
        (
        feature_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        group_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        group_data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),	
    CONSTRAINT feature_name_fk FOREIGN KEY (feature_name, feature_data_domain) REFERENCES {0}._efs_features (name, data_domain),
    CONSTRAINT group_name_fk FOREIGN KEY (group_name, group_data_domain) REFERENCES {0}._efs_feature_group (name, data_domain),
    CONSTRAINT data_domain_fk1 FOREIGN KEY (feature_data_domain) REFERENCES {0}._efs_data_domains (name),
    CONSTRAINT data_domain_fk2 FOREIGN KEY (group_data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (feature_name, feature_data_domain, group_name, group_data_domain);
"""

EFS_GROUP_FEATURES_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        feature_name VARCHAR(255),
        feature_data_domain VARCHAR(255),
        group_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        group_data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6)
        )
    NO PRIMARY INDEX ;  
"""

EFS_GROUP_FEATURES_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.feature_name, DeletedRow.feature_data_domain, DeletedRow.group_name, DeletedRow.group_data_domain, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );   
"""  

# Tables for Entities.

EFS_ENTITY = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain);
"""

EFS_ENTITY_STAGING= """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,      
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6))
    NO PRIMARY INDEX ;
"""

EFS_ENTITY_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.name, DeletedRow.data_domain, DeletedRow.description, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

EFS_ENTITY_XREF= """
    CREATE MULTISET TABLE {0}.{1}
        (
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC, 
        entity_column VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC, 
    CONSTRAINT entity_xref_fk FOREIGN KEY (entity_name, data_domain) REFERENCES {0}._efs_entity (name, data_domain),
    CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (entity_name, data_domain, entity_column);
"""

EFS_ENTITY_XREF_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_column VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,      
        archived_time TIMESTAMP(6)
        )
    NO PRIMARY INDEX ;
"""

EFS_ENTITY_XREF_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.entity_name, DeletedRow.data_domain, DeletedRow.entity_column, 
                current_timestamp(6)
                );       
"""

# Table for Data sources.

EFS_DATA_SOURCE = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        timestamp_column VARCHAR(50) CHARACTER SET LATIN NOT CASESPECIFIC,
        source VARCHAR(5000) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain);
"""

EFS_DATA_SOURCE_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        timestamp_column VARCHAR(50) CHARACTER SET LATIN NOT CASESPECIFIC,
        source VARCHAR(5000) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6))
    NO PRIMARY INDEX;
"""

EFS_DATA_SOURCE_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.name, DeletedRow.data_domain, DeletedRow.description, DeletedRow.timestamp_column, DeletedRow.source, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

# Table for Feature groups.

EFS_FEATURE_GROUP = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,      
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_source_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6), 
    CONSTRAINT data_source_name_fk FOREIGN KEY (data_source_name, data_domain) REFERENCES {0}._efs_data_source (name, data_domain),
    CONSTRAINT entity_fk FOREIGN KEY (entity_name, data_domain) REFERENCES {0}._efs_entity (name, data_domain),
    CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain);
"""

EFS_FEATURE_GROUP_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,      
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_source_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6))
    NO PRIMARY INDEX ;
"""

EFS_FEATURE_GROUP_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.name, DeletedRow.data_domain, DeletedRow.description, DeletedRow.data_source_name, DeletedRow.entity_name, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

# Table for feature process.
EFS_FEATURE_PROCESS = """
    CREATE MULTISET TABLE {0}.{1}
        (
        process_id VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        process_type VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_source VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_id VARCHAR(255) CHARACTER SET LATIN CASESPECIFIC,
        feature_names VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC,
        feature_ids VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (process_id);
"""


EFS_FEATURE_RUNS = """
CREATE MULTISET TABLE {0}.{1}
        (
        run_id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1 MINVALUE 1 NO MAXVALUE NO CYCLE) NOT NULL,
        process_id VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        start_time TIMESTAMP(6),
        end_time TIMESTAMP(6),
        status VARCHAR(20) CHARACTER SET LATIN NOT CASESPECIFIC,
        filter VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        as_of_start TIMESTAMP(6) WITH TIME ZONE,
        as_of_end TIMESTAMP(6) WITH TIME ZONE,
        failure_reason VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC)
    UNIQUE PRIMARY INDEX (run_id);
"""

# Table for storing the features metadata.
EFS_FEATURES_METADATA = """
    CREATE MULTISET TABLE {0}.{1}
        (
        entity_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_id BIGINT NOT NULL,
        table_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (entity_name);
"""

EFS_DATASET_CATALOG = """
    CREATE MULTISET TABLE {0}.{1}
        (
        id VARCHAR(36) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        entity_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        database_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        description VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (id);
"""

EFS_DATASET_FEATURES = """
    CREATE MULTISET TABLE {0}.{1}
        (
        dataset_id VARCHAR(36) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_id BIGINT,
        feature_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        feature_version VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        feature_repo VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        feature_view VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (dataset_id);
"""

EFS_FEATURE_VERSION = """
CREATE VIEW {}.{} AS 
LOCK ROW FOR ACCESS
SELECT
    data_domain,
    entity_id,        
    trim(NGRAM) AS feature_name,
    PROCESS_ID as feature_version
FROM NGramSplitter (
    ON (
        SELECT * FROM {}.{}
        ) as paragraphs_input
        USING
            TextColumn ('FEATURE_NAMES')
            ConvertToLowerCase ('false')
            Grams ('1')
            Delimiter(',')
    ) AS dt; 
"""

# Select the archived records.
EFS_ARCHIVED_RECORDS = """
SELECT {}, 
CASE WHEN valid_end < current_timestamp then 1 else 0 end as is_archived 
FROM {} 
WHERE {}"""

# Table to store the version of feature store. This is very important.
# When teradataml incrementally adds functionality for feature store, this
# version will be deciding factor whether teradataml should automatically
# update metadata or not.

EFS_VERSION = """
    CREATE MULTISET TABLE {0}.{1} (
        version VARCHAR(20) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6)
    );
"""

EFS_VERSION_ = "2.0.0"

EFS_DB_COMPONENTS = {
    "data_domain": "_efs_data_domains",
    "feature": "_efs_features",
    "feature_staging": "_efs_features_staging",
    "feature_trg": "_efs_features_trg",
    "group_features": "_efs_group_features",
    "group_features_staging": "_efs_group_features_staging",
    "group_features_trg": "_efs_group_features_trg",
    "entity": "_efs_entity",
    "entity_staging": "_efs_entity_staging",
    "entity_trg": "_efs_entity_trg",
    "entity_xref": "_efs_entity_xref",
    "entity_staging_xref": "_efs_entity_xref_staging",
    "entity_xref_trg": "_efs_entity_xref_trg",
    "data_source": "_efs_data_source",
    "data_source_staging": "_efs_data_source_staging",
    "data_source_trg": "_efs_data_source_trg",
    "feature_group": "_efs_feature_group",
    "feature_group_staging": "_efs_feature_group_staging",
    "feature_group_trg": "_efs_feature_group_trg",
    "feature_process": "_efs_feature_process",
    "feature_runs": "_efs_feature_runs",
    "feature_metadata": "_efs_features_metadata",
    "dataset_catalog": "_efs_dataset_catalog",
    "dataset_features": "_efs_dataset_features",
    "feature_version": "_efs_feature_version",
    "version": "_efs_version"
}


EFS_TABLES = {
    EFS_DATA_DOMAINS: "_efs_data_domains",
    EFS_FEATURES: "_efs_features",
    EFS_FEATURES_STAGING: "_efs_features_staging",
    EFS_GROUP_FEATURES: "_efs_group_features",
    EFS_GROUP_FEATURES_STAGING: "_efs_group_features_staging",
    EFS_ENTITY: "_efs_entity",
    EFS_ENTITY_STAGING: "_efs_entity_staging",
    EFS_ENTITY_XREF: "_efs_entity_xref",
    EFS_ENTITY_XREF_STAGING: "_efs_entity_xref_staging",
    EFS_DATA_SOURCE: "_efs_data_source",
    EFS_DATA_SOURCE_STAGING: "_efs_data_source_staging",
    EFS_FEATURE_GROUP: "_efs_feature_group",
    EFS_FEATURE_RUNS: "_efs_feature_runs",
    EFS_FEATURE_GROUP_STAGING: "_efs_feature_group_staging",
    EFS_FEATURE_PROCESS: "_efs_feature_process",
    EFS_FEATURES_METADATA: "_efs_features_metadata",
    EFS_DATASET_CATALOG: "_efs_dataset_catalog",
    EFS_DATASET_FEATURES: "_efs_dataset_features",
    EFS_VERSION: "_efs_version"
}

EFS_TRIGGERS = {
    EFS_FEATURES_TRG: "_efs_features_trg",
    EFS_GROUP_FEATURES_TRG: "_efs_group_features_trg",
    EFS_ENTITY_TRG: "_efs_entity_trg",
    EFS_ENTITY_XREF_TRG: "_efs_entity_xref_trg",
    EFS_DATA_SOURCE_TRG: "_efs_data_source_trg",
    EFS_FEATURE_GROUP_TRG: "_efs_feature_group_trg"
}

class FeatureStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2


class FeatureType(Enum):
    CONTINUOUS = 1
    CATEGORICAL = 2
    NUMERICAL = 3

class ProcessType(Enum):
    DENORMALIZED_VIEW = 'denormalized view'
    FEATURE_GROUP = 'feature group'
    NEW = 'new'
    EXISTING = 'existing'


class ProcessStatus(Enum):
    NOT_STARTED = 'not started'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


class _FeatureStoreDFContainer:
    """
    Utility class for FeatureStore DataFrame operations.
    
    This class provides static methods for creating and managing DataFrames
    used across different FeatureStore components, eliminating code duplication
    and providing a centralized, efficient approach to DataFrame handling.
    """
    __df_container = {}

    @staticmethod
    def get_df(obj_type, repo, data_domain):
        """
        DESCRIPTION:
            Generic static method to create and manage DataFrames for different object types
            in FeatureStore. Handles joins and special object type processing.

        PARAMETERS:
            obj_type:
                Required Argument.
                Specifies the type of DataFrame to return.
                Supported types: 'feature', 'feature_staging', 'entity', 'entity_staging',
                'feature_wog', 'feature_info', 'feature_catalog', 'entity_info', and all
                other types defined in EFS_DB_COMPONENTS.
                Types: str

            repo:
                Required Argument.
                Specifies the repository name.
                Types: str

            data_domain:
                Required Argument.
                Specifies the data domain for filtering operations.
                Types: str

        RETURNS:
            teradataml DataFrame.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> # Basic DataFrame retrieval
            >>> df = _FeatureStoreDFContainer.get_df(
            ...     obj_type='feature',
            ...     repo='my_repo',
            ...     data_domain='analytics'
            ... )
            
            >>> # Complex join for feature info
            >>> df = _FeatureStoreDFContainer.get_df(
            ...     obj_type='feature_info',
            ...     repo='my_repo',
            ...     data_domain='analytics'
            ... )
        """
        from teradataml.dataframe.dataframe import DataFrame, in_schema
        repo_obj = repo + '.' + data_domain + '.' + obj_type

        if repo_obj not in _FeatureStoreDFContainer.__df_container:

            # Handle complex FeatureStore-specific patterns with joins
            if obj_type in ["feature", "feature_staging"]:
                # Join features with group_features for group name
                map_ = {"feature": "group_features", "feature_staging": "group_features_staging"}
                features = DataFrame(in_schema(repo, EFS_DB_COMPONENTS[obj_type]))
                features_xref = DataFrame(in_schema(repo, EFS_DB_COMPONENTS[map_[obj_type]]))
                features = features[features.data_domain == data_domain]
                features_xref = features_xref[features_xref.feature_data_domain == data_domain].select(["feature_name", "group_name"])
                df = features.join(features_xref, on=["name==feature_name"], how='left')
                _FeatureStoreDFContainer.__df_container[repo_obj] = df.select(features.columns + ["group_name"])

            elif obj_type in ["entity", "entity_staging"]:
                # Join entity with entity_xref for entity columns
                ent_df = DataFrame(in_schema(repo, EFS_DB_COMPONENTS[obj_type]))
                xref_df = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["{}_xref".format(obj_type)]))
                ent_df = ent_df[ent_df.data_domain == data_domain]
                xref_df = xref_df[xref_df.data_domain == data_domain].select(['entity_name', 'entity_column'])
                df = ent_df.join(xref_df, on=["name==entity_name"], how="inner")
                _FeatureStoreDFContainer.__df_container[repo_obj] = df.select(ent_df.columns + ["entity_column"])

            elif obj_type == "feature_wog":
                # Feature without group - direct access to feature table
                _FeatureStoreDFContainer.__df_container[repo_obj] = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["feature"]))

            elif obj_type == "feature_info":
                # join: features + metadata
                # Use feature_wog (without group)
                feature = _FeatureStoreDFContainer.get_df('feature_wog', repo, data_domain)

                # Get metadata DataFrame
                feature_metadata = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["feature_metadata"]))
                
                # Drop ValidPeriod column if it exists
                if 'ValidPeriod' in feature_metadata.columns:
                    feature_metadata = feature_metadata.drop(columns=["ValidPeriod"])

                df = feature_metadata.join(feature,
                                           how="inner",
                                           on=[feature_metadata.feature_id == feature.id,
                                               feature_metadata.data_domain == feature.data_domain,
                                               feature_metadata.data_domain == data_domain],
                                           lsuffix="_meta",
                                           rsuffix="_feat")
                _FeatureStoreDFContainer.__df_container[repo_obj] = df

            elif obj_type == "feature_catalog":
                # join: features + metadata + version
                # Get the required DataFrames directly
                fv = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["feature_version"]))
                f_ = _FeatureStoreDFContainer.get_df("feature", repo, data_domain)

                # Feature can be mapped to more than one feature group. So, 'f_' can have duplicate rows
                # which propagates these duplicates to final result.
                f_ = f_.drop_duplicate(['id', 'data_domain', 'name'])
                fm = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["feature_metadata"]))

                ndf = fm.select(['entity_name', 'data_domain', 'feature_id', 'table_name', 'valid_end'])
                hdf = ndf.join(
                    f_, on=((f_.id == ndf.feature_id) & (ndf.data_domain == f_.data_domain)),
                    how='inner',
                    lprefix='l'
                ).select(['entity_name', 'data_domain', 'id', 'name', 'table_name', 'valid_end'])

                vdf = hdf.join(fv,
                               on=(
                                       (hdf.data_domain == fv.data_domain) &
                                       (hdf.entity_name == fv.entity_id) &
                                       (fv.feature_name == hdf.name) &
                                       (fv.data_domain == data_domain)
                               ),
                               how='inner',
                               lprefix='l'
                               )

                _FeatureStoreDFContainer.__df_container[repo_obj] = vdf.select(
                    ['entity_id', 'data_domain', 'id', 'name', 'table_name', 'feature_version', 'valid_end']
                )
                
            elif obj_type == "entity_info":
                # join: entity + entity_xref
                entity_df = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["entity"]))
                entity_xref_df = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["entity_xref"]))

                # Build join conditions
                join_conditions = [
                    entity_df.name == entity_xref_df.entity_name,
                    entity_df.data_domain == entity_xref_df.data_domain,
                    entity_df.data_domain == data_domain
                ]
                
                df = entity_df.join(
                    other=entity_xref_df,
                    on=join_conditions,
                    lsuffix="l"
                )

                _FeatureStoreDFContainer.__df_container[repo_obj] = df.select(
                    ['entity_name', 'data_domain', 'entity_column', 'description']
                )

            elif obj_type == 'data_domain':
                _FeatureStoreDFContainer.__df_container[repo_obj] = DataFrame(in_schema(repo, EFS_DB_COMPONENTS["data_domain"]))

            # Default case: simple DataFrame creation
            else:
                df = DataFrame(in_schema(repo, EFS_DB_COMPONENTS[obj_type]))
                if 'data_domain' in df.columns:
                    df = df[df.data_domain == data_domain]
                
                _FeatureStoreDFContainer.__df_container[repo_obj] = df

        return _FeatureStoreDFContainer.__df_container[repo_obj]