# ##################################################################
#
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Kesavaragavan B (kesavaragavan.b@teradata.com)
# Secondary Owner: Prafulla V Tekawade (prafulla.tekawade@teradata.com)
#                  Aanchal Kavedia (aanchal.kavedia@teradata.com)
#
# Notes: 
#   * This code is only for internal use. 
#   * The code may perform modify, create, or delete operations 
#     in database based on given query. Hence, limit the permissions 
#     granted to the credentials.
#  This code is used for performing Text Analytics using LLM endpoints
#  also models from hugging face.
# ##################################################################

import os
import pandas as pd
from teradataml import copy_to_sql, DataFrame
from teradatagenai.llm.llm import TeradataAI
from teradatagenai.common.exceptions import TeradataGenAIException
from teradataml.utils.dtypes import _Dtypes
from teradataml.utils.validators import _Validators
from teradatasqlalchemy import VARCHAR
from teradataml.common.utils import UtilFuncs

class _TextAnalyticsAICommon:
    """
    Class for holding common functions required for TextAnalytics.
    """
    def __init__(self, llm):
        """
        DESCRIPTION:
            Constructor for the _TextAnalyticsAICommon class.
            This class has common functions required for TextAnalytics 
            by the client side as well as BYO LLM.

        PARAMETERS:
            llm:
                Required Argument.
                Specifies the language model to be used.
                Types: TeradataAI instance

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            >>> _TextAnalyticsAICommon(llm=llm)

        """
        self.llm = llm
        self._table_name = None
        self.data = None
        self._base_dir = os.path.dirname(os.path.dirname(__file__))

    def _validate_arguments(self,
                            column,
                            data,
                            validate_matrix,
                            **kwargs):
        """
        DESCRIPTION:
            Internal method to validate the arguments passed to the text analytics
            functions.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame
                containing the text content.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column to analyze.
                Types: teradataml DataFrame

            validate_matrix:
                Optional Argument.
                Specifies the matrix to be validated.
                Types: list

            kwargs:
                Optional Argument.
                Specifies the additional arguments passed to the function.
                Types: dict

        RETURNS:
            None

        RAISES:
            TeradataMlException, TypeError

        EXAMPLES:
            self._validate_arguments(column="text", data=data, validate_matrix=[])
        """
        # Validate missing required arguments.
        _Validators._validate_missing_required_arguments(validate_matrix)

        # Validate argument types
        _Validators._validate_function_arguments(validate_matrix)

        columns = UtilFuncs._as_list(column)
        for col in columns:
            if _Validators._check_isinstance(col, str):
                _Validators._validate_column_exists_in_dataframe([col], data._metaexpr)

    def _restore_table(self, result, persist=False):
        """
        DESCRIPTION:
            Internal function to restore a table in Vantage. It replaces any existing table
            with the same name. It generates unique table name with prefix 'TA_'. Then it
            uses the 'copy_to_sql' function to copy the data to the table in Vantage.
            If a table with the same name already exists, it is replaced.

        PARAMETERS:
            result:
                Required Argument.
                Specifies the data to be restored as a table in Vantage.
                Types: Pandas Dataframe, Teradataml DataFrame

            persist:
                Required Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent tables, otherwise in volatile tables.
                Default Value: False
                Types: bool

        RETURNS:
            None

        RAISES:
            None

        EXAMPLES:
            self._restore_table(output_df, persist=False)
        """
        # Generate a table name with a prefix of "ta_".
        # If persist is True, the table will not be garbage collected at the end of the session.
        self._table_name = UtilFuncs._generate_temp_table_name(prefix="ta_",
                                                               gc_on_quit=not persist)
        # Set index=True if result is pandas dataframe, else False.
        index = False
        if isinstance(result, pd.DataFrame):
            index = True

        # If a table with the same name already exists, it will be replaced.
        # If persist is True, the table will be permanent.
        copy_to_sql(df=result, table_name=self._table_name, if_exists='replace',
                    temporary=not persist, index=index)
        
    def _prepare_validate_matrix(self, **kwargs):
        """
        DESCRIPTION:
           Internal method to prepare the validation matrix.

        PARAMETERS:
           column:
               Required Argument.
               Specifies the column of the teradataml DataFrame
               containing the text content.
               Types: str

           data:
               Required Argument.
               Specifies the teradataml DataFrame containing the column to analyze.
               Types: teradataml DataFrame

        RETURNS:
           list

        RAISES:
           TeradataMlException, TypeError

        EXAMPLES:
           self._validate_arguments(column="text", data=data)
        """
        # Prepare a validation matrix.
        validate_matrix = []
        col_type = [str]
        # Append list type is columns accept list.
        if kwargs.get("allows_list_in_columns", False):
            col_type.append(list)
        validate_matrix.append(["column", kwargs.get('column', None), False, tuple(col_type), True])
        validate_matrix.append(["data", kwargs.get('data', None), False, (DataFrame)])
        validate_matrix.append(["persist", kwargs.get('persist', False), False, (bool)])
        return validate_matrix

class TextAnalyticsAI:
    """
    Class for performing text analytics using the given LLM inference endpoint.
    """
    def __init__(self, llm):
        """
        DESCRIPTION:
            Create an instance of TextAnalyticsAI to perform various text
            analytics tasks using the given LLM inference endpoint
            with the following methods:
                * analyze_sentiment
                * classify
                * detect_language
                * extract_key_phrases
                * mask_pii
                * recognize_entities
                * recognize_linked_entities
                * recognize_pii_entities
                * summarize
                * translate
                * embeddings

        PARAMETERS:
            llm:
                Required Argument.
                Specifies the language model to be used.
                Types: TeradataAI

        RETURNS:
            None

        RAISES:
            TypeError

        EXAMPLES:
            # Import the modules.
            >>> from teradatagenai import TeradataAI
            # Example 1: Create LLM endpoint and TextAnalyticsAI object
            #            using api_type = 'azure'.
            >>> llm_azure = TeradataAI(api_type = "azure",
                                       api_base = ""********"",
                                       api_version = "2000-11-35",
                                       api_key = "********",
                                       engine = "********",
                                       model_name = "gpt-3.5-turbo")
            >>> TA_obj = TextAnalyticsAI(llm=llm_azure)

            # Example 2: Create LLM endpoint and TextAnalyticsAI object
            #            using api_type = 'hugging_face'.
            >>> model_name = 'bhadresh-savani/distilbert-base-uncased-emotion'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm)

            # Example 3: Create LLM endpoint and TextAnalyticsAI object
            #            using api_type = 'onnx'.
            >>> from teradatagenai import TeradataAI
            >>> llm_onnx = TeradataAI(api_type = "onnx",
                                      model_name = "bge-small-en-v1.5",
                                      model_id = "bge-small-model",
                                      tokenizer_id = "bge-small-tokenizer",
                                      model_path = "/path/to/onnx/model",
                                      tokenizer_path = "/path/to/tokenizer",
                                      model_table_name = "onnx_models",
                                      tokenizer_table_name = "onnx_tokenizers"
                                )
            
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_onnx)
        """

        # Validate the 'llm' argument.
        _Validators._validate_function_arguments([["llm", llm, False,
                                                   (TeradataAI)]])

        from teradatagenai.text_analytics.TextAnalyticsAIHuggingFace\
            import _TextAnalyticsAIHuggingFace
        from teradatagenai.text_analytics.TextAnalyticsAIFPF \
            import _TextAnalyticsAIFPF
        from teradatagenai.text_analytics.TextAnalyticsAIONNX \
            import _TextAnalyticsAIONNX

        mapping_dict = {'azure': _TextAnalyticsAIFPF,
                        'nim': _TextAnalyticsAIFPF,
                        'aws': _TextAnalyticsAIFPF,
                        'gcp': _TextAnalyticsAIFPF,
                        'hugging_face': _TextAnalyticsAIHuggingFace,
                        'onnx': _TextAnalyticsAIONNX}

        # Wrapping the instance of '_TextAnalyticsAIFPF' and
        # '_TextAnalyticsAIHuggingFace' into TextAnalyticsAI instance.
        self._wrapped_instance = mapping_dict[llm.api_type](llm)

    def __getattr__(self, name):
        """
        DESCRIPTION:
            Delegate attribute access to the wrapped instance.

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
    
    def analyze_sentiment(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Analyze the sentiment of the text in the specified column of a DataFrame.
            Sentiment Analysis is a sub-field of Natural Language Processing (NLP) that
            tries to identify and extract opinions within a given text. The goal of
            sentiment analysis is to determine the attitude of a speaker or a writer with
            respect to some topic.

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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict

            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

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
            # Example 1: Analyze sentiment of food reviews in the 'reviews' column of a
            #            teradataml DataFrame using hugging face model
            #            'distilbert-base-uncased-emotion'.
            #            Reviews are passed as a column name along with the teradataml
            #            DataFrame.
            >>> model_name = 'bhadresh-savani/distilbert-base-uncased-emotion'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm)
            >>> obj.analyze_sentiment(column='reviews', data=df_reviews, delimiter="#")

            # Example 2: Extending example 1 and use "output_labels" to format the output.
            >>> obj.analyze_sentiment(column ='reviews',
                                      data = df_reviews,
                                      output_labels = {'label': str, 'score': float},
                                      delimiter = "#")

            # Example 3: Extending example 1 to use user defined script for inferencing.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> sentiment_analyze_script = os.path.join(base_dir, 'example-data',
                                                        'analyze_sentiment.py')
            >>> obj.analyze_sentiment(column ='reviews',
                                      data = df_reviews,
                                      script = sentiment_analyze_script,
                                      delimiter = "#")
        
            # Example 4: Analyze sentiment of food reviews in the 'reviews' column of
            #            teradataml DataFrame using AWS Bedrock.
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'analyze_sentiment', self.llm.api_type)
        return self._wrapped_instance.analyze_sentiment(column, data, **kwargs)
        
    def detect_language(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Detect the language of the text data in a specified DataFrame column. It
            processes each text entry in the specified column and assigns a language
            label to it. The languages supported align with those supported by the
            respective large language models (LLMs) in use.
            
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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str

            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

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
            >>> df_quotes = data.select(["employee_id", "employee_name", "quotes"])

            # Example 1: Detect the language of text in the 'quotes' column of a
            #            teradataml DataFrame using hugging face model:
            #            'xlm-roberta-base-language-detection'.
            #            The text for language detection is passed as a column
            #            name along with the teradataml DataFrame.
            #            A specific language is passed in the
            #            'language' argument.

            # Create LLM endpoint.
            >>> model_name = 'papluca/xlm-roberta-base-language-detection'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> ues_args = {'env_name' : 'demo_env'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args,
                                 ues_args = ues_args)

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm = llm)

            # Detecting the language of the 'quotes' column in the
            # 'df_quotes' teradataml DataFrame.
            >>> obj.detect_language(column = "quotes",
                                    data = df_quotes,
                                    delimiter = "#")

            # Example 2: Extending Example 1 to use default script
            #            with 'output_labels' to format the output.
            >>> obj.detect_language(column = 'quotes',
                                    data = df_quotes,
                                    output_labels = {'label': str, 'score': float},
                                    delimiter = "#")

            # Example 3: Extending Example 2 to use user defined
            #            script for inference.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> language_detection_script = os.path.join(base_dir, 'example-data',
                                                         'detect_language.py')
            >>> obj.detect_language(column = 'quotes',
                                    data = df_quotes,
                                    script = language_detection_script,
                                    delimiter = "#")
        
            # Example 4: Detect the language of text in the 'quotes' column of teradataml DataFrame
            #            using AWS BedRock. A list of languages to consider during detection is passed
            #            in the 'lang' argument.
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'detect_language', self.llm.api_type)
        return self._wrapped_instance.detect_language(column, data, **kwargs)

    def extract_key_phrases(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Extract key phrases from the text in the specified column of a DataFrame.
            These key phrases, often referred to as "keywords",are words or phrases
            that best describe the subject or themes underlying the text data. It
            analyzes the text and recognizes words or phrases that appear significantly
            often and carry substantial meaning. These could include names, locations,
            technical terms, or any other significant nouns or phrases.

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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

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

            # Example 1: Extract key phrases from articles in the 'articles' column
            #            of a teradataml DataFrame using hugging face model
            #            ml6team/keyphrase-extraction-kbir-kpcrowd. Articles are passed
            #            as a column name along with the teradataml DataFrame.
            # Create LLM endpoint.
            >>> model_name = 'ml6team/keyphrase-extraction-kbir-kpcrowd'
            >>> model_args = {'transformer_class': 'AutoModelForTokenClassification',
                              'task' : 'token-classification'}

            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm = llm)
            >>> obj.extract_key_phrases(column = "articles",
                                        data = df_articles,
                                        delimiter = "#")

            # Example 2: Extending example 1 to use user defined script for inferencing.
            >>> obj = TextAnalyticsAI(llm=llm)
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> extract_key_phrases_script = os.path.join(base_dir, 'example-data',
                                                          'extract_key_phrases.py')
            >>> obj.extract_key_phrases(column = "articles",
                                        data = df_articles,
                                        script = extract_key_phrases_script,
                                        delimiter = "#")
                                        
            # Example 3: Extract key phrases from articles in the 'articles' column
            #            of a teradataml DataFrame using AWS BedRock.
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'extract_key_phrases', self.llm.api_type)
        return self._wrapped_instance.extract_key_phrases(column, data, **kwargs)
            
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
            are masked with asterisk (*) sign and returned.
            Note:
                This method handles sensitive information and is compatible with "api_type" 
                as 'GCP' exclusively when the `enable_safety` parameter is set to False.

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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict
                
            internal_mask:
                Optional Argument.
                Specifies whether to mask using an internal function
                or not.
                When set to True, masking is done internally by the function,
                else masking is done by the model itself.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * Not supported when user provides his own script.
                    * The model should output the entities in a list of dict.
                      The entities to be masked should be in the 'word' key
                      of the output dict.
                      Example:
                        text = 'Linda Taylor is a famous artist'
                        op = [{'entity': 'B-FULLNAME', 'word': 'Linda',},
                              {'entity': 'I-FULLNAME', 'word': 'Taylor'}]
                Types: bool

            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

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
            >>> df_employeeData = data.select(["employee_id", "employee_name", "employee_data"])

            # Example 1: Recognize PII entities in the 'employee_data' column of a
            #            teradataml DataFrame using hugging face model
            #            'lakshyakh93/deberta_finetuned_pii'. The text containing potential
            #            PII like names, addresses, credit card numbers, etc., is passed as a
            #            column name along with the teradataml DataFrame.
            #            Setting the 'internal_mask' as True indicates
            #            masking to be done by the inbuilt function.
            # Create LLM endpoint.
            >>> model_name = 'lakshyakh93/deberta_finetuned_pii'
            >>> model_args = {'transformer_class': 'AutoModelForTokenClassification',
                              'task' : 'token-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm = llm)
            >>> obj.mask_pii(column="employee_data",
                             data=df_employeeData,
                             delimiter="#",
                             internal_mask=True)

            # Example 2: Extending example 1 to use user defined script for masking.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> mask_pii_script = os.path.join(base_dir, 'example-data',
                                               'mask_pii.py')
            >>> obj.mask_pii(column = "employee_data",
                             data = df_employeeData,
                             script = mask_pii_script,
                             delimiter = "#")
    
            # Example 3: Mask PII entities in the 'employee_data' column of
            #            teradataml DataFrame using AWS BedRock.
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'mask_pii', self.llm.api_type)
        return self._wrapped_instance.mask_pii(column, data, **kwargs)
    
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
            other data.
            Note:
                This method handles sensitive information and is compatible with "api_type" 
                as 'GCP' exclusively when the `enable_safety` parameter is set to False.

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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

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
                # Example 1: Recognize PII entities in the 'employee_data' column of a teradataml
            #            DataFrame using hugging face model 'lakshyakh93/deberta_finetuned_pii'.
            #            The column containing potential PII like names, addresses,
            #            credit card numbers, etc., is passed as a
            #            column name along with the teradataml DataFrame.
            # Create LLM endpoint.
            >>> model_name = 'lakshyakh93/deberta_finetuned_pii'
            >>> model_args = {'transformer_class': 'AutoModelForTokenClassification',
                              'task': 'token-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm)
            # Recognizing PII entities in the 'employee_data' column in 'df_employeeData'.
            >>> obj.recognize_pii_entities(column="employee_data",
                                           data=df_employeeData,
                                           delimiter="#")

            # Example 2: Extending Example 1 to use user defined script for inferencing.
            >>> import teradatagenai
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> recognize_script = os.path.join(base_dir, 'example-data', 'recognize_pii.py')
            >>> obj.recognize_pii_entities(column = "employee_data",
                                           data = df_employeeData,
                                           script = recognize_script,
                                           delimiter = "#")
                                           
            # Example 3: Recognize PII entities in the 'employee_data' column of teradataml
            #            DataFrame using AWS BedRock.
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'recognize_pii_entities', self.llm.api_type)
        return self._wrapped_instance.recognize_pii_entities(column, data, **kwargs)
                    
    def summarize(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Summarize the text in the specified column of a DataFrame. It generates an
            abstractive summary for the input using different levels. Abstractive
            summarization is a process in which the function not only extracts key
            information from the text but also paraphrases and presents it in a condensed
            form, much like a human summarizer would.

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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
                        
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

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
            # Example 1: Summarize articles in the 'articles' column of a teradataml DataFrame
            #            using hugging face model: 'facebook/bart-large-cnn'.
            #            Articles are passed as a column name along with
            #            the teradataml DataFrame.

            # Getting the env object using get_env().
            >>> env = get_env('demo_env')

            # Create LLM endpoint.
            >>> model_name = 'facebook/bart-large-cnn'
            >>> model_args = {'transformer_class': 'AutoModelForSeq2SeqLM',
                              'task': 'summarization'}
            >>> ues_args = {'env_name' : env}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args,
                                 ues_args = ues_args)
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm)

            >>> obj.summarize(column = 'articles',
                              data = df_articles,
                              delimiter = "#",
                              quotechar="|")

            # Example 2: Extending Example 1 to use user_defined script for inferencing.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> summarization_script = os.path.join(base_dir, 'example-data', 'summarize_text.py')
            >>> obj.summarize(column='articles',
                              returns = {"text": VARCHAR(10000),
                                         "summarized_text": VARCHAR(10000)},
                              data = df_articles,
                              script = summarization_script,
                              delimiter = "#",
                              quotechar="|")
                              
            # Example 3: Summarize articles in the 'articles' column of teradataml DataFrame
            #            using AWS BedRock with a summarization level set to 2.
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'summarize', self.llm.api_type)
        return self._wrapped_instance.summarize(column, data, **kwargs)

    def translate(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Translate the input language to target language from the specified column of
            a DataFrame. The function is capable of translating the text content to the
            targeted language. The languages supported align with
            those supported by the respective large language models (LLMs) in use. By
            default the target language is set to 'English'.

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
                Notes:
                    * If the "api_type" is 'hugging_face' and user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str

            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool
                
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
            >>> df_reviews = data.select(["employee_id", "employee_name", "reviews"])
            
            # Example 1: Translate the reviews from the 'reviews' column of a
            #            teradataml DataFrame into French using hugging
            #            face model 'Helsinki-NLP/opus-mt-en-fr'.
            #            The text for translation is passed as a
            #            column name along with the teradataml DataFrame.
            #            The target language for translation is set as French.
            # Create LLM endpoint.
            >>> model_name = 'Helsinki-NLP/opus-mt-en-fr'
            >>> model_args = {'transformer_class': 'AutoModelForSeq2SeqLM',
                              'task': 'translation'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm = llm)
            >>> obj.translate(column = "reviews",
                              data = df_reviews,
                              target_lang = "French",
                              delimiter = "#",
                              libs="sentencepiece")

            # Example 2: Extending example 1 to pass "output_labels" and get the respective
            # columns as output.
            >>> obj.translate(column = "reviews",
                              data = df_reviews,
                              target_lang = "French",
                              output_labels = {'translation_text': str},
                              delimiter = "#",
                              libs="sentencepiece")
        
            # Example 3: Translate the quotes from the 'quotes' column of teradataml DataFrame
            #          into Chineese using AWS BedRock.The target language for translation is set
            #          as German.
            #          Note: Similar operation can be performed for GCP and Azure by initializing
            #                the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'translate', self.llm.api_type)
        return self._wrapped_instance.translate(column, data, **kwargs)
    
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
            'percentages', 'currencies', and 'names'.

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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict    
            
            entity_groups:
                Optional Argument.
                Specifies the list of strings representing different types of entities like:
                'ORG', 'PERSON', 'DATE', 'PRODUCT', 'GPE', 'EVENT'. This can be used so
                 that the entities are classifies into appropriate groups.
                 Notes:
                     * Applicable only if "api_type" is 'hugging_face'.
                     * Either "entity_groups" or "output_labels" can be used.
                       Both cannot be used together.
                     * "returns" argument is mandatory when "entity_groups" is present.
                       All the groups specified in "entity_groups" should be present
                       in "returns".
                     * If the user uses his own script in "script" argument,
                       "entity_groups" are passed as the third argument
                       to the Python script which is used in 'apply' query with:
                        * 'script name' as first,
                        * 'delimiter' as second
                        * 'entity_groups' as third.
                 Types: list of str
                        
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> import os
            >>> import teradatagenai
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> from teradataml import DataFrame
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')
            >>> df_articles = data.select(["employee_id", "employee_name", "articles"])

            # Example 1: Recognize entities from articles in the 'articles' column
            #            of a teradataml DataFrame using hugging face model
            #            'roberta-large-ontonotes5'. Articles are
            #            passed as a column name along with the teradataml DataFrame.

            # Getting the env object using get_env().
            >>> env = get_env('demo')

            # Create LLM endpoint.
            >>> model_name = 'tner/roberta-large-ontonotes5'
            >>> model_args = {'transformer_class': 'AutoModelForTokenClassification',
                              'task' : 'token-classification'}
            >>> ues_args = {'env_name' : env}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args,
                                 ues_args = ues_args)
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm = llm)

            >>> obj.recognize_entities(column = 'articles',
                                       data = df_articles,
                                       delimiter = "#")

            # Example 2: Extending example 2 to use user_defined script for inferencing.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> entity_recognition_script = os.path.join(base_dir, 'example-data', 'entity_recognition.py')
            >>> obj.recognize_entities(column = 'articles',
                                       returns = {"text": VARCHAR(64000),
                                                  "ORG": VARCHAR(64000),
                                                  "PERSON": VARCHAR(64000),
                                                  "DATE1": VARCHAR(64000),
                                                  "PRODUCT": VARCHAR(64000),
                                                  "GPE": VARCHAR(64000)},
                                       data = df_articles,
                                       script = entity_recognition_script
                                       delimiter = "#")

            # Example 3: Extending example 1 to use 'aggregation_strategy' as
            # 'simple' in pipeline as well as classify the entites into
            # entity_groups listed below.
            >>> pipeline_kwargs = {"aggregation_strategy":"simple"}
            >>> obj.recognize_entities(column='articles',
                                       data=df_articles,
                                       entity_groups=["ORG",
                                                      "PERSON",
                                                      "DATE1",
                                                      "PRODUCT",
                                                      "GPE",
                                                      "EVENT",
                                                      "LOC",
                                                      "WORK_OF_ART"],
                                       returns = {"text": VARCHAR(64000),
                                                  "ORG": VARCHAR(64000),
                                                  "PERSON": VARCHAR(64000),
                                                  "DATE1": VARCHAR(64000),
                                                  "PRODUCT": VARCHAR(64000),
                                                  "GPE": VARCHAR(64000),
                                                  "EVENT": VARCHAR(64000),
                                                  "LOC": VARCHAR(64000),
                                                  "WORK_OF_ART": VARCHAR(64000)},
                                       delimiter="#",
                                       pipeline_kwargs=pipeline_kwargs)
    
            # Example 4: Recognize entities from articles in the 'articles' column
            #            of a teradataml DataFrame using AWS BedRock.
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'recognize_entities', self.llm.api_type)
        return self._wrapped_instance.recognize_entities(column, data, **kwargs)
    
    def classify(self, column, data, **kwargs):
        """
        DESCRIPTION:
            Text classification is a LLM powererd pproac that classifies unstructured
            text using a set of predetermined labels. Almost any kind of text can be
            classified with the classify() function.

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
                It takes either a list of labels or a list of multiple labels for
                classification.
                Notes:
                    * If "api_type" is 'hugging_face' and user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str or list of strings (str)

            multi_label:
                Optional Argument.
                Specifies whether the classification is multi-label or not.
                When set to True, the multi-label classification is performed on the text.
                Otherwise, multi-class classification is performed.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specify whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes. 
                    Setting accumulate='0:2' will include the first three columns.
                Note:
                    * If api_type is 'hugging_face', a list of
                      column names can also be passed.
                Types: str or list of str
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict

            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool

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
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
            >>> obj.classify("articles", df_classify_articles,
                             labels=["Medical", "Hospitality", "Healthcare"])

            # Example 2: Perform multi-label classification for the text in the 'articles' column
            #            of a teradataml DataFrame using AWS BedRock.
            >>> obj.classify("articles",
                             df_classify_articles,
                             labels=["Medical", "Hospitality", "Healthcare"],
                             multi_label=True,
                             persist=True)
            
            # Example 3: Perform classification in the 'articles' column of a
            #            teradataml DataFrame using hugging face model
            #            'facebook/bart-large-mnli'.
            #            A list of labels are passed and the model classifies articles
            #            according to the labels.
            # Create LLM endpoint.
            >>> model_name = 'facebook/bart-large-mnli'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'zero-shot-classification'}
            >>> ues_args = {'env_name' : 'demo_env'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args,
                                 ues_args = ues_args)

            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm)
            >>> obj.classify("articles",
                             df_classify_articles,
                             labels = ["Medical", "Hospitality", "Healthcare",
                                       "historical-news", "Games",
                                       "Environment", "Technology",
                                       "Games"],
                             delimiter = "#")

            # Example 4: Extend Example 3 to use user defined script for inferencing.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> classify_script = os.path.join(base_dir, 'example-data', 'classify_text.py')

            >>> obj.classify("articles",
                             df_classify_articles,
                             labels = ["Medical", "Hospitality", "Healthcare",
                                       "historical-news", "Games",
                                       "Environment", "Technology",
                                       "Games"],
                             script = classify_script,
                             delimiter = "#")
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'classify', self.llm.api_type)
        return self._wrapped_instance.classify(column, data, **kwargs)
         
    def embeddings(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Retrieve embeddings for the text in a column in the dataset.
    
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
            
            accumulate:
                Required only if "api_type" is 'onnx', optional otherwise.
                Specifies the column(s) of input teradataml DataFrame to
                copy to the output.
                Note:
                    * If "api_type" is 'onnx', it specifies one or more column names to add to the 
                      output table in a comma-separated list.
                    * If "api_type" is 'azure', 'gcp', 'nim', or 'aws', it specifies the name or range of 
                      column(s) from the input `teradataml` DataFrame to include in the output. By default,
                      the method copies all input teradataml Dataframe colums to the output.
                      For example:
                        If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                        'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes', 
                        then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                        Alternatively, column ranges can be specified using zero-based indexes. 
                        Setting accumulate='0:2' will include the first three columns.
                    * If "api_type" is 'hugging_face', a list of column names can also be passed.
                Types: str or list of strings

            model_output_tensor:
                Required only if "api_type" is 'onnx', optional otherwise.
                Specifies which tensor model to use for output.
                Note:
                    * Applicable only if "api_type" is 'onnx'.
                Permitted Values: 'sentence_embedding', 'token_embeddings'
                Types: str
            
            encode_max_length:
                Optional Argument.
                Specifies the maximum length of the tokenizer output token
                encodings(only applies for models that do not have fixed dimension).
                Note:
                    * Applicable only if "api_type" is 'onnx'.
                Default Value: 512
                Types: int
            
            show_model_properties:
                Optional Argument.
                Specifies whether to display the input and output tensor
                properties of the model as a varchar column. When set to True, 
                scoring is not run and only the current model properties 
                are shown.
                Note:
                    * Applicable only if "api_type" is 'onnx'.
                Default Value: False
                Types: bool
            
            output_column_prefix:
                Optional Argument.
                Specifies the column prefix for each of the output columns
                when using float32 "output_format".
                Note:
                    * Applicable only if "api_type" is 'onnx'.
                Default Value: "emb_"
                Types: str
            
            output_format:
                Optional Argument.
                Specifies the format for the resultant embeddings,
                that is, the embeddings output column data type.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim', 'aws', or 'onnx'.
                Permitted Values: VECTOR, VARCHAR, VARBYTE, or FLOAT32.
                Default Value:
                    For 'azure', 'gcp', 'nim', or 'aws' : VECTOR
                    For 'onnx' : VARBYTE(3072)
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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
                
            is_debug:
                Optional Argument.
                Specifies whether to enable error logging.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            data_partition_column:
                Optional Argument.
                Specifies the column used to partition the data for processing.
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Types: str

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns 'text' and 'sentiment'
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

            delimiter:
                Optional Argument.
                Specifies a delimiter to use when reading columns from a row and
                writing result columns. Delimiter must be a valid Unicode code point.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the Delimiter.
                    * The value of delimiter cannot be an empty string,
                       newline and carriage return.
                Default value: comma (,)
                Types: str

            quotechar:
                Optional Argument.
                Specifies the character used to quote all input and
                output values for the script.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                    * More details can be found here:
                    https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    * Applicable only if "api_type" is 'hugging_face'.
                    * This can be used in both sample script and user defined script.
                    * Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict
            
            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: dict
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: bool
            
            embeddings_dim:
                Optional Argument.
                Specifies the dimension of the embeddings generated by the model.
                Exception is raised, if the model does not generate the expected number of embeddings.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Default Value: 384
                Types: int
                
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
                                     model_name = "amazon.titan-embed-text-v2:0")
            # Create a TextAnalyticsAI object.
            >>> obj = TextAnalyticsAI(llm=llm_aws)

            # Example 1: Generate the embeddings for employee reviews from the 'reviews' column
            #            of a teradataml DataFrame using AWS BedRock. 
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
            >>> obj.embeddings(column="reviews", data=df_reviews)
            
            # Example 2: Generate the embeddings for employee reviews from the 'reviews' column
            #            of a teradataml DataFrame using hugging face model 'all-MiniLM-L6-v2'.
            # Create LLM endpoint.
            >>> model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            >>> model_args = {'transformer_class': 'AutoModel',
                              'task' : 'token-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            >>> obj = TextAnalyticsAI(llm=llm)

            >>> obj.embeddings(column = "articles",
                               data = df_articles,
                               libs = 'sentence_transformers',
                               delimiter = '#')

            # Example 3: Extending example 2 to use user defined script as input.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> embeddings_script = os.path.join(base_dir,
                                                 'example-data',
                                                 'embeddings.py')
            # Construct returns argument based on the user script.
            >>> returns = OrderedDict([('text', VARCHAR(512))])

            >>> _ = [returns.update({"v{}".format(i+1): VARCHAR(1000)}) for i in range(384)]
            >>> obj.embeddings(column = "articles",
                               data = df_articles,
                               script = embeddings_script,
                               returns = returns,
                               libs = 'sentence_transformers',
                               delimiter = '#')

            # Example 4: Generate the embeddings for employee reviews from the 'reviews' column
            #            of a teradataml DataFrame using hugging face model 'distilbert-base-uncased'.
            # Create LLM endpoint.
            >>> model_name = 'distilbert/distilbert-base-uncased'
            >>> model_args = {'transformer_class': 'DistilBertModel'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            >>> obj = TextAnalyticsAI(llm=llm)

            # Construct returns argument based on the user script.
            >>> returns = OrderedDict([('text', VARCHAR(512))])

            >>> _ = [returns.update({"v{}".format(i+1): FLOAT()}) for i in range(768)]
            >>> obj.embeddings(column = "articles",
                               data = df_articles,
                               returns = returns,
                               libs = 'sentence_transformers',
                               delimiter = '#')
            
            # Example 6: Generate the embeddings for employee reviews 
            #            from the 'reviews' column of a teradataml 
            #            DataFrame using onnx model.
            # Create LLM endpoint.
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> llm_onnx = TeradataAI(api_type = "onnx",
                                      model_name = "bge-small-en-v1.5",
                                      model_id = "bge-small-model",
                                      tokenizer_id = "bge-small-tokenizer",
                                      model_path = "/path/to/onnx/model",
                                      tokenizer_path = "/path/to/tokenizer",
                                      model_table_name = "onnx_models",
                                      tokenizer_table_name = "onnx_tokenizers"
                                    )
            
            # Configure byom location
            >>> from teradataml import configure, DataFrame
            >>> configure.byom_install_location="mldb"

            >>> load_data("byom", "amazon_reviews_25")
            >>> amazon_reviews_25 = DataFrame.from_table("amazon_reviews_25")
            >>> obj = TextAnalyticsAI(llm=llm_onnx)
            >>> obj.embeddings(data=amazon_reviews_25,
                               column = "rev_text", 
                               accumulate= "rev_id",
                               model_output_tensor = "sentence_embedding")

            # Example 7: Create a TextAnalyticsAI object and generate embeddings 
            #            for 'rev_text' column in amazon_reviews_25 teradataml dataframe.
            #            Include 'rev_id' and 'rev_text' columns in the output dataframe,
            #            and generate output embeddings in float32 format with 
            #            384 dimensions.
            >>> obj = TextAnalyticsAI(llm=llm_onnx)
            
            # Configure byom location
            >>> from teradataml import configure,
            >>> configure.byom_install_location="mldb"
            >>> obj.embeddings(data=amazon_reviews_25,
                               column = "rev_text", 
                               accumulate= "rev_id",
                               model_output_tensor = "sentence_embedding",
                               output_format = "FLOAT32(384)")
        """
        TeradataGenAIException.validate_method(self._wrapped_instance , 'embeddings', self.llm.api_type)
        return self._wrapped_instance.embeddings(column, data, **kwargs)
    
    def ask(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Method enables users to ask questions to a large language model (LLM) 
            using the provided data and context as relevant information. The LLM generates 
            answers based on the input question, leveraging the supplied data and context 
            to provide accurate and meaningful responses.
            Note:
                * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.

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
                Note:
                    * Applicable only if "api_type" is 'azure', 'gcp', 'nim' or 'aws'.
                Default Value: False
                Types: bool
            
            is_debug:
                Optional Argument.
                Specifies whether to enable error logging.
                Default Value: False
                Types: bool
            
            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes',
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes.
                    Setting accumulate='0:2' will include the first three columns.
                Types: str

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
            #            Note: Similar operation can be performed for GCP, NIM and Azure by initializing
            #                  the TeradataAI class with the appropriate parameters.
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
        TeradataGenAIException.validate_method(self._wrapped_instance, 'ask', self.llm.api_type)
        return self._wrapped_instance.ask(column, data, **kwargs)
        
    def sentence_similarity(self, column1, column2, data=None, **kwargs):
        """
        DESCRIPTION:
            Function to check the similarity between two sentances.
            Based on the hugging face model used, it will give output
            on how much the sentences are similar to each other.
            Note:
                * Applicable only if "api_type" is 'hugging_face'.

        PARAMETERS:
            column1:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the first sentence.
                to compare.
                Types: str

            column2:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the second sentence.
                to compare.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column
                specified in "column1" and "column2" to analyze the sentence similarity.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent tables, otherwise in volatile tables.
                Default Value: False
                Types: bool

            accumulate:
                Optional Argument.
                Specifies the name or range of column(s) from the input `teradataml` DataFrame to 
                include in the output. By default, the method copies all input teradataml
                DataFrame columns to the output.
                For example:
                    If the input DataFrame contains the columns 'employee_id', 'employee_name', 'quotes', and 
                    'articles'(in the exact order), and the 'accumulate' argument is set to 'employee_id:quotes',
                    then the output DataFrame will include all columns from 'employee_id' to 'quotes', inclusive.
                    Alternatively, column ranges can be specified using zero-based indexes.
                    Setting accumulate='0:2' will include the first three columns.
                Types: str or list of str

            output_labels:
                Optional Argument.
                Specifies the output labels which are used in the
                "returns" argument for the apply query.
                This is used while using the default script and
                when the user wants to have specific columns
                from the output.
                For example:
                    If the model outputs text:
                    [{'label': 'anger', 'score': 0.9979689717292786}],
                    in order to extract 'label' and 'score' as
                    separate columns, "output_labels" can be
                    specified as follows:
                        output_labels={'label': str, 'score': float}
                Types: dict

            returns:
                Optional Argument.
                Specifies the "returns" argument for the apply query.
                This is used mainly when the user writes his own script for
                inferencing. It contains a dict which specifies the
                column name as key and datatype as the value.
                For example:
                    The script returns two columns ‘text’ and ‘sentiment’
                    of VARCHAR datatype, then the "returns" argument
                    looks like this:
                    {"text": VARCHAR(10000), "sentiment": VARCHAR(10000)}
                Note:
                    * By default, all the columns from the input
                      teradataml DataFrame are copied to the output.
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script
                'td_sample_embeddings_script.py'
                attached in the user guide.
                Notes:
                    * The sample script uses the following mechanism to load and
                      use the model:
                        1. It uses 'AutoTokenizer.from_pretrained()' function from the
                           transformers library that automatically detects the correct
                           tokenizer class based on the model's configuration.
                        2. The "transformer_class" provided in the "model_args"
                           argument of TeradataAI class is used to load the given
                           pre-trained model.
                           Example: 'AutoModelForSequenceClassification',
                                    'AutoModelForTokenClassification' etc.
                        3. It then generated tokenized sentences using tokenizer class which is loaded in step 1.
                        4. Using the model loaded in step 2, it generates the output.
                        5. It performs mean_pooling to correct averaging.
                        6. It also uses torch.nn.functional.normalize to normalize embeddings.
                    * The sample script is tested for generating embeddings and
                      sentence_similarity using 'all-MiniLM-L6-v2', 'distilbert-base-uncased',
                      'albert-base-v2' and 'xlnet-base-cased' hugging face model.

                    * If user defined script is to be used, then following are
                      the command line arguments which are already supplied.
                        * Oth argument: script_name
                        * 1st argument: string containing extra parameters in dict format.
                          Using json.loads() will convert this to dict format.
                            Following arguments are passed if supplied by the respective function:
                                * classify_labels = "labels" argument for classify_text().
                                * target_lang = "target_lang" argument for translate().
                                * entity_groups = "entity_groups" argument for recognize_entities().
                                * pipeline_kwargs = "pipeline_kwargs" for all functions.
                                * delimiter = "delimiter" for all functions.
                                * func_name = "func_name" for all functions.
                Types: str

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
                Notes:
                    * The "quotechar" cannot be the same as the "delimiter".
                Default value: double quote (")
                Types: str

            task:
                Optional Argument.
                Specifies the task defining which pipeline will be returned.
                Examples: text-classification, summarization.
                Notes:
                    "task" mentioned here overides the "task" in 'model_args'
                    parameter of TeradataAI class.
                More details can be found here:
                https://huggingface.co/docs/transformers/en/main_classes/pipelines.
                Types: str

            libs:
                Optional Argument.
                Specifies the add-on Python library name(s)
                to be installed.
                Note:
                    * Applicable only if "api_type" is 'hugging_face'.
                Types: str OR list of str

            pipeline_kwargs:
                Optional Argument.
                Specifies any extra parameters which needs to be supplied to
                the 'pipeline' function of transformers module.
                Notes:
                    This can be used in both sample script and user defined script.
                    Refer the notes in "script" argument section which gives more
                    insights on usage.
                Types: dict

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        Example:
            # Import the modules and create a teradataml DataFrame.
            >>> import os
            >>> import teradatagenai
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> from teradataml import DataFrame
            >>> load_data('employee', 'employee_data')
            >>> data = DataFrame('employee_data')

            # Example 1: Get the similarity score for 'employee_data' and 'articles' columns
            #            using hugging face model: 'sentence-transformers/all-MiniLM-L6-v2'.

            >>> model_name = 'sentence-transformers/all-MiniLM-L6-v2'
            >>> model_args = {'transformer_class': 'AutoModel',
                              'task': 'token-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            >>> obj = TextAnalyticsAI(llm=llm)

            >>> obj.sentence_similarity(column1 = "employee_data",
                                        column2 = "articles",
                                        data = data,
                                        libs = 'sentence_transformers',
                                        delimiter = "#")

            # Example 2: Extending example 1 to use user defined script for inferencing.
            >>> base_dir = os.path.dirname(teradatagenai.__file__)
            >>> sentence_similarity_script = os.path.join(base_dir, 'example-data', 'sentence_similarity.py')
            >>> returns = {"sentence1": VARCHAR(10000),
                           "sentence2": VARCHAR(10000),
                           "similarity_score": VARCHAR(10000)}
            >>> obj.sentence_similarity(column1 = "employee_data",
                                        column2 = "articles",
                                        data = data,
                                        script = sentence_similarity_script,
                                        returns = returns,
                                        libs = 'sentence_transformers',
                                        delimiter = "#")

            # Example 3: Get the similarity score for 'employee_data' and 'articles' columns
            #            using hugging face model: 'distilbert-base-uncased'.
            >>> model_name = 'distilbert/distilbert-base-uncased'
            >>> model_args = {'transformer_class': 'DistilBertModel'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            >>> obj = TextAnalyticsAI(llm=llm)

            >>> obj.sentence_similarity(column1 = "employee_data",
                                        column2 = "articles",
                                        data = data,
                                        libs = 'sentence_transformers',
                                        delimiter = "#")
        """
        TeradataGenAIException.validate_method(self._wrapped_instance, 'sentence_similarity', self.llm.api_type)
        return self._wrapped_instance.sentence_similarity(column1, column2, data, **kwargs)