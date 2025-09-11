import pandas as pd
from inspect import getsource
import re
from teradataml.dataframe.copy_to import copy_to_sql
from teradataml.dataframe.dataframe import DataFrame
from teradataml.dbutils.filemgr import install_file, list_files, remove_file
from teradataml.utils.utils import execute_sql
import teradatasqlalchemy as tdsqlalchemy
from teradataml.utils.validators import _Validators
from teradataml.dataframe.sql import _SQLColumnExpression
from teradatasqlalchemy import VARCHAR, CLOB, CHAR, DATE, TIMESTAMP
from teradataml.common.constants import TableOperatorConstants, TeradataConstants, TeradataTypes
from teradataml.common.utils import UtilFuncs
from teradataml.dataframe.sql_interfaces import ColumnExpression
from teradataml.table_operators.table_operator_util import _TableOperatorUtils
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.scriptmgmt.lls_utils import get_env
from sqlalchemy import literal_column

def udf(user_function=None, returns=VARCHAR(1024), env_name = None, delimiter=',', quotechar=None, debug=False):
    """
    DESCRIPTION:
        Creates a user defined function (UDF).
        
        Notes: 
            1. Date and time data types must be formatted to supported formats.
               (See Prerequisite Input and Output Structures in Open Analytics Framework for more details.)
            2. Packages required to run the user defined function must be installed in remote user 
               environment using install_lib method of UserEnv class. Import statements of these
               packages should be inside the user defined function itself.
            3. Do not call a regular function defined outside the udf() from the user defined function.
               The function definition and call must be inside the udf(). Look at Example 9 to understand more.
            4. One can use the `td_buffer` to cache the data in the user defined function. 
               Look at Example 10 to understand more.

    PARAMETERS:
        user_function:
            Required Argument.
            Specifies the user defined function to create a column for
            teradataml DataFrame.
            Types: function
            Note:
                Lambda functions are not supported. Re-write the lambda function as regular Python function to use with UDF.

        returns:
            Optional Argument.
            Specifies the output column type.
            Types: teradatasqlalchemy types object
            Default: VARCHAR(1024)

        env_name:
            Optional Argument.
            Specifies the name of the remote user environment or an object of
            class UserEnv for VantageCloud Lake.
            Types: str or oject of class UserEnv.
            Note:
                * One can set up a user environment with required packages using teradataml
                  Open Analytics APIs. If no ``env_name`` is provided, udf use the default 
                  ``openml_env`` user environment. This default environment has latest Python
                  and scikit-learn versions that are supported by Open Analytics Framework
                  at the time of creating environment.

        delimiter:
            Optional Argument.
            Specifies a delimiter to use when reading columns from a row and
            writing result columns.
            Default value: ','
            Types: str with one character
            Notes:
                * This argument cannot be same as "quotechar" argument.
                * This argument cannot be a newline character.
                * Use a different delimiter if categorial columns in the data contains
                  a character same as the delimiter.

        quotechar:
            Optional Argument.
            Specifies a character that forces input of the user function
            to be quoted using this specified character.
            Using this argument enables the Advanced SQL Engine to
            distinguish between NULL fields and empty strings.
            A string with length zero is quoted, while NULL fields are not.
            Default value: None
            Types: str with one character
            Notes:
                * This argument cannot be same as "delimiter" argument.
                * This argument cannot be a newline character.

        debug:
            Optional Argument.
            Specifies whether to display the script file path generated during function execution or not. This
            argument helps in debugging when there are any failures during function execution. When set
            to True, function displays the path of the script and does not remove the file from local file system.
            Otherwise, file is removed from the local file system.
            Default Value: False
            Types: bool

    RETURNS:
        ColumnExpression

    RAISES:
        TeradataMLException

    EXAMPLES:
        # Load the data to run the example.
        >>> load_example_data("dataframe", "sales")

        # Create a DataFrame on 'sales' table.
        >>> df = DataFrame("sales")
        >>> df
                    Feb    Jan    Mar    Apr    datetime
        accounts                                          
        Yellow Inc   90.0    NaN    NaN    NaN  04/01/2017
        Jones LLC   200.0  150.0  140.0  180.0  04/01/2017
        Red Inc     200.0  150.0  140.0    NaN  04/01/2017
        Alpha Co    210.0  200.0  215.0  250.0  04/01/2017
        Blue Inc     90.0   50.0   95.0  101.0  04/01/2017
        Orange Inc  210.0    NaN    NaN  250.0  04/01/2017

        # Example 1: Create the user defined function to get the values in 'accounts'
        #            to upper case without passing returns argument.
        >>> from teradataml.dataframe.functions import udf
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(upper_stats = to_upper('accounts'))
        >>> res
                    Feb    Jan    Mar    Apr  datetime upper_stats
        accounts                                                    
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC
        >>>

        # Example 2: Create a user defined function to add length of string values in column  
        #           'accounts' with column 'Feb' and store the result in Integer type column.
        >>> from teradatasqlalchemy.types import INTEGER
        >>> @udf(returns=INTEGER()) 
        ... def sum(x, y):
        ...     return len(x)+y
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(len_sum = sum('accounts', 'Feb'))
        >>> res
                    Feb    Jan    Mar    Apr  datetime  len_sum
        accounts                                                 
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04      218
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04       98
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04      100
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04      209
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04      220
        Red Inc     200.0  150.0  140.0    NaN  17/01/04      207
        >>>

        # Example 3: Create a function to get the values in 'accounts' to upper case
        #            and pass it to udf as parameter to create a user defined function.
        >>> from teradataml.dataframe.functions import udf
        >>> def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>> upper_case = udf(to_upper)
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(upper_stats = upper_case('accounts'))
        >>> res
                    Feb    Jan    Mar    Apr  datetime upper_stats
        accounts                                                    
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC
        >>>
    
        # Example 4: Create a user defined function to add 4 to the 'datetime' column
        #            and store the result in DATE type column.
        >>> from teradatasqlalchemy.types import DATE
        >>> import datetime
        >>> @udf(returns=DATE())
        ... def add_date(x, y):
        ...     return (datetime.datetime.strptime(x, "%y/%m/%d")+datetime.timedelta(y)).strftime("%y/%m/%d")
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date('datetime', 4))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  new_date
        accounts                                                  
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  17/01/08
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  17/01/08
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  17/01/08
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  17/01/08
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  17/01/08
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  17/01/08

        # Example 5: Create a user defined function to add 4 to the 'datetime' column
        #            without passing returns argument.
        >>> from teradatasqlalchemy.types import DATE
        >>> import datetime
        >>> @udf
        ... def add_date(x, y):
        ...     return (datetime.datetime.strptime(x, "%y/%m/%d")+datetime.timedelta(y))
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date('datetime', 4))
        >>> res
                      Feb    Jan    Mar    Apr  datetime             new_date
        accounts                                                             
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  2017-01-08 00:00:00
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  2017-01-08 00:00:00
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  2017-01-08 00:00:00
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  2017-01-08 00:00:00
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  2017-01-08 00:00:00
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  2017-01-08 00:00:00

        # Example 6: Create a two user defined function to 'to_upper' and 'sum',
        #            'to_upper' to get the values in 'accounts' to upper case and 
        #            'sum' to add length of string values in column 'accounts' 
        #            with column 'Feb' and store the result in Integer type column.
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        >>> from teradatasqlalchemy.types import INTEGER
        >>> @udf(returns=INTEGER()) 
        ... def sum(x, y):
        ...     return len(x)+y
        >>>
        # Assign the both Column Expression returned by user defined functions
        # to the DataFrame.
        >>> res = df.assign(upper_stats = to_upper('accounts'), len_sum = sum('accounts', 'Feb'))
        >>> res
                      Feb    Jan    Mar    Apr  datetime upper_stats  len_sum
        accounts                                                             
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC       98
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC      207
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC      100
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC      209
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC      220
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO      218
        >>>

        # Example 7: Convert the values is 'accounts' column to upper case using a user 
        #            defined function on Vantage Cloud Lake.
        # Create a Python 3.10.5 environment with given name and description in Vantage.
        >>> env = create_env('test_udf', 'python_3.10.5', 'Test environment for UDF')
        User environment 'test_udf' created.
        >>>
        # Create a user defined functions to 'to_upper' to get the values in upper case 
        # and pass the user env to run it on.
        >>> from teradataml.dataframe.functions import udf
        >>> @udf(env_name = env)
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> df.assign(upper_stats = to_upper('accounts'))
                    Feb    Jan    Mar    Apr  datetime upper_stats
        accounts                                                    
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04    ALPHA CO
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04    BLUE INC
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  YELLOW INC
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   JONES LLC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  ORANGE INC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04     RED INC

        # Example 8: Create a user defined function to add 4 to the 'datetime' column
        #            and store the result in DATE type column on Vantage Cloud Lake.
        >>> from teradatasqlalchemy.types import DATE
        >>> import datetime
        >>> @udf(returns=DATE())
        ... def add_date(x, y):
        ...     return (datetime.datetime.strptime(x, "%Y-%m-%d")+datetime.timedelta(y)).strftime("%Y-%m-%d")
        >>>
        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date('datetime', 4))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  new_date
        accounts                                                  
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  17/01/08
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  17/01/08
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  17/01/08
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  17/01/08
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  17/01/08
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  17/01/08
        >>>

        # Example 9: Define a function 'inner_add_date' inside the udf to create a 
        #            date object by passing year, month, and day and add 1 to that date.
        #            Call this function inside the user defined function.
        >>> @udf
        ... def add_date(y,m,d):
        ... import datetime
        ... def inner_add_date(y,m,d):
        ...     return datetime.date(y,m,d) + datetime.timedelta(1)
        ... return inner_add_date(y,m,d)

        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(new_date = add_date(2021, 10, 5))
        >>> res
                    Feb    Jan    Mar    Apr  datetime    new_date
        accounts                                                    
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04  2021-10-06
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04  2021-10-06
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04  2021-10-06
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04  2021-10-06
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04  2021-10-06
        Red Inc     200.0  150.0  140.0    NaN  17/01/04  2021-10-06
        >>>

        # Example 10: Define a user defined function 'sentiment_analysis' to perform
        #             sentiment analysis on the 'review' column using VADER.
        #             Note - Cache the model in UDF using 'td_buffer' to avoid loading 
        #             the model every time the UDF is called.

        # Load the data to run the example.
        >>> from teradataml import *
        >>> load_example_data("sentimentextractor", "sentiment_extract_input")
        >>> df = DataFrame("sentiment_extract_input")

        # Create the environment and install the required library.
        >>> env = create_env('text_analysis', 'python_3.10', 'Test environment for UDF')
        >>> env.install_lib('vaderSentiment')

        # Create a user defined function to perform sentiment analysis.
        >>> from teradatasqlalchemy.types import VARCHAR
        >>> @udf(env_name = env, returns = VARCHAR(80),  delimiter='|')
        ... def sentiment_analysis(txt):
        ...    if 'vader_model' not in td_buffer:
        ...        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        ...        td_buffer['vader_model'] = SentimentIntensityAnalyzer()
        ...    sid_obj = td_buffer['vader_model']
        ...
        ...    sentiment_dict = sid_obj.polarity_scores(txt)
        ...    if sentiment_dict['compound'] >= 0.05 :
        ...        sentiment = "Positive"
        ...    elif sentiment_dict['compound'] <= - 0.05 :
        ...        sentiment = "Negative"
        ...    else :
        ...        sentiment = "Neutral"
        ...    return sentiment

        # Assign the Column Expression returned by user defined function
        # to the DataFrame.
        >>> res = df.assign(sentiment = sentiment_analysis('review'))
        >>> res = res.select(["id", "product", "sentiment"])
        >>> res
           id       product sentiment
        0   5           gps  Positive
        1   9    television  Negative
        2   8        camera  Negative
        3  10        camera  Negative
        4   1        camera  Positive
        5   4           gps  Positive
        6   2  office suite  Positive
        7   7           gps  Negative
        8   6           gps  Negative
        9   3        camera  Positive
        >>>
    """

    allowed_datatypes = TeradataTypes.TD_ALL_TYPES.value
    # Validate datatypes in returns.
    _Validators._validate_function_arguments([["returns", returns, False, allowed_datatypes]])
    
    # Notation: @udf(returnType=INTEGER())
    if user_function is None:
        def wrapper(f):
            def func_(*args):
                return _SQLColumnExpression(expression=None, udf=f, udf_type=returns, udf_args=args,\
                                            env_name=env_name, delimiter=delimiter, quotechar=quotechar, debug=debug)
            return func_
        return wrapper
    # Notation: @udf
    else:
        def func_(*args):
            return _SQLColumnExpression(expression=None, udf=user_function, udf_type=returns, udf_args=args,\
                                        env_name=env_name, delimiter=delimiter, quotechar=quotechar, debug=debug)
    return func_


def register(name, user_function, returns=VARCHAR(1024)):
    """
    DESCRIPTION:
        Registers a user defined function (UDF).

        Notes: 
            1. Date and time data types must be formatted to supported formats.
               (See Requisite Input and Output Structures in Open Analytics Framework for more details.)
            2. On VantageCloud Lake, user defined function is registered by default in the 'openml_env' environment.
               User can register it in their own user environment, using the 'openml_user_env' configuration option.

    PARAMETERS:
        name:
            Required Argument.
            Specifies the name of the user defined function to register.
            Types: str

        user_function:
            Required Argument.
            Specifies the user defined function to create a column for
            teradataml DataFrame.
            Types: function, udf
            Note:
                Lambda functions are not supported. Re-write the lambda function as regular Python function to use with UDF.

        returns:
            Optional Argument.
            Specifies the output column type used to register the user defined function.
            Note:
                * If 'user_function' is a udf, then return type of the udf is used as return type
                  of the registered user defined function.
            Default Value: VARCHAR(1024)
            Types: teradatasqlalchemy types object

    RETURNS:
        None

    RAISES:
        TeradataMLException, TypeError

    EXAMPLES:
        # Example 1: Register the user defined function to get the values upper case.
        >>> from teradataml.dataframe.functions import udf, register
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Register the created user defined function.
        >>> register("upper_val", to_upper)
        >>>

        # Example 2: Register a user defined function to get factorial of a number and
        #            store the result in Integer type column.
        >>> from teradataml.dataframe.functions import udf, register
        >>> from teradatasqlalchemy.types import INTEGER
        >>> @udf
        ... def factorial(n):
        ...    import math
        ...    return math.factorial(n)
        >>>
        # Register the created user defined function.
        >>> register("fact", factorial, INTEGER())
        >>>

        # Example 3: Register a Python function to get the values upper case.
        >>> from teradataml.dataframe.functions import register
        >>> def to_upper(s):
        ...     return s.upper()
        >>>
        # Register the created Python function.
        >>> register("upper_val", to_upper)
        >>>
    """

    # Validate the arguments.
    arg_matrix = []
    allowed_datatypes = TeradataTypes.TD_ALL_TYPES.value
    arg_matrix.append(["returns", returns, True, allowed_datatypes])
    arg_matrix.append(["name", name, False, str])
    _Validators._validate_function_arguments(arg_matrix)

    function = []
    # Check if the user_function is Python function or
    # a user defined function(udf) or ColumnExpression returned by udf.
    if isinstance(user_function, ColumnExpression):
        function.append(user_function._udf)
        returns = user_function._type
    elif "udf.<locals>" not in user_function.__qualname__:
        function.append(user_function)
    else:
        user_function = user_function.__call__()
        function.append(user_function._udf)
        returns = user_function._type

    # Create a dictionary of user defined function name to return type.
    returns = {name: _create_return_type(returns)}

    exec_mode = 'REMOTE' if UtilFuncs._is_lake() else 'IN-DB'

    tbl_operators = _TableOperatorUtils([],
                                        None,
                                        "register",
                                        function,
                                        exec_mode,
                                        chunk_size=None,
                                        num_rows=1,
                                        delimiter=None,
                                        quotechar=None,
                                        data_partition_column=None,
                                        data_hash_column=None,
                                        style = "csv",
                                        returns = returns,
                                        )

    # Install the file on the lake/enterprise environment.
    if exec_mode == 'REMOTE':
        _Validators._check_auth_token("register")
        env_name = UtilFuncs._get_env_name()
        tbl_operators.__env = get_env(env_name)
        tbl_operators.__env.install_file(tbl_operators.script_path, suppress_output=True, replace=True)
    else:
        install_file(file_identifier=tbl_operators.script_base_name,
                        file_path=tbl_operators.script_path,
                        suppress_output=True, replace=True)


def call_udf(udf_name, func_args = () , **kwargs):
    """
    DESCRIPTION:
        Call a registered user defined function (UDF).

        Notes: 
            1. Packages required to run the registered user defined function must be installed in remote user 
               environment using install_lib method of UserEnv class. Import statements of these
               packages should be inside the user defined function itself.
            2. On VantageCloud Lake, user defined function runs by default in the 'openml_env' environment.
               User can use their own user environment, using the 'openml_user_env' configuration option.

    PARAMETERS:
        udf_name:
            Required Argument.
            Specifies the name of the registered user defined function.
            Types: str

        func_args:
            Optional Argument.
            Specifies the arguments to pass to the registered UDF.
            Default Value: ()
            Types: tuple

        delimiter:
            Optional Argument.
            Specifies a delimiter to use when reading columns from a row and
            writing result columns.
            Notes:
                * This argument cannot be same as "quotechar" argument.
                * This argument cannot be a newline character.
                * Use a different delimiter if categorial columns in the data contains
                  a character same as the delimiter.
            Default Value: ','
            Types: one character string

        quotechar:
            Optional Argument.
            Specifies a character that forces input of the user function
            to be quoted using this specified character.
            Using this argument enables the Analytics Database to
            distinguish between NULL fields and empty strings.
            A string with length zero is quoted, while NULL fields are not.
            Notes:
                * This argument cannot be same as "delimiter" argument.
                * This argument cannot be a newline character.
            Default Value: None
            Types: one character string

    RETURNS:
        ColumnExpression

    RAISES:
        TeradataMLException

    EXAMPLES:
        # Load the data to run the example.
        >>> load_example_data("dataframe", "sales")

        # Create a DataFrame on 'sales' table.
        >>> import random
        >>> dfsales = DataFrame("sales")
        >>> df = dfsales.assign(id = case([(df.accounts == 'Alpha Co', random.randrange(1, 9)),
        ...                           (df.accounts == 'Blue Inc', random.randrange(1, 9)),
        ...                           (df.accounts == 'Jones LLC', random.randrange(1, 9)),
        ...                           (df.accounts == 'Orange Inc', random.randrange(1, 9)),
        ...                           (df.accounts == 'Yellow Inc', random.randrange(1, 9)),
        ...                           (df.accounts == 'Red Inc', random.randrange(1, 9))]))

        # Example 1: Register and Call the user defined function to get the values upper case.
        >>> from teradataml.dataframe.functions import udf, register, call_udf
        >>> @udf
        ... def to_upper(s):
        ...     if s is not None:
        ...         return s.upper()
        >>>
        # Register the created user defined function with name "upper".
        >>> register("upper", to_upper)
        >>>
        # Call the user defined function registered with name "upper" and assign the
        # ColumnExpression returned to the DataFrame.
        >>> res = df.assign(upper_col = call_udf("upper", ('accounts',)))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  id   upper_col
        accounts
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04   4  YELLOW INC
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04   2    ALPHA CO
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   5   JONES LLC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04   3     RED INC
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04   1    BLUE INC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04   4  ORANGE INC
        >>>

        # Example 2: Register and Call user defined function to get factorial of a number
        #            and store the result in Integer type column.
        >>> from teradataml.dataframe.functions import udf, register
        >>> @udf(returns = INTEGER())
        ... def factorial(n):
        ...    import math
        ...    return math.factorial(n)
        >>>
        # Register the created user defined function with name "fact".
        >>> from teradatasqlalchemy.types import INTEGER
        >>> register("fact", factorial)
        >>>
        # Call the user defined function registered with name "fact" and assign the
        # ColumnExpression returned to the DataFrame.
        >>> res = df.assign(fact_col = call_udf("fact", ('id',)))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  id  fact_col
        accounts
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   5       120
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04   4        24
        Red Inc     200.0  150.0  140.0    NaN  17/01/04   3         6
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04   1         1
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04   2         2
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04   4        24
        >>>

        # Example 3: Register and Call the Python function to get the values upper case.
        >>> from teradataml.dataframe.functions import register, call_udf
        >>> def to_upper(s):
        ...     return s.upper()
        >>>
        # Register the created Python function with name "upper".
        >>> register("upper", to_upper, returns = VARCHAR(1024))
        >>>
        # Call the Python function registered with name "upper" and assign the
        # ColumnExpression returned to the DataFrame.
        >>> res = df.assign(upper_col = call_udf("upper", ('accounts',)))
        >>> res
                      Feb    Jan    Mar    Apr  datetime  id   upper_col
        accounts
        Yellow Inc   90.0    NaN    NaN    NaN  17/01/04   4  YELLOW INC
        Alpha Co    210.0  200.0  215.0  250.0  17/01/04   2    ALPHA CO
        Jones LLC   200.0  150.0  140.0  180.0  17/01/04   5   JONES LLC
        Red Inc     200.0  150.0  140.0    NaN  17/01/04   3     RED INC
        Blue Inc     90.0   50.0   95.0  101.0  17/01/04   1    BLUE INC
        Orange Inc  210.0    NaN    NaN  250.0  17/01/04   4  ORANGE INC
        >>>
    """
    env = None
    delimiter = kwargs.pop('delimiter', ',')
    quotechar = kwargs.pop('quotechar', None)
    unknown_args = list(kwargs.keys())
    if len(unknown_args) > 0:
        raise TypeError(Messages.get_message(MessageCodes.UNKNOWN_ARGUMENT,
                                                "call_udf", unknown_args[0]))

    if UtilFuncs._is_lake():
        _Validators._check_auth_token("call_udf")
        env = get_env(UtilFuncs._get_env_name())
        file_list = env.files
        if file_list is None:
            raise TeradataMlException(Messages.get_message(
            MessageCodes.FUNC_EXECUTION_FAILED, "'call_udf'", "No UDF is registered with the name '{}'.".format(udf_name)),
                                MessageCodes.FUNC_EXECUTION_FAILED)
        file_column = 'File'
    else:
        file_list = list_files().to_pandas()
        file_column = 'Files'

    # Get the script name from the environment that starts with tdml_udf_name_<udf_name>_.
    script_file = [file for file in file_list[file_column] if file.startswith('tdml_udf_name_{}_udf_type_'.format(udf_name))]
    if len(script_file) != 1:
        raise TeradataMlException(Messages.get_message(
        MessageCodes.FUNC_EXECUTION_FAILED, "'call_udf'", "Multiple UDFs or no UDF is registered with the name '{}'.".format(udf_name)),
                                MessageCodes.FUNC_EXECUTION_FAILED)

    script_name = script_file[0]
    # Get the return type from the script name.
    x = re.search(r"tdml_udf_name_{}_udf_type_([A-Z_]+)(\d*)_register".format(udf_name), script_name)
    returns = getattr(tdsqlalchemy, x.group(1))
    # If the return type has length, get the length from the script name.
    returns = returns(x.group(2)) if x.group(2) else returns()

    return _SQLColumnExpression(expression=None, udf_args = func_args, udf_script = script_name, udf_type=returns,\
                                 delimiter=delimiter, quotechar=quotechar, env_name=env)


def list_udfs(show_files=False):
    """
    DESCRIPTION:
        List all the UDFs registered using 'register()' function.

    PARAMETERS:
        show_files:
            Optional Argument.
            Specifies whether to show file names or not.
            Default Value: False
            Types: bool

    RETURNS:
        Pandas DataFrame containing files and it's details or
        None if DataFrame is empty.

    RAISES:
        TeradataMLException.

    EXAMPLES:
        # Example 1: Register the user defined function to get the values in lower case,
                     then list all the UDFs registered.
        >>> @udf
        ... def to_lower(s):
        ...   if s is not None:
        ...        return s.lower()

        # Register the created user defined function.
        >>> register("lower", to_lower)

        # List all the UDFs registered
        >>> list_udfs(True)
        id      name  return_type                                          file_name
         0     lower  VARCHAR1024  tdml_udf_name_lower_udf_type_VARCHAR1024_register.py
         1     upper  VARCHAR1024  tdml_udf_name_upper_udf_type_VARCHAR1024_register.py
         2  add_date         DATE   tdml_udf_name_add_date_udf_type_DATE_register.py
         3  sum_cols      INTEGER  tdml_udf_name_sum_cols_udf_type_INTEGER_register.py
        >>>
    """

    if UtilFuncs._is_lake():
        _Validators._check_auth_token("list_udfs")
        env_name = UtilFuncs._get_env_name()
        _df = get_env(env_name).files
        if _df is not None:
            # rename the existing DataFrame Column
            _df.rename(columns={'File': 'Files'}, inplace=True)
            _df = _df[_df['Files'].str.startswith('tdml_udf_') & _df['Files'].str.endswith('_register.py')][['Files']]
            if len(_df) == 0:
                print("No files found in remote user environment {}.".format(env_name))
            else:
                return _create_udf_dataframe(_df, show_files)

    else:
        _df = list_files()
        _df = _df[_df['Files'].startswith('tdml_udf_') & _df['Files'].endswith('_register.py')].to_pandas()
        if len(_df) == 0:
            print("No files found in Vantage")
        else:
            return _create_udf_dataframe(_df, show_files)

def _create_udf_dataframe(pandas_df, show_files=False):
    """
    DESCRIPTION:
        Internal function to return pandas DataFrame with
        column names "id", "name", "return_type", "filename".

    PARAMETERS:
        pandas_df:
            Required Argument.
            Specifies the pandas DataFrame containing one column 'Files'.
            Types: pandas DataFrame

        show_files:
            Optional Argument.
            Specifies whether to show file names or not.
            Types: bool

    RETURNS:
        pandas DataFrame.

    EXAMPLES:
        >>> _create_udf_dataframe(pandas_dataframe)

    """
    _lists = pandas_df.values.tolist()
    _data = {"id": [], "name": [], "return_type": []}
    if show_files:
        _data.update({"file_name": []})

    for _counter, _list in enumerate(_lists):
        # Extract udf name and type "tdml_udf_name_fact_udf_type_VARCHAR1024_register.py" -> ['fact', 'VARCHAR1024']
        value = _list[0][14:-12].split('_udf_type_')
        _data["id"].append(_counter)
        _data["name"].append(value[0])
        _data["return_type"].append(value[1])
        if show_files:
            _data["file_name"].append(_list[0])
    return pd.DataFrame(_data)


def deregister(name, returns=None):
    """
    DESCRIPTION:
        Deregisters a user defined function (UDF).

    PARAMETERS:
        name:
            Required Argument.
            Specifies the name of the user defined function to deregister.
            Types: str

        returns:
            Optional Argument.
            Specifies the type used to deregister the user defined function.
            Types: teradatasqlalchemy types object

    RETURNS:
        None

    RAISES:
        TeradataMLException.

    EXAMPLES:
        # Example 1: Register the user defined function to get the values in lower case,
        #            then deregister it.
        >>> @udf
        ... def to_lower(s):
        ...   if s is not None:
        ...        return s.lower()

        # Register the created user defined function.
        >>> register("lower", to_lower)

        # List all the UDFs registered
        >>> list_udfs(True)
        id      name  return_type                                          file_name
         0     lower  VARCHAR1024  tdml_udf_name_lower_udf_type_VARCHAR1024_register.py
         1     upper  VARCHAR1024  tdml_udf_name_upper_udf_type_VARCHAR1024_register.py
         2  add_date         DATE   tdml_udf_name_add_date_udf_type_DATE_register.py
         3  sum_cols      INTEGER  tdml_udf_name_sum_cols_udf_type_INTEGER_register.py
        >>>

        # Deregister the created user defined function.
        >>> deregister("lower")

        # List all the UDFs registered
        >>> list_udfs(True)
        id      name  return_type                                          file_name
         0     upper  VARCHAR1024  tdml_udf_name_upper_udf_type_VARCHAR1024_register.py
         1  add_date         DATE   tdml_udf_name_add_date_udf_type_DATE_register.py
         2  sum_cols      INTEGER  tdml_udf_name_sum_cols_udf_type_INTEGER_register.py
        >>>

        # Example 2: Deregister only specified udf function with it return type.
        >>> @udf(returns=FLOAT())
        ... def sum(x, y):
        ...    return len(x) + y

        # Deregister the created user defined function.
        >>> register("sum", sum)

        # List all the UDFs registered
        >>> list_udfs(True)
        id name return_type                                       file_name
         0  sum       FLOAT    tdml_udf_name_sum_udf_type_FLOAT_register.py
         1  sum     INTEGER  tdml_udf_name_sum_udf_type_INTEGER_register.py
         >>>

        # Deregister the created user defined function.
        >>> from teradatasqlalchemy import FLOAT
        >>> deregister("sum", FLOAT())

        # List all the UDFs registered
        >>> list_udfs(True)
        id name return_type                                       file_name
         0  sum     INTEGER  tdml_udf_name_sum_udf_type_INTEGER_register.py
         >>>
    """
    _df = list_udfs(show_files=True)
    # raise Exception list_udfs  when DataFrame is empty
    if _df is None:
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                       "'deregister'",
                                                       f"UDF '{name}' does not exist."),
                                  MessageCodes.FUNC_EXECUTION_FAILED)

    if returns is None:
        _df = _df[_df['file_name'].str.startswith(f'tdml_udf_name_{name}_udf_type_')]
    else:
        _df = _df[_df['file_name'].str.startswith(f'tdml_udf_name_{name}_udf_type_{_create_return_type(returns)}_register.py')]

    if len(_df) == 0:
        raise TeradataMlException(Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                       "'deregister'",
                                                       f"UDF '{name}' does not exist."),
                                  MessageCodes.FUNC_EXECUTION_FAILED)

    _df = _df.values.tolist()

    # Remove the file on the lake/enterprise environment.
    if UtilFuncs._is_lake():
        env = get_env(UtilFuncs._get_env_name())
        for file_name in _df:
            env.remove_file(file_name[3], suppress_output=True)
    else:
        for file_name in _df:
            remove_file(file_name[3][:-3], force_remove = True, suppress_output = True)


def _create_return_type(returns):
    """
    DESCRIPTION:
        Internal function to return string representation of
        type "returns" in such a way it is included in file name.

    PARAMETERS:
        returns:
            Required Argument.
            Specifies the teradatasqlalchemy types object.
            Types: teradatasqlalchemy types object

    RETURNS:
        string

    EXAMPLES:
        >>> _create_udf_dataframe(VARCHAR(1024))
        'VARCHAR1024'
    """
    if isinstance(returns, (VARCHAR, CLOB, CHAR)):
        # If the length is not provided, set it to empty string.
        str_len = str(returns.length) if returns.length else ""
        return_str = str(returns) + str_len
    else:
        return_str = str(returns)
    # Replace the space with underscore in the return type.
    return_str = return_str.replace(" ", "_")
    return return_str

def td_range(start, end=None, step=1):
    """
    DESCRIPTION:
        Creates a DataFrame with a specified range of numbers.

        Notes: 
            1. The range is inclusive of the start and exclusive of the end.
            2. If only start is provided, then end is set to start and start is set to 0.
        
    PARAMETERS:
        start:
            Required Argument.
            Specifies the starting number of the range.
            Types: int

        end:
            Optional Argument.
            Specifies the end number of the range(exclusive).
            Default Value: None
            Types: int

        step:
            Optional Argument.
            Specifies the step size of the range.
            Default Value: 1
            Types: int

    RETURNS:
        teradataml DataFrame

    RAISES:
        TeradataMlException

    EXAMPLES:
            # Example 1: Create a DataFrame with a range of numbers from 0 to 5.
            >>> from teradataml.dataframe.functions import td_range
            >>> df = td_range(5)
            >>> df.sort('id')
               id
            0   0
            1   1
            2   2
            3   3
            4   4

            # Example 2: Create a DataFrame with a range of numbers from 5 to 1 with step size of -2.
            >>> from teradataml.dataframe.functions import td_range
            >>> td_range(5, 1, -2)
               id
            0   3
            1   5

            >>> Example 3: Create a DataFrame with a range of numbers from 1 to 5 with default step size of 1.
            >>> from teradataml.dataframe.functions import td_range
            >>> td_range(1, 5)
               id
            0   3
            1   4
            2   2
            3   1
        
    """
    # Validate the arguments.
    arg_matrix = []
    arg_matrix.append(["start", start, False, int])
    arg_matrix.append(["end", end, True, int])
    arg_matrix.append(["step", step, True, int])
    _Validators._validate_function_arguments(arg_matrix)

    # If only start is provided, then set end to start and start to 0.
    if end is None:
        end = start
        start = 0

    # If start is greater than end, then set the operation to "-" and operator to ">".
    # If end is less than start, then set the operation to "+" and operator to "<".
    if end < start:
        operation, operator, step = "-", ">", -step
    else:
        operation, operator = "+", "<"

    # Create a temporary table with the start value.
    table_name = UtilFuncs._generate_temp_table_name(prefix="tdml_range_df",
                                    table_type=TeradataConstants.TERADATA_TABLE)
    execute_sql(f"CREATE MULTISET TABLE {table_name} AS (SELECT {start} AS id) WITH DATA;")
    
    # Create a DataFrame from the range query.
    range_query = TableOperatorConstants.RANGE_QUERY.value \
                        .format(table_name, step, end, operation, operator)
    df = DataFrame.from_query(range_query)
    return df

def current_date(time_zone='local'):
    """
    DESCRIPTION:
        Returns the current date based on the specified time zone.

    PARAMETERS:
        time_zone:
            Optional Argument.
            Specifies the time zone to use for retrieving the current date.
            Permitted Values:
                - "local": Uses the local time zone.
                - Any valid time zone string.
            Default Value: "local"
            Types: str

    RETURNS:
        ColumnExpression.

    RAISES:
        None

    EXAMPLES:
        # Example 1: Add a new column to the DataFrame that contains the
        #            current date as its value. Consider system specified
        #            timezone as timezone.
        >>> from teradataml.dataframe.functions import current_date
        >>> load_example_data('dataframe', 'sales')
        >>> df = DataFrame("sales")
        >>> df.assign(current_date=current_date())
            accounts        Feb    Jan    Mar    Apr      datetime    current_date
            Alpha Co      210.0  200.0    215    250    04/01/2017        25/05/27
            Blue Inc       90.0     50     95    101    04/01/2017        25/05/27
           Jones LLC      200.0    150    140    180    04/01/2017        25/05/27
          Orange Inc      210.0   None   None    250    04/01/2017        25/05/27
          Yellow Inc       90.0   None   None   None    04/01/2017        25/05/27
             Red Inc      200.0    150    140   None    04/01/2017        25/05/27

        # Example 2: Add a new column to the DataFrame that contains the
        #            current date in a specific time zone as its value.
        >>> from teradataml.dataframe.functions import current_date
        >>> load_example_data('dataframe', 'sales')
        >>> df = DataFrame("sales")
        >>> df.assign(current_date=current_date("GMT"))
            accounts        Feb    Jan    Mar    Apr      datetime    current_date
            Alpha Co      210.0  200.0    215    250    04/01/2017        25/05/27
            Blue Inc       90.0     50     95    101    04/01/2017        25/05/27
           Jones LLC      200.0    150    140    180    04/01/2017        25/05/27
          Orange Inc      210.0   None   None    250    04/01/2017        25/05/27
          Yellow Inc       90.0   None   None   None    04/01/2017        25/05/27
             Red Inc      200.0    150    140   None    04/01/2017        25/05/27

    """
    if time_zone == "local":
        expr_ = "CURRENT_DATE AT LOCAL"
    else:
        expr_ = "CURRENT_DATE AT TIME ZONE '{}'".format(time_zone)
    return _SQLColumnExpression(literal_column(expr_), type = DATE())

def current_timestamp(time_zone='local'):
    """
    DESCRIPTION:
        Returns the current timestamp based on the specified time zone.

    PARAMETERS:
        time_zone:
            Optional Argument.
            Specifies the time zone to use for retrieving the current timestamp.
            Permitted Values:
                - "local": Uses the local time zone.
                - Any valid time zone string.
            Default Value: "local"
            Types: str

    RETURNS:
        ColumnExpression.

    RAISES:
        None

    EXAMPLES:
        # Example 1: Assign the current timestamp in the local time zone to a DataFrame column.
        >>> from teradataml.dataframe.functions import current_timestamp
        >>> load_example_data('dataframe', 'sales')
        >>> df = DataFrame("sales")
        >>> df.assign(current_timestamp = current_timestamp())
          accounts      Feb    Jan    Mar    Apr      datetime                  current_timestamp
          Alpha Co    210.0    200    215    250    04/01/2017   2025-05-27 17:36:56.750000+00:00
          Blue Inc     90.0     50     95    101    04/01/2017   2025-05-27 17:36:56.750000+00:00
         Jones LLC    200.0    150    140    180    04/01/2017   2025-05-27 17:36:56.750000+00:00
        Orange Inc    210.0   None   None    250    04/01/2017   2025-05-27 17:36:56.750000+00:00
        Yellow Inc     90.0   None   None   None    04/01/2017   2025-05-27 17:36:56.750000+00:00
           Red Inc    200.0    150    140   None    04/01/2017   2025-05-27 17:36:56.750000+00:00
        
        # Example 2: Assign the current timestamp in a specific time zone to a DataFrame column.
        >>> from teradataml.dataframe.functions import current_timestamp
        >>> load_example_data('dataframe', 'sales')
        >>> df = DataFrame("sales")
        >>> df.assign(current_timestamp = current_timestamp("GMT+10"))
          accounts      Feb    Jan    Mar    Apr      datetime                  current_timestamp
          Blue Inc     90.0     50     95    101    04/01/2017   2025-05-28 03:39:00.790000+10:00
           Red Inc    200.0    150    140   None    04/01/2017   2025-05-28 03:39:00.790000+10:00
        Yellow Inc     90.0   None   None   None    04/01/2017   2025-05-28 03:39:00.790000+10:00
         Jones LLC    200.0    150    140    180    04/01/2017   2025-05-28 03:39:00.790000+10:00
        Orange Inc    210.0   None   None    250    04/01/2017   2025-05-28 03:39:00.790000+10:00
          Alpha Co    210.0    200    215    250    04/01/2017   2025-05-28 03:39:00.790000+10:00

    """

    if time_zone == "local":
        expr_ = "CURRENT_TIMESTAMP AT LOCAL"
    else:
        expr_ = "CURRENT_TIMESTAMP AT TIME ZONE '{}'".format(time_zone)
    return _SQLColumnExpression(literal_column(expr_), type = TIMESTAMP())

def get_formatters(formatter_type = None):
        """
        DESCRIPTION:
            Function to get the formatters for NUMERIC, DATE and CHAR types.
        
        PARAMETERS:
            formatter_type:
                Optional Argument.
                Specifies the category of formatter to format data.
                Default Value: None
                Permitted values:
                    "NUMERIC" - Formatters to convert given data to a numeric type.
                    "DATE" - Formatters to convert given data to a date type.
                    "CHAR" - Formatters to convert given data to a character type.
                Types: str
        RAISES:
            ValueError
        
        RETURNS:    
            None

        EXAMPLES:
            # Example 1: Get the formatters for the NUMERIC type.
            >>> from teradataml.dataframe.functions import get_formatters
            >>> get_formatters("NUMERIC")

        """
        numeric_formatters = """
            Formatters to convert given data to a Numeric type:
            +--------------------------------------------------------------------------------------------------+
            |    FORMATTER                             DESCRIPTION                                             |
            +--------------------------------------------------------------------------------------------------+
            |    , (comma)                             A comma in the specified position.                      |
            |                                          A comma cannot begin a number format.                   |
            |                                          A comma cannot appear to the right of a decimal         |
            |                                          character or period in a number format.                 |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "1,234"            "9,999"           1234     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    . (period)                            A decimal point. Only one allowed in a format.          |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "12.34"            "99.99"          12.34     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    $                                     A value with a leading dollar sign.                     |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "$1234"            "$9999"           1234     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    0                                     Leading or trailing zeros.                              |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "0123"             "0999"            123      | |
            |                                              |   "1230"             "9990"            1230     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    9                                     Specified number of digits.                             |
            |                                          Leading space if positive, minus if negative.           |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    "1234"            "9999"            1234     | |
            |                                              |   "-1234"            "9999"           -1234     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    B                                     Blanks if integer part is zero.                         |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    "0"               "B9999"             0      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    C                                     ISO currency symbol (from SDF ISOCurrency).             |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "USD123"            "C999"             123    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    D                                     Radix separator for non-monetary values.                |
            |                                          From SDF RadixSeparator.                                |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "12.34"            "99D99"           12.34    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    EEEE                                  Scientific notation.                                    |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "1.2E+04"         "9.9EEEE"          12000    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    G                                     Group separator for non-monetary values.                |
            |                                          From SDF GroupSeparator.                                |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "1,234,567"       "9G999G999"       1234567   | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    L                                     Local currency (from SDF Currency element).             |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "$123"             "L999"              123    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MI                                    Trailing minus sign if value is negative.               |
            |                                          Can only appear in the last position.                   |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |   "1234-"            "9999MI"          -1234    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    PR                                    Negative value in angle brackets.                       |
            |                                          Positive value with leading/trailing blank.             |
            |                                          Only in the last position.                              |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    " 123 "          "9999PR"            123     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    S                                     Sign indicator: + / - at beginning or end.              |
            |                                          Can only appear in first or last position.              |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    "-1234"           "S9999"           -1234    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    U                                     Dual currency (from SDF DualCurrency).                  |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    "$123"             "U999"             123    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    X                                     Hexadecimal format.                                     |
            |                                          Accepts only non-negative values.                       |
            |                                          Must be preceded by 0 or FM.                            |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    "FF"                "XX"             255     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            """

        date_formatters = """
            Formatters to convert given data to a Date type:
            +--------------------------------------------------------------------------------------------------+
            |    FORMATTER                             DESCRIPTION                                             |
            +--------------------------------------------------------------------------------------------------+
            |    -                                                                                             |
            |    /                                                                                             |
            |    ,                                     Punctuation characters are ignored and text enclosed in |
            |    .                                     quotation marks is ignored.                             |
            |    ;                                                                                             |
            |    :                                                                                             |
            |    "text"                                                                                        |
            |                                         Example: Date with value '2003-12-10'                    |
            |                                              +-------------------------------------------------+ |
            |                                              | data             formatter          value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | '2003-12-10'     YYYY-MM-DD         03/12/10    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    D                                     Day of week (1-7).                                      |
            |                                          Example: day of week with value '2'                     |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2               D                   24/01/01    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DAY	                               Name of day.                                            |
            |                                          Example: Date with value '2024-TUESDAY-01-30'           |
            |                                              +-------------------------------------------------+ |
            |                                              | data                formatter         value     | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024-TUESDAY-01-30   YYYY-DAY-MM-DD   24/01/30  | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DD                                    Day of month (1-31).                                    |
            |                                          Example: Date with value '2003-10-25'                   |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2003-10-25       YYYY-MM-DD         03/10/25    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DDD	                               Day of year (1-366).                                    |
            |                                          Example: Date with value '2024-366'                     |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024-366       YYYY-DDD             24/12/31    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DY                                    abbreviated name of day.                                |
            |                                          Example: Date with value '2024-Mon-01-29'               |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024-Mon-01-29   YYYY-DY-MM-DD   24/01/29       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    HH                                                                                            |
            |    HH12                                 Hour of day (1-12).                                      |
            |                                          Example: Date with value '2016-01-06 09:08:01'          |
            |                                              +-------------------------------------------------+ |
            |                                              | data                formatter            value  | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01 YYYY-MM-DD HH:MI:SS  6/01/06| |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    HH24	                              Hour of the day (0-23).                                  |
            |                                          Example:  Date with value '2016-01-06 23:08:01'         |
            |                                           +----------------------------------------------------+ |
            |                                           | data                formatter              value   | |
            |                                           +----------------------------------------------------+ |
            |                                           | 2016-01-06 23:08:01 YYYY-MM-DD HH24:MI:SS  6/01/06 | |
            |                                           +----------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    J                                    Julian day, the number of days since January 1, 4713 BC. |
            |                                         Number specified with J must be integers.                |
            |                                         Teradata uses the Gregorian calendar in calculations to  |
            |                                         and from Julian Days.                                    |
            |                                          Example: Number of julian days with value '2457394'     |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2457394         J                   16/01/06    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MI                                   Minute (0-59).                                           |
            |                                          Example: Date with value '2016-01-06 23:08:01'          |
            |                                           +----------------------------------------------------+ |
            |                                           | data                formatter              value  | |
            |                                           +----------------------------------------------------+ |
            |                                           | 2016-01-06 23:08:01 YYYY-MM-DD HH24:MI:SS  6/01/06 | |
            |                                           +----------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MM                                   Month (01-12).                                           |
            |                                          Example: Date with value '2016-01-06 23:08:01'          |
            |                                           +----------------------------------------------------+ |
            |                                           | data                formatter              value  | |
            |                                           +----------------------------------------------------+ |
            |                                           | 2016-01-06 23:08:01 YYYY-MM-DD HH24:MI:SS  6/01/06 | |
            |                                           +----------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MON	                              Abbreviated name of month.                               |
            |                                          Example: Date with value '2016-JAN-06'                  |
            |                                           +----------------------------------------------------+ |
            |                                           | data                formatter              value   | |
            |                                           +----------------------------------------------------+ |
            |                                           | 2016-JAN-06         YYYY-MON-DD           16/01/06 | |
            |                                           +----------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MONTH	                              Name of month.                                           |
            |                                          Example: Date with value '2016-JANUARY-06'              |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter              value    | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-JANUARY-06  YYYY-MONTH-DD         16/01/06 | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    PM                                                                                            |
            |    P.M.                                 Meridian indicator.                                      |
            |                                          Example:  Date with value '2016-01-06 23:08:01 PM'      |
            |                                      +---------------------------------------------------------+ |
            |                                      | data                   formatter                value   | |
            |                                      +---------------------------------------------------------+ |
            |                                      | 2016-01-06 23:08:01 PM YYYY-MM-DD HH24:MI:SS PM 16/01/06| |
            |                                      +---------------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    RM                                   Roman numeral month (I - XII).                           |
            |                                          Example: Date with value '2024-XII'                     |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024-XII       YYYY-RM             24/12/01     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    RR                                   Stores 20th century dates in the 21st century using only |
            |                                         2 digits. If the current year and the specified year are |
            |                                         both in the range of 0-49, the date is in the current    |
            |                                         century.                                                 |
            |                                         Example: Date with value '2024-365, 21'                  |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024-365, 21      YYYY-DDD, RR      21/12/31    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    RRRR	                              Round year. Accepts either 4-digit or 2-digit input.     |
            |                                         2-digit input provides the same return as RR.            |
            |                                          Example: Date with value '2024-365, 21'                  |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024-365, 21       YYYY-DDD, RRRR   24/12/31    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    SS                                   Second (0-59).                                           |
            |                                          Example: Date with value '2016-01-06 23:08:01'          |
            |                                           +----------------------------------------------------+ |
            |                                           | data                formatter              value   | |
            |                                           +----------------------------------------------------+ |
            |                                           | 2016-01-06 23:08:01 YYYY-MM-DD HH24:MI:SS  6/01/06 | |
            |                                           +----------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    SSSSS	                              Seconds past midnight (0-86399).                         |
            +--------------------------------------------------------------------------------------------------+
            |    TZH	                              Time zone hour.                                          |
            +--------------------------------------------------------------------------------------------------+
            |    TZM	                              Time zone minute.                                        |
            +--------------------------------------------------------------------------------------------------+
            |    X                                    Local radix character.                                   |
            |                                         Example: Date with value '2024.366'                      |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024.366       YYYYXDDD             24/12/31    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    Y,YYY	                              Year with comma in this position.                        |
            |                                          Example: Date with value '2,024-366'                    |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2,024-366       Y,YYY-DDD           24/12/31    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    YYYY                                                                                          |
            |    SYYYY                                4-digit year. S prefixes BC dates with a minus sign.     |
            |                                          Example: Date with value '2024-366'                     |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter           value       | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2024-366       YYYY-DDD             24/12/31    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    YYY                                  Last 3, 2, or 1 digit of year.                           |
            |    YY                                   If the current year and the specified year are both in   |
            |    Y                                    the range of 0-49, the date is in the current century.   |
            |                                          Example: Date with value '24-366'                       |
            |                                              +-------------------------------------------------+ |
            |                                              | data            formatter       value           | |
            |                                              +-------------------------------------------------+ |
            |                                              | 24-366       YY-DDD             24/12/31        | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            """

        char_formatters = """
            Formatters to convert given data to a Char type:
            +--------------------------------------------------------------------------------------------------+
            |    FORMATTER                             DESCRIPTION                                             |
            +--------------------------------------------------------------------------------------------------+
            |    , (comma)                             A comma in the specified position.                      |
            |                                          A comma cannot begin a number format.                   |
            |                                          A comma cannot appear to the right of a decimal         |
            |                                          character or period in a number format.                 |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             9,999             1,234     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |   . (period)                             A decimal point.                                        |
            |                                          User can only specify one period in a number format.    |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    123.46             9999.9             123.5  | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    $                                     A value with a leading dollar sign.                     |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             $9999              $1234    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    0                                     Leading zeros.                                          |
            |                                          Trailing zeros.                                         |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             09999              01234    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    9                                     A value with the specified number of digits with a      |
            |                                          leading space if positive or with a leading minus       |
            |                                          if negative.                                            |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             9999              1234      | |
            |                                              |    1234             999               ####      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    B                                     Blank space for the integer part of a fixed point number|
            |                                          when the integer part is zero.                          |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    0.1234             B.999          Blank space| |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    C                                     The ISO currency symbol as specified in the ISOCurrency |
            |                                          element in the SDF file.                                |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    234              C999              USD234    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    D                                     The character that separates the integer and fractional |
            |                                          part of non-monetary values.                            |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    234.56           999D9             234.6     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    EEEE                                  A value in scientific notation.                         |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    234.56           9.9EEEE             2.3E+02 | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    G                                     The character that separates groups of digits in the    |
            |                                          integer part of non-monetary values.                    |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    123456           9G99G99           1,234,56  | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    L                                     The string representing the local currency as specified |
            |                                          in the Currency element according to system settings.   |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    234              L999              $234      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MI                                    A trailing minus sign if the value is negative.         |
            |                                          The MI format element can appear only in the last       |
            |                                          position of a number format.                            |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    -1234            9999MI            1234-     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    PR                                    A negative value in <angle brackets>, or                |
            |                                          a positive value with a leading and trailing blank.     |
            |                                          The PR format element can appear only in the last       |
            |                                          position of a number format.                            |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    -1234            9999PR            <1234>    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    S                                     A negative value with a leading or trailing minus sign. |
            |                                          a positive value with a leading or trailing plus sign.  |
            |                                          The S format element can appear only in the first or    |
            |                                          last position of a number format.                       |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    +1234            S9999             +1234     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    TM                                    (text minimum format) Returns the smallest number of    |
            |                                          characters possible. This element is case insensitive.  |
            |                                          TM or TM9 return the number in fixed notation unless    |
            |                                          the output exceeds 64 characters. If the output exceeds |
            |                                          64 characters, the number is returned in scientific     |
            |                                          notation.                                               |
            |                                          TME returns the number in scientific notation with the  |
            |                                          smallest number of characters.                          |
            |                                          You cannot precede this element with an other element.  |
            |                                          You can follow this element only with one 9 or one E    |
            |                                          (or e), but not with any combination of these.          |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             TM                1234      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    U                                    (dual currency) The string that represents the dual     |
            |                                          currency as specified in the DualCurrency element       |
            |                                          according to system settings.                           |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             U9999             $1234     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    V                                     A value multiplied by 10 to the n (and, if necessary,   |
            |                                          rounded up), where n is the number of 9's after the V.  |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             9999V99           123400    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    X                                     The hexadecimal value of the specified number of digits.|
            |                                          If the specified number is not an integer, the function |
            |                                          will round it to an integer.                            |
            |                                          This element accepts only positive values or zero.      |
            |                                          Negative values return an error. You can precede this   |
            |                                          element only with zero (which returns leading zeros) or |
            |                                          FM. Any other elements return an error. If you do not   |
            |                                          specify zero or FM, the return always has one leading   |
            |                                          blank.                                                  |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    1234             XXXX              4D2       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            +--------------------------------------------------------------------------------------------------+
            |    FORMATTER                             DESCRIPTION                                             |
            +--------------------------------------------------------------------------------------------------+
            |    -                                                                                             |
            |    /                                                                                             |
            |    ,                                     Punctuation characters are ignored and text enclosed in |
            |    .                                     quotation marks is ignored.                             |
            |    ;                                                                                             |
            |    :                                                                                             |
            |    "text"                                                                                        |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         MM-DD             09-17     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    AD                                    AD indicator.                                           |
            |    A.D.                                                                                          |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         CCAD              21AD      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    AM                                    Meridian indicator.                                     |
            |    A.M.                                                                                          |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         CCAM              21AM     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    BC                                                                                            |
            |    B.C.                                  BC indicator.                                           |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         CCBC              21BC      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    CC                                    Century.                                                |
            |    SCC                                   If the last 2 digits of a 4-digit year are between 01   |
            |                                          and 99 inclusive, the century is 1 greater than the     |
            |                                          first 2 digits of that year.                            |
            |                                          If the last 2 digits of a 4-digit year are 00, the      |
            |                                          century is the same as the first 2 digits of that year. |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         CCBC              21BC      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    D                                     Day of week (1-7).                                      |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         D                 4         | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DAY	                               Name of day.                                            |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         DAY               WEDNESDAY | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DD                                    Day of month (1-31).                                    |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         DD                17        | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DDD                                   Day of year (1-366).                                    |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         DDD               260       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DL                                    Date Long. Equivalent to the format string ‘FMDay,      |
            |                                          Month FMDD, YYYY’.                                      |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              | data       formatter         result             | |
            |                                              +-------------------------------------------------+ |
            |                                              | 03/09/17   DL      Wednesday, September 17, 2003| |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DS                                    Date Short. Equivalent to the format string             |
            |                                          ‘FMMM/DD/YYYYFM’.                                       |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         DS                9/17/2003 | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    DY                                    abbreviated name of day.                                |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              |    data             formatter         result    | |
            |                                              +-------------------------------------------------+ |
            |                                              |    03/09/17         DY                WED       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    FF                                    [1..9]	Fractional seconds.                            |
            |                                          Use [1..9] to specify the number of fractional digits.  |
            |                                          FF without any number following it prints a decimal     |
            |                                          followed by digits equal to the number of fractional    |
            |                                          seconds in the input data type. If the data type has no |
            |                                          fractional digits, FF prints nothing.                   |
            |                                          Any fractional digits beyond 6 digits are truncated.    |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  FF         000000   | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    HH                                                                                            |
            |    HH12                                 Hour of day (1-12).                                      |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  HH         09       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    HH24	                              Hour of the day (0-23).                                  |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  HH24         09     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    IW                                   Week of year (1-52 or 1-53) based on ISO model.          |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  IW         01       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    IYY                                                                                           |
            |    IY                                   Last 3, 2, or 1 digits of ISO year.                      |
            |    I                                                                                             |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  IY         16       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    IYYY	                              4-digit year based on the ISO standard.                  |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  IYYY         2016   | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    J                                    Julian day, the number of days since January 1, 4713 BC. |
            |                                         Number specified with J must be integers.                |
            |                                         Teradata uses the Gregorian calendar in calculations to  |
            |                                         and from Julian Days.                                    |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  J          2457394  | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MI                                   Minute (0-59).                                           |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  MI         08       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MM                                   Month (01-12).                                           |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  MM         01       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MON	                              Abbreviated name of month.                               |
            |                                          Example:                                                |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  MON        JAN      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    MONTH	                              Name of month.                                           |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  MONTH      JANUARY  | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    PM                                                                                            |
            |    P.M.                                 Meridian indicator.                                      |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  HHPM       09PM     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    Q                                    Quarter of year (1, 2, 3, 4).                            |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  Q       1           | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    RM                                   Roman numeral month (I - XII).                           |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  RM         I        | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    SP                                   Spelled. Any numeric element followed by SP is spelled in|
            |                                         English words. The words are capitalized according to how|
            |                                         the element is capitalized.                              |
            |                                         For example: 'DDDSP' specifies all uppercase, 'DddSP'    |
            |                                         specifies that the first letter is capitalized, and      |
            |                                         'dddSP' specifies all lowercase.                         |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  HHSP       NINE     | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    SS                                   Second (0-59).                                           |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  SS         03       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    SSSSS	                              Seconds past midnight (0-86399).                         |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  SSSSS      32883    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    TS                                   Time Short. Equivalent to the format string              |
            |                                         'HH:MI:SS AM'.                                           |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  TS     09:08:01 AM  | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    TZH	                              Time zone hour.                                          |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  TZH        +00      | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    TZM	                              Time zone minute.                                        |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  TZM        00       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    TZR	                              Time zone region. Equivalent to the format string        |
            |                                         'TZH:TZM'.                                               |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  TZR        +00:00   | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    WW                                   Week of year (1-53) where week 1 starts on the first day |
            |                                         of the year and continues to the 7th day of the year.    |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  WW         01       | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    W                                    Week of month (1-5) where week 1 starts on the first day |
            |                                         of the month and ends on the seventh.                    |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  W          1        | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    X                                    Local radix character.                                   |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  MMXYY      01.16    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    Y,YYY	                              Year with comma in this position.                        |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                        formatter  result   | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  Y,YYY      2,016    | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    YEAR                                 Year, spelled out. S prefixes BC dates with a minus sign.|
            |    SYEAR                                                                                         |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                     formatter  result      | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  YEAR  TWENTY SIXTEEN| |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    YYYY                                                                                          |
            |    SYYYY                                4-digit year. S prefixes BC dates with a minus sign.     |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                     formatter  result      | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  YYYY    2016        | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            |    YYY                                  Last 3, 2, or 1 digit of year.                           |
            |    YY                                   If the current year and the specified year are both in   |
            |    Y                                    the range of 0-49, the date is in the current century.   |
            |                                         Example:                                                 |
            |                                              +-------------------------------------------------+ |
            |                                              | data                     formatter  result      | |
            |                                              +-------------------------------------------------+ |
            |                                              | 2016-01-06 09:08:01.000000  YY      16          | |
            |                                              +-------------------------------------------------+ |
            +--------------------------------------------------------------------------------------------------+
            """
        # Validate formatter_type
        if formatter_type not in [None, "NUMERIC", "DATE", "CHAR"]:
            raise ValueError(
                "formatter_type must be one of 'NUMERIC', 'DATE', 'CHAR' or None."
            )
        if formatter_type is None:
            formatter = (
                numeric_formatters
                + "\n\n"
                + date_formatters
                + "\n\n"
                + char_formatters
                + "\n\n"
            )
        elif formatter_type == "NUMERIC":
            formatter = numeric_formatters
        elif formatter_type == "DATE":
            formatter = date_formatters
        elif formatter_type == "CHAR":
            formatter = char_formatters
        print(formatter)
