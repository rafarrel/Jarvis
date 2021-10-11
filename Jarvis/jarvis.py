"""
    Jarvis - A data-collecting chatbot for Slack
    Current Release: 1.0

    Jarvis is a chatbot designed for seamless integration with Slack 
    workspaces. It will collect data from users and train itself 
    to interact within the workspace.

    ------------------------------------------------------------------
    Release notes for v.1.0:
        - IN PROGRESS

    ------------------------------------------------------------------
    This project is released as open-source under the permissive MIT 
    license with the approval of its sponsor, Bagrow Industries.
"""
# Database management
import sqlite3

# Slack interaction
import json
import requests
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
# and the actual websocket connection will be established below in the # 
# main section.                                                        #
# -------------------------------------------------------------------- #
class Jarvis:
    """Class that will contain all logic for Jarvis."""
    def __init__(self):
        # Jarvis states
        self.IDLE  = 0
        self.TRAIN = 1
        
        # Jarvis settings
        self.currentState = self.IDLE      # Starting state for Jarvis
        self.database     = Database()     # Database containing training data
        
    def __del__(self):
        # Clean up when Jarvis is finished.
        self.database.close_connection()

    # ---------------------------------------------------------------------- #

    def start_training(self):
        # Start training mode.
        self.currentState = self.TRAIN

    def stop_training(self):
        # Stop training and switch to idle mode.
        self.currentState = self.IDLE
        
    # ---------------------------------------------------------------------- #
            
    def display_message(self, message):
        # Display received message from Slack.
        if 'payload' in message:
            print('--------------------------')
            print('New Message:')
            print(message['payload']['event']['text'])
            print('--------------------------')
        
    def send_message_confirmation(self, message):
        # Send a response message to Slack to confirm that the incoming
        # message was received.
        if 'envelope_id' in message:
            response = {'envelope_id': message['envelope_id']}
            self.connection.send(str.encode(json.dumps(response)))
            
    def message_to_slack(self, text):
        SLACK_URL = "https://slack.com/api/chat.postMessage"
        auth = {'Content-type' : "application/json",
                'Authorization': "Bearer " + APP_TOKEN}
        WORK_URL = requests.post(SLACK_URL, headers=auth).json()['url']
        data = {'text': text}
        response = requests.post(WORK_URL, json.dumps(data))
        if response.status_code != 200:
            raise ValueError('error')
        
    def process_message(self, message):
        if message.lower() == "hi":
            print("Hi there!")
            self.message_to_slack("Hi there!")
        if message.lower() == "training time":
            #self.start_training()
            print("OK, I'm ready for training.  What NAME should this ACTION be?")
            self.message_to_slack("OK, I'm ready for training.  What NAME should this ACTION be?")
        if message.lower() == "done":
            #self.stop_training()
            print("OK, I'm finished training")
            self.message_to_slack("OK, I'm finished training")

    # ---------------------------------------------------------------------- #

    def on_message(self, message, *args):
        # Called when a message is received in the websocket connection. 
        # --------------------------------------------------------------
        # Load message into a dictionary.
        message = json.loads(message)
        
        # Perform processing.
        self.display_message(message)
        self.send_message_confirmation(connection, message)
    
    def on_error(self, connection, error):
        # Called when an error occurs in the websocket connection. This can
        # be used for debugging purposes. To enable/disable error messages:
        #   1) True  -> Enable
        #   2) False -> Disable
        if False:
            print("ERROR ->", error)
            
    def on_open(self, *args):
        # Called when websocket connection is first established.
        print("------------------------------------------------------")
        print("| Connection Established - Jarvis is in the houuuse! |")
        print("------------------------------------------------------")

    def on_close(self, *args):
        # Called when websocket connection is closed.
        print("------------------------------------------------------")
        print("| Jarvis disconnected - See ya later alligator :)    |") 
        print("------------------------------------------------------")
 
    
class Database:
    """Class for interacting with Jarvis' database."""
    def __init__(self):
        # Open connection to database on startup.
        self.open_connection()
    
    def open_connection(self):
        # Set up the database connection. If the database or table
        # in the database don't exist, create them. 
        self.conn = sqlite3.connect('jarvis.db')
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
    
    def print_training_data(self):
        # This will print the message text and action (training data)
        # currently in the database, with message text of common actions
        # grouped together.
        self.curr.execute("SELECT * FROM training_data ORDER BY action")
        for row in self.curr.fetchall():
            print(row)


# -------------------------------------------------------------------- #
# This is the main section which is run when the script is run by      #
# calling: "python jarvis.py." All main code (initializing Jarvis,     #
# establishing the websocket connection, etc.) will be written here,   #
# making use of the above definitions.                                 #
# -------------------------------------------------------------------- #
if __name__ == '__main__':
    # Authorization headers to allow Jarvis to connect to the workspace. 
    authorization = {'Content-type' : "application/x-www-form-urlencoded",
                     'Authorization': "Bearer " + APP_TOKEN}
  
    # Get workspace url from the Slack API that is compatible with the
    # websocket protocol using the authentication headers.
    SLACK_API_URL = "https://slack.com/api/apps.connections.open"
    WORKSPACE_URL = requests.post(SLACK_API_URL, headers=authorization).json()['url']

    # Initiate Jarvis
    jarvis = Jarvis()

    # Enable/Disable debugging messages for websocket:
    #   1) Enable  -> True
    #   2) Disable -> False
    websocket.enableTrace(False)

    # Start websocket to connect Jarvis to the Slack workspace.
    connection = websocket.WebSocketApp(WORKSPACE_URL,
                                         on_message = jarvis.on_message,
                                         on_error   = jarvis.on_error,
                                         on_open    = jarvis.on_open,
                                         on_close   = jarvis.on_close)

    # Run Jarvis
    connection.run_forever()