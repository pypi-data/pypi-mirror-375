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
# This file contains different authentication modes and corresponding classes for the OpenAPI SDK.
#
# ################################################################################################

import json
import logging
import os
import re
import time
from abc import ABC, abstractmethod
from enum import Enum

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session

from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import MessageCodes, Messages
from teradataml.utils.validators import _Validators

from .spinner import spin_it

logger = logging.getLogger(__name__)


class AuthMode(Enum):
    DEVICE_CODE = "device_code"
    CLIENT_CREDENTIALS = "client_credentials"
    BEARER = "bearer"


class _BaseAuth(ABC):
    AUTH_MODE = None

    def __init__(self):
        
        self.session = None
        self._ssl_verify = None
        self._base_url = None

    @abstractmethod
    def authenticate(self, **kwargs):
        raise NotImplementedError("Subclasses must implement authenticate method")

    def _set_session_tls(self):
        self.session.verify = self._ssl_verify
        if not self._ssl_verify:
            import urllib3
            from urllib3.exceptions import InsecureRequestWarning

            logger.warning(
                "Certificate validation disabled. Adding certificate verification is"
                " strongly advised"
            )
            urllib3.disable_warnings(InsecureRequestWarning)


class ClientCredentialsAuth(_BaseAuth):
    """
    Class to handle authentication using client credentials.
    """
    AUTH_MODE = AuthMode.CLIENT_CREDENTIALS

    def __init__(self, auth_token_url, auth_client_id, auth_client_secret):
        """
        DESCRIPTION:
            Initializes the object to authenticate through client credentials authentication.

        PARAMETERS:
            auth_token_url:
                Required Argument.
                Specifies the token endpoint URL to fetch the access token.
                Types: str

            auth_client_id:
                Required Argument.
                Specifies the client ID for authentication.
                Types: str

            auth_client_secret:
                Required Argument.
                Specifies the client secret for authentication.
                Types: str

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml.sdk import ClientCredentialsAuth
            >>> auth = ClientCredentialsAuth(
                    auth_token_url="https://example.com/token",
                    auth_client_id="your_client_id",
                    auth_client_secret="your_client_secret"
                )
        """
        arg_info_matrix = []
        arg_info_matrix.append(["auth_token_url", auth_token_url, False, (str,), True])
        arg_info_matrix.append(["auth_client_id", auth_client_id, False, (str,), True])
        arg_info_matrix.append(["auth_client_secret", auth_client_secret, False, (str,), True])
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        self._auth_client_id = auth_client_id
        self._auth_client_secret = auth_client_secret
        self._auth_token_url = auth_token_url

    def authenticate(self):
        """
        DESCRIPTION:
            Authenticates using client credentials and fetches the access token.

        PARAMETERS:
            None

        RETURNS:
            requests.Session: Authenticated session with the access token.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml.sdk import ClientCredentialsAuth
            >>> auth = ClientCredentialsAuth(
                    auth_token_url="https://example.com/token",
                    auth_client_id="your_client_id",
                    auth_client_secret="your_client_secret"
                )
            >>> session = auth.authenticate()
        """
        self.session = OAuth2Session(client=BackendApplicationClient(client_id=self._auth_client_id))

        self._set_session_tls()
        self.session.fetch_token(
            token_url=self._auth_token_url,
            auth=HTTPBasicAuth(self._auth_client_id, self._auth_client_secret),
            verify=self._ssl_verify,
        )

        return self.session


class DeviceCodeAuth(_BaseAuth):
    """
    Class to handle authentication using device code.
    """
    AUTH_MODE = AuthMode.DEVICE_CODE

    def __init__(self, auth_token_url, auth_device_auth_url, auth_client_id, auth_client_secret=None):
        """
        DESCRIPTION:
            Initializes the object to authenticate through device code authentication.

        PARAMETERS:
            auth_token_url:
                Required Argument.
                Specifies the token endpoint URL to fetch the access token.
                Types: str

            auth_device_auth_url:
                Required Argument.
                Specifies the device code endpoint URL to initiate device code flow.
                Types: str

            auth_client_id:
                Required Argument.
                Specifies the client ID for authentication.
                Types: str

            auth_client_secret:
                Optional Argument.
                Specifies the client secret for authentication.
                Types: str or None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml.sdk import DeviceCodeAuth
            >>> auth = DeviceCodeAuth(
                    auth_token_url="https://example.com/token",
                    auth_device_auth_url="https://example.com/device_auth",
                    auth_client_id="your_client_id",
                    auth_client_secret="your_client_secret"
                )
        """
        arg_info_matrix = []
        arg_info_matrix.append(["auth_token_url", auth_token_url, False, (str,), True])
        arg_info_matrix.append(["auth_device_auth_url", auth_device_auth_url, False, (str,), True])
        arg_info_matrix.append(["auth_client_id", auth_client_id, False, (str,), True])
        arg_info_matrix.append(["auth_client_secret", auth_client_secret, True, (str,), True])
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        self._auth_client_id = auth_client_id
        self._auth_client_secret = auth_client_secret
        self._auth_token_url = auth_token_url
        self._auth_device_auth_url = auth_device_auth_url

    def authenticate(self, token_cache_file_path=None):
        """
        DESCRIPTION:
            Authenticates using device code flow and fetches the access token.
        
        PARAMETERS:
            token_cache_file_path:
                Optional Argument.
                Specifies the file path to load and/or cache the token data.
                Types: str
        
        RETURNS:
            requests.Session: Authenticated session with the access token.
        
        RAISES:
            None
        
        EXAMPLES:
            >>> from teradataml.sdk import DeviceCodeAuth
            >>> auth = DeviceCodeAuth(
                    auth_token_url="https://example.com/token",
                    auth_device_auth_url="https://example.com/device_auth",
                    auth_client_id="your_client_id",
                    auth_client_secret="your_client_secret"
                )
            >>> session = auth.authenticate(token_cache_file_path="/path/to/token_cache.json")
        """
        arg_info_matrix = []
        arg_info_matrix.append(["token_cache_file_path", token_cache_file_path, True, (str,), True])
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        token = None
        if token_cache_file_path and os.path.exists(token_cache_file_path):
            logger.debug(
                f"Loading cached token data from {token_cache_file_path}"
            )
            with open(token_cache_file_path, "r") as f:
                token = json.load(f)

        if not token:
            self.session = requests.session()
            self._set_session_tls()
            token = self._get_device_code()

        if "access_token" in token:
            logger.debug(f"Access token acquired successfully: {token}")

            self.__prepare_session_for_token()

            # Create session.
            _bearer = BearerAuth(auth_bearer=token["access_token"])
            _bearer._ssl_verify = self._ssl_verify
            _bearer._base_url = self._base_url
            self.session = _bearer.authenticate()
        
        elif "refresh_token" in token:
            logger.debug(f"Refresh token acquired successfully: {token}")

            self.__prepare_session_for_token()

            # Refresh token for the session.
            self.session.refresh_token(
                token_url=self._auth_token_url,
                refresh_token=token["refresh_token"],
                auth=HTTPBasicAuth(self._auth_client_id, self._auth_client_secret),
                verify=self._ssl_verify,
            )
        
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.REST_DEVICE_CODE_NO_BOTH, token),
                                      MessageCodes.REST_DEVICE_CODE_NO_BOTH)

        with open(token_cache_file_path, "w") as f:
            json.dump(token, f)
        
        return self.session

    def __prepare_session_for_token(self):
        session = OAuth2Session(client_id=self._auth_client_id)

        # don't chase certs/print warning for TLS if already done for _get_device_code
        if hasattr(self, "session"):
            session.verify = self.session.verify
            self.session = session
        else:
            self.session = session
            self._set_session_tls()

    def _get_device_code(self):
        device_code_response = self.session.post(
            self._auth_device_auth_url,
            data={"client_id": self._auth_client_id, "scope": "openid profile"},
        )

        if device_code_response.status_code != 200:
            raise TeradataMlException(Messages.get_message(MessageCodes.REST_DEVICE_CODE_GEN_FAILED,
                                                           device_code_response.status_code),
                                      MessageCodes.REST_DEVICE_CODE_GEN_FAILED)

        device_code_data = device_code_response.json()
        print(
            "1. On your computer or mobile device navigate to: ",
            device_code_data["verification_uri_complete"],
        )
        print("2. Enter the following code: ", device_code_data["user_code"])

        def authorize():
            authenticated = False
            token_data = None

            while not authenticated:
                token_response = self.session.post(
                    self._auth_token_url,
                    data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                        "device_code": device_code_data["device_code"],
                        "client_id": self._auth_client_id,
                    },
                )

                token_data = token_response.json()
                if token_response.status_code == 200:
                    authenticated = True

                elif "error" in token_data:
                    if token_data["error"] in ("authorization_pending", "slow_down"):
                        time.sleep(device_code_data["interval"])
                    else:
                        raise TeradataMlException(Messages.get_message(MessageCodes.REST_DEVICE_CODE_AUTH_FAILED,
                                                                       token_data["error_description"]),
                                                  MessageCodes.REST_DEVICE_CODE_AUTH_FAILED)

                else:
                    raise TeradataMlException(Messages.get_message(MessageCodes.REST_DEVICE_CODE_AUTH_FAILED,
                                                                   f"Bad response code: {token_response.status_code}"),
                                              MessageCodes.REST_DEVICE_CODE_AUTH_FAILED)

            return token_data

        msg = "Waiting for device code to be authorized\n"
        res = spin_it(authorize, msg, 3)
        print(
            "\033[32m\U0001f512 This device has been authorized successfully.\033[0m\n"
        )
        return res


class BearerAuth(_BaseAuth):
    """
    Class to handle authentication using bearer token.
    """
    AUTH_MODE = AuthMode.BEARER

    def __init__(self, auth_bearer):
        """
        DESCRIPTION:
            Initializes the object to authenticate through bearer token authentication.

        PARAMETERS:
            auth_bearer:
                Required Argument.
                Specifies the raw bearer token to be used for authentication.
                Types: str

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml.sdk import BearerAuth
            >>> auth = BearerAuth(auth_bearer="your_bearer_token")
        """
        arg_info_matrix = [["auth_bearer", auth_bearer, False, (str,), True]]
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        self._auth_bearer = f"Bearer {auth_bearer}"

    def authenticate(self):
        """
        DESCRIPTION:
            Authenticates using the provided bearer token.

        PARAMETERS:
            None

        RETURNS:
            requests.Session: Authenticated session with the bearer token.

        RAISES:
            None

        EXAMPLES:
            >>> from teradataml.sdk import BearerAuth
            >>> auth = BearerAuth(auth_bearer="your_bearer_token")
            >>> session = auth.authenticate()
        """
        self.session = requests.session()
        self.session.headers.update({"Authorization": self._auth_bearer})

        self._set_session_tls()

        return self.session
