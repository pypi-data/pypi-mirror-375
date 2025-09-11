"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: karthik.thelukuntla@teradata.com
Secondary Owner:

This file implements the wrapper's around AED API's init_dag and close_dag from eleCommon library.
"""

import os
import platform
from ctypes import c_int, c_char_p, POINTER, cdll
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages

class AEDContext:

    _int_array1 = c_int * 1
    _int_array2 = c_int * 2
    _int_array3 = c_int * 3

    _instance = None

    def __new__(self):
        #  Creating singleton instance to load library only once.
        if not self._instance:
            self._instance=super(AEDContext, self).__new__(self)
            # Enable logger for ELECommon library for AED  requests.
            os.putenv("ELE_COMMON_LOG_ENABLED", "TRUE")
            self.ele_common_lib = self._instance._load_aed_lib()
        return self._instance

    def _arr_c(self, lst):
        """
        Utility function to return C array of character pointers, with length equal to list.

        PARAMETERS:
            lst = List for which an C array needs to be returned.

        RETURNS:
            An array of character pointers.
        """
        arr = (c_char_p * len(lst))()
        for i in range(0, len(lst)):
            arr[i] = lst[i].encode('utf-8')
        return arr

    def _decode_list(self, lst):
        """
        Utility function to return Python list of strings, with length equal to list.

        PARAMETERS:
            lst = C array of character pointers.

        RETURNS:
            Python list of strings
            
        EXAMPLES:
            output_nodeids = self.aed_context._decode_list(nodeid_out)
        """
        py_list = []
        for i in range(0, len(lst)):
            py_list.append(lst[i].decode('utf-8'))
        return py_list

    def _validate_aed_return_code(self, ret_code, ret_value = None):
        """
        This function takes in the return code and and value to be returned, in case
        of correct return code.

        PARAMETERS:
            ret_code - Return code from AED call.
            ret_value - Value to be returned in case of success.

        EXAMPLES:
            return self._validate_aed_return_code(ret_code, ret_value)

        RETURNS:
            ret_value provided when called upon, is returned on success, else exception
            is thrown.

        RAISES:
            teradataml exception:
                AED_NON_ZERO_STATUS
        """
        if ret_code == 0:
            if ret_value is None:
                return True
            return ret_value
        else:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_NON_ZERO_STATUS, ret_code),
                                      MessageCodes.AED_NON_ZERO_STATUS)


    def _load_aed_lib(self):
        """
        Function to load AED library. The function gets the absolute file path of AED library
        based on the OS platform and returns the object of loaded library.

        PARAMETERS:
            None

        EXAMPLES:
            _load_aed_lib()

        RETURNS:
            returns the object of loaded library.

        RAISES:
            teradataml exception:
                AED_LIBRARY_LOAD_FAIL
        """
        # Define extension to load AED library depending on the OS platform.
        os_type = platform.system()
        arch_suffix = ""
        if (os_type == "Windows"):
            extension = "dll"
            lib_name = "aed"
        elif (os_type == "Darwin"):
            extension = "dylib"
            lib_name = "libaed"
        else:
            # Linux case
            extension = "so"
            lib_name = "libaed"
            # Only apply architecture suffix for aarch64/ARM64
            machine = platform.uname().machine
            if machine == "aarch64":
                arch_suffix = "_" + machine

        # TODO:: Use logger when it is available.
        from teradataml import _TDML_DIRECTORY
        libPathName = os.path.join(os.sep, _TDML_DIRECTORY, "lib", 
                                   "{0}_0_1{1}.{2}".format(lib_name, arch_suffix, extension))
        try:
            elecommon = cdll.LoadLibrary(libPathName)
        except Exception as err:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_LIBRARY_LOAD_FAIL, str(err)),
                MessageCodes.AED_LIBRARY_LOAD_FAIL)
        return elecommon

    def _init_dag(self, user_name, temp_database, log_level, log_file):
        """
        This wrapper function facilitates a integration with 'init_dag'
        a C++ function, in AED library, with Python tdml library.

        This  function is called when connection object is created using
        create_context or set_context

        PARAMETERS:
            user_name - Database username.
            temp_database - User connected database.
            log_level - log level at AED.
            log_file - Log file to store AED logs.
        EXAMPLES:
            # TODO: Need to update this example once AED log feature is enabled.
            AedCon._init_dag("alice","alice", AED_LOG_TRACE, "sample")

        RETURNS:
            None

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED - When unable to init the dag.
        """
        # Specify the argument types
        self.ele_common_lib.init_dag.argtypes = [POINTER(c_char_p),
                                                 POINTER(c_char_p),
                                                 POINTER(c_int),
                                                 POINTER(c_char_p),
                                                 POINTER(c_int)
                                                ]

        # return code
        ret_code = self._int_array1(0)

        try:
            # *** AED request for init_dag
            self.ele_common_lib.init_dag(self._arr_c([user_name]),
                                          self._arr_c([temp_database]),
                                          c_int(log_level),
                                          self._arr_c([log_file]),
                                          ret_code)

        except Exception as emsg:
            raise TeradataMlException(Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(init_dag)" + str(emsg)),
                                      MessageCodes.AED_EXEC_FAILED)

        return self._validate_aed_return_code(ret_code[0])

    def _close_dag(self):
        """
        This wrapper function facilitates a integration with 'close_dag',
        a C++ function in AED library, with Python tdml library.

        Removes DAG instance in AED.

        PARAMETERS:
            None

        EXAMPLES:
            AedCon._close_dag()

        RETURNS:
            None

        RAISES:
             teradataml exceptions:
                AED_EXEC_FAILED - When failed to close the dag.
        """
        # Specify the argument types
        self.ele_common_lib.close_dag.argtypes = []
        try:
            # *** AED request to close DAG path
            self.ele_common_lib.close_dag()
        except Exception as emsg:
            raise TeradataMlException(
                Messages.get_message(MessageCodes.AED_EXEC_FAILED, "(close_dag)" + str(emsg)),
                MessageCodes.AED_EXEC_FAILED)
