"""
    This script detects dat bad data tho and alerts project personnel
    so that they can manually review flagged data files.
"""
import json
import nltk
import re
import pandas as pd

from string        import punctuation
from nltk.corpus   import stopwords
from nltk.tokenize import word_tokenize

##############################
#         FUNCTIONS          #
##############################
def clean_data(data):
    """Pre-process data to remove things that don't convey mearning."""
    # Stuff to remove
    exclude    = set(punctuation)
    stop_words = stopwords.words('english')
    
    # Remove stop words
    text_tokenize = word_tokenize(data['TXT'].lower())
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
    # UNCOMMENT THESE IF NEED TO DOWNLOAD
    #nltk.download('punkt')
    #nltk.download('stopwords')
    
    # THIS IS FOR TESTING
    test_data = load_data('OriginalTrainingData\\original_data4.txt')
    for line in test_data:
        print(line)
    