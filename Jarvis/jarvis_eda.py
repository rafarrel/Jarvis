# PROJECT 02 - EXPLORATORY DATA ANALYSIS
# TEAM RED PIRANHA


##############################
#          IMPORTS           #
##############################

import os
import re
import csv
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


def load_csv(directory, file):
    data = {}

    filepath = os.path.join(os.getcwd(), directory, file)
    with open(filepath, 'r') as f:
        csvReader = csv.reader(f)
        for row in csvReader:
            if 'TXT' not in row:
                data[row[0]] = row[1]
            else:
                pass
    
    return data
            

def run_mlp(train_X, test_X, train_Y, test_Y):
    mlp = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = False, learning_rate = 'adaptive', activation = 'relu')
    mlp.fit(train_X, train_Y)
    pm = performance_metrics(mlp, test_X, test_Y)

    return pm
    
def vectorize_data(X, Y):
    vectorizer = CountVectorizer()
    jarvis_vectorizer = vectorizer.fit_transform(X)
    jarvis_array = jarvis_vectorizer.toarray()
    jarvis_words = vectorizer.get_feature_names()
    
    # Split data into training and testing subsets
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y)
    
    # Fitting Vectorizer to training and testing data, then sending to an array 
    trainX_vec = vectorizer.fit_transform(X_train)
    trainX_array = trainX_vec.toarray()
    testX_vec = vectorizer.transform(X_test)
    testX_array = testX_vec.toarray()
    
    return trainX_array, testX_array, Y_train, Y_test
    
##############################
#         MAIN CODE          #
##############################

#load dictionaries of original (provided) and cleaned external training data
original_data = load_data('original_data')
cleaned_data = load_data('training_data')
pr01_data = load_csv('PR01_data', 'pr01_data.csv')
combined_data = {**cleaned_data, **pr01_data}


#calculate counts of each ACTION
original_counts = Counter(original_data.values())
cleaned_counts = Counter(cleaned_data.values())  

#get lists of keys and values for original data
origX, origY = map(list, zip(*original_data.items()))
pr01X, pr01Y = map(list, zip(*pr01_data.items()))
combinedX, combinedY = map(list, zip(*combined_data.items()))


#vectorize data
origtrainX, origtestX, origYtrain, origYtest = vectorize_data(origX, origY)
pr01trainX, pr01testX, pr01Ytrain, pr01Ytest = vectorize_data(pr01X, pr01Y)
combinedtrainX, combinedtestX, combinedYtrain, combinedYtest = vectorize_data(combinedX, combinedY)


#run MLP
run_mlp(origtrainX, origtestX, origYtrain, origYtest)
run_mlp(trainX_array, testX_array, Y_train, Y_test)
run_mlp(pr01trainX, pr01testX, pr01Ytrain, pr01Ytest)
run_mlp(combinedtrainX, combinedtestX, combinedYtrain, combinedYtest)




##############################
#      VISUALIZATIONS        #
##############################

#bar plot of counts of each ACTION for original vs. cleaned external data
orig_count = plt.bar(original_counts.keys(), original_counts.values(), width = 0.3, align = 'edge', color = '#D81B60', label = 'Original Data')
clean_count = plt.bar(cleaned_counts.keys(), cleaned_counts.values(), width = 0.3, align = 'center', color = '#1E88E5', label = 'Cleaned Data')
plt.legend(loc = 'lower right')
plt.ylabel('Number of Occurrences')
plt.show()
