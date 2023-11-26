import sqlite3
import hashlib

class user_db_interaction:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user = ""

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
    
    def chat_creation(self, user_2):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        
        #checks if the user already has a chat with the username submitted.
        #fetches chats of user1
        list_of_names = []
        cursor.execute("SELECT username_2 FROM chats WHERE username_1 = (?)", (self.username,))  
        fetched_chats_of_user1 = cursor.fetchall()
        for i in fetched_chats_of_user1:
            list_of_names.append(str(i).strip("[(', )]"))
        
        #fetches chats of user2
        try:
            cursor.execute("SELECT username_1 FROM chats WHERE username_2 = (?)", ("123456",))
            fetched_chats_of_user2 = cursor.fetchall()
            
            for i in fetched_chats_of_user2:
                list_of_names.append(str(i).strip("[(', )]"))
        except:
            pass
        
        if self.username in list_of_names:
            print("True")
        else:
            print("False")

        if self.username not in list_of_names or user_2 not in list_of_names:
            #creates and adds the user and the user they choose to chat with to the 'chats' database
            create_chats_table = """
                CREATE TABLE IF NOT EXISTS chats (
                chatid INTEGER PRIMARY KEY NOT NULL,
                username_1 INTEGER,
                username_2 INTEGER
                ) """
            cursor.execute(create_chats_table)
            values = [
                self.username,user_2
            ]
            cursor.execute("INSERT INTO chats (username_1,username_2) VALUES(?,?)", (values))
            connection.commit()
        connection.close()