"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file implements the core framework that allows user to load BYOM to Vantage.
"""

from teradataml.dataframe.dataframe import DataFrame, in_schema
from teradataml.utils.validators import _Validators
from teradataml.context.context import _get_current_databasename, get_connection, get_context
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.exceptions import TeradataMlException
from teradatasql import OperationalError as SqlOperationalError
from teradatasqlalchemy.types import *
from teradatasqlalchemy.types import _TDType
from teradataml.dbutils.dbutils import _get_quoted_object_name, _create_table
from teradataml.common.utils import UtilFuncs
from teradataml.utils.dtypes import _Dtypes
from teradataml.catalog.model_cataloging_utils import __get_like_filter_expression_on_col
from teradataml.options.display import display
from teradataml.common.constants import ModelCatalogingConstants as mac
from teradataml.options.configure import configure
from teradataml.utils.utils import execute_sql
from teradataml.telemetry_utils.queryband import collect_queryband

validator = _Validators()


def __check_if_model_exists(model_id,
                            table_name,
                            schema_name=None,
                            raise_error_if_model_found=False,
                            raise_error_if_model_not_found=False):
    """
    DESCRIPTION:
        Internal function to check if byom model with given "model_id", exists or not.

    PARAMETERS:
        model_id:
            Required Argument.
            Specifies the name of the model identifier to check whether it exists or not.
            Types: str

        table_name:
            Required Argument.
            Specifies the table name that may or may not contain entry for the model.
            Types: str

        schema_name:
            Optional Argument.
            Specifies the name of the schema, to look out for table specified in
            "table_name". If not specified, then "table_name" is looked over in
            the current database.
            Types: str

        raise_error_if_model_found:
            Optional Argument.
            Specifies the flag to decide whether to raise error when model exists or not.
            Default Value: False (Do not raise exception)
            Types: bool

        raise_error_if_model_not_found:
            Optional Argument.
            Specifies the flag to decide whether to raise error when model is found or not.
            Default Value: False (Do not raise exception)
            Types: bool

    RETURNS:
        bool.

    RAISES:
        TeradataMlException - MODEL_ALREADY_EXISTS, MODEL_NOT_FOUND

    EXAMPLES:
        >>> meta_df = __check_if_model_exists("glm_out")
    """
    # If external model, create DataFrame on table specified in parameters within
    # current schema. Else, create DataFrame on table & schema specified in parameters.
    schema_name = schema_name if schema_name is not None else _get_current_databasename()
    models_meta_df = DataFrame(in_schema(schema_name, table_name))
    models_meta_df = models_meta_df[models_meta_df.model_id == model_id]

    num_rows = models_meta_df.shape[0]

    if raise_error_if_model_found:
        if num_rows == 1:
            # If model with name 'name' already exists.
            raise TeradataMlException(Messages.get_message(MessageCodes.MODEL_ALREADY_EXISTS,
                                                           model_id),
                                      MessageCodes.MODEL_ALREADY_EXISTS)

    if raise_error_if_model_not_found:
        if num_rows == 0:
            # 'name' MODEL_NOT_FOUND
            raise TeradataMlException(Messages.get_message(MessageCodes.MODEL_NOT_FOUND,
                                                           model_id, ''),
                                      MessageCodes.MODEL_NOT_FOUND)

    return True if num_rows == 1 else False


def __set_validate_catalog_parameters(table_name=None, schema_name=None):
    """
     DESCRIPTION:
        Internal function to set the table and schema name
        for byom catalog API's according to the model cataloging
        parameters and the user inputs.

    PARAMETERS:
        table_name:
            Optional Argument.
            Specifies the name of the byom catalog table.
            Notes:
                * One must either specify this argument or set the byom model catalog table
                    name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in function call take precedence and is used for
                    function execution when saving an model.
            Types: str

        schema_name:
            Optional Argument.
            Specifies the name of the schema/database in which the table specified in
            "table_name" is looked up.
            Notes:
                * One must either specify this argument or set the byom model catalog schema
                    name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in function call take precedence and is used for
                    function execution when saving an model.
            Types: str

    RETURNS:
        List of "table_name" and "schema_name".

    RAISES:
        ValueError

    EXAMPLES:
        >>> __set_validate_catalog_parameters(table_name = "model_catalog_table",
                                              schema_name="model_catalog_schema")
    """
    # Raise an error if schema_name is provided and table_name is not provided
    _Validators._validate_dependent_argument("schema_name", schema_name, "table_name", table_name)

    # Set the schema_name to default schema_name if only table_name is provided.
    # Set the table_name and schema_name to model catalog session level variables if not provided.
    schema_name = schema_name if schema_name is not None else\
        _get_current_databasename() if table_name is not None else configure._byom_model_catalog_database
    table_name = table_name if table_name is not None else configure._byom_model_catalog_table

    # Check whether table information is present and not None.
    additional_error = Messages.get_message(MessageCodes.EITHER_FUNCTION_OR_ARGS, "catalog", "set_byom_catalog",
                                                "catalog", "")
    validator._validate_argument_is_not_None(table_name, "table_name", additional_error)

    return [table_name, schema_name]


@collect_queryband(queryband="stByomCtlg")
def set_byom_catalog(table_name,
                     schema_name=None):
    """
        DESCRIPTION:
            Function to set the BYOM model catalog information to be used by
            BYOM model cataloging APIs such as:
                * delete_byom
                * list_byom
                * retrieve_byom
                * save_byom
                * set_license

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the name of the table to be used for BYOM model cataloging.
                This table will be used for saving, retrieving BYOM model information
                by BYOM model cataloging APIs.
                Types: str.

            schema_name:
                Optional Argument.
                Specifies the name of the schema/database in which the table specified in
                "table_name" is looked up. If not specified, then table is looked
                up in current schema/database.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> from teradataml import set_byom_catalog

            # Example 1 - Set global parameters table_name = 'model_table_name' and schema_name = 'model_schema_name';
            >>> set_byom_catalog(table_name='model_table_name', schema_name='model_schema_name')
            The model cataloging parameters are set to table_name='model_table_name' and schema_name='model_schema_name'

    """

    # Let's perform argument validations.
    # Create argument information matrix to do parameter checking.
    __arg_info_matrix = []
    __arg_info_matrix.append(["table_name", table_name, False, str, True])
    __arg_info_matrix.append(["schema_name", schema_name, True, str, True])

    # Make sure that a correct type of values has been supplied to the arguments.
    validator._validate_function_arguments(__arg_info_matrix)

    schema_name = schema_name if schema_name is not None else _get_current_databasename()

    # Perform required validations for the API.
    # Check whether the table given exist or not.
    conn = get_connection()
    validator._check_table_exists(conn, table_name, schema_name)

    configure._byom_model_catalog_table = table_name
    configure._byom_model_catalog_database = schema_name
    print("The model cataloging parameters are set to table_name='{}' and "
          "schema_name='{}'".format(table_name, schema_name))


@collect_queryband(queryband="svByom")
def save_byom(model_id,
              model_file,
              table_name=None,
              schema_name=None,
              additional_columns=None,
              additional_columns_types=None):
    """
    DESCRIPTION:
        Function to save externally trained models in Teradata Vantage in the
        specified table. Function allows user to save various models stored in
        different formats such as PMML, MOJO etc. If the specified model table
        exists in Vantage, model data is saved in the same, otherwise model table
        is created first based on the user parameters and then model data is
        saved. See below 'Note' section for more details.
        
        Notes:
            If user specified table exists, then
                a. Table must have at least two columns with names and types as
                   specified below:
                   * 'model_id' of type VARCHAR of any length and
                   * 'model' column of type BLOB.
                b. User can choose to have the additional columns as well to store
                   additional information of the model. This information can be passed
                   using "additional_columns" parameter. See "additional_columns"
                   argument description for more details.
            If user specified table does not exist, then
                a. Function creates the table with the name specified in "table_name".
                b. Table is created in the schema specified in "schema_name". If
                   "schema_name" is not specified, then current schema is considered
                   for "schema_name".
                c. Table is created with columns:
                    * 'model_id' with type specified in "additional_columns_types". If
                      not specified, table is created with 'model_id' column as VARCHAR(128).
                    * 'model' with type specified in "additional_columns_types". If
                      not specified, table is created with 'model' column as BLOB.
                    * Columns specified in "additional_columns" parameter. See "additional_columns"
                      argument description for more details.
                    * Datatypes of these additional columns are either taken from
                      the values passed to "additional_columns_types" or inferred
                      from the values passed to the "additional_columns". See
                      "additional_columns_types" argument description for more details.

    PARAMETERS:
        model_id:
            Required Argument.
            Specifies the unique model identifier for model.
            Types: str.

        model_file:
            Required Argument.
            Specifies the absolute path of the file which has model information.
            Types: str

        table_name:
            Optional Argument.
            Specifies the name of the table where model is saved. If "table_name"
            does not exist, this function creates table according to "additional_columns"
            and "additional_columns_types".
            Notes:
                * One must either specify this argument or set the byom model catalog table
                    name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in save_byom() take precedence and is used for
                    function execution when saving an model.
            Types: str

        schema_name:
            Optional Argument.
            Specifies the name of the schema/database in which the table specified in
            "table_name" is looked up.
            Notes:
                * One must either specify this argument and table_name argument
                    or set the byom model catalog schema and table name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in save_byom() take precedence and is used for
                    function execution when saving an model.
                * If user specifies schema_name argument table_name argument has to be specified,
                    else exception is raised.
            Types: str

        additional_columns:
            Optional Argument.
            Specifies the additional information about the model to be saved in the
            model table. Additional information about the model is passed as key value
            pair, where key is the name of the column and value is data to be stored
            in that column for the model being saved.
            Notes:
                 1. Following are the allowed types for the values passed in dictionary:
                    * int
                    * float
                    * str
                    * bool
                    * datetime.datetime
                    * datetime.date
                    * datetime.time
                 2. "additional_columns" does not accept keys model_id and model.
            Types: dict

        additional_columns_types:
            Optional Argument.
            Specifies the column type of additional columns. These column types are used
            while creating the table using the columns specified in "additional_columns"
            argument. Additional column datatype information is passed as key value pair
            with key being the column name and value as teradatasqlalchemy.types.
            Notes:
                 1. If, any of the column type for additional columns are not specified in
                    "additional_columns_types", it then derives the column type according
                    the below table:
                    +---------------------------+-----------------------------------------+
                    |     Python Type           |        teradatasqlalchemy Type          |
                    +---------------------------+-----------------------------------------+
                    | str                       | VARCHAR(1024)                           |
                    +---------------------------+-----------------------------------------+
                    | int                       | INTEGER                                 |
                    +---------------------------+-----------------------------------------+
                    | bool                      | BYTEINT                                 |
                    +---------------------------+-----------------------------------------+
                    | float                     | FLOAT                                   |
                    +---------------------------+-----------------------------------------+
                    | datetime                  | TIMESTAMP                               |
                    +---------------------------+-----------------------------------------+
                    | date                      | DATE                                    |
                    +---------------------------+-----------------------------------------+
                    | time                      | TIME                                    |
                    +---------------------------+-----------------------------------------+
                 2. Columns model_id, with column type as VARCHAR and model, with column type
                    as BLOB are mandatory for table. So, for the columns model_id and model,
                    acceptable values for "additional_columns_types" are VARCHAR and BLOB
                    respectively.
                 3. This argument is ignored if table exists.
            Types: dict

        Note:
            The following table describes the system behaviour in different scenarios:
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            |         In save_byom()       |          In set_byom_catalog()      |     System Behavior                 |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | table_name     | schema_name | table_name            | schema_name |                                     |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Set         | Set                   | Set         |  schema_name and table_name in      |
            |                |             |                       |             |  save_byom() are used for           |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            |  Set        | Not set               | Not set     |  schema_name and table_name in      |
            |                |             |                       |             |  save_byom() is used for            |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Not set     | Set                   | Set         |  table_name from save_byom()        |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Set         | Set                   | Set         |  Exception is raised.               |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Set         |  table_name and schema_name         |
            |                |             |                       |             |  from set_byom_catalog()            |
            |                |             |                       |             |  are used for function execution.   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Not set     |  table_name from set_byom_catalog() |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Not set               | Not set     |  Exception is raised                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+

    RETURNS:
        None.

    RAISES:
        TeradataMlException, TypeError, ValueError

    EXAMPLES:

        >>> import teradataml, os, datetime
        >>> model_file = os.path.join(os.path.dirname(teradataml.__file__), 'data', 'models', 'iris_kmeans_model')
        >>> from teradataml import save_byom

        # Example 1 - Create table "byom_model" with additional columns by specifying the type
        #             of the columns as below and save the model in it.
        #             +---------------------------+-----------------------------------------+
        #             |     Column name           |        Column Type                      |
        #             +---------------------------+-----------------------------------------+
        #             | model_id                  | VARCHAR(128)                            |
        #             +---------------------------+-----------------------------------------+
        #             | model                     | BLOB                                    |
        #             +---------------------------+-----------------------------------------+
        #             | Description               | VARCHAR(2000)                           |
        #             +---------------------------+-----------------------------------------+
        #             | UserId                    | NUMBER(5)                               |
        #             +---------------------------+-----------------------------------------+
        #             | ProductionReady           | BYTEINT                                 |
        #             +---------------------------+-----------------------------------------+
        #             | ModelEfficiency           | NUMBER(11,10)                           |
        #             +---------------------------+-----------------------------------------+
        #             | ModelSavedTime            | TIMESTAMP                               |
        #             +---------------------------+-----------------------------------------+
        #             | ModelGeneratedDate        | DATE                                    |
        #             +---------------------------+-----------------------------------------+
        #             | ModelGeneratedTime        | TIME                                    |
        #             +---------------------------+-----------------------------------------+
        #
        >>> save_byom('model1',
        ...           model_file,
        ...           'byom_models',
        ...           additional_columns={"Description": "KMeans model",
        ...                               "UserId": "12345",
        ...                               "ProductionReady": False,
        ...                               "ModelEfficiency": 0.67412,
        ...                               "ModelSavedTime": datetime.datetime.now(),
        ...                               "ModelGeneratedDate":datetime.date.today(),
        ...                               "ModelGeneratedTime": datetime.time(hour=0,minute=5,second=45,microsecond=110)
        ...                               },
        ...           additional_columns_types={"Description": VARCHAR(2000),
        ...                                    "UserId": NUMBER(5),
        ...                                    "ProductionReady": BYTEINT,
        ...                                    "ModelEfficiency": NUMBER(11,10),
        ...                                    "ModelSavedTime": TIMESTAMP,
        ...                                    "ModelGeneratedDate": DATE,
        ...                                    "ModelGeneratedTime": TIME}
        ...           )
        Created the table 'byom_models' as it does not exist.
        Model is saved.
        >>>

        # Example 2 - Create table "byom_model1" in "test" DataBase, with additional columns
        #             by not specifying the type of the columns and once table is created,
        #             save the model in it.
        >>> save_byom('model1',
        ...           model_file,
        ...           'byom_models1',
        ...           additional_columns={"Description": "KMeans model",
        ...                               "UserId": "12346",
        ...                               "ProductionReady": False,
        ...                               "ModelEfficiency": 0.67412,
        ...                               "ModelSavedTime": datetime.datetime.now(),
        ...                               "ModelGeneratedDate":datetime.date.today(),
        ...                               "ModelGeneratedTime": datetime.time(hour=0,minute=5,second=45,microsecond=110)
        ...                               },
        ...           schema_name='test'
        ...           )
        Created the table 'byom_models1' as it does not exist.
        Model is saved.
        >>>

        # Example 3 - Save the model in the existing table "byom_models".
        >>> save_byom('model2',
        ...           model_file,
        ...           'byom_models',
        ...           additional_columns={"Description": "KMeans model duplicated"}
        ...           )
        Model is saved.
        >>>

        # Example 4 - Set the cataloging parameters and save the model
        #             in the existing table "byom_models".
        >>> set_byom_catalog(table_name='byom_models', schema_name='alice')
        The model cataloging parameters are set to table_name='byom_models' and schema_name='alice'
        >>> save_byom('model3', model_file=model_file)
        Model is saved.

        # Example 4 - Set the cataloging table_name to 'byom_models'
        #             and save the model in table 'byom_licensed_models' other than model catalog table.
        >>> set_byom_catalog(table_name='byom_models', schema_name='alice')
        The model cataloging parameters are set to table_name='byom_models' and schema_name='alice'
        >>> save_byom('licensed_model2', model_file=model_file, table_name='byom_licensed_models',
        ...           additional_columns={"license_data": "A5sUL9KU_kP35Vq"})
        Created the model table 'byom_licensed_models' as it does not exist.
        Model is saved.
        >>>
    """
    try:
        # Let's perform argument validations.
        # Create argument information matrix to do parameter checking.
        __arg_info_matrix = []
        __arg_info_matrix.append(["model_id", model_id, False, str, True])
        __arg_info_matrix.append(["model_file", model_file, False, str, True])
        __arg_info_matrix.append(["table_name", table_name, True, str, True])
        __arg_info_matrix.append(["schema_name", schema_name, True, str, True])
        __arg_info_matrix.append(["additional_columns", additional_columns, True, dict])
        __arg_info_matrix.append(["additional_columns_types", additional_columns_types, True, dict])

        # Make sure that a correct type of values has been supplied to the arguments.
        validator._validate_function_arguments(__arg_info_matrix)

        # Set the table and schema name according to the model cataloging parameters and the user inputs.
        table_name, schema_name = __set_validate_catalog_parameters(table_name, schema_name)

        # Change the additional_columns_types and additional_columns to dictionary if
        # it is None so that retrieval would be easy.
        if additional_columns_types is None:
            additional_columns_types = {}

        if additional_columns is None:
            additional_columns = {}

        # Check if model_id or model in additional columns.
        for column in ["model_id", "model"]:
            if column in additional_columns:
                error_code = MessageCodes.NOT_ALLOWED_VALUES
                error_msg = Messages.get_message(error_code, column, "additional_columns")
                raise TeradataMlException(error_msg, error_code)

        # Add model_id and model columns information to lists
        # which will be used in creating insert query.
        column_names = ["model_id", "model"]
        insert_parameters = [model_id, UtilFuncs._get_file_contents(model_file, True)]

        connection = get_connection()
        # Check if table already exists.
        # If exists, extract required information about table columns types
        # else extract from additional_columns_types.
        # Also validate model_id against allowed length.
        table_exists = connection.dialect.has_table(connection, table_name=table_name,
                                                    schema=schema_name, table_only=True)
        if table_exists:
            # Check if model exists or not. If exists, raise error.
            __check_if_model_exists(
                model_id, table_name, schema_name, raise_error_if_model_found=True)

            # Gather column name and type information from existing table
            existing_table_df = DataFrame(in_schema(schema_name, table_name))
            existing_columns_name_sql_type_dict = existing_table_df._td_column_names_and_sqlalchemy_types

            existing_table_model_id_type = existing_columns_name_sql_type_dict["model_id"]
            # Validate length of model_id argument
            _Validators._validate_column_value_length("model_id", model_id, existing_table_model_id_type.length,
                                                      "save the model")
        else:
            # Validate length of model_id argument
            _Validators._validate_column_value_length("model_id", model_id, 128, "save the model")

            columns_name_type_dict = {"model_id": additional_columns_types.get("model_id", VARCHAR(128)),
                                      "model": additional_columns_types.get("model", BLOB)}

        # List of columns whose type is not provided in additional_columns_types.
        undefined_column_types = []

        # If user passes any additional columns data, extract that also to insert it
        # in table.
        # If table exists, use the information about column types from existing table,
        # ignore additional_columns_types argument.
        if additional_columns:
            for col_name, col_value in additional_columns.items():
                # Before proceeding further, validate the additional column data.
                # One should not pass custom types such as list, dict, user defined
                # objects etc.
                _Validators._validate_py_type_for_td_type_conversion(type(col_value), "additional_columns")

                # If table exists, use same column data type.
                # If table does not exist and column type is not specified
                # in additional column types, derive the appropriate one.
                if table_exists:
                    col_name_lower = col_name.lower()
                    if col_name_lower in existing_columns_name_sql_type_dict:
                        col_type = existing_columns_name_sql_type_dict[col_name_lower]
                    else:
                        raise TeradataMlException(Messages.get_message(MessageCodes.INSERTION_INCOMPATIBLE),
                                                  MessageCodes.INSERTION_INCOMPATIBLE)
                else:
                    col_type = additional_columns_types.get(
                        col_name, _Dtypes._python_type_to_teradata_type(type(col_value)))
                    # Update columns_name_type_dict
                    columns_name_type_dict[col_name] = col_type

                    # Collect undefined column types to show warning.
                    if additional_columns_types.get(col_name) is None:
                        undefined_column_types.append(col_name)

                # Validate the length of input varchar columns against allowed column lengths.
                if isinstance(col_type, VARCHAR):
                    _Validators._validate_column_value_length(col_name, col_value, col_type.length,
                                                              "save the model")

                # Add current column name and corresponding value in respective lists.
                column_names.append(col_name)
                insert_parameters.append(col_value)

        # If table doesn't exist, create one using additional_columns_types
        if not table_exists:
            __mandatory_columns_types = {"model_id": VARCHAR, "model": BLOB}
            is_mandatory_col_type_expected = lambda c_name, c_type: \
                c_type == __mandatory_columns_types[c_name] or type(c_type) == __mandatory_columns_types[c_name]

            # Validate additional_columns_types.
            for c_name, c_type in additional_columns_types.items():
                # Check if model_id & model columns have appropriate types.
                if c_name in __mandatory_columns_types and not is_mandatory_col_type_expected(c_name, c_type):
                    error_code = MessageCodes.INVALID_COLUMN_DATATYPE
                    err_msg = Messages.get_message(error_code,
                                                   c_name,
                                                   "additional_columns_types",
                                                   "Valid",
                                                   "[{}]".format(__mandatory_columns_types[c_name].__name__)
                                                   )
                    raise TeradataMlException(err_msg, error_code)

                # Check if value passed to additional_columns_types is a valid type or not.
                # User can pass a class or an object of a class from teradatasqlalchemy.types .
                # So, Check if c_type is either a subclass of TDType or a TDType.
                # isinstance(c_type, _TDType), checks if c_type is an object of teradatasqlalchemy.types
                # issubclass(c_type, _TDType), checks if c_type is a proper Teradata type or not.
                # However, issubclass accepts only class in its 1st parameter so check if c_type is
                # a class or not, before passing it to issubclass.
                elif not (isinstance(c_type, _TDType) or (isinstance(c_type, type) and issubclass(c_type, _TDType))):
                    error_code = MessageCodes.INVALID_COLUMN_DATATYPE
                    err_msg = Messages.get_message(
                        error_code, c_name, "additional_columns_types", "Valid", "teradatasqlalchemy.types")
                    raise TeradataMlException(err_msg, error_code)

            if len(undefined_column_types) > 0:
                warnings.warn("Specified table does not exist and data types of {0} "\
                        "columns are not provided. Taking default datatypes."\
                              .format(", ".join(undefined_column_types)), stacklevel=2)

            # Create empty vantage table using sqlalchemy object.
            _create_table(
                table_name, columns_name_type_dict, primary_index="model_id", schema_name=schema_name)
            print("Created the model table '{}' as it does not exist.".format(table_name))

        # If schema is specified, then concatenate schema name with table name.
        if schema_name:
            table_name = in_schema(schema_name, table_name)

        # Generate insert query.
        columns_clause = ", ".join(column_names)
        values_clause = ", ".join(("?" for _ in range(len(column_names))))
        insert_model = f"insert into {table_name} ({columns_clause}) values ({values_clause});"
        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()
        execute_sql(insert_model, tuple([insert_parameters]))
        print("Model is saved.")

    except (SqlOperationalError, TeradataMlException, TypeError, ValueError):
        raise
    except Exception as err:
        error_code = MessageCodes.MODEL_CATALOGING_OPERATION_FAILED
        raise TeradataMlException(Messages.get_message(error_code, "save", str(err)), error_code)


@collect_queryband(queryband="dltByom")
def delete_byom(model_id, table_name=None, schema_name=None):
    """
    DESCRIPTION:
        Delete a model from the user specified table in Teradata Vantage.

    PARAMETERS:
        model_id:
            Required Argument.
            Specifies the unique model identifier of the model to be deleted.
            Types: str

        table_name:
            Optional Argument.
            Specifies the name of the table to delete the model from.
            Notes:
                * One must either specify this argument or set the byom model catalog table
                    name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in delete_byom() take precedence and is used for
                    function execution.
            Types: str

        schema_name:
            Optional Argument.
            Specifies the name of the schema/database in which the table specified in
            "table_name" is looked up.
            Notes:
                * One must either specify this argument and table_name argument
                    or set the byom model catalog schema and table name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in delete_byom() take precedence and is used for
                    function execution.
                * If user specifies schema_name argument table_name argument has to be specified,
                    else exception is raised.
            Types: str

        Note:
            The following table describes the system behaviour in different scenarios:
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            |         In delete_byom()     |          In set_byom_catalog()      |     System Behavior                 |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | table_name     | schema_name | table_name            | schema_name |                                     |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Set         | Set                   | Set         |  schema_name and table_name in      |
            |                |             |                       |             |  delete_byom() are used for         |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Set         | Not set               | Not set     |  schema_name and table_name in      |
            |                |             |                       |             |  delete_byom() is used for          |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Set         |  table_name from delete_byom()      |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Set         | Set                   | Set         |  Exception is raised.               |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Set         |  table_name and schema_name         |
            |                |             |                       |             |  from set_byom_catalog()            |
            |                |             |                       |             |  are used for function execution.   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Not set     |  table_name from set_byom_catalog() |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Not set               | Not set     |  Exception is raised                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+

    RETURNS:
        None.

    RAISES:
        TeradataMlException

    EXAMPLES:

        >>> import teradataml, os, datetime
        >>> model_file = os.path.join(os.path.dirname(teradataml.__file__), 'data', 'models', 'iris_kmeans_model')
        >>> from teradataml import save_byom, delete_byom
        >>> save_byom('model3', model_file, 'byom_models')
        Model is saved.
        >>> save_byom('model4', model_file, 'byom_models', schema_name='test')
        Model is saved.
        >>> save_byom('model5', model_file, 'byom_models', schema_name='test')
        Model is saved.
        >>> save_byom('model4', model_file, 'byom_models')
        Model is saved.
        >>> save_byom('model5', model_file, 'byom_models')
        Model is saved.

        # Example 1 - Delete a model with id 'model3' from the table byom_models.
        >>> delete_byom(model_id='model3', table_name='byom_models')
        Model is deleted.
        >>>

        # Example 2 - Delete a model with id 'model4' from the table byom_models
        #             and the table is in "test" DataBase.
        >>> delete_byom(model_id='model4', table_name='byom_models', schema_name='test')
        Model is deleted.
        >>>

        # Example 3 - Delete a model with id 'model4' from the model cataloging table 'byom_models'
        #             set by set_byom_catalog().
        >>> set_byom_catalog(table_name='byom_models', schema_name='alice')
        The model cataloging parameters are set to table_name='byom_models' and schema_name='alice'
        >>> delete_byom(model_id='model4')
        Model is deleted.

        # Example 4 - Set the cataloging table_name to 'byom_models'
        #             and delete the model in table other than model catalog table 'byom_licensed_models'.
        >>> set_byom_catalog(table_name='byom_models', schema_name= 'alice')
        The model cataloging parameters are set to table_name='byom_models' and schema_name='alice'
        >>> save_byom('licensed_model2', model_file=model_file, table_name='byom_licensed_models')
        Created the model table 'byom_licensed_models' as it does not exist.
        Model is saved.
        >>> delete_byom(model_id='licensed_model2', table_name='byom_licensed_models')
        Model is deleted.

    """

    # Let's perform argument validations.
    # Create argument information matrix to do parameter checking
    __arg_info_matrix = []
    __arg_info_matrix.append(["model_id", model_id, False, str, True])
    __arg_info_matrix.append(["table_name", table_name, True, str, True])
    __arg_info_matrix.append(["schema_name", schema_name, True, str, True])

    # Make sure that a correct type of values has been supplied to the arguments.
    validator._validate_function_arguments(__arg_info_matrix)

    # Set the table and schema name according to the model cataloging parameters and the user inputs.
    table_name, schema_name = __set_validate_catalog_parameters(table_name, schema_name)

    # Before proceed further, check whether table exists or not.
    conn = get_connection()
    if not conn.dialect.has_table(conn, table_name=table_name, schema=schema_name, table_only=True):
        error_code = MessageCodes.MODEL_CATALOGING_OPERATION_FAILED
        error_msg = Messages.get_message(
            error_code, "delete", 'Table "{}.{}" does not exist.'.format(schema_name, table_name))
        raise TeradataMlException(error_msg, error_code)

    # Let's check if the user created the model since only the creator can delete it
    __check_if_model_exists(model_id, table_name, schema_name, raise_error_if_model_not_found=True)

    # Get the FQTN before deleting the model.
    table_name = _get_quoted_object_name(schema_name, table_name)

    try:
        delete_model = f"delete from {table_name} where model_id = (?)"
        # Empty queryband buffer before SQL call.
        UtilFuncs._set_queryband()
        execute_sql(delete_model, tuple([model_id]))
        print("Model is deleted.")

    except (SqlOperationalError, TeradataMlException):
        raise
    except Exception as err:
        error_code = MessageCodes.MODEL_CATALOGING_OPERATION_FAILED
        error_msg = Messages.get_message(error_code, "delete", str(err))
        raise TeradataMlException(error_msg, error_code)


@collect_queryband(queryband="stLcns")
def set_license(license,
                table_name=None,
                schema_name=None,
                source='string'):
    """
        DESCRIPTION:
            The set_license() function allows a user to set the license information
            associated with the externally generated model in a session level variable
            which is required by H2O DAI models. It is used by the retrieve_byom()
            function to retrieve the license information while retrieving the specific model.
            If specified table name does not exist and is not the same as BYOM catalog tables,
            then this function creates the table and stores the license information;
            otherwise, this function just validates and sets the license information.

            The license can be set by passing the license in the following ways:
                * Passing the license as a variable;
                * Passing the column name in the model table itself;
                * Passing the table and the column name containing the license;
                * Passing the license in a file.

        PARAMETERS:
            license:
                Required Argument.
                Specifies the license key information that can be passed as:
                    * a variable.
                    * in a file.
                    * name of the column containing license information in a table
                      specified by "table_name" argument.
                Note:
                    Argument "source" must be set accordingly.
                Types: str

            table_name:
                Optional Argument.
                Specifies the table name containing the license information if "source" is 'column',
                otherwise specifies the table to store the license into.
                Note:
                    Argument "table_name" and "schema_name"
                    both should be specified or both should be None.
                Types: str

            schema_name:
                Optional Argument.
                Specifies the name of the schema in which the table specified in
                "table_name" is looked up.
                Note:
                    Argument "table_name" and "schema_name"
                    both should be specified or both should be None.
                Types: str

            source:
                Required Argument.
                Specifies whether license key specified in "license" is a string, file
                or column name.
                Default value: string
                Permitted values: string, file, column

        RETURNS:
            None.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> import os
            >>> from teradataml import save_byom, retrieve_byom, get_context, set_license, set_byom_catalog

            # Example 1: When license is passed as a string.
            >>> set_license(license='eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI',
            ...             table_name=None, schema_name=None, source='string')
            The license parameters are set.
            The license is : eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI

            # Example 2: When license is stored in a file and file is passed as input to "license".
            #            "source" must be set to "file".
            >>> license_file = os.path.join(os.path.dirname(teradataml.__file__),
            ...                             'data', 'models', 'License_file.txt')
            >>> set_license(license=license_file, source='file')
            The license parameters are set.
            The license is: license_string

            # Example 3: When license is present in the byom model catalog table itself.
            # Store a model with license information in the model table.
            >>> model_file = os.path.join(os.path.dirname(teradataml.__file__),
            ...                           'data', 'models', 'iris_kmeans_model')
            >>> save_byom('licensed_model1', model_file, 'byom_licensed_models',
            ...           additional_columns={"license_data": "A5sUL9KU_kP35Vq"})
            Created the model table 'byom_licensed_models' as it does not exist.
            Model is saved.
            >>> set_byom_catalog(table_name='byom_licensed_models', schema_name='alice')
            The model cataloging parameters are set to table_name='byom_licensed_models'
            and schema_name='alice'
            >>> set_license(license='license_data', source='column')
            The license parameters are set.
            The license is present in the table='byom_licensed_models',schema='alice' and
            column='license_data'.

            # Example 4: Set the license information using the license stored in a column
            #            'license_key' of a table 'license_table'.
            # Create a table and insert the license information in the table.
            >>> license = 'eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI'
            >>> lic_table = 'create table license (id integer between 1 and 1,
            license_key varchar(2500)) unique primary index(id);'
            >>> execute_sql(lic_table)
            <sqlalchemy.engine.cursor.LegacyCursorResult object at 0x000001DC4F2EE9A0>
            >>> execute_sql("insert into license values (1, 'peBVRtjA-ib')")
            <sqlalchemy.engine.cursor.LegacyCursorResult object at 0x000001DC4F2EEF10>
            >>> set_license(license='license_key', table_name='license', schema_name='alice',
            ...             source='column')
            The license parameters are set.
            The license is present in the table='license', schema='alice' and column='license_key'.

            # Example 5: Set License when license is passed as a string, table
            # and schema name are passed. Since table does not exist, table is
            # created and license is stored in the table.
            >>> set_license(license="eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI",
            ...             table_name='license_table', schema_name='alice', source='string')
            The license parameters are set.
            The license is present in the table='license_table', schema='alice' and column='license'.

            # Example 6: Set License when license is passed as a file
            # and table and schema name are passed. Since table does not exist,
            # table is created and license is stored in the table.
            >>> set_license(license=license_file, table_name='license_t1', schema_name= 'alice', source='file')
            The license parameters are set.
            The license is present in the table='license_t1', schema='alice' and column='license'.
    """
    # Create argument information matrix for validations.
    __arg_info_matrix = []
    __arg_info_matrix.append(["license", license, False, str, True])
    __arg_info_matrix.append(["source", source, True, str, True, mac.LICENSE_SOURCE.value])
    __arg_info_matrix.append(["table_name", table_name, True, str, True])
    __arg_info_matrix.append(["schema_name", schema_name, True, str, True])

    # Make sure that a correct type of values has been supplied to the arguments.
    validator._validate_function_arguments(__arg_info_matrix)

    # Make sure if table_name is provided, schema_name is also provided and vice_versa.
    validator._validate_mutually_inclusive_arguments(table_name, "table_name", schema_name,
                                                     "schema_name")

    source = source.lower()
    if source == 'column':
        conn = get_connection()
        additional_error = ""
        if table_name is None:
            # Assign the table and schema name to model cataloging table and schema as
            # table_name is not provided.
            table_name = configure._byom_model_catalog_table
            schema_name = configure._byom_model_catalog_database

            # Raise an error if the catalog information is not set or table name is not passed
            additional_error = Messages.get_message(MessageCodes.EITHER_FUNCTION_OR_ARGS, "catalog",
                                                    "set_byom_catalog", "catalog", "")
            validator._validate_argument_is_not_None(table_name, "table_name", additional_error)

        if validator._check_table_exists(conn, table_name, schema_name,
                                         raise_error_if_does_not_exists=True,
                                         additional_error=additional_error):

            # Validate the column name provided in the license argument
            # to check if column exists or not.
            license_table = DataFrame(in_schema(schema_name=schema_name,
                                                table_name=table_name))

            _Validators._validate_column_exists_in_dataframe(license,
                                                             license_table._metaexpr,
                                                             for_table=True)

            # Set the configuration option _byom_model_catalog_license,
            # _byom_model_catalog_license_source, _byom_model_catalog_license_table,
            # _byom_model_catalog_license_database.

            configure._byom_model_catalog_license = license
            configure._byom_model_catalog_license_source = 'column'
            configure._byom_model_catalog_license_table = table_name
            configure._byom_model_catalog_license_database = schema_name

            print("The license parameters are set.")
            print("The license is present in the table='{}', schema='{}' and column='{}'"
                  ".".format(configure._byom_model_catalog_license_table,
                             configure._byom_model_catalog_license_database,
                             configure._byom_model_catalog_license))
    else:
        # Set the configuration option _byom_model_catalog_license.
        # If license is passed in a file, extract the same from the file and then set the option.
        configure._byom_model_catalog_license = license if source == 'string' else \
            UtilFuncs._get_file_contents(license)

        if table_name is None:
            # Set the configuration option _byom_model_catalog_license_source.
            # If table_name is not provided set the value to 'string' and print the information.
            configure._byom_model_catalog_license_source = 'string'
            print("The license parameters are set.")
            print("The license is: {}".format(configure._byom_model_catalog_license))

        else:
            conn = get_connection()
            if not validator._check_table_exists(conn, table_name, schema_name, False):
                # Create the license table with constraints
                license_table = table_name
                columns_to_create = {"id": NUMBER,
                                     "license": VARCHAR}

                try:
                    _create_table(license_table, columns_to_create, primary_index="id",
                                  schema_name=schema_name, check_constraint='id between 1 and 1')
                    query = "insert into {}.{} values (1, '{}')".format(
                        schema_name, license_table, configure._byom_model_catalog_license)

                    # Empty queryband buffer before SQL call.
                    UtilFuncs._set_queryband()
                    execute_sql(query)
                except:
                    raise

                configure._byom_model_catalog_license = 'license'
                configure._byom_model_catalog_license_source = 'column'
                configure._byom_model_catalog_license_table = license_table
                configure._byom_model_catalog_license_database = schema_name

                print("The license parameters are set.")
                print("The license is present in the table='{}', schema='{}' and column='{}'"
                      ".".format(configure._byom_model_catalog_license_table,
                                 configure._byom_model_catalog_license_database,
                                 configure._byom_model_catalog_license))
            else:
                raise TeradataMlException(Messages.get_message(MessageCodes.TABLE_ALREADY_EXISTS, table_name),
                                          MessageCodes.TABLE_ALREADY_EXISTS)


@collect_queryband(queryband="gtLcns")
def get_license():
    """
        DESCRIPTION:
            Get the license information set by set_license() function at the session level.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            >>> import os, teradataml
            >>> from teradataml import save_byom, get_license, set_license

            # Example 1: When license is passed as a string.
            >>> set_license(license='eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI',
                            source='string')
            The license parameters are set.
            The license is: eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI
            >>> get_license()
            The license is: eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI

            # Example 2: When license is present in the column='license_data' and table='byom_licensed_models'.
            >>> set_license(license='license_data', table_name='byom_licensed_models', schema_name='alice',
                            source='column')
            The license parameters are set.
            The license is present in the table='byom_licensed_models', schema='alice' and
            column='license_data'.
            >>> get_license()
            The license is stored in:
            table = 'byom_licensed_models'
            schema = 'alice'
            column = 'license_data'
            >>>

    """
    license = configure._byom_model_catalog_license
    source = configure._byom_model_catalog_license_source
    table_name = configure._byom_model_catalog_license_table
    schema_name = configure._byom_model_catalog_license_database

    # Check whether license information is present or not.
    if license is not None:
        if source in 'string':
            print("The license is: {}".format(license))
        else:
            print("The license is stored in:\ntable = '{}'\nschema = '{}'\ncolumn = '{}'"
                .format(table_name, schema_name, license))
    else:
        print('Set the license information using set_license() function.')


@collect_queryband(queryband="rtrvByom")
def retrieve_byom(model_id,
                  table_name=None,
                  schema_name=None,
                  license=None,
                  is_license_column=False,
                  license_table_name=None,
                  license_schema_name=None,
                  require_license=False,
                  return_addition_columns=False):
    """
    DESCRIPTION:
        Function to retrieve a saved model. Output of this function can be
        directly passed as input to the PMMLPredict and H2OPredict functions.
        Some models generated, such as H2O-DAI has license associated with it.
        When such models are to be used for scoring, one must retrieve the model
        by passing relevant license information. Please refer to "license_key"
        for more details.

    PARAMETERS:
        model_id:
            Required Argument.
            Specifies the unique model identifier of the model to be retrieved.
            Types: str

        table_name:
            Optional Argument.
            Specifies the name of the table to retrieve external model from.
            Notes:
                * One must either specify this argument or set the byom model catalog table
                    name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in retrieve_byom() take precedence and is used for
                    function execution.
            Types: str

        schema_name:
            Optional Argument.
            Specifies the name of the schema/database in which the table specified in
            "table_name" is looked up.
            Notes:
                * One must either specify this argument and table_name argument
                    or set the byom model catalog schema and table name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in retrieve_byom() take precedence and is used for
                    function execution.
                * If user specifies schema_name argument table_name argument has to be specified,
                    else exception is raised.
            Types: str

        license:
            Optional Argument.
            Specifies the license key information in different ways specified as below:
            * If the license key is stored in a variable, user can pass it as string.
            * If the license key is stored in table, then pass a column name containing
              the license. Based on the table which has license information stored,
                * If the information is stored in the same model table as that of the
                  model, one must set "is_license_column" to True.
                * If the information is stored in the different table from that of the
                  "table_name", one can specify the table name and schema name using
                  "license_table_name" and "license_schema_name" respectively.
            Types: str

        is_license_column:
            Optional Argument.
            Specifies whether license key specified in "license" is a license key
            or column name. When set to True, "license" contains the column name
            containing license data, otherwise contains the actual license key.
            Default Value: False
            Types: str

        license_table_name:
            Optional Argument.
            Specifies the name of the table which holds license key. One can specify this
            argument if license is stored in a table other than "table_name".
            Types: str

        license_schema_name:
            Optional Argument.
            Specifies the name of the Database associated with the "license_table_name".
            If not specified, current Database would be considered for "license_table_name".
            Types: str

        require_license:
            Optional Argument.
            Specifies whether the model to be retrieved is associated with a license.
            If True, license information set by the set_license() is retrieved.
            Note:
                If license parameters are passed, then this argument is ignored.
            Default value: False
            Types: bool

        return_addition_columns:
            Optional Argument.
            Specifies whether to return additional columns saved during save_byom() along with
            model_id and model columns.
            Default value: False
            Types: bool

        Note:
            The following table describes the system behaviour in different scenarios:
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            |       In retrieve_byom()     |          In set_byom_catalog()      |     System Behavior                 |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | table_name     | schema_name | table_name            | schema_name |                                     |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Set         | Set                   | Set         |  schema_name and table_name in      |
            |                |             |                       |             |  retrieve_byom() are used for       |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Set         | Not set               | Not set     |  schema_name and table_name in      |
            |                |             |                       |             |  retrieve_byom() is used for        |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Set         |  table_name from retrieve_byom()    |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Set         | Set                   | Set         |  Exception is raised.               |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Set         |  table_name and schema_name         |
            |                |             |                       |             |  from set_byom_catalog()            |
            |                |             |                       |             |  are used for function execution.   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Not set     |  table_name from set_byom_catalog() |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            |  Not set       | Not set     | Not set               | Not set     |  Exception is raised                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+

    RETURNS:
        teradataml DataFrame

    RAISES:
        TeradataMlException, TypeError

    EXAMPLES:
        >>> import teradataml, os, datetime
        >>> model_file = os.path.join(os.path.dirname(teradataml.__file__), 'data', 'models', 'iris_kmeans_model')
        >>> from teradataml import save_byom, retrieve_byom, get_context
        >>> save_byom('model5', model_file, 'byom_models')
        Model is saved.
        >>> save_byom('model6', model_file, 'byom_models', schema_name='test')
        Model is saved.
        >>> # Save the license in an addtional column named "license_data" in the model table.
        >>> save_byom('licensed_model1', model_file, 'byom_licensed_models', additional_columns={"license_data": "A5sUL9KU_kP35Vq"})
        Created the model table 'byom_licensed_models' as it does not exist.
        Model is saved.
        >>> # Store the license in a table.
        >>> license = 'eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI'
        >>> lic_table = 'create table license (id integer between 1 and 1,license_key varchar(2500)) unique primary index(id);'
        >>> execute_sql(lic_table)
        <sqlalchemy.engine.cursor.LegacyCursorResult object at 0x0000014AAFF27080>
        >>> execute_sql("insert into license values (1, 'peBVRtjA-ib')")
        <sqlalchemy.engine.cursor.LegacyCursorResult object at 0x0000014AAFF27278>
        >>>

        # Example 1 - Retrieve a model with id 'model5' from the table 'byom_models'.
        >>> df = retrieve_byom('model5', table_name='byom_models')
        >>> df
                                     model
        model_id
        model5    b'504B03041400080808...'

        # Example 2 - Retrieve a model with id 'model6' from the table 'byom_models'
        #             and the table is in 'test' DataBase.
        >>> df = retrieve_byom('model6', table_name='byom_models', schema_name='test')
        >>> df
                                     model
        model_id
        model6    b'504B03041400080808...'

        # Example 3 - Retrieve a model with id 'model5' from the table 'byom_models'
        #             with license key stored in a variable 'license'.
        >>> df = retrieve_byom('model5', table_name='byom_models', license=license)
        >>> df
                                     model                                                         license
        model_id
        model5    b'504B03041400080808...'  eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI
        >>>

        # Example 4 - Retrieve a model with id 'licensed_model1' and associated license
        #             key stored in table 'byom_licensed_models'. License key is stored
        #             in column 'license_data'.
        >>> df = retrieve_byom('licensed_model1',
        ...                    table_name='byom_licensed_models',
        ...                    license='license_data',
        ...                    is_license_column=True)
        >>> df
                                            model          license
        model_id
        licensed_model1  b'504B03041400080808...'  A5sUL9KU_kP35Vq
        >>>

        # Example 5 - Retrieve a model with id 'licensed_model1' from the table
        #             'byom_licensed_models' and associated license key stored in
        #             column 'license_key' of the table 'license'.
        >>> df = retrieve_byom('licensed_model1',
        ...                    table_name='byom_licensed_models',
        ...                    license='license_key',
        ...                    is_license_column=True,
        ...                    license_table_name='license')
        >>> df
                                            model      license
        model_id
        licensed_model1  b'504B03041400080808...'  peBVRtjA-ib
        >>>

        # Example 6 - Retrieve a model with id 'licensed_model1' from the table
        #             'byom_licensed_models' and associated license key stored in
        #             column 'license_key' of the table 'license' present in the
        #             schema 'mldb'.
        >>> df = retrieve_byom('licensed_model1',
        ...                    table_name='byom_licensed_models',
        ...                    license='license_key',
        ...                    is_license_column=True,
        ...                    license_table_name='license',
        ...                    license_schema_name='mldb')
        >>> df
                                            model      license
        model_id
        licensed_model1  b'504B03041400080808...'  peBVRtjA-ib
        >>>

        # Example 7 - Retrieve a model with id 'model5' from the table 'byom_models'
        #             with license key stored by set_license in a variable 'license'.
        #             The catalog information is set using set_byom_catalog()
        #             to table_name='byom_models', schema_name='alice'
        #             schema_name='alice' and is used to retrieve the model.
        >>> set_byom_catalog(table_name='byom_models', schema_name='alice')
        The model cataloging parameters are set to table_name='byom_models' and
        schema_name='alice'
        >>> set_license(license=license, source='string')
        The license parameters are set.
        The license is: eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI
        >>> df = retrieve_byom('model5', require_license=True)
        >>> df
                                     model                                                         license
        model_id
        model5    b'504B03041400080808...'  eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI
        >>>

        # Example 8 - Retrieve a model with id 'model5' from the table 'byom_models'
        #             with license key stored by set_license in a file. Since the
        #             schema name is not provided, default schema is used.
        >>> license_file = os.path.join(os.path.dirname(teradataml.__file__),
        ...                             'data', 'models', 'License_file.txt')
        >>> set_license(license=license_file, source='file')
        The license parameters are set.
        The license is: license_string
        >>> df = retrieve_byom('model5', table_name='byom_models', require_license=True)
        >>> df
                                     model         license
        model_id
        model5    b'504B03041400080808...'  license_string

        # Example 9 - Retrieve a model with id 'licensed_model1' and associated license
        #             key stored in column 'license_key' of the table 'license' present
        #             in the schema 'alice'. The byom catalog and license information is
        #             set using set_byom_catalog() and set_license() respectively.
        #             Function is executed with license parameters passed,
        #             which overrides the license information set at the session level.
        >>> set_byom_catalog(table_name='byom_licensed_models', schema_name='alice')
        The model cataloging parameters are set to table_name='byom_licensed_models'
        and schema_name='alice'
        >>> set_license(license=license, source='string')
        The license parameters are set.
        The license is: eZSy3peBVRtjA-ibVuvNw5A5sUL9KU_kP35Vq4ZNBQ3iGY6oVSpE6g97sFY2LI
        >>> df = retrieve_byom('licensed_model1', license='license_key',
        ...                    is_license_column=True, license_table_name='license')
        >>> df
                                                            model      license
                        model_id
                        licensed_model1  b'504B03041400080808...'  peBVRtjA-ib

        # Example 10 - Retrieve a model with id 'licensed_model1' from the table
        #              'byom_licensed_models' and associated license key stored in
        #              column 'license_data' of the table 'byom_licensed_models'.
        #              The byom catalog and license information is already set
        #              at the session level, passing the table_name to the
        #              function call overrides the byom catalog information
        #              at the session level.
        >>> set_byom_catalog(table_name='byom_models', schema_name='alice')
        The model cataloging parameters are set to table_name='byom_models' and
        schema_name='alice'
        >>> set_license(license='license_data', table_name='byom_licensed_models',
                        schema_name='alice', source='column')
        The license parameters are set.
        The license is present in the table='byom_licensed_models', schema='alice'
        and column='license_data'.
        >>> df = retrieve_byom('licensed_model1', table_name='byom_licensed_models',
        ...                    require_license=True)
        >>> df
                                            model          license
        model_id
        licensed_model1  b'504B03041400080808...'  A5sUL9KU_kP35Vq

        # Example 11 - If require license=False which is the default value for the above example,
        #              the license information is not retrieved.
        >>> df = retrieve_byom('licensed_model1', table_name='byom_licensed_models')
        >>> df
                                            model
        model_id
        licensed_model1  b'504B03041400080808...'

        # Example 12 - Retrieve a model with id 'licensed_model1' from the table along with all
        #              additional columns saved during save_byom().
        >>> df = retrieve_byom('licensed_model1', table_name='byom_licensed_models',
                               return_addition_columns=True)
        >>> df
                                            model     license_data
        model_id
        licensed_model1  b'504B03041400080808...'  A5sUL9KU_kP35Vq
    """


    # Let's perform argument validations.
    # Create argument information matrix to do parameter checking
    __arg_info_matrix = []
    __arg_info_matrix.append(["model_id", model_id, False, str, True])
    __arg_info_matrix.append(["table_name", table_name, True, str, True])
    __arg_info_matrix.append(["schema_name", schema_name, True, str, True])
    __arg_info_matrix.append(["license", license, True, str, True])
    __arg_info_matrix.append(["is_license_column", is_license_column, False, bool])
    __arg_info_matrix.append(["license_table_name", license_table_name, True, str, True])
    __arg_info_matrix.append(["license_schema_name", license_schema_name, True, str, True])

    # Make sure that a correct type of values has been supplied to the arguments.
    validator._validate_function_arguments(__arg_info_matrix)
    
    # Set the table and schema name according to the model cataloging parameters and the user inputs.
    table_name, schema_name = __set_validate_catalog_parameters(table_name, schema_name)

    if require_license and license is None:
        license = configure._byom_model_catalog_license
        is_license_column = True if configure._byom_model_catalog_license_source == 'column' else False
        license_table_name = configure._byom_model_catalog_license_table
        license_schema_name = configure._byom_model_catalog_license_database

        # Check whether license information is present or not.
        additional_error = Messages.get_message(MessageCodes.EITHER_FUNCTION_OR_ARGS, "license", "set_license",
                                                "license", "")
        validator._validate_argument_is_not_None(license, "license", additional_error)

    # Before proceeding further, check whether table exists or not.
    conn = get_connection()
    if not conn.dialect.has_table(conn, table_name=table_name, schema=schema_name, table_only=True):
        error_code = MessageCodes.MODEL_CATALOGING_OPERATION_FAILED
        error_msg = Messages.get_message(
            error_code, "retrieve", 'Table "{}.{}" does not exist.'.format(schema_name, table_name))
        raise TeradataMlException(error_msg, error_code)

    table_name = in_schema(schema_name=schema_name, table_name=table_name)
    model_details = DataFrame(table_name)
    model_details = model_details[model_details.model_id == model_id]

    # __check_if_model_exists does the same check however, but it do not return DataFrame.
    # So, doing the model existence check here.
    if model_details.shape[0] == 0:
        error_code = MessageCodes.MODEL_NOT_FOUND
        error_msg = Messages.get_message(error_code, model_id, " in the table '{}'".format(table_name))
        raise TeradataMlException(error_msg, error_code)

    if model_details.shape[0] > 1:
        error_code = MessageCodes.MODEL_CATALOGING_OPERATION_FAILED
        error_msg = Messages.get_message(
            error_code, "retrieve", "Duplicate model found for model id '{}'".format(model_id))
        raise TeradataMlException(error_msg, error_code)

    # If license holds the actual license key, assign it to model DataFrame.
    # If license holds the column name, i.e., license data is stored in a table,
    #   If table which holds license data is same as model table, select the column.
    #   If table which holds license data is different from model table, create a
    #       DataFrame on the table which holds license data and do cross join with
    #       models DataFrame. The cross join creates a new DataFrame which has columns
    #       of both tables.
    # Note that, license table should hold only one record. so even cartesian
    #   product should hold only record in the DataFrame.

    if not license:
        if return_addition_columns:
            # Return all columns if return_addition_columns is True.
            return model_details
        return model_details.select(["model_id", "model"])

    # Lambda function for attaching the license to model DataFrame.
    _get_license_model_df = lambda license: model_details.assign(drop_columns=True,
                                                                 model_id=model_details.model_id,
                                                                 model=model_details.model,
                                                                 license=license)

    # If user passed a license as a variable, attach it to the model DataFrame.
    if not is_license_column:
        return _get_license_model_df(license)

    # If license exists in the column of the same model table.
    if is_license_column and not license_table_name:
        _Validators._validate_column_exists_in_dataframe(license,
                                                         model_details._metaexpr,
                                                         for_table=True,
                                                         column_arg='license',
                                                         data_arg=table_name)
        return _get_license_model_df(model_details[license])

    # If license exists in the column of the table different from model table.
    license_schema_name = license_schema_name if license_schema_name else schema_name
    license_table = in_schema(license_schema_name, license_table_name)

    # Check whether license table exists or not before proceed further.
    if not conn.dialect.has_table(conn, table_name=license_table_name, schema=license_schema_name,
                                  table_only=True):
        error_code = MessageCodes.EXECUTION_FAILED
        error_msg = Messages.get_message(
            error_code, "retrieve the model", 'Table "{}" does not exist.'.format(license_table))
        raise TeradataMlException(error_msg, error_code)

    license_df = DataFrame(license_table)
    # Check column existed in table.
    _Validators._validate_column_exists_in_dataframe(license,
                                                     license_df._metaexpr,
                                                     for_table=True,
                                                     column_arg='license',
                                                     data_arg=license_table)

    if license_df.shape[0] > 1:
        error_code = MessageCodes.MODEL_CATALOGING_OPERATION_FAILED
        error_msg = Messages.get_message(
            error_code, "retrieve", "Table which holds license key should have only one row.")
        raise TeradataMlException(error_msg, error_code)

    if not return_addition_columns:
        # Return only model_id and model columns if return_addition_columns is False.
        model_details = model_details.select(["model_id", "model"])

    # Make sure license is the column name for license key.
    license_df = license_df.assign(drop_columns=True, license=license_df[license])
    return model_details.join(license_df, how="cross")


@collect_queryband(queryband="lstByom")
def list_byom(table_name=None, schema_name=None, model_id=None):
    """
    DESCRIPTION:
        The list_byom() function allows a user to list saved models, filtering the results based on the optional arguments.

    PARAMETERS:
        table_name:
            Optional Argument.
            Specifies the name of the table to list models from.
            Notes:
                * One must either specify this argument or set the byom model catalog table
                    name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in list_byom() take precedence and is used for
                    function execution.
            Types: str

        schema_name:
            Optional Argument.
            Specifies the name of the schema/database in which the table specified in
            "table_name" is looked up.
            Notes:
                * One must either specify this argument and table_name argument
                    or set the byom model catalog schema and table name using set_byom_catalog().
                * If none of these arguments are set, exception is raised; If both arguments
                    are set, the settings in list_byom() take precedence and is used for
                    function execution.
                * If user specifies schema_name argument table_name argument has to be specified,
                    else exception is raised.
            Types: str

        model_id:
            Optional Argument.
            Specifies the unique model identifier of the model(s). If specified,
            the models with either exact match or a substring match, are listed.
            Types: str OR list

        Note:
            The following table describes the system behaviour in different scenarios:
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            |      In list_byom()          |        In set_byom_catalog()        |        System Behavior              |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | table_name     | schema_name | table_name            | schema_name |                                     |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Set         | Set                   | Set         |  schema_name and table_name in      |
            |                |             |                       |             |  list_byom() are used for           |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Set         | Not set               | Not set     |  schema_name and table_name in      |
            |                |             |                       |             |  list_byom() is used for            |
            |                |             |                       |             |  function execution.                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Set            | Not set     | Set                   | Set         |  table_name from list_byom()        |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Set         | Set                   | Set         |  Exception is raised.               |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Set         |  table_name and schema_name         |
            |                |             |                       |             |  from set_byom_catalog()            |
            |                |             |                       |             |  are used for function execution.   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Set                   | Not set     |  table_name from set_byom_catalog() |
            |                |             |                       |             |  is used and schema name            |
            |                |             |                       |             |  associated with the current        |
            |                |             |                       |             |  context is used.                   |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
            | Not set        | Not set     | Not set               | Not set     |  Exception is raised                |
            +----------------+-------------+-----------------------+-------------+-------------------------------------+
    RETURNS:
        None.

    RAISES:
        TeradataMlException, TypeError

    EXAMPLES:
        >>> import teradataml, os, datetime
        >>> model_file = os.path.join(os.path.dirname(teradataml.__file__), 'data', 'models', 'iris_kmeans_model')
        >>> from teradataml import save_byom, list_byom
        >>> save_byom('model7', model_file, 'byom_models')
        Model is saved.
        >>> save_byom('iris_model1', model_file, 'byom_models')
        Model is saved.
        >>> save_byom('model8', model_file, 'byom_models', schema_name='test')
        Model is saved.
        >>> save_byom('iris_model1', model_file, 'byom_licensed_models')
        Model is saved.
        >>>

        # Example 1 - List all the models from the table byom_models.
        >>> list_byom(table_name='byom_models')
                                        model
        model_id
        model7       b'504B03041400080808...'
        iris_model1  b'504B03041400080808...'
        >>>

        # Example 2 - List all the models with model_id containing 'iris' string.
        #             List such models from 'byom_models' table.
        >>> list_byom(table_name='byom_models', model_id='iris')
                                        model
        model_id
        iris_model1  b'504B03041400080808...'
        >>>

        # Example 3 - List all the models with model_id containing either 'iris'
        #             or '7'. List such models from 'byom_models' table.
        >>> list_byom(table_name='byom_models', model_id=['iris', '7'])
                                        model
        model_id
        model7       b'504B03041400080808...'
        iris_model1  b'504B03041400080808...'
        >>>

        # Example 4 - List all the models from the 'byom_models' table and table is
        #             in 'test' DataBase.
        >>> list_byom(table_name='byom_models', schema_name='test')
                                        model
        model_id
        model8       b'504B03041400080808...'
        >>>

        # Example 5 - List all the models from the model cataloging table
        #             set by set_byom_catalog().
        >>> set_byom_catalog(table_name='byom_models', schema_name='alice')
        The model cataloging parameters are set to table_name='byom_models' and schema_name='alice'
        >>> list_byom()
                                        model
        model_id
        model8       b'504B03041400080808...'

        # Example 6 - List all the models from the table other than model cataloging table
        #             set at the session level.
        >>> set_byom_catalog(table_name='byom_models', schema_name= 'alice')
        The model cataloging parameters are set to table_name='byom_models' and schema_name='alice'
        >>> list_byom(table_name='byom_licensed_models')
                                           model
        model_id
        iris_model1         b'504B03041400080808...'

    """

    # Let's perform argument validations.
    # Create argument information matrix to do parameter checking
    __arg_info_matrix = []
    __arg_info_matrix.append(["table_name", table_name, True, str, True])
    __arg_info_matrix.append(["schema_name", schema_name, True, str, True])
    __arg_info_matrix.append(["model_id", model_id, True, (str, list), True])

    # Make sure that a correct type of values has been supplied to the arguments.
    validator._validate_function_arguments(__arg_info_matrix)

    # Set the table and schema name according to the model cataloging parameters and the user inputs.
    table_name, schema_name = __set_validate_catalog_parameters(table_name, schema_name)

    # Before proceeding further, check whether table exists or not.
    conn = get_connection()
    if not conn.dialect.has_table(conn, table_name=table_name, schema=schema_name, table_only=True):
        error_code = MessageCodes.MODEL_CATALOGING_OPERATION_FAILED
        error_msg = Messages.get_message(
            error_code, "list", 'Table "{}.{}" does not exist.'.format(schema_name, table_name))
        raise TeradataMlException(error_msg, error_code)

    model_details = DataFrame(in_schema(schema_name, table_name))

    filter_condition = None
    if model_id:
        model_ids = UtilFuncs._as_list(model_id)
        for modelid in model_ids:
            # Filter Expression on model_id column.
            # We are looking to find all rows with model_id matching with 'modelid' string.
            # This is case-insensitive look-up.
            filter_expression = __get_like_filter_expression_on_col(model_details._metaexpr,
                                                                    "model_id", modelid)
            filter_condition = filter_condition | filter_expression \
                if filter_condition else filter_expression

    if filter_condition:
        model_details = model_details[filter_condition]

    if model_details.shape[0] != 0:
        orig_max_rows_num = display.max_rows
        try:
            display.max_rows = 99999
            print(model_details)
        except Exception:
            raise
        finally:
            display.max_rows = orig_max_rows_num
    else:
        print("No models found.")
