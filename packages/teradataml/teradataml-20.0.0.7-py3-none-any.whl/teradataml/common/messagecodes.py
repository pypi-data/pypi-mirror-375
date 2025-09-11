# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2018 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: rameshchandra.d@teradata.com
Secondary Owner:

teradataml.common.messagecodes
----------
A messages class for holding all message codes related to messages that are displayed to the user
"""

from enum import Enum
import re

class ErrorInfoCodes(Enum):
    """
    This class contains error codes that to be set for the error messages displayed to user.
    The error codes are associated with the respective  messages.
    Information codes are coded with prefix TDML_100x.
    Error codes are prefixed with TDML_200x
    AED error codes with TDML_210x
    Add codes as below whenever required if a new message code added
    """
    # below codes are the information message codes
    # Error code numbers missing and can be used for new codes:
    # --
    # Error codes between TDML_2500 and TDML_2510 are reserved for
    # Json data errors.
    CONNECTION_SUCCESS = 'TDML_1000'
    CONNECTION_FAILURE = 'TDML_2000'
    MISSING_ARGS = 'TDML_2001'
    OVERWRITE_CONTEXT = 'TDML_2002'
    FORMULA_INVALID_FORMAT = 'TDML_2003'
    ARG_EMPTY = 'TDML_2004'
    TDF_UNKNOWN_COLUMN = 'TDML_2005'
    DISCONNECT_FAILURE = 'TDML_2006'
    INVALID_ARG_VALUE = 'TDML_2007'
    UNSUPPORTED_DATATYPE = 'TDML_2008'
    SQL_UNKNOWN_KEY = 'TDML_2009'
    TDMLDF_CREATE_FAIL  = 'TDML_2010'
    TDMLDF_EXEC_SQL_FAILED  = 'TDML_2102'
    TDMLDF_CREATE_GARBAGE_COLLECTOR  = 'TDML_2103'
    TDMLDF_DELETE_GARBAGE_COLLECTOR  = 'TDML_2104'
    IS_NOT_VALID_DF  = 'TDML_2011'
    TD_MAX_COL_MESSAGE  = 'TDML_2012'
    INVALID_PRIMARY_INDEX  = 'TDML_2013'
    UNKNOWN_INSTALL_LOCATION = 'TDML_2014'
    INDEX_ALREADY_EXISTS  = 'TDML_2015'
    INVALID_INDEX_LABEL = 'TDML_2016'
    UNKNOWN_ARGUMENT = 'TDML_2017'
    INVALID_COLUMN_RANGE_FORMAT = 'TDML_2018'
    TABLE_ALREADY_EXISTS = 'TDML_2019'
    COPY_TO_SQL_FAIL = 'TDML_2020'
    TDMLDF_INFO_ERROR  = 'TDML_2021'
    TDMLDF_UNKNOWN_TYPE = 'TDML_2022'
    MIXED_TYPES_IN_COLUMN_RANGE = 'TDML_2023'
    TDMLDF_POSITIVE_INT = 'TDML_2024'
    TDMLDF_SELECT_DF_FAIL = 'TDML_2025'
    TDMLDF_SELECT_INVALID_FORMAT = 'TDML_2026'
    TDMLDF_SELECT_INVALID_COLUMN = 'TDML_2027'
    TDMLDF_SELECT_EXPR_UNSPECIFIED = 'TDML_2028'
    TDMLDF_SELECT_NONE_OR_EMPTY = 'TDML_2029'
    INVALID_LENGTH_ARGS = 'TDML_2030'
    TDMLDF_DROP_ARGS = 'TDML_2031'
    TDMLDF_INVALID_DROP_AXIS = 'TDML_2032'
    TDMLDF_DROP_INVALID_COL = 'TDML_2033'
    TDMLDF_DROP_INVALID_INDEX_TYPE = 'TDML_2034'
    TDMLDF_DROP_INVALID_COL_NAMES = 'TDML_2035'
    TDMLDF_DROP_ALL_COLS = 'TDML_2036'
    DROP_FAILED = 'TDML_2038'
    DF_WITH_NO_COLUMNS = 'TDML_2039'
    DATA_EXPORT_FAILED = 'TDML_2040'
    DF_LABEL_MISMATCH = 'TDML_2041'
    TDMLDF_INVALID_JOIN_CONDITION = "TDML_2043"
    TDMLDF_INVALID_TABLE_ALIAS = "TDML_2044"
    TDMLDF_AGGREGATE_UNSUPPORTED = 'TDML_2045'
    TDMLDF_INVALID_AGGREGATE_OPERATION = 'TDML_2047'
    INSERTION_INCOMPATIBLE = 'TDML_2048'
    TABLE_OBJECT_CREATION_FAILED = 'TDML_2049'
    FORMULA_MISSING_DEPENDENT_VARIABLE = 'TDML_2050'
    TDMLDF_COLUMN_IN_ARG_NOT_FOUND = 'TDML_2051'
    INVALID_TABLE_KIND_EMPTY_ARGS = 'TDML_2052'
    LIST_DB_TABLES_FAILED = 'TDML_2053'
    INVALID_CONTEXT_CONNECTION = 'TDML_2054'
    TDMLDF_REQUIRED_TABLE_ALIAS = "TDML_2055"
    TDMLDF_ALIAS_REQUIRED = TDMLDF_REQUIRED_TABLE_ALIAS
    TDMLDF_COLUMN_ALREADY_EXISTS = "TDML_2056"
    TDMLDF_AGGREGATE_INVALID_COLUMN = 'TDML_2057'
    TDMLDF_AGGREGATE_COMBINED_ERR = 'TDML_2058'
    DEPENDENT_ARGUMENT = 'TDML_2059'
    UNSUPPORTED_ARGUMENT = 'TDML_2060'
    EITHER_THIS_OR_THAT_ARGUMENT = 'TDML_2061'
    TDMLDF_UNEQUAL_NUMBER_OF_COLUMNS = 'TDML_2062'
    TDMLDF_INDEXES_ARE_NONE = 'TDML_2063'
    MUST_PASS_ARGUMENT = 'TDML_2064'
    CONFIG_ALIAS_DUPLICATES = "TDML_2065"
    CONFIG_ALIAS_ENGINE_NOT_SUPPORTED = "TDML_2066"
    CONFIG_ALIAS_ANLY_FUNC_NOT_FOUND = "TDML_2067"
    CONFIG_ALIAS_VANTAGE_VERSION_NOT_SUPPORTED = "TDML_2068"
    CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND = "TDML_2069"
    CONFIG_ALIAS_INVALID_FUNC_MAPPING = "TDML_2070"
    UNSUPPORTED_OPERATION = 'TDML_2071'
    INVALID_COLUMN_TYPE = 'TDML_2072'
    SETOP_COL_TYPE_MISMATCH = 'TDML_2073'
    SETOP_FAILED = 'TDML_2074'
    SET_TABLE_DUPICATE_ROW = 'TDML_2075'
    IGNORE_ARGS_WARN = 'TDML_2076'
    SET_TABLE_NO_PI = 'TDML_2077'
    FUNCTION_NOT_SUPPORTED = 'TDML_2078'
    UNABLE_TO_GET_VANTAGE_VERSION = 'TDML_2079'
    SETOP_INVALID_DF_COUNT = 'TDML_2080'
    ARG_VALUE_INTERSECTION_NOT_ALLOWED = 'TDML_2081'
    TDMLDF_LBOUND_UBOUND = 'TDML_2082'
    ARG_VALUE_CLASS_DEPENDENCY = 'TDML_2083'
    INVALID_DF_LENGTH = 'TDML_2084'
    DEPENDENT_ARG_MISSING = 'TDML_2085'
    VANTAGE_WARNING = 'TDML_2086'
    FASTLOAD_FAILS = 'TDML_2087'
    FROM_QUERY_SELECT_SUPPORTED = 'TDML_2088'
    INVALID_LENGTH_ARG = 'TDML_2089'
    INVALID_LENGTH_STRING_ARG = INVALID_LENGTH_ARG
    SPECIFY_AT_LEAST_ONE_ARG = 'TDML_2037'
    CANNOT_USE_TOGETHER_WITH = 'TDML_2042'
    TABLE_DOES_NOT_EXIST = 'TDML_2046'
    DEPENDENT_METHOD = 'TDML_2113'
    TDMLDF_COLUMN_IN_ARG_FOUND = 'TDML_2114'
    EITHER_ANY_ARGUMENT = 'TDML_2115'

    # Reserved for Generic Error Messages: 2121 - 2199
    RESERVED_KEYWORD = 'TDML_2121'

    # Reserving a range of error codes for SeriesObject : 2090 - 2099
    USE_FUNCTION_TO_INSTANTIATE = 'TDML_2090'
    SERIES_INFO_ERROR = 'TDML_2091'
    SERIES_CREATE_FAIL = 'TDML_2093'
    # MODEL CATALOGING ERROR CODES starting from 2200 - Reserved till 2220
    MODEL_ALREADY_EXISTS = 'TDML_2200'
    MODEL_NOT_FOUND = 'TDML_2201'
    MODEL_WITH_SEARCH_CRITERION_NOT_FOUND = 'TDML_2202'
    MODEL_CATALOGING_OPERATION_FAILED = 'TDML_2204'
    FUNCTION_JSON_MISSING = 'TDML_2205'
    UNKNOWN_MODEL_ENGINE = 'TDML_2206'
    CANNOT_SAVE_RETRIEVED_MODEL = 'TDML_2207'
    CANNOT_TRANSLATE_TO_TDML_NAME = 'TDML_2208'

    # STORED PROCEDURE WRAPPERS FAILURE : 2221 - 2230
    STORED_PROCEDURE_FAILED = 'TDML_2221'
    NO_ENVIRONMENT_FOUND = 'TDML_2222'
    UNSUPPORTED_FILE_EXTENSION = 'TDML_2223'
    FILE_EMPTY = 'TDML_2224'

    # AED Library Error Codes starting from 2100 - Reserved till 2110
    AED_LIBRARY_LOAD_FAIL = 'TDML_2100'
    AED_LIBRARY_NOT_LOADED = 'TDML_2101'
    AED_EXEC_FAILED = 'TDML_2102'
    AED_NON_ZERO_STATUS = 'TDML_2103'
    AED_QUERY_COUNT_MISMATCH = 'TDML_2104'
    AED_NODE_QUERY_LENGTH_MISMATCH = 'TDML_2105'
    AED_INVALID_ARGUMENT = 'TDML_2106'
    AED_INVALID_GEN_TABLENAME = 'TDML_2107'
    AED_INVALID_SQLMR_QUERY = 'TDML_2108'
    AED_NODE_ALREADY_EXECUTED = 'TDML_2109'
    AED_SETOP_INVALID_NUMBER_OF_INPUT_NODES = 'TDML_2110'
    AED_SETOP_INPUT_TABLE_COLUMNS_COUNT_MISMATCH = 'TDML_2111'
    AED_SHOW_QUERY_MULTIPLE_OPTIONS = 'TDML_2112'

    # Table Operator Error Codes starting from 2300 - Reserved till 2314
    INPUT_FILE_NOT_FOUND = 'TDML_2300'
    REMOVE_FILE_FAILED = 'TDML_2301'
    INSTALL_FILE_FAILED = 'TDML_2302'
    REPLACE_FILE_FAILED = 'TDML_2303'
    URL_UNREACHABLE = 'TDML_2304'
    LIST_SELECT_NONE_OR_EMPTY = 'TDML_2305'
    DATAFRAME_LIMIT_ERROR = 'TDML_2306'
    NOT_ALLOWED_VALUES = 'TDML_2307'
    ARGUMENT_VALUE_SAME = 'TDML_2308'
    PYTHON_NOT_INSTALLED = 'TDML_2309'
    PYTHON_VERSION_MISMATCH = 'TDML_2310'
    PYTHON_VERSION_MISMATCH_OAF = 'TDML_2416'
    EMPTY_FILE = 'TDML_2311'
    ARG_NONE = 'TDML_2312'
    EITHER_FUNCTION_OR_ARGS = 'TDML_2313'
    INVALID_LIST_LENGTH = 'TDML_2314'

    IMPORT_PYTHON_PACKAGE = 'TDML_2414'
    PATH_NOT_FOUND = 'TDML_2415'

    # Script local run Error codes
    SCRIPT_LOCAL_RUN_ERROR = 'TDML_2410'
    INT_ARGUMENT_COMPARISON = 'TDML_2411'
    EXECUTION_FAILED = 'TDML_2412'
    INVALID_COLUMN_DATATYPE = 'TDML_2413'

    # GeoDataFrame Error codes starting from 2421 - Reserved till 2430
    NO_GEOM_COLUMN_EXIST = 'TDML_2421'
    GEOSEQ_USER_FIELD_NUM = 'TDML_2422'

    # Json files related error codes starting from 2500 - Reserved till 2520.
    INVALID_JSON = 'TDML_2500'
    MISSING_JSON_FIELD = "TDML_2501"
    INVALID_FUNCTION_NAME = 'TDML_2502'
    DUPLICATE_PARAMETER = "TDML_2503"

    # Scriptmgmt Error codes.
    FUNC_EXECUTION_FAILED = EXECUTION_FAILED

    # Dictionary argument Error codes starting from 2521 - Reserved till 2530.
    INVALID_DICT_ARG_VALUE = 'TDML_2521'
    UNSUPPORTED_DICT_KEY_VALUE_DTYPE = 'TDML_2522'
    DICT_ARG_KEY_VALUE_EMPTY = 'TDML_2523'
    INVALID_DICT_KEYS = 'TDML_2524'
    INVALID_DICT_KEY_VALUE_LENGTH = 'TDML_2525'
    DUPLICATE_DICT_KEYS_NAMES = 'TDML_2526'

    # Opensource Error codes starting from 2531 - Reserved till 2550.
    MODEL_NOT_FITTED = 'TDML_2531'
    DFS_NO_COMMON_PARENT = 'TDML_2532'
    NODE_NOT_GIVEN_TYPE = 'TDML_2534'
    ARGS_WITH_SAME_COLUMNS = 'TDML_2535'
    PARTITIONING_COLS_DIFFERENT = 'TDML_2536'
    PARTITIONING_COLS_IN_FEATURE_COLS = 'TDML_2537'
    PARTITION_VALUES_NOT_MATCHING = 'TDML_2538'
    PARTITION_IN_BOTH_FIT_AND_PREDICT = 'TDML_2539'
    INVALID_PARTITIONING_COLS = 'TDML_2540'
    TARGET_COL_NOT_FOUND_FOR_EVALUATE = 'TDML_2541'

    # OpenAF Error codes starting from 2551 - Reserved till 2560.
    SET_REQUIRED_PARAMS = 'TDML_2551'
    INVALID_USAGE = 'TDML_2552'

    # Error codes for OTF. Reserved till 2570.
    OTF_TABLE_REQUIRED = 'TDML_2561'

    # Rest Excceptions. Reserved for 2570 - 2580
    REST_HTTP_ERROR = 'TDML_2570'
    REST_AUTH_MISSING_ARG = 'TDML_2571'
    REST_NOT_CONFIGURED = 'TDML_2572'
    REST_DEVICE_CODE_NO_BOTH = 'TDML_2573'
    REST_DEVICE_CODE_GEN_FAILED = 'TDML_2574'
    REST_DEVICE_CODE_AUTH_FAILED = 'TDML_2575'

    # Python SDK Error codes starting from 2580 - Reserved till 2590.
    INFO_NOT_PROVIDED_USE_DEFAULT = 'TDML_W_2580' # Logger warning.

    # EFS Error codes starting from 2600 - Reserved till 2650.
    EFS_COMPONENT_NOT_EXIST = 'TDML_2600'
    EFS_INVALID_PROCESS_TYPE = 'TDML_2601'
    EFS_INVALID_FEATURE_TYPE = 'TDML_2602'
    EFS_FEATURE_IN_DATASET = 'TDML_2603'
    EFS_FEATURE_IN_CATALOG = 'TDML_2604'
    EFS_ENTITY_IN_CATALOG = 'TDML_2605'
    DF_DUPLICATE_VALUES = 'TDML_2606'
    DF_NULL_VALUES = 'TDML_2607'
    EFS_FEATURE_ENTITY_MISMATCH = 'TDML_2608'
    FEATURES_ARCHIVED = 'TDML_2609'
    EFS_DELETE_BEFORE_ARCHIVE = 'TDML_2610'
    EFS_OBJ_IN_FEATURE_PROCESS = 'TDML_2611'
    EFS_OBJECT_NOT_EXIST = 'TDML_2612'
    EFS_OBJECT_IN_OTHER_DOMAIN = 'TDML_2613'


class MessageCodes(Enum):
    """
    MessageCodes contains all the messages that are displayed to the user which are informational
    or raised when an exception/error occurs.
    Add messages to the class whenever a message need to be displayed to the user
    """
    CONNECTION_SUCCESS              = "Connection successful to Teradata Vantage."
    CONNECTION_FAILURE              = "Failed to connect to Teradata Vantage."
    MISSING_ARGS                    = "Following required arguments are missing: {}."

    TABLE_DOES_NOT_EXIST            = "Table '{}.{}' does not exist. {}"
    OVERWRITE_CONTEXT               = "Overwriting an existing context associated with Teradata Vantage Connection. " \
                                      "Most of the operations on any teradataml DataFrames created before this will not work."
    DISCONNECT_FAILURE              = 'Failed to disconnect from Teradata Vantage.'
    FORMULA_INVALID_FORMAT          = "Invalid formula expression format '{}'"
    ARG_EMPTY                       = "Argument '{}' should not be empty string"
    ARG_NONE                        = "Argument '{}' should not be {}. {}"
    DICT_ARG_KEY_VALUE_EMPTY        = "{} of dictionary passed to argument '{}' should not be empty string."
    INVALID_DICT_KEYS               = "Keys of dictionary passed to argument '{}' are not of {}."
    INVALID_DICT_KEY_VALUE_LENGTH   = "Length of {} of dictionary passed to argument '{}' should be equal to length of '{}' {}."
    DUPLICATE_DICT_KEYS_NAMES       = "{} are duplicated in '{}' argument."
    EITHER_FUNCTION_OR_ARGS         = "Either set the {} information using {}() function or " \
                                      "pass the {} information.{}"
    TDF_UNKNOWN_COLUMN              = "DataFrame does not have column {}"
    INVALID_ARG_VALUE               = "Invalid value(s) '{}' passed to argument '{}', should be: {}."
    INVALID_DICT_ARG_VALUE          = "Invalid value(s) '{}' specified in {} of dictionary passed to argument '{}', should be: {}."
    SQL_UNKNOWN_KEY                 = "Unable to retrieve SQL text, invalid key."
    TDMLDF_CREATE_FAIL              = "Failed to create Teradata DataFrame."
    AED_LIBRARY_LOAD_FAIL           = "Failed to load AED Library."
    AED_LIBRARY_NOT_LOADED          = "Internal Error: AED Library not loaded. Please make sure AED library is loaded."
    TDMLDF_CREATE_GARBAGE_COLLECTOR = "Error occured while writing to garbage collector file."
    TDMLDF_DELETE_GARBAGE_COLLECTOR = "Error occured while dropping Teradata view/table during garbage cleanup."
    IS_NOT_VALID_DF                 = "DataFrame specified is invalid (None, empty, or unsupported format)."
    TD_MAX_COL_MESSAGE              = "Too many columns in DataFrame, max limit is 2048."
    INVALID_PRIMARY_INDEX           = "Primary index specified not found in DataFrame column list."
    INDEX_ALREADY_EXISTS            = 'Index specified or defaulted to, {}, already exists in DataFrame column list.'
    INVALID_INDEX_LABEL             = "Index label specified without index. Provide an index label only when index parameter is True. "
    UNSUPPORTED_DATATYPE            = "Invalid type(s) passed to argument '{}', should be: {}."
    UNSUPPORTED_DICT_KEY_VALUE_DTYPE = "Invalid type(s) specified to {} of dictionary passed to argument '{}', should be: {}."
    TABLE_ALREADY_EXISTS            = "Table with name {} already exists in database."
    EMPTY_FILE                      = "The file {} is empty."
    COPY_TO_SQL_FAIL                = "Failed to copy dataframe to Teradata Vantage."
    TDMLDF_INFO_ERROR               = "Unable to retrieve information for the DataFrame."
    TDMLDF_UNKNOWN_TYPE             = "Invalid type for argument(s) '{}', it should be {}."
    TDMLDF_POSITIVE_INT             = "Value '{}' must be a positive integer {} 0"
    TDMLDF_LBOUND_UBOUND            = "Value of '{}' must be {}{}."
    TDMLDF_EXEC_SQL_FAILED          = "Failed to execute SQL: '{}'"
    TDMLDF_SELECT_DF_FAIL           = "Unable to create new DataFrame while selecting requested columns."
    TDMLDF_SELECT_INVALID_FORMAT    = "Requested column selection format is not supported. " \
                                      "Formats supported are: df.select('col1'), df.select(['col1']), df.select(['col1', 'col2']) " \
                                      "and df.select([['col1', 'col2', 'col3']])."
    TDMLDF_INVALID_TABLE_ALIAS      = "{} should not be equal."
    TDMLDF_REQUIRED_TABLE_ALIAS     = "All arguments lsuffix, rsuffix, lprefix and rprefix should not be None as TeradataML DataFrames contains common column(s)."
    TDMLDF_ALIAS_REQUIRED           = "Use aliased DataFrames for self {}."
    TDMLDF_COLUMN_ALREADY_EXISTS    = "Column name with alias '{}' already exists in {} TeradataML DataFrame, change '{}'"
    TDMLDF_INVALID_JOIN_CONDITION   = "Invalid 'on' condition(s): '{}', check documentation for valid conditions."
    TDMLDF_UNEQUAL_NUMBER_OF_COLUMNS = "Number of columns in '{}' and '{}' should be equal."
    TDMLDF_INDEXES_ARE_NONE         = "Indexes of left or right TeradataML DataFrame are None."
    MUST_PASS_ARGUMENT              = "Arguments {} and {} are mutually inclusive. Please provide all arguments or None."
    TDMLDF_SELECT_INVALID_COLUMN    = "Requested column(s) does not exist in parent DataFrame. Valid DataFrame columns for selection are: {}"
    TDMLDF_SELECT_EXPR_UNSPECIFIED  = "Select Expression not specified. Please provide an expression of one of the following formats: " \
                                      "df.select('col1'), df.select(['col1']), df.select(['col1', 'col2']) " \
                                      "or df.select([['col1', 'col2', 'col3']])."
    TDMLDF_SELECT_NONE_OR_EMPTY     = "Select Expression specified contains an empty string/list or an invalid index (such as '', None, [None] or ['None'])."
    INVALID_LENGTH_ARGS             = "Number of values in arguments {} doesn't match."
    INSERTION_INCOMPATIBLE          = "Unable to perform insertion to existing table; columns do not match. "
    TABLE_OBJECT_CREATION_FAILED    = "Unable to create table definition to save to database."
    TDMLDF_DROP_ARGS                = "Specify at least one of 'labels' OR 'columns'. Single label/columns or list-like label/columns."
    TDMLDF_INVALID_DROP_AXIS        = "Axis can be either (0 or 'index') for index OR (1 or 'columns') for columns"
    TDMLDF_DROP_INVALID_COL         = "Invalid column '{0}', valid columns values are: {1}."
    TDMLDF_DROP_INVALID_INDEX_TYPE  = "Invalid index. Index values must be the same type as the index column type '{}'."
    TDMLDF_DROP_INVALID_COL_NAMES   = "Invalid columns. Column labels must be string values."
    TDMLDF_DROP_ALL_COLS            = "Invalid columns. Cannot drop all columns from DataFrame."
    DF_LABEL_MISMATCH               = "The DataFrame object has a mismatching index with respect to its columns."
    DF_WITH_NO_COLUMNS              = "Cannot create DataFrame without columns."
    DATA_EXPORT_FAILED              = "{}() failed to convert teradataml DataFrame to {}. {}"
    TDMLDF_AGGREGATE_UNSUPPORTED    = "All selected columns [{0}] are unsupported for '{1}' operation."
    TDMLDF_INVALID_AGGREGATE_OPERATION = "Invalid aggregate operation(s) [{0}] requested on TeradataML DataFrame. Valid aggregate operation(s) are: {1}."
    TDMLDF_AGGREGATE_COMBINED_ERR   = "No results. Below is/are the error message(s):\n{0}"
    TDMLDF_AGGREGATE_INVALID_COLUMN = "Invalid column names(s) [{0}] passed to argument '{1}'. Valid column names are: {2}."
    TDMLDF_AGGREGATE_AGG_DICT_ERR   = "All requested operations on column(s) [{0}] are " \
                                      "unsupported. Please provide at least one valid operation to be performed per column."
    AED_EXEC_FAILED                 = "Internal Error: Failed to execute AED library call."
    AED_NON_ZERO_STATUS             = "Internal Error: Non-zero status returned from AED."
    AED_QUERY_COUNT_MISMATCH        = "Internal Error: Query count mismatch for the provided node. Please provide the correct DAG node ID."
    AED_NODE_QUERY_LENGTH_MISMATCH  = "Internal Error: Node query length mismatch for the provided node. Please provide the correct DAG node ID."
    AED_INVALID_ARGUMENT            = "{0} Internal Error: Invalid '{1}', valid types: {2}."
    AED_INVALID_GEN_TABLENAME       = "Internal Error: Temp table name passed to the API, does not have fully qualified name. " \
                                      "Example, Table name must be in 'dbname.tablename' format."
    AED_SHOW_QUERY_MULTIPLE_OPTIONS = "{0} Internal Error: Both the options '{1}', '{2}' cannot be used together."
    AED_INVALID_SQLMR_QUERY         = "Internal Error: SQL-MR query must be passed to argument: "
    AED_INVALID_NODE_TYPE           = "Internal Error: Invalid node type (node id) is passed."
    DROP_FAILED                     = "Drop {0} '{1}' failed."
    AED_NODE_ALREADY_EXECUTED       = "Internal Error: Node is already executed. Cannot execute: "
    LIST_DB_TABLES_FAILED           = "Listing of Database Tables failed."
    INVALID_CONTEXT_CONNECTION      = "Current Teradata Vantage Connection context is empty or not set. Use " \
                                      "create_context or set_context."
    FORMULA_MISSING_DEPENDENT_VARIABLE = "Response/Dependent variable is not specified correctly in the formula."
    TDMLDF_COLUMN_IN_ARG_NOT_FOUND  = "Column '{}' provided in '{}' argument, does not exist in '{}' {}."
    DEPENDENT_ARGUMENT              = "'{}' can only be used when '{}' is specified (not None)."
    UNSUPPORTED_ARGUMENT            = "Argument '{}' is not supported. Re-run without '{}' argument."
    EITHER_THIS_OR_THAT_ARGUMENT    = "Provide either '{}' argument(s) or '{}' argument(s)."
    MODEL_ALREADY_EXISTS            = "Model with name '{}' already exists."
    MODEL_WITH_SEARCH_CRITERION_NOT_FOUND = "Model with the given search criterion not found."
    MODEL_NOT_FOUND                 = "Model '{}' not found{}."
    MODEL_CATALOGING_OPERATION_FAILED = "Failed to {} the model. {}"
    UNKNOWN_MODEL_ENGINE            = "Unable to find model generating engine for model of type {}"
    FUNCTION_JSON_MISSING           = "Failed to load JSON file for function: '{}', engine: '{}'"
    CANNOT_SAVE_RETRIEVED_MODEL     = "Cannot save a retrieved model."
    CANNOT_TRANSLATE_TO_TDML_NAME   = "Cannot find teradataml name for SQL name: {}"
    CONFIG_ALIAS_DUPLICATES         = "The config file '{}' has the following duplicate function names: {}."
    CONFIG_ALIAS_ENGINE_NOT_SUPPORTED = "Engine '{}' is not supported. Supported engines is/are {}."
    CONFIG_ALIAS_ANLY_FUNC_NOT_FOUND = "Missing entry for function '{0}' in the configuration file '{1}'. Please add an entry in the configuration file."
    CONFIG_ALIAS_VANTAGE_VERSION_NOT_SUPPORTED = "Current Vantage version '{}' is not supported " \
                                                 "for function aliases. Supported Vantage versions is/are {}."
    CONFIG_ALIAS_CONFIG_FILE_NOT_FOUND = "Alias config file '{}' is not defined for the current Vantage version '{}'. Please add the config file."
    CONFIG_ALIAS_INVALID_FUNC_MAPPING  = "Invalid function mapping(s) '{0}' at line number(s) {1} respectively in configuration file '{2}'. It should be 'functionName:aliasName'. Please check documentation for more details."
    USE_FUNCTION_TO_INSTANTIATE          = "{} is available only using {}"
    SERIES_INFO_ERROR                  = "Unable to retrieve information for the Series."
    SERIES_CREATE_FAIL                 = "Failed to create teradataml Series."
    UNSUPPORTED_OPERATION           = "Invalid operation applied, check documentation for correct usage."
    INVALID_COLUMN_TYPE             = "Column argument '{}' is of unsupported datatype: {}. Should be {}."
    SETOP_COL_TYPE_MISMATCH         = "{}() operation failed possibly due to datatype incompatibility."
    SETOP_FAILED                    = "Failed to {} the teradataml DataFrames."
    SETOP_INVALID_DF_COUNT          = "Not enough teradataml DataFrames passed to {} operation; requires at least two teradataml DataFrames."
    AED_SETOP_INVALID_NUMBER_OF_INPUT_NODES = "Internal Error: Number of input nodes for setop should be more than one. Please provide the correct input_nodeids list."
    AED_SETOP_INPUT_TABLE_COLUMNS_COUNT_MISMATCH = "Internal Error: Input table columns count doesn't match with number of nodes. Please provide the correct input_table_column list."
    SET_TABLE_DUPICATE_ROW          = "Duplicate row error in {}."
    IGNORE_ARGS_WARN                = "Argument(s) '{}' ignored since argument(s) '{}' is/are {}."
    SET_TABLE_NO_PI                 = "A SET table cannot be created without primary_index or timecode_column."
    FUNCTION_NOT_SUPPORTED          = "Function is not supported on '{}'."
    UNABLE_TO_GET_VANTAGE_VERSION   = "Using Vantage version based on the configuration option '{}'. " \
                                      "Please update the configuration option vantage_version, if Vantage " \
                                      "used in creating context has vantage version different from '{}'. " \
                                      "Ignore otherwise. " \
                                      "\n\tE.g.: " \
                                      "\n\tfrom teradataml import configure" \
                                      "\n\tconfigure.vantage_version = 'vantage1.1'"
    ARG_VALUE_INTERSECTION_NOT_ALLOWED = "Column '{}' used in '{}' argument may not be used in '{}' argument."
    ARG_VALUE_CLASS_DEPENDENCY = "Illegal use of '{}' argument for {}. This can be set to '{}', only when {} is operated on {} object."
    INVALID_DF_LENGTH               = "teradataml DataFrames lists passed do not contain the same number of columns or column expressions."
    DEPENDENT_ARG_MISSING           = "Argument(s) '{}' must be specified when '{}' is used."
    VANTAGE_WARNING                = "Following warning raised from Vantage with warning code: {}\n{}"
    FASTLOAD_FAILS                  = "fastload() failed to load pandas dataframe to Teradata Vantage."
    REMOVE_FILE_FAILED              = "Failed to remove {} from Teradata Vantage"
    INPUT_FILE_NOT_FOUND            = "Input file(s) '{}' not found. Please check the file path(s)."
    INSTALL_FILE_FAILED             = "File '{}' cannot be installed."
    REPLACE_FILE_FAILED             = "Unable to replace '{}'"
    URL_UNREACHABLE                 = "URL '{}' is unreachable."
    FROM_QUERY_SELECT_SUPPORTED     = "Encountered problem with the query. {}"
    INVALID_LENGTH_STRING_ARG       = "Length of the string passed to '{}' argument should be {}."
    INVALID_LENGTH_ARG              = "Length of the {} passed to '{}' argument should be {}."
    LIST_SELECT_NONE_OR_EMPTY = "{} specified contains an empty string/list or an invalid index (such as '', None, [None] or ['None'])."
    DATAFRAME_LIMIT_ERROR           = "Number of rows in the Dataframe is greater than {}. Either increase the limit on the number of rows by setting {} or create a dataframe with less than or equal to {} rows."
    SPECIFY_AT_LEAST_ONE_ARG        = "At least one of the '{}' or '{}' arguments must be specified."
    NOT_ALLOWED_VALUES   = "'{}' is not allowed for argument '{}'."
    ARGUMENT_VALUE_SAME             = "Arguments '{}' and '{}' cannot have the same value."
    UNKNOWN_INSTALL_LOCATION        = "{} install location is unknown. Set {} to specify the install location."
    UNKNOWN_ARGUMENT                = "{0}() got an unexpected keyword argument '{1}'"
    CANNOT_USE_TOGETHER_WITH        = "Argument(s) '{}' cannot be used together with '{}'"
    INVALID_COLUMN_RANGE_FORMAT     = "Column range specified for the argument '{}' has more than two boundaries."
    MIXED_TYPES_IN_COLUMN_RANGE     = "Column range specified for the argument '{}' has mix of index and column name. " \
                                      "Provide either indices or column names."
    SCRIPT_LOCAL_RUN_ERROR = "Error occurred while running user script locally: {}"
    STORED_PROCEDURE_FAILED         = "Failed to execute function '{}'.\n{}"
    NO_ENVIRONMENT_FOUND            = "No {} environment(s) found."
    UNSUPPORTED_FILE_EXTENSION      = "Unsupported file extension specified. Supported file extensions is/are {}."
    FILE_EMPTY               = "Input file {} is empty."
    EITHER_ANY_ARGUMENT    = "Provide either {} argument(s)."

    PYTHON_NOT_INSTALLED = "Python is not installed on Vantage. " \
                           "Please install Python interpreter and add-on packages on Vantage."
    PYTHON_VERSION_MISMATCH = "Python version on Vantage is not same as that of local environment. " \
                               "Use the same Python version '{}' or '{}.x' in local environment."
    PYTHON_VERSION_MISMATCH_OAF = "Python version of Lake user environment '{}' is not same as that of local environment '{}'. " \
                                  "Maintain similar version of Python between Lake user environment and local environment."
    IMPORT_PYTHON_PACKAGE = "Module '{}' not found. Install '{}' before running {}()."
    INT_ARGUMENT_COMPARISON = "Argument '{}' must be {} to argument '{}'"
    EXECUTION_FAILED = "Failed to {}. {}"
    INVALID_COLUMN_DATATYPE = "Invalid datatype column(s) [{}] passed to argument '{}'." \
                              " {} column types are: {}."
    INVALID_JSON = "Incorrect JSON data in {}. {}"
    MISSING_JSON_FIELD = "Missing Json field '{}' in '{}' section."
    INVALID_FUNCTION_NAME = "{} is not present in the JSONStore."
    DUPLICATE_PARAMETER = "Duplicate argument '{}' found in section '{}'."
    NO_GEOM_COLUMN_EXIST = 'Table/query result does not contain Geometry column. Use GeoDataFrame,' \
                           ' only when table/query result contains Geometry column(s).'
    GEOSEQ_USER_FIELD_NUM = "Number of user fields for each coordinate must be same as " \
                            "the 'user_field_count'."
    RESERVED_KEYWORD = "'{}' is a Teradata reserved keyword."
    INVALID_LIST_LENGTH = "Length of the list passed to argument '{}' should be of size {}."
    FUNC_EXECUTION_FAILED = "Failed to execute {}. {}"
    MODEL_NOT_FITTED = "Model should be fitted before running {}() or getting attributes."
    DFS_NO_COMMON_PARENT = "DataFrames passed must be derived from same DataFrame, "\
                            "i.e., their parent DataFrame must be same."
    NODE_NOT_GIVEN_TYPE = "The DataFrame passed in '{}' argument is not a DataFrame derived using {}() API."
    ARGS_WITH_SAME_COLUMNS = "Column(s)/DataFrame columns(s) in '{}' and '{}' arguments "\
                                "should{} be same."
    PARTITIONING_COLS_DIFFERENT = "Model is fitted using 'partition_columns' but " \
                "'partition_columns' are not passed. Partition columns should be same as fit()'s "\
                "'partition_columns' or pass 'partition_columns' to the function. In either case "\
                "they should be present in '{}' DataFrame."
    PARTITIONING_COLS_IN_FEATURE_COLS = "Columns in '{}' argument should not be part of"\
                                        " feature columns."
    PARTITION_VALUES_NOT_MATCHING = "Values in {} and {} data partition columns should be same."
    PARTITION_IN_BOTH_FIT_AND_PREDICT = "Use \"partition_columns\" only if model is fitted with partition_column(s)."
    INVALID_PARTITIONING_COLS = "Provided partition_column(s) '{}' is/are not present in parent of '{}' DataFrame(s)."
    PATH_NOT_FOUND = "Specified local path '{}' not found. Please check the path."
    TARGET_COL_NOT_FOUND_FOR_EVALUATE = "Target column '{}' not found in the passed dataFrame. "\
                                        "evaluate() requires target column to be present in the dataFrame."
    SET_REQUIRED_PARAMS = "{} is required to run '{}'. Set it using {}()."
    CONNECTION_PARAMS = "Required connection parameters are missing. Connection parameters should either be " \
                        "explicitly passed to function or specified using a configuration file, or setting up " \
                        "the environment variables."
    DEPENDENT_METHOD = "Method(s) {} must be called before calling '{}'."
    TDMLDF_COLUMN_IN_ARG_FOUND = "Column '{}' provided in '{}' argument, exist in {} {}."
    INVALID_USAGE = "Invalid usage of {0} {1}. Use {0} {1} only {2}."
    REST_HTTP_ERROR = "Failed to run rest API:\n{}"
    REST_AUTH_MISSING_ARG = "For '{}' authentication, '{}' is/are not provided in config file or "\
                            "environment variable or through constructor argument 'auth'."
    REST_NOT_CONFIGURED = "The argument '{}' is not set. {} endpoint not configured.\n" \
                          "Try (re)copy the CLI configuration from {} UI -> Session Details -> CLI Config."
    REST_DEVICE_CODE_NO_BOTH = "Token does not contain access_token or refresh_token. Received token: {}"
    REST_DEVICE_CODE_GEN_FAILED = "Error generating the device code. Received code: {}."
    REST_DEVICE_CODE_AUTH_FAILED = "Error authenticating the device code.\n{}."

    INFO_NOT_PROVIDED_USE_DEFAULT = "{} is not provided in path '{}' method '{}' for operationID '{}' using default {}."
    OTF_TABLE_REQUIRED = "{} is supported only with OTF table."
    EFS_COMPONENT_NOT_EXIST = "{} '{}' does not exist. Use {} to list valid {}."
    EFS_INVALID_PROCESS_TYPE = "Invalid process type '{}' detected. Valid types are: {}."
    EFS_INVALID_FEATURE_TYPE = ("Invalid feature type '{}' detected for feature ''. "
                                "Features cannot ignest for types: {}.")
    EFS_FEATURE_IN_DATASET = ("Feature(s) {} is/are associated with an existing dataset(s) {}. "
                              "Feature(s) can be {} only when they are not associated with any dataset. "
                              "Use 'DatasetCatalog.list_datasets()' to see the list of features associated with datasets.")
    EFS_FEATURE_IN_CATALOG = ("Feature '{}' exists in feature catalog. " 
                              "Delete the feature first using FeatureCatalog.delete_features().")
    EFS_ENTITY_IN_CATALOG = ("Entity '{}' is associated with feature(s) {} in Feature catalog. "
                             "Delete these features using FeatureCatalog.delete_features().")
    DF_DUPLICATE_VALUES = "Duplicate {} are not allowed. Found the duplicate value(s) {}."
    DF_NULL_VALUES = ("Null value(s) are not allowed in {} while {}. "
                       "Found the null value(s) {}.")
    EFS_FEATURE_ENTITY_MISMATCH = ("Feature(s) {} is/are associated with entities {}. One cannot "
                                   "ingest same feature for another entity in the same data domain. "
                                   "Either choose a different feature name or choose a different data domain.")
    FEATURES_ARCHIVED = "Feature(s) {} is/are archived. {}"
    EFS_DELETE_BEFORE_ARCHIVE = ("{0} '{1}' is not archived. Archive the {0} before deleting it."
                                 "Use 'FeatureStore.archive_{2}()' to archive the {0}.")
    EFS_OBJ_IN_FEATURE_PROCESS = ("{0} '{1}' is associated with {2}. {0} can be modified only when it is "
                                  "not associated with {2}. Archive the {3} using {4} and try again.")
    EFS_OBJECT_NOT_EXIST = "{} with {} does not exist in data domain '{}'."
    EFS_OBJECT_IN_OTHER_DOMAIN = "{} with {} does not exist in data domain '{}'. It exists in other data domain(s): {}."
