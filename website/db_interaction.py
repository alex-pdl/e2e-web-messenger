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
            #connecting to the database
            connection = sqlite3.connect('users.db')
            cursor = connection.cursor()
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
        #connecting to the database
        connection = sqlite3.connect('users.db')  
        #establishing a cursor
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
        
    def username_check(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT username FROM users WHERE username = (?)", (self.username,))
        fetched_username = str(cursor.fetchall()).strip("[(', )]")
        if self.username == fetched_username:
            return True
        else:
            return False

    def retrieve_user_id(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = (?)", (self.username,))
        retrieved_id = str(cursor.fetchall()).strip("[(', )]")
        return retrieved_id