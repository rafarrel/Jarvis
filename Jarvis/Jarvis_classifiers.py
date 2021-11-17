# PROJECT 02 - PICKLING JARVIS
# TEAM RED PIRANHA
# COMPETITION 1

##############################
#          IMPORTS           #
##############################

import os
import json
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
                    if line_dict['ACTION'] == 'joke': #check for typo
                        line_dict['ACTION'] = 'JOKE'
                    if line_dict['ACTION'] == ' PIZZA': #check for typo
                        line_dict['ACTION'] = 'PIZZA'
                except:
                    # Only split on last comma, signifying the separator between
                    # text and action label.
                    txt, action = line.rstrip('\n').rsplit(',', maxsplit=1)
                    
                    if action == 'joke': #check for typo
                        action = 'JOKE'
                    if action == ' PIZZA': #check for typo
                       action = 'PIZZA' 
                        
                    line_dict['TXT'   ] = txt
                    line_dict['ACTION'] = action
                finally:
                    data.append([line_dict['TXT'], line_dict['ACTION']]) 
    return data
            

def vectorize_data(X, Y):
    """Create training and testing vectors of X and return X vextors and Y lists"""
    vectorizer = CountVectorizer() # Instanatiates a CountVectorizer() object to run frequencies for every unique word in X
    jarvis_vectorizer = vectorizer.fit_transform(X)
    jarvis_array = jarvis_vectorizer.toarray()
    jarvis_words = vectorizer.get_feature_names()
    
    # Split data into training and testing subsets
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y) # Split data into training and testing subsets
    
    # Fitting Vectorizer to training and testing data, then sending to an array 
    trainX_vec = vectorizer.fit_transform(X_train)
    trainX_array = trainX_vec.toarray()
    testX_vec = vectorizer.transform(X_test)
    testX_array = testX_vec.toarray()
    
    return X_train, X_test, trainX_array, testX_array, Y_train, Y_test



def performance_metrics(clf, X_test, y_test):
    """Generates performance metrics output and confusion matrix plot for the given classifier"""
    print('\nPERFORMANCE METRICS: ', type(clf))
    print("Generating performance data...")
    predictions = clf.predict(X_test)
    cm = metrics.confusion_matrix(y_test, predictions)
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report:")
    print(metrics.classification_report(y_test, predictions))
    disp = metrics.ConfusionMatrixDisplay(cm)
    disp.plot()
    plt.show()


def pickled_piranha(clf, directory, filename, X_train, Y_train):
    """Created .pkl from specified classifier in the given location with given name"""
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
        
        
def open_pickle_jar(directory, filename):
    """loads .pkl file"""
    return pickle.load(open(os.path.join(directory, filename), 'rb'))

    

##############################
#         MAIN CODE          #
##############################

# Load data into list
cleaned_data = load_data('CleanedTrainingData')
rc_data = load_data('RecoveryCoachTrainingData')

#Separate into lists of X (text) and Y (actions)
X, Y = map(list, zip(*cleaned_data))
X_rc, Y_rc = map(list, zip(*rc_data))

#Vectorize Data
X_train, X_test, trainX_array, testX_array, Y_train, Y_test = vectorize_data(X, Y)
Xrc_train, Xrc_test, trainXrc_array, testXrc_array, Yrc_train, Yrc_test = vectorize_data(X_rc, Y_rc)


################# MULTINOMIAL NAIVE BAYES CLASSIFIER #############################

print('********** Mulitnomial Naive Bayes Classifier Results *******************')
nb = MultinomialNB()
nb.fit(trainX_array, Y_train)
performance_metrics(nb, testX_array, Y_test)
print('***********************************************************************')



####################### RANDOM FOREST CLASSIFIER ##################################

print('**************** Random Forest Classifier Results ***********************')
rfc = ensemble.RandomForestClassifier(n_estimators=25)
rfc.fit(trainX_array, Y_train)
performance_metrics(rfc, testX_array, Y_test)
print('***********************************************************************')


################# MULTI-LAYER PERCEPTRON CLASSIFIER #############################

print('************ Multi-Layer Perceptron Classifier Results ******************')
mlp = MLPClassifier(hidden_layer_sizes=400)
mlp.fit(trainX_array, Y_train)
performance_metrics(mlp, testX_array, Y_test)
print('***********************************************************************')

###################### DECISION TREE CLASSIFIER #################################

print('*************** Decision Tree Classifier Results ***********************')
dtc = DecisionTreeClassifier()
dtc.fit(trainX_array, Y_train)
performance_metrics(dtc, testX_array, Y_test)
print('***********************************************************************')


############################ SVC CLASSIFIER #####################################

print('******************** SVC Classifier Results ****************************')
svc = SVC()
svc.fit(trainX_array, Y_train)
performance_metrics(svc, testX_array, Y_test)
print('***********************************************************************')


##################### K NEAREST NEIGHBOR CLASSIFIER #############################

print('************ K Nearest Neighbor Classifier Results *********************')
kn = KNeighborsClassifier()
kn.fit(trainX_array, Y_train)
performance_metrics(kn, testX_array, Y_test)
print('***********************************************************************')


################################ GRID SEARCH ####################################

#UNCOMMENT ONLY WHEN NEEDED TO SAVE TIME WHEN RUNNING
# mlp_params = {'activation': ['identity', 'logistic', 'tanh', 'relu'],
              # 'solver': ['lbfgs', 'sgd', 'adam'],'learning_rate': ['constant', 'invscaling', 'adaptive'],
              # 'shuffle': [True, False]}



# mlp_clf = RandomizedSearchCV(mlp, mlp_params, random_state=None, n_jobs = -1)
# search = mlp_clf.fit(trainX_array, Y_train)
# print()
# print('mlp', 'best params:')
# print('------------------')
# print(search.best_params_)

# search_rc = mlp_clf.fit(trainXrc_array, Yrc_train)
# print()
# print('mlp_rc', 'best params:')
# print('------------------')
# print(search_rc.best_params_)




################# TUNED MULTI-LAYER PERCEPTRON CLASSIFIER ########################

print('********** Tuned Multi-Layer Perceptron Classifier Results *************')
mlp_tuned = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = True, learning_rate = 'adaptive', activation = 'relu')
mlp_tuned.fit(trainX_array, Y_train)
performance_metrics(mlp_tuned, testX_array, Y_test)
print('***********************************************************************')

print('****** Competition 3 Multi-Layer Perceptron Classifier Results *********')
mlp_rc = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = True, learning_rate = 'invscaling', activation = 'relu')
mlp_rc.fit(trainXrc_array, Yrc_train)
performance_metrics(mlp_rc, testXrc_array, Yrc_test)
print('***********************************************************************')


############################## PICKLING JARVIS ##################################

pickled_piranha(mlp_tuned, 'Classifiers', 'jarvis_REDPIRANHA.pkl', X_train, Y_train)
mlp_brain = open_pickle_jar('Classifiers', 'jarvis_REDPIRANHA.pkl')
print('mlp:', mlp_brain.predict(['Hello funny roboooot!']))

pickled_piranha(mlp_rc, 'Classifiers', 'jarvis_comp3_REDPIRANHA', Xrc_train, Yrc_train)
mlp_rc_brain = open_pickle_jar('Classifiers', 'jarvis_comp3_REDPIRANHA.pkl')
print('mlp_rc:', mlp_rc_brain.predict(['I feel like I may use']))
