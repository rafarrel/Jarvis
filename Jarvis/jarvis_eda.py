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
from matplotlib import pyplot as plt
from collections import Counter

##############################
#         FUNCTIONS          #
##############################

def load_data(directory):
    "Loads contents of data files from the given directory into a  dictionary with key:value pairs ACTION:TXT"
    data = {'PIZZA': [], 'JOKE': [], 'WEATHER': [], 'TIME': [], 'GREET': []}
    one_line_list = []
    
    original_files = os.listdir(os.path.join(os.getcwd(), directory))
    
    for file in original_files:
        filepath = os.path.join(directory, file)
        with open(filepath, 'r') as f:
            if 'DS_Store' not in filepath:
                for line in f:
                    filetest = f.readline()
                    try:
                        if filetest[0] == "{":
                            sub_dict = json.loads(line)
                            temp = data[sub_dict['ACTION']]
                            temp.append(sub_dict['TXT'].lower())
                            data[sub_dict['ACTION']] = temp
                        else:
                            one_line_list.append(re.split(r',([A-Z]+)', filetest))
                            temp = data[one_line_list[-1][1]]
                            temp.append(one_line_list[-1][0])
                            data[one_line_list[-1][1]] = temp
                    except:
                        pass
    return data


 
    
    
##############################
#         MAIN CODE          #
##############################

#load dictionaries of original (provided) and cleaned external training data
original_data = load_data('original_data')
cleaned_data = load_data('training_data')

#calculate counts of each ACTION
original_counts = {}
for key in original_data.keys():
    original_counts[key] = len(original_data[key])

cleaned_counts = {}
for key in cleaned_data.keys():
    cleaned_counts[key] = len(cleaned_data[key])  
    





##############################
#      VISUALIZATIONS        #
##############################


orig_count = plt.bar(original_counts.keys(), original_counts.values(), width = 0.3, align = 'edge', color = '#D81B60', label = 'Original Data')
clean_count = plt.bar(cleaned_counts.keys(), cleaned_counts.values(), width = 0.3, align = 'center', color = '#1E88E5', label = 'Cleaned Data')
plt.legend(loc = 'lower right')
plt.ylabel('Number of Occurrences')
plt.show()
