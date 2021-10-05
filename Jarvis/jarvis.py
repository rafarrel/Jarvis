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
import websocket
try:
    import thread 
except ImportError:
    import _thread as thread

# Slack connection token
from botsettings import API_TOKEN


class Jarvis:
    def __init__(self):
        self.currentState = 'Idle'

    def start_training(self):
        self.currentState = 'Training'

    def stop_training(self):
        self.currentState = 'Idle'

    def create_database(self):
        pass

    def store_training_data(self, msg_txt, action):
        pass

    def get_stored_data(self):
        pass

    def on_message(connection, msg):
        pass

    def on_error(connection, error):
        pass

    def on_close(connection):
        pass

    def on_open(connection):
        pass

# ==================================================================== #

# This is run when the script is run. So for example, calling: 
# python jarvis.py will execute this. This is where we will call all
# the main code. Functions will be defined above and called here.
if __name__ == '__main__':
    # Initiate Jarvis
    jarvis = Jarvis()

    # Enable/Disable debugging messages for websocket:
    #   1) Enable  -> True
    #   2) Disable -> False
    websocket.enableTrace(True)

    # Start websocket connection
    connection = websocket.WebSocketApp('URL_PLACEHOLDER',
                                         on_message = jarvis.on_message,
                                         on_error   = jarvis.on_error,
                                         on_close   = jarvis.on_close)

    # Set initial behavior when connection is established
    connection.on_open = jarvis.on_open

    # Run Jarvis
    connection.run_forever()