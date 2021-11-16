# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

##############################
#          IMPORTS           #
##############################

import os
import re
import json
from string import punctuation
import pandas as pd
from collections import Counter
import nltk
from nltk.corpus import stopwords

##############################
#         FUNCTIONS          #
##############################
def clean_data(data):
    """Pre-process data to remove things that don't convey mearning."""
    # Stuff to remove
    exclude    = set(punctuation)
    stop_words = stopwords.words('english')
    
    # Remove stop words
    text_tokenize = data['TXT'].lower().split(' ')
    removed_stop  = [token for token in text_tokenize if not token in stop_words]
    removed_stop  = " ".join(removed_stop)
    
    # Remove punctuation
    removed_punc = [char for char in removed_stop if char not in exclude]
    data['TXT']  = "".join(removed_punc).rstrip(' ')
    
    
def load_data(directory_name):
    """Load data into a pandas dataframe."""
    # Initialize
    data = []
    
    # Loads contents of data files into a master dictionary with key:value pairs ACTION:TXT
    training_files = os.listdir(os.path.join(os.getcwd(), directory_name))
    
    for training_file in training_files:
        filename = os.path.join(directory_name, training_file)
        with open(filename, 'r') as file:
            for line in file:
                try:
                    # Convert each line to dict
                    line_dict = json.loads(line)
                except:
                    # Separate only at commas that are followed by all caps 
                    # text without a space (Action label is the all the caps thing)
                    txt_action_values = re.split(r',([A-Z]+)', line)

                    # Use try to skip over improperly formatted data
                    try:
                        # Convert each line to dict
                        line_dict = {'TXT':txt_action_values[0], 'ACTION':txt_action_values[1]}
                    except:
                        pass
                finally:
                    # Clean data and append to list of lists
                    clean_data(line_dict) 
                    data.append([line_dict['TXT'], line_dict['ACTION']])
    
    # return a pandas data frame
    return pd.DataFrame(data, columns = ['TXT', 'ACTION'])

##############################
#         MAIN CODE          #
##############################

if __name__ == '__main__':
    # UNCOMMENT THESE IF NEED TO DOWNLOAD
    #nltk.download('punkt')
    #nltk.download('stopwords')
    
    # THIS IS FOR TESTING
    df = load_data('CleanedTrainingData')
    
    # Separate data by labels into list of lists
    dat = []
    for action in ['PIZZA', 'JOKE', 'WEATHER', 'GREET', 'TIME']:
        # Filter data frame for a specific action
        filtered_df = df[df['ACTION'] == action]
        # Convert data frame column into a list
        flatten_col = []
        for x in filtered_df['TXT'].tolist():
            # Split each text by its words
            x = x.split(' ')
            for y in x:
                flatten_col.append(y)
        dat.append(flatten_col)
        
    # Initialize counter objects for each action
    counters = [Counter(),Counter(),Counter(),Counter(),Counter()]
    # Update each counter with the data from dat
    for i in range(5):
        counters[i].update(dat[i])
    
    # Initialize list for keywords for each action
    keys = [[], [], [], [], []]
    for i in range(5):
        for word in counters[i].keys():
            # Initialize array to be filled with boolean if 
            unique = []
            for j in range(5):
                # Test if word is at least 10x more prevalent for action i
                # than any other action, if so append True to unique
                if i != j and counters[j][word]*10 < counters[i][word]:
                    unique.append(True)
            # Test if condition was true for all 4 other actions, if so
            # qualifies as a keyword for action i
            if sum(unique) == 4:
                keys[i].append(word)
    
    # Saves each keyword into a separate .txt file for later use
    actions = ['pizza', 'joke', 'weather', 'greet', 'time']
    for i in range(5):
        with open('keyword_data/keys_{}.txt'.format(actions[i]), 'w') as file:
            for word in keys[i]:
                # Use try to skip over words with non-compatable characters
                try:
                    file.write(word + '\n')
                except:
                    pass
                
        
    
    
