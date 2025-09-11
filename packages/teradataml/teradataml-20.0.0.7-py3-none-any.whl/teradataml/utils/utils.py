"""
Unpublished work.
Copyright (c) 2023 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: shivani.kondewar@teradata.com
Secondary Owner: pradeep.garre@teradata.com
This includes common functionalities required
by other classes which can be reused according to the need.

"""

import functools
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, wait
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages, MessageCodes
from teradataml.common.constants import AsyncStatusColumns
from teradataml.utils.validators import _Validators
from teradatasql import OperationalError
from teradataml.utils.dtypes import _ListOf

# TODO: Add an option to set concurrency.
_td_th_executor = ThreadPoolExecutor(max_workers=4)
# Internal storage for storing information of async run ids.
_async_run_id_info = {}


def execute_sql(statement, parameters=None, ignore_errors=None):
    """
    DESCRIPTION:
        Executes the SQL statement by using provided parameters.
        Note:
            Execution of stored procedures and user defined functions is not supported.

    PARAMETERS:
        statement:
            Required Argument.
            Specifies the SQL statement to execute.
            Types: str

        parameters:
            Optional Argument.
            Specifies parameters to be used in case of parameterized query.
            Types: list of list, list of tuple

        ignore_errors:
            Optional Argument.
            Specifies the error code(s) to ignore while running the statement.
            Note:
                * Error code(s) are Teradata Vantage error codes. Not teradataml
                  error codes.
                * All errors can be ignored by setting "ignore_errors" to 'all'.
            Permitted Values:
                * all - Ignore all the errors during execution.
            Types: str, int or list of int

    RETURNS:
        Cursor object.

    RAISES:
        TeradataMlException, teradatasql.OperationalError, TypeError, ValueError

    EXAMPLES:
        # Example 1: Create a table and insert values into the table using SQL.
        # Create a table.
        execute_sql("Create table table1 (col_1 int, col_2 varchar(10), col_3 float);")

        # Insert values in the table created above.
        execute_sql("Insert into table1 values (1, 'col_val', 2.0);")

        # Insert values in the table using a parameterized query.
        execute_sql(statement="Insert into table1 values (?, ?, ?);",
                    parameters=[[1, 'col_val_1', 10.0],
                                [2, 'col_val_2', 20.0]])

        # Example 2: Execute parameterized 'SELECT' query.
        result_cursor = execute_sql(statement="Select * from table1 where col_1=? and col_3=?;",
                                    parameters=[(1, 10.0),(1, 20.0)])

        # Example 3: Run Help Column query on table.
        result_cursor = execute_sql('Help column table1.*;')

        # Example 4: Create table 'Table_xyz' with one column of type integer.
        #            Ignore the error if table already exists.
        #            Note: Teradata error code while creating duplicate table is 3804.
        result = execute_sql("Create table table_xyz (col_1 integer)", ignore_errors=[3804])

        # Example 5: Drop table 'test_table' which does not exists.
        #            Ignore all the errors if table not exists.
        result = execute_sql("drop table test_table", ignore_errors='all')

    """
    # Validate argument types
    arg_info_matrix = []
    arg_info_matrix.append(["statement", statement, False, str, True])
    arg_info_matrix.append(["parameters", parameters, True, (tuple, list), False])
    arg_info_matrix.append(["ignore_errors", ignore_errors, True, (int, _ListOf(int), str), True])

    _Validators._validate_function_arguments(arg_info_matrix)

    # Validate permitted values, if its string.
    if isinstance(ignore_errors, str):
        _Validators._validate_permitted_values(ignore_errors, ['ALL'], "ignore_errors")

    from teradataml.context.context import get_context
    if get_context() is not None:
        tdsql_con = get_context().raw_connection().driver_connection
        cursor = tdsql_con.cursor()
        # If user specifies error codes, then ignore those.
        if not isinstance(ignore_errors, str):
            return cursor.execute(statement, parameters, ignore_errors)

        try:
            return cursor.execute(statement, parameters)
        except OperationalError as oe:
            # When 'ignore_errors' is set to 'all', ignore all
            # the errors during execution.
            if ignore_errors == 'all':
                pass
            else:
                raise oe
    else:
        raise TeradataMlException(Messages.get_message(MessageCodes.INVALID_CONTEXT_CONNECTION),
                                  MessageCodes.INVALID_CONTEXT_CONNECTION)

class _AsyncDBExecutor:
    """
    An internal utility to run teradataml API's parallelly by opening
    multiple connections with Vantage.
    Note:
        The utility opens 4 parallel threads to execute the functions
        parallelly.
    """
    def __init__(self, wait=False):
        """
        DESCRIPTION:
            Constructor of the class.

        PARAMETERS:
            wait:
                Optional Argument.
                Specifies the option whether to wait for completion of all
                the threads or not. When set to True, the utility waits till
                all the corresponding threads complete. Otherwise, it executes
                all the threads in background thus making the subsequent action to
                not wait for the completion of threads.
                Default Value: False
                Type: bool

        RAISES:
            None

        EXAMPLES:
            # Example1: Execute analytic function ANOVA parallelly by passing different values
            # to parameter 'alpha'.
            load_example_data("teradataml", "insect_sprays")
            insect_sprays = DataFrame("insect_sprays")

            # Declare the parameters to run ANOVA.
            params1 = {"data": insect_sprays, "alpha": 0.05}
            params2 = {"data": insect_sprays, "alpha": 0.06}
            params3 = {"data": insect_sprays, "alpha": 0.07}
            params4 = {"data": insect_sprays, "alpha": 0.08}
            params5 = {"data": insect_sprays, "alpha": 0.09}
            params6 = {"data": insect_sprays, "alpha": 0.10}

            # Import "_Async" utility and run ANOVA with above parameters.
            from teradataml.utils.utils import _Async
            async_obj = _Async(wait=True)
            response = async_obj.submit(ANOVA, params1, params2, params3, params4, params5, params6)

            # Access the results.
            response.results()

            # Example2: Execute analytic function XGBOOST parallelly in background with
            # different parameters.
            load_example_data("teradataml", "titanic")
            titanic = DataFrame("titanic")

            # Declare the parameters to run XGBOOST.
            params1 = {"data": titanic,
                       "input_columns": ["age", "survived", "pclass"],
                       "response_column": 'fare',
                       "max_depth": 3,
                       "lambda1": 1000.0,
                       "model_type": 'Regression',
                       "seed": 1,
                       "shrinkage_factor": 0.2,
                       "iter_num": 3}
            params2 = {"data": titanic,
                       "input_columns": ["age", "survived", "pclass"],
                       "response_column": 'fare',
                       "max_depth": 3,
                       "lambda1": 1000.0,
                       "model_type": 'Regression',
                       "seed": 2,
                       "shrinkage_factor": 0.3,
                       "iter_num": 4}
            params3 = {"data": titanic,
                       "input_columns": ["age", "survived", "pclass"],
                       "response_column": 'fare',
                       "max_depth": 3,
                       "lambda1": 1000.0,
                       "model_type": 'Regression',
                       "seed": 3,
                       "shrinkage_factor": 0.4,
                       "iter_num": 5}
            params4 = {"data": titanic,
                       "input_columns": ["age", "survived", "pclass"],
                       "response_column": 'fare',
                       "max_depth": 3,
                       "lambda1": 1000.0,
                       "model_type": 'Regression',
                       "seed": 4,
                       "shrinkage_factor": 0.5,
                       "iter_num": 6}
            params5 = {"data": titanic,
                       "input_columns": ["age", "survived", "pclass"],
                       "response_column": 'fare',
                       "max_depth": 3,
                       "lambda1": 1000.0,
                       "model_type": 'Regression',
                       "seed": 5,
                       "shrinkage_factor": 0.6,
                       "iter_num": 7}
            params6 = {"data": titanic,
                       "input_columns": ["age", "survived", "pclass"],
                       "response_column": 'fare',
                       "max_depth": 3,
                       "lambda1": 1000.0,
                       "model_type": 'Regression',
                       "seed": 6,
                       "shrinkage_factor": 0.7,
                       "iter_num": 8}

            # Import "_Async" utility and run ANOVA with above parameters.
            from teradataml.utils.utils import _Async
            async_obj = _Async()
            response = async_obj.submit(XGBOOST, params1, params2, params3, params4, params5, params6)

            # Access the result for first parameter.
            response.result()

            # Access the result for second parameter.
            response.result(1)

            # Access the result for last parameter.
            response.result(5)
        """
        self.__async_runs = []
        self.__wait = wait
        # Note: Do not initiate a seperate thread pool executor.
        # That will create seperate executors for every object.
        # create_context by default uses SingletonThreadPool which
        # means every corresponding thread pool executor opens
        # sessions. Since default cap on connections is 5, this will
        # fail one or the other threads for sure. Also, along with the above
        # mentioned advantage, since the object can run in background, user
        # can invoke any number of _Async objects. Making a seperate
        # executor creates many threads and it will try to open many connections.
        # Setting the executor at global level and using the same will limit
        # the number of connections though user can call any number of _Async
        # jobs as background runs.
        self.__executor = _td_th_executor

    def submit(self, func, *parameters):
        """
        DESCRIPTION:
            Function to execute teradataml API with the parameters.
            The function can run "func" with "parameters" either in
            background or foreground based on "wait" option.

        PARAMETERS:
            func:
                Required Argument.
                Specifies the teradataml API which needs to be executed
                asynchronously.
                Type: class OR function

            parameters:
                Required Argument.
                Specifies the non keyword arguments which needs to be considered as
                input for "func". The argument accepts any number of arguments and
                every argument should be keyword argument.
                Type: tuple

        RAISES:
            None

        RETURNS:
            None
        """
        self.__async_runs.clear()
        for parameter in parameters:
            self.__async_runs.append(self.__executor.submit(func, **parameter))

        if self.__wait:
            wait(self.__async_runs)

    def is_running(self):
        """
        DESCRIPTION:
            Function to check whether all the threads are completed or not.
            The function returns True when any single thread is either
            running or about to run. It returns False when all individual
            threads are complete.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            bool
        """
        return any(async_run.running() for async_run in self.__async_runs)

    def result(self, index=0):
        """
        DESCRIPTION:
            Function to get the result for a specific parameter. Order of
            results remains same as input order.

        PARAMETERS:
            index:
                Optional Argument.
                Specifies the index to get the result.
                Default Value: 0
                Type: int

        RAISES:
            None

        RETURNS:
            Result of "func" after execution is complete.
        """
        return self.__async_runs[index].result()

    def results(self):
        """
        DESCRIPTION:
            Function to get the results.

        PARAMETERS:
            None

        RAISES:
            None

        RETURNS:
            list.
        """
        return [async_run.result() for async_run in self.__async_runs]

def async_run_status(run_ids):
    """
    DESCRIPTION:
        Function to check the status of asynchronous run(s)
        using the unique run id(s).


    PARAMETERS:
        run_ids:
            Required Argument.
            Specifies the unique identifier(s) of the asynchronous run.
            Types: str OR list of Strings (str)

    RETURNS:
        Pandas DataFrame with columns as below:
            * Run Id: Unique identifier of the asynchronous run.
            * Run Description: Description of the asynchronous run.
            * Status: Status of the asynchronous run.
            * Timestamp: Timestamp for 'status'.
            * Additional Details: Addition information of the asynchronous run.


    RAISES:
        None

    EXAMPLES:
        # Examples to showcase the status of asynchronous run ids for OpenAF.

        # Example 1: Get the status of an environment that has been removed asynchronously.
        >>> env = create_env("testenv1", "python_3.7.13","test env 1")
        User environment 'testenv1' created.
        >>> remove_env("testenv1", asynchronous=True)
        Request to remove environment initiated successfully. Check the status using list_user_envs(). If environment is not removed, check the status of asynchronous call using async_run_status('1ba43e0a-4285-41e1-8738-5f8895c180ee') or get_env('testenv1').status('1ba43e0a-4285-41e1-8738-5f8895c180ee')
        '1ba43e0a-4285-41e1-8738-5f8895c180ee'
        >>> async_run_status('1ba43e0a-4285-41e1-8738-5f8895c180ee')
                                         Run Id                      Run Description    Status             Timestamp Additional Details
        0  1ba43e0a-4285-41e1-8738-5f8895c180ee  Remove 'testenv1' user environment.   Started  2023-08-31T09:27:06Z
        1  1ba43e0a-4285-41e1-8738-5f8895c180ee  Remove 'testenv1' user environment.  Finished  2023-08-31T09:27:07Z

        # Example 2: Get the status of multiple asynchronous run ids for removed environments.
        >>> env1 = create_env("testenv1", "python_3.7.13","test env 1")
        >>> env2 = create_env("testenv2", "python_3.7.13","test env 2")
        User environment 'testenv1' created.
        User environment 'testenv2' created.

        # Remove 'testenv1' environment asynchronously.
        >>> remove_env("testenv1", asynchronous=True)
        Request to remove environment initiated successfully. Check the status using list_user_envs(). If environment is not removed, check the status of asynchronous call using async_run_status('24812988-b124-45c7-80b1-6a4a826dc110') or get_env('testenv1').status('24812988-b124-45c7-80b1-6a4a826dc110')
        '24812988-b124-45c7-80b1-6a4a826dc110'

        # Remove 'testenv2' environment asynchronously.
        >>> remove_env("testenv2", asynchronous=True)
        Request to remove environment initiated successfully. Check the status using list_user_envs(). If environment is not removed, check the status of asynchronous call using async_run_status('f686d756-58bb-448b-81e2-979155cb8140') or get_env('testenv2').status('f686d756-58bb-448b-81e2-979155cb8140')
        'f686d756-58bb-448b-81e2-979155cb8140'

        # Check the status of claim IDs for asynchronously installed libraries and removed environments.
        >>> async_run_status(['24812988-b124-45c7-80b1-6a4a826dc110', 'f686d756-58bb-448b-81e2-979155cb8140'])
                                          Run Id	                   Run Description	  Status	           Timestamp	Additional Details
        0	24812988-b124-45c7-80b1-6a4a826dc110	Remove 'testenv1' user environment.	 Started	2023-08-31T04:00:44Z
        1	24812988-b124-45c7-80b1-6a4a826dc110	Remove 'testenv1' user environment.	Finished	2023-08-31T04:00:45Z
        2	f686d756-58bb-448b-81e2-979155cb8140	Remove 'testenv2' user environment.	 Started	2023-08-31T04:00:47Z
        3	f686d756-58bb-448b-81e2-979155cb8140	Remove 'testenv2' user environment.	Finished	2023-08-31T04:00:48Z
    """
    __arg_info_matrix = []
    __arg_info_matrix.append(["run_ids", run_ids, False, (str, list), True])

    # Validate arguments.
    _Validators._validate_function_arguments(__arg_info_matrix)

    # Create thread pool executor to get the status of claim_ids parallelly.
    executor = ThreadPoolExecutor(max_workers=10)

    run_ids = [run_ids] if isinstance(run_ids, str) else run_ids

    # Store all the future object in a list.
    futures = []
    for run_id in run_ids:
        # Get the function mapped with the ID.
        func = _async_run_id_info.get(run_id, {}).get("mapped_func")
        futures.append(executor.submit(func, run_id))

    # Wait till all the futures complete.
    wait(futures)

    pd_columns = [AsyncStatusColumns.RUN_ID.value,
                  AsyncStatusColumns.RUN_DESCRIPTION.value,
                  AsyncStatusColumns.STATUS.value,
                  AsyncStatusColumns.TIMESTAMP.value,
                  AsyncStatusColumns.ADDITIONAL_DETAILS.value]
    return pd.DataFrame.from_records(
        functools.reduce(lambda x, y: x + y, (future.result() for future in futures)),
        columns=pd_columns)
