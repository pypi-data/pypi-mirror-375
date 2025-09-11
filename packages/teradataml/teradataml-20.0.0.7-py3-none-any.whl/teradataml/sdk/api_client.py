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
# This file contains Client class for OpenAPI SDK.
# NOTE: It is currently taken from AoA SDK and is refactored to use the OpenAPI SDK client object.
#
# ################################################################################################

from __future__ import absolute_import

import json
import logging
import os
import time
from typing import Dict, List, Optional, Union

import requests
import yaml
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, InvalidTokenError
from requests.exceptions import ConnectionError

from teradataml.common.exceptions import (TeradataMlException,
                                          TeradatamlRestException)
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.messages import MessageCodes, Messages
from teradataml.utils.validators import _Validators

from ._auth_modes import BearerAuth, ClientCredentialsAuth, DeviceCodeAuth
from ._utils import _select_header_accept

os.system("")  # enables ansi escape characters in terminal


class Client(object):
    DEFAULT_CONFIG_DIR = os.path.join(GarbageCollector._get_temp_dir_name(), "sdk")
    DEFAULT_TOKEN_CACHE_FILE_PATH = os.path.join(DEFAULT_CONFIG_DIR, ".token")
    DEFAULT_CONFIG_FILE_PATH = os.path.join(DEFAULT_CONFIG_DIR, "config.yaml")
    MAX_RETRIES = 3
    SDK_NAME = "BaseSDK"

    def __init__(self, base_url=None, auth=None, ssl_verify=True, config_file=None):
        """
        DESCRIPTION:
            Initializes the Client object and sets up the configuration for the client.

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
                    - For device_code authentication, token is searched in "~/.teradataml/sdk/.token".
                      If it is not present, token is created, used for authentication and saved in
                      the same location.

                Types: ClientCredentialsAuth, DeviceCodeAuth, BearerAuth or None

            ssl_verify:
                Optional Argument.
                Specifies whether to enable or disable TLS Cert validation. If True, TLS cert
                validation is enabled. If False, TLS cert validation is disabled. It can be provided
                directly, or derived from the "BASE_SSL_VERIFY" environment variable or the YAML
                configuration variable "ssl_verify". If ssl_verify is not provided in any of
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
                      ~/.teradataml/sdk/config.yaml is used. If the default config file is not
                      found, this function tries to read the configuration from the environment
                      variables or other arguments.

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

        RETURNS:
            None

        RAISES:
            - TeradataMlException: If the base_url, auth_mode, or ssl_verify is not provided in
              any of the 3 ways (YAML config file, environment variables, or constructor arguments).
            - ValueError: If the base_url is not provided in any of the 3 ways.
            - FileNotFoundError: If the specified YAML file does not exist.
            - yaml.YAMLError: If there is an error in parsing the YAML file.

        EXAMPLES:
            >>> from teradataml.sdk import Client, ClientCredentialsAuth, DeviceCodeAuth
            >>> import os

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
            >>> obj = Client(config_file=cc_config_file)

            # Example 2: Using environment variables.
            >>> os.environ["BASE_URL"] = "https://example.com"
            >>> os.environ["BASE_API_AUTH_MODE"] = "client_credentials"
            >>> os.environ["BASE_API_AUTH_CLIENT_ID"] = "your_client_id"
            >>> os.environ["BASE_API_AUTH_CLIENT_SECRET"] = "your_client_secret"
            >>> os.environ["BASE_API_AUTH_TOKEN_URL"] = "https://example.com/token"
            >>> os.environ["BASE_SSL_VERIFY"] = "false"
            >>> obj = Client()

            # Example 3: Using constructor arguments.
            >>> obj = Client(
                    base_url="https://example.com",
                    auth=DeviceCodeAuth(
                        auth_client_id="your_client_id",
                        auth_client_secret="your_client_secret",
                        auth_token_url="https://example.com/token",
                        auth_device_auth_url="https://example.com/device_auth"
                    ),
                    ssl_verify=True
                )

        """
        self.logger = logging.getLogger(__name__)

        # Use the class attributes of the actual instance's class (could be a child class)
        # rather than Client's class attributes
        cls = self.__class__
        os.makedirs(cls.DEFAULT_CONFIG_DIR, exist_ok=True)


        arg_info_matrix = []
        arg_info_matrix.append(["base_url", base_url, True, (str,)])
        arg_info_matrix.append(["ssl_verify", ssl_verify, True, (bool,)])
        arg_info_matrix.append(["config_file", config_file, True, (str,)])
        arg_info_matrix.append(["auth", auth, True, (ClientCredentialsAuth, DeviceCodeAuth, BearerAuth)])

        _Validators._validate_function_arguments(arg_info_matrix)

        # Client config file.
        self.__config_file = config_file
        self.yaml_config = self.__parse_yaml()

        # Keep all required parameters in the constructor without any default values.
        # They is updated while parsing the config file, environment variables and constructor arguments.

        ## Step 1: Process SSL Verify.
        self.__process_ssl_verify(ssl_verify=ssl_verify)

        ## Step 2: Process Endpoint URL.
        # Raise error if base_url is not provided in config file or environment variable or constructor.        
        self.__process_endpoint_url(base_url=base_url)

        ## Step 3: Process Auth Mode.
        # Raise error if auth_mode is not provided in config file or environment variable or 
        # through constructor argument "auth".        
        self.__process_auth_mode(auth=auth)

        ## Step 3: Process Auth and create auth object if "auth" argument is not provided.
        auth = self.__process_auth(auth=auth)

        # Set required parameters for auth objects before calling authenticate method.
        # These parameters are used in the authenticate method of the auth object.
        auth._ssl_verify = self.ssl_verify
        auth._base_url = self.base_url


        if self.auth_mode == DeviceCodeAuth.AUTH_MODE.value:
            try:
                self.session = auth.authenticate(token_cache_file_path=cls.DEFAULT_TOKEN_CACHE_FILE_PATH)
            except InvalidGrantError as ge:
                if ge.description in ["Token is not active", "Session not active"]:
                    logging.warning(ge.description + "\nRetrying one more time\n")

                    self.__remove_cached_token()

                    self.session = auth.authenticate(token_cache_file_path=cls.DEFAULT_TOKEN_CACHE_FILE_PATH)
                else:
                    raise ge
            except InvalidTokenError as ge:
                logging.warning(ge.description + "\nRetrying one more time\n")

                self.__remove_cached_token()

                self.__create_oauth_session_device_code()
        else:
            self.session = auth.authenticate()

        logging.info(f"Connected to {self.base_url}")

    def __raise_exception_for_args(self, auth_mode, missing_value):
        raise TeradataMlException(Messages.get_message(MessageCodes.REST_AUTH_MISSING_ARG,
                                                       auth_mode,
                                                       missing_value),
                                  MessageCodes.REST_AUTH_MISSING_ARG)

    def __parse_yaml(self):
        """
        DESCRIPTION:
            Parses a YAML configuration file to extract and load configuration settings.

        PARAMETERS:
           - None

        RETURNS:
           None

        RAISES:
           - FileNotFoundError: If the specified YAML file does not exist.
           - yaml.YAMLError: If there is an error in parsing the YAML file.

        EXAMPLES:
           # Example 1: Using a custom configuration file
           obj = Client(config_file="custom_config.yaml")
           obj.__parse_yaml()

           # Example 2: Using the default configuration file
           obj = Client()
           obj.__parse_yaml()
        """

        yaml_file_path = None
        if self.__config_file is not None:
            yaml_file_path = self.__config_file
        elif os.path.isfile(self.__class__.DEFAULT_CONFIG_FILE_PATH):
            yaml_file_path = self.__class__.DEFAULT_CONFIG_FILE_PATH
        if yaml_file_path:
            with open(yaml_file_path, "r") as handle:
                conf = yaml.safe_load(handle)
            return conf
        return {}

    def __process_ssl_verify(self, ssl_verify):
        """
        DESCRIPTION:
            Processes the SSL verification configuration by determining its value based on the 
            provided argument, environment variables, and YAML configuration. If no value is set,
            it defaults to True.

            
        PARAMETERS:
           - ssl_verify: Optional Argument
                         Specifies whether SSL verification is enabled. Can be provided directly, 
                         or derived from the "BASE_SSL_VERIFY" environment variable or
                         the YAML configuration variable "ssl_verify".
                         Type: bool or None

        RETURNS:
           None

        RAISES:
           None

        EXAMPLES:
            # Create client object.
            obj = Client(....)

            # Example 1: Directly passing the ssl_verify argument
            obj.__process_ssl_veify(ssl_verify=True)

            # Example 2: Using environment variable "BASE_SSL_VERIFY"
            os.environ["BASE_SSL_VERIFY"] = "false"
            obj.__process_ssl_veify(ssl_verify=None)

            # Example 3: Using YAML configuration
            obj.yaml_config = {"ssl_verify": False}
            obj.__process_ssl_veify(ssl_verify=None)
        """

        self.ssl_verify = ssl_verify or \
            os.environ.get("BASE_SSL_VERIFY", str(ssl_verify)).lower() == "true" or \
            self.yaml_config.get("ssl_verify", False)

        if self.ssl_verify is None:
            # Set default SSL Verify to True if not set in config file or environment variable 
            # or constructor.
            self.ssl_verify = True

    def __process_endpoint_url(self, base_url: Optional[str]=None):
        """
        DESCRIPTION:
            Processes the base URL configuration by determining its value based on the 
            provided argument, environment variables, and YAML configuration. If no value is set,
            it raises an Exception.

        PARAMETERS:
           - base_url: Optional Argument
                       Specifies the base URL. Can be provided directly, 
                       or derived from the "BASE_URL" environment variable or
                       the YAML configuration variable "base_url".
                       Type: str or None

        RETURNS:
           None

        RAISES:
           TeradataMlException: If no endpoint URL is provided.

        EXAMPLES:
            # Create client object.
            obj = Client(....)

            # Example 1: Directly passing the base_url argument
            obj.__process_endpoint_url(base_url="https://example.com")

            # Example 2: Using environment variable "BASE_URL"
            os.environ["BASE_URL"] = "https://example.com"
            obj.__process_endpoint_url(base_url=None)

            # Example 3: Using YAML configuration
            obj.yaml_config = {"base_url": "https://example.com"}
            obj.__process_endpoint_url(base_url=None)
        """
        self.base_url = base_url or \
            os.environ.get("BASE_URL", None) or \
            self.yaml_config.get("base_url", "")
        
        if not self.base_url:
            raise TeradataMlException(Messages.get_message(MessageCodes.REST_NOT_CONFIGURED,
                                                           "base_url",
                                                           self.SDK_NAME,
                                                           self.SDK_NAME),
                                      MessageCodes.REST_NOT_CONFIGURED)

    def __process_auth_mode(self, auth: Union[DeviceCodeAuth, ClientCredentialsAuth, BearerAuth]):
        """
        DESCRIPTION:
            Processes the authentication mode configuration by determining its value based on the 
            provided argument "auth", environment variables, and YAML configuration.

        PARAMETERS:
           - auth: Optional Argument
                   Specifies the authentication mode. Can be provided directly, 
                   or derived from the "BASE_API_AUTH_MODE" environment variable or
                   the YAML configuration variable "auth_mode".
                   Type: str or None

        RETURNS:
           None

        RAISES:
           TeradataMlException: If no authentication mode is provided.

        EXAMPLES:
            # Create client object.
            obj = Client(....)

            # Example 1: Directly passing the auth argument
            obj.__process_auth_mode(auth="client_credentials")

            # Example 2: Using environment variable "BASE_API_AUTH_MODE"
            os.environ["BASE_API_AUTH_MODE"] = "bearer"
            obj.__process_auth_mode(auth=None)

            # Example 3: Using YAML configuration
            obj.yaml_config = {"auth_mode": "device_code"}
            obj.__process_auth_mode(auth=None)
        """
        self.auth_mode = (auth.AUTH_MODE.value if auth else None) or \
            os.environ.get("BASE_API_AUTH_MODE", None) or \
            self.yaml_config.get("auth_mode", None)

        if not self.auth_mode:
            raise TeradataMlException(Messages.get_message(MessageCodes.REST_NOT_CONFIGURED,
                                                           "auth",
                                                           self.SDK_NAME,
                                                           self.SDK_NAME),
                                      MessageCodes.REST_NOT_CONFIGURED)

        self.__update_legacy_auth_mode()

    def __process_auth(self, auth):
        """
        DESCRIPTION:
            Processes the authentication configuration by determining its value based on the 
            provided argument "auth", environment variables, and YAML configuration.

        PARAMETERS:
           - auth: Optional Argument
                   Specifies the authentication mode. Can be provided directly, 
                   or derived from the "BASE_API_AUTH_MODE" environment variable or
                   the YAML configuration variable "auth_mode".
                   Type: str or None

        RETURNS:
           None

        RAISES:
           TeradataMlException: If no authentication mode is provided.

        EXAMPLES:
            # Create client object.
            obj = Client(....)

            # Example 1: Directly passing the auth argument
            obj.__process_auth(auth="client_credentials")

            # Example 2: Using environment variable "BASE_API_AUTH_MODE"
            os.environ["BASE_API_AUTH_MODE"] = "bearer"
            obj.__process_auth(auth=None)

            # Example 3: Using YAML configuration
            obj.yaml_config = {"auth_mode": "device_code"}
            obj.__process_auth(auth=None)
        """
        if auth is None:
            if self.auth_mode == BearerAuth.AUTH_MODE.value:
                # Create Bearer auth object.
                self.__bearer_token = os.environ.get("BASE_API_AUTH_BEARER_TOKEN", None) or \
                    self.yaml_config.get("auth_bearer")
                self.__raise_exception_for_args(self.auth_mode, "Bearer token") if not self.__bearer_token \
                    else None
                auth = BearerAuth(auth_bearer=self.__bearer_token)

            else:
                # Create ClientCredentials or DeviceCode auth object.
                self.__client_id = os.environ.get("BASE_API_AUTH_CLIENT_ID", None) or \
                    self.yaml_config.get("auth_client_id")
                self.__raise_exception_for_args(self.auth_mode, "Client ID") if not self.__client_id \
                    else None

                self.__client_secret = os.environ.get("BASE_API_AUTH_CLIENT_SECRET", None) or \
                    self.yaml_config.get("auth_client_secret")
                if self.auth_mode == ClientCredentialsAuth.AUTH_MODE.value:
                    # Client Secret is required for client_credentials authentication.
                    # It can be empty for device_code authentication.
                    # Raise error if client_secret is not provided for client_credentials authentication.
                    self.__raise_exception_for_args(self.auth_mode, "Client Secret") if not self.__client_secret \
                        else None

                self.__token_url = os.environ.get("BASE_API_AUTH_TOKEN_URL", None) or \
                    self.yaml_config.get("auth_token_url")
                self.__raise_exception_for_args(self.auth_mode, "Token URL") if not self.__token_url \
                    else None

                if self.auth_mode == ClientCredentialsAuth.AUTH_MODE.value:
                    # Create ClientCredentials auth object.
                    auth = ClientCredentialsAuth(
                        auth_client_id=self.__client_id,
                        auth_client_secret=self.__client_secret,
                        auth_token_url=self.__token_url,
                    )

                elif self.auth_mode == DeviceCodeAuth.AUTH_MODE.value:
                    # Create DeviceCode auth object.
                    self.__device_auth_url = os.environ.get("BASE_API_AUTH_DEVICE_AUTH_URL", None) \
                        or self.yaml_config.get("auth_device_auth_url")
                    self.__raise_exception_for_args(self.auth_mode, "Device Auth URL") \
                        if not self.__device_auth_url else None

                    auth = DeviceCodeAuth(
                        auth_client_id=self.__client_id,
                        auth_client_secret=self.__client_secret,
                        auth_token_url=self.__token_url,
                        auth_device_auth_url=self.__device_auth_url,
                    )
                else:
                    raise ValueError(
                        "Invalid auth mode. Please use either "
                        "'client_credentials' [ClientCredentialsAuth() in 'auth' argument] or "\
                        "'device_code' [DeviceCodeAuth() in 'auth' argument] or "\
                        "'bearer' [BearerAuth() in 'auth' argument]."
                    )
        return auth

    def __update_legacy_auth_mode(self):
        if self.auth_mode == "oauth-cc":
            self.auth_mode = "client_credentials"
        elif self.auth_mode == "oauth":
            self.auth_mode = "device_code"

    def get_request(self, path, header_params: Dict[str, str], query_params: Dict[str, str]):
        """
        DESCRIPTION:
            Sends a GET request to the specified API endpoint using the provided parameters.

        PARAMETERS:
            path:
                Required Argument.
                Specifies the URL path for the API endpoint along with path parameters.
                Note:
                    It should be a relative path to the base URL.
                Types: str

            header_params:
                Required Argument.
                Specifies the header parameters to be included in the request.
                Types: dict

            query_params:
                Required Argument.
                Specifies the query parameters to be included in the request.
                Types: dict

        RETURNS:
            dict for resources if the request is successful, None if resource is not found (404), or str for errors.

        RAISES:
            TeradatamlRestException: If a network or HTTP error occurs.
            HTTPError: If the response contains an HTTP error status code.

        EXAMPLES:
            >>> client = Client(...)
            >>> client.get_request("/api/projects", header_params, query_params)
        """
        retry = 0

        while retry < self.MAX_RETRIES:
            try:
                resp = self.session.get(
                    url=self.__strip_url(self.base_url) + path,
                    headers=header_params,
                    params=query_params,
                )

                if resp.status_code == 404:
                    return None

                return self.__validate_and_extract_body(resp)

            except ConnectionError:
                retry += 1
                time.sleep(5)

            except Exception as e:
                raise TeradatamlRestException(
                    Messages.get_message(MessageCodes.REST_HTTP_ERROR, e),
                    MessageCodes.REST_HTTP_ERROR,
                    str(e))

        if retry == self.MAX_RETRIES:
            logging.error("Max retries reached. Please check your network connection.")
            return None

    def post_request(
        self,
        path,
        header_params: Dict[str, str],
        query_params: Dict[str, str],
        body: Dict[str, str],
    ):
        """
        DESCRIPTION:
            Sends a POST request to the specified API endpoint with the provided body and parameters.

        PARAMETERS:
            path:
                Required Argument.
                Specifies the URL path for the API endpoint along with path parameters.
                Note:
                    It should be a relative path to the base URL.
                Types: str

            header_params:
                Required Argument.
                Specifies the header parameters to be included in the request.
                Types: dict

            query_params:
                Required Argument.
                Specifies the query parameters to be included in the request.
                Types: dict

            body:
                Required Argument.
                Specifies the request body to be sent in the POST request.
                Types: dict

        RETURNS:
            dict for resources if the request is successful, or str for errors.

        RAISES:
            HTTPError: If the response contains an HTTP error status code.

        EXAMPLES:
            >>> client = Client(...)
            >>> client.post_request("/api/projects", header_params, query_params, body)
        """

        resp = self.session.post(
            url=self.__strip_url(self.base_url) + path,
            headers=header_params,
            params=query_params,
            data=json.dumps(body),
        )

        return self.__validate_and_extract_body(resp)

    def put_request(
        self,
        path,
        header_params: Dict[str, str],
        query_params: Dict[str, str],
        body: Dict[str, str],
    ):
        """
        DESCRIPTION:
            Sends a PUT request to the specified API endpoint with the provided body and parameters.

        PARAMETERS:
            path:
                Required Argument.
                Specifies the URL path for the API endpoint along with path parameters.
                Note:
                    It should be a relative path to the base URL.
                Types: str

            header_params:
                Required Argument.
                Specifies the header parameters to be included in the request.
                Types: dict

            query_params:
                Required Argument.
                Specifies the query parameters to be included in the request.
                Types: dict

            body:
                Required Argument.
                Specifies the request body to be sent in the PUT request.
                Types: dict

        RETURNS:
            dict for resources if the request is successful, or str for errors.

        RAISES:
            HTTPError: If the response contains an HTTP error status code.

        EXAMPLES:
            >>> client = Client(...)
            >>> client.put_request("/api/projects/123", header_params, query_params, body)
        """

        resp = self.session.put(
            url=self.__strip_url(self.base_url) + path,
            headers=header_params,
            params=query_params,
            data=json.dumps(body),
        )

        return self.__validate_and_extract_body(resp)

    def patch_request(self,
                      path,
                      header_params: Dict[str, str],
                      query_params: Dict[str, str],
                      body: Dict[str, str]
                      ):
        """
        DESCRIPTION:
            Sends a PATCH request to the specified API endpoint with the provided body and parameters.

        PARAMETERS:
            path:
                Required Argument.
                Specifies the URL path for the API endpoint along with path parameters.
                Note:
                    It should be a relative path to the base URL.
                Types: str

            header_params:
                Required Argument.
                Specifies the header parameters to be included in the request.
                Types: dict

            query_params:
                Required Argument.
                Specifies the query parameters to be included in the request.
                Types: dict

            body:
                Required Argument.
                Specifies the request body to be sent in the PATCH request.
                Types: dict

        RETURNS:
            dict for resources if the request is successful, or str for errors.

        RAISES:
            HTTPError: If the response contains an HTTP error status code.

        EXAMPLES:
            >>> client = Client(...)
            >>> client.patch_request("/api/projects/123", header_params, query_params, body)
        """

        resp = self.session.patch(
            url=self.__strip_url(self.base_url) + path,
            headers=header_params,
            params=query_params,
            data=json.dumps(body),
        )

        return self.__validate_and_extract_body(resp)

    def delete_request(
        self,
        path,
        header_params: Dict[str, str],
        query_params: Dict[str, str],
        body: Dict[str, str],
    ):
        """
        DESCRIPTION:
            Sends a DELETE request to the specified API endpoint with the provided body and parameters.

        PARAMETERS:
            path:
                Required Argument.
                Specifies the URL path for the API endpoint along with path parameters.
                Note:
                    It should be a relative path to the base URL.
                Types: str

            header_params:
                Required Argument.
                Specifies the header parameters to be included in the request.
                Types: dict

            query_params:
                Required Argument.
                Specifies the query parameters to be included in the request.
                Types: dict

            body:
                Required Argument.
                Specifies the request body to be sent in the DELETE request.
                Types: dict

        RETURNS:
            dict for resources if the request is successful, or str for errors.

        RAISES:
            HTTPError: If the response contains an HTTP error status code.

        EXAMPLES:
            >>> client = Client(...)
            >>> client.delete_request("/api/projects/123", header_params, query_params, body)
        """

        resp = self.session.delete(
            url=self.__strip_url(self.base_url) + path,
            headers=header_params,
            params=query_params,
            data=json.dumps(body),
        )

        return self.__validate_and_extract_body(resp)

    def __validate_and_extract_body(self, resp):
        if resp.status_code == 401:
            self.__remove_cached_token()
            self.logger.warning(
                "Clearing the token cache. Please re-run cmd and login again."
            )

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if resp.text:
                raise requests.exceptions.HTTPError(f"Error message: {resp.text}")
            else:
                raise err

        try:
            return resp.json()
        except ValueError:
            return resp.text

    def __strip_url(self, url):
        return url.rstrip("/")

    def __remove_cached_token(self):
        if os.path.exists(self.__class__.DEFAULT_TOKEN_CACHE_FILE_PATH):
            os.remove(self.__class__.DEFAULT_TOKEN_CACHE_FILE_PATH)

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
        headers = {}

        if isinstance(content_type, str):
            content_type = [content_type] 
        headers["Content-Type"] = _select_header_accept(content_type) if content_type else "application/json"

        if isinstance(accept, str):
            accept = [accept]
        headers["Accept"] = _select_header_accept(accept) if accept else "application/json"

        if additional_headers:
            headers.update(additional_headers)

        return headers