# ##################################################################
#
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Kesavaragavan B (kesavaragavan.b@teradata.com)
# Secondary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
#                  Snigdha Biswas (snigdha.biswas@teradata.com)
#
# Notes: 
#   * This code is only for internal use. 
#   * The code may perform modify, create, or delete operations 
#     in database based on given query. Hence, limit the permissions 
#     granted to the credentials.
# This file provides access to the LLM endpoints for inference.
# ##################################################################
# Import required packages.

import json
import os
from abc import ABC, abstractmethod
from time import sleep
from typing import Optional
from dotenv import dotenv_values
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.deprecations import argument_deprecation

from teradatagenai.common.exceptions import TeradataGenAIException
from teradataml import configure, create_env, get_env, list_user_envs
from teradataml import save_byom, retrieve_byom, delete_byom, ONNXEmbeddings
from teradataml.scriptmgmt.UserEnv import UserEnv
from teradataml.utils.validators import _Validators
from teradataml.hyperparameter_tuner.utils import _ProgressBar
from teradataml.common.utils import UtilFuncs
from teradatasqlalchemy.types import (BIGINT, BLOB, VARCHAR)
        
class _TeradataAIStruct(ABC):
    """
    Abstract class for holding the structure as well as the
    common functions/methods.
    """
    def __init__(self, api_type, model_name):
        """
        DESCRIPTION:
            Constructor for the _TeradataAIStruct class.

        PARAMETERS:
            api_type:
               Required Argument.
               Specifies the LLM API type.
               Permitted Values: 'azure', 'aws', 'gcp', 'hugging_face'
               Types: str

            model_name:
               Required Argument.
               Specifies the LLM model name.
               Types: str

        RETURNS:
            None

        RAISES:
            None
        """
        self.api_type = api_type
        self.model_name = model_name

    @abstractmethod
    def get_llm(self):
        """
        DESCRIPTION:
            Get the LLM inference endpoint.

        PARAMETERS:
            None

        RETURNS:
            LLM endpoint object, str

        RAISES:
            None
        """
        pass

class _TeradataAIFPF(_TeradataAIStruct):
    """
    Class to hold the functions required to set up the enviornment
    and initialize the LLM endpoint.
    """
    def __init__(self, api_type, model_name, **kwargs):
        """
        DESCRIPTION:
            Function sets up the environment and initializes the LLM endpoint.

        PARAMETERS:
            api_key:
                Required Argument, Optional if 'authorization' is provided.
                Specifies the API key for Azure OpenAI.
                Note:
                    Applicable only if "api_type" is 'azure'.
                Types: str

            access_token:
                Required Argument, Optional if 'authorization' is provided.
                Specifies the access token for GCP.
                Note:
                    Applicable only if "api_type" is 'gcp'.
                Types: str

            access_key:
                Required Argument, Optional if 'authorization' is provided.
                Specifies the access key for AWS Bedrock.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: str

            api_type:
                Required Argument.
                Specifies the LLM API type.
                Permitted Values: 'azure', 'aws', 'gcp', 'hugging_face'
                Types: str

            authorization:
                Optional argument, Required if:
                    * For Azure: "api_key", "api_base", and "api_version" are not provided.
                    * For AWS: "access_key", "secret_key" and "session_key" are not provided.
                    * For GCP: "access_token", "project" and "region" are not provided.
                Specifies the authorization object name for the LLM API.
                Note:
                    Applicable only if "api_type" is 'azure', 'aws', 'nim' or 'gcp'.
                Types: str

            deployment_id:
                Required Argument.
                Specifies the deployment ID of the LLM.
                It takes engine id for Azure OpenAI.
                Note:
                    Applicable only if "api_type" is 'azure'.
                Types: str

            model_name:
                Required Argument.
                Specifies the LLM model name.
                Types: str

            api_base:
                Required Argument, Optional if "authorization" is provided.
                Specifies AzureAI LLM endpoint URL.
                Note:
                    Applicable only if "api_type" is 'azure'.
                Types: str

            api_version:
                Required Argument, Optional if "authorization" is provided.
                Specifies the api version of LLM in use.
                Note:
                    Applicable only if "api_type" is 'azure'.
                Types: str

            region:
                Required argument, Optional for 'gcp' if 'authorization' is provided.
                Specifies the AWS bedrock or Google Cloud region.
                Note:
                    Applicable only if "api_type" is either 'gcp' or 'aws'.
                Types: str

            secret_key:
                Required Argument, Optional if "authorization" is provided.
                Specifies the secret key for AWS Bedrock.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: str

            session_key:
                Optional Argument.
                Specifies the session key for AWS Bedrock.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: str

            project:
                Required Argument, Optional if "authorization" is provided.
                Specifies the name of the GCP project.
                Note:
                    Applicable only if "api_type" is 'gcp'.
                Types: str

            enable_safety:
                Optional Argument.
                Specifies whether to enable safety settings for the gcp inference.
                Note:
                    Applicable only if "api_type" is 'gcp'.
                Default Value: True
                Types: bool

        RETURNS:
           None

        RAISES:
           TeradataMlException, ValueError, TypeError

        EXAMPLES:
            >>> llm = _TeradataAIFPF(api_type = "azure",
                                     model_name = 'gpt-35-turbo',
                                     api_key = "999***",
                                     api_base = "https://***.openai.azure.com/",
                                     api_version = "2021-12-35",
                                     deployment_id = "gpt-35-turbo")

        """
        self.__deployment_id = kwargs.get('deployment_id', None)
        self.__api_key = kwargs.get('api_key', None)
        self.__api_base = kwargs.get('api_base', None)
        self.__api_version = kwargs.get('api_version', None)
        self.__region = kwargs.get('region', None)
        self.__secret_key = kwargs.get('secret_key', None)
        self.__session_key = kwargs.get('session_key', None)
        self.__authorization = kwargs.get('authorization', None)
        self._project = kwargs.get('project', None)
        self._model_args = kwargs.get('model_args', None)
        self.__access_key = kwargs.get('access_key', None)
        self.__access_token = kwargs.get('access_token', None)
        self._enable_safety = kwargs.get("enable_safety", True)

        super().__init__(api_type=api_type, model_name=model_name)

        if self.__authorization is not None:
            # Validate mutually exclusive arguments.
            if api_type == "azure":
                _Validators._validate_mutually_exclusive_arguments(self.__authorization, "authorization", 
                                                                   any([self.__api_key, self.__api_base, self.__api_version]), 
                                                                   "[api_key, api_base, api_version]",)
            if api_type == "aws":
                _Validators._validate_mutually_exclusive_arguments(self.__authorization, "authorization",
                                                                   any([self.__access_key, self.__secret_key, self.__session_key]),
                                                                   "[access_key, secret_key, session_key]")
            if api_type == "gcp":
                _Validators._validate_mutually_exclusive_arguments(self.__authorization, "authorization",
                                                                   any([self.__access_token, self._project, self.__region]),
                                                                   "[access_token, project, region]")
            if api_type == "nim":
                _Validators._validate_mutually_exclusive_arguments(self.__authorization, "authorization",
                                                                   any([self.__api_key]), 
                                                                   "[api_key]")

        arg_matrix = []
        arg_matrix.append(["authorization", self.__authorization, True, (str), True])
        if api_type == "azure" and self.__authorization is None:
            arg_matrix.append(["api_key", self.__api_key, False, (str), True])
            arg_matrix.append(["api_base", self.__api_base, False, (str), True])
            arg_matrix.append(["api_version", self.__api_version, False, (str), True])
            arg_matrix.append(["deployment_id", self.__deployment_id, False, (str), True])

        if api_type == "aws" and self.__authorization is None:
            arg_matrix.append(["access_key", self.__access_key, False, (str), True])
            arg_matrix.append(["region", self.__region, False, (str), True])
            arg_matrix.append(["secret_key", self.__secret_key, False, (str), True])
            arg_matrix.append(["session_key", self.__session_key, True, (str), True])

        if api_type == "gcp" and self.__authorization is None:
            arg_matrix.append(["access_token", self.__access_token, False, (str), True])
            arg_matrix.append(["project", self._project, False, (str), True])
            arg_matrix.append(["region", self.__region, False, (str), True])
            arg_matrix.append(["enable_safety", self._enable_safety, True, (bool)])
        
        if api_type == "nim" and self.__authorization is None:
            arg_matrix.append(["api_key", self.__api_key, False, (str), True])
            arg_matrix.append(["api_base", self.__api_base, False, (str), True])

        # Validate missing required arguments.
        _Validators._validate_missing_required_arguments(arg_matrix)

        # Validate argument types.
        _Validators._validate_function_arguments(arg_matrix)

    def get_llm_params(self):
        """
        DESCRIPTION:
            Get the parameters specific to a CSP in a dictionary.

        PARAMETERS:
            None

        RETURNS:
            dict

        RAISES:
            None

        EXAMPLES:
            obj.get_llm_params()
        """
        if self.api_type == "azure":
            return {
                "authorization": self.__authorization,
                "api_key": self.__api_key,
                "api_base": self.__api_base,
                "api_version": self.__api_version,
                "deployment_id": self.__deployment_id,
                "model_name": self.model_name,
                # Convert model_args to json string if it is not None for the FPF.
                "model_args": json.dumps(self._model_args) if self._model_args is not None else None 
            }
        elif self.api_type == "aws":
            return {
                "authorization": self.__authorization,
                "access_key": self.__access_key,
                "region": self.__region,
                "secret_key": self.__secret_key,
                "session_key": self.__session_key,
                "model_name": self.model_name,
                # Convert model_args to json string if it is not None for the FPF.
                "model_args": json.dumps(self._model_args) if self._model_args is not None else None
            }
        elif self.api_type == "gcp":
            return {
                "authorization": self.__authorization,
                "access_token": self.__access_token,
                "project": self._project,
                "region": self.__region,
                # Convert enable_safety to string for FPF processing.
                "enable_safety": str(self._enable_safety),
                "model_name": self.model_name,
                # Convert model_args to json string if it is not None for FPF processing.
                "model_args": json.dumps(self._model_args) if self._model_args is not None else None
            }
        elif self.api_type == "nim":
            return {
                "authorization": self.__authorization,
                "api_key": self.__api_key,
                "api_base": self.__api_base,
                "model_name": self.model_name,
                # Convert model_args to json string if it is not None for the FPF.
                "model_args": json.dumps(self._model_args) if self._model_args is not None else None
            }
        return None

    def get_llm(self):
        """
        DESCRIPTION:
            Get LLM model name.

        PARAMETERS:
            None

        RETURNS:
            LLM model name.

        RAISES:
            None

        EXAMPLES:
            obj.get_llm()
        """
        return self.model_name

class _TeradataAIHuggingFace(_TeradataAIStruct):

    """
    Class to hold the functions required to setup the enviornment
    to use the hugging face models.
    """
    def __init__(self, model_name, **kwargs):
        """
        DESCRIPTION:
            Constructor to instantiate the class.
            Instantiation helps setup the environment,
            which includes downlaoding and installing the hugging face model.
            Prerequites for BYO LLM:
                * Bring Your Own LLM is a capability of Teradata’s Open Analytics Framework
                  which works on Vantage Cloud Lake on AWS only.
                * The combination of LLMs and GPU processing significantly boosts performance,
                  leading to a larger impact. To support these capabilities,
                  Teradata has added a new Analytic GPU cluster to the VantageCloud
                  Lake environment. Though BYO LLM work with Analytic clusters,
                  it is advisable to use with Analytic GPU clusters.
                Notes:
                    * When using any api_type as 'hugging_face', make sure to,
                        * establish connection with database using 'create_context()' function from teradataml.
                        * authenticate against the CCP using 'set_auth_token()' function from teradataml.
                    * Currently we can bring in hugging face models only upto 5 GB.

        PARAMETERS:
           api_type:
               Required Argument.
               Specifies the LLM API type.
               Permitted Values: 'azure', 'aws', 'vertexai', 'hugging_face'
               Types: str

           model_name:
               Required Argument.
               Specifies the LLM model name.
               Types: str

           model_args:
               Required Argument.
               Specifies the LLM arguments for generation.
               It can include the following keys:
                   - 'transformer_class': Sets the class specific to the model which allows
                                          easy loading of models.
                   - 'task': Specifies the task defining which pipeline will be returned.
                             This is used for doing tasks like sentiment-analysis,
                             summarization using the same model.
                             Note: Set the 'task' here if it is common to all TextAnalytics
                                   functions else we can set them at individual function calls.
                             More details can be found here:
                                https://huggingface.co/docs/transformers/en/main_classes/pipelines.
               Types: dict

           ues_args:
               Optional Argument.
               Specifies the parameters for the user environment service.
               It can include the following arguments:
                   - 'env_name': Specifies the remote user env. It can be the
                                 name of env or the UserEnv object.
               Types: dict

           asynchronous:
                Optional Argument.
                Specifies whether the model installation should be asynchronous.
                Default Value: False
                Types: bool

        RETURNS:
           None

        RAISES:
           TeradataMlException, ValueError, TypeError

        EXAMPLES:
            # Import the required modules.
            >>> from teradatagenai import TeradataAI

            # Example 1: Setup the environment to work with the
            #            'xlm-roberta-base-language-detection' hugging_face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task': 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Example 2: Setup the environment 'demo' to work with the
            #            'xlm-roberta-base-language-detection' hugging_face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> ues_args = {'env_name': 'demo'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args,
                                 ues_args = ues_args)
        """
        super().__init__(api_type="hugging_face", model_name=model_name)

        self._ues_args = kwargs.get("ues_args", {})
        self.model_args = kwargs.get('model_args', None)
        arg_matrix = []
        arg_matrix.append(["ues_args", self._ues_args, True, dict])
        arg_matrix.append(["model_args", self.model_args, False, dict])

        # Validate missing required arguments.
        _Validators._validate_missing_required_arguments(arg_matrix)
        # Validate argument types.
        _Validators._validate_function_arguments(arg_matrix)

        # Validate model_args and ues_args
        self.model_name = model_name
        self._transformer_class = self.model_args.get('transformer_class', None)
        self._task = self.model_args.get('task', None)
        env_name = self._ues_args.get("env_name", "td_gen_ai_env")
        self.__asynchronous = kwargs.get('asynchronous', None)
        arg_matrix = []
        arg_matrix.append(["transformer_class", self._transformer_class, False, str, True])
        arg_matrix.append(["task", self._task, True, (str), True])
        arg_matrix.append(["env_name", env_name, True, (str, UserEnv), True])
        arg_matrix.append(["asynchronous", self.__asynchronous, True, bool, True])

        # Validate missing required arguments.
        _Validators._validate_missing_required_arguments(arg_matrix)

        # Validate argument types.
        _Validators._validate_function_arguments(arg_matrix)

        # Set the example-data path which is base dir for all the example files.
        self.__base_dir = os.path.dirname(os.path.dirname(__file__))

        # Create/set a default env - td_gen_ai_env if env_name is not provided by the user.
        if isinstance(env_name, UserEnv):
            self._env = env_name
        else:
            # Get environments created by the current logged in user.
            user_envs_df = list_user_envs()
            is_none_user_env = user_envs_df is None
            env_not_exists = env_name not in user_envs_df.env_name.values if not is_none_user_env else True
            # If there are no envs or if the given env_name does not exist,
            # raise an error if it is anything other than default env.
            # If its default env, create it.
            if is_none_user_env or env_not_exists:
                if env_name == "td_gen_ai_env":
                    json_file = os.path.join(self.__base_dir, "example-data",
                                             "td_gen_ai_env_template.json")
                    create_env(template=json_file)
                # Raise an error if any other env_name is given which is not present.
                else:
                    raise Exception(
                        "User environment not present. Either use the default environment"
                        " or create the environment and pass the name.")
            # Get the env from env_name.
            self._env = get_env(env_name)
        print(f"Using env: '{env_name}'.")
        self._local_model = False  # Flag to track if model is installed using the old way
        self._install_model(**kwargs)
        self._llm = model_name

    def _install_model(self, **kwargs):
        """
        DESCRIPTION:
            Install the model if not present in the user_env.

        PARAMETERS:
            asynchronous:
                Optional Argument.
                Specifies whether the model installation should be asynchronous.
                Default Value: False
                Types: bool

        RETURNS:
            None

        RAISES:
            None
        """
        model_installed = False
        if self._env.models is not None:
            installed_models = self._env.models["Model"].to_list()
            # Create search patterns for different model name formats
            model_normalized = self.model_name.replace('/', '--') 
            models_prefixed = f"models--{model_normalized}"
            simple_name = self.model_name.split('/')[-1]
            
            # First, search for the model in HF cache format (models-- prefix)
            for model in installed_models:
                if models_prefixed in model:
                    model_installed = True
                    break
            
            # If not found in HF cache format, check for simple model name and set local_model flag
            if not model_installed:
                for model in installed_models:
                    if simple_name in model:
                        model_installed = True
                        self._local_model = True  # Set flag when found with simple name
                        # Issue deprecation warning for outdated model installation
                        print(f"DeprecationWarning: Model '{self.model_name}' was found installed using a legacy method. "
                              f"Consider reinstalling the model to use the current standard format for better compatibility.")
                        break
            
        if self._env.models is None or (not(model_installed)):
            print("Fetching the model from Hugging Face and installing it in the user environment.")

            claim_id = self._env.install_model(model_name=self.model_name, asynchronous=True)

            # If asynchronous is set to False, the cursor will not move ahead
            # and will keep checking till the model is installed.
            if not self.__asynchronous:
                status = "STARTED"
                pg = _ProgressBar(jobs=100, prefix="Installing", verbose=2)
                while True:
                    if status.upper() in ['FILE INSTALLED', 'ERRORED', 'MODELINSTALLED']:
                        pg.completed_jobs = 99
                        pg.update(msg="Model Installation completed.")
                        break

                    response = self._env.status(claim_id).to_dict('records')
                    status = response[-1].get("Stage", "")
                    pg.update()
                    sleep(20)
        else:
            print("Model is already available in the user environment.")

    def get_llm(self):
        """
        DESCRIPTION:
            Get the name of hugging face model.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Import the required modules.
            >>> from teradatagenai import TeradataAI

            # Example 1: Setup the environment to work with the
            #            'xlm-roberta-base-language-detection' hugging_face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task': 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)
            # Get the LLM in use.
            >>> llm.get_llm()
        """
        return self.model_name

    def remove(self):
        """
        DESCRIPTION:
            Remove the installed hugging_face model.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Import the required modules.
            >>> from teradatagenai import TeradataAI

            # Example 1: Removing the installed model
            #            'xlm-roberta-base-language-detection'.

            # Setup the env and install the model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Remove the model
            >>> llm.remove()
        """
        # Find the actual installed model name using expanded search logic
        models_to_remove = []
        if self._env.models is not None:
            installed_models = self._env.models["Model"].to_list()
            
            # Create search patterns for different model name formats
            model_normalized = self.model_name.replace('/', '--')
            models_prefixed = f"models--{model_normalized}"
            simple_name = self.model_name.split('/')[-1]
            
            for model in installed_models:
                # Check for HF cache format with models-- prefix
                if models_prefixed in model:
                    models_to_remove.append(model)
                # Check for simple model name (just the part after /)
                elif simple_name in model:
                    models_to_remove.append(model)
        
        if models_to_remove:
            for model_to_remove in models_to_remove:
                print(f"Uninstalling model from user environment: '{model_to_remove}'.")
                self._env.uninstall_model(model_to_remove)
                print(f"Successfully uninstalled model: '{model_to_remove}'.")
        else:
            print(f"Model '{self.model_name}' not found in user environment.")

    def get_env(self):
        """
        DESCRIPTION:
            Get the user enviornment in use.

        PARAMETERS:
            None

        RETURNS:
            UserEnv object.

        RAISES:
            None

        EXAMPLES:
            # Example 1: Get the user enviornment in use while installing the
            #           'xlm-roberta-base-language-detection' hugging face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)
            >> llm.get_env()
        """
        return self._env

    def get_model_args(self):
        """
        DESCRIPTION:
            Get the model args which are being used.
            Specifically the 'transformer_class' and the 'pipeline'.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            # Example 1: Get the model args which are used while installing the
            #           'xlm-roberta-base-language-detection' hugging face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)
            >>> llm.get_model_args()
        """
        return self.model_args

    def task(self, **kwargs):
        """
        DESCRIPTION:
            This function can do any task which the llm supports.
            The advantage of this method is that it is not bounded
            to any operation and can be tweaked
            according to the requirements.
            Refer to the example for more details on how it can be used.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column(s) of the teradataml DataFrame
                which needs to be used for inferencing.
                Types: str or list of str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column(s)
                specified in "column" to analyze the content from.
                Types: teradataml DataFrame

            returns:
                Required Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns ‘text’ and ‘sentiment’
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Default Value: {"Text": VARCHAR(10000), "Sentiment": VARCHAR(10000)}
                Types: dict

            script:
                Required Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
                Types: str

            persist:
                Optional Argument.
                Specifies whether to persist the output or not.
                When set to True, results are stored in permanent tables,
                otherwise in volatile tables.
                Default Value: False
                Types: bool

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    1) The "quotechar" cannot be the same as the Delimiter.
                    2) The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Note:
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on python library name(s)
                to be installed.
                Types: str OR list of str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> import os
            >>> import teradatagenai
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> from teradataml import DataFrame
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_articles = data.select(["employee_id", "employee_name", "articles"])
            >>> base_dir = os.path.dirname(teradatagenai.__file__)

            # Create LLM endpoint.
            >>> model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            >>> model_args = {'transformer_class': 'AutoModelForTokenClassification',
                              'task': 'token-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Example 1: Generate the embeddings for employee reviews from the 'articles' column
            #            of a teradataml DataFrame using hugging face model 'all-MiniLM-L6-v2'.

            >>> embeddings_script = os.path.join(base_dir,
                                                 'example-data',
                                                 'embeddings.py')
            # Construct returns argument based on the user script.
            >>> returns = OrderedDict([('text', VARCHAR(512))])

            >>> _ = [returns.update({"v{}".format(i+1): VARCHAR(1000)}) for i in range(384)]
            >>> llm.task(column = "articles",
                         data = df_articles,
                         script = embeddings_script,
                         returns = returns,
                         libs = 'sentence_transformers',
                         delimiter = '#')

            # Example 2: Get the similarity score for 'employee_data' and 'articles' columns
            #            using the same hugging face model: 'all-MiniLM-L6-v2'.
            >>> sentence_similarity_script = os.path.join(base_dir, 'example-data',
                                                          'sentence_similarity.py')
            >>> llm.task(column = ["employee_data", "articles"],
                         data = data,
                         script = sentence_similarity_script,
                         libs = 'sentence_transformers',
                         returns = {"column1": VARCHAR(10000),
                                    "column2": VARCHAR(10000),
                                    "similarity_score": VARCHAR(10000)},
                         delimiter = "#")
        """
        from teradatagenai.text_analytics.TextAnalyticsAIHuggingFace\
            import _TextAnalyticsAIHuggingFace

        validate_matrix = []
        validate_matrix.append(["script", kwargs.get('script', None),
                                False, (str)])
        validate_matrix.append(["returns", kwargs.get('returns', None), False, (str)])
        # Validate missing required arguments.
        _Validators._validate_missing_required_arguments(validate_matrix)

        return _TextAnalyticsAIHuggingFace(self)._exec(allows_list_in_columns=True,**kwargs)
    
    def cleanup_env(self):
        """
            Cleanup the user environment by removing the installed sample files.
        """
        env = self._env

        # Get list of files in the environment as a Python list
        if env.files is not None and not env.files.empty:
            file_list = [str(f).strip() for f in env.files["File"]]
            # Filter files that start with "td_sample_"
            sample_files = [f for f in file_list if f.startswith("td_sample_")]

            # Remove each sample file individually
            for file_name in sample_files:
                try:
                    env.remove_file(file_name=file_name, force_remove=True)
                except Exception as e:
                    print(f"Failed to remove file {file_name}: {e}")
        else:
            print("No files found in the environment.")

class _TeradataAIONNX(_TeradataAIStruct):
    """
    Class to hold the functions required to store externally trained
    models in ONNX format to Vantage.
    """
    def __init__(self, api_type , model_name, **kwargs):
        """
        DESCRIPTION
            Constructor to instantiate the class.
            Instantiation helps store externally trained models of ONNX 
            format in Vantage.
            Notes:
                * When using any "api_type" as 'onnx', ensure you have
                  established connection with database using 'create_context()'
                  from teradataml.
                If user specified table exists (for either model or tokenizer), it must:
                    a. Containt at least 2 columns:
                        * 'model_id' of type VARCHAR (any length)
                        * 'model' of type BLOB and,
                    b. Optionally include additional columns for extra metadata.
                If user-specified tables do not exist:
                    a. For the model table:
                        - The table is created with the name in "model_table_name"
                          and the id in "model_id".
                        - If "model_table_name" is not provided, defaults to
                          'td_genai_byom_models'.
                    b. For the tokenizer table:
                        - The table is created with the name in "tokenizer_table_name" and
                          the id in "tokenizer_id".
                        - If "tokenizer_table_name" is not provided, defaults to
                          'td_genai_byom_tokenizers'.
                        - If "tokenizer_id" is not provided, it defaults to the same value
                          as "model_id".
                    c. User may specify both schema and table names using corresponding
                        schema_name and table_name arguments.
                        If schema is not specified, the current schema is used.
                        See save_byom() in the teradataml User Guide for more details.
                    d. Created tables contain:
                        - 'model_id' column as VARCHAR(128)
                        - 'model' column as BLOB
        
        PARAMETERS
            api_type:
                Required Argument.
                Specifies the LLM API type.
                Permitted Values: 'onnx'
                Types: str

            model_name:
                Required Argument.
                Specifies the name of the ONNX model.
                Types: str
            
            model_id:
                Required Argument.
                Specifies the unique model identifier for model.
                Types: str

            model_path:
                Optional Argument. Required if ONNX model is not saved in the database.
                Specifies the absolute path of the file which has the ONNX model.
                Types: str
            
            tokenizer_id:
                Optional Argument.
                Specifies the unique model identifier for tokenizer.
                Note:
                    If not specified, defaults to value of "model_id".
                Types: str

            tokenizer_path:
                Optional Argument. Required if ONNX model is not saved in the database.
                Specifies the absolute path of the tokenizer JSON file.
                Types: str

            model_table_name:
                Optional Argument.
                Specifies the name of the table where model should be saved or is
                to be read from. 
                Types: str
            
            tokenizer_table_name:
                Optional Argument.
                Specifies the name of the table where tokenizer is saved or is 
                to be read from.
                Types: str

            table_name:
                Optional Argument.
                Specifies the name of the table where model and tokenizer are saved.
                Types: str
            
            schema_name:
                Optional Argument.
                Specifies the database name where model and tokenizer is saved.
                Note:
                    * If specified, then "table_name" must also be provided.
                Types: str

            model_schema_name:
                Optional Argument.
                Specifies the database name for the model table.
                Note:
                    * If specified, then "model_table_name" must also be provided.
                Types: str
            
            tokenizer_schema_name:
                Optional Argument.
                Specifies the database name for the tokenizer table.
                Note:
                    * If specified, then "tokenizer_table_name" must also be provided.
                Types: str

            additional_columns_model, additional_columns_tokenizer:
                Optional Argument.
                Specify additional information to be saved in the model or tokenizer 
                respectively. Passed as a dictionary of key-value pairs, where the key 
                is the column name and the value is the data to be stored for the 
                model/tokenizer being saved.
                Notes:
                    1. Following are the allowed types for the values passed in dictionary:
                        * int
                        * float
                        * str
                        * bool
                        * datetime.datetime
                        * datetime.date
                        * datetime.time
                        * bytes
                    2. This argument does not accept keys model_id and model.
                Types: dict
            
            additional_columns_types_model, additional_columns_types_tokenizer:
                Optional Argument.
                Specifies the column type of the additional columns. Additional column 
                datatype information is passed as key value pair with key being the 
                column name and value as teradatasqlalchemy.types.
                Note:
                    If any of the column type for additional columns are not specified,
                    it then derives the column type according to the below table:
                    +---------------------------+-----------------------------------------+
                    |     Python Type           |        teradatasqlalchemy Type          |
                    +---------------------------+-----------------------------------------+
                    | str                       | VARCHAR(1024)                           |
                    +---------------------------+-----------------------------------------+
                    | int                       | INTEGER                                 |
                    +---------------------------+-----------------------------------------+
                    | bool                      | BYTEINT                                 |
                    +---------------------------+-----------------------------------------+
                    | float                     | FLOAT                                   |
                    +---------------------------+-----------------------------------------+
                    | datetime                  | TIMESTAMP                               |
                    +---------------------------+-----------------------------------------+
                    | date                      | DATE                                    |
                    +---------------------------+-----------------------------------------+
                    | time                      | TIME                                    |
                    +---------------------------+-----------------------------------------+
                    | bytes                     | BLOB                                    |
                    +---------------------------+-----------------------------------------+
                Types: dict
        
        RETURNS:
            None

        RAISES:
            TeradataMlException, ValueError, TypeError
        
        EXAMPLE:
            # Example 1: Create LLM endpoint for api type onnx for the
            #            ONNX model 'bge-small-en-v1.5' with "model_id"
            #            as 'bge-small-model' , "model_table_name" as 
            #            'onnx_models', "tokenizer_id" as 'bge-small-tokenizer',
            #            "tokenizer_table_name" as 'onnx_tokenizers'
            >>> from teradatagenai import TeradataAI
            >>> llm = TeradataAI(api_type = "onnx",
                                 model_name = "bge-small-en-v1.5",
                                 model_id = "bge-small-model",
                                 tokenizer_id = "bge-small-tokenizer",
                                 model_path = "/path/to/onnx/model",
                                 tokenizer_path = "/path/to/tokenizer",
                                 model_table_name = "onnx_models",
                                 tokenizer_table_name = "onnx_tokenizers"
                                )
        """
        super().__init__(api_type=api_type, model_name=model_name)
        # arg_matrix = []

        self.model_id       = kwargs.get("model_id", None)
        self.tokenizer_id   = kwargs.get("tokenizer_id", None)

        self.__model_path      = kwargs.get("model_path", None)
        self.__tokenizer_path  = kwargs.get("tokenizer_path", None)

        #----------- Depreacted Arguments -------------------
        self.old_table_name = kwargs.get("table_name", None)
        self.old_schema_name = kwargs.get("schema_name", None)

        # ---------- 1 · Raw user table / schema values ------------------
        raw_model_table_name          = kwargs.get("model_table_name", None)
        raw_model_schema_name         = kwargs.get("model_schema_name", None)

        raw_tok_table_name      = kwargs.get("tokenizer_table_name", None)
        raw_tok_schema_name     = kwargs.get("tokenizer_schema_name", None)

        # ---------- 2 · Validate table / schema dependencies ------------
        if self.old_table_name or raw_model_table_name:
            _Validators._validate_mutually_exclusive_arguments(self.old_table_name, "table_name",
                                                               raw_model_table_name, "model_table_name"
            )

        _Validators._validate_dependent_argument(
            "schema_name", self.old_schema_name, "table_name", self.old_table_name
        )

        _Validators._validate_dependent_argument(
            "model_schema_name", raw_model_schema_name, "model_table_name", raw_model_table_name
        )
        _Validators._validate_dependent_argument(
            "tokenizer_schema_name", raw_tok_schema_name,
            "tokenizer_table_name", raw_tok_table_name
        )
        
        # ---------- 3 · Apply defaults *after* the dependency checks ----
        self.model_table_name    = raw_model_table_name or "td_genai_byom_models"
        self.model_schema_name    = raw_model_schema_name

        self.tokenizer_table_name  = raw_tok_table_name or "td_genai_byom_tokenizers"
        self.tokenizer_schema_name = raw_tok_schema_name


        # Check if model_table_name or tokenizer_table_name is 
        self.__explicit_new_tables = any(v is not None for v in (
            raw_model_table_name, raw_tok_table_name
        ))

        # ---------- 4 · Extra columns -----------------------------------
        self.__additional_columns_model     = kwargs.get("additional_columns_model", {})
        self.__additional_columns_types_model = kwargs.get("additional_columns_types_model", {})
        self.__additional_columns_tokenizer = kwargs.get("additional_columns_tokenizer", {})
        self.__additional_columns_types_tokenizer = kwargs.get("additional_columns_types_tokenizer", {})

        # ---------- 5 · Validator matrix (re-uses project helpers) ------
        arg_matrix = []
        arg_matrix.append(["model_id", self.model_id, False, (str,), True])
        _Validators._validate_missing_required_arguments(arg_matrix)

        arg_matrix.append(["model_path", self.__model_path, True, (str,)])
        arg_matrix.append(["tokenizer_path", self.__tokenizer_path, True, (str,)])
        arg_matrix.append(["tokenizer_id", self.tokenizer_id, True, (str,)])
        arg_matrix.append(["model_table_name", self.model_table_name, True, (str,)])
        arg_matrix.append(["model_schema_name", self.model_schema_name, True, (str,)])
        arg_matrix.append(["tokenizer_table_name", self.tokenizer_table_name, True, (str,)])
        arg_matrix.append(["tokenizer_schema_name", self.tokenizer_schema_name, True, (str,)])
        arg_matrix.append(["additional_columns_model", self.__additional_columns_model, True, dict])
        arg_matrix.append(["additional_columns_types_model", self.__additional_columns_types_model, True, dict])
        arg_matrix.append(["additional_columns_tokenizer", self.__additional_columns_tokenizer, True, dict])
        arg_matrix.append(["additional_columns_types_tokenizer", self.__additional_columns_types_tokenizer, True, dict])

        _Validators._validate_function_arguments(arg_matrix)

        if self.__model_path is not None or self.__tokenizer_path is not None:
            _Validators._validate_mutually_inclusive_n_arguments(
                model_path=self.__model_path,
                tokenizer_path=self.__tokenizer_path
            )

            # If paths provided, ensure "table_name" is not provided.
            if self.old_table_name:
                error_code = MessageCodes.CANNOT_USE_TOGETHER_WITH
                base_msg = Messages.get_message(
                    error_code,
                    "table_name",
                    "model_path"
                )
                custom_msg = "Use 'model_table_name' and 'tokenizer_table_name' instead."
                error_msg = base_msg + custom_msg
                raise TeradataMlException(error_msg, error_code)

        # Inherit model_id → tokenizer_id when saving & no explicit ID.
        if self.__model_path and not self.tokenizer_id:
            self.tokenizer_id = self.model_id
        
        # Initialize modeldata and tokenizer_data
        self.model_data     = None
        self.tokenizer_data = None

        # Handle the model logic.
        self._handle_model_logic()

    def _handle_model_logic(self):
        """
        DESCRIPTION:
            Function handles the logic to either save or retrieve the ONNX model
            based on the parameters provided to TeradataAI class.
        
        PARAMETERS:
            None
        
        RETURNS:
            None
        
        RAISES:
            TeradataMlException
        """
        # Determine the intent to save or retrieve the model and tokenizer.
        # Currently saving is only done if both model and tokenizer paths are provided.
        saving_pair = bool(self.__model_path or self.__tokenizer_path)

        if saving_pair:
            self._save_pair()
            self._retrieve_pair()
        else:
            self._retrieve_pair()

    def _save_pair(self):
        """
        DESCRIPTION:
            Function to save both the ONNX model and tokenizer to Teradata Vantage.

        PARAMETERS:
            None
        
        RETURNS:
            None

        RAISES:
            TeradataMlException
        """ 
        try:
            print(f"Saving model id '{self.model_id}' to {self.model_table_name}")
            save_byom(
                model_id=self.model_id,
                model_file=self.__model_path,
                table_name=self.model_table_name,
                schema_name=self.model_schema_name,
                additional_columns=self.__additional_columns_model,
                additional_columns_types=self.__additional_columns_types_model
            )

        except TeradataMlException as e:
            # idempotent save OK; otherwise propagate
            if getattr(e, "error_code", None) == MessageCodes.MODEL_ALREADY_EXISTS:
                print(f"Model id {self.model_id} already exists in table {self.model_table_name}")
            else:
                raise e
        
        # Save for tokenizer
        try:
            print(f"Saving tokenizer id '{self.tokenizer_id}' to {self.tokenizer_table_name}")
            save_byom(
                model_id=self.tokenizer_id,
                model_file=self.__tokenizer_path,
                table_name=self.tokenizer_table_name,
                schema_name=self.tokenizer_schema_name,
                additional_columns=self.__additional_columns_tokenizer,
                additional_columns_types=self.__additional_columns_types_tokenizer
            )
        except TeradataMlException as e:
            # idempotent save OK; otherwise propagate
            if getattr(e, "error_code", None) == MessageCodes.MODEL_ALREADY_EXISTS:
                print(f"Tokenizer id {self.tokenizer_id} already exists in table {self.tokenizer_table_name}")
            else:
                raise e

    def _retrieve_pair(self):
        """
        DESCRIPTION:
            Internal function to decide whether to retrieve the ONNX model and tokenizer
            from the new tables or fall back to the legacy table.
        
        PARAMETERS:
            None
        
        RETURNS:
            None
        
        RAISES:
            TeradataMlException
        """
        # ----- Case 1: Distinct tokenizer_id provided. Don't fallback to legacy table -------------
        if self.tokenizer_id and self.tokenizer_id != self.model_id:
            self._retrieve_new_pair(mandatory=True)
            return

        # ----- Case 2: User provided old_table_name. Always fallback to legacy table -----------------
        if self.old_table_name:
            self._retrieve_legacy_pair(
                self.old_table_name, self.old_schema_name
            )
            return

        # ----- Default path: try new tables, maybe fall back -------------
        try:
            self._retrieve_new_pair(mandatory=False)
            return
        except TeradataMlException as e_new:
            # Fallback if model_table_name or tokenizer_table_name are not provided and 
            # tokenizer_id is not specified.
            can_be_legacy = (
                not self.__explicit_new_tables
                and (self.tokenizer_id is None or self.tokenizer_id == self.model_id)
            )
            # If we can't fall back to legacy tables, propagate the error.
            if not can_be_legacy:
                raise e_new

            print(
                "Model/tokenizer not found in default tables – "
                "attempting legacy table lookup..."
            )
            self._retrieve_legacy_pair("td_genai_byom", None)

    # ------------------------------------------------------------------ #
    def _retrieve_new_pair(self, mandatory):
        """
        DESCRIPTION:
            Internal function that retrieves both the ONNX model and tokenizer
            from Teradata Vantage in separate tables.
            If 'mandatory' is True, any miss immediately raises an exception 
            and if False, it checks whether to fall back to legacy tables.
        
        PARAMETERS:
            mandatory
                Optional Argument.
                Specifies whether the retrieval of model and tokenizer is mandatory.
                Types: bool
        
        RETURNS:
            None
        
        RAISES:
            TeradataMlException
        """

        try:
            print(
                f"Retrieving model id '{self.model_id}' from {self.model_table_name}"
            )
            self.model_data = retrieve_byom(
                model_id=self.model_id,
                table_name=self.model_table_name,
                schema_name=self.model_schema_name,
                return_addition_columns=True
            )

            effective_tokenizer_id = self.tokenizer_id or self.model_id
            print(
                f"Retrieving tokenizer id '{effective_tokenizer_id}' from {self.tokenizer_table_name}"
            )
            self.tokenizer_data = retrieve_byom(
                model_id=effective_tokenizer_id,
                table_name=self.tokenizer_table_name,
                schema_name=self.tokenizer_schema_name,
                return_addition_columns=True
            )
        except TeradataMlException as e:
            if mandatory:
                raise
            # if optional path, bubble up for caller to decide fallback
            raise

    # ------------------------------------------------------------------ #
    def _retrieve_legacy_pair(self, table_name, schema_name):
        """
        DESCRIPTION:
            Internal function that retrieves both the ONNX model and tokenizer
            from Teradata Vantage from the same table(legacy code).
        
        PARAMETERS:
            table_name
                Optional Argument.
                Specifies the name of the table where model and tokenizer are saved.
                Types: str
            
            schema_name
                Optional Argument.
                Specifies the database name for the table.
                Types: str
        
        RETURNS:
            None
        
        RAISES:
            TeradataMlException
        """
        print(
            f"Retrieving model '{self.model_id}' from {table_name}"
        )
        try:
            legacy_row = retrieve_byom(
                model_id=self.model_id,
                table_name=table_name,
                schema_name=schema_name,
                return_addition_columns=True
            )
        except TeradataMlException as e:
            print("Failed to retrieve ONNX model from legacy table.")
            raise

        # Assign to model_data and tokenizer_data for downstream use.
        self.model_data = legacy_row.select(["model_id", "model"])
        self.tokenizer_data = (
            legacy_row.assign(
                model_id=legacy_row.model_id,
                model=legacy_row.tokenizer
            )
            .select(["model_id", "model"])
        )


    def remove(self):
        """
        DESCRIPTION:
            Function Deletes the saved ONNX model 
            from Teradata Vantage in the specified table.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            TeradataMlException
        
        EXAMPLES:
            # Import the required modules.
            >>> from teradatagenai import TeradataAI
            >>> llm = TeradataAI(api_type = "onnx",
                             model_name = "bge-small-en-v1.5",
                             model_id = "td-bge-small",
                             model_table_name = "onnx_models",
                             )
            # Remove the instance of ONNX model and cleanup the model from Vantage
            >>> llm.remove()
        """
        print(f"Removing model id {self.model_id} from {self.model_table_name}")
        delete_byom(model_id = self.model_id , table_name = self.model_table_name , schema_name = self.model_schema_name)

        print(f"Removing tokenizer id {self.tokenizer_id} from {self.tokenizer_table_name}")
        delete_byom(model_id = self.tokenizer_id , table_name = self.tokenizer_table_name , schema_name = self.tokenizer_schema_name)

    def get_llm(self):
        """
        DESCRIPTION:
            Get the id of the ONNX model 
            that was stored in Vantage.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None

        EXAMPLES:
            # Import the required modules.
            >>> from teradatagenai import TeradataAI
            >>> llm = TeradataAI(api_type = "onnx",
                             model_name = "bge-small-en-v1.5",
                             model_path = "/path/to/onnx/model",
                             model_table_name = "onnx_models",
                             tokenizer_path = "/path/to/onnx/tokenizer,
                             tokenizer_table_name = "onnx_tokenizer",
                             )
            # Get the LLM in use.
            >>> llm.get_llm()
        """
        return self.model_name
    
class TeradataAI:
    """
    Class sets up the environment and initializes the LLM endpoint depending
    on the API type.
    It also wraps the instance of '_TeradataAIFPF' and '_TeradataAIHuggingFace'
    into TeradataAI instance.
    """
    @argument_deprecation("20.00.00.05", ["table_name", "schema_name"])
    def __init__(self, api_type, model_name, **kwargs):
        """
        DESCRIPTION:
            Instantiates the TeradataAI class to set up the
            environment and initializes the LLM endpoint.
            Prerequites for BYO LLM:
                * Bring Your Own LLM is a capability of Teradata’s Open
                  Analytics Framework which works on Vantage Cloud Lake.
                  Look at the respective user guide for more details.
                * The combination of LLMs and GPU processing significantly
                  boosts performance, leading to a larger impact.
                  To support these capabilities, Teradata has added a new
                  Analytic GPU cluster to the VantageCloud
                  Lake environment. Though BYO LLM work with Analytic clusters,
                  it is advisable to use with Analytic GPU clusters.
                Notes:
                    * When using any api_type as 'hugging_face', make sure to,
                        * establish connection with database using 'create_context()'
                          function from teradataml.
                        * authenticate against the CCP using 'set_auth_token()'
                          function from teradataml.
                    * When using any "api_type" as 'onnx', ensure you have
                      established connection with database using 'create_context()'
                      from teradataml.
                    If user specified table exists (for either model or tokenizer), it must:
                        a. Containt at least 2 columns:
                            * 'model_id' of type VARCHAR (any length)
                            * 'model' of type BLOB and,
                        b. Optionally include additional columns for extra metadata.
                    If user-specified tables do not exist:
                        a. For the model table:
                            - The table is created with the name in "model_table_name"
                            and the id in "model_id".
                            - If "model_table_name" is not provided, defaults to
                            'td_genai_byom_models'.
                        b. For the tokenizer table:
                            - The table is created with the name in "tokenizer_table_name" and
                            the id in "tokenizer_id".
                            - If "tokenizer_table_name" is not provided, defaults to
                            'td_genai_byom_tokenizers'.
                            - If "tokenizer_id" is not provided, it defaults to the same value
                            as "model_id".
                        c. User may specify both schema and table names using corresponding
                            schema_name and table_name arguments.
                            If schema is not specified, the current schema is used.
                            See save_byom() in the teradataml User Guide for more details.
                        d. Created tables contain:
                            - 'model_id' column as VARCHAR(128)
                            - 'model' column as BLOB
                    * Following parameters can be passed as an OS environment variables or in config file:
                        * Azure:
                            AZURE_OPENAI_API_KEY for api_key
                            AZURE_OPENAI_ENDPOINT for api_base
                            AZURE_OPENAI_API_VERSION for api_version
                            AZURE_OPENAI_DEPLOYMENT_ID for deployment_id
                        * AWS:
                            AWS_ACCESS_KEY_ID for access_key
                            AWS_SECRET_ACCESS_KEY for secret_key
                            AWS_DEFAULT_REGION for region
                            AWS_SESSION_TOKEN for session_key
                        * GCP:
                            GOOGLE_APPLICATION_CREDENTIALS for access_token
                            GOOGLE_PROJECT for project
                            GOOGLE_REGION for region
                        * NIM:
                            NVIDIA_API_KEY for api_key
                        
        PARAMETERS:
            api_key:
                Required Argument, Optional if 'authorization' is provided.
                Specifies the API key to access the LLM.
                Note:
                    Applicable only if "api_type" is 'azure' or 'nim'.
                Types: str

            access_token:
                Required Argument, Optional if 'authorization' is provided.
                Specifies the access token for GCP.
                Note:
                    Applicable only if "api_type" is 'gcp'.
                Types: str

            access_key:
                Required Argument, Optional if 'authorization' is provided.
                Specifies the access key for AWS Bedrock.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: str

            api_type:
                Required Argument.
                Specifies the LLM API type.
                Permitted Values: 'azure', 'aws', 'gcp', 'nim', 'hugging_face', 'onnx'
                Types: str

            authorization:
                Optional argument, Required if:
                    * For Azure: "api_key", "api_base", and "api_version" are not provided.
                    * For AWS: "access_key", "secret_key" and "session_key" are not provided.
                    * For GCP: "access_token", "project" and "region" are not provided.
                    * For NIM: "api_key" is not provided.
                Specifies the authorization object name for the LLM API.
                Note:
                    Applicable only if "api_type" is 'azure', 'aws', 'nim' or 'gcp'.
                Types: str

            deployment_id:
                Required Argument.
                Specifies the deployment ID of the LLM.
                It takes engine id for Azure OpenAI.
                Note:
                    Applicable only if "api_type" is 'azure'.
                Types: str

            model_name:
                Required Argument.
                Specifies the LLM model name.
                Types: str

            api_base:
                Required Argument, Optional if "authorization" is provided.
                Specifies LLM endpoint URL.
                Note:
                    Applicable only if "api_type" is 'azure' or 'nim'.
                Types: str

            api_version:
                Required Argument, Optional if "authorization" is provided.
                Specifies the api version of LLM in use.
                Note:
                    Applicable only if "api_type" is 'azure'.
                Types: str

            region:
                Required argument, Optional if 'authorization' is provided.
                Specifies the AWS bedrock or Google Cloud region.
                Note:
                    Applicable only if "api_type" is either 'gcp' or 'aws'.
                Types: str

            model_args:
                Required if "api_type" is 'hugging_face', optional otherwise.
                Specifies the LLM arguments for generation.
                It can include the following keys:
                    - 'temperature': Adjusts prediction randomness by scaling logits before
                        softmax.
                    - 'top_k': Sets the limit for the highest probability vocabulary tokens
                        to keep for top-k-filtering.
                    - 'top_p': Sets the cumulative probability of the highest probability
                        vocabulary tokens to keep for nucleus sampling.
                    - 'transformer_class': Sets the class specific to the model which allows
                                            easy loading of models.
                                            Note:
                                                Only applicable if "api_type" is 'hugging_face'.
                    - 'task': Sets the task defining which pipeline will be returned.
                                Note:
                                    Only applicable if "api_type" is 'hugging_face'.
                Types: dict

            secret_key:
                Required Argument, Optional if "authorization" is provided.
                Specifies the secret key for AWS Bedrock.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: str

            session_key:
                Optional Argument.
                Specifies the session key for AWS Bedrock.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: str

            project:
                Required Argument, Optional if "authorization" is provided.
                Specifies the name of the GCP project.
                Note:
                    Applicable only if "api_type" is 'gcp'.
                Types: str

            enable_safety:
                Optional Argument.
                Specifies whether to enable safety settings for the gcp inference.
                Note:
                    Applicable only if "api_type" is 'gcp'.
                Default Value: True
                Types: bool

            ues_args:
                Optional Argument.
                Specifies the parameters for the user environment service.
                It can include the following arguments:
                    - 'env_name': Specifies the remote user env. It can be the
                                    name of env or the UserEnv object.
                                    Note:
                                        If not specified, the model is installed in
                                        the default env which is 'td_gen_ai_env'.
                Note:
                    Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            asynchronous:
                    Optional Argument.
                    Specifies whether the model installation should be
                    asynchronous or not.
                    Note:
                        Applicable only if "api_type" is 'hugging_face'.
                    Default Value: False
                    Types: bool

            config_file:
                Optional Argument.
                Specifies the path to the config file containing the 
                parameters for the LLM.
                Types: str

            model_id:
                Required only if "api_type" is 'onnx', optional otherwise.
                Specifies the unique model identifier for model.
                Note:
                    Applicable only if "api_type" is 'onnx'.
                Types: str
            
            tokenizer_id:
                Optional Argument.
                Specifies the unique model identifier for tokenizer.
                Note:
                    Applicable only if "api_type" is 'onnx'.
                    If not specified, defaults to value of "model_id".
                Types: str

            model_path:
                Optional Argument. Required if ONNX model is not saved in the database.
                Specifies the absolute path of the file which has the ONNX model.
                Note:
                    Applicable only if "api_type" is 'onnx'.
                Types: str
                        
            tokenizer_path:
                Optional Argument. Required if ONNX model is not saved in the database.
                Specifies the absolute path of the tokenizer JSON file.
                Note:
                    Applicable only if "api_type" is 'onnx'.
                Types: str

            model_table_name:
                Optional Argument.
                Specifies the name of the table where the ONNX model should be saved
                or is to be read from.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
                Types: str
            
            tokenizer_table_name:
                Optional Argument.
                Specifies the name of the table where the tokenizer is saved or is
                to be read from.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
            
            table_name:
                Optional Argument
                Specifies the name of the table where the model and tokenizer are saved.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
            
            schema_name:
                Optional Argument.
                Specifies the database name for the table where the model and tokenizer
                are saved.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
            
            model_schema_name:
                Optional Argument.
                Specifies the database name for the model table.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
                    * If specified, then "model_table_name" must also be provided.
                Types: str
            
            tokenizer_schema_name:
                Optional Argument.
                Specifies the database name for the tokenizer table.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
                    * If specified, then "tokenizer_table_name" must also be provided.
                Types: str
            
            additional_columns_model , additional_columns_tokenizer:
                Optional Argument.
                Specifies the additional information about the model or tokenizer to be saved in the
                table. Passed as key value pair, where key is the name of the column
                and value is data to be stored in that column for the model being saved.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
                    * Following are the allowed types for the values passed in dictionary:
                        * int
                        * float
                        * str
                        * bool
                        * datetime.datetime
                        * datetime.date
                        * datetime.time
                        * bytes
                    * "additional_columns" does not accept keys model_id and model.
                Types: dict
            
            additional_columns_types_model , additional_columns_types_tokenizer:
                Optional Argument.
                Specifies the column type of the additional columns. Additional column 
                datatype information is passed as key value pair with key being the 
                column name and value as teradatasqlalchemy.types.
                Notes:
                    * Applicable only if "api_type" is 'onnx'.
                    * If any of the column type for additional columns are not specified in
                        "additional_columns_types", it then derives the column type according
                        the below table:
                        +---------------------------+-----------------------------------------+
                        |     Python Type           |        teradatasqlalchemy Type          |
                        +---------------------------+-----------------------------------------+
                        | str                       | VARCHAR(1024)                           |
                        +---------------------------+-----------------------------------------+
                        | int                       | INTEGER                                 |
                        +---------------------------+-----------------------------------------+
                        | bool                      | BYTEINT                                 |
                        +---------------------------+-----------------------------------------+
                        | float                     | FLOAT                                   |
                        +---------------------------+-----------------------------------------+
                        | datetime                  | TIMESTAMP                               |
                        +---------------------------+-----------------------------------------+
                        | date                      | DATE                                    |
                        +---------------------------+-----------------------------------------+
                        | time                      | TIME                                    |
                        +---------------------------+-----------------------------------------+
                Types: dict       

        RETURNS:
           None

        RAISES:
           TeradataMlException, ValueError, TypeError

        EXAMPLES:

        # Import the required modules.
        >>> from teradatagenai import TeradataAI

        # Example 1: Create LLM endpoint for azure OpenAI.
        >>> obj = TeradataAI(api_type = "azure",
                             api_base = "<https://****.openai.azure.com/>",
                             api_version = "2000-11-35",
                             api_key = <provide your llm API key>,
                             deployment_id = <provide your azure OpenAI engine name>,
                             model_name = "gpt-3.5-turbo")

        # Example 2: Create LLM endpoint for AWS bedrock.
        >>> obj = TeradataAI(api_type = "aws",
                             access_key = "<AWS bedrock access key>",
                             secret_key = "<AWS bedrock secret key>",
                             session_key = "<AWS bedrock session key>",
                             region = "us-west-2",
                             model_name = "anthropic.claude-v2",
                             model_args = {"max_tokens_to_sample": 2048,
                                           "temperature": 0,
                                           "top_k": 250,
                                           "top_p": 1})

        # Example 3: Create LLM endpoint for GCP vertex AI.
        >>> obj = TeradataAI(api_type = "gcp",
                             project = "<GCP project name>",
                             model_name = "gemini-1.5-pro-001",
                             region = "us-central1",
                             enable_safety = True,
                             access_token = "<GCP ACCESS TOKEN>",
                             model_args = {"temperature": 1,
                                           "top_p": 0.95}
                             )

        # Example 4: Setup the environment to work with the
        #            'xlm-roberta-base-language-detection' hugging_face model.
        >>> model_name = 'papluca/xlm-roberta-base-language-detection'
        >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                          'task' : 'text-classification'}
        >>> llm = TeradataAI(api_type = "hugging_face",
                             model_name = model_name,
                             model_args = model_args)

        # Example 5: Setup the environment 'demo' to work with the
        #            'xlm-roberta-base-language-detection' hugging_face model.
        >>> model_name = 'papluca/xlm-roberta-base-language-detection'
        >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                          'task' : 'text-classification'}
        >>> ues_args = {'env_name': 'demo'}
        >>> llm = TeradataAI(api_type = "hugging_face",
                             model_name = model_name,
                             model_args = model_args,
                             ues_args = ues_args)

        # Example 6: Setup the environment variable to work with the
        #            aws bedrock model.
        >>> import os
        >>> os.environ["AWS_DEFAULT_REGION"] = "us-west-2"
        >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
        >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
        >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
        >>> llm = TeradataAI(api_type = "aws",
                             model_name = "amazon.titan-embed-text-v1")

        # Example 7: Pass the .env file path to work with the
        #            Azure OpenAI model.
        # Create a .env file with the following content:
        -------------- env file ----------------
        AZURE_OPENAI_API_KEY = <azure OpenAI API key>
        AZURE_OPENAI_ENDPOINT = <https://****.openai.azure.com/>
        AZURE_OPENAI_API_VERSION = 2000-11-35
        AZURE_OPENAI_DEPLOYMENT_ID = <azure OpenAI engine name>
        ----------------------------------------
        >>> llm = TeradataAI(api_type = "azure",
                             model_name = "gpt-3.5-turbo",
                             config_file = "<path to .env file>")

        # Example 8: Setup the environment variable and pass the .env file path to work with the
        #            GCP vertex AI model.
        # Create a .env file with the following content:
        -------------- env file ----------------
        GOOGLE_APPLICATION_CREDENTIALS = "<gcp access token>"
        ----------------------------------------
        >>> import os
        >>> os.environ["GOOGLE_CLOUD_PROJECT"] = "<gcp project name>"
        >>> os.environ["GOOGLE_CLOUD_REGION"] = "us-central1"
        >>> llm = TeradataAI(api_type = "gcp",
                             model_name = "gemini-1.5-pro-001",
                             config_file = "<path to .env file>")

        # Example 9: Pass the authorization object to work with the
        #             azure OpenAI model.
        >>> from teradatagenai import TeradataAI
        >>> llm = TeradataAI(api_type = "azure",
                             model_name = "gpt-3.5-turbo",
                             authorization = "<authorization object>")
        
        # Example 10: Setup the environment variable to work with the
        #            NVIDIA NIM model.
        >>> import os
        >>> os.environ["NVIDIA_API_KEY"] = "<NVIDIA NIM API key>"
        >>> llm = TeradataAI(api_type = "nim",
                             api_base = "<nim base url>",
                             model_name = "meta/llama-3.1-8b-instruct")

        # Example 11: Create LLM endpoint for api type 'onnx' for the
        #             ONNX model 'bge-small-en-v1.5' where the model and 
        #             tokenizer do not exist in the database and have to
        #             be stored in separate tables with their respective ids.
        >>> from teradatagenai import TeradataAI
        >>> llm = TeradataAI(api_type = "onnx",
                              model_name = "bge-small-en-v1.5",
                              model_id = "bge-small-model",
                              tokenizer_id = "bge-small-tokenizer",
                              model_path = "<Enter/path/to/onnx/model>",
                              tokenizer_path = "<Enter/path/to/onnx/tokenizer>",
                              model_table_name = "onnx_models",
                              tokenizer_table_name = "onnx_tokenizers")

        # Example 12: Create LLM endpoint for "api_type" = 'onnx' for
        #             the ONNX model "bge-small-en-v1.5" with "model_id"
        #             as 'td-bge-small' that does not yet exist in the 
        #             database. Since both model and tokenizer tables are not
        #             specified, the ONNX model is saved in the default model table
        #             'td_genai_byom_models' and tokenizer is stored in the default
        #             tokenizer table 'td_genai_byom_tokenizers'. The tokenizer
        #             will be saved with the same id as the model id.
        >>> from teradatagenai import TeradataAI
        >>> llm = TeradataAI(api_type = "onnx",
                             model_name = "bge-small-en-v1.5",
                             model_id = "td-bge-small",
                             model_path = "<Enter/path/to/onnx/model>",
                             tokenizer_path = "<Enter/path/to/onnx/tokenizer>"

        # Example 13: Create LLM endpoint for "api_type" as 'onnx'
        #             for the ONNX model "bge-m3" with "model_id"
        #             as 'td-bge-m3' already stored in the
        #             table 'onnx_models' and tokenizer_id as 'td-bge-m3-tok'
        #             already stored in the table 'onnx_tokenizers'.
        >>> from teradatagenai import TeradataAI
        >>> llm = TeradataAI(api_type = "onnx",
                             model_name = "bge-m3",
                             model_id = "td-bge-m3",
                             model_table_name = "onnx_models",
                             tokenizer_id = "td-bge-m3-tok",
                             tokenizer_table_name = "onnx_tokenizers")
        
        # Example 14: Create LLM endpoint for "api_type" as 'onnx'
        #             for the ONNX model "bge-m3" with "model_id"
        #             as 'td-bge-m3' and "tokenizer_id" as 'td-bge-m3-tok'
        #             already stored in the default tables.
        >>> from teradatagenai import TeradataAI
        >>> llm = TeradataAI(api_type = "onnx",
                             model_name = "bge-m3",
                             model_id = "td-bge-m3",
                             tokenizer_id = "td-bge-m3-tok")
        """
        arg_matrix = []
        model_args = kwargs.get('model_args', None)
        config_file = kwargs.get("config_file", None)

        # Define permitted values for api_type
        permitted_values_api = ["azure", "aws", "gcp", "nim", "hugging_face", "onnx"]
        arg_matrix.append(["api_type", api_type, False, str, False, permitted_values_api])
        arg_matrix.append(["model_name", model_name, False, (str), True])
        arg_matrix.append(["model_args", model_args, True, (dict)])
        arg_matrix.append(["config_file", config_file, True, (str)])
        # Validate missing required arguments.
        _Validators._validate_missing_required_arguments(arg_matrix)
        # Validate argument types.
        _Validators._validate_function_arguments(arg_matrix)

        self.api_type = api_type.lower()
        self.model_name = model_name
        
        kwargs = self.__load_args_to_env_args(**kwargs)

        mapping_dict = {'azure': _TeradataAIFPF,
                        'nim': _TeradataAIFPF,
                        'aws': _TeradataAIFPF,
                        'gcp': _TeradataAIFPF,
                        'hugging_face': _TeradataAIHuggingFace,
                        'onnx': _TeradataAIONNX}
        self._wrapped_instance = mapping_dict[self.api_type](api_type=self.api_type,
                                                             model_name=self.model_name,
                                                             **kwargs)
     
    def get_llm_params(self):
        """
        DESCRIPTION:
            Get the parameters used to create the LLM.

        PARAMETERS:
            None

        RETURNS:
            dict

        RAISES:
            NotImplementedError

        EXAMPLES:
            >>> llm.get_llm_params()
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'get_llm_params', self.api_type)
        return self._wrapped_instance.get_llm_params()
    
    def get_llm(self):
        """
        DESCRIPTION:
            Get the name of the large language model.

        PARAMETERS:
            None

        RETURNS:
            str

        RAISES:
            None
            
        EXAMPLES:
            # Import the required modules.
            >>> from teradatagenai import TeradataAI

            # Example 1: Setup the environment to work with the
            #            'xlm-roberta-base-language-detection' hugging_face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)
            # Get the LLM in use.
            >>> llm.get_llm()
        """
        return self._wrapped_instance.get_llm()
            
    def task(self, **kwargs):
        """
        DESCRIPTION:
            This function can do any task which the llm supports.
            The advantage of this method is that it is not bounded
            to any operation and can be tweaked
            according to the requirements.
            Refer to the example for more details on how it can be used.
            Note:
                * Supported only when "api_type" is set to 'hugging_face'.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column(s) of the teradataml DataFrame
                which needs to be used for inferencing.
                Types: str or list of str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column(s)
                specified in "column" to analyze the content from.
                Types: teradataml DataFrame

            returns:
                Required Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns ‘text’ and ‘sentiment’
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Default Value: {"Text": VARCHAR(10000), "Sentiment": VARCHAR(10000)}
                Types: dict

            script:
                Required Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
                Types: str

            persist:
                Optional Argument.
                Specifies whether to persist the output or not.
                When set to True, results are stored in permanent tables,
                otherwise in volatile tables.
                Default Value: False
                Types: bool

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    1) The "quotechar" cannot be the same as the Delimiter.
                    2) The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Note:
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on python library name(s)
                to be installed.
                Types: str OR list of str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError, NotImplementedError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> import os
            >>> import teradatagenai
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> from teradataml import DataFrame
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_articles = data.select(["employee_id", "employee_name", "articles"])
            >>> base_dir = os.path.dirname(teradatagenai.__file__)

            # Create LLM endpoint.
            >>> model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            >>> model_args = {'transformer_class': 'AutoModelForTokenClassification',
                              'task': 'token-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Example 1: Generate the embeddings for employee reviews from the 'articles' column
            #            of a teradataml DataFrame using hugging face model 'all-MiniLM-L6-v2'.

            >>> embeddings_script = os.path.join(base_dir,
                                                 'example-data',
                                                 'embeddings.py')
            # Construct returns argument based on the user script.
            >>> returns = OrderedDict([('text', VARCHAR(512))])

            >>> _ = [returns.update({"v{}".format(i+1): VARCHAR(1000)}) for i in range(384)]
            >>> llm.task(column = "articles",
                         data = df_articles,
                         script = embeddings_script,
                         returns = returns,
                         libs = 'sentence_transformers',
                         delimiter = '#')

            # Example 2: Get the similarity score for 'employee_data' and 'articles' columns
            #            using the same hugging face model: 'all-MiniLM-L6-v2'.
            >>> sentence_similarity_script = os.path.join(base_dir, 'example-data',
                                                          'sentence_similarity.py')
            >>> llm.task(column = ["employee_data", "articles"],
                         data = data,
                         script = sentence_similarity_script,
                         libs = 'sentence_transformers',
                         returns = {"column1": VARCHAR(10000),
                                    "column2": VARCHAR(10000),
                                    "similarity_score": VARCHAR(10000)},
                         delimiter = "#")
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'task', self.api_type)
        return self._wrapped_instance.task(**kwargs)
    
    def remove(self):
        """
        DESCRIPTION:
            Remove the installed hugging_face model.
            Note:
                * Supported only when "api_type" is set to 'hugging_face'.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            NotImplementedError

        EXAMPLES:
            # Import the required modules.
            >>> from teradatagenai import TeradataAI

            # Example 1: Removing the installed model
            #            'xlm-roberta-base-language-detection'.

            # Setup the env and install the model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Remove the model
            >>> llm.remove()
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'remove', self.api_type)
        return self._wrapped_instance.remove()

    def get_env(self):
        """
        DESCRIPTION:
            Get the user enviornment in use.
            Note:
                * Supported only when "api_type" is set to 'hugging_face'.

        PARAMETERS:
            None

        RETURNS:
            UserEnv object.

        RAISES:
            NotImplementedError

        EXAMPLES:
            # Example 1: Get the user enviornment in use while installing the
            #           'xlm-roberta-base-language-detection' hugging face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)
            >> llm.get_env()
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'get_env', self.api_type)
        return self._wrapped_instance.get_env()

    def get_model_args(self):
        """
        DESCRIPTION:
            Get the model args which are being used.
            Specifically the 'transformer_class' and the 'pipeline'.
            Note:
                * Supported only when "api_type" is set to 'hugging_face'.

        PARAMETERS:
            None

        RETURNS:
            None

        RAISES:
            NotImplementedError

        EXAMPLES:
            # Example 1: Get the model args which are used while installing the
            #           'xlm-roberta-base-language-detection' hugging face model.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)
            >>> llm.get_model_args()
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'get_model_args', self.api_type)
        return self._wrapped_instance.get_model_args()
    
    def cleanup_env(self):
        """
        DESCRIPTION:
            Remove the default scripts starting with 'td_sample_' from the active user environment.
            Note:
                * Supported only when "api_type" is set to 'hugging_face'.
        
        PARAMETERS:
            None
        
        RETURNS:
            None
        
        RAISES:
            TeradataMLException
        
        EXAMPLES:
            # Example 1: Cleanup the user environment
            >>> llm.cleanup_env()
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'cleanup_env', self.api_type)
        return self._wrapped_instance.cleanup_env()
    

    def __load_args_to_env_args(self, **kwargs):
        """
        DESCRIPTION:
            Internal function performs the following:
                1. Loads the arguments from the environment variables and config file.
                2. Sets the arguments in the kwargs dictionary.

        PARAMETERS:
            None

        RETURNS:
            dict containing updated kwargs dictionary with the loaded arguments.

        RAISES:
            TeradataMlException, ValueError, TypeError

        EXAMPLES:
            self.__load_args_to_env_args()
        """
        # Define the mapping of API credentials to the arguments.
        api_cred_mapping = {}
        
        if self.api_type == "azure":
            api_cred_mapping["AZURE_OPENAI_API_KEY"] = "api_key"
            api_cred_mapping["AZURE_OPENAI_ENDPOINT"] = "api_base"
            api_cred_mapping["AZURE_OPENAI_API_VERSION"] = "api_version"
            api_cred_mapping["AZURE_OPENAI_DEPLOYMENT_ID"] = "deployment_id"
        elif self.api_type == "aws":
            api_cred_mapping["AWS_DEFAULT_REGION"] = "region"
            api_cred_mapping["AWS_ACCESS_KEY_ID"] = "access_key"
            api_cred_mapping["AWS_SECRET_ACCESS_KEY"] = "secret_key"
            api_cred_mapping["AWS_SESSION_TOKEN"] = "session_key"
        elif self.api_type == "gcp":
            api_cred_mapping["GOOGLE_CLOUD_PROJECT"] = "project"
            api_cred_mapping["GOOGLE_CLOUD_REGION"] = "region"
            api_cred_mapping["GOOGLE_APPLICATION_CREDENTIALS"] = "access_token"
        elif self.api_type == "nim":
            api_cred_mapping["NVIDIA_API_KEY"] = "api_key"


        # Load the arguments from the config file.
        # If config_file is not None, then load the arguments from the config file.
        config_file = kwargs.pop("config_file", None)
        config_file_args = {}
        if config_file is not None:
            _Validators._validate_file_exists(config_file)
            _Validators._validate_file_extension(config_file, "env")
            config_file_args = dotenv_values(config_file)

        
        # Loop over the API credentials to set them from kwargs, config_file, or environment variables.
        # If config_file, OS env and kwargs are present, then
        # kwargs will be given priority, then config_file and then OS env.
        for arg, td_arg in api_cred_mapping.items():
            # Set the argument from kwargs first, then from config_file if provided, and lastly from OS environment.
            if kwargs.get(td_arg) is not None:
                value = kwargs.get(td_arg)
            elif config_file_args.get(arg, None) is not None:
                value = config_file_args.get(arg)
            else:
                value = os.getenv(arg, None)
            
            # If a value is found (from kwargs, config_file, or environment), set it.
            if value:
                kwargs[td_arg] = value

        return kwargs

    def __getattr__(self, name):
        """
        DESCRIPTION:
            Delegate attribute access to the wrapped instance

        PARAMETERS:
            name:
            Required Argument.
            Specifies the parameter name to be retrieved.
            Types: str

        RETURNS:
            str

        RAISES:
            None
        """
        return getattr(self._wrapped_instance, name)