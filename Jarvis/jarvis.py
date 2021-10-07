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
import requests
import websocket
try:
    import thread 
except ImportError:
    import _thread as thread

# Slack connection token
from botsettings import API_TOKEN
from botsettings import APP_TOKEN


# ----------------------------------------------------------------------
# NOTE: ALL CODE BELOW THIS POINT IS A ROUGH DRAFT SKELETON/OUTLINE AND
# IS SUBJECT TO CHANGE. THIS IS JUST TO PROVIDE A STARTING POINT FOR OUR
# DESIGN.
# ----------------------------------------------------------------------
class Jarvis:
    """Class that will contain all logic for Jarvis."""
    def __init__(self):
        # Jarvis states
        self.IDLE  = 'Idle'
        self.TRAIN = 'Training'
        
        # Jarvis settings
        self.currentState = self.IDLE      # Starting state for Jarvis
        self.database     = Database()     # Database containing training data

    def start_training(self):
        # Start training mode.
        self.currentState = self.TRAIN

    def stop_training(self):
        # Stop training and switch to idle mode.
        self.currentState = self.IDLE

    def on_message(self, connection, msg):
        pass

    def on_error(self, connection, error):
        pass

    def on_close(self, connection, close_status_code, close_msg):
        pass

    def on_open(self, connection):
        print("Connection Established - Jarvis is here!")
        
    def __del__(self):
        # Called when Jarvis is finished.
        self.database.close_connection()
    
    
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
            print('TABLE FOUND')
    
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
    
# ==================================================================== #

# This is run when the script is run. So for example, calling: 
# python jarvis.py will execute this. This is where we will put all
# the main code. Functions will be defined above and called here.
if __name__ == '__main__':
    # Slack workspace authentication headers. This allows Jarvis to have 
    # access to the Slack workspace
    authentication = {'Content-type' : "application/x-www-form-urlencoded",
                      'Authorization': "Bearer " + APP_TOKEN}
  
    # Request websocket url for the Slack Workspace using the authentication
    # headers.
    SLACK_API_URL = 'https://slack.com/api/apps.connections.open'
    WORKSPACE_URL = requests.post(SLACK_API_URL, headers=authentication).json()["url"]

    # Initiate Jarvis
    jarvis = Jarvis()

    # Enable/Disable debugging messages for websocket:
    #   1) Enable  -> True
    #   2) Disable -> False
    websocket.enableTrace(False)

    # Start websocket connection, connecting Jarvis to the Slack workspace.
    connection = websocket.WebSocketApp(WORKSPACE_URL,
                                         on_message = jarvis.on_message,
                                         on_error   = jarvis.on_error,
                                         on_open    = jarvis.on_open,
                                         on_close   = jarvis.on_close)

    # Run Jarvis
    connection.run_forever()