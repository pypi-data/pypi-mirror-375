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
#   * The script is used in apply query for recognizing pii
#     using 'deberta_finetuned_pii' hugging face model.
# ##################################################################
# -*- coding: utf-8 -*-
import sys
import warnings
import json

warnings.simplefilter('ignore')
input_str = sys.stdin.read()

DELIMITER = '#'
if len(input_str) > 0:
    # Load model directly
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

    model_path = "lakshyakh93/deberta_finetuned_pii"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    pipe = pipeline("token-classification", model=model, tokenizer=tokenizer,
                    device='cuda', aggregation_strategy='first')

    for line in input_str.splitlines():
        fields = line.strip().split(DELIMITER)
        text_to_process = fields[0]
        l_s = []
        prediction = pipe(text_to_process)
        for p in prediction:
            l_s.append(p['word'])
        # Print: processed column, then remaining columns, then result
        remaining_cols = fields[1:]
        output_fields = [text_to_process] + remaining_cols + [','.join(l_s)]
        print(DELIMITER.join(map(str, output_fields)))
