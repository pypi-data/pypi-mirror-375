"""
Unpublished work.
Copyright (c) 2023 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: Dhanashri.Thigale@teradata.com
Secondary Owner: Pradeep.Garre@teradata.com

This file has internal buffer which acts as local storage for teradataml.
"""

class _InternalBuffer:
    """ An internal class to store teradataml's internal data. """
    __data = {}

    @classmethod
    def add(cls, **buff_data):
        """
        DESCRIPTION:
            Function to add the object to _InternalBuffer.

        PARAMETERS:
            buff_data:
                Required Argument.
                Specifies the dict object.
                Types: dict

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Add auth token to internal buffer.
            _InternalBuffer.add(auth_token="abc")
        """
        cls.__data.update(buff_data)

    @classmethod
    def clean(cls):
        """
        DESCRIPTION:
            Function to clean the internal buffer. This function removes
            all the keys and values from _InternalBuffer.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Remove all json objects from _InternalBuffer.
            _InternalBuffer.clean()
        """
        cls.__data.clear()

    @classmethod
    def get(cls, key):
        """
        DESCRIPTION:
            Function to get value of specified "key".

        PARAMETERS:
            key:
                Required Argument.
                Specifies the key name.
                Note:
                    If key does not exists in the __data, it will return None.
                Types: str

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Get auth token from _InternalBuffer.
            _InternalBuffer.get("auth_token")
        """
        if key in cls.__data:
            return cls.__data.get(key)

    @classmethod
    def remove_key(cls, key):
        """
        DESCRIPTION:
            Remove a particular key from the internal buffer.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Remove key "vs_session_id" from _InternalBuffer.
            >>> _InternalBuffer.remove_key("vs_session_id")
        """
        del cls.__data[key]

    @classmethod
    def remove_keys(cls, keys):
        """
        DESCRIPTION:
            Removes specified keys from the internal buffer.

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Remove keys "list_base_envs" and "default_base_env_python" from _InternalBuffer.
            >>> _InternalBuffer.remove_keys(['list_base_envs', 'default_base_env_python'])
        """
        for key in keys:
            if cls.__data.get(key) is not None:
                del cls.__data[key]
