import sqlite3
import datetime

class user_db_interaction:
    def __init__(self, username, password, public_key="public_key", private_key="priavate_key"):
        self.username = username
        self.password = password
        self.public_key = public_key
        self.private_key = private_key

    def register(self):        
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        #inserting username & password hash into the database
        info = [
                (self.username, self.password,self.public_key,self.private_key)
        ]
        cursor.executemany("INSERT INTO users (username,password,public_key,private_key) VALUES (?,?,?,?)", info)
        #committing changes & closing the connection
        connection.commit()
        connection.close()

    def password_check(self):
        connection = sqlite3.connect('users.db')  
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = (?)", (self.username,))
        #when the pass hash is fetched, it is in the form of a list and has many characters that aren't part of the hash
        hashed_pass = str(cursor.fetchall()).strip("[(', )]")
        connection.commit()
        connection.close()

        if self.password == hashed_pass:
            return True
        else:
            return False

    def retrieve_user_id(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = (?)", (self.username,))
        retrieved_id = str(cursor.fetchall()).strip("[(', )]")
        connection.commit()
        connection.close()
        return retrieved_id    

    def retrieve_privatekey(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT private_key FROM users WHERE username = ?", (self.username,))
        result = cursor.fetchone()
        encrypted_private_key = result[0]
        connection.close()
        return encrypted_private_key
    
#checks if the username is not in use
def username_check(username):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users WHERE username = (?)", (username,))
    fetched_username = str(cursor.fetchall()).strip("[(', )]")
    if username == fetched_username:
        return True
    else:
        return False
    
def chat_creation(user_1, user_2):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    #checks if user tried to chat with themselves
    if user_1 != user_2:
        #checks if user_2 exists
        cursor.execute("SELECT username FROM users")
        raw_existing_users = cursor.fetchall()
        existing_users = []
        #formats the name of the users by removing everything but the username
        for i in raw_existing_users:
            existing_users.append(str(i).strip("[(', )]"))
        #checks if user 2 exists
        if user_2 in existing_users:
            if retrieve_chatid(user_1,user_2) == "None":  #Checks if user already has chat with this person
                #adds the user and the person they choose to chat with to the 'chats' database
                values = [user_1,user_2]
                cursor.execute("INSERT INTO chats (username_1,username_2) VALUES(?,?)", (values))
                connection.commit()
                connection.close()
                return "Success"
            else:
                return("Error_1")
        else:
            return("Error_2")
    else:
        return("Error_3")

def chats_retrieval(username):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
        
    cursor.execute("SELECT username_2 from chats WHERE username_1 = (?)", (username,))
    get_names = cursor.fetchall()

    cursor.execute("SELECT username_1 from chats WHERE username_2 = (?)", (username,))
    get_names_2 = cursor.fetchall()

    chat_names = []
    for i in get_names_2:
        chat_names.append(str(i).strip("[(', )]"))
    for i in get_names:
        chat_names.append(str(i).strip("[(', )]"))
    return chat_names

def retrieve_chatid(username_1,username_2):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute(f"SELECT chatid FROM chats WHERE (username_1 = '{username_1}' AND username_2 = '{username_2}') OR (username_1 = '{username_2}' AND username_2 = '{username_1}')")
    chat_id = str(cursor.fetchone()).strip("[(', )]")
    connection.close()
    return chat_id   

def create_message(sender,chat_id,contents_1, contents_2):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    x = datetime.datetime.now() #get timestamp of message
    
    formatted_time = x.strftime("%Y-%m-%d %H:%M:%S")  # Format to exclude microseconds

    cursor.execute("INSERT INTO message (sender, chat_id, contents_1, contents_2, timestamp) VALUES (?, ?, ?, ?, ?)",
    (sender, chat_id, contents_1, contents_2, formatted_time))

    connection.commit()
    connection.close()

def retrieve_messages(chat_id,which_contents):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT timestamp,sender FROM message WHERE chat_id = ? ORDER BY timestamp", (chat_id,))
        message_info = cursor.fetchall()
        cursor.execute(f"SELECT {which_contents} FROM message WHERE chat_id = ? ORDER BY timestamp", (chat_id,))
        contents = cursor.fetchall()
        return message_info,contents
    except:
        pass

def retrieve_public_key(username):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute("SELECT public_key FROM users WHERE username = (?)", (username,))
    public_key = str(cursor.fetchone()).strip("[(', )]")
    connection.close()
    return public_key

def determine_column(username,chatid):
    # Determine which column (contents_1 or contents_2) the sender is a part of
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    # If the user's username is stored in username_1, their message contents is stored in conents_1 and vica versa
    cursor.execute("SELECT username_1 FROM chats WHERE chatid = (?)", (chatid,))
    username_1 = str(cursor.fetchone()).strip("[(', )]")
    connection.close()
    if username == username_1:
        return "contents_1"
    else:
        return "contents_2"

def create_database():
    #creates database with all tables if it doesn't already exist
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    create_users_table = """
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY NOT NULL,
                username TEXT,
                password TEXT,
                private_key TEXT,
                public_key TEXT
            ) """
    cursor.execute(create_users_table)
    create_chats_table = """
                CREATE TABLE IF NOT EXISTS chats (
                chatid INTEGER PRIMARY KEY NOT NULL,
                username_1 TEXT,
                username_2 TEXT
            ) """
    cursor.execute(create_chats_table)
    create_message_table = """
        CREATE TABLE IF NOT EXISTS message (
        msg_id INTEGER PRIMARY KEY NOT NULL,
        sender TEXT,
        chat_id INTEGER,
        contents_1 TEXT,
        contents_2 TEXT,
        timestamp DATETIME
    ) """
    cursor.execute(create_message_table)
    connection.commit()
    connection.close()

def statistics(): # Gathers general usage statistics and returns them.
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    # Enclose sub queries in brackets to distinguish between them and the main query
    gather_statistics = """
        SELECT 
            (SELECT COUNT(*) FROM users) AS total_users,
            (SELECT MAX(chatid) FROM chats) AS max_chat_id,
            COUNT(*) AS total_messages
        FROM 
            message;
    """
    cursor.execute(gather_statistics)
    result = cursor.fetchone()
    connection.commit()
    connection.close()
    
    total_users, total_chats, total_messages = result
    if total_chats is None:
        total_chats = 0
# Returns total users, the amount of chats and the total amount of messages in that order
    return total_users,total_chats,total_messages 