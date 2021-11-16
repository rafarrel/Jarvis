"""
    This script detects dat bad data tho and alerts project personnel
    so they can manually review flagged data files.
"""
import json
import nltk
import sys

from string        import punctuation
from nltk.corpus   import stopwords
from nltk.tokenize import word_tokenize

##############################
#         FUNCTIONS          #
##############################
def clean_data(data):
    """Pre-process data to remove things that don't convey meaning."""
    # Stuff to remove
    exclude    = set(punctuation)
    stop_words = stopwords.words('english')
    
    # Remove stop words
    tokenized_text = word_tokenize(data['TXT'].lower().replace("'", "").replace("â€™", ""))
    tokenized_text = " ".join(tokenized_text)
    
    # Remove punctuation
    removed_punc = [char for char in tokenized_text if char not in exclude]
    data['TXT']  = "".join(removed_punc).strip(' ')
 
    
def load_data(filename):
    """Load data into a list of [txt, action] pairs for processing."""
    data = []
    
    with open(filename, 'r') as file:
        for line in file:
            try:
                line_dict = json.loads(line)
            except:
                # Only split on last comma, signifying the separator between
                # text and action label.
                txt, action = line.rstrip('\n').rsplit(',', maxsplit=1)
                
                line_dict = {}
                line_dict['TXT'   ] = txt
                line_dict['ACTION'] = action
            finally:
                clean_data(line_dict) 
                data.append([line_dict['TXT'], line_dict['ACTION']]) 
    
    return data
    

##############################
#         MAIN CODE          #
##############################
if __name__ == '__main__':
    nltk.download('punkt'    , quiet=True)
    nltk.download('stopwords', quiet=True)
    
    ############### INSERT FILENAME HERE ################
    filename = '..\\OriginalTrainingData\\original_data7.txt'
    
    
    ############### PERFORM DATA ANALYSIS ###############
    data = load_data(filename)
    
    # Initial checks
    initial_passed = True
    for d in data:
        if (d[0] == 'testing time' or 
            d[0] == 'training time'   or
            d[0] == 'done'):
            initial_passed = False
    
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
        with open('KeywordData/keys_{}.txt'.format(action.lower()),'r') as file:
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
    # Ratios greater than threshold will be considered bad.
    # If bad, at least threshold% of data is potentionally wrong and should 
    # be reviewed.
    if sus / file_length <= 0.076 and initial_passed:
        print("good")
    else:
        print("bad")