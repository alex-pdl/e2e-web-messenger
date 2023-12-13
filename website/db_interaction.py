import sqlite3
import hashlib
import datetime

class user_db_interaction:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    #function hashes the password attribute of the class user and returns the hash password
    def hash(self):
        h = hashlib.new('SHA256')
        h.update(self.password.encode())
        return h.hexdigest()
    
    def register(self):
        #if username is not in use
        if self.username_check() == False:
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()
            sql = """
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY NOT NULL,
                username TEXT,
                password TEXT
                )
                """
            #inserting username & password hash into the database
            info = [
                    (self.username, self.hash())
            ]
            cursor.executemany("INSERT INTO users (username, password) VALUES (?,?)", info)
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
        if self.hash() == hashed_pass:
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
    
def chat_creation(user_1, user_2):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    #checks if user tried to chat with themselves
    if user_1 != user_2:
        #checks if user_2 exists
        get_usernames = """SELECT username FROM users"""
        cursor.execute(get_usernames)
        raw_existing_users = cursor.fetchall()
        existing_users = []
    
        for i in raw_existing_users:
            existing_users.append(str(i).strip("[(', )]"))

        if user_2 in existing_users:
            
            list_of_names = chats_retrieval(user_1)
            
            if user_1 not in list_of_names and user_2 not in list_of_names:
                #adds the user and the user they choose to chat with to the 'chats' database
                create_chats_table = """
                    CREATE TABLE IF NOT EXISTS chats (
                    chatid INTEGER PRIMARY KEY NOT NULL,
                    username_1 INTEGER,
                    username_2 INTEGER
                ) """
                cursor.execute(create_chats_table)
                values = [
                    user_1,user_2
                ]
                cursor.execute("INSERT INTO chats (username_1,username_2) VALUES(?,?)", (values))
                connection.commit()
                connection.close()
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

def create_message(sender,chat_id,contents):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()

    create_table = f"""
            CREATE TABLE IF NOT EXISTS message (
            msg_id INTEGER PRIMARY KEY NOT NULL,
            sender TEXT,
            chat_id INTEGER,
            contents TEXT,
            timestamp DATETIME
        ) """
    cursor.execute(create_table)

    x = datetime.datetime.now() #get timestamp of message
    
    formatted_time = x.strftime("%Y-%m-%d %H:%M:%S")  # Format to exclude microseconds

    cursor.execute(
    "INSERT INTO message (sender, chat_id, contents, timestamp) VALUES (?, ?, ?, ?)",
    (sender, chat_id, contents, formatted_time)
)

    print(formatted_time)
    connection.commit()
    connection.close()

def retrieve_messages(chat_id):
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT timestamp,sender,contents FROM message WHERE chat_id = ? ORDER BY timestamp", (chat_id,))
        raw_messages = cursor.fetchall()
        
        formatted_messages = []
        for i in raw_messages:  #removes "[(', )]" from every message and appends it to a new list
            formatted_messages.append(str(i).strip("[(', )]")) 

        return formatted_messages
    except:
        formatted_messages = ["You don't have any messages with this person, enter a message in the box to start!"]
        return formatted_messages

#function which checks if string has any special characters and if so, returns them
def special_char_checker(string):
    #users can only make usernames consisting of these characters.
    allowed_characters =  ["a","b","c","d","e","f"
                           ,"g","h","i","j","k","l"
                           ,"m","n","o","p","q","r"
                           ,"s","t","u","v","w","x"
                           ,"y","z","0","1","2","3",
                           "4","5","6","7","8","9","10"]
    for i in string:
        if i not in allowed_characters:
            return i