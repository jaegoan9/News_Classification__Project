import sys
import re
import os.path
import unicodedata
import multiprocessing
import json
import argparse

import pandas as pd
import numpy as np
from collections import defaultdict, OrderedDict
from sklearn.model_selection import train_test_split

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable

#import current directory files
import model
import train
import pre_processing

parser = argparse.ArgumentParser(description='News Header Classification')
# learning
parser.add_argument('-lr', type=float, default=0.001, help='initial learning rate [default: 0.001]')
parser.add_argument('-epochs', type=int, default=64, help='number of epochs for train [default: 256]')
parser.add_argument('-batch-size', type=int, default=1024, help='batch size for training [default: 64]')
# data 
parser.add_argument('-shuffle', action='store_true', default=False, help='shuffle the data every epoch')
args = parser.parse_args()

#check if dataset exist
data_process = pre_processing.Preprocessing()
if not os.path.exists('lemmatized.txt'):
	data_process.lemmatize()
if not os.path.exists('/feature_json_multi'):
	data_process.process_data(process=True)

#Loading Data
#--------------------------------------#
true_labels = []
with open('label.txt', 'r') as labels:
	for label in labels:
		true_labels.append(label)
true_labels = true_labels[:80000]

data_vector = []
for i in range(0, 8, 2):
	for j in range(1, 21):
		data_json = json.load(open('/feature_json_multi/feature_vector' +str(i*10000 + j) +'.json'), object_pairs_hook=OrderedDict)
		data_vector += data_json.values()
print("Completely loaded data")

train_data = np.asarray(data_vector).astype(float)
train_label = np.asarray(true_labels).astype(float)
idx = np.random.permutation(len(train_data))
train_data, train_label = train_data[idx], train_label[idx]

train_data, test_data, train_labels, test_labels = train_test_split(train_data,
													train_label,
													test_size=0.1) #do a train_test split
train_iter = []
number_of_batch = int(len(train_data) / args.batch_size)

for i in range(number_of_batch):
	if len(train_data[i*args.batch_size:(i+1)*args.batch_size]) > 0:
		train_iter.append((train_data[i*args.batch_size:(i+1)*args.batch_size], train_labels[i*args.batch_size:(i+1)*args.batch_size]))
if len(train_data[number_of_batch*args.batch_size:]) > 0:
	train_iter.append((train_data[number_of_batch*args.batch_size:], train_labels[number_of_batch*args.batch_size:]))

test_iter = []
number_of_test_batch = int(len(test_data) / args.batch_size)
for i in range(number_of_test_batch):
	if len(train_data[i*args.batch_size:(i+1)*args.batch_size]) > 0:
		test_iter.append((train_data[i*args.batch_size:(i+1)*args.batch_size], train_labels[i*args.batch_size:(i+1)*args.batch_size]))
if len(train_data[number_of_test_batch*args.batch_size:]) > 0:
	test_iter.append((train_data[number_of_test_batch*args.batch_size:], train_labels[number_of_test_batch*args.batch_size:]))

model = model.Simple_Net()

#Run Train
#--------------------------------------#
train.train(model, train_iter, test_iter, args)
