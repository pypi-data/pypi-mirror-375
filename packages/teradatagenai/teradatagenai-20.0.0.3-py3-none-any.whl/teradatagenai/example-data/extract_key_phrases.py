# ##################################################################
#
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
# Secondary Owner: Sukumar Burra (sukumar.burra@teradata.com)
#
# Notes:
#   * This code is only for internal use.
#   * The script is used in apply query for extracting key phrases
#     using 'keyphrase-extraction-kbir-kpcrowd' hugging face model.
# ##################################################################
# -*- coding: utf-8 -*-
import sys
import warnings

from transformers import (AutoModelForTokenClassification, AutoTokenizer,
                          TokenClassificationPipeline)
from transformers.pipelines import AggregationStrategy

warnings.simplefilter('ignore')
input_str = sys.stdin.read()

DELIMITER = '#'
if len(input_str) > 0:
    import numpy as np

    # Define keyphrase extraction pipeline.
    class KeyphraseExtractionPipeline(TokenClassificationPipeline):
        def __init__(self, model, *args, **kwargs):
            super().__init__(
                model=AutoModelForTokenClassification.from_pretrained(model),
                tokenizer=AutoTokenizer.from_pretrained(model),
                *args,
                **kwargs
            )

        def postprocess(self, all_outputs):
            results = super().postprocess(
                all_outputs=all_outputs,
                aggregation_strategy=AggregationStrategy.SIMPLE,
            )
            return np.unique([result.get("word").strip() for result in results])

    # Load pipeline.
    model_name = "ml6team/keyphrase-extraction-kbir-kpcrowd"
    extractor = KeyphraseExtractionPipeline(model=model_name)
    for line in input_str.splitlines():
        fields = line.strip().split(DELIMITER)
        text_to_process = fields[0]
        keyphrases = extractor(text_to_process)
        # Print: processed column, then remaining columns, then result
        remaining_cols = fields[1:]
        output_fields = [text_to_process] + remaining_cols + [', '.join(keyphrases)]
        print(DELIMITER.join(map(str, output_fields)))