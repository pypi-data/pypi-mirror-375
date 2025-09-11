"""
Unpublished work.
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: aanchal.kavedia@teradata.com
Secondary Owner: akhil.bisht@teradata.com

This file implements VectorStore class along with its method.
"""
import base64
import json, os, pandas as pd, time, re, glob, warnings
from urllib.parse import quote
from json.decoder import JSONDecodeError
from teradataml.common.constants import HTTPRequest, TeradataConstants
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import Messages
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.utils import UtilFuncs
from teradataml.context.context import _get_user
from teradataml import DataFrame, copy_to_sql, execute_sql, in_schema
from teradataml.options.configure import configure
from teradataml.utils.validators import _Validators
from teradataml.scriptmgmt.UserEnv import _get_auth_token
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.telemetry_utils.queryband import collect_queryband
from teradatagenai.garbage_collector.garbage_collector import GarbageCollector

from teradatagenai.llm.llm import TeradataAI
from teradatagenai.common.constants import VectorStoreURLs, _Grant, _Revoke, VSApi, VSParameters, VSIndex, SimilaritySearchParams
from teradatagenai.common.messages import Messages as MessagesGenAI
from teradatagenai.common.message_codes import MessageCodes as MessageCodesGenAI
from teradatagenai.common.exceptions import TeradataGenAIException
from teradatagenai.utils.doc_decorator import docstring_handler
from teradatagenai.common.constants import VECTOR_STORE_SEARCH_PARAMS, COMMON_PARAMS, NIM_PARAMS,\
                                           FILE_BASED_VECTOR_STORE_PARAMS, UPDATE_PARAMS


# Getting VectorStoreURLs.
vector_store_urls = VectorStoreURLs()

class VSManager:
    """
    Vector store manager allows user to:
        * Perform health check for the vector store service.
        * List all the vector stores.
        * List all the active sessions of the vector store service.
        * List all available patterns for creating metadata-based vector store.
        * Disconnect from the database session.
    """
    log = False

    @classmethod
    @collect_queryband(queryband="VS_get_log")
    def get_log(cls):
        """
        DESCRIPTION:
            Get the int representation of log which is required for the API calls.

        PARAMETERS:
            None.

        RETURNS:
            int value required for API calls.

        RAISES:
            None.

        EXAMPLES:
            >>> VSManager.get_log()
        """
        return 0 if not cls.log else 1

    @staticmethod
    def _connect(**kwargs):
        """
        DESCRIPTION:
            Establishes connection to Teradata Vantage.

        PARAMETERS:
             host:
                Optional Argument.
                Specifies the fully qualified domain name or IP address of the
                Teradata System to connect to.
                Types: str

            username:
                Optional Argument.
                Specifies the username for connecting to/create a vector
                store in Teradata Vantage.
                Types: str

            password:
                Optional Argument.
                Specifies the password required for the username.
                Types: str

            database:
                Optional Argument.
                Specifies the initial database to use after logon,
                instead of the user's default database.
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            from teradatagenai import VSManager
            # Example 1: Connect to the database using host, database,
            #            username and password.
            >>> VSManager._connect(host='<host>',
                                   username='<user>',
                                   password='<password>',
                                   database='<database>')
        """
        ## Initialize connection parameters.
        host = kwargs.get("host", None)
        user = kwargs.get("username", None)
        password = kwargs.get("password", None)
        database = kwargs.get("database", _get_user())

        # get the JWT token or basic authentication token in case of username
        # and password is passed.
        headers = _get_auth_token()

        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(["host", host, True, (str), True])
        arg_info_matrix.append(["username", user, True, (str), True])
        arg_info_matrix.append(["password", password, True, (str), True])
        arg_info_matrix.append(["database", database, True, (str), True])

        if user and password:
            # Check if vector_store_base_url is set or not.
            _Validators._check_required_params(arg_value=configure._vector_store_base_url,
                                               arg_name="configure._vector_store_base_url",
                                               caller_func_name="_connect()",
                                               target_func_name="set_config_params")
        else:
            _Validators._check_required_params(arg_value=configure._vector_store_base_url,
                                               arg_name="Auth token",
                                               caller_func_name="VectorStore()",
                                               target_func_name="set_auth_token")

        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Form the header with username and password if it is non ccp enabled
        # tenant when explictly _connect is called.
        if user and password:
            # If the host and user are passed, we will set the new connection params.
            credentials = f"{user}:{password}"
            # Encode the credentials string using Base64
            encoded_credentials = base64.b64encode(
                credentials.encode('utf-8')).decode('utf-8')
            # Form the Authorization header value
            headers = {"Authorization": f"Basic {encoded_credentials}"}

        # Triggering the 'connect' API
        data = {
            'database_name': database,
            'hostname': host
        }
        # Only add arguments which are not None as
        # service accepts only non None arguments.                                                                                                        
        data = {k: v for k, v in data.items() if v is not None}

        http_params = {
            "url": vector_store_urls.session_url,
            "method_type": HTTPRequest.POST,
            "headers": headers,
            "json": data,
            "verify": configure._ssl_verify
        }

        response = UtilFuncs._http_request(**http_params)

        session_id = response.cookies.get("session_id")
        # Only add the session id if it is not None,
        # meaning when connect went through.
        if session_id:
            _InternalBuffer.add(vs_session_id=session_id)
            _InternalBuffer.add(vs_header=headers)

        VectorStore._process_vs_response(api_name="connect", response=response)

    @staticmethod
    def _generate_session_id(**kwargs):
        """
        DESCRIPTION:
            Internal function to generate or get the session_id.

        PARAMETERS:
            generate:
                Optional Argument.
                Specifies whether to generate the session_id or not.
                In case of 'disconnect()`, we do not want to generate
                the session_id again in case it is called multiple times.
                Default Value: True
                Types: bool

        RETURNS:
            dict containing the headers and the session_id.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> VSManager._generate_session_id()
        """
        # If the buffer is empty, meaning its the first call to
        # _connect, call _connect to generate the session id.
        if _InternalBuffer.get("vs_session_id") is None and kwargs.get("generate", True):
            VSManager._connect()
        # This is for cases when 'vs_session_id' is not stored in the buffer,
        # it should return None instead of returning a dict with None values.
        if _InternalBuffer.get("vs_session_id") is not None:
            return {"vs_session_id": _InternalBuffer.get("vs_session_id"),
                    "vs_header": _InternalBuffer.get("vs_header")}

    @collect_queryband(queryband="VS_list")
    @staticmethod
    def list(**kwargs):
        """
        DESCRIPTION:
            Lists all the vector stores.
            Notes:
                * Lists all vector stores if user has admin role permissions.
                * Lists vector stores permitted to the user.

        RETURNS:
            teradataml DataFrame containing the vector store details.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VSManager

            # List all the vector stores.
            >>> VSManager.list()
        """
        # Triggering the 'list_vector_stores' API
        list_vs_url = vector_store_urls.vectorstore_url
        session_header = VSManager._generate_session_id()
        response = UtilFuncs._http_request(list_vs_url, HTTPRequest.GET,
                                           cookies={'session_id': session_header["vs_session_id"]},
                                           headers=session_header["vs_header"]
                                           )
        # Process the response and return the dataframe.
        if kwargs.get("return_type", "teradataml") == "json":
            return VectorStore._process_vs_response("list_vector_stores", response)['vector_stores_list']
        data = pd.DataFrame(VectorStore._process_vs_response("list_vector_stores", response)['vector_stores_list'])
        return VectorStore._convert_to_tdmldf(data)

    @collect_queryband(queryband="VS_health")
    @staticmethod
    def health():
        """
        DESCRIPTION:
            Performs sanity check for the service.

        RETURNS:
            teradataml DataFrame containing details on the health of the service.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1: Check the health of the service.
            >>> VSManager.health()
        """
        health_url = f'{vector_store_urls.base_url}health'
        session_header = VSManager._generate_session_id()
        response = UtilFuncs._http_request(health_url, HTTPRequest.GET,
                                           headers=session_header["vs_header"])
        data = pd.DataFrame([VectorStore._process_vs_response("health", response)])
        return VectorStore._convert_to_tdmldf(data)

    @collect_queryband(queryband="VS_list_sessions")
    @staticmethod
    def list_sessions():
        """
        DESCRIPTION:
            Lists all the active sessions of the vector store service.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.
        RETURNS:
            teradataml DataFrame containing the active sessions.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VSManager

            # List all the vector stores.
            >>> VSManager.list_sessions()
        """
        session_header = VSManager._generate_session_id()
        response = UtilFuncs._http_request(f"{vector_store_urls.session_url}s",
                                           HTTPRequest.GET,
                                           cookies={'session_id': session_header["vs_session_id"]},
                                           headers=session_header["vs_header"]
                                           )
        result = _ListSessions(VectorStore._process_vs_response("list_sessions", response))
        return result

    @collect_queryband(queryband="VS_list_patterns")
    @staticmethod
    def list_patterns():
        """
        DESCRIPTION:
            Lists all the patterns in the vector store.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            None.

        RETURNS:
            teradataml DataFrame containing the patterns.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            from teradatagenai import VSManager

            # List all the patterns.
            VSManager.list_patterns()
        """
        session_header = VSManager._generate_session_id()
        response = UtilFuncs._http_request(f"{vector_store_urls.patterns_url}?log_level={VSManager.get_log()}",
                                           HTTPRequest.GET,
                                           cookies={'session_id': session_header["vs_session_id"]},
                                           headers=session_header["vs_header"]
                                           )
        data = pd.DataFrame(VectorStore._process_vs_response("list_patterns", response)['pattern_list'])
        return VectorStore._convert_to_tdmldf(data)

    @collect_queryband(queryband="VS_disconnect")
    @staticmethod
    def disconnect(session_id=None, raise_error=True):
        """
        DESCRIPTION:
            Databse session created for vector store operation is disconnected
            and corresponding underlying objects are deleted.
            Notes:
                * When 'session_id' argument is passed, only that session is
                  disconnected, else all session IDs created during the
                  current Python session are disconnected.
                * Only admin users can disconnect session
                  created by other users.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            session_id:
                Optional Argument.
                Specifies the session ID to terminate.
                If not specified all the database sessions created
                in current Python session are terminated.
                Types: str

            raise_error:
                Optional Argument.
                Specifies a boolean flag that decides whether to raise error or not.
                Default Values: True
                Types: bool

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VSManager
            # Example 1: Disconnect from the database.
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vec1")

            # Create a vector store.
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1")

            # Disconnect from the database.
            >>> VSManager.disconnect()
        """
        # Validations
        arg_info_matrix = []
        arg_info_matrix.append(["session_id", session_id, True, (str), True])
        arg_info_matrix.append(["raise_error", raise_error, True, (bool), True])

        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)
        session_header = VSManager._generate_session_id(generate=False)
        if session_header is None:
            if raise_error:
                error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                                 "disconnect",
                                                 "No active database session to disconnect.")
                raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)
            return

        if session_id:
            # Delete a user specified session.
            url = f"{vector_store_urls.session_url}s/{session_id}"
            update_internal_buffer = session_id == session_header["vs_session_id"]
            func_name = "terminate_session"
        else:
            # Delete the current active session.
            url = vector_store_urls.session_url
            update_internal_buffer = True
            func_name = "disconnect"

        response = UtilFuncs._http_request(url,
                                           HTTPRequest.DELETE,
                                           cookies={'session_id': session_header["vs_session_id"]},
                                           headers=session_header["vs_header"])
        VectorStore._process_vs_response(func_name, response, raise_error=raise_error)

        # Remove the session_id and header from the internal header.
        if update_internal_buffer and _InternalBuffer.get("vs_session_id"):
            _InternalBuffer.remove_key("vs_session_id")
            _InternalBuffer.remove_key("vs_header")

class _SimilaritySearch:
    """
    Internal class to create a similarity search object which is needed
    to display the results in a tabular format and at the same time store
    the json object which is used in prepare response.
    """
    def __init__(self, response, batch=False, **kwargs):
        """
        DESCRIPTION:
            Initializes the SimilaritySearch object.

        PARAMETERS:
            response:
                Required Argument.
                Specifies the response from the REST API.
                Types: dict

            batch:
                Optional Argument.
                Specifies whether the batch is enabled or not.
                Default Value: False
                Types: bool

            return_type:
                Optional Argument.
                Specifies the return type of similarity_search.
                By default returns a teradataml DataFrame.
                Permitted Values: "teradataml", "pandas", "json"
                Default Value: "teradataml"
                Types: str

        RETURNS:
            None.

        RAISES:
            None.
        """
        self.similar_objects_count = response['similar_objects_count']
        self._json_obj = response['similar_objects_list']
        return_type = kwargs.get('return_type')
        return_type = 'teradataml' if return_type is None else return_type.lower()
        __arg_info_matrix = [["return_type", return_type, False, str, True, ["teradataml", "pandas", "json"]]]
        # Make sure that a correct type of values has been supplied to the arguments.
        _Validators._validate_function_arguments(__arg_info_matrix)

        if return_type == "json":
            self.similar_objects = self._json_obj
        else:
            if batch:
                data = pd.DataFrame([
                {**item, "batch_id": batch_id} for batch_id, values in self._json_obj.items() for item in values
                ]).set_index("batch_id")
            else:
                data = pd.DataFrame(self._json_obj)
            self.similar_objects = VectorStore._convert_to_tdmldf(data, index=True) if return_type == "teradataml" else data

    def __repr__(self):
        return f"similar_objects_count:{self.similar_objects_count}\nsimilar_objects:\n{self.similar_objects})"

class _ListSessions:
    """
    Internal class to create a _ListSessions object which is needed
    to display the results in a readable format.
    """
    def __init__(self, response):
        self.total_active_sessions = response['count']
        self.current_session_id = response['self_session_id']
        # Currently copy_to does not support adding list into columns, hence the
        # list should be converted to str before giving it to copy_to
        response = pd.DataFrame(response['session_details'])
        response['vs_names'] = response['vs_names'].apply(lambda x: ','.join(map(str, x)))
        self.session_details = VectorStore._convert_to_tdmldf(pd.DataFrame(response))

    def __repr__(self):
        return f"total_active_sessions:{self.total_active_sessions}\n\ncurrent_session_id:\n{self.current_session_id}" \
               f"\n\nsession_details:\n{self.session_details}"

def _ProcessDataFrameObjects(obj):
    """
    DESCRIPTION:
        Processes the DataFrame objects,
        extracts fully qualified table name of each DataFrame
        and formats it based on Vector Store requirements.

    PARAMETERS:
        obj:
            Required Argument.
            Specifies the teradataml DataFrame or list of teradataml DataFrames.
            Types: teradataml DataFrame or list of teradataml DataFrames

    RETURNS:
        None or list of str.

    RAISES:
        None.
    """
    if obj is not None:
        obj = UtilFuncs._as_list(obj)
        processed_obj = []
        for obj_temp in obj:
            if _Validators._check_isinstance(obj_temp, DataFrame):
                # If table_name is None, materialize the DataFrame
                if obj_temp._table_name is None:
                    obj_temp = obj_temp.materialize()
                processed_obj.append(obj_temp._table_name.replace("\"", ""))
            else:
                processed_obj.append(obj_temp)
        return processed_obj


class VectorStore:
    _DOCUMENT_TYPES = (str, list)
    _EMBEDDINGS_TYPES = (str, TeradataAI)
    _CHAT_MODEL_TYPES = (str, TeradataAI)

    def __init__(self,
                 name=None,
                 log=False,
                 **kwargs):
        """
        DESCRIPTION:
            VectorStore contains a vectorized version of data.
            The vectorization typically is a result of embeddings generated by
            an AI LLM.
            There are two types of vector stores based on the use cases:
                * Content-based vector store: A vector store built on the
                  contents of table/view/teradataml DataFrame.
                  The table can be formed from the contents of file / pdf.
                  Questions can be asked against the contents of the table and
                  top matches of relevant rows are returned based on search.
                  This can be followed by a textual response generated using
                  an LLM by manipulating the top matches.

                * Metadata-based vector store: A vector store built on the
                  metadata of a set of tables. Questions can be asked
                  against a table or set of tables and top table
                  matches are returned.
            Notes:
                * If the vector store mentioned in the name argument
                  already exists, it is initialized for use.
                * If not, user needs to call create() to create the same.

        PARAMETERS:
            name:
                Optional Argument.
                Specifies the name of the vector store either to connect, if it
                already exists or to create a new vector store.
                Types: str

            log:
                Optional Argument.
                Specifies whether logging should be enabled for vector store
                methods.
                Note:
                    In case of any errors, by default it will be written
                    in datadog even if logging not enabled.
                Default Value: False
                Types: bool

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> vs = VectorStore(name="vs", log=True)
        """
        # Initialize variables.
        self.name = name
        self._log = log
        self.store_type = None
        self._database = None
        self.exists = False
        # Validating name and log.
        arg_info_matrix = []
        arg_info_matrix.append(["name", self.name, True, (str), True])
        arg_info_matrix.append(["log", self._log, True, (bool)])

        # As the rest call accepts 0, 1 converting it.
        self._log = 0 if not self._log else 1
        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)
        
        # Check if vector_store_base_url is set or not.
        _Validators._check_required_params(arg_value=configure._vector_store_base_url,
                                           arg_name="Auth token",
                                           caller_func_name="VectorStore()",
                                           target_func_name="set_auth_token")

        # Call connect in case of CCP enabled tenant.
        # If non-ccp, connect should be explicitly called passing the required params.
        session_header = VSManager._generate_session_id()
        self.__session_id = session_header["vs_session_id"]
        self.__headers = session_header["vs_header"]

        if self.name is not None:
            vs_name = self.name.lower()
            self.__set_urls()
            # Check if the vector store exists by calling the list API and validating for the name.
            try:
                vs_list = VSManager.list(return_type="json")
            except Exception as e:
                if 'No authorized vector stores found for the user' in str(e):
                    vs_list = pd.DataFrame(columns=["vs_name", "description", "target_database"])
                else:
                    raise e

            # Check for the name in the list.
            for vs in vs_list:
                if vs_name == vs['vs_name'].lower():
                    # If status does not contain keyword 'FAILED' and Vector Store is there in
                    # the dict, then initialize it for the session
                    # Vector Store entry exists
                    self.exists = True
                    if 'FAILED' not in vs['vs_status']:
                        print(f"Vector store {self.name} is initialized.")
                    else:
                        # This means some operation failed and hence print which operation failed.
                        warnings.warn(f"Vector Store {self.name} has status '{vs['vs_status']}'."
                                      f" Take the appropriate action before moving ahead.")
                    # Store the type of vector store and the database which it resides in for further processing.
                    self.store_type = vs['store_type']
                    # Setting a different parameter other than target_database
                    # because if we pass target_database it takes as if we are updating it.
                    self._database = vs['database_name']
                    break

            if not self.exists:
                # Otherwise, it does not exist and guide the user to create it.
                warnings.warn(f"Vector Store {self.name} does not exist. Call create() to create the same.")
        else:
            warnings.warn(f"Vector Store class is initialized without a name. "
                          f"Make sure to call create() with appropriate parameters.")
    def __set_urls(self):
        """
        DESCRIPTION:
            Internal method to set the common URLs for VectorStore.

        PARAMETERS:
            None.

        RETURNS:
            None

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")
            >>> vs.__set_urls()
        """
        # Create all the REST API urls.
        self.__url = f'{vector_store_urls.vectorstore_url}/{self.name}'
        self.__common_url = f'{self.__url}?log_level={self._log}'
        self.__list_user_permission_url = f'{vector_store_urls.base_url}permissions/{self.name}'
        self.__similarity_search_url = '{0}/similarity-search?question={1}&log_level={2}'
        self.__similarity_search_embeddings_url = '{0}/similarity-search?log_level={1}'

        self.__prepare_response_url = f'{self.__url}/prepare-response?log_level={self._log}'
        self.__ask_url = f'{self.__url}/ask?log_level={self._log}'
        self.__set_user_permissions_url = "{0}permissions/{1}?user_name={2}&action={3}&permission={4}&log_level={5}"
        self.__get_objects_url = f"{self.__url}?get_object_list=true&log_level={self._log}"
        self.__get_details_url = f"{self.__url}?get_details=true&log_level={self._log}"
        self.__batch_url = '{0}/{1}?log_level={2}'

    @property
    def exists(self):
        if self.name is not None:
            vs_list = VSManager.list(return_type="json")
            for vs in vs_list:
                if self.name.lower() == vs['vs_name'].lower():
                    self.__exists = True
            return self.__exists
        else:
            warnings.warn(f"Vector Store class is initialized without a name. "
                          f"Make sure to call create() with appropriate parameters.")

    @exists.setter
    def exists(self, value):
        self.__exists = value

    @staticmethod
    def _process_documents_object(documents):
        return documents
    
    @staticmethod
    def _process_embeddings_object(embedding):
        """
        DESCRIPTION:
            Internal method to process the embeddings object.

        PARAMETERS:
            embedding:
                Required Argument.
                Specifies the embedding model name or TeradataAI 
                embedding object.
                Types: str or TeradataAI object

        RETURNS:
            str

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1:
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore()
            >>> vs.__process_embeddings_object(embedding="amazon.titan-embed-text-v1")

            # Example 2:
            # Create an instance of the TeradataAI class.
            >>> from teradatagenai import TeradataAI
            >>> llm_embedding = TeradataAI(api_type = "aws",
                                           model_name = "amazon.titan-embed-text-v2:0")
            >>> vs.__process_embeddings_object(embedding=llm_embedding)
        """
        #TODO: https://teradata-pe.atlassian.net/browse/ELE-8082
        if isinstance(embedding, str):
            return embedding
        elif isinstance(embedding, TeradataAI):
            return embedding.model_name
    
    @staticmethod
    def _process_chat_model_object(chat_completion_model):
        """
        DESCRIPTION:
            Internal method to process the chat completions model object.

        PARAMETERS:
            chat_completion_model:
                Required Argument.
                Specifies the chat completions model name or TeradataAI
                chat model object.
                Types: str or TeradataAI object

        RETURNS:
            str

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1:
            # Pass the chat model name as a string.
            >>> vs = VectorStore()
            >>> vs._process_chat_model_object(chat_completion_model="anthropic.claude-instant-v1")

            # Example 2:
            # Create an instance of the TeradataAI class.
            >>> from teradatagenai import TeradataAI
            >>> llm_chat_model = TeradataAI(api_type = "aws",
                                           model_name = "anthropic.claude-3-haiku-20240307-v1:0")
            >>> vs._process_chat_model_object(chat_completion_model=llm_chat_model)
        """
        if isinstance(chat_completion_model, str):
            return chat_completion_model
        elif isinstance(chat_completion_model, TeradataAI):
            return chat_completion_model.model_name
    
    def _process_datasets_operation(self, data, operation, **kwargs):
        """
        DESCRIPTION:
            Common helper method for processing dataset operations (add/delete).
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the name of the tables or teradataml DataFrames to be processed.
                Types: str, DataFrame, or list of str/DataFrame
            
            operation:
                Required Argument.
                Specifies the operation type ("ADD" or "DELETE").
                Types: str
            
            **kwargs:
                Optional keyword arguments passed to update method.
        
        RETURNS:
            None.
        
        RAISES:
            TeradataMlException.
        """
        # Validate the arguments.
        arg_info_matrix = [
            ["data", data, False, (str, list, DataFrame), True],
        ]
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        kwargs["object_names"] = data
        kwargs["alter_operation"] = operation

        self.update(**kwargs)

    def _process_documents_operation(self, documents, operation, **kwargs):
        """
        DESCRIPTION:
            Common helper method for processing document operations (add/delete).
        
        PARAMETERS:
            documents:
                Required Argument.
                Specifies the files to be processed in the Vector Store.
                Types: str, list
            
            operation:
                Required Argument.
                Specifies the operation type ("ADD" or "DELETE").
                Types: str
            
            **kwargs:
                Optional keyword arguments passed to update method.
        
        RETURNS:
            None.
        
        RAISES:
            TeradataMlException.
        """

        arg_info_matrix = [
            ["documents", documents, False, self._DOCUMENT_TYPES, True],
        ]
        _Validators._validate_function_arguments(arg_info_matrix)

        # Process inputs.
        processed_docs = self._process_documents_object(documents)

        # If inputs is pdf set processed docs to document_files.
        if isinstance(processed_docs, (str, list)):
            kwargs["document_files"] = processed_docs
        # If input is Document object, set processed docs to object_names.
        else:
            kwargs["object_names"] = processed_docs
        
        # Set the operation and call update method.
        kwargs["alter_operation"] = operation
        self.update(**kwargs)

    @classmethod
    @collect_queryband(queryband="VS_from_documents")
    @docstring_handler(
        common_params = {**COMMON_PARAMS, **FILE_BASED_VECTOR_STORE_PARAMS, **NIM_PARAMS},
    )
    def from_documents(cls, 
                       name, 
                       documents, 
                       embedding = None, 
                       **kwargs):
        """
        DESCRIPTION:
            Creates a new 'file-based' vector store from the input 
            documents and embeddings.
            If vector store already exists, an error is raised.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.    

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the vector store to be created from 
                input document(s).
                Types: str

            documents:
                Required Argument.
                Specifies the input dataset in document files format.
                It can be used to specify input documents in file format.
                A directory path or wildcard pattern can also be specified
                The files are processed internally, converted to chunks and 
                stored into a database table.
                Notes:
                    * Only PDF format is currently supported.
                    * Multiple document files can be supplied.
                    * Fully qualified file name should be specified.
                Examples:
                    Example 1 : Multiple files specified within a list
                    >>> documents=['file1.pdf','file2.pdf']

                    Example 2 : Path to the directory containing pdf files 
                    >>> documents = "/path/to/pdfs"

                    Example 3 : Path to directory containing pdf files as a wildcard string
                    >>> documents = "/path/to/pdfs/*.pdf"

                    Example 4 : Path to directory containing pdf files and subdirectory of pdf files
                    >>> documents = "/path/to/pdfs/**/*.pdf
                Types: str, list
            
            object_names:
                Optional Argument.
                Specifies the table name that is to be used for file content splits.
                Notes:
                    * Only one table name should be specified.
                Types: str
            
            target_database:
                Optional Argument.
                Specifies the database name where the file content splits are stored.
                Note:
                    If not specified, vector store is created in the database
                    which is in use.
                Types: str

            data_columns:
                Optional Argument.
                Specifies the column name(s) where the content splits are 
                to be stored.
                Notes:
                    * Only one name should be specified.
                Types: str

        RETURNS:
            VectorStore instance.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1: Create an instance of a file based vector store from
            #            a PDF file in a directory by passing the file 
            #            path in "documents" and 'amazon.titan-embed-text-v1' model
            #            in "embedding".
            # Get the absolute path of the directory.
            >>> import teradatagenai
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> file_1 = os.path.join(base_dir, 'example-data', 'SQL_Fundamentals.pdf')
            >>> vs_instance = VectorStore.from_documents(name = "vs_example_1",
                                                         documents = file_1,
                                                         embedding = "amazon.titan-embed-text-v1")

            # Example 2: Create an instance of a file based vector store from
            #            list of PDF files by passing the list of file names in
            #            in 'documents' and 'embedding' as a TeradataAI object 
            #            of api_type "aws" and model_name "amazon.titan-embed-text-v1".
            # 
            # Initialize the TeradataAI object using environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "amazon.titan-embed-text-v2:0")
            # Create the vector store instance.
            >>> file_2 = os.path.join(base_dir, 'example-data', 'LLM_handbook.pdf')
            >>> files = [file_1, file_2]
            >>> vs_instance = VectorStore.from_documents(name = "vs_example_2",
                                                        documents = files,
                                                        embedding = llm_aws)

            # Example 3: Create an instance of a file based vector store from
            #            a directory containing PDF files by passing the directory
            #            path in "documents" , 'amazon.titan-embed-text-v1' model
            #            in "embedding" as a string and "chat_completion_model" as a 
            #            TeradataAI object.
            # Create TeradataAI object for chat completion model.
            >>> obj = TeradataAI(api_type = "aws",
                                 access_key = "<AWS bedrock access key>",
                                 secret_key = "<AWS bedrock secret key>",
                                 session_key = "<AWS bedrock session key>",
                                 region = "us-west-2",
                                 model_name = "anthropic.claude-instant-v1",
                                 model_args = {"max_tokens_to_sample": 2048})
            # Create the vector store instance.
            >>> vs_instance = VectorStore.from_documents(name = "vs_example_3",
                                                         documents = "<Enter/path/to/directory/containing/pdf/files>",
                                                         embedding = "amazon.titan-embed-text-v1",
                                                         chat_completion_model = obj)

        """
        arg_info_matrix = [
            ["name", name, False, (str), True],
            ["documents", documents, False, cls._DOCUMENT_TYPES, True],
            ["embedding", embedding, True, cls._EMBEDDINGS_TYPES, True],
            ["chat_completion_model", kwargs.get("chat_completion_model"), True, cls._CHAT_MODEL_TYPES, True],
        ]

        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        # Process inputs.
        processed_docs = cls._process_documents_object(documents)
        processed_embedding = cls._process_embeddings_object(embedding)
        processed_chat_model = cls._process_chat_model_object(kwargs.get(("chat_completion_model"), None))

        # https://teradata-pe.atlassian.net/browse/ELE-8082
        # TODO: Handle unsupported embedding models.

        # If inputs is pdf set processed docs to document_files.
        if isinstance(processed_docs, (str, list)):
            kwargs["document_files"] = processed_docs
        
        # If input is Document object, set processed docs to object_names.
        else:
            kwargs["object_names"] = processed_docs
            kwargs["data_columns"] = "text"

        kwargs["embeddings_model"] = processed_embedding
        kwargs["chat_completion_model"] = processed_chat_model
        # Create the vector store instance.
        instance = cls(name = name , **kwargs)

        instance.create(**kwargs)
        return instance

    @classmethod
    @collect_queryband(queryband="VS_from_texts")
    @docstring_handler(
        common_params = {**COMMON_PARAMS, **NIM_PARAMS},
    )
    def from_texts(cls, 
                   name,
                   texts,
                   embedding = None,
                   **kwargs):
        """     
        DESCRIPTION:
            Creates a new 'content-based' vector store from the input 
            text(s) and embeddings.
            If vector store already exists, an error is raised.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.    
        
        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the vector store to be created
                from input list of raw text strings.
                Types: str

            texts:
                Required Argument.
                Specifies the text(s) to be indexed for vector store.
                Types: str or list of str

        RETURNS:
            VectorStore instance.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1: Create an instance of a content-based vector store by
            #            passing list of raw strings in "texts" and
            #            "amazon.titan-embed-text-v1" in "embedding".
            >>> vs_instance = VectorStore.from_texts(name = "vs_example_1",
                                                     texts = ["This is a sample text.",
                                                              "This is another sample text."],
                                                     embedding="amazon.titan-embed-text-v1")
        """
        arg_info_matrix = [
            ["name", name, False, (str), True],
            ["texts", texts, False, (str, list), True],
            ["embedding", embedding, True, cls._EMBEDDINGS_TYPES, True],
            ["chat_completion_model", kwargs.get("chat_completion_model"), True, cls._CHAT_MODEL_TYPES, True]
        ]
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        # Process inputs.
        processed_embedding = cls._process_embeddings_object(embedding)
        processed_chat_model = cls._process_chat_model_object(kwargs.get(("chat_completion_model"), None))

        texts = UtilFuncs._as_list(texts)
        object_names = DataFrame.from_dict(data = {"text": texts}, persist = True)

        kwargs["object_names"] = object_names
        kwargs["data_columns"] = ["text"]
        kwargs["embeddings_model"] = processed_embedding
        kwargs["chat_completion_model"] = processed_chat_model

        # Create the vector store instance.
        instance = cls(name = name , **kwargs)

        instance.create(**kwargs)
        return instance

    @classmethod
    @collect_queryband(queryband="VS_from_datasets")
    @docstring_handler(
        common_params = {**COMMON_PARAMS, **NIM_PARAMS},
    )
    def from_datasets(cls,
                     name,
                     data,
                     embedding = None,
                     **kwargs):
        """
        DESCRIPTION:
            Creates a new 'content-based' vector store from the input 
            dataset(s) containing table(s) or teradataml DataFrames(s).
            If vector store already exists, an error is raised.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.    
        
        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the vector store to be created from
                the input dataset(s).
                Types: str
            
            data:
                Required Argument.
                Specifies the table name(s)/teradataml DataFrame(s) to be indexed for
                vector store. Teradata recommends to use teradataml DataFrame as input.
                Notes:
                    * Multiple tables/views/DataFrames can be passed in "dataset".
                    * If the table is in another database than
                      the database in use, make sure to pass in
                      the fully qualified name or a DataFrame object.
                      For example,
                        * If the table name is 'amazon_reviews' and it is
                          under 'oaf' database which is not the user's
                          logged in database
                            * Pass argument as DataFrame(in_schema('oaf', 'amazon_reviews'))
                    * If multiple tables/views are passed, each table should
                      have the columns which are mentioned in "data_columns"
                      and "key_columns".
                    * When "target_database" is not set and only table name is passed to
                      "dataset", then the input is searched in default database.
                Types: str or list of str or DataFrame

            data_columns:
                Required Argument.
                Specifies the name(s) of the data column(s) to be used
                for embedding generation(vectorization).
                Note:
                    When multiple data columns are specified, data is unpivoted
                    to get a new key column "AttributeName" and a single data column
                    "AttributeValue".
                Types: str or list of str
            
            key_columns:
                Optional Argument.
                Specifies the name(s) of the key column(s) to be used for indexing.
                Types: str, list of str
            
        RETURNS:
            VectorStore instance.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1: Create an instance of a content-based vector store by
            #            passing 'amazon_reviews_25' as a string in "data"
            #            and 'amazon.titan-embed-text-v1' in "embedding".
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame
            # Load the amazon reviews data.
            >>> load_data('byom', 'amazon_reviews_25')
            >>> vs_instance1 = VectorStore.from_datasets(name = "vs_example_1",
                                                        data = "amazon_reviews_25",
                                                        data_columns = ["rev_text"],
                                                        embedding = "amazon.titan-embed-text-v1")
            
            # Example 2: Create an instance of a content-based vector store by
            #            loading the 'employee_reviews' from teradatagenai and
            #            passing it in "dataset" along with TeradataAI object
            #            in "embedding".
            # Initialize the required imports.
            >>> from teradatagenai import load_data, TeradataAI
            >>> from teradataml import DataFrame
            >>> import os
            # Initialize the TeradataAI object using environment variables.
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "amazon.titan-embed-text-v2:0")
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> vs_instance2 = VectorStore.from_datasets(name = "vs_example_2",
                                                         data = data,
                                                         data_columns = ["articles"],
                                                         embedding = llm_aws)
        
        """
        # Validate the arguments.
        arg_info_matrix = [
            ["name", name, False, (str), True],
            ["data", data, False, (str, list, DataFrame), True],
            ["embeddings", embedding, True, cls._EMBEDDINGS_TYPES, True],
            ["chat_completion_model", kwargs.get("chat_completion_model"), True, cls._CHAT_MODEL_TYPES, True],
            
        ]
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        # Process inputs.
        # https://teradata-pe.atlassian.net/browse/ELE-8082
        # TODO: Handle unsupported embedding models.
        processed_embedding = cls._process_embeddings_object(embedding)
        processed_chat_model = cls._process_chat_model_object(kwargs.get(("chat_completion_model"), None))

        kwargs["object_names"] = data
        kwargs["embeddings_model"] = processed_embedding
        kwargs["chat_completion_model"] = processed_chat_model

        # Create the vector store instance.
        instance = cls(name=name , **kwargs)

        instance.create(**kwargs)
        return instance

    @classmethod
    @collect_queryband(queryband="VS_from_embeddings")
    @docstring_handler(
        common_params = {**COMMON_PARAMS}
    )
    def from_embeddings(cls,
                        name,
                        data,
                        **kwargs):
        """
        DESCRIPTION:
            Creates a new 'embedding-based' vector store from the
            pre embedded input table(s) or DataFrame(s).
            If vector store already exists, an error is raised.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.    

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the vector store to be created from
                input data.
                Types: str

            data:
                Required Argument.
                Specifies the table name(s)/teradataml DataFrame(s) that are pre embedded to be
                indexed for vector store. Teradata recommends to use teradataml DataFrame as input.
                Notes:
                    * If multiple tables/views are passed, each table should
                      have the columns which are mentioned in "data_columns"
                      and "key_columns".
                    * When "target_database" is not set, and only table name is passed to
                      "data", then the input is searched in default database.
                Types: str or list of str or DataFrame

            data_columns:
                Required Argument.
                Specifies the name of the column that contains the
                pre embedded data.
                Note:
                    When multiple data columns are specified, data is unpivoted
                    to get a new key column "AttributeName" and a single data column
                    "AttributeValue".
                Types: str, list of str

            key_columns:
                Optional Argument.
                Specifies the name(s) of the key column(s) to be used for indexing.
                Types: str, list of str
 
            is_normalized:
                Optional Argument.
                Specifies whether the input contains normalized embeddings.
                Default Value: False
                Types: bool

        RETURNS:
            VectorStore instance.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Example 1: Create an instance of an 'embedding-based' vector store 
            #            by passing the 'amazon_reviews_embedded' table to 
            #            "data" and "data_columns" as 'embedding'.
            # Load the amazon reviews embedded data.
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame    
            >>> load_data('amazon', 'amazon_reviews_embedded')
            >>> vs_instance = VectorStore.from_embeddings(name = "vs_example_1",
                                                          data = 'amazon_reviews_embedded',
                                                          data_columns = ['embedding'])

            # Example 2: Create an instance of an 'embedding-based' vector store from
            #            embeddings generated using TextAnalyticsAI.
            # Import the required modules.
            >>> import os
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> from teradataml import DataFrame
            
            # Load the employee data.
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            
            # Initialize the TeradataAI object using environment variables.
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> llm_embedding = TeradataAI(api_type = "aws",
                                           model_name = "amazon.titan-embed-text-v2:0")
            
            # Create an instance of the TextAnalyticsAI class.
            >>> obj_embeddings = TextAnalyticsAI(llm=llm_embedding)
            
            # Get the embeddings for the 'articles' column in the data.
            >>> TAI_embeddings = obj_embeddings.embeddings(column="articles", 
                                                           data=data,
                                                           accumulate='articles',
                                                           output_format='VECTOR')
            
            # Create an instance of the VectorStore class.
            >>> vs_instance = VectorStore.from_embeddings(name = "vs_example_2",
                                                          data = TAI_embeddings,
                                                          data_columns = ['Embedding'])

        """
        # Validate the arguments.
        arg_info_matrix = [
            ["name", name, False, (str), True],
            ["data", data, False, (str, DataFrame, list) , True]
        ]
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)
        
        kwargs["object_names"] = data
        kwargs["is_embedded"] = True
        
        # Create the vector store instance.
        instance = cls(name = name , **kwargs)
        instance.create(**kwargs)
        return instance

    @collect_queryband(queryband="VS_add_datasets")
    @docstring_handler(
        common_params = {**COMMON_PARAMS, **UPDATE_PARAMS, **NIM_PARAMS},
    )    
    def add_datasets(self, data, **kwargs):
        """
        DESCRIPTION:
            Adds the specified data to an existing content-based vector store.
            Creates a new Vector Store in case it does not exists.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the table name(s)/teradataml DataFrame(s) to be indexed or 
                added to the vector store. Teradata recommends to use teradataml DataFrame as input.
                Notes:
                    * Multiple tables/views/DataFrames can be passed in "dataset".
                    * If the table is in another database than
                      the database in use, make sure to pass in
                      the fully qualified name or a DataFrame object.
                      For example,
                        * If the table name is 'amazon_reviews' and it is
                          under 'oaf' database which is not the user's
                          logged in database
                            * Pass argument as DataFrame(in_schema('oaf', 'amazon_reviews'))
                    * If multiple tables/views are passed, each table should
                      have the columns which are mentioned in "data_columns"
                      and "key_columns".
                    * When "target_database" is not set and only table name is passed to
                      "dataset", then the input is searched in default database.
                Types: str or list of str or DataFrame

            name:
                Optional Argument.
                Specifies the name of the vector store to be created from
                the input dataset(s).
                Types: str

            data_columns:
                Required Argument.
                Specifies the name(s) of the data column(s) to be used
                for embedding generation(vectorization).
                Note:
                    When multiple data columns are specified, data is unpivoted
                    to get a new key column "AttributeName" and a single data column
                    "AttributeValue".
                Types: str or list of str
            
            key_columns:
                Optional Argument.
                Specifies the name(s) of the key column(s) to be used for indexing.
                Types: str, list of str

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame
            >>> load_data("byom", "amazon_reviews_25")
            >>> amazon_reviews_25 = DataFrame('amazon_reviews_25')
            # Example 1: Add data to an existing content-based vector store "vs_example_1"
            # Create an instance of an 'content-based' vector store by passing the 'amazon_reviews_25' table.
            >>> vs_instance1 = VectorStore.from_datasets(name = "vs_example_1",
                                                         data = "amazon_reviews_25",
                                                         data_columns = ["rev_text"],
                                                         embedding = "amazon.titan-embed-text-v1")
            >>> load_data("byom", "amazon_reviews_10")
            >>> vs_instance1.add_datasets(data="amazon_reviews_10")
            # Example 2: Create a new embedding-based vector store "vs_example_2"
            >>> vs = VectorStore()
            >>> vs.add_datasets(name = "vs_example_2",
                               data = "amazon_reviews_10",
                               data_columns = ["rev_text"],
                               embedding = "amazon.titan-embed-text-v1")
        """

        # Check if vector store exists, if not create it using from_datasets
        self.name = kwargs.pop('name', self.name)
        if not self.exists:
            new_instance = self.from_datasets(name=self.name, data=data, **kwargs)
            self.__dict__.update(new_instance.__dict__)
            return
        
        self._process_datasets_operation(data, "ADD", **kwargs)    
    
    @collect_queryband(queryband="VS_add_documents")
    @docstring_handler(
        common_params = {**UPDATE_PARAMS, **COMMON_PARAMS, **FILE_BASED_VECTOR_STORE_PARAMS, **NIM_PARAMS},
    )   
    def add_documents(self, documents, **kwargs):
        """
        DESCRIPTION:
            Adds documents to an existing file-based Vector Store.
            Creates a new Vector Store in case it does not exists.

        PARAMETERS:
            documents:
                Required Argument.
                Specifies the files to be updated to the Vector Store.
                It can be used to specify input documents in file format.
                A directory path or wildcard pattern can also be specified.
                Types: str, list

            name:
                Optional Argument.
                Specifies the name of the vector store to be created from 
                input document(s).
                Types: str
            
            object_names:
                Optional Argument.
                Specifies the table name that is to be used for file content splits.
                Notes:
                    * Only one table name should be specified.
                Types: str
            
            target_database:
                Optional Argument.
                Specifies the database name where the file content splits are stored.
                Note:
                    If not specified, vector store is created in the database
                    which is in use.
                Types: str

            data_columns:
                Optional Argument.
                Specifies the column name(s) where the content splits are 
                to be stored.
                Notes:
                    * Only one name should be specified.
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VectorStore
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> file = os.path.join(base_dir, 'example-data', 'SQL_Fundamentals.pdf')
            # Example 1: Add "LLM_handbook.pdf" to an existing'file-based' vector store.
            # Create an instance of an 'file-based' vector store by passing path
            # to a PDF file in "documents".
            >>> vs_instance = VectorStore.from_documents(name = "vs_example_1",
                                                         documents = file ,
                                                         embedding = "amazon.titan-embed-text-v1")
            >>> file = os.path.join(base_dir, 'example-data', 'LLM_handbook.pdf')
            >>> vs_instance.add_documents(documents=file)
            # Example 2: Create a new embedding-based vector store "vs_example_2"
            >>> vs = VectorStore()
            >>> vs.add_documents(name = "vs_example_2",
                                 documents = file ,
                                 embedding = "amazon.titan-embed-text-v1")
        """
        # Check if vector store exists, if not create it using from_documents
        self.name = kwargs.pop('name', self.name)
        if not self.exists:
            new_instance = self.from_documents(name=self.name, documents=documents, **kwargs)
            self.__dict__.update(new_instance.__dict__)
            return

        self._process_documents_operation(documents, "ADD", **kwargs)

    @collect_queryband(queryband="VS_add_embeddings")
    @docstring_handler(
        common_params = {**UPDATE_PARAMS,**COMMON_PARAMS},
    )      
    def add_embeddings(self, data, **kwargs):
        """
        DESCRIPTION:
            Adds data to an existing embedding-based vector store.
            Creates a new Vector Store in case it does not exists.
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the table name(s)/teradataml DataFrame(s) that are pre embedded to be
                indexed or to be added to the vector store.
                Teradata recommends to use teradataml DataFrame as input.
                Notes:
                    * If multiple tables/views are passed, each table should
                      have the columns which are mentioned in "data_columns"
                      and "key_columns".
                    * When "target_database" is not set, and only table name is passed to
                      "data", then the input is searched in default database.
                Types: str, DataFrame, or list of str/DataFrame

            name:
                Optional Argument.
                Specifies the name of the vector store to be created from
                input data.
                Types: str

            data_columns:
                Optional Argument.
                Specifies the name of the column that contains the
                pre embedded data.
                Note:
                    When multiple data columns are specified, data is unpivoted
                    to get a new key column "AttributeName" and a single data column
                    "AttributeValue".
                Types: str, list of str
            
            is_normalized:
                Optional Argument.
                Specifies whether the input contains normalized embeddings.
                Default Value: False
                Types: bool
            
            key_columns:
                Optional Argument.
                Specifies the name(s) of the key column(s) to be used for indexing.
                Types: str, list of str
            
        RETURNS:
            None

        RAISES:
            TeradataMlException
        
        EXAMPLES:
            # Load the amazon reviews embedded data.
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame
            >>> load_data('amazon', 'amazon_reviews_embedded')
            >>> amazon_reviews_embedded = DataFrame('amazon_reviews_embedded')
            >>> load_data('amazon', 'amazon_reviews_embedded_10_alter')
            >>> amazon_reviews_embedded_10_alter = DataFrame('amazon_reviews_embedded_10_alter')
            # Example 1: Add data to an existing embedding-based vector store "vs_example_1"
            # Create an instance of an 'embedding-based' vector store by passing the 'amazon_reviews_embedded' table to 
            # "data" and "embedding" as 'data_columns'.
            >>> vs_instance = VectorStore.from_embeddings(name = "vs_example_1",
                                                          data = amazon_reviews_embedded,
                                                          data_columns = ['embedding'])
            >>> vs_instance.add_embeddings(data=amazon_reviews_embedded_10_alter)
            # Example 2: Create a new embedding-based vector store "vs_example_2".
            >>> vs = VectorStore()
            >>> vs.add_embeddings(name = "vs_example_2",
                                  data = amazon_reviews_embedded_10,
                                  data_columns = ['embedding'])
        """
        # Check if vector store exists, if not create it using from_embeddings
        self.name = kwargs.pop('name', self.name)
        if not self.exists:
            new_instance = self.from_embeddings(name=self.name, data=data, **kwargs)
            self.__dict__.update(new_instance.__dict__)
            return

       # Validate the argument.
        arg_info_matrix = [
            ["data", data, False, (str, list, DataFrame), True],
        ]
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        kwargs["object_names"] = data
        kwargs["alter_operation"] = "ADD"
        self.update(**kwargs)

    @collect_queryband(queryband="VS_add_texts")
    @docstring_handler(
        common_params = {**UPDATE_PARAMS,**COMMON_PARAMS, **NIM_PARAMS},
    ) 
    def add_texts(self, texts, **kwargs):
        """
        DESCRIPTION:
            Adds text/list of texts to an existing Vector Store.
            Creates a new Vector Store in case it does not exists.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the vector store to be created
                from input list of raw text strings.
                Types: str

            texts:
                Required Argument.
                Specifies the text or list of texts to be added to the vector store.
                Types: str or list of str
            
        EXAMPLES:
            # Example 1: Add texts to an existing content-based vector store "vs_example_1"
            # Create an instance of a content-based vector store by
            # passing list of raw strings in "texts" and
            # "amazon.titan-embed-text-v1" in "embedding".
            >>> vs_instance = vs.from_texts(name = "vs_example_1",
                                            texts = ["This is a sample text.",
                                                    "This is another sample text."],
                                            embedding = "amazon.titan-embed-text-v1")
            >>> vs_instance1.add_texts(texts = ["This is a sample text1.",
                                            "This is another sample text2."])
            # Example 2: Create a new embedding-based vector store "vs_example_2".
            >>> vs = VectorStore()
            >>> vs.add_texts(name = "vs_example_2",
                             texts = ["This is a sample text.",
                                       "This is another sample text."],
                             embedding = "amazon.titan-embed-text-v1")
        """
        # Check if vector store exists, if not create it using from_texts
        self.name = kwargs.pop('name', self.name)
        if not self.exists:
            new_instance = self.from_texts(name=self.name, texts=texts, **kwargs)
            self.__dict__.update(new_instance.__dict__)
            return
            
        arg_info_matrix = [
            ["texts", texts, False, (str, list), True],
        ]
        _Validators._validate_function_arguments(arg_info_matrix)
        texts = UtilFuncs._as_list(texts)
        processed_texts = DataFrame.from_dict(data = {"text": texts}, persist = True)
        kwargs["object_names"] = processed_texts
        kwargs["alter_operation"] = "ADD"

        # Call the update method with appropriate parameters.
        self.update(**kwargs)
        
    @collect_queryband(queryband="VS_delete_documents")
    @docstring_handler(
        common_params = {**UPDATE_PARAMS},
    )    
    def delete_documents(self, documents, **kwargs):
        """
        DESCRIPTION:
            Deletes documents from an existing file-based Vector Store.
        
        PARAMETERS:
            documents:
                Required Argument.
                Specifies the files to be deleted from the Vector Store.
                It can be used to specify input documents in file format.
                A directory path or wildcard pattern can also be specified.
                Types: str, list

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of an 'file-based' vector store by passing path
            # to a PDF file in "documents".
            # Note:
            #   This is optional and can be skipped if the vector store is already created.
            >>> import teradatagenai
            >>> import os
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> file = os.path.join(base_dir, 'example-data', 'SQL_Fundamentals.pdf')
            >>> vs_instance = VectorStore.from_documents(name = "vs_example_1",
                                                         documents = file ,
                                                         embedding = "amazon.titan-embed-text-v1")
            # Example 1: Delete "SQL_Fundamentals.pdf" from an existing 'file-based' vector store.
            >>> vs_instance.delete_documents(documents=file)
        """
        self._process_documents_operation(documents, "DELETE", **kwargs)

    @collect_queryband(queryband="VS_delete_datasets")
    @docstring_handler(
        common_params = {**UPDATE_PARAMS},
    ) 
    def delete_datasets(self, data, **kwargs):
        """
        DESCRIPTION:
            Deletes the specified dataset(s) from the an existing content-based vector store.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the name of the tables or teradataml DataFrames to be deleted from the VectorStore.
                Types: str, DataFrame, or list of str/DataFrame

        RETURNS:
            None

        RAISES:
            TeradataMlException

        EXAMPLES:
            # Create an instance of an 'content-based' vector store by passing the 'amazon_reviews_25' table.
            # Note:
            #   This is optional and can be skipped if the vector store is already created.
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame
            >>> load_data("byom", "amazon_reviews_25")       
            >>> amazon_reviews_25 = DataFrame('amazon_reviews_25')
            >>> load_data("byom", "amazon_reviews_10")
            >>> vs_instance1 = VectorStore.from_datasets(name = "vs_example_1",
                                                         data = ["amazon_reviews_25", "amazon_reviews_10"],
                                                         key_columns = ["rev_id", "aid"],
                                                         data_columns = ["rev_text"],
                                                         embeddings = "amazon.titan-embed-text-v1")
            # Example 1: Delete data from an existing content-based vector store "vs_example_1"
            >>> vs_instance1.delete_datasets(data="amazon_reviews_10")
        """
        self._process_datasets_operation(data, "DELETE", **kwargs)

    @collect_queryband(queryband="VS_delete_embeddings")
    @docstring_handler(
        common_params = {**UPDATE_PARAMS},
    ) 
    def delete_embeddings(self, data, **kwargs):
        """
        DESCRIPTION:
            Deletes data from an existing embedding-based vector store.
        
        PARAMETERS:
            data:
                Required Argument.
                Specifies the name of the tables or teradataml DataFrames containing the embedding data
                to be deleted from the Vector Store.
                Types: str, DataFrame, or list of str/DataFrame
        
        RETURNS:
            None
        
        RAISES:
            TeradataMlException
        
        EXAMPLES:
            # Create an instance of an 'embedding-based' vector store by passing the 'amazon_reviews_embedded' and 
            # 'amazon_reviews_embedded_10' tables to "data" and "embedding" as 'data_columns'.
            # Note:
            #   This is optional and can be skipped if the vector store is already created with the embedding data.
            # Load the amazon reviews embedded data.
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame
            >>> load_data('amazon', 'amazon_reviews_embedded')
            >>> load_data('amazon', 'amazon_reviews_embedded_10_alter')
            >>> vs_instance = VectorStore.from_embeddings(name = "vs_example_1",
                                                          data = ['amazon_reviews_embedded', 'amazon_reviews_embedded_10_alter'],
                                                          data_columns = ['embedding'])

            # Example 1: Delete data from an existing embedding-based vector store "vs_example_1"
            >>> amazon_reviews_embedded_10_alter = DataFrame('amazon_reviews_embedded_10_alter')
            >>> vs_instance.delete_embeddings(data=amazon_reviews_embedded_10_alter)

            # Example 2: Delete data from an existing embedding-based vector store "vs_example_1"
            >>> vs = VectorStore(name="vs_example_1")
            >>> amazon_reviews_embedded = DataFrame('amazon_reviews_embedded')
            >>> vs.delete_embeddings(data=amazon_reviews_embedded)
        """
        update_style = kwargs.get("update_style", "MINOR")

        # Validate the argument.
        arg_info_matrix = [
            ["data", data, False, (str, list, DataFrame), True],
        ]
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        _Validators._validate_function_arguments(arg_info_matrix)

        kwargs["object_names"] = data
        kwargs["alter_operation"] = "DELETE"
        self.update(**kwargs)

    def get_ids(self, **kwargs):
        # Get only the ids and corresponding row in tabular format so that user
        # can get the ids and do the further processing.
        # Note: Currently this is not being supported by service so once
        # they do it, we need to do it.
        raise NotImplementedError("Method is not available.")

    def delete_by_ids(self, **kwargs):
        # Delete the contents of Vector Store corresponding to ids.
        # Note: Currently this is not being supported by service so once
        # they do it, we need to do it.
        raise NotImplementedError("Method is not available.")

    @collect_queryband(queryband="VS_get_indexes_embeddings")
    def get_indexes_embeddings(self):
        """
        DESCRIPTION:
            Get the output table containing the indexing and embedding information.

        PARAMETERS:
            None.

        RETURNS:
            Teradataml DataFrame.

        RAISES:
            None.

        EXAMPLES:
            >>> vs.get_indexes_embeddings()
        """
        return DataFrame(in_schema(self._database, f"vectorstoreV_{self.name}"))

    @collect_queryband(queryband="VS_get_model_info")
    def get_model_info(self):
        """
        DESCRIPTION:
            Get the output table(s) depending on the search algorithm.
                * hnsw_model: Output table which contains centroids information.
                  Underlying table name which contains these details is 'vectorstore_<vs_name>_hnsw_model'.
                  Note:
                    Applicable only if search_algorithm is "HNSW".
                * centroids_table: Output table which contains centroids information.
                  Underlying table name which contains these details is 'vectorstore_<vs_name>_centroids'.
                  Note:
                    Applicable only if search_algorithm is "KMEANS".
                * kmeans_model: Output table which contains kmeans model information.
                  Underlying table name which contains these details is 'vectorstore_<vs_name>_kmeans_model'.
                  Note:
                    Applicable only if search_algorithm is "KMEANS".

        PARAMETERS:
            None.

        RETURNS:
            dict or Teradataml DataFrame.

        RAISES:
            None.

        EXAMPLES:
            >>> vs.get_model_info()
        """
        if not hasattr(self, "_search_algorithm") or self._search_algorithm is None:
            details = self.get_details(return_type="json")
            self._search_algorithm = details["search_algorithm"]

        if self._search_algorithm.lower() == "kmeans":
            return {"kmeans_model": DataFrame(in_schema(self._database, f"vectorstore_{self.name}_kmeans_model")),
                    "centroids_table": DataFrame(in_schema(self._database, f"vectorstore_{self.name}_centroids"))}

        if self._search_algorithm.lower() == "hnsw":
            return DataFrame(in_schema(self._database, f"vectorstore_{self.name}_hnsw_model"))

    # TODO: https://teradata-pe.atlassian.net/browse/ELE-7518
    @collect_queryband(queryband="VS_get_objects")
    def get_objects(self):
        """
        DESCRIPTION:
            Get the list of objects in the metadata-based vector store.

        PARAMETERS:
            None.

        RETURNS:
            teradataml DataFrame containing the list of objects.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")

            # Example: Get the list of objects that are used for creating the vector store.
            >>> vs.get_objects()
        """
        response = UtilFuncs._http_request(self.__get_objects_url, HTTPRequest.GET,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})

        data = VectorStore._process_vs_response("get_objects", response)
        return VectorStore._convert_to_tdmldf(pd.DataFrame({'Object List':data['object_list']}))

    @collect_queryband(queryband="VS_get_details")
    def get_details(self, **kwargs):
        """
        DESCRIPTION:
            Get details of the vector store.
            Details include embeddings model, search algorithm
            and any other details which the user has setup while
            creating or updating the vector store.

        PARAMETERS:
            None.

        RETURNS:
            teradataml DataFrame containing the details.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the VectorStore 'vs'
            # which already exists.
            >>> vs = VectorStore(name="vs")

            # Example: Get details of a vector store.
            >>> vs.get_details()
        """
        response = UtilFuncs._http_request(self.__get_details_url, HTTPRequest.GET,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        data = VectorStore._process_vs_response("get_details", response)
        # Adding a return_type parameter so that internally we avoid creating a DataFrame.
        if kwargs.get("return_type", "teradataml") == "json":
            return data
        return VectorStore._convert_to_tdmldf(pd.DataFrame([data]))

    def __set_vs_index_and_vs_parameters(self, create=True, **kwargs):
        """
        DESCRIPTION:
            Internal function to set the parameters for the vector store.
            Keeping it common, as it will be required by update and initialize
            methods.

        PARAMETERS:
            create:
                Optional Argument.
                Specifies whether call is from create or update function.
                Default Value: True
                Types: bool

            kwargs:
                Optional Argument.
                Specifies keyword arguments required for creating/updating vector store.
        RAISES:
            TeradataGenAIException.

        EXAMPLES:
            >>> self.__set_vs_index_and_vs_parameters(key_columns="a",
                                                      create=False)
        """
        ## Initializing vs_index params
        for attr_name in VSIndex:
            setattr(self, f"_{attr_name}", kwargs.get(attr_name, None))

        self._document_files = kwargs.get('document_files', None)

        ## Initializing vs_parameters
        for attr_name in VSParameters:
            setattr(self, f"_{attr_name}", kwargs.get(attr_name, None))

        # Set the default value of database.
        # Setting a different parameter other than target_database
        # because if we pass target_database it takes as if we are updating it.
        self._database = self._database if self._database is not None else _get_user()

        # TODO ELE-6025: Bug in Feb drop for these arguments, hence commented them.
        # self._acronym_objects = kwargs.get('acronym_objects', None)
        # self._acronym_objects_global = kwargs.get('acronym_objects_global', None)
        # self._acronym_files_global = kwargs.get('acronym_files_global', None)


        # Validating vs_index
        arg_info_matrix = []
        arg_info_matrix.append(["name", self.name, False, (str), True])
        arg_info_matrix.append(["target_database", self._target_database, True, (str), True])
        arg_info_matrix.append(["object_names", self._object_names, True, (str, DataFrame, list), True])
        arg_info_matrix.append(["key_columns", self._key_columns, True, (str, list), True])
        arg_info_matrix.append(["data_columns", self._data_columns, True, (str, list), True])
        arg_info_matrix.append(["vector_column", self._vector_column, True, (str), True])
        arg_info_matrix.append(["chunk_size", self._chunk_size, True, (int), True])
        arg_info_matrix.append(["optimized_chunking", self._optimized_chunking, True, (bool), True])
        arg_info_matrix.append(["is_embedded", self._is_embedded, True, (bool), True])
        arg_info_matrix.append(["is_normalized", self._is_normalized, True, (bool), True])
        arg_info_matrix.append(["header_height", self._header_height, True, (int), True])
        arg_info_matrix.append(["footer_height", self._footer_height, True, (int), True])
        arg_info_matrix.append(["extract_text", self._extract_text, True, (bool), True])
        arg_info_matrix.append(["extract_images", self._extract_images, True, (bool), True])
        arg_info_matrix.append(["extract_tables", self._extract_tables, True, (bool), True])
        arg_info_matrix.append(["extract_method", self._extract_method, True, (str), True])
        arg_info_matrix.append(["extract_infographics", self._extract_infographics, True, (bool), True])
        arg_info_matrix.append(["hf_access_token", self._hf_access_token, True, (str), True])

        arg_info_matrix.append(["tokenizer", self._tokenizer, True, (str), True])
        # TODO ELE-4937 check if this is str or DataFrame.
        arg_info_matrix.append(["include_objects", self._include_objects, True, (str, DataFrame, list), True])
        arg_info_matrix.append(["exclude_objects", self._exclude_objects, True, (str, DataFrame, list), True])
        arg_info_matrix.append(["include_patterns", self._include_patterns, True, (VSPattern, list), True])
        arg_info_matrix.append(["exclude_patterns", self._exclude_patterns, True, (VSPattern, list), True])
        arg_info_matrix.append(["sample_size", self._sample_size, True, (int), True])
        arg_info_matrix.append(["nv_ingestor", self._nv_ingestor, True, (bool), True])
        arg_info_matrix.append(["display_metadata", self._display_metadata, True, (bool), True])
        arg_info_matrix.append(["alter_operation", self._alter_operation, True, (str), True])
        arg_info_matrix.append(["update_style", self._update_style, True, (str), True])

        # TODO ELE-6025: Bug in Feb drop for these arguments, hence commented them.
        # arg_info_matrix.append(["acronym_objects", self._acronym_objects, True, (str, list), True])
        # arg_info_matrix.append(["acronym_objects_global", self._acronym_objects_global, True, (bool, list), True])
        # arg_info_matrix.append(["acronym_files_global", self._acronym_files_global, True, (bool, list), True])

        # Validating vs_parameters
        arg_info_matrix.append(["description", self._description, True, (str), True])
         # embeddings_model has default values, hence making optional.
        arg_info_matrix.append(["embeddings_model", self._embeddings_model, True, (str), True])
        arg_info_matrix.append(["embeddings_dims", self._embeddings_dims, True, (int), True])
        arg_info_matrix.append(["metric", self._metric, True, (str), True])
        arg_info_matrix.append(["search_algorithm", self._search_algorithm, True, (str), True])
        arg_info_matrix.append(["top_k", self._top_k, True, (int), True])
        arg_info_matrix.append(["initial_centroids_method", self._initial_centroids_method, True, (str),
                                True])
        arg_info_matrix.append(["train_numcluster", self._train_numcluster, True, (int), True])
        arg_info_matrix.append(["max_iternum", self._max_iternum, True, (int), True])
        arg_info_matrix.append(["stop_threshold", self._stop_threshold, True, (float), True])
        arg_info_matrix.append(["seed", self._seed, True, (int), True])
        arg_info_matrix.append(["num_init", self._num_init, True, (int), True])
        arg_info_matrix.append(["search_threshold", self._search_threshold, True, (float), True])
        arg_info_matrix.append(["search_numcluster", self._search_numcluster, True, (int), True])
        arg_info_matrix.append(["prompt", self._prompt, True, (str), True])
        arg_info_matrix.append(["chat_completion_model", self._chat_completion_model, True, (str),
                                True])
        arg_info_matrix.append(["document_files", self._document_files, True, (str, list),
                                True])
        arg_info_matrix.append(["ef_search", self._ef_search, True, (int), True])
        arg_info_matrix.append(["num_layer", self._num_layer, True, (int), True])
        arg_info_matrix.append(["ef_construction", self._ef_construction, True, (int), True])
        arg_info_matrix.append(["num_connpernode", self._num_connpernode, True, (int), True])
        arg_info_matrix.append(["maxnum_connpernode", self._maxnum_connpernode, True, (int), True])
        arg_info_matrix.append(["apply_heuristics", self._apply_heuristics, True, (bool), True])
        arg_info_matrix.append(["rerank_weight", self._rerank_weight, True, (float), True])
        arg_info_matrix.append(["relevance_top_k", self._relevance_top_k, True, (int), True])
        arg_info_matrix.append(["relevance_search_threshold", self._relevance_search_threshold, True, (float), True])
        
        # TODO: ELE-6015 : Need to understand why to handle on client side if service already handles it 
        arg_info_matrix.append(["time_zone", self._time_zone, True, (str), True])

        # TODO: ELE-6018
        #arg_info_matrix.append(["batch", self._batch, True, (bool), True])
        arg_info_matrix.append(["ignore_embedding_errors", self._ignore_embedding_errors, True, (bool), True])
        arg_info_matrix.append(["chat_completion_max_tokens", self._chat_completion_max_tokens, True, (int), True])
        arg_info_matrix.append(["embeddings_base_url", self._embeddings_base_url, True, (str), True])
        arg_info_matrix.append(["completions_base_url", self._completions_base_url, True, (str), True])
        arg_info_matrix.append(["ingest_host", self._ingest_host, True, (str), True])
        arg_info_matrix.append(["ingest_port", self._ingest_port, True, (int), True])

        # Validate required arguments.
        _Validators._validate_missing_required_arguments(arg_info_matrix)
        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Forming document files structure as the API accepts:
        # Input document files structure is: [fully_qualified_file_name1,
        #                                     fully_qualified_file_name2]
        # document_files = [('document_files', ('file1.pdf',
        #                    open('/location/file1.pdf', 'rb'),
        #                    'application/pdf')),
        #                   ('document_files', ('file2.pdf',
        #                    open('/location/file2.pdf', 'rb'),
        #                    'application/pdf'))
        #                   ]
        
        if self._data_columns and type(self._data_columns) is str:
            # Convert single string to list
            self._data_columns = [self._data_columns]

        if self._document_files:
            # Normalize input to a list
            if isinstance(self._document_files, str):
                self._document_files = [self._document_files]

            resolved_files = []
            for path in self._document_files:
                files = []
                # Wildcard pattern
                if any(char in path for char in ['*', '?']):
                    files = glob.glob(path, recursive="**" in path)
                # Directory path
                elif os.path.isdir(path):
                    for root, _, filenames in os.walk(path):
                        files.extend(os.path.join(root, f) for f in filenames)
                # Single file path
                else:
                    files = [path]
                
                # Add all resolved files to the list
                resolved_files.extend(files)
            
            # Validate ALL resolved files at once - reports all invalid files together
            _Validators._validate_file_exists(resolved_files)

            # Now process the validated files
            self._document_files = []
            # Get the file name from fully qualified path
            for file in resolved_files:
                file_name = os.path.basename(file)
                # Form the string 'application/pdf' based on the file extension.
                file_type = f"application/{os.path.splitext(file_name)[1]}".replace(".", "")
                file_handle = open(file, 'rb')
                self._document_files.append(('document_files', (file_name, file_handle, file_type)))
                # Register the file handle with the GarbageCollector.
                GarbageCollector.add_open_file(file_handle)

        # TODO ELE-6025: Bug in Feb drop for these arguments, hence commented them.
        # Will reuse again in April drop.
        # if self._acronym_objects:
        #     acronym_objects = self._acronym_objects
        #     self._acronym_objects = []

        #     for file in acronym_objects:
        #         # Get the file name from fully qualified path
        #         file_name = os.path.basename(file)
        #         # Form the string 'application/pdf' based on the file extension.
        #         file_type = f"application/{os.path.splitext(file_name)[1]}".replace(".", "")
        #         self._acronym_objects.append(('acronym_objects', (file_name,
        #                                                         open(file, 'rb'),
        #                                                         file_type)))

        # Extracting pattern names from include_patterns and exclude_patterns
        if self._include_patterns is not None:     
            include_patterns = []
            for pattern in UtilFuncs._as_list(self._include_patterns):
                include_patterns.append(pattern._pattern_name)
            self._include_patterns = include_patterns

        if self._exclude_patterns is not None:
            exclude_patterns = []
            for pattern in UtilFuncs._as_list(self._exclude_patterns):
                exclude_patterns.append(pattern._pattern_name)
            self._exclude_patterns = exclude_patterns

        # Check if the object_name is a DataFrame and extract table_name to put in self._object_names.
        self._object_names = _ProcessDataFrameObjects(self._object_names)
        self._include_objects = _ProcessDataFrameObjects(self._include_objects)
        self._exclude_objects = _ProcessDataFrameObjects(self._exclude_objects)

        # Only add the keys which are not None and populate the vs_index as needed by the service.
        self.__vs_parameters = {
            param_name: getattr(self, f"_{attr_name}")
            for attr_name, param_name in VSParameters.items()
            if getattr(self, f"_{attr_name}") is not None
        }

        # Only add the keys which are not None and populate the vs_index as needed by the service.
        self.__vs_index = {
            param_name: getattr(self, f"_{attr_name}")
            for attr_name, param_name in VSIndex.items()
            if getattr(self, f"_{attr_name}") is not None
        }

        # Check if any other argument is provided which is not in VSParameters and VSIndex.
        # Combine keys of VSParameters and VSIndex.
        combined_keys = set(VSParameters) | set(VSIndex)
        combined_keys.add("document_files")
        combined_keys.add("name")

        # Find missing keys
        missing_keys = [key for key in kwargs if key not in combined_keys]
        if missing_keys:
            api = 'create' if create else 'update'
            raise TeradataGenAIException(MessagesGenAI.get_message(MessageCodesGenAI.INVALID_FUNCTION_PARAMETER,
                                                                   params=', '.join(missing_keys),
                                                                   api=api),
                                                              MessageCodesGenAI.INVALID_FUNCTION_PARAMETER)

        # TODO ELE-6025: Bug in Feb drop for these arguments, hence commented them.
        # 'acronym_objects': self._acronym_objects,
        # 'acronym_objects_global': self._acronym_objects_global,
        # 'acronym_files_global': self._acronym_files_global
        if create:
            self.__set_urls()

    @collect_queryband(queryband="VS_create")
    def create(self, **kwargs):
        """
        DESCRIPTION:
            Creates a new vector store.
            Once vector store is created, it is initialized for use.
            If vector store already exists, error is raised.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            name:
                Optional Argument.
                Specifies the name of the vector store either to connect, if it
                already exists or to create a new vector store.
                Types: str


            description:
                Optional Argument.
                Specifies the description of the vector store.
                Types: str

            target_database:
                Optional Argument.
                Specifies the database name where the vector store is created.
                When "document_files" is passed, it refers to the database where
                the file content splits are stored.
                Note:
                    If not specified, vector store is created in the database
                    which is in use.
                Types: str

            vector_column:
                Optional Argument.
                Specifies the name of the column to be used for storing
                the embeddings.
                Default Value: vector_index
                Types: str

            object_names:
                Required for 'content-based vector store' and 'embeddings-based vector store',
                Optional otherwise.
                Specifies the table name(s)/teradataml DataFrame(s) to be indexed for
                vector store. Teradata recommends to use teradataml DataFrame as input.
                Notes:
                    * For content-based vector store:
                        * Multiple tables/views can be passed in object_names.
                        * If the table is in another database than
                          the database in use, make sure to pass in
                          the fully qualified name or a DataFrame object.
                          For example,
                            * If the table_name is 'amazon_reviews' and it is
                              under 'oaf' database which is not the user's
                              logged in database,
                                * Either pass in str as 'oaf.amazon_reviews' or
                                * DataFrame(in_schema('oaf', 'amazon_reviews'))
                        * If multiple tables/views are passed, each table should
                          have the columns which are mentioned in "data_columns"
                          and "key_columns".
                        * When document_files are used, only one name should be
                          specified to be used for file content splits.
                    * For metadata-based vector store:
                        * Use "include_objects" or
                          "include_patterns" parameters instead of "object_names".
                    * When "target_database" is not set, and only table name is passed to
                      "object_names", then the input is searched in default database.
                Types: str or list of str or DataFrame

            key_columns:
                Optional Argument.
                Specifies the name(s) of the key column(s) to be used for indexing.
                Notes:
                     * Not supported, when "document_files" is used.
                     * In case of multiple input files, a key_column containing
                       the file names is generated.
                Default Value: content/embeddings-based: ['TD_ID']
                               file-based: ['TD_ID', 'TD_FILENAME']
                Types: str, list of str

            data_columns:
                Optional Argument.
                Specifies the name(s) of the data column(s) to be used
                for embedding generation(vectorization).
                Notes:
                    * When multiple data columns are specified, data is unpivoted
                      to get a new key column "AttributeName" and a single data column
                      "AttributeValue".
                    * When "document_files" is specified, specifies the column name 
                      where the content splits to be stored.
                Default Value: content/embeddings-based: []
                               file-based: ['file-splits']
                Types: str, list of str

            chunk_size:
                Optional Argument.
                Specifies the number of characters in each chunk to be used while
                splitting the input file.
                Note:
                    Applicable only for 'file-based' vector stores.
                Default Value: 512
                Types: int

            optimized_chunking:
                Optional Argument.
                Specifies whether an optimized splitting mechanism supplied by
                Teradata should be used.
                The documents are parsed internally in an intelligent fashion
                based on file structure and chunks are dynamically created
                based on section layout.
                Notes:
                    * The "chunk_size" field is not applicable when
                      "optimized_chunking" is set to True.
                    *  Applicable only for 'file-based' vector stores.
                Default Value: True
                Types: bool

            nv_ingestor:
                Optional Argument.
                Specifies whether to use NVIDIA NV-Ingest for processing the 
                document files.
                Notes:
                     * Applicable only while using NVIDIA NIM endpoints.
                     * Applicable only for 'file-based' vector stores.
                Default Value: False
                Types: bool

            display_metadata:
                Optional Argument.
                Specifies whether to display metadata describing objects extracted 
                from document files when using NVIDIA NV-Ingest.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Default Value: False
                Types: bool

            extract_text:
                Optional Argument.
                Specifies whether to extract text from the document files when 
                using NVIDIA NV-Ingest.
                Notes:
                    * Applicable only for 'file-based' vector stores.
                    * Applicable only while using NVIDIA NIM endpoints and
                      when "nv_ingestor" is set to True.
                Default Value: True
                Types: bool

            extract_images:
                Optional Argument.
                Specifies whether to extract images from the document files when 
                using NVIDIA NV-Ingest.
                Notes:
                    * Applicable only for 'file-based' vector stores.
                    * Applicable only while using NVIDIA NIM endpoints and
                      when "nv_ingestor" is set to True.
                Default Value: True
                Types: bool

            extract_tables:
                Optional Argument.
                Specifies whether to extract tables from the document files when 
                using NVIDIA NV-Ingest.
                Notes:
                    * Applicable only for 'file-based' vector stores.
                    * Applicable only while using NVIDIA NIM endpoints and
                      when "nv_ingestor" is set to True.
                Default Value: True
                Types: bool

            extract_infographics:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies whether to extract infographics from
                document files.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Default Value: False
                Types: bool

            extract_method:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the method to be used for extracting text from
                 the document files.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Permitted Values: pdfium, nemoretriever_parse
                Default Value: pdfium
                Types: str
            
            tokenizer:
                Optional Argument
                Specifies the tokenizer to be used for splitting the text into chunks.
                Notes:
                     * Applicable only when "nv_ingestor" is set to True
                       and "document_files" is supplied.
                     * Applicable only while using NVIDIA NIM endpoints.
                Defaut Value: meta-llama/Llama-3.2-1B
                Types: str

            header_height:
                Optional Argument.
                Specifies the height (in points) of the header section of a PDF
                document to be trimmed before processing the main content.
                This is useful for removing unwanted header information
                from each page of the PDF.
                Recommended value is 55.
                Note:
                    * Applicable only for 'file-based' vector stores.
                Default Value: 0
                Types: int

            footer_height:
                Optional Argument.
                Specifies the height (in points) of the footer section of a PDF
                document to be trimmed before processing the main content.
                This is useful for removing unwanted footer information from
                each page of the PDF.
                Note:
                    * Applicable only for 'file-based' vector stores.
                Recommended value is 55.
                Default Value: 0
                Types: int

            include_objects:
                Optional Argument.
                Specifies the list of tables and views included
                in the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: str or list of str or DataFrame

            exclude_objects:
                Optional Argument.
                Specifies the list of tables and views excluded from
                the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: str or list of str or DataFrame

            include_patterns:
                Optional Argument.
                Specifies the list of patterns to be included in the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: VSPattern or list of VSPattern

            exclude_patterns:
                Optional Argument.
                Specifies the list of patterns to be excluded from the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: VSPattern or list of VSPattern

            sample_size:
                Optional Argument.
                Specifies the number of rows to sample from tables and views
                for the metadata-based vector store embeddings.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Default Value: 20
                Types: int

            is_embedded:
                Required for 'embeddings-based' vector stores, Optional otherwise.
                Specifies whether the input contains the embedded data.
                Note:
                    * Applicable only for 'embeddings-based' vector store.
                Default Value: False
                Types: bool

            is_normalized:
                Optional Argument.
                Specifies whether the input contains normalized embedding.
                Note:
                    * Applicable only for 'embeddings-based' vector store.
                Default Value: False
                Types: bool

            embeddings_model:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the embeddings model to be used for generating the
                embeddings.
                Default Values:
                    * AWS: amazon.titan-embed-text-v2:0
                    * Azure: text-embedding-3-small
                Permitted Values:
                    * AWS
                        * amazon.titan-embed-text-v1
                        * amazon.titan-embed-image-v1
                        * amazon.titan-embed-text-v2:0
                    * Azure
                        * text-embedding-ada-002
                        * text-embedding-3-small
                        * text-embedding-3-large
                Types: str

            embeddings_dims:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the number of dimensions to be used for generating the embeddings.
                The value depends on the "embeddings_model".
                Permitted Values:
                    AWS:
                        * amazon.titan-embed-text-v1: 1536
                        * amazon.titan-embed-image-v1: [256, 384, 1024]
                        * amazon.titan-embed-text-v2:0: [256, 512, 1024]
                    Azure:
                        * text-embedding-ada-002: 1536 only
                        * text-embedding-3-small: 1 <= dims <= 1536
                        * text-embedding-3-large: 1 <= dims <= 3072
                Default Value:
                    AWS:
                        * amazon.titan-embed-text-v1: 1536
                        * amazon.titan-embed-image-v1: 1024
                        * amazon.titan-embed-text-v2:0: 1024
                    Azure:
                        * text-embedding-ada-002: 1536
                        * text-embedding-3-small: 1536
                        * text-embedding-3-large: 3072
                Types: str

            metric:
                Optional Argument.
                Specifies the metric to be used for calculating the distance
                between the vectors.
                Permitted Values:
                    * EUCLIDEAN
                    * COSINE
                    * DOTPRODUCT
                Default Value: COSINE
                Types: str

            search_algorithm:
                Optional Argument.
                Specifies the algorithm to be used for searching the
                tables and views relevant to the question.
                Permitted Values: VECTORDISTANCE, KMEANS, HNSW.
                Default Value: VECTORDISTANCE
                Types: str

            initial_centroids_method:
                Optional Argument.
                Specifies the algorithm to be used for initializing the
                centroids.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: RANDOM, KMEANS++
                Default Value: RANDOM
                Types: str

            train_numcluster:
                Optional Argument.
                Specifies the number of clusters to be trained.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: [2-33553920]
                Types: int

            max_iternum:
                Optional Argument.
                Specifies the maximum number of iterations to be run during
                training.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: [1-2147483647]
                Default Value: 10
                Types: int

            stop_threshold:
                Optional Argument.
                Specifies the threshold value at which training should be
                stopped.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Default Value: 0.0395
                Types: float

            seed:
                Optional Argument.
                Specifies the seed value to be used for random number
                generation.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS' and 'HNSW'.
                Permitted Values: [0-2147483647]
                Default Value: 0
                Types: int

            num_init:
                Optional Argument.
                Specifies the number of times the k-means algorithm should
                run with different initial centroid seeds.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: [1-2147483647]
                Default Value: 1
                Types: int

            top_k:
                Optional Argument.
                Specifies the number of top clusters to be considered while searching.
                Permitted Values: [1-1024]
                Default Value: 10
                Types: int

            search_threshold:
                Optional Argument.
                Specifies the threshold value to consider for matching tables/views
                while searching.
                A higher threshold value limits responses to the top matches only.
                Note:
                    Applicable when "search_algorithm" is 'VECTORDISTANCE' and 'KMEANS'.
                Types: float

            search_numcluster:
                Optional Argument.
                Specifies the number of clusters to be considered while
                searching.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Types: int

            prompt:
                Optional Argument.
                Specifies the prompt to be used by language model
                to generate responses using top matches.
                Types: str

            chat_completion_model:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the name of the chat completion model to be used for
                generating text responses.
                Permitted Values:
                    AWS:
                        * anthropic.claude-3-haiku-20240307-v1:0
                        * anthropic.claude-instant-v1
                        * anthropic.claude-3-5-sonnet-20240620-v1:0
                    Azure:
                        gpt-35-turbo-16k
                Default Value:
                    AWS: anthropic.claude-3-haiku-20240307-v1:0
                    Azure: gpt-35-turbo-16k
                Types: str

            document_files:
                Optional Argument.
                Specifies the input dataset in document files format.
                It can be used to specify input documents in file format.
                A directory path or wildcard pattern can also be specified
                The files are processed internally, converted to chunks and stored
                into a database table.
                Alternatively, users can choose to chunk their files themselves,
                store them into a database table, create a table and specify
                the details of that using "target_database", "object_names",
                "data_columns" where the file content splits are stored.
                Notes:
                    * Only PDF format is currently supported.
                    * Multiple document files can be supplied.
                    * Fully qualified file name should be specified.
                Examples:
                    Example 1 : Multiple files specified within a list
                    >>> document_files=['file1.pdf','file2.pdf']

                    Example 2 : Path to the directory containing pdf files 
                    >>> document_files = "/path/to/pdfs"

                    Example 3 : Path to directory containing pdf files as a wildcard string
                    >>> document_files = "/path/to/pdfs/*.pdf"

                    Example 4 : Path to directory containing pdf files and subdirectory of pdf files
                    >>> document_files = "/path/to/pdfs/**/*.pdf
                Types: str, list

            ef_search:
                Optional Argument.
                Specifies the number of neighbors to be considered during search
                in HNSW graph.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Default Value: 32
                Types: int

            num_layer:
                Optional Argument.
                Specifies the maximum number of layers for the HNSW graph.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Types: int

            ef_construction:
                Optional Argument.
                Specifies the number of neighbors to be considered during
                construction of the HNSW graph.
                Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Default Value: 32
                Types: int

            num_connpernode:
                Optional Argument.
                Specifies the number of connections per node in the HNSW graph
                during construction.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Default Value: 32
                Types: int

            maxnum_connpernode:
                Optional Argument.
                Specifies the maximum number of connections per node in the
                HNSW graph during construction.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Default Value: 32
                Permitted Values: [1-1024]
                Types: int

            apply_heuristics:
                Optional Argument.
                Specifies whether to apply heuristics optimizations during construction
                of the HNSW graph.
                Applicable when "search_algorithm" is 'HNSW'.
                Default Value: True
                Types: bool

            rerank_weight:
                Optional Argument.
                Specifies the weight to be used for reranking the search results.
                Applicable range is 0.0 to 1.0.
                Default Value: 0.2
                Types: float

            relevance_top_k:
                Optional Argument.
                Specifies the number of top similarity matches to be considered for reranking.
                Applicable range is 1 to 1024.
                Permitted Values: [1-1024]
                Default Value: 60
                Types: int

            relevance_search_threshold:
                Optional Argument.
                Specifies the threshold value to consider matching tables/views while reranking.
                A higher threshold value limits responses to the top matches only.
                Types: float
            
            embeddings_base_url:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the base URL for the service to be used for generating embeddings.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Types: str

            completions_base_url:
                Optional Argument.
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the base URL for the service to be used for generating completions.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Types: str

            ingest_host:
                Required for NVIDIA NIM, Optional otherwise.
            	Specifies the HTTP host for the service to be used for document parsing.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Types: str

            ingest_port:
                Optional Argument.
                Specifies the HTTP port for the service to be used for document parsing.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Default Value: 7670
                Types: int

            ignore_embedding_errors:
                Optional Argument.
                Specifies whether to ignore errors during embedding generation.
                Default Value: False
                Types: bool

            chat_completion_max_tokens:
                Optional Argument.
                Specifies the maximum number of tokens to be generated by the "chat_completion_model".
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Permitted Values: [1-16384]
                Default Value: 16384
                Types: int

            hf_access_token:
               Optional Argument.
                Specifies the Hugging Face access token to be used for
                accessing the tokenizer.
                 Note:
                     Applicable only while using NVIDIA NIM endpoints
                     and when "nv_ingestor" is set to True.
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataGenAIException, TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VectorStore

            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vec1")

            # Example 1: Create a content based vector store for the data
            #            in table 'amazon_reviews_25'.
            #            Use 'amazon.titan-embed-text-v1' embedding model for
            #            creating vector store.
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          target_database='oaf',
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1")

            # Example 2: Create a content based vector store for the data
            #            in DataFrame 'df'.
            #            Use 'amazon.titan-embed-text-v1' embedding model for
            #            creating vector store.
            >>> from teradataml import DataFrame
            >>> df = DataFrame("amazon_reviews_25")
            >>> vs = VectorStore('vs_example_2') 
            >>> vs.create(object_names=df,
                          description="vector store testing",
                          target_database='oaf',
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1")

            # Example 3: Create a content based vector store for the data
            #            in 'SQL_Fundamentals.pdf' file.
            #            Use 'amazon.titan-embed-text-v1' embedding model
            #            for creating vector store.

            # Get the absolute path for 'SQL_Fundamentals.pdf' file.
            >>> import teradatagenai
            >>> files= [os.path.join(os.path.dirname(teradatagenai.__file__), "example-data",
                                 "SQL_Fundamentals.pdf")]
            >>> vs = VectorStore('vs_example_3')
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          target_database='oaf',
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1"
                          document_files=files)

            # Example 4: Create a content based vector store of all PDF files
            #            in a directory by passing the directory path
            #            Use 'amazon.titan-embed-text-v1' embedding model
            #            for creating vector store.

            # Get the absolute path of the directory.
            >>> files= "/path/to/pdfs"
            >>> vs = VectorStore('vs_example_4')
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          target_database='oaf',
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1"
                          document_files=files)

            # Example 5: Create a content based vector store of all PDF files
            #            in a directory by passing the path as a wildcard
            #            Use 'amazon.titan-embed-text-v1' embedding model
            #            for creating vector store.

            # Pass the wildcard pattern containing the pdf files
            >>> files= "/path/to/pdfs/*.pdf"
            >>> vs = VectorStore('vs_example_5')
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          target_database='oaf',
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1"
                          document_files=files)
    
            # Example 6: Create a content based vector store in which the
            #            input is already in vectorized format and input 
            #            contains normalized embeddings.
            >>> vs = VectorStore('vs_example_6')
            >>> vs.create(object_names="amazon_reviews_embedded",
                          description="vector store testing",
                          target_database='oaf',
                          key_columns=['rev_id', 'aid'],
                          data_columns=['embedding'],
                          vector_column='VectorIndex',
                          is_embedded = True,
                          is_normalized = True)
        """
        if kwargs.get("name", None) is not None:
            self.name = kwargs.get("name")
        # Set the vs_index and vs_parameters
        self.__set_vs_index_and_vs_parameters(**kwargs)

        # Form the data to be passed to the API
        data = {}
        if self.__vs_parameters or self.__vs_index:
            data = {}
            if self.__vs_parameters:
                data['vs_parameters'] = json.dumps(self.__vs_parameters)
            if self.__vs_index:
                data['vs_index'] = json.dumps(self.__vs_index)
        # Form the http_params
        http_params = {
            "url": self.__common_url,
            "method_type": HTTPRequest.POST,
            "headers": self.__headers,
            "data": data,
            "files": self._document_files,
            "cookies": {'session_id': self.__session_id}
        }
        # Call the 'create' API
        response = UtilFuncs._http_request(**http_params)
        # Process the response
        self._process_vs_response("create", response) 
        self.__display_status_check_message()
        self.store_type = self.get_details(return_type="json")["store_type"]

    @collect_queryband(queryband="VS_destroy")
    def destroy(self):
        """
        DESCRIPTION:
            Destroys the vector store.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VectorStore

            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vec1")

            # Example 1: Create a content based vector store for the data
            #            in table 'amazon_reviews_25'.
            #            Use 'amazon.titan-embed-text-v1' embedding model for
            #            creating vector store.

            # Note this step is not needed if vector store already exists.
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          target_database='oaf',
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1")

            # Destroy the Vector Store.
            >>> vs.destroy()
        """
        response = UtilFuncs._http_request(self.__common_url, HTTPRequest.DELETE,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        self._process_vs_response("destroy", response)
        self.__display_status_check_message()

    @collect_queryband(queryband="VS_update")
    def update(self, **kwargs):
        """
        DESCRIPTION:
            Updates an existing vector store with the specified parameters.
            Notes:
                * Addition of new data and deletion of existing data
                  stored in table/view(s) is possible using
                  "alter_operation" and "update_style".
                * Updating when input data is present in pdf files is not supported.
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            description:
                Optional Argument.
                Specifies the description of the vector store.
                Types: str

            object_names:
                Required for 'content-based vector store' and 'embeddings-based vector store',
                Optional otherwise.
                Specifies the table name(s)/teradataml DataFrame(s) to be indexed for
                vector store. Teradata recommends to use teradataml DataFrame as input.
                Notes:
                    * For content-based vector store:
                        * Multiple tables/views can be passed in object_names.
                        * If the table is in another database than
                          the database in use, make sure to pass in
                          the fully qualified name or a DataFrame object.
                          For example,
                            * If the table_name is 'amazon_reviews' and it is
                              under 'oaf' database which is not the user's
                              logged in database,
                                * Either pass in str as 'oaf.amazon_reviews' or
                                * DataFrame(in_schema('oaf', 'amazon_reviews'))
                        * If multiple tables/views are passed, each table should
                          have the columns which are mentioned in "data_columns"
                          and "key_columns".
                        * When document_files are used, only one name should be
                          specified to be used for file content splits.
                    * For metadata-based vector store:
                        * Use "include_objects" or
                          "include_patterns" parameters instead of "object_names".
                    * When "target_database" is not set, and only table name is passed to
                      "object_names", then the input is searched in default database.
                Types: str or list of str or DataFrame

            chunk_size:
                Optional Argument.
                Specifies the number of characters in each chunk to be used while
                splitting the input file.
                Note:
                    Applicable only for 'file-based' vector stores.
                Default Value: 512
                Types: int

            optimized_chunking:
                Optional Argument.
                Specifies whether an optimized splitting mechanism supplied by
                Teradata should be used.
                The documents are parsed internally in an intelligent fashion
                based on file structure and chunks are dynamically created
                based on section layout.
                Notes:
                     * The "chunk_size" field is not applicable when
                       "optimized_chunking" is set to True.
                     * Applicable only for 'file-based' vector stores.
                Default Value: True
                Types: bool

            nv_ingestor:
                Optional Argument.
                Specifies whether to use NVIDIA NV-Ingest for processing the
                document files.
                Notes:
                     * Applicable only while using NVIDIA NIM endpoints.
                     * Applicable only for 'file-based' vector stores.
                Default Value: False
                Types: bool

            display_metadata:
                Optional Argument.
                Specifies whether to display metadata describing objects extracted
                from document files when using NVIDIA NV-Ingest.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Default Value: False
                Types: bool

            extract_text:
                Optional Argument.
                Specifies whether to extract text from the document files when
                using NVIDIA NV-Ingest.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Default Value: True
                Types: bool

            extract_images:
                Optional Argument.
                Specifies whether to extract images from the document files when
                using NVIDIA NV-Ingest.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Default Value: True
                Types: bool

            extract_tables:
                Optional Argument.
                Specifies whether to extract tables from the document files when
                using NVIDIA NV-Ingest.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                      when "nv_ingestor" is set to True.
                Default Value: True
                Types: bool

            extract_infographics:
                Optional Argument.
                Specifies whether to extract infographics from
                document files.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Default Value: False
                Types: bool

            extract_method:
                Optional Argument.
                Specifies the method to be used for extracting text from
                the document files.
                Notes:
                     * Applicable only for 'file-based' vector stores.
                     * Applicable only while using NVIDIA NIM endpoints and
                       when "nv_ingestor" is set to True.
                Permitted Values: pdfium, nemoretriever_parse
                Default Value: pdfium
                Types: str

            tokenizer:
                Optional Argument
                Specifies the tokenizer to be used for splitting the text into chunks.
                Notes:
                    * Applicable only for 'file-based' vector stores.
                    * Applicable only while using NVIDIA NIM endpoints and
                      when "nv_ingestor" is set to True.
                Defaut Value: meta-llama/Llama-3.2-1B
                Types: str

            header_height:
                Optional Argument.
                Specifies the height (in points) of the header section of a PDF
                document to be trimmed before processing the main content.
                This is useful for removing unwanted header information
                from each page of the PDF.
                Recommended value is 55.
                Note:
                    * Applicable only for 'file-based' vector stores.
                Default Value: 0
                Types: int

            footer_height:
                Optional Argument.
                Specifies the height (in points) of the footer section of a PDF
                document to be trimmed before processing the main content.
                This is useful for removing unwanted footer information from
                each page of the PDF.
                Note:
                    * Applicable only for 'file-based' vector stores.
                Recommended value is 55.
                Default Value: 0
                Types: int

            include_objects:
                Optional Argument.
                Specifies the list of tables and views included
                in the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: str or list of str or DataFrame

            exclude_objects:
                Optional Argument.
                Specifies the list of tables and views excluded from
                the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: str or list of str or DataFrame

            include_patterns:
                Optional Argument.
                Specifies the list of patterns to be included in the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: VSPattern or list of VSPattern

            exclude_patterns:
                Optional Argument.
                Specifies the list of patterns to be excluded from the metadata-based vector store.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Types: VSPattern or list of VSPattern

            sample_size:
                Optional Argument.
                Specifies the number of rows to sample from tables and views
                for the metadata-based vector store embeddings.
                Note:
                    * Applicable only for 'metadata-based' vector store.
                Default Value: 20
                Types: int

            is_embedded:
                Required for 'embeddings-based' vector stores, Optional otherwise.
                Specifies whether the input contains the embedded data.
                Note:
                    * Applicable only for 'embeddings-based' vector store.
                Default Value: False
                Types: bool

            is_normalized:
                Optional Argument.
                Specifies whether the input contains normalized embedding.
                Note:
                    * Applicable only for 'embeddings-based' vector store.
                Default Value: False
                Types: bool

            embeddings_model:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the embeddings model to be used for generating the
                embeddings.
                Default Values:
                    * AWS: amazon.titan-embed-text-v2:0
                    * Azure: text-embedding-3-small
                Permitted Values:
                    * AWS
                        * amazon.titan-embed-text-v1
                        * amazon.titan-embed-image-v1
                        * amazon.titan-embed-text-v2:0
                    * Azure
                        * text-embedding-ada-002
                        * text-embedding-3-small
                        * text-embedding-3-large
                Types: str

            embeddings_dims:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the number of dimensions to be used for generating the embeddings.
                The value depends on the "embeddings_model".
                Permitted Values:
                    AWS:
                        * amazon.titan-embed-text-v1: 1536
                        * amazon.titan-embed-image-v1: [256, 384, 1024]
                        * amazon.titan-embed-text-v2:0: [256, 512, 1024]
                    Azure:
                        * text-embedding-ada-002: 1536 only
                        * text-embedding-3-small: 1 <= dims <= 1536
                        * text-embedding-3-large: 1 <= dims <= 3072
                Default Value:
                    AWS:
                        * amazon.titan-embed-text-v1: 1536
                        * amazon.titan-embed-image-v1: 1024
                        * amazon.titan-embed-text-v2:0: 1024
                    Azure:
                        * text-embedding-ada-002: 1536
                        * text-embedding-3-small: 1536
                        * text-embedding-3-large: 3072
                Types: str

            metric:
                Optional Argument.
                Specifies the metric to be used for calculating the distance
                between the vectors.
                Permitted Values:
                    * EUCLIDEAN
                    * COSINE
                    * DOTPRODUCT
                Default Value: COSINE
                Types: str

            search_algorithm:
                Optional Argument.
                Specifies the algorithm to be used for searching the
                tables and views relevant to the question.
                Permitted Values: VECTORDISTANCE, KMEANS, HNSW.
                Default Value: VECTORDISTANCE
                Types: str

            initial_centroids_method:
                Optional Argument.
                Specifies the algorithm to be used for initializing the
                centroids.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: RANDOM, KMEANS++
                Default Value: RANDOM
                Types: str

            train_numcluster:
                Optional Argument.
                Specifies the number of clusters to be trained.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: [2-33553920]
                Types: int

            max_iternum:
                Optional Argument.
                Specifies the maximum number of iterations to be run during
                training.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: [1-2147483647]
                Default Value: 10
                Types: int

            stop_threshold:
                Optional Argument.
                Specifies the threshold value at which training should be
                stopped.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Default Value: 0.0395
                Types: float

            seed:
                Optional Argument.
                Specifies the seed value to be used for random number
                generation.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS' and 'HNSW'.
                Permitted Values: [0-2147483647]
                Default Value: 0
                Types: int

            num_init:
                Optional Argument.
                Specifies the number of times the k-means algorithm should
                run with different initial centroid seeds.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Permitted Values: [1-2147483647]
                Default Value: 1
                Types: int

            top_k:
                Optional Argument.
                Specifies the number of top clusters to be considered while searching.
                Permitted Values: [1-1024]
                Default Value: 10
                Types: int

            search_threshold:
                Optional Argument.
                Specifies the threshold value to consider for matching tables/views
                while searching.
                A higher threshold value limits responses to the top matches only.
                Note:
                    Applicable when "search_algorithm" is 'VECTORDISTANCE' and 'KMEANS'.
                Types: float

            search_numcluster:
                Optional Argument.
                Specifies the number of clusters to be considered while
                searching.
                Note:
                    Applicable when "search_algorithm" is 'KMEANS'.
                Types: int

            prompt:
                Optional Argument.
                Specifies the prompt to be used by language model
                to generate responses using top matches.
                Types: str

            chat_completion_model:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the name of the chat completion model to be used for
                generating text responses.
                Permitted Values:
                    AWS:
                        * anthropic.claude-3-haiku-20240307-v1:0
                        * anthropic.claude-instant-v1
                        * anthropic.claude-3-5-sonnet-20240620-v1:0
                    Azure:
                        gpt-35-turbo-16k
                Default Value:
                    AWS: anthropic.claude-3-haiku-20240307-v1:0
                    Azure: gpt-35-turbo-16k
                Types: str

            document_files:
                Optional Argument.
                Specifies the input dataset in document files format.
                It can be used to specify input documents in file format.
                A directory path or wildcard pattern can also be specified
                The files are processed internally, converted to chunks and stored
                into a database table.
                Alternatively, users can choose to chunk their files themselves,
                store them into a database table, create a table and specify
                the details of that using "target_database", "object_names",
                "data_columns" where the file content splits are stored.
                Notes:
                    * Only PDF format is currently supported.
                    * Multiple document files can be supplied.
                    * Fully qualified file name should be specified.
                Examples:
                    Example 1 : Multiple files specified within a list
                    >>> document_files=['file1.pdf','file2.pdf']

                    Example 2 : Path to the directory containing pdf files
                    >>> document_files = "/path/to/pdfs"

                    Example 3 : Path to directory containing pdf files as a wildcard string
                    >>> document_files = "/path/to/pdfs/*.pdf"

                    Example 4 : Path to directory containing pdf files and subdirectory of pdf files
                    >>> document_files = "/path/to/pdfs/**/*.pdf
                Types: str, list

            ef_search:
                Optional Argument.
                Specifies the number of neighbors to be considered during search
                in HNSW graph.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Default Value: 32
                Types: int

            num_layer:
                Optional Argument.
                Specifies the maximum number of layers for the HNSW graph.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Types: int

            ef_construction:
                Optional Argument.
                Specifies the number of neighbors to be considered during
                construction of the HNSW graph.
                Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Default Value: 32
                Types: int

            num_connpernode:
                Optional Argument.
                Specifies the number of connections per node in the HNSW graph
                during construction.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Permitted Values: [1-1024]
                Default Value: 32
                Types: int

            maxnum_connpernode:
                Optional Argument.
                Specifies the maximum number of connections per node in the
                HNSW graph during construction.
                Note:
                    Applicable when "search_algorithm" is 'HNSW'.
                Default Value: 32
                Permitted Values: [1-1024]
                Types: int

            apply_heuristics:
                Optional Argument.
                Specifies whether to apply heuristics optimizations during construction
                of the HNSW graph.
                Applicable when "search_algorithm" is 'HNSW'.
                Default Value: True
                Types: bool

            rerank_weight:
                Optional Argument.
                Specifies the weight to be used for reranking the search results.
                Applicable range is 0.0 to 1.0.
                Default Value: 0.2
                Types: float

            relevance_top_k:
                Optional Argument.
                Specifies the number of top similarity matches to be considered for reranking.
                Applicable range is 1 to 1024.
                Permitted Values: [1-1024]
                Default Value: max(top_k*2, 60)
                Types: int

            relevance_search_threshold:
                Optional Argument.
                Specifies the threshold value to consider matching tables/views while reranking.
                A higher threshold value limits responses to the top matches only.
                Types: float

            embeddings_base_url:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the base URL for the service to be used for generating embeddings.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Types: str

            completions_base_url:
                Optional Argument.
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the base URL for the service to be used for generating completions.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Types: str

            ingest_host:
                Required for NVIDIA NIM, Optional otherwise.
            	Specifies the HTTP host for the service to be used for document parsing.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Types: str

            ingest_port:
                Optional Argument.
                Specifies the HTTP port for the service to be used for document parsing.
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Default Value: 7670
                Types: int

            ignore_embedding_errors:
                Optional Argument.
                Specifies whether to ignore errors during embedding generation.
                Default Value: False
                Types: bool

            chat_completion_max_tokens:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the maximum number of tokens to be generated by the "chat_completion_model".
                Note:
                    Applicable only while using NVIDIA NIM endpoints.
                Permitted Values: [1-16384]
                Default Value: 16384
                Types: int

            hf_access_token:
                Required for NVIDIA NIM, Optional otherwise.
                Specifies the Hugging Face access token to be used for
                accessing the tokenizer.
                 Note:
                     Applicable only while using NVIDIA NIM endpoints
                     and when "nv_ingestor" is set to True.
                Types: str

            alter_operation:
                Optional Argument.
                Specifies the type of operation to be performed while adding new data or
                deleting existing data from the vector store.
                Permitted Values: ADD, DELETE
                Types: str

            update_style:
                Optional Argument.
                Specifies the style to be used for "alter_operation" of the data
                from the vector store when "search_algorithm" is KMEANS/HNSW.
                Permitted Values:
                    * MINOR: Involves building the index with only the new data which is added/deleted.
                    * MAJOR: Involves building the entire index again with the entire data including
                             the data which was added/deleted.
                Default Value: MINOR
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataGenAIException, TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VectorStore
            >>> from teradataml import DataFrame

            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vec1")
            >>> load_data("byom", "amazon_reviews_10")
            >>> load_data("byom", "amazon_reviews_25")

            # Create the Vector Store.
            # Note this step is not needed if vector store already exists.
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1",
                          search_algorithm='VECTORDISTANCE',
                          top_k=10
                          )

            # Example 1: Update the search_algorithm, search_threshold and
            #            description of the Vector Store.
            >>> vs.update(search_algorithm='KMEANS',
                          search_threshold=0.6,
                          description='KMeans clustering method')
            
            # Example 2: Add the object_names of the content-based Vector Store using
            #            alter_operation and update_style.
            >>> vs = VectorStore(name="vs_update")
            >>> vs.create(embeddings_model= 'amazon.titan-embed-text-v1',
                          chat_completion_model= 'anthropic.claude-instant-v1',
                          search_algorithm= 'HNSW',
                          seed=10,
                          top_k=10,
                          ef_construction=32,
                          num_connpernode=32,
                          maxnum_connpernode=32,
                          metric='EUCLIDEAN',
                          apply_heuristics=True,
                          ef_search=32,
                          object_names= 'amazon_reviews_25',
                          key_columns= ['rev_id', 'aid'],
                          data_columns= ['rev_text'],
                          vector_column= 'VectorIndex')

            >>> vs.update(object_names='amazon_reviews_10',
                          alter_operation="ADD",
                          update_style="MINOR")

            # Example 3: Delete the object_names of the content-based Vector Store using
            #            alter_operation and update_style.
            >>> vs.update(object_names='amazon_reviews_25',
                          alter_operation="DELETE",
                          update_style="MAJOR")

            # Example 4: Add the object_names of the content-based Vector Store using
            #            alter_operation where the input is embedded.
            >>> vs.update(object_names='amazon_reviews_embedded_10_alter',
                          alter_operation="ADD",
                          is_embedded = True)
        """
        self.__set_vs_index_and_vs_parameters(**kwargs, create=False)
        data = {}

        data = {}
        if self.__vs_parameters or self.__vs_index:
            if self.__vs_parameters:
                data['vs_parameters'] = json.dumps(self.__vs_parameters)
            if self.__vs_index:
                data['vs_index'] = json.dumps(self.__vs_index)

        response = UtilFuncs._http_request(self.__common_url,
                                           HTTPRequest.PATCH,
                                           data=data,
                                           files=self._document_files,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        self._process_vs_response("update", response)
        self.__display_status_check_message()

    @collect_queryband(queryband="VS_similarity_search")
    def similarity_search(self, 
                          question=None,
                          **kwargs):
        """
        DESCRIPTION:
            Performs similarity search in the Vector Store for the input question.
            The algorithm specified in "search_algorithm" is used to perform
            the search against the vector store.
            The result contains "top_k" rows along with similarity score
            found by the "search_algorithm".

        PARAMETERS:
            question:
                Required Argument, Optional for batch mode.
                Specifies a string of text for which similarity search
                needs to be performed.
                Types: str

            batch_data:
                Required for batch mode.
                Specifies the table name or teradataml DataFrame to be indexed for batch mode.
                Note:
                    Applicable only for AWS.
                Types: str, teradataml DataFrame
            
            batch_id_column:
                Required for batch mode.
                Specifies the ID column to be indexed for batch mode.
                Note:
                    Applicable only for AWS.
                Types: str

            batch_query_column:
                Required for batch mode.
                Specifies the query column to be indexed for batch mode.
                Note:
                    Applicable only for AWS.
                Types: str
            
            return_type:
                Optional Argument.
                Specifies the return type of similarity_search.
                Permitted Values: "teradataml", "pandas", "json"
                Default Value: "teradataml"
                Types: str

        RETURNS:
            list.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VectorStore

            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")

            # Create a Vector Store.

            # Note this step is not needed if vector store already exists.
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1",
                          search_algorithm='VECTORDISTANCE',
                          top_k=10
                          )

            # Example 1: Perform similarity search in the Vector Store for
            #            the input question.
            >>> question = 'Are there any reviews about books?'
            >>> response = vs.similarity_search(question=question)

            Example 2: Perform batch similarity search in the Vector Store.
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs_batch")

            # Creates a Vector Store.
            # Note this step is not needed if vector store already exists.
            >>> vs.create(embeddings_model="amazon.titan-embed-text-v1",
                          embeddings_dims=2048,
                          chat_completion_model="anthropic.claude-3-haiku-20240307-v1:0",
                          search_algorithm="HNSW",
                          top_k=10,
                          object_names="valid_passages",
                          key_columns="pid",
                          data_columns="passage",
                          vector_column="VectorIndex")

            # Perform batch similarity search in the Vector Store.
            >>> response = vs.similarity_search(batch_data="valid_passages",
                                                batch_id_column="pid",
                                                batch_query_column="passage")

            # Retrieve the batch similarity results.
            from teradatagenai import VSApi
            >>> similarity_results = vs.get_batch_result(api_name=VSApi.SimilaritySearch)

        """
        # Check if batch mode is enabled
        batch = self.__batch_mode_args_validation(**kwargs)

        if batch:
            # Post request for batch similarity search
            response = UtilFuncs._http_request(self.__batch_url.format(self.__url,
                                                                       'similarity-search-batch',
                                                                       self._log),
                                               HTTPRequest.POST,
                                               headers=self.__headers,
                                               json=self.__set_batch_index,
                                               cookies={'session_id': self.__session_id})
            self._process_vs_response(api_name="similarity-search-batch", response=response)
            self.__display_status_check_message(batch)
            return
        else:

            # Initializing params
            self._question = question

            # Validating params
            arg_info_matrix = []
            arg_info_matrix.append(["question", self._question, False, (str), True])
            _Validators._validate_missing_required_arguments(arg_info_matrix)

            # Validate argument types.
            _Validators._validate_function_arguments(arg_info_matrix)

            response = UtilFuncs._http_request(self.__similarity_search_url.format(self.__url,
                                                                                   question,
                                                                                   self._log),
                                               HTTPRequest.POST,
                                               headers=self.__headers,
                                               cookies={'session_id': self.__session_id})

            return _SimilaritySearch(self._process_vs_response(api_name="similarity-search",
                                                               response=response),
                                     return_type=kwargs.get("return_type"))

    @collect_queryband(queryband="VS_similarity_search_by_vector")
    def similarity_search_by_vector(self,
                                    **kwargs):
        """
        DESCRIPTION:
            Performs similarity search in the Vector Store for
            the input question vector or embedded question stored in the table.
            The algorithm specified in "search_algorithm" is used to perform
            the search against the vector store.
            The result contains "top_k" rows along with similarity score
            found by the "search_algorithm".
            Note:
                Applicable only for 'embeddings-based' Vector Store.

        PARAMETERS:
            question:
                Optional Argument.
                 Specifies the vector for a question,
                 i.e., embeddings generated for a question.
                Types: str

            data:
                Optional Argument.
                Specifies table name or corresponding
                teradataml DataFrame where the question is stored.
                Note: Only one question(row) should be present
                      in the table.
                Types: str or DataFrame

            column:
                Optional Argument.
                Specifies the column name which contains the
                question in embedded format.
                Types: str or DataFrame

            return_type:
                Optional Argument.
                Specifies the return type of similarity_search.
                Permitted Values: "teradataml", "pandas", "json"
                Default Value: "teradataml"
                Types: str

        RETURNS:
            list.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VectorStore, load_data
            >>> from teradataml import DataFrame

            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")

            # Create a Vector Store.

            # Note this step is not needed if vector store already exists.
            >>> vs.create(target_database = 'oaf',
                          object_names= 'amazon_reviews_embedded',
                          key_columns= ['rev_id', 'aid'],
                          data_columns= ['embedding'],
                          vector_column = 'VectorIndex',
                          is_embedded = True
                          )

            # Check the status of Vector Store creation.
            >>> vs.status()

            # Example 1: Perform similarity search in the Vector Store for
            #            the input question.
            >>> response = vs.similarity_search_by_vector(question='-0.06944,0.080352,0.045963,0.006985,-0.000496,-0.025461,0.045302,-0.028107,0.031248,0.00077,-0.028107,0.016781,-0.023147,-0.068779,-0.07936,-0.030091,0.027611,-0.047616,-0.025461,0.029595,0.024635,-0.025461,-0.029926,0.046294,-0.065142,-0.019013,0.037366,-0.008019,0.065472,-0.054891,-0.009507,0.022816,0.009341,-0.041995,0.022651,0.028603,0.059851,0.047286,0.014467,0.002118,0.016616,-0.009383,-0.001643,0.015624,0.002831,0.005539,0.0248,0.018517,-0.007109,-0.013723,0.029926,0.006903,-0.011325,0.075723,0.009259,0.043648,0.035382,-0.02943,0.023147,-0.036208,-0.017856,-0.032736,0.019013,-0.037035,0.022155,-0.036704,-0.003596,-0.012069,0.021824,0.013805,-0.062827,0.016616,0.008928,-0.04431,-0.019592,-0.002397,0.048608,-0.00341,-0.024139,0.006985,-0.005001,0.002542,0.001777,0.002025,0.026123,0.055883,0.015707,0.014963,0.024304,0.001157,0.042326,-0.004753,-0.044971,0.005373,0.074731,0.002728,-0.028934,0.032736,0.011573,-0.012483,-0.040507,0.040507,0.001736,-0.036539,0.028438,0.053568,0.048278,0.082006,0.011739,0.064811,0.034059,0.062496,-0.013309,-0.065803,0.05456,-0.046624,0.009837,0.005539,-0.015376,0.016947,-0.065472,0.015128,-0.018352,0.062496,0.005539,-0.036208,0.001715,-0.023643,-0.000646,-0.047616,0.035712,0.011325,0.013723,0.07936,-0.010375,-0.021989,0.030091,0.013475,0.038358,-0.034059,-0.068118,0.013475,0.036043,-0.017029,-0.028107,-0.002687,0.00992,-0.001963,-0.04431,-0.009052,-0.088619,-0.016699,-0.027611,0.006861,-0.046624,-0.047286,-0.00744,0.00187,0.004133,-0.008225,-0.018352,0.001405,-0.033067,-0.000858,-0.001705,-0.028107,-0.01984,-0.010251,-0.013888,0.002005,0.046294,0.025461,-0.021163,-0.044971,-0.034886,-0.010747,-0.024304,0.006035,-0.019344,0.001126,-0.018352,0.015045,0.02728,-0.020749,0.000527,0.007523,-0.019427,-0.010499,0.038027,-0.027445,-0.018931,0.021659,0.037035,-0.054891,0.005539,-0.051254,-0.003968,0.011739,-0.041003,0.017029,0.011408,-0.007564,0.051584,0.010499,-0.001788,0.001075,0.032902,0.020997,-0.015624,0.020749,0.038027,0.020749,-0.046955,-0.012069,0.050262,-0.048608,0.028934,-0.074731,0.025461,-0.056875,0.013971,-0.018104,-0.054891,-0.001343,0.013888,0.019427,0.038688,0.057536,-0.011077,0.082006,0.024139,0.033894,0.037366,0.02943,-0.026619,-0.032075,-0.040672,-0.021493,0.001891,-0.013805,-0.005415,0.016451,-0.001963,0.003617,0.003286,0.016533,-0.071424,-0.042987,0.023808,-0.071424,0.008101,0.018683,-0.037862,-0.036208,0.037366,0.006531,0.016203,0.031083,-0.006448,0.008349,-0.045963,0.012648,0.032571,-0.007688,-0.043318,0.025792,0.000889,0.015211,-0.018765,-0.013061,0.040176,-0.035712,0.02232,-0.011243,-0.030091,-0.04431,-0.059851,0.011904,-0.013888,0.060182,0.04431,-0.017691,-0.008721,-0.000509,-0.010375,-0.033563,-0.03968,-0.018104,0.010044,0.020005,-0.024304,0.046955,0.001447,0.017029,-0.011739,-0.042326,0.014219,0.036539,0.028768,-0.008597,-0.005745,0.00868,-0.040011,-0.036704,0.007192,-0.042326,0.061504,0.015789,-0.023147,-0.005373,-0.039184,0.014053,-0.000713,0.003038,-0.009135,0.012483,-0.028107,-0.014549,-0.060512,0.048939,-0.069771,0.000607,0.012648,0.017195,0.018683,0.008804,0.030918,-0.038027,-0.00279,0.027611,0.007068,0.031579,0.029099,-0.004898,0.04431,-0.056875,-0.034886,-0.008267,-0.005911,-0.018517,0.009837,0.0248,0.023147,0.04464,-0.017029,0.016285,-0.0124,0.030091,0.012069,-0.013392,-0.000163,0.038027,0.008721,0.005621,-0.015707,-0.062827,-0.060182,0.026453,0.028107,0.015293,0.014219,-0.047616,0.006076,0.032571,-0.047616,-0.027115,0.046294,-0.006985,-0.027445,0.005167,-0.03191,-0.009383,-0.022981,0.025957,0.001974,0.010127,-0.038854,-0.020253,-0.046955,0.011408,-0.047616,0.006985,-0.058198,0.021989,-0.001674,0.011987,-0.006861,0.043979,0.011408,-0.007853,-0.03439,0.025957,0.013557,0.02976,0.008721,-0.012731,-0.054891,-0.058859,-0.004857,-0.005291,-0.008349,0.007895,-0.020997,0.038854,-0.008349,0.016616,-0.060843,0.040507,0.021824,0.002253,-0.012565,0.006324,0.040011,0.073078,-0.02943,0.014384,-0.031083,0.010995,-0.025131,0.009011,0.015707,0.060182,0.05919,0.017443,0.033563,-0.039184,0.051915,0.040011,-0.021493,0.036208,-0.030091,0.022981,0.056214,0.070432,-0.004071,-0.019013,-0.000377,0.014549,-0.044971,-0.019592,0.013392,0.008308,-0.002563,-0.032902,0.001405,0.013061,0.013061,-0.018269,0.022155,-0.038358,0.048608,0.078699,-0.023477,-0.031744,-0.008308,-0.042326,0.015045,0.072086,0.010333,-0.058859,0.001467,0.040011,-0.011243,0.045302,-0.028107,-0.012731,0.056875,-0.003265,-0.015541,0.007771,0.030091,-0.057206,-0.014632,0.020667,-0.041995,0.030752,0.014053,-0.038027,0.013061,0.012565,0.002366,0.049931,-0.02976,0.015045,0.007564,-0.015459,0.04464,0.005745,-0.029099,-0.013557,-0.005869,0.024304,-0.026784,0.007688,-0.073078,-0.046624,-0.00155,0.000107,0.009259,-0.022155,0.015376,0.003885,-0.080352,0.011408,-0.020749,-0.01612,0.011573,0.055222,0.013557,0.00155,0.000961,0.012069,0.002955,-0.014797,-0.041499,-0.018683,-0.035216,-0.043648,0.103169,-0.007688,-0.024965,-0.005911,-0.012483,-0.024635,0.033398,-0.014053,0.015872,0.013723,0.000314,0.033728,-0.020088,0.016947,-0.061504,-0.046624,0.07407,-0.009383,0.001602,-0.040507,-0.071424,0.000899,-0.010127,-0.024635,-0.005828,0.03968,0.021989,-0.001684,-0.028272,0.035216,-0.046294,-0.002614,-0.027941,-0.020667,0.016368,0.001157,0.005952,0.007523,0.017195,0.038027,0.004402,-0.004505,0.057536,0.042987,-0.028438,-0.033728,0.010747,-0.004629,0.026123,0.014219,-0.003245,-0.028107,0.060182,0.03439,0.016947,-3.8e-05,-0.005229,0.013144,0.042987,0.007275,-0.028768,-0.000734,-0.002687,0.030091,-0.01488,-0.027611,-0.012813,-0.015707,-0.023477,0.001509,0.028934,-0.015376,0.000372,0.005456,-0.041334,0.032571,-0.030422,0.009837,-0.054891,-0.016368,0.005497,0.03224,-0.012648,-0.038027,0.002056,-0.035216,-0.017029,-0.046955,0.035712,0.019013,-0.023477,-0.033894,0.005787,0.021493,0.011491,0.0248,0.026288,0.035712,-0.031248,0.012896,0.025627,0.046955,-0.047947,-0.076054,0.054891,-0.045632,5.1e-05,0.006613,-0.003761,-0.021659,-0.038854,0.031414,-0.028438,-0.013061,-0.05952,-0.01612,-0.018021,0.002997,0.003038,-0.047286,-0.015376,-0.021163,-0.016285,-0.002893,-0.011656,0.021659,0.024469,0.01612,0.09391,0.030918,0.009672,-0.021659,0.056214,-0.04431,0.021824,-0.011325,0.014384,-0.0248,0.043318,0.005249,-0.010664,0.030422,0.060182,-0.006903,-0.038854,-0.000153,0.007936,-0.032075,0.008473,-0.008473,0.021989,0.020749,0.020667,-0.016037,-0.016781,-0.004898,0.00744,0.020088,0.026784,0.020088,0.005022,-0.036208,-0.00186,-0.006861,0.005663,-0.014797,0.052907,-0.013723,0.04431,-0.001963,0.043318,-0.006365,0.002501,-0.011987,0.024304,0.010375,-0.017608,-0.033728,0.018517,0.00092,0.002687,-0.004629,-0.002015,0.041499,0.010664,0.048278,0.011573,-0.065142,0.029926,0.018352,0.007812,-0.03439,0.019592,0.026784,0.0496,-0.007688,0.006531,-0.001457,0.0124,0.016285,0.004505,-0.014963,-0.030091,-0.07936,0.001602,0.013144,-0.026288,-0.00062,0.000297,-0.001225,-0.011408,-0.0124,0.007027,-0.004009,-0.003968,0.029926,0.007895,0.033563,0.013061,0.006696,0.009507,-0.009796,0.05456,-0.048608,0.006076,0.032902,-0.020667,-0.002914,0.000925,0.05423,0.011077,-0.036208,0.008845,-0.030752,-0.05919,0.04431,0.037035,-0.009011,-0.020749,0.007647,0.033894,-0.052246,0.037862,0.041334,0.019344,-0.075723,-0.004795,-0.000889,-0.011325,-0.006944,0.036539,0.021163,0.015211,0.075723,-0.02976,-0.022816,-0.027445,-0.014797,0.068779,0.03472,0.107137,-0.03439,-0.001059,-0.013723,-0.023973,0.046955,-0.000853,-0.05456,-0.025957,-0.044971,-0.0496,0.048608,-0.014219,0.010499,-0.015376,-0.026784,-0.023477,0.042326,0.018104,0.018517,0.046955,0.018269,-0.02976,0.028934,-0.031579,-0.009713,0.010747,-0.023477,0.062496,0.046624,-0.042987,0.070763,0.004898,-1.1e-05,-0.03439,0.001953,0.001788,0.016781,-0.02232,0.028768,0.044971,0.028768,-0.00868,-0.037035,0.001498,-0.02728,-0.006985,0.011656,-0.013557,0.010664,-0.052576,-0.026619,0.002645,0.021328,-0.009383,0.007688,-0.026619,0.045963,-0.037862,-0.024139,0.06448,-0.060843,0.045302,0.070432,-0.013805,0.023973,-0.066795,0.095233,0.006159,0.009011,0.04183,-0.065142,0.026123,-0.007068,-0.02232,0.016947,0.038027,0.014384,0.015211,-0.050262,0.038358,-0.008804,0.021659,0.03439,0.023973,0.00248,0.023477,0.002366,-0.003451,0.002459,0.095894,0.004898,-0.001059,0.034886,0.006944,0.005993,0.05952,-0.021328,0.005373,-0.037035,-0.001297,0.051584,-0.0496,0.028934,0.018021,0.042987,0.003989,-0.03191,0.043318,0.036043,0.017029,0.009383,-0.001405,-0.084651,-0.003079,-0.011325,0.004175,0.01488,-0.012483,0.041995,-0.018765,-0.011243,-0.001591,0.024635,0.01984,0.006241,0.009383,0.003761,0.04927,0.011325,0.020667,-0.022816,-0.0496,-0.014715,0.028107,0.001225,0.012152,-0.013888,-0.058198,0.03935,0.024635,0.072416,-0.048939,0.020336,0.015128,0.004237,-0.008597,0.031414,-0.040507,-0.018765,-0.011325,0.056544,0.029595,0.001044,-0.015789,0.05423,0.032902,-0.0031,-0.010333,-0.022816,-0.025461,0.006241,-0.000273,-0.011987,-0.038027,-0.061174,0.003865,-0.02943,0.012731,0.06448,-0.040507,0.011408,0.047947,0.015128,-0.011739,0.021659,0.012069,0.020997,-0.011325,0.003637,0.014549,-0.015045,0.011077,-0.008184,0.005869,-0.037862,-0.000806,0.018517,0.028603,0.00992,-0.000245,0.005249,-0.005084,-0.000692,-0.00094,-0.019179,-0.000625,-0.009135,-0.002811,-0.018104,-0.060182,-0.0248,0.000605,0.017856,0.005022,-0.017443,0.014384,-0.010127,-0.007523,0.041003,0.033563,-0.037366,0.003927,0.00806,-0.048278,0.016533,-0.021989,-0.009176,0.019013,0.022485,-0.005332,-0.026123,-0.014632,0.023973,-0.022155,0.016947,-0.020088,0.008184,-0.021493,0.027941,0.073408,0.03224,0.018104,-0.01736,-0.007275,0.031414,-0.007357,-0.04464,0.045302,-0.010664,-0.016203,0.010375,0.004567,0.0124,-0.009011,-0.010457')

            # Example 2: Perform similarity search in the Vector Store when question is stored in a table and output
            # should be returned in 'json' format.
            >>> load_data("amazon", "amazon_review_query")
            >>> response = vs.similarity_search_by_vector(data="amazon_review_query",
                                                          column="queryEmbedding",
                                                          return_type="json")
        """
        ## Initializing params
        for attr_name in SimilaritySearchParams:
            setattr(self, f"_{attr_name}", kwargs.get(attr_name, None))

        # Validating params
        arg_info_matrix = []
        arg_info_matrix.append(["question", self._question, True, (str), True])
        arg_info_matrix.append(["data", self._data, True, (str, DataFrame), True])
        arg_info_matrix.append(["column", self._column, True, (str), True])

        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Both data and column should be present or absent.
        _Validators._validate_mutually_inclusive_arguments(self._data, "data", self._column, "column")
        # If data is supplied, question should not be supplied or vice-versa
        _Validators._validate_mutually_exclusive_arguments(self._data, "data", self._question, "question")

        # Validate whether the column exists in DataFrame and extract table_name to be passed to service.
        if self._data is not None:
            if isinstance(self._data, str):
                db_name = UtilFuncs._extract_db_name(self._data)
                db_name = _get_user() if db_name is None else db_name
                table_name = UtilFuncs._extract_table_name(self._data)
                self._data = DataFrame(in_schema(db_name, table_name))
            _Validators._validate_dataframe_has_argument_columns(columns=self._column, column_arg="column",
                                                                 data=self._data, data_arg="data")
            self._data = _ProcessDataFrameObjects(self._data)[0]


        # Only add the keys which are not None and populate the params as needed by the service.
        input_index = {
            param_name: getattr(self, f"_{attr_name}")
            for attr_name, param_name in SimilaritySearchParams.items()
            if getattr(self, f"_{attr_name}") is not None
        }

        response = UtilFuncs._http_request(self.__similarity_search_embeddings_url.format(self.__url, self._log),
                                           HTTPRequest.POST,
                                           json=input_index,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})

        return _SimilaritySearch(self._process_vs_response(api_name="similarity-search",
                                                           response=response),
                                 return_type=kwargs.get("return_type"))

    @collect_queryband(queryband="VS_prepare_response")
    def prepare_response(self,
                         similarity_results,
                         question=None,
                         prompt=None,
                         **kwargs):
        """
        DESCRIPTION:
            Prepare a natural language response to the user using the input
            question and similarity_results provided by
            VectorStore.similarity_search() method.
            The response is generated by a language model configured
            in the environment using a pre-configured prompt.
            An optional parameter prompt can be used to specify a customized
            prompt that replaces the internal prompt.

        PARAMETERS:
            question:
                Required Argument, Optional for batch mode.
                Specifies a string of text for which response
                needs to be performed.
                Types: str

            similarity_results:
                Required Argument.
                Specifies the similarity results obtained by similarity_search().
                Types: list

            prompt:
                Optional Argument.
                Specifies a customized prompt that replaces the internal prompt.
                Types: str
            
            batch_data:
                Required for batch mode.
                Specifies the table name or teradataml DataFrame to be indexed for batch mode.
                Types: str, teradataml DataFrame

            batch_id_column:
                Required for batch mode.
                Specifies the ID column to be indexed for batch mode.
                Types: str

            batch_query_column:
                Required for batch mode.
                Specifies the query column to be indexed for batch mode.
                Types: str
            
            temperature:
                Optional Argument.
                Specifies the temperature for tuning the chat_completion_model.
                Types: float, int
                Permitted Values: [0.0, 2.0]

        RETURNS:
            str.

        RAISES:
            TypeError, TeradataMlException.

        EXAMPLES:
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")

            # Creates a Vector Store.
            # Note this step is not needed if vector store already exists.
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1",
                          search_algorithm='VECTORDISTANCE',
                          top_k=10
                          )

            # Perform similarity search in the Vector Store for
            # the input question.
            >>> question = 'Are there any reviews about books?'
            >>> response = vs.similarity_search(question=question)

            # Example 1: Prepare a natural language response to the user
            #            using the input question and similarity_results
            #            provided by similarity_search().

            question='Did any one feel the book is thin?'
            similar_objects_list = response['similar_objects_list']
            >>> vs.prepare_response(question=question,
                                    similarity_results=similar_objects_list)

            # Example 2: Perform batch similarity search in the Vector Store.
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs_batch")

            # Creates a Vector Store.
            # Note this step is not needed if vector store already exists.
            >>> vs.create(embeddings_model="amazon.titan-embed-text-v1",
                          embeddings_dims=2048,
                          chat_completion_model="anthropic.claude-3-haiku-20240307-v1:0",
                          search_algorithm="HNSW",
                          top_k=10,
                          object_names="valid_passages",
                          key_columns="pid",
                          data_columns="passage",
                          vector_column="VectorIndex")

            # Perform batch similarity search in the Vector Store.
            >>> vs.similarity_search(batch_data="valid_passages",
                                     batch_id_column="pid",
                                     batch_query_column="passage")

            # Get the similarity results.
            from teradatagenai import VSApi
            >>> similar_objects_list = vs.get_batch_result(api_name=VSApi.SimilaritySearch)

            # Perform batch prepare response with temperature.
            >>> vs.prepare_response(similarity_results=similar_objects_list,
                                    batch_data="valid_passages",
                                    batch_id_column="pid",
                                    batch_query_column="passage",
                                    temperature=0.7)

            # Retrieve the batch prepare response.
            >>> similarity_results = vs.get_batch_result(api_name=VSApi.PrepareResponse)

        """ 

        # Initializing params
        self._question = question
        self._similarity_results = similarity_results
        self._prompt = prompt
        self._temperature = kwargs.get('temperature', None)
        # Check if batch mode is enabled
        batch = self.__batch_mode_args_validation(**kwargs)

        # Validating params
        arg_info_matrix = []
        arg_info_matrix.append(["similarity_results", self._similarity_results, False, _SimilaritySearch, True])
        arg_info_matrix.append(["prompt", self._prompt, True, (str), True])
        arg_info_matrix.append(["temperature", self._temperature, True, (int, float), True])

        # Non-batch mode params
        if not batch:
            arg_info_matrix.append(["question", self._question, False, (str), True])

        _Validators._validate_missing_required_arguments(arg_info_matrix)

        # Explicitly checking similarity search API, as correct message is not displayed.
        if not isinstance(similarity_results, _SimilaritySearch):
            raise TypeError(Messages.get_message(MessageCodes.UNSUPPORTED_DATATYPE,
                                                 "similarity_results", "output of similarity_search()"))
        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        # data for prepare response
        data = {'similar_objects': self._similarity_results._json_obj,
                'prompt': self._prompt}

        # Prepare response in batch mode
        if batch:
            data['batch_input_index'] = self.__set_batch_index
            api_name = "prepare-response-batch"
            url = self.__batch_url.format(self.__url, api_name, self._log)
        else:
            # Non-batch mode
            api_name = "prepare-response"
            data['question'] = self._question
            url = self.__prepare_response_url
        
        # If temperature is set, add it to the data
        if self._temperature is not None:
            data['temperature'] = self._temperature

        # POST request for prepare response
        response = UtilFuncs._http_request(url, 
                                           HTTPRequest.POST,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id},
                                           json=data)
        
        response = self._process_vs_response(api_name=api_name, response=response)
        if batch:
            self.__display_status_check_message(batch)
            return
        return response


    @collect_queryband(queryband="VS_ask")
    def ask(self, 
            question=None,
            prompt=None,
            **kwargs):
        """
        DESCRIPTION:
            Performs similarity search in the vector store for
            the input question followed by preparing a natural
            language response to the user. This method combines
            the operation of similarity_search() and prepare_response()
            into one call for faster response time.

        PARAMETERS:
            question:
                Required Argument, Optional for batch mode.
                Specifies the question which needs to be answered.
                Types: str

            prompt:
                Optional Argument.
                Specifies a customized prompt that replaces the internal prompt.
                Types: str

            batch_data:
                Required for batch mode.
                Specifies the table name or teradataml DataFrame to be indexed for batch mode.
                Types: str, teradataml DataFrame

            batch_id_column:
                Required for batch mode.
                Specifies the ID column to be indexed for batch mode.
                Types: str

            batch_query_column:
                Required for batch mode.
                Specifies the query column to be indexed for batch mode.
                Types: str
            
            temperature:
                Optional Argument.
                Specifies the temperature for tuning the chat_completion_model.
                Types: float, int
                Permitted Values: [0.0, 2.0]

        RETURNS:
            str.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")

            # Create a Vector Store.

            # Note this step is not needed if vector store already exists.
            >>> vs.create(object_names="amazon_reviews_25",
                          description="vector store testing",
                          key_columns=['rev_id', 'aid'],
                          data_columns=['rev_text'],
                          vector_column='VectorIndex',
                          embeddings_model="amazon.titan-embed-text-v1",
                          search_algorithm='VECTORDISTANCE',
                          top_k=10
                          )

            >>> custom_prompt = '''List good reviews about the books. Do not assume information.
                                Only provide information that is present in the data.
                                Format results like this:
                                Review ID:
                                Author ID:
                                Review:
                                '''
            # Example 1: Perform similarity search in the Vector Store for
            #            the input question followed by preparing a natural
            #            language response to the user.

            >>> question = 'Are there any reviews saying that the books are inspiring?'
            >>> response = vs.ask(question=question, prompt=custom_prompt)

            # Example 2: Perform batch similarity search in the Vector Store.
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs_batch")

            # Create a Vector Store.
            >>> vs.create(embeddings_model="amazon.titan-embed-text-v1",
                          embeddings_dims=2048,
                          chat_completion_model="anthropic.claude-3-haiku-20240307-v1:0",
                          search_algorithm="HNSW",
                          top_k=10,
                          object_names="valid_passages",
                          key_columns="pid",
                          data_columns="passage",
                          vector_column="VectorIndex")

            # Perform batch similarity search followed by prepare response in the Vector Store with temperature of 0.7
            >>> prompt = "Structure the response briefly in 1-2 lines."
            >>> vs.ask(batch_data="home_depot_train",
                       batch_id_column="product_uid",
                       batch_query_column="search_term",
                       prompt=prompt,
                       temperature=0.7)

            # Retrieve the batch ask results.
            from teradatagenai import VSApi
            >>> ask_results = vs.get_batch_result(api_name=VSApi.Ask)

        """
        # Initializing params
        self._question = question
        self._prompt = prompt
        self._temperature = kwargs.get('temperature', None)
        # Validating batch mode arguments
        batch = self.__batch_mode_args_validation(**kwargs)

        # Validating params
        arg_info_matrix = []

        # Non-batch mode params
        if not batch: 
            arg_info_matrix.append(["question", self._question, False, (str), True])
        arg_info_matrix.append(["prompt", self._prompt, True, (str), True])
        arg_info_matrix.append(["temperature", self._temperature, True, (float, int), True])
        _Validators._validate_missing_required_arguments(arg_info_matrix)

        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Data for ask
        data = {'prompt': self._prompt}

        # Ask in batch mode
        if batch:
            # Data for batch mode
            data['batch_input_index'] = self.__set_batch_index
            api_name = "ask-batch"
            url = self.__batch_url.format(self.__url, api_name, self._log)
        else:
            # Non-batch mode
            data['question'] = self._question
            api_name = "ask"
            url = self.__ask_url
        # If temperature is set, add it to the data
        if self._temperature is not None:
            data['temperature'] = self._temperature

        # POST request for ask
        response = UtilFuncs._http_request(url,
                                           HTTPRequest.POST,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id},
                                           json=data)
        
        response = self._process_vs_response(api_name=api_name, response=response)
        if batch:
            self.__display_status_check_message(batch)
            return
        return response
    

    @property
    def __set_batch_index(self):
        """ Set the batch index for the batch APIs. """
        return {"batch_input_table": self._batch_data,
                "batch_input_id_column": self._batch_id_column,
                "batch_input_query_column": self._batch_query_column
                }
    
    def __batch_mode_args_validation(self, **kwargs):
        """
        DESCRIPTION:
            Internal method to validate the batch mode and batch arguments.

        PARAMETERS:
            batch_data:
                Required Argument for batch mode.
                Specifies the table name/teradataml DataFrame to be indexed for batch mode.
                Types: str, teradataml DataFrame

            batch_id_column:
                Required Argument for batch mode.
                Specifies the ID column to be indexed for batch mode.
                Types: str

            batch_query_column:
                Required Argument for batch mode.
                Specifies the query column to be indexed for batch mode.
                Types: str
            
        RETURNS:
            bool.

        RAISES:
            TeradataMlException.
        
        """
        # Check if any batch argument is available
        if len(kwargs) == 0:
            return False

        # initialize the batch arguments
        self._batch_data = kwargs.get('batch_data', None)
        self._batch_id_column = kwargs.get('batch_id_column', None)
        self._batch_query_column = kwargs.get('batch_query_column', None)

        # Check if any batch argument is available
        if any([self._batch_data, self._batch_id_column, self._batch_query_column]):

            # Validate batch arguments
            arg_info_matrix = []
            arg_info_matrix.append(["batch_data", self._batch_data, False, (str, DataFrame), True])
            arg_info_matrix.append(["batch_id_column", self._batch_id_column, False, (str), True])
            arg_info_matrix.append(["batch_query_column", self._batch_query_column, False, (str), True])
            _Validators._validate_missing_required_arguments(arg_info_matrix)

            # Validate argument types.
            _Validators._validate_function_arguments(arg_info_matrix)

            # Check if batch_data is not a string or not
            # if not, extract the table name string from the TeradataMl DataFrame
            if not isinstance(self._batch_data, str):
                self._batch_data = self._batch_data._table_name.replace("\"", "")

            return True
        
        return False
    
    def __display_status_check_message(self, batch=False):
        """ 
        DESCRIPTION:
            Internal method to display the status check message for Vector Store operations.

        PARAMETERS:
            batch:
                Optional Argument.
                Specifies whether to display the message for batch apis.
                Default Value: False
                Types: bool

        RETURNS:
            None.

        RAISES:
            None.

        EXAMPLES:
            # Display the status check message.
            >>> self.__display_status_check_message(batch=True)
        """
        print("Use the 'status()' api to check the status of the operation.")
        if batch:
            print("Use the 'get_batch_result()' api to retrieve the batch result.")

    @collect_queryband(queryband="VS_get_batch_result")
    def get_batch_result(self, api_name, **kwargs):
        """
        DESCRIPTION:
            Retrieves the batch result for the specified API.
            The API name can be one of the following:   
                * similarity-search
                * prepare-response
                * ask
            Applicable only for batch mode operations.

        PARAMETERS:
            api_name:
                Required Argument.
                Specifies the name of the API.
                Permitted Values:
                    * VSApi.SimilaritySearch
                    * VSApi.PrepareResponse
                    * VSApi.Ask
                Types: Enum(VSApi)

        RETURNS:
            * teradataml DataFrame containing the batch result for ask, prepare_response.
            * SimilaritySearch object for similarity_search.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")

            # Create a Vector Store.
            # Note this step is not needed if vector store already exists.
            >>> vs.create(embeddings_model="amazon.titan-embed-text-v1",
                          embeddings_dims=2048,
                          chat_completion_model="anthropic.claude-3-haiku-20240307-v1:0",
                          search_algorithm="HNSW",
                          top_k=10,
                          object_names="valid_passages",
                          key_columns="pid",
                          data_columns="passage",
                          vector_column="VectorIndex")

            # Perform batch similarity search in the Vector Store.
            >>> vs.similarity_search(batch_data="home_depot_train",
                                     batch_id_column="product_uid",
                                     batch_query_column="search_term")

            from teradatagenai import VSApi
            # Get the batch result for the similarity_search API.
            >>> res = vs.get_batch_result(api_name=VSApi.SimilaritySearch)

            # Perform batch prepare_response in the Vector Store.
            >>> prompt= "Structure response in question-answering format
                         Question: 
                         Answer:"
            >>> vs.prepare_response(batch_data="home_depot_train",
                                    batch_id_column="product_uid",
                                    batch_query_column="search_term",
                                    prompt=prompt)
            # Get the batch result for the prepare_response API.
            >>> res = vs.get_batch_result(api_name=VSApi.PrepareResponse)

            # Perform batch ask in the Vector Store.
            >>> vs.ask(batch_data="home_depot_train",
                       batch_id_column="product_uid",
                       batch_query_column="search_term",
                       prompt=prompt)
            # Get the batch result for the ask API.
            >>> res = vs.get_batch_result(api_name=VSApi.Ask)

        """
        # Initializing params
        self._api_name = api_name

        # Validating params
        arg_info_matrix = []
        arg_info_matrix.append(["api_name", self._api_name, False, (VSApi)])

        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        response = UtilFuncs._http_request(self.__batch_url.format(self.__url, 
                                                                   f"{self._api_name.value}-batch",
                                                                   self._log),
                                           HTTPRequest.GET,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        if 'status' in response.json():
            print(f"{response.json()['status'].capitalize()}. Try again after sometime.")
            return
        if self._api_name.value == "similarity-search":
            return _SimilaritySearch(self._process_vs_response(self._api_name.value, response), batch=True,
                                     return_type=kwargs.get("return_type"))
        else:
            data = self._process_vs_response(self._api_name.value, response)
            return VectorStore._convert_to_tdmldf(pd.DataFrame(data['response_list']))


    @staticmethod
    def _process_vs_response(api_name, response, success_status_code=None, raise_error=True):
        """
        DESCRIPTION:
            Process and validate the Vector Store service response.

        PARAMETERS:
            api_name:
                Required Argument.
                Specifies the name of the Vector Store method.
                Types: str

            response:
                Required Argument.
                Specifies the response recieved from Vector Store service.
                Types: requests.Response

            success_status_code:
                Optional Argument.
                Specifies the expected success status code for the corresponding
                Vector Store service.
                Default Value: None
                Types: int

            raise_error:
                Optional Argument.
                Specifies a boolean flag that decides whether to raise error or not.
                Default Values: True
                Types: bool

        RETURNS:
            Response object.

        RAISES:
            TeradataMlException, JSONDecodeError.

        EXAMPLES:
                >>> _process_vs_response("create", resp)
        """
        try:
            data = response.json()
            # Success status code ranges between 200-300.
            if (success_status_code is None and 200 <= response.status_code <= 303) or \
                    (success_status_code == response.status_code):
                if "message" in data:
                    if api_name not in ["similarity-search", "prepare-response", "ask"]:
                        print(data['message'])
                    return data['message']
                else:
                    return data
                return

            # teradataml API got an error response. Error response is expected as follows -
            # Success
            # Response:
            # {
            #     "message": "success string"
            # }
            # Failure
            # Response:
            # {
            #     "detail": "error message string"
            # }
            # Validation
            # Error:
            # {
            #     "detail": [
            #         {
            #             "loc": [
            #                 "string",
            #                 0
            #             ],
            #             "msg": "string",
            #             "type": "string"
            #         }
            #     ]
            # }
            # Extract the fields and raise error accordingly.
            if isinstance(data['detail'], str):
                error_description = data['detail']
            else:
                error_description = []
                for dict_ele in data['detail']:
                    error_msg = f"{dict_ele['msg']} for {dict_ele['loc'][1] if len(dict_ele['loc']) > 1 else dict_ele['loc'][0]}"
                    error_description.append(error_msg)
                error_description = ",".join(error_description)

            error_description = f'Response Code: {response.status_code}, Message:{error_description}'

            error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                             api_name,
                                             error_description)
            if api_name == "status" and "Vector store" in error_msg and 'does not exist.' in error_msg:
                print("Vector Store does not exist or it is has been destroyed successfully.")
                return
            if raise_error:
                raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)

        # teradatagenai API may not get a Json API response in some cases.
        # So, raise an error with the response received as it is.
        except JSONDecodeError:
            error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                             api_name,
                                             f'Response Code: {response.status_code}, Message: {response.text}')
            if raise_error:
                raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)
        except Exception as e:
            if raise_error:
                raise

    @staticmethod
    # TODO: https://teradata-pe.atlassian.net/browse/ELE-6100: Replace this with
    #  DataFrame.json() once implemented.
    def _convert_to_tdmldf(pdf, index=False):
        """
        DESCRIPTION:
            Converts pandas DataFrame to teradataml DataFrame.

        PARAMETERS:
            pdf:
                Required Argument.
                Specifies the pandas DataFrame to be converted to teradataml DataFrame.
                Types: pandas DF.

        RETURNS:
            teradataml DataFrame.

        RAISES:
            None.

        EXAMPLES:
           VectorStore._convert_to_tdmldf(pdDf)
        """
        # Form the table name and return teradataml DataFrame.
        table_name = UtilFuncs._generate_temp_table_name(prefix="vs",
                                                         table_type=TeradataConstants.TERADATA_TABLE,
                                                         gc_on_quit=True)
        if len(pdf) > 0:
            copy_to_sql(pdf, table_name, index=index)
            return DataFrame(table_name)

    @collect_queryband(queryband="VS_status")
    def status(self):
        """
        DESCRIPTION:
            Checks the status of the below operations:
               * create
               * destroy
               * update

        PARAMETERS:
            None.

        RETURNS:
            Pandas DataFrame containing the status of vector store operations.

        RAISES:
            None.

        EXAMPLES:
           # Create an instance of the VectorStore class.
           >>> vs = VectorStore(name="vs")
           # Example 1: Check the status of create operation.

           # Create VectorStore.
           # Note this step is not needed if vector store already exists.
           >>> vs.create(object_names="amazon_reviews_25",
                         description="vector store testing",
                         key_columns=['rev_id', 'aid'],
                         data_columns=['rev_text'],
                         vector_column='VectorIndex',
                         embeddings_model="amazon.titan-embed-text-v1")

           # Check status.
           >>> vs.status()
        """

        response = UtilFuncs._http_request(self.__common_url, HTTPRequest.GET,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        status_op = self._process_vs_response("status", response)
        if status_op is None:
            return
        if 'status' in status_op and 'failed' in status_op['status'].lower():
            # The status API has the following output:
            # {'vs_name': 'vs_example1', 'status': 'create failed',
            # 'error': 'Error in function
            # TD_VectorNormalize: Number of elements do not match with embedding size'}
            # The 'status' key contains text like 'create failed', 'update failed'.
            # Hence extracting the word before 'failed' to get the operation which has failed.
            api_name = re.search(r"(\w+)\s+" + re.escape('failed'), status_op['status'].lower()).group(1)
            msg = status_op["error"] if 'error' in status_op else ""

            error_msg = Messages.get_message(MessageCodes.FUNC_EXECUTION_FAILED,
                                             api_name, msg)
            raise TeradataMlException(error_msg, MessageCodes.FUNC_EXECUTION_FAILED)
        return pd.DataFrame([self._process_vs_response("status", response)])

    @collect_queryband(queryband="VS_list_user_permissions")
    def list_user_permissions(self):
        """
        DESCRIPTION:
            Lists the users and their corresponding permissions
            on the vector store.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            None.

        RETURNS:
            teradataml DataFrame containing the users and the
            corresponding permissions on the vector store.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # Create an instance of an already existing vector store.
            >>> vs = VectorStore(name="vs")

            # Example: List the user permissions on the vector store.
            >>> vs.list_user_permissions()
        """

        # Get the user permissions on the vector store.
        response = UtilFuncs._http_request(self.__list_user_permission_url,
                                           HTTPRequest.GET,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        # Process the response and return the user permissions.
        data = self._process_vs_response("list_user_permissions", response)
        return VectorStore._convert_to_tdmldf(pd.DataFrame({"Users": data['authenticated_users'].keys(),
                            "Permissions": data['authenticated_users'].values()}))
    
    @property
    def revoke(self):
        """
        DESCRIPTION:
            Revoke the permission of the user on the vector store.
            Notes:
                * Only admin users can use this method.
                * Admin can revoke admin/user permssions of other users and
                  admins on the vector store.
                * Admin/User cannot revoke his own permssions.
                * Admin cannot revoke user permissions of another admin.
                  First the admin permissions needs to be revoked and
                  then the user permission can be revoked.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # NOTE: It is assumed that vector store "vs" already exits.
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")
            # Revoke 'admin' permission of user 'alice' on the vector store 'vs'.
            >>> vs.revoke.admin('alice')
            # Revoke 'user' permission of user 'alice' on the vector store 'vs'.
            >>> vs.revoke.user('alice')
        """
        return _Revoke(self)
    
    @property
    def grant(self):
        """
        DESCRIPTION:
            Grant permissions to the user on the vector store.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            # NOTE: It is assumed that vector store "vs" already exits.
            # Create an instance of the VectorStore class.
            >>> vs = VectorStore(name="vs")
            # Grant 'admin' permission to the user 'alice' on the vector store 'vs'.
            >>> vs.grant.admin('alice')
            # Grant 'user' permission to the user 'alice' on the vector store 'vs'.
            >>> vs.grant.user('alice')
        """
        return _Grant(self)


class VSPattern:
    """
    Patterns are kind of regex which is used for combining names of tables or views
    matching the pattern string which can then be used for creating metadata based vector store.
    """
    def __init__(self,
                 name, 
                 log=False):
        """
        DESCRIPTION:
            Initialize the VSPattern class for metadata-based vector store.
            For metadata-based vector stores, the selection of tables/views can be huge.
            They can span multiple databases and it can become tedious to list them using
            "include_objects" and "exclude_objects".
            Patterns provide a way to select these tables/views and columns
            using simple regular expressions.

        PARAMETERS:
            name:
                Required Argument.
                Specifies the name of the pattern for vector store.
                Types: str

            log:
                Optional Argument.
                Specifies whether to enable logging.
                Default Value: False
                Types: bool

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VSPattern
            >>> pattern = VSPattern(pattern_name="metadata")
        """
        # Initialize variables.
        self._pattern_name = name
        self._enable_logging = log
        self._pattern_string = None

        # Validating name and enable_logging.
        arg_info_matrix = []
        arg_info_matrix.append(["name", self._pattern_name, False, (str), True])
        arg_info_matrix.append(["enable_logging", self._enable_logging, True, (bool)])

        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        # As the rest call accepts 0, 1 converting it.
        self._enable_logging = 0 if not self._enable_logging else 1

        # Initialize URLs.
        self.__pattern_url = f'{vector_store_urls.patterns_url}/{self._pattern_name}'
        self.__common_pattern_url = f'{self.__pattern_url}?log_level={self._enable_logging}'

        # Call connect in case of CCP enabled tenant.
        # If non-ccp, connect should be explicitly called passing the required params.
        session_header = VSManager._generate_session_id()
        self.__session_id = session_header["vs_session_id"]
        self.__headers = session_header["vs_header"]
    
    @property
    def __create_pattern_url(self):
        """ Returns the URL for creating the pattern. """
        return f'{self.__pattern_url}?pattern_string={self._pattern_string}'

    def get(self):
        """
        DESCRIPTION:
            Gets the list of objects that matches the pattern name.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            None.

        RETURNS:
            teradataml dataFrame containing the list of objects that matches the pattern name.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VSPattern
            >>> pattern = VSPattern(pattern_name="metadata")
            >>> pattern.create(pattern_string='SEMANTIC_DATA.CRICKET_%')
            >>> pattern.get()
        """
        response = UtilFuncs._http_request(self.__common_pattern_url, HTTPRequest.GET,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        # Process the response
        data = VectorStore._process_vs_response("get_pattern", response)
        return VectorStore._convert_to_tdmldf(pd.DataFrame({'Object list': data['object_list']}))
        
    def create(self, pattern_string):
        """
        DESCRIPTION:
            Creates the pattern for metadata-based vector store.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            pattern_string:
                Required Argument.
                Specifies the pattern string to be used for creating the pattern.
                A pattern string can be formed by using SQL wildcards "%" or "_".
                For example:
                    * `SEMANTIC_DATA.CRICKET%` - This pattern string will internally fetch all tables and
                                                 views in the SEMANTIC_DATA database starting with CRICKET
                                                 at the time of vector store creation.
                    * `log__` - This pattern string will internally fetch all tables and views starting
                                with log and having two extra characters like `log_a` or `log12` in the
                                logged-in database at the time of vector store creation.
                    * `data_.%` - This pattern string will internally fetch all tables and views in all
                                  databases starting with data and having one extra character like
                                  `data1.t1`, `data2.v2`, `datax.train` at the time of vector store creation.
                Types: str

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VSPattern
            >>> pattern = VSPattern(pattern_name="metadata")
            >>> pattern.create(pattern_string='SEMANTIC_DATA.CRICKET_%')
        """
        # Validating pattern_string.
        arg_info_matrix = []
        arg_info_matrix.append(["pattern_string", pattern_string, False, (str), True])

        # Validate argument types.
        _Validators._validate_function_arguments(arg_info_matrix)

        # Assign pattern_string.
        self._pattern_string = quote(pattern_string)

        response = UtilFuncs._http_request(self.__create_pattern_url, HTTPRequest.POST,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        # Process the response
        VectorStore._process_vs_response("create_pattern", response)

    def delete(self):
        """
        DESCRIPTION:
            Deletes the pattern.
            Notes:
                * Only admin users can use this method.
                * Refer to the 'Admin Flow' section in the
                  User guide for details.

        PARAMETERS:
            None.

        RETURNS:
            None.

        RAISES:
            TeradataMlException.

        EXAMPLES:
            >>> from teradatagenai import VSPattern
            >>> pattern = VSPattern(pattern_name="metadata")
            >>> pattern.delete()
        """
        response = UtilFuncs._http_request(self.__common_pattern_url, HTTPRequest.DELETE,
                                           headers=self.__headers,
                                           cookies={'session_id': self.__session_id})
        # Process the response
        VectorStore._process_vs_response("delete_pattern", response)
