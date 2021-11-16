# PROJECT 02 - EXPLORATORY DATA ANALYSIS
# TEAM RED PIRANHA


##############################
#          IMPORTS           #
##############################

import os
import csv
import json
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
    """Load data into a list of nested lists with text, action pairs."""
    data = []
    files = os.listdir(os.path.join(os.getcwd(), directory))
    
    for filename in files:
        filepath = os.path.join(os.getcwd(), directory, filename)
        with open(filepath, 'r') as file:
            for line in file:
                line_dict={}
                try:
                    line_dict.update(json.loads(line))
                except:
                    # Only split on last comma, signifying the separator between
                    # text and action label.
                    txt, action = line.rstrip('\n').rsplit(',', maxsplit=1)
                    
                    line_dict['TXT'   ] = txt
                    line_dict['ACTION'] = action
                finally:
                    data.append([line_dict['TXT'], line_dict['ACTION']]) 
    return data
            

def run_mlp(train_X, test_X, train_Y, test_Y):
    """Runs Multi-Level Perceptron Classifier on the specified training and testing data"""
    mlp = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = False, learning_rate = 'adaptive', activation = 'relu')
    mlp.fit(train_X, train_Y)
    pm = performance_metrics(mlp, test_X, test_Y)

    return pm
    
def vectorize_data(X, Y):
    """Create training and testing vectors of X and return X vextors and Y lists"""
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

#load dataframes using load_data for original, cleaned, and PR01 custom data


original_data = load_data('OriginalTrainingData')
cleaned_data = load_data('CleanedTrainingData')
pr01_data = load_data('CustomTrainingDataPR01')
combined_data = []
combined_data.extend(cleaned_data).extend(pr01_data)


#get lists of keys and values for original data
origX, origY = map(list, zip(*original_data))
cleanX, cleanY = map(list, zip(*cleaned_data))
pr01X, pr01Y = map(list, zip(*pr01_data))
combinedX, combinedY = map(list, zip(*combined_data))

#calculate counts of each ACTION
original_counts = Counter(origY)
cleaned_counts = Counter(cleanY)
combined_counts = Counter(combinedY)  


#vectorize data
origtrainX, origtestX, origYtrain, origYtest = vectorize_data(origX, origY)
pr01trainX, pr01testX, pr01Ytrain, pr01Ytest = vectorize_data(pr01X, pr01Y)
combinedtrainX, combinedtestX, combinedYtrain, combinedYtest = vectorize_data(combinedX, combinedY)


#run MLP to get range, mean, variance, standard deviation

for i in range(0,10):
    locals()['orig \0'.format(i)] = run_mlp(origtrainX, origtestX, origYtrain, origYtest)
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

