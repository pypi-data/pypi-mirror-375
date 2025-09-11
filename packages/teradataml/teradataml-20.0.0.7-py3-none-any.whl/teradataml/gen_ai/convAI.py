# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Kesavaragavan B (kesavaragavan.b@teradata.com)
# Secondary Owner: Prafulla V Tekawade (prafulla.tekawade@teradata.com)
#
# This file implements tdmlAI and DBChain which is used for Vantage 
# database interaction. The tdmlAI manages LLM inference endpoints and
# DBChain enables interaction between user, Vantage database.
# Notes: 
#   * This code is only for internal use. 
#   * The code may perform modify, create, or delete operations 
#     in database based on given query. Hence, limit the permissions 
#     granted to the credentials.
# 
# ##################################################################

# Import required packages.
import openai
import os
from langchain.llms import AzureOpenAI
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts.prompt import PromptTemplate
from teradataml import get_context, get_connection
from teradataml.utils.validators import _Validators

def _set_openAI(api_key, api_type, api_base, api_version):
    """
        DESCRIPTION:
            Internal function to set environment variables for AzureAI.
            
        PARAMETERS:
            api_key:
                Required Argument.
                Specifies the AzureAI API key.
                Types: str

            api_type:
                Required Argument.
                Specifies the AzureAI API type.
                Types: str
            
            api_base:
                Required Argument.
                Specifies the AzureAI API base url.
                Types: str

            api_version:
                Required Argument.
                Specifies the AzureAI API version.
                Types: str

        RETURNS:
            None

        RAISES:
           None

        EXAMPLES:
            _set_openAI(api_type = "azure"
                        api_base = "https://***.openai.azure.com/"
                        api_version = "2021-12-35"
                        api_key = "999***")
        """
    # Set API type.
    os.environ["OPENAI_API_TYPE"] = api_type
    # Set API version like follow "2022-06-10".
    os.environ["OPENAI_API_VERSION"] = api_version
    # Set API Base URL as follow 
    # "https://****instance.openai.azure.com/".
    os.environ["OPENAI_API_BASE"] = api_base
    # Set API key.
    os.environ["OPENAI_API_KEY"] = api_key     


class tdmlAI:
    """tdmlAI provides convenient access to the LLM endpoints for inference."""

    def __init__(self,api_key, 
                 api_type,
                 api_base, 
                 api_version, 
                 engine,
                 model_name):
        """
        DESCRIPTION:
            Constructor of tdmlAI that sets up the environment and 
            initializes the LLM endpoint.
            
        PARAMETERS:
            api_key:
                Required Argument.
                Specifies the LLM API key.
                Types: str

            api_type:
                Required Argument.
                Specifies the LLM API type.
                Types: str
            
            api_base:
                Required Argument.
                Specifies the LLM API base url.
                Types: str

            api_version:
                Required Argument.
                Specifies the LLM API version.
                Types: str                       
                  
            engine:
                Required Argument.
                Specifies the deployment name of the LLM.
                Types: str           

            model_name:
                Required Argument.
                Specifies the LLM model name.
                Types: str

        RETURNS:
            None

        RAISES:
            TeradataMlException, ValueError, TypeError

        EXAMPLES:
            # Import the modules.
            from teradataml.gen_ai.convAI import tdmlAI
            # Create LLM endpoint.
            tdml_ai_obj = tdmlAI(api_type = "azure",
                     api_base = "https://****.openai.azure.com/",
                     api_version = "2000-11-35",
                     api_key = <provide your llm API key>,
                     engine = <provide your llm engine name>,
                     model_name = "gpt-3.5-turbo")
        """

        # Argument validations
        awu_matrix = []
        awu_matrix.append(["api_key", api_key, False, (str)])
        awu_matrix.append(["api_type", api_type, False, (str)])
        awu_matrix.append(["api_base", api_base, False, (str)])
        awu_matrix.append(["api_version", api_version, False, (str)])
        awu_matrix.append(["engine", engine, False, (str)])
        awu_matrix.append(["model_name", model_name, False, (str)])
        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        # Set API type.
        self.api_type = api_type
        # Set API Base URL as follow 
        # "https://****instance.openai.azure.com/".
        self.api_base = api_base
        # Set API version like follow "2022-06-10".
        self.api_version = api_version
        # Set API key.
        self.api_key = api_key
        # Set LLM engine name.
        self.__engine = engine
        # Set model name.
        self.model_name = model_name

        # Update environment and openai variables.
        self.__set_llm_env()

        # Initialize AzureOpenAI LLM. 
        self._llm = AzureOpenAI(engine=self.__engine, model_name=self.model_name)


    def __set_llm_env(self):
        """
        DESCRIPTION:
            Internal function to set all LLM info in OS environment and 
            openai variables.
            
        PARAMETERS:
            None
        
        RETURNS:
            None

        RAISES:
           None

        EXAMPLES:
            self.__set_llm_env()
        """
        # Set API type.
        openai.api_type = self.api_type
        # Set API Base URL as follow 
        openai.api_base = self.api_base 
        # Set API version.
        openai.api_version = self.api_version
        # Set API key.
        openai.api_key = self.api_key 
        # Update OS environment variables.
        _set_openAI(api_type=self.api_type, api_base=self.api_base, 
                    api_version=self.api_version, api_key=self.api_key)
        
        
    def get_llm(self):
        """
        DESCRIPTION:
            Get LLM inference endpoint.
            
        PARAMETERS:
            None
        
        RETURNS:
            LLM endpoint object.

        RAISES:
           None

        EXAMPLES:
            tdml_ai_obj.get_llm()
        """
        return self._llm
    

    def answer(self, query):
        """
        DESCRIPTION:
            Get the answer to the query.
            
        PARAMETERS:
            query:
                Required Argument.
                Specifies the question which needs to be answered by LLM.
                Types: str
        
        RETURNS:
            str

        RAISES:
            TeradataMlException, ValueError

        EXAMPLES:
            tdml_ai_obj.run("Tell me a joke")
        """
        awu_matrix = []
        awu_matrix.append(["query", query, False, (str)])
        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)
        return self._llm(query)
    

class DBChain(tdmlAI):
    """Class manages database chain and communication between user, database, and LLM."""
    # Prompt to retrieve the answer with high accuracy.
    __DEFAULT_TEMPLATE = """
        You are a Teradata Vantage DataBase expert. Given an input question, 
        first create a syntactically correct Teradata query to run, 
        then look at the results of the query and return the answer to 
        the input question. Unless the user specifies in the question a specific 
        number of examples to obtain, query for at most 2 results using the LIMIT 
        clause as per Teradata SQL query. You can order the results to return the most 
        informative data in the database. Never query for all columns from a table. 
        You must query only the columns that are needed to answer the question. 
        Wrap each column name in double quotes (") to denote them as delimited identifiers.
        
        Pay attention to use only the column names you can see in the tables below. 
        Be careful to not query for columns that do not exist. Also, pay attention 
        to which column is in which table.
        Pay attention to select correct table names and column names for teradatasql query generation.

        Given an input question, first create a syntactically correct teradatasql query 
        to run, then look at the results of the query and return the answer.
        Use the following format:

        Question: "Question here"
        SQLQuery: "SQL Query to run"
        SQLResult: "Result of the SQLQuery"
        Answer: "Final answer here"

        Only use the following tables:

        {table_info}

        If someone asks to list out tables present in 'DBC' DataBase user, 
        then following is an example teradatasql query for 'DBC' user:
        SQL Query:      SELECT  TableName,
                        FROM    DBC.TablesV
                        WHERE   TableKind = 'T'
                        and     DatabaseName = 'DBC'
                        ORDER BY  TableName; 


        Question: {input}"""

    def __init__(self, llm, include_tables=None, verbose=False, ignore_tdml_prompt=False):        
        """
        DESCRIPTION:
            Constructor of DBChain that sets up interaction channel between client (user), 
            Vantage database, and LLM endpoint.
            Notes:
                * LLM input tokens size must be greater than 1k to perform basic operations
                  and increase LLM token size based on operation complexity.
                * Establish connection with Vantage before initializing DBChain.
            
        PARAMETERS:
            llm:
                Required Argument.
                Specifies the LLM endpoint object for inference.
                Types: tdmlAI

            include_tables:
                Optional Argument.
                Specifies the table names to be included for interaction.
                When a list of tables is provided, DBChain gives the 
                highest priority to those tables for data exploration.
                Otherwise, entire database tables present in Vantage is taken 
                into account for data exploration.
                Notes:
                    * List of tables has to be provided for more 
                      accurate results.
                    * Provide list of tables When LLM input token size is 
                      less than 4k.
                    * Views present in database may cause inconsistent result when
                      include_tables are not provided.
                Types: list of str
            
            verbose:
                Optional Argument.
                Specifies whether to display the interaction between LLM and Vantage.
                Default Value: False
                Types: bool

            ignore_tdml_prompt:
                Optional Argument.
                Specifies wether to ignore tdml engineered prompt design.
                When "ignore_tdml_prompt" is set to True then tdml engineered 
                prompt is ignored. Otherwise, prompt is used for accurate results.
                Notes:
                    * Custom engineered prompt is used for higher accurate results.
                    * Set "ignore_tdml_prompt" to True when LLM contains limitation on 
                      input token size.
                Default Value: False
                Types: bool

        RETURNS:
            TeradataMlException, ValueError, TypeError

        RAISES:
           None

        EXAMPLES:
            # Import the modules.
            from teradataml.gen_ai.convAI import tdmlAI
            # Create LLM endpoint.
            tdml_ai_obj = tdmlAI(api_type = "azure",
                     api_base = "https://****.openai.azure.com/",
                     api_version = "2000-11-35",
                     api_key = <provide your llm API key>,
                     engine=<provide your llm engine name>,
                     model_name="gpt-3.5-turbo")

            # Create DBChain object.
            dbchain_obj = DBChain(llm=tdml_ai_obj,verbose=False)
        """

        # Argument validations
        awu_matrix = []
        awu_matrix.append(["llm", llm, False, (tdmlAI)])
        awu_matrix.append(["include_tables", include_tables, True, (list)])
        awu_matrix.append(["verbose", verbose, True, (bool)])
        awu_matrix.append(["ignore_tdml_prompt", ignore_tdml_prompt, True, (bool)])
        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)
        # Set LLM inference endpoint used for sql query generation.
        self._llm = llm.get_llm()
        # Set table names needs to be explored.
        self._table_names = include_tables
        # Set verbose to display intermediate steps.
        self._verbose = verbose
        # Database custom prompt to improve the SQL generation accuracy.
        self.__PROMPT = PromptTemplate(
            input_variables=["input", "table_info"], template=self.__DEFAULT_TEMPLATE ) \
                if not ignore_tdml_prompt else None
        # Maintains interaction records.
        self.__records = []

        # Get all table names except views when table name is 'None'.
        if self._table_names is None:
            self.__pull_db_details()
        # set tdsqlalchemy engine.
        self.__engine = get_context()

        # Initialize SQLDatabase chain.
        self.__db = SQLDatabase(engine=self.__engine, include_tables=self._table_names)
        # Initialize SQLDatabase Chain.
        self.__db_chain = SQLDatabaseChain.from_llm(self._llm, self.__db, verbose=verbose, prompt=self.__PROMPT)


    def run(self, query):
        """
        DESCRIPTION:
            Function interact with Vantage Database using human natural 
            language.
            
        PARAMETERS:
            query:
                Required Argument.
                Specifies the question which needs to be answered by LLM.
                Query must be precise and represented in English.
                Types: str
        
        RETURNS:
            str

        RAISES:
            TeradataMlException, ValueError

        EXAMPLES:
            dbchain_obj.run("How many house present in Boston")
        """
        awu_matrix = []
        awu_matrix.append(["query", query, False, (str)])
        # Validate argument types
        _Validators._validate_function_arguments(awu_matrix)

        # Trigger the Database chain interaction.
        result = self.__db_chain.run(query)
        self.__records.append({query:result})
        # return result when verbose is set to 'False'.
        if not self._verbose:
            return result

    
    def __pull_db_details(self):
        """
        DESCRIPTION:
            Internal function to retrieve table names.

        PARAMETERS:
            None

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            self.__pull_db_details()
        """
        _connection = get_connection()
        self._table_names = _connection.dialect.get_table_names(_connection)
        
    
    def get_interaction_records(self):
        """
        DESCRIPTION:
            Get the interaction records.

        PARAMETERS:
            None

        RETURNS:
            list

        RAISES:
            None

        EXAMPLES:
            dbchain_obj.get_interaction_records()
        """
        return self.__records
        