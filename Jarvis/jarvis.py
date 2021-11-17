"""
    Jarvis - A data-collecting chatbot for Slack
    Current Release: 1.0
    Jarvis is a chatbot designed for seamless integration with Slack 
    workspaces. It will collect data from users and train itself 
    to interact within the workspace.
    
    ------------------------------------------------------------------
    Release notes for v.1.0:
        - Jarvis can receive and send messages from/to Slack
        - Jarvis can enter different modes such as training and idle
        - Jarvis can store processed messages in a database
        
    ------------------------------------------------------------------
    This project is released as open-source under the permissive MIT 
    license with the approval of its sponsor, Bagrow Industries.
"""
# Database management
import sqlite3
import pandas as pd

# Jarvis brain
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split


# Slack interaction
import json 
import requests
import string
import websocket
try:
    import thread 
except ImportError:
    import _thread as thread

# Slack connection tokens
from botsettings import API_TOKEN
from botsettings import APP_TOKEN


# -------------------------------------------------------------------- #
# Any definitions for Jarvis go here and will be called in the main    #
# section below. Essentially, all Jarvis logic will be written here    #
# and called down below in the main section.                           #
# -------------------------------------------------------------------- #
class Jarvis:
    """Class that will contain all logic for Jarvis."""
    def __init__(self, WORKSPACE_URL, WORKSPACE_AUTH, POST_AUTH, debug_mode=False, display_mode=False):
        # Jarvis states
        self.IDLE   = 0  # Jarvis remains idle
        self.ACTION = 1  # Jarvis waits to receive the action name
        self.TRAIN  = 2  # Jarvis waits to receive training text
        self.TEST   = 3  # Jarvis predicts action from message text
        
        # Jarvis authorization headers
        self.WORKSPACE_AUTH = WORKSPACE_AUTH
        self.POST_AUTH      = POST_AUTH
        
        # Jarvis urls
        self.WORKSPACE_URL    = WORKSPACE_URL
        self.POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
        
        # Jarvis database
        self.database = Database()
        
        # Jarvis brain
        self.BRAIN = pickle.load(open("Classifiers/jarvis_REDPIRANHA.pkl", 'rb'))
        
        # Jarvis settings
        self.current_action = ''            # Starting action for Jarvis
        self.current_state  = self.IDLE     # Starting state for Jarvis
        self.display_mode   = display_mode  # Display Slack messages to console (on/off)
        
        # Websocket settings
        websocket.enableTrace(debug_mode)  # Debug mode for troubleshooting (on/off)
        
        # Start websocket to connect Jarvis to the Slack workspace.
        self.connection = websocket.WebSocketApp(self.WORKSPACE_URL,
                                             on_message = self.on_message,
                                             on_error   = self.on_error,
                                             on_open    = self.on_open,
                                             on_close   = self.on_close)
        
        # Run Jarvis
        self.connection.run_forever()

    # ---------------------------------------------------------------------- #
    # Jarvis States
    
    def start_action(self):
        # Start action mode
        self.current_state = self.ACTION

    def start_training(self):
        # Start training mode.
        self.current_state = self.TRAIN

    def start_idle(self):
        # Start idle mode.
        self.current_state = self.IDLE
    
    def start_testing(self):
        # Start testing mode
        self.current_state = self.TEST
        
    # ---------------------------------------------------------------------- #
    # Message Processing     
    
    def process_message(self, message):
        # Process incoming message and perform any actions in response.
        # -------------------------------------------------------------
        # Load message into a dictionary.
        message = json.loads(message)
        
        # Send confirmation to Slack that the message was received.
        self.send_message_confirmation(message)
        
        # Perform actions
        if 'payload' in message:
            channel  = message['payload']['event']['channel']
            msg_text = message['payload']['event']['text'   ]
            
            # Clean message 
            msg_text = self.remove_jarvis_tag(msg_text)
            msg_text = self.remove_punctuation(msg_text)
            
            # Make sure message isn't from Jarvis.
            if 'bot_profile' not in message['payload']['event']:
                self.display_message(msg_text)
                self.interact(msg_text, channel)
                
    def remove_jarvis_tag(self, message):
        # Remove Jarvis user ID from message
        id_start_index = message.find('<@')
        id_end_index   = message.find('>', id_start_index)
        id_full_string = message[id_start_index:id_end_index+1]
        message        = message.replace(id_full_string, '').lstrip(' ')
            
        return message
    
    def remove_punctuation(self, message):
        # Remove punctuation from message
        removePunc = str.maketrans({punc: None for punc in string.punctuation})
        message    = message.translate(removePunc)
        
        return message
    
    def send_message_confirmation(self, message):
        # Send a response message to Slack to confirm that the incoming 
        # message was received.
        if 'envelope_id' in message:
            response = {'envelope_id': message['envelope_id']}
            self.connection.send(str.encode(json.dumps(response)))
    
    def display_message(self, message):
        # Display received message from Slack.
        if self.display_mode:
            print('--------------------------')
            print('New Message:')
            print(message)
            print('--------------------------')
            
    def post_message(self, message, channel):
        # Send messages back to the Slack repo
        # ------------------------------------
        # Message payload
        message = {'channel': channel,
                   'text'   : message}
        
        # Send the message to the Slack workspace.
        requests.post(self.POST_MESSAGE_URL, data=message, headers=self.POST_AUTH)
        
    def interact(self, message, channel):
        # Interact with the Slack Workspace
        if 'training time' in message.lower():
            self.start_action()
            self.post_message("OK, I'm ready for training. What NAME should this ACTION be?", channel)
        elif 'testing time' in message.lower():
            self.start_testing()
            self.post_message("I'm training my brain with the data you've already given me...", channel)
            ##############################################
            # ADD THE RE-TRAIN JARVIS FUNCTIONALITY HERE #
            ##############################################
            self.update_brain()
            self.post_message("OK, I'm ready for testing. Write me something and I'll try to figure it out.", channel)
        elif 'done' in message.lower():
            self.current_action = ''
            if self.current_state == self.TRAIN:
                self.start_idle()
                self.post_message("OK, I'm finished training.", channel)
            elif self.current_state == self.TEST:
                self.start_idle()
                self.post_message("OK, I'm finished testing.", channel)
            else:
                self.start_idle()
        elif self.current_state == self.ACTION:
            self.start_training()
            self.current_action = message.upper()
            self.post_message("OK, let's call this action `{}`. Now give me some training text!".format(self.current_action), channel)
        elif self.current_state == self.TRAIN:
            self.database.store_training_data(message.lower(), self.current_action)
            self.post_message("OK, I've got it! What else?", channel)
        elif self.current_state == self.TEST:
            self.post_message("OK, I think the action you mean is `{}`...".format(self.BRAIN.predict([message.lower()])[0].upper()), channel)
            self.post_message("Write me something else and I'll try to figure it out.", channel)
            
    # ---------------------------------------------------------------------- #
    # Jarvis Brain Actions
    
    def update_brain(self):
        df = pd.DataFrame(self.database.retrieve_data())
        X = df[0]
        Y = df[1]
        
        # Instanatiates a CountVectorizer() object to run frequencies for every unique word in X and put
        # those frequencies into one 1868 x 952 word frequency matrix where each line is associated with one
        # TXT and can map to the corresponding entry in Y, which is the label
        
        vectorizer = CountVectorizer() 
        
        # Split data into training and testing subsets
        
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y)
        
        # Fitting Vectorizer to training and testing data, then sending to an array 
        
        trainX = vectorizer.fit_transform(X_train)
        trainX_array = trainX.toarray()
        
        # Updates Jarvis's brain
        
        self.BRAIN.fit(trainX_array, Y_train)
    
    # ---------------------------------------------------------------------- #
    # Websocket Events

    def on_message(self, message):
        # Called when a message is received in the websocket connection. 
        # --------------------------------------------------------------
        # Added threading to hopefully help with messages being delayed
        # due to having to wait for previous messages to be processed.
        thread.start_new_thread(self.process_message, (message,))
        
    def on_error(self, error):
        # Called when an error occurs in the websocket connection. This can
        # be used for debugging purposes. To enable/disable error messages:
        #   1) True  -> Enable
        #   2) False -> Disable
        if False:
            print("ERROR ->", error)
            
    def on_open(self):
        # Called when websocket connection is first established.
        print("------------------------------------------------------")
        print("| Connection Established - Jarvis is in the houuuse! |")
        print("------------------------------------------------------")

    def on_close(self):
        # Called when websocket connection is closed.
        print("------------------------------------------------------")
        print("| Jarvis disconnected - See ya later alligator :)    |") 
        print("------------------------------------------------------")
        self.database.print_training_data()
        self.database.close_connection()

    
class Database:
    """Class for interacting with Jarvis' database."""
    def __init__(self):
        # Open connection to database on startup.
        self.open_connection()
    
    def open_connection(self):
        # Set up the database connection. If the database or table
        # in the database don't exist, create them. 
        self.conn = sqlite3.connect('jarvis.db', check_same_thread=False)
        self.curr = self.conn.cursor()
        
        try:
            self.curr.execute("CREATE TABLE training_data (txt TEXT, action TEXT)")
        except sqlite3.OperationalError:
            print("TABLE FOUND")
    
    def close_connection(self):
        # This should be called when Jarvis is finished running to close 
        # the connection to the database.
        self.conn.close()

    def store_training_data(self, msg_txt, action):
        # This will store the message text and action (training data) 
        # into the database.
        self.curr.execute("INSERT INTO training_data VALUES (?, ?)", (msg_txt, action))
        self.conn.commit()
    
    def clear_table(self):
        self.curr.execute("DELETE FROM training_data")
        self.conn.commit()
        
    def add_batch_data(self, df):
        # This will add large amounts of data to the training data at once.
        # Data must be a pandas dataframe.
        df.to_sql(name='training_data',con=self.conn,if_exists='append',index=False)
        self.conn.commit()
        print("{} rows inserted into training data".format(df.size/2))
    
    def retrieve_data(self):
        returned_data = []
        self.curr.execute("SELECT * FROM training_data")
        for row in self.curr.fetchall():
            returned_data.append(row)
        return returned_data
    
    def print_training_data(self):
        # This will print the message text and action (training data)
        # currently in the database, with message text of common actions
        # grouped together.
        self.curr.execute("SELECT * FROM training_data ORDER BY action")
        for row in self.curr.fetchall():
            print(row)


# -------------------------------------------------------------------- #
# This is the main section which is run when the script is run by      #
# calling: "python jarvis.py." All main code will be written here,     #
# making use of the above definitions to initialize and run Jarvis.    #
# -------------------------------------------------------------------- #
if __name__ == '__main__':
    # Authorization headers to allow Jarvis to connect to the workspace. 
    WORKSPACE_AUTH = {'Content-type' : "application/x-www-form-urlencoded",
                      'Authorization': "Bearer " + APP_TOKEN}
    
    # Authorization headers to allow Jarvis to post messages to the workspace.
    POST_AUTH = {'Content-type' : "application/x-www-form-urlencoded",
                 'Authorization': "Bearer " + API_TOKEN}
  
    # Get workspace url from the Slack API that is compatible with the
    # websocket protocol using the workspace authorization headers.
    SLACK_URL     = "https://slack.com/api/apps.connections.open"
    WORKSPACE_URL = requests.post(SLACK_URL, headers=WORKSPACE_AUTH).json()['url']

    # Initiate Jarvis
    jarvis = Jarvis(WORKSPACE_URL, WORKSPACE_AUTH, POST_AUTH, 
                    debug_mode   = False, 
                    display_mode = True)