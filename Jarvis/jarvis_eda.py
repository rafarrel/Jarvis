# PROJECT 02 - EXPLORATORY DATA ANALYSIS
# TEAM RED PIRANHA


##############################
#          IMPORTS           #
##############################

import os
import json
from matplotlib import pyplot as plt
from collections import Counter
from sklearn import metrics
import statistics as stats
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
            

def run_mlp(train_X, test_X, train_Y, test_Y):
    """Runs Multi-Level Perceptron Classifier on the specified training and testing data"""
    mlp = MLPClassifier(hidden_layer_sizes=400, solver = 'adam',
                          shuffle = False, learning_rate = 'adaptive', activation = 'relu')
    mlp.fit(train_X, train_Y)
    performance_metrics(mlp, test_X, test_Y)
    predictions = mlp.predict(test_X)
    mcr = metrics.classification_report(test_Y, predictions)

    return mcr
    
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

#create list of combined clean and custom data
combined_data = [[]]
combined_data.extend(cleaned_data)
combined_data.extend(pr01_data)
combined_data= combined_data[1:]


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


#run MLP 35 times for each dataset to get range, mean, variance, standard deviation
clean_perf = []
pr01_perf = []
combined_perf = []
for i in range(0,35):
    temp1 = run_mlp(trainX_array, testX_array, Y_train, Y_test)
    temp2 = run_mlp(pr01trainX, pr01testX, pr01Ytrain, pr01Ytest)
    temp3 = run_mlp(combinedtrainX, combinedtestX, combinedYtrain, combinedYtest)
    clean_perf.append(float(temp1[365:369]))
    pr01_perf.append(float(temp2[365:369]))
    combined_perf.append(float(temp3[365:369]))

#statistical metrics on accuracy of MLP for each dataset
#Cleaned External Data
min_clean = min(clean_perf) #0.95
max_clean = max(clean_perf) #0.96
mean_clean = stats.mean(clean_perf) #0.959
stdev_clean = stats.stdev(clean_perf) #0.003
var_clean = stats.variance(clean_perf) #0.00001

#Custom PR01 Data
min_pr01 = min(pr01_perf) #0.79
max_pr01 = max(pr01_perf) #0.79
mean_pr01 = stats.mean(pr01_perf) #0.79
stdev_pr01 = stats.stdev(pr01_perf) #0
var_pr01 = stats.variance(pr01_perf) #0

#Combined Cleaned and PR01 Data
min_comb = min(combined_perf) #0.95
max_comb = max(combined_perf) #0.96
mean_comb = stats.mean(combined_perf) #0.957
stdev_comb = stats.stdev(combined_perf) #0.005
var_comb = stats.variance(combined_perf) #0.00002

##############################
#      VISUALIZATIONS        #
##############################

#bar plot of counts of each ACTION for original vs. cleaned external data
orig_count = plt.bar(original_counts.keys(), original_counts.values(), width = 0.3, align = 'edge', color = '#D81B60', label = 'Original Data')
clean_count = plt.bar(cleaned_counts.keys(), cleaned_counts.values(), width = 0.3, align = 'center', color = '#1E88E5', label = 'Cleaned Data')
plt.legend(loc = 'lower right')
plt.ylabel('Number of Occurrences')
plt.show()

