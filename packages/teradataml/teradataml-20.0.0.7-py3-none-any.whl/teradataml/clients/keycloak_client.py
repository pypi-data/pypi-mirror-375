"""
Unpublished work.
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET
Primary Owner: shivani.kondewar@teradata.com
Secondary Owner: aanchal.kavedia@teradata.com
This file implements _KeycloakManager class used to store data for keycloak token generation.
"""

import time
from enum import Enum

from teradataml import TeradataMlException, MessageCodes
from teradataml.common.constants import HTTPRequest
from teradataml.context.context import _get_user


class GrantType(Enum):
    PASS = "password"
    REFRESH = "refresh_token"
    CLIENT = "client_credentials"


class _KeycloakManager():

    def __init__(self, auth_url, client_id):
        """
        DESCRIPTION:
            Constructor to initiate keycloak manager.

        PARAMETERS:
            auth_url:
                Required Argument.
                Specifies the endpoint URL for a keycloak server.
                Types: str

            client_id:
                Required Argument.
                Specifies the client/service for which keycloak server avails a token.
                Types: str

        RETURNS:
            Instance of _KeycloakManager.

        RAISES:
            None

        EXAMPLES:
            >>> token_generator = _KeycloakManager(auth_url=auth_url,
            ...                                    username=username,
            ...                                    client_id=client_id)
        """
        self._auth_url = auth_url
        self._client_id = client_id
        self._header = {"Content-Type": "application/x-www-form-urlencoded"}
        self._expires_at = None
        self._refresh_expires_at = None

    def generate_token(self, username=None, password=None, refresh=False):
        """
        DESCRIPTION:
            Method generates keycloak token.
            Token can be generated using any one of the following information:
                * Username and password
                * Refresh token

        PARAMETERS:
            username:
                Optional Argument.
                Specifies the username for database user for which keycloak token is
                to be generated. If not specified, then user associated with current
                connection is used.
                Types: str

            password:
                Optional Argument.
                Specifies the password for database user.
                Types: str

            refresh:
                Optional Argument.
                Specifies the boolean flag to indicate if token needs to be generated
                using existing refresh token or not.
                Default value: False
                Types: Boolean

        RETURNS:
            Keycloak token

        RAISES:
            RuntimeError.

        EXAMPLES:
            # Example 1: Generate the authentication token using username and password.
            >>> keycloak_obj.generate_token(username="username", password="password")

            # Example 2: Generate the authentication token using default username for
            #            current session and provided password.
            >>> keycloak_obj.generate_token(password="password")

            # Example 3: Generate the authentication token using refresh token which is
            #            already available.
            >>> keycloak_obj.generate_token(refresh=True)
            """
        # Define the payload.
        if password:
            payload = {
                "grant_type": GrantType.PASS.value,
                "client_id": self._client_id,
                "username": username if username else _get_user(),
                "password": password
            }
        if refresh:
            payload = {
                "grant_type": GrantType.REFRESH.value,
                "client_id": self._client_id,
                "refresh_token": self._refresh_token
            }

        # Make the POST request.
        # Importing locally to avoid circular import.
        from teradataml import UtilFuncs
        response = UtilFuncs._http_request(self._auth_url, HTTPRequest.POST,
                                           headers=self._header, data=payload)

        # Check the response.
        if 200 <= response.status_code < 300:
            response_data = response.json()
            self._auth_token = response_data['access_token']
            self._refresh_token = response_data['refresh_token']
            # 30 is buffer time to assume delay in processing of response_data.
            self._expires_at = time.time() + response_data['expires_in'] - 30
            self._refresh_expires_at = time.time() + response_data['refresh_expires_in'] - 30
        else:
            raise

        return self._auth_token

    def get_token(self):
        """
        DESCRIPTION:
            Function to get keycloak token.
            If access token is not expired, existing token is returned.
            If access token is expired, and refresh token is alive, new access token is generated.
            If both access token and refresh token are expired, TeradataMlException is raised

        RETURNS:
            Keycloak token

        RAISES:
            TeradataMlException.

        """
        # If existing auth_token is expired, regenerate using refresh token.
        if self._expires_at and time.time() > self._expires_at:
            # If refresh token is expired, raise error.
            if self._refresh_expires_at and time.time() > self._refresh_expires_at:
                raise TeradataMlException("Refresh token for keycloak is expired."
                                          " Execute set_auth_token() to set fresh authentication token.",
                                          MessageCodes.FUNC_EXECUTION_FAILED)
            else:
                # Regenerate fresh access token using refresh token.
                self.generate_token(refresh=True)

        return self._auth_token
