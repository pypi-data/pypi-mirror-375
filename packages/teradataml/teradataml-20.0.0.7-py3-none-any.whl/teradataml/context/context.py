# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rameshchandra.d@teradata.com
Secondary Owner:

teradataml context
----------
A teradataml context functions provide interface to Teradata Vantage. Provides functionality to get and set a global
context which can be used by other analytical functions to get the Teradata Vantage connection.

"""
import atexit
import ipaddress
import os
import socket
import sys
import threading
import warnings
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL

from teradataml.common.constants import Query, SQLConstants, TeradataConstants
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.sqlbundle import SQLBundle
from teradataml.common.warnings import TeradataMlRuntimeWarning
from teradataml.context.aed_context import AEDContext
from teradataml.options.configure import configure
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.utils.utils import execute_sql
from teradataml.utils.validators import _Validators

# Store a global Teradata Vantage Connection.
# Right now user can only provide a single Vantage connection at any point of time.
td_connection = None
td_sqlalchemy_engine = None
temporary_database_name = None
user_specified_connection = False
python_packages_installed = False
python_version_vantage = None
python_version_local = None
td_user = None

function_alias_mappings = {}

# Current directory is context folder.
teradataml_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_folder = os.path.join(teradataml_folder, "config")


def _get_current_databasename():
    """
    Returns the database name associated with the current context.

    PARAMETERS:
        None.

    RETURNS:
        Database name associated with the current context

    RAISES:
        TeradataMlException - If Vantage connection can't be established using the engine.

    EXAMPLES:
        _get_current_databasename()
    """
    if configure._current_database_name:
        return configure._current_database_name
    else:
        if get_connection() is not None:
            select_user_query = ""
            try:
                sqlbundle = SQLBundle()
                select_user_query = sqlbundle._get_sql_query(SQLConstants.SQL_SELECT_DATABASE)
                result = execute_sql(select_user_query)
                configure._current_database_name = result.fetchall()[0][0]
                return configure._current_database_name
            except TeradataMlException:
                raise
            except Exception as err:
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_EXEC_SQL_FAILED, select_user_query),
                                          MessageCodes.TDMLDF_EXEC_SQL_FAILED) from err
        else:
            return None


def _get_database_username():
    """
    Function to get the database user name.

    PARAMETERS:
        None.

    RETURNS:
        Database user name.

    RAISES:
        TeradataMlException - If "select user" query fails.

    EXAMPLES:
        _get_database_username()
    """
    if configure._database_username:
        return configure._database_username
    else:
        if get_connection() is not None:
            select_query = ""
            try:
                sqlbundle = SQLBundle()
                select_query = sqlbundle._get_sql_query(SQLConstants.SQL_SELECT_USER)
                result = execute_sql(select_query)
                configure._database_username = result.fetchall()[0][0]
                return configure._database_username
            except TeradataMlException:
                raise
            except Exception as err:
                raise TeradataMlException(Messages.get_message(MessageCodes.TDMLDF_EXEC_SQL_FAILED, select_query),
                                          MessageCodes.TDMLDF_EXEC_SQL_FAILED) from err
        else:
            return None


def __cleanup_garbage_collection():
    """initiate the garbage collection."""
    GarbageCollector._cleanup_garbage_collector()


def _get_other_connection_parameters(logmech=None, logdata=None, database=None, **kwargs):
    """
    DESCRIPTION:
        Internal function to return the connection parameters.

    PARAMETERS:
        logmech:
            Optional Argument.
            Specifies the logon mechanism - TD2, LDAP, TDNEGO, KRB5 or JWT, to establish the connection.
            Types: str

        logdata:
            Optional Argument.
            Specifies additional connection information needed for the given logon mechanism.
            Types: str

        database:
            Optional Argument.
            Specifies the initial database to use after logon, instead of the user's default database.
            Types: str

        kwargs:
            Optional Argument.
            Specifies the keyword value pairs of other connection parameters to create the connection string.

    RETURNS:
        dict, needed to generate engine URL.

    EXAMPLES:
        __get_other_connection_parameters(logmech = "JWT", logdata = "<jwt_token>", database = "<database_name>",
                                          kwargs)
    """
    # Return empty string if there are no additional connection parameters.
    if not logmech and not logdata and not database and len(kwargs) == 0:
        return ""

    result = {}

    if logmech:
        result['LOGMECH'] = logmech.upper()
    if logdata:
        result['LOGDATA'] = logdata
    if database:
        result['DATABASE'] = database

    # Create connection parameters string.
    other_params = []
    for key, val in kwargs.items():
        if isinstance(val, str):
            # Value of TMODE connection parameter should be upper case (as per driver specification) i.e., ansi -> ANSI.
            # Converting all string values to upper case.
            if key != "LOGDATA":
                val = val.upper()
        else:
            # Other type values like integer, boolean etc, are converted to string.
            # For boolean values, the connection string should contain lower case values i.e., True -> true
            val = str(val).lower()
        result[key] = val

    return result


@collect_queryband(queryband='CrtCxt')
def create_context(host=None, username=None, password=None, tdsqlengine=None, temp_database_name=None,
                   logmech=None, logdata=None, database=None, **kwargs):
    """
    DESCRIPTION:
        Creates a connection to the Teradata Vantage using the teradatasql + teradatasqlalchemy DBAPI and dialect
        combination.
        Users can create a connection by passing the connection parameters using any one of the following methods:
            1. Pass all required parameters (host, username, password) directly to the function.
            2. Set the connection parameters in a configuration file (.cfg or .env) and
               pass the configuration file.
            3. Set the connection parameters in environment variables and create_context() reads from
               environment variables.

        Alternatively, users can pass a SQLAlchemy engine object to the `tdsqlengine` parameter to override the default DBAPI
        and dialect combination.

        Function also enables user to set the authentication token which is required to access services running
        on Teradata Vantage.

        Note:
            1. teradataml requires that the user has certain permissions on the user's default database or the initial
               default database specified using the database argument, or the temporary database when specified using
               temp_database_name. These permissions allow the user to:
                a. Create tables and views to save results of teradataml analytic functions.
                b. Create views in the background for results of DataFrame APIs such as assign(),
                   filter(), etc., whenever the result for these APIs are accessed using a print().
                c. Create view in the background on the query passed to the DataFrame.from_query() API.

               It is expected that the user has the correct permissions to create these objects in the database that
               will be used.
               The access to the views created may also require issuing additional GRANT SELECT ... WITH GRANT OPTION
               permission depending on which database is used and which object the view being created is based on.

            2. The temp_database_name and database parameters play a crucial role in determining which database
               is used by default to lookup for tables/views while creating teradataml DataFrame using 'DataFrame()'
               and 'DataFrame.from_table()' and which database is used to create all internal temporary objects.
               +------------------------------------------------------+---------------------------------------------+
               |                     Scenario                         |            teradataml behaviour             |
               +------------------------------------------------------+---------------------------------------------+
               | Both temp_database_name and database are provided    | Internal temporary objects are created in   |
               |                                                      | temp_database_name, and database table/view |
               |                                                      | lookup is done from database.               |
               +------------------------------------------------------+---------------------------------------------+
               | database is provided but temp_database_name is not   | Database table/view lookup and internal     |
               |                                                      | temporary objects are created in database.  |
               +------------------------------------------------------+---------------------------------------------+
               | temp_database_name is provided but database is not   | Internal temporary objects are created in   |
               |                                                      | temp_database_name, database table/view     |
               |                                                      | lookup from the users default database.     |
               +------------------------------------------------------+---------------------------------------------+
               | Neither temp_database_name nor database are provided | Database table/view lookup and internal     |
               |                                                      | temporary objects are created in users      |
               |                                                      | default database.                           |
               +------------------------------------------------------+---------------------------------------------+

            3. The function prioritizes parameters in the following order:
                1. Explicitly passed arguments (host, username, password).
                2. Environment variables (TD_HOST, TD_USERNAME, TD_PASSWORD, etc.).
                   Note:
                       * The environment variables should start with 'TD_' and all must be in upper case.
                         Example:
                                os.environ['TD_HOST'] = 'tdhost'
                                os.environ['TD_USERNAME'] = 'tduser'
                                os.environ['TD_PASSWORD'] = 'tdpassword'
                3. A configuration file if provided (such as a .env file).

            4. Points to note when user sets authentication token with create_context():
                * The username provided in create_context() is not case-sensitive. For example,
                  if a user is created with the username xyz, create_context() still establishes
                  a connection if user passes the username as XyZ. However, authentication token
                  generation requires the username to be in the same case as when it was created.
                  Therefore, Teradata recommends to pass the username with the same case as when
                  it was created.
                * User must have a privilege to login with a NULL password to use set_auth_token().
                  Refer to GRANT LOGON section in Teradata Documentation for more details.
                * When "auth_mech" is not specified, arguments are used in the following combination
                  to derive authentication mechanism.
                    * If "base_url" and "client_id" are specified then token generation is done through OAuth.
                    * If "base_url", "pat_token", "pem_file" are specified then token generation is done using PAT.
                    * If "base_url" and "auth_token" are specified then value provided for "auth_token" is used.
                    * If only "base_url" is specified then token generation is done through OAuth.
                * If Basic authentication mechanism is to be used then user must specify argument
                  "auth_mech" as "BASIC" along with "username" and "password".
                * Refresh token works only for OAuth authentication.
                * Use the argument "kid" only when key used during the pem file generation is different
                  from pem file name. For example, if you use the key as 'key1' while generating pem file
                  and the name of the pem file is `key1(1).pem`, then pass value 'key1' to the argument "kid".

    PARAMETERS:
        host:
            Optional Argument.
            Specifies the fully qualified domain name or IP address of the Teradata System.
            Types: str
        
        username:
            Optional Argument.
            Specifies the username for logging onto the Teradata Vantage.
            Types: str
        
        password:
            Optional Argument.
            Specifies the password required for the "username".
            Types: str
            Note:
                * Encrypted passwords can also be passed to this argument, using Stored Password Protection feature.
                  Examples section below demonstrates passing encrypted password to 'create_context'.
                  More details on Stored Password Protection and how to generate key and encrypted password file
                  can be found at https://pypi.org/project/teradatasql/#StoredPasswordProtection
                * Special characters used in the password are encoded by default.

        tdsqlengine:
            Optional Argument.
            Specifies Teradata Vantage sqlalchemy engine object that should be used to establish a Teradata Vantage
            connection.
            Types: str
            
        temp_database_name:
            Optional Argument.
            Specifies the temporary database name where temporary tables, views will be created.
            Types: str
            
        logmech:
            Optional Argument.
            Specifies the type of logon mechanism to establish a connection to Teradata Vantage. 
            Permitted Values: As supported by the teradata driver.
            Notes:
                1. teradataml expects the client environments are already setup with appropriate
                   security mechanisms and are in working conditions.
                2. User must have a valid ticket-granting ticket in order to use KRB5 (Kerberos) logon mechanism.
                3. User must use logdata parameter when using 'JWT' as the logon mechanism.
                4. Browser Authentication is supported for Windows and macOS.
                For more information please refer Teradata Vantage™ - Advanced SQL Engine
                Security Administration at https://www.info.teradata.com/
            Types: str

        logdata:
            Optional Argument.
            Specifies parameters to the LOGMECH command beyond those needed by the logon mechanism, such as 
            user ID, password and tokens (in case of JWT) to successfully authenticate the user.
            Types: str

        database:
            Optional Argument.
            Specifies the initial database to use after logon, instead of the user's default database.
            Types: str

        kwargs:
            Specifies optional keyword arguments accepted by create_context().
            Below are the supported keyword arguments:

            Connection parameters for Teradata SQL Driver:
                Specifies the keyword-value pairs of connection parameters that are passed to Teradata SQL Driver for
                Python. Please refer to https://github.com/Teradata/python-driver#ConnectionParameters to get information
                on connection parameters of the driver.
                Note:
                    * When type of a connection parameter is integer or boolean (eg: log, lob_support etc,.), pass
                      integer or boolean value, instead of quoted integer or quoted boolean as suggested in the
                      documentation. Please check the examples for usage.
                    * "sql_timeout" represents "request_timeout" connection parameter.

            config_file:
                Specifies the name of the configuration file to read the connection parameters.
                Notes:
                    * If user does not specify full path of file, then file look up is done at current working directory.
                    * The content of the file must be in '.env' format.
                    * Use parameters of create_context() as key in the configuration file.
                      Example:
                          host=tdhost
                          username=tduser
                          password=tdpassword
                          temp_database_name=tdtemp_database_name
                          logmech=tdlogmech
                          logdata=tdlogdata
                          database=tddatabase
                    * For more information please refer examples section.
                Default Value : td_properties.cfg
                Types: str

            base_url:
                Specifies the endpoint URL for a given environment on Teradata Vantage.
                Types: str

            client_id:
                Specifies the id of the application that requests the access token from
                VantageCloud Lake.
                Types: str

            pat_token:
                Specifies the PAT token generated from VantageCloud Lake Console.
                Types: str

            pem_file:
                Specifies the path to private key file which is generated from VantageCloud Lake Console.
                Types: str

            auth_token:
                Specifies the authentication token required to access services running
                on Teradata Vantage.

            expiration_time:
                Specifies the expiration time of the token in seconds. After expiry time JWT token expires and
                UserEnv methods does not work, user should regenerate the token.
                Note:
                    This option is used only for PAT and not for OAuth.
                Default Value: 31536000
                Types: int

            kid:
                Specifies the name of the key which is used while generating 'pem_file'.
                Note:
                    * Use the argument "kid" only when key used during the pem file generation is different
                      from pem file name. For example, if you use the key as 'key1' while generating pem file
                      and the name of the pem file is `key1(1).pem`, then pass value 'key1' to the argument "kid".
                Types: str

            auth_url:
                Optional Argument.
                Specifies the endpoint URL for a keycloak server.
                Types: str

            rest_client:
                Optional Argument.
                Specifies the service for which keycloak token is to be generated.
                Permitted values: "VECTORSTORE"
                Default value: "VECTORSTORE"
                Types: str

            auth_mech:
                Specifies the mechanism to be used for generating authentication token.
                Notes:
                    * User must use this argument if Basic authentication is to be used.
                    * When "auth_mech" is provided, other arguments are used in the following
                      combination as per value of "auth_mech":
                        * OAuth: Token generation is done through OAuth by using client id
                                 which can be sepcified by user in "client_id" argument or
                                 can be derived internally from "base_url".
                        * PAT  : Token generation is done using "pat_token" and "pem_file".
                        * BASIC: Authentication is done via Basic authentication mechanism
                                 using user credentials passed in "username" and "password"
                                 arguments.
                        * JWT  : Readily available token in "auth_token" argument is used.
                        * KEYCLOAK: Token generation is done using keycloak.
                Permitted Values: "OAuth", "PAT", "BASIC", "JWT", "KEYCLOAK".
                Types: str

    RETURNS:
        A Teradata sqlalchemy engine object.

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>> from teradataml.context.context import *

        # Example 1: Create context using hostname, username and password
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword')

        # Example 2: Create context using already created sqlalchemy engine
        >>> from sqlalchemy import create_engine
        >>> sqlalchemy_engine  = create_engine('teradatasql://'+ tduser +':' + tdpassword + '@'+tdhost)
        >>> td_context = create_context(tdsqlengine = sqlalchemy_engine)

        # Example 3: Creating context for Vantage with default logmech 'TD2'
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword', logmech = 'TD2')

       # Example 4: Creating context for Vantage with logmech as 'TDNEGO'
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword', logmech = 'TDNEGO')

        # Example 5: Creating context for Vantage with logmech as 'LDAP'
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword', logmech = 'LDAP')

        # Example 6: Creating context for Vantage with logmech as 'KRB5'
        >>> td_context = create_context(host = 'tdhost', logmech = 'KRB5')

        # Example 7: Creating context for Vantage with logmech as 'JWT'
        >>> td_context = create_context(host = 'tdhost', logmech = 'JWT', logdata = 'token=eyJpc...h8dA')

        # Example 8: Create context using encrypted password and key passed to 'password' parameter.
        #            The password should be specified in the format mentioned below:
        #            ENCRYPTED_PASSWORD(file:<PasswordEncryptionKeyFileName>, file:<EncryptedPasswordFileName>)
        #            The PasswordEncryptionKeyFileName specifies the name of a file that contains the password encryption key
        #            and associated information.
        #            The EncryptedPasswordFileName specifies the name of a file that contains the encrypted password and
        #            associated information.
        #            Each filename must be preceded by the 'file:' prefix. The PasswordEncryptionKeyFileName must be separated
        #            from the EncryptedPasswordFileName by a single comma.
        >>> encrypted_password = "ENCRYPTED_PASSWORD(file:PassKey.properties, file:EncPass.properties)"
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = encrypted_password)

        # Example 9: Create context using encrypted password in LDAP logon mechanism.
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = encrypted_password,
        ...                             logmech = 'LDAP')

       # Example 10: Create context using hostname, username, password and database parameters, and connect to a
       # different initial database by setting the database parameter.
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword', database =
        ...                            'database_name')

        # Example 11: Create context using already created sqlalchemy engine, and connect to a different initial
        # database by setting the database parameter.
        >>> from sqlalchemy import create_engine
        >>> sqlalchemy_engine = create_engine('teradatasql://'+ tduser +':' + tdpassword + '@'+tdhost +
        ...                                   '/?DATABASE=database_name')
        >>> td_context = create_context(tdsqlengine = sqlalchemy_engine)

        # Example 12: Create context for Vantage with logmech as 'LDAP', and connect to a different initial
        # database by setting the database parameter.
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword', logmech = 'LDAP',
        ...                             database = 'database_name')

        # Example 13: Create context using 'tera' mode with log value set to 8 and lob_support disabled.
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword', tmode = 'tera',
        ...                             log = 8, lob_support = False)

        # Example 14: Create context from config file with name 'td_properties.cfg'
        #             available under current working directory.
        #             td_properties.cfg content:
        #                 host=tdhost
        #                 username=tduser
        #                 password=tdpassword
        #                 temp_database_name=tdtemp_database_name
        #                 logmech=tdlogmech
        #                 logdata=tdlogdata
        #                 database=tddatabase
        >>> td_context = create_context()

        # Example 15: Create context using the file specified in user's home directory
        #             with name user_td_properties.cfg.
        #             user_td_properties.cfg content:
        #                 host=tdhost
        #                 username=tduser
        #                 password=tdpassword
        #                 temp_database_name=tdtemp_database_name
        #                 logmech=tdlogmech
        #                 logdata=tdlogdata
        #                 database=tddatabase
        >>> td_context = create_context(config_file = "user_td_properties.cfg")

        # Example 16: Create context using environment variables.
        #             Set these using os.environ and then run the example:
        #                  os.environ['TD_HOST'] = 'tdhost'
        #                  os.environ['TD_USERNAME'] = 'tduser'
        #                  os.environ['TD_PASSWORD'] = 'tdpassword'
        #                  os.environ['TD_TEMP_DATABASE_NAME'] = 'tdtemp_database_name'
        #                  os.environ['TD_LOGMECH'] = 'tdlogmech'
        #                  os.environ['TD_LOGDATA'] = 'tdlogdata'
        #                  os.environ['TD_DATABASE'] = 'tddatabase'
        >>> td_context = create_context()

        # Example 17: Create a context by providing username and password. Along with it,
        #             set authentication token by providing the pem file and pat token.
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword',
        ...                             base_url = 'base_url', pat_token = 'pat_token', pem_file = 'pem_file')

        # Example 18: Create a context by providing username and password. Along with it,
        #             generate authentication token by providing the client id.
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword',
        ...                             base_url = 'base_url', client_id = 'client_id')

        # Example 19: Create context and set authentication token by providing all the details in a config file.
        #             td_properties.cfg content:
        #                 host=tdhost
        #                 username=tduser
        #                 password=tdpassword
        #                 base_url=base_url
        #                 pat_token=pat_token
        #                 pem_file=pem_file
        >>> td_context = create_context()

        # Example 20: Create context and set authentication token by providing all the details in environment variables.
        #             Set these using os.environ and then run the example:
        #                  os.environ['TD_HOST'] = 'tdhost'
        #                  os.environ['TD_USERNAME'] = 'tduser'
        #                  os.environ['TD_PASSWORD'] = 'tdpassword'
        #                  os.environ['TD_BASE_URL'] = 'base_url'
        #                  os.environ['TD_PAT_TOKEN'] = 'pat_token'
        #                  os.environ['TD_PEM_FILE'] = 'pem_file'
        >>> td_context = create_context()

        # Example 21: Create context with sql_timeout set to 3.
        >>> td_context = create_context(host = 'tdhost', username = 'tduser', password = 'tdpassword', sql_timeout = 3)

        # Example 22: Create context and set authentication token via Basic authentication mechanism
        #             using username and password.
        >>> import getpass
        >>> create_context(host="host",
        ...                username=getpass.getpass("username : "),
        ...                password=getpass.getpass("password : "),
        ...                base_url=getpass.getpass("base_url : "),
        ...                auth_mech="BASIC")

        # Example 23: Create context and set authentication token by providing auth_mech argument.
        >>> import getpass
        >>> create_context(host="vcl_host",
        ...                username=getpass.getpass("username : "),
        ...                password=getpass.getpass("password : "),
        ...                base_url=getpass.getpass("base_url : "),
        ...                auth_mech="OAuth")

        # Example 24: Create context and set authentication token by providing auth_url and
        #             rest_client arguments.
        >>> import getpass
        >>> create_context(host="host",
        ...                username=getpass.getpass("username : "),
        ...                password=getpass.getpass("password : "),
        ...                base_url=getpass.getpass("base_url : "),
        ...                auth_url=getpass.getpass("auth_url : "),
        ...                rest_client=getpass.getpass("rest_client : "))
    """
    global td_connection
    global td_sqlalchemy_engine
    global temporary_database_name
    global user_specified_connection
    global python_packages_installed
    global python_version_vantage
    global python_version_local
    global td_user

    # Check if the user has provided the connection parameters or tdsqlengine.
    # If not, check if the user has provided the connection parameters in the environment variables.
    # If not, check if the user has provided the connection parameters in the config file.
    if not (host or tdsqlengine) and host != "":
        return _load_context_from_env_config(kwargs.pop('config_file', 'td_properties.cfg'))

    awu_matrix = []
    awu_matrix.append(["host", host, True, (str), True])
    awu_matrix.append(["username", username, True, (str), True])
    awu_matrix.append(["password", password, True, (str), True])
    awu_matrix.append(["tdsqlengine", tdsqlengine, True, (Engine)])
    awu_matrix.append(["logmech", logmech, True, (str), True])
    awu_matrix.append(["logdata", logdata, True, (str), True])
    awu_matrix.append(["database", database, True, (str), True])
    # set_auth_token parameters
    _set_auth_token_params = {}
    auth_mech = kwargs.get('auth_mech', None)
    for param in ['base_url', 'pat_token', 'pem_file', 'client_id', 'auth_token', 'expiration_time',
                  'kid', 'auth_mech', 'auth_url', 'rest_client']:
        if kwargs.get(param):
            _set_auth_token_params[param] = kwargs.pop(param)

    # Set the "sql_timeout" parameter to "request_timeout" which is consumed by teradatasql.
    if kwargs.get('sql_timeout'):
        awu_matrix.append(["sql_timeout", kwargs.get('sql_timeout'), True, (int), True])
        kwargs['request_timeout'] = kwargs.pop('sql_timeout')

    awu = _Validators()
    awu._validate_function_arguments(awu_matrix)

    # Clearing the internal buffer.
    _InternalBuffer.clean()
    if logmech == "JWT" and not logdata:
        raise TeradataMlException(Messages.get_message(MessageCodes.DEPENDENT_ARG_MISSING,
                                                       'logdata',
                                                       'logmech=JWT'),
                                  MessageCodes.DEPENDENT_ARG_MISSING)

    # Setting the filter to raise warning every time.
    warnings.simplefilter("always", TeradataMlRuntimeWarning)
    # Throwing warning and removing context if any.
    if td_connection is not None:
        warnings.warn(Messages.get_message(MessageCodes.OVERWRITE_CONTEXT), stacklevel=2)
        remove_context()

    # Check if teradata sqlalchemy engine is provided by the user    
    if tdsqlengine:
        try:
            td_connection = tdsqlengine.connect()
            td_sqlalchemy_engine = tdsqlengine
            user_specified_connection = True
        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                      MessageCodes.CONNECTION_FAILURE) from err
    # Check if host and username and password are provided
    elif host:
        username = '' if username is None else username

        if logmech and logmech.upper() in ['JWT', 'BROWSER']:
            host_value = host
        elif logmech and logmech.upper() == 'KRB5':
            host_value = '{}:@{}'.format(username, host)
        else:
            host_value = '{}:{}@{}'.format(username, password, host)
        url_object = URL.create(
            "teradatasql",
            username=username,
            password=password,  # plain (unescaped) text
            host=host,
            query=_get_other_connection_parameters(logmech, logdata, database, **kwargs)
        )

        try:
            td_sqlalchemy_engine = create_engine(url_object)
            td_connection = td_sqlalchemy_engine.connect()
            td_user = username.upper()

            # Masking sensitive information - password, logmech and logdata.
            if password:
                try:
                    # Below statement raises an AttributeError with SQLAlchemy
                    # version 1.4.x
                    td_sqlalchemy_engine.url.password = "***"
                except AttributeError:
                    # Masking the password should be different from above as SQLAlchemy
                    # converted _URL object to immutable object from version 1.4.x.
                    new_url = td_sqlalchemy_engine.url.set(password="***")
                    td_sqlalchemy_engine.url = new_url
                except Exception:
                    pass
            _mask_logmech_logdata()

            user_specified_connection = False

        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                      MessageCodes.CONNECTION_FAILURE) from err

    python_packages_installed = False
    python_version_vantage = None
    python_version_local = sys.version.split(" ")[0].strip()

    # Assign the tempdatabase name to global
    if temp_database_name is None:
        temporary_database_name = _get_current_databasename()
    else:
        temporary_database_name = temp_database_name

    # Connection is established initiate the garbage collection
    atexit.register(__cleanup_garbage_collection)
    __cleanup_garbage_collection()
    # Initialise Dag
    __initalise_dag()

    # Set database version.
    _get_database_version()
    # Set current database name.
    _get_current_databasename()
    # Set database user name.
    _get_database_username()

    # Process Analytic functions.
    from teradataml.analytics import _process_analytic_functions
    _process_analytic_functions()

    if _set_auth_token_params.get('base_url'):
        from teradataml.scriptmgmt.lls_utils import set_auth_token
        try:
            # password needs to be passed to set_auth_token only when any of the following is True:
            # 1. auth_mech is set to either 'basic' or 'keycloak'
            # 2. 'auth_url' argument is passed which represents 'keycloak' authentication mechanism.
            if ((auth_mech and auth_mech.lower() in ['basic', 'keycloak']) or
                _set_auth_token_params.get('auth_url'))\
                    and password:
                _set_auth_token_params['password'] = password
            set_auth_token(**_set_auth_token_params)
        except Exception as err:
            print("Connection to Vantage established successfully.")
            mssg = f"Failed to set authentication token. Rerun \"set_auth_token()\" again to set the authentication token." \
                   f" Reason for failure: {err.args[0]}"
            warnings.warn(mssg, stacklevel=2)

    # Add global lock to internal buffer
    _InternalBuffer.add(global_lock=threading.Lock())

    # Set _check_py_version to True to check the python version between local and Vantage.
    _InternalBuffer.add(_check_py_version=True)

    # Return the connection by default
    return td_sqlalchemy_engine


def _load_context_from_env_config(config_file=None):
    """
    DESCRIPTION:
        Reads the connection parameters from the configuration file or environment variables.

    PARAMETERS:
        config_file:
            Optional Argument.
            Specifies the name of the configuration file to read the connection parameters.
            Types: str

    RETURNS:
        A Teradata sqlalchemy engine object.

    RAISES:
        TeradataMlException
    """
    host = os.environ.get('TD_HOST')
    if host:
        connection_params_from_env = {key[3:].lower(): value for key, value in os.environ.items()
                                      if key.startswith('TD_')}
        return create_context(**connection_params_from_env)
    elif config_file is not None:
        connection_params_from_file = dotenv_values(config_file)
        if connection_params_from_file.get('host'):
            return create_context(**connection_params_from_file)
    raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_PARAMS),
                              MessageCodes.MISSING_ARGS)


def _mask_logmech_logdata():
    """
    Masks sensitive connection information LOGMECH, LOGDATA exposed by sqlalchemy engine object
    """
    global td_sqlalchemy_engine
    try:
        # Below statement raises a TypeError with SQLAlchemy version 1.4.x
        if ('LOGMECH' in td_sqlalchemy_engine.url.query):
            td_sqlalchemy_engine.url.query['LOGMECH'] = "***"
        if ('LOGDATA' in td_sqlalchemy_engine.url.query):
            td_sqlalchemy_engine.url.query['LOGDATA'] = "***"
    except TypeError:
        # Masking the password should be different from above as SQLAlchemy
        # converted _URL object to immutable object from version 1.4.x.
        new_url = td_sqlalchemy_engine.url.update_query_dict({"LOGMECH": "***", "LOGDATA": "***"})
        td_sqlalchemy_engine.url = new_url
    except Exception:
        pass


def get_context():
    """
    DESCRIPTION:
        Returns the Teradata Vantage connection associated with the current context.

    PARAMETERS:
        None

    RETURNS:
        A Teradata sqlalchemy engine object.

    RAISES:
        None.

    EXAMPLES:
        td_sqlalchemy_engine = get_context()
        
    """
    global td_sqlalchemy_engine
    return td_sqlalchemy_engine


def get_connection():
    """
    DESCRIPTION:
        Returns the Teradata Vantage connection associated with the current context.

    PARAMETERS:
        None

    RETURNS:
        A Teradata dbapi connection object.

    RAISES:
        None.

    EXAMPLES:
        tdconnection = get_connection()
        
    """
    global td_connection
    return td_connection


@collect_queryband(queryband='SetCxt')
def set_context(tdsqlengine, temp_database_name=None):
    """
    DESCRIPTION:
        Specifies a Teradata Vantage sqlalchemy engine as current context.

    PARAMETERS:
        tdsqlengine:
            Required Argument.
            Specifies Teradata Vantage sqlalchemy engine object that should be used to establish a Teradata Vantage
            connection.
            Types: str
            
        temp_database_name:
            Optional Argument.
            Specifies the temporary database name where temporary tables, views will be created.
            Types: str

    RETURNS:
        A Teradata Vantage connection object.

    RAISES:
        TeradataMlException

    EXAMPLES:
        set_context(tdsqlengine = td_sqlalchemy_engine)
        
    """
    global td_connection
    global td_sqlalchemy_engine
    global temporary_database_name
    global user_specified_connection
    global python_packages_installed
    global python_version_local
    global python_version_vantage
    if td_connection is not None:
        # Clearing the internal buffer.
        _InternalBuffer.clean()
        warnings.warn(Messages.get_message(MessageCodes.OVERWRITE_CONTEXT), stacklevel=2)
        remove_context()

    if tdsqlengine:
        try:
            td_connection = tdsqlengine.connect()
            td_sqlalchemy_engine = tdsqlengine
            # Assign the tempdatabase name to global
            if temp_database_name is None:
                temporary_database_name = _get_current_databasename()
            else:
                temporary_database_name = temp_database_name

            user_specified_connection = True
        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(MessageCodes.CONNECTION_FAILURE),
                                      MessageCodes.CONNECTION_FAILURE) from err
    else:
        return None

    python_packages_installed = False
    python_version_vantage = None
    python_version_local = sys.version.split(" ")[0].strip()

    # Initialise Dag
    __initalise_dag()

    # Add global lock to internal buffer
    _InternalBuffer.add(global_lock=threading.Lock())

    # Set _check_py_version to True to check the python version between local and Vantage.
    _InternalBuffer.add(_check_py_version=True)

    return td_connection


@collect_queryband(queryband='RmCxt')
def remove_context():
    """
    DESCRIPTION:
        Removes the current context associated with the Teradata Vantage connection.

    PARAMETERS:
        None.

    RETURNS:
        None.

    RAISES:
        None.

    EXAMPLES:
        remove_context()
        
    """
    global td_connection
    global td_sqlalchemy_engine
    global user_specified_connection
    global python_packages_installed
    global python_version_vantage
    global python_version_local
    global td_user

    # Initiate the garbage collection
    __cleanup_garbage_collection()

    # Clearing the internal buffer.
    _InternalBuffer.clean()

    # Check if connection is established or not.
    if user_specified_connection is not True:
        try:
            # Close the connection if not user specified connection.
            td_connection.close()
            td_sqlalchemy_engine.engine.dispose()
        except TeradataMlException:
            raise
        except Exception as err:
            raise TeradataMlException(Messages.get_message(MessageCodes.DISCONNECT_FAILURE),
                                      MessageCodes.DISCONNECT_FAILURE) from err
    td_connection = None
    td_sqlalchemy_engine = None
    python_packages_installed = False
    python_version_local = None
    python_version_vantage = None
    td_user = None
    configure._current_database_name = None
    configure._database_username = None
    configure.database_version = None
    configure.indb_install_location = ''

    # Closing Dag
    __close_dag()
    return True


def _get_context_temp_databasename(table_type=TeradataConstants.TERADATA_VIEW):
    """
    Returns the temporary database name associated with the current context.

    PARAMETERS:
        table_type:
            Optional Argument.
            Specifies the type of object - table or view.
            Default value: TeradataConstants.TERADATA_VIEW
            Types: TeradataConstant

    RETURNS:
        Database name associated with the current context

    RAISES:
        None.

    EXAMPLES:
        _get_context_temp_databasename()
        _get_context_temp_databasename(table_type=TeradataConstants.TERADATA_TABLE)
    """
    global temporary_database_name
    if table_type == TeradataConstants.TERADATA_TABLE and \
            configure.temp_table_database is not None:
        return configure.temp_table_database
    if table_type == TeradataConstants.TERADATA_VIEW and \
            configure.temp_view_database is not None:
        return configure.temp_view_database
    # ELE-6710 - Use database user associated with the current context for volatile tables.
    if table_type == TeradataConstants.TERADATA_VOLATILE_TABLE:
        return _get_user()
    return temporary_database_name


def __initalise_dag():
    """
        Intialises the Dag

        PARAMETERS:
            None.

        RETURNS:
            None

        RAISES:
            None.

        EXAMPLES:
            __initalise_dag()
    """
    aed_context = AEDContext()
    # Closing the Dag if previous instance is still exists.
    __close_dag()
    # TODO: Need to add logLevel and log_file functionlaity once AED is implemented these functionalities
    aed_context._init_dag(_get_database_username(), _get_context_temp_databasename(),
                          log_level=4, log_file="")


def __close_dag():
    """
    Closes the Dag

    PARAMETERS:
        None.

    RETURNS:
        None

    RAISES:
        None.

    EXAMPLES:
        __close_dag()
    """
    try:
        AEDContext()._close_dag()
    # Ignore if any exception occurs.
    except TeradataMlException:
        pass


def _load_function_aliases():
    """
    Function to load function aliases for analytical functions
    based on the vantage version from configuration file.

    PARAMETERS:
        None

    RETURNS:
        None

    RAISES:
        TeradataMLException

    EXAMPLES:
        _load_function_aliases()
    """

    global function_alias_mappings
    function_alias_mappings = {}

    supported_engines = TeradataConstants.SUPPORTED_ENGINES.value
    vantage_versions = TeradataConstants.SUPPORTED_VANTAGE_VERSIONS.value

    __set_vantage_version()

    for vv in vantage_versions.keys():
        function_alias_mappings_by_engine = {}
        for engine in supported_engines.keys():
            alias_config_file = os.path.join(config_folder,
                                             "{}_{}".format(supported_engines[engine]["file"], vantage_versions[vv]))
            engine_name = supported_engines[engine]['name']
            ContextUtilFuncs._check_alias_config_file_exists(vv, alias_config_file)
            function_alias_mappings_by_engine[engine_name] = \
                ContextUtilFuncs._get_function_mappings_from_config_file(alias_config_file)
            function_alias_mappings[vv] = function_alias_mappings_by_engine


def _get_vantage_version():
    """
    Function to determine the underlying Vantage version.

    PARAMETERS:
        None

    RETURNS:
        A string specifying the Vantage version, else None when not able to determine it.

    RAISES:
        Warning

    EXAMPLES:
        _get_vantage_version()
    """
    if td_connection.dialect.has_table(td_connection, "versionInfo", schema="pm",
                                       table_only=True):

        # BTEQ -- Enter your SQL request or BTEQ command:
        # select * from pm.versionInfo;
        #
        # select * from pm.versionInfo;
        #
        # *** Query completed. 2 rows found. 2 columns returned.
        # *** Total elapsed time was 1 second.
        #
        # InfoKey                        InfoData
        # ------------------------------ --------------------------------------------
        # BUILD_VERSION                  08.10.00.00-e84ce5f7
        # RELEASE                        Vantage 1.1 GA

        try:
            vantage_ver_qry = "select InfoData from pm.versionInfo where InfoKey = 'RELEASE' (NOT CASESPECIFIC)"
            res = execute_sql(vantage_ver_qry)
            return res.fetchall()[0][0]
        except:
            return None
    else:
        # If "pm.versionInfo" does not exist, then vantage version is 1.0
        return "vantage1.1"


def _get_database_version():
    """
    DESCRIPTION:
        An internal function to determine the underlying Vantage Database version.

    PARAMETERS:
        None

    RETURNS:
        A string specifying the Vantage Database version, else None when not able to determine it.

    RAISES:
        None

    EXAMPLES:
        _get_database_version()
    """

    # BTEQ -- Enter your SQL request or BTEQ command:
    # select * from DBC.DBCInfoV;
    # *** Query completed. 3 rows found. 2 columns returned.
    # *** Total elapsed time was 1 second.
    #
    # InfoKey                        InfoData
    # ------------------------------ --------------------------------------------
    # VERSION                        17.05a.00.147
    # LANGUAGE SUPPORT MODE          Standard
    # RELEASE                        17.05a.00.147

    try:
        if configure.database_version is None:
            configure.database_version = execute_sql(Query.VANTAGE_VERSION.value).fetchall()[0][0]
        return configure.database_version
    except:
        return None


def __set_vantage_version():
    """
    Function to set the configuration option vantage_version.

    PARAMETERS:
        None

    RETURNS:
        None

    RAISES:
        TeradataMLException

    EXAMPLES:
        __set_vantage_version()
    """
    vantage_version = _get_vantage_version()
    if vantage_version is None:
        # Raise warning here.
        warnings.warn(Messages.get_message(
            MessageCodes.UNABLE_TO_GET_VANTAGE_VERSION).format("vantage_version", configure.vantage_version))
    elif "vantage1.1" in vantage_version.lower().replace(" ", ""):
        configure.vantage_version = "vantage1.1"
    elif "mlengine9.0" in vantage_version.lower().replace(" ", ""):
        configure.vantage_version = "vantage1.3"
    elif "mlengine08.10" in vantage_version.lower().replace(" ", ""):
        configure.vantage_version = "vantage2.0"
    else:
        # If "pm.versionInfo" does not exist, then vantage version is 1.0
        configure.vantage_version = "vantage1.0"


def _get_function_mappings():
    """
    Function to return function aliases for analytical functions.

    PARAMETERS:
        None

    RETURNS:
        Dict of function aliases of the format
        {'mle' : {'func_name': "alias_name", ...},
        'sqle' : {'func_name': "alias_name", ...}
        ......
        }

    RAISES:
        None

    EXAMPLES:
        get_function_aliases()
    """
    global function_alias_mappings
    return function_alias_mappings


def _get_user():
    """
    DESCRIPTION:
        An internal function to get the database username associated with the current context.

    PARAMETERS:
        None.

    RETURNS:
        Database username associated with the current context.

    RAISES:
        TeradataMlException

    EXAMPLES:
        _get_user()
    """
    global td_user
    if not td_user:
        td_user = _get_database_username()
    return td_user


def _get_host():
    """
    DESCRIPTION:
        An internal function to get the host associated with the current context.
    
    PARAMETERS:
        None.
    
    RETURNS:
        Host associated with the current context.
    
    RAISES:
        None.
    
    EXAMPLES:
        _get_host()
    """
    if td_connection is None:
        return None
    else:
        return td_sqlalchemy_engine.url.host


def _get_host_ip():
    """
    DESCRIPTION:
        Function to return the host IP address or host name associated with the current context.

    PARAMETERS:
        None.

    RETURNS:
        Host IP address or host name associated with the current context.

    RAISES:
        None.

    EXAMPLES:
        GarbageCollector._get_host_ip()
    """
    # Return None if connection is not established.
    if td_connection is None:
        return None

    host = _get_host()
    try:
        # Validate if host_ip is a valid IP address (IPv4 or IPv6)
        ipaddress.ip_address(host)
        return host
    except ValueError:
        # If host is not an IP address, get the IP address by DNS name from _InternalBuffer.
        dns_host_ip = _InternalBuffer.get('dns_host_ip')
        if dns_host_ip:
            return dns_host_ip

        # If DNS host ip not found, resolve the host name to get the IP address.
        # If there is issue in resolving the host name, it will proceed with DNS host as it is.
        try:
            # Get the list of addresses(compatible for both IPv4 and IPv6)
            addr_info = socket.getaddrinfo(host, None)
            # Pick the first address from the list
            host_ip = addr_info[0][4][0]
            # Add the DNS host IP to the _InternalBuffer.
            _InternalBuffer.add(dns_host_ip=host_ip)
        except socket.gaierror:
            # Use dns host as it is
            host_ip = host
    return host_ip


class ContextUtilFuncs():
    @staticmethod
    def _check_alias_config_file_exists(vantage_version, alias_config_file):
        """
        Function to validate whether alias_config_file exists for the current vantage version.

        PARAMETERS:
            vantage_version:
                Required Argument.
                Specifies the current vantage version.

            alias_config_file:
                Required Argument.
                Specifies the location of configuration file to be read.

        RETURNS:
            True, if the file 'alias_config_file' is present in the
            teradataml/config directory for the current vantage version.

        RAISES:
            TeradataMLException

        EXAMPLES:
            ContextUtilFuncs._check_alias_config_file_exists("vantage1.0", "config_file_location")

        """
        # Raise exception if alias config file is not defined.
        if not Path(alias_config_file).exists():
            raise TeradataMlException(Messages.get_message(
                MessageCodes.CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND).format(alias_config_file,
                                                                        vantage_version),
                                      MessageCodes.CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND)
        return True

    @staticmethod
    def _get_function_mappings_from_config_file(alias_config_file):
        """
        Function to return the function mappings given the location of configuration file in
        argument 'alias_config_file'.

        PARAMETERS:
            alias_config_file:
                Required Argument.
                Specifies the location of configuration file to be read.

        RETURNS:
            Function mappings as a dictionary of function_names to alias_names.

        RAISES:
            TeradataMLException

        EXAMPLES:
            ContextUtilFuncs._get_function_mappings_from_config_file("config_file_location")

        """
        repeated_function_names = []
        function_mappings = {}
        invalid_function_mappings = []
        invalid_function_mappings_line_nos = []
        # Reading configuration files
        with open(alias_config_file, 'r') as fread:
            for line_no, line in enumerate(fread.readlines()):
                line = line.strip()

                # Ignoring empty lines in the config files.
                if line == "":
                    continue

                # If the separator ":" is not present.
                if ':' not in line:
                    invalid_function_mappings.append(line)
                    invalid_function_mappings_line_nos.append(str(line_no + 1))
                else:
                    func_name, alias_name = line.split(":")
                    func_name = func_name.strip()
                    alias_name = alias_name.strip()

                    # First line of 'alias_config_file' has header "functionName:aliasName".
                    if line_no == 0 and func_name == "functionName" and alias_name == "aliasName":
                        continue

                    if func_name == "" or alias_name == "":
                        invalid_function_mappings.append(line)
                        invalid_function_mappings_line_nos.append(str(line_no + 1))
                        continue

                    if func_name.lower() in function_mappings:
                        repeated_function_names.append(func_name.lower())

                    # Loading function maps with lower values for key.
                    function_mappings[func_name.lower()] = alias_name

        # Presence of Invalid function mappings in the 'alias_config_file'.
        if len(invalid_function_mappings) > 0:
            err_ = Messages.get_message(MessageCodes.CONFIG_ALIAS_INVALID_FUNC_MAPPING)
            err_ = err_.format("', '".join(invalid_function_mappings),
                               ", ".join(invalid_function_mappings_line_nos),
                               alias_config_file)
            raise TeradataMlException(err_, MessageCodes.CONFIG_ALIAS_INVALID_FUNC_MAPPING)

        # Raising teradataml exception if there are any duplicates in function names.
        if len(repeated_function_names) > 0:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.CONFIG_ALIAS_DUPLICATES).format(alias_config_file,
                                                             ", ".join(repeated_function_names)),
                                      MessageCodes.CONFIG_ALIAS_DUPLICATES)

        return function_mappings
