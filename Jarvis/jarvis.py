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
import random
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
        self.CHAT   = 4  # Jarvis generates response to input text
        
        #Recovery Coach Jarvis Conversations TOPICS
        self.TOPICS = {'RELAPSE': ['It sounds like things are tough and you might be thinking about using. Here is where you can get help immediately: https://www.uvmhealth.org/medcenter/conditions-and-treatments/substance-abuse?utm_term=Day_One_Substance_Abuse. Call 911 if you feel you need immediate medical support.', 
                                   'Relapse is part of recovery - there is no reason to feel ashamed. Every day is another day to begin again.',
                                   'If you need something other than detox, try calling the National Substance Abuse and Mental Health Hotline for free, confidential help: 1-800-662-4357.',
                                   'Here are your local meetings, too. Don\'t be afraid to be the new guy who asks for help. https://findrecovery.com',
                                   'You may have made a mistake, but you are showing great strength in reaching out for help. Recovery is about progress, not perfection.',
                                   'It sounds like you need support. If you have a sponsor, reach out - that\'s what they\'re there for!'], 
                       'MENTAL HEALTH': ['It sounds like things are tough and you might need a helping hand. Here is where you can get help immediately through First Call: 802-488-7777. Call 911 if you are having thoughts of suicide or need immediate medical support',
                                      'Taking care of yourself is your number one priority. Make a list of people you can reach out to and start making the calls.',
                                      'Your mind, body, and soul are all connected. If you feel like something\'s not right, maybe you need to up your wellness routine.',
                                      'Therapy is an important part of self-care. Getting help is a sign of strength.', 
                                      'NAMI can help you connect with support and resources if you often feel this way. Call their helpline at 1-800-950-NAMI.',
                                      'Remember what to do if you\'re feeling Hungry, Angry, Lonely, or Tired. HALT and take care of that need.'], 
                       'INSPIRATION': ['There is hope in recovery.', 'A song to inspire you - you can do this! https://www.youtube.com/watch?v=_-D7hBRCF_Q',
                                       '\'When I am willing to do the right thing I am rewarded with an inner peace no amount of liquor could ever provide.\'',
                                       '\'Those events that once made me feel ashamed and disgraced now allow me to share with others how to become a useful member of the human race.\'',
                                       '\'And acceptance is the answer to all my problems today.\'',
                                       '\'Those events that once made me feel ashamed and disgraced now allow me to share with others how to become a useful member of the human race.\'',
                                       'There is inspiration all around you! For ideas on where to look, check out: https://www.hcrcenters.com/blog/the-power-of-inspiration-during-recovery/'], 
                       'MEETINGS': ['It sounds like you might be looking for a local meeting. Here is where you can search for a meeting near you: https://findrecovery.com',
                                    'Service is an important part of your recovery and giving back to your local community. Here is more information on how to help conduct a meeting: http://www.aanapa.org/wp-content/uploads/SuggestedMeetingFormat-1.pdf',
                                    'Whether you are a newcomer, have 20 years sober, or you are thinking of using, you are always welcome at your local meeting.',
                                    'Did you know about the wide variety of meetings there are to help address different types of addiction? For example, check out Workaholics Anonymous here: https://workaholics-anonymous.org/10-literature/34-twelve-steps',
                                    'It works if you work it, so work it - you\'re worth it! Keep coming back!',
                                    'If your local meeting doesn\'t work for your schedule, consider an online meeting.'], 
                       'DISTRACTION': ['Need a distraction? I\'m here to help!',
                                    'Check it out! Adorable BUNNIES! Click \'Show me another photo!\' for hours of happy bunny time. <3 https://rabbit.org/fun/net-bunnies.html',
                                    'Watch this crazy amazing (and kinda creepy) army ant documentary!! https://www.youtube.com/watch?v=p16g5IVCdeE',
                                    'Remember FeministRyanGosling? You know you do. https://feministryangosling.tumblr.com/post/12016363872',
                                    'Check out some terrible real estate agent photos: https://terriblerealestateagentphotos.com/',
                                    'What\'s in the stars for you? https://www.horoscope.com/us/index.aspx']}
        
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
        self.RC_BRAIN = pickle.load(open("Classifiers/jarvis_comp3_REDPIRANHA.pkl", 'rb'))
        
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
        
    def start_chatting(self):
        self.current_state = self.CHAT
        
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

    def recovery_chat(self, message, channel):
        result = self.RC_BRAIN.predict([message])
        for i in self.TOPICS.keys():
            if result == i:
                self.post_message(self.TOPICS[i][0], channel)
                response_choice = random.randint(1, 4)
                self.post_message(self.TOPICS[i][response_choice], channel)
        self.post_message('I hope that helped. Do you need more support?', channel)

    def interact(self, message, channel):
        # Interact with the Slack Workspace
        if 'training time' in message.lower():
            self.start_action()
            self.post_message("OK, I'm ready for training. What NAME should this ACTION be?", channel)
        elif 'testing time' in message.lower():
            self.start_testing()
            self.post_message("I'm training my brain with the data you've already given me...", channel)
            self.update_brain()
            self.post_message("OK, I'm ready for testing. Write me something and I'll try to figure it out.", channel)
        elif 'hey coach' in message.lower():
            self.start_chatting()
            self.post_message("Recovery and a better life is possible. \nI'm here for you. \nTell me what's going on for you right now.", channel)
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
        elif self.current_state == self.CHAT:
            if message.lower() == 'done':
                self.start_idle()
                self.post_message('Goodbye! Take good care of yourself.', channel)
            elif message.lower() == 'help':
                self.post_message("""I\'m here to help support your recovery. Let me know
                                  what I can do to help. For example, you could let me know. 
                                  if you're thinking of using or want to know where you can 
                                  find a meeting. \nType \'done\' if you are all done!""", channel)
            elif 'yes' in message.lower():
                self.post_message('I\'m here for you. Tell me more about what\'s going on.', channel)
            elif 'no' in message.lower():
                self.post_message("Glad I was able to help. Reach out any time! I'm always here for you.", channel)
                self.current_state = self.IDLE
            else:
                self.recovery_chat(message, channel)    
     
    # ---------------------------------------------------------------------- #
    # Jarvis Brain Actions
    
    def update_brain(self):
        df = pd.DataFrame(self.database.retrieve_data())
        X = df[0]
        Y = df[1]
        
        # Instanatiates a CountVectorizer() object to run frequencies for every unique word in X
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
        self.curr.commit()
        
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