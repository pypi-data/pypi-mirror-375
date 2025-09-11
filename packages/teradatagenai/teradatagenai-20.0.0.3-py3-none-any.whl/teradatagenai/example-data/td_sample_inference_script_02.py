# -*- coding: utf-8 -*-
# ##################################################################
#
# Copyright 2024 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
# Secondary Owner: Sukumar Burra (sukumar.burra@teradata.com)
#                  Snigdha Biswas (snigdha.biswas@teradata.com)
#
# Notes:
#   * This code is only for internal use.
#   * The script is used as a standard script for
#     inference. It takes the 'model_name', 'transformer_class', 'task',
#     'labels' as input and gives the output.
# ##################################################################

import importlib
import json
import re
import sys
import warnings
from collections import defaultdict

from transformers import AutoTokenizer, pipeline

warnings.simplefilter('ignore')
input_str = sys.stdin.read()

model_name = sys.argv[1]
transformer_class = sys.argv[2]
task = sys.argv[3]

# All extra parameters required for processing.
extra_kwargs = json.loads(sys.argv[4])
DELIMITER = extra_kwargs['delimiter']

def mask_label(sentence, l_s, mask_token="***"):
    """
    Masking the entities with '***'.
    """
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in l_s) + r')\b'
    updated_sentence = re.sub(pattern, '***', sentence)
    return updated_sentence


if len(input_str) > 0:
    model_name = model_name.split('/')[1]
    model_ckpt = f"./models/{model_name}"
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt)

    model = getattr(getattr(importlib.import_module("transformers"),
                            transformer_class), "from_pretrained")(model_ckpt)

    # Check for any extra arguments required for pipeline and load them as dict.
    pipeline_kwargs = extra_kwargs.get('pipeline_kwargs', {})
    pipe = pipeline(task, model=model_ckpt, tokenizer=tokenizer, device='cuda', **pipeline_kwargs)

    l_s = []
    for line in input_str.splitlines():
        l_s = []
        fields = line.strip().split(DELIMITER)
        # Only process the first value (column) before delimiter
        text_to_process = fields[0]
        # Add the labels while inferencing in case of classification.
        if 'classify_labels' in extra_kwargs:
            prediction = pipe(text_to_process, extra_kwargs['classify_labels'])
        else:
            prediction = pipe(text_to_process)

        # Check if 'entity_group' is present. If yes, separate those to columns and output them.
        if 'entity_groups' in extra_kwargs:
            entity_group = extra_kwargs['entity_groups'].split(',')
            groups = defaultdict(list, {key: [] for key in entity_group})
            i = 0
            while i < len(prediction):
                if prediction[i]['entity_group'] in entity_group:
                    groups[prediction[i]['entity_group']].append(prediction[i]['word'])
                i += 1
            
            # Create separate output fields for each entity group
            # Using the original field
            output_fields = [text_to_process]
            # Add any remaining columns from the input
            remaining_cols = fields[1:]
            output_fields.extend(remaining_cols)
            
            # Add each entity group as its own field in the order specified
            for key in entity_group:
                output_fields.append(",".join(groups[key]) if groups[key] else "")
                
            # Join all fields with the delimiter and print
            print(DELIMITER.join(map(str, output_fields)))
        else:
            # If internal_mask==True, then mask the recognized entities.
            if 'internal_mask' in extra_kwargs and extra_kwargs['internal_mask']:
                for p in prediction:
                    l_s.append(p['word'])
                remaining_cols = fields[1:]
                output_fields = [text_to_process] + remaining_cols + [mask_label(text_to_process, ','.join(l_s))]
                print(DELIMITER.join(map(str, output_fields)))
            else:
                # if output_label is present, then extract the columns from the output_labels.
                if 'output_labels' in extra_kwargs:
                    output_labels = extra_kwargs['output_labels'].split(",")
                    for i in output_labels:
                        l_s.append(prediction[0][i])
                # Print: processed column, then remaining columns, then result
                remaining_cols = fields[1:]
                output_fields = [text_to_process] + remaining_cols + [DELIMITER.join(str(x) for x in l_s) if len(l_s) > 0 else str(prediction)]
                print(DELIMITER.join(map(str, output_fields)))