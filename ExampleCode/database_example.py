"""
    Example code for working with sqlit3 to manage the database.

    This file is mostly for Ted but if anyone else needs an example for 
    understanding the database code, this is a good resource.

    Here is the official Python guide as well:
        https://docs.python.org/3/library/sqlite3.html

    You can also look up sqlit3 tutorials and tons will come up (such as
    the one from tutorialspoint).
"""
# This is how you import sqlit3
import sqlite3

# This is the relative filename to the database. Relative file name
# means the path from the current directory. Don't put something like:
# C:\\Users\\blahblahblah\\..., that would be an absolute path.
database_file = "DB_FILENAME.db"

# This command creates the CONNECTED_DATABASE_OBJECT_NAME object from
# the README_FOR_TED file. This object is used to interact with the 
# database. 
conn = sqlite3.connect(database_file)

# This creates what's called a cursor object which essentially points 
# to the database and allows you to execute SQL commands on it. This is
# the "wrapper" for the Python code to interact with SQLite (the database
# management system).
c = conn.cursor()

# These are example variables that can be used in the safe insertion
# logic below.
msg_txt = "What time is it?"
action  = "TIME"

# This command is how you execute SQL commands in sqlit3. The example 
# command here is inserting data into a table in the database called
# training_data in the columns "txt" and "action". The (?, ?) part 
# might look a little scary but all it's actually doing is safely
# inserting whatever is passed into the second argument: a tuple -> 
# (msg_txt, action,). This helps to avoid things like SQL injection and
# accidentally altering the wrong things in the database. Notice how the
# tuple has a comma at the end. This is required because otherwise, 
# Python would treat it as an operation grouping; so if it were instead
# (msg_txt, action) without the comma at the end, you would get an error 
# that can be tricky to spot. 
c.execute("INSERT INTO training_data (txt,action) VALUES (?, ?)", (msg_txt, action,))

# This command "commits" the changes and makes them permanent.
conn.commit()