# 
# ##################################################################
#
# Copyright 2024-2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Sushant Mhambrey (sushant.mhambrey@teradata.com)
# Secondary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
#                  Snigdha Biswas (snigdha.biswas@teradata.com)
#
# Notes:
#   * This code is only for internal use.
#   * The code is used for performing text analytics using ONNX 
#     models
# ##################################################################

import json
import os
import re
import sys
import warnings
from teradatagenai.text_analytics.TextAnalyticsAI import _TextAnalyticsAICommon
from teradataml import configure, retrieve_byom, DataFrame, ONNXEmbeddings
from teradataml.telemetry_utils.queryband import collect_queryband
from teradataml.utils.validators import _Validators
from teradataml.common.exceptions import TeradataMlException

class _TextAnalyticsAIONNX(_TextAnalyticsAICommon):
    """
    Class holds methods for performing embedding generation 
    using ONNX models. 
    """
    def __init__(self, llm):
        """
        DESCRIPTION:
            Constructor for _TextAnalyticsAIONNX class.

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
            # Example 1: Create LLM endpoint and _TextAnalyticsAIONNX
            #            object using "api_type" as 'onnx'.
            >>> from teradatagenai import TeradataAI
            >>> llm_onnx= TeradataAI(api_type = "onnx",
                                     model_name = "bge-small-en-v1.5",
                                     model_id = "td-bge-small",
                                     model_path = "/path/to/onnx/model",
                                     tokenizer_path = "/path/to/onnx/tokenizer,
                                     table_name = "onnx_models")
            >>> obj = _TextAnalyticsAIONNX(llm=llm_onnx)
        """
        super().__init__(llm)

        self.__model_data = self.llm.model_data
        self.__tokenizer_data = self.llm.tokenizer_data

    def _exec(self,**kwargs):
        """
        DESCRIPTION:
            This internal method sets up Text Analytics AI methods.
    
        PARAMETERS:
            data:
                Required Argument.
                Specifies the teradataml DataFrame containing the column specified
                in "column" to analyze the content from.
                Types: teradataml DataFrame
    
            column:
                Required Argument.
                Specifies the column of the teradataml DataFrame containing the text 
                content to analyze.
                Types: str
    
            kwargs:
                Optional Arguments.
                Additional arguments to be passed to the text analytics task.
    
        RETURNS:
            teradataml DataFrame
    
        RAISES:
            TeradataMlException, TypeError, ValueError
    
        EXAMPLES:
            >>> self._exec(data=df_reviews, column="reviews", **kwargs)
        """
        column = kwargs.get("column", None)
        data = kwargs.get("data", None)

        validate_matrix = self._prepare_validate_matrix(**kwargs)
        self._validate_arguments(column=column, data=data, validate_matrix=validate_matrix)
        # Validate if byom location is set
        _Validators()._validate_function_install_location_is_set(configure.byom_install_location, 
                                                                 "Bring Your Own Model", 
                                                                 "configure.byom_install_location")

        # Build the tokenizer DataFrame with the expected column names for ONNXEmbeddings.
        tokenizerdata = (
            self.__tokenizer_data
            .assign(tokenizer_id=self.__tokenizer_data.model_id,
                    tokenizer=self.__tokenizer_data.model)
        )

        # Assign txt column to input dataframe
        data = data.assign(txt = data[column])
        try:
            embeddings = ONNXEmbeddings(
                modeldata=self.__model_data.select(["model_id", "model"]),
                tokenizerdata=tokenizerdata.select(["tokenizer_id", "tokenizer"]),
                newdata=data,
                **kwargs
            )
            return embeddings.result
        
        except TeradataMlException as e:
            raise e

    @collect_queryband(queryband="TAAI_embeddings_onnx")
    def embeddings(self, column, data, **kwargs):
        """
        DESCRIPTION:
            Method Calculates embedding values in
            Vantage with a model that has been created outside
            Vantage and exported to Vantage using ONNX format.

        PARAMETERS:
            data:
                Required Argument.
                Specifies the input teradataml DataFrame that contains
                the data to be scored.
                Types: teradataml DataFrame

            column:
                Required Argument.
                Specifies the name of the input teradataml DataFrame column 
                on which the embedding generation should be applied.
                Types: str

            accumulate:
                Required Argument.
                Specifies the name(s) of input teradataml DataFrame column(s) to
                copy to the output.
                Types: str OR list of strings

            model_output_tensor:
                Required Argument.
                Specifies which tensor model to use for output.
                Permitted Values: 'sentence_embedding', 'token_embeddings'
                Types: str

            encode_max_length:
                Optional Argument.
                Specifies the maximum length of the tokenizer output token
                encodings(only applies for models that do not have fixed dimension).
                Default Value: 512
                Types: int

            show_model_properties:
                Optional Argument.
                Specifies whether to display the input and output tensor
                properties of the model as a varchar column. When set to True, 
                scoring is not run and only the current model properties 
                are shown.
                Default Value: False
                Types: bool

            output_column_prefix:
                Optional Argument.
                Specifies the column prefix for each of the output columns
                when using float32 "output_format".
                Default Value: "emb_"
                Types: str

            output_format:
                Optional Argument.
                Specifies the output format for the model embeddings output.
                Permitted Values: "VARBYTE", "BLOB", "FLOAT32", and "VARCHAR"
                Default Value: "VARBYTE(3072)"
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

        RETURNS:
            teradataml DataFrame

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            # Import the modules and create a teradataml DataFrame.
            >>> from teradatagenai import TeradataAI, TextAnalyticsAI, load_data
            >>> from teradataml import DataFrame
            >>> load_data("byom", "amazon_reviews_25")
            >>> amazon_reviews_25 = DataFrame.from_table("amazon_reviews_25")
            
            # Setup a TeradataAI onnx endpoint.
            >>> llm_onnx= TeradataAI(api_type = "onnx",
                                     model_name = "bge-small-en-v1.5",
                                     model_id = "td-bge-small",
                                     model_path = "/path/to/onnx/model",
                                     tokenizer_path = "/path/to/onnx/tokenizer,
                                     table_name = "onnx_models")

            # Example 1: Create a TextAnalyticsAI object and generate embeddings 
            #            for 'rev_text' column in amazon_reviews_25 teradataml dataframe.
            >>> obj = TextAnalyticsAI(llm=llm_onnx)
            >>> obj.embeddings(data=amazon_reviews_25,
                               column = "rev_text", 
                               accumulate= "rev_id",
                               model_output_tensor = "sentence_embedding")

            # Example 2: Create a TextAnalyticsAI object and generate embeddings 
            #            for 'rev_text' column in amazon_reviews_25 teradataml dataframe.
            #            Include 'rev_id' and 'rev_text' columns in the output dataframe
            #            and generate output embeddings in float32 format with 
            #            384 dimensions.
            >>> obj = TextAnalyticsAI(llm=llm_onnx)
            >>> obj.embeddings(data=amazon_reviews_25,
                               column = "rev_text", 
                               accumulate= "rev_id",
                               model_output_tensor = "sentence_embedding",
                               output_format = "FLOAT32(384)")
        """
        return self._exec(column=column, data=data, **kwargs)
