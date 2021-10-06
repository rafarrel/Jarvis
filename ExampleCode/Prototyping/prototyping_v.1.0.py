"""
    Jarvis - A data-collecting chatbot for Slack 
    v.1.0 protoype
    
    All prototyping/testing code for Jarvis should go in this file
    before implementing into the main jarvis.py codebase. This file is
    just to help us test out certain things before jumping right in to 
    development.
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