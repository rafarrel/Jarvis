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

import json

# Slack interaction
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

    def start_training(self):
        # Start training mode.
        self.currentState = self.TRAIN

    def stop_training(self):
        # Stop training and switch to idle mode.
        self.currentState = self.IDLE

    def on_message(self, connection, message):
        # Called when a message is received in the websocket connection. 
        # Prepare response for received message to confirm that it
        # was received.
        message     = json.loads(message)
        envelope_id = message['envelope_id']
        response    = {'envelope_id': envelope_id}
        
        # Send response to Slack
        connection.send(str.encode(json.dumps(response)))

    def on_error(self, connection, error):
        # Called when an error occurs in the websocket connection.
        pass

    def on_close(self, connection, close_status_code, close_msg):
        # Called when websocket connection is closed.
        pass

    def on_open(self, connection):
        # Called when websocket connection is first established.
        print("Connection Established - Jarvis has arrived!")
    
    
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