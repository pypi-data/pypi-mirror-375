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
#   * The script is used in apply query for finding similarity
#     between sentences using 'all-MiniLM-L6-v2' hugging face model.
# ##################################################################
# -*- coding: utf-8 -*-

import re
import sys
import warnings

import torch
import torch.nn.functional as F
from sentence_transformers import util
from transformers import AutoModel, AutoTokenizer

def extract_numbers(string):
   numbers = re.findall(r'\b\d+\.\d+|\b\d+', string)
   # Join numbers with a space or another desired separator.
   return ' '.join(numbers)

# Mean Pooling - Take attention mask into account for correct averaging.
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] # First element of model_output contains all token embeddings.
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


warnings.simplefilter('ignore')
input_str = sys.stdin.read()

DELIMITER = '#'
if len(input_str) > 0:
    torch_device = 'cuda'
    model_path = "sentence-transformers/all-MiniLM-L6-v2"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModel.from_pretrained(model_path)
    for line in input_str.splitlines():
        fields = line.strip().split(DELIMITER)
        sentences = fields[:2]  # Only the first two columns for sentence similarity
        
        # Tokenize sentences.
        encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings.
        with torch.no_grad():
            model_output = model(**encoded_input)
    
        # Perform pooling.
        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    
        # Normalize embeddings.
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
       
        # Compute cosine-similarities for each sentence with each other sentence.
        cosine_scores = util.cos_sim(sentence_embeddings[0], sentence_embeddings[1])
        cosine_scores = extract_numbers(str(cosine_scores))
        
        # Print: first two columns, then remaining columns, then result
        remaining_cols = fields[2:]
        output_fields = [sentences[0], sentences[1]] + remaining_cols + [cosine_scores]
        print(DELIMITER.join(map(str, output_fields)))
