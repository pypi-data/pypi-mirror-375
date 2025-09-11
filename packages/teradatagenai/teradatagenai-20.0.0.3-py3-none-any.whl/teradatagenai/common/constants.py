# -*- coding: utf-8 -*-
"""
Unpublished work.
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: aanchal.kavedia@teradata.com
Secondary Owner: PankajVinod.Purandare@teradata.com

teradatagenai.common.constants
----------
A class for holding all constants
"""
from enum import Enum
from teradataml.options.configure import configure
from teradataml.common.constants import HTTPRequest
from teradataml.common.utils import UtilFuncs
from teradataml.utils.validators import _Validators

class Action(Enum):
    # Holds variable names for the type of grant to be provided.
    GRANT = "GRANT"
    REVOKE = "REVOKE"

class Permission(Enum):
    # Holds variable names for the type of permission to be provided.
    USER = "USER"
    ADMIN = "ADMIN"

class VSApi(Enum):
    # Holds variable names for the type of API to be used.
    Ask = "ask"
    PrepareResponse = "prepare-response"
    SimilaritySearch = "similarity-search"

class VectorStoreURLs:
    # Class to store the vector store URLs
    @property
    def base_url(self):
        return f"{configure._vector_store_base_url}/api/v1/"

    @property
    def session_url(self):
        return f"{self.base_url}session"

    @property
    def vectorstore_url(self):
        return f"{self.base_url}vectorstores"

    @property
    def patterns_url(self):
        return f"{self.base_url}patterns"

class _Authenticate:
    """ Parent class to either grant or revoke access on the vector store. """

    def __init__(self, action, vs):
        """
        DESCRIPTION:
            Method to initialize the _Authenticate class.

        PARAMETERS:
            action:
                Required Arguments.
                Specifies the action to be performed (grant/revoke).
                Type: str

            vs:
                Required Arguments.
                Specifies the vector store object.
                Type: VectorStore
        
        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> _Authenticate(action="GRANT", vs=vs)
        """
        self.action = action
        self.vs = vs
        self.__set_user_permissions_url = "{0}permissions/{1}?user_name={2}&action={3}&permission={4}&log_level={5}"
        # Avoid circular import
        from teradatagenai.vector_store import VSManager
        self._session_header = VSManager._generate_session_id()
        self.__base_url = VectorStoreURLs().base_url

    def _submit_permission_request(self, username, permission):
        """
        DESCRIPTION:
            Internal function to submit the grant/revoke permission request to the vector store.

        PARAMETERS:
            username:
                Required Arguments.
                Specifies the name of the user.
                Type: str
            
            permission:
                Required Arguments.
                Specifies the type of permission to be provided.
                Type: str

        RETURNS:
            HTTP response

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Authenticate._submit_permission_request(username="test_user", permission=Permission.ADMIN.value)
        """
        # Validate the username
        arg_info_matrix = []
        arg_info_matrix.append(["username", username, False, (str), True])
        _Validators._validate_function_arguments(arg_info_matrix)

        # HTTP request to grant/revoke USER/ADMIN access to the user
        response = UtilFuncs._http_request(self.__set_user_permissions_url.format(
                                                                                  self.__base_url,
                                                                                  self.vs.name,
                                                                                  username,
                                                                                  self.action,
                                                                                  permission,
                                                                                  self.vs._log),
                                            HTTPRequest.PUT,
                                            headers=self._session_header['vs_header'],
                                            cookies={'session_id': self._session_header['vs_session_id']})
        # Return the response
        return response

    def admin(self, username):
        """
        DESCRIPTION:
            Internal function to provide admin permissions of the
            vector store to the user.

        PARAMETERS:
            username:
                Required Arguments.
                Specifies the name of the user.
                Type: str

        RETURNS:
            None

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Authenticate.admin(username="test_user")
        """
        # Submit the grant/revoke ADMIN permission request to the vector store for the user
        response = self._submit_permission_request(username, Permission.ADMIN.value)
        # Process the response
        self.vs._process_vs_response(self.action, response)

    def user(self, username):
        """
        DESCRIPTION:
            Internal function to provide user permissions to the vector store.

        PARAMETERS:
            username:
                Required Arguments.
                Specifies the name of the user.
                Type: str

        RETURNS:
            None

        RAISES:
            TeradataMLException

        EXAMPLES:
            >>> _Authenticate.user(username="test_user")
        """
        # Submit the grant/revoke USER permission request to the vector store for the user
        response = self._submit_permission_request(username, Permission.USER.value)
        # Process the response
        self.vs._process_vs_response(self.action, response)

class _Grant(_Authenticate):
    """ Class to grant access to the vector store."""
    def __init__(self, vs):
        super().__init__(Action.GRANT.value, vs)

class _Revoke(_Authenticate):
    """ Class to revoke access to the vector store."""
    def __init__(self, vs):
        super().__init__(Action.REVOKE.value, vs)

# Dict to map the python variable names of vs_parameters to REST variable names.
VSParameters = {
    "description": "description",
    "embeddings_model": "embeddings_model",
    "embeddings_dims": "embeddings_dims",
    "metric": "metric",
    "search_algorithm": "search_algorithm",
    "top_k": "top_k",
    "initial_centroids_method": "initial_centroids_method",
    "train_numcluster": "train_numcluster",
    "max_iternum": "max_iternum",
    "stop_threshold": "stop_threshold",
    "seed": "seed",
    "num_init": "num_init",
    "search_threshold": "search_threshold",
    "search_numcluster": "search_numcluster",
    "prompt": "prompt",
    "chat_completion_model": "chat_completion_model",
    "ef_search": "ef_search",
    "num_layer": "num_layer",
    "ef_construction": "ef_construction",
    "num_connpernode": "num_connPerNode",
    "maxnum_connpernode": "maxNum_connPerNode",
    "apply_heuristics": "apply_heuristics",
    "rerank_weight": "rerank_weight",
    "relevance_top_k": "relevance_top_k",
    "relevance_search_threshold": "relevance_search_threshold",
    "time_zone": "time_zone",
    "ignore_embedding_errors": "ignore_embedding_errors",
    "chat_completion_max_tokens": "chat_completion_max_tokens",
    "completions_base_url": "base_url_completions",
    "embeddings_base_url": "base_url_embeddings",
    "ingest_host": "doc_ingest_host",
    "ingest_port": "doc_ingest_port"
}

# Dict to map the python variable names of vs_index to REST variable names.
VSIndex = {
    "target_database": "target_database",
    "object_names": "object_names",
    "key_columns": "key_columns",
    "data_columns": "data_columns",
    "vector_column": "vector_column",
    "chunk_size": "chunk_size",
    "optimized_chunking": "optimized_chunking",
    "is_embedded": "is_embedded",
    "is_normalized": "is_normalized",
    "header_height": "header_height",
    "footer_height": "footer_height",
    "include_objects": "include_objects",
    "exclude_objects": "exclude_objects",
    "include_patterns": "include_patterns",
    "exclude_patterns": "exclude_patterns",
    "sample_size": "sample_size",
    "alter_operation": "alter_operation",
    "update_style": "update_style",
    "nv_ingestor": "nv_ingestor",
    "display_metadata": "display_metadata",
    "extract_text": "extract_text",
    "extract_images": "extract_images",
    "extract_tables": "extract_tables",
    "extract_method": "extract_method",
    "tokenizer": "tokenizer",
    "extract_infographics": "extract_infographics",
    "hf_access_token": "hf_access_token"
}

# Dict to map the python variable names of vs_parameters to REST variable names.
SimilaritySearchParams = {
    "data": "input_table",
    "column": "input_query_column",
    "question": "question_vector"
}

VECTOR_STORE_SEARCH_PARAMS = {
"metric": {
    "argument_name": "metric",
    "required": "Optional Argument",
    "description": """Specifies the metric to be used for calculating the distance
                      between the vectors.""",
    "notes": "",
    "default_values": "COSINE",
    "permitted_values": "EUCLIDEAN, COSINE, DOTPRODUCT",
    "types": "str",
},

"search_algorithm": {
    "argument_name": "search_algorithm",
    "required": "Optional Argument",
    "description": """Specifies the algorithm to be used for searching the
                      tables and views relevant to the question.""",
    "notes": "",
    "default_values": "VECTORDISTANCE",
    "permitted_values": "VECTORDISTANCE, KMEANS, HNSW",
    "types": "str",
},

"initial_centroids_method": {
    "argument_name": "initial_centroids_method",
    "required": "Optional Argument",
    "description": """Specifies the algorithm to be used for initializing the
                      centroids.""",
    "notes": """Applicable when "search_algorithm" is 'KMEANS'.""",
    "default_values": "RANDOM",
    "permitted_values": "RANDOM, KMEANS++",
    "types": "str",
},

"train_numcluster": {
    "argument_name": "train_numcluster",
    "required": "Optional Argument",
    "description": """Specifies the number of clusters to be trained.""",
    "notes": """Applicable when "search_algorithm" is 'KMEANS'.""",
    "default_values": "",
    "permitted_values": "",
    "types": "int",
},

"max_iternum": {
    "argument_name": "max_iternum",
    "required": "Optional Argument",
    "description": """Specifies the maximum number of iterations to be run during
                      training.""",
    "notes": """Applicable when "search_algorithm" is 'KMEANS'.""",
    "default_values": 10,
    "permitted_values": "[1, 2147483647]",
    "types": "int",
},

"stop_threshold": {
    "argument_name": "stop_threshold",
    "required": "Optional Argument",
    "description": """Specifies the threshold value at which training should be
                      stopped.""",
    "notes": """Applicable when "search_algorithm" is 'KMEANS'.""",
    "default_values": 0.0395,
    "permitted_values": "",
    "types": "float",
},

"seed": {
    "argument_name": "seed",
    "required": "Optional Argument",
    "description": """Specifies the seed value to be used for random number
                      generation.""",
    "notes": """Applicable when "search_algorithm" is 'KMEANS'.""",
    "default_values": 0,
    "permitted_values": "[0, 2147483647]",
    "types": "int",
},

"num_init": {
    "argument_name": "num_init",
    "required": "Optional Argument",
    "description": """Specifies the number of times the k-means algorithm should
                      run with different initial centroid seeds.""",
    "notes": "",
    "default_values": 1,
    "permitted_values": "[1, 2147483647]",
    "types": "int",
},

"top_k": {
    "argument_name": "top_k",
    "required": "Optional Argument",
    "description": """Specifies the number of top clusters to be considered while searching.""",
    "notes": "",
    "default_values": 10,
    "permitted_values": "[1, 1024]",
    "types": "int",
},

"search_threshold": {
    "argument_name": "search_threshold",
    "required": "Optional Argument",
    "description": """Specifies the threshold value to consider for matching tables/views
                      while searching. A higher threshold value limits responses to the top matches only.""",
    "notes": """Applicable when "search_algorithm" is 'VECTORDISTANCE' and 'KMEANS'.""",
    "default_values": "",
    "permitted_values": "",
    "types": "float",
},

"search_numcluster": {
    "argument_name": "search_numcluster",
    "required": "Optional Argument",
    "description": """Specifies the number of clusters to be considered while
                      searching.""",
    "notes": """Applicable when "search_algorithm" is 'KMEANS'.""",
    "default_values": "",
    "permitted_values": "",
    "types": "int",
},

"ef_search": {
    "argument_name": "ef_search",
    "required": "Optional Argument",
    "description": """Specifies the number of neighbors to be considered during search
                      in HNSW graph.""",
    "notes": """Applicable when "search_algorithm" is 'HNSW'.""",
    "default_values": 32,
    "permitted_values": "[1, 1024]",
    "types": "int",
},

"num_layer": {
    "argument_name": "num_layer",
    "required": "Optional Argument",
    "description": """Specifies the maximum number of layers for the HNSW graph.""",
    "notes": """Applicable when "search_algorithm" is 'HNSW'.""",
    "default_values": "",
    "permitted_values": "[1, 1024]",
    "types": "int",
},

"ef_construction": {
    "argument_name": "ef_construction",
    "required": "Optional Argument",
    "description": """Specifies the number of neighbors to be considered during
                      construction of the HNSW graph.""",
    "notes": """Applicable when "search_algorithm" is 'HNSW'.""",
    "default_values": 32,
    "permitted_values": "[1, 1024]",
    "types": "int",
},

"num_connpernode": {
    "argument_name": "num_connpernode",
    "required": "Optional Argument",
    "description": """Specifies the number of connections per node in the HNSW graph
                      during construction.""",
    "notes": """Applicable when "search_algorithm" is 'HNSW'.""",
    "default_values": 32,
    "permitted_values": "[1, 1024]",
    "types": "int",
},

"maxnum_connpernode": {
    "argument_name": "maxnum_connpernode",
    "required": "Optional Argument",
    "description": """Specifies the maximum number of connections per node in the
                      HNSW graph during construction.""",
    "notes": """Applicable when "search_algorithm" is 'HNSW'.""",
    "default_values": 32,
    "permitted_values": "[1, 1024]",
    "types": "int",
},

"apply_heuristics": {
    "argument_name": "apply_heuristics",
    "required": "Optional Argument",
    "description": """Specifies whether to apply heuristics optimizations during construction
                      of the HNSW graph.""",
    "notes": """Applicable when "search_algorithm" is 'HNSW'.""",
    "default_values": True,
    "permitted_values": "",
    "types": "bool",
},

"rerank_weight": {
    "argument_name": "rerank_weight",
    "required": "Optional Argument",
    "description": """Specifies the weight to be used for reranking the search results.
                      Applicable range is 0.0 to 1.0.""",
    "notes": "",
    "default_values": 0.2,
    "permitted_values": "",
    "types": "float",
},

"relevance_top_k": {
    "argument_name": "relevance_top_k",
    "required": "Optional Argument",
    "description": """Specifies the number of top similarity matches to be considered for reranking.
                      Applicable range is 1 to 1024.""",
    "notes": "",
    "default_values": 60,
    "permitted_values": "[1, 1024]",
    "types": "int",
},

"relevance_search_threshold": {
    "argument_name": "relevance_search_threshold",
    "required": "Optional Argument",
    "description": """Specifies the threshold value to consider matching tables/views while reranking.
                      A higher threshold value limits responses to the top matches only.""",
    "notes": "",
    "default_values": "",
    "permitted_values": "",
    "types": "float",
},
}

FILE_BASED_VECTOR_STORE_PARAMS = {
"chunk_size": {
    "argument_name": "chunk_size",
    "required": "Optional Argument",
    "description": """Specifies the number of characters in each chunk to be used while
                      splitting the input file.""",
    "notes": """Applicable only for 'file-based' vector stores.""",
    "default_values": 512,
    "permitted_values": "",
    "types": "int",
},

"optimized_chunking": {
    "argument_name": "optimized_chunking",
    "required": "Optional Argument",
    "description": """Specifies whether an optimized splitting mechanism supplied by
                      Teradata should be used. The documents are parsed internally in an
                      intelligent fashion based on file structure and chunks are dynamically
                      created based on section layout.""",
    "notes": """* The "chunk_size" field is not applicable when
               "optimized_chunking" is set to True.
              * Applicable only for 'file-based' vector stores.""",
    "default_values": False,
    "permitted_values": "",
    "types": "bool",
},

"nv_ingestor": {
    "argument_name": "nv_ingestor",
    "required": "Optional Argument",
    "description": """Specifies whether to use NVIDIA NV-Ingest for processing the
                      document files.""",
    "notes": """* Applicable only while using NVIDIA NIM endpoints.
               * Applicable only for 'file-based' vector stores.""",
    "default_values": False,
    "permitted_values": "",
    "types": "bool",
},

"display_metadata": {
    "argument_name": "display_metadata",
    "required": "Optional Argument",
    "description": """Specifies whether to display metadata describing objects extracted
                      from document files when using NVIDIA NV-Ingest.""",
    "notes": """* Applicable only for 'file-based' vector stores.
                * Applicable only while using NVIDIA NIM endpoints and
                  when "nv_ingestor" is set to True.""",
    "default_values": False,
    "permitted_values": "",
    "types": "bool",
},

"extract_text": {
    "argument_name": "extract_text",
    "required": "Optional Argument",
    "description": """Specifies whether to extract text from the document files when
                      using NVIDIA NV-Ingest.""",
    "notes": """* Applicable only for 'file-based' vector stores.
                * Applicable only while using NVIDIA NIM endpoints and
                  when "nv_ingestor" is set to True.""",
    "default_values": True,
    "permitted_values": "",
    "types": "bool",
},

"extract_images": {
    "argument_name": "extract_images",
    "required": "Optional Argument",
    "description": """Specifies whether to extract images from the document files when
                      using NVIDIA NV-Ingest.""",
    "notes": """* Applicable only for 'file-based' vector stores.
                * Applicable only while using NVIDIA NIM endpoints and
                  when "nv_ingestor" is set to True.""",
    "default_values": True,
    "permitted_values": "",
    "types": "bool",
},

"extract_tables": {
    "argument_name": "extract_tables",
    "required": "Optional Argument",
    "description": """Specifies whether to extract tables from the document files when
                      using NVIDIA NV-Ingest.""",
    "notes": """* Applicable only for 'file-based' vector stores.
                * Applicable only while using NVIDIA NIM endpoints and
                    when "nv_ingestor" is set to True.""",
    "default_values": True,
    "permitted_values": "",
    "types": "bool",
},

"extract_infographics": {
    "argument_name": "extract_infographics",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies whether to extract infographics from
                      document files.""",
    "notes": """* Applicable only for 'file-based' vector stores.
                * Applicable only while using NVIDIA NIM endpoints and
                  when "nv_ingestor" is set to True.""",
    "default_values": False,
    "permitted_values": "",
    "types": "bool",
},

"extract_method": {
    "argument_name": "extract_method",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the method to be used for extracting text from
                      the document files.""",
    "notes": """* Applicable only for 'file-based' vector stores.
                * Applicable only while using NVIDIA NIM endpoints and
                  when "nv_ingestor" is set to True.""",
    "default_values": "pdfium",
    "permitted_values": "pdfium, nemoretriever_parse",
    "types": "str",
},

"tokenizer": {
    "argument_name": "tokenizer",
    "required": "Optional Argument",
    "description": """Specifies the tokenizer to be used for splitting the text into chunks.""",
    "notes": """* Applicable only when "nv_ingestor" is set to True
               and "document_files" is supplied.
              * Applicable only while using NVIDIA NIM endpoints.""",
    "default_values": "meta-llama/Llama-3.2-1B",
    "permitted_values": "",
    "types": "str",
},

"header_height": {
    "argument_name": "header_height",
    "required": "Optional Argument",
    "description": """Specifies the height (in points) of the header section of a PDF
                      document to be trimmed before processing the main content.
                      This is useful for removing unwanted header information
                      from each page of the PDF. Recommended value is 55.""",
    "notes": """* Applicable only for 'file-based' vector stores.""",
    "default_values": 0,
    "permitted_values": "",
    "types": "int",
},

"footer_height": {
    "argument_name": "footer_height",
    "required": "Optional Argument",
    "description": """Specifies the height (in points) of the footer section of a PDF
                      document to be trimmed before processing the main content.
                      This is useful for removing unwanted footer information from
                      each page of the PDF. Recommended value is 55.""",
    "notes": """* Applicable only for 'file-based' vector stores.""",
    "default_values": 0,
    "permitted_values": "",
    "types": "int",
},

"ingest_host": {
    "argument_name": "ingest_host",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the HTTP host for the service to be used for document parsing.""",
    "notes": """* Applicable only while using NVIDIA NIM endpoints.""",
    "default_values": "",
    "permitted_values": "",
    "types": "str",
},

"ingest_port": {
    "argument_name": "ingest_port",
    "required": "Optional Argument",
    "description": """Specifies the HTTP port for the service to be used for document parsing.""",
    "notes": """* Applicable only while using NVIDIA NIM endpoints.""",
    "default_values": 7670,
    "permitted_values": "",
    "types": "int",
},
}

LANGCHAIN_PARAMS = {
    "embeddings_langchain": {
    "argument_name": "embedding",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the embeddings model to be used for generating the
                        embeddings.""",
    "notes": "",
    "default_values": """ For AWS: amazon.titan-embed-text-v2:0
                        For Azure: text-embedding-3-small""",
    "permitted_values": """For AWS:
                            * amazon.titan-embed-text-v1
                            * amazon.titan-embed-image-v1
                            * amazon.titan-embed-text-v2:0
                            For Azure:
                            * text-embedding-ada-002
                            * text-embedding-3-small
                            * text-embedding-3-large""",
    "types": "str, TeradataAI, LangChain Embeddings",
},

"chat_completion_model_lc": {
    "argument_name": "chat_completion_model",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the name of the chat completion model to be used for
                        generating text responses.""",
    "notes": "",
    "default_values": """ For AWS: anthropic.claude-3-haiku-20240307-v1:0
                        For Azure: gpt-35-turbo-16k""",
    "permitted_values": """*For AWS:
                                * anthropic.claude-3-haiku-20240307-v1:0
                                * anthropic.claude-instant-v1
                                * anthropic.claude-3-5-sonnet-20240620-v1:0
                            *For Azure:
                                * gpt-35-turbo-16k""",
    "types": "str, TeradataAI, LangChain BaseChatModel",
},
}

NIM_PARAMS = {
"embeddings_tdgenai": {
    "argument_name": "embedding",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the embeddings model to be used for generating the
                        embeddings.""",
    "notes": "",
    "default_values": """ For AWS: amazon.titan-embed-text-v2:0
                        For Azure: text-embedding-3-small""",
    "permitted_values": """For AWS:
                            * amazon.titan-embed-text-v1
                            * amazon.titan-embed-image-v1
                            * amazon.titan-embed-text-v2:0
                            For Azure:
                            * text-embedding-ada-002
                            * text-embedding-3-small
                            * text-embedding-3-large""",   
    "types": "str, TeradataAI",
},

"embeddings_dims": {
    "argument_name": "embeddings_dims",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the number of dimensions to be used for generating the embeddings.
                        The value depends on the "embeddings".""",
    "notes": "",
    "default_values": """ * For AWS:
                                * amazon.titan-embed-text-v1: 1536
                                * amazon.titan-embed-image-v1: 1024
                                * amazon.titan-embed-text-v2:0: 1024
                            * For Azure:
                                * text-embedding-ada-002: 1536
                                * text-embedding-3-small: 1536
                                * text-embedding-3-large: 3072""",
    "permitted_values": """*For AWS:
                                * amazon.titan-embed-text-v1: 1536
                                * amazon.titan-embed-image-v1: [256, 384, 1024]
                                * amazon.titan-embed-text-v2:0: [256, 512, 1024]
                            *For Azure:
                                * text-embedding-ada-002: 1536 only
                                * text-embedding-3-small: 1 <= dims <= 1536
                                * text-embedding-3-large: 1 <= dims <= 3072""",
    "types": "str",
},

"chat_completion_model_tdgenai": {
    "argument_name": "chat_completion_model",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the name of the chat completion model to be used for
                        generating text responses.""",
    "notes": "",
    "default_values": """ For AWS: anthropic.claude-3-haiku-20240307-v1:0
                        For Azure: gpt-35-turbo-16k""",
    "permitted_values": """*For AWS:
                                * anthropic.claude-3-haiku-20240307-v1:0
                                * anthropic.claude-instant-v1
                                * anthropic.claude-3-5-sonnet-20240620-v1:0
                            *For Azure:
                                * gpt-35-turbo-16k""",
    "types": "str, TeradataAI",
},

"embeddings_base_url": {
    "argument_name": "embeddings_base_url",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the base URL for the service to be used for generating embeddings.""",
    "notes": """* Applicable only while using NVIDIA NIM endpoints.""",
    "default_values": "",
    "permitted_values": "",
    "types": "str",
},

"completions_base_url": {
    "argument_name": "completions_base_url",
    "required": "Optional Argument",
    "description": """Specifies the base URL for the service to be used for generating completions.""",
    "notes": """* Applicable only while using NVIDIA NIM endpoints.""",
    "default_values": "",
    "permitted_values": "",
    "types": "str",
},

"chat_completion_max_tokens": {
    "argument_name": "chat_completion_max_tokens",
    "required": "Required for NVIDIA NIM, Optional otherwise",
    "description": """Specifies the maximum number of tokens to be generated by the
                      "chat_completion_model".""",
    "notes": "",
    "default_values": 16384,
    "permitted_values": "[1, 16384]",
    "types": "int",

},
}

COMMON_PARAMS = {
"description": {
    "argument_name": "description",
    "required": "Optional Argument",
    "description": """Specifies the description of the vector store.""",
    "notes": "",
    "default_values": "",
    "permitted_values": "",
    "types": "str",
},
"target_db": {
    "argument_name": "target_database",
    "required": "Optional Argument",
    "description": """Specifies the database name where the vector store is created.""",
    "notes": """* If not specified, vector store is created in the database
                which is in use.""",
    "default_values": "",
    "permitted_values": "",
    "types": "str",
},
"vector_column": {
    "argument_name": "vector_column",
    "required": "Optional Argument",
    "description": """Specifies the name of the column to be used for storing
                      the embeddings.""",
    "notes": "",
    "default_values": "vector_index",
    "permitted_values": "",
    "types": "str",
},
}

UPDATE_PARAMS ={
    "update_style": {
        "argument_name": "update_style",
        "required": "Optional Argument",
        "description": """Specifies the style to be used for alter operation of the data
                          from the vector store when "search_algorithm" is KMEANS/HNSW.""",
        "notes": "",
        "default_values": "MINOR",
        "permitted_values": "MINOR, MAJOR",
        "types": "str",
    },
}