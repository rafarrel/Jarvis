# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 14:56:51 2021

@author: tedha
"""

import json
import re
from string import punctuation
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
    
    
def load_data(filename):
    """Load data into a pandas dataframe."""
    data = []
    
    with open(filename, 'r') as file:
        for line in file:
            try:
                line_dict = json.loads(line)
            except:
                # Separate only at commas that are followed by all caps 
                # text without a space (Action label is the all the caps thing)
                txt_action_values = re.split(r',([A-Z]+)', line)[:-1]
                line_dict = {'TXT':txt_action_values[0], 'ACTION':txt_action_values[1]}
            finally:
                clean_data(line_dict) 
                data.append([line_dict['TXT'], line_dict['ACTION']]) 
                
    return data
    

##############################
#         MAIN CODE          #
##############################
if __name__ == '__main__':
    # UNCOMMENT THESE IF NEED TO DOWNLOAD
    #nltk.download('punkt')
    #nltk.download('stopwords')
    
    ############ INSERT FILENAME HERE #############
    filename = "OriginalTrainingData/original_data59.txt"
    
    # load data from given filename
    data = load_data(filename)
    
    # Get file length
    file_length = len(data)
    
    # Converts data to a list of lists where outer list is the actions
    # and the inner list is all text for those actions
    dat = []
    actions = ['PIZZA', 'JOKE', 'WEATHER', 'GREET', 'TIME']
    for action in actions:
        txt_dat = []
        for datapt in data:
            if datapt[1] == action:
                txt_dat.append(datapt[0])
        dat.append(txt_dat)
    
    # Load the keywords from text files for each action
    keywords = {'PIZZA':[], 
                'JOKE':[],
                'WEATHER':[],
                'GREET':[],
                'TIME':[]}
   
    # Loop through to load the keywords
    for action in actions:
        keys_cleaned = []
        with open('keyword_data/keys_{}.txt'.format(action.lower()),'r') as file:
            keys = file.readlines()
        for key in keys:
            key = key.replace('\n', '')
            keys_cleaned.append(key)
        keywords[action] = keys_cleaned
    
    # Determine number of suspicious data points
    sus = 0 # indicates number of suspicious data points in file
    sus_txt = [] # lists the text of the suspicious data points, for testing
    for i in range(5):
        # Construct keywords string for other actions
        keys_other = []
        for j in range(5):
            if i != j:
                keys_other = keys_other + keywords[actions[j]]
        # Construct keywords string for current action
        keys = keywords[actions[i]]
        
        # Check if txt has no keywords for current action but has keywords for other actions
        # If so, txt labelled as sus
        txt = dat[i]
        for string in txt:
            # Conditions for 'bad' data
            cond1 = any([word in string for word in keys_other])
            cond2 = not any([word in string for word in keys])
            cond3 = string != ''
            if cond1 and cond2 and cond3:
                sus_txt.append([string, actions[i], cond1, cond2]) # for testing
                sus += 1
                
    # Determine if file is good or bad depending on sus/file_length ratio
    # Ratios greater than 0.05 will be considered bad.
    # If bad, at least 5% of data is potentionally wrong and should be
    # reviewed.
    if sus / file_length < 0.05:
        print("good")
    else:
        print("bad")
        
    
    
