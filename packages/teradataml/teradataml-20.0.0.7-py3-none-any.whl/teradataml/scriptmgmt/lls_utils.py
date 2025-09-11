"""
Copyright (c) 2020 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Trupti.purohit@teradata.com
Secondary Owner: Gouri.patwardhan@Teradata.com

teradataml load library service wrappers.
----------
All teradataml wrappers to provide interface to load library service stored procedures
from Open Analytics Framework.
"""
import base64
import concurrent.futures
import functools
import json
import operator
import os
import warnings
from json.decoder import JSONDecodeError
from time import sleep, time
from urllib.parse import urlparse

import pandas as pd

from teradataml import configure
from teradataml.clients.auth_client import _AuthWorkflow
from teradataml.clients.keycloak_client import _KeycloakManager
from teradataml.clients.pkce_client import _DAWorkflow
from teradataml.common.constants import (AsyncOpStatus, AsyncStatusColumns,
                                         AuthMechs, HTTPRequest, TDServices)
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import _get_user, get_connection
from teradataml.scriptmgmt.UserEnv import (UserEnv, _AuthToken,
                                           _get_auth_token, _get_ccp_url,
                                           _get_ues_url, _process_ues_response)
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.utils.utils import _async_run_id_info
from teradataml.utils.validators import _Validators


@collect_queryband(queryband="LstBsEnv")
def list_base_envs():
    """
    DESCRIPTION:
        Lists the available Python and R base environments versions configured in the
        Open Analytics Framework.
        Note:
            Function is not applicable for conda environments.
            User can use any Python version while creating conda environment as long as Anaconda supports it.

    PARAMETERS:
            None.

    RETURNS:
        Pandas DataFrame.
        If the operation is successful, function returns
        environment name, language and version of the language interpreter in a Pandas dataframe.

    RAISES:
        TeradataMlException.

    EXAMPLES:
            >>> from teradataml import list_base_envs
            >>> list_base_envs()
                   base_name language version
            0  python_3.7.13   Python  3.7.13
            1  python_3.8.13   Python  3.8.13
            2  python_3.9.13   Python  3.9.13
            3        r_4.1.3        R   4.1.3
            4        r_3.6.3        R   3.6.3
            5        r_4.0.2        R   4.0.2
            >>>
    """
    # Check if the cache data is available and is not stale.
    # If available, return the data.
    if _InternalBuffer.get('list_base_envs') is not None:
        return _InternalBuffer.get('list_base_envs')

    try:
        response = UtilFuncs._http_request(_get_ues_url("base_environments"), headers=_get_auth_token())

        response = _process_ues_response(api_name="list_base_envs", response=response)
        data = response.json()

        # If no data, raise warning.
        if len(data) == 0:
            warnings.warn(Messages.get_message(MessageCodes.NO_ENVIRONMENT_FOUND, "Python/R base"))
            return

        # Create a pandas DataFrame from data.
        _InternalBuffer.add(list_base_envs=pd.DataFrame.from_records(data))
        return _InternalBuffer.get('list_base_envs')

    except (TeradataMlException, RuntimeError):
        raise
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "list_base_envs", str(emsg))
        raise TeradataMlException(error_msg, msg_code)


@collect_queryband(queryband="LstUsrEnv")
def list_user_envs(env_name=None, **kwargs):
    """
    DESCRIPTION:
        Lists the Python OR R environments created by the session user in
        Open Analytics Framework.

    PARAMETERS:
        env_name:
            Optional Argument.
            Specifies the string or regular expression to filter name of the environment.
            Types: str

        base_env:
            Optional Argument.
            Specifies the string or regular expression to filter the base Python environment.
            Types: str

        desc:
            Optional Argument.
            Specifies the string or regular expression to filter the description
            about the environment.
            Types: str
        
        case:
            Optional Argument.
            Specifies whether filtering operation should be case sensitive or not.
            Default Value: False
            Types: boolean

        conda_env:
            Optional Argument.
            Specifies the boolean value to filter the conda environment(s).
            When set to True, all conda environments are listed.
            When set to False, all non-conda environments are listed.
            If not specified, all user environments are listed.
            Types: bool

        regex:
            Optional Argument.
            Specifies whether string passed to "env_name", "base_env", and "desc"
            should be treated as regular expression or a literal.
            When set to True, string is considered as a regular expression pattern,
            otherwise treats it as literal string.
            Default Value: True
            Types: boolean
        
        flags:
            Optional Argument.
            Specifies flags to pass for regular expressions in filtering.
            For example
                re.IGNORECASE.
            Default Value: 0
            Types: int

    RETURNS:
        Pandas DataFrame.
        Function returns remote user environments and their details in a Pandas dataframe.
        Function will help user find environments created, version of Python language used
        in the environment and description of each environment if provided at the time of
        environment creation.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # Create example environments.
        >>> create_env('Fraud_Detection',
        ...            'python_3.7.13',
        ...            'Fraud detection through time matching')
            User environment 'Fraud_detection' created.
        >>> create_env('Lie_Detection',
        ...            'python_3.7.13',
        ...            'Lie detection through time matching')
            User environment 'Lie_Detection' created.
        >>> create_env('Lie_Detection_ML',
        ...            'python_3.8.13',
        ...            'Detect lie through machine learning.')
            User environment 'Lie_Detection_ML' created.
        >>> create_env('Sales_env',
        ...            'python_3.9.13',
        ...            'Sales team environment.')
            User environment 'Sales_env' created.
        >>> create_env('Customer_Trends',
        ...            'r_4.1.3',
        ...            'Analyse customer trends.')
        User environment 'Customer_Trends' created.
        >>> create_env('Carbon_Credits',
        ...            'r_3.6.3',
        ...            'Prediction of carbon credits consumption.')
        User environment 'Carbon_Credits' created.
        >>> create_env('Sales_cond_env',
        ...            'python_3.9',
        ...            'Sales team environment.',
        ...            conda_env=True)
        Conda environment creation initiated.
        User environment 'Sales_cond_env' created.

        # Example 1: List all available user environments.
        >>> list_user_envs()
                   env_name                           env_description  base_env_name language  conda
        0    Carbon_Credits  Prediction of carbon credits consumption        r_3.6.3        R  False
        1   Customer_Trends                   Analyse customer trends        r_4.1.3        R  False
        2   Fraud_Detection     Fraud detection through time matching  python_3.7.13   Python  False
        3     Lie_Detection       Lie detection through time matching  python_3.7.13   Python  False
        4  Lie_Detection_ML      Detect lie through machine learning.  python_3.8.13   Python  False
        5         Sales_env                   Sales team environment.  python_3.9.13   Python  False
        6    Sales_cond_env                   Sales team environment.     python_3.9   Python  True


        # Example 2: List all user environments with environment name containing string
        #            "Detection" and description that contains string "."(period).
        >>> list_user_envs(env_name="Detection", desc=".", regex=False)
                   env_name                       env_description base_env_name language  conda
        2  Lie_Detection_ML  Detect lie through machine learning. python_3.8.13   Python  False
        >>>

        # Example 3: List all user environments with description that contains string "lie"
        #            and is case sensitive. 
        >>> list_user_envs(desc="lie", case=True)
                   env_name                       env_description  base_env_name language  conda
        4  Lie_Detection_ML  Detect lie through machine learning.  python_3.8.13   Python  False
        >>>

        # Example 4: List all user environments with base environment version containing string
        #            "3.".
        >>> list_user_envs(base_env="3.")
                   env_name                           env_description  base_env_name language  conda
        0    Carbon_Credits  Prediction of carbon credits consumption        r_3.6.3        R  False
        2   Fraud_Detection     Fraud detection through time matching  python_3.7.13   Python  False
        3     Lie_Detection       Lie detection through time matching  python_3.7.13   Python  False
        4  Lie_Detection_ML      Detect lie through machine learning.  python_3.8.13   Python  False
        5         Sales_env                   Sales team environment.  python_3.9.13   Python  False
        6   Sales_conda_env                   Sales team environment.     python_3.9   Python  True

        >>>

        # Example 5: List all user environments with environment name contains string "detection",
        #            description containing string "fraud" and base environment containing string "3.7".
        >>> list_user_envs("detection", desc="fraud", base_env="3.7")
                  env_name                        env_description  base_env_name language  conda
        2  Fraud_Detection  Fraud detection through time matching  python_3.7.13   Python  False
        >>>

        # Example 6: List all user environments with environment name that ends with "detection".
        >>> list_user_envs("detection$")
                  env_name                        env_description  base_env_name language  conda
        2  Fraud_Detection  Fraud detection through time matching  python_3.7.13   Python  False
        3    Lie_Detection    Lie detection through time matching  python_3.7.13   Python  False
        >>>

        # Example 7: List all user environments with description that has either "lie" or "sale".
        #            Use re.VERBOSE flag to add inline comment.
        >>> list_user_envs(desc="lie|sale # Search for lie or sale.", flags=re.VERBOSE)
                   env_name                       env_description  base_env_name language  conda
        3     Lie_Detection   Lie detection through time matching  python_3.7.13   Python  False
        4  Lie_Detection_ML  Detect lie through machine learning.  python_3.8.13   Python  False
        5         Sales_env               Sales team environment.  python_3.9.13   Python  False
        6   Sales_conda_env               Sales team environment.     python_3.9   Python  True
        >>>

        # Example 8: List all user environments where python 3 environment release version has 
        #            odd number. For e.g. python_3.7.x. 
        >>> list_user_envs(base_env="\\.\\d*[13579]\\.")
                  env_name                        env_description  base_env_name language
        1  Customer_Trends                Analyse customer trends        r_4.1.3        R
        2  Fraud_Detection  Fraud detection through time matching  python_3.7.13   Python
        3    Lie_Detection    Lie detection through time matching  python_3.7.13   Python
        5        Sales_env                Sales team environment.  python_3.9.13   Python
        >>>

        # Example 9: List all conda environments.
        >>> list_user_envs(conda_env=True)
                  env_name          env_description base_env_name language  conda
        6  Sales_conda_env  Sales team environment.    python_3.9   Python   True
        >>>
        # Remove example environments.
        remove_env("Fraud_Detection")
        remove_env("Lie_Detection")
        remove_env("Lie_Detection_ML")
        remove_env("Sales_env")
        remove_env("Carbon_Credits")
        remove_env("Customer_Trends")
        remove_env("Sales_conda_env")
    """
    base_env = kwargs.pop("base_env", None)
    desc = kwargs.pop("desc", None)
    case = kwargs.pop("case", False)
    conda_env = kwargs.pop("conda_env", None)

    __arg_info_matrix = []
    __arg_info_matrix.append(["env_name", env_name, True, (str), True])
    __arg_info_matrix.append(["base_env", base_env, True, (str), True])
    __arg_info_matrix.append(["desc", desc, True, (str), True])
    __arg_info_matrix.append(["conda_env", conda_env, True, (bool)])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    try:
        response = UtilFuncs._http_request(_get_ues_url(), headers=_get_auth_token())
        # Below condition is special case handling when remove_all_envs() used by user, remove_all_envs()
        # removes all the envs which result in a status_code 404 and due to which warnings provided in
        # list_user_envs() not appears.
        if response.status_code == 404 and "No user environments found." in response.text:
            data = []
        else:
            response = _process_ues_response(api_name="list_user_envs", response=response)
            data = response.json()

        if len(data) > 0:
            unknown_label = "Unknown"
            # Check if environment is corrupted or not. If it is corrupted, alter the details.
            for base_env_details in data:
                if base_env_details["base_env_name"] == "*":
                    base_env_details["base_env_name"] = unknown_label
                    base_env_details["language"] = unknown_label
                    base_env_details["env_description"] = "Environment is corrupted. Use remove_env() to remove environment."

            # Return result as Pandas dataframe.
            pandas_df = pd.DataFrame.from_records(data)
            # Filter based on arguments passed by user.
            exprs = []
            if env_name is not None:
                exprs.append(pandas_df.env_name.str.contains(pat=env_name, case=case, **kwargs))
            if base_env is not None:
                exprs.append(pandas_df.base_env_name.str.contains(pat=base_env, case=case, **kwargs))
            if desc is not None:
                exprs.append(pandas_df.env_description.str.contains(pat=desc, case=case, **kwargs))
            if conda_env is not None:
                exprs.append(pandas_df.conda == conda_env)

            pandas_df = pandas_df[functools.reduce(operator.and_, exprs)] if exprs else pandas_df

            # Return the DataFrame if not empty.
            if len(pandas_df) > 0:
                return pandas_df

        print("No user environment(s) found.")
    except (TeradataMlException, RuntimeError):
        raise
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "list_user_envs", emsg)
        raise TeradataMlException(error_msg, msg_code)


def __create_envs(template):
    """
    DESCRIPTION:
        Function creates remote environment(s) as per the specifications provided
        in template json file. Template file contains information about each env
        w.r.t. env name, base env name, env description, files/libs to be
        installed in env.

    PARAMETERS:
        template:
            Required Argument.
            Specifies the path to template json file to be used for
            env creation.
            Types: str

    RETURNS:
        None.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # Create environments.
        >>> __create_envs(template="create_env_template.json")
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["template", template, False, (str), True])
    # Validate argument.
    _Validators._validate_function_arguments(__arg_info_matrix)

    # Validate the file extension.
    _Validators._validate_file_extension(template, ['json'])

    # Validate existence of template file.
    _Validators._validate_file_exists(template)

    # Extract env specs from template file and
    # process request for each env one by one.
    create_env_specs = {}
    try:
        with open(template, 'r') as f:
            create_env_specs = json.load(f)
    except IOError:
        raise
    except JSONDecodeError as json_err:
        raise Exception("Failed to read template json file. {}".format(json_err))

    requested_envs = UtilFuncs._as_list(create_env_specs['env_specs'])

    last_successful_env = None
    for env_request in requested_envs:
        # Create env.
        env_name = env_request.get('env_name', None)
        conda_env = env_request.get('conda_env', False)

        if env_name:
            try:
                # Remove from dictionary and store the specifications
                # which are not required for env creation.
                files = env_request.pop('files', None)
                libs = env_request.pop('libs', None)
                libs_file_path = env_request.pop('libs_file_path', None)

                print("Creating environment '{}'...".format(env_name))
                create_env(**env_request)

                print("An empty environment '{}' is created.".format(env_name))

                env_handle = get_env(env_name)

                errored = False
                # Install files if requested any.
                if files:
                    print("Installing files in environment '{}'...".format(env_name))
                    if isinstance(files, str):
                        files = [files]

                    for file in files:
                        try:
                            if os.path.isfile(file):
                                env_handle.install_file(file)
                            elif os.path.isdir(file):
                                errored = __install_files(env_handle, file)
                        except Exception as file_installation_failure:
                            print("Failed to install file '{}' in environment '{}'.".format(file, env_name))
                            print(str(file_installation_failure))
                            errored = True
                            pass

                # Install libraries if requested any.
                if libs or libs_file_path:
                    print("Installing libraries in environment '{}'...".format(env_name))
                    try:
                        status = env_handle.install_lib(libs, libs_file_path)
                        if status['Stage'][1] == 'Errored':
                            err_message = status['Additional Details'][1].replace("Error with package maintenance -> ", "\n")
                            raise Exception(err_message)
                        else:
                            print("Libraries installation in environment '{}' - Completed.".format(env_name))
                    except Exception as lib_installation_failure:
                        error_code = MessageCodes.FUNC_EXECUTION_FAILED
                        error_msg = Messages.get_message(error_code,
                                                         "'install_lib' request for enviornment: '{}'".format(env_name),
                                                         '\n' + str(lib_installation_failure))
                        print(error_msg)
                        errored = errored or True
                        pass

                # Print specifications of created env.
                if errored:
                    print("Created environment '{}'.".format(env_name))
                    print("Part of request is not successful. Address manually.")
                else:
                    print("Created environment '{}' with specified requirements.".format(env_name))
                print(env_handle)
                last_successful_env = env_handle
            except Exception as env_creation_failure:
                print("Failed to process request for environment: '{}'".format(env_name))
                print(str(env_creation_failure))
                pass
    return last_successful_env


def __get_default_base_env(lang="python"):
    """
    DESCRIPTION:
        Function returns the name of latest environment available with
        Open Analytics Framework for given programming language.

    PARAMETERS:
        lang:
            Optional Argument.
            Specifies the language for which latest base env is to be retrieved.
            Default value: "python"
            Permitted values: "python", "r", "PYTHON", "R"
            Types: str

    RETURNS:
        Base environment name.

    RAISES:
        None.

    EXAMPLES:
        # Get default R base environment.
        >>> __get_default_base_env(lang="R")
    """
    lang = lang.lower()
    default_env_key = "default_base_env_{}".format(lang)
    # Check if the default base environment is already available.
    if _InternalBuffer.get(default_env_key) is not None:
        return _InternalBuffer.get(default_env_key)

    try:
        base_envs = list_base_envs()
        versions = base_envs[base_envs.language.str.lower() == lang]['version']
        # Convert version strings to tuples of integers for comparison
        version_tuples = [tuple(map(int, version.split('.'))) for version in versions]
        # Find the latest version tuple using max() function
        latest_version_tuple = max(version_tuples)
        # Convert the latest version tuple back to a string
        latest_version = '.'.join(map(str, latest_version_tuple))
        # Get the base environment name for the latest version and add in internal buffer.
        _InternalBuffer.add(**{default_env_key:
                                   base_envs[base_envs.version == latest_version]['base_name'].to_list()[0]})
        return _InternalBuffer.get(default_env_key)
    except Exception as base_env_err:
        raise Exception("Failed to obtain default base environment.", str(base_env_err))


def __install_files(env, directory):
    """
    Function to install files under given directory and
    all the subdirectories recursively.
    """
    errored = False
    for (dir_path, dir_names, file_names) in os.walk(directory):
        # install the files under all the directories.
        # If any problem with any file installation, skip the error
        # and proceed to install other files.
        for file_name in file_names:
            try:
                env.install_file(os.path.join(dir_path, file_name))
            except Exception as file_installation_failure:
                print("Failed to install file '{}' in environment '{}'.".format(file_name, env.env_name))
                print(str(file_installation_failure))
                errored = True

    return errored


@collect_queryband(queryband="CrtEnv")
def create_env(env_name=None, base_env=None, desc=None, template=None, conda_env=False):
    """
    DESCRIPTION:
        Creates isolated remote user environment(s) in the Open Analytics
        Framework that include a specific Python or R language interpreter version.
        Available base Python or R environments can be found using list_base_envs()
        function. When "template" argument is provided, additionally, files/libs are
        installed if specified in template file. Out of provided specifications in
        template file, if any of the environment creation fails, failure message is
        printed on console and next environment creation is taken up.

    PARAMETERS:
        env_name:
            Required when "template" is not used, optional otherwise.
            Specifies the name of the environment to be created.
            Note:
                 Either "env_name" or "template" argument must be specified.
            Types: str

        base_env:
            Optional Argument.
            Specifies the name of the base Python or R environment
            to be used to create remote user environment when "env_name"
            is provided. This argument is ignored when "template" is provided.
            Notes:
                 *   When "base_env" is not provided, highest Python
                     base environment listed by list_base_envs() is used.
                 *   When creating a conda environment, user can pass any Python version
                     supported by Anaconda to "base_env", irrespective of base environments
                     listed with list_base_envs().
            Types: str

        desc:
            Optional Argument.
            Specifies description for the remote environment when "env_name"
            is provided. This argument is ignored when "template" is provided.
            Default value: "This env '<env_name>' is created with base env
                           '<base_env>'."
            Types: str

        template:
            Required when "env_name" is not used, optional otherwise.
            Specifies the path to template json file containing details
            of the user environment(s) to be created. Using the template
            file one can create one or more user environments with same or
            different requirements. This template file can contain following
            information about the environments to be created:
                * Name of the environment. (Required)
                * Base Python version to be used. (Optional)
                * Description for the environment. (Optional)
                * Files or libraries to be installed in the environment. (Optional).

            Here is a sample example of the template file:
                {
                    "env_specs" : [
                        {
                            "env_name" : "<name of the user environment_MUST_BE_SPECIFIED>",
                            "base_env" : "<OPTIONAL_base_env>",
                            "desc": "<OPTIONAL_env_description>",
                            "libs": ["<OPTIONAL>", "<List_of_libs_to_be_installed>"] OR "<location_of_requirements.txt>"
                            "files": ["<OPTIONAL>", "<full_path_the_file>", "<full_path_to_dir>"]
                        },
                        {
                            "env_name" : "....",
                            "base_env" : "...",
                            "desc": "..",
                            "libs": ..
                            "files": ...
                        },
                        {
                            ...
                        },
                        {
                            ...
                        }
                    ]
                }
            Notes:
                * Either "template" or "env_name" argument must be specified.
                * Template file can contain details about single or multiple
                  environments to be created. At least one is required.
                * Content of template file should adhere to the syntax mentioned
                  above. Check example for more details.
            Types: str

        conda_env:
            Optional Argument.
            Specifies whether the environment to be created is a conda environment or not.
            When set to True, conda environment is created.
            Otherwise, non conda environment is created.
            Note:
                * Currently, only Python conda environment is supported.
            Default value: False
            Types: bool


    RETURNS:
        An object of class UserEnv representing the user environment.
        When template file provided with "template" has specifications for multiple
        environments, an object of class UserEnv representing last created environment
        is returned.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # List all available user environments.
        >>> list_base_envs()
                   base_name language version
                0  python_3.7.13   Python  3.7.13
                1  python_3.8.13   Python  3.8.13
                2  python_3.9.13   Python  3.9.13
                3  python_3.10.5   Python  3.10.5
                4          r_4.1        R   4.1.3
                5          r_4.0        R   4.0.5
                6          r_4.2        R   4.2.2

        # Example 1: Create a Python 3.7.13 environment with given name and description in the Vantage.
        >>> fraud_detection_env = create_env('Fraud_detection',
        ...                                  'python_3.7.13',
        ...                                  'Fraud detection through time matching')
            User environment 'Fraud_detection' created.

        # Example 2: Create a R 4.1.3 environment with given name and description in the Vantage.
        >>> fraud_detection_env = create_env('Carbon_Credits',
        ...                                  'r_4.1',
        ...                                  'Prediction of carbon credits consumption')
            User environment 'Carbon_Credits' created.

        # Example 3: Create multiple environments and install files/libraries
        #            in those by providing specifications in template file.

        # Create a template json file.
        >>> import teradataml, os, json
        >>> tdml_data_path = os.path.join(os.path.dirname(teradataml.__file__), "data")
        ... python_base_env = "python_3.9.13"
        ... r_base_env = "r_4.1"
        ... env_specs = [
        ...     {
        ...         "env_name": "env_1",
        ...         "base_env": python_base_env,
        ...         "desc": "Desc for test env 1"
        ...     },
        ...     {
        ...         "env_name": "env_2",
        ...         "base_env": r_base_env,
        ...         "libs": ["glm2", "stringi"]
        ...         "files": [os.path.join(tdml_data_path, "load_example_data.py"),
        ...                   os.path.join(tdml_data_path, "scripts")]
        ...     }
        ... ]
        ... json_data = {"env_specs": env_specs}
        ... with open("template.json", "w") as json_file:
        ...    json.dump(json_data, json_file)

        # Create environments.
        >>> create_env(template="template.json")
        Creating environment 'env_1'...
        User environment 'env_1' created.
        An empty environment 'env_1' is created.
        Created environment 'env_1' with specified requirements.
        Environment Name: env_1
        Base Environment: python_3.9.13
        Description: Desc for test env 1

        Creating environment 'env_2'...
        User environment 'env_2' created.
        An empty environment 'env_2' is created.
        Installing files in environment 'env_2'...
        File 'load_example_data.py' installed successfully in the remote user environment 'env_2'.
        File 'mapper.py' installed successfully in the remote user environment 'env_2'.
        File 'mapper.R' installed successfully in the remote user environment 'env_2'.
        File 'mapper_replace.py' installed successfully in the remote user environment 'env_2'.
        File installation in environment 'env_2' - Completed.
        Created environment 'env_2' with specified requirements.
        Environment Name: env_2
        Base Environment: r_4.1
        Description: This env 'env_2' is created with base env 'r_4.1'.


        ############ Files installed in User Environment ############

                           File   Size             Timestamp
        0             mapper.py    547  2023-11-07T10:14:06Z
        1              mapper.R    613  2023-11-07T10:14:09Z
        2  load_example_data.py  14158  2023-11-07T10:14:03Z
        3     mapper_replace.py    552  2023-11-07T10:14:12Z


        ############ Libraries installed in User Environment ############

                  name  version
        0   KernSmooth  2.23-20
        1         MASS   7.3-55
        2       Matrix    1.4-0
        3         base    4.1.3
        4         boot   1.3-28
        5        class   7.3-20
        6      cluster    2.1.2
        7    codetools   0.2-18
        8     compiler    4.1.3
        9     datasets    4.1.3
        10     foreign   0.8-82
        11   grDevices    4.1.3
        12    graphics    4.1.3
        13        grid    4.1.3
        14     lattice  0.20-45
        15     methods    4.1.3
        16        mgcv   1.8-39
        17        nlme  3.1-155
        18        nnet   7.3-17
        19    parallel    4.1.3
        20     remotes    2.4.2
        21       rpart   4.1.16
        22     spatial   7.3-15
        23     splines    4.1.3
        24       stats    4.1.3
        25      stats4    4.1.3
        26    survival   3.2-13
        27       tcltk    4.1.3
        28       tools    4.1.3
        29       utils    4.1.3

        # Example 4: Create a Conda Python 3.8 environment with given name and
        #            description in the Vantage.
        >>> fraud_detection_env = create_env('Fraud_detection_conda',
        ...                                  'python_3.8',
        ...                                  'Fraud detection through time matching',
        ...                                   conda_env=True)
        Conda environment creation initiated.
        User environment 'Fraud_detection_conda' created.

        # Example 5: Create a Conda R 4.2 environment with given name and
        #            description in the Vantage.
        >>> conda_r_env = create_env('conda_r_env',
        ...                          'r_4.2',
        ...                          'Conda R environment',
        ...                           conda_env=True)
        Conda environment creation initiated.
        User environment 'conda_r_env' created.
    """

    # Either env_name or template can be used.
    # At least one is required.
    _Validators._validate_mutually_exclusive_arguments(env_name,
                                                       "env_name",
                                                       template,
                                                       "template",
                                                       skip_all_none_check=False)
    # When env_name is provided, proceed with the conventional way.
    if env_name is not None:
        __arg_info_matrix = []
        __arg_info_matrix.append(["env_name", env_name, False, (str), True])
        __arg_info_matrix.append(["base_env", base_env, True, (str), True])
        __arg_info_matrix.append(["desc", desc, True, (str)])
        __arg_info_matrix.append(["conda_env", conda_env, True, (bool)])

        # Validate arguments
        _Validators._validate_function_arguments(__arg_info_matrix, skip_empty_check=False)

        # Get the latest python base env in OpenAF, if base_env is not provided,
        # Or if base_env is provided and not in the list of base envs.
        # Note: By default python base env is obtained.
        if configure.ues_url is not None and \
                get_connection() is not None:
            # Check if base_env is provided or not in the list of base envs.

            # Check if user requested for conda environment but do not specify the base_env.
            # In such case, set base_env to the default python base environment.
            if conda_env:
                if base_env is None:
                    base_env = __get_default_base_env()
            # Not a conda environment.
            else:
                # Check if base_env provided or not. If provided, check if it is available in
                # the list of base envs. If not available, set base_env to the default python base env.
                if not base_env or \
                        base_env.lower() not in list_base_envs()['base_name'].str.lower().to_list():
                    lang = "python"
                    # Print warning message if base_env provided is not available.
                    if base_env:
                        print(f"Note: The specified base environment '{base_env}' is unavailable. " \
                              "Using the default base environment as specified in the documentation.")
                        lang = base_env.split('_')[0].lower() # Extract language for given base_env.
                    # Set base_env to the default
                    base_env = __get_default_base_env(lang=lang)
        if not desc:
            desc = "This env '{}' is created with base env '{}'.".format(env_name, base_env)
        try:
            data = {"env_name": env_name,
                    "env_description": desc,
                    "base_env_name": base_env
                    }
            response = UtilFuncs._http_request(
                _get_ues_url(conda_env=conda_env), HTTPRequest.POST, headers=_get_auth_token(), json=data)

            # Validate UES response.
            _process_ues_response(api_name="create_env", response=response)

            msg = "User environment '{}' created."

            if conda_env:
                print("Conda environment creation initiated.")
                # Get claim_id.
                claim_id = response.json().get("claim_id", "")

                # Since create_env() for conda environment is internally
                # asynchronous but exposed as synchronous API, keep polling
                # the status of underlying asynchronous operation until
                # it is either successful or errored.
                __poll_claim_id_status(claim_id, "create_env")
            print(msg.format(env_name))

            # Return an instance of class UserEnv.
            return UserEnv(env_name, base_env, desc, conda_env)

        except (TeradataMlException, RuntimeError):
            raise

        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "create_env", str(emsg))
            raise TeradataMlException(error_msg, msg_code)

    else:
        # When template is provided, proceed with recursive way.
        return __create_envs(template)


def _async_run_status_open_af(claim_id):
    """
    DESCRIPTION:
        Internal function to get the status of a claim_id.


    PARAMETERS:
        claim_id:
            Required Argument.
            Specifies the unique identifier of the asynchronous process.
            Types: str

    RETURNS:
        list

    RAISES:
        None

    EXAMPLES:
        __get_claim_id_status('278381bf-e3b3-47ff-9ba5-c3b5d9007363')
    """
    # Get the claim id status.
    resp_data = _get_status(claim_id)

    desc = _async_run_id_info.get(claim_id, {}).get("description", "Unknown")
    get_details = lambda data: {AsyncStatusColumns.ADDITIONAL_DETAILS.value:
                                    data.pop("details", None),
                                AsyncStatusColumns.STATUS.value:
                                    data.pop("stage", None),
                                AsyncStatusColumns.TIMESTAMP.value:
                                    data.pop("timestamp", None),
                                AsyncStatusColumns.RUN_ID.value:
                                    claim_id,
                                AsyncStatusColumns.RUN_DESCRIPTION.value: desc}

    return [get_details(sub_step) for sub_step in resp_data]


def _get_status(claim_id):
    """
    DESCRIPTION:
        Internal function to get the status of a claim_id using
        status API's REST call.


    PARAMETERS:
        claim_id:
            Required Argument.
            Specifies the unique identifier of the asynchronous process.
            Types: str

    RETURNS:
        list

    RAISES:
        None

    EXAMPLES:
        _get_status('278381bf-e3b3-47ff-9ba5-c3b5d9007363')
    """
    # Get the claim id status
    response = UtilFuncs._http_request(_get_ues_url(env_type="fm",
                                                    claim_id=claim_id,
                                                    api_name="status"),
                                       headers=_get_auth_token())
    return _process_ues_response(api_name="status",
                                 response=response).json()


@collect_queryband(queryband="RmEnv")
def remove_env(env_name, **kwargs):
    """
    DESCRIPTION:
        Removes the user's Python or R environment from the Open Analytics Framework.
        The remote user environments are created using create_env() function.
        Note:
            remove_env() should not be triggered on any of the environment if
            install_lib/uninstall_lib/update_lib is running on the corresponding
            environment.

    PARAMETERS:
        env_name:
            Required Argument.
            Specifies the name of the environment to be removed.
            Types: str

        **kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to remove environment synchronously or
                asynchronously. When set to True, environment will be removed
                asynchronously. Otherwise, the environment will be removed synchronously.
                Default Value: False
                Types: bool


    RETURNS:
        True, if the operation is synchronous, str otherwise.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
        # Create a Python 3.7.13 environment with given name and description in the Vantage.
        >>> fraud_detection_env = create_env('Fraud_detection',
        ...                                  'python_3.7.13',
        ...                                  'Fraud detection through time matching')
        User environment 'Fraud_detection' created.
        >>>
        # Create a R 4.1.3 environment with given name and description in the Vantage.
        >>> fraud_detection_env = create_env('Carbon_Credits',
        ...                                  'r_4.1',
        ...                                  'Prediction of carbon credits consumption')
        User environment 'Carbon_Credits' created.
        >>>
        # Example 1: Remove Python environment asynchronously.
        >>> remove_env('Fraud_detection', asynchronous=True)
        Request to remove environment initiated successfully. Check the status using list_user_envs(). If environment is not removed, check the status of asynchronous call using async_run_status('ab34cac6-667a-49d7-bac8-d0456f372f6f') or get_env('Fraud_detection').status('ab34cac6-667a-49d7-bac8-d0456f372f6f')
        'ab34cac6-667a-49d7-bac8-d0456f372f6f'

        >>>
        # Example 2: Remove R environment synchronously.
        >>> remove_env('Carbon_Credits')
        User environment 'Carbon_Credits' removed.
        True
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env_name", env_name, False, (str), True])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    status = __manage_envs(env_name=env_name, api_name="remove_env",
                           **kwargs)

    return status


def __manage_envs(env_name=None, api_name="remove_env", **kwargs):
    """
    Internal function to manage environment deletion synchronously or
    asynchronously.

    PARAMETERS:
        env_name:
            Optional Argument.
            Specifies the name of the environment to be removed.
            Types: str

        api_name:
            Optional Argument.
            Specifies the name of the API.
            Permitted Values: remove_env, remove_all_envs
            Default Value: remove_env
            Types: str

        kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to remove environment synchronously or
                asynchronously.
                Default Value: False
                Types: bool

            is_print:
                Optional Argument.
                Specifies whether to print the message or not.
                Default Value: True
                Types: bool


    RETURNS:
        True, if the operation is synchronous, str otherwise.

    RAISES:
        TeradatamlException.

    EXAMPLES:
        __manage_envs(env_name="test_env", api_name="remove_env", asynchronous=True)
    """
    asynchronous = kwargs.get("asynchronous", False)
    # In case of remove_all_envs(env_type="R") it was printing async msges
    # multiple times. To restrict that internally introduced is_print.
    is_print = kwargs.get("is_print", True)

    __arg_info_matrix = []
    __arg_info_matrix.append(["api_name", api_name, False, (str), True,
                              ["remove_env", "remove_all_envs"]])
    __arg_info_matrix.append(["asynchronous", asynchronous, True, bool])
    __arg_info_matrix.append(["is_print", is_print, True, bool])

    # Argument validation.
    _Validators._validate_missing_required_arguments(__arg_info_matrix)
    _Validators._validate_function_arguments(__arg_info_matrix)

    try:
        # Get the ues url for corresponding API.
        # While deleting environment, endpoint UES URL for deleting
        # normal and conda environment is same, unlike creating
        # normal and conda environment.
        ues_url = _get_ues_url(env_name=env_name, api_name=api_name) if api_name == "remove_env" \
            else _get_ues_url(remove_all_envs=True, api_name=api_name)

        response = UtilFuncs._http_request(ues_url, HTTPRequest.DELETE,
                                           headers=_get_auth_token())

        resp = _process_ues_response(api_name=api_name, response=response)
        claim_id = resp.json().get("claim_id", "")

        # If env removal is asynchronous, then print the msg for user with
        # the claim_id. Else, poll the status using __poll_claim_id_status().
        if asynchronous:
            if is_print:
                msg = "Request to remove environment initiated successfully. " \
                      "Check the status using "
                if api_name == "remove_env":
                    msg = "{2}list_user_envs(). If environment is not removed, " \
                          "check the status of asynchronous call using" \
                          " async_run_status('{1}') or get_env('{0}').status('{1}')". \
                        format(env_name, claim_id, msg)
                else:
                    msg = "{0}async_run_status('{1}')".format(msg, claim_id)
                print(msg)
            # End of 'is_print' condition.

            # Get the description as per the API.
            desc = "Remove '{}' user environment.".format(env_name) \
                if api_name == "remove_env" else "Removing all user environments."

            _async_run_id_info[claim_id] = {"mapped_func": _async_run_status_open_af,
                                            "description": desc}
            return claim_id
        else:
            # Poll the claim_id status.
            __poll_claim_id_status(claim_id, api_name)
            msg = "User environment '{}' removed.".format(env_name) \
                if api_name == "remove_env" else \
                "All user environment(s) removed."
            print(msg)
            return True

    except Exception as exc:
        raise exc


def __poll_claim_id_status(claim_id, api_name="remove_env"):
    """
    Internal function to periodically poll and check the
    status of a claim_id.

    PARAMETERS:
        claim_id:
            Required Argument.
            Specifies the unique identifier of the asynchronous process.
            Types: str

        api_name:
            Optional Argument.
            Specifies the name of the API.
            Permitted Values: remove_env, remove_all_envs, create_env
            Default Value: remove_env
            Types: str

    RETURNS:
        None.

    RAISES:
        TeradataMlException

    EXAMPLES:
        __poll_claim_id_status('cf7245f0-e962-4451-addf-efa7e123998d')
    """
    err_details = None
    while True:
        sleep(2)

        # Poll the claim id to get the status.
        resp_data = _get_status(claim_id)

        # Breaking condition -
        # For create_env and remove_env: Check for the 'Finished' stage in the list of resp.
        # For remove_all_envs: above cond. and No user envs condition should break it .
        for data in resp_data:
            if AsyncOpStatus.FINISHED.value in data["stage"]:
                return
            elif AsyncOpStatus.ERRED.value in data["stage"]:
                err_details = data["details"]
                break
        if err_details:
            break

    raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                   api_name, err_details),
                              MessageCodes.FUNC_EXECUTION_FAILED)


@collect_queryband(queryband="GtEnv")
def get_env(env_name):
    """
    DESCRIPTION:
        Returns an object of class UserEnv which represents an existing remote user environment
        created in the Open Analytics Framework. The user environment can be created using
        create_env() function. This function is useful to get an object of existing user
        environment. The object returned can be used to perform further operations such as
        installing, removing files and libraries.

    PARAMETERS:
        env_name:
            Required Argument.
            Specifies the name of the existing remote user environment.
            Types: str

    RETURNS:
        An object of class UserEnv representing the remote user environment.

    RAISES:
        TeradataMlException.

    EXAMPLES:
        # List available Python environments in the Vantage.
        >>> list_base_envs()
           base_name      language  version
        0  python_3.6.11  Python   3.6.11
        1  python_3.7.9   Python   3.7.9
        2  python_3.8.5   Python   3.8.5

        # Create a Python 3.8.5 environment with given name and description in the Vantage and
        # get an object of class UserEnv.
        #
        >>> test_env = create_env('test_env', 'python_3.8.5', 'Fraud detection through time matching')
        User environment 'test_env' created.

        # In a new terdataml session, user can use get_env() function to get an object pointing to
        # existing user environment created in previous step so that further operations can be
        # performed such as install files/libraries.
        >>> test_env = get_env('test_env')
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env_name", env_name, False, (str), True])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    try:
        # Get environments created by the current logged in user.
        user_envs_df = list_user_envs()

        if (user_envs_df is None or
                (not user_envs_df.empty and env_name not in user_envs_df.env_name.values)):
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "get_env()", "User environment '{}' not found."
                                                                    " Use 'create_env()' function to create"
                                                                    " user environment.".format(env_name))
            raise TeradataMlException(error_msg, msg_code)

        # Get row matching the environment name.
        userenv_row = user_envs_df[user_envs_df['env_name'] == env_name]

        if userenv_row.base_env_name.values[0] == "Unknown":
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "get_env()", "User environment '{}' is corrupted."
                                                                    " Use 'remove_env()' function to remove"
                                                                    " user environment.".format(env_name))
            raise TeradataMlException(error_msg, msg_code)

        # Return an instance of class UserEnv.
        return UserEnv(userenv_row.env_name.values[0],
                       userenv_row.base_env_name.values[0],
                       userenv_row.env_description.values[0],
                       userenv_row.conda.values[0]
                       )
    except (TeradataMlException, RuntimeError) as tdemsg:
        # TeradataMlException and RuntimeError are raised by list_user_envs.
        # list_user_envs should be replaced with get_env in the error 
        # message for final users.
        tdemsg.args = (tdemsg.args[0].replace("list_user_envs", "get_env"),)
        raise tdemsg
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "get_env", emsg)
        raise TeradataMlException(error_msg, msg_code)


@collect_queryband(queryband="RmAllEnvs")
def remove_all_envs(env_type=None, **kwargs):
    """
        DESCRIPTION:
            Removes user environments from the Open Analytics Framework. Function allows user
            to remove only Python user environments or only R user environments or all user
            environments based on the value passed to argument "env_type".
            Note:
                * Do not execute remove_all_envs() if any of the library management functions(install_lib()
                  /uninstall_lib()/update_lib()) are being executed on any environment.

        PARAMETERS:
            env_type:
                Optional Argument.
                Specifies the type of the user environment to be removed.
                Permitted Values:
                    * 'PY' - Remove only Python user environments.
                    * 'R'  - Remove only R user environments.
                    * None - Remove all (Python and R) user environments.
                Default Value: None
                Types: str

            kwargs:
                asynchronous:
                    Optional Argument.
                    Specifies whether to remove environment synchronously or
                    asynchronously.
                    Default Value: False
                    Types: bool


        RETURNS:
            True when
                * Operation is synchronous.
                * Operation is asynchronous with "env_type".
            str otherwise.

        RAISES:
            TeradataMlException, RuntimeError.

        EXAMPLES:
            # Example 1: Remove all the Python and R user environments.
            >>> create_env('Lie_Detection_ML', 'python_3.8.13', 'Detect lie through machine learning.')
            >>> create_env('Customer_Trends', 'r_4.1.3', 'Analyse customer trends.')
            >>> list_user_envs()
                           env_name                           env_description  base_env_name language
            0   Customer_Trends                   Analyse customer trends        r_4.1.3        R
            1  Lie_Detection_ML      Detect lie through machine learning.  python_3.8.13   Python

            >>> remove_all_envs()
            All user environment(s) removed.
            True

            >>> list_user_envs()
            No user environment(s) found.


            # Example 2: Remove all the Python user environments.
            >>> create_env('Lie_Detection_ML', 'python_3.8.13', 'Detect lie through machine learning.')
            >>> create_env('Customer_Trends', 'r_4.1.3', 'Analyse customer trends.')
            >>> list_user_envs()
                          env_name                           env_description  base_env_name language
            0   Customer_Trends                   Analyse customer trends        r_4.1.3        R
            1  Lie_Detection_ML      Detect lie through machine learning.  python_3.8.13   Python

            >>> remove_all_envs(env_type="PY")
            User environment 'Lie_Detection_ML' removed.
            All Python environment(s) removed.
            True
            >>> list_user_envs()
                         env_name                           env_description  base_env_name language
            0   Customer_Trends                   Analyse customer trends        r_4.1.3        R


            # Example 3: Remove all the R user environments.
            >>> create_env('Lie_Detection_ML', 'python_3.8.13', 'Detect lie through machine learning.')
            >>> create_env('Customer_Trends', 'r_4.1.3', 'Analyse customer trends.')
            >>> list_user_envs()
                          env_name                           env_description  base_env_name language
            0   Customer_Trends                   Analyse customer trends        r_4.1.3        R
            1  Lie_Detection_ML      Detect lie through machine learning.  python_3.8.13   Python

            >>> remove_all_envs(env_type="R")
            User environment 'Customer_Trends' removed.
            All R environment(s) removed.
            True
            >>> list_user_envs()
                         env_name                           env_description  base_env_name language
            0  Lie_Detection_ML      Detect lie through machine learning.  python_3.8.13   Python


            # Example 4: Remove all Python and R environments synchronously.
            #            Note: The example first removes all R environments synchronously,
            #                  followed by Python environments.
            >>> env1 = create_env("env1", "python_3.7.13", "Environment 1")
            >>> env2 = create_env("env2", "python_3.7.13", "Environment 2")
            >>> env3 = create_env("env3", "r_4.1", "Environment 3")
            >>> env4 = create_env("env4", "r_4.1", "Environment 4")

            >>> list_user_envs()
              env_name env_description  base_env_name language
            0     env1   Environment 1  python_3.7.13   Python
            1     env2   Environment 2  python_3.7.13   Python
            2     env3   Environment 3          r_4.1        R
            3     env4   Environment 4          r_4.1        R

            # Remove all R environments.
            >>> remove_all_envs(env_type="R")
            User environment 'env3' removed.
            User environment 'env4' removed.
            All R environment(s) removed.
            True
            >>> list_user_envs()
              env_name env_description  base_env_name language
            0     env1   Environment 1  python_3.7.13   Python
            1     env2   Environment 2  python_3.7.13   Python

            # Try to remove R environments again.
            >>> remove_all_envs(env_type="R")
            No R user environment(s) found.
            True

            # Remove all remaining Python environments.
            >>> remove_all_envs()
            All user environment(s) removed.
            True


            # Example 5: Remove all Python and R environments asynchronously.
            #            Note: The example first removes all R environments asynchronously,
            #                  followed by Python environments.
            >>> env1 = create_env("env1", "python_3.7.13", "Environment 1")
            >>> env2 = create_env("env2", "python_3.7.13", "Environment 2")
            >>> env3 = create_env("env3", "r_4.1", "Environment 3")
            >>> env4 = create_env("env4", "r_4.1", "Environment 4")

            >>> list_user_envs()
              env_name env_description  base_env_name language
            0     env1   Environment 1  python_3.7.13   Python
            1     env2   Environment 2  python_3.7.13   Python
            2     env3   Environment 3          r_4.1        R
            3     env4   Environment 4          r_4.1        R

            # Remove all R environments asynchronously.
            >>> remove_all_envs(env_type="R", asynchronous=True)
            Request to remove environment initiated successfully. Check the status using async_run_status(['5c23f956-c89a-4d69-9f1e-6491bac9973f', '6ec9ecc9-9223-4d3f-92a0-9d1abc652aca'])
            True
             >>> list_user_envs()
              env_name env_description  base_env_name language
            0     env1   Environment 1  python_3.7.13   Python
            1     env2   Environment 2  python_3.7.13   Python

            # Remove all remaining Python environments asynchronously.
            >>> remove_all_envs(asynchronous=True)
            Request to remove environment initiated successfully. Check the status using async_run_status('7d86eb99-9ab3-4e0d-b4dd-8b5f1757b9c7')
            '7d86eb99-9ab3-4e0d-b4dd-8b5f1757b9c7'


            # Example 6: Remove all environments asynchronously.
            >>> env1 = create_env("env1", "python_3.7.13", "Environment 1")
            >>> env2 = create_env("env2", "python_3.7.13", "Environment 2")
            >>> env3 = create_env("env3", "r_4.1", "Environment 3")
            >>> env4 = create_env("env4", "r_4.1", "Environment 4")

            >>> list_user_envs()
              env_name env_description  base_env_name language
            0     env1   Environment 1  python_3.7.13   Python
            1     env2   Environment 2  python_3.7.13   Python
            2     env3   Environment 3          r_4.1        R
            3     env4   Environment 4          r_4.1        R

            # Remove all environments asynchronously.
            >>> remove_all_envs(asynchronous=True)
            Request to remove environment initiated successfully. Check the status using async_run_status('22f5d693-38d2-469e-b434-9f7246c7bbbb')
            '22f5d693-38d2-469e-b434-9f7246c7bbbb'
        """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env_type", env_type, True, (str), True, ["PY", "R"]])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)
    if env_type is None:
        status = __manage_envs(api_name="remove_all_envs",
                               **kwargs)
        return status
    else:
        return _remove_all_envs(env_type, **kwargs)


def _remove_all_envs(env_type, **kwargs):
    """
    DESCRIPTION:
        Internal Function removes Python or R user environments.

    PARAMETERS:
            env_type:
                Required Argument.
                Specifies the type of the user environment to be removed.
                Permitted Values:
                    * 'PY' - Remove only Python user environments.
                    * 'R' - Remove only R user environments.
                Types: str

            kwargs:
                asynchronous:
                    Optional Argument.
                    Specifies whether to remove environment synchronously or
                    asynchronously.
                    Default Value: False
                    Types: bool

                is_print:
                    Optional Argument.
                    Specifies whether to print the message or not.
                    Default Value: True
                    Types: bool


    RETURNS:
        True, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
          >>> _remove_all_envs(env_type="PY")
              User environment 'Fraud_detection' removed.
              User environment 'Sales' removed.
              User environment 'Purchase' removed.
              All Python environment(s) removed.
          >>> _remove_all_envs(env_type="R")
              User environment 'Fraud_detection' removed.
              User environment 'Carbon_Credits' removed.
              All R environment(s) removed.
          >>> remove_all_envs(env_type="R", asynchronous=True)
              Request to remove environment initiated successfully. Check status using async_run_status(['82cd24d6-1264-49f5-81e1-76e83e09c303'])
    """
    # Variable for the message on lines 1437 and 1444.
    env_type_message = "Python"
    if env_type.capitalize() == "Py":
        env_type = ["Python", "python"]
    else:
        env_type = ["R", "r"]
        env_type_message = "R"
    asynchronous = kwargs.get("asynchronous", False)

    try:
        # Retrieve all user env data.
        user_envs_df = list_user_envs()
        user_envs_lang_df = user_envs_df[user_envs_df.language.isin(env_type)] if \
            user_envs_df is not None else pd.DataFrame(index=[])

        claim_id_list = []
        if not user_envs_lang_df.empty:
            env_name = user_envs_lang_df["env_name"]
            # Executing remove_env in multiple threads (max_workers set to 10).
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Execute remove_env for each env_name.
                future_remove_env = {
                    executor.submit(remove_env, env,
                                    asynchronous=asynchronous, is_print=False):
                        env for env in env_name}
                # Get the result of all executions.
                failed_envs = {}
                for future in concurrent.futures.as_completed(future_remove_env):
                    env = future_remove_env[future]
                    try:
                        future_result = future.result()
                        # Populate the claim ids of all the envs that
                        # have been removed asynchronously.
                        if asynchronous:
                            claim_id_list.append(future_result)

                    except (TeradataMlException, RuntimeError, Exception) as emsg:
                        # Catching exceptions by remove_env if occurred in any thread.
                        failed_envs[env] = emsg

            # Negative case - Failed to remove env.
            if len(failed_envs) > 0:
                emsg = ""
                for env, tdemsg in failed_envs.items():
                    emsg += "\nUser environment '{0}' failed to remove. Reason: {1}" \
                        .format(env, tdemsg.args[0])
                msg_code = MessageCodes.FUNC_EXECUTION_FAILED
                error_msg = Messages.get_message(msg_code, "remove_all_envs()", emsg)
                raise TeradataMlException(error_msg, msg_code)

            # Positive case - Envs removed without any failure print msg
            # as per sync or async removal.
            if not asynchronous:
                msg = "All {} environment(s) removed.".format(env_type_message)
            else:
                msg = "Request to remove environment initiated successfully. Check " \
                      "the status using " \
                      "async_run_status(['" + "', '".join(claim_id_list) + "'])"
            print(msg)
        elif user_envs_lang_df.empty and user_envs_df is not None:
            print("No {} user environment(s) found.".format(env_type_message))
        return True
    except (TeradataMlException, RuntimeError) as tdemsg:
        # TeradataMlException and RuntimeError are raised by list_user_envs.
        # list_user_envs should be replaced with remove_all_envs in the error 
        # message for final users.
        tdemsg.args = (tdemsg.args[0].replace("list_user_envs", "remove_all_envs"),)
        raise tdemsg
    except Exception as emsg:
        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
        error_msg = Messages.get_message(msg_code, "remove_all_envs", emsg)
        raise TeradataMlException(error_msg, msg_code)


@collect_queryband(queryband="StUsrEnv")
def set_user_env(env):
    """
    DESCRIPTION:
        Function allows to set the default user environment to be used for the Apply()
        and DataFrame.apply() function execution.

    PARAMETERS:
        env:
            Required Argument.
            Specifies the remote user environment name to set as default for the session.
            Types: str OR Object of UserEnv

    RETURNS:
        True, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
        # Create remote user environment.
        >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
        User environment 'testenv' created.

        # Example 1: Set the environment 'testenv' as default environment.
        >>> set_user_env('testenv')
        Default environment is set to 'testenv'.
        >>>

        # Example 2: Create an environment with name 'demo_env' and set it as default environment.
        >>> set_user_env(get_env('test_env'))
        User environment 'testenv' created.
        Default environment is set to 'testenv'.
        >>>
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["env", env, False, (str, UserEnv), True])

    # Validate arguments
    _Validators._validate_function_arguments(__arg_info_matrix)

    # Get the environment name.
    env = get_env(env_name=env) if isinstance(env, str) else env

    configure._default_user_env = env
    print("Default environment is set to '{}'.".format(env.env_name))

    return True


@collect_queryband(queryband="GtUsrEnv")
def get_user_env():
    """
    DESCRIPTION:
        Function to get the default user environment set for the session.

    PARAMETERS:
        None.

    RETURNS:
        An object of UserEnv, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:
        # Create remote user environment.
        >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
        User environment 'testenv' created.
        >>> set_user_env('testenv')
        Default environment is set to 'testenv'.
        >>>

        # Example 1: Get the default environment.
        >>> env = get_user_env()
    """
    if configure._default_user_env is None:
        print("Default environment is not set. Set default environment using set_user_env().")
        return

    return configure._default_user_env


def _validate_jwt_token(base_url, token_data):
    """
    DESCRIPTION:
        Function to validate the authentication token generated using PAT and PEM file.

    PARAMETERS:
        base_url:
            Required Argument.
            Specifies the endpoint URL for a given environment on VantageCloud Lake.
            Types: str

        token_data:
            Required Argument.
            Specifies the JWT token to be authenticated.

    RETURNS:
        Boolan flag representing validation status.
            * True: Indicates that token is valid.
            * None: Indicates that token is not validated.

    RAISES:
        TeradataMlException

    EXAMPLES:
        Example 1: Validate JWT token.
        >>> _validate_jwt_token(base_url, token_data)

    """
    # Extract environment id from base_url.
    try:
        url_parser = urlparse(base_url)
        env_id = url_parser.path.split("accounts/")[1].split("/")[0]
        if not env_id:
            raise
    except Exception:
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                       "set_auth_token",
                                                       "Use valid value for 'base_url'"),
                                  MessageCodes.FUNC_EXECUTION_FAILED)

    valid_token = None
    try:
        response = UtilFuncs._http_request(url="{}/{}/{}/{}".format(_get_ccp_url(base_url),
                                                                    "api", "accounts", env_id),
                                           method_type=HTTPRequest.GET,
                                           headers={"Authorization": "Bearer {}".format(token_data)})
        if 200 <= response.status_code < 300:  # Authorized access.
            valid_token = True
        elif 400 <= response.status_code < 500:  # Unauthorized access.
            valid_token = False
    except:
        pass

    if valid_token is False:
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                       "set_auth_token",
                                                       "Use valid values for input arguments ['base_url',"
                                                       " 'pat_token', 'pem_file']."),
                                  MessageCodes.FUNC_EXECUTION_FAILED)
    return valid_token


@collect_queryband(queryband="StAthTkn")
def set_auth_token(base_url=None, client_id=None, pat_token=None, pem_file=None, **kwargs):
    """
    DESCRIPTION:
        Function to set the authentication token required to access services running on
        Teradata Vantage.
        Notes:
            * User must have a privilege to login with a NULL password to use set_auth_token().
              Refer to GRANT LOGON section in Teradata Documentation for more details.
            * When "auth_mech" is not specified, arguments are used in the following combination
              to derive authentication mechanism.
                * If "base_url" and "client_id" are specified then token generation is done through OAuth.
                * If "base_url", "pat_token", "pem_file" are specified then token generation is done using PAT.
                * If "base_url", "username" and "password" are specified then authentication is done via
                  Basic authentication mechanism using user credentials.
                * If "base_url" and "auth_token" are specified then readily available token is used.
                * If only "base_url" is specified then token generation is done through OAuth.
            * Refresh token works only for OAuth authentication.
            * Use the argument "kid" only when key used during the pem file generation is different
              from pem file name. For example, if you use the key as 'key1' while generating pem file
              and the name of the pem file is `key1(1).pem`, then pass value 'key1' to the argument "kid".

    PARAMETERS:
        base_url:
            Required Argument.
            Specifies the endpoint URL for a given environment on Teradata Vantage system.
            Types: str

        client_id:
            Optional Argument.
            Specifies the id of the application that requests the access token from
            VantageCloud Lake.
            Types: str

        pat_token:
            Required, if PAT authentication is to be used, optional otherwise.
            Specifies the PAT token generated from VantageCloud Lake Console.
            Types: str

        pem_file:
            Required, if PAT authentication is to be used, optional otherwise.
            Specifies the path to private key file which is generated from VantageCloud Lake Console.
            Note:
                Teradata recommends not to change the name of the file generated from VantageCloud Lake
                Console. If the name of the file is changed, then authentication token generated from
                this function will not work.
            Types: str

        **kwargs:
            username:
                Optional Argument.
                Specifies the user for which authentication is to be requested.
                If not specified, then user associated with current connection is used.
                Notes:
                    * Use this option only if name of the database username has lowercase letters.
                    * This option is used only for PAT and not for OAuth.
                Types: str

            expiration_time:
                Optional Argument.
                Specifies the expiration time of the token in seconds. After expiry time, JWT
                token expires and UserEnv methods does not work, user should regenerate the token.
                Note:
                    * This option is used only for PAT and not for OAuth.
                Default Value: 31536000
                Types: int

            auth_token:
                Optional Argument.
                Specifies the authentication token required to access services running
                on Teradata Vantage.
                Notes:
                    * If "auth_token" is set through this function, then this function
                      should always be used only after create_context().
                    * Use this option only if user has got JWT token and wants to set
                      the same instead of generating it again from this function.

                Types: str

            kid:
                Optional Argument.
                Specifies the name of the key which is used while generating 'pem_file'.
                Types: str

            password:
                Optional Argument.
                Specifies the password for database user to be used for Basic authentication.
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
                Optional Argument.
                Specifies the mechanism to be used for generating authentication token.
                Note:
                    * When "auth_mech" is provided, other arguments are used in the following
                      combination as per value of "auth_mech":
                        * OAuth: Token generation is done through OAuth by using client id
                                 which can be sepcified by user in "client_id" argument or
                                 can be derived internally from "base_url".
                        * PAT: Token generation is done using "pat_token" and "pem_file".
                        * BASIC: Authentication is done via Basic authentication mechanism
                                 using user credentials passed in "username" and "password"
                                 arguments.
                        * JWT: Readily available token in "auth_token" argument is used.
                        * KEYCLOAK: Token generation is done using keycloak.
                Permitted Values: "OAuth", "PAT", "BASIC", "JWT", "KEYCLOAK".
                Types: str

            validate_jwt:
                Optional Argument.
                Specifies whether to validate generated JWT token or not.
                Note:
                    * Applicable only when "auth_mech" is "PAT".
                Default value: True
                Types: boolean

            valid_from:
                Optional Argument.
                Specifies epoch seconds representing time from which JWT token will be valid.
                Note:
                    * Applicable only when "auth_mech" is "PAT".
                Default value: 0
                Types: int

    RETURNS:
        True, if the operation is successful.

    RAISES:
        TeradataMlException, RuntimeError.

    EXAMPLES:

        # Example 1: Set the Authentication token using default client_id.
        >>> import getpass
        >>> set_auth_token(base_url=getpass.getpass("ues_url : "))
        Authentication token is generated and set for the session.
        True

        # Example 2: Set the Authentication token by specifying the client_id.
        >>> set_auth_token(base_url=getpass.getpass("base_url : "),
        ...                client_id=getpass.getpass("client_id : "))
        Authentication token is generated and set for the session.
        True

        # Example 3: Set the Authentication token by specifying the "pem_file" and "pat_token"
        #            without specifying "username".
        >>> import getpass
        >>> set_auth_token(base_url=getpass.getpass("base_url : "),
        ...                pat_token=getpass.getpass("pat_token : "),
        ...                pem_file=getpass.getpass("pem_file : "))
        Authentication token is generated, authenticated and set for the session.
        True

        # Example 4: Set the Authentication token by specifying the "pem_file" and "pat_token"
        #            and "username".
        >>> import getpass
        >>> set_auth_token(base_url=getpass.getpass("base_url : "),
        ...                pat_token=getpass.getpass("pat_token : "),
        ...                pem_file=getpass.getpass("pem_file : "),
        ...                username=getpass.getpass("username : "))
        Authentication token is generated, authenticated and set for the session.
        True

        # Example 5: Set the Authentication token by specifying the "pem_file" and "pat_token"
        #            and "kid".
        >>> import getpass
        >>> set_auth_token(base_url=getpass.getpass("base_url : "),
        ...                pat_token=getpass.getpass("pat_token : "),
        ...                pem_file=getpass.getpass("pem_file : ")
        ...                kid="key1")
        Authentication token is generated, authenticated and set for the session.
        True

        # Example 6: Set the authentication token via Basic Authentication mechanism by
        #            specifying the "base_url", "username" and "password".
        >>> import getpass
        >>> set_auth_token(base_url=getpass.getpass("base_url : "),
        ...                username=getpass.getpass("username : "),
        ...                password=getpass.getpass("password : "))
        Authentication token is generated and set for the session.
        True

        # Example 7: Set the authentication token for by specifying "base_url" and
        #            "auth_mech" as "OAuth".
        >>> import getpass
        >>> set_auth_token(base_url=getpass.getpass("base_url : "),
        ...                auth_mech="OAuth")
        Authentication token is generated and set for the session.
        True

        # Example 8: Set the authentication token for by specifying "base_url", "auth_url"
        #            "password" and "rest_client" and generating keycloak token internally.
        >>> import getpass
        >>> set_auth_token(base_url=getpass.getpass("base_url : "),
        ...                auth_url=getpass.getpass("auth_url : "),
        ...                password=getpass.getpass("password : "),
        ...                rest_client=getpass.getpass("rest_client : "))
        Authentication token is generated and set for the session.
        True

    """

    # Deriving global connection using get_connection().
    if get_connection() is None:
        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_CONTEXT_CONNECTION),
                                  MessageCodes.INVALID_CONTEXT_CONNECTION)

    # Remove keys from _InternalBuffer which are interrelated to base_url and authentication token.
    _InternalBuffer.remove_keys(['list_base_envs', 'default_base_env_python', 'default_base_env_r',
                                 'vs_session_id', 'vs_header'])

    # ---------------------------------ARGUMENT VALIDATION------------------------------------------------------
    # STEP 1: Validate arguments for allowed types.
    # ----------------------------------------------------------------------------------------------------------
    __arg_info_matrix = []
    __arg_info_matrix.append(["base_url", base_url, True, (str), True])
    __arg_info_matrix.append(["client_id", client_id, True, (str), True])
    __arg_info_matrix.append(["pat_token", pat_token, True, (str), True])
    __arg_info_matrix.append(["pem_file", pem_file, True, (str), True])

    # Get keyword arguments.
    ues_url = kwargs.get("ues_url", None)
    __arg_info_matrix.append(["ues_url", ues_url, True, (str), True])

    username = kwargs.get("username", _get_user())
    __arg_info_matrix.append(["username", username, True, (str), True])

    password = kwargs.get("password", None)
    __arg_info_matrix.append(["password", password, True, (str), True])

    auth_token = kwargs.get("auth_token")
    __arg_info_matrix.append(["auth_token", auth_token, True, (str), True])

    expiration_time = kwargs.get("expiration_time", 31536000) # 31536000 seconds meaning 365 days.
    __arg_info_matrix.append(["expiration_time", expiration_time, True, (int), True])

    kid = kwargs.get("kid")
    __arg_info_matrix.append(["kid", kid, True, (str), True])

    auth_url = kwargs.get("auth_url", None)
    __arg_info_matrix.append(["auth_url", auth_url, True, (str), True])

    rest_client = kwargs.get("rest_client", "VECTORSTORE")
    __arg_info_matrix.append(["rest_client", rest_client, True, (str), True, [svc.name for svc in TDServices]])

    auth_mech = kwargs.get("auth_mech", None)
    __arg_info_matrix.append(["auth_mech", auth_mech, True, (str), True, [mech.name for mech in AuthMechs]])

    validate_jwt = kwargs.get("validate_jwt", True)
    __arg_info_matrix.append(["validate_jwt", validate_jwt, True, (bool)])

    valid_from = kwargs.get("valid_from", 0) # This sets iat to UTC beginning.
    __arg_info_matrix.append(["valid_from", valid_from, True, int])

    # Validate arguments.
    _Validators._validate_function_arguments(__arg_info_matrix)

    # ---------------------------------BASE_URL PROCESSING------------------------------------------------------
    # STEP 2: Process base_url/ues_url and set applicable config options.
    # ----------------------------------------------------------------------------------------------------------

    # base_url should not end with 'open-analytics' or 'data-insights'
    if base_url:
        if base_url.endswith('open-analytics') or base_url.endswith('data-insights'):
            message = Messages.get_message(MessageCodes.ARG_NONE,
                                           "base_url", "ending with 'data-insights' or 'open-analytics", "")
            raise TeradataMlException(message, MessageCodes.ARG_NONE)

        # Set the vector_store_base_url. This should only be done if base_url is set.
        # In case ues_url is set, vector_store_base_url should not be set.
        # Remove trailing forward slash from base_url if present.
        base_url = base_url[: -1] if base_url.endswith("/") else base_url
        configure._vector_store_base_url = f'{base_url}/data-insights'

    if ues_url:
        # If incorrectly formatted UES service URL is passed, set it to None
        # and let further validation raise error.
        if not (ues_url.endswith('open-analytics') or ues_url.endswith('user-environment-service/api/v1/')):
            ues_url = None

    # If ues_url is provided, then use it as base_url.
    base_url = ues_url if ues_url else base_url

    if not (base_url or ues_url):
        raise TeradataMlException(Messages.get_message(MessageCodes.MISSING_ARGS, ["base_url"]),
                                  MessageCodes.MISSING_ARGS)

    # Set the OpenAF url.
    # If ues_url is present, then use that otherwise generate it from base_url.
    configure.ues_url = ues_url if ues_url else f'{base_url}/open-analytics'

    # Extract the base URL and org id.
    url_parser = urlparse(base_url)
    parsed_base_url = "{}://{}".format(url_parser.scheme, url_parser.netloc)
    org_id = url_parser.netloc.split('.')[0]

    # ---------------------------------TOKEN GENERATION------------------------------------------------------
    # STEP 3: Based on auth_mech, generate authentication token data and store in _InternalBuffer.
    # Note: auth_mech can be user-provided or can be derived from valid combination of supporting parameters.
    # --------------------------------------------------------------------------------------------------------
    if auth_mech:
        auth_mech = auth_mech.lower()
        if auth_mech == 'oauth':
            pat_token = pem_file = password = auth_token = auth_url = None
        elif auth_mech == 'jwt':
            pat_token = pem_file = password = client_id = auth_url = None
        elif auth_mech == 'basic':
            pat_token = pem_file = auth_token = client_id = auth_url = None
        elif auth_mech == 'pat':
            password = client_id = auth_token = auth_url = None
        elif auth_mech == 'keycloak':
            pat_token = pem_file = auth_token = client_id = None

    # Validate arguments for mutual exclusiveness.
    all_groups_none = \
        _Validators._validate_mutually_exclusive_argument_groups({"client_id": client_id},
                                                                 {"auth_token": auth_token},
                                                                 {"pat_token": pat_token,
                                                                  "pem_file": pem_file},
                                                                 {"password": password} if not auth_url else
                                                                 {"password": password, "auth_url": auth_url},
                                                                 return_all_falsy_status=True)

    # Determine authentication mechanism from availability of supportive arguments.
    if auth_mech is None:
        if auth_token:
            auth_mech = 'jwt'
        elif any([pat_token, pem_file]):
            auth_mech = 'pat'
        elif auth_url:
            auth_mech = 'keycloak'
        elif password:
            # Authentication is done via Basic authentication mechanism
            # by passing 'basic' field in header.
            auth_mech = 'basic'
        # When all supporting arguments are None, default mechanism is OAuth.
        elif client_id or all_groups_none:
            auth_mech = 'oauth'

    token_validated = False
    # Generate and use authentication data as per authentication mechanism.
    if auth_mech == 'jwt':
        if not auth_token:
            raise TeradataMlException(Messages.get_message(MessageCodes.MISSING_ARGS, ["auth_token"]),
                                      MessageCodes.MISSING_ARGS)
        # Validate JWT token if base_url points to CCP environment.
        # TODO: Uncomment when mechanism to validate JWT for AI-On-prem system is available.
        # if not ues_url:
        #     token_validated = _validate_jwt_token(base_url, auth_token)

        _InternalBuffer.add(auth_token=_AuthToken(token=auth_token,
                                                  auth_type='bearer'))
    elif auth_mech == 'oauth':
        configure._oauth = True
        client_id = "{}-oaf-device".format(org_id) if client_id is None else client_id
        da_wf = _DAWorkflow(parsed_base_url, client_id)
        token_data = da_wf._get_token_data()

        # Set Open AF parameters.
        configure._oauth_client_id = client_id
        configure._oauth_end_point = da_wf.device_auth_end_point
        configure._auth_token_expiry_time = time() + token_data["expires_in"] - 15

        # Store the jwt token in internal class attribute.
        _InternalBuffer.add(auth_token=_AuthToken(token=token_data["access_token"],
                                                  auth_type='bearer'))
    elif auth_mech == 'pat':
        if any([pat_token, pem_file]):
            _Validators._validate_mutually_inclusive_n_arguments(pat_token=pat_token,
                                                                 pem_file=pem_file)
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.MISSING_ARGS, ["pat_token", "pem_file"]),
                                      MessageCodes.MISSING_ARGS)

        # Check if pem file exists.
        if pem_file is not None:
            _Validators._validate_file_exists(pem_file)

        # Generate JWT token.
        auth_wf = _AuthWorkflow({"base_url": parsed_base_url,
                                 "org_id": org_id,
                                 "pat_token": pat_token,
                                 "pem_file": pem_file,
                                 "username": username,
                                 "expiration_time": expiration_time,
                                 "kid": kid,
                                 "valid_from": valid_from})
        token_data = auth_wf._proxy_jwt()

        if validate_jwt:
            # Validate generated JWT token.
            token_validated = _validate_jwt_token(base_url, token_data)

        # Store the jwt token in internal class attribute.
        _InternalBuffer.add(auth_token=_AuthToken(token=token_data,
                                                  auth_type='bearer'))
    elif auth_mech == 'basic':
        if not password:
            raise TeradataMlException(Messages.get_message(MessageCodes.MISSING_ARGS, ["password"]),
                                      MessageCodes.MISSING_ARGS)
        credentials = f"{username}:{password}"
        # Encode the credentials string using Base64.
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        # Store the header data in internal class attribute.
        _InternalBuffer.add(auth_token=_AuthToken(token=encoded_credentials,
                                                  auth_type='basic'))
    elif auth_mech == 'keycloak':
        _Validators._validate_missing_required_arguments([["password", password, False, (str), True],
                                                          ["auth_url", auth_url, False, (str), True]
                                                          ])
        token_generator = _KeycloakManager(auth_url=auth_url,
                                           client_id=TDServices[rest_client].value)

        # Store manager object in _InternalBuffer in order to generate token after expiry time.
        _InternalBuffer.add(keycloak_manager=token_generator)
        try:
            token_data = token_generator.generate_token(username=username,
                                                        password=password)
        except:
            raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                           "set_auth_token",
                                                           "Failed to generate keycloak token."),
                                      MessageCodes.FUNC_EXECUTION_FAILED)

        _InternalBuffer.add(auth_token=_AuthToken(token=token_data,
                                                  auth_type='keycloak'))

    if token_validated:
        print("Authentication token is generated, authenticated and set for the session.")
    else:
        print("Authentication token is generated and set for the session.")

    return True
