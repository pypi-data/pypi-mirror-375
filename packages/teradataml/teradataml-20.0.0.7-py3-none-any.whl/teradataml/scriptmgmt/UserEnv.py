#!/usr/bin/python
# ####################################################################
#
# Copyright (c) 2023 by Teradata Corporation. All rights reserved.
# TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
#
# Version: 1.0
# Represents remote user environment from Vantage Languages Ecosystem.
# ####################################################################

import functools
import inspect
import json
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, wait
from json.decoder import JSONDecodeError
from urllib.parse import urlparse

import pandas as pd

from teradataml import configure
from teradataml.clients.pkce_client import _DAWorkflow
from teradataml.common.constants import (AsyncOpStatus, CloudProvider,
                                         HTTPRequest, AsyncOpStatusOAFColumns)
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import _get_user
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.utils.validators import _Validators


def _get_ues_url(env_type="users", **kwargs):
    """
    DESCRIPTION:
        Function to get the URL for inititating REST call to UES.

    PARAMETERS:
        env_type:
            Optional Argument.
            Specifies the type of resource in URL.
            Default Value: users
            Types: str

        api_name:
            Optional Argument.
            Specifies the name of the teradataml UES API to mention in the error message.
            Types: str

        kwargs:
            Specifies keyword arguments that can be passed to get the URL.

    RETURNS:
        str

    RAISES:
        TeradataMlException, RuntimeError

    EXAMPLES:
            >>> _get_ues_url("base_environments") # URL for listing base environments.
            >>> _get_ues_url() # URL to create/remove/list the user environment(s).
            >>> _get_ues_url(remove_all_envs=True) # URL requires for remove_all_envs().
            >>> _get_ues_url(logs=True, query_id='307161028465226056') # URL requires for query-logs.
            >>> _get_ues_url(env_name="alice_env") # URL to delete/list files in an environment.
            >>> _get_ues_url(env_name="alice_env", files=True, api_name="install_file") # URL to install/replace file in environment.
            >>> _get_ues_url(env_name="alice_env", files=True, file_name="a.py") # URL to remove a file in environment.
            >>> _get_ues_url(env_name="alice_env", libs=True, api_name="libs") # URL to install/uninstall/update/list library in environment.
            >>> _get_ues_url(env_type="fm", claim_id="123-456", api_name=status) # URL for checking the task status.
            >>> _get_ues_url(env_type="fm", fm_type="export", claim_id="123-456") # URL for exporting a file.
            >>> _get_ues_url(env_type="fm", fm_type="import", api_name="install_file") # URL for generating end point to upload file.
            >>> _get_ues_url(env_name=self.env_name, files=True, is_property=True, api_name="files") # URL for listing down the files.
    """
    api_name = kwargs.pop("api_name", inspect.stack()[1].function)
    conda_env = kwargs.get("conda_env", False)

    # Raise error if user is not connected to Vantage.
    if _get_user() is None:
        error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                         api_name,
                                         "Create context before using {}.".format(api_name))
        raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)

    if configure.ues_url is None:
        error_msg = Messages.get_message(MessageCodes.SET_REQUIRED_PARAMS,
                                         'Authentication Token', api_name, 'set_auth_token')
        raise RuntimeError(error_msg)

    ues_url = "{}/{}".format(configure.ues_url, env_type)

    if kwargs.get("remove_all_envs", False):
        return "{0}/{1}".format(ues_url, _get_user())
    if kwargs.get("logs", False):
        return "{0}/{1}/{2}/{3}".format(ues_url, _get_user(), 'query-logs', kwargs['query_id'])

    if env_type not in ("users", "fm"):
        return ues_url

    elif env_type == "fm":
        fm_type = kwargs.get("fm_type")
        if fm_type == "import":
            return "{}/import".format(ues_url)
        elif fm_type == "export":
            return "{}/export/{}".format(ues_url, kwargs["claim_id"])
        else:
            return "{}/users/{}/{}/tasks/{}".format(configure.ues_url,
                                                    _get_user(),
                                                    env_type, kwargs["claim_id"])

    # We will reach here to process "users" env type.
    env_type = "environments"
    if conda_env:
        env_type = "conda-environments"

    ues_url = "{0}/{1}/{2}".format(ues_url, _get_user(), env_type)
    env_name, files, libs = kwargs.get("env_name"), kwargs.get("files", False), kwargs.get("libs", False)
    models = kwargs.get("models", False)

    if env_name is not None:
        ues_url = "{0}/{1}".format(ues_url, env_name)

    if files:
        ues_url = "{0}/{1}".format(ues_url, "files")
        file_name = kwargs.get("file_name")
        if file_name is not None:
            ues_url = "{0}/{1}".format(ues_url, file_name)
    elif libs:
        ues_url = "{0}/{1}".format(ues_url, "libraries")
    elif models:
        ues_url = "{0}/{1}".format(ues_url, "models")
    return ues_url


def _process_ues_response(api_name, response, success_status_code=None):
    """
    DESCRIPTION:
        Function to process and validate the UES Response.

    PARAMETERS:
        api_name:
            Required Argument.
            Specifies the name of the teradataml UES API.
            Types: str

        response:
            Required Argument.
            Specifies the response recieved from UES.
            Types: requests.Response

        success_status_code:
            Optional Argument.
            Specifies the expected success status code for the corresponding UES API.
            Default Value: None
            Types: int

    RETURNS:
        Response object.

    RAISES:
        TeradataMlException.

    EXAMPLES:
            >>> _process_ues_response("list_base_envs", resp)
    """
    try:
        # Success status code ranges between 200-300.
        if (success_status_code is None and 200 <= response.status_code < 300) or \
                (success_status_code == response.status_code):
            return response

        # teradataml API got an error response. Error response is expected as follows -
        # {
        #     "status": 404,
        #     "req_id": "1122.3.1",
        #     "error_code": "201",
        #     "error_description": "Environment not found."
        # }
        # Extract the fields and raise error accordingly.

        add_paranthesis = lambda msg: "({})".format(msg) if msg else msg

        data = response.json()
        request_id = add_paranthesis(data.get("req_id", ""))
        error_code = add_paranthesis(data.get("error_code", ""))
        error_description = "{}{} {}".format(request_id, error_code, data.get("error_description",
                                                                              response.text))

        exception_message = "Request Failed - {}".format(error_description)

        error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                         api_name,
                                         exception_message)
        raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)

    # teradataml API may not get a Json API response in some cases.
    # So, raise an error with the response received as it is.
    except JSONDecodeError:
        error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                         api_name,
                                         response.text)
        raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)


def _get_auth_token():
    """
    DESCRIPTION:
        Internal function to get authentication token required to access services
        running on Teradata Vantage.

    PARAMETERS:
        None

    RETURNS:
        dict

    RAISES:
        TeradataMlException

    EXAMPLES:
        >>>_get_auth_token()
    """
    # Check the current time. If token is expiring, get another one from refresh token.
    if configure._oauth:
        if configure._auth_token_expiry_time and time.time() > configure._auth_token_expiry_time:
            # Extract the base URL from "ues_url".
            ues_url = configure.ues_url
            client_id = configure._oauth_client_id

            url_parser = urlparse(ues_url)
            base_url = "{}://{}".format(url_parser.scheme, url_parser.netloc)

            # Get the JWT Token details.
            da_wf = _DAWorkflow(base_url, client_id)
            token_data = da_wf._get_token_data()

            # Replace the options with new values.
            configure._auth_token_expiry_time = time.time() + token_data["expires_in"] - 15

            # Store the jwt token in internal class attribute.
            _InternalBuffer.add(auth_token=_AuthToken(token=token_data["access_token"],
                                                      auth_type='bearer'))

    auth_token = _InternalBuffer.get("auth_token")
    if auth_token:
        return auth_token.get_header()


def _get_ccp_url(base_url):
    """
    DESCRIPTION:
        Internal function to get ccp URL from base_url.

    PARAMETERS:
        base_url:
            Required Argument.
            Specifies the base url.
            Types: str

    RETURNS:
        str

    RAISES:
        None

    EXAMPLES:
        >>> base_url = 'https://<part_1>.<part_2>.<part_3>.com/<part_4>/<part_5>/<part_6>'
        >>> _get_ccp_url(base_url)
        'https://<part_1>.<part_2>.<part_3>.com'
    """
    parsed_url = urlparse(base_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


class UserEnv:

    def __init__(self, env_name, base_env, desc=None, conda_env=False):
        """
        DESCRIPTION:
            Represents remote user environment from Vantage Languages Ecosystem.
            The object of the class can be created either by using create_env() function which will
            create a new remote user environment and returns an object of UserEnv class or
            by using get_env() function which will return an object representing the existing remote user environment.

        PARAMETERS:
            env_name:
                Required Argument.
                Specifies the name of the remote user environment.
                Types: str

            base_env:
                Required Argument.
                Specifies base environment interpreter which is used to create remote user environment.
                Types: str

            desc:
                Optional Argument.
                Specifies description associated with the remote user environment.
                Types: str
            
            conda_env:
                Optional Argument.
                Specifies whether the environment to be created is a conda environment or not.
                When set to True, conda environment is created. Otherwise, non conda environment is created.
                Default value: False
                Types: bool

        RETURNS:
            Instance of the class UserEnv.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create a new environment and get instance of UserEnv class.
            env1 = create_env('testenv', 'python_3.7.9', 'Test environment')

            # Get an object for existing user environment.
            env2 = get_env('testenv')
        """

        # Make sure the initialization happens only using either create_env() or get_env().
        if inspect.stack()[1][3] not in ['create_env', 'get_env']:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.USE_FUNCTION_TO_INSTANTIATE).format("A teradataml UserEnv object",
                                                                 "create_env() and get_env() functions from teradataml.scriptmgmt.lls_utils"),
                                      MessageCodes.USE_FUNCTION_TO_INSTANTIATE)

        self.env_name = env_name
        self.base_env = base_env
        self.desc = desc

        self.conda_env = conda_env
        # Initialize variable for R environment.
        self._r_env = True if self.base_env.lower().startswith("r_") else False

        # Initialize variables to store files, libraries and models from
        # the remote user environment.
        self.__files = None
        self.__libs = None
        self.__models = None

        # This variable will be used to detect if files from the remote user environment are changed by
        # install_file or remove_file functions.
        self.__files_changed = None

        # This variable will be used to detect if libraries from the remote user environment are changed by
        # install_lib, remove_lib or update_lib functions in teradataml.
        # Updates from only current session are recorded by this variable.
        self.__libs_changed = None

        # This variable will be used to detect if models from the remote
        # user environment are changed by install_model or remove_model functions.
        self.__models_changed = None

        # This variable will be set to False when remove() method is called to indicate that.
        self.__exists = True

        # Create argument information matrix to do parameter checking
        self.__arg_info_matrix = []
        self.__arg_info_matrix.append(["env_name", self.env_name, False, (str), True])
        self.__arg_info_matrix.append(["base_env", self.base_env, False, (str), True])
        self.__arg_info_matrix.append(["desc", self.desc, True, (str), False])

        # Argument validation.
        _Validators._validate_function_arguments(self.__arg_info_matrix)

        # Map to store the claim id and corresponding file.
        self.__claim_ids = {}

        # Define the order of columns in output DataFrame.
        self.__status_columns = ['Claim Id', 'File/Libs/Model', 'Method Name', 'Stage', 'Timestamp', 'Additional Details']

    def __repr__(self):
        """
        Returns the string representation for class instance.
        """
        repr_string = "\n================================================\n"
        repr_string = repr_string + "Environment Name: {}\n".format(self.env_name)
        repr_string = repr_string + "Base Environment: {}\n".format(self.base_env)
        repr_string = repr_string + "Description: {}\n".format(self.desc)

        # Fetch latest state of remote env.
        self._set_files()
        self._set_libs()
        self._set_models()

        if self.__files is not None and len(self.__files) > 0:
            repr_string_files = "############ Files installed in User Environment ############"
            repr_string = "{}\n{}\n\n{}\n".format(repr_string, repr_string_files, self.__files)

        if self.__libs is not None and len(self.__libs) > 0:
            repr_string_libs = "############ Libraries installed in User Environment ############"
            repr_string = "{}\n{}\n\n{}\n".format(repr_string, repr_string_libs, self.__libs)

        if self.__models is not None and len(self.__models) > 0:
            repr_string_models = "############ Models installed in User Environment ############"
            repr_string = "{}\n{}\n\n{}\n".format(repr_string, repr_string_models, self.__models)

        repr_string = repr_string + "\n================================================\n"
        return repr_string

    @collect_queryband(queryband="InstlFl")
    def install_file(self, file_path, replace=False, **kwargs):
        """
        DESCRIPTION:
            Function installs or replaces a file from client machine to the remote user environment created in
            Vantage Languages Ecosystem.
            * If the size of the file is more than 10 MB, the function installs the file synchronously
              and returns the status of installation when 'asynchronous' is set to False. Otherwise, the
              function installs the file asynchronously and returns claim-id to check the installation status
              using status().
            * If the size of the file is less than or equal to 10 MB, the function installs the
              file synchronously and returns the status of installation.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to be installed in the
                remote user environment.
                Types: str

            replace:
                Optional Argument.
                Specifies if the file should be forcefully replaced in remote user environment.
                * When set to True,
                   * If the file already exists in remote user environment, it will be replaced with the file
                     specified by argument "file_path".
                   * If the file does not already exist in remote user environment, then the specified file will
                     be installed.
                * Argument is ignored when file size <= 10MB.
                Default Value: False
                Types: bool

        **kwargs:
            Specifies the keyword arguments.
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Default Value: False
                    Types: bool

            asynchronous:
                Optional Argument.
                Specifies whether to install the file in remote user environment
                synchronously or asynchronously. When set to True, file is installed
                asynchronously. Otherwise, file is installed synchronously.
                Note:
                    Argument is ignored when file size <= 10MB.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the file. If the file is
                not installed with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            True, if the file size is less than or equal to 10 MB and operation is successful.
            str(claim-id), if the file size is greater than 10 MB.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Create conda environment.
            >>> testenv_conda = create_env('testenv_conda', 'python_3.8', 'Test conda environment', conda_env=True)
            Conda environment creation initiated.
            User environment 'testenv_conda' created.

            # Example 1: Install the file mapper.py in the 'testenv' environment.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path)
            File 'mapper.py' installed successfully in the remote user environment 'testenv'.

            # Example 2: Replace the file mapper.py.
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path, replace=True)
            File 'mapper.py' replaced successfully in the remote user environment 'testenv'.

            # Example 3: Install the file 'large_file' asynchronously with 'large_file' found in
                         temp folder and check the status of installation.
            # Note:
            #     Running this example creates a file 'large_file' with size
            #     approximately 11MB in the temp folder.
            >>> import tempfile, os
            >>> def create_large_file():
            ...     file_name = os.path.join(tempfile.gettempdir(),"large_file")
            ...     with open(file_name, 'xb') as fp:
            ...         fp.seek((1024 * 1024 * 11) - 1)
            ...         fp.write(b'\0')
            ...
            >>> create_large_file()
            >>> claim_id = env.install_file(file_path = os.path.join(tempfile.gettempdir(),"large_file"), asynchronous=True)
            File installation is initiated. Check the status using status() with the claim id 76588d13-6e20-4892-9686-37768adcfadb.
            >>> env.status(claim_id)
                                            Claim Id              File/Libs    Method Name               Stage             Timestamp Additional Details
            0   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file       File Uploaded  2022-07-13T10:34:02Z               None
            >>> env.status(claim_id, stack=True)
                                            Claim Id              File/Libs    Method Name               Stage             Timestamp Additional Details
            0   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file  Endpoint Generated  2022-07-13T10:34:00Z               None
            1   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file       File Uploaded  2022-07-13T10:34:02Z               None
            2   76588d13-6e20-4892-9686-37768adcfadb             large_file   install_file      File Installed  2022-07-13T10:34:08Z               None

            # Example 4: Install the file 'large_file' synchronously with 'large_file' found in
                         temp folder and check the status of installation.
            # Note:
            #     Running this example creates a file 'large_file' with size
            #     approximately 11MB in the temp folder.
            >>> import tempfile, os
            >>> def create_large_file():
            ...     file_name = os.path.join(tempfile.gettempdir(), "large_file")
            ...     with open(file_name, 'xb') as fp:
            ...         fp.seek((1024 * 1024 * 11) - 1)
            ...         fp.write(b'\0')
            ...
            >>> create_large_file()
            >>> result = env.install_file(file_path = os.path.join(tempfile.gettempdir(),"large_file"))

            >>> result
                                            Claim Id              File/Libs    Method Name               Stage             Timestamp Additional Details
            0   87588d13-5f20-3461-9686-46668adcfadb             large_file   install_file  Endpoint Generated  2022-07-13T10:34:00Z               None
            1   87588d13-5f20-3461-9686-46668adcfadb             large_file   install_file       File Uploaded  2022-07-13T10:34:02Z               None
            2   87588d13-5f20-3461-9686-46668adcfadb             large_file   install_file      File Installed  2022-07-13T10:34:08Z               None

            >>> os.remove(os.path.join(tempfile.gettempdir(),"large_file")) # Remove the file created using function 'create_large_file'.

            # Example 5: Install the file mapper.py in the 'testenv_conda' environment.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> testenv_conda.install_file(file_path = file_path)
            File 'mapper.py' installed successfully in the remote user environment 'testenv_conda'.

            # Remove the environment.
            >>> remove_env('testenv')
            User environment 'testenv' removed.
            >>> remove_env("testenv_conda")
            User environment 'testenv_conda' removed.
        """
        # Install/Replace file on Vantage
        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout")
        suppress_output = kwargs.get("suppress_output", False)
        is_model = kwargs.get("is_model", False)
        is_llm = kwargs.pop("is_llm", False)
        api_name = "install_file"
        path_arg_name = "file_path"
        if is_model:
            api_name = "install_model"
            path_arg_name = "model_path"

        __arg_info_matrix = []
        __arg_info_matrix.append([path_arg_name, file_path, False, (str), True])
        __arg_info_matrix.append(["replace", replace, True, (bool)])
        __arg_info_matrix.append(["asynchronous", asynchronous, True, (bool)])
        __arg_info_matrix.append(["timeout", timeout, True, (int, float)])
        __arg_info_matrix.append(["suppress_output", suppress_output, True, (bool)])

        # Argument validation.
        _Validators._validate_function_arguments(__arg_info_matrix)

        # For LLM, only zip file is allowed.
        if is_model and is_llm:
            _Validators._validate_file_extension(file_path, ['zip'])

        # Check if file exists or not.
        _Validators._validate_file_exists(file_path)
        # Check if file is empty or not.
        _Validators._check_empty_file(file_path)

        try:
            # If file size is more than 10 MB, upload the file to cloud and export it to UES.
            if is_model or UtilFuncs._get_file_size(file_path) > configure._ues_max_file_upload_size:
                res = self.__install_file_from_cloud(file_path, asynchronous, timeout,
                                                     suppress_output, is_model)
            else:
                res = self.__install_file_from_local(file_path, replace, suppress_output)

            # Update the flags which are used by refresh API and
            # APIs for listing entities like files and models.
            if is_model:
                self.__models_changed = True
            else:
                self.__files_changed = True
            return res

        except (TeradataMlException, RuntimeError):
            raise

        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, api_name, str(emsg))
            raise TeradataMlException(error_msg, msg_code)

    def __install_file_from_local(self, file_path, replace, suppress_output=False):
        """
        DESCRIPTION:
            Internal function to install or replace a file from client machine to the remote
            user environment created in Vantage Languages Ecosystem.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to be installed in the
                remote user environment.
                Types: str

            replace:
                Required Argument.
                Specifies if the file should be forcefully replaced in remote user environment.
                When set to True,
                    * If the file already exists in remote user environment, it will be replaced with the file
                      specified by argument "file_path".
                    * If the file does not already exist in remote user environment, then the specified file will
                      be installed.
                Types: bool

            suppress_output:
                Optional Argument.
                Specifies whether to print the output message or not.
                When set to True, then the output message is not printed.
                Default Value: False
                Types: bool

        RETURNS:
            True, if the operation is successful.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.
            >>> env.__install_file_from_local("abc.py")
            File 'abc.py' is installed successfully in 'testenv' environment.
        """
        file_name = os.path.basename(file_path)

        # Prepare the payload.
        files = {
            'env-file': (file_name, UtilFuncs._get_file_contents(file_path, read_in_binary_mode=True))
        }

        http_method = HTTPRequest.POST
        success_msg = "installed"
        params = {"env_name": self.env_name, "files": True, "api_name": "install_file"}

        if replace:
            http_method = HTTPRequest.PUT
            success_msg = "replaced"
            params["file_name"] = file_name

        resource_url = _get_ues_url(**params)
        # UES accepts multiform data. Specifying the 'files' attribute makes 'requests'
        # module to send it as multiform data.
        resp = UtilFuncs._http_request(resource_url, http_method, headers=_get_auth_token(), files=files)

        # Process the response.
        _process_ues_response(api_name="install_file", response=resp)

        if not suppress_output:
            print("File '{}' {} successfully in the remote user environment '{}'.".format(
                  file_name, success_msg, self.env_name))

        return True

    @staticmethod
    def __upload_file_to_cloud(file_path, is_model=False, api_name="install_file"):
        """
        DESCRIPTION:
            Internal function to upload a file to the cloud environment.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to be uploaded
                to the cloud.
                Types: str

        RETURNS:
            str, if the operation is successful.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.
            >>> env.__upload_file_to_cloud("abc.txt")
        """
        # Prepare the payload for UES to get the URL and claim-id.
        payload = {"user": _get_user(), "file": os.path.basename(file_path)}

        response = UtilFuncs._http_request(_get_ues_url(env_type="fm", fm_type="import", api_name=api_name),
                                           HTTPRequest.POST,
                                           json=payload,
                                           headers=_get_auth_token())
        response_header = response.headers
        data = _process_ues_response(api_name, response).json()

        # Get the URL to upload file to cloud and the claim-id from response.
        cloud_storage_url, claim_id = data["url"], data["claim_id"]
        # Get the Cloud Provider from response header.
        cloud_provider = response_header["X-Oaf-Cloud-Provider"]

        headers = None
        if cloud_provider == CloudProvider.AZURE.value:
            headers = {"Content-Type": "application/octet-stream",
                       "x-ms-date": response_header["Date"],
                       "x-ms-version": CloudProvider.X_MS_VERSION.value,
                       "x-ms-blob-type": CloudProvider.X_MS_BLOB_TYPE.value}

        # Initiate file upload to cloud.
        with open(file_path, 'rb') as fp:
            response = UtilFuncs._http_request(cloud_storage_url,
                                               HTTPRequest.PUT,
                                               data=fp,
                                               headers=headers)

        # Since the API is not for UES, it is better to validate and raise error separately.
        if not (200 <= response.status_code < 300):
            raise Exception("{} upload failed with status code - {}"
                            .format('Model' if is_model else 'File',
                                    response.status_code))

        return claim_id

    def __install_file_from_cloud(self, file_path, asynchronous=False, timeout=None,
                                  suppress_output=False, is_model=False):
        """
        DESCRIPTION:
            Internal Function to export file from cloud environment to the remote user
            environment created in Vantage Languages Ecosystem.

        PARAMETERS:
            file_path:
                Required Argument.
                Specifies absolute or relative path of the file (including file name) to
                be installed in the remote user environment.
                Types: str

            asynchronous:
                Optional Argument.
                Specifies whether to install the file in remote user environment
                synchronously or asynchronously. When set to True, file is installed
                asynchronously. Otherwise, file is installed synchronously.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the file. If the file is
                not installed with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

            suppress_output:
                Optional Argument.
                Specifies whether to print the output message or not.
                When set to True, then the output message is not printed.
                Default Value: False
                Types: bool

        RETURNS:
            str, if the operation is successful.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.
            >>> env.__install_file_from_cloud("abc.py")
            File installation is initiated. Check the status using 'status' API with the claim id abc-xyz.
            abc-xyz
        """
        # Decide API type.
        api_name = "install_file"
        if is_model:
            api_name = "install_model"

        # Upload file to cloud.
        claim_id = self.__upload_file_to_cloud(file_path, is_model, api_name)

        # Initiate file export from cloud to UES file system. Note that, the corresponding call to
        # UES is an asynchronous call.
        data = {"user": _get_user(),
                "environment": self.env_name,
                "claim_id": claim_id
                }
        # Add additional payload field to specify that
        # model is getting installed.
        if is_model:
            data['model'] = True

        url = _get_ues_url(env_type="fm", fm_type="export", claim_id=claim_id,
                           api_name=api_name)
        response = UtilFuncs._http_request(url, HTTPRequest.POST, json=data,
                                           headers=_get_auth_token())

        # Validate the response.
        _process_ues_response(api_name, response)

        # Store the claim id locally to display the file/library name in status API.
        self.__claim_ids[claim_id] = {"action": api_name, "value": file_path}

        # In case of synchronous mode, keep polling the status
        # of underlying asynchronous operation until it is either
        # successful or errored or timed out.
        if not asynchronous:
            return self.__get_claim_status(claim_id, timeout, api_name)

        if not suppress_output:
            # Print a message to user console.
            print("{} installation is initiated. Check the status"
                  " using status() with the claim id {}.".
                  format('Model' if is_model else 'File', claim_id))

        return claim_id

    @collect_queryband(queryband="RmFl")
    def remove_file(self, file_name, **kwargs):
        """
        DESCRIPTION:
            Function removes the specified file from the remote user environment.

        PARAMETERS:
            file_name:
                Required Argument.
                Specifies the file name to be removed. If the file has an extension, specify the filename with extension.
                Types: str

        **kwargs:
            Specifies the keyword arguments.
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Types: bool

        RETURNS:
            True, if the operation is successful.

        RAISES:
            TeradataMlException, RuntimeError

        EXAMPLES:
            # Create a Python 3.7.3 environment with given name and description in Vantage.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment 'testenv' created.

            # Install the file "mapper.py" using the default text mode in the remote user environment.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path)
            File 'mapper.py' installed successfully in the remote user environment 'testenv'.

            # Example 1: Remove file from remote user environment.
            >>> env.remove_file('mapper.py')
            File 'mapper.py' removed successfully from the remote user environment 'testenv'.

            # Remove the environment.
            >>> remove_env('testenv')
            User environment 'testenv' removed.
        """

        api_name = "remove_file"
        file_model_arg_name = "file_name"

        is_model = kwargs.get("is_model", False)
        if is_model:
            api_name = "uninstall_model"
            file_model_arg_name = "model_name"

        __arg_info_matrix = []
        __arg_info_matrix.append([file_model_arg_name, file_name, False, (str), True])
        __arg_info_matrix.append(["suppress_output", kwargs.get("suppress_output", False), True, (bool)])

        # Argument validation.
        _Validators._validate_missing_required_arguments(__arg_info_matrix)
        _Validators._validate_function_arguments(__arg_info_matrix)

        try:
            response = UtilFuncs._http_request(_get_ues_url(env_name=self.env_name, files=True, file_name=file_name),
                                               HTTPRequest.DELETE,
                                               headers=_get_auth_token())

            _process_ues_response(api_name=api_name, response=response)

            if not kwargs.get("suppress_output", False):
                msg = "File '{0}' removed"
                if is_model:
                    msg = "Model '{0}' uninstalled"
                print("{0} successfully from the remote user environment '{1}'.".
                      format(msg, self.env_name).format(file_name))

            # Files/Models are changed, change the flag.
            if is_model:
                self.__models_changed = True
            else:
                self.__files_changed = True
            return True

        except (TeradataMlException, RuntimeError):
            raise
        except Exception as err:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, api_name, err)
            raise TeradataMlException(error_msg, msg_code)

    @property
    @collect_queryband(queryband="EnvFls")
    def files(self):
        """
        DESCRIPTION:
            A class property that returns list of files installed in remote user environment.

        PARAMETERS:
            None

        RETURNS:
            Pandas DataFrame containing files and it's details.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            >>> env.install_file(file_path = 'data/scripts/mapper.py')
            File mapper.py installed successfully in the remote user environment testenv.

            # List files installed in the user environment.
            >>> env.files
                     File  Size                Timestamp
            0   mapper.py   233     2020-08-06T21:59:22Z
        """
        # Fetch the list of files from remote user environment only when they are not already fetched in this object
        # or files are changed either by install or remove functions.
        if self.__files is None or self.__files_changed:
            self._set_files()

        if len(self.__files) == 0:
            print("No files found in remote user environment {}.".format(self.env_name))
        else:
            return self.__files

    def _set_files(self):
        """
        DESCRIPTION:
            Function fetches the list of files installed in a remote user environment using
            the REST call to User Environment Service.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> self._set_files()
        """

        try:
            response = UtilFuncs._http_request(_get_ues_url(env_name=self.env_name, files=True, api_name="files"),
                                               headers=_get_auth_token())
            data = _process_ues_response(api_name="files", response=response).json()

            # Create a lamda function to extract only required columns from the data.
            get_details = lambda data: {"File": data.pop("name", None),
                                        "Size": data.pop("size", None),
                                        "Timestamp": data.pop("last_updated_dttm", None)
                                        }

            if len(data) > 0:
                self.__files = pd.DataFrame.from_records([get_details(file) for file in data
                                                          if file['is_model'] == False])
            else:
                self.__files = pd.DataFrame(columns=["File", "Size", "Timestamp"])

            # Latest files are fetched; reset the flag.
            self.__files_changed = False

        except (TeradataMlException, RuntimeError):
            raise

        except Exception as err:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "files", err)
            raise TeradataMlException(error_msg, msg_code)

    def _set_libs(self):
        """
        DESCRIPTION:
            Function lists the installed libraries in the remote user environment using
            the REST call to User Environment Service and sets the '__libs' data member.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            self._set_libs()
        """
        try:
            response = UtilFuncs._http_request(_get_ues_url(env_name=self.env_name, libs=True, api_name="libs"),
                                               headers=_get_auth_token())
            data = _process_ues_response(api_name="libs", response=response).json()

            if len(data) > 0:
                # Return result as Pandas dataframe.
                df = pd.DataFrame.from_records(data)
                self.__libs = df

            # Latest libraries are fetched; reset the flag.
            self.__libs_changed = False

        except (TeradataMlException, RuntimeError):
            raise
        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "libs", emsg)
            raise TeradataMlException(error_msg, msg_code)

    @property
    @collect_queryband(queryband="EnvLbs")
    def libs(self):
        """
        DESCRIPTION:
            A class property that returns list of libraries installed in the remote user environment.

        PARAMETERS:
            None

        RETURNS:
            Pandas DataFrame containing libraries and their versions.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Example 1: libs property for Python environment.
            # Create a remote Python user environment.
            >>> env = create_env('test_env', 'python_3.7.9', 'Test environment')
            User environment test_env created.

            # View existing libraries installed.
            >>> env.libs
                     name version
            0         pip  20.1.1
            1  setuptools  47.1.0

            # Install additional Python libraries.
            >>> env.install_lib(['numpy','nltk>=3.3'])
            Request to install libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '1e23d244-3c88-401f-a432-277d72dc6835'.
            '1e23d244-3c88-401f-a432-277d72dc6835'

            # List libraries installed.
            >>> env.libs
                     name version
            0        nltk   3.4.5
            1       numpy  1.21.6
            2         pip  20.1.1
            3  setuptools  47.1.0
            4         six  1.16.0

            # Example 2: libs property for R environment.
            # Create a remote R user environment.
            >>> r_env = create_env('test_r_env', 'r_4.1', 'Test R environment')
            User environment 'test_r_env' created.

            # List installed libraries in environment.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            4         boot   1.3-28
            ..         ...      ...
            26    survival   3.2-13
            27       tcltk    4.1.3
            28       tools    4.1.3
            29       utils    4.1.3

            # Install additional R libraries.
            >>> r_env.install_lib(['dplyr','testthat==3.0.4'])
                                            Claim Id	            File/Libs	Method Name	  Stage	             Timestamp	Additional Details
            0	3823217b-89ee-423c-9ed1-f72a6b6d0511	dplyr, testthat=3.0.4	install_lib	 Started  2023-08-31T07:14:57Z
            1	3823217b-89ee-423c-9ed1-f72a6b6d0511	dplyr, testthat=3.0.4	install_lib	Finished  2023-08-31T07:20:35Z

            # List installed libraries in environment.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            9        dplyr    1.1.2
            ..         ...      ...
            58    testthat    3.0.4
            ..         ...      ...
            61       vctrs    0.6.3
            62       waldo    0.5.1
            63       withr    2.5.0
            [64 rows x 2 columns]

        """
        # Fetch the list of libraries from remote user environment only when they are not
        # already fetched in this object or libraries are changed either by
        # install_lib/uninstall_lib/update_lib functions.
        if self.__libs is None or self.__libs_changed:
            self._set_libs()

        return self.__libs

    def _set_models(self):
        """
        DESCRIPTION:
            Function fetches the list of models installed in a remote user environment using
            the REST call to User Environment Service.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> self._set_models()
        """
        try:
            response = UtilFuncs._http_request(_get_ues_url(env_name=self.env_name, files=True, api_name="models"),
                                               headers=_get_auth_token())
            data = _process_ues_response(api_name="models", response=response).json()

            # Create a lamda function to extract only required columns from the data.
            get_details = lambda data: {"Model": data.pop("name", None),
                                        "Size": data.pop("size", None),
                                        "Timestamp": data.pop("last_updated_dttm", None)
                                        }

            if len(data) > 0:
                self.__models = pd.DataFrame.from_records([get_details(model) for model in data
                                                           if model['is_model'] == True])
            else:
                self.__models = pd.DataFrame(columns=["Model", "Size", "Timestamp"])

            # Latest models are fetched; reset the flag.
            self.__models_changed = False

        except (TeradataMlException, RuntimeError):
            raise

        except Exception as err:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "models", err)
            raise TeradataMlException(error_msg, msg_code)

    @property
    @collect_queryband(queryband="EnvMdls")
    def models(self):
        """
        DESCRIPTION:
            A class property that returns list of models installed in remote user environment.

        PARAMETERS:
            None

        RETURNS:
            Pandas DataFrame containing models and their details.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('testenv', 'python_3.8.13', 'Test environment')
            User environment testenv created.

            # User should create a zip file containing all files related to model
            # and use path to that zip file to install model using install_model()
            # API. Let's assume that all models files are zipped under 'large_model.zip'
            >>> model = 'large_model.zip'

            # Install the model in the 'testenv' environment.
            >>> env.install_model(model_path = model)
            Request for install_model is completed successfully.
                                           Claim Id  File/Libs/Model    Method Name               Stage             Timestamp  Additional Details
            0  70ba8bb6-9c0b-41f1-af44-5fd1b9e31c7d  large_model.zip  install_model  Endpoint Generated  2023-10-31T07:34:21Z
            1  70ba8bb6-9c0b-41f1-af44-5fd1b9e31c7d  large_model.zip  install_model       File Uploaded  2023-10-31T07:35:37Z
            2  70ba8bb6-9c0b-41f1-af44-5fd1b9e31c7d  large_model.zip  install_model      File Installed  2023-10-31T07:35:38Z

            # List models installed in the user environment.
            >>> env.models
                     Model  Size             Timestamp
            0  large_model  6144  2023-10-31T07:35:38Z
            """
        # Fetch the list of files from remote user environment only when they are not already fetched in this object
        # or files are changed either by install or remove functions.
        if self.__models is None or self.__models_changed:
            self._set_models()

        if len(self.__models) == 0:
            print("No models found in remote user environment {}.".format(self.env_name))
        else:
            return self.__models

    def __manage(self, file_contents, option="INSTALL"):
        """
        DESCRIPTION:
            Function installs, removes and updates Python libraries from
            remote user environment.

        PARAMETERS:
            file_contents:
                Required Argument.
                Specifies the contents of the file in binary format.
                Types: binary

            option:
                Required Argument.
                Specifies the action intended to be performed on the libraries.
                Permitted Values: INSTALL, UNINSTALL, UPDATE
                Types: str
                Default Value: INSTALL

        RETURNS:
            True, if the operation is successful.

        RAISES:
            TeradataMlException, SqlOperationalError

        EXAMPLES:
            self.__manage(b'pandas' ,"INSTALL")
            self.__manage(b'pandas', "UNINSTALL")
            self.__manage(b'pandas', "UPDATE")
        """
        # Common code to call XSP manage_libraries with options "INSTALL", "UNINSTALL", "update"
        # This internal method will be called by install_lib, uninstall_lib and update_lib.
        __arg_info_matrix = []
        __arg_info_matrix.append(["option", option, False, (str), True, ["INSTALL", "UNINSTALL", "UPDATE"]])

        # Validate arguments
        _Validators._validate_missing_required_arguments(__arg_info_matrix)
        _Validators._validate_function_arguments(__arg_info_matrix)

        try:
            # Prepare the payload.
            # Update the action to 'UPGRADE' for the post call as the UES accepts 'UPGRADE'.
            http_req = HTTPRequest.POST
            if option == "UPDATE":
                http_req = HTTPRequest.PUT
            elif option == "UNINSTALL":
                http_req = HTTPRequest.DELETE

            files = {
                'reqs-file': ("requirements.txt", file_contents),
            }

            # Get the API name (install_lib or uninstall_lib or update_lib) which calls
            # __manage_libraries which ends up calling this function.
            api_name = inspect.stack()[2].function

            # UES accepts multiform data. Specifying the 'files' attribute makes 'requests'
            # module to send it as multiform data.
            resp = UtilFuncs._http_request(url=_get_ues_url(env_name=self.env_name, libs=True, api_name=api_name),
                                           method_type=http_req,
                                           headers=_get_auth_token(),
                                           files=files)

            # Process the response.
            resp = _process_ues_response(api_name="{}_lib".format(option.lower()), response=resp)

            # Set the flag to indicate that libraries are changed in remote user environment.
            self.__libs_changed = True
            return resp.json().get("claim_id", "")

        except (TeradataMlException, RuntimeError):
            raise
        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, "{}_lib".format(option.lower()), str(emsg))
            raise TeradataMlException(error_msg, msg_code)

    def __validate(self, libs=None, libs_file_path=None, asynchronous=True, timeout=None):
        """
        DESCRIPTION:
            Function performs argument validations.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies file path with extension.
                Types: str

            asynchronous:
                Optional Argument.
                Specifies whether to install/uninstall/update the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are installed/uninstalled/updated
                asynchronously. Otherwise, libraries are installed/uninstalled/updated synchronously.
                Default Value: True
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the libraries. If the library is
                not installed/uninstalled/updated with in 'timeout' seconds, the function returns a
                claim-id and one can check the status using the claim-id. If 'timeout' is not specified,
                then there is no limit on the wait time.
                Types: int OR float

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            __validate_requirement_filename(libs_file_path = 'data/requirements.txt')
            __validate_requirement_filename(libs="numpy")
            __validate_requirement_filename(libs=['pandas','numpy'])
        """
        __arg_info_matrix = []
        __arg_info_matrix.append(["libs", libs, True, (str, list), True])
        __arg_info_matrix.append(["libs_file_path", libs_file_path, True, str, True])
        __arg_info_matrix.append(["asynchronous", asynchronous, True, bool])
        __arg_info_matrix.append(["timeout", timeout, True, (int, float)])

        # Argument validation.
        _Validators._validate_missing_required_arguments(__arg_info_matrix)
        _Validators._validate_function_arguments(__arg_info_matrix)
        _Validators._validate_mutually_exclusive_arguments(libs, "libs", libs_file_path, "libs_file_path")

        if libs_file_path is not None:
            # If user has specified libraries in a file.
            _Validators._validate_file_exists(libs_file_path)

            # Verify only files with .txt extension are allowed for Python environment and
            # with .txt or .json extension are allowed for R environment.
            if self.base_env.lower().startswith('python_'):
                _Validators._validate_file_extension(libs_file_path, ['txt'])
            elif self.base_env.lower().startswith('r_'):
                if self.conda_env:
                    _Validators._validate_file_extension(libs_file_path, ['txt'])
                else:
                    _Validators._validate_file_extension(libs_file_path, ['txt', 'json'])

            _Validators._check_empty_file(libs_file_path)

        if timeout is not None:
            _Validators._validate_argument_range(timeout, 'timeout', lbound=0, lbound_inclusive=False)

    def __manage_libraries(self, libs=None, libs_file_path=None, action="INSTALL", asynchronous=False, timeout=None):
        """
        DESCRIPTION:
            Internal function to perform argument validation, requirement text file
            generation and executing XSP call to get the results.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the file (including file name)
                which supplies a list of libraries to be installed in remote user
                environment. Path specified should include the filename with extension.
                Notes:
                    1. The file must have an ".txt" extension for Python environment
                       and ".txt"/".json" extension for R environment.
                    2. Either "libs" or "libs_file_path" argument must be specified.
                Types: str

            action:
                Optional Argument.
                Specifies if libraries are to be installed or uninstalled or updated
                from remote user environment.
                Default Value: 'INSTALL'
                Types: str

            asynchronous:
                Optional Argument.
                Specifies whether to install/uninstall/update the library in
                remote user environment synchronously or asynchronously. When
                set to True, libraries are installed/uninstalled/updated asynchronously.
                Otherwise, libraries are installed/uninstalled/updated synchronously.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the maximum number of seconds to install/uninstall/update
                the libraries in remote user environment. If None, then there is
                no limit on the wait time.
                * Argument is ignored when 'asynchronous' is True.
                Types: int OR float

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            __manage_libraries(libs_file_path="/data/requirement.txt", action="INSTALL")
            __manage_libraries(libs="pandas", action="UNINSTALL")
            __manage_libraries(libs=["pandas","numpy","joblib==0.13.2"], action="UPDATE")
        """
        # Argument validation.
        self.__validate(libs, libs_file_path, asynchronous, timeout)

        # If file is provided, store the file_name and also extracts it contents
        if libs_file_path is not None:
            value = libs_file_path
            file_contents = UtilFuncs._get_file_contents(libs_file_path, read_in_binary_mode=True)
        else:
            # If libs are provided as string or list, convert the contents to binary.
            # When library names are provided in a list, create a string.
            file_contents = self.__get_file_contents(libs, action)
            # Store it with comma separated values if it is a list.
            value = ', '.join(libs) if isinstance(libs, list) else libs
            # Convert to binary.
            file_contents = file_contents.encode('ascii')

        claim_id = self.__manage(file_contents, action)
        action = action.lower()
        self.__claim_ids[claim_id] = {"action": "{}_lib".format(action), "value": value}

        # Check if installation should be asynchronous or not. If it is, then
        # return claim id and let user poll the status using status API.
        # Else, poll the status API for 'timeout' seconds.
        if asynchronous:
            print("Request to {} libraries initiated successfully in the remote user environment {}. "
                  "Check the status using status() with the claim id '{}'.".format(
                   action, self.env_name, claim_id))
            return claim_id
        else:
            return self.__get_claim_status(claim_id, timeout, "{} libraries".format(action))

    def __get_file_contents(self, libs, action):
        """
        DESCRIPTION:
            Function takes the list of string or string and converts it to
            a single string in case of Python environment and converts it
            to Json format for the R environment.

        PARAMETER:
            libs: Specifies the add-on library name(s), to be converted to
            file content.

        Returns:
            None
        """
        # Check if the env is python or conda env
        if not self._r_env or self.conda_env:
            if isinstance(libs, list):
                return '\n'.join(libs)
            return libs
        else:
            # render library and version from libs parameter, as dict
            # with lib as key and value as version
            result = UtilFuncs._get_dict_from_libs(libs)
            # When action is 'UNINSTALL' return in json format which is different from 'INSTALL' json format
            if action == 'UNINSTALL':
                return json.dumps({"packages": [key for key in result.keys()]})

            return json.dumps({"repositories": configure.cran_repositories if configure.cran_repositories is not None else [],
                                "cran_packages": [{
                                    "name": key,
                                    "version": value
                                } for key, value in result.items()]
                             })

    @collect_queryband(queryband="InstlLbs")
    def install_lib(self, libs=None, libs_file_path=None, **kwargs):
        """
        DESCRIPTION:
            Function installs Python or R libraries in the remote user environment.
            Note:
                * Use "install_lib" API call for first time package installation within
                  the environment. Use "update_lib" API only to upgrade or downgrade installed
                  packages and do not use it for fresh package installation when multiple
                  packages have the same dependency as it messes pip's package resolution ability.
                * For Conda R environment:
                  * The library version cannot be specified. Conda only install packages to the
                    latest compatible version and cannot install to a specific version.
                  * The libraries should have "r-" prefix in the library name.


        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the add-on library name(s).
                Notes:
                    *   Either "libs" or "libs_file_path" argument must be specified.
                    *   Version specified during the installation of R libraries
                        is not taken into consideration. The versions specified
                        in the parameters are only considered when update_lib()
                        is used.
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the file (including file name)
                which supplies a list of libraries to be installed in remote user environment.
                Path specified should include the filename with extension.
                The file should contain library names and version number(optional) of libraries.
                Notes:
                    *   Either "libs" or "libs_file_path" argument must be specified.
                    *   The file must have ".txt" extension for Python environment
                        and ".txt"/".json" extension for R environment.
                    *   The file must have ".txt" extension for conda environment.
                    *   The file format should adhere to the specifications of the
                        requirements file used by underlying language's package
                        manager to install libraries.
                        Sample text file content for Python environment:
                            numpy
                            joblib==0.13.2
                        Sample json/txt file content for R environment:
                            {
                                "cran_packages": [{
                                    "name": "anytime",
                                    "version": ""
                                }, {
                                    "name": "glm2",
                                    "version": ""
                                }]
                            }
                    *   Version specified during the installation of R libraries
                        is not taken into consideration. The versions specified in
                        the parameters are only considered when update_lib() is used.
                Types: str

        **kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to install the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are installed
                asynchronously. Otherwise, libraries are installed synchronously.
                Note:
                    One should not use remove_env() on the same environment till the
                    asynchronous call is complete.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for installing the libraries. If the library is
                not installed with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            Pandas DataFrame when libraries are installed synchronously.
            claim_id, to track status when libraries are installed asynchronously.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create remote user Python environment.
            >>> env = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Example 1: Install single Python library asynchronously.
            >>> env.install_lib('numpy', asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '4b062b0e-6e9f-4996-b92b-5b20ac23b0f9'.

            # Check the status.
            >>> env.status('4b062b0e-6e9f-4996-b92b-5b20ac23b0f9')
                                           Claim Id File/Libs  Method Name     Stage             Timestamp Additional Details
            0  4b062b0e-6e9f-4996-b92b-5b20ac23b0f9     numpy  install_lib   Started  2022-07-13T11:07:34Z               None
            1  4b062b0e-6e9f-4996-b92b-5b20ac23b0f9     numpy  install_lib  Finished  2022-07-13T11:07:35Z               None
            >>>

            # Verify if libraries are installed.
            >>> env.libs
                  library version
            0       numpy  1.21.6
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Example 2: Install libraries asynchronously by passing them as list of library names.
            >>> env.install_lib(["pandas",
            ...                   "joblib==0.13.2",
            ...                   "scikit-learn",
            ...                   "numpy>=1.17.1",
            ...                   "nltk>=3.3,<3.5"], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '90aae7df-5efe-4b5a-af26-150aab35f1fb'.

            # Check the status.
            >>> env.status('90aae7df-5efe-4b5a-af26-150aab35f1fb')
                                           Claim Id                                                           File/Libs  Method Name     Stage             Timestamp Additional Details
            0  90aae7df-5efe-4b5a-af26-150aab35f1fb pandas, joblib==0.13.2, scikit-learn, numpy>=1.17.1, nltk>=3.3,<3.5  install_lib   Started  2022-07-13T11:09:39Z               None
            1  90aae7df-5efe-4b5a-af26-150aab35f1fb pandas, joblib==0.13.2, scikit-learn, numpy>=1.17.1, nltk>=3.3,<3.5  install_lib  Finished  2022-07-13T11:09:40Z               None

            # Verify if libraries are installed with specific version.
            >>> env.libs
                        library version
            0            joblib  0.13.2
            1              nltk   3.4.5
            2             numpy  1.21.6
            3            pandas   1.3.5
            4               pip  20.1.1
            5   python-dateutil   2.8.2
            6              pytz  2022.1
            7      scikit-learn   1.0.2
            8             scipy   1.7.3
            9        setuptools  47.1.0
            10              six  1.16.0
            11    threadpoolctl   3.1.0

            # Example 3: Install libraries synchronously by passing them as list of library names.
            >>> env.install_lib(["Flask", "gunicorn"])
                                           Claim Id        File/Libs  Method Name     Stage             Timestamp Additional Details
            0  ebc11a82-4606-4ce3-9c90-9f54d1260f47  Flask, gunicorn  install_lib   Started  2022-08-12T05:35:58Z
            1  ebc11a82-4606-4ce3-9c90-9f54d1260f47  Flask, gunicorn  install_lib  Finished  2022-08-12T05:36:13Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                              name version
            0                click   8.1.3
            1                Flask   2.2.2
            2             gunicorn  20.1.0
            3   importlib-metadata  4.12.0
            4         itsdangerous   2.1.2
            5               Jinja2   3.1.2
            6               joblib  0.13.2
            7           MarkupSafe   2.1.1
            8                 nltk   3.4.5
            9                numpy  1.21.6
            10              pandas   1.3.5
            11                 pip  20.1.1
            12     python-dateutil   2.8.2
            13                pytz  2022.2
            14        scikit-learn   1.0.2
            15               scipy   1.7.3
            16          setuptools  64.0.1
            17                 six  1.16.0
            18       threadpoolctl   3.1.0
            19   typing-extensions   4.3.0
            20            Werkzeug   2.2.2
            21                zipp   3.8.1
            >>>

            # Example 4: Install libraries synchronously by passing them as list of library names within a
            #            specific timeout of 5 seconds.
            >>> env.install_lib(["teradataml",  "teradatasqlalchemy"], timeout=5)
            Request to install libraries initiated successfully in the remote user environment 'testenv' but unable to get the status. Check the status using status() with the claim id '30185e0e-bb09-485a-8312-c267fb4b3c1b'.
            '30185e0e-bb09-485a-8312-c267fb4b3c1b'

            # Check the status.
            >>> env.status('30185e0e-bb09-485a-8312-c267fb4b3c1b')
                                           Claim Id                       File/Libs  Method Name     Stage             Timestamp Additional Details
            0  30185e0e-bb09-485a-8312-c267fb4b3c1b  teradataml, teradatasqlalchemy  install_lib   Started  2022-08-12T05:42:58Z
            1  30185e0e-bb09-485a-8312-c267fb4b3c1b  teradataml, teradatasqlalchemy  install_lib  Finished  2022-08-12T05:43:29Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                              name    version
            0              certifi  2022.6.15
            1   charset-normalizer      2.1.0
            2                click      8.1.3
            3               docker      5.0.3
            4                Flask      2.2.2
            5             greenlet      1.1.2
            6             gunicorn     20.1.0
            7                 idna        3.3
            8   importlib-metadata     4.12.0
            9         itsdangerous      2.1.2
            10              Jinja2      3.1.2
            11              joblib     0.13.2
            12          MarkupSafe      2.1.1
            13                nltk      3.4.5
            14               numpy     1.21.6
            15              pandas      1.3.5
            16                 pip     20.1.1
            17              psutil      5.9.1
            18        pycryptodome     3.15.0
            19     python-dateutil      2.8.2
            20                pytz     2022.2
            21            requests     2.28.1
            22        scikit-learn      1.0.2
            23               scipy      1.7.3
            24          setuptools     64.0.1
            25                 six     1.16.0
            26          SQLAlchemy     1.4.40
            27          teradataml  17.10.0.1
            28         teradatasql  17.20.0.1
            29  teradatasqlalchemy   17.0.0.3
            30       threadpoolctl      3.1.0
            31   typing-extensions      4.3.0
            32             urllib3    1.26.11
            33    websocket-client      1.3.3
            34            Werkzeug      2.2.2
            35                zipp      3.8.1
            >>>

            # Example 5: Install libraries asynchronously by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            pandas
            joblib==0.13.2
            scikit-learn
            numpy>=1.17.1
            nltk>=3.3,<3.5
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> env.install_lib(libs_file_path="requirement.txt", asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'f11c7f28-f958-4cae-80a8-926733954bdc'.

            # Check the status.
            >>> env.status('8709b464-f144-4c37-8918-ef6a98ecf295')
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  f11c7f28-f958-4cae-80a8-926733954bdc  requirements.txt  install_lib   Started  2022-07-13T11:23:23Z               None
            1  f11c7f28-f958-4cae-80a8-926733954bdc  requirements.txt  install_lib  Finished  2022-07-13T11:25:37Z               None
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                        library version
            0            joblib  0.13.2
            1              nltk   3.4.5
            2             numpy  1.21.6
            3            pandas   1.3.5
            4               pip  20.1.1
            5   python-dateutil   2.8.2
            6              pytz  2022.1
            7      scikit-learn   1.0.2
            8             scipy   1.7.3
            9        setuptools  47.1.0
            10              six  1.16.0
            11    threadpoolctl   3.1.0

            # Example 6: Install libraries synchronously by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            matplotlib
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> env.install_lib(libs_file_path="requirements.txt")
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  6221681b-f663-435c-80a9-3f99d2af5d83  requirements.txt  install_lib   Started  2022-08-12T05:49:09Z
            1  6221681b-f663-435c-80a9-3f99d2af5d83  requirements.txt  install_lib  Finished  2022-08-12T05:49:41Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                              name    version
            0              certifi  2022.6.15
            1   charset-normalizer      2.1.0
            2                click      8.1.3
            3               cycler     0.11.0
            4               docker      5.0.3
            5                Flask      2.2.2
            6            fonttools     4.34.4
            7             greenlet      1.1.2
            8             gunicorn     20.1.0
            9                 idna        3.3
            10  importlib-metadata     4.12.0
            11        itsdangerous      2.1.2
            12              Jinja2      3.1.2
            13              joblib     0.13.2
            14          kiwisolver      1.4.4
            15          MarkupSafe      2.1.1
            16          matplotlib      3.5.3
            17                nltk      3.4.5
            18               numpy     1.21.6
            19           packaging       21.3
            20              pandas      1.3.5
            21              Pillow      9.2.0
            22                 pip     20.1.1
            23              psutil      5.9.1
            24        pycryptodome     3.15.0
            25           pyparsing      3.0.9
            26     python-dateutil      2.8.2
            27                pytz     2022.2
            28            requests     2.28.1
            29        scikit-learn      1.0.2
            30               scipy      1.7.3
            31          setuptools     64.0.1
            32                 six     1.16.0
            33          SQLAlchemy     1.4.40
            34          teradataml  17.10.0.1
            35         teradatasql  17.20.0.1
            36  teradatasqlalchemy   17.0.0.3
            37       threadpoolctl      3.1.0
            38   typing-extensions      4.3.0
            39             urllib3    1.26.11
            40    websocket-client      1.3.3
            41            Werkzeug      2.2.2
            42                zipp      3.8.1
            >>>

            # Create remote user R environment.
            >>> env = create_env('testenv', 'r_4.1', 'Test environment')
            User environment 'testenv' created.

            # Example 1: Install single R library asynchronously.
            >>> env.install_lib('glm2', asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'd073a1c8-08bc-45d0-99de-65dc189db408'.

            # Check the status.
            >>> env.status('d073a1c8-08bc-45d0-99de-65dc189db408')

                                        Claim Id	File/Libs	Method Name	   Stage	      Timestamp	        Additional Details
            0	d073a1c8-08bc-45d0-99de-65dc189db408	glm2	install_lib	   Started	  2023-08-29T09:09:30Z
            1	d073a1c8-08bc-45d0-99de-65dc189db408	glm2	install_lib	   Finished	  2023-08-29T09:09:35Z
            >>>

            # Verify if libraries are installed.
            >>> env.libs
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
            30        glm2    1.2.1
            >>>

            # Example 2: Install libraries asynchronously by passing them as list of library names.
            >>> env.install_lib(['glm2', 'stringi'], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '6b2ca7ac-f113-440c-bf24-1ce75ed59f36'.

            # Check the status.
            >>> env.status('90aae7df-5efe-4b5a-af26-150aab35f1fb')

                                            Claim Id	File/Libs	            Method Name	   Stage	  Timestamp	           Additional Details
            0	6b2ca7ac-f113-440c-bf24-1ce75ed59f36	glm2==1.2.1, stringi	install_lib	   Started	  2023-08-29T09:42:39Z
            1	6b2ca7ac-f113-440c-bf24-1ce75ed59f36	glm2==1.2.1, stringi	install_lib	   Finished	  2023-08-29T09:43:58Z
            >>>

            # Verify if libraries are installed or not.
            >>> env.libs
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
            30        glm2    1.2.1
            31     stringi   1.7.12
            >>>

            # Example 3: Install libraries synchronously by passing them as list of library names.
            >>> env.install_lib(["lubridate", "zoo"])
                                            Claim Id	File/Libs	    Method Name	  Stage	     Timestamp	          Additional Details
            0	7483fa01-dedb-4fb2-9262-403da6b49a3b	lubridate, zoo	install_lib	  Started	 2023-08-29T09:51:25Z
            1	7483fa01-dedb-4fb2-9262-403da6b49a3b	lubridate, zoo	install_lib	  Finished	 2023-08-29T09:52:20Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
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
            30       cpp11    0.4.6
            31    generics    0.1.3
            32        glm2    1.2.1
            33   lubridate    1.9.2
            34     stringi   1.7.12
            35  timechange    0.2.0
            36         zoo   1.8-12
            >>>
            
            # Example 4: Install libraries synchronously by passing them as list of library names within a
            #            specific timeout of 1 seconds.
            >>> env.install_lib(["stringi",  "glm2"], timeout=1)
            Request to install libraries initiated successfully in the remote user environment 'testenv' but Timed out
            status check. Check the status using status() with the claim id '7303cf6d-acea-4ab0-83b8-e6cf9149fe51'.

            # Check the status.
            >>> env.status('7303cf6d-acea-4ab0-83b8-e6cf9149fe51')
                                            Claim Id	File/Libs	    Method Name	   Stage	  Timestamp	           Additional Details
            0	7303cf6d-acea-4ab0-83b8-e6cf9149fe51	stringi, glm2	install_lib	   Started	  2023-08-29T10:18:48Z
            1	7303cf6d-acea-4ab0-83b8-e6cf9149fe51	stringi, glm2	install_lib	   Finished	  2023-08-29T10:20:08Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
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
            30       cpp11    0.4.6
            31    generics    0.1.3
            32        glm2    1.2.1
            33   lubridate    1.9.2
            34     stringi   1.7.12
            35  timechange    0.2.0
            36         zoo   1.8-12
            >>>

            # Example 5: Install libraries synchronously by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            {
                "cran_packages": [{
                    "name": "anytime",
                    "version": ""
                }, {
                    "name": "glm2",
                    "version": ""
                }]
            }
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> env.install_lib(libs_file_path="requirement.txt")
                                            Claim Id	File/Libs	      Method Name	Stage	    Timestamp	         Additional Details
            0	eab69326-5e14-4c81-8157-408fe0b633c2	requirement.txt	  install_lib	Started	    2023-08-29T12:18:26Z
            1	eab69326-5e14-4c81-8157-408fe0b633c2	requirement.txt	  install_lib	Finished	2023-08-29T12:23:12Z
            >>>

            # Verify if libraries are installed with specific version.
            >>> env.libs
                      name   version
            0   KernSmooth   2.23-20
            1         MASS    7.3-55
            2       Matrix     1.4-0
            3         base     4.1.3
            4         boot    1.3-28
            5        class    7.3-20
            6      cluster     2.1.2
            7    codetools    0.2-18
            8     compiler     4.1.3
            9     datasets     4.1.3
            10     foreign    0.8-82
            11   grDevices     4.1.3
            12    graphics     4.1.3
            13        grid     4.1.3
            14     lattice   0.20-45
            15     methods     4.1.3
            16        mgcv    1.8-39
            17        nlme   3.1-155
            18        nnet    7.3-17
            19    parallel     4.1.3
            20     remotes     2.4.2
            21       rpart    4.1.16
            22     spatial    7.3-15
            23     splines     4.1.3
            24       stats     4.1.3
            25      stats4     4.1.3
            26    survival    3.2-13
            27       tcltk     4.1.3
            28       tools     4.1.3
            29       utils     4.1.3
            30          BH  1.81.0-1
            31        Rcpp    1.0.11
            32     anytime     0.3.9
            33       cpp11     0.4.6
            34    generics     0.1.3
            35        glm2     1.2.1
            36   lubridate     1.9.2
            37     stringi    1.7.12
            38  timechange     0.2.0
            39         zoo    1.8-12
            >>>

            # Create remote user conda R environment.
            >>> env = create_env('testenv', base_env='r_4.3', desc='Test environment', conda_env=True)
            Conda environment creation initiated.
            User environment 'testenv' created.

            # Example 1: Install single R library asynchronously.
            >>> env.install_lib('r-glm2', asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'cccc29fe-ca45-49a6-9565-3d50bf310c92'.

            # Check the status.
            >>> env.status('cccc29fe-ca45-49a6-9565-3d50bf310c92')
            Claim Id                                 File/Libs/Model   Method Name   Stage    Timestamp              Additional Details
            cccc29fe-ca45-49a6-9565-3d50bf310c92     r-glm2            install_lib   Started  2024-12-27T08:42:10Z   
            cccc29fe-ca45-49a6-9565-3d50bf310c92     r-glm2            install_lib   Finished 2024-12-27T08:42:20Z

            # Verify if libraries are installed.
            >>> env.libs[env.libs['name'].isin(['r-glm2'])]
            	name	version
            91	r-glm2	1.2.1

            # Example 2: Install libraries asynchronously by passing them as list of library names.
            >>> env.install_lib(['r-ggplot2', 'r-dplyr'], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '1125fa9e-b0f4-49cb-9c9f-d4931a22222d'.

            # Check the status.
            >>> env.status('1125fa9e-b0f4-49cb-9c9f-d4931a22222d')
            Claim Id                                 File/Libs/Model     Method Name   Stage    Timestamp              Additional Details
            1125fa9e-b0f4-49cb-9c9f-d4931a22222d     r-ggplot2, r-dplyr  install_lib   Started  2024-12-27T08:42:10Z   
            1125fa9e-b0f4-49cb-9c9f-d4931a22222d     r-ggplot2, r-dplyr  install_lib   Finished 2024-12-27T08:42:20Z

            # Verify if libraries are installed or not.
            >>> env.libs[env.libs['name'].isin(['r-ggplot2', 'r-dplyr'])]
            	name	    version
            79	r-dplyr     1.1.3
            90	r-ggplot2   3.4.4

            # Example 3: Install libraries synchronously by passing them as list of library names.
            >>> env.install_lib(["r-lubridate", "r-zoo"])
            Claim Id                                 File/Libs/Model      Method Name   Stage    Timestamp              Additional Details
            7a026a0d-6616-4398-bd89-9f8d0e06a54f     r-lubridate, r-zoo   install_lib   Started  2024-12-27T08:46:55Z   
            7a026a0d-6616-4398-bd89-9f8d0e06a54f     r-lubridate, r-zoo   install_lib   Finished 2024-12-27T08:47:06Z

            # Verify if libraries are installed.
            >>> env.libs[env.libs['name'].isin(['r-lubridate', 'r-zoo'])]
            	name	    version
            108	r-lubridate 1.9.3
            157	r-zoo       1.8_12

            # Example 4: Install libraries synchronously by passing them as list of library names within a
            #            specific timeout of 1 seconds.
            >>> env.install_lib(["r-stringi",  "r-glm2"], timeout=1)
            Request to install libraries initiated successfully in the remote user environment 'testenv' but Timed out status check. 
            Check the status using status() with the claim id '440eff39-c6d7-4efc-b797-1201a5906065'.

            # Check the status.
            >>> env.status('440eff39-c6d7-4efc-b797-1201a5906065')
            Claim Id                                 File/Libs/Model      Method Name   Stage    Timestamp              Additional Details
            440eff39-c6d7-4efc-b797-1201a5906065     r-stringi, r-glm2    install_lib   Started  2024-12-27T08:49:17Z   
            440eff39-c6d7-4efc-b797-1201a5906065     r-stringi, r-glm2    install_lib   Finished 2024-12-27T08:49:27Z

            # Verify if libraries are installed.
            >>> env.libs[env.libs['name'].isin(['r-stringi', 'r-glm2'])]
                    name	version
            91	   r-glm2	1.2.1
            140	 r-stringi	1.7.12
            
            # Example 5: Install libraries synchronously by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            r-caret
            r-forecast
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> env.install_lib(libs_file_path="requirement.txt")
            Claim Id                               File/Libs/Model    Method Name   Stage    Timestamp              Additional Details
            f3963a46-2225-412d-a470-17f26c759b42   requirement.txt    install_lib   Started  2024-12-27T08:52:28Z   
            f3963a46-2225-412d-a470-17f26c759b42   requirement.txt    install_lib   Finished 2024-12-27T08:53:32Z

            # Verify if libraries are installed.
            >>> env.libs[env.libs['name'].isin(['r-caret', 'r-forecast'])]
                name	    version
            68	r-caret	    6.0_94
            85	r-forecast  8.21.1
        """
        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout")
        async_task_info = self.__manage_libraries(libs, libs_file_path, "INSTALL", asynchronous, timeout)
        return async_task_info

    @collect_queryband(queryband="UninstlLbs")
    def uninstall_lib(self, libs=None, libs_file_path=None, **kwargs):
        """
        DESCRIPTION:
            Function uninstalls libraries from corresponding Python or R
            remote user environment.
            Note:
                * For Conda R environment, the libraries should have "r-" prefix in the library name.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the library name(s).
                Note:
                    Either "libs" or "libs_file_path" argument must be specified.
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the file (including file name)
                which supplies a list of libraries to be uninstalled from the remote user
                environment. Path specified should include the filename with extension.
                The file should contain library names and version number(optional) of libraries.
                Notes:
                    *   Either "libs" or "libs_file_path" argument must be specified.
                    *   The file must have ".txt" extension for Python environment
                        and ".txt"/".json" extension for R environment.
                    *   The file must have ".txt" extension for conda environment.
                    *   The file format should adhere to the specifications of the
                        requirements file used by underlying language's package
                        manager for uninstalling libraries.
                        Sample text file content for Python environment:
                            numpy
                            joblib==0.13.2
                        Sample json/txt file content for R environment:
                            {
                                "packages": ["anytime","glm2"]
                            }
                Types: str

        **kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to uninstall the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are uninstalled
                asynchronously. Otherwise, libraries are uninstalled synchronously.
                Note:
                    One should not use remove_env() on the same environment till the
                    asynchronous call is complete.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for uninstalling the libraries. If the library is
                not uninstalled with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            Pandas DataFrame when libraries are uninstalled synchronously.
            claim_id, to track status when libraries are uninstalled asynchronously.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Examples for Python environment.
            # Create remote Python user environment.
            >>> testenv = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Example 1: Install and uninstall a single Python library.
            >>> testenv.install_lib('numpy')
                                           Claim Id File/Libs  Method Name     Stage             Timestamp Additional Details
            0  407e644d-3630-4085-8a0b-169406f52340     numpy  install_lib   Started  2022-07-13T11:32:32Z               None
            1  407e644d-3630-4085-8a0b-169406f52340     numpy  install_lib  Finished  2022-07-13T11:32:33Z               None
            >>>

            # Verify installed library.
            >>> testenv.libs
                  library version
            0       numpy  1.21.6
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Uninstall single Python library asynchronously.
            >>> testenv.uninstall_lib('numpy', asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '16036846-b9d7-4c5b-be92-d7cf14aa2016'.

            # Check the status.
            >>> testenv.status('16036846-b9d7-4c5b-be92-d7cf14aa2016')
                                           Claim Id File/Libs    Method Name     Stage             Timestamp Additional Details
            0  16036846-b9d7-4c5b-be92-d7cf14aa2016     numpy  uninstall_lib   Started  2022-07-13T11:33:42Z               None
            1  16036846-b9d7-4c5b-be92-d7cf14aa2016     numpy  uninstall_lib  Finished  2022-07-13T11:33:42Z               None
            >>>

            # Verify library is uninstalled.
            >>> testenv.libs
                library	    version
            0	pip	        20.1.1
            1	setuptools	47.1.0

            # Example 2: Install list of Python libraries asynchronously and uninstall them synchronously.
            >>> testenv.install_lib(["pandas", "scikit-learn"], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'a91af321-cf57-43cc-b864-a67fa374cb42'.

            # Check the status
            >>> testenv.status('a91af321-cf57-43cc-b864-a67fa374cb42')
                                           Claim Id             File/Libs  Method Name     Stage             Timestamp Additional Details
            0  a91af321-cf57-43cc-b864-a67fa374cb42  pandas, scikit-learn  install_lib   Started  2022-07-13T11:34:38Z               None
            1  a91af321-cf57-43cc-b864-a67fa374cb42  pandas, scikit-learn  install_lib  Finished  2022-07-13T11:36:40Z               None
            >>>

            # Verify libraries are installed along with its dependant libraries.
            >>> testenv.libs
                        library version
            0            joblib   1.1.0
            1             numpy  1.21.6
            2            pandas   1.3.5
            3               pip  20.1.1
            4   python-dateutil   2.8.2
            5              pytz  2022.1
            6      scikit-learn   1.0.2
            7             scipy   1.7.3
            8        setuptools  47.1.0
            9               six  1.16.0
            10    threadpoolctl   3.1.0

            # Uninstall libraries by passing them as a list of library names.
            >>> testenv.uninstall_lib(["pandas", "scikit-learn"])
                                           Claim Id             File/Libs    Method Name     Stage             Timestamp Additional Details
            0  8d6bb524-c047-4aae-8597-b48ab467ef37  pandas, scikit-learn  uninstall_lib   Started  2022-07-13T11:46:55Z               None
            1  8d6bb524-c047-4aae-8597-b48ab467ef37  pandas, scikit-learn  uninstall_lib  Finished  2022-07-13T11:47:20Z               None
            >>>

            # Verify if the specified libraries are uninstalled.
             >>> testenv.libs
                       library version
            0           joblib   1.1.0
            1            numpy  1.21.6
            2              pip  20.1.1
            3  python-dateutil   2.8.2
            4             pytz  2022.1
            5            scipy   1.7.3
            6       setuptools  47.1.0
            7              six  1.16.0
            8    threadpoolctl   3.1.0

            # Example 3: Install and uninstall libraries specified in
            #            requirement text file asynchronously.

            # Install libraries by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            pandas
            joblib==0.13.2
            scikit-learn
            numpy>=1.17.1
            nltk>=3.3,<3.5
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> testenv.install_lib(libs_file_path="requirements.txt", asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'c3669eea-327c-453f-b068-6b5f3f4768a5'.

            # Check the status.
            >>> testenv.status('c3669eea-327c-453f-b068-6b5f3f4768a5')
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  c3669eea-327c-453f-b068-6b5f3f4768a5  requirements.txt  install_lib   Started  2022-07-13T11:48:46Z               None
            1  c3669eea-327c-453f-b068-6b5f3f4768a5  requirements.txt  install_lib  Finished  2022-07-13T11:50:09Z               None
            >>>

            # Verify libraries are installed along with its dependant libraries.
                        library version
            0            joblib   1.1.0
            1             numpy  1.21.6
            2            pandas   1.3.5
            3               pip  20.1.1
            4   python-dateutil   2.8.2
            5              pytz  2022.1
            6      scikit-learn   1.0.2
            7             scipy   1.7.3
            8        setuptools  47.1.0
            9               six  1.16.0
            10    threadpoolctl   3.1.0

            # Uninstall libraries specified in the file.
            >>> testenv.uninstall_lib(libs_file_path="requirements.txt", asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '95ebfc7b-2910-4aab-be80-3e47f84737bd'.

            # Check the status.
            >>> testenv.status('95ebfc7b-2910-4aab-be80-3e47f84737bd')
                                           Claim Id         File/Libs    Method Name     Stage             Timestamp Additional Details
            0  95ebfc7b-2910-4aab-be80-3e47f84737bd  requirements.txt  uninstall_lib   Started  2022-07-13T11:52:03Z               None
            1  95ebfc7b-2910-4aab-be80-3e47f84737bd  requirements.txt  uninstall_lib  Finished  2022-07-13T11:52:39Z               None
            >>>

            # Verify if the specified libraries are uninstalled.
             >>> testenv.libs
                       library version
            0           joblib   1.1.0
            1            numpy  1.21.6
            2              pip  20.1.1
            3  python-dateutil   2.8.2
            4             pytz  2022.1
            5            scipy   1.7.3
            6       setuptools  47.1.0
            7              six  1.16.0
            8    threadpoolctl   3.1.0

            # Example 4: Install and uninstall libraries specified in requirement text file synchronously
            #            by specifying the timeout.

            # Install libraries by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            matplotlib
            -----------------------------------------------------------

            # Install libraries specified in the file.
            >>> testenv.install_lib(libs_file_path="requirements.txt")
                                           Claim Id         File/Libs  Method Name     Stage             Timestamp Additional Details
            0  d441bc45-6594-4244-ba26-de2ca3272d3f  requirements.txt  install_lib   Started  2022-08-12T06:03:54Z
            1  d441bc45-6594-4244-ba26-de2ca3272d3f  requirements.txt  install_lib  Finished  2022-08-12T06:04:44Z
            >>>

            # Verify libraries are installed along with its dependant libraries.
            >>> testenv.libs
                             name version
            0              cycler  0.11.0
            1           fonttools  4.34.4
            2          kiwisolver   1.4.4
            3          matplotlib   3.5.3
            4               numpy  1.21.6
            5           packaging    21.3
            6              Pillow   9.2.0
            7                 pip  20.1.1
            8           pyparsing   3.0.9
            9     python-dateutil   2.8.2
            10         setuptools  47.1.0
            11                six  1.16.0
            12  typing-extensions   4.3.0
            >>>

            # Uninstall libraries specified in the file.
            >>> testenv.uninstall_lib(libs_file_path="requirements.txt", timeout=1)
            Request to uninstall libraries initiated successfully in the remote user environment 'testenv' but unable to get the status. Check the status using status() with the claim id '3e811857-969d-418c-893d-29ec38f54020'.
            '3e811857-969d-418c-893d-29ec38f54020'
            >>>

            # Check the status.
            >>> testenv.status('3e811857-969d-418c-893d-29ec38f54020')
                                           Claim Id         File/Libs    Method Name     Stage             Timestamp Additional Details
            0  3e811857-969d-418c-893d-29ec38f54020  requirements.txt  uninstall_lib   Started  2022-08-12T06:05:51Z
            1  3e811857-969d-418c-893d-29ec38f54020  requirements.txt  uninstall_lib  Finished  2022-08-12T06:05:57Z
            >>>

            # Verify if the specified libraries are uninstalled.
            >>> testenv.libs
                             name version
            0              cycler  0.11.0
            1           fonttools  4.34.4
            2          kiwisolver   1.4.4
            3               numpy  1.21.6
            4           packaging    21.3
            5              Pillow   9.2.0
            6                 pip  20.1.1
            7           pyparsing   3.0.9
            8     python-dateutil   2.8.2
            9          setuptools  47.1.0
            10                six  1.16.0
            11  typing-extensions   4.3.0
            >>>

            # Examples for R environment.
            # Create remote R user environment.
            >>> r_env = create_env('test_r_env', 'r_4.1', 'Test R environment')
            User environment 'test_r_env' created.
            >>>

            # Install R libraries in environment.
            >>> r_env.install_lib(['glm2', 'stringi', "lubridate", "zoo", "anytime", "plyr", "testthat", "dplyr"])
                                            Claim Id	                                       File/Libs	Method Name	   Stage	           Timestamp	Additional Details
            0	6c7d049e-bf80-49a3-bee3-e058f78655fd	glm2, stringi, lubridate, zoo, anytime, plyr, ...	install_lib	 Started	2023-09-12T09:30:14Z
            1	6c7d049e-bf80-49a3-bee3-e058f78655fd	glm2, stringi, lubridate, zoo, anytime, plyr, ...	install_lib	Finished	2023-09-12T09:42:48Z
            >>>

            # Verify installed libraries.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            33     anytime    0.3.9
            ..         ...      ...
            42       dplyr    1.1.3
            ..         ...      ...
            48        glm2    1.2.1
            ..         ...      ...
            52   lubridate    1.9.2
            ..         ...      ...
            57        plyr    1.8.8
            ..         ...      ...
            64     stringi   1.7.12
            65    testthat   3.1.10
            ..         ...      ...
            72       withr    2.5.0
            73         zoo   1.8-12
            >>>

            # Example 5: Uninstall single R library synchronously.
            >>> r_env.uninstall_lib('glm2')
                                            Claim Id	File/Libs	   Method Name	   Stage	           Timestamp	Additional Details
            0	f98cfbfd-8b1d-4ff8-8145-001a1e5b2009	     glm2	 uninstall_lib	 Started	2023-09-12T10:14:59Z
            1	f98cfbfd-8b1d-4ff8-8145-001a1e5b2009	     glm2	 uninstall_lib	Finished	2023-09-12T10:15:01Z
            
            # Verify if library is uninstalled.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            33     anytime    0.3.9
            ..         ...      ...
            42       dplyr    1.1.3
            ..         ...      ...
            51   lubridate    1.9.2
            ..         ...      ...
            56        plyr    1.8.8
            ..         ...      ...
            63     stringi   1.7.12
            64    testthat   3.1.10
            ..         ...      ...
            71       withr    2.5.0
            72         zoo   1.8-12
            >>>

            # Example 6: Uninstall multiple R libraries synchronously
            #            by passing them as a list of library names.
            >>> r_env.uninstall_lib(['stringi', "lubridate"])

                                            Claim Id	         File/Libs	  Method Name	   Stage	           Timestamp	Additional Details
            0	11103430-62fa-4983-ae52-fa176c5efa93	stringi, lubridate	uninstall_lib	 Started	2023-09-12T10:21:21Z
            1	11103430-62fa-4983-ae52-fa176c5efa93	stringi, lubridate	uninstall_lib	Finished	2023-09-12T10:21:23Z
            >>>

            # Verify if libraries are uninstalled.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            33     anytime    0.3.9
            ..         ...      ...
            42       dplyr    1.1.3
            ..         ...      ...
            55        plyr    1.8.8
            ..         ...      ...
            62    testthat   3.1.10
            ..         ...      ...
            69       withr    2.5.0
            70         zoo   1.8-12
            >>>

            # Example 7: Uninstall libraries synchronously by specifying
            #            them in a file.

            # Create a requirement.json file with below contents.
            -----------------------------------------------------------
            {
                "packages": ["zoo", "anytime"]
            }
            -----------------------------------------------------------

            # Uninstall libraries specified in the file.
            >>> r_env.uninstall_lib(libs_file_path="requirement.json")
                                            Claim Id	       File/Libs	  Method Name	   Stage	           Timestamp	Additional Details
            0	7fbba8d7-7f16-47d1-b02d-b1df8a79ad6b	requirement.json	uninstall_lib	 Started	2023-09-12T12:14:31Z
            1	7fbba8d7-7f16-47d1-b02d-b1df8a79ad6b	requirement.json	uninstall_lib	Finished	2023-09-12T12:14:33Z
            >>>

            # Verify if libraries are uninstalled.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            41       dplyr    1.1.3
            ..         ...      ...
            54        plyr    1.8.8
            ..         ...      ...
            61    testthat   3.1.10
            ..         ...      ...
            68       withr    2.5.0

            # Example 8: Uninstall R libraries asynchronously.
            >>> r_env.uninstall_lib(["plyr", "testthat"], asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment test_r_env. Check the status using status() with the claim id 'e6f90aaf-ecf5-467d-95cb-8032444494d6'.
            'e6f90aaf-ecf5-467d-95cb-8032444494d6'
            >>>

            # Check the status using claim id.
            >>> r_env.status('e6f90aaf-ecf5-467d-95cb-8032444494d6')
                                            Claim Id	     File/Libs	  Method Name	   Stage	           Timestamp	Additional Details
            0	e6f90aaf-ecf5-467d-95cb-8032444494d6	plyr, testthat	uninstall_lib	 Started	2023-09-12T12:18:50Z
            1	e6f90aaf-ecf5-467d-95cb-8032444494d6	plyr, testthat	uninstall_lib	Finished	2023-09-12T12:18:51Z
            >>>

            # Verify if libraries are uninstalled.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            4	      boot	 1.3-28
            ..         ...      ...
            41       dplyr    1.1.3
            ..         ...      ...
            65	     waldo	  0.5.1
            66       withr    2.5.0
            >>>

            # Examples for conda R environment.
            # Create remote conda R user environment.
            >>> conda_r_env = create_env('test_conda_r_env', 'r_4.3', 'Test conda R environment', conda_env=True)
            Conda environment creation initiated.
            User environment 'test_conda_r_env' created.

            # Install R libraries in conda environment.
            >>> conda_r_env.install_lib(['r-caret', 'r-forecast', 'r-glm2', 'r-anytime'])
            Claim Id                                 File/Libs/Model                          Method Name   Stage    Timestamp              Additional Details
            ec6c087e-aee5-42fd-8677-a5f2a8bc5050     r-caret, r-forecast, r-glm2, r-anytime   install_lib   Started  2024-12-27T10:23:34Z   
            ec6c087e-aee5-42fd-8677-a5f2a8bc5050     r-caret, r-forecast, r-glm2, r-anytime   install_lib   Finished 2024-12-27T10:28:15Z

            # Verify installed libraries.
            >>> conda_r_env.libs[conda_r_env.libs['name'].isin(['r-caret', 'r-forecast', 'r-glm2', 'r-anytime'])]
                      name  version
            67   r-anytime  0.3.9
            70     r-caret  6.0_94
            87  r-forecast  8.21.1
            93      r-glm2  1.2.1

            # Uninstall single R library asynchronously.
            >>> conda_r_env.uninstall_lib('r-caret', asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '77db7baf-1c4f-4de0-8019-d0f72718b90f'.

            # Check the status.
            >>> conda_r_env.status('77db7baf-1c4f-4de0-8019-d0f72718b90f')
            Claim Id                                 File/Libs   Method Name    Stage    Timestamp              Additional Details
            77db7baf-1c4f-4de0-8019-d0f72718b90f     r-caret    uninstall_lib  Started  2024-12-27T08:49:17Z   
            77db7baf-1c4f-4de0-8019-d0f72718b90f     r-caret    uninstall_lib  Finished 2024-12-27T08:49:19Z


            # Verify if library is uninstalled.
            >>> conda_r_env.libs[conda_r_env.libs['name'].isin(['r-caret'])]
                name	version

            # Example 5: Uninstall libraries synchronously by creating requirement.txt file.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            r-glm2
            r-anytime
            -----------------------------------------------------------

            # Uninstall libraries specified in the file.
            >>> conda_r_env.uninstall_lib(libs_file_path="requirement.txt")
            Claim Id                                 File/Libs        Method Name   Stage    Timestamp              Additional Details
            0f3963a46-2225-412d-a470-17f26c759b42   requirement.txt  install_lib   Started  2024-12-27T08:52:28Z   
            0f3963a46-2225-412d-a470-17f26c759b42   requirement.txt  install_lib   Finished 2024-12-27T08:52:32Z

            # Verify if libraries are uninstalled.
            >>> conda_r_env.libs[conda_r_env.libs['name'].isin(['r-glm2', 'r-anytime'])]
                name  version
 
        """
        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout")
        async_task_info = self.__manage_libraries(libs, libs_file_path, "UNINSTALL", asynchronous, timeout)
        return async_task_info

    @collect_queryband(queryband="UpdtLbs")
    def update_lib(self, libs=None, libs_file_path=None, **kwargs):
        """
        DESCRIPTION:
            Function updates Python or R libraries if already installed,
            otherwise installs the libraries in remote user environment.
            Notes:
                * Use "install_lib" API call for first time package installation within
                  the environment. Use "update_lib" API only to upgrade or downgrade installed
                  packages and do not use it for fresh package installation when multiple
                  packages have the same dependency as it messes pip's package resolution ability.
                * Use "update_lib" to update packages one at a time to prevent dependency resolution
                  issues.
                * For Conda R environment:
                  * The library version cannot be specified. Conda only updates the installed packages to the
                    latest compatible version and cannot update to a specific version.
                  * The libraries should have "r-" prefix in the library name.

        PARAMETERS:
            libs:
                Optional Argument.
                Specifies the library name(s).
                Notes:
                    *   Either "libs" or "libs_file_path" argument must be specified.
                    *   While passing the libraries as string or list of
                        strings, one should adhere to the requirements
                        specified by underlying language's package manager.
                        For conda environment:
                        *   Only library name(s) should be specified. Library version
                            cannot be specified.
                            Conda only updates the installed packages to the latest
                            compatible version and cannot update to a specific version.
                        For R environment:
                        *   Refer to allowed formats here:
                            https://remotes.r-lib.org/reference/install_version.html
                        *   Specifying as a character vector is not supported as one
                            of the accepted value.
                        *   Whitespace is required between comparator operator(s) and
                            version.
                        *   '==' should be used for exact version, '=' is not allowed.
                Types: str OR list of Strings(str)

            libs_file_path:
                Optional Argument.
                Specifies the absolute/relative path of the file (including file name)
                which supplies a list of libraries to be updated from the remote user
                environment. Path specified should include the filename with extension.
                The file should contain library name and version number(optional) of
                libraries.
                Notes:
                    *   Either "libs" or "libs_file_path" argument must be specified.
                    *   The file must have ".txt" extension for Python environment
                        and ".txt"/".json" extension for R environment.
                    *   The file format should adhere to the specifications of the
                        requirements file used by underlying language's package
                        manager for updating libraries.
                        Sample text file content for Python environment:
                            numpy
                            joblib==0.13.2
                        Sample json/txt file content for R environment:
                            {
                                "cran_packages": [{
                                    "name": "anytime",
                                    "version": "0.3.9"
                                }, {
                                    "name": "glm2",
                                    "version": ">= 1.1.2, < 1.2"
                                }]
                            }
                    * For conda environment:
                        * The file should only contain the package names.
                          Library version cannot be specified. Conda only updates the
                          installed packages to the latest compatible version and
                          cannot update to a specific version.
                        * The file should have ".txt" extension for R environment.
                          Sample text file content for R conda environment:
                            r-glm2
                            r-anytime
                Types: str

        **kwargs:
            asynchronous:
                Optional Argument.
                Specifies whether to update the library in remote user environment
                synchronously or asynchronously. When set to True, libraries are updated
                asynchronously. Otherwise, libraries are updated synchronously.
                Note:
                    One should not use remove_env() on the same environment till the
                    asynchronous call is complete.
                Default Value: False
                Types: bool

            timeout:
                Optional Argument.
                Specifies the time to wait in seconds for updating the libraries. If the library is
                not updated with in "timeout" seconds, the function returns a claim-id and one
                can check the status using the claim-id. If "timeout" is not specified, then there
                is no limit on the wait time.
                Note:
                     Argument is ignored when "asynchronous" is True.
                Types: int OR float

        RETURNS:
            claim_id, to track status.

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Examples for Python environment.
            # Create remote Python user environment.
            >>> testenv = create_env('testenv', 'python_3.7.9', 'Test environment')
            User environment testenv created.

            # Example 1: Update a single Python library asynchronously.
            # Install a Python library.
            >>> testenv.install_lib(["joblib==0.13.2"], asynchronous=True)
            Request to install libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'f44443a9-42c3-4fd3-b4a2-735d1bfb7c27'.

            # Check the status.
            >>> testenv.status('f44443a9-42c3-4fd3-b4a2-735d1bfb7c27')
                                           Claim Id       File/Libs  Method Name     Stage             Timestamp Additional Details
            0  f44443a9-42c3-4fd3-b4a2-735d1bfb7c27  joblib==0.13.2  install_lib  Finished  2022-07-13T11:54:31Z               None
            >>>

            # Verify joblib library is installed with specified version.
            >>> testenv.libs
                  library version
            0      joblib  0.13.2
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Update joblib libary to the new version specified.
            >>> testenv.update_lib("joblib==0.14.1", asynchronous=True)
            Request to update libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id '8bfe55fc-efaa-44c7-9137-af24b6bb9ef8'.

            # Check the status.
            >>> testenv.status('8bfe55fc-efaa-44c7-9137-af24b6bb9ef8')
                                           Claim Id       File/Libs Method Name     Stage             Timestamp Additional Details
            0  8bfe55fc-efaa-44c7-9137-af24b6bb9ef8  joblib==0.14.1  update_lib  Finished  2022-07-13T11:55:29Z               None
            >>>

            # Verify joblib library version is updated with specified version.
            >>> testenv.libs
                  library version
            0      joblib  0.14.1
            1         pip  20.1.1
            2  setuptools  47.1.0

            # Example 2: Update multiple Python libraries synchronously.
            >>> testenv.update_lib(["joblib==0.14.1","numpy==1.19.5"])
                                           Claim Id                      File/Libs Method Name     Stage             Timestamp Additional Details
            0  28e0e03e-469b-440c-a939-a0e8a901078f  joblib==0.14.1, numpy==1.19.5  update_lib   Started  2022-07-13T11:56:32Z               None
            1  28e0e03e-469b-440c-a939-a0e8a901078f  joblib==0.14.1, numpy==1.19.5  update_lib  Finished  2022-07-13T11:56:34Z               None
            >>>

            # Verify if numpy is installed with the specific version.
            >>> testenv.libs
                  library version
            0      joblib  0.14.1
            1       numpy  1.19.5
            2         pip  20.1.1
            3  setuptools  47.1.0

            # Example 3: update libraries specified in the requirements text file asynchrnously.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            numpy==1.21.6
            -----------------------------------------------------------
            >>> testenv.update_lib(libs_file_path="requirement.txt", asynchronous=True)
            Request to update libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'd3301da5-f5cb-4248-95dc-a59e77fe9db5'.

            # Verify if numpy is updated to the specific version.
            >>> testenv.libs
                  library version
            0      joblib  0.14.1
            1       numpy  1.21.6
            2         pip  20.1.1
            3  setuptools  47.1.0

            # Example 4: Downgrade the Python library joblib to 0.13.2 synchronously by specifying timeout.
            # As higher version of the package is not automatically uninstalled, we need to uninstall the higher version
            # to use the lower version.
            >>> testenv.uninstall_lib("joblib", asynchronous=True)
            Request to uninstall libraries initiated successfully in the remote user environment testenv.
            Check the status using status() with the claim id 'e32d69d9-452b-4600-be4b-1d5c60647a54'.

            >>> testenv.status('e32d69d9-452b-4600-be4b-1d5c60647a54')
                                           Claim Id File/Libs    Method Name     Stage             Timestamp Additional Details
            0  e32d69d9-452b-4600-be4b-1d5c60647a54    joblib  uninstall_lib   Started  2022-07-13T11:59:14Z               None
            1  e32d69d9-452b-4600-be4b-1d5c60647a54    joblib  uninstall_lib  Finished  2022-07-13T11:59:17Z               None
            >>>

            # Verify if joblib package is uninstalled or not.
            >>> testenv.libs
                  library version
            0         pip  20.1.1
            1  setuptools  47.1.0

            >>> testenv.update_lib(["joblib==0.13.2"], timeout=1)
            Request to update libraries initiated successfully in the remote user environment 'testenv' but unable to get the status. Check the status using status() with the claim id 'ca669e5b-bd2c-4037-ae65-e0147954b85d'.
            'ca669e5b-bd2c-4037-ae65-e0147954b85d'

            # Check the status.
            >>> testenv.status('ca669e5b-bd2c-4037-ae65-e0147954b85d')
                                           Claim Id       File/Libs Method Name     Stage             Timestamp Additional Details
            0  ca669e5b-bd2c-4037-ae65-e0147954b85d  joblib==0.13.2  update_lib   Started  2022-07-13T11:57:41Z               None
            1  ca669e5b-bd2c-4037-ae65-e0147954b85d  joblib==0.13.2  update_lib  Finished  2022-07-13T11:57:47Z               None
            >>>

            # Listing the available libraries.
            >>> testenv.libs
                  library version
            0      joblib  0.13.2
            1         pip  20.1.1
            2  setuptools  47.1.0
            >>>

            # Examples for R environment.
            # Create remote R user environment.
            >>> r_env = create_env('test_r_env', 'r_4.1', 'Test R environment')
            User environment 'test_r_env' created.
            >>>

            # Install R libraries in environment.
            >>> r_env.install_lib(['glm2', 'stringi', "plyr"])
                                             Claim Id              File/Libs     Method Name       Stage               Timestamp    Additional Details
            0    6b9c006a-35a6-4f98-ab88-7010af98c3b9    glm2, stringi, plyr     install_lib     Started    2023-09-15T17:14:12Z
            1    6b9c006a-35a6-4f98-ab88-7010af98c3b9    glm2, stringi, plyr     install_lib    Finished    2023-09-15T17:16:37Z
            >>>

            # Verify installed libraries.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            4         boot   1.3-28
            5        class   7.3-20
            6      cluster    2.1.2
            ..         ...      ...
            31        glm2    1.2.1
            32        plyr    1.8.8
            33     stringi   1.7.12
            >>>

            # Example 5: Update single R library synchronously which is not present.
            #            in environment. This installs the library with specified
            #            version.
            >>> r_env.update_lib('dplyr== 1.1.1')
                                             Claim Id        File/Libs    Method Name        Stage                Timestamp    Additional Details
            0    44d7ef77-e904-4bb9-bc6f-fd10e6294d2d    dplyr== 1.1.1     update_lib      Started     2023-09-15T17:58:23Z
            1    44d7ef77-e904-4bb9-bc6f-fd10e6294d2d    dplyr== 1.1.1     update_lib     Finished     2023-09-15T18:01:23Z
            >>>

            # Verify if library is installed with correct version.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            33       dplyr    1.1.1
            ..         ...      ...
            37        glm2    1.2.1
            ..         ...      ...
            43        plyr    1.8.8
            ..         ...      ...
            45     stringi   1.7.12
            ..         ...      ...
            50       withr    2.5.0
            >>>

            # Example 6: Downgrade multiple R libraries synchronously
            #            by passing them as a list of library names.
            >>> r_env.update_lib(['stringi== 1.1.5', 'dplyr== 1.0.8'])
                                             Claim Id                         File/Libs      Method Name       Stage                Timestamp    Additional Details
            0    0b481a55-66c5-41b3-bba6-bec553274538    stringi== 1.1.5, dplyr== 1.0.8       update_lib     Started     2023-09-15T18:11:00Z
            1    0b481a55-66c5-41b3-bba6-bec553274538    stringi== 1.1.5, dplyr== 1.0.8       update_lib    Finished     2023-09-15T18:15:11Z
            >>>

            # Verify if libraries are downgraded.
            >>> r_env.libs
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            33       dplyr    1.0.8
            ..         ...      ...
            37        glm2    1.2.1
            ..         ...      ...
            43        plyr    1.8.8
            ..         ...      ...
            45     stringi    1.1.5
            ..         ...      ...
            50       withr    2.5.0
            >>>

            # Example 7: Update libraries synchronously by specifying
            #            them in a file.

            # Create a requirement.json file with below contents.
            -----------------------------------------------------------
            {
                "cran_packages":
                    [{
                        "name": "dplyr",
                        "version": "1.1.1"
                    },
                    {
                        "name": "glm2",
                        "version": ">= 1.1.2, < 1.2"
                    }]
            }
            -----------------------------------------------------------

            # Update libraries specified in the file.
            >>> r_env.update_lib(libs_file_path="requirement.json")
                                             Claim Id           File/Libs    Method Name        Stage               Timestamp    Additional Details
            0    3399d416-8daa-49b5-a608-55e15fcbe89e    requirement.json     update_lib      Started    2023-09-15T18:23:24Z
            1    3399d416-8daa-49b5-a608-55e15fcbe89e    requirement.json     update_lib     Finished    2023-09-15T18:26:33Z
            >>>

            # Verify if libraries are updated.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            33       dplyr    1.1.1
            ..         ...      ...
            37        glm2    1.1.3
            ..        ...       ...
            43        plyr    1.8.8
            ..        ...       ...
            45     stringi    1.1.5
            ..        ...       ...
            50       withr    2.5.0
            >>>

            # Example 8: Update R libraries asynchronously.
            >>> r_env.update_lib(["plyr== 1.0.3", "glm2<= 1.1.1"], asynchronous=True)
            Request to update libraries initiated successfully in the remote user environment r2_env_spk. Check the status using status() with the claim id '81c60527-88c8-4372-9336-c3bd7793b2b1'.
            '81c60527-88c8-4372-9336-c3bd7793b2b1'
            >>>

            # Check the status using claim id.
            >>> r_env.status('81c60527-88c8-4372-9336-c3bd7793b2b1')
                                             Claim Id                     File/Libs    Method Name        Stage                Timestamp    Additional Details
            0    81c60527-88c8-4372-9336-c3bd7793b2b1    plyr== 1.0.3, glm2== 1.1.1     update_lib      Started     2023-09-15T18:35:02Z
            1    81c60527-88c8-4372-9336-c3bd7793b2b1    plyr== 1.0.3, glm2== 1.1.1     update_lib     Finished     2023-09-15T18:35:19Z
            >>>

            # Verify if libraries are updated.
            >>> r_env.libs
                      name  version
            0   KernSmooth  2.23-20
            1         MASS   7.3-55
            2       Matrix    1.4-0
            3         base    4.1.3
            ..         ...      ...
            33       dplyr    1.1.1
            ..         ...      ...
            37        glm2    1.1.1
            ..         ...      ...
            43        plyr    1.0.3
            ..         ...      ...
            45     stringi    1.1.5
            ..         ...      ...
            50       withr    2.5.0

            # Example 9: Update Conda R libraries.
            # Create remote R conda user environment.
            >>> r_env = create_env('test_r_env', 'r_4.3', 'Test R environment', conda_env=True)
            Conda environment creation initiated
            User environment 'test_r_env' created.

            # Install R libraries in environment.
            # Create a requirement.txt file with below contents.
            -----------------------------------------------------------
            r-glm2
            r-anytime
            r-ggplot2
            -----------------------------------------------------------

            >>> r_env.install_lib(libs_file_path="requirement.txt")
                Claim Id                                File/Libs/Model Method Name Stage       Timestamp            Additional Details
            0	10afb2ae-8517-4858-8cf9-82bc54abd7ed    requirement.txt install_lib Started     2024-12-17T07:17:26Z	
            1	10afb2ae-8517-4858-8cf9-82bc54abd7ed    requirement.txt install_lib Finished    2024-12-17T07:21:06Z	

            # update the libraries in the environment through libs
            >>> r_env.update_lib(libs=["r-glm2", "r-anytime"])
                Claim Id                                File/Libs/Model  Method Name  Stage     Timestamp            Additional Details
            0	7106cb78-2dcf-4638-ab91-500fe8144787    libs.txt         update_lib   Started   2024-12-17T07:23:57Z	
            1	7106cb78-2dcf-4638-ab91-500fe8144787    libs.txt         update_lib   Finished  2024-12-17T07:24:11Z	

            # update the libraries in the environment through libs_file_path
            >>> r_env.update_lib(libs_file_path="requirement.txt")
                Claim Id                                File/Libs/Model Method Name Stage       Timestamp            Additional Details
            0	6d6a3b3d-7b9d-4b0b-8f7f-1d1c7b4b3b5a    requirement.txt update_lib  Started     2024-12-17T07:25:35Z
            1	6d6a3b3d-7b9d-4b0b-8f7f-1d1c7b4b3b5a    requirement.txt update_lib  Finished	2024-12-17T07:25:49Z

            # Verify if libraries are updated.
            >>> r_env.libs
                        name	version
            0	_libgcc_mutex	0.1
            1	_openmp_mutex	5.1
            2	     _r-mutex   1.0.0
            ...	      ...	    ...
            103	       tzdata	2024b
            104	        wheel   0.44.0
            105	           xz   5.4.6
            106	         zlib   1.2.13
            107	         zstd   1.5.6
        """
        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout")
        async_task_info = self.__manage_libraries(libs, libs_file_path, "UPDATE", asynchronous, timeout)
        return async_task_info

    @collect_queryband(queryband="EnvRfrsh")
    def refresh(self):
        """
        DESCRIPTION:
            Function refreshes the UserEnv properties 'files' and 'libs'.
            'files' and 'libs' properties cache user environment file and library
            information respectively when invoked. This information is refreshed
            when user invokes any of the following methods of 'UserEnv' class:
                * install_lib
                * uninstall_lib
                * update_lib
                * install_file
                * remove_file
                * refresh

            This method should be used when user environment is updated outside
            of teradataml or cache is not updated after user environment updates.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            NOne

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('test_env', 'python_3.7.9', 'Test environment')
            User environment 'test_env' created.

            # Example 1: Install the libs in the 'test_env' environment.
            # View existing libraries installed.
            >>> env.libs
                     name version
            0         pip  22.0.4
            1  setuptools  47.1.0

            # Install additional Python library using UserEnv method.
            >>> env.install_lib("joblib")
                                           Claim Id File/Libs  Method Name     Stage             Timestamp Additional Details
            0  263c4600-9b68-4cae-b601-270936cb965a    joblib  install_lib   Started  2023-09-22T10:47:09Z
            1  263c4600-9b68-4cae-b601-270936cb965a    joblib  install_lib  Finished  2023-09-22T10:47:15Z

            # View installed libraries.
            >>> env.libs
                     name version
            0      joblib   1.3.2
            1         pip  22.0.4
            2  setuptools  47.1.0

            # Install additional 'numpy' Python library from outside, i.e. without using the UserEnv methods.

            # View installed libraries. Note that 'numpy' library is not visible as "libs" cache is not updated.
            # To refresh cache execute the 'refresh()' method.
            >>> env.libs
                     name version
            0      joblib   1.3.2
            1         pip  22.0.4
            2  setuptools  47.1.0

            # Refresh the 'libs' and 'files' in the environment.
            >>> env.refresh()

            # View refreshed libraries.
            >>> env.libs
                     name version
            0      joblib   1.3.2
            1       numpy  1.21.6
            2         pip  22.0.4
            3  setuptools  47.1.0

            # Example 2: Install the files in the 'test_env' environment.
            # View existing files.
            >>> env.files
            No files found in remote user environment test_env.

            # Install the file mapper.py in the 'test_env' environment using UserEnv method.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path)
            File 'mapper.py' installed successfully in the remote user environment 'test_env'.
            True

            # View installed files.
            >>> env.files
                    File  Size             Timestamp
            0  mapper.py   532  2023-09-22T11:28:02Z

            # Install 'mapper_replace.py' file from outside, i.e. without using the UserEnv methods.

            # View installed files. Note that recently installed file using REST call
            # is not visible as "files" cache is not updated. To refresh cache execute the 'refresh()' method.
            >>> env.files
                    File  Size             Timestamp
            0  mapper.py   532  2023-09-22T11:28:02Z

            # Refresh the 'libs' and 'files' in the environment.
            >>> env.refresh()

            # View refreshed files.
            >>> env.files
                            File  Size             Timestamp
            0          mapper.py   532  2023-09-22T11:28:02Z
            1  mapper_replace.py   537  2023-09-22T11:30:11Z

            # Create a remote R user environment.
            >>> env = create_env('r_test_env', 'r_4.1', 'R Test environment')
            User environment 'test_env' created.

            # Example 1: Install the libs in the R environment 'r_test_env'.
            # View existing libraries installed.
            >>> env.libs
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

            # Install additional R library using UserEnv method.
            >>> env.install_lib("glm2")
                                           Claim Id File/Libs  Method Name     Stage             Timestamp Additional Details
            0  8eceab10-cc12-4889-b17e-8bed3757a123      glm2  install_lib   Started  2023-09-22T11:38:27Z
            1  8eceab10-cc12-4889-b17e-8bed3757a123      glm2  install_lib  Finished  2023-09-22T11:38:33Z

            # View installed libraries.
            >>> env.libs
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
            30        glm2    1.2.1

            # Install additional 'anytime' and 'stringi' R libraries from outside, i.e. without using the UserEnv methods.

            # View installed libraries. Note that 'anytime' and 'stringi' libraries are not visible as "libs" cache is not updated.
            # To refresh cache execute the 'refresh()' method.
            >>> env.libs
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
            30        glm2    1.2.1

            # Refresh the 'libs' and 'files' in the environment.
            >>> env.refresh()

            # View refreshed libraries.
            >>> env.libs
                      name   version
            0   KernSmooth   2.23-20
            1         MASS    7.3-55
            2       Matrix     1.4-0
            3         base     4.1.3
            4         boot    1.3-28
            5        class    7.3-20
            6      cluster     2.1.2
            7    codetools    0.2-18
            8     compiler     4.1.3
            9     datasets     4.1.3
            10     foreign    0.8-82
            11   grDevices     4.1.3
            12    graphics     4.1.3
            13        grid     4.1.3
            14     lattice   0.20-45
            15     methods     4.1.3
            16        mgcv    1.8-39
            17        nlme   3.1-155
            18        nnet    7.3-17
            19    parallel     4.1.3
            20     remotes     2.4.2
            21       rpart    4.1.16
            22     spatial    7.3-15
            23     splines     4.1.3
            24       stats     4.1.3
            25      stats4     4.1.3
            26    survival    3.2-13
            27       tcltk     4.1.3
            28       tools     4.1.3
            29       utils     4.1.3
            30          BH  1.81.0-1
            31        Rcpp    1.0.11
            32     anytime     0.3.9
            33        glm2     1.2.1
            34     stringi    1.7.12

            # Example 2: Install the files in the R environment 'r_test_env'.
            # View existing files.
            >>> env.files
            No files found in remote user environment r_test_env.

            # Install the file temp_file.R in the 'r_test_env' environment using UserEnv method.
            >>> file_path = "temp_file.R"
            >>> with open(file_path, "w") as fp:
            ...     fp.write("print('HelloWorld')")
            >>> env.install_file(file_path = file_path)
            File 'temp_file.R' installed successfully in the remote user environment 'r_test_env'.
            True

            # View installed files.
            >>> env.files
                      File  Size             Timestamp
            0  temp_file.R    19  2023-09-25T04:54:44Z

            # Install 'temp_file_1.R' file from outside, i.e. without using the UserEnv methods.

            # View installed files. Note that recently installed file using REST call
            # is not visible as "files" cache is not updated. To refresh cache execute the 'refresh()' method.
            >>> env.files
                      File  Size             Timestamp
            0  temp_file.R    19  2023-09-25T04:54:44Z

            # Refresh the 'libs' and 'files' in the environment.
            >>> env.refresh()

            # View refreshed files.
            >>> env.files
                        File  Size             Timestamp
            0  temp_file_1.R    20   2023-09-25T05:01:11Z
            1    temp_file.R    19   2023-09-25T04:54:44Z
        """
        # Set self.__libs_changed, self.__files_changed and self.__models_changed flags to True.
        self.__libs_changed = True
        self.__files_changed = True
        self.__models_changed = True

    @collect_queryband(queryband="EnvSts")
    def status(self, claim_ids=None):
        """
        DESCRIPTION:
            Function to check the status of the operations performed by the library/file
            management methods of UserEnv. Status of the following operations can be checked:
              * File installation, when installed asynchronously. Applicable for the files
                with size greater than 10 MB.
              * Install/Uninstall/Update of the libraries in user environment.

        PARAMETERS:
            claim_ids:
                Optional Argument.
                Specifies the unique identifier(s) of the asynchronous process
                started by the UserEnv management methods.
                If user do not pass claim_ids, then function gets the status
                of all the asynchronus process'es in the current session.
                Types: str OR list of Strings (str)

        RETURNS:
            Pandas DataFrame.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env = create_env('test_env', 'python_3.7.9', 'Test environment')
            User environment test_env created.

            # Example 1: Install the file 'large_file' asynchronously with 'large_file' found in
                         temp folder and check the latest status of installation.
            # Note:
            #     Running this example creates a file 'large_file' with size
            #     approximately 41MB in the temp folder.
            >>> import tempfile, os
            >>> def create_large_file():
            ...     file_name = os.path.join(tempfile.gettempdir(),"large_file")
            ...     with open(file_name, 'xb') as fp:
            ...         fp.seek((1024 * 1024 * 41) - 1)
            ...         fp.write(b'\0')
            ...
            >>> claim_id = env.install_file('large_file')
                File installation is initiated. Check the status using status() with the claim id 53e44892-1952-45eb-b828-6635c0447b59.
            >>> env.status(claim_id)
                                           Claim Id                                                       File/Libs   Method Name               Stage             Timestamp Additional Details
            0  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz  install_file  Endpoint Generated  2022-07-27T18:20:34Z               None
            1  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz  install_file       File Uploaded  2022-07-27T18:20:35Z               None
            2  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz  install_file      File Installed  2022-07-27T18:20:38Z               None
            >>>

            # Example 2: Install the library 'teradataml' asynchronously and check the status of installation.
            >>> claim_id = env.install_lib('teradataml')
                Request to install libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '349615e2-9257-4a70-8304-ac76f50712f8'.
            >>> env.status(claim_id)
                                           Claim Id   File/Libs  Method Name     Stage             Timestamp Additional Details
            0  349615e2-9257-4a70-8304-ac76f50712f8  teradataml  install_lib   Started  2022-07-13T10:37:40Z               None
            1  349615e2-9257-4a70-8304-ac76f50712f8  teradataml  install_lib  Finished  2022-07-13T10:39:29Z               None
            >>>

            # Example 3: update the library 'teradataml' to 17.10.0.0 asynchronously and check the status of installation.
            >>> claim_id = env.update_lib('teradataml==17.10.0.0')
            Request to update libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '29d06296-7444-4851-adef-ca1f921b1dd6'.
            >>> env.status(claim_id)
                                           Claim Id              File/Libs Method Name     Stage             Timestamp Additional Details
            0  29d06296-7444-4851-adef-ca1f921b1dd6  teradataml==17.10.0.0  update_lib   Started  2022-07-13T10:47:39Z               None
            1  29d06296-7444-4851-adef-ca1f921b1dd6  teradataml==17.10.0.0  update_lib  Finished  2022-07-13T10:49:52Z               None
            >>>

            # Example 4: uninstall the library 'teradataml' and check the complete status of all the asynchronous process'es.
            >>> claim_id = env.uninstall_lib('teradataml')
            Request to uninstall libraries initiated successfully in the remote user environment test_env. Check the status using status() with the claim id '5cd3b3f7-f3b8-4bfd-8abe-7c811a6728db'.
            >>> env.status()
                                           Claim Id                                                       File/Libs    Method Name               Stage             Timestamp Additional Details
            0  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz   install_file  Endpoint Generated  2022-07-27T18:20:34Z               None
            1  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz   install_file       File Uploaded  2022-07-27T18:20:35Z               None
            2  53e44892-1952-45eb-b828-6635c0447b59  TeradataToolsAndUtilitiesBase__ubuntu_x8664.17.10.19.00.tar.gz   install_file      File Installed  2022-07-27T18:20:38Z               None
            3  29d06296-7444-4851-adef-ca1f921b1dd6                                           teradataml==17.10.0.0     update_lib             Started  2022-07-13T10:47:39Z               None
            4  29d06296-7444-4851-adef-ca1f921b1dd6                                           teradataml==17.10.0.0     update_lib            Finished  2022-07-13T10:49:52Z               None
            5  349615e2-9257-4a70-8304-ac76f50712f8                                           teradataml               install_lib             Started  2022-07-13T10:37:40Z               None
            6  349615e2-9257-4a70-8304-ac76f50712f8                                           teradataml               install_lib            Finished  2022-07-13T10:39:29Z               None
            7  5cd3b3f7-f3b8-4bfd-8abe-7c811a6728db                                           teradataml             uninstall_lib             Started  2022-07-13T10:37:40Z               None
            8  5cd3b3f7-f3b8-4bfd-8abe-7c811a6728db                                           teradataml             uninstall_lib            Finished  2022-07-13T10:39:29Z               None

        """
        __arg_info_matrix = []
        __arg_info_matrix.append(["claim_ids", claim_ids, True, (list, str), True])

        # Validate arguments
        _Validators._validate_function_arguments(__arg_info_matrix)

        # Raise error if user is not connected to Vantage.
        if _get_user() is None:
            error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                             "status",
                                             "Create context before using {}.".format("status"))
            raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)

        # If user do not pass any claim_ids, get the status for all the claim-ids
        # created in the current session.
        if claim_ids is None:

            # If there are no claim_ids in the current session, print a message and return.
            if not self.__claim_ids:
                print("No file/library management operations found.")
                return

            # Get all the claim_ids.
            claim_ids = self.__claim_ids.keys()
        else:
            # If user pass a single claim_id as string, convert to list.
            claim_ids = UtilFuncs._as_list(claim_ids)

        return pd.DataFrame.from_records(self.__process_claim_ids(claim_ids=claim_ids), columns=self.__status_columns)

    def __process_claim_ids(self, claim_ids):
        """
        DESCRIPTION:
            Function processes the claim IDs of asynchronous process using
            their 'claim_ids' parallelly to get the status.

        PARAMETERS:
            claim_ids:
                Required Argument.
                Specifies the unique identifier(s) of the asynchronous process
                started by the UserEnv management methods.
                Types: str OR list of Strings (str)

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__process_claim_ids(['123-456-789', 'abc-xyz'])
        """
        # Create thread pool executor to get the status parallelly.
        executor = ThreadPoolExecutor(max_workers=10)

        # executor.submit returns a future object. Store all the futures in a list.
        futures = [executor.submit(self.__get_claim_id_status, claim_id) for claim_id in claim_ids]

        # Wait forever, till all the futures complete.
        wait(futures)

        # Add all the results to a list.
        return functools.reduce(lambda x, y: x + y, (future.result() for future in futures))

    def __get_claim_id_status(self, claim_id):
        """
        DESCRIPTION:
            Function to get the status of asynchronus process using the claim_id.

        PARAMETERS:
            claim_id:
                Required Argument.
                Specifies the unique identifier of the asynchronous process
                started by the UserEnv management methods.
                Types: str

        RETURNS:
            Pandas DataFrame.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__get_claim_id_status('123-456')
        """
        # Get the claim_id details.
        claim_id_details = {"Claim Id": claim_id,
                            "Method Name": self.__claim_ids.get(claim_id, {}).get("action", "Unknown"),
                            "File/Libs/Model": self.__claim_ids.get(claim_id, {}).get("value", "Unknown")}

        try:
            # TODO: _get_status() from teradataml.scriptmgmt.lls_utils does similar job.
            #  _get_status() can be reused.
            response = UtilFuncs._http_request(_get_ues_url(env_type="fm",
                                                            claim_id=claim_id,
                                                            api_name="status"),
                                               headers=_get_auth_token())
            data = _process_ues_response(api_name="status", response=response).json()
            # if claim_id is for install_file - 'data' looks as below:
            #      [
            #         {'timestamp': '2022-06-29T17:03:49Z', 'stage': 'Endpoint Generated'},
            #         {'timestamp': '2022-06-29T17:03:50Z', 'stage': 'File Uploaded'},
            #         {'timestamp': '2022-06-29T17:03:52Z', 'stage': 'File Installed'}
            #      ]

            # if claim_id is for install_lib/uninstall_lib/update_lib - 'data' looks as below:
            #     [
            #         {
            #             "timestamp": "2022-07-07T09:43:04Z",
            #             "stage": "Started"
            #         },
            #         {
            #             "timestamp": "2022-07-07T09:43:06Z",
            #             "stage": "Finished",
            #             "details": "WARNING: Skipping numpysts as it is not installed."
            #                        "WARNING: Skipping pytest as it is not installed."
            #         }
            #      ]

            # Create a lamda function to extract the data.
            get_details = lambda data: {"Additional Details": data.pop("details", None),
                                        "Stage": data.pop("stage", None),
                                        "Timestamp": data.pop("timestamp", None),
                                        **claim_id_details}

            return [get_details(sub_step) for sub_step in data]

        except Exception as e:
            # For any errors, construct a row with error reason in 'additional_details' column.
            record = {"Additional Details": str(e), "Timestamp": None, "Stage": AsyncOpStatus.ERRED.value}
            record.update(claim_id_details)
            return [record]

    def __get_claim_status(self, claim_id, timeout, action, **kwargs):
        """
        DESCRIPTION:
            Function to get the status of asynchronus process using the claim_id.
            The function polls the status of asynchronous process using the 'status' API
            for 'timeout' seconds and gets the status of it. When asynchronus process
            is not completed in 'timeout' seconds, the function stops polling the status
            API and returns the claim-id.

        PARAMETERS:
            claim_id:
                Required Argument.
                Specifies the unique identifier of the asynchronous process
                started by the UserEnv management methods.
                Types: str

            timeout:
                Required Argument.
                Specifies the maximum time in seconds to poll the status.
                Types: int OR float

            action:
                Required Argument.
                Specifies the action for asynchronous process.
                Types: str

            kwargs:
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Default Value: False
                    Types: bool

        RETURNS:
            Pandas DataFrame OR claim id.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__get_claim_status('123-456', 5, 'install_file')
        """
        # If user specifies 'timeout', poll only for 'timeout' seconds. Otherwise,
        # poll status API indefinitely.
        timeout = UtilFuncs._get_positive_infinity() if timeout is None else timeout
        suppress_output = kwargs.get("suppress_output", False)
        start_time = time.time()
        while time.time() - start_time <= timeout:
            time.sleep(3)
            records = self.__is_async_operation_completed(claim_id, suppress_output=suppress_output)
            if records:
                return pd.DataFrame.from_records(records, columns=self.__status_columns)

        # Unable to get the response with in 'timeout' seconds. Print a message and
        # return claim id.
        if not suppress_output:
            print("Request to {} initiated successfully in the remote user environment '{}' "
                  "but Timed out status check. Check the status using status() with the "
                  "claim id '{}'.".format(action, self.env_name, claim_id))
        return claim_id

    def __is_async_operation_completed(self, claim_id, **kwargs):
        """
        DESCRIPTION:
            Function to check whether asynchronous process to install/update/uninstall libraries/file
            has completed or not.

        PARAMETERS:
            claim_id:
                Required Argument.
                Specifies the unique identifier of the asynchronous process
                started by the UserEnv management methods.
                Types: str

            kwargs:
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Default Value: False
                    Types: bool

        RETURNS:
            list OR bool.

        RAISES:
            None

        EXAMPLES:
            # Create a remote user environment.
            >>> env.__is_async_operation_completed('123-456')
        """
        suppress_output = kwargs.get("suppress_output", False)
        records = self.__get_claim_id_status(claim_id)

        # For library installation/uninstallation/updation, if the background process in
        # UES completes, it always returns two records. However, for file, this may not
        # be the case. So, validating both separately.
        action = self.__claim_ids.get(claim_id, {}).get("action")
        if action in ["install_file", "install_model"]:
            for record in records:
                if record["Stage"] in [AsyncOpStatus.FILE_INSTALLED.value,
                                       AsyncOpStatus.ERRED.value,
                                       AsyncOpStatus.MODEL_INSTALLED.value]:
                    if record["Stage"] in [AsyncOpStatus.FILE_INSTALLED.value,
                                           AsyncOpStatus.MODEL_INSTALLED.value]:
                        if not suppress_output:
                            print("Request for {} is {}.".format(action, "completed successfully"))
                    elif record["Stage"] == AsyncOpStatus.ERRED.value:
                        if not suppress_output:
                            print("Request for {} is {}.".format(action, AsyncOpStatus.ERRED.value))
                            print("Check the status using status() with the claim id '{}'".format(claim_id))
                    return records
            return False

        # For library installation/uninstallation/updation.
        return records if len(records) == 2 else False

    @collect_queryband(queryband="InstlMdl")
    def install_model(self, model_path=None, model_name=None, model_type=None, api_key=None, **kwargs):
        """
        DESCRIPTION:
            Function installs a model into the remote user environment created
            in Vantage Languages Ecosystem. Model can be installed from a zip file
            containing all the files related to the model or from a model registry
            like Hugging Face. If model with same name already exists in the remote
            user environment, error is thrown.
            Note:
                Maximum size of the model should be less than or equal to 5GB when
                installing using zip.

        PARAMETERS:
            model_path:
                Optional Argument.
                Specifies absolute or relative path of the zip file containing
                model (including file name) to be installed in the remote user
                environment.
                Notes:
                    * Model file should be in zip format.
                    * Arguments "model_path" and "model_name" are mutually exclusive.
                Types: str

            model_name:
                Optional Argument.
                Specifies the name/identifier of the model in the registry (e.g. "google-t5/t5-small"
                from Hugging Face registry).
                Note:
                    * Arguments "model_name" and "model_path" are mutually exclusive.
                Types: str

            model_type:
                Optional Argument.
                Specifies the name of model registry like Hugging Face.
                Note:
                    * Applicable when model is installed from a model registry.
                Default Value: "HF" (Hugging Face registry)
                Permitted Values: "HF"
                Types: str

            api_key:
                Optional Argument.
                Specifies the API key for accessing the private models in registry.
                Note:
                    Applicable only when model is installed from a model registry.
                Types: str

        **kwargs:
            Specifies the keyword arguments.
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Default Value: False
                    Types: bool

                asynchronous:
                    Optional Argument.
                    Specifies whether to install the model in remote user environment
                    synchronously or asynchronously. When set to True, model is installed
                    asynchronously. Otherwise, model is installed synchronously.
                    Default Value: False
                    Types: bool

                timeout:
                    Optional Argument.
                    Specifies the time to wait in seconds for installing the model.
                    If the model is not installed with in "timeout" seconds, the
                    function returns a claim-id and one can check the status using
                    the claim-id. If "timeout" is not specified, then there is no
                    limit on the wait time.
                    Note:
                         Argument is ignored when "asynchronous" is True.
                    Types: int OR float

        RETURNS:
            Pandas DataFrame when model is installed synchronously and installation
            is completed before timeout.
            claim_id, to track status, when model is getting installed asynchronously
            or installation times out in synchronous execution mode.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create remote user environment.
            >>> env = create_env('testenv', 'python_3.9.13', 'Test environment')
            User environment 'testenv' created.

            # User should create a zip file containing all files related to model
            # and use path to that zip file to install model using install_model()
            # API. Let's assume that all models files are zipped under 'large_model.zip'
            >>> model = 'large_model.zip'

            # Example 1: Install the model in the 'testenv' environment.
            >>> env.install_model(model_path = model)
            Request for install_model is completed successfully.
                                           Claim Id  File/Libs/Model    Method Name               Stage             Timestamp  Additional Details
            0  3fe99ef5-cc5b-41c6-92a4-595d60ecfbb5  large_model.zip  install_model  Endpoint Generated  2023-10-30T12:04:40Z
            1  3fe99ef5-cc5b-41c6-92a4-595d60ecfbb5  large_model.zip  install_model       File Uploaded  2023-10-30T12:05:37Z
            2  3fe99ef5-cc5b-41c6-92a4-595d60ecfbb5  large_model.zip  install_model      File Installed  2023-10-30T12:05:39Z

            # Verify the model installation.
            >>> env.models
                     Model  Size             Timestamp
            0  large_model  6144  2023-10-30T13:11:00Z

            # Example 2: Install the model asynchronously and check the
            #            status of installation.
            >>> claim_id = env.install_model(model_path = model, asynchronous=True)
            Model installation is initiated. Check the status using status() with the claim id 7e840c47-3d70-4a11-a079-698203603854.
            >>> env.status(claim_id)
                                           Claim Id  File/Libs/Model    Method Name               Stage             Timestamp Additional Details
            0  7e840c47-3d70-4a11-a079-698203603854  large_model.zip  install_model  Endpoint Generated  2023-10-30T13:32:52Z
            1  7e840c47-3d70-4a11-a079-698203603854  large_model.zip  install_model       File Uploaded  2023-10-30T13:34:02Z
            2  7e840c47-3d70-4a11-a079-698203603854  large_model.zip  install_model      File Installed  2023-10-30T13:34:03Z

            # Verify the model installation.
            >>> env.models
                     Model  Size             Timestamp
            0  large_model  6144  2023-10-30T13:34:03Z

            # Example 3: Install the model from default registry 'Hugging Face'
            #            in the 'testenv' environment synchronously.
            >>> env.install_model(model_name="google-bert/bert-base-uncased")
            Request for install_model is completed successfully.
            Model 'google-bert/bert-base-uncased' installed successfully in the remote user environment 'testenv'.

            # Verify the model installation.
            >>> env.models
                                                  Model       Size                  Timestamp
            0    models--google-bert--bert-base-uncased       6144       2025-07-30T03:58:01Z

            # Example 4: Install the model from default registry 'Hugging Face'
            #            in the 'testenv' environment asynchronously.
            >>> claim_id = env.install_model(model_name="Helsinki-NLP/opus-mt-en-fr", asynchronous=True)
            Model installation is initiated. Check the status using <UserEnv_obj>.status() with the claim id 'ac284706-0b72-4b83-8add-3cff632747f4'.

            # Check status using claim-id.
            >>> env.status(claim_id)
                                             Claim Id    File/Libs/Model                 Method Name    Stage                         Timestamp      Additional Details
            0    ac284706-0b72-4b83-8add-3cff632747f4    Helsinki-NLP/opus-mt-en-fr    install_model    Started            2025-07-30T03:58:09Z    Begin downloading model named Helsinki-NLP/opu...
            1    ac284706-0b72-4b83-8add-3cff632747f4    Helsinki-NLP/opus-mt-en-fr    install_model    ModelInstalled     2025-07-30T03:58:28Z    Model installed successfully

            # Verify the model installation.
            >>> env.models
                                                  Model    Size               Timestamp
            0       models--Helsinki-NLP--opus-mt-en-fr    6144    2025-07-30T03:58:27Z
            1    models--google-bert--bert-base-uncased    6144    2025-07-30T03:58:01Z
        """
        # Get default values for optional keyword arguments.
        suppress_output = kwargs.get("suppress_output", False)
        asynchronous = kwargs.get("asynchronous", False)
        timeout = kwargs.get("timeout", None)

        # Get default value for optional positional argument.
        model_type = model_type if model_type is not None else "HF"

        # Argument validation.
        __arg_info_matrix = []
        __arg_info_matrix.append(["model_path", model_path, True, (str), True])
        __arg_info_matrix.append(["model_name", model_name, True, (str), True])
        __arg_info_matrix.append(["model_type", model_type, True, (str), True, ["HF"]])
        __arg_info_matrix.append(["api_key", api_key, True, (str), True])
        __arg_info_matrix.append(["suppress_output", suppress_output, True, (bool)])
        __arg_info_matrix.append(["asynchronous", asynchronous, True, (bool)])
        __arg_info_matrix.append(["timeout", timeout, True, (int, float)])

        _Validators._validate_function_arguments(__arg_info_matrix)

        # Validate mutually exclusive arguments.
        _Validators._validate_mutually_exclusive_argument_groups({"model_name": model_name},
                                                                 {"model_path": model_path},
                                                                 all_falsy_check=True)

        # Install model from zip file.
        if model_path:
            kwargs["is_model"] = True
            if not "is_llm" in kwargs:
                kwargs["is_llm"] = True
            records = self.install_file(model_path, **kwargs)
            return records

        # Install models from registry.
        api_name = "install_model"
        try:
            # Prepare the payload
            payload = {
                "model_name": model_name,
                "model_type": model_type
            }

            if api_key is not None:
                payload["api_key"] = api_key

            # Make the REST call to install model from registry
            resource_url = _get_ues_url(env_name=self.env_name, api_name=api_name, models=True)
            response = UtilFuncs._http_request(resource_url,
                                               HTTPRequest.POST,
                                               headers=_get_auth_token(),
                                               json=payload)

            data = _process_ues_response(api_name, response).json()

            # Get claim-id model install async operation from response.
            claim_id = data["claim_id"]

            # Store the claim id locally to display the model name in status API.
            self.__claim_ids[claim_id] = {"action": api_name, "value": model_name}
            installation_status = "is initiated"

            # In case of synchronous mode, keep polling the status
            # of underlying asynchronous operation until it is either
            # successful or errored or timed out.
            if not asynchronous:
                installation_status =  self.__get_claim_status(claim_id=claim_id,
                                                               timeout=timeout,
                                                               action=api_name,
                                                               suppress_output=True)
                self.__models_changed = True
                # If model installation is complete(either success or fail),
                # pandas DF will be returned.
                if isinstance(installation_status, pd.DataFrame):
                    # Model installation successful.
                    if AsyncOpStatus.MODEL_INSTALLED.value in installation_status[AsyncOpStatusOAFColumns.STAGE.value].to_list():
                        # Update the models changed flag
                        self.__models_changed = True
                        if not suppress_output:
                            print("Model '{}' installed successfully in the remote user environment '{}'.".format(
                                model_name, self.env_name))
                        return True
                    # Model installation erred out.
                    if AsyncOpStatus.ERRED.value in installation_status[AsyncOpStatusOAFColumns.STAGE.value].to_list():
                        err = ""
                        for record in installation_status.to_dict("records"):
                            if record["Stage"] == AsyncOpStatus.ERRED.value:
                                err = record[AsyncOpStatusOAFColumns.ADDITIONAL_DETAILS.value]
                        msg_code = MessageCodes.FUNC_EXECUTION_FAILED
                        error_msg = Messages.get_message(msg_code, api_name, "Check the details using <UserEnv_obj>.status() with the claim id '{}'".format(claim_id) + "\nAdditional details: {}".format(err))
                        raise TeradataMlException(error_msg, msg_code)

                # Underlying asynchronous operation timed out, claim_id is returned.
                else:
                    if not suppress_output:
                        print("Request to install_model initiated successfully in the remote user environment '{}' "
                              "but it is timed out. Check the status using <UserEnv_obj>.status() with the "
                              "claim id '{}'.".format(self.env_name, claim_id))
                    return claim_id

            if not suppress_output:
                # Print a message to user console.
                print("Model installation {}. Check the status"
                      " using <UserEnv_obj>.status() with the claim id '{}'.".format(installation_status, claim_id))
            self.__models_changed = True
            return claim_id

        except (TeradataMlException, RuntimeError):
            raise
        except Exception as emsg:
            msg_code = MessageCodes.FUNC_EXECUTION_FAILED
            error_msg = Messages.get_message(msg_code, api_name, str(emsg))
            raise TeradataMlException(error_msg, msg_code)


    @collect_queryband(queryband="UninstlMdl")
    def uninstall_model(self, model_name, **kwargs):
        """
        DESCRIPTION:
            Function uninstalls the specified model from the
            user environment.

        PARAMETERS:
            model_name:
                Required Argument.
                Specifies the name of the model to be uninstalled.
                Types: str

        **kwargs:
            Specifies the keyword arguments.
                suppress_output:
                    Optional Argument.
                    Specifies whether to print the output message or not.
                    When set to True, then the output message is not printed.
                    Types: bool

        RETURNS:
            True, if the operation is successful.

        RAISES:
            TeradataMlException, RuntimeError

        EXAMPLES:
            # Create a Python_3.8.13 environment with given name and description in Vantage.
            >>> env = create_env("test_env", "python_3.8.13", "Test environment")
            User environment 'test_env' created.

            # User should create a zip file containing all files related to model
            # and use path to that zip file to install model using install_model()
            # API. Let's assume that all models files are zipped under 'large_model.zip'
            >>> model = 'large_model.zip'

            # Install the model in the 'test_env' environment using local zip file.
            >>> env.install_model(model_path = model)
            Request for install_model is completed successfully.
                                           Claim Id  File/Libs/Model    Method Name               Stage             Timestamp  Additional Details
            0  766423af-7cc4-46db-8ee2-b6b5ded299c6  large_model.zip  install_model  Endpoint Generated  2023-11-09T09:21:24Z
            1  766423af-7cc4-46db-8ee2-b6b5ded299c6  large_model.zip  install_model       File Uploaded  2023-11-09T09:22:28Z
            2  766423af-7cc4-46db-8ee2-b6b5ded299c6  large_model.zip  install_model      File Installed  2023-11-09T09:22:30Z

            # List models.
            >>> env.models
                     Model  Size             Timestamp
            0  large_model  6144  2023-11-09T09:22:30Z

            # Install model from Hugging Face registry.
            >>> env.install_model(model_name="google-bert/bert-base-uncased")
            Request for install_model is completed successfully.
            Model 'google-bert/bert-base-uncased' installed successfully in the remote user environment 'test_env'.
            # List models.
            >>> env.models
                                                  Model     Size               Timestamp
            0                               large_model     6144    2023-11-09T09:22:30Z
            1    models--google-bert--bert-base-uncased     6144    2025-07-30T03:58:01Z

            # Example 1: Uninstall model from remote user environment.
            >>> env.uninstall_model('large_model')
            Model 'large_model' uninstalled successfully from the remote user environment 'test_env'.
            True

             # Verify the uninstallation of model.
                                                  Model    Size               Timestamp
            0    models--google-bert--bert-base-uncased    6144    2025-07-30T03:58:01Z

            # Example 2: Uninstall Hugging Face model from remote user environment.
            >>> env.uninstall_model('models--google-bert--bert-base-uncased')
            Model 'models--google-bert--bert-base-uncased' uninstalled successfully from the remote user environment 'test_env'.
            True

            # Verify the uninstallation of model.
            >>> env.models
            No models found in remote user environment test_env.

        """
        # Uninstall model from User environment.
        kwargs["is_model"] = True
        return self.remove_file(model_name, **kwargs)

    @collect_queryband(queryband="EnvSnpsht")
    def snapshot(self, dir=None):
        """
        DESCRIPTION:
            Take the snapshot of the user environment.
            Function stores the snapshot of the user environment in a
            JSON file, which can be used as input to re-create the exact
            same user environment by passing the snapshot file to create_env().

        PARAMETERS:
            dir:
                Optional Argument.
                Specifies the directory path to store the snapshot file.
                Note:
                    * when "dir" is not provided, function creates temporary folder
                      and store the snapshot files in the temp folder.
                    * While taking the snapshot, if file is installed in the enviornment,
                      to re-create the exact same user environment user has to provide
                      the absolute path of file to be installed in the generated snapshot
                      file by replacing <ADD_YOUR_LOCAL_FILE_PATH>.

                Types: str

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create a Python environment with name"env_1" in the Vantage.
            >>> env = create_env("env_1")
            ... User environment 'env_1' created.

            # Install the file mapper.py in the 'testenv' environment.
            >>> import os, teradataml
            >>> file_path = os.path.join(os.path.dirname(teradataml.__file__), "data", "scripts", "mapper.py")
            >>> env.install_file(file_path = file_path)
            File 'mapper.py' installed successfully in the remote user environment 'env_1'.
            True

            # Install 'numpy' Python library.
            >>> env.install_lib('numpy')
                                           Claim Id  ... Additional Details
            0  fa72b8ec-429e-4a63-a6d1-598869a57bc3  ...
            1  fa72b8ec-429e-4a63-a6d1-598869a57bc3  ...

            # Take a snapshot of 'env_1'.
            >>> env.snapshot()
            Snapshot for environment "env_1" is stored at "...:\\...\\...\\snapshot_env_1_python_3.10.5_1700740261.2757893.json"
        """

        __arg_info_matrix = []
        __arg_info_matrix.append(["dir", dir, True, (str), True])

        # Validate argument.
        _Validators._validate_function_arguments(__arg_info_matrix)

        if dir is not None:
            if not os.path.exists(dir):
                err_msg = "The directory path '{}' does not exist.".format(
                    dir)
                raise TeradataMlException(err_msg, MessageCodes.INPUT_FILE_NOT_FOUND)
            if not os.path.isdir(dir):
                err_msg = 'Please provide directory path instead of file path.'.format(
                    dir)
                raise TeradataMlException(err_msg, MessageCodes.INPUT_FILE_NOT_FOUND)

        env_name = self.env_name
        base_env = self.base_env
        env_specs = [
            {
                "env_name": env_name,
                "base_env": base_env,
                "desc": self.desc
            }
        ]

        if self.libs is not None:
            libs = ["{}=={}".format(name, version)
                    for name, version in
                    zip(self.libs.name.to_list(), self.libs.version.to_list())]

            env_specs[0].update({"libs": libs})

        if self.files is not None:
            files = ["<ADD_YOUR_LOCAL_FILE_PATH>/{}".format(file)
                     for file in self.files.File.to_list()]

            env_specs[0].update({"files": files})

        if not dir:
            dir = tempfile.mkdtemp()

        snap_file_path = os.path.join(dir,
                                      "snapshot_{}_{}_{}.json".format(env_name, base_env, time.time()))

        json_data = {"env_specs": env_specs}
        with open(snap_file_path, "w",) as json_file:
            json.dump(json_data, json_file, indent=4)

        print('Snapshot for environment "{}" is stored at "{}"'.format(env_name, snap_file_path))


class _AuthToken:
    """
    Internal class for storing details of authentication data to be used in headers.
    """
    def __init__(self, token, auth_type):
        self.__value = token
        self.__auth_type = auth_type

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, token_value):
        """
        DESCRIPTION:
            Sets value of _AuthToken.
        """
        self.__value = token_value

    @property
    def auth_type(self):
        return self.__auth_type

    def get_header(self):
        """
        Method for generating header using authentication data and type.
        """
        if self.auth_type.lower() == "basic":
            # Form the Authorization header value by prepending 'Basic ' to the encoded credentials string.
            return {"Authorization": "Basic {}".format(self.value)}
        elif self.auth_type.lower() == "bearer":
            # Form the Authorization header value by prepending 'Bearer ' to the JWT token.
            return {"Authorization": "Bearer {}".format(self.value)}
        elif self.auth_type.lower() == "keycloak":
            # Get valid token value for current time.
            self.value = _InternalBuffer.get("keycloak_manager").get_token()
            return {"Authorization": "Bearer {}".format(self.value)}
