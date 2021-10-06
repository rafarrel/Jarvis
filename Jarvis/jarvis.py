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
from sqlite3.dbapi2 import connect

# Slack interaction
import requests
import websocket
try:
    import thread 
except ImportError:
    import _thread as thread

# Slack connection token
from botsettings import API_TOKEN


# ----------------------------------------------------------------------
# NOTE: ALL CODE BELOW THIS POINT IS A ROUGH DRAFT SKELETON/OUTLINE AND
# IS SUBJECT TO CHANGE. THIS IS JUST TO PROVIDE A STARTING POINT FOR OUR
# DESIGN.
# ----------------------------------------------------------------------
class Jarvis:
    """Class that will contain all logic for Jarvis."""
    def __init__(self):
        self.currentState = 'Idle'

    def start_training(self):
        self.currentState = 'Training'

    def stop_training(self):
        self.currentState = 'Idle'

    def on_message(connection, msg):
        pass

    def on_error(connection, error):
        pass

    def on_close(connection):
        pass

    def on_open(connection):
        pass
    
class Database:
    """Class for interacting with Jarvis' database."""
    def __init__(self):
        # Open connection to database on startup
        self.open_connection()
    
    def open_connection(self):
        # Set up the database connection. If the database or table
        # in the database don't exist, create them. 
        self.conn = sqlite3.connect('jarvis.db')
        self.curr = self.conn.cursor()
        
        try:
            self.curr.execute("INSERT TABLE CREATE COMMAND HERE BECAUSE IM LAZY")
        except sqlite3.OperationalError:
            print('TABLE FOUND')
    
    def close_connection(self):
        # This should be called when Jarvis is finished running to close 
        # the connection to the database.
        self.conn.close()

    def store_training_data(self, msg_txt, action):
        # This will store the message text and action (training data) 
        # into the database.
        pass 
    
# ==================================================================== #

# This is run when the script is run. So for example, calling: 
# python jarvis.py will execute this. This is where we will put all
# the main code. Functions will be defined above and called here.
if __name__ == '__main__':
    # Initiate Jarvis and open the database
    jarvis   = Jarvis()
    database = Database()

    # Enable/Disable debugging messages for websocket:
    #   1) Enable  -> True
    #   2) Disable -> False
    websocket.enableTrace(True)

    # Start websocket connection
    connection = websocket.WebSocketApp('URL_PLACEHOLDER',
                                         on_message = jarvis.on_message,
                                         on_error   = jarvis.on_error,
                                         on_open    = jarvis.on_open,
                                         on_close   = jarvis.on_close)

    # Run Jarvis
    connection.run_forever()
    
    # Close database when done
    database.close_connection()