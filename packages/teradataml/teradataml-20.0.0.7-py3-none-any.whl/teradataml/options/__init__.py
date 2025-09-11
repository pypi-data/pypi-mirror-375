from teradataml.common.deprecations import argument_deprecation
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.options.configure import configure
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.telemetry_utils.queryband import collect_queryband


@collect_queryband(queryband="StCnfgPrms")
def set_config_params(**kwargs):
    """
    DESCRIPTION:
        Function to set the configurations in Vantage. Alternatively, user can set the
        configuration parameters independently using 'teradataml.configure' module.

    PARAMETERS:
        kwargs:
            Optional Argument.
            Specifies keyword arguments. Accepts following keyword arguments:

            certificate_file:
                Optional Parameter.
                Specifies the path of the certificate file, which is used in
                encrypted REST service calls.
                Types: str

            default_varchar_size:
                Specifies the size of varchar datatype in Teradata Vantage, the default
                size is 1024.
                User can configure this parameter using options.
                Types: int

            vantage_version:
                Specifies the Vantage version of the system teradataml is connected to.
                Types: string

            val_install_location:
                Specifies the name of the database where Vantage Analytic Library functions
                are installed.
                Types: string

            byom_install_location:
                Specifies the name of the database where Bring Your Own Model functions
                are installed.
                Types: string

            database_version:
                Specifies the actual database version of the system teradataml is connected to.
                Types: string

            read_nos_function_mapping:
                Specifies the function mapping name for the read_nos table operator function.
                Types: string

            write_nos_function_mapping:
                Specifies the function mapping name for the write_nos table operator function.
                Types: string

            inline_plot:
                Specifies whether to display the plot inline or not.
                Note:
                    Not applicable for machines running Linux and Mac OS.
                Types: bool

            indb_install_location:
                Specifies the installation location of In-DB Python package.
                Types: str
                Default Value: "/var/opt/teradata/languages/sles12sp3/Python/"
                Note:
                    The default value is the installation location of In-DB 2.0.0 packages.
                    Older versions of In-DB packages are installed at
                    "/opt/teradata/languages/Python/".

            openml_user_env:
                Specifies the user environment to be used for OpenML.
                Types: UserEnv

            local_storage:
                Specifies the location on client where garbage collector folder will be created.
                Types: string

            stored_procedure_install_location:
                Specifies the name of the database where stored procedures
                are installed.
                Types: string

            table_operator:
                Specifies the name of the table operator.
                Permitted Values: "Apply", "Script"
                Types: string

            temp_object_type:
                Specifies the type of temporary database objects created internally by teradataml.
                Permitted Values:
                    * "VT" - Volatile tables.
                Types: String
                Default Value: None
                Note:
                    * If this option is set to "VT" and "persist" argument of analytic functions is
                      set to True, then volatile tables are not created as volatile table can't be
                      persisted and "persist" argument takes precedence.
                    * Default behavior is to create views that will be garbage collected at the end.

    RETURNS:
        bool

    RAISES:
        None

    EXAMPLES:
        # Example 1: Set configuration params using set_config_params() function.
        >>> from teradataml import set_config_params
        >>> set_config_params(certificate_file="cert.crt",
        ...                   default_varchar_size=512,
        ...                   val_install_location="VAL_USER",
        ...                   read_nos_function_mapping="read_nos_fm",
        ...                   write_nos_function_mapping="write_nos_fm",
        ...                   indb_install_location="/opt/teradata/languages/Python",
        ...                   local_storage="/Users/gc")
        True

        # Example 2: Alternatively, set configuration parameters without using set_config_params() function.
        #            To do so, we will use configure module.
        >>> from teradataml import configure
        >>> configure.certificate_file="cert.crt"
        >>> configure.default_varchar_size=512
        >>> configure.val_install_location="VAL_USER"
        >>> configure.read_nos_function_mapping="read_nos_fm"
        >>> configure.write_nos_function_mapping="write_nos_fm"
        >>> configure.indb_install_location="/opt/teradata/languages/Python"
        >>> configure.local_storage = "/Users/gc/"
    """
    for option in kwargs:
        try:
            if option == "auth_token" or option == 'ues_url':
                raise TeradataMlException(Messages.get_message(
                    MessageCodes.FUNC_EXECUTION_FAILED, 'set_config_params',
                    'Setting of parameter \'{}\' is prohibited from set_config_params(). '
                    'Use set_auth_token() to set parameter.'.format(option)),
                    MessageCodes.FUNC_EXECUTION_FAILED)
            else:
                setattr(configure, option, kwargs[option])
        except AttributeError as e:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.FUNC_EXECUTION_FAILED, 'set_config_params', 'Invalid parameter \'{}\'.'.format(option)),
                                      MessageCodes.FUNC_EXECUTION_FAILED)
    return True
