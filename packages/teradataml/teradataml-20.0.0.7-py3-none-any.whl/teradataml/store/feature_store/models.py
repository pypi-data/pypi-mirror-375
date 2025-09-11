"""
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements the models required for Teradata Enterprise Feature Store.
"""

import inspect
import uuid
from collections import OrderedDict, namedtuple
from datetime import datetime as dt
from datetime import timezone
from sqlalchemy import literal_column
from teradatasqlalchemy import types as tdtypes
from teradatasqlalchemy.types import *

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.sqlbundle import SQLBundle
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import _get_current_databasename
from teradataml.dataframe.dataframe import DataFrame, in_schema
from teradataml.dataframe.sql import ColumnExpression, _SQLColumnExpression
from teradataml.dbutils.dbutils import (_create_temporal_table, _delete_data,
                                        _insert_data, _merge_data,
                                        _update_data, _upsert_data,
                                        db_list_tables, db_transaction,
                                        execute_sql, db_drop_table, db_drop_view, _get_quoted_object_name)
from teradataml.store.feature_store.constants import *
from teradataml.store.feature_store.constants import _FeatureStoreDFContainer
from teradataml.store.feature_store.utils import _FSUtils
from teradataml.utils.validators import _Validators
from teradataml.utils.dtypes import _Dtypes, _ListOf


class Feature:
    """Class for Feature. """
    def __init__(self,
                 name,
                 column,
                 feature_type=FeatureType.CONTINUOUS,
                 description=None,
                 tags=None,
                 status=FeatureStatus.ACTIVE):
        """
        DESCRIPTION:
            Constructor for Feature.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the Feature.
                Types: str.

            column:
                Required Argument.
                Specifies the DataFrame Column.
                Types: teradataml DataFrame Column

            feature_type:
                Optional Argument.
                Specifies whether feature is continuous or discrete.
                Default Value: FeatureType.CONTINUOUS
                Types: FeatureType Enum

            description:
                Optional Argument.
                Specifies human readable description for Feature.
                Types: str

            tags:
                Optional Argument.
                Specifies the tags for Feature.
                Types: str OR list of str

            status:
                Optional Argument.
                Specifies whether feature is archived or active.
                Types: FeatureStatus Enum

        RETURNS:
            None.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, Feature, FeatureType, load_example_data, FeatureStatus
            # Load the sales data to Vantage.
            >>> load_example_data("dataframe", "sales")
            # Create DataFrame on sales data.
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017

            # Example 1: Create a Categorical Feature for column 'Feb' for 'sales' DataFrame
            # create a Categorical Feature for column 'Feb' for 'sales' DataFrame and name it as
            # 'sales_Feb'.
            >>> from teradataml import Feature
            >>> feature = Feature('sales_Feb', column=df.Feb, 
            ...                   feature_type=FeatureType.CATEGORICAL, status=FeatureStatus.ACTIVE)
            >>> feature
            Feature(name=sales_Feb)

            # Example 2: Create a Continuous Feature for column 'Jan' for 'sales' DataFrame
            # create a Continuous Feature for column 'Jan' for 'sales' DataFrame and name it as
            # 'sales_Jan'.
            >>> feature = Feature('sales_Jan', column='Jan',
            ...                   feature_type=FeatureType.CONTINUOUS, status=FeatureStatus.ACTIVE)
            >>> feature
            Feature(name=sales_Jan)
        """
        argument_validation_params = []
        argument_validation_params.append(['name', name, False, str, True])
        argument_validation_params.append(['column', column, False, ColumnExpression, True])
        argument_validation_params.append(['feature_type', feature_type, True, FeatureType, True])
        argument_validation_params.append(['description', description, True, str, True])
        argument_validation_params.append(['tags', tags, True, (str, list), True])
        argument_validation_params.append(['status', status, True, FeatureStatus, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        self.name = name
        self.column_name = column.name
        self.description = description
        self.tags = UtilFuncs._as_list(tags) if tags else None
        self.data_type = column.type
        self.feature_type = feature_type
        self.status = status
        self.id = None

    @classmethod
    def _from_df(cls, df):
        """
        DESCRIPTION:
            Internal method to create object of Feature from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has Feature details.
                Types: teradataml DataFrame.

        RETURNS:
            Feature or list of Feature.

        RAISES:
            None

        EXAMPLES:
            >>> Feature._from_df(df)
        """
        _features = []
        recs = [rec._asdict() for rec in df.itertuples()]

        for rec in recs:
            # Pop out unnecessary details.
            rec.pop("creation_time")
            rec.pop("modified_time")
            rec.pop("group_name", None)
            rec.pop("data_domain")
            id = rec.pop("id")
            rec["column"] = _SQLColumnExpression(rec.pop("column_name"),
                                                 type=getattr(tdtypes, rec.pop("data_type"))())
            rec["feature_type"] = FeatureType.CONTINUOUS if rec["feature_type"] == FeatureType.CONTINUOUS.name \
                else FeatureType.CATEGORICAL
            rec["status"] = FeatureStatus.ACTIVE if rec["status"] == FeatureStatus.ACTIVE.name else FeatureStatus.INACTIVE
            feature = cls(**rec)
            feature.id = id
            _features.append(feature)

        return _features if len(_features) > 1 else _features[0]
    
    @classmethod
    def _from_row(cls, row):
        """
        DESCRIPTION:
            Internal method to create object of Feature from a row.

        PARAMETERS:
            row:
                Required Argument.
                Specifies a row containing Feature details.
                Types: teradataml DataFrame Row.

        RETURNS:
            Feature

        RAISES:
            None

        EXAMPLES:
            >>> Feature._from_row(row)
        """
        return cls(name=row.name,
                   column=_SQLColumnExpression(row.column_name, type=getattr(tdtypes, row.data_type)()),
                   feature_type=FeatureType[row.feature_type],
                   description=row.description,
                   tags=row.tags.split(",") if row.tags else None,
                   status=FeatureStatus[row.status])

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for Feature object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import Feature, load_example_data
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")


            # Example 1: Create a Feature and get it's string representation.
            >>> feature = Feature('sales_Feb', column=df.Feb,
            ...                   feature_type=FeatureType.CATEGORICAL, status=FeatureStatus.ACTIVE)
            >>> feature
            Feature(name=sales_Feb)
        """
        return "Feature(name={name})".format(name=self.name)

    def __get_max_id(self, repo):
        """
        DESCRIPTION:
            Internal method to get the max id from Feature table.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to get the max id.
                Types: str.

        RETURNS:
            int

        RAISES:
            None

        EXAMPLES:
            >>> feature.__get_max_id('vfs_v1')
            10
        """
        feature_table = _get_quoted_object_name(schema_name=repo, 
                                                object_name=EFS_DB_COMPONENTS['feature'])
        query = "SELECT MAX(id) FROM {}".format(feature_table)
        c = execute_sql(query)
        # Note: Max will always return a single record even if table does
        # not have any records. If not records, it returns `[None]`.
        max_id = next(c)[0]
        if max_id is None:
            # If no records, return 0.
            return 0
        return max_id

    def publish(self, repo, data_domain):
        """
        DESCRIPTION:
            Method to publish the Feature details to repository.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the Feature details.
                Types: str.
            
            data_domain:
                Required Argument.
                Specifies the data domain of the Feature.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create a FeatureStore repo 'vfs_v1'.
            fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore.
            >>> fs.setup()

            # Example 1: Publish the Feature details to repo 'vfs_v1' for column
            #            'Feb' from 'sales' DataFrame.
            >>> from teradataml import Feature
            >>> feature = Feature('sales:Feb', df.Feb)
            >>> feature.publish('vfs_v1', data_domain='sales')
            True

            # Example 2: Republish the Feature published in Example 1 by updating
            #            it's tags.
            # First, Get the existing Feature.
            >>> feature = fs.get_feature('sales:Feb')
            >>> feature
            Feature(name=sales:Feb)

            # Update it's tags.
            >>> feature.tags = ["sales_data", "monthly_sales"]
            # Republish the details to same repo.
            >>> feature.publish('vfs_v1', data_domain='sales')
            True

            # Validate the tags.
            >>> feature.tags
            ['sales_data', 'monthly_sales']
        """
        argument_validation_params = []
        argument_validation_params.append(['repo', repo, False, str, True])
        argument_validation_params.append(['data_domain', data_domain, False, str, True])

        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Get the value for id from table.
        id = self.__get_max_id(repo) + 1

        _upsert_data(schema_name=repo,
                     table_name=EFS_DB_COMPONENTS['feature'],
                     insert_columns_values = OrderedDict({
                         'name': self.name,
                         'column_name': self.column_name,
                         'description': self.description,
                         'creation_time': dt.utcnow(),
                         'tags': ", ".join(self.tags) if self.tags else None,
                         'data_type': type(self.data_type).__name__,
                         'feature_type': self.feature_type.name,
                         'status': self.status.name,
                         'data_domain': data_domain,
                         'id': id}),
                     upsert_conditions=OrderedDict({
                         'name': self.name,
                         'data_domain': data_domain}),
                     update_columns_values=OrderedDict({
                         'column_name': self.column_name,
                         'description': self.description,
                         'modified_time': dt.utcnow(),
                         'tags': ", ".join(self.tags) if self.tags else None,
                         'data_type': type(self.data_type).__name__,
                         'feature_type': self.feature_type.name,
                         'status': self.status.name})
                     )
        return True

class Entity:
    """Class for Entity. """
    def __init__(self, name, columns, description=None):
        """
        DESCRIPTION:
            Constructor for creating Entity Object.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the entity.
                Types: str.

            columns:
                Required Argument.
                Specifies the names of the columns.
                Types: teradataml DataFrame Column OR str OR list of teradataml DataFrame Columns, str.

            description:
                Optional Argument.
                Specifies human readable description for Feature.
                Types: str

        RETURNS:
            Object of Entity.

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create a Entity for above mentioned DataFrame with name 'sales_accounts'.
            # create a Entity with column 'accounts' for 'sales' DataFrame and name it as
            # 'sales_accounts'.
            >>> from teradataml import Entity
            >>> entity = Entity('sales_accounts', df.accounts)
            >>> entity
            Entity(name=sales_accounts)

            # Example 2: Create a Entity with column name 'accounts'.
            >>> entity = Entity('sales_accounts', 'accounts')
            >>> entity
            Entity(name=sales_accounts)

            # Example 3: Create a Entity with multiple columns.
            >>> entity = Entity('sales_cols', ['accounts', 'jan'])
            >>> entity
            Entity(name=sales_cols)
        """
        argument_validation_params = []
        argument_validation_params.append(['name', name, False, str, True])
        argument_validation_params.append(['columns', columns, False, (ColumnExpression, str, list), True])
        argument_validation_params.append(['description', description, True, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        self.name = name
        self.columns = UtilFuncs._get_normalize_and_deduplicate_columns(columns)
        self.description = description

    @classmethod
    def _from_df(cls, df):
        """
        DESCRIPTION:
            Internal method to create object of Entity from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has details for Entity.
                Types: teradataml DataFrame.

        RETURNS:
            Entity

        RAISES:
            None

        EXAMPLES:
            >>> Entity._from_df(df)
        """
        entity_name = None
        description = None
        columns = []

        # Get all the entity columns and update there.
        for rec in df.itertuples():
            entity_name = rec.name
            description = rec.description
            columns.append(rec.entity_column)

        return cls(name=entity_name, description=description, columns=columns)
    
    @classmethod
    def _from_row(cls, row):
        """
        DESCRIPTION:
            Internal method to create object of Entity from a row.

        PARAMETERS:
            row:
                Required Argument.
                Specifies a row containing Entity details.
                Types: teradataml DataFrame Row.

        RETURNS:
            Entity

        RAISES:
            None

        EXAMPLES:
            >>> Entity._from_row(row)
        """
        return cls(name=row.entity_name,
                   columns=row.entity_column,
                   description=row.description)


    def __repr__(self):
        """
        DESCRIPTION:
            String representation for Entity object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import Entity, load_example_data
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create a Entity and get it's string representation.
            >>> entity = Entity('sales_accounts', df.accounts)
            >>> entity
            Entity(name=sales_accounts)
        """
        return "Entity(name={})".format(self.name)

    @db_transaction
    def publish(self, repo, data_domain):
        """
        DESCRIPTION:
            Method to publish the Entity details to repository.
            Note:
                * If the Entity is already registered with same name, columns and description in the repository, it is not updated.
                * If the Entity is associated with any feature process, an error is raised while modifying Entity.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the Entity details.
                Types: str.
            
            data_domain:
                Required Argument.
                Specifies the data domain of the Entity.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create a FeatureStore repo 'vfs_v1'.
            fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore.
            >>> fs.setup()

            # Example 1: Publish the Entity details to repo 'vfs_v1' for column
            #            'accounts' from 'sales' DataFrame.
            >>> from teradataml import Entity
            >>> entity = Entity('sales:accounts', 'accounts')
            >>> entity.publish('vfs_v1', data_domain='sales')
            True
        """
        argument_validation_params = []
        argument_validation_params.append(['repo', repo, False, str, True])
        argument_validation_params.append(['data_domain', data_domain, False, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Check if Entity already exists in Feature Catalog. If yes, it should not be touched.
        entity_status = _FSUtils._is_entity_exists_in_fc(self.name, repo, data_domain, self.description, self.columns)
        
        # If same entity exists, no changes required.
        if entity_status == "exists":
            return True

        if entity_status == "modify":
            err_code = MessageCodes.EFS_OBJ_IN_FEATURE_PROCESS
            err_msg = Messages.get_message(err_code,
                                           'Entity',
                                           self.name,
                                           "Feature catalog",
                                           "Feature(s) associated with the entity",
                                           "FeatureCatalog.archive_features() & FeatureCatalog.delete_features()"
                                           )
            raise TeradataMlException(err_msg, err_code)

        # Upsert should be triggered for every corresponding entity ID and column.
        _upsert_data(schema_name=repo,
                     table_name=EFS_DB_COMPONENTS['entity'],
                     insert_columns_values=OrderedDict({
                         'name': self.name,
                         'description': self.description,
                         'creation_time': dt.utcnow(),
                         'data_domain': data_domain}),
                     upsert_conditions=OrderedDict({
                         'name': self.name,
                         'data_domain': data_domain}),
                     update_columns_values=OrderedDict({
                         'description': self.description,
                         'modified_time': dt.utcnow()})
                     )

        # Insert into xref table now. Before that, delete for that key.
        _delete_data(schema_name=repo,
                     table_name=EFS_DB_COMPONENTS['entity_xref'],
                     delete_conditions=(_SQLColumnExpression("entity_name")==self.name) &
                                       ( _SQLColumnExpression("data_domain")==data_domain))

        values = [(self.name, data_domain, col) for col in self.columns]
        # Insert into xref table.
        _insert_data(EFS_DB_COMPONENTS['entity_xref'], values, schema_name=repo)

        return True

    def __eq__(self, other):
        """
        Compare the Entity with other Entity to check if both are
        same or not.

        PARAMETERS:
            other :
                Required Argument.
                Specifies another Entity.
                Types: Entity

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create two entities and compare whether they are same or not.
            >>> from teradataml import Entity
            >>> entity1 = Entity('sales:accounts', 'accounts')
            >>> entity2 = Entity('sales:accounts', 'accounts')
            >>> entity1 == entity2
            True
            >>>
        """
        if not isinstance(other, Entity):
            return False
        # Both entities will be same only when corresponding columns are same.
        return set(self.columns) == set(other.columns)


class DataSource:
    """Class for DataSource. """
    def __init__(self, name, source, description=None, timestamp_column=None):
        """
        DESCRIPTION:
            Constructor for creating DataSource Object.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the DataSource.
                Types: str.

            source:
                Required Argument.
                Specifies the source query of DataSource.
                Types: str OR teradataml DataFrame.

            description:
                Optional Argument.
                Specifies human readable description for DataSource.
                Types: str

            timestamp_column:
                Optional Argument.
                Specifies the timestamp column indicating when the row was created.
                Types: str OR teradataml DataFrame Column

        RETURNS:
            Object of DataSource.

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create a DataSource for above mentioned DataFrame with name 'Sales_Data'.
            >>> from teradataml import DataSource
            >>> data_source = DataSource('Sales_Data', df)
            >>> data_source
            DataSource(Sales_Data)

            # Example 2: Create a DataSource with source query.
            >>> data_source = DataSource('Sales_Data_Query', source="SELECT * FROM sales")
            >>> data_source
            DataSource(Sales_Data_Query)
        """
        argument_validation_params = []
        argument_validation_params.append(['name', name, False, str, True])
        argument_validation_params.append(['source', source, False, (str, DataFrame), True])
        argument_validation_params.append(['description', description, True, str, True])
        argument_validation_params.append(['timestamp_column', timestamp_column, True, (str, ColumnExpression), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        self.name = name
        if isinstance(timestamp_column, ColumnExpression):
            timestamp_column = timestamp_column.name
        self.timestamp_column = timestamp_column
        self.source = source if isinstance(source, str) else source.show_query()
        self.description = description

    @classmethod
    def _from_df(cls, df):
        """
        DESCRIPTION:
            Internal method to create object of DataSource from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has a single
                record denoting DataSource.
                Types: teradataml DataFrame.

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> DataSource._from_df(df)
        """
        rec = next(df.itertuples())._asdict()
        rec.pop("creation_time")
        rec.pop("modified_time")
        rec.pop("data_domain")
        return cls(**(rec))

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for DataSource object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, load_example_data
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create a DataSource and get it's string representation.
            >>> DataSource('Sales_Data', df)
            DataSource(name=Sales_Data)
        """
        return "DataSource(name={})".format(self.name)

    def publish(self, repo, data_domain):
        """
        DESCRIPTION:
            Method to publish the DataSource details to repository.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the DataSource details.
                Types: str.

            data_domain:
                Required Argument.
                Specifies the data domain of the DataSource.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create a FeatureStore repo 'vfs_v1'.
            fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore.
            >>> fs.setup()

            # Example 1: Publish the above mentioned DataFrame as DataSource
            #            and name it as "Sales_Data".
            >>> from teradataml import DataSource
            >>> data_source = DataSource('Sales_Data', df)
            >>> data_source.publish('vfs_v1', data_domain='sales')
            True

            # Example 2: Republish the published DataSource in example 1 with
            #            updated description.
            # First, Get the existing DataSource.
            >>> from teradataml import FeatureStore
            >>> data_source = fs.get_data_source('Sales_Data')

            # Update it's description.
            >>> data_source.description = "Pivoted sales data."

            # Republish the details to same repo.
            >>> data_source.publish('vfs_v1', data_domain='sales')
            True
        """
        argument_validation_params = []
        argument_validation_params.append(['repo', repo, False, str, True])
        argument_validation_params.append(['data_domain', data_domain, False, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        _upsert_data(schema_name=repo,
                     table_name=EFS_DB_COMPONENTS['data_source'],
                     insert_columns_values=OrderedDict({
                         'name': self.name,
                         'description': self.description,
                         'timestamp_column': self.timestamp_column,
                         'source': self.source,
                         'creation_time': dt.utcnow(),
                         'data_domain': data_domain
                     }),
                     upsert_conditions={"name": self.name,
                                        "data_domain": data_domain},
                     update_columns_values=OrderedDict({
                         'description': self.description,
                         'timestamp_column': self.timestamp_column,
                         'modified_time': dt.utcnow(),
                         'source': self.source})
                     )
        return True


class FeatureGroup:
    """Class for FeatureGroup. """
    def __init__(self, name, features, entity, data_source, description=None):
        """
        DESCRIPTION:
            Constructor for creating FeatureGroup Object.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the unique name of the FeatureGroup.
                Types: str.

            features:
                Required Argument.
                Specifies the features required to create a group.
                Types: Feature or list of Feature.

            entity:
                Required Argument.
                Specifies the entity associated with corresponding features.
                Types: Entity

            data_source:
                Required Argument.
                Specifies the DataSource associated with Features.
                Types: DataSource

            description:
                Optional Argument.
                Specifies human readable description for DataSource.
                Types: str

        RETURNS:
            Object of FeatureGroup.

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create a FeatureGroup for above mentioned DataFrame.
            # First create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Feb", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Apr", df.Apr)

            # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)

            # Create DataSource.
            >>> data_source = DataSource("sales_source", df.show_query())

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature, apr_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)
            >>> fg
            FeatureGroup(name=Sales, features=[Feature(name=sales:Jan), Feature(name=sales:Feb), Feature(name=sales:Mar), Feature(name=sales:Apr)], entity=Entity(name=sales:accounts), data_source=DataSource(Sales_Data))
        """
        argument_validation_params = []
        argument_validation_params.append(['name', name, False, str, True])
        argument_validation_params.append(['features', features, False, (Feature, list), True])
        argument_validation_params.append(['entity', entity, False, Entity, True])
        argument_validation_params.append(['data_source', data_source, False, DataSource, True])
        argument_validation_params.append(['description', description, True, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        self.name = name
        self.features = UtilFuncs._as_list(features)
        self.entity = entity
        self.data_source = data_source
        self.description = description
        self.__redundant_features = []
        self._labels = []

    @property
    def features(self):
        """
        DESCRIPTION:
            Get's the features from FeatureGroup.

        PARAMETERS:
            None

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "sales")
            # Let's create DataFrame first.
            >>> df = DataFrame("sales")

            # create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Apr", df.Apr)

            # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)

            # Create DataSource.
            >>> data_source = DataSource("sales_source", df)

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature, apr_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Get the features from FeatureGroup.
            >>> fg.features
            [Feature(name=sales:Jan),
             Feature(name=sales:Feb),
             Feature(name=sales:Mar),
             Feature(name=sales:Apr)]
        """
        return [feature for feature in self._features if feature.name not in self._labels]

    @property
    def labels(self):
        """
        DESCRIPTION:
            Get's the labels from FeatureGroup.
            Note:
                Use this function only after setting the labels using "set_labels".

        PARAMETERS:
            None

        RETURNS:
            Feature OR list

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")

            # create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)

            # Create Entity.
            >>> entity = Entity("id", df.id)

            # Create DataSource.
            >>> data_source = DataSource("admissions_source", df)

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Set feature 'admitted' as label.
            >>> fg.set_labels('admitted')
            True

            # Get the labels from FeatureGroup
            >>> fg.labels
            Feature(name=admitted)
        """
        labels = [feature for feature in self._features if feature.name in self._labels]
        if len(labels) == 1:
            return labels[0]
        return labels

    @features.setter
    def features(self, features):
        """
        DESCRIPTION:
            Set the features for the FeatureGroup.

        PARAMETERS:
            features:
                Required Argument.
                Specifies the name(s) of the features to refer as features.
                Types: Feature or list of Feature

        RETURNS:
            bool

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "sales")

            # Let's create DataFrame first.
            >>> df = DataFrame("sales")

            # create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Apr", df.Apr)

            # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)

            # Create DataSource.
            >>> data_source = DataSource("sales_source", df)

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature, apr_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Set the features for FeatureGroup.
            >>> fg.features = [jan_feature, feb_feature]
            True

            # Get the features from FeatureGroup
            >>> fg.features
            [Feature(name=sales:Jan), Feature(name=sales:Feb)]
        """
        argument_validation_params = []
        argument_validation_params.append(['features', features, False, (Feature, list), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        self._features = UtilFuncs._as_list(features)
        return True

    def set_labels(self, labels):
        """
        DESCRIPTION:
            Sets the labels for FeatureGroup.
            This method is helpful, when working with analytic functions to consume the Features. 
            Note:
                Label is for the current session only.

        PARAMETERS:
            labels:
                Required Argument.
                Specifies the name(s) of the features to refer as labels.
                Types: str or list of str

        RETURNS:
            bool

        RAISES:
            ValueError

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")

            # create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)

            # Create Entity.
            >>> entity = Entity("id", df.id)

            # Create DataSource.
            >>> data_source = DataSource("admissions_source", df)

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Example 1: Set feature 'admitted' as label.
            # Set feature 'admitted' as label.
            >>> fg.set_labels('admitted')
            True

            # Get the labels from FeatureGroup.
            >>> fg.labels
            Feature(name=admitted)

            # Example 2: Set multiple features as labels.
            # Set features 'masters' and 'gpa' as labels.
            >>> fg.set_labels(['masters', 'gpa'])
            True

            # Get the labels from FeatureGroup.
            >>> fg.labels
            [Feature(name=masters), Feature(name=gpa)]
            
        """
        argument_validation_params = []
        argument_validation_params.append(['labels', labels, False, (str, list), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        
        # Validate that all labels exist in features
        if labels is not None:
            labels_list = UtilFuncs._as_list(labels)
            feature_names = [feature.name for feature in self._features]
            invalid_labels = [label for label in labels_list if label not in feature_names]
            
            if invalid_labels:
                raise ValueError(
                    Messages.get_message(MessageCodes.INVALID_ARG_VALUE).format(
                        invalid_labels, 'labels', feature_names
                    ))
        
        self._labels = [] if labels is None else UtilFuncs._as_list(labels)

        return True

    @labels.setter
    def labels(self, labels):
        """
        DESCRIPTION:
            Sets the labels for FeatureGroup.
            This method is helpful, when working with analytic functions to consume the Features.
            Note:
                Label is for the current session only.

        PARAMETERS:
            labels:
                Required Argument.
                Specifies the name(s) of the features to refer as labels.
                Types: str or list of str

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")

            # Create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)

            # Create Entity.
            >>> entity = Entity("id", df.id)

            # Create DataSource.
            >>> data_source = DataSource("admissions_source", df)

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Set feature 'admitted' as label.
            >>> fg.labels = 'admitted'
            True

            # Get the labels from FeatureGroup.
            >>> fg.labels
            Feature(name=admitted)
        """
        return self.set_labels(labels)

    def reset_labels(self):
        """
        DESCRIPTION:
            Resets the labels for FeatureGroup.

        PARAMETERS:
            None

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "admissions_train")
            # Let's create DataFrame first.
            >>> df = DataFrame("admissions_train")

            # create the features.
            >>> masters_feature = Feature("masters", df.masters)
            >>> gpa_feature = Feature("gpa", df.gpa)
            >>> stats_feature = Feature("stats", df.stats)
            >>> admitted_feature = Feature("admitted", df.admitted)

            # Create Entity.
            >>> entity = Entity("id", df.id)

            # Create DataSource.
            >>> data_source = DataSource("admissions_source", df)

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Admissions',
            ...                   features=[masters_feature, gpa_feature, stats_feature, admitted_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)
            # Set feature 'admitted' as label.
            >>> fg.set_labels('admitted')
            True

            # Remove the labels from FeatureGroup.
            >>> fg.reset_labels()
            True

            # Get the labels from FeatureGroup.
            >>> fg.labels
            []
        """
        self._labels = []
        return True

    def ingest_features(self, repo, data_domain=None):
        """
        DESCRIPTION:
            Ingests the features from feature group. Method considers associated DataSource 
            as data source for feature process and ingests the feature values in feature catalog.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to ingest the features.
                Types: str.

            data_domain:
                Optional Argument.
                Specifies the name of the data domain to ingest the features for.
                Note:
                    * If not specified, then default database name is considered as data domain.
                Types: str.

        RETURNS:
            Object of FeatureProcess.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore("vfs_test", data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Example 1: create a FeatureGroup 'sales_data_fg' for above mentioned
            #            DataFrame and publish it to 'vfs_v1'.
            # First create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Apr", df.Apr)

            >>> # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)
            
            # Create DataSource.
            >>> data_source = DataSource("sales_source", df.show_query())
            
            # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature, apr_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Ingest the features.
            >>> fp = fg.ingest_features()
            Process 'e04fd157-6c23-11f0-8bd4-f020ffe7fe09' started.
            Process 'e04fd157-6c23-11f0-8bd4-f020ffe7fe09' completed.
            >>> fp
            FeatureProcess(repo=vfs_v1, data_domain=sales, process_id=e04fd157-6c23-11f0-8bd4-f020ffe7fe09)
        """
        argument_validation_params = []
        argument_validation_params.append(['repo', repo, True, str, False])
        argument_validation_params.append(['data_domain', data_domain, True, str, False])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        data_domain = data_domain if data_domain is not None else _get_current_databasename()

        fp = FeatureProcess(
                repo=repo,
                data_domain=data_domain,
                object=self)
        fp.run()

        # Return the FeatureProcess object.
        return fp

    def apply(self, object):
        """
        DESCRIPTION:
            Register objects to FeatureGroup.

        PARAMETERS:
            object:
                Required Argument.
                Specifies the object to update the FeatureGroup.
                Types: Feature OR DataSource OR Entity.

        RETURNS:
            bool.

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            >>> from teradataml import Feature, Entity, DataSource, FeatureGroup

            # Create the features.
            >>> feature = Feature('sales:Feb', df.Feb)

            # Create Entity.
            >>> entity = Entity('sales:accounts', df.accounts)

            # Create DataSource.
            >>> data_source = DataSource('Sales_Data', df)

            >>> fg = FeatureGroup('Sales',
            ...                   features=feature,
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Example 1: Create a new Feature for column df.Mar and
            #            apply the feature to FeatureGroup.
            # Create Feature.
            >>> feature = Feature('sales:Mar', df.Mar)

            # Register the above Feature with FeatureGroup.
            >>> fg.apply(feature)
            True

            # Get the features from FeatureGroup.
            >>> fg.features
            [Feature(name=sales:Feb), Feature(name=sales:Mar)]

            # Example 2: Register the DataSource with FeatureGroup.
            >>> load_example_data("dataframe", "admissions_train")
            >>> admissions = DataFrame("admissions_train")
            >>> admissions_source = DataSource('admissions', admissions)

            # Register the DataSource with FeatureGroup.
            >>> fg.apply(admissions_source)
            True

            # Get the DataSource from FeatureGroup.
            >>> fg.data_source
            DataSource(name=admissions)

            # Example 3: Register the Entity with FeatureGroup.
            >>> entity = Entity('admissions:accounts', admissions.accounts)
            # Register the Entity with FeatureGroup.
            >>> fg.apply(entity)
            True
        """
        argument_validation_params = []
        argument_validation_params.append(['object', object, False, (Feature, Entity, DataSource), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        if isinstance(object, Feature):
            # Before adding feature, check if already feature with
            # the name exists or not.
            feature_exists = [i for i in range(len(self._features)) if self._features[i].name == object.name]
            if feature_exists:
                self._features[feature_exists[0]] = object
            else:
                self._features.append(object)
        elif isinstance(object, Entity):
            self.entity = object
        elif isinstance(object, DataSource):
            self.data_source = object
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                     'object', "Feature or Entity or DataSource"),
                                      MessageCodes.UNSUPPORTED_DATATYPE)

        return True

    def remove_feature(self, object):
        """
        DESCRIPTION:
            Method to remove the objects from FeatureGroup. One can use this
            method to detach a Feature from FeatureGroup.

        PARAMETERS:
            object:
                Required Argument.
                Specifies the object to be removed from FeatureGroup.
                Types: Feature.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # First create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Jan", df.Apr)

            # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)

            # Create DataSource.
            >>> data_source = DataSource("sales_source", df.show_query())

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)

            # Example 1: Remove the Feature with name "sales:Feb" from FeatureGroup.
            >>> fg.remove_feature(feb_feature)
            True

            # Get the features from FeatureGroup
            >>> fg.features
            [Feature(name=sales:Jan), 
             Feature(name=sales:Mar), 
             Feature(name=sales:Apr)]
        """
        argument_validation_params = []
        argument_validation_params.append(['object', object, False, (Feature), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        get_msg = lambda object: "{} '{}' is not associated with FeatureGroup.".format(
            object.__class__.__name__, object.name)

        if isinstance(object, Feature):
            # Find the position of feature first, then pop it.
            index = [i for i in range(len(self._features)) if self._features[i].name == object.name]
            if index:
                self.__redundant_features.append(self._features.pop(index[0]))
            else:
                print(get_msg(object))
                return False
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                           'object', "Feature"),
                                      MessageCodes.UNSUPPORTED_DATATYPE)
        return True

    @classmethod
    def _from_df(cls, df, repo, features_df, entity_df, data_source_df, data_domain):
        """
        DESCRIPTION:
            Internal method to create object of FeatureGroup from DataFrame.

        PARAMETERS:
            df:
                Required Argument.
                Specifies teradataml DataFrame which has a single
                record denoting FeatureGroup.
                Types: teradataml DataFrame.

            repo:
                Required Argument.
                Specifies the repo name of FeatureStore.
                Types: str

            features_df:
                Required Argument.
                Specifies teradataml DataFrame which has features.
                Types: teradataml DataFrame.

            entity_df:
                Required Argument.
                Specifies teradataml DataFrame which has entities.
                Types: teradataml DataFrame.

            data_source_df:
                Required Argument.
                Specifies teradataml DataFrame which has data sources.
                Types: teradataml DataFrame.

            data_domain:
                Required Argument.
                Specifies the data domain of the FeatureGroup.
                Types: str.

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> FeatureGroup._from_df(df, "repo", features_df, entity_df, data_source_df)
        """
        rec = next(df.itertuples())._asdict()

        # Select active features.
        features_df = features_df[features_df.status != FeatureStatus.INACTIVE.name]
        req_features_df = features_df[(features_df['group_name'] == rec['name']) &
                                      (features_df['data_domain'] == data_domain)]

        features = Feature._from_df(req_features_df)
        entity = Entity._from_df(entity_df[(entity_df['name'] == rec['entity_name']) &
                                           (entity_df['data_domain'] == data_domain)])
                                           
        data_source = DataSource._from_df(data_source_df[(data_source_df['name'] == rec['data_source_name']) &
                                                         (data_source_df['data_domain'] == data_domain)])

        return cls(name=rec["name"], features=features, entity=entity, data_source=data_source, description=rec["description"])

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for FeatureGroup object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataSource, Entity, Feature, FeatureGroup, load_example_data
            >>> load_example_data("dataframe", "sales")
            # Let's create DataFrame first.
            >>> df = DataFrame("sales")

            # create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)

            # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)

            # Create DataSource.
            >>> data_source = DataSource("sales_source", df.show_query())

            # Create FeatureGroup.
            >>> fg = FeatureGroup("sales_data_fg", features=[jan_feature, feb_feature, mar_feature],
            ...                   entity=entity, data_source=data_source)

            # Get the string representation of FeatureGroup.
            >>> fg
            FeatureGroup(sales_data_fg, features=[Feature(name=sales:Jan), Feature(name=sales:Feb), Feature(name=sales:Mar)], entity=Entity(name=sales:accounts), data_source=DataSource(Sales_Data))
        """
        return "FeatureGroup({}, features=[{}], entity={}, data_source={})".format(
            self.name, ", ".join((str(feature) for feature in self.features)), self.entity, self.data_source)

    @db_transaction
    def publish(self, repo, data_domain):
        """
        DESCRIPTION:
            Method to publish the FeatureGroup details to repository.
            Note:
                * If the FeatureGroup is already registered with same name, features, entity and data source in the repository, it is not updated.
                * If the FeatureGroup is associated with any feature process, an error is raised while modifying FeatureGroup.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repository to publish the FeatureGroup details.
                Types: str.
            
            data_domain:
                Required Argument.
                Specifies the data domain of the FeatureGroup.
                Types: str.

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create a FeatureStore repo 'vfs_v1'.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            # Setup FeatureStore.
            >>> fs.setup()

            # Example 1: Create a FeatureGroup 'sales_data_fg' for above mentioned
            #            DataFrame and publish it to 'vfs_v1'.
            # First create the features.
            >>> jan_feature = Feature("sales:Jan", df.Jan)
            >>> feb_feature = Feature("sales:Fan", df.Feb)
            >>> mar_feature = Feature("sales:Mar", df.Mar)
            >>> apr_feature = Feature("sales:Jan", df.Apr)

            # Create Entity.
            >>> entity = Entity("sales:accounts", df.accounts)

            # Create DataSource.
            >>> data_source = DataSource("sales_source", df.show_query())

            # Create FeatureGroup.
            >>> fg = FeatureGroup('Sales',
            ...                   features=[jan_feature, feb_feature, mar_feature],
            ...                   entity=entity,
            ...                   data_source=data_source)
            >>> fg.publish('vfs_v1', data_domain='sales')

            # Example 2: Republish the FeatureGroup published in example1 with
            #            updated description.
            # First, Get the existing FeatureGroup.
            >>> from teradataml import FeatureStore
            >>> fg = fs.get_feature_group('Sales')

            # Update it's description.
            >>> fg.description = "Feature group for Sales."

            # Republish the details to same repo.
            >>> fg.publish('vfs_v1', data_domain='sales')
        """
        argument_validation_params = []
        argument_validation_params.append(['repo', repo, False, str, True])
        argument_validation_params.append(['data_domain', data_domain, False, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        # Do not publish if any of required associated parameter does not exist.
        message = "FeatureGroup can not be published with out {}"
        if not self.features:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'publish', message.format("Features")),
                MessageCodes.FUNC_EXECUTION_FAILED)

        if not self.data_source:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'publish', message.format("DataSource")),
                MessageCodes.FUNC_EXECUTION_FAILED)

        if not self.entity:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'publish', message.format("Entity")),
                MessageCodes.FUNC_EXECUTION_FAILED)

        # Check if FG already exists in Feature Process. If yes, it should not be touched.
        is_fg_in_fp = _FSUtils._is_fg_exists_in_fp(self.name, repo, data_domain)
        if is_fg_in_fp:
            err_code = MessageCodes.EFS_OBJ_IN_FEATURE_PROCESS
            err_msg = Messages.get_message(err_code,
                                           'Feature group',
                                           self.name,
                                           "Feature process",
                                           "Feature group is used with feature process.",
                                           "FeatureStore.archive_feature_process() and FeatureStore.delete_feature_process()"
                                           )
            raise TeradataMlException(err_msg, err_code)

        # Before publish FeatureGroup, publish other elements.
        for feature in self.features:
            feature.publish(repo, data_domain)

        self.entity.publish(repo, data_domain)
        self.data_source.publish(repo, data_domain)
        _upsert_data(schema_name=repo,
                    table_name=EFS_DB_COMPONENTS['feature_group'],
                    insert_columns_values=OrderedDict({
                        'name': self.name,
                        'description': self.description,
                        'data_source_name': self.data_source.name,
                        'entity_name': self.entity.name,
                        'creation_time': dt.utcnow(),
                        'data_domain': data_domain
                    }),
                    upsert_conditions={'name': self.name,
                                       'data_domain': data_domain},
                    update_columns_values=OrderedDict({
                        'description': self.description,
                        'data_source_name': self.data_source.name,
                        'modified_time': dt.utcnow(),
                        'entity_name': self.entity.name
                    })
                    )      

        for feature in self.features:
            _upsert_data(
                        schema_name=repo,
                        table_name=EFS_DB_COMPONENTS['group_features'],
                        insert_columns_values=OrderedDict({
                            'feature_name': feature.name,
                            'feature_data_domain': data_domain,
                            'group_name': self.name,
                            'group_data_domain': data_domain,
                            'creation_time': dt.utcnow()
                        }),
                        upsert_conditions={
                            'feature_name': feature.name,
                            'feature_data_domain': data_domain,
                            'group_name': self.name,
                            'group_data_domain': data_domain
                        },
                        update_columns_values=OrderedDict({
                            'modified_time': dt.utcnow()
                        })
                    )

        # Cut down the link between features and FeatureGroup if any of the
        # features is removed from FeatureGroup.
        if self.__redundant_features:
            col_expression = _SQLColumnExpression("feature_name") == self.__redundant_features[0].name
            for feature in self.__redundant_features[1:]:
                col_expression = ((col_expression) | (_SQLColumnExpression("feature_name") == feature.name))
            _delete_data(schema_name=repo,
                         table_name=EFS_DB_COMPONENTS['group_features'],
                         delete_conditions=((_SQLColumnExpression("group_name") == self.name) & 
                                            (_SQLColumnExpression("group_data_domain") == data_domain) &
                                            (col_expression)))
            # After removing the data, set this back.
            self.__redundant_features = []

        return True

    def __add__(self, other):
        """
        Combines two Feature groups.

        PARAMETERS:
            other :
                Required Argument.
                Specifies another FeatureGroup.
                Types: FeatureGroup

        RETURNS:
            FeatureGroup

        RAISES:
            TypeError, ValueError

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017

            # Example 1: Create two feature groups and then create a new feature
            #            group by combining those two feature groups.
            # Creating first feature group.
            >>> f1 = Feature("sales_Jan", column=df.Jan)
            >>> f2 = Feature("sales_Feb", column=df.Feb)
            >>> entity = Entity(name="sales", columns='accounts')
            >>> data_source = DataSource("sales", source=df.show_query())
            >>> fg1 = FeatureGroup(name="sales_jan_feb", entity=entity, features=[f1, f2], data_source=data_source)
            >>> fg1
            FeatureGroup(sales_jan_feb, features=[Feature(name=sales_Jan), Feature(name=sales_Feb)], entity=Entity(name=sales), data_source=DataSource(name=sales))

            # Creating second feature group.
            >>> f3 = Feature("sales_Mar", column=df.Mar)
            >>> f4 = Feature("sales_Apr", column=df.Apr)
            >>> data_source = DataSource("sales_Mar_Apr", source=df.show_query())
            >>> fg2 = FeatureGroup(name="sales_Mar_Apr", entity=entity, features=[f3, f4], data_source=data_source)
            >>> fg2
            FeatureGroup(sales_Mar_Apr, features=[Feature(name=sales_Mar), Feature(name=sales_Apr)], entity=Entity(name=sales), data_source=DataSource(name=sales))

            # Combining two feature groups.
            >>> new_fg = feature_group1 + feature_group2
            >>> new_fg
            FeatureGroup(sales_jan_feb_sales_Mar_Apr, features=[Feature(name=sales_Jan), Feature(name=sales_Feb), Feature(name=sales_Mar), Feature(name=sales_Apr)], entity=Entity(name=sales), data_source=DataSource(name=sales))
            >>>
        """
        if not isinstance(other, FeatureGroup):
            err_ = Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, "other",
                                        "FeatureGroup")
            raise TypeError(err_)

        if self.entity != other.entity:
            raise ValueError("Two FeatureGroups can be merged only when the corresponding entities are same.")

        # While merging two datasets, time stamp columns also should be same.
        if ((self.data_source.timestamp_column and not other.data_source.timestamp_column) or
                (other.data_source.timestamp_column and not self.data_source.timestamp_column) or
                (self.data_source.timestamp_column != other.data_source.timestamp_column)):
            raise ValueError("Two FeatureGroups can be merged only when the corresponding "
                             "'timestamp_column' for the DataSources are same.")

        if self.entity == other.entity:

            existing_columns = {feature.column_name for feature in self.features}
            # New features should be combined features of both "self" and other.
            # However, these two features may share common features too. In such cases,
            # consider only one.
            effective_other_features = [feature for feature in other.features
                                        if feature.column_name not in existing_columns]

            # Prepare new DataSource.
            query_1 = self.data_source.source
            query_2 = other.data_source.source

            # If both the queries a.k.a sources are not same, then combine those
            # sources with join. While combining, make sure to specify only the
            # columns which are required.
            if query_2 != query_1:

                # Consider adding timestamp column to query.
                time_stamp_column = []
                if self.data_source.timestamp_column:
                    time_stamp_column.append("A.{}".format(self.data_source.timestamp_column))

                feature_columns = (["A.{}".format(feature.column_name) for feature in self.features] +
                                   ["B.{}".format(feature.column_name) for feature in effective_other_features])

                columns = ", ".join(["A.{}".format(col) for col in self.entity.columns] + time_stamp_column + feature_columns)
                on_clause_columns = [col for col in self.entity.columns]
                if self.data_source.timestamp_column:
                    on_clause_columns.append(self.data_source.timestamp_column)
                where_clause = " AND ".join(["A.{0} = B.{0}".format(column) for column in on_clause_columns])

                query = f"""
                SELECT {columns}
                FROM ({query_1.strip(";")}) AS A, ({query_2.strip(";")}) AS B
                WHERE {where_clause}
                """
                data_source = DataSource(name="{}_{}".format(self.data_source.name, other.data_source.name),
                                         source=query,
                                         description="Combined DataSource for {} and {}".format(
                                             self.data_source.name, other.data_source.name),
                                         timestamp_column=self.data_source.timestamp_column
                                         )
            else:
                data_source = self.data_source

            # Create new feature group.
            feature_group = FeatureGroup(name="{}_{}".format(self.name, other.name),
                                         features=self.features + effective_other_features,
                                         data_source=data_source,
                                         entity=Entity(name="{}_{}".format(self.name, other.name),
                                                       columns=self.entity.columns),
                                         description="Combined FeatureGroup for groups {} and {}.".format(
                                             self.name, other.name)
                                         )
            return feature_group

    @classmethod
    def from_query(cls, name, entity_columns, query, timestamp_column=None):
        """
        DESCRIPTION:
            Method to create FeatureGroup from Query.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the FeatureGroup.
                Note:
                    * Entitiy, DataSource also get the same name as "name".
                      Users can change the name of Entity or DataSource by accessing
                      object from FeatureGroup.
                Types: str.

            entity_columns:
                Required Argument.
                Specifies the column names for the Entity.
                Types: str or list of str.

            query:
                Required Argument.
                Specifies the query for DataSource.
                Types: str.

            timestamp_column:
                Optional Argument.
                Specifies the name of the column in the Query which
                holds the record creation time.
                Types: str OR teradataml DataFrame column

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: Create a FeatureGroup from query 'SELECT * FROM SALES' and
            #            consider 'accounts' column as entity and 'datetime' column
            #            as timestamp_column.
            >>> from teradataml import FeatureGroup
            >>> query = 'SELECT * FROM SALES'
            >>> fg = FeatureGroup.from_query(
            ...             name='sales',
            ...             entity_columns='accounts',
            ...             query=query,
            ...             timestamp_column='datetime'
            ...         )

            # Example 2: Create a FeatureGroup from query 'SELECT * FROM SALES' and
            #            consider 'accounts' and 'jan' columns as entity and 'datetime' column
            #            as timestamp_column. Here, timestamp_column is specified
            #            as ColumnExpression.
            >>> from teradataml import FeatureGroup, ColumnExpression
            >>> query = 'SELECT * FROM SALES'
            >>> fg = FeatureGroup.from_query(
            ...             name='sales',
            ...             entity_columns=['accounts', 'jan'],
            ...             query=query,
            ...             timestamp_column=df.datetime)
        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, str, True])
        argument_validation_params.append(["entity_columns", entity_columns, False, (str, list), True])
        argument_validation_params.append(["query", query, False, str, True])
        argument_validation_params.append(["timestamp_column", timestamp_column, True, (str, ColumnExpression), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        if isinstance(timestamp_column, ColumnExpression):
            timestamp_column = timestamp_column.name
        return cls.__create_feature_group(name, entity_columns, query, timestamp_column)

    @classmethod
    def from_DataFrame(cls, name, entity_columns, df, timestamp_column=None):
        """
        DESCRIPTION:
            Method to create FeatureGroup from DataFrame.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the FeatureGroup.
                Note:
                    * Entitiy, DataSource also get the same name as "name".
                      User's can change the name of Entity or DataSource by accessing
                      object from FeatureGroup.
                Types: str.

            entity_columns:
                Required Argument.
                Specifies the column names for the Entity.
                Types: str or list of str.

            df:
                Required Argument.
                Specifies teradataml DataFrame for creating DataSource.
                Types: teradataml DataFrame.

            timestamp_column:
                Optional Argument.
                Specifies the name of the column in the Query which
                holds the record creation time.
                Types: str OR teradataml DataFrame column

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a FeatureGroup from DataFrame created on 'sales' table and
            #            consider 'accounts' column as entity and 'datetime' column
            #            as timestamp_column.
            >>> from teradataml import FeatureGroup
            >>> df = DataFrame("sales")
            >>> fg = FeatureGroup.from_DataFrame(
            ...             name='sales',
            ...             entity_columns='accounts',
            ...             df=df,
            ...             timestamp_column='datetime'
            ...         )
            >>> fg
            FeatureGroup(sales, features=[Feature(name=Feb), Feature(name=Jan), Feature(name=Mar), Feature(name=Apr)], entity=Entity(name=sales), data_source=DataSource(name=sales))

            # Example 2: create a FeatureGroup from DataFrame created on 'sales' table and
            #            consider 'accounts' and 'jan' columns as entity and 'datetime' column
            #            as timestamp_column. Here, timestamp_column is specified
            #            as ColumnExpression.
            >>> from teradataml import FeatureGroup, ColumnExpression
            >>> fg = FeatureGroup.from_DataFrame(
            ...             name='sales',
            ...             entity_columns=['accounts', 'jan'],
            ...             df=df,
            ...             timestamp_column=df.datetime
            ...         )
            >>> fg
            FeatureGroup(sales, features=[Feature(name=Feb), Feature(name=Jan), Feature(name=Mar), Feature(name=Apr)], entity=Entity(name=sales), data_source=DataSource(name=sales))

        """
        argument_validation_params = []
        argument_validation_params.append(["name", name, False, str, True])
        argument_validation_params.append(["entity_columns", entity_columns, False, (str, list), True])
        argument_validation_params.append(["df", df, False, DataFrame, True])
        argument_validation_params.append(["timestamp_column", timestamp_column, True, (str, ColumnExpression), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        if isinstance(timestamp_column, ColumnExpression):
            timestamp_column = timestamp_column.name
        return cls.__create_feature_group(name, entity_columns, df, timestamp_column)

    @classmethod
    def __create_feature_group(cls, name, entity_columns, obj, timestamp_column=None):
        """
        DESCRIPTION:
            Internal method to create FeatureGroup from either DataFrame or from Query.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the FeatureGroup.
                Types: str.

            entity_columns:
                Required Argument.
                Specifies the column names for the Entity.
                Types: str or list of str.

            obj:
                Required Argument.
                Specifies either teradataml DataFrame or Query for creating DataSource.
                Types: teradataml DataFrame OR str.

            timestamp_column:
                Optional Argument.
                Specifies the name of the column in the Query or DataFrame which
                holds the record creation time.
                Types: str

        RETURNS:
            FeatureGroup

        RAISES:
            None

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Example 1: create a FeatureGroup from DataFrame created on 'sales' table and
            #            consider 'accounts' column as entity and 'datetime' column
            #            as timestamp_column.
            >>> from teradataml import FeatureGroup
            >>> df = DataFrame("sales")
            >>> fg = FeatureGroup.__create_feature_group(
            ...             name='sales',
            ...             entity_columns='accounts',
            ...             df=df,
            ...             timestamp_column='datetime'
            ...         )
        """
        # Check the caller. And decide the type of 'obj'.
        is_obj_dataframe = False
        if inspect.stack()[1][3] == 'from_DataFrame':
            # Perform the function validations.
            is_obj_dataframe = True

        argument_validation_params = []
        argument_validation_params.append(["name", name, False, str, True])
        argument_validation_params.append(["entity_columns", entity_columns, False, (str, list), True])
        argument_validation_params.append(["timestamp_column", timestamp_column, True, str, True])
        param = ["df", obj, False, DataFrame, True] if is_obj_dataframe else ["query", obj, False, str, True]
        argument_validation_params.append(param)
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        df = obj if is_obj_dataframe else DataFrame.from_query(obj)
        entity_columns = UtilFuncs._as_list(entity_columns)

        _Validators._validate_dataframe_has_argument_columns(entity_columns,
                                                             'entity_columns',
                                                             df,
                                                             'df' if is_obj_dataframe else 'query'
                                                             )

        if timestamp_column:
            _Validators._validate_dataframe_has_argument_columns(timestamp_column,
                                                                 'timestamp_column',
                                                                 df,
                                                                 'df' if is_obj_dataframe else 'query')

        features = [Feature(name=col, column=df[col]) for col in df.columns if (
                col not in entity_columns and col != timestamp_column)
            ]
        data_source = DataSource(
            name=name,
            source=df.show_query(),
            timestamp_column=timestamp_column
        )
        entity = Entity(name='_'.join(entity_columns), columns=entity_columns)
        fg = FeatureGroup(
            name=name,
            features=features,
            data_source=data_source,
            entity=entity
        )
        return fg


class DataDomain:

    def __init__(self, repo, data_domain):
        """
        DESCRIPTION:
            Constructor for DataDomain class.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repo to which Datadomain points to.
                Types: str.

            data_domain:
                Required Argument.
                Specifies the name of the data domain.
                Types: str.

        RETURNS:
            DataDomain

        RAISES:
            None

        EXAMPLES:
            # Example 1: Create a DataDomain object.
            # Load data to be used.
            >>> from teradataml import load_example_data, DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame('sales')

            # Define repo and data doamin.
            >>> repo = 'vfs_test'
            >>> data_domain = 'sales'

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo=repo, data_domain=data_domain)
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            >>> from teradataml import DataDomain
            >>> data_domain = DataDomain(repo='vfs_test',
            ...                          data_domain='sales')

        """
        argument_validation_params = []
        argument_validation_params.append(["repo", repo, False, str, True])
        argument_validation_params.append(["data_domain", data_domain, False, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        self.__repo = repo
        self.__data_domain = data_domain

        # Store the table names here. Then use this where ever required.
        self.__table_names = EFS_DB_COMPONENTS

        # Lambda to get filtered dataframe having matching data_domain.
        self.__validate_df_data_domain = lambda df: df[df['data_domain'] == self.__data_domain].drop(
            columns=['ValidPeriod'])

        # Lambda functions used in the DataDomain class.
        self.__get_features_df = lambda: _FeatureStoreDFContainer.get_df("feature", self.__repo, self.__data_domain)
        self.__get_metadata_df = lambda: _FeatureStoreDFContainer.get_df("feature_metadata", self.__repo, self.__data_domain)
        self.__get_entity_df = lambda: _FeatureStoreDFContainer.get_df("entity", self.__repo, self.__data_domain)
        self.__get_entity_info_df = lambda: _FeatureStoreDFContainer.get_df("entity_info", self.__repo, self.__data_domain)
        self.__get_entity_xref_df = lambda: _FeatureStoreDFContainer.get_df("entity_xref", self.__repo, self.__data_domain)
        self.__get_feature_process_df = lambda: _FeatureStoreDFContainer.get_df("feature_process", self.__repo, self.__data_domain)
        self.__get_dataset_catalog_df = lambda: _FeatureStoreDFContainer.get_df("dataset_catalog", self.__repo, self.__data_domain)

    @property
    def features(self):
        """
        DESCRIPTION:
            Returns the list of Feature objects in feature catalog which are associated with the data domain.

        PARAMETERS:
            None

        RETURNS:
            list of Feature.

        RAISES:
            None

        EXAMPLES:
            # Load data to be used.
            >>> from teradataml import load_example_data, DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame('sales')

            # Define repo and data doamin.
            >>> repo = 'vfs_test'
            >>> data_domain = 'sales'

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo=repo, data_domain=data_domain)
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo=repo,
            ...                     data_domain=data_domain,
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' started.
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' completed.

            # Example 1: Get the features from data domain.
            # Create DataDomain object.
            >>> from teradataml import DataDomain
            >>> dd = DataDomain(repo=repo,
            ...                 data_domain=data_domain)

            # List features.
            >>> dd.features
            [Feature(name=Feb), Feature(name=Apr), Feature(name=Jan), Feature(name=Mar)]

        """
        feature_lst = []

        feature_df = self.__get_features_df()
        feature_meta_df = self.__get_metadata_df()

        # Filter out features for current data_domain.
        valid_features = self.__validate_df_data_domain(feature_meta_df)

        # If there are no valid features for the data domain, return empty list.
        if valid_features.shape[0] == 0:
            return feature_lst

        feature_ids = [row.feature_id for row in valid_features.itertuples()]

        # Get the features from _efs_feature table based on the feature_ids.
        features = feature_df[feature_df['id'].isin(feature_ids)]

        for row in features.itertuples():
            feature_lst.append(Feature._from_row(row))

        return feature_lst

    @property
    def entities(self):
        """
        DESCRIPTION:
            Returns the list of Entitity objects in feature catalog which are associated with the data domain.

        PARAMETERS:
            None

        RETURNS:
            list of Entity.

        RAISES:
            None

        EXAMPLES:
            # Load data to be used.
            >>> from teradataml import load_example_data, DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame('sales')

            # Define repo and data doamin.
            >>> repo = 'vfs_test'
            >>> data_domain = 'sales'

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo=repo, data_domain=data_domain)
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo=repo,
            ...                     data_domain=data_domain,
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' started.
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' completed.

            # Example 1: Get the entities in data domain.
            # Create DataDomain object.
            >>> from teradataml import DataDomain
            >>> dd = DataDomain(repo=repo,
            ...                 data_domain=data_domain)

            # List entities.
            >>> dd.entities
            [Entity(name=accounts)]

        """
        entities_lst = []
        feature_metadata_df = self.__get_metadata_df()

        # Filter out entities for current data_domain.
        valid_entities = self.__validate_df_data_domain(feature_metadata_df)

        # If there are no valid entities for the data domain, return empty list.
        if valid_entities.shape[0] == 0:
            return entities_lst

        entity_names = [row.entity_name for row in valid_entities.itertuples()]
        # Get the entities from _efs_entity_xref table based on the entity_names.
        entity_info_df = self.__get_entity_info_df()
        entities_df = entity_info_df[entity_info_df['entity_name'].isin(entity_names) &
                                     (entity_info_df['data_domain'] == self.__data_domain)]

        return _FSUtils._get_entities_from_entity_df(entities_df)

    @property
    def processes(self):
        """
        DESCRIPTION:
            Returns the list of FeatureProcess objects which are associated with the data domain.

        PARAMETERS:
            None

        RETURNS:
            list of FeatureProcess.

        RAISES:
            None

        EXAMPLES:
            # Load data to be used.
            >>> from teradataml import load_example_data, DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame('sales')

            # Define repo and data doamin.
            >>> repo = 'vfs_test'
            >>> data_domain = 'sales'

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo=repo, data_domain=data_domain)
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo=repo,
            ...                     data_domain=data_domain,
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' started.
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' completed.

            # Example 1: Get the processes in data domain.
            # Create DataDomain object.
            >>> from teradataml import DataDomain
            >>> dd = DataDomain(repo=repo,
            ...                 data_domain=data_domain)

            # List processes.
            >>> dd.processes
            [FeatureProcess(repo=vfs_v1, data_domain=sales, process_id=e04fd157-6c23-11f0-8bd4-f020ffe7fe09)]

        """
        processes_lst = []
        feature_processes = self.__get_feature_process_df()

        # Filter out entities for current data_domain.
        valid_processes = self.__validate_df_data_domain(feature_processes)

        # If there are no valid entities for the data domain, return empty list.
        if valid_processes.shape[0] == 0:
            return processes_lst

        for row in valid_processes.itertuples():
            processes_lst.append(FeatureProcess(repo=self.__repo,
                                                data_domain=self.__data_domain,
                                                object=row.process_id,
                                                entity=row.entity_id))
        return processes_lst

    @property
    def datasets(self):
        """
        DESCRIPTION:
            Returns the list of Dataset objects associated with corresponding data domain.

        PARAMETERS:
            None

        RETURNS:
            list of Dataset.

        RAISES:
            None

        EXAMPLES:
            # Load data to be used.
            >>> from teradataml import load_example_data, DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame('sales')

            # Define repo and data doamin.
            >>> repo = 'vfs_test'
            >>> data_domain = 'sales'

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo=repo, data_domain=data_domain)
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo=repo,
            ...                     data_domain=data_domain,
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' started.
            Process '4098c3ea-6c8d-11f0-837a-24eb16d15109' completed.

            # Build dataset.
            >>> from teradataml import DatasetCatalog
            >>> dataset_catalog = DatasetCatalog(repo=repo, data_domain=data_domain)
            >>> dataset_catalog.build_dataset(entity='accounts',
            ...                               selected_features={
            ...                                   'Jan': fp.process_id,
            ...                                   'Feb': fp.process_id,
            ...                                   'Mar': fp.process_id},
            ...                               view_name='dd_test_view',
            ...                               description='DataDomain Test')
                 accounts    Jan    Feb    Mar
            0  Yellow Inc    NaN   90.0    NaN
            1    Alpha Co  200.0  210.0  215.0
            2   Jones LLC  150.0  200.0  140.0
            3    Blue Inc   50.0   90.0   95.0
            4  Orange Inc    NaN  210.0    NaN
            5     Red Inc  150.0  200.0  140.0

            # Example 1: Get the datasets in data domain.
            # Create DataDomain object.
            >>> from teradataml import DataDomain
            >>> dd = DataDomain(repo=repo,
            ...                 data_domain=data_domain)

            # List datasets.
            >>> dd.datasets
            [<teradataml.store.feature_store.models.Dataset at 0x1b6bf9f12d0>]

        """
        dataset_lst = []
        valid_datasets = self.__validate_df_data_domain(self.__get_dataset_catalog_df())
        for row in valid_datasets.itertuples():
            dataset_lst.append(Dataset(repo=self.__repo,
                                       id=row.id,
                                       data_domain=self.__data_domain))
        return dataset_lst


    def __repr__(self):
        """
        DESCRIPTION:
            String representation for DataDomain object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> dd = DataDomain(repo='repo', data_domain='abc')
            >>> dd
            DataDomain(repo=repo, data_domain=abc)
        """
        return "DataDomain(repo={}, data_domain={})".format(self.__repo, self.__data_domain)

class FeatureCatalog:

    def __init__(self, repo, data_domain=None):
        """
        DESCRIPTION:
            Constructor for FeatureCatalog class.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repo to which Feature Catalog points to.
                Note:
                    * If feature store is not setup on repo, then it would error out.
                Types: str.

            data_domain:
                Optional Argument.
                Specifies the name of the data domain the feature catalog refers to.
                If not specified, then default database is used as data domain.
                Types: str.

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> from teradataml import FeatureCatalog

            # Create FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()

            # Create FeatureCatalog object.
            >>> feature_catalog = FeatureCatalog(repo='vfs_v1', data_domain='sales')
            >>> feature_catalog
            FeatureCatalog(repo=vfs_v1, data_domain=sales)
        """
        argument_validation_params = []
        argument_validation_params.append(["repo", repo, False, str, True])
        argument_validation_params.append(["data_domain", data_domain, True, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        self.__repo = repo
        self.__data_domain = data_domain if data_domain is not None \
                             else _get_current_databasename()

        # Only keep the lambda functions that are actually used in the FeatureCatalog class
        self.__get_features_df = lambda: _FeatureStoreDFContainer.get_df("feature", self.__repo, self.__data_domain)
        self.__get_metadata_df = lambda: _FeatureStoreDFContainer.get_df("feature_metadata", self.__repo, self.__data_domain)
        self.__get_catalog_df = lambda: _FeatureStoreDFContainer.get_df("feature_catalog", self.__repo, self.__data_domain)
        self.__get_dataset_features_df = lambda: _FeatureStoreDFContainer.get_df("dataset_features", self.__repo, self.__data_domain)
        self.__get_feature_info_df = lambda: _FeatureStoreDFContainer.get_df("feature_info", self.__repo, self.__data_domain)
        self.__get_entity_info_df = lambda: _FeatureStoreDFContainer.get_df("entity_info", self.__repo, self.__data_domain)

    @property
    def data_domain(self):
        """
        DESCRIPTION:
            Returns the data domain name.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Example 1: Get the data domain name from FeatureCatalog object.
            >>> fc = FeatureCatalog(repo='repo', data_domain='customer analytics')
            >>> fc.data_domain
            'customer analytics'
        """
        return self.__data_domain

    @property
    def features(self):
        """
        DESCRIPTION:
            Returns the list of Feature objects available in Feature Catalog for corresponding data domain.

        PARAMETERS:
            None

        RETURNS:
            list of Feature.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import FeatureCatalog, load_example_data, DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo='repo', 
            ...                     data_domain='sales', 
            ...                     object=df, 
            ...                     entity='accounts', 
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '893d3326-36ab-11f0-2370-f020ff57c63d' started.
            Process '893d3326-36ab-11f0-2370-f020ff57c63d' completed.

            # Example 1: Get the features from Feature Catalog.
            # Create FeatureCatalog object.
            >>> fc = FeatureCatalog('repo', data_domain='sales')
            >>> fc.features
            [Feature(name=Jan), Feature(name=Feb), Feature(name=Mar), Feature(name=Apr)]
        """
        feature_df = self.__get_features_df()
        feature_meta_df = self.__get_metadata_df()
        feature_lst = []

        valid_features = feature_meta_df.drop(columns=['ValidPeriod'])[feature_meta_df['data_domain'] == self.__data_domain]

        # If there are no valid features for the data domain, return empty list.
        if valid_features.shape[0] == 0:
            return feature_lst
        
        feature_ids = [row.feature_id for row in valid_features.itertuples()]

        # Get the features from _efs_feature table based on the feature_ids.
        features = feature_df[feature_df['id'].isin(feature_ids)]

        for row in features.itertuples():
            feature_lst.append(Feature._from_row(row))

        return feature_lst

    @property
    def entities(self):
        """
        DESCRIPTION:
            Returns the list of Entity objects available in Feature Catalog for corresponding data domain.

        PARAMETERS:
            None

        RETURNS:
            List of Entity.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import FeatureCatalog, load_example_data, DataFrame
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Run FeatureProcess to ingest features.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo='repo',
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '893d3326-36ab-11f0-2370-f020ff57c63d' started.
            Process '893d3326-36ab-11f0-2370-f020ff57c63d' completed.

            # Example 1: Get the entities from Feature Catalog.
            # Create FeatureCatalog object.
            >>> fc = FeatureCatalog('repo', data_domain='sales')
            >>> fc.entities
            [Entity(name=accounts)]
        """
        feature_metadata_df = self.__get_metadata_df()
        entity_info_df = self.__get_entity_info_df()
        entities_lst = []

        valid_entities = feature_metadata_df[feature_metadata_df['data_domain'] == self.__data_domain]

        # If there are no valid entities for the data domain, return empty list.
        if valid_entities.shape[0] == 0:
            return entities_lst
        
        entity_names = [row.entity_name for row in valid_entities.itertuples()]

        # Get the entities from _efs_entity_xref table based on the entity_names.
        entities_df = entity_info_df[entity_info_df['entity_name'].isin(entity_names) & 
                                    (entity_info_df['data_domain'] == self.__data_domain)]

        return _FSUtils._get_entities_from_entity_df(entities_df)

    def upload_features(self,
                        object,
                        entity=None,
                        filters=None,
                        features=None,
                        as_of=None,
                        description=None):
        """
        DESCRIPTION:
            Uploads the features in to Feature Catalog from the DataFrame.
            Notes:
                 * Values in Entity column(s) must be unique.
                 * Entity column(s) should not have null values.
                 * One can associate a feature with only one entity in a specific
                   data domain. Use other data domain if the feature with same name
                   is associated with same entity.

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

            filters:
                Optional Argument.
                Specifies filters to be applied on data source while ingesting
                feature values for FeatureProcess.
                Types: str or list of str or ColumnExpression or list of ColumnExpression.

            as_of:
                Optional Argument.
                Specifies the time period for which feature values are ingested.
                Note:
                    * If "as_of" is specified as either string or datetime.datetime,
                      then specified value is considered as starting time period and
                      ending time period is considered as '31-DEC-9999 23:59:59.999999+00:00'.
                Types: str or datetime.datetime or tuple

            description:
                Optional Argument.
                Specifies description for the FeatureProcess.
                Types: str

        RETURNS:
            FeatureProcess.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Create an instance of FeatureCatalog.
            >>> fc = FeatureCatalog(repo='vfs_v1', data_domain='sales')

            # Example 1: Upload features from DataFrame.
            # Before uploading features, let's first look at available features. 
            >>> fc.list_features()
            entity_name feature_id name data_type feature_type valid_start valid_end
                                                                                                                    
            >>> fp = fc.upload_features(object=df,
            ...                         entity=["accounts"],
            ...                         features=["Feb", "Jan", "Mar", "Apr"])
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' started.
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' completed.

            # Verify the features are uploaded.
            >>> fc.list_features()
                        feature_id name data_type feature_type                      valid_start                       valid_end
            entity_name                                                                                                        
            accounts              4  Feb     FLOAT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              6  Apr    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              5  Mar    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts         100002  Jan    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00: 

            # Example 2: Upload features from FeatureGroup.
            # Create a FeatureGroup object.
            >>> fg = FeatureGroup.from_DataFrame(name="sales", entity_columns="accounts", df=df)
            
            # Create FeatureCatalog object.
            >>> fc = FeatureCatalog(repo='vfs_v1', data_domain='sales')
            >>> fp = fc.upload_features(object=fg)
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' started.
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' completed.

            # Verify the features are uploaded.
            >>> fc.list_features()
                         feature_id name data_type feature_type                     valid_start                       valid_end
            entity_name                                                                                                        
            accounts              4  Feb     FLOAT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              6  Apr    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              5  Mar    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts         100002  Jan    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00: 

            # Example 3: Upload features through process id.
            # Create FeatureProcess object.
            >>> fp = FeatureProcess(repo='vfs_v1', 
            ...                     data_domain='sales', 
            ...                     object=df, 
            ...                     entity='accounts', 
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' started.
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' completed.

            # Create FeatureCatalog object.
            >>> fc = FeatureCatalog(repo='vfs_v1', data_domain='sales')
            >>> fp = fc.upload_features(object=fp.process_id)
        """
        # Create FeatureProcess object and run the process.
        fp_obj = FeatureProcess(repo=self.__repo,
                                data_domain=self.__data_domain,
                                object=object,
                                entity=entity,
                                features=features,
                                description=description)
        # Run the feature process.
        fp_obj.run(filters=filters, as_of=as_of)

        return fp_obj

    def list_features(self, archived=False):
        """
        DESCRIPTION:
            Lists the details of available features in the repo for the
            corresponding data domain.

        PARAMETERS:
            archived:
                Optional Argument.
                Specifies whether to retrieve archived features or not from catalog.
                When set to True, returns only archived features, Otherwise
                returns active features from catalog.
                Types: bool.

        RETURNS:
            DataFrame

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Create an instance of FeatureCatalog.
            >>> fc = FeatureCatalog(repo='vfs_v1', data_domain='sales')

            # Upload features from DataFrame.                                                 
            >>> fp = fc.upload_features(object=df,
            ...                         entity=["accounts"],
            ...                         features=["Feb", "Jan", "Mar", "Apr"])
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' started.
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' completed.

            # Example: List the features.
            >>> fc.list_features()
                         feature_id name data_type feature_type                     valid_start                       valid_end
            entity_name                                                                                                        
            accounts              4  Feb     FLOAT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              6  Apr    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              5  Mar    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts         100002  Jan    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00: 
        """
        validate_params = []
        validate_params.append(["archived", archived, True, bool, True])
        # Validate argument types
        _Validators._validate_function_arguments(validate_params)

        # Get the feature info.
        df = self.__get_feature_info_df()
        
        if archived:
            # Filter out the active features. Only archived features are returned.
            df = df[(_SQLColumnExpression("valid_end") < _SQLColumnExpression('current_timestamp'))]
        
        return df.select(['feature_id', 'name', 'entity_name',
                          'data_type', 'feature_type',
                          'valid_start', 'valid_end'])

    def list_feature_versions(self):
        """
        DESCRIPTION:
            Lists the details of available feature versions in the repo for the
            corresponding data domain.

        PARAMETERS:
            None

        RETURNS:
            DataFrame

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Ingest sales data to feature catalog configured for repo 'vfs_v1'.
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017

            # Look at tdtypes before ingesting features.
            >>> df.tdtypes
            accounts    VARCHAR(length=20, charset='LATIN')
            Feb                                     FLOAT()
            Jan                                    BIGINT()
            Mar                                    BIGINT()
            Apr                                    BIGINT()
            datetime                                 DATE()

            # Create FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Initiate FeatureProcess to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts', features=['Jan', 'Feb', 'Mar', 'Apr'])
            # Run the feature process.
            >>> fp.run()
            Process 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c' started.
            Process 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c' completed.

            # Example: List features and its versions from the feature catalog.
            >>> from teradataml import FeatureCatalog
            >>> fc = FeatureCatalog(repo='vfs_v1', data_domain='sales')
            >>> fc.list_feature_versions()
              entity_id data_domain      id name                                 table_name                       feature_version
            0  accounts       sales  100001  Feb  FS_T_19fadd83_620c_3603_4ced_95991bf3b44c  a9f29a4e-3f75-11f0-b43b-f020ff57c62c
            1  accounts       sales  300001  Apr  FS_T_fa01ca99_6169_008c_6b72_cff03d7ee9e1  a9f29a4e-3f75-11f0-b43b-f020ff57c62c
            2  accounts       sales       1  Jan  FS_T_fa01ca99_6169_008c_6b72_cff03d7ee9e1  a9f29a4e-3f75-11f0-b43b-f020ff57c62c
            3  accounts       sales  200001  Mar  FS_T_fa01ca99_6169_008c_6b72_cff03d7ee9e1  a9f29a4e-3f75-11f0-b43b-f020ff57c62c
        """
        df = self.__get_catalog_df()

        # Filter active features.
        df = df[(_SQLColumnExpression("valid_end") > _SQLColumnExpression('current_timestamp'))].drop(columns=['valid_end'])

        return df

    def archive_features(self, features):
        """
        DESCRIPTION:
            Archives the feature values from feature catalog.

        PARAMETERS:
            features:
                Required Argument.
                Specifies name(s) of the feature(s) to be archived from feature catalog.
                Types: str or list of str.

        RETURNS:
            bool

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and
            >>> fs.setup()
            True

            # Create an instance of FeatureCatalog.
            >>> fc = FeatureCatalog(repo='vfs_v1', data_domain='sales')

            # Upload features from DataFrame.                                                 
            >>> fp = fc.upload_features(object=df,
            ...                         entity=["accounts"],
            ...                         features=["Feb", "Jan", "Mar", "Apr"])
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' started.
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' completed.

            # List archived features.
            >>> fc.list_features(archived=True)
            feature_id name data_type feature_type valid_start valid_end

            # Example 1: Archive the single feature from feature catalog.
            >>> fc.archive_features(features='Apr')
            True

            # Validate archived features.
            >>> fc.list_features(archived=True)
                         feature_id name data_type feature_type                     valid_start                       valid_end
            entity_name                                                                                                        
            accounts              4  Apr    BIGINT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  2025-06-17 15:27:10.190000+00:

            # Example 2: Archive multiple feature values from feature catalog.
            >>> fc.archive_features(features=['Jan', 'Feb'])
            True

            # Validate archived features.
            >>> fc.list_features(archived=True)
                         feature_id name data_type feature_type                     valid_start                       valid_end
            entity_name                                                                                                        
            accounts              1  Feb     FLOAT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  2025-06-17 15:27:59.360000+00:
            accounts              2  Jan    BIGINT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  2025-06-17 15:27:59.360000+00:
            accounts              4  Apr    BIGINT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  2025-06-17 15:27:10.190000+00:

        """
        argument_validation_params = []
        argument_validation_params.append(["feature", features, False, (str, list), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        features = UtilFuncs._as_list(features)

        dataset_features_df = self.__get_dataset_features_df()
        # Validate the feature names.
        _Validators._validate_features_not_in_efs_dataset(df=dataset_features_df[(dataset_features_df['data_domain'] == self.__data_domain)],
                                                          feature_names=features,
                                                          action='archived')

        # Get the feature id, feature name, table name for the given features.
        feature_details = self._get_feature_details(
            repo=self.__repo, data_domain=self.__data_domain, feature_names=features)

        return db_transaction(self._remove_features)(
            features_to_remove=features,
            feature_details=feature_details,
            archived=True
        )

    def delete_features(self, features):
        """
        DESCRIPTION:
            Deletes the archived feature values from feature catalog.
            Note:
                * After deleting the feature values from feature catalog table,
                  the function also drops the feature table from the repo if
                  the feature table is not used by any other feature.

        PARAMETERS:
            features:
                Required Argument.
                Specifies name of the feature(s) to be deleted from feature catalog.
                Types: str or list of str.

        RETURNS:
            bool

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Load example data.
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create an instance of FeatureCatalog.
            >>> fc = FeatureCatalog(repo='vfs_v1', data_domain='sales')

            # Upload features from DataFrame.                                                 
            >>> fp = fc.upload_features(object=df,
            ...                         entity=["accounts"],
            ...                         features=["Feb", "Jan", "Mar", "Apr"])
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' started.
            Process '01c70f05-4067-11f0-9e8a-fb57338c2e68' completed.

            # List the features.
            >>> fc.list_features()
                        feature_id name data_type feature_type                      valid_start                        valid_end
            entity_name
            accounts              1  Feb     FLOAT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              4  Apr    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              3  Mar    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:
            accounts              2  Jan    BIGINT   CONTINUOUS  2025-06-12 05:28:42.916821+00:  9999-12-31 23:59:59.999999+00:

            # Example 1: Delete the single feature value from feature catalog.
            # Before deleting, let's archive the feature values.
            >>> fc.archive_features(features='Apr')
            True
            >>> fc.delete_features(features='Apr')
            True

            # Validate the feature is deleted.
            >>> fc.list_features()
                        feature_id name data_type feature_type                      valid_start                        valid_end
            entity_name                                                                                                        
            accounts              3  Mar    BIGINT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  9999-12-31 23:59:59.999999+00:
            accounts              2  Jan    BIGINT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  2025-06-17 15:27:59.360000+00:
            accounts              1  Feb     FLOAT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  2025-06-17 15:27:59.360000+00:

            # Example 2: Delete multiple feature values from feature catalog.
            >>> fc.archive_features(features=['Jan', 'Feb'])
            True
            >>> fc.delete_features(features=['Jan', 'Feb'])
            True

            # Validate the feature values are deleted.
            >>> fc.list_features()
                         feature_id name data_type feature_type                     valid_start                       valid_end
            entity_name                                                                                                        
            accounts              3  Mar    BIGINT   CONTINUOUS  2025-06-17 15:17:25.057869+00:  9999-12-31 23:59:59.999999+00:
        """
        # Validate the arguments.
        argument_validation_params = []
        argument_validation_params.append(["feature", features, False, (str, list), True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)
        
        features = UtilFuncs._as_list(features)

        dataset_features_df = self.__get_dataset_features_df()

        # Validate the features to be deleted are not in dataset features.
        _Validators._validate_features_not_in_efs_dataset(df=dataset_features_df[(dataset_features_df['data_domain'] == self.__data_domain)],
                                                          feature_names=features,
                                                          action='deleted')

        # Get the feature id and table name map for the given features.
        feature_details = self._get_feature_details(
            repo=self.__repo, data_domain=self.__data_domain, feature_names=features)

        return db_transaction(self._remove_features)(
            features_to_remove=features,
            feature_details=feature_details,
            archived=False
        )

    def _remove_features(self,
                         features_to_remove,
                         feature_details,
                         archived=False,
                         shared_features=[],
                         feature_version=None):
        """
        DESCRIPTION:
            Internal method to delete the feature values from feature catalog.
            Note:
                Caller function should open the transaction before calling this method.

        PARAMETERS:
            features_to_remove:
                Required Argument.
                Specifies name of the feature(s) to be deleted from feature catalog.
                Types: list of str.

            feature_details:
                Required Argument.
                Specifies the named tuple for a feature which contains feature name,
                feature id and feature table.
                Types: list

            archived:
                Optional Argument.
                Specifies whether to delete or archive the feature values.
                When set to True, archives the feature values, Otherwise
                deletes the feature values from catalog.
                Default Value: False.
                Types: bool.

            shared_features:
                Optional Argument.
                Specifies the list of shared features that existed in feature catalog.
                If a feature is a shared features, then it is not removed from metadata.
                Also, underlying feature table is not dropped.
                Default Value: [].
                Types: list of str.

            feature_version:
                Optional Argument.
                Specifies the feature version to be deleted.
                If provided, only the features with the specified version are removed.
                Otherwise, all versions of the features are removed.
                Types: str

        RETURNS:
            bool

        RAISES:
            TeradataMlException

        EXAMPLES:
        >>> fc = FeatureCatalog(repo='repo', data_domain='sales')
        # Example 1: Delete the feature values from feature catalog.
        >>> fc.delete_features(features=['Apr', 'Feb'])
        True
        """
        Col = _SQLColumnExpression
        remove_s_ = "archived" if archived else "deleted"
        tables_ = set()
        is_removed = True
        for feature in features_to_remove:

            feature_detail = feature_details.get(feature)

            if feature_detail is None:
                print(f"Feature '{feature}' does not exist in feature catalog.")
                is_removed = is_removed and False
                continue

            # if operation is for archive and feature is already archived do not proceed.
            if archived and feature_detail.is_archived:
                print(f"Feature '{feature}' is already archived.")
                is_removed = is_removed and False
                continue

            # if operation is for delete and feature is not archived do not proceed.
            elif (not archived) and (not feature_detail.is_archived) and (feature not in shared_features):
                print(f"Feature '{feature}' is not archived. Archive the feature before deleting it.")
                is_removed = is_removed and False
                continue

            # If it is delete, then archive should have been done before.
            # Which means, end time should be less than current timestamp.
            feature_deletion_con = Col("feature_id") == feature_detail.id
            metadata_deletion_con = (Col("data_domain") == self.__data_domain) & feature_deletion_con
            temporal_clause = "CURRENT VALIDTIME"
            if not archived:
                time_stamp_con = (Col("valid_start") <= Col('current_timestamp'))
                feature_deletion_con = feature_deletion_con & time_stamp_con
                metadata_deletion_con = metadata_deletion_con & time_stamp_con
                temporal_clause = None

            if feature_version is not None:
                # If process_id is provided, then remove only the features for that process.
                feature_deletion_con = feature_deletion_con & (Col("feature_version") == feature_version)

            # Remove it from main table.
            res = _delete_data(schema_name=self.__repo,
                               table_name=feature_detail.table_name,
                               delete_conditions=feature_deletion_con,
                               temporal_clause=temporal_clause)
            if res == 0:
                print(f"Feature '{feature_detail.name}' is not {remove_s_} from table '{feature_detail.table_name}'.")
                is_removed = is_removed and False
            else:
                print(f"Feature '{feature_detail.name}' is {remove_s_} from table '{feature_detail.table_name}'.")
                tables_.add(feature_detail.table_name)
                is_removed = is_removed and True

            # If feature is a shared feature, do not remove it from metadata.
            if feature in shared_features:
                continue

            # First remove it from metadata table.
            res = _delete_data(schema_name=self.__repo,
                               table_name=EFS_DB_COMPONENTS['feature_metadata'],
                               delete_conditions=metadata_deletion_con,
                               temporal_clause=temporal_clause)
            if res == 0:
                print(f"Feature '{feature_detail.name}' is not {remove_s_} from metadata.")
                is_removed = is_removed and False
            else:
                print(f"Feature '{feature_detail.name}' is {remove_s_} from metadata.")
                is_removed = is_removed and True

        # If not archived, drop intermediate tables not referenced in metadata
        if not archived and tables_:
            sql = """
            select distinct table_name from {0}.{1} where 
            data_domain = '{2}' and table_name in ({3});
            """.format(self.__repo,
                       EFS_DB_COMPONENTS['feature_metadata'],
                       self.__data_domain,
                       ", ".join(["'{}'".format(t) for t in tables_])
                       )
            existing_tables = set(row[0] for row in execute_sql(sql))
            tables_to_drop = tables_ - existing_tables

            # Drop tables not found in metadata
            for table_name in tables_to_drop:
                db_drop_table(schema_name=self.__repo, table_name=table_name)
                print(f"Table '{table_name}' is dropped as it is not referenced in metadata.")
                
        return is_removed

    @staticmethod
    def _get_feature_details(repo, data_domain, feature_names):
        """
        DESCRIPTION:
            Internal function to get the tables and feature ids for the given feature names.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repo to which Feature Catalog points to.
                Types: str.

            data_domain:
                Required Argument.
                Specifies the name of the data domain the feature catalog refers to.
                Types: str.

            feature_names:
                Required Argument.
                Specifies the list of feature names for which details are required.
                Types: list of str.

        RETURNS:
            dict
                A dictionary with feature names as keys and named tuples as values.
                Named tuple contains fields: name, id, table_name, is_archived.
        """
        # Define a named tuple called 'Point' with fields 'name', 'id' and 'table_name'.
        feature_ = namedtuple('feature_', ['name', 'id', 'table_name', 'is_archived'])

        sql = """
        select name, id, table_name, case when valid_end < current_timestamp Then 1 else 0 end is_archived  
        from {0}.{1} f, {0}.{2} m
        where f.data_domain = m.data_domain and m.feature_id = f.id
        and f.data_domain = '{3}' and name in ({4});
        """.format(repo,
                   EFS_DB_COMPONENTS['feature'],
                   EFS_DB_COMPONENTS['feature_metadata'],
                   data_domain,
                   ",".join(["'{}'".format(f) for f in feature_names])
                   )
        return {rec[0]: feature_(rec[0], rec[1], rec[2], rec[3]) for rec in execute_sql(sql)}

    @staticmethod
    def _get_shared_features(repo, data_domain):
        """
        DESCRIPTION:
            Internal method to get the shared features.

        PARAMETERS:
            None

        RETURNS:
            list
                List of shared feature names.

        RAISES:
            TeradataMlException
        """
        # Single feature can be processed by multiple processes.
        # Derive shared features and non shared features.
        sql = """
        select feature_name
        from (SELECT data_domain, entity_id, trim(NGRAM) AS feature_name, PROCESS_ID as feature_version
                FROM NGramSplitter (ON {}.{} as inp USING
                    TextColumn ('FEATURE_NAMES')
                    ConvertToLowerCase ('false')
                    Grams ('1')
                    Delimiter(',')
                ) AS dt) 
        as dt1
        where data_domain = '{}'
        group by feature_name
        having count(distinct feature_version) > 1
        """.format(repo,
                   EFS_DB_COMPONENTS["feature_process"],
                   data_domain
                   )
        return [rec[0] for rec in execute_sql(sql)]

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for FeatureCatalog object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
        """
        return "FeatureCatalog(repo={}, data_domain={})".format(self.__repo, self.__data_domain)

class DatasetCatalog:
    """ Class for DatasetCatalog. """
    def __init__(self, repo, data_domain=None):
        """
        DESCRIPTION:
            Constructor for DatasetCatalog class.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repo to which Dataset Catalog points to.
                Note:
                    * If feature store is not setup on repo, then it would error out.
                Types: str.

            data_domain:
                Optional Argument.
                Specifies the name of the data domain the feature catalog refers to.
                If not specified, then default database is used as data domain.
                Types: str.

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> from teradataml import FeatureCatalog
            # Create FeatureStore repo 'vfs_v1'.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()

            # Create an instance of DatasetCatalog on repo 'vfs_v1'.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dc
            DatasetCatalog(repo=vfs_v1, data_domain=sales)
            """
        arg_validation_params = []
        arg_validation_params.append(["repo", repo, False, str, True])
        arg_validation_params.append(["data_domain", data_domain, True, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(arg_validation_params)

        self.__repo = repo
        self.__data_domain = data_domain if data_domain is not None else _get_current_databasename()
        self.__feature_catalog = FeatureCatalog(repo, data_domain)

        # Only keep the lambda functions that are actually used in the DatasetCatalog class
        self.__get_dataset_catalog_df = lambda: _FeatureStoreDFContainer.get_df("dataset_catalog", self.__repo, self.__data_domain)
        self.__get_dataset_features_df = lambda: _FeatureStoreDFContainer.get_df("dataset_features", self.__repo, self.__data_domain)

        # lambda functions
        # Validate the DataFrame for data domain.
        self.__validate_df_data_domain = lambda df: df[df['data_domain'] == self.__data_domain].drop(columns=['ValidPeriod'])


    @property
    def data_domain(self):
        """
        DESCRIPTION:
            Returns the data domain associated with the DatasetCatalog.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Create an instance of DatasetCatalog on existing repo 'vfs_v1'.
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='customer analytics')
            >>> dc.data_domain
            'customer analytics'
        """
        return self.__data_domain

    def _build_dataset(self, entity, selected_features, view_name, description=None,
                       include_historic_records=False, include_time_series=False,
                       temporary=False):
        """
        DESCRIPTION:
            Internal function to build a dataset.

        PARAMETERS:
            entity:
                Required Argument.
                Specifies the name of the Entity of Object of Entity
                to be included in the dataset.
                Types: str or Entity.

            selected_features:
                Required Argument.
                Specifies the names of Features and the corresponding feature version
                to be included in the dataset.
                Notes:
                     * Key is the name of the feature and value is the version of the
                       feature.
                     * Look at FeatureCatalog.list_feature_versions() to get the list of
                       features and their versions.
                Types: dict

            view_name:
                Required Argument.
                Specifies the name of the view to be named for dataset.
                Types: str.

            description:
                Optional Argument.
                Specifies the description for the dataset.
                Types: str.

            include_time_series:
                Optional Argument.
                Specifies whether to include time series features in the dataset.
                Default Value: False.
                Types: bool.

            include_historic_records:
                Optional Argument.
                Specifies whether to include historic data in the dataset.
                Default Value: False.
                Types: bool.

            temporary:
                Optional Argument.
                Specifies whether the dataset is temporary or not.
                When a dataset is temporary, it is not persisted in the
                dataset catalog. View will be created and destroyed at
                the end of the session.
                Default Value: False.
                Types: bool.

        RETURNS:
            Teradataml DataFrame.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> self._build_dataset(entity='accounts',
            ...                      selected_features = {
            ...                         'Jan': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c',
            ...                         'Feb': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c'},
            ...                      view_name='ds_jan_feb',
            ...                      description='Dataset with Jan and Feb features')
        """
        args = []
        args.append(["entity", entity, False, (str, Entity), True])
        args.append(["selected_features", selected_features, False, dict, True])
        args.append(["view_name", view_name, False, str, True])
        args.append(["description", description, True, str, True])
        args.append(["include_historic_records", include_historic_records, True, bool, True])
        args.append(["include_time_series", include_time_series, True, bool, True])

        # Validate argument types
        _Validators._validate_function_arguments(args)

        entity_name = entity.name if isinstance(entity, Entity) else entity

        features_versions = self.__feature_catalog.list_feature_versions()

        # Filter for entity and data domain first for feature selection
        entity_features = features_versions[
            (features_versions.entity_id == entity_name) &
            (features_versions.data_domain == self.__data_domain)
        ]

        if entity_features.shape[0] == 0:
            res = _FSUtils._get_data_domains(self.__repo, entity_name, 'ds_entity')
            if res:
                msg_code = MessageCodes.EFS_OBJECT_IN_OTHER_DOMAIN
                error_msg = Messages.get_message(msg_code, "Entity", "name '{}'".format(entity_name),
                                                 self.__data_domain, res)
            else:
                msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
                error_msg = Messages.get_message(msg_code, "Entity", "name '{}'".format(entity_name),
                                                 self.__data_domain)
            raise TeradataMlException(error_msg, msg_code)

        # Get all the feature-version pairs of the given entity in the current data domain
        # Create a set of available and selected feature-version pairs
        available_pairs = set((row.name, row.feature_version) for row in entity_features.itertuples())
        requested_pairs = set(selected_features.items())

        # Get the invalid selected feature-version pairs that does not exist in the 
        # available pairs of the given entity in the current data domain.
        invalid_pairs = requested_pairs - available_pairs

        # If there are invalid pairs, raise an exception.
        if invalid_pairs:
            features, versions = zip(*invalid_pairs)
            features_str = ', '.join(f"'{f}'" for f in features)
            versions_str = ', '.join(f"'{v}'" for v in versions)

            msg_code = MessageCodes.EFS_OBJECT_NOT_EXIST
            error_msg = Messages.get_message(msg_code, 
                                            f"Feature(s) {features_str}",
                                            f"version(s) {versions_str}", 
                                            self.__data_domain)
            error_msg += " It might exist in other domain."
            error_msg += " Use FeatureCatalog.list_feature_versions() to list valid features and versions."
            raise TeradataMlException(error_msg, msg_code)

        # Generate UUID first.
        uid = str(uuid.uuid4())

        query, fid_names = self._get_query(
            entity, selected_features,
            include_historic_records=include_historic_records,
            include_validity_period=include_time_series)

        query = SQLBundle()._build_create_view(
            '"{}"."{}"'.format(self.__repo, view_name) if not temporary else view_name,
            query,
            lock_rows=True
        )
        execute_sql(query)

        # If temporary view is requested, return the DataFrame created from the view.
        if temporary:
            return DataFrame(view_name)

        # Prepare inline view for dataset_catalog
        select_row = (
            "SELECT "
            "CAST('{id}' AS VARCHAR(36)) AS id, "
            "CAST('{data_domain}' AS VARCHAR(255)) AS data_domain, "
            "CAST('{name}' AS VARCHAR(255)) AS name, "
            "CAST('{entity_name}' AS VARCHAR(255)) AS entity_name, "
            "CAST('{database_name}' AS VARCHAR(255)) AS database_name, "
            "CAST('{description}' AS VARCHAR(255)) AS description "
            "FROM (SELECT 1 AS dummy) AS t"
        ).format(
            id=uid,
            data_domain=self.__data_domain,
            name=view_name,
            entity_name=entity_name,
            database_name=self.__repo,
            description=description
        )

        _merge_data(
            target_table=EFS_DB_COMPONENTS['dataset_catalog'],
            target_table_schema=self.__repo,
            target_table_alias_name="tgt",
            source=f"({select_row})",
            source_alias_name="src",
            condition="tgt.id = src.id",
            matched_details=None,
            non_matched_clause={
                "action": "INSERT",
                "columns": ["id", "data_domain", "name", "entity_name", "database_name", "description"],
                "values": ["src.id", "src.data_domain", "src.name", "src.entity_name", "src.database_name", "src.description"]
            },
            temporal_clause="CURRENT VALIDTIME"
        )

        # Prepare inline view for dataset_features
        select_rows = []
        for feature, f_version in selected_features.items():
            select_rows.append(
                "SELECT "
                "CAST('{dataset_id}' AS VARCHAR(36)) AS dataset_id, "
                "CAST('{data_domain}' AS VARCHAR(255)) AS data_domain, "
                "{feature_id} AS feature_id, "
                "CAST('{feature_version}' AS VARCHAR(255)) AS feature_version, "
                "CAST('{feature_name}' AS VARCHAR(255)) AS feature_name, "
                "CAST('{feature_repo}' AS VARCHAR(255)) AS feature_repo, "
                "CAST('{feature_view}' AS VARCHAR(255)) AS feature_view "
                "FROM (SELECT 1 AS dummy) AS t".format(
                    dataset_id=uid,
                    data_domain=self.__data_domain,
                    feature_id=fid_names[feature],
                    feature_version=f_version,
                    feature_name=feature,
                    feature_repo=self.__repo,
                    feature_view=view_name
                )
            )
        source_query = "(" + " UNION ALL ".join(select_rows) + ")"

        _merge_data(
            target_table=EFS_DB_COMPONENTS['dataset_features'],
            target_table_schema=self.__repo,
            target_table_alias_name="tgt",
            source=source_query,
            source_alias_name="src",
            condition="tgt.dataset_id = src.dataset_id AND tgt.feature_id = src.feature_id",
            matched_details=None,
            non_matched_clause={
                "action": "INSERT",
                "columns": ["dataset_id", 
                            "data_domain", 
                            "feature_id",
                            "feature_version",
                            "feature_name", 
                            "feature_repo", 
                            "feature_view"
                            ],
                "values": ["src.dataset_id", 
                           "src.data_domain", 
                           "src.feature_id", 
                           "src.feature_version",
                           "src.feature_name", 
                           "src.feature_repo", 
                           "src.feature_view"
                           ]
            },
            temporal_clause="CURRENT VALIDTIME")

        return DataFrame(in_schema(self.__repo, view_name))


    def build_dataset(self, entity, selected_features, view_name, description=None,
                      include_historic_records=False):
        """
        DESCRIPTION:
            Builds the dataset from the feature values available in feature catalog.
            Once dataset is created, user can create a teradataml DataFrame on the dataset.

        PARAMETERS:
            entity:
                Required Argument.
                Specifies the name of the Entity of Object of Entity
                to be included in the dataset.
                Types: str or Entity.

            selected_features:
                Required Argument.
                Specifies the names of Features and the corresponding feature version
                to be included in the dataset.
                Notes:
                     * Key is the name of the feature and value is the version of the
                       feature.
                     * Look at FeatureCatalog.list_feature_versions() to get the list of
                       features and their versions.
                Types: dict

            view_name:
                Required Argument.
                Specifies the name of the view to be named for dataset.
                Types: str.

            description:
                Optional Argument.
                Specifies the description for the dataset.
                Types: str.

            include_historic_records:
                Optional Argument.
                Specifies whether to include historic data in the dataset.
                Default Value: False.
                Types: bool.

        RETURNS:
            Teradataml DataFrame.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Ingest sales data to feature catalog configured for repo 'vfs_v1'.
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Initiate FeatureProcess to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts', features=['Jan', 'Feb', 'Mar', 'Apr'])
            # Run the feature process.
            >>> fp.run()
            Process 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c' started.
            Process 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c' completed.

            # Example 1: Build dataset with features 'Jan', 'Feb' from repo 'vfs_v1' and sales data domain.
            #            Name the dataset as 'ds_jan_feb'.
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                 'Jan': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c',
            ...                                 'Feb': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c'},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')
            >>> dataset
                 accounts    Jan    Feb
            0    Blue Inc   50.0   90.0
            1    Alpha Co  200.0  210.0
            2  Yellow Inc    NaN   90.0
            3  Orange Inc    NaN  210.0
            4   Jones LLC  150.0  200.0
            5     Red Inc  150.0  200.0

            # Example 2: Build dataset with features 'Jan', 'Feb', 'Mar' from repo 'vfs_v1' and sales data domain.
            #            Name the dataset as 'ds_jan_feb_mar'.
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                 'Jan': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c',
            ...                                 'Feb': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c',
            ...                                 'Mar': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c'},
            ...                            view_name='ds_jan_feb_mar',
            ...                            description='Dataset with Jan, Feb and Mar features')
            >>> dataset
                 accounts    Jan    Feb    Mar
            0  Yellow Inc    NaN   90.0    NaN
            1    Alpha Co  200.0  210.0  215.0
            2   Jones LLC  150.0  200.0  140.0
            3    Blue Inc   50.0   90.0   95.0
            4  Orange Inc    NaN  210.0    NaN
            5     Red Inc  150.0  200.0  140.0

            # Example 3: Build dataset with features 'Feb', 'Jan' from repo 'vfs_v1' and 'sales' data domain.
            #            Show the latest data.
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
            >>> fp = FeatureProcess(repo='vfs_v1',
            ...                     data_domain='sales',
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

            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> exclude_history = dc.build_dataset(entity='accounts',
            ...                                    selected_features={'Feb': fp.process_id,
            ...                                                       'Jan': fp.process_id},
            ...                                    view_name='exclude_history',
            ...                                    include_historic_records=False)
            >>> exclude_history
               accounts     Feb   Jan
            0  Blue Inc  9000.0  5000

            # Example 4: Build dataset with features 'Feb', 'Jan' from repo 'vfs_v1' and 'sales' data domain.
            #            Show the historic data.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> include_history = dc.build_dataset(entity='accounts',
            ...                                    selected_features={'Feb': fp.process_id,
            ...                                                       'Jan': fp.process_id},
            ...                                    view_name='include_history',
            ...                                    include_historic_records=True)
            >>> include_history
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

        """
        return self._build_dataset(entity, selected_features, view_name,
                                    description, include_historic_records)

    def build_time_series(self, entity, selected_features, view_name, description=None,
                          include_historic_records=False):
        """
        DESCRIPTION:
            Builds the dataset with start time and end time for feature values available in
            feature catalog. Once dataset is created, user can create a teradataml DataFrame
            on the dataset.

        PARAMETERS:
            entity:
                Required Argument.
                Specifies the name of the Entity of Object of Entity
                to be included in the dataset.
                Types: str or Entity.

            selected_features:
                Required Argument.
                Specifies the names of Features and the corresponding feature version
                to be included in the dataset.
                Notes:
                     * Key is the name of the feature and value is the version of the
                       feature.
                     * Look at FeatureCatalog.list_feature_versions() to get the list of
                       features and their versions.
                Types: dict

            view_name:
                Required Argument.
                Specifies the name of the view to be named for dataset.
                Types: str.

            description:
                Optional Argument.
                Specifies the description for the dataset.
                Types: str.

            include_historic_records:
                Optional Argument.
                Specifies whether to include historic data in the dataset.
                Default Value: False.
                Types: bool.

        RETURNS:
            Teradataml DataFrame.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Ingest sales data to feature catalog configured for repo 'vfs_v1'.
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")
            >>> df
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Red Inc     200.0  150.0  140.0    NaN  04/01/2017
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
            Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
            Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
            Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            Jones LLC   200.0  150.0  140.0  180.0  04/01/2017

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Initiate FeatureProcess to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts', features=['Jan', 'Feb', 'Mar', 'Apr'])
            # Run the feature process.
            >>> fp.run()
            Process 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c' started.
            Process 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c' completed.

            # Example 1: Build dataset with features 'Jan', 'Feb' from repo 'vfs_v1' and sales data domain.
            #            Name the dataset as 'ds_jan_feb'.
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_time_series(entity='accounts',
            ...                                selected_features = {
            ...                                    'Jan': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c',
            ...                                    'Feb': 'a9f29a4e-3f75-11f0-b43b-f020ff57c62c'},
            ...                                view_name='ds_jan_feb',
            ...                                description='Dataset with Jan and Feb features')
            >>> dataset
                 accounts    Jan                  Jan_start_time                    Jan_end_time    Feb                  Feb_start_time                    Feb_end_time
            0    Blue Inc   50.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:   90.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:
            1     Red Inc  150.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:  200.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:
            2  Yellow Inc    NaN  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:   90.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:
            3    Alpha Co  200.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:  210.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:
            4   Jones LLC  150.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:  200.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:
            5  Orange Inc    NaN  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:  210.0  2025-06-20 12:17:14.040000+00:  9999-12-31 23:59:59.999999+00:

            # Example 2: Build dataset with features 'f_int', 'f_float' from repo 'vfs_v1' and 'sales' data domain.
            #            Show the latest and history of the data.
            >>> import time
            >>> from datetime import datetime as dt, date as d

            # Retrieve the record where accounts == 'Blue Inc'.
            >>> df_test = df[df['accounts'] == 'Blue Inc']
            >>> df_test
                          Feb    Jan    Mar    Apr    datetime
            accounts
            Blue Inc     90.0   50.0   95.0  101.0  04/01/2017

            # Writes record stored in a teradataml DataFrame to Teradata Vantage.
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

            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> exclude_history = dc.build_time_series(entity='accounts',
            ...                                        selected_features={'Feb': fp.process_id,
            ...                                                           'Jan': fp.process_id},
            ...                                        view_name='exclude_history',
            ...                                        include_historic_records=False)
            >>> exclude_history
               accounts     Feb                  Feb_start_time                    Feb_end_time   Jan                  Jan_start_time                    Jan_end_time
            0  Blue Inc  9000.0  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:  5000  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:

            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> include_history = dc.build_time_series(entity='accounts',
            ...                                        selected_features={'Feb': fp.process_id,
            ...                                                           'Jan': fp.process_id},
            ...                                        view_name='include_history',
            ...                                        include_historic_records=True)
            >>> include_history
               accounts     Feb                  Feb_start_time                    Feb_end_time   Jan                  Jan_start_time                    Jan_end_time
            0  Blue Inc  9000.0  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:  5000  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:
            1  Blue Inc    90.0  2025-08-15 13:23:41.780000+00:  2025-08-15 13:24:31.320000+00:    50  2025-08-15 13:23:41.780000+00:  2025-08-15 13:24:31.320000+00:
            2  Blue Inc    90.0  2025-08-15 13:23:41.780000+00:  2025-08-15 13:24:31.320000+00:  5000  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:
            3  Blue Inc   900.0  2025-08-15 13:24:31.320000+00:  2025-08-15 13:24:58.140000+00:   500  2025-08-15 13:24:31.320000+00:  2025-08-15 13:24:58.140000+00:
            4  Blue Inc   900.0  2025-08-15 13:24:31.320000+00:  2025-08-15 13:24:58.140000+00:  5000  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:
            5  Blue Inc   900.0  2025-08-15 13:24:31.320000+00:  2025-08-15 13:24:58.140000+00:    50  2025-08-15 13:23:41.780000+00:  2025-08-15 13:24:31.320000+00:
            6  Blue Inc    90.0  2025-08-15 13:23:41.780000+00:  2025-08-15 13:24:31.320000+00:   500  2025-08-15 13:24:31.320000+00:  2025-08-15 13:24:58.140000+00:
            7  Blue Inc  9000.0  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:    50  2025-08-15 13:23:41.780000+00:  2025-08-15 13:24:31.320000+00:
            8  Blue Inc  9000.0  2025-08-15 13:24:58.140000+00:  9999-12-31 23:59:59.999999+00:   500  2025-08-15 13:24:31.320000+00:  2025-08-15 13:24:58.140000+00:

        """
        return self._build_dataset(entity, selected_features, view_name, description,
                                    include_historic_records, include_time_series=True)

    def _get_query(self, entity, selected_features, include_historic_records=False, include_validity_period=False):
        """
        DESCRIPTION:
            Internal method to build the below formatted query.
            query format:
                # CURRENT VALIDTIME
                # SELECT
                #       A1.CustomerID
                #     , A1.sum_Transaction_Amount
                # 	, A2.mean_Transaction_Amount
                # , A3.nb_days_since_last_transactions
                # , A4.count_Transaction_Amount
                #
                #
                # FROM (
                #                 SEQUENCED VALIDTIME
                #                 SELECT
                #                    B1.CustomerID
                #                   ,B1.feature_value AS sum_Transaction_Amount
                #                 FROM "DB_LAB"."FS_T_0307630a_54f6_5871_8cd0_89b8710d7313" B1
                #                 WHERE (feature_id = 3 AND feature_version='0b14d933-40e9-4ea0-b338-3376619d3a8b')
                #                 ) A1
                #
                #     INNER JOIN (
                #                 SEQUENCED VALIDTIME
                #                 SELECT
                #                    B1.CustomerID
                #                   ,B1.feature_value AS mean_Transaction_Amount
                #                 FROM "DB_LAB"."FS_T_0307630a_54f6_5871_8cd0_89b8710d7313" B1
                #                 WHERE (feature_id = 4 AND feature_version='0b14d933-40e9-4ea0-b338-3376619d3a8b')
                #                 ) A2
                #     ON A1.CustomerID= A2.CustomerID
                #
                #     INNER JOIN (
                #                 SEQUENCED VALIDTIME
                #                 SELECT
                #                    B1.CustomerID
                #                   ,B1.feature_value AS nb_days_since_last_transactions
                #                 FROM "DB_LAB"."FS_T_2a778654_aac0_5f1c_8d6e_a1025995e27e" B1
                #                 WHERE (feature_id = 6 AND feature_version='0b14d933-40e9-4ea0-b338-3376619d3a8b')
                #                 ) A3
                #     ON A1.CustomerID= A3.CustomerID
                #
                #     INNER JOIN (
                #                 SEQUENCED VALIDTIME
                #                 SELECT
                #                    B1.CustomerID
                #                   ,B1.feature_value AS count_Transaction_Amount
                #                 FROM "DB_LAB"."FS_T_a6c64c2c_58e9_5060_b811_00839ea493ed" B1
                #                 WHERE (feature_id = 5 AND feature_version='0b14d933-40e9-4ea0-b338-3376619d3a8b')
                #                 ) A4
                #     ON A1.CustomerID= A4.CustomerID

        PARAMETERS:
            entity:
                Required Argument.
                Specifies the name of the Entity of Object of Entity
                to be included in the dataset.
                Types: str or Entity.

            selected_features:
                Required Argument.
                Specifies the names of Features and the corresponding feature version
                to be included in the dataset.
                Notes:
                     * Key is the name of the feature and value is the version of the
                       feature.
                     * Look at FeatureCatalog.list_feature_versions() to get the list of
                       features and their versions.
                Types: dict

            include_validity_period:
                Optional Argument.
                Specifies whether to include start time and end time for feature values in the dataset.
                When set to True, the query will include start time and end time for each feature value.
                Otherwise, it will not include start time and end time.
                Default Value: False.
                Types: bool

            include_historic_records:
                Optional Argument.
                Specifies whether to include historic data in the dataset.
                Default Value: False.
                Types: bool.

        RETURNS:
            tuple.
                1st element represents the query string.
                2nd element represents the dict having feature name as key & id as value.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='repo', data_domain='customer analytics')
            >>> entity = Entity(name='sales', columns=['accounts'])
            >>> selected_features = {'sum_sales': 'v1', 'mean_sales': 'v2'}
            >>> query = dc._get_query(entity, selected_features)
        """
        entity_columns = self.__get_entity_columns(entity)
        features_tables = {}
        features_id = {}
        for rec in self.__feature_catalog.list_feature_versions().itertuples():
            if rec['name'] in selected_features:
                features_tables[rec['name']] = rec['table_name']
                features_id[rec['name']] = rec['id']

        # Construct data set. Prepare below kind of query.
        add_join_condition = False
        queries = []
        entity_cols = ", ".join(entity_columns)
        alias_names = []
        historic_record_clause = 'SEQUENCED VALIDTIME' if include_historic_records else 'CURRENT VALIDTIME'

        for index, (feature, version) in enumerate(selected_features.items(), 1):
            alias_names.append('A{}."{}"'.format(index, feature))
            if include_validity_period:
                alias_names.append("A{}.{}_start_time".format(index, feature))
                alias_names.append("A{}.{}_end_time".format(index, feature))
            query = """
            (
                {historic_record_clause}
                SELECT {entity_cols}, B1.feature_value AS "{feature}" {validity_period_clause}
                FROM "{repo}"."{table_name}" B1
                WHERE (feature_id = {feature_id} AND feature_version='{version}')
            ) A{index}\n
            """.format(
                historic_record_clause=historic_record_clause,
                entity_cols=entity_cols,
                repo=self.__repo,
                table_name=features_tables[feature],
                feature=feature,
                feature_id=features_id[feature],
                version=version,
                index=index,
                validity_period_clause="" if not include_validity_period else
                ", B1.valid_start as {}_start_time, B1.valid_end as {}_end_time".format(feature, feature)
            )


            if add_join_condition:
                join_con = " AND ".join(
                    (f"A{index - 1}.{ent_col} = A{index}.{ent_col}" for
                     ent_col in entity_columns)
                )
                query = query + " ON " + join_con

            queries.append(query)

            add_join_condition = True

        # Join all the queries.
        all_features_q = " INNER JOIN ".join(queries)

        # Prepare final query.
        entity_cols = ", ".join(('A1.{}'.format(col) for col in entity_columns))
        feature_cols = ", ".join(alias_names)
        final_query = """
        SELECT {entity_cols}, {features}
        FROM ({all_features_q})
        """.format(
            entity_cols=entity_cols, features=feature_cols, all_features_q=all_features_q
        )

        return final_query, features_id

    def __get_entity_columns(self, entity):
        """
        DESCRIPTION:
            Internal method to get the columns of the entity.

        PARAMETERS:
            None

        RETURNS:
            list of str

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> self.__get_entity_columns('accounts')
        """
        entity_name = entity if isinstance(entity, str) else entity.name
        sql = """
        select entity_column from "{}"."{}" where entity_name = '{}' and 
        data_domain = '{}' """.format(
            self.__repo, EFS_DB_COMPONENTS['entity_xref'], entity_name, self.__data_domain
        )
        recs = execute_sql(sql).fetchall()
        return [record[0] for record in recs]

    def list_datasets(self):
        """
        DESCRIPTION:
            Lists the available datasets in the repo for the corresponding data domain.

        PARAMETERS:
            None

        RETURNS:
            Teradataml DataFrame

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Upload features first to create a dataset. 
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run the feature process to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])

            # Build dataset. 
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                    'Jan': fp.process_id,
            ...                                    'Feb': fp.process_id},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # Example: List datasets. 
            >>> dc.list_datasets()
                                                 data_domain        name entity_name                        description                      valid_start                       valid_end
            id                                                                                                                                                                         
            201bb332-dcb3-4fe1-9a7d-d575b36c8790       sales  ds_jan_feb    accounts  Dataset with Jan and Feb features   2025-06-12 12:06:15.572420+00:  9999-12-31 23:59:59.999999+00:
        """
        df = self.__validate_df_data_domain(self.__get_dataset_catalog_df())
        return df.drop(columns=['database_name'])

    def list_entities(self):
        """
        DESCRIPTION:
            Lists the available entities along with the assocaited dataset.

        PARAMETERS:
            None

        RETURNS:
            Teradataml DataFrame

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Upload features first to create a dataset.
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run the feature process to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])

            # Build dataset. 
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                        'Jan': fp.process_id,
            ...                                        'Feb': fp.process_id},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # Example: List entities. 
            >>> dc.list_entities()
                                                 data_domain        name entity_name                        description
            id                                                                                                         
            201bb332-dcb3-4fe1-9a7d-d575b36c8790       sales  ds_jan_feb    accounts  Dataset with Jan and Feb features

        """
        df = self.__validate_df_data_domain(self.__get_dataset_catalog_df())
        return df.select(['id', 'data_domain', 'name', 'entity_name', 'description'])

    def list_features(self):
        """
        DESCRIPTION:
            Lists the available features for the corresponding dataset.

        PARAMETERS:
            None

        RETURNS:
            Teradataml DataFrame

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Upload features first to create a dataset. 
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run the feature process to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> from teradataml import DatasetCatalog

            # Build dataset.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                        'Jan': fp.process_id,
            ...                                        'Feb': fp.process_id},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # Example: List features.
            >>> dc.list_features()
                                                 data_domain  feature_id feature_name feature_view
            dataset_id                                                                            
            201bb332-dcb3-4fe1-9a7d-d575b36c8790       sales      100001          Feb   ds_jan_feb
            201bb332-dcb3-4fe1-9a7d-d575b36c8790       sales           1          Jan   ds_jan_feb
        """
        df = self.__validate_df_data_domain(self.__get_dataset_features_df()) 
        return df.select(['dataset_id', 'data_domain', 'feature_id', 
                          'feature_name', 'feature_view'])     

    def get_dataset(self, id):
        """
        DESCRIPTION:
            Gets the Dataset object from the given dataset id.

        PARAMETERS:
            id:
                Required Argument.
                Specifies the dataset id to retrieve dataset from.
                Types: str.

        RETURNS:
            Dataset object

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Upload features first to create a dataset.
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run the feature process to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '3acf5632-5d73-11f0-99c5-a30631e77953' started.
            Process '3acf5632-5d73-11f0-99c5-a30631e77953' completed.
            True

            # Build dataset.
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                        'Jan': fp.process_id,
            ...                                        'Feb': fp.process_id},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List datasets.
            >>> dc.list_datasets()
                                                 data_domain          name entity_name                            description                       valid_start                       valid_end
            id
            851a651a-68a3-4eb6-b606-df2617089068       sales  ds_jan_feb_1    accounts      Dataset with Jan and Feb features    2025-07-10 09:50:25.527852+00:  9999-12-31 23:59:59.999999+00:

            # Example: get dataset.
            >>> ds = dc.get_dataset('851a651a-68a3-4eb6-b606-df2617089068')
            >>> ds
            Dataset(repo=vfs_test, id=851a651a-68a3-4eb6-b606-df2617089068, data_domain=sales)
        """
        # Validate argument type.
        args = []
        args.append(["id", id, True, (str), True])
        _Validators._validate_function_arguments(args)

        return Dataset(repo=self.__repo, id=id, data_domain=self.__data_domain)

    def archive_datasets(self, id):
        """
        DESCRIPTION:
            Archives the dataset from the dataset catalog.

        PARAMETERS:
            id:
                Required Argument.
                Specifies id(s) of the dataset(s) to be archived from dataset catalog.
                Note:
                    * Duplicate ids are processed only once.
                Types: str or list of str.

        RETURNS:
            bool

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Upload features first to create a dataset.
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run the feature process to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '3acf5632-5d73-11f0-99c5-a30631e77953' started.
            Process '3acf5632-5d73-11f0-99c5-a30631e77953' completed.
            True

            # Build dataset.
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                        'Jan': fp.process_id,
            ...                                        'Feb': fp.process_id},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List datasets.
            >>> dc.list_datasets()
                                                 data_domain          name entity_name                            description                      valid_start                        valid_end
            id
            851a651a-68a3-4eb6-b606-df2617089068       sales  ds_jan_feb_1    accounts      Dataset with Jan and Feb features    2025-07-10 09:50:25.527852+00:  9999-12-31 23:59:59.999999+00:

            # Example: Archive dataset.
            >>> dc.archive_datasets('851a651a-68a3-4eb6-b606-df2617089068')
            Dataset id(s) '851a651a-68a3-4eb6-b606-df2617089068' is/are archived from the dataset catalog.
            True

            # List datasets.
            >>> dc.list_datasets()
                                                 data_domain          name entity_name                            description                      valid_start                       valid_end
            id
            851a651a-68a3-4eb6-b606-df2617089068       sales  ds_jan_feb_1    accounts      Dataset with Jan and Feb features   2025-07-10 09:50:25.527852+00:  2025-07-10 09:55:02.830000+00:

        """

        # Validate argument types.
        args = []
        args.append(["id", id, True, (str, list), True])
        _Validators._validate_function_arguments(args)

        # Validate dataset id present in dataset catalog.
        _Validators._validate_dataset_ids_not_in_efs(
            df=self.__get_dataset_catalog_df(),
            ids=id,
            data_domain=self.__data_domain,
            repo=self.__repo
        )

        # Get the id, view_name for the given ids.
        id_details = self._get_id_details(ids=id)

        return db_transaction(self._remove_datasets)(
            id_details=id_details,
            archived=True
        )

    def delete_datasets(self, id):
        """
        DESCRIPTION:
            Deletes the archived dataset from the dataset catalog.
            Note:
                * Delete datasets operation should be done only on archived datasets.

        PARAMETERS:
            id:
                Required Argument.
                Specifies id(s) of the dataset(s) to be deleted from dataset catalog.
                Note:
                    * Duplicate ids are processed only once.
                Types: str or list of str.

        RETURNS:
            bool

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Upload features first to create a dataset.
            >>> from teradataml import load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Run the feature process to ingest features.
            >>> fp = FeatureProcess(repo='vfs_v1', data_domain='sales', object=df, entity='accounts',
            ...                     features=['Jan', 'Feb', 'Mar', 'Apr'])
            >>> fp.run()
            Process '3acf5632-5d73-11f0-99c5-a30631e77953' started.
            Process '3acf5632-5d73-11f0-99c5-a30631e77953' completed.
            True

            # Build dataset.
            >>> from teradataml import DatasetCatalog
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                                        'Jan': fp.process_id,
            ...                                        'Feb': fp.process_id},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List datasets.
            >>> dc.list_datasets()
                                                 data_domain          name entity_name                            description                       valid_start                       valid_end
            id
            851a651a-68a3-4eb6-b606-df2617089068       sales  ds_jan_feb_1    accounts      Dataset with Jan and Feb features    2025-07-10 09:50:25.527852+00:  9999-12-31 23:59:59.999999+00:

            # Example: Archive dataset.
            >>> dc.delete_datasets('851a651a-68a3-4eb6-b606-df2617089068')
            Dataset id(s) '851a651a-68a3-4eb6-b606-df2617089068' is/are deleted from the dataset catalog.
            True

            >>> dc.list_datasets()
            Empty DataFrame
            Columns: [data_domain, name, entity_name, description, valid_start, valid_end]
            Index: []
        """

        # Validate argument type.
        args = []
        args.append(["id", id, True, (str, list), True])
        _Validators._validate_function_arguments(args)

        # Validate dataset id present in dataset catalog.
        _Validators._validate_dataset_ids_not_in_efs(
            df=self.__get_dataset_catalog_df(),
            ids=id,
            data_domain=self.__data_domain,
            repo=self.__repo
        )

        # Get the id, view_name for the given ids.
        id_details = self._get_id_details(ids=id)

        return db_transaction(self._remove_datasets)(
            id_details=id_details,
            archived=False
        )

    def _remove_datasets(self, id_details, archived=False):
        """
        DESCRIPTION:
            Internal method to delete the dataset ids from dataset catalog.
            Note:
                Caller function should open the transaction before calling this method.

        PARAMETERS:
            id_details:
                Required Argument.
                Specifies the named tuple for a id which contains dataset_id, view_name
                and is_archived.
                Types: list

            archived:
                Optional Argument.
                Specifies whether to delete or archive the dataset id.
                When set to True, archives the dataset id, Otherwise
                deletes the dataset id from catalog.
                Default Value: False
                Types: bool

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> dc = DatasetCatalog(repo='repo', data_domain='sales')
            # Example 1: Delete the feature values from feature catalog.
            >>> dc.delete_datasets('ans-231-mwl1')
            True
        """
        rm_id_list = []
        non_rm_id_list = []
        is_removed = True
        temporal_clause = "CURRENT VALIDTIME" if archived else None
        rm_value = "archived" if archived else "deleted"
        common_conditions = (_SQLColumnExpression("data_domain") == self.__data_domain)

        # Iterating over list.
        for id_detail in id_details:
            dataset_id = id_detail[0]
            is_archived = id_detail[2]

            # if operation is for archive and feature is already archived do not proceed.
            if archived and is_archived:
                print(f"Dataset id '{dataset_id}' is already archived.")
                is_removed = is_removed and False
                continue

            # if operation is for delete and dataset_id is not archived do not proceed.
            elif (not archived) and (not is_archived):
                print(f"Dataset id '{dataset_id}' is not archived. Archive the dataset before deleting it.")
                is_removed = is_removed and False
                continue

            tables = [
                (EFS_DB_COMPONENTS['dataset_catalog'], "id"),
                (EFS_DB_COMPONENTS['dataset_features'], "dataset_id")
            ]

            for table_name, id_col in tables:
                res = _delete_data(
                    schema_name=self.__repo,
                    table_name=table_name,
                    delete_conditions=(_SQLColumnExpression(id_col) == dataset_id) & common_conditions,
                    temporal_clause=temporal_clause
                )

                if res == 0:
                    non_rm_id_list.append(dataset_id)
                    is_removed = is_removed and False
                else:
                    rm_id_list.append(dataset_id)
                    is_removed = is_removed and True

            # Drop the view only when dataset id deleted successfully.
            if is_removed and not archived:
                db_drop_view(id_detail[1], schema_name=self.__repo)

        if len(non_rm_id_list) > 0:
            print("Dataset id(s) '{}' is/are not {} from the dataset catalog.".format(
                ", ".join(set(non_rm_id_list)), rm_value
            ))
        elif len(rm_id_list) > 0:
            print("Dataset id(s) '{}' is/are {} from the dataset catalog.".format(
                ", ".join(set(rm_id_list)), rm_value
            ))

        return is_removed

    def _get_id_details(self, ids):
        """
        DESCRIPTION:
            Internal function to get the view_names for given dataset ids.

        PARAMETERS:
            ids:
                Optional Argument.
                Specifies id(s) of the dataset(s) to be deleted from dataset catalog.
                Types: str or list of str.

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            >>> self._get_id_details(['sdew-erec', 'cncw-1d3wmke'])
        """
        ids = UtilFuncs._as_list(ids)

        sql = EFS_ARCHIVED_RECORDS.format("id, name",
                                          "{}.{}".format(self.__repo,
                                                         EFS_DB_COMPONENTS["dataset_catalog"]),
                                          "id in ({})".format(",".join(
                                              ["'{}'".format(f) for f in ids])))

        # List elements - [[dataset_id, feature_view_name, is_archive]]
        return [[rec[0], rec[1], rec[2]] for rec in execute_sql(sql)]

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for DatasetCatalog object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dc
            DatasetCatalog(repo=vfs_v1, data_domain=sales)
        """
        return "DatasetCatalog(repo={}, data_domain={})".format(self.__repo, self.__data_domain)

class Dataset:
    """ Class for Dataset. """
    def __init__(self, repo, id, data_domain=None):
        """
        DESCRIPTION:
            Constructor for Dataset class.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the repo to which dataset belongs to.
                Types: str.

            id:
                Required Argument.
                Specifies the id of the dataset.
                Types: str.

            data_domain:
                Optional Argument.
                Specifies the name of the data domain to refer for managing datasets.
                If not specified, then default database is used as data domain.
                Types: str.

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            
            >>> from teradataml import load_example_data, FeatureStore
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Create a FeatureProcess object and ingest features on existing repo 'vfs_v1'.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' started.
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' completed.

            # Build dataset.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                             'Jan': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09',
            ...                             'Feb': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09'},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List available datasets.
            >>> dc.list_datasets()
                                                 data_domain        name entity_name                        description                      valid_start                       valid_end
            id                                                                                                                                                                         
            abbde025-83b3-4cd8-bb72-57c40ba68f49       sales  ds_jan_feb    accounts  Dataset with Jan and Feb features   2025-06-12 12:06:15.572420+00:  9999-12-31 23:59:59.999999+00:

            # Use one of the dataset IDs to create Dataset object.
            >>> ds = Dataset(repo='vfs_v1',
            ...              id='abbde025-83b3-4cd8-bb72-57c40ba68f49',
            ...              data_domain='sales')
        """
        argument_validation_params = []
        argument_validation_params.append(["repo", repo, False, str, True])
        argument_validation_params.append(["id", id, False, str, True])
        argument_validation_params.append(["data_domain", data_domain, True, str, True])
        # Validate argument types
        _Validators._validate_function_arguments(argument_validation_params)

        self.__repo = repo
        self.__id = id
        self.__data_domain = data_domain if data_domain is not None \
                             else _get_current_databasename()

        # Only keep the lambda functions that are actually used in the Dataset class
        self.__get_feature_df = lambda: _FeatureStoreDFContainer.get_df("feature", self.__repo, self.__data_domain)
        self.__get_dataset_features_df = lambda: _FeatureStoreDFContainer.get_df("dataset_features", self.__repo, self.__data_domain)
        self.__get_entity_info_df = lambda: _FeatureStoreDFContainer.get_df("entity_info", self.__repo, self.__data_domain)
        self.__get_dataset_catalog_df = lambda: _FeatureStoreDFContainer.get_df("dataset_catalog", self.__repo, self.__data_domain)

        # Validate dataset id present in dataset catalog.
        _Validators._validate_dataset_ids_not_in_efs(
            df=self.__get_dataset_catalog_df(),
            ids=id,
            data_domain=self.__data_domain,
            repo=self.__repo
        )

        # lambda functions
        # Validate the DataFrame for given dataset id and data domain.
        self.__validate_dataset_id = lambda df, id_column_name: df[(df[id_column_name] == self.__id) &
                                                                   (df['data_domain'] == self.__data_domain)].drop(columns=['ValidPeriod'])

    @property
    def features(self):
        """
        DESCRIPTION:
            Returns Feature objects associated with this Dataset.

        PARAMETERS:
            None

        RETURNS:
            list of Feature objects.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import load_example_data, FeatureStore
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            >>> fs.setup()
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            True

            # Create a FeatureProcess object and ingest features on existing repo 'vfs_v1'.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' started.
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' completed.

            # Build dataset.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                             'Jan': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09',
            ...                             'Feb': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09'},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List available datasets.
            >>> dc.list_datasets()
                                                 data_domain        name entity_name                        description                      valid_start                       valid_end
            id                                                                                                                                                                         
            abbde025-83b3-4cd8-bb72-57c40ba68f49       sales  ds_jan_feb    accounts  Dataset with Jan and Feb features   2025-06-12 12:06:15.572420+00:  9999-12-31 23:59:59.999999+00:

            # Use one of the dataset IDs to create Dataset object.
            >>> ds = Dataset(repo='vfs_v1',
            ...              id='abbde025-83b3-4cd8-bb72-57c40ba68f49',
            ...              data_domain='sales')

            # Example: Retrieve features.
            >>> ds.features
            [Feature(name=Jan), Feature(name=Feb)]
        """
        feature_df = self.__get_feature_df()
        features_lst = []

        # Filter dataset features for given dataset id and data domain.
        valid_dataset_features = self.__validate_dataset_id(self.__get_dataset_features_df(),
                                                            'dataset_id')

        # Join with dataset features and feature table to get the feature details.
        joined_features_df = valid_dataset_features.join(other=feature_df,
                                                         on=[valid_dataset_features.feature_id == feature_df.id,
                                                             valid_dataset_features.data_domain == feature_df.data_domain],
                                                         lsuffix='_left')
        # Iterate through the rows of joined dataframe and create Feature objects.
        for row in joined_features_df.itertuples():
            features_lst.append(Feature._from_row(row))

        return features_lst

    @property
    def entity(self):
        """
        DESCRIPTION:
            Returns Entity object associated with this Dataset.

        PARAMETERS:
            None

        RETURNS:
            Entity object.

        RAISES:
            None

        EXAMPLES:

            >>> from teradataml import load_example_data, FeatureStore
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")
            
            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Create a FeatureProcess object and ingest features on existing repo 'vfs_v1'.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' started.
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' completed.

            # Build dataset.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                             'Jan': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09',
            ...                             'Feb': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09'},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List available datasets.
            >>> dc.list_datasets()
                                                 data_domain        name entity_name                        description                      valid_start                       valid_end
            id                                                                                                                                                                         
            abbde025-83b3-4cd8-bb72-57c40ba68f49       sales  ds_jan_feb    accounts  Dataset with Jan and Feb features   2025-06-12 12:06:15.572420+00:  9999-12-31 23:59:59.999999+00:

            # Use one of the dataset IDs to create Dataset object.
            >>> ds = Dataset(repo='vfs_v1',
            ...              id='abbde025-83b3-4cd8-bb72-57c40ba68f49',
            ...              data_domain='sales')

            # Example: Retrieve entities.
            >>> ds.entity
            [Entity(name=accounts)]
        """
        entity_info_df = self.__get_entity_info_df()
        entities_lst = []

        # Filter dataset entities for given dataset id and data domain.
        valid_dataset_entities = self.__validate_dataset_id(self.__get_dataset_catalog_df(),
                                                            'id')

        entity_names = [row.entity_name for row in valid_dataset_entities.itertuples()]
        # Filter entity info for the entity names and data domain.
        dataset_entities_df = entity_info_df[(entity_info_df.entity_name.isin(entity_names)) &
                                             (entity_info_df.data_domain == self.__data_domain)]

        return _FSUtils._get_entities_from_entity_df(dataset_entities_df)

    @property
    def view_name(self):
        """
        DESCRIPTION:
            Returns the name of the view which is associated with this Daataset.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import load_example_data, FeatureStore
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()

            # Create a FeatureProcess and ingest features on existing repo 'vfs_v1'.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' started.
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' completed.

            # Build dataset.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                             'Jan': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09',
            ...                             'Feb': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09'},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List available datasets.
            >>> dc.list_datasets()
                                                 data_domain        name entity_name                        description                     valid_start                       valid_end
            id                                                                                                                                                                         
            abbde025-83b3-4cd8-bb72-57c40ba68f49       sales  ds_jan_feb    accounts  Dataset with Jan and Feb features   2025-06-12 12:06:15.572420+00:  9999-12-31 23:59:59.999999+00:

            # Use one of the dataset IDs to create Dataset object.
            >>> ds = Dataset(repo='vfs_v1',
            ...              id='abbde025-83b3-4cd8-bb72-57c40ba68f49',
            ...              data_domain='sales')

            # Example: Retrieve view names.
            >>> ds.view_name
            'ds_jan_feb'
        """
        valid_views = self.__validate_dataset_id(self.__get_dataset_catalog_df(),
                                                 'id')

        return next(valid_views.itertuples()).name

    @property
    def id(self):
        """
        DESCRIPTION:
            Returns the id of the Dataset.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import load_example_data, FeatureStore
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")
            
            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Create a FeatureProcess and ingest features on existing repo 'vfs_v1'.
            >>> from teradataml import FeatureProcess
            >>> fp = FeatureProcess(repo="vfs_v1",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' started.
            Process 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09' completed.

            # Build dataset.
            >>> dc = DatasetCatalog(repo='vfs_v1', data_domain='sales')
            >>> dataset = dc.build_dataset(entity='accounts',
            ...                            selected_features = {
            ...                             'Jan': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09',
            ...                             'Feb': 'eadf3787-4ad4-11f0-8afd-f020ffe7fe09'},
            ...                            view_name='ds_jan_feb',
            ...                            description='Dataset with Jan and Feb features')

            # List available datasets.
            >>> dc.list_datasets()
                                                 data_domain        name entity_name                        description                      valid_start                       valid_end
            id                                                                                                                                                                         
            abbde025-83b3-4cd8-bb72-57c40ba68f49       sales  ds_jan_feb    accounts  Dataset with Jan and Feb features   2025-06-12 12:06:15.572420+00:  9999-12-31 23:59:59.999999+00:

            # Use one of the dataset IDs to create Dataset object.
            >>> ds = Dataset(repo='vfs_v1',
            ...              id='abbde025-83b3-4cd8-bb72-57c40ba68f49',
            ...              data_domain='sales')
            
            # Example: Retrieve id.
            >>> ds.id
            'abbde025-83b3-4cd8-bb72-57c40ba68f49'
        """
        return self.__id

    def __repr__(self):
        """
        DESCRIPTION:
            String representation for Dataset object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import Dataset
            >>> ds = Dataset(repo='vfs_v1', id='abbde025-83b3-4cd8-bb72-57c40ba68f49', data_domain='sales')
            >>> ds
            Dataset(repo=vfs_v1, id=abbde025-83b3-4cd8-bb72-57c40ba68f49, data_domain=sales)
        """
        return "Dataset(repo={}, id={}, data_domain={})".format(self.__repo, self.__id, self.__data_domain)

class FeatureProcess:
    """
    Class for FeatureProcess. This class is responsible for running the feature
    processing workflow, which ingests feature values into the feature catalog.
    """

    def __init__(self,
                 repo,
                 object,
                 entity=None,
                 features=None,
                 data_domain=None,
                 description=None):
        """
        DESCRIPTION:
            Constructor for FeatureProcess class. Once the object is created, use it to
            run the feature process. One can ingest the feature values either by specifying
            teradataml DataFrame or process id or feature group. Look at argument description
            for more details.
            Notes:
                 * Values in Entity column(s) must be unique.
                 * Entity column(s) should not have null values.
                 * One can associate a feature with only one entity in a specific
                   data domain. Use other data domain if the feature with same name
                   is associated with same entity.

        PARAMETERS:
            repo:
                Required Argument.
                Specifies the name of the database where the ingested feature
                values are stored.
                Note:
                    * Feature store should be setup on the database before running
                      feature process. Use FeatureStore.setup() to setup feature store
                      on "repo" database.
                Types: str

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

            data_domain:
                Optional Argument.
                Specifies the data domain for the feature process. If "data_domain" is
                not specified, then default database is considered as data domain.
                Types: str

            description:
                Optional Argument.
                Specifies description for the FeatureProcess.
                Types: str

        RETURNS:
            FeatureProcess

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data("dataframe", "sales")
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            Repo vfs_test does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Example 1: Create a FeatureProcess to ingest features "Jan", "Feb", "Mar"
            #            and "Apr" using DataFrame 'df'. Use 'accounts' column as entity.
            #            Ingest the features to data domain 'sales'.
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process 'e0cdbca3-5c80-11f0-8b86-f020ffe7fe09' started.
            Process 'e0cdbca3-5c80-11f0-8b86-f020ffe7fe09' completed.
            True

            # Example 2: Create a FeatureProcess to ingest features using feature group.
            #            Ingest the features to default data domain.
            >>> fg = FeatureGroup.from_DataFrame(name="sales", entity_columns="accounts", df=df)
            >>> fp = FeatureProcess(repo="vfs_test", object=fg)

            # Example 3: Create a FeatureProcess to ingest features using process id.
            #            Run example 1 first to create process id. Then use process
            #            id to run process again. Alternatively, one can use
            #            FeatureStore.list_feature_process() to get the list of existing process id's.
            >>> fp1 = FeatureProcess(repo="vfs_test", object=df, entity="accounts", features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp1.run()
            Process '593c3326-33cb-11f0-8459-f020ff57c62c' started.
            Process '593c3326-33cb-11f0-8459-f020ff57c62c' completed.
            # Run the process again using process id.
            >>> fp = FeatureProcess(repo="vfs_test", object=fp1.process_id)

            # Example 4: Ingest the sales features 'Jan' and 'Feb' for only entity
            #            'Blue Inc' to the 'sales' data domain. Use 'accounts' column as entity.
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb'])
            >>> fp.run(filters=df.accounts=='Blue Inc')
            Process '7b9f76d6-562c-11f0-bb98-c934b24a960f' started.
            Ingesting the features for filter 'accounts = 'Blue Inc'' to catalog.
            Process '7b9f76d6-562c-11f0-bb98-c934b24a960f' completed.
            True

            # Let's verify the ingested feature values.
            >>> fs = FeatureStore(repo='vfs_v1', data_domain='sales')
            FeatureStore is ready to use.

            >>> fs.list_feature_catalogs()
                        data_domain  feature_id                                 table_name                     valid_start                       valid_end
            entity_name                                                                                                                                   
            accounts          sales           1  FS_T_a38baff6_821b_3bb7_0850_827fe5372e31  2025-07-09 05:08:37.500000+00:  9999-12-31 23:59:59.999999+00:
            accounts          sales           2  FS_T_6003dc24_375e_7fd6_46f0_eeb868305c4a  2025-07-09 05:08:37.500000+00:  9999-12-31 23:59:59.999999+00:

            # Verify the data.
            >>> DataFrame(in_schema('vfs_v1', 'FS_T_6003dc24_375e_7fd6_46f0_eeb868305c4a'))
                      feature_id  feature_value                       feature_version                     valid_start                       valid_end                     ValidPeriod
            accounts                                                                                                                                                                 
            Blue Inc           2           90.0  c0a7704a-5c82-11f0-812f-f020ffe7fe09  2025-07-09 05:08:43.890000+00:  9999-12-31 23:59:59.999999+00:  ('2025-07-09 05:08:43.890000+0
            >>> DataFrame(in_schema('vfs_v1', 'FS_T_a38baff6_821b_3bb7_0850_827fe5372e31'))
                      feature_id  feature_value                       feature_version                     valid_start                       valid_end                     ValidPeriod
            accounts                                                                                                                                                                 
            Blue Inc           1             50  c0a7704a-5c82-11f0-812f-f020ffe7fe09  2025-07-09 05:08:43.890000+00:  9999-12-31 23:59:59.999999+00:  ('2025-07-09 05:08:43.890000+0

            # Example 5: Create a FeatureProcess to ingest features "Jan_v2", "Feb_v2",
            #            using DataFrame 'df'. Use 'accounts' column as entity.
            #            Ingest the features to data domain 'sales'.
            >>> jan_feature = Feature('Jan_v2',
            ...                       df.Jan,
            ...                       feature_type=FeatureType.CATEGORICAL)

            >>> feb_feature = Feature('Feb_v2',
            ...                        df.Feb,
            ...                        feature_type=FeatureType.CATEGORICAL)

            >>> entity = Entity(name='accounts_v2', columns='accounts')

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity=entity,
            ...                     features=[jan_feature, feb_feature])
            >>> fp.run()
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' started.
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' completed.
            True
        """
        # Validate argument types
        args = []
        args.append(["repo", repo, False, (str), True])
        args.append(["object", object, False, (DataFrame, FeatureGroup, str), True])
        args.append(["data_domain", data_domain, True, str, True])
        args.append(["entity", entity, True, (Entity, str, _ListOf(str)), True])
        args.append(["features", features, True, (Feature, str, list), True])
        args.append(["description", description, True, str, True])

        _Validators._validate_function_arguments(args)

        # Verify whether the user input includes duplicate features.
        _Validators._validate_duplicate_objects(features)

        # Validate if it is a list of duplicate entity column names.
        if isinstance(entity, list):
            _Validators._validate_duplicate_objects(entity, type_="entities", arg_name="entity")

        if isinstance(object, DataFrame):
            _Validators._validate_mutually_inclusive_n_arguments(object=object, entity=entity, features=features)

        self.__repo = repo
        self.__feature_group = object if isinstance(object, FeatureGroup) else None
        self.__process_id = object if isinstance(object, str) else None
        self.__df = object if isinstance(object, DataFrame) else None
        self.__entity = object.entity if isinstance(object, FeatureGroup) else entity
        self.__features = object.features if isinstance(object, FeatureGroup) else features

        self.__data_domain = data_domain if data_domain else _get_current_databasename()

        self.__filters = None
        self.__as_of = None

        self.__description = description if description else ""
        self.__fs = None
        self.__start_time = None
        self.__end_time = None
        self.__status = ProcessStatus.NOT_STARTED.value
        
        # Variable to store merge condition.
        self.__merge_condition = None

        self.__feature_process_table = EFS_DB_COMPONENTS["feature_process"]
        self.__feature_metadata_table = EFS_DB_COMPONENTS["feature_metadata"]
        self.__feature_runs_table = EFS_DB_COMPONENTS["feature_runs"]
        self.__data_domain_table = EFS_DB_COMPONENTS["data_domain"]

    def __add_data_domain(self):
        """
        DESCRIPTION:
            Adds the data domain to the FeatureStore object if it is not already available.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo='repo', data_domain='customer analytics')
            >>> fp.__add_data_domain()
        """
        # Add data domain if it is not already present.
        # Error code 2801 is to ignore the error if data domain
        # already exists.
        _insert_data(table_name=self.__data_domain_table,
                     schema_name=self.__repo,
                     values=[(self.__data_domain, dt.now(tz=timezone.utc))],
                     ignore_errors=[2801]
                     )

    @property
    def fs(self):
        """
        DESCRIPTION:
            Returns the FeatureStore object associated with this FeatureProcess.

        PARAMETERS:
            None

        RETURNS:
            FeatureStore

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo='repo', data_domain='customer analytics')
            >>> fp.fs
            FeatureStore(repo='repo')
        """
        if self.__fs is None:
            from teradataml.store.feature_store.feature_store import \
                FeatureStore

            self.__fs = FeatureStore(self.__repo, 
                                     data_domain=self.__data_domain,
                                     check=False)

        return self.__fs

    def run(self, filters=None, as_of=None):
        """
        DESCRIPTION:
            Runs the feature process.

        PARAMETERS:
            filters:
                Optional Argument.
                Specifies filters to be applied on data source while ingesting
                feature values for FeatureProcess.
                Types: str or list of str or ColumnExpression or list of ColumnExpression.

            as_of:
                Optional Argument.
                Specifies the time period for which feature values are ingested.
                Note:
                    * If "as_of" is specified as either string or datetime.datetime,
                      then specified value is considered as starting time period and
                      ending time period is considered as '31-DEC-9999 23:59:59.999999+00:00'.
                Types: str or datetime.datetime or tuple

        RETURNS:
            bool.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create a FeatureStore.
            >>> from teradataml import FeatureStore
            >>> fs = FeatureStore("vfs_test", data_domain='sales')
            Repo vfs_v1 does not exist. Run FeatureStore.setup() to create the repo and setup FeatureStore.
            >>> fs.setup()
            True

            # Example 1: Ingest the feature values using DataFrame 'df' to the repo "vfs_test".
            # Create FeatureProcess using DataFrame as source.
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.run()
            Process '76049397-6b8e-11f0-b77a-f020ffe7fe09' started.
            Process '76049397-6b8e-11f0-b77a-f020ffe7fe09' completed.
            True
            
            # Verify the FeatureProcess was recorded
            >>> fs.list_feature_processes()
                                                 description data_domain       process_type  data_source    entity_id       feature_names feature_ids                     valid_start                       valid_end
            process_id                                                                                                                                                                                               
            a5de0230-6b8e-11f0-ae70-f020ffe7fe09                   sales      feature group  sales_group  sales_group  Apr, Feb, Jan, Mar        None  2025-07-28 08:41:42.460000+00:  9999-12-31 23:59:59.999999+00:
            76049397-6b8e-11f0-b77a-f020ffe7fe09                   sales  denormalized view      "sales"     accounts  Apr, Feb, Jan, Mar        None  2025-07-28 08:40:17.600000+00:  9999-12-31 23:59:59.999999+00:

            # Example 2: Ingest the feature values using feature group to the repo "vfs_test".
            #            Create FeatureGroup from DataFrame and use it as source for FeatureProcess.
            >>> from teradataml import FeatureGroup
            >>> fg = FeatureGroup.from_DataFrame(name="sales_group", 
            ...                                  entity_columns="accounts", 
            ...                                  df=df,
            ...                                  timestamp_column="datetime")
            >>> fs.apply(fg)
            True
            
            # Create FeatureProcess using FeatureGroup as source
            >>> fp = FeatureProcess(repo="vfs_test", 
            ...                     data_domain='sales',
            ...                     object=fg)
            >>> fp.run()
            Process 'b2c3d4e5-2345-11f0-8765-f020ffe7fe09' started.
            Process 'b2c3d4e5-2345-11f0-8765-f020ffe7fe09' completed.
            True
            
            # Verify the process was recorded
            >>> fs.list_feature_processes()
                                                 description data_domain       process_type  data_source    entity_id       feature_names feature_ids                     valid_start                       valid_end
            process_id                                                                                                                                                                                               
            a5de0230-6b8e-11f0-ae70-f020ffe7fe09                   sales      feature group  sales_group  sales_group  Apr, Feb, Jan, Mar        None  2025-07-28 08:41:42.460000+00:  9999-12-31 23:59:59.999999+00:
            76049397-6b8e-11f0-b77a-f020ffe7fe09                   sales  denormalized view      "sales"     accounts  Apr, Feb, Jan, Mar        None  2025-07-28 08:40:17.600000+00:  9999-12-31 23:59:59.999999+00:


            # Example 3: Ingest the feature values using process id to the repo "vfs_test".
            #            Rerun an existing feature process using its process_id.
            # Create FeatureProcess using existing process_id as source
            >>> fp_rerun = FeatureProcess(repo="vfs_test", 
            ...                           data_domain='sales',
            ...                           object=fp.process_id,
            ...                           description="Rerun existing process")
            >>> fp_rerun.run()
            Process 'b2c3d4e5-2345-11f0-8765-f020ffe7fe09' started.
            Process 'b2c3d4e5-2345-11f0-8765-f020ffe7fe09' completed.
            True
            
            # Verify the process runs
            >>> fs.list_feature_processes()
                                                             description data_domain       process_type  data_source    entity_id       feature_names feature_ids                     valid_start                       valid_end
            process_id                                                                                                                                                                                                           
            a5de0230-6b8e-11f0-ae70-f020ffe7fe09                               sales      feature group  sales_group  sales_group  Apr, Feb, Jan, Mar        None  2025-07-28 08:41:42.460000+00:  9999-12-31 23:59:59.999999+00:
            76049397-6b8e-11f0-b77a-f020ffe7fe09                               sales  denormalized view      "sales"     accounts  Apr, Feb, Jan, Mar        None  2025-07-28 08:40:17.600000+00:  2025-07-28 08:44:52.220000+00:
            76049397-6b8e-11f0-b77a-f020ffe7fe09  Rerun existing process       sales  denormalized view      "sales"     accounts  Apr, Feb, Jan, Mar        None  2025-07-28 08:44:52.220000+00:  9999-12-31 23:59:59.999999+00:

            # Example 4: Ingest the sales features 'Mar' and 'Apr' for entities 'Alpha Co' and
            #            'Jones LLC' to the 'sales' data domain. Use 'accounts' column as entity.
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Mar', 'Apr'])
            >>> fp.run(filters=[df.accounts=='Alpha Co', "accounts='Jones LLC'"])
            Process '2a5d5eee-738e-11f0-99c5-a30631e77953' started.
            Ingesting the features for filter 'accounts = 'Alpha Co'' to catalog.
            Ingesting the features for filter 'accounts='Jones LLC'' to catalog.
            Process '2a5d5eee-738e-11f0-99c5-a30631e77953' completed.
            True

            # Let's verify the ingested feature values.
            >>> fs.list_feature_catalogs()
                        data_domain  feature_id                                 table_name                     valid_start                       valid_end
            entity_name
            accounts          sales           1  FS_T_a38baff6_821b_3bb7_0850_827fe5372e31  2025-08-07 12:58:41.250000+00:  9999-12-31 23:59:59.999999+00:
            accounts          sales           2  FS_T_a38baff6_821b_3bb7_0850_827fe5372e31  2025-08-07 12:58:41.250000+00:  9999-12-31 23:59:59.999999+00:

            # Verify the feature data.
            >>> dc = DatasetCatalog(repo='vfs_test', data_domain='sales')
            >>> dc.build_dataset(entity='accounts',
            ...                  selected_features={'Mar': fp.process_id,
            ...                                     'Apr': fp.process_id},
            ...                  view_name='sales_mar_data')
                        Mar	Apr
            accounts
            Jones LLC	140	180
            Alpha Co	215	250

            # Example 5: Ingest feature values for a specific time using DataFrame as source.
            >>> from datetime import datetime, timezone
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Jan', 'Feb'])
            >>> fp.run(as_of='2024-01-01 00:00:00+00:00')
            Process '2a5d5eee-738e-11f0-99c5-a30631e77953' started.
            Process '2a5d5eee-738e-11f0-99c5-a30631e77953' completed.
            True

            # Example 6: Ingest feature values for a specific time using feature group as source.
            >>> fg = FeatureGroup.from_DataFrame(name="sales_temporal",
            ...                                  entity_columns="accounts",
            ...                                  df=df)
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=fg)
            >>> fp.run(as_of='2024-01-01 00:00:00+00:00')
            Process '6e5a8da0-738f-11f0-99c5-a30631e77953' started.
            Process '6e5a8da0-738f-11f0-99c5-a30631e77953' completed.
            True
        """
        args = []
        args.append(["filters", filters, True, (str, ColumnExpression, list), True])
        args.append(["as_of", as_of, True, (str, dt, tuple), True])
        _Validators._validate_function_arguments(args)
        # Verify whether the user input includes duplicate time in as_of.
        _Validators._validate_duplicate_objects(as_of, type_="values", arg_name="as_of")

        self.__as_of = (as_of, '9999-12-31 23:59:59.999999+00:00') if isinstance(as_of, (str, dt)) else as_of
        self.__filters = filters
        self.__filters_str = []

        process_id = None
        temp_table_names = []
        try:
            # First add data domain.
            self.__add_data_domain()

            # Extract data source, entities, features:
            #   If run is initiated using process id, then extract the view, features and entities.
            #   If run is initiated using feature group, then extract the data source, features and entities.
            #   If run is initiated using DF, then use entity and features. While doing so, check entity and
            #   features exist or not. If not exist, then create them.
            (df, entity, features, process_id, process_type, data_source,
             existing_or_new) = self.__get_process_id_df_entity_features()

            ent_cols = entity.columns if isinstance(entity, Entity) else UtilFuncs._as_list(entity)

            # Validate the NULL values in entity columns.
            _Validators._validate_null_values(df, ent_cols, arg_name="entity")

            # Validate the duplicate values in entity columns.
            _Validators._validate_duplicate_values(df, ent_cols, arg_name="entity")

            # If a feature is already archived, then feature process should raise error.
            archived_features = _FSUtils._get_archived_features_from_catalog(
                self.__repo, self.__data_domain)
            msg = ("Feature process cannot be run with archived features. "
                   "Delete the archived features and rerun the process.")
            _Validators._validate_archived_features(
                [f.name for f in features],
                archived_features,
                msg
            )

            self.__features = features
            self.__entity = entity

            # Check if any of the feature is associated with other entity or not.
            existing_features = self.__get_features_entity_from_catalog()

            features_with_other_entity = [feature.name for feature in self.__features if
                                          existing_features.get(feature.name, self.__entity.name)
                                          != self.__entity.name]

            if features_with_other_entity:
                msg = ", ".join(("'{}'".format(f) for f in features_with_other_entity))
                entity_ids = ", ".join(("'{}'".format(existing_features[f]) for f in
                                        features_with_other_entity))
                raise TeradataMlException(
                    Messages.get_message(
                        MessageCodes.EFS_FEATURE_ENTITY_MISMATCH,
                        msg, entity_ids
                    ),
                    MessageCodes.EFS_FEATURE_ENTITY_MISMATCH)

            # Log the start time of the process.
            self.__log_start_time()
            print("Process '{}' started.".format(process_id))

            # At this point, we have the DataFrame with the features and entity columns.
            # Create tables in feature catalog.
            table_names = self.__process_feature_catalog(df, entity, features)

            # If user specifies filters, then apply the filter and create a table.
            # Creating a table will reduce the spool. So, if user has huge data,
            # then user can pass filters and teradataml will upload chunk by chunk
            # by creating temporary tables.
            if self.__filters:
                filters = UtilFuncs._as_list(self.__filters)
                for filter in filters:
                    if isinstance(filter, str):
                        filter = literal_column(filter)
                        filter_str = str(filter.compile())
                    else:
                        filter_str = filter.compile()

                    ndf = df[filter]

                    # Generate temp table and ingest features.
                    # Create temp table.
                    temp_table_name = UtilFuncs._generate_temp_table_name()
                    ndf.to_sql(table_name=temp_table_name, if_exists='replace', schema_name=self.__repo)

                    # Store the temp table name for cleanup.
                    temp_table_names.append(temp_table_name)

                    # Ingest features to catalog.
                    print("Ingesting the features for filter '{}' to catalog.".format(filter_str))
                    self.__ingest_features(source=temp_table_name,
                                           process_id=process_id,
                                           entity=entity,
                                           features=features,
                                           target_tables=table_names)
                    self.__filters_str.append(filter_str)

            else:
                temp_table_name = UtilFuncs._generate_temp_table_name()
                df.to_sql(table_name=temp_table_name, if_exists='replace', schema_name=self.__repo)
                # Store the temp table name for cleanup.
                temp_table_names.append(temp_table_name)
                # Ingest features to catalog.
                self.__ingest_features(source=temp_table_name,
                                       process_id=process_id,
                                       entity=entity,
                                       features=features,
                                       target_tables=table_names)

        except Exception as e:
            self.__status = ProcessStatus.FAILED.value
            if process_id:
                self.__log_end_time(process_id, status=ProcessStatus.FAILED.value, failure_reason=str(e))
            raise e
        else:
            self.__status = ProcessStatus.COMPLETED.value
            # Update Process catalog.
            self.__log_end_time(process_id)
            self.__update_process_catalog(
                process_id, process_type, data_source, entity, features, existing_or_new)
            print("Process '{}' completed.".format(process_id))
            self.__process_id = process_id
            return True
        finally:
            # Drop the temp tables.
            for temp_table_name in temp_table_names:
                db_drop_table(temp_table_name, schema_name=self.__repo)

    @db_transaction
    def __ingest_features(self, source, process_id, entity, features, target_tables):
        """
        DESCRIPTION:
            Ingest features in to feature catalog.

        PARAMETERS:
            source:
                Required Argument.
                Specifies the source table name to ingest features from.
                Types: teradataml DataFrame.

            process_id:
                Required Argument.
                Specifies the process id of the feature process.
                Types: str.

            entity:
                Required Argument.
                Specifies the Entity.
                Types: Entity

            features:
                Required Argument.
                Specifies the features to be ingested.
                Types: list of Feature

            target_tables:
                Required Argument.
                Specifies the table names to ingest the features for.
                Types: dict.

        RETURNS:
            bool

        RAISES:
            None
        """
        if self.__merge_condition is None:
            # Derive the condition.
            condition = " AND ".join(("tgt.{} = src.{}".format(col, col) for col in entity.columns))
            # Append the process id also to the condition.
            self.__merge_condition = " AND ".join((condition, "tgt.feature_version = '{}'".format(process_id)))

        tgt_alias = "tgt"
        src_alias = "src"

        columns = entity.columns + ["feature_id", "feature_value", "feature_version"]
        temporal_clause = "CURRENT VALIDTIME"
        if self.__as_of:
            columns = columns + ["valid_start", "valid_end"]

            # When user specifies as_of, then Merge statement should be triggered
            # with temporal clause VALIDTIME PERIOD instead of CURRENT VALIDTIME.
            temporal_clause = "VALIDTIME PERIOD '({}, {})'".format(
                self.__as_of[0], self.__as_of[1])

        for feature in features:
            # Add Feature ID to condition.
            effective_condition = "{} AND tgt.feature_id = {}".format(self.__merge_condition, feature.id)

            values = ["src.{}".format(col) for col in entity.columns] + [
                "{}".format(feature.id), "src.{}".format(feature.column_name), "'{}'".format(process_id)]

            if self.__as_of:
                values = values + ["'{}'".format(self.__as_of[0]), "'{}'".format(self.__as_of[1])]

            _merge_data(target_table=target_tables[feature.name],
                        target_table_schema=self.__repo,
                        target_table_alias_name=tgt_alias,
                        source=source,
                        source_table_schema=self.__repo,
                        source_alias_name=src_alias,
                        condition=effective_condition,
                        matched_details={
                            "action": "UPDATE",
                            "set": {
                                "feature_value": "src.{}".format(feature.column_name),
                            }
                        },
                        non_matched_clause={
                            "action": "INSERT",
                            "columns": columns,
                            "values": values
                        },
                        temporal_clause=temporal_clause
                        )

    def __log_start_time(self):
        """
        DESCRIPTION:
            Log the start time for the feature process.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test", df=df, entity="accounts", features=["Jan", "Feb", "Mar", "Apr"])
            >>> run_id = fp.__log_start_time()
        """
        self.__start_time = dt.now(tz=timezone.utc)
        self.__status = ProcessStatus.RUNNING.value

    def __log_end_time(self, process_id, status=ProcessStatus.COMPLETED.value, failure_reason=None):
        """
        DESCRIPTION:
            Log the end time for the feature process.

        PARAMETERS:
            process_id:
                Required Argument.
                Specifies the process id of the feature process.
                Types: str.

            status:
                Optional Argument.
                Specifies the status of the feature process.
                Default Value: "completed"
                Types: str.

            failure_reason:
                Optional Argument.
                Specifies the failure reason for the feature process.
                Types: str.

        RETURNS:
            int

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test", df=df, entity="accounts", features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.__log_end_time(process_id=1234, status="COMPLETED", failure_reason=None)
        """
        self.__end_time = dt.now(tz=timezone.utc)
        columns = ["process_id", "data_domain", "start_time", "end_time", "status", "failure_reason"]
        values = [(process_id, self.__data_domain, self.__start_time, self.__end_time, status, failure_reason)]

        # Store the as_of period in feature runs table if it is specified.
        if self.__as_of:
            columns = columns + ["as_of_start", "as_of_end"]
            st_period, end_period = self.__as_of
            values[0] = values[0] + (st_period, end_period)
        
        if self.__filters:
            columns = columns + ["filter"]
            # Use the already processed filters string from run() method
            filter_str = ", ".join(self.__filters_str)
            values[0] = values[0] + (filter_str,)

        run_id = _insert_data(table_name=self.__feature_runs_table,
                              columns=columns,
                              values=values,
                              schema_name=self.__repo,
                              return_uid=True
                              )
        return run_id

    def __update_process_catalog(self, process_id, process_type, data_source, entity, features, existing_or_new):
        """
        DESCRIPTION:
            Update the process catalog.

        PARAMETERS:
            process_id:
                Required Argument.
                Specifies the process id of the feature process.
                Types: str.

            process_type:
                Required Argument.
                Specifies the type of the feature process.
                Types: str.

            data_source:
                Required Argument.
                Specifies the data source of the feature process.
                Types: str.

            entity:
                Required Argument.
                Specifies the entity of the feature process.
                Types: Entity

            features:
                Required Argument.
                Specifies the features of the feature process.
                Types: list of Feature

            existing_or_new:
                Required Argument.
                Specifies whether the process is existing or new.
                Types: bool

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test", df=df, entity="accounts", features=["Jan", "Feb", "Mar", "Apr"])
            >>> fp.__update_process_catalog(process_id="1234-xyz-abc-pqrtd",
            ...                             process_type="feature_group",
            ...                             data_source="sales_data",
            ...                             entity=Entity(name="sales"),
            ...                             features=[Feature(name="max_sales")],
            ...                             existing_or_new=True
            ...                             )
        """
        # Prepare source data first.
        src = "( SELECT '{}' process_id, '{}' data_domain )".format(process_id, self.__data_domain)
        condition = """
        tgt.process_id = src.process_id and 
        tgt.data_domain = src.data_domain and 
        tgt.process_id='{}'
        """.format(process_id)
        features_ = ", ".join(sorted((feature.name for feature in features)))
        _merge_data(target_table=self.__feature_process_table,
                    target_table_schema=self.__repo,
                    target_table_alias_name="tgt",
                    source=src,
                    source_alias_name="src",
                    condition=condition,
                    matched_details={
                        "action": "UPDATE",
                        "set": {
                            "description": UtilFuncs._teradata_quote_arg(self.__description, call_from_wrapper=False),
                            "process_type": UtilFuncs._teradata_quote_arg(process_type, call_from_wrapper=False),
                            "data_source": UtilFuncs._teradata_quote_arg(data_source, call_from_wrapper=False),
                            "entity_id": UtilFuncs._teradata_quote_arg(entity.name, call_from_wrapper=False),
                            "feature_names": UtilFuncs._teradata_quote_arg(features_, call_from_wrapper=False)
                        }
                    },
                    non_matched_clause={
                        "action": "INSERT",
                        "columns": [
                            "process_id",
                            "description",
                            "data_domain",
                            "process_type",
                            "data_source",
                            "entity_id",
                            "feature_names"
                        ],
                        "values": [
                            UtilFuncs._teradata_quote_arg(process_id, call_from_wrapper=False),
                            UtilFuncs._teradata_quote_arg(self.__description, call_from_wrapper=False),
                            UtilFuncs._teradata_quote_arg(self.__data_domain, call_from_wrapper=False),
                            UtilFuncs._teradata_quote_arg(process_type, call_from_wrapper=False),
                            UtilFuncs._teradata_quote_arg(data_source, call_from_wrapper=False),
                            UtilFuncs._teradata_quote_arg(entity.name, call_from_wrapper=False),
                            UtilFuncs._teradata_quote_arg(features_ if features else "", call_from_wrapper=False)
                        ]
                    },
                    temporal_clause="CURRENT VALIDTIME"
                    )

    def __get_process_id_df_entity_features(self):
        """
        DESCRIPTION:
            Get the DataFrame, Entity and Features required to ingest features.
            Notes:
                 * If user specifies only process id while creating FeatureProcess object,
                   then this method returns the DF created from process id. Also extracts
                   Features and Entity for the corresponding process and run it.
                 * If user specifies only feature group while creating FeatureProcess object,
                   then this method returns the DF created from feature group. Also extracts
                   Features and Entity for the corresponding feature group. In this case, process
                   id will be first looked at feature process table. If found, return that
                   process ID. Else, create a new process id.
                 * If user specifies DF, features and Entity while creating FeatureProcess object,
                   then this method returns the DF, features and Entity. In this case also, first
                   process ID will be first looked at feature process table. If found, return that
                   process ID. Else, create a new process id.

        PARAMETERS:
            None

        RETURNS:
            tuple
                (df, entity, features, process_id, process_type, data_source, existing or new process)

        RAISES:
            None
        """
        if self.__process_id:
            # If process id is provided, then get the process id.
            return self.__get_process_id_df_entity_features_from_process()

        if self.__feature_group:
            return self.__get_process_id_df_entity_features_from_fg()

        return self.__get_process_id_df_entity_features_from_df()

    def __get_process_id_df_entity_features_from_process(self):
        """
        DESCRIPTION:
            Get the DataFrame, Entity and Features required to ingest features
            from process id.

        PARAMETERS:
            None

        RETURNS:
            tuple
                (df, entity, features, process_id, process_type, data_source, existing or new process)

        RAISES:
            None
        """
        # Extract process type, data source, entity_id, feature_names from latest process.
        process_rec = _FSUtils._get_open_feature_process(
            self.__repo, self.__data_domain, self.__process_id)

        process_type = process_rec['process_type']
        data_source = process_rec['data_source']
        entity_id = process_rec['entity_id']
        feature_names = process_rec['feature_names']

        # If process type is denormalized view, then user run process by creating
        # view from transformation.
        if process_type == ProcessType.DENORMALIZED_VIEW.value:
            df = DataFrame(data_source)
            entity = self.fs.get_entity(entity_id)
            features = [self.fs.get_feature(fname) for fname in feature_names]
            return df, entity, features, self.__process_id, process_type, data_source, True

        elif process_type == ProcessType.FEATURE_GROUP.value:
            # If process type is feature group, then user run process by creating
            # feature group.
            fg = self.fs.get_feature_group(data_source)
            df = DataFrame.from_query(fg.data_source.source)
            entity = fg.entity
            features = [feature for feature in fg.features if feature.name in feature_names]
            return (df, entity, features, self.__process_id, process_type, data_source,
                    ProcessType.EXISTING.value)

        raise TeradataMlException(
            Messages.get_message(
                MessageCodes.EFS_INVALID_PROCESS_TYPE,
                process_type,
                "'{}', '{}'".format(ProcessType.FEATURE_GROUP.value, ProcessType.DENORMALIZED_VIEW.value)
            ),
            MessageCodes.EFS_INVALID_PROCESS_TYPE
        )

    def __get_feature_id(self, feature_name):
        """
        DESCRIPTION:
            Get the feature id for the given feature name.

        PARAMETERS:
            feature_name:
                Required Argument.
                Specifies the name(s) of the feature.
                Types: str OR list of str

        RETURNS:
            int

        RAISES:
            TeradataMlException
        """
        sql = """
        select id from "{}"."{}" where name = '{}' and data_domain = '{}'
        """.format(self.__repo, "_efs_features", feature_name, self.__data_domain)
        recs = execute_sql(sql).fetchone()
        if recs:
            return recs[0]
        return

    def __get_process_id_df_entity_features_from_fg(self):
        """
        DESCRIPTION:
            Get the DataFrame, Entity and Features required to ingest features
            from feature group.

        PARAMETERS:
            None

        RETURNS:
            tuple
                (df, entity, features, process_id, process_type, data_source)

        RAISES:
            None
        """

        # Derive the process id.
        process_id, existing_or_new = self.__get_process_id(self.__feature_group.entity.name)

        # Prepare Entity, DataSource and Feature objects.
        df = DataFrame.from_query(self.__feature_group.data_source.source)
        entity = self.__feature_group.entity
        features = self.__feature_group.features

        return (df, entity, features, process_id, ProcessType.FEATURE_GROUP.value,
                self.__feature_group.name, existing_or_new)

    def __get_process_id_df_entity_features_from_df(self):
        """
        DESCRIPTION:
            Get the DataFrame, Entity and Features required to ingest features
            from DataFrame.

        PARAMETERS:
            None

        RETURNS:
            tuple
                (df, entity, features, process_id, process_type, data_source)

        RAISES:
            None
        """
        # First materialize the DF.
        self.__df.materialize()

        # Check if Entity is existed or not. If not, push it.
        entity = self.__process_entity()

        process_id, existing_or_new = self.__get_process_id(entity_name=entity.name)

        # Check if features are existed or not. If not, push it.
        features = [f if isinstance(f, Feature) else Feature(name=f, column=self.__df[f])
                    for f in UtilFuncs._as_list(self.__features)]

        return (self.__df, entity, features, process_id, ProcessType.DENORMALIZED_VIEW.value,
                self.__df._table_name, existing_or_new)

    def __get_process_id(self, entity_name):
        """
        DESCRIPTION:
            Get the process id for the feature group.

        PARAMETERS:
            entity_name:
                Required Argument.
                Specifies the entity name.
                Types: str

        RETURNS:
            tuple, 2 elements. First element refers to process id and
                               second element refers whether process is old or new.

        RAISES:
            None
        """
        if self.__feature_group:
            process_type = ProcessType.FEATURE_GROUP.value
            data_source = self.__feature_group.name
        else:
            process_type = ProcessType.DENORMALIZED_VIEW.value
            data_source = self.__df._table_name

        sql = """
              CURRENT VALIDTIME SELECT PROCESS_ID FROM "{}"."{}" WHERE 
              DATA_DOMAIN = '{}' AND PROCESS_TYPE = '{}' AND DATA_SOURCE = '{}'
              AND ENTITY_ID = '{}'
              """.format(self.__repo,
                         self.__feature_process_table,
                         self.__data_domain,
                         process_type,
                         data_source,
                         entity_name
                         )
        recs = execute_sql(sql).fetchone()

        if recs:
            return recs[0], ProcessType.EXISTING.value

        return str(uuid.uuid1()), ProcessType.NEW.value

    def __process_feature_catalog(self, df, entity, features):
        """
        DESCRIPTION:
            Process the feature catalog. Method first checks if the table _efs_features_metadata
            has entry for the feature id. If not, then it inserts the entry in the table.
            Then it tries to create table for the feature. If table is already created, then
            it skips the creation of table. Finally, it returns the table names for the features.

        PARAMETERS:
            df:
                Required Argument.
                Specifies the DataFrame to process.
                Types: teradataml DataFrame.

            entity:
                Required Argument.
                Specifies the Entity.
                Types: Entity

            features:
                Required Argument.
                Specifies the features to be processed.
                Types: list of Feature

        RETURNS:
            dict
                Dictionary with feature name as key and feature catalog table name as value.

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     df=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> table_names = fp.__process_feature_catalog(df, entity, features)
        """
        # Mapper to store feature names and corresponding table names.
        table_names = {}

        # Store the feature ids extracted from feature object.
        feature_ids = []

        # Mapper to store feature ids and corresponding feature names.
        fid_names = {}

        # Mapper to store table names and corresponding columns.
        tables_to_create = {}

        if self.__feature_group:
            # Before publishing, check if feature group is already published or not.
            if not _FSUtils._is_fg_exists_in_fs(self.__feature_group.name, self.__repo, self.__data_domain):
                # If feature group is not published, then publish it.
                self.__feature_group.publish(repo=self.__repo, data_domain=self.__data_domain)
        else:
            # If feature group is not provided, then process the entity.
            entity.publish(repo=self.__repo, data_domain=self.__data_domain)

        for feature in features:

            # Publish the feature and assign ID. If user source FeatureGroup, then it
            # feature would have automatically published.
            if self.__feature_group is None:
                feature.publish(repo=self.__repo, data_domain=self.__data_domain)

            feature.id = self.__get_feature_id(feature.name)

            # Derive type for every feature.
            td_type = df[feature.column_name].type

            normalized_type, identifier = _Dtypes._get_normalized_type(td_type)

            # If feature is of below types, raise error.
            if isinstance(identifier, (XML, JSON, CLOB, BLOB, MBB, MBR, VECTOR, GEOMETRY)):
                message = Messages.get_message(
                    MessageCodes.EFS_INVALID_FEATURE_TYPE,
                    normalized_type.__type__.__name__,
                    feature.name,
                    "'XML', 'JSON', 'CLOB', 'BLOB', 'MBB', 'MBR', 'VECTOR', 'GEOMETRY'"
                )
                raise TeradataMlException(message, MessageCodes.EFS_INVALID_FEATURE_TYPE)

            # Add entity columns to form complete identifier.
            identifier = "{}_{}_{}".format(identifier, "_".join(entity.name), self.__data_domain)
            table_name = "FS_T_{}".format(UtilFuncs._get_hash_value(identifier))

            # Store the table names vs feature names.
            table_names[feature.name] = table_name

            # Store the feature id vs feature names.
            fid_names[feature.id] = feature.name

            # Store feature ids.
            feature_ids.append(feature.id)

            # Prepare table schema to use if further.
            columns = {column: df[column].type for column in entity.columns}

            # Add feature type columns.
            columns['feature_id'] = BIGINT()
            columns['feature_value'] = normalized_type
            columns['feature_version'] = VARCHAR(100)

            # Add temporal columns.
            columns['valid_start'] = 'TIMESTAMP(6) WITH TIME ZONE NOT NULL'
            columns['valid_end'] = 'TIMESTAMP(6) WITH TIME ZONE NOT NULL'
            tables_to_create[table_name] = columns

        missing_ids = self.__get_missing_features_from_catalog(feature_ids)
        if missing_ids:
            # insert missing records using _merge_data with CURRENT VALIDTIME.
            fid_tables = {id: table_names[fid_names[id]] for id in missing_ids}

            # Use UNION ALL SELECT to create an inline view for merge_data source
            select_rows = []
            for id, table_name in fid_tables.items():
                select_rows.append(
                    (
                        "SELECT "
                        "CAST('{entity_name}' AS VARCHAR(255)) AS entity_name, "
                        "CAST('{data_domain}' AS VARCHAR(255)) AS data_domain, "
                        "{feature_id} AS feature_id, "
                        "CAST('{table_name}' AS VARCHAR(255)) AS table_name "
                        "FROM (SELECT 1 AS dummy) AS t"
                    ).format(
                        entity_name=entity.name,
                        data_domain=self.__data_domain,
                        feature_id=id,
                        table_name=table_name
                    )
                )
            source_query = "(" + " UNION ALL ".join(select_rows) + ")"

            condition = "tgt.entity_name = src.entity_name AND tgt.data_domain = src.data_domain AND tgt.feature_id = src.feature_id"

            _merge_data(
                target_table=EFS_DB_COMPONENTS["feature_metadata"],
                target_table_schema=self.__repo,
                target_table_alias_name="tgt",
                source=source_query,
                source_alias_name="src",
                condition=condition,
                matched_details=None,
                non_matched_clause={
                    "action": "INSERT",
                    "columns": ["entity_name", 
                                "data_domain", 
                                "feature_id", 
                                "table_name"],
                    "values": ["src.entity_name", 
                               "src.data_domain", 
                               "src.feature_id", 
                               "src.table_name"]
                },
                temporal_clause="CURRENT VALIDTIME"
            )

        # Create tables in feature catalog.
        for table_name, columns in tables_to_create.items():
            _create_temporal_table(table_name=table_name,
                                   schema_name=self.__repo,
                                   columns=columns,
                                   primary_index=entity.columns,
                                   partition_by_range='feature_id  BETWEEN 0  AND 1000000  EACH 1',
                                   validtime_columns=['valid_start', 'valid_end'],
                                   skip_if_exists=True
                                   )

        return table_names

    def __process_entity(self):
        """
        DESCRIPTION:
            Insert the entity in the table _efs_entity_xref.

        PARAMETERS:
            None

        RETURNS:
            Entity object

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     df=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> entity = fp.__process_entity()
        """

        if isinstance(self.__entity, str):
            entity = Entity(name=self.__entity, columns=self.__entity)
        elif isinstance(self.__entity, list):
            entity = Entity(name="_".join(self.__entity), columns=self.__entity)
        else:
            entity = self.__entity

        return entity

    def __get_missing_features_from_catalog(self, id):
        """
        DESCRIPTION:
            Returns the missing feature ids from the feature catalog.

        PARAMETERS:
            id:
                Required Argument.
                Specifies the feature id(s) to be checked.
                Types: int or list of int.

        RETURNS:
            bool

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     df=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> missing_features = fp.__get_missing_features_from_catalog(id=[5, 6, 7])
        """
        ids = UtilFuncs._as_list(id)
        sql = """
        SELECT feature_id FROM "{}"."{}" WHERE feature_id IN ({})
        """.format(self.__repo, self.__feature_metadata_table, ", ".join((str(i) for i in ids)))
        recs = execute_sql(sql).fetchall()
        available_features = {rec[0] for rec in recs}
        return set(ids) - available_features

    def __get_features_entity_from_catalog(self):
        """
        DESCRIPTION:
            Get the features and entity from the feature catalog.

        PARAMETERS:
            None

        RETURNS:
            dict
                Dictionary with feature name as key and entity id as value.

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     df=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> features_entity = fp.__get_features_entity_from_catalog()
            >>> features_entity
            {'Jan': 'accounts', 'Feb': 'accounts', 'Mar': 'accounts', 'Apr': 'accounts'}
        """
        sql = """
        select distinct entity_id, feature_name from "{}".{}
        where data_domain = '{}'
        """.format(self.__repo, EFS_DB_COMPONENTS['feature_version'], self.__data_domain)
        recs = execute_sql(sql)

        return {rec[1]: rec[0] for rec in recs}

    @property
    def process_id(self):
        """
        DESCRIPTION:
            Returns the process id of the feature process.
            Note:
                This is the process id which is used to run the feature process.
                If user specifies process id, then this will be the same process id.
                If user does not specify process id, then this will be a new process id.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> fp.run()
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' started.
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' completed.
            True

            # Get the process id.
            >>> fp.process_id
            '587b9a68-7b57-11f0-abc5-a188eb171d46'
        """
        return self.__process_id

    @property
    def df(self):
        """
        DESCRIPTION:
            Returns the DataFrame which is used to ingest features
            while running the feature process.

        PARAMETERS:
            None

        RETURNS:
            teradataml DataFrame

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            # Create FeatureProcess.
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> fp.df
                 accounts    Feb    Jan    Mar    Apr    datetime
            0    Blue Inc   90.0   50.0   95.0  101.0  04/01/2017
            1    Alpha Co  210.0  200.0  215.0  250.0  04/01/2017
            2   Jones LLC  200.0  150.0  140.0  180.0  04/01/2017
            3  Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
            4     Red Inc  200.0  150.0  140.0    NaN  04/01/2017
            5  Orange Inc  210.0    NaN    NaN  250.0  04/01/2017
        """
        return self.__df

    @property
    def features(self):
        """
        DESCRIPTION:
            Returns the ingested features while running feature process.

        PARAMETERS:
            None

        RETURNS:
            list of Feature or list of str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> fp.features
            ["Jan", "Feb", "Mar", "Apr"]
            >>>
        """
        # If features are not available and user pass a process id,
        # then pull out from system.
        if self.__features is None and self.__process_id:
            # If process id is provided, then get the features from the process.
            process_details = _FSUtils._get_open_feature_process(
                self.__repo, self.__data_domain, self.__process_id)

            self.__features = [self.fs.get_feature(f) for f in process_details['feature_names']]
        return self.__features

    @property
    def entity(self):
        """
        DESCRIPTION:
            Returns the entity of the feature process.

        PARAMETERS:
            None

        RETURNS:
            Entity object

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> fp.entity
            'accounts'
        """
        # If Entity is not available and user pass a process id,
        # then pull out from system.
        if self.__entity is None and self.__process_id:
            # If process id is provided, then get the features from the process.
            process_details = _FSUtils._get_open_feature_process(
                self.__repo, self.__data_domain, self.__process_id)

            self.__entity = self.fs.get_entity(process_details['entity_id'])
        return self.__entity

    @property
    def data_domain(self):
        """
        DESCRIPTION:
            Returns the data domain of the feature process.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', 'sales')
            >>> df = DataFrame("sales")

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales_data',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> fp.data_domain
            'sales_data'
        """
        return self.__data_domain

    @property
    def filters(self):
        """
        DESCRIPTION:
            Returns the filters used while running the feature process.
            Note:
                * Property is updated only after every run of the feature process.

        PARAMETERS:
            None

        RETURNS:
            str or list of str or list of ColumnExpression or ColumnExpression.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data
            # Create a DataFrame from the sales data
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")
            # Create a FeatureProcess with filters on existing repository 'vfs_v1'.
            >>> fp = FeatureProcess(repo="test",
            ...                     data_domain='test_domain',
            ...                     object=df,
            ...                     entity='accounts',
            ...                     features=['Mar', 'Apr']
            ...                     )
            >>> fp.run(filters=[df.accounts=='Alpha Co', "accounts='Jones LLC'"])
            Process '108de34f-6b83-11f0-a819-f020ffe7fe09' started.
            Ingesting the features for filter 'accounts = 'Alpha Co'' to catalog.
            Ingesting the features for filter 'accounts='Jones LLC'' to catalog.
            Process '108de34f-6b83-11f0-a819-f020ffe7fe09' completed.
            True
            >>> fp.filters
            [<teradataml.dataframe.sql._SQLColumnExpression at 0x20ea1b24fa0>, "accounts='Jones LLC'"]
        """
        return self.__filters

    @property
    def as_of(self):
        """
        DESCRIPTION:
            Returns the time for which features are ingested.
            Note:
                * Property is updated only after every run of the feature process.

        PARAMETERS:
            None

        RETURNS:
            str or datetime.datetime

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")
            # Create a FeatureProcess with as_of period.
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> fp.run(as_of='2024-01-01 00:00:00+00:00')
            Process '7917d31f-6c7f-11f0-a99f-f020ffe7fe09' started.
            Process '7917d31f-6c7f-11f0-a99f-f020ffe7fe09' completed.
            True
            # Get the as_of timestamp.
            >>> fp.as_of
            ('2024-01-01 00:00:00+00:00', '9999-12-31 23:59:59.999999+00:00')
        """
        return self.__as_of

    @property
    def description(self):
        """
        DESCRIPTION:
            Returns the description of the feature process.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            # Create a FeatureProcess.
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain='sales',
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"],
            ...                     description="Feature process for sales data"
            ...                     )

            # Get the description of the feature process.
            >>> fp.description
            'Feature process for sales data'
        """
        return self.__description

    @property
    def start_time(self):
        """
        DESCRIPTION:
            Returns the start time of the feature process.

        PARAMETERS:
            None

        RETURNS:
            datetime.datetime

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )

            # Run the feature process.
            >>> fp.run()
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' started.
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' completed.
            True

            # Get the start time of the feature process.
            >>> fp.start_time
            datetime.datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc)
        """
        return self.__start_time

    @property
    def end_time(self):
        """
        DESCRIPTION:
            Returns the end time of the feature process.

        PARAMETERS:
            None

        RETURNS:
            datetime.datetime

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )

            # Run the feature process.
            >>> fp.run()
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' started.
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' completed.
            True

            >>> fp.end_time
            datetime.datetime(2023, 10, 1, 12, 5, 0, tzinfo=timezone.utc)
        """
        return self.__end_time

    @property
    def status(self):
        """
        DESCRIPTION:
            Returns the status of the feature process.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml import DataFrame, load_example_data, FeatureProcess
            >>> load_example_data('dataframe', ['sales'])
            >>> df = DataFrame("sales")

            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     object=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )

            # Run the feature process.
            >>> fp.run()
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' started.
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' completed.
            True

            >>> fp.status
            'COMPLETED'
        """
        return self.__status
    
    def __repr__(self):
        """
        DESCRIPTION:
            Returns a string representation of the FeatureProcess object.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            >>> fp = FeatureProcess(repo="vfs_test",
            ...                     data_domain="sales_data",
            ...                     df=df,
            ...                     entity="accounts",
            ...                     features=["Jan", "Feb", "Mar", "Apr"]
            ...                     )
            >>> fp
            FeatureProcess(repo=vfs_test, data_domain=sales_data)

            >>> fp.run()
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' started.
            Process '587b9a68-7b57-11f0-abc5-a188eb171d46' completed.
            True
            >>> fp
            FeatureProcess(repo=vfs_test, data_domain=sales_data, process_id=587b9a68-7b57-11f0-abc5-a188eb171d46)
        """
        return (
                f"FeatureProcess(repo={self.__repo}, data_domain={self.__data_domain}"
                + (f", process_id={self.__process_id}" if self.__process_id else "")
                + ")"
                )
