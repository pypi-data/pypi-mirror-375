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
#   * The script is used in apply query for masking pii
#     using 'deberta_finetuned_pii' hugging face model.
# ##################################################################
import json
import re
import sys
import warnings

from transformers import (AutoModelForTokenClassification, AutoTokenizer,
                          pipeline)

warnings.simplefilter('ignore')
input_str = sys.stdin.read()

def mask_label(sentence, l_s, mask_token="***"):
    # Replace the words
    l_s = l_s.split(',')
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in l_s) + r')\b'
    updated_sentence = re.sub(pattern, '***', sentence)
    return updated_sentence

DELIMITER = '#'
if len(input_str) > 0:
    model_path = "lakshyakh93/deberta_finetuned_pii"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    pipe = pipeline("token-classification", model=model, tokenizer=tokenizer, device='cuda', aggregation_strategy='first')

    l_s = []
    for line in input_str.splitlines():
        fields = line.strip().split(DELIMITER)
        text_to_process = fields[0]
        l_s = []
        prediction = pipe(text_to_process)
        for p in prediction:
            l_s.append(p['word'])
        # Print: processed column, then remaining columns, then result
        remaining_cols = fields[1:]
        output_fields = [text_to_process] + remaining_cols + [mask_label(text_to_process, ','.join(l_s))]
        print(DELIMITER.join(map(str, output_fields)))
