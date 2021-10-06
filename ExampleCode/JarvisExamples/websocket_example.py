# https://github.com/websocket-client/websocket-client

import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time


# This will be called every time a message is received so all
# code inside can be used to perform an action for that message. 
def on_message(ws, message):
    message = json.loads(message)
    envelope_id = message['envelope_id']
    resp = {'envelope_id': envelope_id }
    ws.send(str.encode(json.dumps(resp )))
    print(message)

# This will be called whenever there is an error and can be used for
# debugging.
def on_error(ws, error):
    print(error)

# This will be called when the connection is closed and can be used
# to perform any finishing actions or cleanup if necessary.
def on_close(ws):
    print("### closed ###")

# This will be called when a connection is established and can be used
# to perform any initial actions or setup if necessary.
def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    # This enables error debugging messages for the websocket
    websocket.enableTrace(True)
    
    # This creates the websocket object and establishes a connection to
    # the URL passed to it.
    ws = websocket.WebSocketApp('PLACEHOLDER_URL',
                              on_message = on_message,
                              on_error = on_error,
                              on_open  = on_open,
                              on_close = on_close)
    
    # This runs the websocket indefinitely so that it can keep performing 
    # actions on established connections.
    ws.run_forever()

