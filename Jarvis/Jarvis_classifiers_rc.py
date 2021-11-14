# PROJECT 02 - PICKLING JARVIS
# TEAM RED PIRANHA
# COMPETITION 1

##############################
#          IMPORTS           #
##############################

import os
import re
import csv
from string import punctuation
import pandas as pd
import numpy as  np
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn import ensemble
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
import pickle

##############################
#         FUNCTIONS          #
##############################

def performance_metrics(clf, X_test, y_test):
    print('\nPERFORMANCE METRICS: ', type(clf))
    print("Generating performance data...")
    predictions = clf.predict(X_test)
    cm = metrics.confusion_matrix(y_test, predictions)
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(metrics.classification_report(y_test, predictions))
    class_report = metrics.classification_report(y_test, predictions)
    disp = metrics.ConfusionMatrixDisplay(cm)
    disp.plot()
    plt.show()

    return class_report

def pickled_piranha(clf, directory, filename):
    vec_clf = Pipeline([('vec', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('class', clf)])
    vec_clf.fit(X_train, Y_train)
    print("\nSaving classifier...")

    try:
        with open(os.path.join(os.getcwd(), directory, filename), 'wb') as file:
            pickle.dump(vec_clf, file)
    except:
        os.mkdir(directory)
        with open(os.path.join(os.getcwd(), directory, filename), 'wb') as file:
            pickle.dump(vec_clf, file)
            
    path = os.path.join(os.getcwd(), directory, filename) + '.pkl'
    with open(path, 'wb') as pickle_jar:
        pickle.dump(vec_clf, pickle_jar)
        


##############################
#         MAIN CODE          #
##############################

# Loads contents of data files into a master dictionary with key:value pairs TXT:ACTION 

data = {}

filepath = os.path.join(os.getcwd(), 'addiction_training_data', 'addiction-training-data.csv')
with open(filepath, 'r') as f:
    csvReader = csv.reader(f)
    for row in csvReader:
        if 'TXT' not in row:
            data[row[0]] = row[1]
        else:
            pass


X, Y = map(list, zip(*data.items()))

# Instanatiates a CountVectorizer() object to run frequencies for every unique word in X 
vectorizer = CountVectorizer()
jarvis_vectorizer = vectorizer.fit_transform(X)
jarvis_array = jarvis_vectorizer.toarray()
jarvis_words = vectorizer.get_feature_names()

# Split data into training and testing subsets

X_train, X_test, Y_train, Y_test = train_test_split(X, Y)

# Fitting Vectorizer to training and testing data, then sending to an array 

trainX = vectorizer.fit_transform(X_train)
trainX_array = trainX.toarray()
testX = vectorizer.transform(X_test)
testX_array = testX.toarray()


################# TUNED MULTI-LAYER PERCEPTRON CLASSIFIER ########################

print('********** Tuned Multi-Layer Perceptron Classifier Results *************')
mlp_tuned = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = False, learning_rate = 'adaptive', activation = 'relu')
mlp_tuned.fit(trainX_array, Y_train)
performance_metrics(mlp_tuned, testX_array, Y_test)
print('***********************************************************************')


############################## PICKLING JARVIS ##################################
pickled_piranha(mlp_tuned, 'Classifiers', 'jarvis_mlp_REDPIRANHA_recoverycoach')
