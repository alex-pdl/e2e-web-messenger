import sqlite3
import hashlib

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
            #checks if user already has a chat with the user_2
            list_of_names = []
            cursor.execute("SELECT username_2 FROM chats WHERE username_1 = (?)", (user_1,))  
            fetched_chats_of_user1 = cursor.fetchall()
            for i in fetched_chats_of_user1:
                list_of_names.append(str(i).strip("[(', )]"))
            try:
                cursor.execute("SELECT username_1 FROM chats WHERE username_2 = (?)", (user_2,))
                fetched_chats_of_user2 = cursor.fetchall()            
                for i in fetched_chats_of_user2:
                    list_of_names.append(str(i).strip("[(', )]"))
            except:
                pass
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