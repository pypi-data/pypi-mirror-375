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
#   * The script is used in apply query for language detection
#     using 'xlm-roberta-base-language-detection' hugging face model.
# ##################################################################
# -*- coding: utf-8 -*-
import sys
import warnings

from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          pipeline)

warnings.simplefilter('ignore')
input_str = sys.stdin.read()

MAPPING_DICT = {"ar": "arabic",
                "bg": "bulgarian",
                "de": "german",
                "el": "modern greek",
                "en": "english",
                "es": "spanish",
                "fr": "french",
                "hi": "hindi",
                "it": "italian",
                "ja": "japanese",
                "nl": "dutch",
                "pl": "polish",
                "pt": "portuguese",
                "ru": "russian",
                "sw": "swahili",
                "th": "thai",
                "tr": "turkish",
                "ur": "urdu",
                "vi": "vietnamese",
                "zh": "chinese"}

DELIMITER = '#'
if len(input_str) > 0:
    model_ckpt = "papluca/xlm-roberta-base-language-detection"
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
    model = AutoModelForSequenceClassification.from_pretrained(model_ckpt)
    pipe = pipeline("text-classification", model=model_ckpt, tokenizer=tokenizer, device=0)
    i = -1
    for line in input_str.splitlines():
        fields = line.strip().split(DELIMITER)
        text_to_process = fields[0]
        res = MAPPING_DICT[pipe(text_to_process, top_k=1, truncation=True)[0]['label']]
        # Print: processed column, then remaining columns, then result
        remaining_cols = fields[1:]
        output_fields = [text_to_process] + remaining_cols + [res]
        print(DELIMITER.join(map(str, output_fields)))