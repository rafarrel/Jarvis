# PROJECT 02 - PICKLING JARVIS
# TEAM RED PIRANHA
# COMPETITION 1

##############################
#          IMPORTS           #
##############################

import os
import re
import json
from string import punctuation
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn import ensemble
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import RandomizedSearchCV
import pickle

##############################
#         FUNCTIONS          #
##############################

def dict_to_df(dict, action, df):
    exclude = set(punctuation) # Keep a set of "bad" characters.
    for i in dict:
        list_letters_noPunct = [ char for char in i if char not in exclude ]  
        text_noPunct = "".join(list_letters_noPunct)
        i=text_noPunct.lower() 
        del list_letters_noPunct[-1]
        df.loc[len(df)] = [i, action]
    return df

def performance_metrics(clf, X_test, y_test):
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

def pickled_piranha(clf, filename):
    #destination = os.path.join(classifier_directory, filename)
    vec_clf = Pipeline([('vec', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('class', clf)])
    vec_clf.fit(X_train, Y_train)
    print("\nSaving classifier...")
    with open(filename, 'wb') as file:
        pickle.dump(vec_clf, file)
    print(f"Classifier saved to {os.getcwd()}\n")
    path = filename + '.pkl'
    with open(path, 'wb') as pickle_jar:
        pickle.dump(vec_clf, pickle_jar)
        
        
def open_pickle_jar(filename):   
    return pickle.load(open(filename, 'rb'))
    


##############################
#    OBJECT INSTANTIATION    #
##############################

master_dict = {'PIZZA': [], 'JOKE': [], 'WEATHER': [], 'TIME': [], 'GREET': []}
dict_list = []
one_line_list = []

##############################
#         MAIN CODE          #
##############################

# Loads contents of data files into a master dictionary with key:value pairs ACTION:TXT 

training_files = os.listdir(os.path.join(os.getcwd(), 'training_data'))

for file in training_files:
    filepath = os.path.join('training_data', file)
    with open(filepath, 'r') as f:
        if 'DS_Store' not in filepath:
            for line in f:
                filetest = f.readline()
                try:
                    if filetest[0] == "{":
                        sub_dict = json.loads(line)
                        temp = master_dict[sub_dict['ACTION']]
                        temp.append(sub_dict['TXT'].lower())
                        master_dict[sub_dict['ACTION']] = temp
                    else:
                        one_line_list.append(re.split(r',([A-Z]+)', filetest))
                        temp = master_dict[one_line_list[-1][1]]
                        temp.append(one_line_list[-1][0])
                        master_dict[one_line_list[-1][1]] = temp
                except:
                    pass

# Creates an empty dataframe with two columns labeled TXT, ACTION

df = pd.DataFrame(columns = ['TXT', 'ACTION'])



# Populates the dataframe with 1,868 TXT entries and ACTION labels

pizza_list = dict_to_df(master_dict['PIZZA'], 'PIZZA', df)
joke_list = dict_to_df(master_dict['JOKE'], 'JOKE', df)
weather_list = dict_to_df(master_dict['WEATHER'], 'WEATHER', df)
greet_list = dict_to_df(master_dict['GREET'], 'GREET', df)
time_list = dict_to_df(master_dict['TIME'], 'TIME', df)

# Separates the dataframe into input and target column vectors for the classifiers to use

X = df['TXT']
Y = df['ACTION']

# Instanatiates a CountVectorizer() object to run frequencies for every unique word in X and put
# those frequencies into one 1868 x 952 word frequency matrix where each line is associated with one
# TXT and can map to the corresponding entry in Y, which is the label

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



# """ K NEAREST NEIGHBORS CLASSIFIER """
# print('************ K Nearest Neighbor Classifier Results *********************')
# kn = KNeighborsClassifier()
# kn.fit(trainX_array, Y_train)
# performance_metrics(kn, testX_array, Y_test)
# print('***********************************************************************')



############################## PICKLING JARVIS ##################################
pickled_piranha(nb, 'nb')
nb_brain = open_pickle_jar('nb.pkl')
print(nb_brain.predict(['Hello funny roboooot!']))

pickled_piranha(rfc, 'rfc')
rfc_brain = open_pickle_jar('rfc.pkl')
print(rfc_brain.predict(['Hello funny roboooot!']))

pickled_piranha(mlp, 'mlp')
mlp_brain = open_pickle_jar('mlp.pkl')
print(mlp_brain.predict(['Hello funny roboooot!']))

pickled_piranha(dtc, 'dtc')
dtc_brain = open_pickle_jar('dtc.pkl')
print(dtc_brain.predict(['Hello funny roboooot!']))

pickled_piranha(svc, 'svc')
svc_brain = open_pickle_jar('svc.pkl')
print(svc_brain.predict(['Hello funny roboooot!']))


################################ GRID SEARCH ####################################
filename = 'nb.pkl'
classifiers = ['nb']

for classifier in classifiers:
    model = open_pickle_jar(filename)
    clf = RandomizedSearchCV(model, model.get_params, random_state=0)
    search = clf.fit()
    print(classifier, 'best params:')
    print('------------------------')
    print(search.best_params_)