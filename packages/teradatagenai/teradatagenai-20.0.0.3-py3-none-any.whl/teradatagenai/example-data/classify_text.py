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
#   * The script is used in apply query for performing classification
#     using 'bart-large-mnli' hugging face model.
# ##################################################################
# -*- coding: utf-8 -*-
import json
import sys
import warnings

from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          pipeline)

warnings.simplefilter('ignore')
input_str = sys.stdin.readlines()
extra_kwargs = json.loads(sys.argv[1])
labels = extra_kwargs['classify_labels']
labels = labels.split(',')

DELIMITER = '#'
if len(input_str) > 0:
    torch_device = 'cuda'
    model_path = 'facebook/bart-large-mnli'
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    classifier = pipeline("zero-shot-classification",
                          model=model, tokenizer=tokenizer)
    
    for line in input_str:
        fields = line.strip().split(DELIMITER)
        text_to_process = fields[0]
        res = classifier(text_to_process, labels)
        max_index = res['scores'].index(max(res['scores']))
        # Print: processed column, then remaining columns, then result
        remaining_cols = fields[1:]
        output_fields = [text_to_process] + remaining_cols + [res['labels'][max_index]]
        print(DELIMITER.join(map(str, output_fields)))