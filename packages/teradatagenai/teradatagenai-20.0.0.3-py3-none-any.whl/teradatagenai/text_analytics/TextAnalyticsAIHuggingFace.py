# ##################################################################
#
# Copyright 2024-2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
# Secondary Owner: Sukumar Burra (sukumar.burra@teradata.com)
#
# Notes:
#   * This code is only for internal use.
#   * The code is used for performing text analytics using models from
#     hugging face.
# ##################################################################

import json, re
import os
from collections import OrderedDict

from teradatagenai.text_analytics.TextAnalyticsAI import _TextAnalyticsAICommon
from teradataml import Apply, DataFrame
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messages import MessageCodes, Messages
from teradataml.utils.dtypes import _Dtypes
from teradataml.utils.validators import _Validators
from teradataml.common.utils import UtilFuncs
from teradataml.telemetry_utils.queryband import collect_queryband
from teradatasqlalchemy import VARCHAR, INTEGER, FLOAT

class _TextAnalyticsAIHuggingFace(_TextAnalyticsAICommon):
    """
    Class for holding functions required to do various TextAnalytics task
    using hugging face models.

    Using BYO LLM we can get any hugging face model in Vantage,
    and using the below functions can use the model and based
    on the inference script provided, can do the inferencing.

    The examples section contain sample models which can be
    used for doing the specific task.
    For majority functions, the inbuilt script can do the inferencing.
    Please check the examples of each API to get more details on the same.
    """
    def __init__(self, llm):
        """
        DESCRIPTION:
            Constructor for _TextAnalyticsAIHuggingFace.

        PARAMETERS:
           llm:
               Required Argument.
               Specifies the language model to be used.
               Types: TeradataAI instance

        RAISES:
            None

        RETURNS:
            None

        EXAMPLES:
            # Example 1: Create LLM endpoint and _TextAnalyticsAIHuggingFace object
            #            using api_type = 'hugging_face'.
            >>> model_name = 'bhadresh-savani/distilbert-base-uncased-emotion'
            >>> model_args = {'transformer_class': 'AutoModelForSequenceClassification',
                              'task' : 'text-classification'}
            >>> llm = TeradataAI(api_type = "hugging_face",
                                 model_name = model_name,
                                 model_args = model_args)

            # Create a TextAnalyticsAI object.
            >>> obj = _TextAnalyticsAIHuggingFace(llm=llm)
        """
        super().__init__(llm)
        # Choose script version based on local_model flag
        if hasattr(llm, '_local_model') and llm._local_model:
            # Use older script version for legacy model installations
            self.__sample_script_path = os.path.join(self._base_dir, 'example-data',
                                                     'td_sample_inference_script_02.py')
            self.__sample_embeddings_script_path = os.path.join(self._base_dir, 'example-data',
                                                                'td_sample_embeddings_script_02.py')
        else:
            # Use newer script version for standard model installations
            self.__sample_script_path = os.path.join(self._base_dir, 'example-data',
                                                     'td_sample_inference_script_03.py')
            self.__sample_embeddings_script_path = os.path.join(self._base_dir, 'example-data',
                                                                'td_sample_embeddings_script_03.py')
        self._user_env = self.llm._env

        self._default_file_exists = False

    def _prepare_validate_matrix(self, **kwargs):
        """
        DESCRIPTION:
           Internal method to prepare the validation matrix specific to BYO LLM.

        PARAMETERS:
           kwargs:
               Optional Argument.
               Specifies the arguments need to form the
               validation matrix.

        RETURNS:
           list

        RAISES:
           None

        EXAMPLES:
           self._prepare_validate_matrix(returns={"text": VARCHAR(10000),
                                                  "sentiment": VARCHAR(10000)},
                                         script="C://abc//script.py")
        """
        validate_matrix = super()._prepare_validate_matrix(**kwargs)
        validate_matrix.append(["script", self._script,
                                True, (str)])
        validate_matrix.append(["task", kwargs.get('task', None), True, (str)])
        validate_matrix.append(["returns", self._returns,
                                True, (dict)])
        validate_matrix.append(["libs", self._libs, True, (str, list)])
        validate_matrix.append(["pipeline_kwargs", kwargs.get('pipeline_kwargs', {}), True, (dict)])
        validate_matrix.append(["accumulate", self._accumulate, True, (str, list), True])
        validate_matrix.append(["replace", self._replace, True, (bool)])
        validate_matrix.append(["embeddings_dim", self._embeddings_dim, True, (int)])
        return validate_matrix

    def __hugging_face_setup(self, **kwargs):
        """
        DESCRIPTION:
           Internal method to set the required variables.
           Install the files, libs required for the particular operation.

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

           kwargs:
               Optional Argument.
               Specifies the additional arguments.

        RETURNS:
           None

        RAISES:
           TeradataMlException, TypeError

        EXAMPLES:
           self.__hugging_face_setup(data=data, column="column")
        """
        
        # Select columns based on accumulate, but ensure self._column is first
        if self._accumulate is None:
            # If accumulate is None, add all columns to accumulate except self._column(s)
            all_cols = UtilFuncs._as_list(self.data.columns)
            columns_to_prepend = UtilFuncs._as_list(self._column)
            # Remove columns_to_prepend from all_cols to avoid duplication
            self._selected_column = [col for col in all_cols if col not in columns_to_prepend]
            self._selected_column = columns_to_prepend + self._selected_column
            self.data = self.data.select(self._selected_column)
        elif self._accumulate:
            # Handle if accumulate is a list of columns
            if isinstance(self._accumulate, list):
                self._selected_column = [col for col in self._accumulate]
            # Handle string-based accumulate (range or comma-separated)
            elif isinstance(self._accumulate, str):
                if ':' in self._accumulate:
                    # Range selection (e.g., 'col1:col3' or '0:2')
                    cols = self.data.columns
                    if self._accumulate.replace(':', '').isdigit():
                        # Index-based range
                        start, end = map(int, self._accumulate.split(':'))
                        self._selected_column = UtilFuncs._as_list(cols[start:end+1])
                    else:
                        # Name-based range
                        start_col, end_col = self._accumulate.split(':')
                        start_idx = cols.index(start_col)
                        end_idx = cols.index(end_col)
                        self._selected_column = UtilFuncs._as_list(cols[start_idx:end_idx+1])
                else:
                    # Comma-separated list
                    self._selected_column = [col.strip() for col in self._accumulate.split(',')]
            # Ensure self._column(s) are first
            columns_to_prepend = UtilFuncs._as_list(self._column)
            for col in columns_to_prepend:
                if col in self._selected_column:
                    self._selected_column.remove(col)
            self._selected_column = columns_to_prepend + self._selected_column
            self.data = self.data.select(self._selected_column)
        else:
            self.data = self.data.select(self._column)

        if self._libs:
            self._user_env.install_lib(libs=self._libs)

        if self._default_file and not self._default_file_exists:
            # Always install default scripts if not already marked as installed
            self._user_env.install_file(file_path=self.__sample_script_path, replace=True)
            self._user_env.install_file(file_path=self.__sample_embeddings_script_path, replace=True)
            self._default_file_exists = True
        else:
            # For user scripts, check if file exists and handle replace logic
            script_name = os.path.basename(self._script)
            file_list = [str(f).strip() for f in self._user_env.files["File"]]
            if script_name in file_list and not self._replace:
                # File exists and user does NOT want to replace, so do nothing
                pass
            else:
                # Install or replace as needed
                self._user_env.install_file(file_path=self._script, replace=self._replace)
    
    def __create_dict_from_variables(self, **kwargs):
        """
        DESCRIPTION:
            Creates a dictionary from keyword arguments, excluding any
            arguments with None values.

        PARAMETERS:
          **kwargs: Keyword arguments to be included in the dictionary.

        RETURNS:
            A dictionary containing only the keyword arguments
            that are not None.

        RAISES:
            None
        """
        extra_args = {}
        for key, value in kwargs.items():
            if isinstance(value, list):
                # Convert list values to a string separated by ',' to
                # be passed as Python command line argument.
                value = ','.join(value)
            if value:
                extra_args[key] = value

        return extra_args

    def __apply_command(self, **kwargs):
        """
        DESCRIPTION:
           Internal function to prepare and run the apply command.

        PARAMETERS:
           kwargs:
               Optional Argument.
               Specifies the arguments needed for the apply command.

        RETURNS:
           DataFrame

        RAISES:
           None

        EXAMPLES:
           self.__apply_command(returns={"text": VARCHAR(10000),
                                         "sentiment": VARCHAR(10000)},
                                script="C://abc//script.py")
        """
        model_name = self.llm.model_name
        self._script = os.path.basename(self._script)
        task = kwargs.get('task', self.llm.model_args.get('task'))
        delimiter = kwargs.get('delimiter', ",")
        quotechar = kwargs.get('quotechar', "\"")
        func_name = kwargs.get('func_name', None)
        pipeline_kwargs = kwargs.get('pipeline_kwargs', {})
        internal_mask = kwargs.get('internal_mask', False)
        op_cols = None

        # Form the output labels if they are present and add them to the returns
        # clause if we are using the sample script.
        if self._script in [os.path.basename(self.__sample_script_path),
                            os.path.basename(self.__sample_embeddings_script_path)]:
            if self._returns is not None:
                pass  # Use the user-provided returns as is
            else:
                self._returns = OrderedDict()
                # Add selected columns
                if self._selected_column:
                    for col in self._selected_column:
                        self._returns[col] = self.data[col].type
                else:
                    self._returns = OrderedDict({"text": VARCHAR(10000)})

                # Add output_col only if output_labels is not present
                if not self._output_labels and self._output_col and self._output_col not in self._returns:
                    self._returns[self._output_col] = VARCHAR(10000)

                # Add output_labels columns if present
                if self._output_labels:
                    op_cols = list(self._output_labels.keys())
                    for colname, coltype in self._output_labels.items():
                        self._returns[colname] = (
                            _Dtypes._python_type_to_teradata_type(coltype)
                            if coltype == str
                            else _Dtypes._python_type_to_teradata_type(coltype)()
                        )
                if kwargs['func_name'] == 'embeddings':
                    for i in range(self._embeddings_dim):
                        self._returns.update({"v{}".format(i+1): VARCHAR(1000)})

            apply_command = f"python {self._script} {model_name} " \
                            f"{self.llm.model_args['transformer_class']} " \
                            f"{task}"
        else:
            apply_command = f"python {self._script}"

        # Adding all the extra_args required for processing in the
        # dictonary so that the sample script can use them as per the need.

        # If delimiter is '#', need to escape it as it is
        # considered as a comment in command line args.
        extra_args = self.__create_dict_from_variables(
                        classify_labels=kwargs.get('labels', None),
                        target_lang=kwargs.get('target_lang', "English"),
                        entity_groups=kwargs.get('entity_groups', None),
                        output_labels=op_cols,
                        pipeline_kwargs=pipeline_kwargs,
                        delimiter=delimiter,
                        func_name=func_name,
                        internal_mask=internal_mask)
        # Convert the extra_args to string to pass to the Python command line.
        if len(extra_args) > 0:
            extra_args = json.dumps(extra_args)
            # Quotes need to be escaped.
            extra_args = extra_args.replace('"', '\\"')
            apply_command = f"{apply_command} \"{extra_args}\""

        apply_obj = Apply(data=self.data,
                          apply_command=apply_command,
                          returns=self._returns,
                          env_name=self._user_env,
                          delimiter=delimiter,
                          quotechar=quotechar
                          )
        return (apply_obj.execute_script())

    def _exec(self, **kwargs):
        """
        DESCRIPTION:
           Internal function to execute the commands common
           to all the Text Analytic functions

        PARAMETERS:
           kwargs:
               Optional Argument.
               Specifies the arguments needed for the execution.

        RETURNS:
           DataFrame

        RAISES:
           None

        EXAMPLES:
           self._exec(returns={"text": VARCHAR(10000),
                                "sentiment": VARCHAR(10000)},
                       script="C://abc//script.py")
        """
        persist = kwargs.get("persist", False)
        self._column = kwargs.get("column", None)
        self.data = kwargs.get("data", None)
        validate_matrix = kwargs.get("validate_matrix", [])
        self._output_col = kwargs.get("output_col", None)
        self._libs = kwargs.get('libs', None)
        self._output_labels = kwargs.get('output_labels', None)
        self._script = kwargs.get('script', None)
        self._returns = kwargs.get('returns', None)
        self._accumulate = kwargs.get('accumulate', None)
        self._replace = kwargs.get('replace', False)
        self._embeddings_dim = kwargs.get('embeddings_dim', 384)
        self._default_file = False
        if self._script is None:
            self._default_file = True
            # If script is not provided, use the default sample script
            self._script = self.__sample_script_path

        # Perform validation
        validate_matrix.extend(self._prepare_validate_matrix(**kwargs))
        self._validate_arguments(column=self._column, data=self.data, validate_matrix=validate_matrix)

        self.__hugging_face_setup(**kwargs)
        # Restore the table and return the DataFrame.
        self._restore_table(result=self.__apply_command(**kwargs), persist=persist)
        print("The results are stored in the table: {}".format(self._table_name))
        return DataFrame(self._table_name)
    
    @collect_queryband(queryband="TAAI_analyze_sentiment_oaf")
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
                Specifies the column of the teradataml DataFrame
                containing the text content to analyze the sentiment.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column
                specified in "column" to analyze the content from.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not.
                When set to True, results are stored in permanent tables,
                otherwise in volatile tables.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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

            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
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
        """
        kwargs['func_name'] = 'analyze_sentiment'
        return self._exec(column=column, data=data, language=None, output_col="Sentiment", **kwargs)

    @collect_queryband(queryband="TAAI_detect_language_oaf")
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
                in "column" to detect the language of the input data.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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
        
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
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
        """
        kwargs['func_name'] = 'language_detection'
        return self._exec(column=column, data=data, output_col="Detected_Language", **kwargs)

    @collect_queryband(queryband="TAAI_classify_oaf")
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
                Types: str or List of str

            persist:
                Optional Argument.
                Specifies whether to persist the output or not.
                When set to True, results are stored
                in permanent tables, otherwise in volatile tables.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
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
            >>> df_classify_articles = data.select(["employee_id", "articles"])

            # Example 1: Perform classification in the 'articles' column of a
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

            # Example 2: Extend Example 1 to use user defined script for inferencing.
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
        validate_matrix = []
        labels = kwargs.get('labels', None)
        validate_matrix.append(["labels", labels, True, (str, list)])
        kwargs['func_name'] = 'classify'
        return self._exec(column=column, data=data, output_col="Labels",
                          validate_matrix=validate_matrix, **kwargs)

    @collect_queryband(queryband="TAAI_extract_key_phrases_oaf")
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
                Specifies the column of the teradataml DataFrame
                containing the text content to extract key phrases.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified in
                "column" to extract key phrases from.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
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

        """
        kwargs['func_name'] = 'extract_key_phrases'
        return self._exec(column=column, data=data, output_col="Key_Phrases", **kwargs)

    @collect_queryband(queryband="TAAI_mask_pii_oaf")
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
            data. Examples include dates or unique device identifiers. The function is
            capable of recognizing a diverse set of PII entities including 'Name',
            'address', 'contact numbers', 'date/time' and 'serial numbers'. The output
            has two columns 'PII_Entities' which contains the name, start position and
            the length of the identified entity and 'Masked_Phrase' where PII entities
            are masked with astrick(*) sign and returned.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text
                content to recognize and mask pii entities.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to mask the PII.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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

            internal_mask:
                Optional Argument.
                Specifies whether to mask using an internal function
                or not.
                When set to True, masking is done internally by the function,
                else masking is done by the model itself.
                Notes:
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
        """
        kwargs['func_name'] = 'mask_pii'
        validate_matrix = []
        validate_matrix.append(["internal_mask", kwargs.get('internal_mask', False), True, bool])
        return self._exec(column=column, data=data, output_col="Masked_Phrase",
                          validate_matrix=validate_matrix, **kwargs)

    @collect_queryband(queryband="TAAI_recognize_entities_oaf")
    def recognize_entities(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Identify and extract various types of entities from the text data in the
            specified column of a DataFrame. By identifying these entities, we can gain
            a more nuanced understanding of the text's context and semantic structure.
            It provides an efficient way to extract this valuable information, enabling
            users to quickly analyze and interpret large volumes of text. The function
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
                in "column" to recognize the entities.
                Types: teradataml DataFrame

            entity_groups:
                Optional Argument.
                Specifies the list of strings representing different types of entities like:
                'ORG', 'PERSON', 'DATE', 'PRODUCT', 'GPE', 'EVENT'. This can be used so
                 that the entities are classifies into appropriate groups.
                 Notes:
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

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
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
        """
        kwargs['func_name'] = 'recognize_entities'
        entity_groups = kwargs.get('entity_groups')
        output_labels = kwargs.get('output_labels')
        returns = kwargs.get('returns')
        _Validators._validate_mutually_exclusive_arguments(entity_groups, "entity_groups", output_labels,
                                                           "output_labels", skip_all_none_check=True)
        if entity_groups and not returns:
            raise TeradataMlException(Messages.get_message(
                MessageCodes.DEPENDENT_ARGUMENT, "entity_groups",
                "returns"), MessageCodes.DEPENDENT_ARGUMENT)

        return self._exec(column=column, data=data, output_col="Labeled_Entities",
                          **kwargs)

    @collect_queryband(queryband="TAAI_recognize_pii_entities_oaf")
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

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text
                content to recognize pii entities.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to recognize the PII entities.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
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
            >>> data = DataFrame("employee_data")
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
        """
        kwargs['func_name'] = 'recognize_pii'
        return self._exec(column=column, data=data, output_col="PII_Entities",
                          **kwargs)

    @collect_queryband(queryband="TAAI_summarize_oaf")
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
                in "column" to generate a concise summary for the text.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a certain way.
                To create the scripts, refer to the sample script 
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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

            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Types: bool

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
        """
        kwargs['func_name'] = 'summarization'
        return self._exec(column=column, data=data, output_col="Summarized_Text",
                          **kwargs)

    @collect_queryband(queryband="TAAI_translate_oaf")
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
                in "column" to translate the given text.
                Types: teradataml DataFrame

            target_lang:
                Optional Argument.
                Specifies the target language to translate the text content to.
                Notes:
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
                Default Value: "English".
                Types: str

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
                Types: dict

            script:
                Optional Argument.
                Specifies the user defined script for inferencing.
                This is used when the user wants to use the model to
                process the input and output in a user defined way.
                Refer to the sample script attached in the user guide for more
                details on custom script compilation.
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
                        3. It then uses the 'pipeline' module for using the model.
                           Pipeline makes use of "task" argument which defines which
                           pipeline to be used for processing.
                           Example: 'token-classification', 'summarization' etc.
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

            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
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
            >>> df_reviews = data.select(["employee_id", "employee_name", "reviews"])

            # Example 1: Translate the quotes from the 'quotes' column of a
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
            >>> obj.translate(column = "quotes",
                              data = df_quotes,
                              target_lang = "French",
                              output_labels = {'translation_text': str},
                              delimiter = "#",
                              libs="sentencepiece")
        """
        validate_matrix = []
        target_lang = kwargs.get('target_lang', "English")
        validate_matrix.append(["target_lang", target_lang, True, (str)])
        kwargs['func_name'] = 'translation'
        return self._exec(column=column, data=data, output_col="Translation",
                          validate_matrix=validate_matrix, **kwargs)

    @collect_queryband(queryband="TAAI_embeddings_oaf")
    def embeddings(self, column, data=None, **kwargs):
        """
        DESCRIPTION:
            Generate embeddings for the given column of a DataFrame.

        PARAMETERS:
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text content
                to generate embeddings.
                Types: str

            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to generate the text embeddings.
                Types: teradataml DataFrame

            persist:
                Optional Argument.
                Specifies whether to persist the output or not. When set to True, results are stored
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Types: bool
            
            embeddings_dim:
                Optional Argument.
                Specifies the dimension of the embeddings generated by the model.
                Exception is raised, if the model does not generate the expected number of embeddings.
                Default Value: 384
                Types: int

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

            # Example 1: Generate the embeddings for employee reviews from the 'reviews' column
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

            # Example 2: Extending example 1 to use user defined script as input.
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

            # Example 3: Generate the embeddings for employee reviews from the 'reviews' column
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

        """
        # Update the default script and the api_type as the sample script
        # differs for 'sentence_similarity' and 'embeddings'.
        kwargs['script'] = kwargs.get('script', self.__sample_embeddings_script_path)
        kwargs['func_name'] = 'embeddings'

        return self._exec(column=column, data=data,**kwargs)

    @collect_queryband(queryband="TAAI_sentence_similarity_oaf")
    def sentence_similarity(self, column1, column2, data=None, **kwargs):
        """
        DESCRIPTION:
            Function to check the similarity between two sentances.
            Based on the hugging face model used, it will give output
            on how much the sentences are similar to each other.

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
                in permanent table, otherwise in volatile table.
                Default Value: False
                Types: bool

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
            
            replace:
                Optional Argument.
                Specifies whether to replace the script in the user environment
                or not. If set to True, the script is replaced with the new one.
                Default Value: False
                Types: bool

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
        # Validating columns here so as to give an appropraite error messages.
        validate_matrix = []
        validate_matrix.append(["column1", column1, False, (str), True])
        validate_matrix.append(["column2", column2, False, (str), True])
        # Validate missing required arguments.
        _Validators._validate_missing_required_arguments(validate_matrix)

        # Validate argument types
        _Validators._validate_function_arguments(validate_matrix)

        # Update the default script and the api_type as the sample script
        # differs for 'sentence_similarity' and 'embeddings'.
        kwargs['script'] = kwargs.get('script', self.__sample_embeddings_script_path)
        kwargs['func_name'] = 'sentence_similarity'
        return self._exec(column=[column1, column2], data=data, output_col="similarity_score",
                          allows_list_in_columns=True, **kwargs)
