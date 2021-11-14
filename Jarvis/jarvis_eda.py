# PROJECT 02 - EXPLORATORY DATA ANALYSIS
# TEAM RED PIRANHA


##############################
#          IMPORTS           #
##############################

import os
import re
import json
from string import punctuation
import numpy as  np
import pandas as pd
from matplotlib import pyplot as plt
from collections import Counter
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from Jarvis_classifiers import performance_metrics, trainX_array, testX_array, Y_train, Y_test

##############################
#         FUNCTIONS          #
##############################

def load_data(directory):
    "Loads contents of data files from the given directory into a  dictionary with key:value pairs ACTION:TXT"
    data = {}
    #one_line_list = []
    
    files = os.listdir(os.path.join(os.getcwd(), directory))
    
    for file in files:
        filepath = os.path.join(directory, file)
        with open(filepath, 'r') as f:
            if 'DS_Store' not in filepath:
                for line in f:
                    filetest = f.readline()
                    try:
                        if filetest[0] == "{":
                            data['TXT'] = filetest['ACTION']
                        else:
                            temp = re.split(r',([A-Z]+)', filetest)
                            data[temp[0]] = temp[1]
                    except:
                        pass
    return data

    
##############################
#         MAIN CODE          #
##############################

#load dictionaries of original (provided) and cleaned external training data
original_data = load_data('original_data')
cleaned_data = load_data('training_data')
pr01_data = load_data('PR01_data')

#calculate counts of each ACTION
original_counts = Counter(original_data.values())
cleaned_counts = Counter(cleaned_data.values())  

#get lists of keys and values for original data
origX, origY = map(list, zip(*original_data.items()))


#vectorize original data
vectorizer = CountVectorizer()
jarvis_vectorizer = vectorizer.fit_transform(origX)
jarvis_array = jarvis_vectorizer.toarray()
jarvis_words = vectorizer.get_feature_names()

# Split data into training and testing subsets
origX_train, origX_test, origY_train, origY_test = train_test_split(origX, origY)

# Fitting Vectorizer to training and testing data, then sending to an array 
trainX_orig = vectorizer.fit_transform(origX_train)
origtrainX_array = trainX_orig.toarray()
testX_orig = vectorizer.transform(origX_test)
origtestX_array = testX_orig.toarray()


#MLP for original data
print('********** Original Multi-Layer Perceptron Classifier Results *************')
mlp_orig = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = False, learning_rate = 'adaptive', activation = 'relu')
mlp_orig.fit(origtrainX_array, origY_train)
performance_metrics(mlp_orig, origtestX_array, origY_test)
print('***********************************************************************')

#MLP for cleaned data
print('********** Cleaned Multi-Layer Perceptron Classifier Results *************')
mlp_clean = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = False, learning_rate = 'adaptive', activation = 'relu')
mlp_clean.fit(trainX_array, Y_train)
performance_metrics(mlp_clean, testX_array, Y_test)
print('***********************************************************************')



##############################
#      VISUALIZATIONS        #
##############################

#bar plot of counts of each ACTION for original vs. cleaned external data
orig_count = plt.bar(original_counts.keys(), original_counts.values(), width = 0.3, align = 'edge', color = '#D81B60', label = 'Original Data')
clean_count = plt.bar(cleaned_counts.keys(), cleaned_counts.values(), width = 0.3, align = 'center', color = '#1E88E5', label = 'Cleaned Data')
plt.legend(loc = 'lower right')
plt.ylabel('Number of Occurrences')
plt.show()
