import sqlite3
import hashlib
import datetime

class user_db_interaction:
    def __init__(self, username, password, public_key="public_key", private_key="priavate_key"):
        self.username = username
        self.password = password
        self.public_key = public_key
        self.private_key = private_key

    def register(self):        
        #if username is not in use
        if self.username_check() == False:
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
        else:
            return False

    def password_check(self):
        connection = sqlite3.connect('users.db')  
        cursor = connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = (?)", (self.username,))
        #when the pass hash is fetched, it is in the form of a list and has many characters that aren't part of the hash
        hashed_pass = str(cursor.fetchall()).strip("[(', )]")
        if self.password == hashed_pass:
            return True
        else:
            return False
        connection.commit()
        connection.close()
        
    #checks if the username is not in use
    def username_check(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM users WHERE username = (?)", (self.username,))
        fetched_username = str(cursor.fetchall()).strip("[(', )]")
        if self.username == fetched_username:
            return True
        else:
            return False
        connection.commit()
        connection.close()

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
        cursor.execute("SELECT private_key FROm users WHERE username = (?)", (self.username,))
        encrypted_private_key = str(cursor.fetchall()).strip("[(', )]")
        connection.commit()
        connection.close()
        return encrypted_private_key
    
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

#function which checks if string has any special characters and if so, returns them
def special_char_checker(string):
    special_characters = []
    #users can only make usernames consisting of these characters.
    allowed_characters =  ["a","b","c","d","e","f"
                           ,"g","h","i","j","k","l"
                           ,"m","n","o","p","q","r"
                           ,"s","t","u","v","w","x"
                           ,"y","z","0","1","2","3",
                           "4","5","6","7","8","9","10"]
    for i in string:
        if i.lower() not in allowed_characters and i.lower() not in special_characters:
            special_characters.append(i)
    return special_characters

def ascii_checker(string): 
    #returns a list of all characters in a string which cannot be represented as an ascii character
    #this is needed to ensure the hashing and encryption algorithms work properly
    list_of_special_chars = []
    for char in string:
        if ord(char) > 128 and char not in list_of_special_chars:
            list_of_special_chars.append(char)
    return list_of_special_chars

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