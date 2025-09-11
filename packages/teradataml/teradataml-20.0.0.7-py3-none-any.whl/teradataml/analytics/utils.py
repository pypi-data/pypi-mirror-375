import json
from json.decoder import JSONDecodeError
import re
from teradataml.common.constants import TeradataConstants
from teradataml.analytics.json_parser.json_store import _JsonStore
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.context.context import get_connection
from teradataml.utils.validators import _Validators
from teradataml.common.constants import ValibConstants
from teradataml.common.utils import UtilFuncs


def display_analytic_functions(type=None, name=None):
    """
    DESCRIPTION:
        Display list of analytic functions available to use on the Teradata Vantage system, user is connected to.

    PARAMETERS:
        type:
            Optional Argument.
            Specifies the type(s) of functions to list down.
            Permitted Values: "BYOM", "TABLE OPERATOR", "SQLE", "UAF", "VAL".
            Types: str or list of str(s)

        name:
            Optional Argument.
            Specifies the search string for function name. When this argument 
            is used, all functions matching the name are listed.
            Types: str or list of str(s)

    RETURNS:
        None

    RAISES:
        TeradataMlException.

    EXAMPLES:
        >>> from teradataml import create_context, display_analytic_functions

        # Example 1: Displaying a list of available analytic functions
        >>> connection_name = create_context(host = host, username=user, password=password)
        >>> display_analytic_functions()

            List of available functions:
                Analytics Database Functions:
                    * PATH AND PATTERN ANALYSIS functions:
                         1. Attribution
                         2. NPath
                         3. Sessionize
                    * MODEL SCORING functions:
                         1. DecisionTreePredict
                         2. KMeansPredict
                         3. NaiveBayesPredict
                         4. TDGLMPredict
                    * FEATURE ENGINEERING TRANSFORM functions:
                         1. Antiselect
                         2. BincodeFit
                         .
                         .
                Unbounded Array Framework (UAF) Functions:
                    * MODEL PREPARATION AND PARAMETER ESTIMATION functions:
                         1. ACF
                         2. ArimaEstimate
                         3. ArimaValidate
                         4. DIFF
                         5. LinearRegr
                         6. MultivarRegr
                         7. PACF
                         8. PowerTransform
                         9. SeasonalNormalize
                         .
                         .
                TABLE OPERATOR Functions:
                     1. ReadNOS
                     2. WriteNOS
                BYOM Functions:
                     1. H2OPredict
                     2. ONNXPredict
                     3. PMMLPredict
                Vantage Analytic Library (VAL) Functions:
                    * DESCRIPTIVE STATISTICS functions:
                         1. AdaptiveHistogram
                         2. Explore
                         3. Frequency
             ...

         # Example 2: When no analytic functions are available on the cluster.
         >>> display_analytic_functions(name="Func_does_not_exists")
         No analytic functions available with connected Teradata Vantage system with provided filters.

         # Example 3: List all available SQLE analytic functions.
         >>> display_analytic_functions(type="SQLE")

            List of available functions:
                
                Analytics Database Functions:
                    * PATH AND PATTERN ANALYSIS functions:
                         1. Attribution
                         2. NPath
                         3. Sessionize
                    * MODEL SCORING functions:
                         1. DecisionTreePredict
                         2. KMeansPredict
                         3. NaiveBayesPredict
                         4. TDGLMPredict
                    * FEATURE ENGINEERING TRANSFORM functions:
                         1. Antiselect
                         2. BincodeFit
                         3. BincodeTransform
                         4. ColumnTransformer
                         .
                         .
                    * FEATURE ENGINEERING UTILITY functions:
                         1. FillRowId
                         2. NumApply
                         3. RoundColumns
                         4. StrApply
          ...

         # Example 4: List all functions with function name containing string "fit".
         >>> display_analytic_functions(name="fit")

            List of available functions:
                
                Analytics Database Functions:
                    * FEATURE ENGINEERING TRANSFORM functions:
                        1. BincodeFit
                        2. Fit
                        3. NonLinearCombineFit
                        4. OneHotEncodingFit
                        5. OrdinalEncodingFit
                        6. PolynomialFeaturesFit
                        7. RandomProjectionFit
                        8. RowNormalizeFit
                        9. ScaleFit
                    * DATA CLEANING functions:
                        1. OutlierFilterFit
                        2. SimpleImputeFit

                Unbounded Array Framework (UAF) Functions:
                    * DIAGNOSTIC STATISTICAL TEST functions:
                        1. FitMetrics

         # Example 5: List all SQLE functions with function name containing string "fit".
         >>> display_analytic_functions(type="SQLE", name="fit")

            List of available functions:
                
                Analytics Database Functions:
                    * FEATURE ENGINEERING TRANSFORM functions:
                        1. BincodeFit
                        2. Fit
                        3. NonLinearCombineFit
                        4. OneHotEncodingFit
                        5. OrdinalEncodingFit
                        6. PolynomialFeaturesFit
                        7. RandomProjectionFit
                        8. RowNormalizeFit
                        9. ScaleFit
                    * DATA CLEANING functions:
                        1. OutlierFilterFit
                        2. SimpleImputeFit


         # Example 6: List all functions of type "TABLE OPERATOR" or "SQLE" containing "fit" or "nos".
         >>> display_analytic_functions(type=["SQLE", "TABLE OPERATOR"], name=["fit", "nos"])

            List of available functions:

                Analytics Database Functions:
                    * FEATURE ENGINEERING TRANSFORM functions:
                        1. BincodeFit
                        2. Fit
                        3. NonLinearCombineFit
                        4. OneHotEncodingFit
                        5. OrdinalEncodingFit
                        6. PolynomialFeaturesFit
                        7. RandomProjectionFit
                        8. RowNormalizeFit
                        9. ScaleFit
                    * DATA CLEANING functions:
                        1. OutlierFilterFit
                        2. SimpleImputeFit

                TABLE OPERATOR Functions:
                    1. ReadNOS
                    2. WriteNOS

        # Example 7: List all functions of type "UAF" containing "estimate".
        >>> display_analytic_functions(type = "UAF", name = "estimate")

        List of available functions:
        
        	Unbounded Array Framework (UAF) Functions:
                * MODEL PREPARATION AND PARAMETER ESTIMATION functions:
                     1. ArimaEstimate

    """
    # Argument validation.
    validator = _Validators()
    arg_info_matrix = []

    arg_info_matrix.append(["name", name, True, (str, list)])
    arg_info_matrix.append(["type", type, True, (str, list), False, \
            ["SQLE", "TABLE OPERATOR", "BYOM", "UAF", "VAL"]])

    validator._validate_function_arguments(arg_info_matrix)

    if get_connection() is None:
        error_code = MessageCodes.INVALID_CONTEXT_CONNECTION
        error_msg = Messages.get_message(error_code)
        raise TeradataMlException(error_msg, error_code)

    func_type_category_name_dict = _JsonStore._get_func_type_category_name_dict()
    # Add entry for VAL functions in func_type_category_name_dict.
    func_type_category_name_dict["VAL"] = ValibConstants.CATEGORY_VAL_FUNCS_MAP.value
    _display_functions(func_type_category_name_dict, type, name)



def _display_functions(func_type_category_name_dict, func_types=None, search_keywords=None):
    """
    Function to display the available functions.
    Functions are filtered based on function_type and function_filter, if provided.

    PARAMETERS:
        func_type_category_name_dict:
            Required Argument.
            Specifies the dictionary with key as function name and 
            value as function metadata.
            Types: dict

        func_types:
            Optional Argument.
            Specifies the type of function.
            Types: str

        search_keywords:
            Optional Argument.
            Specifies the filter for function.
            Types: str

    RETURNS:
        None

    RAISES:
        None

    EXAMPLES:
        _display_functions(func_type_category_name_dict = {'WhichMin':
                                                           <teradataml.analytics.json_parser.metadata.
                                                           _AnlyFuncMetadata object at 0x7f2918084ac8>,
                          type = "SQLE", name="min")

    """
    # Store a flag to decide whether to print header or not.
    list_header_printed = False

    # If type is not specified, print functions under all types.
    if func_types is None:
        func_types = list(func_type_category_name_dict.keys())

    # Check for type of 'type'. If str, convert it to list.
    func_types = UtilFuncs._as_list(func_types)
    func_types = list(map(lambda x: x.upper(), func_types))

    # Map to store function types and corresponding type to be printed.
    func_type_display_type_map = {"SQLE": "Analytics Database",
                                  "VAL": "Vantage Analytic Library (VAL)",
                                  "UAF": "Unbounded Array Framework (UAF)"}

    # Template for function type header.
    type_header = "\n\t{} Functions:"

    # Iterate over all function types one by one and print the corresponding functions.
    for func_type in func_types:
        type_header_printed = False
        funcs = func_type_category_name_dict.get(func_type)
        if isinstance(funcs, dict):
            # For function types having function categories,
            # get list of all functions under all categories.
            for func_cat, func_list in funcs.items():
                func_list = _get_filtered_list(func_list, search_keywords)
                if len(func_list) > 0:
                    if not list_header_printed:
                        print("\nList of available functions:")
                        list_header_printed = True
                    if not type_header_printed:
                        print(type_header.format(func_type_display_type_map.get(func_type, func_type)))
                        type_header_printed = True
                    _print_indexed_list(func_name_list=func_list,
                                        margin="\t\t\t",
                                        header="\t\t* {} functions:".format(func_cat.upper()))

        elif isinstance(funcs, list):
            func_list = _get_filtered_list(funcs, search_keywords)
            if len(func_list) > 0:
                if not list_header_printed:
                    print("\nList of available functions:")
                    list_header_printed = True
                _print_indexed_list(func_name_list=func_list,
                                    margin="\t\t",
                                    header=type_header.format(func_type_display_type_map.get(func_type, func_type)))

    if not list_header_printed:
        print("No analytic functions available with connected Teradata Vantage system with provided filters.")


def _get_filtered_list(name_list, search_keywords=None):
    """
    Function to filter out the names of functions which contain search_keywords in their names.

    PARAMETERS:
        name_list:
            Required Argument.
            Specifies the list of function names.
            Types: List of str(s)

        search_keywords:
            Optional Argument.
            Specifies the filter for the function.
            Types: str or list of str(s)

    RETURNS:
        list

    RAISES:
        None

    EXAMPLES:
        _get_filtered_list("SQLE", ["WhichMin", "Fit"], ["fit", "min"])
    """

    # If search_keyword is specified.
    if search_keywords is not None:
        func_name_list = []

        # Check for type of search_keywords. If str, convert it to list.
        search_keywords = UtilFuncs._as_list(search_keywords)

        # Filter one by one and return list of filtered functions.
        for search_keyword in search_keywords:
            filtered_func_list = [func for func in name_list if search_keyword.lower() in func.lower()]
            func_name_list.extend(filtered_func_list)

        return func_name_list

    # Return all available functions to print.
    else:
        return name_list

def _print_indexed_list(func_name_list, margin, header):
    """
    Function to print a list with index, margin and header provided.

    PARAMETERS:
        func_name_list:
            Required Argument.
            Specifies the list of function names to print.
            Types: List of str(s)

        margin:
            Required Argument.
            Specifies the margin from home.
            Types: str

        header:
            Optional Argument.
            Specifies the header for list.
            Types: str

    RETURNS:
        None

    RAISES:
        None

    EXAMPLES:
        _print_indexed_list(["OutlierFilterFit","SimpleImputeFit"], "\t\t\t")

    """
    if header:
        print(header)
    functions = enumerate(sorted(func_name_list, key=lambda function_name: function_name.lower()), 1)
    for key, value in functions:
        print("{} {}. {}".format(margin, key, value))

class FuncSpecialCaseHandler():
    """ 
    Class to handle the special function and methods are specific to special function(s) attributes
    Steps to add the handler for special functions:
        * Create a handling method based on special function argument.
        * Add general handle method if required.
        * Add the function name, function argument name and special handler to '__handlers'
          dictionary.
        * Set the argument and, Call the 'FuncSpecialCaseHandler()._get_handle()' function from the necessary code section.
    """
    
    def __init__(self, func_name):
        
        # Function related variables.   
        self.__argument = None
        self.__func_name = func_name

        # lambda functions
        self._process_column_index_range = lambda arg_value: '[{0}]'.format(arg_value) if re.match(r'^\d*:\d*$', arg_value) \
                                                        else arg_value
        # Quote "arg_value"
        self._single_quote_arg = lambda arg_value: "'{0}'".format(arg_value)
        # Quote "arg_value" when value is 'NONE'.
        self._single_quote_arg_value_NONE = lambda arg_value: "'{0}'".format(arg_value) if arg_value == 'NONE' else arg_value
        # Remove quotes from "arg_value".
        self._remove_quotes = lambda arg_value, *args, **kwargs: arg_value.replace("'", "") if isinstance(arg_value, str) else arg_value
        

        # Initialize special function handle dictionary.
        self.__handlers = {"Antiselect": {"exclude": self._enclose_square_brackets_add_quote},
                           "BreuschPaganGodfrey": {"formula": self._single_quote_arg},
                           "DickeyFuller": {"algorithm": self._single_quote_arg_value_NONE,
                                            "drift_trend_formula": self._single_quote_arg},
                           "DTW": {"distance": self._single_quote_arg},
                           "GenseriesFormula": {"formula": self._single_quote_arg},
                           "GoldfeldQuandt": {"algorithm": self._single_quote_arg,
                                              "formula": self._single_quote_arg},
                           "HoltWintersForecaster": {"prediction_intervals": self._single_quote_arg},
                           "LinearRegr": {"formula": self._single_quote_arg},
                           "MAMean": {"prediction_intervals": self._single_quote_arg},
                           "MultivarRegr": {"formula": self._single_quote_arg},
                           "ReadNOS": {"authorization": self._add_quote_arg_value_json,
                                       "row_format": self._add_quote_arg_value_json},
                           "SimpleExp": {"prediction_intervals": self._single_quote_arg},
                           "Smoothma": {"well_known": self._single_quote_arg},
                           "WriteNOS": {"authorization": self._add_quote_arg_value_json,
                                        "row_format": self._add_quote_arg_value_json},
                           "NPath": {"mode": self._avoid_quote_for_arg,
                                     "symbols": self._avoid_quote_for_arg,
                                     "result": self._avoid_quote_for_arg,
                                     "filter": self._avoid_quote_for_arg},
                           "Pivoting": {"combined_column_sizes": self._handle_multiple_datatype},
                           "FilterFactory1d": {"database_name": self._single_quote_arg,
                                               "table_name": self._single_quote_arg,
                                               "filter_type": self._single_quote_arg,
                                               "window_type": self._single_quote_arg,
                                               "filter_description": self._single_quote_arg},
                           "CopyArt":{"database_name": self._single_quote_arg,
                                      "table_name": self._single_quote_arg,
                                      "map_name": self._single_quote_arg,
                                      "permanent_table": self._single_quote_arg},
                           "DWT": {"wavelet": self._single_quote_arg},
                           "IDWT": {"part": self._single_quote_arg,
                                    "wavelet": self._single_quote_arg,
                                    "mode": self._single_quote_arg},
                           "DWT2D": {"wavelet": self._single_quote_arg,
                                     "mode": self._single_quote_arg},
                           "IDWT2D": {"wavelet": self._single_quote_arg,
                                      "mode": self._single_quote_arg},
                           "Matrix2Image": {"type": self._single_quote_arg,
                                            "colormap": self._single_quote_arg
                                           },
                           "TDAPIVERTEXAI": {"authorization": self._remove_quotes},
                           "TDAPISAGEMAKER": {"authorization": self._remove_quotes},
                           "TDAPIAZUREML": {"authorization": self._remove_quotes},
                           "AIAnalyzeSentiment": {"authorization": self._remove_quotes},
                           "AITextTranslate": {"authorization": self._remove_quotes},
                           "AITextSummarize": {"authorization": self._remove_quotes},
                           "AITextEmbeddings": {"authorization": self._remove_quotes},
                           "AITextClassifier": {"authorization": self._remove_quotes},
                           "AIRecognizePIIEntities": {"authorization": self._remove_quotes},
                           "AIRecognizeEntities": {"authorization": self._remove_quotes},
                           "AIMaskPII:": {"authorization": self._remove_quotes},
                           "AIExtractKeyPhrases": {"authorization": self._remove_quotes},
                           "AIDetectLanguage": {"authorization": self._remove_quotes},
                           "AIAskLLM": {"authorization": self._remove_quotes},
                           "DataikuPredict": {"accumulate": self._handle_byom_args},
                           "DataRobotPredict": {"accumulate": self._handle_byom_args},
                           "H2OPredict": {"accumulate": self._handle_byom_args},
                           "ONNXEmbeddings": {"accumulate": self._handle_byom_args},
                           "ONNXPredict": {"accumulate": self._handle_byom_args},
                           "PMMLPredict": {"accumulate": self._handle_byom_args}
                           }

    def _handle_byom_args(self, arg_value, *args, **kwargs):
        """
        DESCRIPTION:
            Function to handle the special function arguments for BYOM functions.
            Special character(s) are required to be in single quote for BYOM
            functions. For other SQLE functions, special character(s) to be in double
            quote. Hence removing double quotes and adding single quotes for
            special character(s) in the argument value.

        PARAMETERS:
            arg_value
                Required Argument.
                Specifies the argument value to handle special function arguments.
                Types: str or list of str(s)

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Example 1: Handle the special function arguments for BYOM functions.
            >>> self._handle_byom_args('"alice.deauth"')
            # result: 'alice.deauth'
        """
        arg_values = []
        if isinstance(arg_value, list):
            arg_values = (val.strip('"') for val in arg_value)
            return ", ".join(["'{}'".format(val) for val in arg_values])

        if isinstance(arg_value, str):
            # If argument value is a string, remove quotes.
            arg_value = arg_value.strip('"')
            return "'{}'".format(arg_value)

        return arg_value


    # Setter method for argument.
    def set_arg_name(self, argument):
        """
        DESCRIPTION:
            Set the argument of a function.

        PARAMETERS:
            argument:
                Required Argument.
                Specifies a value to every function argument which contains 
                information about the arguments.
                Types: str

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Setting the "self.__argument" for argument related Information.
            self.__spl_func_obj.set_arg_name(argument)
        """

        # "self.__argument" hold the basic information about the arguments.
        self.__argument = argument

    @staticmethod
    def _is_json(arg_value):
        """
        DESCRIPTION:
            Function to check whether the 'arg_value' argument is python dictionary
            convertible from JSON encoded string.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the 'arg_value' to check the value is valid JSON encoded.
                Types: str

        RETURNS:
            BOOL

        RAISES:
            None

        EXAMPLES:
            FuncSpecialCaseHandler._is_json(arg_value)
        """
        try:
            # Check 'arg_value' is a python dictionary convertible.
            json.loads(arg_value)
            return True
        except JSONDecodeError:
            return False

    def _add_quote_arg_value_json(self, arg_value, *args, **kwargs):
        """
        DESCRIPTION:
            Given a string, list of strings, or dictionary as an argument value:
                * String is single quoted if it is in JSON format.
                * List of strings are single quoted based on special function
                  and combined into a single string separated by comma.
                * Dictionary value is converted to JSON and then value is 
                  single quoted.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the 'arg_value' not to be quoted when authorization object passed,
                Otherwise, to be quoted.
                Types: list OR string

            args:
                Specifies the non-keyword arguments passed to a function.

            kwargs
                Specifies the keyword arguments passed to a function.
        
        RETURNS:
            string

        RAISES:
            None

        EXAMPLES:
            # Example 1: 'arg_value' requires quote for json string. 
            >>> self._add_quote_arg_value_json("{\"json\": 1}")
            # result: '{"json": 1}'
            
            # Example 2: 'arg_value' requires quote for dictionary type. 
            >>> self._add_quote_arg_value_json({'json': 1})
            # result: '{"json": 1}'
            
            # Example 3: 'arg_value' does not require quote for authorization object.
            >>> self._add_quote_arg_value_json("alice.deauth")
            # result: "alice.deauth"
        """
        if isinstance(arg_value, dict):
            # If argument value is of dictionary, convert into string.
            arg_value = json.dumps(arg_value)  
        if FuncSpecialCaseHandler._is_json(arg_value):
            # Add quotes for string in JSON format.
            return "'{0}'".format(arg_value)

        # Avoid quotes for non-JSON string object 'arg_value'.
        return arg_value

    def _avoid_quote_for_arg(self, arg_value, *args, **kwargs):
        """
        DESCRIPTION:
            Given a list of string or string value for 'arg_values':
                * String value will not add single quote for function argument value.
                * List elements will not add quote for special function
                  and, combine the list elements into a single string separated by commas.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the arg_value not to be quoted.
                Types: list OR string 

            args:
                Specifies the non-keyword arguments passed to a function.

            kwargs
                Specifies the keyword arguments passed to a function.

        RETURNS:
            string

        RAISES:
            None

        EXAMPLES:
            self._avoid_quote_for_arg()
        """

        # Avoid quote for special function "arg_value".
        return UtilFuncs._teradata_collapse_arglist(arg_value, "")

    def _enclose_square_brackets_add_quote(self, arg_value, *args, **kwargs):
        """
        DESCRIPTION:
            Function to handle square bracket and quote for 'arg_value'.
                * Function uses special handler method for square bracket. 
                * Function uses generic handler method for single quote.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the arg_value to remove square bracket and add quote(s).
                Types: list OR string

            args:
                Specifies the non-keyword arguments passed to a function.
            
            kwargs
                Specifies the keyword arguments passed to a function.

        RETURNS:
            string

        RAISES:
            None

        EXAMPLES:
            # Scenario 1: column index range require square bracket.
                self._enclose_square_brackets_add_quote(arg_value)
                # returns '[1:2]'

            # Scenario 2: column range  require no square bracket.
                self._enclose_square_brackets_add_quote(arg_value)
                # returns 'col1:col3'
        """
        # Validate if "self.__argument" is a column name.
        if self.__argument.is_column_argument() and self.__argument.get_target_table() and arg_value is not None:
            # Handle square bracket for function argument values.
            arg_value = [arg_value] if not isinstance(arg_value, list) else arg_value

            # Iterate the 'arg_value'.
            # Process column range in "arg_value".
            for index, value in enumerate(arg_value):
                for sep in TeradataConstants.RANGE_SEPARATORS.value:
                    # If argument value is a column with separator and
                    # If value does not start with column exclusion operator "-",
                    # Enclose square bracket for column index range.
                    if sep in value and "-" != value[0]:
                        arg_value[index] = self._process_column_index_range(value) 
                        break
        # In certain cases special function handler also requires generic function handler.
        # In that case, generic function reference(s) passed as a  Non-Keyword argument and utilized.
        # In this instance, Antiselect handler utilises "self._quote_collapse_other_args"
        # generic method to handle quote for the 'arg_value'.
        return args[0](self.__argument, arg_value)
 
    def _get_handle(self):
        """
        DESCRIPTION:
            Function gets special handle required for "self.__func_name".
                * Check "self.__func_name" is a special function.
                * returns function handler for special function. 

        PARAMETERS:
            None
            
        RETURNS:
            FuncSpecialCaseHandler()._add_quote_arg_value_json OR  
            FuncSpecialCaseHandler()._avoid_quote_for_arg OR
            FuncSpecialCaseHandler()._enclose_square_brackets_add_quote

        RAISES:
            None

        EXAMPLES:
            FuncSpecialCaseHandler()._get_handle()
        """
        # Check function requires special handler.
        if self.__func_name in self.__handlers and self.__argument.get_lang_name().lower() in self.__handlers[self.__func_name]:
            # Return special handler.
            return self.__handlers[self.__func_name][self.__argument.get_lang_name().lower()]

        return None

    def _add_square_bracket(self, arg_value):
        """
        DESCRIPTION:
            Function encloses square bracket for column range value in "arg_value".
                * Identifies valid column range value in "arg_value".
                * Append square bracket for valid column range.
        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the "arg_value" to append square bracket.
                Types: list
        RETURNS:
            list
        RAISES:
            None
        EXAMPLES:
            self._add_square_bracket(arg_value)
        """

        # The "Antiselect" function requires a special handler.
        if arg_value is not None and self.__func_name != "Antiselect":
            if not isinstance(arg_value, list):
                arg_value = [arg_value]
            for num, value in enumerate(arg_value):
                for sep in TeradataConstants.RANGE_SEPARATORS.value:
                    # If argument value is a column with separator and
                    # if value starts with column exclusion operator "-",
                    # no need to enclose in square bracket.
                    if sep in value and "-" != value[0]:
                        arg_value[num] = "[{}]".format(arg_value[num])
                        break
        return arg_value
    
    def _handle_multiple_datatype(self, arg_value, *args, **kwargs):

        """
        DESCRIPTION:
            Function to handle multiple data types in "arg_value".
                * Function returns the "arg_value" in sqle expected format.

        PARAMETERS:
            arg_value:
                Required Argument.
                Specifies the arg_value to handle multiple data types.
                Types: int or str or list of str(s)

        RETURNS:
            arg_value converted into sqle expected format.

        RAISES:
            None

        EXAMPLES:
            # Scenario 1: convert list of string into sqle expected format.
                self._handle_multiple_datatype(arg_value)
                # returns "'col1:1234','col2:1144','col3:214'"

            # Scenario 2: convert string into sqle expected format.
                self._handle_multiple_datatype(arg_value)
                # returns "'col1:1234'"
        """
        # Datatype of arg_value already validated inside function.

        # Convert the pass value into sqle expected format.
        # If argument value is a list, convert into sqle expected string format.
        # If argument value is a string, add single quote.
        # If argument value is a integer, return as it is.
        if isinstance(arg_value, list):
            if all(isinstance(i, str) for i in arg_value):
                arg_value = "'" + "','".join(arg_value) + "'"
        elif isinstance(arg_value, str):
            arg_value = [arg_value]
            arg_value = "'" + "','".join(arg_value) + "'"

        return arg_value