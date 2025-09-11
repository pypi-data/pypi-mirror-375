"""
Unpublished work.
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET
Primary Owner: gouri.patwardhan@teradata.com
Secondary Owner: Pradeep.Garre@teradata.com
This file implements workflow for generating JWT token.
"""
import base64
import jwt
import time
from pathlib import Path
import pathlib
from teradataml import configure

class _AuthWorkflow:
    """
    Get the JWT token for requested user.
    """
    def __init__(self, state):
        """
        DESCRIPTION:
            Constructor to initiate Authentication work flow.

        PARAMETERS:
            state:
                Required Argument.
                Specifies the dictionary containing following:
                    1. "base_url" which is extracted from "ues_url".
                    2. "org_id" which is also extracted from "ues_url".
                    3. "pat_token" which is obtained from VantageCloud Lake Console, and it is specific to the user.
                    4. "pem_file" which is obtained from VantageCloud Lake Console, and it is specific to the user.
                    5. "username" which is the DB user.
                    5. "expiration_time" which is the expiration time for the token and has a default value of
                       31536000 seconds.
                    6. "valid_from" which states epoch seconds representing time from which JWT token will be valid
                        and same is used as iat claim in payload.
                Types: dict

        RETURNS:
            Instance of _AuthWorkflow.

        RAISES:
            None

        EXAMPLES :
            >>> _AuthWorkflow(state)
        """
        self.state = state

    def _get_epoch_time(self):
        """
        DESCRIPTION:
            Generate expiry epoch time.

        RETURNS:
            tuple
        """
        current_epoch_time = int(time.time())
        expiry_epoch_time = current_epoch_time + self.state.get('expiration_time')
        return current_epoch_time, expiry_epoch_time

    def _generate_header(self):
        """
        DESCRIPTION:
            Generate JWT header.

        RETURNS:
            dict
        """
        # Extract the pem file name without extension.
        kid = pathlib.Path(self.state.get('pem_file')).stem if not self.state.get('kid') else self.state['kid']
        header = {
            "alg": "RS256",
            "kid": kid,
            "typ": "JWT"
        }
        return header

    def _generate_payload(self):
        """
        DESCRIPTION:
            Generate JWT payload.

        RETURNS:
            A dictionary with the JWT payload.
        """
        _, exp = self._get_epoch_time()
        payload = {
            "aud": [
                "td:service:authentication"
            ],
            "exp": exp,
            "iss": "teradataml",
            "multi-use": True,
            "org_id": self.state['org_id'],
            "pat": self.state['pat_token'],
            "sub": self.state['username']
        }
        # Add iat if applicable.
        if self.state['valid_from'] is not None:
            payload.update({"iat": self.state['valid_from']})
        return payload

    def _sign_jwt(self, payload, header):
        """
        DESCRIPTION:
            Encode JWT using private key.

        PARAMETERS:
            payload:
                Required Argument.
                Specifies the payload required for encoding the JWT token.
                Types: dict
            header:
                Required Argument.
                Specified the header required for encoding the JWT token.
                Types: dict

        RETURNS:
            str
        """
        with open(self.state['pem_file'], "r") as f:
            private_key = f.read()
        return jwt.encode(payload=payload, key=private_key, algorithm=header["alg"], headers=header)

    def _proxy_jwt(self):
        """
        DESCRIPTION:
            Generate JWT token and add the value in dictionary.

        RETURNS:
            str
        """
        jwt_token = self._sign_jwt(self._generate_payload(), self._generate_header())
        self.state['jwt'] = jwt_token
        return jwt_token
