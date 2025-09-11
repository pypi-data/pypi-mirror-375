# ##################################################################
#
# Copyright 2024-2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Snigdha Biswas (snigdha.biswas@teradata.com)
# Secondary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
#                  Prafulla V Tekawade (prafulla.tekawade@teradata.com)
#
# Notes:
#   * This code is only for internal use.
#   * The code is used for performing text analytics on the database side
#     using LLM from azure, aws, gcp.
# ##################################################################

import json
import os
import re
import sys
import warnings
from teradatagenai.text_analytics.TextAnalyticsAI import _TextAnalyticsAICommon
from teradataml import DataFrame
from teradataml import (
    AIRecognizePIIEntities, AIAnalyzeSentiment, AIRecognizeEntities,
    AIDetectLanguage, AITextTranslate, AIExtractKeyPhrases, AITextClassifier,
    AIAskLLM, AITextSummarize, AITextEmbeddings, AIMaskPII
)
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.utils.validators import _Validators
from teradataml.utils.dtypes import _ListOf, _str_list

class _TextAnalyticsAIFPF(_TextAnalyticsAICommon):
    """
    Class holds methods for performing text analytics using models
    provided by aws , azure or gcp.
    """
    def __init__(self, llm):
        """
        DESCRIPTION:
            Constructor for _TextAnalyticsAIFPF class.

        PARAMETERS:
           llm:
               Required Argument.
               Specifies the language model to be used.
               Types: TeradataAI instance
        """
        super().__init__(llm)
        self.__creds = self.llm.get_llm_params()
        self._output_data = None

    def _setup(self, ta_task, data, column, **kwargs):
        """
        DESCRIPTION:
            This internal method sets up Text Analytics AI methods. It validates
            the input arguments and calls the specified text analytics task with 
            the required arguments.
    
        PARAMETERS:
            ta_task:
                Required Argument.
                Specifies the text analytics task to be performed.
                Types: Class
    
            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to analyze the content from.
                Types: teradataml DataFrame
    
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to analyze.
                Types: str
    
            kwargs:
                Optional Arguments.
                Additional arguments to be passed to the text analytics task.
    
        RETURNS:
            teradataml DataFrame
    
        RAISES:
            TeradataMlException, TypeError, ValueError
    
        EXAMPLES:
            >>> self._setup(AIAnalyzeSentiment, data=df_reviews, column="reviews", accumulate="reviews")
        """
        self._validate_and_prepare(column, data, **kwargs)
        # Convert "is_debug" to a string for FPF processing
        kwargs["is_debug"] = str(kwargs.get("is_debug", False))
        # Call the text analytics task with the required arguments.
        self._output_data = ta_task(
            api_type = self.llm.api_type,
            data = data,
            text_column = column,
            **self.__creds,
            **kwargs
        )
        result = self._output_data.result
        return result  
    
    def _validate_and_prepare(self, column, data, **kwargs):
        """
        DESCRIPTION:
            This internal method validates the input arguments and prepares them for 
            the specified text analytics task.
    
        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to analyze.
                Types: str
    
            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to analyze the content from.
                Types: teradataml DataFrame
    
            kwargs:
                Optional Arguments.
                Additional arguments to be validated and prepared.
    
        RETURNS:
            None
    
        RAISES:
            TeradataMlException, TypeError, ValueError
    
        EXAMPLES:
            >>> self._validate_and_prepare(column="reviews", data=df_reviews)
        """
        validate_matrix = kwargs.get("validate_matrix", [])
        validate_matrix.append(["is_debug", kwargs.get("is_debug", False), False, (bool)])
        validate_matrix.append(["accumulate", kwargs.get("accumulate", None), True, (str)])
        self._validate_arguments(column=column, data=data, validate_matrix=validate_matrix)
        
    def _prepare_batch_args(self, kwargs: dict) -> dict:
        """
        DESCRIPTION:
            This internal method prepares the batch arguments for the specified text analytics task.
            
        PARAMETERS:
            kwargs:
                Required Argument.
                Specifies the keyword arguments to be converted to batch arguments.
                Types: dict
        
        RETURNS:
            dict: A dictionary containing the batch arguments.
        
        RAISES:
            None
        
        EXAMPLES:
            >>> batch_args = self._prepare_batch_args(kwargs)
        """
        # Mapping of kwargs keys to their BatchArgs camelCase counterparts
        direct_mappings = {
            "client_request_token": "clientRequestToken",
            "job_name": "jobName",
            "model_id": "modelId",
            "role_arn": "roleArn",
            "timeout_duration_in_hours": "timeoutDurationInHours",
            "tags": "tags"
        }

        batchargs = {}

        # Apply direct mappings
        for k, v in direct_mappings.items():
            if k in kwargs:
                batchargs[v] = kwargs.pop(k)

        # Handle nested input/output config
        input_uri = kwargs.pop("s3_uri_input", None)
        if input_uri:
            batchargs["inputDataConfig"] = {
                "s3InputDataConfig": {
                    "s3Uri": input_uri
                }
            }

        # Handle nested outputDataConfig
        output_uri = kwargs.pop("s3_uri_output", None)
        if output_uri:
            batchargs["outputDataConfig"] = {
                "s3OutputDataConfig": {
                    "s3Uri": output_uri
                }
            }
        # Handle VPC config
        vpc_keys = {
            "security_groups_ids": "securityGroupIds",
            "sub_net_ids": "subnetIds"
        }

        vpc_config = {
            new_key: kwargs.pop(old_key)
            for old_key, new_key in vpc_keys.items()
            if old_key in kwargs
        }

        if vpc_config:
            batchargs["vpcConfig"] = vpc_config
        
        return batchargs if batchargs else None

    @collect_queryband(queryband="TAAI_analyze_sentiment_fpf")
    def analyze_sentiment(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Analyze the sentiment of the text in the specified column of a DataFrame.
            Sentiment Analysis is a sub-field of Natural Language Processing (NLP) that
            tries to identify and extract opinions within a given text. The goal of
            sentiment analysis is to determine the attitude of a speaker or a writer with
            respect to some topic or the overall contextual polarity of a document.
            Based on the text analysis, the sentiment can be positive, negative, or
            neutral. If any error or exception occurs during the sentiment analysis, the
            result is set to None.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to analyze the sentiment.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to analyze the content from.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_reviews = data.select(["employee_id", "employee_name", "reviews"])
            # Example 1: Analyze sentiment of food reviews in the 'reviews' column of
            #            teradataml DataFrame using AWS Bedrock.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            >>> obj.analyze_sentiment(column="reviews", data=df_reviews, accumulate="reviews")
        """
        # Set up AIAnalyzeSentiment based on the API type.
        return self._setup(AIAnalyzeSentiment, data, column, **kwargs)
        
    @collect_queryband(queryband="TAAI_detect_language_fpf")
    def detect_language(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Detect the language of the text data in a specified DataFrame column. It
            processes each text entry in the specified column and assigns a language
            label to it. The languages supported align with those supported by the
            respective large language models (LLMs) in use. In case of any error or
            exception during the language detection process, the result is set to None.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text
                content to detect the language.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to detect the language.
                Types: teradataml DataFrame

            lang:
                Optional Argument.
                Specifies the languages for detection. If no specific language is
                provided, the method will attempt to automatically detect the
                language of the text to the best of its ability. It can also detect
                languages that are not specified in the parameter.
                Types: str

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_quotes = data.select(["employee_id", "employee_name", "quotes"])
            # Example 1: Detect the language of text in the 'quotes' column of teradataml DataFrame
            #            using AWS BedRock. A list of languages to consider during detection is passed
            #            in the 'lang' argument.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            # Detecting the language of the 'quotes' column in the 'df_quotes' teradataml DataFrame.
            >>> obj.detect_language(column="quotes", data=df_quotes, lang="Chinese_Simplified,French")
        """
        validate_matrix = []
        lang = kwargs.get("lang", None)
        validate_matrix.append(["lang", lang, True, (str,_str_list)])
        if isinstance(lang, list):
            kwargs["lang"] = ', '.join(lang)
        # Set up AIDetectLanguage based on the API type.
        return self._setup(AIDetectLanguage, data, column, validate_matrix=validate_matrix, **kwargs)

    @collect_queryband(queryband="TAAI_text_extract_key_phrases_fpf")
    def extract_key_phrases(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Extract key phrases from the text in the specified column of a DataFrame.
            These key phrases, often referred to as "keywords",are words or phrases
            that best describe the subject or themes underlying the text data. It
            analyzes the text and recognizes words or phrases that appear significantly
            often and carry substantial meaning. These could include names, locations,
            technical terms, or any other significant nouns or phrases.
            If any error or exception occurs during the key phrase extraction process,
            the result is set to None.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to extract key phrases.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to extract key phrases.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_articles = data.select(["employee_id", "employee_name", "articles"])
            # Example 1: Extract key phrases from articles in the 'articles' column
            #             of a teradataml DataFrame using AWS BedRock.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            >>> obj.extract_key_phrases(column="articles", data=df_articles)
        """
        # Set up AIExtractKeyPhrases based on the API type.
        return self._setup(AIExtractKeyPhrases, data, column, **kwargs)
        
    @collect_queryband(queryband="TAAI_mask_pii_fpf")
    def mask_pii(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Recognize and mask Personally Identifiable Information (PII) entities within
            a specified column of a DataFrame. PII encompasses any data that could
            potentially identify a specific individual. Direct identifiers are explicit
            pieces of information that can uniquely identify an individual. These include
            sensitive data such as names, email addresses and phone numbers. Indirect
            identifiers, on the other hand, are pieces of information that may not
            identify an individual on their own but can do so when combined with other
            data. Examples include dates or unique device identifiers. The method is
            capable of recognizing a diverse set of PII entities including 'Name',
            'address', 'contact numbers', 'date/time' and 'serial numbers'. The output
            has two columns 'PII_Entities' which contains the name, start position and
            the length of the identified entity and 'Masked_Phrase' where PII entities
            are masked with asterisk (*) sign and returned. In case of any error or
            exception during the PII entity recognition process, the result is set to
            None.
            Note:
                This method handles sensitive information and is compatible with GCP
                exclusively when the `enable_safety` parameter is set to False.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text
                content to mask pii entities.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to mask pii entities.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_employeeData = data.select(["employee_id", "employee_name", "employee_data"])
            # Example 1: Mask PII entities in the 'employee_data' column of
            #            teradataml DataFrame using AWS BedRock.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            >>> obj.mask_pii_(column="employee_data", data=df_employeeData)
        """
        # Set up AIMaskPII based on the API type.
        return self._setup(AIMaskPII, data, column, **kwargs)
    
    @collect_queryband(queryband="TAAI_recognize_pii_entities_fpf")
    def recognize_pii_entities(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Recognize Personally Identifiable Information (PII) entities within a
            specified column of a DataFrame. PII encompasses any data that could
            potentially identify a specific individual. Direct identifiers are explicit
            pieces of information that can uniquely identify an individual. These
            include sensitive data such as names, email addresses and phone numbers.
            Indirect identifiers, on the other hand, are pieces of information that may
            not identify an individual on their own but can do so when combined with
            other data. Examples include dates or unique device identifiers.
            The method is capable of recognizing a diverse set of PII entities
            including 'Name', 'address', 'contact numbers', 'date/time' and 'serial
            numbers'. The output has a column 'PII_Entities' which contains the name,
            start position and the length of the identified entity.
            In case of any error or exception during the PII entity recognition process,
            the result is set to None.
            Note:
                This method handles sensitive information and is compatible with GCP
                exclusively when the `enable_safety` parameter is set to False.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text
                content to recognize pii entities.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to recognize pii entities.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_employeeData = data.select(["employee_id", "employee_name", "employee_data"])
            # Example 1: Recognize PII entities in the 'employee_data' column of teradataml
            #            DataFrame using AWS BedRock.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            # Recognizing PII entities in the 'employee_data' column in the 'df_employeeData' teradataml DataFrame.
            >>> obj.recognize_pii_entities(column="employee_data", data=df_employeeData)
        """

        # Set up AIRecognizePIIEntities based on the API type
        return self._setup(AIRecognizePIIEntities, data, column, **kwargs)
                
    @collect_queryband(queryband="TAAI_summarize_fpf")
    def summarize(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Summarize the text in the specified column of a DataFrame. It generates an
            abstractive summary for the input using different levels. Abstractive
            summarization is a process in which the method not only extracts key
            information from the text but also paraphrases and presents it in a condensed
            form, much like a human summarizer would. The conciseness of the summary can
            be adjusted using different levels. Higher levels yield more concise
            summaries. For instance, if the 'level' parameter is set to 2, the method
            first generates a summary of the original text, and then it further
            summarizes that summary. This recursive process allows for a highly condensed
            representation of the original text, making it easier to grasp the main
            points without having to read through the entire text. The output contains
            the summarized text and count of the characters in the summarized text. In
            case of any error or exception during the summarization process, the result
            is set to None.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text
                content to summarize.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to summarize.
                Types: teradataml DataFrame

            levels:
                Optional Argument.
                Specifies the level of summarization. Higher levels yield more concise
                summaries.
                Default Value: 1
                Types: int

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
                        
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        Example:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_articles = data.select(["employee_id", "employee_name", "articles"])
            # Example 1: Summarize articles in the 'articles' column of teradataml DataFrame
            #            using AWS BedRock with a summarization level set to 2.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            >>> obj_aws = TextAnalyticsAI(llm=llm_aws)
            >>> obj_aws.summarize(column="articles", data=df_articles, level=2)
        """
        validate_matrix = []
        levels =kwargs.get("levels", 1)
        # Validate the input parameters.
        validate_matrix.append(["levels", levels, True, (int)])
        # Convert levels to a string for FPF processing
        kwargs["levels"] = str(levels)
        # Set up AITextSummarize based on the API type.
        return self._setup(AITextSummarize, data, column, validate_matrix=validate_matrix, **kwargs)

    @collect_queryband(queryband="TAAI_translate_fpf")
    def translate(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Translate the input language to target language from the specified column of
            a DataFrame. The method is capable of translating the text content to the
            targeted language. The output has one additional column 'Translation' which
            contains the translated text content. The languages supported align with
            those supported by the respective large language models (LLMs) in use. By
            default the target language is set to 'English'. In case of any error or
            exception during the translation process, the result is set to None.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to translate.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to translate.
                Types: teradataml DataFrame

            target_lang:
                Optional Argument.
                Specifies the target language to translate the text content to.
                Default Value: "English".
                Types: str

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)

            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str
                
        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_quotes = data.select(["employee_id", "employee_name", "quotes"])
            Example 1: Translate the quotes from the 'quotes' column of teradataml DataFrame
            #          into Chineese using AWS BedRock.The target language for translation is set
            #          as German.
            # Import the modules.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            >>> obj.translate(column="quotes", data=df_quotes, target_lang="Chineese")
        """
        validate_matrix = []
        # Validate the input parameters.
        validate_matrix.append(["target_lang", kwargs.get("target_lang","english"),True, (str)])
        # Set up AITranslate based on the API type.
        return self._setup(AITextTranslate, data, column, validate_matrix=validate_matrix, **kwargs)
    
    @collect_queryband(queryband="TAAI_recognize_entities_fpf")
    def recognize_entities(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Identify and extract various types of entities from the text data in the
            specified column of a DataFrame. By identifying these entities, we can gain
            a more nuanced understanding of the text's context and semantic structure.
            It provides an efficient way to extract this valuable information, enabling
            users to quickly analyze and interpret large volumes of text. The method
            is capable of recognizing a diverse set of entities including 'people',
            'places', 'products', 'organizations', 'date/time', 'quantities',
            'percentages', 'currencies', and 'names'. In case of any error or exception
            during the entity recognition process, the result is set to None.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to recognize entities.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to arecognize entities.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_articles = data.select(["employee_id", "employee_name", "articles"])
            # Example 1: Recognize entities from articles in the 'articles' column
            #            of a teradataml DataFrame using AWS BedRock.
                       # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            # Recognizing entities in the 'artciles' column in the 'df_articles' teradataml DataFrame.
            >>> obj.recognize_entities(column="articles", data=df_articles)
        """
        # Set up AIRecognizeEntities based on the API type.
        return self._setup(AIRecognizeEntities, data, column, **kwargs)
    
    @collect_queryband(queryband="TAAI_classify_fpf")
    def classify(self, column, data, **kwargs):
        """
        DESCRIPTION:
            Text classification is a LLM powered approach that classifies unstructured
            text using a set of predetermined labels. Almost any kind of text can be
            classified with the classify() method. classify() method supports both
            multi-class and multi-label classification. In case of any error or
            exception during the classification process, the result is set to None.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text
                content to classify.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to classify the content.
                Types: teradataml DataFrame

            labels:
                Required Argument.
                Specifies the set of labels used to categorize the text.
                Types: str or list of strings (str)

            multi_label:
                Optional Argument.
                Specifies whether the classification is multi-label or not.
                When set to True, the multi-label classification is performed on the text.
                Otherwise, multi-class classification is performed.
                Default Value: False
                Types: bool

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_reviews = data.select(["employee_id", "employee_name", "reviews"])
            >>> df_classify_articles = data.select(["employee_id", "articles"])
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            # Example 1: Classify the text in the 'articles' column of a teradataml DataFrame
            #            using AWS BedRock.
            >>> obj.classify("articles", df_classify_articles,
                             labels=["Medical", "Hospitality", "Healthcare"])

            # Example 2: Perform multi-label classification for the text in the 'articles' column
            #            of a teradataml DataFrame using AWS BedRock.
            >>> obj.classify("articles",
                             df_classify_articles,
                             labels=["Medical", "Hospitality", "Healthcare"],
                             multi_label=True,
                             persist=True)
        """
        validate_matrix = []
        labels = kwargs.get("labels", None)
        multi_label = kwargs.get("multi_label", False)
        validate_matrix.append(["labels", labels, False, (str, _str_list)])
        validate_matrix.append(["multi_label", multi_label, False, (bool)])

        # Convert multi_label/labels to a string for FPF processing
        kwargs["multi_label"] = str(multi_label)
        if isinstance(labels, list):
            kwargs["labels"] = ', '.join(labels)
        # Set up AITextClassier based on the API type.
        return self._setup(AITextClassifier, data, column, validate_matrix=validate_matrix, **kwargs)
        
    @collect_queryband(queryband="TAAI_embeddings_fpf")
    def embeddings(self, column, data=None, persist=False, **kwargs):
        """
        DESCRIPTION:
            Retrieve embeddings for the text in a column in the dataset. This method returns a
            teradataml DataFrame with an 'embeddings' column containing text embeddings.
    
        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to generate embeddings.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column".
                Types: teradataml DataFrame
            
            output_format:
                Optional Argument.
                Specifies the format for the resultant embeddings,
                that is, the embeddings output column data type.
                Permitted Values: VECTOR, VARCHAR, or VARBYTE
                Default Value: VECTOR
                Types: str

            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specifies whether to enable error logging.
                Default Value: False
                Types: bool

            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                Types: str OR list of Strings (str)
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Types: str
            
            client_request_token:
                Optional Argument.
                Specifies a unique, case-sensitive identifier to ensure that the request completes
                no more than one time. If this token matches a previous request, Amazon Bedrock
                ignores the request but does not return an error.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: str

            s3_uri_input:
                Required Argument incase of batch mode.
                Specifies the details about the location of the input to the batch inference job.
                Notes:
                    * Applicable only if "api_type" is 'aws'.
                    * Batch mode is activated if the batch specific arguments are specified.
                Types: str

            job_name:
                Required Argument incase of batch mode.
                Specifies a name to be given to the batch inference job.
                Notes:
                    * Applicable only if "api_type" is 'aws'.
                    * Batch mode is activated if the batch specific arguments are specified.
                Types: str

            model_id:
                Required Argument incase of batch mode.
                The unique identifier of the foundation model to use for the batch inference job.
                Notes:
                    * Applicable only if "api_type" is 'aws'.
                    * Batch mode is activated if the batch specific arguments are specified.
                Types: str

            s3_uri_output:
                Required Argument incase of batch mode.
                Specifies the details about the location of the output of the batch inference job.
                Notes:
                    * Applicable only if "api_type" is 'aws'.
                    * Batch mode is activated if the batch specific arguments are specified.
                Types: str

            role_arn:
                Required Argument incase of batch mode.
                Specifies the Amazon Resource Name (ARN) of the service role with permissions to carry out
                and manage batch inference.
                Notes:
                    * Applicable only if "api_type" is 'aws'.
                    * Batch mode is activated if the batch specific arguments are specified.
                Types: str

            tags:
                Optional Argument.
                Specifies any tags to associate with the batch inference job.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: list of dict

            timeout_duration_in_hours:
                Optional Argument.
                Specifies the number of hours after which to force the batch inference job to time out.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: int
                
            security_group_ids:
                Optional Argument.
                Specifies an list of IDs for each security group in the VPC to use.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: List of strings

            subnet_ids:
                Optional Argument.
                Specifies an list of IDs for each subnet in the VPC to use.
                Note:
                    Applicable only if "api_type" is 'aws'.
                Types: List of strings
                
        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_reviews = data.select(["employee_id", "employee_name", "reviews"])
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)

            # Example 1: Generate the embeddings for employee reviews from the 'reviews' column
            #            of a teradataml DataFrame using AWS BedRock. 
            >>> obj.embeddings(column="reviews", data=df_reviews)
            
            # Example 2: Generate the embeddings for employee reviews from the 'reviews' column
            #            of a teradataml DataFrame using AWS BedRock in Batch mode.
            >>> obj.embeddings(column="reviews", data=df_reviews,
                            s3_uri_input="s3://***-amzn-s3-demo-bucket-input/***.jsonl",
                            s3_uri_output= "s3://***-amzn-s3-demo-bucket-output/",
                            job_name="***-batch-emb",
                            model_id="amazon.titan-embed-text-v1:0",
                            role_arn="arn:aws:iam::*****:role/td-bedrock-aws-batch")
        """
        output_format = kwargs.get("output_format", "VECTOR")
        kwargs["output_format"] = output_format
        client_request_token = kwargs.get("client_request_token", None)
        s3_uri_input = kwargs.get("s3_uri_input", None)
        job_name = kwargs.get("job_name", None)
        model_id = kwargs.get("model_id", None)
        s3_uri_output = kwargs.get("s3_uri_output", None)
        role_arn = kwargs.get("role_arn", None)
        tags = kwargs.get("tags", None)
        timeout_duration_in_hours = kwargs.get("timeout_duration_in_hours", None)
        security_group_ids = kwargs.get("security_group_ids", None)
        subnet_ids = kwargs.get("subnet_ids", None)
        permitted_values = ["VECTOR", "VARCHAR", "VARBYTE"]
        # Validate the input parameters
        validate_matrix = []
        validate_matrix.append(["output_format", output_format, True, (str), False, permitted_values])
        validate_matrix.append(["client_request_token", client_request_token, True, (str)])
        validate_matrix.append(["s3_uri_input", s3_uri_input, True, (str)])
        validate_matrix.append(["job_name", job_name, True, (str)])
        validate_matrix.append(["model_id", model_id, True, (str)])
        validate_matrix.append(["s3_uri_output", s3_uri_output, True, (str)])
        validate_matrix.append(["role_arn", role_arn, True, (str)])
        validate_matrix.append(["tags", tags, True, (_ListOf(dict))])
        validate_matrix.append(["timeout_duration_in_hours", timeout_duration_in_hours, True, (int)])
        validate_matrix.append(["security_group_ids", security_group_ids, True, (_str_list)])
        validate_matrix.append(["subnet_ids", subnet_ids, True, (_str_list)])
        
        batch_args = self._prepare_batch_args(kwargs)
        # If batch_args is not empty, convert it to a JSON string
        if batch_args:
            kwargs["batchargs"] = json.dumps(batch_args)

        # Set up AITextEmbeddings based on the API type
        return self._setup(AITextEmbeddings, data, column, validate_matrix=validate_matrix, **kwargs)
    
    @collect_queryband(queryband="TAAI_ask_fpf")
    def ask(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Method enables users to ask questions to a large language model (LLM) 
            using the provided data and context as relevant information. The LLM generates 
            answers based on the input question, leveraging the supplied data and context 
            to provide accurate and meaningful responses.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to be used for generating answers.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the questions to
                be answered by the LLM.
                Types: teradataml DataFrame

            context:
                Required Argument.
                Specifies the teradataml DataFrame containing the context to be used for 
                answering the questions.
                Types: teradataml DataFrame

            context_column:
                Required Argument.
                Specifies the column in the "context" DataFrame containing the text data 
                to be used as context for answering the questions.
                Types: str

            data_partition_column:
                Required Argument.
                Specifies the column used to partition the data for processing.
                Types: str

            context_partition_column:
                Required Argument.
                Specifies the column used to partition the context for processing.
                Types: str

            prompt:
                Required Argument.
                Specifies the prompt template to be used for generating answers. The prompt 
                should include placeholders for the data and question, which will be replaced 
                during execution.
                Types: str

            data_position:
                Required Argument.
                Specifies the placeholder in the prompt where the data will be inserted.
                Types: str

            question_position:
                Required Argument.
                Specifies the placeholder in the prompt where the question will be inserted.
                Types: str
            
            persist:
                Optional Argument.
                Specifies whether to persist the results of the
                function in a table or not. When set to True,
                results are persisted in a table; otherwise,
                results are garbage collected at the end of the
                session.
                Default Value: False
                Types: bool

            volatile:
                Optional Argument.
                Specifies whether to put the results of the
                function in a volatile table or not. When set to
                True, results are stored in a volatile table,
                otherwise not.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specifies whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to copy to the
                output. By default, the method copies no input teradataml
                DataFrame columns to the output.
                ypes: str OR list of Strings (str)

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError
        
        EXAMPLES:
            # Import the modules and create teradataml DataFrames.
            >>> from teradataml import DataFrame
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> load_data('question', 'question_data')
            >>> load_data('context', 'context_data')
            >>> data = DataFrame('question_data')
            >>> context = DataFrame('context_data')
            
            # Example 1: Answer questions from the 'text_data' column of a teradataml DataFrame
            #            using the 'context' DataFrame as context using AWS BedRock.
            # Create LLM endpoint using the environment variables.
            >>> import os
            >>> os.environ["AWS_DEFAULT_REGION"] = "<Enter AWS Region>"
            >>> os.environ["AWS_ACCESS_KEY_ID"] = "<Enter AWS Access Key ID>"
            >>> os.environ["AWS_SECRET_ACCESS_KEY"] = "<Enter AWS Secret Key>"
            >>> os.environ["AWS_SESSION_TOKEN"] = "<Enter AWS Session key>"
            >>> llm_aws = TeradataAI(api_type = "aws",
                                     model_name = "anthropic.claude-v2")
            >>> obj = TextAnalyticsAI(llm=llm_aws)
            >>> obj.ask(column="text_data", data=data,
                        context=context, context_column='text_data',
                        data_partition_column='id', context_partition_column='id',
                        prompt='Provide an answer to the question using data as information relevant to the question. \nQuestion: #QUESTION# \n Data: #DATA#',
                        data_position='#DATA#',
                        question_position='#QUESTION#')
        """
        validate_matrix = []
        
        validate_matrix.append(["context_column", kwargs.get('context_column', None), False, (str), True])
        validate_matrix.append(["context", kwargs.get('context', None), False, (DataFrame)])
        validate_matrix.append(["data_partition_column", kwargs.get('data_partition_column', None), False, (str), True])
        validate_matrix.append(["context_partition_column", kwargs.get('context_partition_column', None), False, (str), True])
        validate_matrix.append(["prompt", kwargs.get('prompt', None), False, (str), True])
        validate_matrix.append(["data_position", kwargs.get('data_position', None), False, (str), True])
        validate_matrix.append(["question_position", kwargs.get('question_position', None), False, (str), True])
        
        return self._setup(AIAskLLM, data, column, validate_matrix=validate_matrix, **kwargs)