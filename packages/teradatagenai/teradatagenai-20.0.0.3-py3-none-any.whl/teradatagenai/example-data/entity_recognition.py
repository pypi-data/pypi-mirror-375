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
#   * The script is used in apply query for entity recognition
#     using 'roberta-large-ontonotes5' hugging face model.
# ##################################################################
# -*- coding: utf-8 -*-
import json
import sys
import warnings

from transformers import (AutoModelForTokenClassification, AutoTokenizer,
                          pipeline)

warnings.simplefilter('ignore')
input_str = sys.stdin.read()

DELIMITER = '#'
if len(input_str) > 0:
    torch_device = 'cuda'
    model_path = "tner/roberta-large-ontonotes5"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    translator = pipeline("token-classification", model=model, tokenizer=tokenizer,
                          device=torch_device, aggregation_strategy='max')

    for line in input_str.splitlines():
        fields = line.strip().split(DELIMITER)
        text_to_process = fields[0]
        results = translator(text_to_process)
        dict_val = {'ORG': [], 'PERSON': [], 'DATE': [], 'PRODUCT': [],
                    'GPE': [], 'EVENT': [], 'LOC': [], 'WORK_OF_ART': []}
        i = 0
        while i < len(results):
            if results[i]['entity_group'] in dict_val:
                dict_val[results[i]['entity_group']].append(results[i]['word'])
            i += 1
        combined_str = ""
        entity_values = []
        for key, val in dict_val.items():
            entity_values.append(",".join(val))
        combined_str = DELIMITER.join(entity_values)
        # Print: processed column, then remaining columns, then result
        remaining_cols = fields[1:]
        output_fields = [text_to_process] + remaining_cols + [combined_str]
        print(DELIMITER.join(map(str, output_fields)))
