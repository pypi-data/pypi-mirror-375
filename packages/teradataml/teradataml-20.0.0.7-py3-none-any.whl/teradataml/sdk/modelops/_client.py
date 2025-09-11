# ################################################################################################
# 
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
# 
# Primary Owner: Adithya Avvaru (adithya.avvaru@teradata.com)
# Secondary Owner: Pankaj Purandare (pankajvinod.purandare@teradata.com)
# 
# Version: 1.0
# SDK Version: 1.0
#
# This file contains ModelOpsClient class for OpenAPI SDK
#
# ################################################################################################

import logging
import os
from typing import Dict, List, Optional, Union

from teradataml.common.garbagecollector import GarbageCollector
from teradataml.utils.validators import _Validators

from .._utils import _select_header_accept
from ..api_client import Client
from ..constants import SdkNames


class ModelOpsClient(Client):
    DEFAULT_CONFIG_DIR = os.path.join(GarbageCollector._get_temp_dir_name(), "sdk", "modelops")
    DEFAULT_TOKEN_CACHE_FILE_PATH = os.path.join(DEFAULT_CONFIG_DIR, ".token")
    DEFAULT_CONFIG_FILE_PATH = os.path.join(DEFAULT_CONFIG_DIR, "config.yaml")
    MAX_RETRIES = 3
    SDK_NAME = SdkNames.MODELOPS.value

    def __init__(self, base_url=None, auth=None, ssl_verify=True, config_file=None, project_id=None):
        """
        DESCRIPTION:
            Initializes the client object and sets up the configuration for the ModelOps client.

        PARAMETERS:
            base_url:
                Optional Argument.
                Specifies the base URL of API endpoint. All requests are made to a relative path to
                this URL. It can be provided directly, or derived from the "BASE_URL" environment
                variable or the YAML configuration variable "base_url". If not provided in any of
                these 3 ways, appropriate Exception is raised.
                Types: str or None

            auth:
                Optional Argument.
                Specifies the type of authentication to be used. It can be one of the following
                authentication type objects:
                - ClientCredentialsAuth: For client credentials authentication.
                - DeviceCodeAuth: For device code authentication.
                - BearerAuth: For bearer token authentication.

                Authentication mode is property of the auth object that is passed to this argument.
                If this argument is not provided, authentication mode is derived from the
                "BASE_API_AUTH_MODE" environment variable or the YAML configuration variable
                "auth_mode". If this argument and the above 2 (environment variable and YAML
                configuration variable) are not provided, appropriate Exception is raised.

                For Authentication modes through environment variables without passing auth
                argument and config file, the following environment variables are used:
                - BASE_URL: Specifies the base URL of API endpoint.
                - BASE_API_AUTH_MODE: Specifies the authentication mode. It can be one of the
                  following:
                    - "client_credentials": For client credentials authentication.
                    - "device_code": For device code authentication.
                    - "bearer": For bearer token authentication.
                - BASE_SSL_VERIFY: Similar to 'ssl_verify' argument.
                - BASE_API_AUTH_CLIENT_ID: OAuth2 client ID. Required for "client_credentials" and
                    "device_code" authentication modes.
                - BASE_API_AUTH_CLIENT_SECRET: OAuth2 client secret. Required for "client_credentials"
                    and "device_code" authentication modes.
                - BASE_API_AUTH_TOKEN_URL: OAuth2 token endpoint. Required for "client_credentials"
                    and "device_code" authentication modes.
                - BASE_API_AUTH_DEVICE_AUTH_URL: OAuth2 device code endpoint. Required for
                    "device_code" authentication mode.
                - BASE_API_AUTH_BEARER_TOKEN: The raw bearer token. Required for "bearer"
                    authentication.

                Note:
                    - For "device_code" authentication, token is searched in
                      "~/.teradataml/sdk/modelops/.token". If it is not present, token is created,
                      used for authentication and saved in the same location.

                Types: ClientCredentialsAuth, DeviceCodeAuth, BearerAuth or None

            ssl_verify:
                Optional Argument.
                Specifies whether to enable or disable TLS Cert validation. If True, TLS cert
                validation is enabled. If False, TLS cert validation is disabled. It can be provided
                directly, or derived from the "BASE_SSL_VERIFY" environment variable or the YAML
                configuration variable "ssl_verify". If 'ssl_verify' is not provided in any of
                these 3 ways, it is set to True by default.
                Default Value: True (Enable TLS cert validation)
                Types: bool or None

            config_file:
                Optional Argument.
                Specifies the path to the YAML configuration file.

                Note:
                    - At least one of YAML config file or environment variables or above arguments
                       must be provided. If not provided, appropriate Exception is raised.
                    - If config_file is not provided, the default config file
                      ~/.teradataml/sdk/modelops/config.yaml is used. If the default config file
                      is not found, this function tries to read the configuration from the
                      environment variables or other arguments.

                If YAML file is provided, it should have the following details, depending on the
                what is provided in other arguments:
                - ssl_verify (bool) : Same as ssl_verify argument.
                - base_url (str) : Same as base_url argument.
                - auth_mode (str) : Authentication mode to be used. It can be one of the following:
                    - client_credentials: For client credentials authentication.
                    - device_code: For device code authentication.
                    - bearer: For bearer token authentication.
                - auth_client_id (str) : OAuth2 client ID. Required for client_credentials and
                    device_code authentication modes.
                - auth_client_secret (str) : OAuth2 client secret. Required for client_credentials
                    and device_code authentication modes.
                - auth_token_url (str) : OAuth2 token endpoint. Required for client_credentials and
                    device_code authentication modes.
                - auth_device_auth_url (str) : OAuth2 device code endpoint. Required for device_code
                    authentication mode.
                - auth_bearer (str) : The raw bearer token. Required for bearer authentication mode.

                Types: str or None

            project_id:
                Specifies the project ID to be used by the client. If provided, it sets the project
                context for the client. If not provided, the project context is not set, and the
                client operates without a specific project context.
                Note:
                    Some functions may require a project context to be set, and if 'project_id'
                    is not provided, it can be set using the `<client_obj>.set_project_id()` method.
                Types: str or None

        RETURNS:
            None

        RAISES:
            - TeradataMlException: If the base_url, auth_mode, or ssl_verify is not provided in
              any of the 3 ways (YAML config file, environment variables, or constructor arguments).
            - ValueError: If the base_url is not provided in any of the 3 ways.
            - FileNotFoundError: If the specified YAML config file does not exist.
            - yaml.YAMLError: If there is an error in parsing the YAML file.

        EXAMPLES:
            >>> from teradataml.sdk import ClientCredentialsAuth, DeviceCodeAuth
            >>> import os
            >>> from teradataml.sdk.modelops import ModelOpsclient

            # Example 1: Using a custom configuration file for client credentials authentication.
            >>> cc_auth_dict = {"auth_client_id": "your_client_id",
                                "auth_client_secret": "your_client_secret",
                                "auth_token_url": "https://example.com/token",
                                "auth_mode": "client_credentials",
                                "base_url": "https://example.com",
                                "ssl_verify": False}

            >>> # Write data to config file.
            >>> cc_config_file = "custom_config.yaml"
            >>> import yaml
            >>> with open(cc_config_file, "w") as f:
                    yaml.dump(cc_auth_dict, f, sort_keys=False)
            
            >>> # Create client object using config file.
            >>> obj = ModelOpsclient(config_file=cc_config_file)

            # Example 2: Using environment variables and set project id using 
            #            set_project_id() method.
            >>> os.environ["BASE_URL"] = "https://example.com"
            >>> os.environ["BASE_API_AUTH_MODE"] = "client_credentials"
            >>> os.environ["BASE_API_AUTH_CLIENT_ID"] = "your_client_id"
            >>> os.environ["BASE_API_AUTH_CLIENT_SECRET"] = "your_client_secret"
            >>> os.environ["BASE_API_AUTH_TOKEN_URL"] = "https://example.com/token"
            >>> os.environ["BASE_SSL_VERIFY"] = "false"
            >>> obj = ModelOpsclient()
            >>> obj.set_project_id("70d4659b-92a2-4723-841a-9ba5629b5f27")

            # Example 3: Using constructor arguments and passing "project_id" argument.
            >>> obj = ModelOpsclient(
                    base_url="https://example.com",
                    auth=DeviceCodeAuth(
                        auth_client_id="your_client_id",
                        auth_client_secret="your_client_secret",
                        auth_token_url="https://example.com/token",
                        auth_device_auth_url="https://example.com/device_auth"
                    ),
                    ssl_verify=True,
                    project_id="70d4659b-92a2-4723-841a-9ba5629b5f27"
                )
        """
        super().__init__(base_url, auth, ssl_verify, config_file)

        arg_info_matrix = []
        arg_info_matrix.append(["project_id", project_id, True, (str,)])

        _Validators._validate_function_arguments(arg_info_matrix)

        if project_id:
            self.set_project_id(project_id)
        else:
            self.project_id = None

    def set_project_id(self, project_id: str):
        """
        set project id

        Parameters:
           project_id (str): project id(uuid)
        """
        self.project_id = project_id
        if not self.projects().find_by_id(id=project_id):
            logging.warning(
                f"Project with id {project_id} not found, but we'll set it anyway."
            )

    def get_current_project(self):
        """
        get project id

        Return:
           project_id (str): project id(uuid)
        """
        return self.project_id

    def projects(self):
        """
        get projects client
        """
        from teradataml.sdk.modelops import Projects

        return Projects(client=self)

    def datasets(self):
        """
        get datasets client
        """
        from teradataml.sdk.modelops import Datasets

        return Datasets(client=self)

    def dataset_templates(self):
        """
        get dataset templates client
        """

        from teradataml.sdk.modelops import DatasetTemplates
        return DatasetTemplates(client=self)

    def dataset_connections(self):
        """
        get dataset connections client
        """

        from teradataml.sdk.modelops import DatasetConnections
        return DatasetConnections(client=self)

    def deployments(self):
        """
        get deployments client
        """

        from teradataml.sdk.modelops import Deployments
        return Deployments(client=self)

    def feature_engineering(self):
        """
        get feature engineering client
        """

        from teradataml.sdk.modelops import FeatureEngineeringTasks
        return FeatureEngineeringTasks(client=self)

    def jobs(self):
        """
        get jobs client
        """

        from teradataml.sdk.modelops import Jobs
        return Jobs(client=self)

    def job_events(self):
        """
        get job events client
        """

        from teradataml.sdk.modelops import JobEvents
        return JobEvents(client=self)

    def models(self):
        """
        get models client
        """

        from teradataml.sdk.modelops import Models
        return Models(client=self)

    def trained_models(self):
        """
        get trained models client
        """

        from teradataml.sdk.modelops import TrainedModels
        return TrainedModels(client=self)

    def trained_model_artefacts(self):
        """
        get trained model artefacts client
        """

        from teradataml.sdk.modelops import TrainedModelsArtefacts
        return TrainedModelsArtefacts(client=self)

    def trained_model_events(self):
        """
        get trained model events client
        """

        from teradataml.sdk.modelops import TrainedModelEvents
        return TrainedModelEvents(client=self)

    def user_attributes(self):
        """
        get user attributes client
        """

        from teradataml.sdk.modelops import UserAttributes
        return UserAttributes(client=self)

    def describe_current_project(self):
        """
        get details of currently selected project
        """
        import pandas as pd

        if self.project_id:
            project_dict = self.projects().find_by_id(self.project_id, "expandProject")
            if project_dict:
                project_data = [
                    [k, v]
                    for (k, v) in list(project_dict.items())
                    if k not in ["_links", "userAttributes"]
                ]
                return pd.DataFrame(project_data, columns=["attribute", "value"])
            else:
                return None
        else:
            return None

    def get_default_connection_id(self):
        """
        get default dataset connection id
        """
        try:
            conn = self.user_attributes().get_default_connection()
            if conn:
                return conn["value"]["defaultDatasetConnectionId"]
            else:
                return None
        except:
            return None

    def _prepare_header_dict(self, content_type: Optional[Union[str, List[str]]] = "application/json",
                             accept: Optional[Union[str, List[str]]] = "application/json",
                             additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        DESCRIPTION:
            Prepares a header dictionary for API requests.

        PARAMETERS:
            content_type:
                Optional Argument.
                Specifies the Content-Type header value(s) to be included in the request.
                Default Value: "application/json"
                Types: List[str]

            accept:
                Optional Argument.
                Specifies the Accept header value(s) to be included in the request.
                Default Value: "application/json"
                Types: List[str]

            additional_headers:
                Optional Argument.
                Specifies any additional headers to be included in the request.
                Types: Dict[str, str]

        RETURNS:
            A dictionary containing the prepared headers.

        RAISES:
            None

        EXAMPLES:
            >>> client = Client(...)
            >>> headers = client._prepare_header_dict(content_type=["application/json"], accept=["application/json"])
        """
        headers = super()._prepare_header_dict(content_type=content_type,
                                               accept=accept,
                                               additional_headers=additional_headers
                                               )
        # ModelOps client requires project ID in headers.
        headers.update({"AOA-Project-ID": self.project_id, "VMO-Project-ID": self.project_id})
        return headers