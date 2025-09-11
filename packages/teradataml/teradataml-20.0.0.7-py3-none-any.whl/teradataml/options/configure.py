"""
Unpublished work.
Copyright (c) 2021 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Gouri.Patwardhan@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

This file is for providing user configurable options.
"""
import os
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes


class _ConfigureSuper(object):

    def __init__(self):
        pass

    def _SetKeyValue(self, name, value):
        super().__setattr__(name, value)

    def _GetValue(self, name):
        return super().__getattribute__(name)


def _create_property(name):
    storage_name = '_' + name

    @property
    def prop(self):
        return self._GetValue(storage_name)

    @prop.setter
    def prop(self, value):
        self._SetKeyValue(storage_name, value)

    return prop


class _Configure(_ConfigureSuper):
    """
    Options to configure database related values.
    """

    default_varchar_size = _create_property('default_varchar_size')
    column_casesensitive_handler = _create_property('column_casesensitive_handler')
    vantage_version = _create_property('vantage_version')
    val_install_location = _create_property('VAL_install_location')
    byom_install_location = _create_property('BYOM_install_location')
    temp_table_database = _create_property('temp_table_database')
    temp_view_database = _create_property('temp_view_database')
    read_nos_function_mapping = _create_property('read_nos_function_mapping')
    write_nos_function_mapping = _create_property('write_nos_function_mapping')
    cran_repositories = _create_property('cran_repositories')
    inline_plot = _create_property('inline_plot')
    indb_install_location = _create_property('indb_install_location')
    openml_user_env = _create_property('openml_user_env')
    local_storage = _create_property('local_storage')
    stored_procedure_install_location = _create_property('stored_procedure_install_location')
    table_operator = _create_property('table_operator')
    temp_object_type = _create_property('temp_object_type')
    use_short_object_name = _create_property('use_short_object_name')

    def __init__(self, default_varchar_size=1024, column_casesensitive_handler=False,
                 vantage_version="vantage1.1", val_install_location=None,
                 byom_install_location=None, temp_table_database=None,
                 temp_view_database=None, database_version=None,
                 read_nos_function_mapping="read_nos", write_nos_function_mapping="write_nos",
                 cran_repositories=None, inline_plot=True,
                 indb_install_location=None,
                 openml_user_env=None, local_storage=None, stored_procedure_install_location="SYSLIB",
                 table_operator=None, temp_object_type=None, use_short_object_name=False):

        """
        PARAMETERS:
            default_varchar_size:
                Specifies the size of varchar datatype in Teradata Vantage, the default
                size is 1024.
                User can configure this parameter using options.
                Types: int
                Example:
                    teradataml.options.configure.default_varchar_size = 512

            vantage_version:
                Specifies the Vantage version of the system teradataml is connected to.
                Types: string
                Example:
                    # Set the Vantage Version
                    teradataml.options.configure.vantage_version = "vantage1.1"

            val_install_location:
                Specifies the name of the database where Vantage Analytic Library functions
                are installed.
                Types: string
                Example:
                    # Set the Vantage Analytic Library install location to 'SYSLIB'
                    # when VAL functions are installed in 'SYSLIB'.
                    teradataml.options.configure.val_install_location = "SYSLIB"

            byom_install_location:
                Specifies the name of the database where Bring Your Own Model functions
                are installed.
                Types: string
                Example:
                    # Set the BYOM install location to 'SYSLIB'
                    # when BYOM functions are installed in 'SYSLIB'.
                    teradataml.options.configure.byom_install_location = "SYSLIB"

            database_version:
                Specifies the actual database version of the system teradataml is connected to.
                Types: string
                Example:
                    # Set the Vantage Version
                    teradataml.options.configure.database_version = "17.05a.00.147"
            
            read_nos_function_mapping:
                Specifies the function mapping name for the read_nos table operator function.
                Types: string
                Example:
                    # Set the read nos function mapping name
                    teradataml.options.configure.read_nos_function_mapping = "read_nos_fm"
            
            write_nos_function_mapping:
                Specifies the function mapping name for the write_nos table operator function.
                Types: string
                Example:
                    # Set the write nos function mapping name
                    teradataml.options.configure.write_nos_function_mapping = "write_nos_fm"

            inline_plot:
                Specifies whether to display the plot inline or not.
                Note:
                    Not applicable for machines running Linux and Mac OS.
                Types: bool
                Example:
                    # Set the option to display plot in a separate window.
                    teradataml.options.configure.inline_plot = True

            indb_install_location:
                Specifies the installation location of In-DB Python package.
                Default Value: "/var/opt/teradata/languages/sles12sp3/Python/"
                Types: string
                Example:
                    # Set the installation location for older versions.
                    teradataml.options.configure.indb_install_location = "/opt/teradata/languages/Python/"

            openml_user_env:
                Specifies the user environment to be used for OpenML.
                Types: UserEnv
                Example:
                    # Set the environment to be used for OpenML.
                    _env_name = "OpenAF" # Name of the user defined environment.
                    teradataml.options.configure.openml_user_env = get_env(_env_name)

            local_storage:
                Specifies the location on client where garbage collector folder will be created.
                Types: string
                Example:
                    # Set the garbage collector location to "/Users/gc/"
                    teradataml.options.configure.local_storage = "/Users/gc/"

            stored_procedure_install_location:
                Specifies the name of the database where stored procedures
                are installed.
                Types: string
                Example:
                    # Set the Stored Procedure install location to 'SYSLIB'
                    # when stored procedures are installed in 'SYSLIB'.
                    teradataml.options.configure.stored_procedure_install_location = "SYSLIB"

            table_operator:
                Specifies the name of the table operator.
                Permitted Values: "Apply", "Script"
                Types: string
                Example:
                    # Set the table operator name to "Script"
                    teradataml.options.configure.table_operator = "Script"

            temp_object_type:
                Specifies the type of temporary database objects created internally by teradataml.
                Permitted Values:
                    * "VT" - Volatile tables.
                Default Value: None
                Types: String
                Notes:
                    * If this option is set to "VT" and "persist" argument of analytic functions is
                      set to True, then volatile tables are not created as volatile table can't be
                      persisted and "persist" argument takes precedence.
                    * Default behavior is to create views that will be garbage collected at the end.
                Example:
                    # Set the type of temporary database objects to "VT" to create volatile internal
                    # tables.
                    teradataml.options.configure.temp_object_type = "VT"

            use_short_object_name:
                Specifies whether to use shorter names for temporary tables created internally by teradataml.
                When set to True, teradataml generates internal temporary table names with a maximum length 
                of 20 characters. Otherwise, there is no restriction on the length of these table names.
                Default Value: False
                Types: bool
                Example:
                    # Set the option to use short names for temporary tables.
                    teradataml.options.configure.use_short_object_name = True
        """
        super().__init__()
        super().__setattr__('default_varchar_size', default_varchar_size)
        super().__setattr__('column_casesensitive_handler', column_casesensitive_handler)
        super().__setattr__('vantage_version', vantage_version)
        super().__setattr__('val_install_location', val_install_location)
        super().__setattr__('byom_install_location', byom_install_location)
        super().__setattr__('temp_table_database', temp_table_database)
        super().__setattr__('temp_view_database', temp_view_database)
        super().__setattr__('database_version', database_version)
        super().__setattr__('read_nos_function_mapping', read_nos_function_mapping)
        super().__setattr__('write_nos_function_mapping', write_nos_function_mapping)
        super().__setattr__('cran_repositories', cran_repositories)
        super().__setattr__('inline_plot', True)
        super().__setattr__('openml_user_env', openml_user_env)
        super().__setattr__('local_storage', local_storage)
        super().__setattr__('stored_procedure_install_location', stored_procedure_install_location)
        super().__setattr__('table_operator', table_operator)
        super().__setattr__('_indb_install_location', indb_install_location)
        super().__setattr__('temp_object_type', self.__get_temp_object_type(temp_object_type))
        super().__setattr__('use_short_object_name', use_short_object_name)

        # internal configurations
        # These configurations are internal and should not be
        # exported to the user's namespace.
        super().__setattr__('_validate_metaexpression', False)
        # Internal parameter, that should be used while testing to validate whether
        # Garbage collection is being done or not.
        super().__setattr__('_validate_gc', False)
        # Internal parameter, that is used for specifying the global model cataloging schema name which
        # will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_database', None)
        # Internal parameter, that is used for specifying the global model cataloging table name which
        # will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_table', None)
        # Internal parameter, that is used for specifying the license information as a string, file
        # path or column name which will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_license', None)
        # Internal parameter, that is used for specifying the source where the license came from
        # which will be used by the byom APIs.
        super().__setattr__('_byom_model_catalog_license_source', None)
        # Internal parameter, that is used for specifying the license table name
        # where the license is stored
        super().__setattr__('_byom_model_catalog_license_table', None)
        # Internal parameter, that is used for specifying the schema name where
        # the license table is stored
        super().__setattr__('_byom_model_catalog_license_database', None)
        # Internal parameter, that is used for specifying the URL to be used as
        # base URL in UES REST calls
        super().__setattr__('ues_url', None)
        # base URL in Vector Store REST calls
        super().__setattr__('_vector_store_base_url', None)
        # Internal parameter, which is used to specify whether SSL verification is to be done or not.
        # By default, it is set to True.
        super().__setattr__('_ssl_verify', True)
        # Internal parameter, that is used to specify the certificate file in a secured HTTP request.
        super().__setattr__('certificate_file', False)
        # Internal parameter, that is used for specify the maximum size of the file
        # allowed by UES to upload it.
        super().__setattr__('_ues_max_file_upload_size', 10)
        # Internal parameter, that is used to specify the default environment,
        super().__setattr__('_default_user_env', None)
        # Internal parameter, that is used to post the Code verifier in OAuth work flow.
        super().__setattr__('_oauth_end_point', None)
        # Internal parameter, that is used for specifying the client id in OAuth work flow.
        super().__setattr__('_oauth_client_id', None)
        # Internal parameter, that is used for specifying the Authentication token expiry time.
        super().__setattr__('_auth_token_expiry_time', None)
        # Internal parameter, that is used for specifying the OAuth authentication.
        super().__setattr__('_oauth', None)
        # Internal parameter, that is used for specifying the current database associated with current connection.
        super().__setattr__('_current_database_name', None)
        # Internal parameter, that is used for specifying the database username associated with current connection.
        super().__setattr__('_database_username', None)

    @property
    def indb_install_location(self):
        """
        DESCRIPTION:
            Specifies the installation location of In-DB Python package.

        RAISES:
            Operational Error.
        """
        if self._indb_install_location:
            return self._indb_install_location
        from teradataml.context.context import get_context
        if get_context():
            from teradataml.common.constants import TableOperatorConstants
            from teradataml.utils.utils import execute_sql
            _path = execute_sql(TableOperatorConstants.INDB_PYTHON_PATH.value).fetchall()[0][0]
            if 'sles:12:sp3' in _path:
                self._indb_install_location = '/var/opt/teradata/languages/sles12sp3/Python/'
            elif 'sles:15:sp4' in _path:
                self._indb_install_location = '/var/opt/teradata/languages/sles15sp4/Python/'
            else:
                self._indb_install_location = '/opt/teradata/languages/Python/'
            return self._indb_install_location
        else:
            return '/var/opt/teradata/languages/sles12sp3/Python/'

    @indb_install_location.setter
    def indb_install_location(self, value):
        """
        DESCRIPTION:
            Sets the value to "indb_install_location" by user.

        PARAMETERS:
            value:
                Required Argument.
                Specifies the value assigned to "indb_install_location".
                Types: str
        """
        self._indb_install_location = value

    def __setattr__(self, name, value):
        if hasattr(self, name):
            if name == 'default_varchar_size':
                if not isinstance(value, int):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'int'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                if value <= 0:
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT, name,
                                                                   "greater than"),
                                              MessageCodes.TDMLDF_POSITIVE_INT)
            elif name == '_ues_max_file_upload_size':
                # If the value is bool, isinstance(value, int) returns True
                # which is wrong, hence added the condition on bool.
                if isinstance(value, bool) or not isinstance(value, int):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'int'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                if value < 0:
                    raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_POSITIVE_INT, name,
                                                                   "greater than or equal to"),
                                              MessageCodes.TDMLDF_POSITIVE_INT)
            elif name in ['column_casesensitive_handler', '_validate_metaexpression',
                          '_validate_gc', 'inline_plot', '_oauth', '_ssl_verify']:

                if not isinstance(value, bool):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'bool'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
            elif name == 'certificate_file':
                if not isinstance(value, str):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)

                if not os.path.exists(value):
                    msg_code = MessageCodes.EXECUTION_FAILED
                    raise TeradataMlException(Messages.get_message(msg_code,
                                                                   "read contents of file '{}'".format(value),
                                                                   'File does not exist.'),
                                              msg_code)

                if not os.path.isfile(value):
                    msg_code = MessageCodes.EXECUTION_FAILED
                    raise TeradataMlException(Messages.get_message(msg_code,
                                                                   "read contents of file '{}'".format(value),
                                                                   'Not a file.'),
                                              msg_code)

            elif name == 'vantage_version':
                if not isinstance(value, str):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                valid_versions = ['vantage1.0', 'vantage1.1', 'vantage1.3', 'vantage2.0']
                value = value.lower()
                if value not in valid_versions:
                    raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                                   value,
                                                                   name,
                                                                   "a value in {}".format(valid_versions)),
                                              MessageCodes.INVALID_ARG_VALUE)

            elif name in ['val_install_location', 'byom_install_location',
                          'read_nos_function_mapping', 'write_nos_function_mapping',
                          '_byom_model_catalog_database', '_byom_model_catalog_table',
                          '_byom_model_catalog_license', '_byom_model_catalog_license_source',
                          'indb_install_location', 'local_storage', 'stored_procedure_install_location']:
                if not isinstance(value, str):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
                if name == 'local_storage':
                    # Validate if path exists.
                    if not os.path.exists(value):
                        raise TeradataMlException(
                            Messages.get_message(MessageCodes.PATH_NOT_FOUND).format(value),
                            MessageCodes.PATH_NOT_FOUND)

            elif name in {'ues_url', '_oauth_end_point', '_oauth_client_id', '_vector_store_base_url'}:
                if not isinstance(value, str):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name, 'str'))

                if len(value) == 0:
                    raise ValueError(Messages.get_message(MessageCodes.ARG_EMPTY, name))

                if name in ['ues_url', '_vector_store_base_url']:
                    value = value[: -1] if value.endswith("/") else value

            elif name in ['temp_table_database', 'temp_view_database',
                          "_byom_model_catalog_license_table", "_byom_model_catalog_license_database",
                          "_current_database_name", "_database_username", "database_version"]:
                if not isinstance(value, str) and not isinstance(value, type(None)):
                    raise TeradataMlException(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                                   'str or None'),
                                              MessageCodes.UNSUPPORTED_DATATYPE)
            elif name in {'_auth_token_expiry_time'}:
                if not isinstance(value, float):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name, 'float'))

            elif name == 'cran_repositories':
                if not isinstance(value, str) and not isinstance(value, list) and not isinstance(value, type(None)):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                         'str, list of str or None'))
                if isinstance(value, list):
                    for url in value:
                        if not isinstance(url, str):
                            raise TypeError(
                                Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                     'str, list of str or None'))

            elif name == 'openml_user_env':
                from teradataml.scriptmgmt.UserEnv import UserEnv
                if not isinstance(value, UserEnv) and not isinstance(value, type(None)):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name, 'UserEnv or None'))

            elif name == 'table_operator':
                if not isinstance(value, str) and not isinstance(value, type(None)):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name, 'str or None'))

                if value is not None:
                    valid_names = ['script', 'apply']
                    value = value.lower()
                    if value not in valid_names:
                        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                                       value,
                                                                       name,
                                                                       "a value in {}".format(valid_names)),
                                                  MessageCodes.INVALID_ARG_VALUE)
            elif name == "temp_object_type":
                self.__validate_db_tbl_attrs(name, value)
                valid_object_typs = ['VT']
                if value and value.upper() not in valid_object_typs:
                    raise ValueError(Messages.get_message(MessageCodes.INVALID_ARG_VALUE,
                                                          value,
                                                          name,
                                                          "a value in {}".format(valid_object_typs)))

                value = self.__get_temp_object_type(value)

            elif name == 'use_short_object_name':
                if not isinstance(value, bool):
                    raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name, 'bool'))

            super().__setattr__(name, value)
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def __get_temp_object_type(self, value):
        """
        Get the temporary object type based on the value provided.
        Default behavior is to create views that will be garbage collected at the end.
        """
        from teradataml.common.constants import TeradataConstants
        if value and value.upper() == "VT":
            return TeradataConstants.TERADATA_VOLATILE_TABLE
        # This we will need in the future.
        # elif value and value.upper() in ["TT", "PT"]:
        #     return TeradataConstants.TERADATA_TABLE
        return TeradataConstants.TERADATA_VIEW

    def __validate_db_tbl_attrs(self, name, value):
        if not isinstance(value, str) and not isinstance(value, type(None)):
            raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE, name,
                                                 'str or None'))


configure = _Configure()